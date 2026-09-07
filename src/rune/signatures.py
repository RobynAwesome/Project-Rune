"""Canonical JSON + HMAC / Ed25519 signatures for endorsement records."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
    load_pem_private_key,
    load_pem_public_key,
)


def canonical_payload(record: Mapping[str, Any]) -> bytes:
    """Serialize record for signing: omit signature, sort keys, compact JSON."""
    body = {k: v for k, v in record.items() if k != "signature"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _hmac_secret() -> bytes | None:
    secret = os.environ.get("RUNE_HMAC_SECRET")
    if not secret:
        return None
    return secret.encode("utf-8")


def _load_ed25519_private() -> Ed25519PrivateKey | None:
    raw = os.environ.get("RUNE_ED25519_PRIVATE_KEY")
    if not raw:
        return None
    raw = raw.strip()
    if raw.startswith("-----"):
        key = load_pem_private_key(raw.encode("utf-8"), password=None)
        if not isinstance(key, Ed25519PrivateKey):
            raise ValueError("RUNE_ED25519_PRIVATE_KEY is not an Ed25519 private key")
        return key
    return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(raw))


def _load_ed25519_public() -> Ed25519PublicKey | None:
    raw = os.environ.get("RUNE_ED25519_PUBLIC_KEY")
    if not raw:
        priv = _load_ed25519_private()
        if priv is None:
            return None
        return priv.public_key()
    raw = raw.strip()
    if raw.startswith("-----"):
        key = load_pem_public_key(raw.encode("utf-8"))
        if not isinstance(key, Ed25519PublicKey):
            raise ValueError("RUNE_ED25519_PUBLIC_KEY is not an Ed25519 public key")
        return key
    return Ed25519PublicKey.from_public_bytes(bytes.fromhex(raw))


def sign_record(record: Mapping[str, Any]) -> str:
    """Sign with Ed25519 if configured, else HMAC-SHA256. Raises if neither available."""
    payload = canonical_payload(record)
    priv = _load_ed25519_private()
    if priv is not None:
        sig = priv.sign(payload)
        return f"ed25519:{sig.hex()}"
    secret = _hmac_secret()
    if secret is None:
        raise RuntimeError(
            "No signing material: set RUNE_HMAC_SECRET or RUNE_ED25519_PRIVATE_KEY"
        )
    digest = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return f"hmac:{digest}"


def verify_signature(record: Mapping[str, Any]) -> bool:
    signature = record.get("signature")
    if not isinstance(signature, str) or ":" not in signature:
        return False
    scheme, value = signature.split(":", 1)
    payload = canonical_payload(record)
    if scheme == "hmac":
        secret = _hmac_secret()
        if secret is None:
            return False
        expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, value)
    if scheme == "ed25519":
        pub = _load_ed25519_public()
        if pub is None:
            return False
        try:
            pub.verify(bytes.fromhex(value), payload)
            return True
        except (InvalidSignature, ValueError):
            return False
    return False


def generate_ed25519_keypair_hex() -> tuple[str, str]:
    """Utility for tests / bootstrap docs: (private_hex, public_hex)."""
    priv = Ed25519PrivateKey.generate()
    priv_bytes = priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    pub_bytes = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return priv_bytes.hex(), pub_bytes.hex()
