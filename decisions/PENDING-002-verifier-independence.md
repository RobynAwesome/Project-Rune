# PENDING-002 — Verifier independence

**Status:** `PENDING` (revised semantics implemented; independence **not solved**)  
**Proposed decision:** **REVISE** — claim language only; do not pretend proof  
**Opened:** 2026-09-07  
**Implementation pass:** 2026-09-07

## Proposed decision

Rune cannot prove architectural verifier independence. Replace misleading `independent_of_subject` with `independence_claimed`. Keep optional `independence_basis` as non-authoritative evidence text. `independent_system` enum must not auto-prove independence. Self-endorsement refused when `verifier_id == subject.reference` (and when actor equals high-risk subject reference on confirm).

## Implementation evidence

- `src/rune/models.py` — `independence_claimed` + legacy alias read path
- `src/rune/gate.py` — does not use claim/enum as allow proof; self-endorse raises `ValueError`
- Schema updated; stretch scenario records claim-only basis for `independent_system`

## Tests executed

- `test_independence_claimed_not_proof`
- `test_self_endorsement_refused`
- `test_legacy_independent_of_subject_maps_to_claimed`
- `test_poc_stretch_independent_system_is_claim_not_proof`

## Unresolved limitations

- No model-lineage detection
- No organizational independence
- No re-check-over-time mechanism
- Cross-architecture independent verifiers remain future architecture

## Must not claim until `ENDORSED`

- That independence is solved or that `independence_claimed=true` is proof

## External design references (non-dependencies)

These are **not** RUNE runtime dependencies and do not prove verifier independence. They are examples of claim-attribution discipline worth studying when PENDING-002 eventually needs an enforceable independence *basis*:

- **Market/data platforms with source+timestamp+URL attribution on claims** (e.g. Bigdata.com / RavenPack-style entity IDs and `include_source_attribution` audit linking) — every claim bound to a traceable, non-self-asserted source. Useful as a *pattern reference* for how `independence_basis` / `evidence_refs` might one day point at something outside the endorsing process.
- Do **not** wire financial market feeds into the endorsement gate unless KPGS explicitly needs USD/ZAR (or similar) for token-cost reviews — that is a Cost Profiles concern, not coordination verification.

Bigdata MCP may be used in other Claude/Cursor sessions for markets or spend context; that usage is separate from RUNE’s cryptographic gate.
