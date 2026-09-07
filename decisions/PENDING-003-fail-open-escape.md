# PENDING-003 — `RUNE_FAIL_MODE=open` escape hatch

**Status:** `PENDING` (REVISE implemented in code; **not owner-endorsed**)  
**Proposed decision:** **REVISE** — preserve fail-closed default; high-risk never fail-open; low-risk only as explicit dev escape with ledger receipts  
**Opened:** 2026-09-07  
**Implementation pass:** 2026-09-07

## Phase 0 verification (pre-patch)

Inspected checkout `gate.py` at start of pass. Claim verified by code + Phase-1 tests (21 passed):

- `RUNE_FAIL_MODE=open` alone allowed `other` without endorsement
- High-risk trio remained denied without endorsement

## Proposed decision (REVISE)

1. Missing/unknown mode → closed  
2. `closed` → closed  
3. High-risk → closed regardless of open configuration  
4. Low-risk bypass only when `open` **and** `RUNE_DEV_ESCAPE=1` **and** `RUNE_ENV != production`  
5. Every low-risk bypass → append-only `gate_bypass` (+ `fail_open_active` once) with observable facts only  

## Implementation evidence

- `src/rune/gate.py` — `fail_mode`, `fail_open_active`, bypass branch + ledger events  
- `src/rune/ledger.py` — `GATE_BYPASS_EVENT`, `FAIL_OPEN_ACTIVE_EVENT`

## Tests executed

- Phase-1 historical receipt: 21 passed pre-patch (archived/skipped file notes this)
- `tests/test_fail_mode_revised.py` — high-risk under open+escape denied; low-risk allowed with bypass receipt; open without escape closed; production refuses open; garbage/empty/closed deny

## Unresolved limitations

- Env var flip still not itself an endorsed subject (who set the env remains unauthenticated)
- Owner must still ratify REVISE vs remove entirely

## Must not claim until `ENDORSED`

- That fail-open is doctrine-safe or production-approved
