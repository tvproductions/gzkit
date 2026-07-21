"""Tests for `gz validate --deprecated-verb-prescription` (GHI #705).

Assertions derive from the requirement — a `gz` verb that announces its own
deprecation at runtime must not remain prescribed by a binding rule, a skill, or
a runbook — not from a run of the implementation.

The instance that motivated the scope: `gz gates` printed
"will be removed in a future release. Use `gz closeout` instead." while
`.gzkit/rules/governance-core.md` still named it as step 5 of the required
workflow order and an `lifecycle_state: active` skill still wrapped it. Any agent
following the rule literally was routed onto a deprecated surface with no signal.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.deprecations import DEPRECATED_VERBS
from gzkit.governance.trust_audits.deprecated_verb_prescription import (
    audit_deprecated_verb_prescription,
)


def _tree(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


class TestDeprecatedVerbPrescription(unittest.TestCase):
    def test_clean_tree_returns_no_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, {".gzkit/rules/x.md": "5. `uv run gz closeout ADR-0.1.0 --dry-run`\n"})
            self.assertEqual(audit_deprecated_verb_prescription(root), [])

    def test_rule_prescribing_deprecated_verb_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, {".gzkit/rules/governance-core.md": "5. `uv run gz gates --adr ADR-X`\n"})
            errors = audit_deprecated_verb_prescription(root)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, "deprecated_verb_prescription")
            self.assertEqual(errors[0].artifact, ".gzkit/rules/governance-core.md")

    def test_skill_prescribing_deprecated_verb_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, {".gzkit/skills/gz-gates/SKILL.md": "Run `uv run gz gates --adr X`.\n"})
            self.assertEqual(len(audit_deprecated_verb_prescription(root)), 1)

    def test_runbook_prescribing_deprecated_verb_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, {"docs/user/runbook.md": "Then run `gz gates --adr ADR-X`.\n"})
            self.assertEqual(len(audit_deprecated_verb_prescription(root)), 1)

    def test_ungoverned_surface_is_not_scanned(self) -> None:
        # Release notes and ADR packages are historical record. A deprecated verb
        # named there is a true statement about the past, not a live prescription.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(
                root,
                {
                    "RELEASE_NOTES.md": "- Deprecated `gz gates`.\n",
                    "docs/design/adr/foundation/ADR-0.1.0/ADR-0.1.0.md": "`gz gates` ran here.\n",
                },
            )
            self.assertEqual(audit_deprecated_verb_prescription(root), [])

    def test_escape_marker_suppresses_the_finding(self) -> None:
        # A rule that DOCUMENTS the deprecation must be able to name the verb
        # without tripping the gate it describes — otherwise the scope forbids
        # its own doctrine from being written down.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(
                root,
                {
                    ".gzkit/rules/deprecations.md": (
                        "`gz gates` is deprecated. <!-- deprecated-verb-ok: documents the ban -->\n"
                    )
                },
            )
            self.assertEqual(audit_deprecated_verb_prescription(root), [])

    def test_message_carries_the_three_guardrail_parts(self) -> None:
        # .claude/rules/guardrail-feedback-prose.md: what failed / why it is
        # forbidden / a runnable next step. A finding that names only the verb
        # leaves the next agent to guess the successor.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, {".gzkit/rules/governance-core.md": "`uv run gz gates --adr ADR-X`\n"})
            message = audit_deprecated_verb_prescription(root)[0].message
            self.assertIn("gz gates", message)
            self.assertIn("line 1", message)
            self.assertIn("gz closeout", message)
            self.assertIn("#705", message)

    def test_cli_audit_runbook_coverage_inverts_for_a_deprecated_verb(self) -> None:
        # Coupled-surface coherence (AGENTS.md § DO IT RIGHT 1a): `gz cli audit`
        # demands every verb appear in both runbooks, while this scope fails
        # closed when a deprecated one does. Absent the inversion the two checks
        # contradict and no tree can satisfy both.
        from gzkit.doc_coverage.scanner import DiscoveredCommand, check_surfaces

        deprecated = DEPRECATED_VERBS[0].verb
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(
                root,
                {
                    "docs/user/runbook.md": "no verbs here\n",
                    "docs/governance/governance_runbook.md": "no verbs here\n",
                },
            )
            cmd = DiscoveredCommand(name=deprecated, handler_name=None, line=1)
            surfaces = {s.surface: s.passed for s in check_surfaces(root, [cmd], "")[0].surfaces}
            self.assertTrue(surfaces["operator_runbook"])
            self.assertTrue(surfaces["governance_runbook"])

    def test_cli_audit_runbook_coverage_fails_when_deprecated_verb_present(self) -> None:
        from gzkit.doc_coverage.scanner import DiscoveredCommand, check_surfaces

        deprecated = DEPRECATED_VERBS[0].verb
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(
                root,
                {
                    "docs/user/runbook.md": f"Run `uv run gz {deprecated} --adr ADR-X`.\n",
                    "docs/governance/governance_runbook.md": "no verbs here\n",
                },
            )
            cmd = DiscoveredCommand(name=deprecated, handler_name=None, line=1)
            surfaces = {s.surface: s.passed for s in check_surfaces(root, [cmd], "")[0].surfaces}
            self.assertFalse(surfaces["operator_runbook"])

    def test_every_registered_verb_declares_a_successor(self) -> None:
        # A deprecation with no named replacement cannot produce a runnable next
        # step, so the scope could never satisfy the guardrail-prose bar.
        for entry in DEPRECATED_VERBS:
            self.assertTrue(entry.verb.strip())
            self.assertTrue(entry.successor.strip())


if __name__ == "__main__":
    unittest.main()
