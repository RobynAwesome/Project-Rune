"""Jethro Green / Yellow / Red triage hooks for RUNE subjects."""

from __future__ import annotations

from typing import Literal

from rune import HIGH_RISK_SUBJECT_TYPES

TriageColor = Literal["green", "yellow", "red"]


def classify_triage(
    subject_type: str,
    *,
    consensus_claimed: bool = False,
    has_endorsement: bool = False,
    surprise_channel: bool = False,
    evidence_complete: bool = True,
) -> TriageColor:
    """Map subject context to Jethro color.

    Green — routine endorse path
    Yellow — human review / PENDING
    Red — block + FoC
    """
    if consensus_claimed:
        return "red"
    if surprise_channel:
        return "red"
    if subject_type == "agent_coordination_event" and not has_endorsement:
        return "red" if surprise_channel else "yellow"
    if subject_type == "identity_file_change":
        return "yellow" if evidence_complete else "red"
    if subject_type == "completion_claim":
        return "yellow" if not has_endorsement else "green"
    if subject_type in HIGH_RISK_SUBJECT_TYPES and not has_endorsement:
        return "yellow"
    if has_endorsement:
        return "green"
    return "green" if subject_type == "other" else "yellow"


def triage_action(color: TriageColor) -> str:
    return {
        "green": "routine endorse after lightweight human confirm",
        "yellow": "hold PENDING; human review required",
        "red": "block; reject or refuse; open FoC incident",
    }[color]
