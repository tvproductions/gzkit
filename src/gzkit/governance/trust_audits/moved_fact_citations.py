"""No live surface restates two facts the 2026-09-17 rewrite moved or dropped (GHI #1374).

The 2026-09-17 rewrite of root `AGENTS.md` (8ecb176f0, GHI #921) moved the canonical
receipt invocations out of its attestation section into the `gz-arb` skill, carried the
em-dash pattern nowhere (compression sweep S23), and by operator ruling dropped the
recent-fix-commit count from defect-fix routing as a criterion (S14,
`docs/governance/defect-fix-routing.md`). Consumers kept restating both, `ghi-triage`'s
routing among them; that behavior is witnessed by `tests/skills/test_ghi_triage_routing.py`.

This is a phrasing fence over prose in the form ruled for M9 (operator, 2026-11-26, "a"):
it claims only the shapes below. It splits text at sentence ends, blank lines and the
start of a list item or table row, drops backticks, collapses whitespace, and judges each
piece. A table row is judged whole unless a cell holds a sentence end. It refuses a piece
that:

- names the dropped criterion: the word for a prior fix together with its commit-count
  threshold or its day window; or
- places the em-dash pattern or the canonical invocations in the attestation section and
  does not name `gz-arb`, the invocations' current home.

The exact shapes are quoted in `tests/governance/test_audit_moved_fact_citations.py`,
which this scope does not read. A sentence holding an ISO date is a dated record and is
admitted, so a lineage line stays true as written.

It reads the `.md`, `.py`, `.json`, `.toml`, `.yaml` and `.yml` files under
`.gzkit/skills`, `.gzkit/rules`, `.gzkit/templates`, `.gzkit/agents`, `.gzkit/personas`,
`src/gzkit` and `docs/user`, and the root contracts, skipping any path through a `proofs`
or `archive` directory; other suffixes (the `.j2` templates among them) are not read. It
does not read `docs/governance`, which mixes live doctrine with dated records (the
routing doc keeps the replaced criterion as a record), so the consumers repaired there are
held by review only. Nor does it judge a restatement in other words, or one split across
sentences.

It began as the unit test `tests/policy/test_moved_and_dropped_facts_not_restated.py`,
which the tautology audit classed as a content echo; under the operator's ruling on #1370
("A") it is this scope, with its patterns unchanged.
"""

import re
from typing import TYPE_CHECKING

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.prose_fence import live_files, missing_roots

if TYPE_CHECKING:
    from pathlib import Path

_TYPE = "moved_fact_citations"
_PREFIX = "[moved-fact-citations]"
_SCOPE = "moved-fact-citations"

ROOTS = (
    ".gzkit/skills",
    ".gzkit/rules",
    ".gzkit/templates",
    ".gzkit/agents",
    ".gzkit/personas",
    "src/gzkit",
    "docs/user",
)
ROOT_FILES = ("AGENTS.md", "CLAUDE.md", "README.md")
SUFFIXES = (".md", ".py", ".json", ".toml", ".yaml", ".yml")
SKIPPED_PARTS = ("proofs", "archive")

_PRECEDENT = re.compile(r"\bprecedent", re.IGNORECASE)
_THRESHOLD = re.compile(r"(?:≥|>=)\s?3\b|\b60 days\b", re.IGNORECASE)
_ATTESTATION = re.compile(r"§ ?Attestation\b")
_MOVED = re.compile(r"\bem[- ]dash\b|\bcanonical[- ]invocation", re.IGNORECASE)
_GZ_ARB = re.compile(r"\bgz-arb\b")
_DATED = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_SENTENCE = re.compile(r"[.;!?]\s|\n\s*\n|\n(?=\s*(?:[-*+|]|\d+\.)\s?)")

_RECOVERY = (
    "restates a fact the 2026-09-17 AGENTS.md rewrite moved or dropped: the canonical "
    "receipt invocations live in the gz-arb skill, and the fix() precedent criterion left "
    "defect-fix routing (GHI #1374; docs/governance/defect-fix-routing.md). Point at gz-arb "
    "or the routing facts instead, then re-run `uv run gz validate --{scope}`."
)


def stale_restatements(text: str) -> list[str]:
    """Return each sentence of *text* that restates the dropped criterion or the moved home."""
    found: list[str] = []
    for sentence in _SENTENCE.split(text):
        flat = re.sub(r"\s+", " ", sentence.replace("`", "")).strip()
        if _DATED.search(flat):
            continue
        if (_PRECEDENT.search(flat) and _THRESHOLD.search(flat)) or (
            _ATTESTATION.search(flat) and _MOVED.search(flat) and not _GZ_ARB.search(flat)
        ):
            found.append(flat)
    return found


def audit_moved_fact_citations(project_root: Path) -> list[ValidationError]:
    """Fail closed on a live sentence restating a fact the AGENTS.md rewrite moved or dropped.

    Returns:
        One finding per offending sentence, plus one per declared root absent from
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
            for hit in stale_restatements(text)
        )
    return errors
