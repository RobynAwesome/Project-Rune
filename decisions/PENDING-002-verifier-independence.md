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
