"""Ed25519 endorsement signatures (RFC 8032) over RFC 8785-style canonical JSON.

Signed bytes:
1. Take endorsement object
2. Exclude the ``signature`` field entirely (no recursive participation)
3. Canonicalize remaining value per RFC 8785 JSON Canonicalization Scheme
   for the endorsement subset (objects, arrays, strings, bools, null, numbers)
4. Encode canonical JSON as UTF-8
5. Sign with verifier Ed25519 private key (RFC 8032 / FIPS 186-5 EdDSA)

HMAC is not an endorsement identity mechanism and is not used for signing.
Legacy ``hmac:`` string signatures verify as false (deny path).
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
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

ALGORITHM_ED25519 = "Ed25519"


def canonical_jcs(value: Any) -> str:
    """RFC 8785-compatible canonical JSON for endorsement payloads.

    - Object keys sorted lexicographically
    - No insignificant whitespace
    - Arrays preserve element order
    - Signature field must already be excluded by the caller
    """
    return _jcs_encode(value)


def _jcs_encode(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        # RFC 8785 number serialization — use JSON then normalize via ECMA rules
        # Endorsement payloads should prefer strings for timestamps; keep safe fail.
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ",".join(_jcs_encode(v) for v in value) + "]"
    if isinstance(value, dict):
        items = []
        for key in sorted(value.keys()):
            if not isinstance(key, str):
                raise TypeError("JCS object keys must be strings")
            items.append(json.dumps(key, ensure_ascii=False) + ":" + _jcs_encode(value[key]))
        return "{" + ",".join(items) + "}"
    raise TypeError(f"unsupported type for JCS: {type(value)!r}")


def signed_bytes(record: Mapping[str, Any]) -> bytes:
    """Bytes that Ed25519 signs/verifies: UTF-8(JCS(payload without signature))."""
    body = {k: v for k, v in record.items() if k != "signature"}
    return canonical_jcs(body).encode("utf-8")


def public_key_id(public_key: Ed25519PublicKey) -> str:
    raw = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    digest = hashlib.sha256(raw).hexdigest()[:32]
    return f"ed25519:{digest}"


def _load_private_key() -> Ed25519PrivateKey | None:
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


def _parse_public_hex(hex_or_pem: str) -> Ed25519PublicKey:
    text = hex_or_pem.strip()
    if text.startswith("-----"):
        key = load_pem_public_key(text.encode("utf-8"))
        if not isinstance(key, Ed25519PublicKey):
            raise ValueError("not an Ed25519 public key")
        return key
    return Ed25519PublicKey.from_public_bytes(bytes.fromhex(text))


def load_verifier_public_keys() -> dict[str, Ed25519PublicKey]:
    """Map verifier_id -> public key from RUNE_VERIFIER_PUBLIC_KEYS JSON.

    Format: {"sse-robyn": "<64-hex-public>" , ...}
    """
    raw = os.environ.get("RUNE_VERIFIER_PUBLIC_KEYS")
    if not raw:
        # Fallback: single global public key for the signing keypair
        pub_env = os.environ.get("RUNE_ED25519_PUBLIC_KEY")
        priv = _load_private_key()
        out: dict[str, Ed25519PublicKey] = {}
        if pub_env:
            out["*"] = _parse_public_hex(pub_env)
        elif priv is not None:
            out["*"] = priv.public_key()
        return out
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("RUNE_VERIFIER_PUBLIC_KEYS must be a JSON object")
    return {str(k): _parse_public_hex(str(v)) for k, v in data.items()}


def resolve_public_key(
    verifier_id: str | None = None, key_id: str | None = None
) -> Ed25519PublicKey | None:
    keys = load_verifier_public_keys()
    if verifier_id and verifier_id in keys:
        return keys[verifier_id]
    if "*" in keys:
        return keys["*"]
    if key_id:
        for pub in keys.values():
            if public_key_id(pub) == key_id:
                return pub
    return None


def make_signature_object(*, algorithm: str, key_id: str, value: str) -> dict[str, str]:
    return {"algorithm": algorithm, "key_id": key_id, "value": value}


def sign_record(record: Mapping[str, Any]) -> dict[str, str]:
    """Sign endorsement with Ed25519. Raises if no private key is configured."""
    priv = _load_private_key()
    if priv is None:
        raise RuntimeError(
            "No Ed25519 signing key: set RUNE_ED25519_PRIVATE_KEY "
            "(HMAC is not a Rune endorsement identity mechanism)"
        )
    payload = signed_bytes(record)
    sig = priv.sign(payload)
    pub = priv.public_key()
    return make_signature_object(
        algorithm=ALGORITHM_ED25519,
        key_id=public_key_id(pub),
        value=base64.b64encode(sig).decode("ascii"),
    )


def verify_signature(
    record: Mapping[str, Any], *, verifier_id: str | None = None
) -> bool:
    """Return True only for a valid Ed25519 structured signature. Never raises into allow."""
    signature = record.get("signature")
    try:
        if isinstance(signature, str):
            # Legacy string forms (hmac:/ed25519:) are not valid MVP identity signatures.
            return False
        if not isinstance(signature, dict):
            return False
        algorithm = signature.get("algorithm")
        key_id = signature.get("key_id")
        value = signature.get("value")
        if algorithm != ALGORITHM_ED25519:
            return False
        if not isinstance(key_id, str) or not isinstance(value, str):
            return False
        if not value or not re.fullmatch(r"[A-Za-z0-9+/=]+", value):
            return False
        pub = resolve_public_key(verifier_id=verifier_id, key_id=key_id)
        if pub is None:
            return False
        if public_key_id(pub) != key_id:
            return False
        payload = signed_bytes(record)
        pub.verify(base64.b64decode(value), payload)
        return True
    except (InvalidSignature, ValueError, TypeError, json.JSONDecodeError, KeyError):
        return False


def generate_ed25519_keypair_hex() -> tuple[str, str]:
    """Test-only keypair: (private_hex, public_hex). Never use as production credentials."""
    priv = Ed25519PrivateKey.generate()
    priv_bytes = priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    pub_bytes = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return priv_bytes.hex(), pub_bytes.hex()
