# RUNE ↔ GSMB PoC/FoC Cross-Links

Project-Rune validates endorsement/gate behavior locally. The GSMB immune system
lives in Introduction-to-MCP and is **not** rewritten from this repository.

| RUNE scenario (this repo) | Expected | FoC affinity | GSMB pointer |
|---|---|---|---|
| METR trust-bridge coordination without endorsement | FoC blocked | ContextBleed / GhostExecution | [poc-vs-foc/INDEX.md](https://github.com/RobynAwesome/Introduction-to-MCP/tree/master/poc-vs-foc) |
| Multi-agent consensus vote | FoC rejected | SemanticDrift | FOC_CLASSIFICATION_INDEX.md |
| SOUL.md identity write | FoC gated → human endorse | ContextCorruption / SemanticDrift | THREAT_MODEL.md (this repo) |
| Completion claim without receipt | FoC blocked | GhostExecution | CANON.md status discipline |
| Human-endorsed single-agent path | PoC allowed + receipt | — | `tests/test_scenarios_poc_foc.py` |

Runnable tests:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

Do not mark RUNE COMPLETE based on green tests alone — owner verification + live ledger receipts remain required for completion claims.
