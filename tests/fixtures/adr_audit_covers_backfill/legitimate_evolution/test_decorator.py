"""Synthetic test file for the legitimate-evolution fixture (do not collect).

The `@covers` decorator at line 7 is the heuristic's input — its introducing
commit + commit date are declared in `git_history.json` for the BDD scenario
to feed into the mocked `git_runner`. This file is NOT a real test target.
"""


# @covers REQ-0.99.0-01-01
def synthetic_test_for_fixture() -> None:
    """Marker function — never executed; pinned to line 7 by the fixture."""
    return None
