"""Tests for the two-path template render contract (GHI #741 follow-up).

`render_template` formatted through `SafeDict` for every caller, whose
`__missing__` returns the key as its own literal token. An omitted variable
therefore rendered as plausible-looking text instead of raising, and shipped.
That is how 44 ADRs reached the persona grandfather roster — and it was never
persona-specific: a fresh `gz plan create` ADR also carried `{alternatives}`,
`{decision}`, `{intent}`, `{negative_consequences}`, `{positive_consequences}`
and `{qa_transcript}`.

The leniency is not uniformly wrong, which is why the fix is two paths rather
than one flag flip. Surface sync renders adopter-supplied project-local
templates whose unknown tokens are legitimately passthrough — being strict
there would break `gz agent sync` for any adopter with a customised template.
Scaffolding has the opposite need: an unsupplied variable is a bug in the
caller, and the caller is gzkit.

    * `render_template`         — scaffolding. Strict. Raises.
    * `render_surface_template` — surface sync. Lenient. Passthrough preserved.

Tests assert semantics, not strings (Invariant 6f).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.templates import (
    MissingTemplateVariableError,
    render_surface_template,
    render_template,
)


class TestScaffoldingRenderIsStrict(unittest.TestCase):
    def test_missing_variable_raises(self) -> None:
        """Rendering a scaffolding template without a required variable raises.

        Semantic: this is the behaviour `SafeDict` suppressed. A caller that
        forgets a variable must fail at render time, when the omission is a
        one-line fix, rather than writing residue into a governance artifact
        that then needs a grandfather roster.
        """
        with self.assertRaises(MissingTemplateVariableError):
            render_template("adr", id="ADR-0.99.0-probe", title="Probe")

    def test_error_names_every_missing_variable(self) -> None:
        """The raised error enumerates all missing variables, not just the first.

        Semantic: a caller supplying 12 of 18 variables should learn all six
        omissions in one run. Reporting one at a time turns a single fix into
        six render-fail-patch cycles, and that friction is what makes a lenient
        fallback attractive in the first place.
        """
        with self.assertRaises(MissingTemplateVariableError) as ctx:
            render_template(
                "adr",
                id="ADR-0.99.0-probe",
                title="Probe",
                semver="0.99.0",
                lane="lite",
                parent="PRD-X",
                kind="feature",
                decomposition_scorecard="SC",
                checklist="CL",
                persona="P",
            )

        missing = ctx.exception.missing
        self.assertIn("intent", missing)
        self.assertIn("decision", missing)
        self.assertIn("alternatives", missing)
        self.assertGreaterEqual(len(missing), 3, "all omissions reported together")

    def test_complete_context_renders_without_residue(self) -> None:
        """A fully-supplied render leaves no brace-token residue behind.

        Semantic: the point is not merely that it does not raise — it is that
        the artifact written to disk carries no scaffolding. This is the
        property `audit_persona_witness` checks downstream, asserted here at
        the source so both ends of the pipe agree.
        """
        import re

        out = render_template(
            "constitution",
            id="CONST-1",
            title="T",
            semver="1.0.0",
            status="Draft",
            date="2026-07-31",
        )

        self.assertEqual(re.findall(r"\{[a-z_][a-z0-9_]*\}", out), [])

    def test_defaults_still_satisfy_their_variables(self) -> None:
        """Built-in defaults (date, status, lane) count as supplied.

        Semantic: strictness must not defeat the defaults the renderer already
        provides, or every caller would have to restate them.
        """
        out = render_template("constitution", id="CONST-1", title="T", semver="1.0.0")
        self.assertIn("CONST-1", out)


class TestSurfaceRenderIsLenient(unittest.TestCase):
    def test_unknown_token_passes_through(self) -> None:
        """Surface rendering preserves a token it has no value for.

        Semantic: adopters supply project-local templates under
        `.gzkit/templates/`. A token gzkit does not know about is the adopter's,
        not a bug — refusing it would break `gz agent sync` for every project
        that customised a surface. Passthrough is the contract here.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp) / ".gzkit" / "templates"
            tdir.mkdir(parents=True)
            (tdir / "probe.md").write_text(
                "# {project_name}\n\nAdopter token: {adopter_specific}\n",
                encoding="utf-8",
            )
            import os

            cwd = Path.cwd()
            os.chdir(tmp)
            try:
                out = render_surface_template("probe", project_name="demo")
            finally:
                os.chdir(cwd)

        self.assertIn("demo", out)
        self.assertIn("{adopter_specific}", out, "unknown token must survive")

    def test_surface_render_never_raises_on_omission(self) -> None:
        """The lenient path does not raise where the strict path would.

        Semantic: the two paths must genuinely differ. If surface rendering
        also raised, the split would be decorative and adopters would break.
        """
        try:
            render_surface_template("copilot", project_name="demo")
        except MissingTemplateVariableError:  # pragma: no cover
            self.fail("surface render must not enforce strictness")


if __name__ == "__main__":
    unittest.main()
