"""Dependency currency is graded by its chore, never restated as an age (GHI #1368).

`.gzkit/chores/dependency-currency/CHORE.md` owns the grading: every dependency is
brought to upstream latest each run, and a complexity analyzer whose release is
older than its stated age is stale, abandoned only on evidence. The
`gz-tech-debt-review` skill restated a currency grade the chore never held
(">5y", ">2y stale (not yet 5y)"). This scope refuses a dependency age stated as
a currency grade on any live surface other than that chore.

Out of scope, by operator ruling 2026-11-25 ("Separate them (Recommended)"): the
STDLIB-FIRST adoption signal, "Five-year aging is the minimum signal for
ecosystem trust", which judges how long a library has existed before gzkit adopts
it, not how far a pin lags. It carries no currency word, so it passes.

Each file is read whole and split into blocks (paragraphs, list items, table
rows), then into clauses; a clause that names a dependency, an age and a currency
word is a grade, so a grade split across clauses by a comma is a known limit.
Whitespace inside a block is collapsed, so a phrase wrapped across lines is still
seen. Dated records stay as written: `docs/rnd/`, chore proofs and archives are
not read.

It began as the unit test `tests/policy/test_dependency_currency_cites_the_chore.py`,
which the tautology audit classed as a content echo; under the operator's ruling on
#1370 ("A") it is this scope, with its patterns unchanged. The phrasings the #1368
re-review found it missing are recorded on #1370.
"""

import re
from typing import TYPE_CHECKING

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.prose_fence import live_files, missing_roots

if TYPE_CHECKING:
    from pathlib import Path

_TYPE = "dependency_currency_citations"
_PREFIX = "[dependency-currency-citations]"
_SCOPE = "dependency-currency-citations"

ROOTS = (
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
ROOT_FILES = ("AGENTS.md", "CLAUDE.md", "README.md")
SUFFIXES = (".md", ".py", ".json", ".jsonl", ".toml", ".feature", ".yaml", ".yml")
DATED_RECORDS = ("docs/rnd",)
AUTHORITY = (
    ".gzkit/chores/dependency-currency/CHORE.md",
    "src/gzkit/chores/dependency-currency/CHORE.md",
)
SKIPPED_PARTS = ("proofs", "archive")

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

_RECOVERY = (
    "states a dependency age as a currency grade. "
    "`.gzkit/chores/dependency-currency/CHORE.md` owns the grading (GHI #1368); a "
    "second statement of it drifts from the chore. Cite the chore instead of the age, "
    "then re-run `uv run gz validate --{scope}`."
)


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


def _authority_without_grade(project_root: Path) -> list[ValidationError]:
    """Return a finding for each present authority whose text states no grade.

    The fence refuses elsewhere what the chore states. A chore that no longer
    states it leaves every citation pointing at nothing.

    Returns:
        One finding per authority file that exists and holds no currency grade.

    """
    errors: list[ValidationError] = []
    for rel in AUTHORITY:
        path = project_root / rel
        if path.is_file() and not currency_ages(path.read_text(encoding="utf-8")):
            errors.append(
                ValidationError(
                    type=_TYPE,
                    artifact=rel,
                    message=(
                        f"{_PREFIX} {rel} states no currency grade, so every surface "
                        "citing it cites nothing (GHI #1368). Restore the chore's grade "
                        f"line, then re-run `uv run gz validate --{_SCOPE}`."
                    ),
                )
            )
    return errors


def audit_dependency_currency_citations(project_root: Path) -> list[ValidationError]:
    """Fail closed on a dependency age restated as a currency grade outside its chore.

    Returns:
        One finding per offending clause, plus one per declared root or authority
        absent from gzkit's own tree.

    """
    errors = missing_roots(
        project_root,
        (*ROOTS, *ROOT_FILES, *AUTHORITY),
        error_type=_TYPE,
        prefix=_PREFIX,
        scope=_SCOPE,
    )
    paths = live_files(
        project_root,
        ROOTS,
        suffixes=SUFFIXES,
        root_files=ROOT_FILES,
        skip_parts=SKIPPED_PARTS,
        skip_under=DATED_RECORDS,
        exclude=AUTHORITY,
    )
    errors.extend(_authority_without_grade(project_root))
    for path in paths:
        rel = path.relative_to(project_root).as_posix()
        for clause in currency_ages(path.read_text(encoding="utf-8", errors="replace")):
            errors.append(
                ValidationError(
                    type=_TYPE,
                    artifact=rel,
                    message=(f"{_PREFIX} {rel}: {clause!r} {_RECOVERY.format(scope=_SCOPE)}"),
                )
            )
    return errors
