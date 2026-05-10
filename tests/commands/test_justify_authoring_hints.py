"""TDD RED-phase tests for OBPI-0.0.30-05 gz-justify complexity-hints integration.

These tests MUST fail (RED) because:
- ``gzkit.justify.complexity_hints`` does not exist yet.
- ``gzkit.justify.cli`` does not import ``gather_hints_markdown``.
- ``Walkthrough`` has no ``complexity_hints_md`` field.
- The scaffold template does not render the complexity-hints heading.

Since ``gather_hints_markdown`` is not yet imported into ``gzkit.justify.cli``,
``mock.patch("gzkit.justify.cli.gather_hints_markdown", ...)`` raises
``AttributeError`` when entering the patch context — before ``handle_justify``
is called. This IS the correct RED signal. Do NOT add ``create=True`` to the
patch call; that would silently succeed and mask the missing import.

Mocking follows the import-site pattern established in ``test_justify_cmd.py``
(``_patch_substrate``): all mocks target ``gzkit.justify.cli.*``.
"""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from gzkit.justify.cli import handle_justify
from gzkit.justify.models import AnchorRef, EvidenceBundle
from gzkit.traceability import covers


def _fake_obpi_anchor(tmp_path: Path) -> AnchorRef:
    """Return an OBPI-kind AnchorRef with source_path under ``tmp_path``."""
    brief_path = tmp_path / "OBPI-0.0.30-05-brief.md"
    brief_path.write_text(
        "# OBPI-0.0.30-05\n\n## Allowed Paths\n\n- src/gzkit/justify/cli.py\n",
        encoding="utf-8",
    )
    return AnchorRef(
        kind="obpi",
        identifier="OBPI-0.0.30-05",
        title="gz-justify complexity-hints integration",
        body="Integrate authoring-time complexity hints into gz justify.",
        labels=(),
        author=None,
        source_path=str(brief_path),
    )


def _fake_bundle(anchor: AnchorRef) -> EvidenceBundle:
    return EvidenceBundle(
        anchor=anchor,
        matching_rules=(),
        ledger_events=(),
        recent_commits=(),
        related_anchors=(),
        taxonomy_reference="docs/governance/model-regression-taxonomy.md",
        warnings=(),
    )


class TestJustifyComplexityHintsIntegration(unittest.TestCase):
    """Integration tests for the complexity-hints injection in handle_justify."""

    @covers("REQ-0.0.30-05-02")
    def test_py_paths_with_crossings_injects_hints_heading(self) -> None:
        """When gather_hints_markdown returns non-empty hints, the scaffold
        must contain '### Authoring-time complexity hints'.

        Expected RED: AttributeError on mock.patch entry because
        gzkit.justify.cli does not yet import gather_hints_markdown.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            anchor = _fake_obpi_anchor(tmp_path)

            with (
                mock.patch(
                    "gzkit.justify.cli.resolve_anchor",
                    return_value=anchor,
                ),
                mock.patch(
                    "gzkit.justify.cli.gather_evidence",
                    return_value=_fake_bundle(anchor),
                ),
                mock.patch(
                    "gzkit.justify.cli.gather_hints_markdown",
                    return_value=("metric: radon_cc\nband: approaching\n", []),
                ),
                redirect_stdout(io.StringIO()) as out,
            ):
                code = handle_justify(
                    anchor="OBPI-0.0.30-05",
                    save=False,
                    output=None,
                    related=None,
                    draft=None,
                    draft_slug=None,
                    project_root=tmp_path,
                )

        self.assertEqual(code, 0)
        self.assertIn("### Authoring-time complexity hints", out.getvalue())

    @covers("REQ-0.0.30-05-03")
    def test_no_py_paths_skips_hints_heading(self) -> None:
        """When gather_hints_markdown returns empty string (no .py paths),
        the scaffold must NOT contain the complexity hints heading.

        Expected RED: AttributeError on mock.patch entry.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            anchor = _fake_obpi_anchor(tmp_path)

            with (
                mock.patch(
                    "gzkit.justify.cli.resolve_anchor",
                    return_value=anchor,
                ),
                mock.patch(
                    "gzkit.justify.cli.gather_evidence",
                    return_value=_fake_bundle(anchor),
                ),
                mock.patch(
                    "gzkit.justify.cli.gather_hints_markdown",
                    return_value=("", []),
                ),
                redirect_stdout(io.StringIO()) as out,
            ):
                code = handle_justify(
                    anchor="OBPI-0.0.30-05",
                    save=False,
                    output=None,
                    related=None,
                    draft=None,
                    draft_slug=None,
                    project_root=tmp_path,
                )

        self.assertEqual(code, 0)
        self.assertNotIn("### Authoring-time complexity hints", out.getvalue())

    @covers("REQ-0.0.30-05-03")
    def test_py_paths_no_crossings_skips_hints_heading(self) -> None:
        """.py paths present but no advise-band crossings → gather_hints_markdown
        returns empty string → heading absent from scaffold.

        Expected RED: AttributeError on mock.patch entry.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            anchor = _fake_obpi_anchor(tmp_path)

            with (
                mock.patch(
                    "gzkit.justify.cli.resolve_anchor",
                    return_value=anchor,
                ),
                mock.patch(
                    "gzkit.justify.cli.gather_evidence",
                    return_value=_fake_bundle(anchor),
                ),
                mock.patch(
                    "gzkit.justify.cli.gather_hints_markdown",
                    return_value=("", []),
                ),
                redirect_stdout(io.StringIO()) as out,
            ):
                code = handle_justify(
                    anchor="OBPI-0.0.30-05",
                    save=False,
                    output=None,
                    related=None,
                    draft=None,
                    draft_slug=None,
                    project_root=tmp_path,
                )

        self.assertEqual(code, 0)
        self.assertNotIn("### Authoring-time complexity hints", out.getvalue())

    @covers("REQ-0.0.30-05-04")
    def test_engine_failure_fails_open(self) -> None:
        """When gather_hints_markdown returns empty hints with a warning message,
        handle_justify must complete successfully (exit 0) and omit the heading.

        The 'fails open' contract means an engine error never blocks justify.

        Expected RED: AttributeError on mock.patch entry.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            anchor = _fake_obpi_anchor(tmp_path)

            with (
                mock.patch(
                    "gzkit.justify.cli.resolve_anchor",
                    return_value=anchor,
                ),
                mock.patch(
                    "gzkit.justify.cli.gather_evidence",
                    return_value=_fake_bundle(anchor),
                ),
                mock.patch(
                    "gzkit.justify.cli.gather_hints_markdown",
                    return_value=("", ["engine error: distilled-characteristics missing"]),
                ),
                redirect_stdout(io.StringIO()) as out,
            ):
                code = handle_justify(
                    anchor="OBPI-0.0.30-05",
                    save=False,
                    output=None,
                    related=None,
                    draft=None,
                    draft_slug=None,
                    project_root=tmp_path,
                )

        self.assertEqual(code, 0)
        self.assertNotIn("### Authoring-time complexity hints", out.getvalue())


if __name__ == "__main__":
    unittest.main()
