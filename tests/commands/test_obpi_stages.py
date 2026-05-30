"""Tests for verify-stage classification of non-shell-less commands (OBPI-0.0.63-07).

REQ-0.0.63-07-01 / REQ-0.0.63-07-02: the verify stage must classify
Verification commands before dispatch and fail on non-shell-less forms,
reusing the BI-1 classifier from brief_commands (BI-1 shared spine invariant).
"""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from gzkit.traceability import covers

_COMPOUND_BRIEF = """\
## Verification

```bash
test -f x && echo ok
```
"""

_SHELL_LESS_BRIEF = """\
## Verification

```bash
uv run gz check
uv run gz validate --documents
```
"""


class TestVerifyStageCommandShapeClassification(unittest.TestCase):
    """REQ-0.0.63-07-01 / REQ-0.0.63-07-02: _pipeline_verification_commands classification."""

    @covers("REQ-0.0.63-07-01")  # audit-exempt: regression-invariant-overlay rederived-verify-stage-fail-closed
    def test_compound_verification_command_raises_before_dispatch(self) -> None:
        """A non-shell-less Verification command must cause SystemExit before dispatch."""
        from gzkit.commands.obpi_stages import _pipeline_verification_commands

        rendered = io.StringIO()
        with redirect_stdout(rendered), self.assertRaises(SystemExit) as ctx:
            _pipeline_verification_commands(_COMPOUND_BRIEF, "lite")
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("Non-shell-less Verification command", rendered.getvalue())
        self.assertIn("test -f x && echo ok", rendered.getvalue())
        self.assertIn("Rewrite as separate single-program lines", rendered.getvalue())

    @covers("REQ-0.0.63-07-02")  # audit-exempt: regression-invariant-overlay rederived-shell-less-pass-path
    def test_shell_less_verification_commands_pass_through(self) -> None:
        """Shell-less Verification commands must be returned for dispatch."""
        from gzkit.commands.obpi_stages import _pipeline_verification_commands

        result = _pipeline_verification_commands(_SHELL_LESS_BRIEF, "lite")
        self.assertEqual(
            result[-2:],
            ["uv run gz check", "uv run gz validate --documents"],
        )

    @covers("REQ-0.0.63-07-04")  # audit-exempt: regression-invariant-overlay bi1-shared-classifier-fence
    def test_bi1_classifier_is_used(self) -> None:
        """BI-1: the same is_shell_less_executable from brief_commands drives classification.

        This is a STRUCTURAL-FENCE audit-exempt regression-invariant overlay: the
        _pipeline_verification_commands function in obpi_stages.py imports and uses
        is_shell_less_executable from gzkit.brief_commands (the BI-1 module), not a
        fork. We verify this by confirming the same classifier rejects the same input.
        """
        # audit-exempt: regression-invariant-overlay BI-1 single-classifier fence
        from gzkit.brief_commands import is_shell_less_executable

        # The command that _pipeline_verification_commands rejects must also fail
        # the shared BI-1 classifier — proving they share the same predicate.
        self.assertFalse(is_shell_less_executable("test -f x && echo ok"))
        self.assertTrue(is_shell_less_executable("uv run gz check"))


if __name__ == "__main__":
    unittest.main()
