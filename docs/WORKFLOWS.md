# Workflows — Project Rune

Operating loops for the endorsement gate. Cadence cloned from the Token Monday Review Protocol; adapted for endorsements, gate misses, and false completions.

## 1. Pre-action gate

```
classify subject → require endorsement → execute or block → ledger row
```

1. Classify the intended action (`agent_coordination_event`, `identity_file_change`, `completion_claim`, or `other`).
2. If high-risk (MVP: the three named types), call `rune check`.
3. If no valid `ENDORSED` record → **block** (fail closed) and append a gate-block ledger event.
4. If endorsed → allow and append a gate-allow ledger event with endorsement id.
5. Never narrate “safe coordination” without a ledger row.

CLI:

```bash
python -m rune check --subject-type agent_coordination_event --reference <id>
python -m rune endorse --subject-type ... --reference ... --method "..." --confirm
python -m rune revoke --endorsement-id <id> --reason "..."
```

## 2. Weekly Monday RUNE review

**Frequency:** Every Monday (standing governance ritual).  
**Purpose:** Review endorsements and gate health — not a coding ritual.

### Steps

1. Inspect the last 7 days of ledger rows: endorsements issued, blocked checks, revocations, pending holds.
2. Write one review note under `workflows/reviews/` (use the template) covering:
   - Endorsements issued / blocked
   - Gate misses (actions that should have been gated but weren't observed)
   - False completion attempts
   - At most 3 protocol adjustments recommended (do not implement unless ordered)
3. Flag repeated FoC patterns for BREACH-style follow-up.
4. Revive cadence if weeklies go stale (token weeklies last ran May — do not let RUNE weeklies repeat that drift).

Template: [workflows/weekly_monday_review_template.md](../workflows/weekly_monday_review_template.md)

## 3. Incident → FoC

Any trust-bridge / coordination surprise, unauthorized identity-file write, or false completion opens a FoC-style entry:

| RUNE scenario | Suggested FoC affinity |
|---|---|
| Shared writable channel without endorsement | ContextBleed / GhostExecution |
| “We agree it’s safe” multi-agent vote | SemanticDrift (consensus ≠ endorsement) |
| SOUL.md agent write | ContextCorruption / SemanticDrift |
| Completion claim without receipt | GhostExecution |

Cross-link evidence to Introduction-to-MCP `poc-vs-foc/BREACH_LOG.md` when operating inside the GSMB estate. Inside Project-Rune, record evidence refs on the ledger row and optionally under `workflows/incidents/`.

**Do not rewrite** `poc_foc_enforcer.py` — RUNE strengthens KPGS by receipts and scenarios, not by forking the enforcer.

## 4. Status discipline

| Status | Meaning |
|---|---|
| `PENDING` | Requested; awaiting independent verifier |
| `ENDORSED` | Verifier signed; gate may allow |
| `REJECTED` | Verifier refused |
| `REVOKED` | Previously endorsed; no longer valid |

`COMPLETE` / `PROVEN` / `DEMO READY` / `DONE` require a `completion_claim` endorsement with owner confirmation evidence.

## 5. Jethro Green / Yellow / Red hooks

Named integration with KPGS Jethro triage. Minimal MVP code: `rune.jethro.classify_triage`.

| Color | When | Action |
|---|---|---|
| **Green** | Routine single-agent tool path; low ambiguity; prior similar endorsements | Endorse after lightweight human confirm |
| **Yellow** | Novel coordination; identity-file change; incomplete evidence | Hold `PENDING`; human review required |
| **Red** | Trust-bridge surprise; consensus-only claim; missing verifier; suspected FoC | Block; `REJECTED` or refuse check; open FoC incident |

CLI hint:

```bash
python -m rune triage --subject-type identity_file_change --reference SOUL.md
```

## Bootstrap (first verifier)

```bash
export RUNE_HMAC_SECRET="dev-secret-change-me"
python -m rune bootstrap --verifier-id sse-robyn
```

Creates the human verifier bootstrap receipt. Subsequent endorsements use that verifier identity unless overridden.
