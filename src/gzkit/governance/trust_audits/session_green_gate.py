"""Session-green-gate declaration audit (ADR-0.0.68 / OBPI-0.0.68-02).

Fail-closed: absent or unparseable .pre-commit-config.yaml is treated as a
violation, never a pass.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from gzkit.core.validation_rules import ValidationError

_RECOVERY = (
    "Recovery: declare a 'pre-push' stage hook running 'gz check' in "
    ".pre-commit-config.yaml (see ADR-0.0.68 / OBPI-0.0.68-01)."
)

_DELIVERY_RECOVERY = (
    "Recovery: `uv run pre-commit install --hook-type pre-commit --hook-type pre-push`. "
    "If it refuses with 'Cowardly refusing to install hooks with `core.hooksPath` set', "
    "run `git config --local --unset-all core.hooksPath` first, then re-run the install."
)


def configured_hooks_path(project_root: Path) -> Path | None:
    """Return the worktree's ``core.hooksPath`` override, or None when unset.

    Public because two surfaces must agree on the answer: this module's delivery
    arm (which reads hooks from wherever git actually reads them) and
    ``gz init``'s activation step (which must not spend a subprocess on a
    ``pre-commit install`` that git's own refusal will reject). A second parser
    would be a place for the two to drift.
    """
    config_path = project_root / ".git" / "config"
    if not config_path.is_file():
        return None
    try:
        lines = config_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for raw in lines:
        key, sep, value = raw.partition("=")
        if sep and key.strip().lower() == "hookspath":
            candidate = Path(value.strip())
            return candidate if candidate.is_absolute() else project_root / candidate
    return None


def _effective_hooks_dir(project_root: Path) -> Path | None:
    """Resolve the directory git actually reads hooks from, or None outside a worktree.

    Honors ``core.hooksPath`` rather than assuming ``.git/hooks``: a redirect is
    one of the ways the gate goes undelivered, so assuming the default location
    would blind the check to the exact failure it exists to catch.
    """
    git_dir = project_root / ".git"
    if not git_dir.is_dir():
        return None
    return configured_hooks_path(project_root) or git_dir / "hooks"


def _delivery_errors(project_root: Path) -> list[ValidationError]:
    """Return errors when the declared pre-push gate is not installed on disk.

    A declared hook that was never delivered enforces nothing. This repo ran in
    exactly that state: ``.pre-commit-config.yaml`` declared ``gz-check-pre-push``
    while ``.git/hooks/`` held only stock samples, because a local
    ``core.hooksPath`` made ``pre-commit install`` refuse. The declaration arm
    stayed green the whole time.
    """
    hooks_dir = _effective_hooks_dir(project_root)
    if hooks_dir is None:
        # Not a git worktree (fixture tree, sdist export) — delivery is not
        # assertable here, and the declaration arm still applies.
        return []
    hook = hooks_dir / "pre-push"
    if not hook.is_file():
        return [
            ValidationError(
                type="session_green_gate",
                artifact=f"{hooks_dir.as_posix()}/pre-push",
                message=(
                    "Pre-push gz check hook is declared but not installed — no hook file "
                    f"at {hooks_dir.as_posix()}/pre-push, so commits and pushes run "
                    f"unenforced. {_DELIVERY_RECOVERY}"
                ),
            )
        ]
    try:
        body = hook.read_text(encoding="utf-8", errors="replace")
    except OSError:
        body = ""
    if "pre-commit" not in body:
        return [
            ValidationError(
                type="session_green_gate",
                artifact=f"{hooks_dir.as_posix()}/pre-push",
                message=(
                    "Pre-push hook exists but is not the pre-commit shim, so the declared "
                    f"'gz check' gate is not installed. {_DELIVERY_RECOVERY}"
                ),
            )
        ]
    return []


def _runs_gz_check(entry: str) -> bool:
    """Return True when *entry* invokes ``gz check`` as a command, not a prefix.

    Token-adjacency match: ``gz`` immediately followed by the bare ``check``
    token. Rejects check-prefixed sibling verbs (e.g. ``gz check-config-paths``)
    that an unbounded substring match would false-pass (#600).
    """
    tokens = entry.split()
    return any(tokens[i] == "gz" and tokens[i + 1] == "check" for i in range(len(tokens) - 1))


def audit_session_green_gate(
    project_root: Path, *, check_delivery: bool = False
) -> list[ValidationError]:
    """Return errors if the pre-push gz check gate is not declared (and optionally delivered).

    Fails closed when .pre-commit-config.yaml is missing, unparseable, or
    contains no hook with stages: [pre-push] and entry containing 'gz check'.

    When *check_delivery* is set, additionally asserts the declared hook is
    actually installed in the worktree's effective hooks directory. That arm is
    opt-in because a fresh CI checkout legitimately has no hooks installed — CI
    *is* the gate there, it does not push — so making it unconditional would
    fail every CI run. It is enabled on the surfaces that precede a push.
    """
    config_path = project_root / ".pre-commit-config.yaml"
    if not config_path.exists():
        return [
            ValidationError(
                type="session_green_gate",
                artifact=".pre-commit-config.yaml",
                message=(
                    "Missing .pre-commit-config.yaml — no pre-push gz check hook"
                    f" declared. {_RECOVERY}"
                ),
            )
        ]
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return [
            ValidationError(
                type="session_green_gate",
                artifact=".pre-commit-config.yaml",
                message=(
                    "Unparseable .pre-commit-config.yaml — treated as violation"
                    f" (fail-closed). {_RECOVERY}"
                ),
            )
        ]
    if not isinstance(config, dict):
        return [
            ValidationError(
                type="session_green_gate",
                artifact=".pre-commit-config.yaml",
                message=f"Invalid .pre-commit-config.yaml structure. {_RECOVERY}",
            )
        ]
    all_hooks = [hook for repo in config.get("repos", []) for hook in repo.get("hooks", [])]
    pre_push_gz_hooks = [
        h
        for h in all_hooks
        if "pre-push" in (h.get("stages") or []) and _runs_gz_check(h.get("entry", ""))
    ]
    if not pre_push_gz_hooks:
        return [
            ValidationError(
                type="session_green_gate",
                artifact=".pre-commit-config.yaml",
                message=f"No stages: [pre-push] hook running 'gz check' declared. {_RECOVERY}",
            )
        ]
    return _delivery_errors(project_root) if check_delivery else []
