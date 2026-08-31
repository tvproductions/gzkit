"""Validator for the Agent Rule Placement Invariant (ADR-0.0.20).

Enumerates canonical `.gzkit/rules/*.md` files, parses YAML frontmatter,
and flags files with missing `paths:` or universal-glob (`paths: "**"`
or `paths: ["**"]`) as violations. Entries registered in
`.gzkit/manifest.json` under `rules.unscoped_allowlist` are marked
allowlisted and do not fail the gate.

Read-only by contract — never writes files, never invokes shell=True,
never calls an LLM, never reads files outside `.gzkit/rules/*.md` and
`.gzkit/manifest.json` (REQ-0.0.20-01-20).
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from gzkit.rules import NESTED_SURFACE_NAMES

_NULL_TOKENS = {"", "null", "~"}
_UNIVERSAL_GLOB = "**"
# One unquoted / single-quoted / double-quoted scalar.
_SCALAR_RE = re.compile(r"""^(?:"([^"]*)"|'([^']*)'|([^#\s].*?))\s*$""")
# One item inside `[ ... ]` — handles quoted + unquoted, comma or end.
_INLINE_LIST_ITEM_RE = re.compile(r"""\s*(?:"([^"]*)"|'([^']*)'|([^,\]\s]+))\s*""")
_BLOCK_ITEM_RE = re.compile(r"""^\s*-\s*(?:"([^"]*)"|'([^']*)'|([^#\s].*?))\s*$""")


def _extract_scalar_value(raw: str) -> str:
    """Strip optional quotes from a scalar token."""
    m = _SCALAR_RE.match(raw.strip())
    if m is None:
        return raw.strip()
    return next(g for g in m.groups() if g is not None)


def _parse_inline_list(raw: str) -> list[str]:
    """Parse `[ "a", "b" ]` form. Returns the list of item values."""
    inside = raw.strip()[1:-1]  # drop leading `[` and trailing `]`
    items: list[str] = []
    for m in _INLINE_LIST_ITEM_RE.finditer(inside):
        item = next((g for g in m.groups() if g is not None), None)
        if item is not None:
            items.append(item)
    return items


def classify_paths_field(frontmatter_text: str) -> tuple[str, str | None]:
    """Classify a frontmatter's `paths:` key.

    Args:
        frontmatter_text: The YAML frontmatter block (without `---` fences).

    Returns:
        (verdict, detected_value) where verdict is one of
        `"missing"`, `"universal-glob"`, or `"concrete"`. `detected_value`
        is the observed glob when the verdict is `"universal-glob"`, the
        raw scalar when `"concrete"` with a single value, or None.

    """
    lines = frontmatter_text.splitlines()
    paths_values: list[str] | None = None

    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if not stripped.startswith("paths:"):
            continue

        after_colon = stripped[len("paths:") :].lstrip()

        if after_colon == "" or after_colon in _NULL_TOKENS:
            # Could still be a block list on following lines.
            block_items: list[str] = []
            for follow in lines[idx + 1 :]:
                m = _BLOCK_ITEM_RE.match(follow)
                if m is None:
                    # Stop at first non-block-item line.
                    break
                item = next((g for g in m.groups() if g is not None), None)
                if item is not None:
                    block_items.append(item)
            paths_values = block_items or None
            break

        if after_colon.startswith("["):
            paths_values = _parse_inline_list(after_colon)
            break

        # Inline scalar.
        paths_values = [_extract_scalar_value(after_colon)]
        break

    if paths_values is None:
        return "missing", None

    if len(paths_values) >= 1 and all(v == _UNIVERSAL_GLOB for v in paths_values):
        return "universal-glob", _UNIVERSAL_GLOB

    if len(paths_values) == 1:
        return "concrete", paths_values[0]
    return "concrete", None


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_CANONICAL_RULES_DIR = ".gzkit/rules"
_MANIFEST_REL = ".gzkit/manifest.json"


def _extract_frontmatter(text: str) -> str | None:
    """Return the YAML frontmatter block, or None if absent."""
    m = _FRONTMATTER_RE.match(text)
    if m is None:
        return None
    return m.group(1)


def _load_allowlist(
    project_root: Path,
) -> tuple[list[UnscopedAllowlistEntry], str | None]:
    """Load the unscoped-rules allowlist from the manifest.

    Returns (entries, error_message). When the manifest is missing or
    malformed, entries is empty and error_message is populated.
    """
    manifest_path = project_root / _MANIFEST_REL
    if not manifest_path.exists():
        return [], f"manifest not found: {manifest_path}"
    try:
        raw = manifest_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        return [], f"manifest unreadable: {exc}"

    rules_block = data.get("rules") or {}
    raw_entries = rules_block.get("unscoped_allowlist") or []
    entries: list[UnscopedAllowlistEntry] = []
    try:
        for raw_entry in raw_entries:
            entries.append(UnscopedAllowlistEntry(**raw_entry))
    except ValidationError as exc:
        return [], f"allowlist entry invalid: {exc}"
    return entries, None


def run_unscoped_rules(project_root: Path) -> UnscopedRulesResult:
    """Classify every canonical rule file and return an aggregate result.

    Reads only `.gzkit/rules/*.md` (never mirrors — REQ-4) and
    `.gzkit/manifest.json`. Never writes. Never invokes shell.
    """
    allowlist, manifest_error = _load_allowlist(project_root)

    if manifest_error is not None:
        return UnscopedRulesResult(
            result="fail",
            violations=[],
            allowlist_entries=allowlist,
            canonical_root=_CANONICAL_RULES_DIR,
            files_checked=0,
            exit_code=2,
        )

    allowlisted_files = {entry.file for entry in allowlist}
    rules_dir = project_root / _CANONICAL_RULES_DIR
    # Hierarchical AGENTS.md is the canonical home per the invariant (not a
    # rule file) — exclude it from the rule-file scan.
    rule_files = sorted(p for p in rules_dir.glob("*.md") if p.name not in NESTED_SURFACE_NAMES)
    violations: list[Violation] = []

    for rule_path in rule_files:
        try:
            text = rule_path.read_text(encoding="utf-8")
        except OSError:
            return UnscopedRulesResult(
                result="fail",
                violations=violations,
                allowlist_entries=allowlist,
                canonical_root=_CANONICAL_RULES_DIR,
                files_checked=len(rule_files),
                exit_code=2,
            )

        frontmatter = _extract_frontmatter(text) or ""
        verdict, detected = classify_paths_field(frontmatter)
        if verdict == "concrete":
            continue

        rel = rule_path.relative_to(project_root).as_posix()
        violations.append(
            Violation(
                file=rel,
                reason="missing-paths" if verdict == "missing" else "universal-glob",
                allowlisted=rel in allowlisted_files,
                detected_value=detected,
            )
        )

    gating_violations = [v for v in violations if not v.allowlisted]
    if gating_violations:
        return UnscopedRulesResult(
            result="fail",
            violations=violations,
            allowlist_entries=allowlist,
            canonical_root=_CANONICAL_RULES_DIR,
            files_checked=len(rule_files),
            exit_code=3,
        )

    return UnscopedRulesResult(
        result="pass",
        violations=violations,
        allowlist_entries=allowlist,
        canonical_root=_CANONICAL_RULES_DIR,
        files_checked=len(rule_files),
        exit_code=0,
    )


def format_allowlist_listing(entries: list[UnscopedAllowlistEntry]) -> str:
    """Render the allowlist entries for human-readable `--allowlist-only`."""
    if not entries:
        return "Unscoped-rules allowlist: no entries\n"
    lines = ["Unscoped-rules allowlist:"]
    for entry in entries:
        lines.append(f"  - {entry.file}")
        lines.append(f"      rationale:    {entry.rationale}")
        lines.append(f"      tracking_ref: {entry.tracking_ref}")
        lines.append(f"      added_date:   {entry.added_date.isoformat()}")
    return "\n".join(lines) + "\n"


class UnscopedAllowlistEntry(BaseModel):
    """One entry in `.gzkit/manifest.json#/rules/unscoped_allowlist`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    file: str
    rationale: str = Field(..., min_length=20)
    tracking_ref: str = Field(..., pattern=r"^(GHI-\d+|ADR-[\d.]+[-\w]*)$")
    added_date: date


class Violation(BaseModel):
    """A rule file that failed the placement invariant."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    file: str
    reason: Literal["missing-paths", "universal-glob"]
    allowlisted: bool
    detected_value: str | None = None


class UnscopedRulesResult(BaseModel):
    """Aggregate result of one `--unscoped-rules` scope run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scope: str = "unscoped-rules"
    result: Literal["pass", "fail"]
    violations: list[Violation]
    allowlist_entries: list[UnscopedAllowlistEntry]
    canonical_root: str
    files_checked: int
    exit_code: int
