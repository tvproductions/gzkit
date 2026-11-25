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

Each file is read whole with whitespace collapsed, so a phrase wrapped across
lines is still seen (the gap #1367 found in the size fence).
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
        "docs/user",
        "docs/governance",
        "docs/design/adr/pool",
        "src/gzkit",
    )
)
ROOT_FILES = (REPO / "AGENTS.md", REPO / "CLAUDE.md")
SUFFIXES = {".md", ".py", ".json", ".jsonl", ".toml"}
AUTHORITY = (
    REPO / ".gzkit/chores/dependency-currency/CHORE.md",
    REPO / "src/gzkit/chores/dependency-currency/CHORE.md",
)
SKIPPED_PARTS = {"proofs", "archive"}
WINDOW = 60

_AGE = re.compile(
    r"\b\d+(?:\.\d+)?\s?(?:y|yr|yrs|years?|months?|mo)\b"
    r"|\b(?:a|an|one|two|three|four|five|six|ten|twelve|eighteen)[- ](?:years?|months?)\b",
    re.IGNORECASE,
)
_CURRENCY = re.compile(
    r"\b(?:stale\w*|outdated|out[- ]of[- ]date|abandon\w*|unmaintained|lag(?:s|ging)?|behind)\b",
    re.IGNORECASE,
)
_SUBJECT = re.compile(
    r"\b(?:dependenc(?:y|ies)|deps?|packages?|releases?|pins?|librar(?:y|ies)|analy[sz]ers?)\b",
    re.IGNORECASE,
)


def currency_ages(text: str) -> list[str]:
    """Return each dependency age that *text* states as a currency grade."""
    flat = re.sub(r"\s+", " ", text.replace("*", "").replace("`", ""))
    found: list[str] = []
    for match in _AGE.finditer(flat):
        near = flat[max(0, match.start() - WINDOW) : match.end() + WINDOW]
        if _CURRENCY.search(near) and _SUBJECT.search(near):
            found.append(near.strip())
    return found


def _live_files() -> list[Path]:
    paths = [path for root in ROOTS for path in sorted(root.rglob("*")) if path.is_file()]
    paths.extend(ROOT_FILES)
    return [
        path
        for path in paths
        if path.suffix in SUFFIXES
        and path not in AUTHORITY
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
        )
        not_grades = (
            "Five-year aging is the minimum signal for ecosystem trust.",
            "TODOs older than 90 days, FIXMEs without GHI refs",
            "Maintenance health: active releases in last 12 months OR project declares done state.",
            "Stale (>6 months, no promotion signal): Candidate for archival with rationale.",
            "Dependencies behind upstream latest, as the dependency-currency chore grades them.",
        )
        for text in grades:
            with self.subTest(grade=text):
                self.assertTrue(currency_ages(text))
        for text in not_grades:
            with self.subTest(not_grade=text):
                self.assertFalse(currency_ages(text))


if __name__ == "__main__":
    unittest.main()
