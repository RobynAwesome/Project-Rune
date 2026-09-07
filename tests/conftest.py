"""Shared fixtures for RUNE MVP tests."""

from __future__ import annotations

import os

import pytest

from rune.gate import Gate
from rune.ledger import EndorsementLedger


@pytest.fixture()
def hmac_secret(monkeypatch: pytest.MonkeyPatch) -> str:
    secret = "test-rune-hmac-secret"
    monkeypatch.setenv("RUNE_HMAC_SECRET", secret)
    monkeypatch.setenv("RUNE_FAIL_MODE", "closed")
    return secret


@pytest.fixture()
def ledger(tmp_path, hmac_secret: str) -> EndorsementLedger:
    path = tmp_path / "endorsement_ledger.jsonl"
    os.environ["RUNE_LEDGER_PATH"] = str(path)
    return EndorsementLedger(path)


@pytest.fixture()
def gate(ledger: EndorsementLedger) -> Gate:
    g = Gate(ledger)
    g.bootstrap_human_verifier("sse-robyn", actor="owner")
    return g
