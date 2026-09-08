"""Shared fixtures for RUNE MVP tests — Ed25519 test-only keys."""

from __future__ import annotations

import json
import os

import pytest

from rune.gate import Gate
from rune.ledger import EndorsementLedger
from rune.signatures import generate_ed25519_keypair_hex


@pytest.fixture()
def ed25519_keys(monkeypatch: pytest.MonkeyPatch) -> tuple[str, str]:
    """TEST-ONLY keypair. Not production credentials."""
    priv_hex, pub_hex = generate_ed25519_keypair_hex()
    monkeypatch.setenv("RUNE_ED25519_PRIVATE_KEY", priv_hex)
    monkeypatch.setenv("RUNE_ED25519_PUBLIC_KEY", pub_hex)
    monkeypatch.setenv(
        "RUNE_VERIFIER_PUBLIC_KEYS",
        json.dumps({"sse-robyn": pub_hex}),
    )
    monkeypatch.setenv("RUNE_FAIL_MODE", "closed")
    monkeypatch.delenv("RUNE_DEV_ESCAPE", raising=False)
    monkeypatch.delenv("RUNE_HMAC_SECRET", raising=False)
    monkeypatch.delenv("RUNE_ENV", raising=False)
    return priv_hex, pub_hex


@pytest.fixture()
def ledger(tmp_path, ed25519_keys: tuple[str, str]) -> EndorsementLedger:
    path = tmp_path / "endorsement_ledger.jsonl"
    os.environ["RUNE_LEDGER_PATH"] = str(path)
    return EndorsementLedger(path)


@pytest.fixture()
def gate(ledger: EndorsementLedger) -> Gate:
    g = Gate(ledger)
    g.bootstrap_human_verifier("sse-robyn", actor="owner")
    return g
