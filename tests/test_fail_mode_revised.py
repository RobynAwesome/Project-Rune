"""PENDING-003 revised fail-mode behavior + bypass receipts."""

from __future__ import annotations

import pytest

from rune.gate import Gate, fail_open_active, fail_mode
from rune.ledger import (
    FAIL_OPEN_ACTIVE_EVENT,
    GATE_BYPASS_EVENT,
    EndorsementLedger,
)

HIGH_RISK = (
    "agent_coordination_event",
    "identity_file_change",
    "completion_claim",
)


@pytest.fixture()
def bare_gate(tmp_path, monkeypatch: pytest.MonkeyPatch, ed25519_keys) -> Gate:
    path = tmp_path / "ledger.jsonl"
    monkeypatch.setenv("RUNE_LEDGER_PATH", str(path))
    monkeypatch.setenv("RUNE_FAIL_MODE", "closed")
    monkeypatch.delenv("RUNE_DEV_ESCAPE", raising=False)
    monkeypatch.delenv("RUNE_ENV", raising=False)
    return Gate(EndorsementLedger(path))


@pytest.mark.parametrize("subject_type", HIGH_RISK)
def test_high_risk_blocked_under_open_with_dev_escape(
    bare_gate: Gate, monkeypatch: pytest.MonkeyPatch, subject_type: str
) -> None:
    monkeypatch.setenv("RUNE_FAIL_MODE", "open")
    monkeypatch.setenv("RUNE_DEV_ESCAPE", "1")
    d = bare_gate.check(subject_type, f"ref-{subject_type}")
    assert d.allowed is False


def test_low_risk_allowed_under_open_with_dev_escape_and_bypass_receipt(
    bare_gate: Gate, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RUNE_FAIL_MODE", "open")
    monkeypatch.setenv("RUNE_DEV_ESCAPE", "1")
    d = bare_gate.check("other", "low-1")
    assert d.allowed is True
    rows = bare_gate.ledger.list_rows()
    types = [r["event_type"] for r in rows]
    assert GATE_BYPASS_EVENT in types
    assert FAIL_OPEN_ACTIVE_EVENT in types
    bypass = next(r for r in rows if r["event_type"] == GATE_BYPASS_EVENT)
    assert bypass["payload"]["fail_mode"] == "open"
    assert "reason" in bypass["payload"]
    assert "session_id" in bypass["payload"]


def test_open_without_dev_escape_stays_closed(
    bare_gate: Gate, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RUNE_FAIL_MODE", "open")
    monkeypatch.delenv("RUNE_DEV_ESCAPE", raising=False)
    assert fail_open_active() is False
    d = bare_gate.check("other", "low-2")
    assert d.allowed is False


def test_production_env_refuses_fail_open(
    bare_gate: Gate, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RUNE_FAIL_MODE", "open")
    monkeypatch.setenv("RUNE_DEV_ESCAPE", "1")
    monkeypatch.setenv("RUNE_ENV", "production")
    assert fail_open_active() is False
    d = bare_gate.check("other", "prod-1")
    assert d.allowed is False


@pytest.mark.parametrize("mode", ["closed", "garbage", "", " OPEN "])
def test_invalid_or_closed_modes(
    bare_gate: Gate, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    monkeypatch.setenv("RUNE_FAIL_MODE", mode)
    monkeypatch.setenv("RUNE_DEV_ESCAPE", "1")
    if mode.strip().lower() == "open":
        # With spaces, mode normalizes to open — still needs non-production.
        assert fail_mode() == "open"
        d = bare_gate.check("other", "spaced")
        assert d.allowed is True
    else:
        assert fail_mode() == "closed"
        d = bare_gate.check("other", f"m-{mode!r}")
        assert d.allowed is False


def test_unset_defaults_closed(bare_gate: Gate, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RUNE_FAIL_MODE", raising=False)
    assert fail_mode() == "closed"
    for st in [*HIGH_RISK, "other"]:
        assert bare_gate.check(st, f"u-{st}", record_ledger=False).allowed is False
