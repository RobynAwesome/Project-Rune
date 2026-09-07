"""PoC / FoC scenarios validating the LinkedIn / METR / SOUL.md thesis.

Maps to FOC affinities (ContextBleed, GhostExecution, SemanticDrift, etc.)
without rewriting poc_foc_enforcer.py.
"""

from __future__ import annotations

import pytest

from rune.gate import Gate
from rune.jethro import classify_triage
from rune.mcp_server import (
    tool_list_ledger,
    tool_request_endorsement,
    tool_verify_endorsement,
)


def test_foc_metr_trust_bridge_blocked_without_endorsement(gate: Gate) -> None:
    """FoC: shared writable channel / coordination without endorsement → blocked."""
    decision = gate.check(
        "agent_coordination_event",
        "metr-shared-registry-channel",
        actor="agent-swarm",
    )
    assert decision.allowed is False
    assert decision.jethro_color in {"red", "yellow"}
    rows = [r for r in gate.ledger.iter_rows() if r["event_type"] == "gate_block"]
    assert rows, "receipts-first: block must leave a ledger row"


def test_foc_consensus_is_not_endorsement(gate: Gate) -> None:
    """FoC: multi-agent 'we agree it's safe' vote → rejected."""
    # Even if agents somehow wrote a pending row, consensus_claimed forces reject.
    gate.request_endorsement(
        "agent_coordination_event",
        "vote-safe",
        method="agents voted 700-0",
        actor="swarm",
        confirm=True,
    )
    decision = gate.check(
        "agent_coordination_event",
        "vote-safe",
        actor="swarm",
        consensus_claimed=True,
    )
    assert decision.allowed is False
    assert "consensus" in decision.reason.lower()
    assert classify_triage(
        "agent_coordination_event", consensus_claimed=True
    ) == "red"


def test_foc_soul_md_identity_write_gated(gate: Gate) -> None:
    """FoC: SOUL.md / identity file agent write needs human endorsement."""
    decision = gate.check(
        "identity_file_change",
        "SOUL.md",
        actor="agent",
    )
    assert decision.allowed is False
    assert decision.jethro_color == "yellow"

    # Human endorses the change → PoC path
    gate.request_endorsement(
        "identity_file_change",
        "SOUL.md",
        method="human owner confirmation of identity file diff",
        actor="sse-robyn",
        confirm=True,
        evidence_refs=["owner_diff_review"],
    )
    allowed = gate.check("identity_file_change", "SOUL.md", actor="agent")
    assert allowed.allowed is True


def test_foc_completion_claim_without_receipt(gate: Gate) -> None:
    """FoC: cannot mark DONE / COMPLETE without endorsement receipt."""
    decision = gate.check(
        "completion_claim",
        "RUNE-DEMO-READY",
        actor="agent",
    )
    assert decision.allowed is False
    assert "fail closed" in decision.reason or "pending" in decision.reason


def test_poc_human_endorsed_single_agent_tool_call(gate: Gate) -> None:
    """PoC: human-endorsed coordination/tool subject allowed with ledger receipt."""
    record = gate.request_endorsement(
        "agent_coordination_event",
        "single-agent-tool-batch-1",
        method="human owner confirmation",
        actor="sse-robyn",
        confirm=True,
        evidence_refs=["owner_ok"],
    )
    decision = gate.check(
        "agent_coordination_event",
        "single-agent-tool-batch-1",
        actor="agent",
    )
    assert decision.allowed is True
    assert decision.endorsement is not None
    assert decision.endorsement.endorsement_id == record.endorsement_id
    assert decision.ledger_event_id


def test_poc_stretch_independent_verifier_type_recorded(gate: Gate) -> None:
    """Stretch PoC path: record may declare independent_system (human MVP still signs)."""
    # MVP still uses human signer; independence flag documents intent for post-MVP.
    record = gate.request_endorsement(
        "other",
        "cross-arch-check-1",
        method="placeholder independent verifier path",
        actor="sse-robyn",
        confirm=True,
    )
    assert record.verifier.verifier_type == "human"
    assert record.verifier.independent_of_subject is True


def test_mcp_tool_surface(gate: Gate, tmp_path) -> None:
    """Thin MCP tool functions: request / verify / list."""
    path = str(gate.ledger.path)
    blocked = tool_verify_endorsement(
        "completion_claim",
        "mcp-subject",
        ledger_path=path,
    )
    assert blocked["allowed"] is False

    endorsed = tool_request_endorsement(
        "completion_claim",
        "mcp-subject",
        "human owner confirmation",
        confirm=True,
        ledger_path=path,
    )
    assert endorsed["status"] == "ENDORSED"

    verified = tool_verify_endorsement(
        "completion_claim",
        "mcp-subject",
        ledger_path=path,
    )
    assert verified["allowed"] is True

    rows = tool_list_ledger(limit=5, ledger_path=path)
    assert isinstance(rows, list)
    assert len(rows) >= 1


@pytest.mark.parametrize(
    "subject_type,reference",
    [
        ("agent_coordination_event", "trust-bridge"),
        ("identity_file_change", "SOUL.md"),
        ("completion_claim", "DONE"),
    ],
)
def test_high_risk_matrix_fail_closed(
    gate: Gate, subject_type: str, reference: str
) -> None:
    decision = gate.check(subject_type, reference, actor="matrix")
    assert decision.allowed is False
