# PENDING-004 — Cross-link source audit (Introduction-to-MCP)

**Status:** `PENDING` (audit complete; **source PROVEN/COMPLETE claims still unendorsed**; **recommended action #2 OWNER-ENDORSED**)  
**Proposed decision:** **DO NOT** treat `Introduction-to-MCP` README PROVEN/COMPLETE claims as RUNE-authoritative until owner-verified evidence exists; **DO** note that the Issue #3 path targets exist as files; **DO** allow draft-only non-authoritative reference to `mmao-mao` schemas with `independence_claimed=false` (Owner Action #2).  
**Opened:** 2026-09-14  
**Auditor:** BEREA (hands / independent witness)  
**Owner endorsement (#2):** Creator / Master Robyn, group chat 2026-09-14 ("yeah go for it… what you need is in gsmb") — recorded under GSMB sovereign decision authority (Schematics MAIN BRAIN; Master Robyn Tier 0).  
**Scope:** Public GitHub `RobynAwesome/Introduction-to-MCP` @ `master` + live HTTP probes + follow-on body read of `mmao-mao/README.md` (2026-09-14).  
**Non-goals:** No Introduction-to-MCP README rewrites; no Phase-4 authoritative cross-link.

## Proposed decision

Before RUNE Issue #3 cross-links to `governance/kpgs-vnext/agent-governance/mmao-mao/` as an authoritative MMAO+MAO source, apply RUNE’s own doctrine: **no completion status without owner-verified evidence**.

## Owner actions (from original audit)

| # | Action | Status |
|---|---|---|
| 1 | Endorse or retract Introduction-to-MCP README PROVEN/COMPLETE language with dated receipts | `PENDING` (separate track; does not block RUNE draft work) |
| 2 | Allow RUNE to reference `mmao-mao` schemas **as draft contracts only**, with explicit `independence_claimed=false` / non-authoritative binding until (1) | **OWNER-ENDORSED** 2026-09-14 |
| 3 | Reopen Phase-4 authoritative cross-link only after (1) | `STANDS` — still blocked |

See also: [`docs/EXTERNAL_MMAO_MAO_DRAFT_REFERENCE.md`](../docs/EXTERNAL_MMAO_MAO_DRAFT_REFERENCE.md).

## Claimed (source README)

From `RobynAwesome/Introduction-to-MCP/README.md` on `master` (fetched 2026-09-14):

| Claim | Location |
|---|---|
| Status: **FULL STACK DEMO READY** (Verified **2026-04-11**) | README hero |
| **Kopano Context** = **PROVEN** | Ecosystem table |
| **Kopano Studio** = **PROVEN** | Ecosystem table |
| **KasiLink Bridge** = **PROVEN** | Ecosystem table |
| Phases **1–4 COMPLETE**, Phase **5 COMPLETE**, Phase **6 OPERATIONAL** | Roadmap |
| SafeSkill **100/100** (Verified 2026-04-11) | SafeSkill section |
| WhatsApp gateway "Success Verified" | Key capabilities |
| Microsoft Readiness **6/6 READY** | Ecosystem table |

Issue #3 also claims (as path targets, not as PROVEN):

- `…/mmao-mao/README.md`
- `…/identity-provenance.schema.json`

## Path verification (Issue #3 targets)

| Path | Result |
|---|---|
| `governance/kpgs-vnext/agent-governance/mmao-mao/README.md` | **EXISTS** (HTTP 200 raw) |
| `governance/kpgs-vnext/agent-governance/mmao-mao/identity-provenance.schema.json` | **EXISTS** (HTTP 200 raw) |
| Sibling schemas (`authority-boundary`, `failure-receipt`, `validate.py`, fixtures) | **EXISTS** under same folder |

**Verdict on paths:** Issue #3’s stated paths are **not missing**. Path existence ≠ claim endorsement.

## Body read (follow-on, 2026-09-14)

`mmao-mao/README.md` self-status (verbatim posture): **"Canonical contract POC; experiment runs are not yet executed."**

Additional witness notes (not endorsements):

- Folder self-describes as additive governance POC / inspectable contracts — aligns with draft-only binding.
- Structural-maintenance seat table inside that README (Codex CA / Anti-Gravity CF / Cursor LD) is **stale relative to current GSMB MAO** (Forge CA / Cursor CF / Anti-Gravity LD as of 2026-09-11). Treat seat names inside the draft contracts as **historical experiment labels**, not live GSMB law.
- GSMB law remains Schematics MAIN BRAIN (`KPGS_GOVERNANCE_CORE.md`); runtime/docs elsewhere execute, they do not replace.

## Evidence search for PROVEN / COMPLETE

### What exists (partial / non-endorsing)

| Artifact | What it shows | What it does **not** show |
|---|---|---|
| `scripts/demo_day_smoke.py` | Local preflight: GUI dist presence, `.env` presence, optional API/CLI import, agent registry file | No owner endorsement; WARNs allowed; not a semantic proof that Context/Studio/KasiLink are "PROVEN" products |
| `scripts/demo_day_readiness.py`, `demo_day_preflight.ps1`, `demo_day_launch.ps1` | Demo-day tooling present | No archived owner-signed pass receipt attached to README claims |
| `README-safeskill-verified.png` | Image asset exists (HTTP 200) | Image is not an independent third-party audit receipt; no machine-verifiable score ledger found in this pass |
| Live `https://www.kopanolabs.com` / `https://kopanolabs.com` | HTTP 200 (2026-09-14 probe) | Liveness ≠ PROVEN orchestration framework |
| Live `https://www.kasilink.com` / `https://kasilink.com` | HTTP 200 | Liveness ≠ "Full-stack marketplace connectivity PROVEN" |
| Deploy badge on README | Points at Actions workflow `deploy-web.yml` on branch `codex/kc-sovereign-gui-full-dev` | Badge ≠ owner endorsement of Phases 1–6 COMPLETE on `master` |

### What was **not** found (this audit)

| Sought | Result |
|---|---|
| Owner-endorsed receipt that Context/Studio/KasiLink are PROVEN as of 2026-04-11 | **NOT FOUND** on public surfaces audited |
| Test report / CI green proof bound to the exact PROVEN wording | **NOT FOUND** (smoke script is soft WARN-tolerant local check) |
| Independent SafeSkill registry entry / hash-bound 100/100 ledger | **NOT FOUND** beyond README + PNG |
| Dated owner confirmation that Phases 1–6 remain COMPLETE after the KC Delivery Hallucination incident window discussed in session | **NOT FOUND** in this public pass |
| RUNE-style `ENDORSED` decision file inside Introduction-to-MCP for those claims | **NOT FOUND** |

## Claimed vs verified matrix

| Claim | Classification | Notes |
|---|---|---|
| mmao-mao README path exists | **VERIFIED (path)** | Exact Issue #3 path |
| identity-provenance.schema.json exists | **VERIFIED (path)** | Exact Issue #3 path |
| mmao-mao self-status "POC; experiments not executed" | **VERIFIED (body)** | Supports draft-only binding |
| FULL STACK DEMO READY / Verified 2026-04-11 | **SELF_ASSERTED / UNVERIFIED** | README assertion; no owner endorsement receipt found |
| Kopano Context PROVEN | **SELF_ASSERTED / UNVERIFIED** | Same |
| Kopano Studio PROVEN | **SELF_ASSERTED / UNVERIFIED** | Live site ≠ Studio PROVEN |
| KasiLink Bridge PROVEN | **SELF_ASSERTED / UNVERIFIED** | Live site ≠ Bridge PROVEN |
| Phases 1–6 COMPLETE/OPERATIONAL | **SELF_ASSERTED / UNVERIFIED** | Dated 2026-04-11; no post-incident re-endorsement found |
| SafeSkill 100/100 | **PARTIAL / SELF_ASSERTED** | PNG + badge text only |
| WhatsApp "Success Verified" | **SELF_ASSERTED / UNVERIFIED** | No receipt located this pass |
| Microsoft 6/6 READY | **SELF_ASSERTED / UNVERIFIED** | No binding evidence located this pass |
| Owner Action #2 (draft-only reference) | **OWNER-ENDORSED** | Creator chat + GSMB sovereign authority; not a cryptographic endorsement record |

## Doctrine collision (why Phase 4 stays blocked)

RUNE doctrine (Issue #3 + PENDING-001/002/003 pattern): completion/endorsement requires evidence; independence claims are not proof; owner endorsement is explicit.

Cross-linking Introduction-to-MCP governance **as authoritative** while its root README still advertises unendorsed PROVEN/COMPLETE statuses would import **unverified completion claims** into a system whose purpose is to refuse them.

Path validity of `mmao-mao/` does **not** clear that collision. Owner endorsement of **draft-only** reference (#2) does **not** clear that collision either.

## Unresolved limitations of this audit

- GitHub code search API rate-limited / unauthenticated during original pass.
- Did not execute `demo_day_smoke.py` locally.
- No Ed25519-signed `endorsement.schema.json` record for #2 (chat + GSMB sovereign decision recorded in markdown only — PENDING-001 signature scheme remains its own PENDING).

## Must not claim until separately `ENDORSED`

- That Introduction-to-MCP product PROVEN/COMPLETE labels are true.
- That Phase-4 authoritative cross-link is safe.
- That SafeSkill 100/100 is independently verified.
- That this whole PENDING is resolved (only action #2 is owner-endorsed).
- That `independence_claimed=false` draft binding is cryptographic proof of anything.

## Recommended owner actions (updated)

1. Endorse or retract README PROVEN/COMPLETE language with dated receipts — **still open**.
2. Draft-only mmao-mao reference — **done / OWNER-ENDORSED**; see draft reference doc.
3. Only then reopen Phase-4 cross-link work — **still blocked**.

## Implementation evidence (this audit + #2 pass)

- Public fetch of Introduction-to-MCP README (`master`)
- GitHub Contents API listing of `governance/kpgs-vnext/agent-governance/mmao-mao/`
- HTTP 200 on raw mmao-mao README + identity-provenance.schema.json
- Body read of mmao-mao README (POC / experiments not executed)
- HTTP 200 on `scripts/demo_day_smoke.py` (content reviewed: soft local preflight)
- Live HTTP probes: kopanolabs.com / kasilink.com → 200
- GSMB: `KPGS_GOVERNANCE_CORE.md` (Schematics owns law); `MASTER_ROBYN_CORRECTIVE_BASELINE.md` (Robyn Decision = sovereign); Creator chat endorsement of #2
- No modifications made to Introduction-to-MCP by this auditor
