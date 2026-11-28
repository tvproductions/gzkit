"""Tests for ``audit_tidy_verdict_citations`` (GHI #1373, a scope since GHI #1370).

`gz tidy` exits 3 on a breach and 0 only when no breach section has a finding
(GHI #1124); a live sentence saying its exit status ignores its findings is stale.
The audit reads fixture trees here; the live tree is read by the `gz check` step.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.commands import validate_cmd
from gzkit.enforcement import _run_single_claim, production_enforcement_registry
from gzkit.governance.trust_audits import audit_tidy_verdict_citations, tidy_verdict_citations
from gzkit.governance.trust_audits.tidy_verdict_citations import (
    DATED_RECORDS,
    ROOT_FILES,
    ROOTS,
    stale_tidy_status_claims,
)

_STALE = "Tidy exits 0 whatever it reports.\n"


def _tree(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    return root


class TidyVerdictCitationsTests(unittest.TestCase):
    def _artifacts(self, files: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            return [e.artifact for e in audit_tidy_verdict_citations(_tree(Path(tmp), files))]

    def test_a_stale_claim_on_each_root_and_root_file_is_flagged(self) -> None:
        files = {f"{rel}/x.md": _STALE for rel in ROOTS}
        files.update(dict.fromkeys(ROOT_FILES, _STALE))
        expected = sorted([f"{rel}/x.md" for rel in ROOTS] + list(ROOT_FILES))
        self.assertEqual(sorted(self._artifacts(files)), expected)

    def test_dated_records_proofs_and_archives_are_not_read(self) -> None:
        files = {f"{rel}/r.md": _STALE for rel in DATED_RECORDS}
        files[".gzkit/chores/c/proofs/p.md"] = _STALE
        files["docs/archive/a.md"] = _STALE
        self.assertEqual(self._artifacts(files), [])

    def test_the_fence_tells_a_stale_claim_from_the_contract(self) -> None:
        stale = (
            (
                '| "Tidy exited 0, so the project is tidy" | Tidy exits 0 whatever it '
                "reports. Only the printed sections say what it found. |"
            ),
            "- Reading tidy's exit code instead of its output",
            "`gz tidy` always\n   exits 0; read the report.",
            "Tidy returns 0 regardless of what it finds.",
            "Ignore the exit code of gz tidy and read the sections.",
            "gz tidy exits 0 even with findings.",
            "gz tidy exits 0 when it has findings.",
            "The exit status of gz tidy means nothing.",
            "Tidy reports findings but exits 0.",
            "Tidy exits 0, whatever it reports.",
            "gz tidy exits 0, regardless of findings.",
            "gz tidy exits 0 when the report ran, whatever it found.",
            (
                "Tidy exits 0 whatever it finds and exits 1 only when the project is "
                "not initialized."
            ),
        )
        contract = (
            (
                "A finding in any of the first three sections is a policy breach: the run "
                "prints `✗ Maintenance breaches found.` and exits 3 (GHI #1124). It exits 0 "
                "with `✓ All checks passed. Project is tidy.` only when none of them has a "
                "finding, and 1 when the project is not initialized"
            ),
            (
                '| "Tidy exited 0, so there is nothing to report" | Exit 0 says only that no '
                "breach section has a finding. The ADRs pending attestation still print, "
                "never gate, and are the operator's queue to hear about. |"
            ),
            "- Treating exit 3 as a failed run instead of reading which section breached",
            '``tidy.tidy`` once exited 0 with 456 findings and printed "Project is tidy"',
            "`gz check` always exits 0 whatever it reports.",
            "Tidy exits 0 even when ADRs pending attestation print.",
            "gz tidy exits 0 only when no breach section has a finding.",
            "If the --fix sync succeeds, tidy re-validates whatever tree the sync left.",
            (
                "Tidy always prints the pending queue and exits 0 only when no breach "
                "section has a finding."
            ),
        )
        for text in stale:
            with self.subTest(stale=text):
                self.assertTrue(stale_tidy_status_claims(text))
        for text in contract:
            with self.subTest(contract=text):
                self.assertFalse(stale_tidy_status_claims(text))

    def test_a_missing_root_is_a_finding_on_gzkits_tree_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            framework = _tree(Path(tmp), {"src/gzkit/__init__.py": ""})
            on_gzkit = {e.artifact for e in audit_tidy_verdict_citations(framework)}
        with tempfile.TemporaryDirectory() as tmp:
            on_adopter = audit_tidy_verdict_citations(Path(tmp))
        expected = set(ROOTS) - {"src/gzkit"} | set(ROOT_FILES) | set(DATED_RECORDS)
        self.assertEqual(on_gzkit, expected)
        self.assertEqual(on_adopter, [])

    def test_message_names_the_contract_and_the_recovery_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {".gzkit/skills/s/SKILL.md": _STALE})
            (error,) = audit_tidy_verdict_citations(root)
        self.assertIn(".gzkit/skills/s/SKILL.md", error.message)
        self.assertIn("exits 3", error.message)
        self.assertIn("uv run gz validate --tidy-verdict-citations", error.message)


class DispatchAndControlTests(unittest.TestCase):
    """The scope runs in the default tier, and its control fails when the scope narrows."""

    def test_scope_runs_in_the_default_tier(self) -> None:
        entries = {e.stem: e for e in validate_cmd.VALIDATOR_REGISTRY}
        self.assertEqual("default", entries["tidy_verdict_citations"].tier)

    def _control_outcome(self) -> str:
        records = {r.claim_id: r for r in production_enforcement_registry()}
        return _run_single_claim(records["tidy-verdict-citations"]).outcome

    def test_the_control_catches_its_fixture(self) -> None:
        self.assertEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_scope_drops_a_root(self) -> None:
        with patch.object(tidy_verdict_citations, "ROOTS", ROOTS[1:]):
            self.assertNotEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_dated_records_are_read(self) -> None:
        with patch.object(tidy_verdict_citations, "DATED_RECORDS", ()):
            self.assertNotEqual(self._control_outcome(), "PASS")


if __name__ == "__main__":
    unittest.main()
