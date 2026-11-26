"""No live surface says `gz tidy`'s exit status ignores its findings (GHI #1373).

Since GHI #1124, `gz tidy` exits 3 when a breach section has a finding and 0 only
when none has (`src/gzkit/commands/tidy.py`; witnessed by
`tests/commands/test_tidy_verdict.py` and the `tidy-breach-exits-three` load-bearing
claim). The fix rewrote the gz-tidy skill's Overview and left two rows that still
stated the old behavior as the corrective "reality": "Tidy exits 0 whatever it
reports" and the red flag "Reading tidy's exit code instead of its output". This
fence refuses either shape on any live surface.

A sentence (within a paragraph, list item or table cell) is refused when it names
tidy and either says it exits 0 or succeeds whatever it finds or on a finding, or tells
the reader to distrust the exit code. Whitespace inside a block is collapsed before it
is split, so a wrapped phrase is still seen (the gap #1367 found in the size fence).
Known limits: a reworded claim that uses neither shape passes, and so does a claim
whose "tidy" sits in an earlier sentence. True sentences are admitted by shape: a
conditional after the zero is refused only when it names a finding or a breach ("exits 0
even when ADRs pending attestation print" passes), "succeeds" counts only with tidy as
its subject, and a clause (split at a comma or "and") stating the contract with "only
when" or "only if" is dropped before the rest of its sentence is judged. Dated records
stay as written: `docs/rnd/`, `docs/releases/`, chore proofs and archives are not read.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOTS = tuple(
    REPO / part
    for part in (
        ".gzkit/skills",
        ".gzkit/rules",
        ".gzkit/personas",
        ".gzkit/agents",
        ".gzkit/templates",
        ".gzkit/chores",
        ".gzkit/corpus",
        "docs",
        "src/gzkit",
        "data",
        "scripts",
        "features",
    )
)
ROOT_FILES = (REPO / "AGENTS.md", REPO / "CLAUDE.md", REPO / "README.md")
SUFFIXES = {".md", ".py", ".json", ".jsonl", ".toml", ".feature", ".yaml", ".yml"}
DATED_RECORDS = (REPO / "docs" / "rnd", REPO / "docs" / "releases")
SKIPPED_PARTS = {"proofs", "archive"}

_TIDY = re.compile(r"\btidy\b", re.IGNORECASE)
_ZERO = (
    r"\b(?:(?:exits?|exited|returns?|returned)\s+(?:status\s+|code\s+)?0"
    r"|tidy\s+(?:\w+\s+)?(?:succeeds?|succeeded|exits? successfully))\b"
)
_ANYWAY = r"\b(?:whatever|regardless|no matter|always)\b(?!-)"
_ON_FINDINGS = (
    r"\b(?:even\s+)?(?:with|when|on|despite|if)\s+(?:it has\s+|there are\s+)?"
    r"(?:a\s+|any\s+|its\s+)?(?:findings?|breach(?:es)?)\b"
)
_FINDINGS_THEN_ZERO = r"\b(?:findings?|breach(?:es)?)\b.*?\b(?:but|yet|still)\s+"
_STATUS_IGNORES_FINDINGS = re.compile(
    rf"{_ZERO}.*?{_ANYWAY}|{_ZERO}.*?{_ON_FINDINGS}|{_ANYWAY}.*?{_ZERO}"
    rf"|{_FINDINGS_THEN_ZERO}{_ZERO}",
    re.IGNORECASE,
)
_CONTRACT = re.compile(r"\bonly (?:when|if)\b", re.IGNORECASE)
_CLAUSE = re.compile(r"(,\s|\s+and\s+)")
_DISTRUST_EXIT_CODE = re.compile(
    r"\bexit (?:code|status)\b.*?\b(?:instead of|means nothing|is meaningless|tells you nothing)\b"
    r"|\b(?:ignore|disregard|never trust|do not trust|don't trust)\b.*?\bexit (?:code|status)\b",
    re.IGNORECASE,
)
_BLOCK = re.compile(r"\n\s*\n|\n(?=\s*(?:[-*+]|\d+\.|\|)\s)")
_SENTENCE = re.compile(r"[.;!?]\s|\||\",\s")


def stale_tidy_status_claims(text: str) -> list[str]:
    """Return each sentence of *text* that says tidy's exit status ignores its findings."""
    found: list[str] = []
    for block in _BLOCK.split(text):
        flat = re.sub(r"\s+", " ", block.replace("*", "").replace("`", ""))
        for sentence in _SENTENCE.split(flat):
            claim = _without_contract_clauses(sentence)
            if _TIDY.search(sentence) and (
                _STATUS_IGNORES_FINDINGS.search(claim) or _DISTRUST_EXIT_CODE.search(claim)
            ):
                found.append(sentence.strip())
    return found


def _without_contract_clauses(sentence: str) -> str:
    """Drop each clause that states the contract with "only when" or "only if"."""
    parts = _CLAUSE.split(sentence)
    kept = [part for part in parts[::2] if not _CONTRACT.search(part)]
    return ", ".join(kept)


def _live_files() -> list[Path]:
    paths = [path for root in ROOTS for path in sorted(root.rglob("*")) if path.is_file()]
    paths.extend(ROOT_FILES)
    return [
        path
        for path in paths
        if path.suffix in SUFFIXES
        and not any(path.is_relative_to(record) for record in DATED_RECORDS)
        and not SKIPPED_PARTS.intersection(path.relative_to(REPO).parts)
    ]


class TestTidyExitStatusIsTheVerdict(unittest.TestCase):
    def test_every_root_exists(self):
        missing = [p for p in (*ROOTS, *ROOT_FILES, *DATED_RECORDS) if not p.exists()]
        self.assertEqual(missing, [], "a fence root moved; update the roots")

    def test_no_live_surface_says_tidy_ignores_its_findings(self):
        offenders = [
            f"{path.relative_to(REPO).as_posix()}: {hit}"
            for path in _live_files()
            for hit in stale_tidy_status_claims(path.read_text(encoding="utf-8", errors="replace"))
        ]
        self.assertEqual(
            offenders,
            [],
            "gz tidy exits 3 on a breach (GHI #1124); say so, never that its exit "
            "status ignores its findings: " + "; ".join(offenders),
        )

    def test_the_fence_tells_a_stale_claim_from_the_contract(self):
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
            "gz tidy always succeeds, even with findings.",
            "The exit status of gz tidy means nothing.",
            "Tidy reports findings but exits 0.",
            "gz tidy exits successfully whatever it reports.",
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


if __name__ == "__main__":
    unittest.main()
