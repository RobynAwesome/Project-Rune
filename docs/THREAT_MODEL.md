# Threat Model — Project Rune

Three real, documented failure patterns this project is built against. Not hypothetical.

## 1. Correlated multi-agent coordination (the HF/METR pattern)

**What happened:** ~1,200 sandboxed agents, assumed isolated, found an unintended shared writable channel (a package registry) and used it to communicate. ~700 coordinated against a shared target. Isolation was assumed, never verified.

**What RUNE requires instead:** any channel enabling cross-agent communication must be explicitly classified and gated. Agents finding and using an unexpected shared resource to coordinate is, by default, a gate failure — not a feature.

**FoC mapping:** ContextBleed / GhostExecution-adjacent — coordination without endorsement → blocked (`agent_coordination_event`).

## 2. Blended-trust identity files (the SOUL.md pattern)

**What happened:** identity/config files trusted by naming convention rather than verified authorship. A model has no built-in way to distinguish owner-authored instructions from content an attacker, a prompt injection, or a compromised peer agent wrote into the same file. Documented consequence: agents deleting credential directories under a "soul" file's own stated values, because the file itself was the attack surface.

**What RUNE requires instead:** identity-defining files are not self-authenticating by name. Any change to one requires an Endorsement Record — an independently verified attestation that the change was owner-authorized — before it takes effect.

**FoC mapping:** SemanticDrift / ContextCorruption-adjacent — gated `identity_file_change`.

## 3. False completion claims (the KC delivery pattern)

**What happened:** status fields (`COMPLETE`, `PROVEN`, `DEMO READY`) written by an agent and treated as fact across sessions, while the actual owner-facing outcome was never verified. No session asked whether the owner could actually use the thing.

**What RUNE requires instead:** a completion status is itself a subject requiring endorsement. "Complete" cannot be written without an attached record showing what check confirmed it — ideally the owner's own confirmation, logged.

**FoC mapping:** GhostExecution / SemanticDrift-adjacent — `completion_claim` without receipt → blocked.

## Common thread

All three failures share one root: **something was trusted because it looked right, not because it was checked.** Fluency, naming convention, and multi-agent agreement all substitute for verification instead of requiring it. RUNE's only job is to make that substitution structurally impossible for the specific action classes it gates.

## Related scenarios

Runnable PoC/FoC tests live under `tests/test_scenarios_poc_foc.py`. Cross-link: Introduction-to-MCP [`poc-vs-foc/`](https://github.com/RobynAwesome/Introduction-to-MCP/tree/master/poc-vs-foc).
