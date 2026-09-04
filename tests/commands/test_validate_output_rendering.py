"""Rendering tests for `gz validate` operator output (GHI #944).

Rich parses `[...]` in a printed string as console markup and consumes any
bracket whose content begins with `[a-z#/@]`. Every `ValidationError.type` in
this project is lowercase snake_case, so the interpolated type was silently
deleted from every failing `gz validate` run — the operator saw
`   →  path/to/artifact` where the format string plainly intends
`   → [ownership_declaration] path/to/artifact`.

The type is the operator's only handle on *which* validator scope refused, and
`exit 1` vs `exit 3` routing through `_POLICY_BREACH_ERROR_TYPES` is keyed on
it. These tests assert that semantic — the scope name is legible in rendered
output — not the escape mechanism that delivers it.

`tests/policy/test_rich_markup_escaping.py` ratchets the same class across
every Rich-rendered call site; this file pins the operator-visible behavior at
the site where the defect was observed.
"""

from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from rich.console import Console

from gzkit.validate import ValidationError


class TestErrorTypeSurvivesRichMarkup(unittest.TestCase):
    """The bracketed error type must reach the operator's terminal (GHI #944).

    Rich parses ``[...]`` as console markup and consumes any bracket whose
    content begins with ``[a-z#/@]``. Every ``ValidationError.type`` in this
    project is lowercase snake_case, so the interpolated type was silently
    dropped from every failing ``gz validate`` run. The type is the operator's
    only handle on *which* validator scope refused, and ``exit 1`` vs ``exit 3``
    routing through ``_POLICY_BREACH_ERROR_TYPES`` is keyed on it.

    These tests assert the semantic — the scope name is legible in the rendered
    output — not the escape mechanism that delivers it.
    """

    @staticmethod
    def _render(errors: list[ValidationError], scopes: list[str]) -> str:
        """Render ``_print_validation_result`` through a captured Rich console."""

        from gzkit.commands import validate_cmd

        buffer = io.StringIO()
        with (
            patch.object(
                validate_cmd,
                "console",
                Console(file=buffer, no_color=True, highlight=False, width=200),
            ),
            contextlib.suppress(SystemExit),
        ):
            validate_cmd._print_validation_result(errors, scopes)
        return buffer.getvalue()

    def test_lowercase_error_type_is_legible_in_output(self) -> None:
        """A snake_case scope name renders; it is not eaten as a markup tag."""
        output = self._render(
            [
                ValidationError(
                    type="ownership_declaration",
                    artifact=".gzkit/ownership/AGENTS.md.json",
                    message="'floor_event_id' is a required property.",
                )
            ],
            ["documents"],
        )

        self.assertIn("ownership_declaration", output)

    def test_bracketed_token_inside_message_is_legible(self) -> None:
        """Messages carry bracketed tokens too — ``taxonomy.py`` emits ``[missing]``."""
        output = self._render(
            [
                ValidationError(
                    type="adr_status_fresh",
                    artifact="docs/governance/GovZero/adr-status.md::ADR-0.1.0",
                    message="[missing] ADR-0.1.0 absent from the index.",
                )
            ],
            ["adr-status-fresh"],
        )

        self.assertIn("[missing]", output)

    def test_type_colliding_with_a_rich_style_is_not_applied_as_one(self) -> None:
        """A value that *is* a Rich style must print, never restyle the line.

        The swallowed-token case is benign. The hazard is a value colliding
        with a real style name, which Rich applies to the rest of the line.
        """
        output = self._render(
            [
                ValidationError(
                    type="bold",
                    artifact="artifact.md",
                    message="message body",
                )
            ],
            ["documents"],
        )

        self.assertIn("bold", output)


if __name__ == "__main__":
    unittest.main()
