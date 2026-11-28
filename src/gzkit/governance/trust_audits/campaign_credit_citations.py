"""No live surface credits `AGENTS.md` with naming or ruling the campaign (GHI #1376).

The 2026-09-17 rewrite of root `AGENTS.md` (8ecb176f0, GHI #921) moved the campaign
doctrine bullet out of § Operator Doctrine; campaign work selection is now carried
verbatim by `gz-obpi-pipeline`, and 64f35c53e removed the last mention.
`gz-intent-trace` and `docs/governance/untrusted-content.md` went on crediting
`AGENTS.md` with it.

This is a phrasing fence over prose in the form ruled for M9 (operator, 2026-11-26, "a"):
it claims only one shape, spelled in the patterns below and quoted in
`tests/governance/test_audit_campaign_credit_citations.py`, which this scope does not
read. It drops backticks and splits text into pieces at a ".", ";", "!" or "?" followed
by whitespace, at a blank line, and before a line that, after any leading whitespace,
opens a list item ("-", "*" or "+" then whitespace, or a number, "." and whitespace) or a
table row ("|"); a wrapped line opening with emphasis does not start a piece. It
collapses whitespace and refuses a piece that names the campaign, or quotes the phrase
by which its plan was said to govern each session, together with the root contract's
file name or the title of its doctrine section. A piece holding an ISO date (YYYY-MM-DD)
is admitted as a dated record, which also admits a live credit that carries a date.

It reads the `.md`, `.py`, `.json`, `.toml`, `.yaml` and `.yml` files under
`.gzkit/skills`, `.gzkit/rules`, `.gzkit/templates`, `.gzkit/agents`, `.gzkit/personas`,
`.gzkit/chores`, `src/gzkit`, `scripts`, `data`, `docs/user` and `docs/governance`, and the
root contracts. It skips any path through a `proofs` or `archive` directory, any path with
a directory or file name holding an ISO date (dated plans, audits and snapshots), and
`docs/governance/rule-version-history.md`, which is version history. It misses a credit in
other words or one split across pieces, and it cannot tell a negation from a credit, so it
refuses one.

It began as the unit test `tests/policy/test_campaign_not_credited_to_agents_md.py`,
which the tautology audit classed as a content echo; under the operator's ruling on #1370
("A") it is this scope, with its patterns unchanged.
"""

import re
from typing import TYPE_CHECKING

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.prose_fence import live_files, missing_roots

if TYPE_CHECKING:
    from pathlib import Path

_TYPE = "campaign_credit_citations"
_PREFIX = "[campaign-credit-citations]"
_SCOPE = "campaign-credit-citations"

ROOTS = (
    ".gzkit/skills",
    ".gzkit/rules",
    ".gzkit/templates",
    ".gzkit/agents",
    ".gzkit/personas",
    ".gzkit/chores",
    "src/gzkit",
    "scripts",
    "data",
    "docs/user",
    "docs/governance",
)
ROOT_FILES = ("AGENTS.md", "CLAUDE.md", "README.md")
SUFFIXES = (".md", ".py", ".json", ".toml", ".yaml", ".yml")
SKIPPED_PARTS = ("proofs", "archive")
HISTORY_FILES = ("docs/governance/rule-version-history.md",)

_CAMPAIGN = re.compile(r"\bmagna carta\b|\brules every session\b", re.IGNORECASE)
_CANON = re.compile(r"\bAGENTS\.md\b|\bOperator Doctrine\b")
_DATED = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_SENTENCE = re.compile(r"[.;!?]\s|\n\s*\n|\n(?=\s*(?:[-*+]\s|\||\d+\.\s))")


def campaign_credited_to_canon(text: str) -> list[str]:
    """Return each piece of *text* that credits `AGENTS.md` with the campaign doctrine."""
    found: list[str] = []
    for sentence in _SENTENCE.split(text):
        flat = re.sub(r"\s+", " ", sentence.replace("`", "")).strip()
        if _DATED.search(flat):
            continue
        if _CAMPAIGN.search(flat) and _CANON.search(flat):
            found.append(flat)
    return found


_RECOVERY = (
    "credits AGENTS.md with naming or ruling the campaign. Campaign work selection is "
    "carried by gz-obpi-pipeline, and AGENTS.md no longer names or rules the campaign "
    "(GHI #1376). Cite gz-obpi-pipeline or the campaign plan instead, then re-run "
    "`uv run gz validate --{scope}`."
)


def audit_campaign_credit_citations(project_root: Path) -> list[ValidationError]:
    """Fail closed on a live piece crediting AGENTS.md with the campaign doctrine.

    Returns:
        One finding per offending piece, plus one per declared root or history
        file absent from gzkit's own tree.

    """
    errors = missing_roots(
        project_root,
        (*ROOTS, *ROOT_FILES, *HISTORY_FILES),
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
        exclude=HISTORY_FILES,
        skip_part_matching=_DATED,
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
            for hit in campaign_credited_to_canon(text)
        )
    return errors
