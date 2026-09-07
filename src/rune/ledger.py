"""Append-only JSONL endorsement ledger."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable

from rune.models import EndorsementRecord, LedgerEvent


DEFAULT_LEDGER_PATH = Path("data") / "endorsement_ledger.jsonl"
BOOTSTRAP_VERIFIER_EVENT = "bootstrap_verifier"
ENDORSEMENT_EVENT = "endorsement"
GATE_ALLOW_EVENT = "gate_allow"
GATE_BLOCK_EVENT = "gate_block"
REVOKE_EVENT = "revoke"


def ledger_path(path: str | Path | None = None) -> Path:
    if path is not None:
        return Path(path)
    env = os.environ.get("RUNE_LEDGER_PATH")
    if env:
        return Path(env)
    return DEFAULT_LEDGER_PATH


class EndorsementLedger:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = ledger_path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def append(self, row: dict[str, Any]) -> dict[str, Any]:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        return row

    def append_event(self, event: LedgerEvent) -> dict[str, Any]:
        return self.append(event.to_dict())

    def append_endorsement(self, record: EndorsementRecord, *, actor: str) -> dict[str, Any]:
        event = LedgerEvent.create(
            event_type=ENDORSEMENT_EVENT,
            actor=actor,
            subject_type=record.subject.type,
            subject_reference=record.subject.reference,
            endorsement_id=record.endorsement_id,
            detail=record.status,
            evidence_refs=record.evidence_refs,
            payload={"endorsement": record.to_dict()},
        )
        return self.append_event(event)

    def iter_rows(self) -> Iterable[dict[str, Any]]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)

    def list_rows(self, *, limit: int | None = None, reverse: bool = True) -> list[dict[str, Any]]:
        rows = list(self.iter_rows())
        if reverse:
            rows.reverse()
        if limit is not None:
            rows = rows[:limit]
        return rows

    def endorsements(self) -> list[EndorsementRecord]:
        out: list[EndorsementRecord] = []
        for row in self.iter_rows():
            if row.get("event_type") != ENDORSEMENT_EVENT:
                continue
            payload = row.get("payload") or {}
            endorsement = payload.get("endorsement")
            if endorsement:
                out.append(EndorsementRecord.from_dict(endorsement))
        return out

    def latest_endorsement_for(
        self, subject_type: str, reference: str
    ) -> EndorsementRecord | None:
        """Return the newest endorsement snapshot for a subject (any status).

        Walks newest-first. A later REVOKED/REJECTED/PENDING snapshot supersedes
        an earlier ENDORSED row for the same endorsement_id.
        """
        seen_ids: set[str] = set()
        for row in reversed(list(self.iter_rows())):
            if row.get("event_type") != ENDORSEMENT_EVENT:
                continue
            payload = (row.get("payload") or {}).get("endorsement")
            if not payload:
                continue
            rec = EndorsementRecord.from_dict(payload)
            if rec.endorsement_id in seen_ids:
                continue
            seen_ids.add(rec.endorsement_id)
            if rec.subject.type == subject_type and rec.subject.reference == reference:
                return rec
        return None

    def get_endorsement(self, endorsement_id: str) -> EndorsementRecord | None:
        latest: EndorsementRecord | None = None
        for row in self.iter_rows():
            if row.get("event_type") == REVOKE_EVENT and row.get("endorsement_id") == endorsement_id:
                if latest:
                    latest.status = "REVOKED"
                continue
            if row.get("event_type") != ENDORSEMENT_EVENT:
                continue
            payload = (row.get("payload") or {}).get("endorsement")
            if not payload:
                continue
            rec = EndorsementRecord.from_dict(payload)
            if rec.endorsement_id == endorsement_id:
                latest = rec
        return latest

    def bootstrap_verifier_id(self) -> str | None:
        for row in self.iter_rows():
            if row.get("event_type") == BOOTSTRAP_VERIFIER_EVENT:
                return (row.get("payload") or {}).get("verifier_id") or row.get("actor")
        return None
