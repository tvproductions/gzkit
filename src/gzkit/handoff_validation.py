"""Handoff document validation for SESSION handoff governance (ADR-0.0.65).

Extracted from tests/governance/test_handoff_schema.py (OBPI-0.0.25-06).
Provides fail-closed validation: every check returns a list of violations,
and an empty list means the document is clean.

Scope boundary (GHI #763). This module owns ONE of the three systems that used
to share the word "handoff": the session system — synthetic memory refresh from
agent session to agent session, for context management. The OBPI token block's
register entries are **exchange records** and live in
:mod:`gzkit.exchange_records`; the ecosystem's entry/exit gate is **transit**
(``gz airlock``, ADR-0.33.0). Both once lived here, which is why system
membership had to be inferred from a shared field name or directory instead of
read from a discriminator.

What legitimately remains shared is the document FORMAT — Markdown with YAML
frontmatter — so :func:`parse_frontmatter` is imported by the exchange module
rather than duplicated there. A shared format is exactly why no property of the
artifact can discriminate the two systems; the citing ledger event type and the
on-disk location are what do.

@covers ADR-0.0.25 (OBPI-0.0.25-06)
@covers ADR-0.25.0 (OBPI-0.25.0-32)
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

__all__ = [
    "CHECKPOINT_MODE",
    "HANDOFF_SCHEMA_VERSION",
    "PROSPECTIVE_SECTIONS",
    "REQUIRED_SECTIONS",
    "SETTLED_SECTION",
    "HandoffFrontmatter",
    "HandoffValidationError",
    "parse_frontmatter",
    "validate_decision_markers",
    "validate_handoff_document",
    "validate_no_placeholders",
    "validate_no_secrets",
    "validate_referenced_files",
    "validate_sections_populated",
    "validate_sections_present",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HANDOFF_SCHEMA_VERSION = "govzero.handoff.v1"

#: The mid-flight bookmark mode (GHI #756). Named once and read by every
#: consumer that must distinguish a bookmark from a departure notice — the
#: frontmatter enum, `find_exchange_for_release`, the `--mode` flag, and the
#: lock-exchange coupling validator — so the distinction cannot drift per-copy.
CHECKPOINT_MODE = "CHECKPOINT"

REQUIRED_SECTIONS = (
    "Current State Summary",
    "Important Context",
    "Decisions Made",
    "Immediate Next Steps",
    "Pending Work / Open Loops",
    "Verification Checklist",
    "Evidence / Artifacts",
)

#: Optional section carrying rulings that are SETTLED and still relevant
#: (GHI #696 defect 3). Deliberately NOT in ``REQUIRED_SECTIONS``: the
#: ``handoff-documents`` gate validates every post-cutover entry in
#: ``.gzkit/handoffs/``, so promoting it to required would fail the whole
#: existing corpus. It is self-populating (``create_handoff`` carries it forward
#: and promotes operator rulings into it), so it is never a section an author
#: must remember to fill — which is the failure mode GHI #696 documents.
SETTLED_SECTION = "Settled Rulings"

#: The sections whose citations assert LIVE work, and the only ones an authoring
#: liveness check may annotate. Sections are typed by tense: these two are
#: prospective — they name what a future session should pull — so a closed GHI
#: cited here is a false claim. Every other section is retrospective, where a
#: closed GHI is the correct record of what the traversal did, and annotating it
#: would falsify the archive.
#:
#: Both names are members of ``REQUIRED_SECTIONS``; the membership is asserted by
#: ``TestProspectiveSectionsAreRealSections`` rather than by an import-time check,
#: so a section rename cannot silently orphan this tuple.
PROSPECTIVE_SECTIONS = (
    "Immediate Next Steps",
    "Pending Work / Open Loops",
)

# ---------------------------------------------------------------------------
# Compiled patterns
# ---------------------------------------------------------------------------

# Widened to the canonical adr.json id forms (additive: the bare
# ADR-X.Y.Z form 168 committed handoffs use still matches). The bare-only form
# rejected every slug-bearing id — the form `src/gzkit/schemas/adr.json`
# actually mandates — and `ADR-pool.<slug>` entirely. Exactly the defect already
# fixed on the sibling field below under OBPI-0.0.72-02, left unfixed here
# (GHI #709).
_ADR_ID_RE = re.compile(r"^(?:ADR-pool\.[a-z0-9-]+|ADR-\d+\.\d+\.\d+(?:-[a-z0-9-]+)?)$")
# Widened to the canonical obpi.json slug-optional pattern (additive: the
# short OBPI-X.Y.Z-NN form still matches). The strict NN-only form rejected
# every slug-bearing id its own writers emit (OBPI-0.0.72-02).
_OBPI_ID_RE = re.compile(r"^OBPI-\d+\.\d+\.\d+-\d{2}(?:-[a-z0-9-]+)?$")

_PLACEHOLDER_RE = re.compile(
    r"\b(TBD|TODO|FIXME|PLACEHOLDER|XXX|CHANGEME)\b"
    r"|(?:^|\s)\.{3}(?:\s|$)",
    re.IGNORECASE | re.MULTILINE,
)

_SECRET_RE = re.compile(
    r"password\s*="
    r"|secret\s*="
    r"|token\s*="
    r"|api_key\s*="
    r"|Bearer\s+\S+"
    r"|PRIVATE KEY"
    r"|(?<![a-zA-Z])sk-[A-Za-z0-9]{20,}"
    r"|(?<![a-zA-Z])ghp_[A-Za-z0-9]{20,}",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Schema — HandoffFrontmatter model
# ---------------------------------------------------------------------------


def continues_from_refs(value: object) -> list[str]:
    """Fold a ``continues_from`` frontmatter value into its list of parent refs.

    The single place that decides what the field means (GHI #790). Every reader
    delegates here — the model, the chain walk, the settled-ruling composer, and
    the archive chain-integrity guard — because the alternative is four call sites
    each branching on ``isinstance`` and drifting apart. That is the same
    subsumption the ``rename_chain_target`` repair took: one shared fold, both
    readers delegating.

    Accepts the scalar form unchanged, so the 297 authored handoffs already on
    disk keep resolving with no migration. Blank and whitespace-only entries are
    dropped rather than returned: an empty pointer is not a parent, and passing
    one through would turn into a resolution attempt against the handoffs
    directory itself.
    """
    if value is None:
        return []
    if isinstance(value, str):
        ref = value.strip()
        return [ref] if ref else []
    if isinstance(value, list):
        return [ref.strip() for ref in value if isinstance(ref, str) and ref.strip()]
    return []


class HandoffFrontmatter(BaseModel):
    """Pydantic model for handoff document YAML frontmatter."""

    # extra="forbid" is KEPT — typo-defense is preserved by declaring every
    # real field below as an explicit SUPERSET, so unknown/misspelled keys
    # still raise (OBPI-0.0.72-02). Dropping the guard is forbidden.
    model_config = ConfigDict(extra="forbid", frozen=True)

    # CHECKPOINT is the mid-flight bookmark (GHI #756): a session writes one
    # without departing, so it is NOT a token surrender. `find_exchange_for_release`
    # skips it; token-block discipline § Sub-Invariant 5 is unrelaxed.
    mode: Literal["CREATE", "RESUME", "CHECKPOINT"]
    # Optional: a handoff carries continuity for any work, not only ADR-scoped
    # work (GHI #709). Design sessions, triage passes, and GHI burndowns have no
    # parent ADR. `mode` — not `adr_id` — is the is-this-a-handoff discriminator.
    adr_id: str | None = None
    branch: str
    timestamp: str
    agent: str
    obpi_id: str | None = None
    session_id: str | None = None
    # `str | list[str]` — lineage cardinality is {0, 1, N}, not {0, 1} (GHI #790).
    # A fork that later collapses has two genuine ancestors; the scalar form held
    # one, so the second head's rulings arrived only when a human hand-seated them.
    # The scalar is KEPT readable rather than migrated: 297 authored handoffs carry
    # it, and they are append-only historical records. Read via
    # `continues_from_refs` — never branch on the type at a call site.
    continues_from: str | list[str] | None = None
    # Min-info fields the lock-exchange coupling consumer requires
    # (_MIN_INFO_FRONTMATTER_FIELDS, alongside the already-declared `branch`).
    last_lock_event_timestamp: str | None = None
    last_commit_sha: str | None = None
    # Degenerate/reaping fields emitted by write_degenerate_exchange and
    # lock_manager._write_reaping_exchange.
    abandoned: bool | None = None
    category: str | None = None
    abandoned_by: str | None = None
    abandoned_at: str | None = None
    previous_agent: str | None = None
    reason: str | None = None

    @field_validator("adr_id")
    @classmethod
    def _validate_adr_id(cls, v: str | None) -> str | None:
        # An absent ADR is a valid state; a malformed one never is.
        if v is None:
            return None
        if not _ADR_ID_RE.match(v):
            msg = f"Invalid ADR ID format: {v!r} (expected ADR-X.Y.Z)"
            raise ValueError(msg)
        return v

    @field_validator("timestamp")
    @classmethod
    def _validate_timestamp(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v)
        except ValueError as exc:
            msg = f"Invalid ISO 8601 timestamp: {v!r}"
            raise ValueError(msg) from exc
        return v

    @field_validator("obpi_id")
    @classmethod
    def _validate_obpi_id(cls, v: str | None) -> str | None:
        if v is not None and not _OBPI_ID_RE.match(v):
            msg = f"Invalid OBPI ID format: {v!r} (expected OBPI-X.Y.Z-NN)"
            raise ValueError(msg)
        return v


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------


class HandoffValidationError(Exception):
    """Raised when a handoff document fails validation."""


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from Markdown content.

    Args:
        content: Full Markdown document text.

    Returns:
        Parsed YAML as a dict.

    Raises:
        HandoffValidationError: If frontmatter delimiters are missing or YAML is invalid.

    """
    content = content.replace("\r\n", "\n")
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        raise HandoffValidationError("Missing opening frontmatter delimiter (---)")

    end_index = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = i
            break

    if end_index is None:
        raise HandoffValidationError("Missing closing frontmatter delimiter (---)")

    yaml_text = "\n".join(lines[1:end_index])
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise HandoffValidationError(f"Invalid YAML in frontmatter: {exc}") from exc

    if not isinstance(data, dict):
        raise HandoffValidationError("Frontmatter must be a YAML mapping")

    return data


def validate_no_placeholders(content: str) -> list[str]:
    """Scan body for placeholder markers.

    Args:
        content: Full Markdown document text.

    Returns:
        List of violation descriptions (empty = clean).

    """
    content = content.replace("\r\n", "\n")
    # Strip frontmatter before scanning
    body = _strip_frontmatter(content)
    # Strip HTML comments before scanning
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    violations: list[str] = []
    for match in _PLACEHOLDER_RE.finditer(body):
        violations.append(f"Placeholder found: {match.group(0).strip()!r}")
    return violations


def validate_no_secrets(content: str) -> list[str]:
    """Scan content for potential secrets.

    Args:
        content: Full Markdown document text.

    Returns:
        List of violation descriptions (empty = clean).

    """
    content = content.replace("\r\n", "\n")
    violations: list[str] = []
    for match in _SECRET_RE.finditer(content):
        violations.append(f"Potential secret found: {match.group(0).strip()!r}")
    return violations


def validate_sections_present(content: str) -> list[str]:
    """Check that all required section headings are present.

    Args:
        content: Full Markdown document text.

    Returns:
        List of missing section names (empty = all present).

    """
    content = content.replace("\r\n", "\n")
    missing: list[str] = []
    for section in REQUIRED_SECTIONS:
        pattern = rf"^##\s+{re.escape(section)}\s*$"
        if not re.search(pattern, content, re.MULTILINE):
            missing.append(section)
    return missing


def validate_sections_populated(content: str) -> list[str]:
    """Check that every present required section carries a body.

    Presence and population are independent contracts. A required section that
    is absent entirely is :func:`validate_sections_present`'s finding, so only
    *present* headings are judged here — otherwise one missing section would be
    reported twice.

    A section's body runs to the next ``##`` heading or end-of-document. HTML
    comments are stripped before the emptiness test: the skill's acceptance rule
    requires "session-specific content (no HTML comments or placeholders
    remaining)", so a leftover scaffold comment must not satisfy the very
    contract it exists to prompt. Whitespace is likewise not content.

    Args:
        content: Full Markdown document text.

    Returns:
        List of present-but-empty section names (empty = all populated).

    """
    body = _strip_frontmatter(content.replace("\r\n", "\n"))
    empty: list[str] = []
    for section in REQUIRED_SECTIONS:
        heading = re.search(rf"^##\s+{re.escape(section)}\s*$", body, re.MULTILINE)
        if heading is None:
            continue
        rest = body[heading.end() :]
        nxt = re.search(r"^##\s+", rest, re.MULTILINE)
        section_body = rest[: nxt.start()] if nxt else rest
        section_body = re.sub(r"<!--.*?-->", "", section_body, flags=re.DOTALL)
        if not section_body.strip():
            empty.append(section)
    return empty


# An attributed decision, and the list markers `_section_items` will parse. Kept
# local rather than imported from `gzkit.handoff_api`, which imports THIS module.
# Both patterns mirror their originals there (`_ATTRIBUTION_RE`,
# `_ITEM_MARKER_RE`); `tests/governance/test_handoff_validation.py` round-trips an
# accepted document through `parse_decisions` so the two cannot drift apart
# silently.
_DECISION_ATTRIBUTION_RE = re.compile(r"^\[\s*(operator-ruled|agent-chose)\s*\]", re.IGNORECASE)
_DECISION_ITEM_MARKER_RE = re.compile(r"^(?:\d+\.\s+|[-*]\s+)")

_DECISIONS_SECTION = "Decisions Made"


def validate_decision_markers(content: str) -> list[str]:
    """Refuse attributed decisions that carry no list marker (GHI #722).

    ``gzkit.handoff_api._section_items`` treats a line as an entry only when it
    leads with ``-``, ``*``, or ``N.``. A decision written as
    ``[operator-ruled] ...`` with no marker therefore parses to NOTHING:
    ``parse_decisions`` returns an empty list, every ruling in the section is
    dropped, and the successor's ``Settled Rulings`` promotes none of them —
    silently, under an otherwise clean validation pass. Ten operator rulings left
    the chain that way across two handoffs authored 2026-07-26 before anyone
    noticed, and operator canon is verbatim *"MY WORD IS AUTHORITY IN ALL
    CASES"*, so booked rulings are the worst payload in the document to drop
    without a signal.

    The check is deliberately ASYMMETRIC. It fires only on a line that *claims*
    attribution and would be discarded — never on ordinary prose, which carries
    no ruling to lose. Refusing prose would be a formatting opinion; refusing a
    discarded ruling is data-loss prevention, and the wider rule would fail the
    whole legacy corpus.

    Args:
        content: Full Markdown document text.

    Returns:
        List of violation messages (empty = every attributed decision parses).

    """
    body = _strip_frontmatter(content.replace("\r\n", "\n"))
    heading = re.search(rf"^##\s+{re.escape(_DECISIONS_SECTION)}\s*$", body, re.MULTILINE)
    if heading is None:
        return []
    rest = body[heading.end() :]
    nxt = re.search(r"^##\s+", rest, re.MULTILINE)
    section_body = rest[: nxt.start()] if nxt else rest

    orphans = [
        stripped
        for line in section_body.splitlines()
        if (stripped := line.strip())
        and _DECISION_ATTRIBUTION_RE.match(stripped)
        and not _DECISION_ITEM_MARKER_RE.match(stripped)
    ]
    if not orphans:
        return []

    sample = orphans[0][:80]
    return [
        f"Section '{_DECISIONS_SECTION}': {len(orphans)} attributed decision(s) carry no "
        f"list marker, starting with: {sample!r}. "
        "An entry leading with [operator-ruled] or [agent-chose] but no '-', '*', or "
        "'N.' marker is invisible to parse_decisions, so its ruling is dropped from "
        "the successor's Settled Rulings and silently leaves the chain (GHI #722). "
        "Next step: prefix each such line with '- ' so the entry parses, then re-run "
        "the authoring command."
    ]


def validate_referenced_files(content: str, base_path: Path) -> list[str]:
    """Verify that file paths referenced in Evidence section exist on disk.

    Args:
        content: Full Markdown document text.
        base_path: Repository root to resolve relative paths against.

    Returns:
        List of nonexistent file paths (empty = all exist).

    """
    content = content.replace("\r\n", "\n")
    body = _strip_frontmatter(content)
    # Find the Evidence / Artifacts section
    evidence_match = re.search(
        r"^##\s+Evidence\s*/\s*Artifacts\s*$",
        body,
        re.MULTILINE,
    )
    if evidence_match is None:
        return []

    # Extract text until next section heading or end
    rest = body[evidence_match.end() :]
    next_section = re.search(r"^##\s+", rest, re.MULTILINE)
    evidence_text = rest[: next_section.start()] if next_section else rest

    # Strip HTML comments
    evidence_text = re.sub(r"<!--.*?-->", "", evidence_text, flags=re.DOTALL)

    # Find backtick-quoted paths (the convention: `path/to/file`)
    missing: list[str] = []
    for match in re.finditer(r"`([^`]+)`", evidence_text):
        candidate = match.group(1)
        # Skip things that look like commands or inline code, not paths
        if candidate.startswith(("-", "$", "uv ", "git ")):
            continue
        # Must look like a file path (contains / or .)
        if "/" not in candidate and "." not in candidate:
            continue
        # Resolve against committed/tracked state, not local disk: an
        # untracked-but-present path (a stale __pycache__ shell, a git-rm'd
        # directory with lingering bytecode) counts as absent because a clean
        # clone / CI would not have it (GHI #671). Fall back to on-disk
        # existence only when git cannot answer (non-git base_path — e.g. a
        # unit-test temp dir).
        tracked = _is_git_tracked(base_path, candidate)
        present = (base_path / candidate).exists() if tracked is None else tracked
        if not present:
            missing.append(candidate)

    # Ephemeral, gitignored evidence (e.g. ARB receipts under the gitignored
    # artifacts/ tree) is not committed, so a referenced path is legitimately
    # absent on any clone that did not author the session — do not report those
    # as broken references (GHI #633). A genuinely-absent, non-ignored path is
    # still a broken reference.
    if missing:
        missing = [p for p in missing if not _is_git_ignored(base_path, p)]

    # A handoff is a point-in-time register entry, and its Evidence section is a
    # PAST-tense record ("Changed surfaces: ...") of what a finished session
    # touched. Requiring every cited path to exist at HEAD reads that record as a
    # present-tense claim, which makes the handoff corpus a ratchet against ever
    # deleting code: retiring any module retroactively invalidates every handoff
    # that recorded touching it. That structurally opposes the campaign's
    # Movement C (Reduce the accretion), and the design already concedes the
    # point with its pre-2026-06-15 cutover exemption.
    #
    # A path git has never heard of is still a broken reference — a typo or a
    # fabricated citation — and still fails. Git history is the discriminator
    # between "deleted since" and "never existed" (operator ruling 2026-07-25).
    if missing:
        missing = [p for p in missing if not _existed_in_git_history(base_path, p)]
    return missing


def _existed_in_git_history(base_path: Path, rel_path: str) -> bool:
    """Return True when ``rel_path`` was tracked at some commit reachable now.

    Distinguishes a legitimately-retired path (deleted by a later commit, so a
    past handoff's evidence citation remains accurate for the session it
    records) from a path git has never seen (a typo or fabricated citation,
    which is the broken reference this check exists to catch).

    Bytes-mode capture (no stdout decode) keeps this off the non-UTF-8
    subprocess-read class (GHI #582), matching ``_is_git_tracked``.
    """
    try:
        result = subprocess.run(
            ["git", "log", "--all", "--max-count=1", "--", rel_path],
            cwd=base_path,
            capture_output=True,
            check=False,
        )
    except OSError:
        return False
    if result.returncode != 0:
        return False
    return bool(result.stdout.strip())


def validate_handoff_document(
    content: str,
    base_path: Path,
    *,
    allow_empty_sections: bool = False,
) -> list[str]:
    """Run all validation checks on a handoff document.

    Args:
        content: Full Markdown document text.
        base_path: Repository root for file reference checks.
        allow_empty_sections: Waive the section-population contract ONLY (GHI
            #692). Reserved for the four pre-cutover hollow handoffs snapshotted
            in ``data/handoff_section_grandfather.json``, whose sessions are gone
            and whose bodies cannot be honestly reconstructed. Every other
            contract — frontmatter, placeholders, secrets, section presence,
            referenced files — still applies, so this can never become a blanket
            pass. Default ``False``: authoring is fail-closed.

    Returns:
        List of all violation messages (empty = valid).

    """
    content = content.replace("\r\n", "\n")
    errors: list[str] = []

    # 1. Parse and validate frontmatter
    is_register_entry = False
    try:
        fm_data = parse_frontmatter(content)
        HandoffFrontmatter(**fm_data)
        is_register_entry = bool(fm_data.get("abandoned"))
    except (HandoffValidationError, ValidationError) as exc:
        errors.append(f"Frontmatter: {exc}")

    # 2. No placeholders
    errors.extend(validate_no_placeholders(content))

    # 3. No secrets
    errors.extend(validate_no_secrets(content))

    # Shape-awareness (OBPI-0.0.72-02): degenerate/reaping register entries
    # (frontmatter ``abandoned: true``) are a distinct document class — terse
    # abandon/reaping audit artifacts, not full session handoffs. They carry
    # frontmatter + abandon fields plus a self-referential pointer to the
    # now-deleted lock; the seven-section and referenced-file contracts apply
    # only to CREATE/RESUME session handoffs. Frontmatter, placeholder, and
    # secret checks above remain universal.
    if is_register_entry:
        return errors

    # 4. Required sections (session handoffs only)
    for section in validate_sections_present(content):
        errors.append(f"Missing required section: {section}")

    # 4b. ...and populated, not merely present (GHI #692). The skill's § Acceptance
    # Rules always declared "all 7 required sections populated"; only presence was
    # implemented, so a document of seven empty headings passed the gate — a
    # handoff that preserved nothing while certifying that it had.
    if not allow_empty_sections:
        for section in validate_sections_populated(content):
            errors.append(f"Empty required section: {section}")

    # 4c. ...and its attributed decisions are parseable list items (GHI #722).
    # Population is not enough: a populated Decisions Made section whose entries
    # carry no list marker parses to zero decisions, so every ruling in it is
    # dropped from the successor's Settled Rulings without a signal.
    errors.extend(validate_decision_markers(content))

    # 5. Referenced files exist (session handoffs only)
    for path in validate_referenced_files(content, base_path):
        errors.append(f"Referenced file not found: {path}")

    return errors


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _is_git_ignored(base_path: Path, rel_path: str) -> bool:
    """Return True if ``rel_path`` is git-ignored under ``base_path``.

    Exempts ephemeral, uncommitted evidence (e.g. ARB receipts under the
    gitignored ``artifacts/`` tree) from the Evidence-section existence check: a
    referenced receipt is legitimately absent on any clone that did not author
    the session (GHI #633). Returncode-only (no stdout decode) so it cannot trip
    the non-UTF-8 subprocess-read class (GHI #582). Fails open to "not ignored"
    on any error, so a genuinely-broken reference is never masked by a git
    failure or a non-git base path.
    """
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", rel_path],
            cwd=base_path,
            capture_output=True,
            check=False,
        )
    except OSError:
        return False
    return result.returncode == 0


def _is_git_tracked(base_path: Path, rel_path: str) -> bool | None:
    """Return whether ``rel_path`` is tracked in git under ``base_path``.

    ``True`` if git tracks the path — a tracked file, or a directory prefix
    containing at least one tracked file; ``False`` if the path is not tracked;
    ``None`` if committed state cannot be determined (``base_path`` is not a git
    work tree, or git is unavailable), signalling the caller to fall back to a
    local-disk check.

    The Evidence-section referenced-file check must reflect committed/tracked
    state — what any clean clone or CI sees — not the authoring machine's local
    disk, where an untracked leftover (a stale ``__pycache__`` shell, a git-rm'd
    directory with lingering bytecode) would otherwise mask a broken reference
    (GHI #671, the inverse of the gitignored-exemption sibling #633). Bytes-mode
    capture (no stdout decode) keeps this off the non-UTF-8 subprocess-read
    class (GHI #582).
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "--", rel_path],
            cwd=base_path,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return bool(result.stdout.strip())


def _strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from content, returning body only."""
    content = content.replace("\r\n", "\n")
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return content
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[i + 1 :])
    return content
