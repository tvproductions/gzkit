"""Behavior tests for advisory-line rendering in the `gz check` aggregator (GHI #713).

`gz check` rendered a step's captured output only on the failure branch, so a
step that ran green but had something advisory to say was silenced. That is the
symmetric hole to the one the failure branch was authored to close ("a gate that
hides its own failure reason is undiagnosable from a CI log"): a gate that hides
its own *advisory* reasoning is equally undiagnosable, and the codebase forces
non-gating findings onto that channel — `ValidationError` carries no severity
field, so an audit that must not change the exit code has no other way to speak.

The advisory channel is a declared marker rather than "whatever a passing step
wrote to stderr", because ordinary chatter shares that stream: `unittest` writes
its entire summary there, and surfacing it would bury the signal it was meant to
carry.
"""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from gzkit.advisory import ADVISORY_MARKER, advisory_lines, emit_advisory
from gzkit.commands.quality import _render_step_advisories
from gzkit.quality import QualityResult


def _result(
    *,
    success: bool,
    stdout: str = "",
    stderr: str = "",
    command: str = "uv run gz validate --x",
) -> QualityResult:
    return QualityResult(
        success=success,
        command=command,
        stdout=stdout,
        stderr=stderr,
        returncode=0,
    )


class AdvisoryChannelIsMarked(unittest.TestCase):
    """The marker is what separates an advisory from ordinary stream chatter."""

    def test_emitted_advisory_is_recoverable_from_the_captured_stream(self) -> None:
        buffer = io.StringIO()
        with redirect_stderr(buffer):
            emit_advisory("scenario-reachability: orphan bullet 'x'")
        self.assertEqual(
            advisory_lines(buffer.getvalue()),
            [f"{ADVISORY_MARKER} scenario-reachability: orphan bullet 'x'"],
        )

    def test_unmarked_chatter_is_not_an_advisory(self) -> None:
        """`unittest` writes its summary to stderr; that must not surface."""
        noisy = "....\n----------------\nRan 7410 tests in 71.9s\n\nOK\n"
        self.assertEqual(advisory_lines(noisy), [])

    def test_advisories_are_collected_from_both_streams(self) -> None:
        """Emitters differ: some notices go to stdout, warnings to stderr."""
        found = advisory_lines(f"{ADVISORY_MARKER} on stdout", f"{ADVISORY_MARKER} on stderr")
        self.assertEqual(len(found), 2)


class PassingStepsStillSpeak(unittest.TestCase):
    """The defect: a green step's advisory prose was discarded."""

    def test_advisory_from_a_passing_step_is_rendered(self) -> None:
        results = [
            (
                "Instructions files budget",
                _result(success=True, stderr=f"{ADVISORY_MARKER} AGENTS.md: 560 B of headroom"),
            )
        ]
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            _render_step_advisories(results)
        output = buffer.getvalue()
        self.assertIn("560 B of headroom", output)
        self.assertIn("Instructions files budget", output, "the advisory must name its step")

    def test_ordinary_passing_output_is_not_rendered(self) -> None:
        """Only marked lines surface — a green step's normal output stays quiet."""
        results = [("Unit tests", _result(success=True, stderr="Ran 7410 tests\n\nOK\n"))]
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            _render_step_advisories(results)
        self.assertEqual(buffer.getvalue(), "")

    def test_simulated_findings_from_the_test_step_are_not_attributed(self) -> None:
        """Test fixtures exercise the emitters, so the suite's own stderr carries
        advisory-marked lines. Those are claims about temp directories — surfacing
        them would report 28 simulated findings as findings about this repository.
        """
        results = [
            (
                "Test",
                _result(
                    success=True,
                    stderr=f"{ADVISORY_MARKER} fixture finding about /tmp/xyz",
                    command="uv run -m unittest -q",
                ),
            )
        ]
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            _render_step_advisories(results)
        self.assertEqual(buffer.getvalue(), "")

    def test_rendered_prose_survives_rich_markup_interpretation(self) -> None:
        """Advisory prose is audit text, not markup — bracketed content must survive.

        The marker itself is bracketed, and findings quote arbitrary content
        (rule names, section ids, file paths). Rendering any of that as Rich
        markup silently drops it, which is the same class of loss this issue
        was filed about.
        """
        finding = "orphan bullet: [not-a-style] must not vanish"
        results = [
            ("Surface fidelity", _result(success=True, stderr=f"{ADVISORY_MARKER} {finding}"))
        ]
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            _render_step_advisories(results)
        output = buffer.getvalue()
        self.assertIn("[not-a-style]", output, "bracketed prose must not be eaten as markup")
        self.assertNotIn(ADVISORY_MARKER, output, "the marker is plumbing, not operator prose")

    def test_failing_step_advisories_are_not_duplicated(self) -> None:
        """A failing step already dumps its full output; re-printing would double it."""
        results = [
            ("Broken", _result(success=False, stderr=f"{ADVISORY_MARKER} something advisory"))
        ]
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            _render_step_advisories(results)
        self.assertEqual(buffer.getvalue(), "")


class EmittersReachTheRenderer(unittest.TestCase):
    """End-to-end contract: what the audits emit is what the renderer recognizes.

    This is the regression guard that matters. Each audit having its own ad-hoc
    prefix is how the channel silently broke in the first place, so the test
    runs a real emitter rather than a hand-written fixture line.
    """

    def test_surface_delivery_witness_output_is_recognized_as_advisory(self) -> None:
        from pathlib import Path

        from gzkit.governance.trust_audits.surface_delivery_witness import (
            audit_surface_delivery_witness,
        )

        project_root = Path(__file__).resolve().parents[2]
        buffer = io.StringIO()
        with redirect_stderr(buffer):
            audit_surface_delivery_witness(project_root)
        self.assertTrue(
            advisory_lines(buffer.getvalue()),
            "the delivery witness must emit through the advisory channel",
        )


if __name__ == "__main__":
    unittest.main()
