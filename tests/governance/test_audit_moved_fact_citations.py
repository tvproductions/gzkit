"""Tests for ``audit_moved_fact_citations`` (GHI #1374, a scope since GHI #1370).

The 2026-09-17 AGENTS.md rewrite moved the canonical receipt invocations to the
gz-arb skill and dropped the fix() precedent criterion from defect-fix routing; a
live sentence restating either is stale. The audit reads fixture trees here; the
live tree is read by the `gz check` step that runs the scope.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.commands import validate_cmd
from gzkit.enforcement import _run_single_claim, production_enforcement_registry
from gzkit.governance.trust_audits import audit_moved_fact_citations, moved_fact_citations
from gzkit.governance.trust_audits.moved_fact_citations import (
    ROOT_FILES,
    ROOTS,
    stale_restatements,
)

_STALE = "Direct-fix: precedent check (git log --since='60 days ago') then a TDD cycle.\n"


def _tree(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    return root


class MovedFactCitationsTests(unittest.TestCase):
    def _artifacts(self, files: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            return [e.artifact for e in audit_moved_fact_citations(_tree(Path(tmp), files))]

    def test_a_restatement_on_each_root_and_root_file_is_flagged(self) -> None:
        files = {f"{rel}/x.md": _STALE for rel in ROOTS}
        files.update(dict.fromkeys(ROOT_FILES, _STALE))
        expected = sorted([f"{rel}/x.md" for rel in ROOTS] + list(ROOT_FILES))
        self.assertEqual(sorted(self._artifacts(files)), expected)

    def test_records_governance_docs_and_other_suffixes_are_not_read(self) -> None:
        artifacts = self._artifacts(
            {
                ".gzkit/skills/s/proofs/p.md": _STALE,
                "docs/user/archive/a.md": _STALE,
                "docs/governance/defect-fix-routing.md": _STALE,
                ".gzkit/templates/t.j2": _STALE,
            }
        )
        self.assertEqual(artifacts, [])

    def test_the_fence_tells_a_restatement_from_the_current_text(self) -> None:
        stale = (
            (
                "- Binding rule: `AGENTS.md` § Attestation (em-dash pattern + canonical "
                "invocations + lane behavior + receipt-ID discipline)"
            ),
            "single named surface; ≥3 recent `fix(` precedents) — fix in place",
            "Direct-fix: precedent check (`git log --since='60 days ago' --oneline`) → TDD cycle",
            "| Precedent | `git log --since='60 days ago' --oneline --grep='^fix('` ≥3 commits |",
            "enriched per `AGENTS.md` § Attestation (em-dash + session evidence + receipt IDs).",
        )
        current = (
            (
                "- Binding rule: `AGENTS.md` § Attestation (the operator's words verbatim, then "
                "concrete evidence; lane behavior; receipt-ID discipline). It points here for "
                "the canonical invocations, which step 1 lists."
            ),
            "surface the routing facts `AGENTS.md` § Defect-fix routing names — size, surface.",
            "Direct-fix: route per `AGENTS.md` § Defect-fix routing → TDD cycle",
            '"**GHI Triage** — 44 open issues | `fix()` precedent (60d): 262"',
            "Worked precedent: `84519da5` (GHI #852) pinned the authorship guard by LEVEL.",
            (
                "then append concrete evidence per `AGENTS.md` § Attestation: receipt IDs from "
                "the canonical invocations `gz-arb` lists, test counts, file paths."
            ),
            (
                "On 2026-04-23, the retired attestation rule itself was folded: binding content "
                "(em-dash pattern, canonical invocations) moved to `AGENTS.md` § Attestation."
            ),
        )
        for text in stale:
            with self.subTest(stale=text):
                self.assertTrue(stale_restatements(text))
        for text in current:
            with self.subTest(current=text):
                self.assertFalse(stale_restatements(text))

    def test_a_missing_root_is_a_finding_on_gzkits_tree_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            framework = _tree(Path(tmp), {"src/gzkit/__init__.py": ""})
            on_gzkit = {e.artifact for e in audit_moved_fact_citations(framework)}
        with tempfile.TemporaryDirectory() as tmp:
            on_adopter = audit_moved_fact_citations(Path(tmp))
        self.assertEqual(on_gzkit, set(ROOTS) - {"src/gzkit"} | set(ROOT_FILES))
        self.assertEqual(on_adopter, [])

    def test_message_names_the_new_homes_and_the_recovery_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {".gzkit/skills/s/SKILL.md": _STALE})
            (error,) = audit_moved_fact_citations(root)
        self.assertIn(".gzkit/skills/s/SKILL.md", error.message)
        self.assertIn("gz-arb", error.message)
        self.assertIn("defect-fix-routing.md", error.message)
        self.assertIn("uv run gz validate --moved-fact-citations", error.message)


class DispatchAndControlTests(unittest.TestCase):
    """The scope runs in the default tier, and its control fails when the scope narrows."""

    def test_scope_runs_in_the_default_tier(self) -> None:
        entries = {e.stem: e for e in validate_cmd.VALIDATOR_REGISTRY}
        self.assertEqual("default", entries["moved_fact_citations"].tier)

    def _control_outcome(self) -> str:
        records = {r.claim_id: r for r in production_enforcement_registry()}
        return _run_single_claim(records["moved-fact-citations"]).outcome

    def test_the_control_catches_its_fixture(self) -> None:
        self.assertEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_scope_drops_a_root(self) -> None:
        with patch.object(moved_fact_citations, "ROOTS", ROOTS[1:]):
            self.assertNotEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_dated_admission_is_lost(self) -> None:
        with patch.object(moved_fact_citations, "_DATED", moved_fact_citations.re.compile("(?!)")):
            self.assertNotEqual(self._control_outcome(), "PASS")


if __name__ == "__main__":
    unittest.main()
