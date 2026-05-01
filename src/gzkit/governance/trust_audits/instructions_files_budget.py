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
or fall back to packaged defaults shipped with gzkit. Exceeding any budget
raises a ``ValidationError`` with a remediation pointer to the
``gz-context-diet`` skill.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gzkit.validate import ValidationError

_BUDGET_DATA_PATH = Path("data") / "instructions_files_budget.json"
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


def _check_one_file(target: Path, budget: int, artifact: str) -> ValidationError | None:
    if not target.is_file():
        return None
    actual = len(target.read_text(encoding="utf-8"))
    if actual <= budget:
        return None
    return ValidationError(
        type="instructions_files_budget",
        artifact=artifact,
        message=(
            f"file is {actual} chars, exceeds {budget}-char budget by "
            f"{actual - budget}. {_REMEDIATION}"
        ),
    )


def audit_instructions_files_budget(project_root: Path) -> list[ValidationError]:
    """Audit AGENTS.md / CLAUDE.md / glob-matched rule files against budgets."""
    config = _load_budget_config(project_root)
    errors: list[ValidationError] = []
    for relpath, budget in config.get("files", {}).items():
        target = project_root / relpath
        finding = _check_one_file(target, int(budget), relpath)
        if finding is not None:
            errors.append(finding)
    for entry in config.get("globs", []):
        pattern = entry["pattern"]
        per_file_budget = int(entry["max_chars_per_file"])
        for matched in sorted(project_root.glob(pattern)):
            relpath = matched.relative_to(project_root).as_posix()
            finding = _check_one_file(matched, per_file_budget, relpath)
            if finding is not None:
                errors.append(finding)
    return errors
