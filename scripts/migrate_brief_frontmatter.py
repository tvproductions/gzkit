"""Migrate live OBPI briefs onto the BriefStructure structured frontmatter.

GHI #615 cut 2. ``BriefStructure`` shipped with ADR-0.0.37-04 but ``parse_brief``
defaults to ``strict=False`` and the corpus never migrated, so briefs fall back
to ``LegacyBriefShape`` and are "validated" by regex-scraping the markdown body.

Scope is the **non-terminal** corpus. A terminal brief (``Completed``,
``attested_completed``, ``Abandoned``, ``Withdrawn``, ...) is a sealed historical
record: rewriting one would edit a governance artifact under an attestation no
operator can honestly give, and every consumer already scopes it out via
``is_terminal_brief_status``. Those stay legacy on purpose.

The three required fields are LIFTED from the body, never invented — each is the
exact extraction the legacy path already performed, so the migration changes the
CHANNEL and not the semantics:

* ``allowlist``    <- ``_extract_section_paths(body, ## Allowed Paths)``
* ``reqs``         <- ``_acceptance_req_ids(body)`` (Acceptance-Criteria checkbox
  ids -- the only place a legacy brief declares REQ identity, per GHI #664)
* ``verification`` <- the command lines of ``## Verification``. Filtering prose
  out is behaviour-preserving: ``_extract_verbs`` over the filtered lines equals
  ``_extract_verbs`` over the whole section for all 146 briefs, and the filtered
  list is non-empty for all 146.

Writing ``reqs`` activates the REQ-identity dimension, which is unmeasurable for
a legacy brief. Seeding it from the Acceptance Criteria makes the delta zero at
migration time by construction -- that is the honest starting state, not a
tautology: frontmatter becomes the INDEPENDENT declaration, so from here on
editing one side without the other is caught.

The eight pre-frontmatter ADR-0.0.1 briefs are a separate stratum: no
frontmatter at all, ``(Foundational)``-suffixed headings today's section regexes
never match, invisible to ``gz adr status``. Each records ``Status: **Complete**``
with a Gate-5 attestation link in its own ACCEPTANCE NOTES. They are SEALED with
``status: archived`` rather than migrated -- an honest claim that they are no
longer a live authoring surface, without asserting a ledger completion they do
not carry.

Usage:
    uv run python scripts/migrate_brief_frontmatter.py --dry-run
    uv run python scripts/migrate_brief_frontmatter.py
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

import yaml

from gzkit.governance.brief_reconcile import (
    _ALLOWED_HEADING_RE,
    _VERIFICATION_HEADING_RE,
    _acceptance_req_ids,
    _extract_section_paths,
    _extract_section_text,
)
from gzkit.governance.brief_structure import BriefStructure, is_terminal_brief_status
from gzkit.governance.trust_audits.brief_reconcile import _find_obpi_briefs

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FIELDS = ("allowlist", "reqs", "verification")

# Sealed-status for the pre-frontmatter ADR-0.0.1 stratum. `archived` is in
# BRIEF_TERMINAL_STATUSES, so these leave the live corpus without claiming an
# attested completion the ledger does not carry.
ERA0_SEAL_STATUS = "archived"


def split_frontmatter(text: str) -> tuple[str, dict, str]:
    """Return (raw frontmatter block, parsed mapping, body)."""
    if not text.startswith("---\n"):
        return "", {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", {}, text
    raw = text[4:end]
    return raw, yaml.safe_load(raw) or {}, text[end + 5 :]


def verification_commands(body: str) -> list[str]:
    """Return the command lines of the Verification section.

    Prose is dropped only because doing so provably changes no downstream
    decision -- see the module docstring.
    """
    section = _extract_section_text(body, _VERIFICATION_HEADING_RE)
    return [
        line.strip()
        for line in section.splitlines()
        if line.strip() and ("gz " in line or "uv run" in line)
    ]


def synthesize(body: str) -> dict[str, list]:
    """Lift the three required fields out of the brief body."""
    return {
        "allowlist": _extract_section_paths(body, _ALLOWED_HEADING_RE),
        "reqs": _acceptance_req_ids(body),
        "verification": verification_commands(body),
    }


def render_added_fields(fields: dict[str, list]) -> str:
    """Render the new keys as a YAML block, escaping via safe_dump."""
    return yaml.safe_dump(fields, sort_keys=False, allow_unicode=True, width=10_000)


def migrate_brief(path: Path, *, dry_run: bool) -> str:
    """Migrate one brief. Returns a one-word outcome for the summary tally."""
    text = path.read_text(encoding="utf-8")
    raw, frontmatter, body = split_frontmatter(text)

    if not frontmatter:
        return seal_era0(path, text, dry_run=dry_run)

    status = str(frontmatter.get("status", ""))
    if status and is_terminal_brief_status(status):
        return "skipped-terminal"
    if all(field in frontmatter for field in REQUIRED_FIELDS):
        return "already-structured"

    fields = synthesize(body)
    missing = [name for name, value in fields.items() if not value]
    if missing:
        print(f"  REFUSED {path.name}: body yields no {', '.join(missing)}", file=sys.stderr)
        return "refused"

    # Validate BEFORE writing — a brief that would not parse as BriefStructure
    # must never reach disk, or the strict flip inherits a broken corpus.
    candidate = {**frontmatter, **fields}
    try:
        # model_validate, not `BriefStructure(**...)`: frontmatter values are
        # `Unknown | list[Unknown]`, so `**`-unpacking makes the checker match each
        # value against its declared field type and report four false positives.
        # model_validate takes the mapping whole and runs the same validation.
        BriefStructure.model_validate(
            {k: v for k, v in candidate.items() if k in BriefStructure.model_fields}
        )
    except Exception as exc:  # noqa: BLE001 — refuse and report, never write
        print(f"  REFUSED {path.name}: {str(exc).splitlines()[0]}", file=sys.stderr)
        return "refused"

    if dry_run:
        return "would-migrate"

    path.write_text(f"---\n{raw}\n{render_added_fields(fields)}---\n{body}", encoding="utf-8")
    return "migrated"


def seal_era0(path: Path, text: str, *, dry_run: bool) -> str:
    """Seal a pre-frontmatter ADR-0.0.1 brief with a terminal status."""
    if dry_run:
        return "would-seal"
    path.write_text(f"---\nstatus: {ERA0_SEAL_STATUS}\n---\n\n{text}", encoding="utf-8")
    return "sealed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report without writing")
    args = parser.parse_args()

    warnings.simplefilter("ignore", DeprecationWarning)
    tally: dict[str, int] = {}
    for brief in _find_obpi_briefs(ROOT):
        outcome = migrate_brief(brief, dry_run=args.dry_run)
        tally[outcome] = tally.get(outcome, 0) + 1

    for outcome in sorted(tally):
        print(f"{tally[outcome]:5d}  {outcome}")
    return 1 if tally.get("refused") else 0


if __name__ == "__main__":
    raise SystemExit(main())
