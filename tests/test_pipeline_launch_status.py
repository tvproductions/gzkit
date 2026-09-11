"""Launching a pipeline advances its brief out of Draft (GHI #992).

Layer-2 gets `pipeline_launched` at Stage 1. Before this fix Layer-1 kept
saying `Draft` until someone ran `gz frontmatter reconcile` by hand, so every
launched-and-not-completed OBPI failed `gz validate --frontmatter` and blocked
every push for the whole in-flight window. Operator ruling 2026-09-11: "if we
start work on a obpi with draft status, its not draft."

The mandatory catch that DID exist is `gz obpi precomplete`'s
`_check_reconcile_idempotent`, which is self-described "Reactive triage at
Stage 5" — the opposite end of the pipeline from where the drift is created.
"""

import inspect
import tempfile
import unittest
from pathlib import Path

from gzkit.commands import obpi_cmd
from gzkit.commands.obpi_cmd import _advance_brief_status_on_launch


def _write_brief(tmp: Path, status: str) -> Path:
    brief = tmp / "OBPI-test-brief.md"
    brief.write_text(
        f"---\nid: OBPI-test\nparent: ADR-test\nstatus: {status}\n---\n\n# Test\n",
        encoding="utf-8",
    )
    return brief


class AdvanceBriefStatusOnLaunchTest(unittest.TestCase):
    """The launch-time Layer-1 advance, in its own right."""

    def test_draft_brief_becomes_active(self):
        """A launched brief must not keep asserting Draft while work proceeds."""
        with tempfile.TemporaryDirectory() as tmp:
            brief = _write_brief(Path(tmp), "Draft")

            wrote = _advance_brief_status_on_launch(brief)

            self.assertTrue(wrote, "launch must advance a Draft brief")
            self.assertIn("status: Active", brief.read_text(encoding="utf-8"))

    def test_already_active_brief_is_a_noop(self):
        """Re-launch is idempotent — no rewrite, no spurious dirty tree."""
        with tempfile.TemporaryDirectory() as tmp:
            brief = _write_brief(Path(tmp), "Active")
            before = brief.read_text(encoding="utf-8")

            wrote = _advance_brief_status_on_launch(brief)

            self.assertFalse(wrote, "an already-Active brief must not be rewritten")
            self.assertEqual(before, brief.read_text(encoding="utf-8"))

    def test_terminal_status_is_never_clobbered(self):
        """The GHI #348/#668 clobber class stays refused.

        This is the control that keeps the fix honest: advancing on launch must
        not become a licence to write `status:` over a terminal state. The
        verdict belongs to `obpi_status_write_refusal`, so this asserts the
        helper routes through it rather than writing on its own authority.
        """
        with tempfile.TemporaryDirectory() as tmp:
            brief = _write_brief(Path(tmp), "Abandoned")
            before = brief.read_text(encoding="utf-8")

            wrote = _advance_brief_status_on_launch(brief)

            self.assertFalse(wrote, "a terminal brief must not be advanced")
            self.assertEqual(before, brief.read_text(encoding="utf-8"))


class LaunchWiringTest(unittest.TestCase):
    """The advance must be reached from the launch transaction itself.

    Same shape as `tests/test_airlock_enter.py`'s wiring assertion: the helper
    is extracted so `obpi_pipeline_cmd` stays under the complexity ceiling, and
    that extraction is exactly what lets the call be silently dropped. A
    semantic test of the helper cannot see that; this can.
    """

    def test_launch_advances_the_brief_status(self):
        source = inspect.getsource(obpi_cmd.obpi_pipeline_cmd)
        self.assertIn(
            "_advance_brief_status_on_launch(",
            source,
            "obpi_pipeline_cmd must advance the brief's Layer-1 status at launch",
        )

    def test_advance_follows_the_ledger_event(self):
        """Layer-2 first, then Layer-1 — the flip witnesses a launch that happened."""
        source = inspect.getsource(obpi_cmd.obpi_pipeline_cmd)
        self.assertLess(
            source.index("pipeline_launched_event("),
            source.index("_advance_brief_status_on_launch("),
            "Layer-1 must be advanced after the pipeline_launched event is appended",
        )


if __name__ == "__main__":
    unittest.main()
