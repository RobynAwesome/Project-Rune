"""Unit tests for ledger, signatures, and gate basics."""

from __future__ import annotations

from rune.gate import Gate
from rune.signatures import sign_record, verify_signature


def test_bootstrap_creates_receipt(gate: Gate) -> None:
    assert gate.ledger.bootstrap_verifier_id() == "sse-robyn"
    rows = list(gate.ledger.iter_rows())
    assert any(r["event_type"] == "bootstrap_verifier" for r in rows)


def test_fail_closed_without_endorsement(gate: Gate) -> None:
    decision = gate.check(
        "agent_coordination_event",
        "channel-x",
        actor="test",
    )
    assert decision.allowed is False
    assert "fail closed" in decision.reason


def test_endorse_then_allow(gate: Gate) -> None:
    record = gate.request_endorsement(
        "agent_coordination_event",
        "channel-x",
        method="human owner confirmation",
        actor="owner",
        confirm=True,
        evidence_refs=["owner_ok"],
    )
    assert record.status == "ENDORSED"
    assert verify_signature(record.to_dict())

    decision = gate.check("agent_coordination_event", "channel-x", actor="test")
    assert decision.allowed is True
    assert decision.endorsement is not None
    assert decision.endorsement.endorsement_id == record.endorsement_id


def test_revoke_blocks(gate: Gate) -> None:
    record = gate.request_endorsement(
        "completion_claim",
        "feature-42",
        method="human owner confirmation",
        actor="owner",
        confirm=True,
    )
    gate.revoke(record.endorsement_id, actor="owner", reason="premature")
    decision = gate.check("completion_claim", "feature-42", actor="test")
    assert decision.allowed is False
    assert "revoked" in decision.reason


def test_hmac_signature_roundtrip(hmac_secret: str) -> None:
    record = {
        "endorsement_id": "e1",
        "subject": {"type": "other", "reference": "r1"},
        "verifier": {
            "verifier_id": "sse-robyn",
            "verifier_type": "human",
            "independent_of_subject": True,
        },
        "method": "test",
        "issued_at": "2026-09-07T00:00:00Z",
        "status": "ENDORSED",
        "evidence_refs": [],
    }
    sig = sign_record(record)
    record["signature"] = sig
    assert sig.startswith("hmac:")
    assert verify_signature(record)
