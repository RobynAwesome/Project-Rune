# Architecture — Project Rune

Status: architecture with **MVP defaults decided**. Reference implementation lives under `src/rune/`. This is not a claim of production completeness.

## Components

### 1. Endorsement Record

The core artifact. A structured, signed claim that a specific action, coordination event, or identity assertion was independently checked.

Minimum required fields (see `schemas/endorsement.schema.json`):

- what is being endorsed (the subject)
- who issued the endorsement (the verifier)
- whether the verifier is architecturally independent of the subject
- what method was used to check
- when it was issued
- a signature binding the record to the verifier

### 2. Verifier

An entity — human, or a system with a genuinely different architecture, training lineage, or failure surface than the agent being checked — that issues endorsements.

**MVP default:** first verifier is **human (SSE / Robyn)** with `verifier_type: human` and `independent_of_subject: true`. Bootstrap via `rune bootstrap`. Cross-architecture independent system verifiers remain a stretch goal after MVP.

**Still open (post-MVP):** how verifier independence is re-checked over time rather than asserted once.

### 3. Gate

The enforcement point. High-risk actions must have a valid, unexpired Endorsement Record with status `ENDORSED` before execution is permitted.

The gate sits outside the agent's own reasoning. An agent cannot satisfy its own gate by arguing that an action is safe — the gate checks for a valid signed record.

**MVP default:** **fail closed** when no verifier / no valid endorsement is available (`RUNE_FAIL_MODE=closed`).

### 4. Ledger

Append-only JSONL record of endorsements issued, actions gated, and actions blocked. Field patterns mirror the Token Incident Ledger: date, actor, type, evidence refs, follow-up — receipts first, not after-the-fact summaries.

Default path: `./data/endorsement_ledger.jsonl` (override with `RUNE_LEDGER_PATH`).

## High-risk classes (MVP allowlist)

These subject types **always** require endorsement:

| Subject type | Examples |
|---|---|
| `agent_coordination_event` | Shared writable channels, multi-agent planning, trust bridges |
| `identity_file_change` | SOUL.md / identity-config mutation |
| `completion_claim` | Writing COMPLETE / PROVEN / DEMO READY / DONE |

Optional / irreversible classes (`other`) may be classified by policy; MVP gate focuses on the three above.

## Signature scheme (MVP)

- **Primary:** HMAC-SHA256 over canonical JSON (keys sorted, no signature field in payload) using `RUNE_HMAC_SECRET`.
- **Optional:** Ed25519 when `RUNE_ED25519_PRIVATE_KEY` / `RUNE_ED25519_PUBLIC_KEY` are set (PEM or raw hex).
- Schema `signature` field stores `hmac:<hex>` or `ed25519:<hex>`.

Full PKI / multi-vendor verifier marketplace is an explicit non-goal for this pass.

## Jethro integration (named hook)

| Color | Meaning | Gate behavior |
|---|---|---|
| Green | Routine endorse path | Human verifier may endorse after lightweight check |
| Yellow | Human review required | Hold as `PENDING` until owner confirmation |
| Red | Block + FoC | Reject / revoke; open FoC-style incident entry |

See [WORKFLOWS.md](WORKFLOWS.md).

## Explicit non-goals (this pass)

- Full cryptographic PKI / multi-vendor verifier marketplace
- Rewriting Introduction-to-MCP `poc_foc_enforcer.py`
- Claiming MHS partnership
- Marking RUNE COMPLETE / DEMO READY without live gate + ledger receipts
