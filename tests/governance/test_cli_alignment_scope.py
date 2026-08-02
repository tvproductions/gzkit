"""`--cli-alignment` must see the surfaces its rule declares (GHI #745).

Two compounding blind spots let a governed skill prescribe `gz ledger tail`, a
verb that has never existed, while `gz validate --cli-alignment` exited 0:

1. **Source blindness.** ``_cli_alignment_sources`` read only
   ``features/**``, ``docs/user/runbook.md``, ``docs/user/commands/**`` and
   ``docs/user/manpages/**`` — 198 files. ``.gzkit/skills/**/SKILL.md`` is named
   explicitly in `.claude/rules/governance-core.md` § Operator-doc verb
   resolution and was never read at all, so the reproduction in GHI #745 would
   have passed even with backticks.
2. **Markup blindness.** All three recognizers require backticks or quotes, so a
   verb inside a ```` ```bash ```` fence matched none of them — the inverse of
   the intended coverage, since a fenced block is the form operators copy and run.

These tests pin both, against synthetic trees so they fail for behavioral
reasons rather than repository content.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.cli import audit_cli_alignment


class _Tree(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write(self, rel: str, body: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path


class TestFencedBlocksAreScanned(_Tree):
    def test_unregistered_verb_inside_a_fence_is_reported(self) -> None:
        """The runnable form is the one that must be checked."""
        self.write(
            "docs/user/runbook.md",
            "# Runbook\n\nRun it:\n\n```bash\ngz nosuchverb tail --event x\n```\n",
        )
        errors = audit_cli_alignment(self.root)
        self.assertEqual(len(errors), 1, f"expected one finding, got {errors}")
        self.assertIn("nosuchverb", errors[0].message)

    def test_uv_run_prefix_inside_a_fence_is_resolved(self) -> None:
        """`uv run gz <verb>` is the canonical invocation form in gzkit docs."""
        self.write(
            "docs/user/runbook.md",
            "```bash\nuv run gz nosuchverb --flag\n```\n",
        )
        self.assertEqual(len(audit_cli_alignment(self.root)), 1)

    def test_shell_prompt_inside_a_fence_is_resolved(self) -> None:
        """Transcript-style blocks carry a `$ ` prompt before the command."""
        self.write("docs/user/runbook.md", "```console\n$ gz nosuchverb\n```\n")
        self.assertEqual(len(audit_cli_alignment(self.root)), 1)

    def test_registered_verb_inside_a_fence_passes(self) -> None:
        """Widening detection must not invent findings for real verbs."""
        self.write("docs/user/runbook.md", "```bash\nuv run gz status --table\n```\n")
        self.assertEqual(audit_cli_alignment(self.root), [])

    def test_prose_outside_a_fence_still_checked(self) -> None:
        """The pre-existing backticked recognizer keeps working."""
        self.write("docs/user/runbook.md", "See `gz nosuchverb` for details.\n")
        self.assertEqual(len(audit_cli_alignment(self.root)), 1)


class TestSkillsAreInScope(_Tree):
    def test_skill_file_with_unregistered_verb_is_reported(self) -> None:
        """`.gzkit/skills/**/SKILL.md` is named in the rule's declared scope."""
        self.write(
            ".gzkit/skills/gz-demo/SKILL.md",
            "# demo\n\n```bash\ngz nosuchverb tail --event composition_emitted\n```\n",
        )
        errors = audit_cli_alignment(self.root)
        self.assertEqual(len(errors), 1, f"expected one finding, got {errors}")
        self.assertIn("nosuchverb", errors[0].message)
        self.assertIn("SKILL.md", errors[0].artifact)

    def test_governance_runbook_is_in_scope(self) -> None:
        """The rule names `docs/governance/governance_runbook.md` explicitly."""
        self.write(
            "docs/governance/governance_runbook.md",
            "```bash\ngz nosuchverb\n```\n",
        )
        self.assertEqual(len(audit_cli_alignment(self.root)), 1)


class TestDeclaredDocsScopeIsRead(_Tree):
    """The rule declares `docs/**/*.md`, not a hand-listed subset (GHI #745).

    Enumerating four directories under `docs/user` left the rest of the declared
    field unread: a dead verb in a design doc, a governance page, or a PRD was
    invisible indefinitely. The enumeration IS the blind spot — the same
    derivation error as scoping an allowlist by its examples.
    """

    def test_an_arbitrary_docs_file_is_scanned(self) -> None:
        self.write("docs/design/some-proposal.md", "Run `gz nosuchverb` to start.\n")
        self.assertEqual(len(audit_cli_alignment(self.root)), 1)

    def test_a_governance_page_is_scanned(self) -> None:
        self.write("docs/governance/some-doctrine.md", "```bash\ngz nosuchverb\n```\n")
        self.assertEqual(len(audit_cli_alignment(self.root)), 1)


class TestStructuralExemptions(_Tree):
    """Sealed records are exempted, never rewritten.

    Editing a sealed artifact to insert a suppression marker would contradict
    the doctrine that created the terminal-brief exemption in the first place:
    these documents are evidence of what was true at a moment, and a later hand
    reaching into them is the defect, not the fix.

    Pool ADRs are exempt on a different ground (operator ruling, 2026-08-02):
    describing a proposed CLI surface is what a pool ADR is FOR, so its verbs
    are unregistered by definition rather than by mistake.
    """

    def test_pool_adrs_are_exempt(self) -> None:
        self.write("docs/design/adr/pool/ADR-pool.thing.md", "`gz nosuchverb run`\n")
        self.assertEqual(audit_cli_alignment(self.root), [])

    def test_terminal_briefs_are_exempt(self) -> None:
        self.write(
            "docs/design/adr/foundation/ADR-0.0.1-x/obpis/OBPI-0.0.1-01-y.md",
            "---\nstatus: Completed\n---\n\n`gz nosuchverb`\n",
        )
        self.assertEqual(audit_cli_alignment(self.root), [])

    def test_superseded_is_terminal_and_therefore_exempt(self) -> None:
        """`Superseded` is already in BRIEF_TERMINAL_STATUSES.

        GHI #745 proposed a third exemption for "self-declared SUPERSEDED docs".
        It needs no separate predicate — the terminal-brief check already covers
        it, which is why a separate scan for it finds nothing.
        """
        self.write(
            "docs/design/adr/foundation/ADR-0.0.2-x/ADR-0.0.2-x.md",
            "---\nstatus: Superseded\n---\n\n`gz nosuchverb`\n",
        )
        self.assertEqual(audit_cli_alignment(self.root), [])

    def test_adr_audit_artifacts_are_exempt(self) -> None:
        """Audit records are sealed evidence of a completed ceremony."""
        self.write(
            "docs/design/adr/foundation/ADR-0.0.3-x/audit/AUDIT.md",
            "The brief prescribed `gz nosuchverb` at audit time.\n",
        )
        self.assertEqual(audit_cli_alignment(self.root), [])

    def test_evaluation_scorecards_are_exempt(self) -> None:
        self.write(
            "docs/design/adr/foundation/ADR-0.0.4-x/EVALUATION_SCORECARD.md",
            "Scored against `gz nosuchverb`.\n",
        )
        self.assertEqual(audit_cli_alignment(self.root), [])

    def test_releases_are_exempt(self) -> None:
        """Release manifests quote GHI titles verbatim; rewriting falsifies them."""
        self.write("docs/releases/v1.2.3.md", "- #123 `gz nosuchverb` miscounts rows\n")
        self.assertEqual(audit_cli_alignment(self.root), [])

    def test_a_live_doc_beside_an_exempt_one_still_fails(self) -> None:
        """Exemption is per-artifact, never a blanket over the directory."""
        self.write("docs/design/adr/pool/ADR-pool.thing.md", "`gz nosuchverb`\n")
        self.write("docs/design/live-thing.md", "`gz alsonosuchverb`\n")
        errors = audit_cli_alignment(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("alsonosuchverb", errors[0].message)


class TestSpeculativeMarkerIsHonored(_Tree):
    """The escape hatch `governance-core.md` promises, now real on this surface.

    The rule told operators to "mark the reference as speculative so the check
    skips it"; `audit_cli_alignment` was the one governed verb-checker that had
    never adopted the marker, so the promised recovery did not exist here.
    """

    def test_marker_suppresses_a_planned_verb(self) -> None:
        self.write(
            "docs/design/proposal.md",
            "<!-- gz-validate-skip: command-shape -->\nWe will add `gz nosuchverb`.\n",
        )
        self.assertEqual(audit_cli_alignment(self.root), [])

    def test_marker_suppresses_a_planned_fenced_block(self) -> None:
        self.write(
            "docs/design/proposal.md",
            "<!-- gz-validate-skip: command-shape -->\n```bash\ngz nosuchverb --flag\n```\n",
        )
        self.assertEqual(audit_cli_alignment(self.root), [])

    def test_marker_does_not_suppress_the_rest_of_the_file(self) -> None:
        """A blanket-suppressing marker would be an off switch, not an escape."""
        self.write(
            "docs/design/proposal.md",
            "<!-- gz-validate-skip: command-shape -->\n`gz nosuchverb`\n\n`gz alsonosuchverb`\n",
        )
        errors = audit_cli_alignment(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("alsonosuchverb", errors[0].message)


class TestCommittedSurfacesResolve(unittest.TestCase):
    """Every governed surface in the widened scope resolves today.

    This is the re-audit GHI #745 asked for. It is not a snapshot of a count —
    it asserts zero, so a newly authored dead verb reference fails closed.
    """

    def test_repository_cli_alignment_is_clean(self) -> None:
        errors = audit_cli_alignment(Path(__file__).resolve().parents[2])
        self.assertEqual(
            [f"{e.artifact}: {e.message}" for e in errors],
            [],
            "An operator-doc surface prescribes a `gz <verb>` that is not "
            "registered. Rename the reference to a real verb, or register the "
            "verb. Confirm with `uv run gz validate --cli-alignment`.",
        )


if __name__ == "__main__":
    unittest.main()
