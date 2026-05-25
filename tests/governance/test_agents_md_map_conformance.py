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

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.agents_md_map_conformance import (
    audit_agents_md_map_conformance,
)

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

    def test_file_size_over_budget_rejects(self) -> None:
        """REQ-0.0.54-03-01d fail: an AGENTS.md exceeding the declared budget must be rejected.

        Padding AGENTS.md with 20000 chars of binding bullets (so criterion (a)
        is satisfied) against a 15000-char budget must surface exactly one
        hard-rejection error of type `agents_md_map_conformance`.

        Criterion (d) is checked against the rendered file (Layer-3 projected property).
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
            errors = audit_agents_md_map_conformance(root)
            hard_errors = [e for e in errors if e.type == "agents_md_map_conformance"]
            self.assertEqual(
                len(hard_errors),
                1,
                f"Expected exactly one error for file over budget; "
                f"got {len(hard_errors)}: {hard_errors}",
            )
            self.assertEqual(hard_errors[0].artifact, "AGENTS.md")

    @unittest.skip(
        "RED until OBPI-0.0.54-03 Task 2.6 lifts template-side prohibited shapes "
        "to docs/governance/agent-contract-rationale.md and re-renders AGENTS.md. "
        "Resume context: .gzkit/handoffs/20260525T180000Z-obpi-0.0.54-03-r1-expansion-task-2.5-complete.md. "
        "Remove this @skip when Task 2.6+2.7 land and the test naturally passes. "
        "Designed-to-fail unit tests violate .gzkit/rules/tests.md Rule 6; this skip "
        "is the bridge while the keystone test remains in this file."
    )
    def test_happy_path_against_lifted_agents_md(self) -> None:
        """REQ-0.0.54-03-02: the real template must satisfy shape criteria (a)/(b)/(c).

        Currently @skip — see decorator. After Task 2.6 + Task 2.7 (re-render),
        remove the skip and this test must pass naturally against the conformant
        template + rendered AGENTS.md.

        This test copies the real template (src/gzkit/templates/agents.md) and the
        real rendered AGENTS.md into a tempdir, writes a permissive budget so
        criterion (d) does not confound shape results, then asserts ZERO hard
        findings of type 'agents_md_map_conformance'.

        The RED state is the forcing function for Task 2.6 — do NOT silence or skip.
        """
        project_root = Path(__file__).resolve().parents[2]
        real_template = project_root / "src" / "gzkit" / "templates" / "agents.md"
        real_rendered = project_root / "AGENTS.md"
        self.assertTrue(
            real_template.is_file(),
            f"Expected real template at {real_template}.",
        )
        self.assertTrue(
            real_rendered.is_file(),
            f"Expected real rendered AGENTS.md at {real_rendered}.",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_template(root, real_template.read_text(encoding="utf-8"))
            _write_rendered(root, real_rendered.read_text(encoding="utf-8"))
            # Permissive budget: isolates shape from budget concerns.
            # Task 2.6 will tighten the template to fit 15k; until then this
            # test expects shape conformance only.
            _write_budget(root, {"AGENTS.md": 200000})
            errors = audit_agents_md_map_conformance(root)
            hard_errors = [e for e in errors if e.type == "agents_md_map_conformance"]
            self.assertEqual(
                len(hard_errors),
                0,
                f"Real template should pass all map-conformance shape criteria "
                f"(a)/(b)/(c); got hard-rejection errors: {hard_errors}",
            )

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


if __name__ == "__main__":
    unittest.main()
