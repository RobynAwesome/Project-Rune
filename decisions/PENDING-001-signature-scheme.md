# PENDING-001 — Signature scheme

**Status:** `PENDING` (proposed decision implemented in code; **not owner-endorsed**)  
**Proposed decision:** **Ed25519** (reject HMAC as endorsement identity)  
**Opened:** 2026-09-07  
**Implementation pass:** 2026-09-07

## Proposed decision

Implement Ed25519 for verifier signatures. Do **not** use HMAC as the Rune endorsement identity mechanism.

## Implementation evidence

- `src/rune/signatures.py` — `signed_bytes` / `canonical_jcs` (RFC 8785-style), `sign_record` → structured `{algorithm,key_id,value}`, `verify_signature` Ed25519-only
- `schemas/endorsement.schema.json` — `signature` is an object (breaking vs prior string form)
- Legacy `hmac:` / string signatures → verify false (deny)

## Tests executed

- `tests/test_ledger_gate.py` — roundtrip, tamper subject/type/verifier/status, wrong key, malformed, missing key, JCS key-order stability, HMAC legacy rejected
- Full suite: see final validation output in session

## Unresolved limitations

- JCS implementation covers endorsement subset types; not a full RFC 8785 conformance suite
- Key distribution / rotation UX is minimal (env JSON map)
- Owner has not ratified Ed25519 as the endorsed standard

## Must not claim until `ENDORSED`

- That the signature scheme is owner-ratified or production-ready beyond reference MVP
