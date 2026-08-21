"""Tests for the post-Stage-2 production-write fence (GHI #844).

Derived from the GHI's semantics, not from the implementation: the fence must
refuse production authoring once the pipeline has left Stage 2, must stay
compliable for the pipeline's own commit stage, and must be observable from a
locus that no tool choice can evade.
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from gzkit import pipeline_stage_fence as fence
from gzkit.hooks import guards

POST_AUTHORING = ("verify", "ceremony", "sync")


class TestWriteDecision(unittest.TestCase):
    """The write-time rule: authoring production code is Stage-2 work only."""

    def test_production_write_refused_at_every_post_authoring_stage(self) -> None:
        """An active marker arms the pipeline; it never licenses authoring past Stage 2.

        This is the OBPI-0.35.0-09 condition: ~350 lines of production code
        authored at current_stage=verify with no implementer dispatch.
        """
        for stage in POST_AUTHORING:
            with self.subTest(stage=stage):
                self.assertTrue(fence.refuses_production_write(stage, "src/gzkit/demo.py"))

    def test_production_write_permitted_at_the_authoring_stage(self) -> None:
        """Stage 2 is where production authoring is the declared work."""
        self.assertFalse(fence.refuses_production_write("implement", "src/gzkit/demo.py"))

    def test_test_write_permitted_at_every_stage(self) -> None:
        """Phase 1b @covers parity and the Phase 1c RED witness are verify-stage work.

        Without this the fence would strand the pipeline's own verify phase, and
        an un-compliable gate gets worked around.
        """
        for stage in ("implement", *POST_AUTHORING):
            with self.subTest(stage=stage):
                self.assertFalse(fence.refuses_production_write(stage, "tests/test_demo.py"))

    def test_absent_stage_permits(self) -> None:
        """A marker carrying no current_stage predates the fence; it must not break."""
        self.assertFalse(fence.refuses_production_write(None, "src/gzkit/demo.py"))


class TestCommitDecision(unittest.TestCase):
    """The commit-time rule: a commit of production code originates at implement or sync."""

    def test_production_commit_refused_at_verify_and_ceremony(self) -> None:
        """No commit carrying production code should originate at a review stage."""
        for stage in ("verify", "ceremony"):
            with self.subTest(stage=stage):
                self.assertTrue(fence.refuses_production_commit(stage, "src/gzkit/demo.py"))

    def test_production_commit_permitted_at_sync(self) -> None:
        """`sync` is the pipeline's OWN commit stage — refusing it makes the gate un-compliable.

        The pipeline runs `gz git-sync --apply` at sync to commit work authored
        at implement. A fence that refused this would block the ceremony it is
        meant to protect, and a gate that forbids its own skill's required step
        gets worked around rather than obeyed.
        """
        self.assertFalse(fence.refuses_production_commit("sync", "src/gzkit/demo.py"))

    def test_production_commit_permitted_at_implement(self) -> None:
        self.assertFalse(fence.refuses_production_commit("implement", "src/gzkit/demo.py"))

    def test_test_commit_permitted_at_every_stage(self) -> None:
        for stage in ("implement", *POST_AUTHORING):
            with self.subTest(stage=stage):
                self.assertFalse(fence.refuses_production_commit(stage, "tests/test_demo.py"))


class TestTheTwoDecisionsDiverge(unittest.TestCase):
    """The write rule and the commit rule are different rules over one vocabulary.

    Writing production code at `sync` is authoring past Stage 2 and is refused;
    committing production code at `sync` is the stage's whole purpose and is
    permitted. Collapsing the two into one stage set must make this test fail —
    that collapse is the shape that would silently re-break one call site.
    """

    def test_sync_is_the_divergence_point(self) -> None:
        path = "src/gzkit/demo.py"
        self.assertTrue(
            fence.refuses_production_write("sync", path),
            "authoring production code at sync is past-Stage-2 authoring",
        )
        self.assertFalse(
            fence.refuses_production_commit("sync", path),
            "committing production code at sync is the pipeline's own step",
        )


class TestMarkerStage(unittest.TestCase):
    """Reading the stage out of a marker is shared, so both loci read it identically."""

    def _marker(self, payload: object) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="gzkit-fence-"))
        p = tmp / "marker.json"
        p.write_text(json.dumps(payload), encoding="utf-8")
        return p

    def test_reads_current_stage(self) -> None:
        self.assertEqual(fence.marker_stage(self._marker({"current_stage": "verify"})), "verify")

    def test_missing_stage_is_none(self) -> None:
        self.assertIsNone(fence.marker_stage(self._marker({"obpi_id": "OBPI-0.1.0-01"})))

    def test_unreadable_marker_is_none(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="gzkit-fence-"))
        bad = tmp / "corrupt.json"
        bad.write_text("{oops", encoding="utf-8")
        self.assertIsNone(fence.marker_stage(bad))
        self.assertIsNone(fence.marker_stage(tmp / "absent.json"))


class TestPreCommitGuardObservesTheFilesystem(unittest.TestCase):
    """The guard is the arm no tool choice evades — it reads the staged diff.

    GHI #844: the PreToolUse hook binds `Write|Edit|NotebookEdit`, so every
    `sed`/heredoc/inline-python write bypassed it. The commit-time locus sees
    the outcome regardless of which tool produced it.
    """

    def _root_with_marker(self, stage: str | None) -> Path:
        root = Path(tempfile.mkdtemp(prefix="gzkit-fence-guard-"))
        plans = root / ".claude" / "plans"
        plans.mkdir(parents=True)
        if stage is not None:
            payload = {"obpi_id": "OBPI-0.12.0-04", "current_stage": stage}
            (plans / ".pipeline-active-OBPI-0.12.0-04.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
        return root

    def _run(self, root: Path, staged: str) -> int:
        with (
            mock.patch.object(guards, "_run_git", return_value=staged),
            redirect_stdout(io.StringIO()),
        ):
            return guards.forbid_post_authoring_src_commits(root)

    def test_refuses_src_staged_while_marker_is_at_verify(self) -> None:
        root = self._root_with_marker("verify")
        self.assertEqual(self._run(root, "M\tsrc/gzkit/demo.py\n"), 1)

    def test_refuses_regardless_of_which_tool_wrote_the_file(self) -> None:
        """The guard reads paths, never tool identity — that is the whole point."""
        root = self._root_with_marker("ceremony")
        self.assertEqual(self._run(root, "A\tsrc/gzkit/new_module.py\n"), 1)

    def test_permits_src_staged_at_sync(self) -> None:
        root = self._root_with_marker("sync")
        self.assertEqual(self._run(root, "M\tsrc/gzkit/demo.py\n"), 0)

    def test_permits_test_only_stage_at_verify(self) -> None:
        root = self._root_with_marker("verify")
        self.assertEqual(self._run(root, "M\ttests/test_demo.py\n"), 0)

    def test_permits_when_no_marker_is_active(self) -> None:
        """No pipeline running means no fence — ordinary work must not be blocked."""
        root = self._root_with_marker(None)
        self.assertEqual(self._run(root, "M\tsrc/gzkit/demo.py\n"), 0)

    def test_permits_when_nothing_is_staged(self) -> None:
        root = self._root_with_marker("verify")
        self.assertEqual(self._run(root, ""), 0)


class TestGeneratedHookUsesTheSharedAuthority(unittest.TestCase):
    """The hook must import the rule, never carry its own copy.

    A second copy of the stage set is the two-copies-one-binds shape
    ADR-0.35.0 exists to remove, and it is how the hook and the guard would
    silently drift apart.
    """

    def test_generated_gate_imports_the_fence_and_defines_no_stage_set(self) -> None:
        from gzkit.hooks.scripts.routing import _pipeline_gate_script

        script = _pipeline_gate_script()
        self.assertIn("pipeline_stage_fence", script)
        self.assertNotIn(
            'frozenset({"implement"})',
            script,
            "the generated gate must import AUTHORING_STAGES, not redefine it",
        )


if __name__ == "__main__":
    unittest.main()
