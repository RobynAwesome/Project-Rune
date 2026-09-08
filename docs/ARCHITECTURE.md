# Architecture — Project Rune

Status: architecture with a **reference MVP under `src/rune/`**. Owner decisions PENDING-001/002/003 have **proposed implementations** with tests — still **`PENDING` / not owner-endorsed**. Implementation ≠ endorsement.

| Layer | Meaning |
|---|---|
| Implemented | Code path exists in this checkout |
| Tested | Covered by pytest in this checkout |
| Owner-endorsed | Decision record status `ENDORSED` + owner receipt — **none yet** |
| Unresolved | Explicitly open architecture |

## Components

### 1. Endorsement Record

Structured claim that a subject was checked. Fields: subject, verifier, method, issued_at, status, evidence_refs, optional expires_at, **Ed25519 structured signature**.

### 2. Verifier

**Implemented:** human bootstrap label via `rune bootstrap`; Ed25519 key material via env.

**Field:** `independence_claimed` (replaces misleading `independent_of_subject`; legacy alias still readable). Optional `independence_basis` is claim/evidence text only.

**`independent_system` enum:** schema-compatible; **not** treated as proof of independence by the gate.

**Unresolved (`PENDING-002`):** how architectural independence is established and re-checked over time. Do not invent model-lineage or org independence.

### 3. Gate

Fail-closed by default. High-risk subjects (`agent_coordination_event`, `identity_file_change`, `completion_claim`) **never** use fail-open.

Low-risk (`other`) bypass only when **all** of:

1. `RUNE_FAIL_MODE=open` (strip/lower; unknown → closed)
2. `RUNE_DEV_ESCAPE=1`
3. `RUNE_ENV` is not `production`

Every such bypass appends `gate_bypass` (and once per process `fail_open_active`) to the ledger. Facts recorded: fail_mode, subject, reason, session/run id — **not** “enabled by &lt;person&gt;” unless an authenticated control path exists (it does not).

### 4. Ledger

Append-only JSONL. Event types include: `bootstrap_verifier`, `endorsement`, `gate_allow`, `gate_block`, `gate_bypass`, `fail_open_active`, `revoke`. Historical lines are not rewritten.

## Signature scheme (`PENDING-001` — implemented Ed25519, not owner-endorsed)

**Signed bytes (explicit):**

1. Construct endorsement object  
2. **Exclude** `signature` entirely  
3. Canonicalize with RFC 8785-style JCS (`canonical_jcs` / `signed_bytes` in `src/rune/signatures.py`)  
4. UTF-8 encode  
5. Sign with verifier Ed25519 private key (RFC 8032 / FIPS 186-5 EdDSA)  
6. Store structured signature:

```json
{"algorithm": "Ed25519", "key_id": "ed25519:<sha256-prefix>", "value": "<base64>"}
```

7. Gate resolves verifier public key (`RUNE_VERIFIER_PUBLIC_KEYS` / fallbacks)  
8. Reconstruct identical canonical bytes  
9. Verify; failure → endorsement invalid → deny when required  

**HMAC is not a Rune endorsement identity mechanism.** Legacy `hmac:` / string signatures verify as false.

Keys: `RUNE_ED25519_PRIVATE_KEY` (sign), `RUNE_VERIFIER_PUBLIC_KEYS` JSON map verifier_id→public hex (verify). Private keys must not appear in ledger payloads as signing material beyond what the process needs at runtime.

## High-risk classes

Always require valid `ENDORSED` + verifying signature:

| Subject type | Examples |
|---|---|
| `agent_coordination_event` | Shared channels, multi-agent planning |
| `identity_file_change` | SOUL.md / identity-config mutation |
| `completion_claim` | COMPLETE / PROVEN / DEMO READY / DONE |

## Jethro integration (named hook)

| Color | Meaning |
|---|---|
| Green | Routine endorse path |
| Yellow | Human review / PENDING |
| Red | Block + FoC |

## Explicit non-goals

- Full PKI / multi-vendor verifier marketplace  
- Proving architectural independence  
- Claiming MHS partnership  
- Marking RUNE COMPLETE / PROVEN / DEMO READY without owner receipts  
