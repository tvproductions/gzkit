"""Handoff document validation for session handoff governance.

Extracted from tests/governance/test_handoff_schema.py (OBPI-0.0.25-06).
Provides fail-closed validation: every check returns a list of violations,
and an empty list means the document is clean.

@covers ADR-0.0.25 (OBPI-0.0.25-06)
@covers ADR-0.25.0 (OBPI-0.25.0-32)
"""

from __future__ import annotations

import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

__all__ = [
    "ABANDON_CATEGORIES",
    "AbandonSpec",
    "HANDOFF_SCHEMA_VERSION",
    "REQUIRED_SECTIONS",
    "HandoffFrontmatter",
    "HandoffValidationError",
    "InvalidAbandonSpec",
    "find_handoff_for_release",
    "parse_abandon_spec",
    "parse_frontmatter",
    "validate_handoff_document",
    "validate_no_placeholders",
    "validate_no_secrets",
    "validate_referenced_files",
    "validate_sections_populated",
    "validate_sections_present",
    "write_completion_handoff",
    "write_degenerate_handoff",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HANDOFF_SCHEMA_VERSION = "govzero.handoff.v1"

REQUIRED_SECTIONS = (
    "Current State Summary",
    "Important Context",
    "Decisions Made",
    "Immediate Next Steps",
    "Pending Work / Open Loops",
    "Verification Checklist",
    "Evidence / Artifacts",
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


class HandoffFrontmatter(BaseModel):
    """Pydantic model for handoff document YAML frontmatter."""

    # extra="forbid" is KEPT — typo-defense is preserved by declaring every
    # real field below as an explicit SUPERSET, so unknown/misspelled keys
    # still raise (OBPI-0.0.72-02). Dropping the guard is forbidden.
    model_config = ConfigDict(extra="forbid", frozen=True)

    mode: Literal["CREATE", "RESUME"]
    # Optional: a handoff carries continuity for any work, not only ADR-scoped
    # work (GHI #709). Design sessions, triage passes, and GHI burndowns have no
    # parent ADR. `mode` — not `adr_id` — is the is-this-a-handoff discriminator.
    adr_id: str | None = None
    branch: str
    timestamp: str
    agent: str
    obpi_id: str | None = None
    session_id: str | None = None
    continues_from: str | None = None
    # Min-info fields the lock-handoff coupling consumer requires
    # (_MIN_INFO_FRONTMATTER_FIELDS, alongside the already-declared `branch`).
    last_lock_event_timestamp: str | None = None
    last_commit_sha: str | None = None
    # Degenerate/reaping fields emitted by write_degenerate_handoff and
    # lock_manager._write_reaping_handoff.
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
    return missing


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


# ---------------------------------------------------------------------------
# Abandon-category enum and degenerate-handoff writer
# ---------------------------------------------------------------------------
#
# Source of truth: ``.gzkit/rules/token-block-discipline.md`` § Sub-Invariant 1.
# The base category enum is CLOSED here in code; extending it requires an ADR
# per the rule's extension protocol. Mirror — not re-author — the enum.

ABANDON_CATEGORIES: tuple[str, ...] = (
    "network_loss",
    "external_blocker",
    "wrong_obpi_claimed",
    "tool_failure",
    # reaping is the OBPI-03 surface; OBPI-02 ships base + reaping placeholder
    # so reap-driven release in OBPI-03 lands cleanly.
    "reaping",
)


class InvalidAbandonSpec(ValueError):
    """Raised when --abandon argument cannot be parsed or category is unknown."""


class AbandonSpec(BaseModel):
    """Parsed `--abandon <category>:<reason>` specification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: str
    reason: str

    @field_validator("category")
    @classmethod
    def _validate_category(cls, v: str) -> str:
        if v not in ABANDON_CATEGORIES:
            allowed = " | ".join(ABANDON_CATEGORIES)
            raise ValueError(
                f"Unknown abandon category {v!r}; closed enum (see "
                f".gzkit/rules/token-block-discipline.md § Sub-Invariant 1): {allowed}"
            )
        return v


def parse_abandon_spec(raw: str) -> AbandonSpec:
    """Parse ``<category>:<reason>``; reject whitespace around category.

    Whitespace around the category is rejected so the audit surface stays
    canonical — ``" network_loss:reason"`` is the same operator typo class as
    misspelling the category itself.
    """
    if ":" not in raw:
        raise InvalidAbandonSpec("abandon spec must be '<category>:<reason>' (missing colon)")
    category, _, reason = raw.partition(":")
    if category != category.strip():
        raise InvalidAbandonSpec(
            f"abandon category must not have leading/trailing whitespace: {category!r}"
        )
    if not category:
        raise InvalidAbandonSpec("abandon category is empty")
    if not reason:
        raise InvalidAbandonSpec("abandon reason is empty")
    try:
        return AbandonSpec(category=category, reason=reason)
    except ValidationError as e:  # surface as InvalidAbandonSpec for the CLI
        raise InvalidAbandonSpec(str(e)) from e


def _filesystem_safe_timestamp(iso_ts: str) -> str:
    """Render an ISO timestamp into a filesystem-safe filename token."""
    return iso_ts.replace(":", "").replace("-", "").replace(".", "")[:15] + "Z"


def write_degenerate_handoff(
    project_root: Path,
    *,
    obpi_id: str,
    adr_id: str | None = None,
    agent: str,
    spec: AbandonSpec,
    last_claim_timestamp: str | None,
    commit_sha: str,
    branch: str,
    decision_context: str | None = None,
) -> Path:
    """Write an abandoned-state register entry under ``.gzkit/handoffs/``.

    Returns the on-disk path written. The handoff carries the four
    minimum-information fields per Sub-Invariant 2 (last lock-event timestamp,
    last commit SHA, decision context, branch state) plus abandon-specific
    frontmatter (``abandoned: true``, ``category``, ``reason``).
    """
    handoff_dir = project_root / ".gzkit" / "handoffs"
    handoff_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    timestamp_token = _filesystem_safe_timestamp(now)
    filename = f"{timestamp_token}-{obpi_id}-abandoned.md"
    path = handoff_dir / filename

    frontmatter = {
        "mode": "CREATE",
        "adr_id": adr_id,
        "obpi_id": obpi_id,
        "branch": branch,
        "timestamp": now,
        "agent": agent,
        "abandoned": True,
        "category": spec.category,
        "reason": spec.reason,
        "last_lock_event_timestamp": last_claim_timestamp,
        "last_commit_sha": commit_sha,
    }

    decision = decision_context or (
        f"Lock for {obpi_id} abandoned by {agent} (category={spec.category}, reason={spec.reason})."
    )

    body = (
        "---\n"
        + yaml.safe_dump(frontmatter, sort_keys=False)
        + "---\n\n"
        + f"<!-- Degenerate handoff for {obpi_id} — abandon path -->\n\n"
        + "## Current State Summary\n\n"
        + f"Lock surrender via `--abandon {spec.category}:{spec.reason}` "
        + f"by agent `{agent}`.\n\n"
        + "## Important Context\n\n"
        + "Degenerate handoff written as the register-entry pairing for an "
        + "abandoned lock release (token-block discipline; see "
        + "`.gzkit/rules/token-block-discipline.md` § Sub-Invariant 1).\n\n"
        + "## Decisions Made\n\n"
        + f"- {decision}\n\n"
        + "## Immediate Next Steps\n\n"
        + "1. Operator review of the abandonment reason.\n"
        + "2. If recovery is intended, re-claim the lock via `gz obpi lock claim`.\n\n"
        + "## Pending Work / Open Loops\n\n"
        + f"- OBPI {obpi_id} was abandoned mid-traversal; resume work requires "
        + "re-claim plus a fresh handoff at completion.\n\n"
        + "## Verification Checklist\n\n"
        + f"- [ ] `git rev-parse HEAD` returns `{commit_sha}` (or operator "
        + "explains drift).\n"
        + f"- [ ] Branch matches `{branch}`.\n\n"
        + "## Evidence / Artifacts\n\n"
        + f"- `.gzkit/locks/obpi/{obpi_id}.lock.json` — lock file at abandon "
        + "(deleted on release).\n"
    )

    path.write_text(body, encoding="utf-8")
    return path


_PLACEHOLDER_WORD_RE = re.compile(r"\b(?:TBD|TODO|FIXME|PLACEHOLDER|XXX|CHANGEME)\b", re.IGNORECASE)


def _sanitize_handoff_text(text: str | None, *, limit: int = 600) -> str:
    """Collapse whitespace and neutralize placeholder/ellipsis tokens in embedded text.

    Auto-drafted completion handoffs embed operator-authored evidence (attestation
    text, implementation summary, key proof). An elision (``...``) or a placeholder
    word would otherwise trip ``validate_no_placeholders`` at ``gz check`` time, so a
    mechanically-written handoff would fail its own validator. Newlines are collapsed
    so embedded text can never introduce a spurious ``## section`` or ``---`` line into
    the rendered document.
    """
    if not text:
        return ""
    collapsed = " ".join(text.split())
    collapsed = re.sub(r"\.{3,}", "…", collapsed)
    collapsed = _PLACEHOLDER_WORD_RE.sub("(noted)", collapsed)
    return collapsed[:limit]


def write_completion_handoff(
    project_root: Path,
    *,
    obpi_id: str,
    agent: str,
    attestor: str,
    attestation_text: str,
    implementation_summary: str,
    key_proof: str,
    last_lock_event_timestamp: str | None,
    commit_sha: str,
    branch: str,
    brief_rel_path: str,
) -> Path:
    r"""Write a full session handoff as the register entry for OBPI completion.

    Unlike :func:`write_degenerate_handoff` (the abandon path), this is a
    non-abandoned ``CREATE`` handoff carrying all seven required sections, so
    :func:`find_handoff_for_release` accepts it as the completion-surrender register
    entry and ``gz validate --lock-handoff-coupling`` passes. The parent ADR id is
    derived from the OBPI semver (bare ``ADR-X.Y.Z``) when the id is semver-shaped,
    and recorded as absent otherwise — ``adr_id`` is optional (GHI #709).
    Auto-drafted from completion evidence and written mechanically at every
    ``gz obpi complete`` (token-block exit edge, GHI #619); it may be terse. Written
    with explicit ``\n`` newlines so the committed artifact is LF on every platform.
    """
    handoff_dir = project_root / ".gzkit" / "handoffs"
    handoff_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    path = handoff_dir / f"{_filesystem_safe_timestamp(now)}-{obpi_id}-complete.md"

    # An OBPI always has a parent ADR, so derivation normally succeeds. When the
    # id is not semver-shaped the parent is genuinely unknown — record that as
    # absent rather than synthesizing `ADR-0.0.0`, an id naming no real artifact
    # (GHI #709).
    semver_match = re.match(r"OBPI-(\d+\.\d+\.\d+)", obpi_id)
    adr_id = f"ADR-{semver_match.group(1)}" if semver_match else None
    parent_phrase = f" under {adr_id}" if adr_id else ""
    next_step = (
        f"1. Continue the parent {adr_id} checklist, or open the next OBPI.\n\n"
        if adr_id
        else "1. Open the next OBPI, or continue the parent ADR checklist.\n\n"
    )

    frontmatter = {
        "mode": "CREATE",
        "adr_id": adr_id,
        "obpi_id": obpi_id,
        "branch": branch,
        "timestamp": now,
        "agent": agent,
        "last_lock_event_timestamp": last_lock_event_timestamp,
        "last_commit_sha": commit_sha,
    }

    decision = _sanitize_handoff_text(attestation_text) or "Attested complete."
    summary = _sanitize_handoff_text(implementation_summary) or "See brief Implementation Summary."
    proof = _sanitize_handoff_text(key_proof) or "See brief Key Proof and the ledger receipt."

    body = (
        "---\n"
        + yaml.safe_dump(frontmatter, sort_keys=False)
        + "---\n\n"
        + f"<!-- Completion handoff for {obpi_id} — mechanical register entry (GHI #619) -->\n\n"
        + "## Current State Summary\n\n"
        + f"OBPI {obpi_id} completed and attested by `{attestor}`{parent_phrase}. The work "
        + "lock (if held) was surrendered mechanically at completion; the "
        + "`obpi_lock_released` ledger event is the surrender audit.\n\n"
        + "## Important Context\n\n"
        + "Written mechanically at `gz obpi complete` as the token-block exit-edge register "
        + "entry (token surrender at the section's end; see "
        + "`.gzkit/rules/token-block-discipline.md`). Auto-drafted from completion evidence "
        + "and may be terse.\n\n"
        + "## Decisions Made\n\n"
        + f"- {decision}\n\n"
        + "## Immediate Next Steps\n\n"
        + next_step
        + "## Pending Work / Open Loops\n\n"
        + f"- Implementation summary: {summary}\n\n"
        + "## Verification Checklist\n\n"
        + f"- [ ] `git rev-parse HEAD` resolves to `{commit_sha}` (or operator explains drift).\n"
        + f"- [ ] Branch matches `{branch}`.\n"
        + f"- [ ] Key proof: {proof}\n\n"
        + "## Evidence / Artifacts\n\n"
        + f"- `{brief_rel_path}` — the completed OBPI brief.\n"
        + "- `.gzkit/ledger.jsonl` — completion receipt and lock-release event.\n"
    )

    path.write_text(body, encoding="utf-8", newline="\n")
    return path


def find_handoff_for_release(
    project_root: Path,
    *,
    obpi_id: str,
    after_timestamp: str | None = None,
) -> Path | None:
    """Search `.gzkit/handoffs/` for a matching register entry.

    Matches when the handoff frontmatter declares the given `obpi_id` and its
    timestamp is later than ``after_timestamp`` (the matching
    ``obpi_lock_claimed`` event time). Returns the newest match, or ``None``.

    In OBPI-02 this is consulted to decide whether the warning-on-no-handoff
    branch fires; OBPI-03 will promote the check to fail-closed.
    """
    handoff_dir = project_root / ".gzkit" / "handoffs"
    if not handoff_dir.is_dir():
        return None

    candidates: list[tuple[str, Path]] = []
    for path in handoff_dir.glob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
        except (OSError, yaml.YAMLError, HandoffValidationError):
            continue
        if not isinstance(fm, dict):
            continue
        if fm.get("obpi_id") != obpi_id:
            continue
        ts = str(fm.get("timestamp", ""))
        if after_timestamp and ts <= after_timestamp:
            continue
        if fm.get("abandoned") is True:
            # Abandoned handoffs satisfy the pairing only when invoked via the
            # --abandon code path; they are not the same surface as a
            # completion-pairing handoff.
            continue
        candidates.append((ts, path))

    if not candidates:
        return None
    candidates.sort()
    return candidates[-1][1]
