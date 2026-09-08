"""Unit tests for ledger, Ed25519 signatures, and gate basics."""

from __future__ import annotations

import base64
import json

import pytest

from rune.gate import Gate
from rune.models import EndorsementRecord, Subject, Verifier
from rune.signatures import (
    generate_ed25519_keypair_hex,
    public_key_id,
    resolve_public_key,
    sign_record,
    signed_bytes,
    verify_signature,
)


def test_bootstrap_creates_receipt(gate: Gate) -> None:
    assert gate.ledger.bootstrap_verifier_id() == "sse-robyn"
    rows = gate.ledger.list_rows()
    assert any(r["event_type"] == "bootstrap_verifier" for r in rows)


def test_high_risk_blocked_without_endorsement(gate: Gate) -> None:
    d = gate.check("agent_coordination_event", "ch-1")
    assert d.allowed is False
    assert "fail closed" in d.reason.lower()


def test_endorse_then_allow(gate: Gate) -> None:
    rec = gate.request_endorsement(
        "agent_coordination_event",
        "ch-1",
        method="human owner confirmation",
        actor="owner",
        confirm=True,
    )
    assert rec.status == "ENDORSED"
    assert isinstance(rec.signature, dict)
    assert rec.signature["algorithm"] == "Ed25519"
    assert verify_signature(rec.to_dict(), verifier_id="sse-robyn")
    d = gate.check("agent_coordination_event", "ch-1")
    assert d.allowed is True


def test_revoke_blocks(gate: Gate) -> None:
    rec = gate.request_endorsement(
        "completion_claim",
        "task-1",
        method="owner",
        actor="owner",
        confirm=True,
    )
    gate.revoke(rec.endorsement_id, actor="owner", reason="recheck")
    d = gate.check("completion_claim", "task-1")
    assert d.allowed is False


def test_hmac_legacy_string_not_valid_identity(ed25519_keys: tuple[str, str]) -> None:
    record = {
        "endorsement_id": "x",
        "subject": {"type": "other", "reference": "r"},
        "verifier": {
            "verifier_id": "sse-robyn",
            "verifier_type": "human",
            "independence_claimed": False,
        },
        "method": "t",
        "issued_at": "2026-01-01T00:00:00Z",
        "status": "ENDORSED",
        "signature": "hmac:deadbeef",
        "evidence_refs": [],
    }
    assert verify_signature(record, verifier_id="sse-robyn") is False


def test_ed25519_roundtrip(ed25519_keys: tuple[str, str]) -> None:
    record = {
        "endorsement_id": "x",
        "subject": {"type": "other", "reference": "r"},
        "verifier": {
            "verifier_id": "sse-robyn",
            "verifier_type": "human",
            "independence_claimed": False,
        },
        "method": "t",
        "issued_at": "2026-01-01T00:00:00Z",
        "status": "ENDORSED",
        "evidence_refs": [],
    }
    record["signature"] = sign_record(record)
    assert verify_signature(record, verifier_id="sse-robyn")


def test_tamper_subject_reference_invalidates(ed25519_keys: tuple[str, str]) -> None:
    record = {
        "endorsement_id": "x",
        "subject": {"type": "other", "reference": "r1"},
        "verifier": {
            "verifier_id": "sse-robyn",
            "verifier_type": "human",
            "independence_claimed": False,
        },
        "method": "t",
        "issued_at": "2026-01-01T00:00:00Z",
        "status": "ENDORSED",
        "evidence_refs": [],
    }
    record["signature"] = sign_record(record)
    record["subject"]["reference"] = "r2"
    assert verify_signature(record, verifier_id="sse-robyn") is False


def test_tamper_subject_type_invalidates(ed25519_keys: tuple[str, str]) -> None:
    record = {
        "endorsement_id": "x",
        "subject": {"type": "other", "reference": "r1"},
        "verifier": {
            "verifier_id": "sse-robyn",
            "verifier_type": "human",
            "independence_claimed": False,
        },
        "method": "t",
        "issued_at": "2026-01-01T00:00:00Z",
        "status": "ENDORSED",
        "evidence_refs": [],
    }
    record["signature"] = sign_record(record)
    record["subject"]["type"] = "completion_claim"
    assert verify_signature(record, verifier_id="sse-robyn") is False


def test_tamper_verifier_id_invalidates(ed25519_keys: tuple[str, str]) -> None:
    record = {
        "endorsement_id": "x",
        "subject": {"type": "other", "reference": "r1"},
        "verifier": {
            "verifier_id": "sse-robyn",
            "verifier_type": "human",
            "independence_claimed": False,
        },
        "method": "t",
        "issued_at": "2026-01-01T00:00:00Z",
        "status": "ENDORSED",
        "evidence_refs": [],
    }
    record["signature"] = sign_record(record)
    record["verifier"]["verifier_id"] = "other-verifier"
    assert verify_signature(record, verifier_id="sse-robyn") is False


def test_tamper_status_invalidates(ed25519_keys: tuple[str, str]) -> None:
    record = {
        "endorsement_id": "x",
        "subject": {"type": "other", "reference": "r1"},
        "verifier": {
            "verifier_id": "sse-robyn",
            "verifier_type": "human",
            "independence_claimed": False,
        },
        "method": "t",
        "issued_at": "2026-01-01T00:00:00Z",
        "status": "PENDING",
        "evidence_refs": [],
    }
    record["signature"] = sign_record(record)
    record["status"] = "ENDORSED"
    assert verify_signature(record, verifier_id="sse-robyn") is False


def test_wrong_public_key_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    priv_a, pub_a = generate_ed25519_keypair_hex()
    _priv_b, pub_b = generate_ed25519_keypair_hex()
    monkeypatch.setenv("RUNE_ED25519_PRIVATE_KEY", priv_a)
    monkeypatch.setenv("RUNE_VERIFIER_PUBLIC_KEYS", json.dumps({"sse-robyn": pub_a}))
    record = {
        "endorsement_id": "x",
        "subject": {"type": "other", "reference": "r"},
        "verifier": {
            "verifier_id": "sse-robyn",
            "verifier_type": "human",
            "independence_claimed": False,
        },
        "method": "t",
        "issued_at": "2026-01-01T00:00:00Z",
        "status": "ENDORSED",
        "evidence_refs": [],
    }
    record["signature"] = sign_record(record)
    monkeypatch.setenv("RUNE_VERIFIER_PUBLIC_KEYS", json.dumps({"sse-robyn": pub_b}))
    assert verify_signature(record, verifier_id="sse-robyn") is False


def test_malformed_signature_fails_safely(ed25519_keys: tuple[str, str]) -> None:
    record = {
        "endorsement_id": "x",
        "subject": {"type": "other", "reference": "r"},
        "verifier": {
            "verifier_id": "sse-robyn",
            "verifier_type": "human",
            "independence_claimed": False,
        },
        "method": "t",
        "issued_at": "2026-01-01T00:00:00Z",
        "status": "ENDORSED",
        "signature": {"algorithm": "Ed25519", "key_id": "ed25519:x", "value": "!!!"},
        "evidence_refs": [],
    }
    assert verify_signature(record, verifier_id="sse-robyn") is False


def test_missing_key_fails_safely(monkeypatch: pytest.MonkeyPatch) -> None:
    priv, pub = generate_ed25519_keypair_hex()
    monkeypatch.setenv("RUNE_ED25519_PRIVATE_KEY", priv)
    monkeypatch.setenv("RUNE_VERIFIER_PUBLIC_KEYS", json.dumps({"sse-robyn": pub}))
    record = {
        "endorsement_id": "x",
        "subject": {"type": "other", "reference": "r"},
        "verifier": {
            "verifier_id": "sse-robyn",
            "verifier_type": "human",
            "independence_claimed": False,
        },
        "method": "t",
        "issued_at": "2026-01-01T00:00:00Z",
        "status": "ENDORSED",
        "evidence_refs": [],
    }
    record["signature"] = sign_record(record)
    monkeypatch.delenv("RUNE_VERIFIER_PUBLIC_KEYS", raising=False)
    monkeypatch.delenv("RUNE_ED25519_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("RUNE_ED25519_PRIVATE_KEY", raising=False)
    assert verify_signature(record, verifier_id="sse-robyn") is False


def test_jcs_key_order_stable(ed25519_keys: tuple[str, str]) -> None:
    a = {
        "b": 1,
        "a": {"z": True, "y": False},
        "evidence_refs": [],
        "status": "ENDORSED",
    }
    b = {
        "status": "ENDORSED",
        "evidence_refs": [],
        "a": {"y": False, "z": True},
        "b": 1,
    }
    assert signed_bytes(a) == signed_bytes(b)


def test_self_endorsement_refused(gate: Gate) -> None:
    with pytest.raises(ValueError, match="self-endorsement"):
        gate.request_endorsement(
            "agent_coordination_event",
            "sse-robyn",
            method="self",
            actor="owner",
            confirm=True,
            verifier_id="sse-robyn",
        )


def test_independence_claimed_not_proof(gate: Gate) -> None:
    rec = gate.request_endorsement(
        "other",
        "x",
        method="claim",
        actor="owner",
        confirm=True,
        independence_claimed=True,
        independence_basis="I assert independence",
    )
    assert rec.verifier.independence_claimed is True
    # Gate allow is from valid signature + ENDORSED, not from the claim boolean.
    d = gate.check("other", "x")
    assert d.allowed is True
    assert d.reason == "endorsed with valid receipt"


def test_legacy_independent_of_subject_maps_to_claimed() -> None:
    v = Verifier.from_dict(
        {
            "verifier_id": "v1",
            "verifier_type": "human",
            "independent_of_subject": True,
        }
    )
    assert v.independence_claimed is True
    assert "independent_of_subject" not in v.to_dict()
