"""No live surface cites AGENTS.md numbering the 2026-09-17 rewrite dropped (GHI #1375).

The 2026-09-17 rewrite of root `AGENTS.md` (8ecb176f0, GHI #921) rendered § Behavior
Rules, § OPERATOR ECONOMY OF EFFORT and the anti-vibing claims as unnumbered bullets, and
kept only the 6c, 6g and 6h tags on DO IT RIGHT. Surfaces kept citing the old numbers:
a numbered Behavior Rule, a numbered Always or Never heading, a numbered Operator Economy
item, a numbered operative claim, or a dropped DO IT RIGHT tag.
`.gzkit/rules/skill-authoring.md` § Parsimony 2: text attributed to `AGENTS.md` is
quoted from the current file, by section name, or not quoted. GHI #1035 repaired the
same class in runtime messages on a grep and left no standing witness.

This is a phrasing fence over prose in the form ruled for M9 (operator, 2026-11-26, "a"):
it claims only the five shapes above, each spelled exactly in the patterns below and
quoted in `tests/governance/test_audit_agents_md_numbering_citations.py`, which this
scope does not read. It splits text at sentence ends, blank lines and the start of a list
item or table row, drops backticks and collapses whitespace. A numbered Always or Never
heading is admitted in a piece that names `behavior-rules.md`, which keeps its own
numbered headings, and a dropped tag is refused only in a piece that names DO IT RIGHT.
A piece holding a date (YYYY-MM or YYYY-MM-DD) is a dated record and is admitted.

It reads the `.md`, `.py`, `.json`, `.toml`, `.yaml` and `.yml` files under
`.gzkit/skills`, `.gzkit/rules`, `.gzkit/agents`, `.gzkit/personas`, `.gzkit/chores`,
`src/gzkit` and `docs/user`, and `AGENTS.md`, `CLAUDE.md`, `README.md` and
`.gitattributes`, skipping any path through a `proofs`, `archive` or `templates`
directory: the adopter template carries its own numbered Behavior Rules.
`src/gzkit/handoff_api.py` is skipped by name: its parser comments name the old
numbered heading as a text form the handoff corpus still holds. It does not read
`docs/governance`, which mixes live doctrine with dated records and lift anchors, so the
consumers repaired there are held by review only. `tests.md`'s own "invariant 6f" label
is not a shape here.

It began as the unit test `tests/policy/test_agents_md_numbering_not_cited.py`, which the
tautology audit classed as a content echo; under the operator's ruling on #1370 ("A") it
is this scope, with its patterns unchanged.
"""

import re
from typing import TYPE_CHECKING

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.prose_fence import live_files, missing_roots

if TYPE_CHECKING:
    from pathlib import Path

_TYPE = "agents_md_numbering_citations"
_PREFIX = "[agents-md-numbering-citations]"
_SCOPE = "agents-md-numbering-citations"

ROOTS = (
    ".gzkit/skills",
    ".gzkit/rules",
    ".gzkit/agents",
    ".gzkit/personas",
    ".gzkit/chores",
    "src/gzkit",
    "docs/user",
)
ROOT_FILES = ("AGENTS.md", "CLAUDE.md", "README.md", ".gitattributes")
SUFFIXES = (".md", ".py", ".json", ".toml", ".yaml", ".yml")
SKIPPED_PARTS = ("proofs", "archive", "templates")
SKIPPED_FILES = ("src/gzkit/handoff_api.py",)

_BEHAVIOR_RULE = re.compile(r"\bBehavior Rules?\W{0,4}(?:Always|Never)?\W{0,3}#?\d+")
_ALWAYS_NEVER = re.compile(r"\b(?:Always|Never) #\d+")
_ECONOMY = re.compile(r"Operator Economy.{0,30}#\d+")
_CLAIM = re.compile(r"\boperative claim \d+", re.IGNORECASE)
_DROPPED_TAG = re.compile(r"\(6[abdef]\)")
_DO_IT_RIGHT = re.compile(r"DO IT RIGHT")
_BEHAVIOR_DOC = re.compile(r"behavior-rules\.md")
_DATED = re.compile(r"\b\d{4}-\d{2}\b")
_SENTENCE = re.compile(r"[.;!?]\s|\n\s*\n|\n(?=\s*(?:[-*+|]|\d+\.)\s?)")


def _cites_dropped_number(flat: str) -> bool:
    """Return whether one collapsed piece holds a dropped-numbering shape."""
    shapes = (
        _BEHAVIOR_RULE.search(flat),
        _ALWAYS_NEVER.search(flat) and not _BEHAVIOR_DOC.search(flat),
        _ECONOMY.search(flat),
        _CLAIM.search(flat),
        _DROPPED_TAG.search(flat) and _DO_IT_RIGHT.search(flat),
    )
    return any(shapes)


def dropped_numbering(text: str) -> list[str]:
    """Return each piece of *text* that cites AGENTS.md numbering the rewrite dropped."""
    found: list[str] = []
    for piece in _SENTENCE.split(text):
        flat = re.sub(r"\s+", " ", piece.replace("`", "")).strip()
        if not _DATED.search(flat) and _cites_dropped_number(flat):
            found.append(flat)
    return found


_RECOVERY = (
    "cites AGENTS.md numbering the 2026-09-17 rewrite dropped. § Behavior Rules, "
    "§ OPERATOR ECONOMY and the anti-vibing claims are unnumbered since then (GHI #1375; "
    "`.gzkit/rules/skill-authoring.md` § Parsimony 2). Cite the section and quote the "
    "rule, then re-run `uv run gz validate --{scope}`."
)


def audit_agents_md_numbering_citations(project_root: Path) -> list[ValidationError]:
    """Fail closed on a live piece citing AGENTS.md numbering the rewrite dropped.

    Returns:
        One finding per offending piece, plus one per declared root absent from
        gzkit's own tree.

    """
    errors = missing_roots(
        project_root,
        (*ROOTS, *ROOT_FILES),
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
        exclude=SKIPPED_FILES,
    )
    for path in paths:
        rel = path.relative_to(project_root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        errors.extend(
            ValidationError(
                type=_TYPE,
                artifact=rel,
                message=f"{_PREFIX} {rel}: {hit!r} {_RECOVERY.format(scope=_SCOPE)}",
            )
            for hit in dropped_numbering(text)
        )
    return errors
