"""Frontmatter-ledger reconciliation logic (ADR-0.0.16 OBPI-03).

Consumes the OBPI-01 validator (``validate_frontmatter_coherence``) and
OBPI-05's ``STATUS_VOCAB_MAPPING``. For every drifted ADR/OBPI file the
chore finds, governed frontmatter fields (``id``/``parent``/``lane``/
``status``) are rewritten in-place to match the ledger (ledger-wins).
Ungoverned keys and the document body are preserved byte-identically.
Pool ADRs are skipped. Unmapped frontmatter status terms STOP with a
``UnmappedStatusBlocker`` and mutate zero files.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.commands.common import _is_pool_adr_id
from gzkit.commands.validate_frontmatter import validate_frontmatter_coherence
from gzkit.governance.status_vocab import STATUS_VOCAB_MAPPING

GovernedField = Literal["id", "parent", "lane", "status"]

_GOVERNED_KEYS: frozenset[str] = frozenset({"id", "parent", "lane", "status"})
_POOL_PATH_SEGMENT = "/adr/pool/"

# Frontmatter line pattern. Matches a YAML mapping line like
# ``  key: value   # comment`` and groups the key, the value scalar, and the
# trailing whitespace + optional inline comment so rewrites can preserve them.
_FM_LINE_RE = re.compile(
    r"^(?P<head>\s*(?P<key>[A-Za-z_][\w-]*)\s*:\s*)"
    r"(?P<val>[^\n#]*?)"
    r"(?P<trail>\s*(?:#.*)?)$"
)


class FieldDiff(BaseModel):
    """One governed-field rewrite: ``before`` (frontmatter) → ``after`` (ledger)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    field: GovernedField = Field(..., description="Governed frontmatter field being rewritten.")
    before: str = Field(..., description="Frontmatter value observed before rewrite.")
    after: str = Field(..., description="Ledger value written in place of the frontmatter value.")


class FileRewrite(BaseModel):
    """One ADR/OBPI file and the governed-field rewrites applied to it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str = Field(..., description="Path to the file relative to project root.")
    diffs: list[FieldDiff] = Field(
        ..., min_length=1, description="Non-empty list of per-field diffs for this file."
    )


class SkipNote(BaseModel):
    """One file deliberately not considered for reconciliation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str = Field(..., description="Path to the skipped file relative to project root.")
    reason: Literal["pool-adr"] = Field(
        ..., description="Reason the file was skipped. Extensible enum."
    )


class ReconciliationReceipt(BaseModel):
    """Immutable receipt emitted by ``reconcile_frontmatter``."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    ledger_cursor: str = Field(..., description="sha256:<hex> of .gzkit/ledger.jsonl at run-start.")
    run_started_at: str = Field(..., description="ISO8601 UTC timestamp at entry.")
    run_completed_at: str = Field(..., description="ISO8601 UTC timestamp at exit.")
    files_rewritten: list[FileRewrite] = Field(..., description="Per-file rewrite entries.")
    skipped: list[SkipNote] = Field(..., description="Files deliberately skipped.")
    dry_run: bool = Field(..., description="True when --dry-run; no ADR/OBPI files mutated.")


class UnmappedStatusBlocker(Exception):
    """Raised when a drifted frontmatter ``status:`` term is not in STATUS_VOCAB_MAPPING.

    Carrying both the artifact path and the unmapped term so operators can locate
    and correct the vocabulary gap. No files are mutated before this is raised.
    """

    def __init__(self, artifact: str, term: str) -> None:
        self.artifact = artifact
        self.term = term
        super().__init__(
            f"BLOCKER: frontmatter status term {term!r} at {artifact} is not in "
            f"STATUS_VOCAB_MAPPING. No files were mutated. Add the term to "
            f"gzkit.governance.status_vocab.STATUS_VOCAB_MAPPING or correct the "
            f"frontmatter to a recognized term before re-running."
        )


def _compute_ledger_cursor(ledger_path: Path) -> str:
    """Return ``sha256:<hex>`` of the raw ledger file bytes, or all-zeros if missing."""
    if not ledger_path.is_file():
        return "sha256:" + ("0" * 64)
    digest = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    return f"sha256:{digest}"


def _iso_now() -> str:
    """Return current time as ISO8601 UTC with tz offset."""
    return datetime.now(tz=UTC).isoformat()


def _filename_safe_iso(when: datetime) -> str:
    """Return ``YYYYMMDDTHHMMSSZ`` — no colons, Windows-safe filename."""
    return when.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def _is_pool_path(rel_path: str) -> bool:
    """Return True if the file path lives under the pool tree."""
    normalized = rel_path.replace("\\", "/")
    return _POOL_PATH_SEGMENT in normalized


def _read_fm_status(path: Path) -> str:
    """Read the ``status:`` scalar from a file's frontmatter, or empty string."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            if in_fm:
                break
            in_fm = True
            continue
        if not in_fm:
            continue
        match = _FM_LINE_RE.match(line)
        if match and match.group("key") == "status":
            return match.group("val").strip().strip("\"'")
    return ""


def _rewrite_governed_keys_in_place(path: Path, edits: dict[str, str]) -> None:
    """Rewrite only governed keys' scalars; preserve every other byte.

    Operates on the raw file text line-by-line. For each line inside the
    frontmatter block whose key is in ``edits`` and matches a governed key,
    replace only the value portion — leading indent, trailing whitespace,
    inline comments, and the rest of the file are passed through unchanged.
    """
    if not edits:
        return
    raw = path.read_text(encoding="utf-8")
    # Preserve line terminators by splitting on \n and re-joining with \n.
    # UTF-8 repos typically use \n; CRLF edge case would need splitlines(keepends=True).
    lines = raw.split("\n")
    in_fm = False
    fm_closed = False
    for i, line in enumerate(lines):
        if fm_closed:
            break
        stripped = line.strip()
        if stripped == "---":
            if in_fm:
                fm_closed = True
                continue
            in_fm = True
            continue
        if not in_fm:
            continue
        match = _FM_LINE_RE.match(line)
        if not match:
            continue
        key = match.group("key")
        if key not in _GOVERNED_KEYS or key not in edits:
            continue
        head = match.group("head")
        trail = match.group("trail")
        lines[i] = f"{head}{edits[key]}{trail}"
    path.write_text("\n".join(lines), encoding="utf-8")


def _group_errors_by_path(errors: list) -> dict[str, list]:
    """Return a mapping of rel_path → list[ValidationError] for this file."""
    grouped: dict[str, list] = {}
    for err in errors:
        grouped.setdefault(err.artifact, []).append(err)
    return grouped


def _resolve_artifact_id(abs_path: Path) -> str:
    """Derive the (short-form) artifact id from a file's stem.

    Matches the validator's filesystem-path-keyed lookup precedent —
    stem looks like ``ADR-0.1.0-slug`` or ``OBPI-0.0.16-03-slug``.
    """
    stem = abs_path.stem
    adr_match = re.match(r"^(ADR-[\d.]+(?:-pool\.[\w.]+)?|ADR-pool\.[\w.]+)", stem)
    if adr_match:
        return adr_match.group(0)
    obpi_match = re.match(r"^(OBPI-\d+\.\d+\.\d+-\d+)", stem)
    if obpi_match:
        return obpi_match.group(0)
    return stem


def _is_pool_artifact(abs_path: Path, rel_path: str) -> bool:
    """Pool ADR check combining path location and id prefix (ADR-pool.*)."""
    if _is_pool_path(rel_path):
        return True
    artifact_id = _resolve_artifact_id(abs_path)
    return _is_pool_adr_id(artifact_id)


def _build_file_rewrite(
    rel_path: str, errors: list
) -> tuple[FileRewrite | None, SkipNote | None, str | None]:
    """Turn per-file ValidationErrors into a FileRewrite, skip note, or blocker term.

    Returns (rewrite, skip, unmapped_term). Exactly one of rewrite/skip is non-None
    unless the errors list yields no governed-field diffs (all None).
    """
    diffs: list[FieldDiff] = []
    for err in errors:
        field = err.field
        if field not in _GOVERNED_KEYS:
            continue
        diffs.append(
            FieldDiff(
                field=field,
                before=err.frontmatter_value or "",
                after=err.ledger_value or "",
            )
        )
    if not diffs:
        return None, None, None
    return FileRewrite(path=rel_path, diffs=diffs), None, None


def reconcile_frontmatter(project_root: Path, *, dry_run: bool) -> ReconciliationReceipt:
    """Main entry point: detect drift via the validator, rewrite to ledger-wins.

    Pre-flight: every file with drifted ``status:`` must have its current
    frontmatter term in STATUS_VOCAB_MAPPING. Unmapped → UnmappedStatusBlocker
    raised before any mutation.

    Pool ADRs: skipped and noted in the receipt.

    Ledger cursor: sampled once at entry (sha256 of ledger file bytes); never
    re-read mid-run. Mid-run ledger mutations do not leak into this receipt.
    """
    from gzkit.ledger import Ledger  # noqa: PLC0415

    started_at_dt = datetime.now(tz=UTC)
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    ledger_cursor = _compute_ledger_cursor(ledger_path)

    # Pin ledger state at run-start. Pre-materialize the artifact graph on this
    # instance so subsequent mid-run mutations to .gzkit/ledger.jsonl cannot leak
    # into the validator's drift computation (REQ-0.0.16-03-08).
    pinned_ledger = Ledger(ledger_path) if ledger_path.is_file() else None
    if pinned_ledger is not None:
        try:
            pinned_ledger.get_artifact_graph()
        except (json.JSONDecodeError, KeyError, ValueError):
            pinned_ledger = None

    errors = validate_frontmatter_coherence(project_root, ledger=pinned_ledger)
    grouped = _group_errors_by_path(errors)
    pool_paths = _enumerate_pool_artifacts(project_root)

    # Pre-flight: reject unmapped status terms BEFORE any mutation.
    for rel_path, err_list in grouped.items():
        abs_path = project_root / rel_path
        if _is_pool_artifact(abs_path, rel_path):
            continue
        for err in err_list:
            if err.field != "status":
                continue
            current_term = (err.frontmatter_value or "").strip().strip("\"'")
            if not _status_is_known(current_term):
                raise UnmappedStatusBlocker(artifact=rel_path, term=current_term)

    files_rewritten: list[FileRewrite] = []
    skipped: list[SkipNote] = [SkipNote(path=rel, reason="pool-adr") for rel in sorted(pool_paths)]

    try:
        for rel_path in sorted(grouped):
            err_list = grouped[rel_path]
            abs_path = project_root / rel_path
            if _is_pool_artifact(abs_path, rel_path):
                # Already enumerated in the pool pre-pass above; validator should
                # not emit errors for pool ADRs (no ledger entry to compare against),
                # but if it ever does, treat it as a skip and do not mutate.
                continue
            rewrite, _, _ = _build_file_rewrite(rel_path, err_list)
            if rewrite is None:
                continue
            if not dry_run:
                edits: dict[str, str] = {str(diff.field): diff.after for diff in rewrite.diffs}
                _rewrite_governed_keys_in_place(abs_path, edits)
            files_rewritten.append(rewrite)
    finally:
        # REQ-0.0.16-03-10 partial-failure: on any mid-loop exception, still
        # emit a receipt reflecting the N files successfully rewritten so far.
        # Errors from receipt construction/write are suppressed to let the
        # original exception propagate.
        completed_at_dt = datetime.now(tz=UTC)
        try:
            receipt = ReconciliationReceipt(
                ledger_cursor=ledger_cursor,
                run_started_at=started_at_dt.isoformat(),
                run_completed_at=completed_at_dt.isoformat(),
                files_rewritten=files_rewritten,
                skipped=skipped,
                dry_run=dry_run,
            )
            _write_receipt(project_root, receipt, completed_at_dt)
        except (OSError, ValueError):
            receipt = None

    # The finally block above always assigns receipt. On normal completion
    # the final return below returns the fully-populated value. On partial
    # failure, the exception that triggered the finally propagates past
    # this line; this return is only reached on the normal path.
    if receipt is None:
        raise RuntimeError("reconcile_frontmatter: receipt construction failed")
    return receipt


def _enumerate_pool_artifacts(project_root: Path) -> list[str]:
    """Return rel-paths of every ADR/OBPI file under the pool tree.

    Pool ADRs have no ledger entry by design; the validator skips them silently.
    The chore surfaces them explicitly as ``skipped`` so operators see which
    files were deliberately untouched.
    """
    from gzkit.config import GzkitConfig  # noqa: PLC0415

    config_path = project_root / ".gzkit.json"
    if not config_path.is_file():
        return []
    config = GzkitConfig.load(config_path)
    pool_dir = project_root / config.paths.design_root / "adr" / "pool"
    if not pool_dir.is_dir():
        return []
    results: list[str] = []
    for md_path in pool_dir.rglob("*.md"):
        if not md_path.is_file():
            continue
        rel = str(md_path.relative_to(project_root))
        results.append(rel)
    return results


def _status_is_known(term: str) -> bool:
    """True when ``term`` is case-insensitively present as a key in STATUS_VOCAB_MAPPING."""
    if not term:
        return False
    lowered = term.lower()
    return any(key.lower() == lowered for key in STATUS_VOCAB_MAPPING)


def _write_receipt(
    project_root: Path, receipt: ReconciliationReceipt, completed_at: datetime
) -> Path:
    """Write the receipt JSON to ``artifacts/receipts/frontmatter-coherence/<ts>.json``."""
    receipts_dir = project_root / "artifacts" / "receipts" / "frontmatter-coherence"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    out_path = receipts_dir / f"{_filename_safe_iso(completed_at)}.json"
    payload = receipt.model_dump(mode="json")
    _schema_validate(payload)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path


def _schema_validate(payload: dict) -> None:
    """Validate the receipt payload against the JSON schema before writing."""
    import jsonschema  # noqa: PLC0415

    schema = json.loads(_schema_path().read_text(encoding="utf-8"))
    jsonschema.validate(instance=payload, schema=schema)


def _schema_path() -> Path:
    """Return the filesystem path of the reconciliation receipt JSON schema.

    Walks upward from this module's location to find the repo root (marked
    by ``.gzkit.json``), then returns ``data/schemas/<name>.json`` beneath
    it. Decoupled from ``Path.cwd()`` so tests running under
    ``isolated_filesystem`` still resolve to the real schema file.
    """
    candidate = Path(__file__).resolve().parent
    for _ in range(8):
        if (candidate / ".gzkit.json").is_file():
            return candidate / "data" / "schemas" / "frontmatter_coherence_receipt.schema.json"
        candidate = candidate.parent
    return Path.cwd() / "data" / "schemas" / "frontmatter_coherence_receipt.schema.json"


__all__ = [
    "FieldDiff",
    "FileRewrite",
    "ReconciliationReceipt",
    "SkipNote",
    "UnmappedStatusBlocker",
    "reconcile_frontmatter",
]
