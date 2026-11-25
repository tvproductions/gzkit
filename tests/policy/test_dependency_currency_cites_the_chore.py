"""Dependency currency is graded by its chore, never restated as an age (GHI #1368).

`.gzkit/chores/dependency-currency/CHORE.md` owns the grading: every dependency is
brought to upstream latest each run, and a complexity analyzer whose release is
older than its stated age is stale, abandoned only on evidence. The
`gz-tech-debt-review` skill restated a currency grade the chore never held
(">5y", ">2y stale (not yet 5y)"). This fence refuses a dependency age stated as
a currency grade on any live surface other than that chore.

Out of scope, by operator ruling 2026-11-25 ("Separate them (Recommended)"): the
STDLIB-FIRST adoption signal, "Five-year aging is the minimum signal for
ecosystem trust", which judges how long a library has existed before gzkit adopts
it, not how far a pin lags. It carries no currency word, so it passes.

Each file is read whole and split into blocks (paragraphs, list items, table
rows), then into clauses; a clause that names a dependency, an age and a currency
word is a grade, so a grade split across clauses by a comma is a known limit.
Whitespace inside a block is collapsed, so a phrase wrapped across
lines is still seen (the gap #1367 found in the size fence). Dated records stay as
written: `docs/rnd/`, chore proofs and archives are not read.
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
DATED_RECORDS = REPO / "docs" / "rnd"
AUTHORITY = (
    REPO / ".gzkit/chores/dependency-currency/CHORE.md",
    REPO / "src/gzkit/chores/dependency-currency/CHORE.md",
)
SKIPPED_PARTS = {"proofs", "archive"}

_AGE = re.compile(
    r"\b\d+(?:\.\d+)?\s?(?:y|yr|yrs|years?|months?|mo|weeks?|days?)\b"
    r"|\b(?:a|an|one|two|three|four|five|six|ten|twelve|eighteen)[- ]"
    r"(?:years?|months?|weeks?|days?)\b",
    re.IGNORECASE,
)
_CURRENCY = re.compile(
    r"\b(?:stale\w*|outdated|out[- ]of[- ]date|abandon\w*|unmaintained|lag(?:s|ged|ging)?"
    r"|behind|old(?:er)?|ago|no (?:new )?release|not (?:been )?updated"
    r"|since (?:the )?last release)\b",
    re.IGNORECASE,
)
_SUBJECT = re.compile(
    r"\b(?:dependenc(?:y|ies)|deps?|packages?|releases?|pins?|librar(?:y|ies)"
    r"|analy[sz]ers?|tools?|versions?|upstream)\b",
    re.IGNORECASE,
)
_BLOCK = re.compile(r"\n\s*\n|\n(?=\s*(?:[-*+]|\d+\.|\|)\s)")
_CLAUSE = re.compile(r"[.;:]\s|,\s|\|")


def currency_ages(text: str) -> list[str]:
    """Return each clause of *text* that states a dependency age as a currency grade."""
    found: list[str] = []
    for block in _BLOCK.split(text):
        flat = re.sub(r"\s+", " ", block.replace("*", "").replace("`", ""))
        found.extend(
            clause.strip()
            for clause in _CLAUSE.split(flat)
            if _AGE.search(clause) and _CURRENCY.search(clause) and _SUBJECT.search(clause)
        )
    return found


def _live_files() -> list[Path]:
    paths = [path for root in ROOTS for path in sorted(root.rglob("*")) if path.is_file()]
    paths.extend(ROOT_FILES)
    return [
        path
        for path in paths
        if path.suffix in SUFFIXES
        and path not in AUTHORITY
        and not path.is_relative_to(DATED_RECORDS)
        and not SKIPPED_PARTS.intersection(path.relative_to(REPO).parts)
    ]


class TestDependencyCurrencyCitesTheChore(unittest.TestCase):
    def test_every_root_exists(self):
        missing = [p for p in (*ROOTS, *ROOT_FILES, *AUTHORITY) if not p.exists()]
        self.assertEqual(missing, [], "a fence root moved; update the roots")

    def test_no_live_surface_restates_a_currency_age(self):
        offenders = [
            f"{path.relative_to(REPO).as_posix()}: {hit}"
            for path in _live_files()
            for hit in currency_ages(path.read_text(encoding="utf-8", errors="replace"))
        ]
        self.assertEqual(
            offenders,
            [],
            "cite .gzkit/chores/dependency-currency/CHORE.md, never an age: "
            + "; ".join(offenders),
        )

    def test_the_authority_states_its_grade(self):
        """A control: the chore's own line is what the fence would refuse elsewhere."""
        text = AUTHORITY[0].read_text(encoding="utf-8")
        self.assertTrue(currency_ages(text), "the chore no longer states its grade")

    def test_the_fence_tells_a_currency_grade_from_other_ages(self):
        grades = (
            (
                "| `dep-currency` | `dependency-currency` chore "
                "| Outdated runtime deps (>5y aging policy) |"
            ),
            "TODO older than 90 days, dependency >2y stale (not yet 5y), CLI verb registered",
            "Flag any dependency more than 18 months out of date.",
            "A package two years behind upstream is High.",
            "Dependencies\n   older than 2 years are\n   *stale*.",
            "An analyzer with no release in 1y is abandoned.",
            "A dependency not updated in 400 days is High.",
            "A pin 18 months old.",
            "The last release was 3 years ago for that library.",
            "No release for 24 months on the analyzer.",
            "Lagged upstream by 9 months.",
            "Deps over 1y old.",
            "Tool versions more than 6 months stale.",
            "A dependency older than 12 weeks.",
        )
        not_grades = (
            "Five-year aging is the minimum signal for ecosystem trust.",
            "TODOs older than 90 days, FIXMEs without GHI refs",
            "Maintenance health: active releases in last 12 months OR project declares done state.",
            "Stale (>6 months, no promotion signal): Candidate for archival with rationale.",
            "Dependencies behind upstream latest, as the dependency-currency chore grades them.",
            "TODO older than 90 days, a dependency or analyzer the dep-currency probe reports",
            "A library adopted after five years of releases.",
            "Runs ~1 week behind, skips releases with major regressions.",
            "- If ledger entries are older than 7 days\n- If Layer 1 tools have been updated",
            "rows 45b-45d landed; the rule left its grandfather pin behind at rule 0.6.0",
        )
        for text in grades:
            with self.subTest(grade=text):
                self.assertTrue(currency_ages(text))
        for text in not_grades:
            with self.subTest(not_grade=text):
                self.assertFalse(currency_ages(text))


if __name__ == "__main__":
    unittest.main()
