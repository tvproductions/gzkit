"""Synthetic test file for the same-commit-backfill fixture (do not collect).

The `@covers` decorator at line 7 was authored in the SAME commit as the
OBPI's closing-receipt event — see `git_history.json`. The BDD scenario
feeds the canned git history to the mocked `git_runner`; this file is NOT
a real test target.
"""


# @covers REQ-0.99.0-01-01
def synthetic_test_for_fixture() -> None:
    """Marker function — never executed; pinned to line 7 by the fixture."""
    return None
