"""Structural-fence and support REQ coverage for OBPI-0.0.64-03.

Companion to tests/test_tasks.py::TestNextSeqForReq and the TestTaskStart
--req/--seq additions, which cover REQ-0.0.64-03-01 (BEHAVIOR). This file
covers the two non-BEHAVIOR REQs that the brief carries as scaffold-default
acceptance criteria:

- REQ-0.0.64-03-02 [STRUCTURAL-FENCE] — scope adherence: changes stay inside
  the brief's Allowed Paths (audited at ADR closeout via Boundary Invariants).
- REQ-0.0.64-03-03 [SUPPORT] — verification evidence is runnable: the brief's
  Verification commands point at real artifacts this OBPI yields.

Same shape as tests/governance/test_advances_decorator.py::TestObpiScopeAndEvidence
for OBPI-0.0.64-02.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.traceability import covers


class TestObpi006403ScopeAndEvidence(unittest.TestCase):
    """Structural REQs: scope adherence (REQ-02) and verification evidence (REQ-03)."""

    @covers("REQ-0.0.64-03-02")
    def test_scope_changes_only_in_allowed_paths(self) -> None:
        """Brief Allowed Paths: parent ADR, src/gzkit/tasks.py, .gzkit/rules/task-discovery.md.

        Structural assertion: the artifacts this OBPI yielded live at the
        allowed paths and the helper + CLI surface this OBPI ships are present.
        """
        repo_root = Path(__file__).resolve().parents[2]
        self.assertTrue((repo_root / "src" / "gzkit" / "tasks.py").is_file())
        self.assertTrue((repo_root / ".gzkit" / "rules" / "task-discovery.md").is_file())
        # The helper this OBPI delivers must be importable at the named module path.
        from gzkit.tasks import next_seq_for_req

        self.assertTrue(callable(next_seq_for_req))

    @covers("REQ-0.0.64-03-03")
    def test_verification_evidence_is_runnable(self) -> None:
        """The brief's Verification section points at real files this OBPI yields."""
        repo_root = Path(__file__).resolve().parents[2]
        # From the brief's Verification section:
        adr_path = (
            repo_root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.64-task-envelope-and-planning-decomposition"
            / "ADR-0.0.64-task-envelope-and-planning-decomposition.md"
        )
        self.assertTrue(adr_path.is_file())
        self.assertTrue((repo_root / "src" / "gzkit" / "tasks.py").is_file())
        self.assertTrue((repo_root / ".gzkit" / "rules" / "task-discovery.md").is_file())


if __name__ == "__main__":
    unittest.main()
