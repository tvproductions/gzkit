"""Tests for ``audit_size_limit_citations`` (GHI #1366, ported by #1370, widened by #1367).

Function and module size are the threshold table's bands; no live surface may
state one as a number, and dated history passes only in an anchored form. The
audit reads fixture trees here; the live tree is read by the `gz check` step that
runs the scope. This file is not one of the scope's roots, so it quotes the
refused shapes verbatim.
"""

import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.commands import validate_cmd
from gzkit.enforcement import _run_single_claim, production_enforcement_registry
from gzkit.governance.trust_audits import audit_size_limit_citations, size_limit_citations
from gzkit.governance.trust_audits.size_limit_citations import (
    ROOT_FILES,
    ROOTS,
    size_limit_sentences,
    states_size_limit,
)


def _tree(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    return root


def _undated(text: str, *, python: bool = False) -> bool:
    return bool(size_limit_sentences(text, python=python))


#: #1367 F1: the phrasings the #1366 re-review found the first fence missing.
F1_PHRASINGS = (
    "keep functions short, about 40 lines",
    "Split a 600 LOC module.",
    "Keep file length ≤ 500.",
    "Keep each function to 40 lines or fewer",
    "no function longer than 50 lines",
    "modules beyond 600 lines get split",
    "Max function length: 50 lines",
    "files over 600 lines",
    "a module of more than 600 lines",
    "function bodies above 50 lines",
    "split any module past 600 lines",
    "module size limit: 600 lines",
    "Functions: 50 lines max",
    "keep modules below 600 lines",
    "Keep modules under six hundred lines.",
    "A function longer than fifty lines",
)

#: The text of the #1366 sites before their fixes (`git show e36d313e2^`, `f3a3c0e93^`).
PRE_FIX_SITES = {
    "gz-tech-debt-review:150": (
        "| `size-cap` | `uv run lizard <files>` | Filter to functions >50, modules >600, "
        "classes >300. |"
    ),
    "gz-obpi-simplify persona :18": "modification. A function that fits in fifty lines is not",
    "quality-reviewer persona :33": "A function over fifty lines is not inherently wrong",
    "pool ADR B3": (
        "sibling-module proposal. The 600-line module cap and 50-line function cap\n"
        "from `.claude/rules/pythonic.md` are the floor."
    ),
    "governance-core-rationale N2": (
        "`.gzkit/rules/pythonic.md` carries\n`Modules <=600` while the execution authority is"
    ),
}

#: The two pre-fix docstrings whose phrase wrapped across lines (re-review § 2).
PRE_FIX_WRAPPED_DOCSTRINGS = {
    "ceremony_state.py": (
        '"""Ceremony state models.\n\nExtracted from ``closeout_ceremony.py`` to keep both '
        "modules under the\n600-line budget (`.claude/rules/pythonic.md`; precedent).\n"
        '"""\n'
    ),
    "hooks/scripts/mx.py": (
        '"""MX-mode hook script sources (ADR-0.0.74).\n\nKeeping these out of '
        "``validation.py`` holds that module under the\n600-line ceiling and keeps the MX "
        'surface a single discoverable concern.\n"""\n'
    ),
}


#: The #1367 review's counterexamples (B1 to B4, N1, N4): limits a phrasing list missed.
REVIEW_COUNTEREXAMPLES = (
    "Keep functions to 50 lines.",
    "Keep modules to 600 lines.",
    "Keep functions under 50 lines of code.",
    "No function should exceed 50 lines of code.",
    "The module size limit is 600 lines.",
    "The function cap is 50 lines.",
    "Modules are capped at 600 lines.",
    "Limit functions to 50 lines.",
    "Functions should be 50 lines at most.",
    "Split any function that reaches 50 lines.",
    "Functions >50 get split.",
    "modules >600 should be broken up.",
    "pythonic.md carries Modules <=600 while the table is the authority.",
    "Truncate module output over 50 lines, and keep modules under 600 lines.",
    "Keep _functions_ over 50 lines out.",
    "Aim for 50 lines per function.",
)

#: Live sentences a proximity test must not refuse: one measured unit, a change's
#: size counted in files, and shell redirection (measured on the tree, 2026-11-28).
LIVE_NON_LIMITS = (
    '"This 87-line function has three responsibility boundaries" is actionable',
    "This function was the cleanest thing to move: 83 lines, one caller.",
    "Phase 2 routes to direct fix (≤30 lines, 2 files: the brief and the WBS row).",
    "adds two new unit tests — roughly 80 lines across 3 files",
    "The 80-line / 3-file count is a routing fact recorded in the commit body.",
    "Run `uv run gz tidy > <file> 2>&1` and read the file.",
    "wc -l # 13 over 300 lines git ls-files",
    "the defect-fix routing thresholds (≤10 lines / ≤2 files)",
    "| Module >5s total | `setUp` runs expensive ops per test |",
    "it failed `cli/parser_governance.py` (1010 SLOC) — a module the corpus does not block",
)


class PhrasingTests(unittest.TestCase):
    """The fence refuses the phrasings a model writes and admits what states no limit."""

    def test_every_f1_phrasing_is_a_limit(self) -> None:
        for text in F1_PHRASINGS:
            with self.subTest(text=text):
                self.assertTrue(_undated(text))

    def test_every_review_counterexample_is_a_limit(self) -> None:
        for text in REVIEW_COUNTEREXAMPLES:
            with self.subTest(text=text):
                self.assertTrue(_undated(text))

    def test_live_measurements_and_change_sizes_pass(self) -> None:
        for text in LIVE_NON_LIMITS:
            with self.subTest(text=text):
                self.assertFalse(_undated(text))

    def test_a_bound_on_one_named_unit_is_still_a_limit(self) -> None:
        self.assertTrue(_undated("Keeping these out holds that module under the 600-line ceiling."))

    def test_every_pre_fix_site_is_refused(self) -> None:
        for site, text in PRE_FIX_SITES.items():
            with self.subTest(site=site):
                self.assertTrue(_undated(text))
        for site, text in PRE_FIX_WRAPPED_DOCSTRINGS.items():
            with self.subTest(site=site):
                self.assertTrue(_undated(text, python=True))

    def test_the_first_fences_phrasings_are_still_limits(self) -> None:
        for text in (
            "Functions exceeding 50 lines or modules exceeding 600 lines",
            "| size-cap | Functions >50 LOC, modules >600 LOC |",
            "The 600-line module cap and 50-line function cap are the floor.",
            "Extracted to keep both modules under the 600-line cap.",
        ):
            with self.subTest(text=text):
                self.assertTrue(states_size_limit(text))

    def test_what_states_no_limit_passes(self) -> None:
        for text in (
            "This 87-line function has three responsibility boundaries.",
            "Classes >300 lines (pythonic.md owns this one).",
            "Past the warn band of lizard_nloc in the threshold table.",
            "Instruction files: trim before attestation (200-line ceiling).",
            "Flag functions over 5 parameters.",
            "I am NOT writing >50 lines of business logic",
            # #1367 F4: output, logs and counts are not a size limit.
            "Truncate module output over 50 lines",
            "functions that exceed 50 lines of log output",
            "Rules 150,889 B in 26 files, 20 files over 4,000 chars.",
        ):
            with self.subTest(text=text):
                self.assertFalse(_undated(text))


class HistoryTests(unittest.TestCase):
    """Dated history passes only in an anchored form (#1367 F3, F4)."""

    def test_anchored_history_passes(self) -> None:
        for text in (
            "Split to stay under the 600-line module cap then in force.",
            (
                "Held apart under the 600-line module size limit then in\n"
                "``.gzkit/rules/pythonic.md``."
            ),
            "The module was 735 lines (over 600 lines at the time)",
            "modules exceeding 600 lines: 51 (2026-08-16 census)",
            "pythonic.md carried `Modules <=600` (until 227ed3386, 2026-11-13) while",
        ):
            with self.subTest(text=text):
                self.assertTrue(states_size_limit(text))
                self.assertFalse(_undated(text))

    def test_history_anchors_carry_a_date_or_a_commit(self) -> None:
        for text in (
            "At the time of writing, keep functions under 50 lines.",
            "Keep functions under 50 lines until 1234567 is merged.",
        ):
            with self.subTest(text=text):
                self.assertTrue(_undated(text))

    def test_a_bare_then_is_not_history(self) -> None:
        for text in (
            "if a module is over 600 lines then split it",
            "functions under 50 lines were then reviewed",
        ):
            with self.subTest(text=text):
                self.assertTrue(_undated(text))

    def test_history_in_another_sentence_does_not_admit_a_limit(self) -> None:
        self.assertTrue(_undated("The cap then in force was moved. Keep modules under 600 lines."))


class AuditTests(unittest.TestCase):
    def _artifacts(self, files: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            return [e.artifact for e in audit_size_limit_citations(_tree(Path(tmp), files))]

    def test_a_limit_on_each_root_and_root_file_is_flagged(self) -> None:
        body = "intro\n\nKeep functions under 50 lines.\n"
        files = {f"{rel}/x.md": body for rel in ROOTS} | dict.fromkeys(ROOT_FILES, body)
        self.assertEqual(
            sorted(self._artifacts(files)),
            sorted([f"{rel}/x.md:3" for rel in ROOTS] + [f"{rel}:3" for rel in ROOT_FILES]),
        )

    def test_python_is_read_as_its_strings_and_comments(self) -> None:
        artifacts = self._artifacts(
            {
                "src/gzkit/a.py": (
                    "LIMIT = 50  # keep functions under 50 lines\n"
                    "if len(modules) > 0:\n    pass\n"
                    '"""Keep modules under the 600-line cap."""\n'
                ),
            }
        )
        self.assertEqual(artifacts, ["src/gzkit/a.py:1", "src/gzkit/a.py:4"])

    def test_a_comment_run_is_one_block_so_a_wrapped_limit_is_seen(self) -> None:
        artifacts = self._artifacts(
            {"src/gzkit/a.py": "x = 1\n# Keep modules under\n# 600 lines.\ny = 2\n"}
        )
        self.assertEqual(artifacts, ["src/gzkit/a.py:2"])

    def test_source_that_does_not_tokenize_is_still_read(self) -> None:
        artifacts = self._artifacts(
            {"src/gzkit/a.py": 'x = (\n"""Keep modules under the 600-line cap.\n'}
        )
        self.assertEqual(artifacts, ["src/gzkit/a.py:1"])

    def test_dated_records_proofs_and_pool_adrs_are_not_read(self) -> None:
        limit = "Keep functions under 50 lines.\n"
        artifacts = self._artifacts(
            {
                "docs/governance/campaign-2026-09-20.md": limit,
                "docs/governance/harbor-ro7-placement.md": limit,
                "docs/governance/rule-version-history.md": limit,
                "docs/governance/rules-tools-audits-refactors-alignment.md": limit,
                ".gzkit/chores/c/proofs/p.md": limit,
                "docs/design/adr/pool/ADR-pool.x.md": limit,
                ".gzkit/rules/complexity-thresholds.md": limit,
                ".gzkit/rules/notes.txt": limit,
            }
        )
        self.assertEqual(artifacts, [])

    def test_a_missing_root_is_a_finding_on_gzkits_tree_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            framework = _tree(Path(tmp), {"src/gzkit/__init__.py": ""})
            on_gzkit = {e.artifact for e in audit_size_limit_citations(framework)}
        with tempfile.TemporaryDirectory() as tmp:
            on_adopter = audit_size_limit_citations(Path(tmp))
        self.assertEqual(on_gzkit, {*ROOTS, *ROOT_FILES} - {"src/gzkit"})
        self.assertEqual(on_adopter, [])

    def test_message_names_the_rule_and_the_recovery_command(self) -> None:
        # output-contract: guardrail-feedback-prose — what failed, why, the governed next step
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {".gzkit/skills/s/SKILL.md": "modules >600 LOC\n"})
            (error,) = audit_size_limit_citations(root)
        self.assertIn(".gzkit/skills/s/SKILL.md:1", error.message)
        self.assertIn("modules >600 LOC", error.message)
        self.assertIn("pythonic.md", error.message)
        self.assertIn("complexity-thresholds.json", error.message)
        self.assertIn('"then in force"', error.message)
        self.assertIn("uv run gz validate --size-limit-citations", error.message)


class DispatchAndControlTests(unittest.TestCase):
    """The scope runs in the default tier, and its control fails when the scope narrows."""

    def test_scope_runs_in_the_default_tier(self) -> None:
        entries = {e.stem: e for e in validate_cmd.VALIDATOR_REGISTRY}
        self.assertEqual("default", entries["size_limit_citations"].tier)

    def _control_outcome(self) -> str:
        records = {r.claim_id: r for r in production_enforcement_registry()}
        return _run_single_claim(records["size-limit-citations"]).outcome

    def test_the_control_catches_its_fixture(self) -> None:
        self.assertEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_scope_drops_a_root(self) -> None:
        for narrowed in (ROOTS[1:], tuple(r for r in ROOTS if r != "docs/governance")):
            with (
                self.subTest(narrowed=narrowed),
                patch.object(size_limit_citations, "ROOTS", narrowed),
            ):
                self.assertNotEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_history_allowance_is_lost_or_loosened(self) -> None:
        for history in (re.compile(r"(?!)"), re.compile(r"\bthen\b")):
            with (
                self.subTest(history=history.pattern),
                patch.object(size_limit_citations, "HISTORY", history),
            ):
                self.assertNotEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_a_phrasing_is_lost(self) -> None:
        for index in range(len(size_limit_citations.PATTERNS)):
            patterns = size_limit_citations.PATTERNS
            kept = patterns[:index] + patterns[index + 1 :]
            with self.subTest(dropped=index), patch.object(size_limit_citations, "PATTERNS", kept):
                self.assertNotEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_dated_records_are_read(self) -> None:
        with patch.object(size_limit_citations, "DATED_RECORD", re.compile(r"(?!)")):
            self.assertNotEqual(self._control_outcome(), "PASS")


if __name__ == "__main__":
    unittest.main()
