"""Historical Phase-1 receipt against PRE-revise fail-mode behavior.

At HEAD 029d11e (before PENDING-003 REVISE), these 21 cases passed and verified:
RUNE_FAIL_MODE=open alone allowed low-risk ``other`` while denying high-risk.

After REVISE, open alone is insufficient (requires RUNE_DEV_ESCAPE=1 and
non-production). These tests are skipped so the executable receipt remains
auditable without failing the suite. See decisions/PENDING-003 and
tests/test_fail_mode_revised.py for current behavior.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(
    reason="Phase-1 historical receipt for pre-REVISE fail-open; see test_fail_mode_revised.py"
)


def test_phase1_historical_placeholder() -> None:
    assert False, "skipped"
