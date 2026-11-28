"""No live surface says `gz tidy`'s exit status ignores its findings (GHI #1373).

Since GHI #1124, `gz tidy` exits 3 when a breach section has a finding and 0 only
when none has (`src/gzkit/commands/tidy.py`; witnessed by
`tests/commands/test_tidy_verdict.py` and the `tidy-breach-exits-three` load-bearing
claim). The fix rewrote the gz-tidy skill's Overview and left two rows that still
stated the old behavior as the corrective "reality": one said tidy's zero exit holds
whatever it reports, and a red flag warned against reading its exit code over its
output. This scope refuses either shape on any live surface; the shapes are quoted
in `tests/governance/test_audit_tidy_verdict_citations.py`, which it does not read.

This is a phrasing fence over prose, narrowed by operator ruling (2026-11-26, "a") to
the shapes it judges reliably. It began as the unit test
`tests/policy/test_tidy_exit_status_is_the_verdict.py`, which the tautology audit classed
as a content echo; under the operator's ruling on #1370 ("A") it is this scope, with its
patterns unchanged. It reads each sentence (a
paragraph, list item or table cell, split at sentence ends, with whitespace collapsed so
a wrapped phrase is still seen) that names tidy, and refuses one that:

- holds a zero phrase ("exits", "exit", "exited", "returns", "return" or "returned",
  an optional "status" or "code", then 0) and "whatever", "regardless", "no matter"
  or "always", in either order;
- holds a zero phrase followed later by "with", "when", "on", "despite" or "if"
  (optionally after "even"), then "finding(s)" or "breach(es)" with nothing between
  but an optional "it has" or "there are" and an optional "a", "any" or "its";
- names a finding or breach, then "but", "yet" or "still" immediately before a zero
  phrase; or
- holds "exit code" or "exit status" followed later by "instead of", "means nothing",
  "is meaningless" or "tells you nothing", or holds "ignore", "disregard", "never
  trust", "do not trust" or "don't trust" followed later by "exit code" or "exit
  status".

Before judging, it drops each clause (split at a comma or "and") that holds "only
when" or "only if", so the contract stated that way is admitted.

What it does not judge: "succeeds", "passes" or any wording without a literal 0; a
claim whose "tidy" sits in an earlier sentence; a stale claim inside a clause that
also holds "only when" or "only if". It refuses some true sentences that pair a zero
with "regardless" or "whatever" about something other than findings, such as the
count of ADRs pending attestation; reword such a sentence rather
than widen the fence. Dated records stay as written: `docs/rnd/`, `docs/releases/`,
chore proofs and archives are not read.
"""

import re
from typing import TYPE_CHECKING

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.prose_fence import live_files, missing_roots

if TYPE_CHECKING:
    from pathlib import Path

_TYPE = "tidy_verdict_citations"
_PREFIX = "[tidy-verdict-citations]"
_SCOPE = "tidy-verdict-citations"

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
DATED_RECORDS = ("docs/rnd", "docs/releases")
SKIPPED_PARTS = ("proofs", "archive")

_TIDY = re.compile(r"\btidy\b", re.IGNORECASE)
_ZERO = r"\b(?:exits?|exited|returns?|returned)\s+(?:status\s+|code\s+)?0\b"
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


_RECOVERY = (
    "says gz tidy's exit status ignores its findings. Since GHI #1124 `gz tidy` exits 3 "
    "on a breach and 0 only when no breach section has a finding "
    "(`src/gzkit/commands/tidy.py`; GHI #1373). State that contract instead, then re-run "
    "`uv run gz validate --{scope}`."
)


def audit_tidy_verdict_citations(project_root: Path) -> list[ValidationError]:
    """Fail closed on a live sentence that says tidy's exit status ignores its findings.

    Returns:
        One finding per offending sentence, plus one per declared root absent from
        gzkit's own tree.

    """
    errors = missing_roots(
        project_root,
        (*ROOTS, *ROOT_FILES, *DATED_RECORDS),
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
    )
    for path in paths:
        rel = path.relative_to(project_root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        errors.extend(
            ValidationError(
                type=_TYPE,
                artifact=rel,
                message=f"{_PREFIX} {rel}: {claim!r} {_RECOVERY.format(scope=_SCOPE)}",
            )
            for claim in stale_tidy_status_claims(text)
        )
    return errors
