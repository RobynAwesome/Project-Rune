"""Thin MCP tools: request_endorsement, verify_endorsement, list_ledger.

Requires optional dependency: pip install -e ".[mcp]"
Falls back to a clear error if the mcp package is unavailable.
"""

from __future__ import annotations

import json
from typing import Any


def _gate(ledger_path: str | None = None):
    from rune.gate import Gate
    from rune.ledger import EndorsementLedger

    return Gate(EndorsementLedger(ledger_path))


def tool_request_endorsement(
    subject_type: str,
    reference: str,
    method: str,
    *,
    confirm: bool = False,
    reject: bool = False,
    evidence_refs: list[str] | None = None,
    actor: str = "mcp",
    ledger_path: str | None = None,
) -> dict[str, Any]:
    gate = _gate(ledger_path)
    record = gate.request_endorsement(
        subject_type,
        reference,
        method=method,
        actor=actor,
        evidence_refs=evidence_refs,
        confirm=confirm,
        reject=reject,
    )
    return record.to_dict()


def tool_verify_endorsement(
    subject_type: str,
    reference: str,
    *,
    consensus_claimed: bool = False,
    actor: str = "mcp",
    ledger_path: str | None = None,
) -> dict[str, Any]:
    gate = _gate(ledger_path)
    decision = gate.check(
        subject_type,
        reference,
        actor=actor,
        consensus_claimed=consensus_claimed,
    )
    return decision.to_dict()


def tool_list_ledger(
    *,
    limit: int = 20,
    ledger_path: str | None = None,
) -> list[dict[str, Any]]:
    from rune.ledger import EndorsementLedger

    return EndorsementLedger(ledger_path).list_rows(limit=limit)


def run_mcp(*, ledger_path: str | None = None) -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - optional dep
        raise SystemExit(
            "mcp package not installed. Run: pip install -e \".[mcp]\""
        ) from exc

    mcp = FastMCP("project-rune")

    @mcp.tool()
    def request_endorsement(
        subject_type: str,
        reference: str,
        method: str,
        confirm: bool = False,
        reject: bool = False,
        evidence_refs: list[str] | None = None,
        actor: str = "mcp",
    ) -> str:
        """Request or confirm an endorsement (human verifier bootstrap assumed)."""
        result = tool_request_endorsement(
            subject_type,
            reference,
            method,
            confirm=confirm,
            reject=reject,
            evidence_refs=evidence_refs,
            actor=actor,
            ledger_path=ledger_path,
        )
        return json.dumps(result, indent=2)

    @mcp.tool()
    def verify_endorsement(
        subject_type: str,
        reference: str,
        consensus_claimed: bool = False,
        actor: str = "mcp",
    ) -> str:
        """Fail-closed gate check for a subject; returns allow/block + receipt ids."""
        result = tool_verify_endorsement(
            subject_type,
            reference,
            consensus_claimed=consensus_claimed,
            actor=actor,
            ledger_path=ledger_path,
        )
        return json.dumps(result, indent=2)

    @mcp.tool()
    def list_ledger(limit: int = 20) -> str:
        """List recent append-only ledger rows (receipts-first)."""
        result = tool_list_ledger(limit=limit, ledger_path=ledger_path)
        return json.dumps(result, indent=2)

    mcp.run()
