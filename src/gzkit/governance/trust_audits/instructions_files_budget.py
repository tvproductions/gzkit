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
from pathlib import Path
from typing import Any

from gzkit.advisory import emit_advisory
from gzkit.validate import ValidationError

_BUDGET_DATA_PATH = Path("data") / "instructions_files_budget.json"
_PREFIX = "instructions-files-budget:"
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
    return []
