"""Endorsement and ledger event models."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class Subject:
    type: str
    reference: str

    def to_dict(self) -> dict[str, str]:
        return {"type": self.type, "reference": self.reference}


@dataclass
class Verifier:
    verifier_id: str
    verifier_type: str
    independent_of_subject: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "verifier_id": self.verifier_id,
            "verifier_type": self.verifier_type,
            "independent_of_subject": self.independent_of_subject,
        }


@dataclass
class EndorsementRecord:
    endorsement_id: str
    subject: Subject
    verifier: Verifier
    method: str
    issued_at: str
    status: str
    signature: str
    evidence_refs: list[str] = field(default_factory=list)
    expires_at: str | None = None
    jethro_color: str | None = None

    @classmethod
    def create(
        cls,
        *,
        subject: Subject,
        verifier: Verifier,
        method: str,
        status: str,
        evidence_refs: list[str] | None = None,
        expires_at: str | None = None,
        jethro_color: str | None = None,
        endorsement_id: str | None = None,
        issued_at: str | None = None,
        signature: str = "",
    ) -> EndorsementRecord:
        return cls(
            endorsement_id=endorsement_id or str(uuid.uuid4()),
            subject=subject,
            verifier=verifier,
            method=method,
            issued_at=issued_at or utc_now_iso(),
            status=status,
            signature=signature,
            evidence_refs=list(evidence_refs or []),
            expires_at=expires_at,
            jethro_color=jethro_color,
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "endorsement_id": self.endorsement_id,
            "subject": self.subject.to_dict(),
            "verifier": self.verifier.to_dict(),
            "method": self.method,
            "issued_at": self.issued_at,
            "status": self.status,
            "signature": self.signature,
            "evidence_refs": self.evidence_refs,
        }
        if self.expires_at:
            data["expires_at"] = self.expires_at
        if self.jethro_color:
            data["jethro_color"] = self.jethro_color
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EndorsementRecord:
        subject = Subject(**data["subject"])
        verifier = Verifier(**data["verifier"])
        return cls(
            endorsement_id=data["endorsement_id"],
            subject=subject,
            verifier=verifier,
            method=data["method"],
            issued_at=data["issued_at"],
            status=data["status"],
            signature=data.get("signature", ""),
            evidence_refs=list(data.get("evidence_refs") or []),
            expires_at=data.get("expires_at"),
            jethro_color=data.get("jethro_color"),
        )


@dataclass
class LedgerEvent:
    """Append-only ledger row (endorsement or gate telemetry)."""

    event_id: str
    event_type: str
    date: str
    actor: str
    subject_type: str | None = None
    subject_reference: str | None = None
    endorsement_id: str | None = None
    detail: str | None = None
    evidence_refs: list[str] = field(default_factory=list)
    follow_up: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        event_type: str,
        actor: str,
        subject_type: str | None = None,
        subject_reference: str | None = None,
        endorsement_id: str | None = None,
        detail: str | None = None,
        evidence_refs: list[str] | None = None,
        follow_up: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> LedgerEvent:
        return cls(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            date=utc_now_iso(),
            actor=actor,
            subject_type=subject_type,
            subject_reference=subject_reference,
            endorsement_id=endorsement_id,
            detail=detail,
            evidence_refs=list(evidence_refs or []),
            follow_up=follow_up,
            payload=dict(payload or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
