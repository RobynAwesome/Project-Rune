"""Fail-closed endorsement gate."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from rune import (
    HIGH_RISK_SUBJECT_TYPES,
    STATUS_ENDORSED,
    STATUS_PENDING,
    STATUS_REJECTED,
    STATUS_REVOKED,
)
from rune.jethro import TriageColor, classify_triage
from rune.ledger import (
    GATE_ALLOW_EVENT,
    GATE_BLOCK_EVENT,
    REVOKE_EVENT,
    EndorsementLedger,
)
from rune.models import EndorsementRecord, LedgerEvent, Subject, Verifier
from rune.signatures import sign_record, verify_signature


def fail_closed() -> bool:
    mode = (os.environ.get("RUNE_FAIL_MODE") or "closed").strip().lower()
    return mode != "open"


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def _is_expired(record: EndorsementRecord, now: datetime | None = None) -> bool:
    expires = _parse_iso(record.expires_at)
    if expires is None:
        return False
    now = now or datetime.now(timezone.utc)
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return now >= expires


@dataclass
class GateDecision:
    allowed: bool
    reason: str
    endorsement: EndorsementRecord | None = None
    jethro_color: TriageColor | None = None
    ledger_event_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "endorsement_id": self.endorsement.endorsement_id if self.endorsement else None,
            "jethro_color": self.jethro_color,
            "ledger_event_id": self.ledger_event_id,
        }


class Gate:
    def __init__(self, ledger: EndorsementLedger | None = None) -> None:
        self.ledger = ledger or EndorsementLedger()

    def check(
        self,
        subject_type: str,
        reference: str,
        *,
        actor: str = "gate",
        consensus_claimed: bool = False,
        record_ledger: bool = True,
    ) -> GateDecision:
        triage = classify_triage(
            subject_type,
            consensus_claimed=consensus_claimed,
            has_endorsement=False,
        )

        # Consensus-only claims are never sufficient.
        if consensus_claimed and subject_type in HIGH_RISK_SUBJECT_TYPES:
            decision = GateDecision(
                allowed=False,
                reason="consensus is not endorsement; rejected",
                jethro_color="red",
            )
            if record_ledger:
                ev = self.ledger.append_event(
                    LedgerEvent.create(
                        event_type=GATE_BLOCK_EVENT,
                        actor=actor,
                        subject_type=subject_type,
                        subject_reference=reference,
                        detail=decision.reason,
                        follow_up="require independent human endorsement",
                    )
                )
                decision.ledger_event_id = ev["event_id"]
            return decision

        record = self.ledger.latest_endorsement_for(subject_type, reference)
        if record is None:
            if subject_type not in HIGH_RISK_SUBJECT_TYPES and not fail_closed():
                return GateDecision(
                    allowed=True,
                    reason="non-high-risk and fail-open",
                    jethro_color="green",
                )
            decision = GateDecision(
                allowed=False,
                reason="fail closed: no endorsement record",
                jethro_color=triage if triage == "red" else "yellow",
            )
            if record_ledger:
                ev = self.ledger.append_event(
                    LedgerEvent.create(
                        event_type=GATE_BLOCK_EVENT,
                        actor=actor,
                        subject_type=subject_type,
                        subject_reference=reference,
                        detail=decision.reason,
                        follow_up="rune endorse --confirm after human verification",
                    )
                )
                decision.ledger_event_id = ev["event_id"]
            return decision

        if record.status == STATUS_REVOKED:
            decision = GateDecision(
                allowed=False,
                reason="endorsement revoked",
                endorsement=record,
                jethro_color="red",
            )
        elif record.status == STATUS_REJECTED:
            decision = GateDecision(
                allowed=False,
                reason="endorsement rejected",
                endorsement=record,
                jethro_color="red",
            )
        elif record.status == STATUS_PENDING:
            decision = GateDecision(
                allowed=False,
                reason="endorsement pending human verification",
                endorsement=record,
                jethro_color="yellow",
            )
        elif record.status != STATUS_ENDORSED:
            decision = GateDecision(
                allowed=False,
                reason=f"invalid endorsement status: {record.status}",
                endorsement=record,
                jethro_color="red",
            )
        elif _is_expired(record):
            decision = GateDecision(
                allowed=False,
                reason="endorsement expired",
                endorsement=record,
                jethro_color="yellow",
            )
        elif not verify_signature(record.to_dict()):
            decision = GateDecision(
                allowed=False,
                reason="signature verification failed",
                endorsement=record,
                jethro_color="red",
            )
        else:
            decision = GateDecision(
                allowed=True,
                reason="endorsed with valid receipt",
                endorsement=record,
                jethro_color="green",
            )

        if record_ledger:
            ev = self.ledger.append_event(
                LedgerEvent.create(
                    event_type=GATE_ALLOW_EVENT if decision.allowed else GATE_BLOCK_EVENT,
                    actor=actor,
                    subject_type=subject_type,
                    subject_reference=reference,
                    endorsement_id=record.endorsement_id,
                    detail=decision.reason,
                )
            )
            decision.ledger_event_id = ev["event_id"]
        return decision

    def request_endorsement(
        self,
        subject_type: str,
        reference: str,
        *,
        method: str,
        actor: str,
        evidence_refs: list[str] | None = None,
        confirm: bool = False,
        verifier_id: str | None = None,
        reject: bool = False,
        expires_at: str | None = None,
    ) -> EndorsementRecord:
        """Create PENDING, ENDORSED (human confirm), or REJECTED record."""
        bootstrap_id = self.ledger.bootstrap_verifier_id()
        vid = verifier_id or bootstrap_id or "sse-robyn"
        verifier = Verifier(
            verifier_id=vid,
            verifier_type="human",
            independent_of_subject=True,
        )
        if reject:
            status = STATUS_REJECTED
            color: TriageColor = "red"
        elif confirm:
            status = STATUS_ENDORSED
            color = classify_triage(subject_type, has_endorsement=True)
        else:
            status = STATUS_PENDING
            color = "yellow"

        record = EndorsementRecord.create(
            subject=Subject(type=subject_type, reference=reference),
            verifier=verifier,
            method=method,
            status=status,
            evidence_refs=evidence_refs,
            expires_at=expires_at,
            jethro_color=color,
        )
        unsigned = record.to_dict()
        record.signature = sign_record(unsigned)
        self.ledger.append_endorsement(record, actor=actor)
        return record

    def revoke(
        self,
        endorsement_id: str,
        *,
        actor: str,
        reason: str,
    ) -> EndorsementRecord:
        existing = self.ledger.get_endorsement(endorsement_id)
        if existing is None:
            raise KeyError(f"endorsement not found: {endorsement_id}")
        existing.status = STATUS_REVOKED
        # Re-sign revoked snapshot and append revoke event + endorsement snapshot.
        existing.signature = sign_record(existing.to_dict())
        self.ledger.append_event(
            LedgerEvent.create(
                event_type=REVOKE_EVENT,
                actor=actor,
                subject_type=existing.subject.type,
                subject_reference=existing.subject.reference,
                endorsement_id=endorsement_id,
                detail=reason,
                follow_up="re-endorse if still required",
            )
        )
        self.ledger.append_endorsement(existing, actor=actor)
        return existing

    def bootstrap_human_verifier(self, verifier_id: str = "sse-robyn", *, actor: str = "owner") -> dict:
        if self.ledger.bootstrap_verifier_id():
            return {
                "ok": True,
                "already": True,
                "verifier_id": self.ledger.bootstrap_verifier_id(),
            }
        # Bootstrap receipt is itself a signed ledger event (not a subject endorsement).
        payload = {
            "verifier_id": verifier_id,
            "verifier_type": "human",
            "independent_of_subject": True,
            "method": "human owner bootstrap",
            "note": "First verifier = human (SSE/Robyn); fail-closed until endorsements exist.",
        }
        # Sign a stable payload for receipts-first discipline.
        signed = dict(payload)
        signed["signature"] = sign_record(signed)
        event = LedgerEvent.create(
            event_type="bootstrap_verifier",
            actor=actor,
            detail=f"bootstrap human verifier {verifier_id}",
            evidence_refs=["owner_confirmation"],
            payload=signed,
        )
        row = self.ledger.append_event(event)
        return {"ok": True, "already": False, "event": row}
