"""Concurrent five-source grounding gather for gzkit.justify.

`gather_evidence` fans out five independent source fetches via
``concurrent.futures.ThreadPoolExecutor``. Each source is wrapped so that
a missing or failing source produces an empty result and a warning entry
on the returned :class:`EvidenceBundle` — never an exception.

The five sources:

1. matching rules from ``.gzkit/rules/*.md`` whose ``paths:`` globs match
   the anchor surface
2. ledger events filtered to the anchor (OBPI kind only)
3. recent commits via ``git log --since=60.days.ago --grep=<anchor-id>``
4. related anchors (each resolved via :func:`resolve_anchor`)
5. a literal path reference to the model-regression taxonomy document

The library emits nothing to stdout/stderr (the caller owns I/O).
"""

from __future__ import annotations

import concurrent.futures
import fnmatch
import json
import re
from pathlib import Path
from typing import Any

from gzkit.justify.anchors import resolve_anchor
from gzkit.justify.models import (
    AnchorRef,
    AnchorResolutionError,
    CommitRef,
    EvidenceBundle,
    LedgerEvent,
    RuleCitation,
)
from gzkit.utils import run_exec

TAXONOMY_REFERENCE_PATH = "docs/governance/model-regression-taxonomy.md"

_DEFAULT_TIMEOUT_SECONDS = 3.0
_PER_SOURCE_SUBPROCESS_TIMEOUT = 10
_OBPI_SEMVER_PATTERN = re.compile(r"^OBPI-(\d+\.\d+\.\d+)-\d+$")


def gather_evidence(
    anchor: AnchorRef,
    *,
    related: list[str] | None = None,
    project_root: Path | None = None,
    timeout: float = _DEFAULT_TIMEOUT_SECONDS,
) -> EvidenceBundle:
    """Gather five-source grounding evidence for an anchor.

    All sources execute concurrently; any source failure is recorded as a
    warning and produces an empty collection — the function never raises
    for missing data. Anchor resolution for the ``related`` list uses the
    same resolver as :func:`resolve_anchor` and is best-effort.
    """
    root = project_root if project_root is not None else Path.cwd()
    related_ids = list(related or [])
    warnings: list[str] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        rules_future = executor.submit(_gather_matching_rules, anchor, root)
        ledger_future = executor.submit(_gather_ledger_events, anchor, root)
        commits_future = executor.submit(_gather_recent_commits, anchor, root)
        related_future = executor.submit(_gather_related_anchors, related_ids, root)
        taxonomy_future = executor.submit(_gather_taxonomy_reference)

        matching_rules, rules_warnings = _await_future(
            rules_future, "matching_rules", timeout, default=((), ())
        )
        ledger_events, ledger_warnings = _await_future(
            ledger_future, "ledger_events", timeout, default=((), ())
        )
        recent_commits, commits_warnings = _await_future(
            commits_future, "recent_commits", timeout, default=((), ())
        )
        related_anchors, related_warnings = _await_future(
            related_future, "related_anchors", timeout, default=((), ())
        )
        taxonomy, taxonomy_warnings = _await_future(
            taxonomy_future,
            "taxonomy_reference",
            timeout,
            default=(TAXONOMY_REFERENCE_PATH, ()),
        )

    warnings.extend(rules_warnings)
    warnings.extend(ledger_warnings)
    warnings.extend(commits_warnings)
    warnings.extend(related_warnings)
    warnings.extend(taxonomy_warnings)

    return EvidenceBundle(
        anchor=anchor,
        matching_rules=tuple(matching_rules),
        ledger_events=tuple(ledger_events),
        recent_commits=tuple(recent_commits),
        related_anchors=tuple(related_anchors),
        taxonomy_reference=taxonomy,
        warnings=tuple(warnings),
    )


def _await_future(
    future: concurrent.futures.Future[Any],
    source_name: str,
    timeout: float,
    *,
    default: tuple[Any, tuple[str, ...]],
) -> tuple[Any, tuple[str, ...]]:
    try:
        return future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        return default[0], (f"{source_name} source timed out after {timeout}s",)
    except Exception as exc:  # noqa: BLE001 — graceful degradation by design
        return default[0], (f"{source_name} source failed: {exc}",)


# ---------------------------------------------------------------------------
# Source 1: matching rules
# ---------------------------------------------------------------------------


def _gather_matching_rules(
    anchor: AnchorRef, project_root: Path
) -> tuple[tuple[RuleCitation, ...], tuple[str, ...]]:
    rules_dir = project_root / ".gzkit" / "rules"
    if not rules_dir.is_dir():
        return (), ("matching_rules: .gzkit/rules/ not present",)

    surface_paths = _infer_anchor_surface_paths(anchor, project_root)
    matched: list[RuleCitation] = []
    warnings: list[str] = []

    for rule_path in sorted(rules_dir.glob("*.md")):
        try:
            content = rule_path.read_text(encoding="utf-8")
        except OSError as exc:
            warnings.append(f"matching_rules: {rule_path.name} unreadable: {exc}")
            continue

        rule_id, description, globs = _parse_rule_frontmatter(content)
        if rule_id is None:
            continue

        matched_globs = _matched_globs(globs, anchor, surface_paths)
        if not matched_globs:
            continue

        matched.append(
            RuleCitation(
                rule_id=rule_id,
                path=str(rule_path.relative_to(project_root)),
                description=description,
                paths_globs=tuple(matched_globs),
            )
        )
    return tuple(matched), tuple(warnings)


def _infer_anchor_surface_paths(anchor: AnchorRef, project_root: Path) -> tuple[str, ...]:
    if anchor.kind == "obpi" and anchor.source_path:
        brief_path = Path(anchor.source_path)
        try:
            content = brief_path.read_text(encoding="utf-8")
        except OSError:
            return ()
        return _extract_allowed_paths_from_brief(content)
    if anchor.kind == "ghi":
        return ()
    return ()


def _extract_allowed_paths_from_brief(content: str) -> tuple[str, ...]:
    in_section = False
    paths: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Allowed Paths"):
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section and stripped.startswith("- "):
            token = stripped[2:].strip()
            if "—" in token:
                token = token.split("—", 1)[0].strip()
            token = token.strip("`").strip()
            if token:
                paths.append(token)
    return tuple(paths)


def _parse_rule_frontmatter(
    content: str,
) -> tuple[str | None, str | None, tuple[str, ...]]:
    if not content.startswith("---"):
        return None, None, ()
    lines = content.splitlines()
    end_idx: int | None = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return None, None, ()

    rule_id: str | None = None
    description: str | None = None
    globs: list[str] = []
    in_paths = False
    for line in lines[1:end_idx]:
        stripped = line.strip()
        if in_paths:
            if stripped.startswith("- "):
                value = stripped[2:].strip()
                value = value.strip('"').strip("'")
                if value:
                    globs.append(value)
                continue
            in_paths = False
        if stripped.startswith("id:"):
            rule_id = stripped.split(":", 1)[1].strip().strip('"').strip("'")
        elif stripped.startswith("description:"):
            description = stripped.split(":", 1)[1].strip().strip('"').strip("'")
        elif stripped == "paths:" or stripped.startswith("paths:"):
            in_paths = True
    return rule_id, description, tuple(globs)


def _matched_globs(
    rule_globs: tuple[str, ...], anchor: AnchorRef, surface_paths: tuple[str, ...]
) -> list[str]:
    if not rule_globs:
        return []
    matched: list[str] = []
    if anchor.kind == "obpi":
        for glob in rule_globs:
            if any(_glob_matches(glob, path) for path in surface_paths):
                matched.append(glob)
    elif anchor.kind == "ghi":
        for glob in rule_globs:
            if glob == "**" or glob == "**/*":
                matched.append(glob)
    elif anchor.kind == "draft":
        for glob in rule_globs:
            if glob in ("**", "**/*") or glob.endswith("*.py"):
                matched.append(glob)
    return matched


def _glob_matches(glob: str, path: str) -> bool:
    if fnmatch.fnmatch(path, glob):
        return True
    # Support "dir/**" shorthand meaning "dir/**/*"
    if glob.endswith("/**"):
        prefix = glob[:-3]
        return path.startswith(prefix)
    return False


# ---------------------------------------------------------------------------
# Source 2: ledger events
# ---------------------------------------------------------------------------


def _gather_ledger_events(
    anchor: AnchorRef, project_root: Path
) -> tuple[tuple[LedgerEvent, ...], tuple[str, ...]]:
    if anchor.kind != "obpi":
        return (), (f"ledger_events: source not applicable for {anchor.kind} anchor",)
    rc, stdout, stderr = run_exec(
        ["uv", "run", "gz", "state", "--json"],
        cwd=project_root,
        timeout=_PER_SOURCE_SUBPROCESS_TIMEOUT,
    )
    if rc != 0:
        return (), (f"ledger_events: gz state --json unavailable (rc={rc}, stderr={stderr!r})",)
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return (), (f"ledger_events: gz state produced non-JSON output: {exc}",)

    raw_events = data.get("events") if isinstance(data, dict) else data
    if not isinstance(raw_events, list):
        return (), ("ledger_events: gz state payload had no 'events' list",)

    events: list[LedgerEvent] = []
    for raw in raw_events:
        if not isinstance(raw, dict):
            continue
        if raw.get("id") != anchor.identifier:
            continue
        try:
            events.append(
                LedgerEvent(
                    event=str(raw.get("event", "")),
                    id=str(raw.get("id", "")),
                    ts=str(raw.get("ts", "")),
                    parent=raw.get("parent"),
                    extra=dict(raw.get("extra") or {}),
                )
            )
        except Exception:  # noqa: BLE001 — stay resilient to schema drift
            continue
    return tuple(events), ()


# ---------------------------------------------------------------------------
# Source 3: recent commits
# ---------------------------------------------------------------------------


def _gather_recent_commits(
    anchor: AnchorRef, project_root: Path
) -> tuple[tuple[CommitRef, ...], tuple[str, ...]]:
    grep_pattern = _commit_grep_pattern(anchor)
    if not grep_pattern:
        return (), ("recent_commits: no grep pattern derivable from anchor",)
    rc, stdout, stderr = run_exec(
        [
            "git",
            "log",
            "--since=60.days.ago",
            "--oneline",
            f"--grep={grep_pattern}",
        ],
        cwd=project_root,
        timeout=_PER_SOURCE_SUBPROCESS_TIMEOUT,
    )
    if rc != 0:
        return (), (f"recent_commits: git log unavailable (rc={rc}, stderr={stderr!r})",)
    commits: list[CommitRef] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(" ", 1)
        if len(parts) != 2:
            continue
        commits.append(CommitRef(sha=parts[0], subject=parts[1]))
    return tuple(commits), ()


def _commit_grep_pattern(anchor: AnchorRef) -> str:
    if anchor.kind == "draft":
        return anchor.draft_slug or ""
    return anchor.identifier or ""


# ---------------------------------------------------------------------------
# Source 4: related anchors
# ---------------------------------------------------------------------------


def _gather_related_anchors(
    related_ids: list[str], project_root: Path
) -> tuple[tuple[AnchorRef, ...], tuple[str, ...]]:
    resolved: list[AnchorRef] = []
    warnings: list[str] = []
    for rid in related_ids:
        try:
            resolved.append(resolve_anchor(rid, project_root=project_root))
        except (ValueError, AnchorResolutionError) as exc:
            warnings.append(f"related_anchors: {rid} unresolvable: {exc}")
    return tuple(resolved), tuple(warnings)


# ---------------------------------------------------------------------------
# Source 5: taxonomy reference
# ---------------------------------------------------------------------------


def _gather_taxonomy_reference() -> tuple[str, tuple[str, ...]]:
    return TAXONOMY_REFERENCE_PATH, ()
