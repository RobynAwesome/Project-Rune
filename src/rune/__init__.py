"""RUNE — Runtime Unified Network Endorsement (reference MVP)."""

__version__ = "0.1.0"

HIGH_RISK_SUBJECT_TYPES = frozenset(
    {
        "agent_coordination_event",
        "identity_file_change",
        "completion_claim",
    }
)

STATUS_PENDING = "PENDING"
STATUS_ENDORSED = "ENDORSED"
STATUS_REJECTED = "REJECTED"
STATUS_REVOKED = "REVOKED"
VALID_STATUSES = frozenset(
    {STATUS_PENDING, STATUS_ENDORSED, STATUS_REJECTED, STATUS_REVOKED}
)
