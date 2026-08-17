"""RED test matrix for ``audit_agents_md_map_conformance`` (OBPI-0.0.54-03).

Tests derive from the four rejection criteria in ADR-0.0.54 § Decision item 3:
(a) paragraph length; (b) prohibited subsection titles; (c) link resolution;
(d) file size within budget.  Each test cites the governing REQ in its docstring.

Layer split (Task 2.5 retarget):
- Shape criteria (a)/(b)/(c) + advisory: audited against the TEMPLATE at
  src/gzkit/templates/agents.md (Layer-1 edit surface).
- Budget criterion (d): audited against the RENDERED file at AGENTS.md
  (Layer-3 projected property).
Per docs/governance/state-doctrine.md: rendered AGENTS.md is Layer 3,
never source-of-truth. Fixes must flow through the template.
"""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.agents_md_map_conformance import (
    audit_agents_md_map_conformance,
)
from gzkit.traceability import covers

_TEMPLATE_REL = Path("src") / "gzkit" / "templates" / "agents.md"
_RENDERED_REL = Path("AGENTS.md")


def _write_template(root: Path, content: str) -> None:
    """Write content to root/src/gzkit/templates/agents.md (the audit surface for shape)."""
    template_path = root / _TEMPLATE_REL
    template_path.parent.mkdir(parents=True, exist_ok=True)
    template_path.write_text(content, encoding="utf-8")


def _write_rendered(root: Path, content: str) -> None:
    """Write content to root/AGENTS.md (the audit surface for budget)."""
    (root / _RENDERED_REL).write_text(content, encoding="utf-8")


def _write_budget(root: Path, budget: dict[str, int]) -> None:
    """Write a minimal budget config to ``root / "data" / "instructions_files_budget.json"``."""
    target = root / "data" / "instructions_files_budget.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"files": budget}), encoding="utf-8")


class AgentsMdMapConformanceAuditTests(unittest.TestCase):
    """Validator asserts the four map-not-encyclopedia criteria.

    Shape criteria (a)/(b)/(c) are checked against the template
    (src/gzkit/templates/agents.md); budget criterion (d) is checked
    against the rendered file (AGENTS.md).
    """

    # ---- audit-exempt provenance (ADR-0.0.54 audit, 2026-07-12, g0) ----------
    # git-verified: each test BODY below was authored @9b295aed (2026-05-25,
    # "land template-layer validator"); the @covers decorator lines were overlaid
    # ~5h later @b7b5984 (the OBPI-0.0.54-03 completion commit). GHI #309's
    # same-commit-window heuristic flags the later-decorator timing as possible
    # cosmetic backfill; the assertions are in fact genuine REQ-semantic checks
    # (real fixtures + structured-error asserts), independently verified at the
    # ADR-0.0.54 closeout + audit. The inline markers are the operator's
    # attestation that these are legitimate overlays, not cosmetic backfill.
    @covers("REQ-0.0.54-03-01")  # audit-exempt: regression-invariant-overlay body predates tag
    def test_paragraph_over_5_lines_without_marker_rejects(self) -> None:
        """REQ-0.0.54-03-01a: prose paragraph >5 lines without a marker must be rejected.

        A 7-line prose paragraph that does not begin with `- `, `1.`, or `**`
        violates criterion (a). The validator must surface a hard-rejection error
        so that prose accretion cannot silently pass.

        Criterion (a) is checked against the template (Layer-1 edit surface).
        """
        content = "\n".join(
            [
                "# AGENTS.md",
                "",
                "This is line one of a long prose paragraph.",
                "This is line two of the same paragraph.",
                "This is line three — continuing the same block.",
                "This is line four — still going.",
                "This is line five — almost done.",
                "This is line six — exceeds the five-line limit.",
                "This is line seven — clearly over the limit.",
                "",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_template(root, content)
            errors = audit_agents_md_map_conformance(root)
            hard_errors = [e for e in errors if e.type == "agents_md_map_conformance"]
            self.assertEqual(len(hard_errors), 1)
            self.assertEqual(hard_errors[0].artifact, _TEMPLATE_REL.as_posix())

    @covers("REQ-0.0.54-03-01")  # audit-exempt: regression-invariant-overlay body predates tag
    def test_table_shape_passes_paragraph_check_at_any_length(self) -> None:
        """REQ-0.0.54-03-01a table-shape: tables are allowed shape (b), exempt from criterion (a).

        The rule `.gzkit/rules/agents-md-map-doctrine.md` § Invariant enumerates
        five allowed shapes for AGENTS.md content:
        (a) binding bullet rules
        (b) **structured tables** (Persona, Gate Covenant, OBPI kinds,
            canonical-invocations, defect-fix routing thresholds)
        (c) canonical-link references

        Criterion (a) (paragraph length limit) MUST NOT fire on table content,
        regardless of row count. Table rows (lines beginning with `|`) are a
        structurally distinct shape from prose paragraphs and are exempt by
        the rule. This test fixtures a 9-row table (one each for the five
        named example tables, exceeding the 5-line paragraph limit) and
        asserts ZERO hard-rejection errors of type 'agents_md_map_conformance'.

        Criterion (a) is checked against the template (Layer-1 edit surface).
        """
        table_lines = [
            "| Persona | Role | Traits |",
            "|---------|------|--------|",
            "| `main-session` | Primary operator session | direct |",
            "| `implementer` | Task subagent | methodical |",
            "| `narrator` | Evidence presenter | clarity |",
            "| `pipeline-orchestrator` | Pipeline coordination | discipline |",
            "| `quality-reviewer` | Code review | rigor |",
            "| `spec-reviewer` | Spec compliance review | skepticism |",
            "| `extra-row` | Padding to exceed 5-line paragraph limit | extra |",
        ]
        content = "\n".join(["# AGENTS.md", "", "## Persona", ""] + table_lines + [""])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_template(root, content)
            errors = audit_agents_md_map_conformance(root)
            hard_errors = [e for e in errors if e.type == "agents_md_map_conformance"]
            self.assertEqual(
                len(hard_errors),
                0,
                f"A markdown table is allowed shape (b) and must NOT trigger "
                f"criterion (a) regardless of row count; got: {hard_errors}",
            )

    def test_paragraph_with_binding_marker_passes_at_any_length(self) -> None:
        """REQ-0.0.54-03-01a corner: `- ` prefix exempts any paragraph from the length limit.

        A 12-line block beginning with `- ` is a binding bullet — the whole block
        counts as one structured item.  Criterion (a) must NOT fire on it, regardless
        of length.  This test verifies the marker exemption is load-bearing.

        Criterion (a) is checked against the template (Layer-1 edit surface).
        """
        # Build a 12-line binding-bullet block (starts with "- ").
        bullet_lines = ["- This binding bullet spans many lines:"]
        for i in range(2, 13):
            bullet_lines.append(f"  continuation line {i} of 12")
        content = "\n".join(["# AGENTS.md", ""] + bullet_lines + [""])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_template(root, content)
            errors = audit_agents_md_map_conformance(root)
            hard_errors = [e for e in errors if e.type == "agents_md_map_conformance"]
            self.assertEqual(
                len(hard_errors),
                0,
                f"Expected no hard-rejection errors for a binding-bullet paragraph; "
                f"got: {hard_errors}",
            )

    @covers("REQ-0.0.54-03-01")  # audit-exempt: regression-invariant-overlay body predates tag
    def test_prohibited_subsection_title_rejects(self) -> None:
        """REQ-0.0.54-03-01b: any heading from the prohibited-title set must be rejected.

        ADR-0.0.54 bars subsection headings that signal encyclopedic content.
        Each variant in the set must independently trigger a hard-rejection.
        The validator must be case-sensitive for the `Worked example` vs
        `Worked Example` distinction, and handle both capitalizations.

        Criterion (b) is checked against the template (Layer-1 edit surface).
        """
        prohibited = [
            "## Worked example",
            "## Worked Example",
            "## Anti-patterns",
            "## Rationale",
            "## Why this is canon",
            "## Why X is canon",
        ]
        for title in prohibited:
            with self.subTest(title=title):
                content = "\n".join(
                    [
                        "# AGENTS.md",
                        "",
                        title,
                        "",
                        "Some content under the prohibited heading.",
                        "",
                    ]
                )
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    _write_template(root, content)
                    errors = audit_agents_md_map_conformance(root)
                    hard_errors = [e for e in errors if e.type == "agents_md_map_conformance"]
                    self.assertEqual(
                        len(hard_errors),
                        1,
                        f"Expected exactly one hard-rejection for prohibited title '{title}'; "
                        f"got {len(hard_errors)}: {hard_errors}",
                    )
                    self.assertEqual(hard_errors[0].artifact, _TEMPLATE_REL.as_posix())

    @covers("REQ-0.0.54-03-01")  # audit-exempt: regression-invariant-overlay body predates tag
    def test_dangling_link_rejects(self) -> None:
        """REQ-0.0.54-03-01c file-existence: a link to a nonexistent file must be rejected.

        Every relative Markdown link in the template must resolve to an existing file
        on disk.  A link to `docs/governance/nonexistent.md` that does not exist
        in the temp project root must surface a hard-rejection error.

        Criterion (c) is checked against the template (Layer-1 edit surface).
        """
        content = "\n".join(
            [
                "# AGENTS.md",
                "",
                "See [Foo](docs/governance/nonexistent.md) for details.",
                "",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_template(root, content)
            errors = audit_agents_md_map_conformance(root)
            hard_errors = [e for e in errors if e.type == "agents_md_map_conformance"]
            self.assertEqual(
                len(hard_errors),
                1,
                f"Expected one error for dangling link; got {len(hard_errors)}: {hard_errors}",
            )
            self.assertEqual(hard_errors[0].artifact, _TEMPLATE_REL.as_posix())

    def test_dangling_anchor_rejects(self) -> None:
        """REQ-0.0.54-03-01c anchor-resolution: a link with a missing anchor must be rejected.

        When a link like `See [X](docs/governance/real.md#missing-anchor)` points
        to a file that exists but does not contain a heading matching `missing-anchor`,
        the validator must surface a hard-rejection error.  File existence alone is
        not sufficient — the named anchor must also resolve.

        Criterion (c) is checked against the template (Layer-1 edit surface).
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Create the target file with a real heading but NOT the linked anchor.
            target_dir = root / "docs" / "governance"
            target_dir.mkdir(parents=True)
            (target_dir / "real.md").write_text(
                "# Real heading\n\nSome content.\n", encoding="utf-8"
            )
            content = "\n".join(
                [
                    "# AGENTS.md",
                    "",
                    "See [X](docs/governance/real.md#missing-anchor) for details.",
                    "",
                ]
            )
            _write_template(root, content)
            errors = audit_agents_md_map_conformance(root)
            hard_errors = [e for e in errors if e.type == "agents_md_map_conformance"]
            self.assertEqual(
                len(hard_errors),
                1,
                f"Expected one error for dangling anchor; got {len(hard_errors)}: {hard_errors}",
            )
            self.assertEqual(hard_errors[0].artifact, _TEMPLATE_REL.as_posix())

    def test_resolving_link_passes(self) -> None:
        """REQ-0.0.54-03-01c happy: a link with a resolvable path and anchor must pass.

        When `See [X](docs/governance/real.md#real-heading)` resolves — the file
        exists and the heading slugifies to `real-heading` — criterion (c) must
        not fire.

        Criterion (c) is checked against the template (Layer-1 edit surface).
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target_dir = root / "docs" / "governance"
            target_dir.mkdir(parents=True)
            (target_dir / "real.md").write_text(
                "# Real heading\n\nSome content.\n", encoding="utf-8"
            )
            content = "\n".join(
                [
                    "# AGENTS.md",
                    "",
                    "See [X](docs/governance/real.md#real-heading) for details.",
                    "",
                ]
            )
            _write_template(root, content)
            errors = audit_agents_md_map_conformance(root)
            hard_errors = [e for e in errors if e.type == "agents_md_map_conformance"]
            self.assertEqual(
                len(hard_errors),
                0,
                f"Expected no hard-rejection errors for a resolving link; got: {hard_errors}",
            )

    def test_file_size_within_budget_passes(self) -> None:
        """REQ-0.0.54-03-01d happy: an AGENTS.md well within budget must NOT trigger criterion (d).

        A minimal AGENTS.md (~100 chars) against a 15000-char budget must not
        surface any hard-rejection error.  Criterion (d) must not fire when the
        file is well under budget.

        Criterion (d) is checked against the rendered file (Layer-3 projected property).
        """
        content = "# AGENTS.md\n\n- Minimal binding bullet.\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_rendered(root, content)
            _write_budget(root, {"AGENTS.md": 15000})
            errors = audit_agents_md_map_conformance(root)
            hard_errors = [e for e in errors if e.type == "agents_md_map_conformance"]
            self.assertEqual(
                len(hard_errors),
                0,
                f"Expected no errors for file within budget; got: {hard_errors}",
            )

    @covers("REQ-0.0.54-03-01")  # audit-exempt: regression-invariant-overlay body predates tag
    def test_file_size_over_budget_is_reported_but_not_rejected(self) -> None:
        """Criterion (d) measures and reports an over-budget AGENTS.md, and does not reject it.

        SUPERSEDES the original assertion of REQ-0.0.54-03-01d ("must be
        rejected") by operator ruling 2026-08-17, verbatim: *"temporary stay of
        all control surface budget limits until version 1.0. I want to be
        warned, and we may lift the limits as needed, but no blockers."*
        ADR-0.0.54 is Validated and stays sealed — its text records what was
        decided on its own date, which is the reading convention
        `data/instructions_files_budget.json` states for itself. The live
        posture is that data file's LAST entry, and the exit condition is 1.0.

        The REQ's proof channel is intact: this test still covers it, and it
        still exercises criterion (d) end-to-end. What changed is the asserted
        consequence, not the checked property — so both halves are asserted
        here. An audit that had merely stopped LOOKING would satisfy the
        no-rejection half while failing the reported half, which is the
        degeneration the stay must not become.

        Padding AGENTS.md with 20000 chars of binding bullets keeps criterion
        (a) satisfied, isolating (d). Criterion (d) is checked against the
        rendered file (Layer-3 projected property).
        """
        # Build content that exceeds the 15000-char budget.
        header = "# AGENTS.md\n\n"
        # Each bullet line is ~34 chars; repeat until we exceed 15000 chars.
        bullet_line = "- This is a binding bullet line.\n"
        repetitions = (20000 // len(bullet_line)) + 1
        content = header + bullet_line * repetitions
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_rendered(root, content)
            _write_budget(root, {"AGENTS.md": 15000})
            buffer = io.StringIO()
            with contextlib.redirect_stderr(buffer):
                errors = audit_agents_md_map_conformance(root)
            advisories = buffer.getvalue()
            hard_errors = [e for e in errors if e.type == "agents_md_map_conformance"]
            self.assertEqual(
                len(hard_errors),
                0,
                f"Budget overrun must not block under the 2026-08-17 stay; "
                f"got {len(hard_errors)}: {hard_errors}",
            )
            self.assertIn("AGENTS.md", advisories, "the overrun must still be reported")
            self.assertIn("15000", advisories, "the advisory must name the budget")
            self.assertIn(str(len(content)), advisories, "the advisory must name the measured size")

    @covers("REQ-0.0.54-03-02")
    def test_happy_path_against_lifted_agents_md(self) -> None:
        """REQ-0.0.54-03-02: the real template + rendered AGENTS.md satisfy all four criteria.

        Audits the real project state at `Path(__file__).resolve().parents[2]`
        — the template at `src/gzkit/templates/agents.md`, the rendered
        AGENTS.md, and the budget config at `data/instructions_files_budget.json`.
        Zero hard findings means: shape (a/b/c) clean on the template AND
        budget (d) clean on the rendered file. This is the keystone end-to-end
        assertion that the named OBPI deliverables hold against real state.

        Criterion (c) (link resolution) requires the real `docs/governance/`,
        `.gzkit/rules/`, and ADR package files to exist on disk — copying the
        template into a tempdir would break every relative link, so this
        test runs against the real root by design.
        """
        project_root = Path(__file__).resolve().parents[2]
        errors = audit_agents_md_map_conformance(project_root)
        hard_errors = [e for e in errors if e.type == "agents_md_map_conformance"]
        self.assertEqual(
            len(hard_errors),
            0,
            f"Real project should pass all map-conformance criteria "
            f"(a)/(b)/(c)/(d); got hard-rejection errors: {hard_errors}",
        )

    @covers("REQ-0.0.54-03-05")  # audit-exempt: regression-invariant-overlay body predates tag
    def test_advisory_warning_for_long_binding_bullet(self) -> None:
        """REQ-0.0.54-03-05: a long binding bullet emits a WARNING, not a hard rejection.

        Per ADR-0.0.54 § Consequences Negative #7, the per-bullet 3-line heuristic
        must NOT block work — it is a soft advisory.  A bullet starting with `- `
        inside `## Behavior Rules` that spans 5 lines must emit exactly one error of
        type `agents_md_map_conformance_advisory` and ZERO errors of type
        `agents_md_map_conformance` (the hard-rejection type).

        The advisory check runs against the template (Layer-1 edit surface).
        """
        content = "\n".join(
            [
                "# AGENTS.md",
                "",
                "## Behavior Rules",
                "",
                "### Always",
                "",
                "- This binding bullet spans more than three lines:",
                "  continuation line 2.",
                "  continuation line 3.",
                "  continuation line 4.",
                "  continuation line 5 — triggers the advisory.",
                "",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_template(root, content)
            errors = audit_agents_md_map_conformance(root)
            hard_errors = [e for e in errors if e.type == "agents_md_map_conformance"]
            advisory_errors = [e for e in errors if e.type == "agents_md_map_conformance_advisory"]
            self.assertEqual(
                len(hard_errors),
                0,
                f"A long binding bullet must NOT trigger a hard rejection; got: {hard_errors}",
            )
            self.assertEqual(
                len(advisory_errors),
                1,
                f"Expected exactly one advisory warning for long binding bullet; "
                f"got {len(advisory_errors)}: {advisory_errors}",
            )
            self.assertEqual(advisory_errors[0].artifact, _TEMPLATE_REL.as_posix())

    @covers("REQ-0.0.54-03-03")  # audit-exempt: regression-invariant-overlay body predates tag
    def test_remediation_message_points_at_gz_context_diet(self) -> None:
        """REQ-0.0.54-03-03 forward-compat: rejection messages must embed `/gz-context-diet`.

        Per ADR-0.0.53, failures will eventually carry a structured
        `RemediationPayload`.  Until that migration lands, the `recovery` field is
        embedded as a string in `errors[0].message`.  This test asserts that
        `/gz-context-diet` appears in the message — the forward-compat shape that
        ADR-0.0.53-02 will promote to the structured payload `recovery` field.

        Uses a prohibited-title fixture written to the template (Layer-1 edit surface)
        since shape failures originate there.
        """
        # Use the prohibited-title fixture to guarantee at least one error.
        content = "\n".join(
            [
                "# AGENTS.md",
                "",
                "## Worked example",
                "",
                "Some encyclopedic content that violates the map doctrine.",
                "",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_template(root, content)
            errors = audit_agents_md_map_conformance(root)
            self.assertGreater(
                len(errors),
                0,
                "Expected at least one error from the prohibited-title fixture.",
            )
            self.assertIn(
                "/gz-context-diet",
                errors[0].message,
                f"Expected '/gz-context-diet' in errors[0].message; got: '{errors[0].message}'",
            )


class GzCheckPipelineWiringTests(unittest.TestCase):
    """REQ-04: `gz check` default pipeline includes the new validator as a fail-closed step."""

    @covers("REQ-0.0.54-03-04")
    def test_check_pipeline_includes_agents_md_map_conformance(self) -> None:
        """REQ-0.0.54-03-04: `gz check` runs the new validator scope as a default step.

        Structural test: `_build_check_steps()` (the runtime constructor that
        `gz check` invokes) must include a step labeled with the validator
        name and bound to the `run_agents_md_map_conformance_audit` runner.
        REQ semantic: the validator is in the default pipeline, not opt-in.
        """
        from gzkit.commands.quality import _build_check_steps
        from gzkit.quality import run_agents_md_map_conformance_audit

        steps = _build_check_steps()
        names = [name for name, _runner in steps]
        runners = {runner for _name, runner in steps}

        self.assertIn(
            "AGENTS.md map conformance",
            names,
            f"Expected check step 'AGENTS.md map conformance' in pipeline; got: {names}",
        )
        self.assertIn(
            run_agents_md_map_conformance_audit,
            runners,
            "Expected run_agents_md_map_conformance_audit bound to a check step",
        )


if __name__ == "__main__":
    unittest.main()
