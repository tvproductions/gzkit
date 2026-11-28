"""Function and module size are cited from the threshold table, never restated (GHI #1366).

`.gzkit/rules/pythonic.md` § Size Limits: function and module size are the
`lizard_nloc` and `lizard_file_nloc` bands of `.gzkit/rules/complexity-thresholds.json`,
"Cite the table, never a number copied from it" (operator, 2026-11-13, RP-7 H2).
When the table moved off the old 50/600 numbers, the skills, a persona, a pool ADR
and twenty-seven docstrings kept restating them as the rule. This scope refuses a
restated number. The instruction surfaces may state no function or module size as a
number. Source may, but only as dated history: a line that also says "then", as in
"the 600-line cap then in force". Classes stay out of scope, because `pythonic.md`
owns that one number itself, and so does a measured size ("this 87-line function"),
which states no limit.

It began as the unit test `tests/policy/test_size_limits_cite_the_table.py`, which
the tautology audit classed as a content echo; under the operator's ruling on #1370
("A") it is this scope. The patterns and the "then" allowance are carried unchanged;
the known gaps in both are #1367's. One change is deliberate: files are decoded with
``errors="replace"`` where the test decoded strictly, so one non-UTF-8 file cannot
crash the scope (the #1309 class); the patterns are ASCII, so no limit is hidden.
"""

import re
from typing import TYPE_CHECKING

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.prose_fence import live_files, missing_roots

if TYPE_CHECKING:
    from pathlib import Path

_TYPE = "size_limit_citations"
_PREFIX = "[size-limit-citations]"
_SCOPE = "size-limit-citations"

INSTRUCTION_ROOTS = (
    ".gzkit/skills",
    ".gzkit/rules",
    ".gzkit/personas",
    ".gzkit/agents",
    ".gzkit/templates",
    "docs/user",
)
SOURCE_ROOT = "src/gzkit"
#: The authority itself names its bands' numbers.
_AUTHORITY = "complexity-thresholds"

_UNIT = r"(?:lines?|LOC|NLOC|SLOC)"
_NUM = r"(?:\d+|fifty|sixty|hundred)"
_SUBJECT = r"\b(?:functions?|modules?|methods?)\b"
_LIMIT = r"(?:cap|limit|ceiling|budget|guidance)"
_COMPARE = (
    r"(?:>|>=|≥|<=|≤|<|\bover\b|\bexceed\w*|\bunder\b|\bmax(?:imum)?\b"
    r"|\bat most\b|\bup to\b|\bfits in\b)"
)
PATTERNS = (
    # "functions exceeding N lines", "modules >N LOC", "a function over N lines"
    re.compile(rf"{_SUBJECT}[^.\n|]{{0,40}}?{_COMPARE}\s*{_NUM}[- ]?{_UNIT}\b", re.IGNORECASE),
    # "modules under the N-line cap"
    re.compile(
        rf"{_SUBJECT}[^.\n|]{{0,40}}?\b{_NUM}[- ]{_UNIT}\s+(?:\w+\s+)?{_LIMIT}\b", re.IGNORECASE
    ),
    # "the N-line module cap", "N-line function cap"
    re.compile(rf"\b{_NUM}[- ]{_UNIT}\s+{_SUBJECT}\s+(?:size\s+)?{_LIMIT}\b", re.IGNORECASE),
)
HISTORY = re.compile(r"\bthen\b", re.IGNORECASE)

_INSTRUCTION_RECOVERY = (
    "states a function or module size limit as a number. `.gzkit/rules/pythonic.md` "
    "§ Size Limits: cite the lizard_nloc / lizard_file_nloc bands of "
    ".gzkit/rules/complexity-thresholds.json, never a number copied from it (GHI #1366). "
    "Replace the number with the citation, then re-run `uv run gz validate --{scope}`."
)
_SOURCE_RECOVERY = (
    "states a function or module size limit as a number. Source may state one only as "
    'dated history ("the 600-line cap then in force"); otherwise cite the lizard_nloc / '
    "lizard_file_nloc bands of .gzkit/rules/complexity-thresholds.json "
    "(`.gzkit/rules/pythonic.md` § Size Limits, GHI #1366). Date the line or cite the "
    "table, then re-run `uv run gz validate --{scope}`."
)


def states_size_limit(line: str) -> bool:
    """Return whether *line* states a function or module size limit as a number."""
    return any(pattern.search(line) for pattern in PATTERNS)


def _scan(
    paths: list[Path], project_root: Path, *, history_allowed: bool, recovery: str
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for path in paths:
        rel = path.relative_to(project_root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            if not states_size_limit(line):
                continue
            if history_allowed and HISTORY.search(line):
                continue
            errors.append(
                ValidationError(
                    type=_TYPE,
                    artifact=f"{rel}:{number}",
                    message=f"{_PREFIX} {rel}:{number} {recovery.format(scope=_SCOPE)}",
                )
            )
    return errors


def audit_size_limit_citations(project_root: Path) -> list[ValidationError]:
    """Fail closed on a function or module size limit restated as a number.

    Returns:
        One finding per offending line, plus one per declared root absent from
        gzkit's own tree.

    """
    errors = missing_roots(
        project_root,
        (*INSTRUCTION_ROOTS, SOURCE_ROOT),
        error_type=_TYPE,
        prefix=_PREFIX,
        scope=_SCOPE,
    )
    instruction = [
        path
        for path in live_files(project_root, INSTRUCTION_ROOTS, suffixes=(".md",))
        if _AUTHORITY not in path.name
    ]
    errors.extend(
        _scan(instruction, project_root, history_allowed=False, recovery=_INSTRUCTION_RECOVERY)
    )
    source = live_files(project_root, (SOURCE_ROOT,), suffixes=(".py",))
    errors.extend(_scan(source, project_root, history_allowed=True, recovery=_SOURCE_RECOVERY))
    return errors
