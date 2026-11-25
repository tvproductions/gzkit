"""Function and module size are cited from the threshold table, never restated (GHI #1366).

`.gzkit/rules/pythonic.md` § Size Limits: function and module size are the
`lizard_nloc` and `lizard_file_nloc` bands of `.gzkit/rules/complexity-thresholds.json`,
"Cite the table, never a number copied from it" (operator, 2026-11-13, RP-7 H2).
When the table moved off the old 50/600 numbers, the skills, a persona, a pool ADR
and twenty-seven docstrings kept restating them as the rule. This fence refuses a
restated number. The instruction surfaces may state no function or module size as a
number. Source may, but only as dated history: a line that also says "then", as in
"the 600-line cap then in force". Classes stay out of scope, because `pythonic.md`
owns that one number itself, and so does a measured size ("this 87-line function"),
which states no limit.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTRUCTION_ROOTS = tuple(
    REPO / part
    for part in (
        ".gzkit/skills",
        ".gzkit/rules",
        ".gzkit/personas",
        ".gzkit/agents",
        ".gzkit/templates",
        "docs/user",
    )
)
SOURCE_ROOT = REPO / "src" / "gzkit"
AUTHORITY = "complexity-thresholds"

_UNIT = r"(?:lines?|LOC|NLOC|SLOC)"
_NUM = r"(?:\d+|fifty|sixty|hundred)"
_SUBJECT = r"\b(?:functions?|modules?|methods?)\b"
_LIMIT = r"(?:cap|limit|ceiling|budget|guidance)"
_COMPARE = (
    r"(?:>|>=|≥|<=|≤|<|\bover\b|\bexceed\w*|\bunder\b|\bmax(?:imum)?\b"
    r"|\bat most\b|\bup to\b|\bfits in\b)"
)
_PATTERNS = (
    # "functions exceeding 50 lines", "modules >600 LOC", "a function over fifty lines"
    re.compile(rf"{_SUBJECT}[^.\n|]{{0,40}}?{_COMPARE}\s*{_NUM}[- ]?{_UNIT}\b", re.IGNORECASE),
    # "modules under the 600-line cap"
    re.compile(
        rf"{_SUBJECT}[^.\n|]{{0,40}}?\b{_NUM}[- ]{_UNIT}\s+(?:\w+\s+)?{_LIMIT}\b", re.IGNORECASE
    ),
    # "the 600-line module cap", "50-line function cap"
    re.compile(rf"\b{_NUM}[- ]{_UNIT}\s+{_SUBJECT}\s+(?:size\s+)?{_LIMIT}\b", re.IGNORECASE),
)
_HISTORY = re.compile(r"\bthen\b", re.IGNORECASE)


def restated_size_limits(paths: list[Path], *, history_allowed: bool) -> list[str]:
    """Return each line that states a function or module size limit as a number."""
    found: list[str] = []
    for path in paths:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not any(pattern.search(line) for pattern in _PATTERNS):
                continue
            if history_allowed and _HISTORY.search(line):
                continue
            found.append(f"{path.relative_to(REPO).as_posix()}:{number}")
    return found


def _instruction_files() -> list[Path]:
    return [
        path
        for root in INSTRUCTION_ROOTS
        for path in sorted(root.rglob("*.md"))
        if AUTHORITY not in path.name
    ]


class TestSizeLimitsCiteTheTable(unittest.TestCase):
    def test_every_root_exists(self):
        missing = [root for root in (*INSTRUCTION_ROOTS, SOURCE_ROOT) if not root.is_dir()]
        self.assertEqual(missing, [], "a fence root moved; update the roots")

    def test_instruction_surfaces_state_no_size_number(self):
        offenders = restated_size_limits(_instruction_files(), history_allowed=False)
        self.assertEqual(
            offenders,
            [],
            "cite the lizard_nloc / lizard_file_nloc bands of "
            ".gzkit/rules/complexity-thresholds.json, never a number: " + ", ".join(offenders),
        )

    def test_source_states_a_size_number_only_as_history(self):
        paths = sorted(SOURCE_ROOT.rglob("*.py"))
        offenders = restated_size_limits(paths, history_allowed=True)
        self.assertEqual(
            offenders,
            [],
            'date it ("then in force") or cite the table: ' + ", ".join(offenders),
        )

    def test_the_fence_tells_a_limit_from_a_measurement(self):
        limits = (
            "Functions exceeding 50 lines or modules exceeding 600 lines",
            "| size-cap | Functions >50 LOC, modules >600 LOC |",
            "The 600-line module cap and 50-line function cap are the floor.",
            "A function over fifty lines is not inherently wrong.",
            "Extracted to keep both modules under the 600-line cap.",
        )
        not_limits = (
            "This 87-line function has three responsibility boundaries.",
            "Classes >300 lines (pythonic.md owns this one).",
            "Past the warn band of lizard_nloc in the threshold table.",
            "Instruction files: trim before attestation (200-line ceiling).",
        )
        for text in limits:
            with self.subTest(limit=text):
                self.assertTrue(any(p.search(text) for p in _PATTERNS))
        for text in not_limits:
            with self.subTest(not_limit=text):
                self.assertFalse(any(p.search(text) for p in _PATTERNS))

    def test_dated_history_passes_only_in_source(self):
        line = "Split to stay under the 600-line module cap then in force."
        self.assertTrue(any(p.search(line) for p in _PATTERNS))
        self.assertTrue(_HISTORY.search(line))


if __name__ == "__main__":
    unittest.main()
