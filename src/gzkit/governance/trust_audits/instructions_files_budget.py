"""Per-file char-budget audit for AGENTS.md / CLAUDE.md / .claude/rules (GHI #373).

The diet doctrine (`AGENTS.md` § Anti-vibing mantra operative claim 2,
*"lighter ceremony is not a tradeoff axis"*) binds the per-turn agent
contract surface to a maximum char budget. Until this audit landed,
the budget was binding-by-doctrine only — every new invariant authored
inline could re-inflate AGENTS.md past Claude Code's 40,000-char
performance threshold without a structural floor. This audit promotes
the doctrine to mechanical enforcement per the canonical
advisory → mechanical pipeline (`docs/governance/advisory-rules-audit.md`).

Budgets live in ``data/instructions_files_budget.json`` (project-overridable)
or fall back to packaged defaults shipped with gzkit.

**Advisory until 1.0 — operator ruling 2026-08-17, verbatim:** *"temporary stay
of all control surface budget limits until version 1.0. I want to be warned, and
we may lift the limits as needed, but no blockers."* An overrun is reported to
stderr with its byte distance and the ``gz-context-diet`` remediation pointer,
and never changes the exit code.

The measurement is unchanged and the budgets stay in the data file — the stay
suspends the *consequence*, never the observation, so "we may lift the limits as
needed" stays a real per-file decision rather than a blanket amnesty. This is the
same posture its scope-sibling ``surface_delivery_witness`` already holds for the
vendor cap (2026-07-06 ruling): the two arms of
``gz validate --instructions-files-budget`` are now consistently observe-only.

EXIT CONDITION: restore fail-closed at 1.0. The rationale is the 2026-07-28
standing ruling that strictness is earned by the mechanism that discharges it —
the corpus/CMS path (``gz content remember`` -> ``compose`` -> ``land``) is what
makes an over-budget surface *fixable*, and ``ADR-0.35.0`` § Decision 3 is where
it lands. A gate whose satisfaction path does not exist does not force the work;
it only blocks it, and then gets widened under pressure.
"""

from __future__ import annotations

import json
import os
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import yaml

from gzkit.advisory import emit_advisory
from gzkit.mx.awareness import get_banner
from gzkit.validate import ValidationError

_BUDGET_DATA_PATH = Path("data") / "instructions_files_budget.json"
_PREFIX = "instructions-files-budget:"
# Tool output that no agent loads as instructions; never walked for a total.
_PRUNED_DIRS = frozenset(
    {".git", ".venv", "venv", "node_modules", "__pycache__", "site", "build", "dist", ".tox"}
)
_REMEDIATION = (
    "Run /gz-context-diet (or `uv run gz chores show instructions-files-diet`) "
    "to lift inline pedagogy to docs/governance/ behind one-line pointers."
)
_PACKAGED_DEFAULTS: dict[str, Any] = {
    "files": {"AGENTS.md": 40000, "CLAUDE.md": 40000},
    "globs": [{"pattern": ".claude/rules/*.md", "max_chars_per_file": 16000}],
}


def _load_budget_config(project_root: Path) -> dict[str, Any]:
    """Resolve project overlay first, then fall back to packaged defaults."""
    project_overlay = project_root / _BUDGET_DATA_PATH
    if project_overlay.is_file():
        return json.loads(project_overlay.read_text(encoding="utf-8"))
    return _PACKAGED_DEFAULTS


def _check_one_file(target: Path, budget: int, artifact: str) -> str | None:
    """Return the overrun advisory for *target*, or None when it is within budget."""
    if not target.is_file():
        return None
    actual = len(target.read_text(encoding="utf-8"))
    if actual <= budget:
        return None
    return (
        f"{artifact} is {actual} chars, exceeds {budget}-char budget by "
        f"{actual - budget}. {_REMEDIATION}"
    )


def _observe(message: str) -> None:
    """Report one overrun. Never fail-closed (2026-08-17 stay-until-1.0 ruling)."""
    emit_advisory(f"WARNING {_PREFIX} {message}")


def _matching_files(project_root: Path, pattern: str, exclude: list[str]) -> list[Path]:
    """Files under *project_root* matching *pattern*, minus excluded prefixes.

    ``**/`` patterns walk the tree, pruning tool output (``_PRUNED_DIRS``); an
    ``exclude`` entry ending in ``/`` drops a subtree, any other drops one path.
    """
    if pattern.startswith("**/"):
        name_pattern = pattern[3:]
        found: list[Path] = []
        for dirpath, dirnames, filenames in os.walk(project_root):
            dirnames[:] = sorted(d for d in dirnames if d not in _PRUNED_DIRS)
            found.extend(Path(dirpath) / f for f in sorted(filenames) if fnmatch(f, name_pattern))
    else:
        found = sorted(project_root.glob(pattern))

    def _excluded(rel: str) -> bool:
        return any(rel.startswith(e) if e.endswith("/") else rel == e for e in exclude)

    return [
        p for p in found if p.is_file() and not _excluded(p.relative_to(project_root).as_posix())
    ]


def _description_chars(skill_file: Path, project_root: Path) -> int:
    """Chars of a model-invoked skill's YAML ``description``; 0 when it never loads.

    Parsed as YAML so a block scalar counts whole, not as its first line. A
    frontmatter that is not valid YAML is reported and counted as 0, never raised:
    one bad skill must not take down the whole scope.
    """
    parts = skill_file.read_text(encoding="utf-8").split("---", 2)
    if len(parts) < 3:
        return 0
    try:
        frontmatter = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        rel = skill_file.relative_to(project_root).as_posix()
        mark = getattr(exc, "problem_mark", None)
        where = f" (line {mark.line + 1})" if mark is not None else ""
        _observe(
            f"{rel}: frontmatter is not valid YAML{where}, so its description is not "
            "counted; the harness may not load it either. Fix the frontmatter, then "
            "re-run `uv run gz validate --instructions-files-budget`."
        )
        return 0
    if not isinstance(frontmatter, dict) or frontmatter.get("disable-model-invocation"):
        return 0
    return len(str(frontmatter.get("description") or "").strip())


def _report_total(surface: str, actual: int, budget: int, unit: str) -> None:
    """Print every surface's size; an overrun is also an advisory (WP-13 exit condition)."""
    if actual > budget:
        _observe(
            f"{surface} is {actual} {unit}, exceeds the {budget}-{unit} budget by "
            f"{actual - budget}. {_REMEDIATION}"
        )
    else:
        print(f"{_PREFIX} {surface}: {actual} of {budget} {unit}", file=sys.stderr)


def _check_totals(project_root: Path, config: dict[str, Any]) -> None:
    """Measure each ``totals`` surface and the per-turn MX banner (GHI #1249).

    Totals are UTF-8 bytes, except ``measure: description_chars``, which counts the
    description characters of the skills that load. The orientation measures its
    own size at render (operator ruling A, 2026-10-18), because running it has
    side effects; the banner is a pure function of the marker, so it is read here.
    """
    for entry in config.get("totals", []):
        files = _matching_files(project_root, entry["pattern"], list(entry.get("exclude", [])))
        if entry.get("measure") == "description_chars":
            actual = sum(_description_chars(f, project_root) for f in files)
            _report_total(entry["surface"], actual, int(entry["max_chars"]), "chars")
        else:
            actual = sum(len(f.read_bytes()) for f in files)
            _report_total(entry["surface"], actual, int(entry["max_bytes"]), "B")
    hook_text = config.get("injected_hook_text")
    if hook_text is not None:
        banner = get_banner(project_root)
        _report_total("MX banner", len(banner.encode("utf-8")), int(hook_text["max_bytes"]), "B")


def audit_instructions_files_budget(project_root: Path) -> list[ValidationError]:
    """Observe AGENTS.md / CLAUDE.md / glob-matched rule files against budgets.

    Overruns are reported to stderr and never change the exit code — the
    operator's 2026-08-17 stay holds until 1.0 (see module docstring). The
    return type stays ``list[ValidationError]`` because the scope composes with
    ``audit_surface_delivery_witness``, which still fail-closes on
    survival-declaration drift; this arm simply contributes no findings.
    """
    config = _load_budget_config(project_root)
    for relpath, budget in config.get("files", {}).items():
        message = _check_one_file(project_root / relpath, int(budget), relpath)
        if message is not None:
            _observe(message)
    for entry in config.get("globs", []):
        per_file_budget = int(entry["max_chars_per_file"])
        for matched in sorted(project_root.glob(entry["pattern"])):
            relpath = matched.relative_to(project_root).as_posix()
            message = _check_one_file(matched, per_file_budget, relpath)
            if message is not None:
                _observe(message)
    _check_totals(project_root, config)
    return []
