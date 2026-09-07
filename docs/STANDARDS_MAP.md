# Standards Map — MCP, MHS, and RUNE

Industry alignment for the governance-layer product. RUNE does not replace MCP or MHS; it fills the missing coordination/identity endorsement layer.

## Protocol stack

```
MCP  — agent ↔ software tools
MHS  — agent ↔ physical devices (Anthropic research preview, Aug 2026)
RUNE — agent ↔ agent coordination and identity claims (endorsement, not consensus)
```

| Layer | What it standardizes | Safety locus |
|---|---|---|
| **MCP** | Tool invocation, resources, prompts | Client/host policy + tool sandboxing |
| **MHS** | Device access for agents | Driver / protocol safety |
| **RUNE** | Whether coordination or identity claims may proceed | Independent verifier + append-only ledger + fail-closed gate |

## Why RUNE sits beside, not inside, MCP

MCP gives agents a shared language for tools. MHS expects harnesses to speak device protocols safely. Neither answers: *did an independent party check that multi-agent coordination or an identity-file mutation is authorized?*

RUNE answers that question with:

1. Classification of high-risk subjects
2. Human (MVP) or independent-system endorsement
3. Receipts in an append-only ledger
4. A gate that fails closed without a valid `ENDORSED` record

## Thin MCP surface (this repo)

After the ledger/gate MVP, RUNE exposes MCP tools so harnesses can speak the same protocol language:

| Tool | Purpose |
|---|---|
| `request_endorsement` | Create `PENDING` (or immediate human-confirmed) endorsement request |
| `verify_endorsement` | Check subject against ledger / signature |
| `list_ledger` | List recent ledger rows (receipts-first) |

See `src/rune/mcp_server.py` and `python -m rune mcp`.

## Non-claims

- No claimed MHS partnership or open-source equivalence.
- No claim that MCP hosts must embed RUNE — integration is optional and harness-driven.
- No COMPLETE / DEMO READY status for RUNE itself without owner + ledger receipt.
