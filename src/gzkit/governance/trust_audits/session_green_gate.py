"""Session-green-gate declaration audit (ADR-0.0.68 / OBPI-0.0.68-02).

Fail-closed: absent or unparseable .pre-commit-config.yaml is treated as a
violation, never a pass.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from gzkit.advisory import emit_advisory
from gzkit.core.validation_rules import ValidationError
from gzkit.hooks.commit_ledger import recorder_undelivered_reason

_RECOVERY = (
    "Recovery: declare a 'pre-push' stage hook running 'gz check' in "
    ".pre-commit-config.yaml (see ADR-0.0.68 / OBPI-0.0.68-01)."
)


#: The gate's own hook. Required even when a config's type list omits it, because
#: the declaration arm below requires a pre-push `gz check` hook.
_GATE_HOOK_TYPE = "pre-push"

#: pre-commit's own default when a config declares no `default_install_hook_types`.
_PRE_COMMIT_DEFAULT_TYPES = ("pre-commit",)

#: Hook types that RECORD and gate nothing. A missing one is advisory; every
#: other declared type — including one added later that nobody has classified —
#: fails closed, because its absence may lose enforcement. Operator ruling
#: 2026-09-14 on GHI #851, verbatim: "By hook type (Recommended)".
_RECORDING_HOOK_TYPES = frozenset({"prepare-commit-msg", "post-commit"})


def install_command(hook_types: list[str]) -> str:
    """Return the `pre-commit install` invocation delivering every declared hook type.

    Explicit ``--hook-type`` flags rather than a bare install: without a
    ``default_install_hook_types`` list, pre-commit installs only ``pre-commit``,
    leaving the gate's own ``pre-push`` hook undelivered.
    """
    return "uv run pre-commit install " + " ".join(f"--hook-type {t}" for t in hook_types)


def _delivery_recovery(hook_types: list[str]) -> str:
    return (
        f"Recovery: `{install_command(hook_types)}`. If it refuses with 'Cowardly refusing to "
        "install hooks with `core.hooksPath` set', run `git config --local --unset-all "
        "core.hooksPath` first, then re-run the install."
    )


def declared_hook_types(project_root: Path) -> list[str]:
    """Return every hook type the project's config installs, plus the gate's own.

    Public because two surfaces must agree on the answer: ``gz init``, which
    installs the hooks, and this module's delivery arm, which verifies them. An
    installer holding its own list is the producer half of GHI #851 — it
    under-installs exactly what the witness would then under-check. An unreadable
    config reads as pre-commit's default; the declaration arm reports it.
    """
    try:
        config = yaml.safe_load((project_root / ".pre-commit-config.yaml").read_text("utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        config = None
    return _declared_hook_types(config if isinstance(config, dict) else {})


def _declared_hook_types(config: dict[str, object]) -> list[str]:
    """Return every hook type this config installs, plus the gate's own."""
    raw = config.get("default_install_hook_types")
    declared = (
        [t for t in raw if isinstance(t, str)]
        if isinstance(raw, list)
        else list(_PRE_COMMIT_DEFAULT_TYPES)
    )
    return declared if _GATE_HOOK_TYPE in declared else [*declared, _GATE_HOOK_TYPE]


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


def _undelivered_reason(hook: Path) -> str | None:
    """Return why *hook* does not deliver pre-commit, or None when it does."""
    if not hook.is_file():
        return "no hook file is installed"
    try:
        body = hook.read_text(encoding="utf-8", errors="replace")
    except OSError:
        body = ""
    return None if "pre-commit" in body else "the hook file is not the pre-commit shim"


def _delivery_errors(project_root: Path, hook_types: list[str]) -> list[ValidationError]:
    """Return errors for every declared hook type not installed on disk.

    A declared hook that was never delivered enforces nothing. This repo ran in
    exactly that state: ``.pre-commit-config.yaml`` declared ``gz-check-pre-push``
    while ``.git/hooks/`` held only stock samples, because a local
    ``core.hooksPath`` made ``pre-commit install`` refuse. The declaration arm
    stayed green the whole time.

    Every type in ``default_install_hook_types`` is checked, never one literal
    (GHI #851): the witness read ``pre-push`` alone while four types were
    declared, so a clone with no ``pre-commit`` hook reported green. A missing
    recording hook is emitted as an advisory rather than returned.
    """
    hooks_dir = _effective_hooks_dir(project_root)
    if hooks_dir is None:
        # Not a git worktree (fixture tree, sdist export) — delivery is not
        # assertable here, and the declaration arm still applies.
        return []
    errors: list[ValidationError] = []
    for hook_type in hook_types:
        reason = _undelivered_reason(hooks_dir / hook_type)
        recovery = _delivery_recovery(hook_types)
        if reason is None and hook_type == "post-commit":
            # The shim alone records nothing: the recorder runs as its legacy
            # hook, outside pre-commit's stash (GHI #1092).
            reason = recorder_undelivered_reason(hooks_dir)
            recovery = "Recovery: `uv run -m gzkit.hooks.commit_ledger --install`."
        if reason is None:
            continue
        artifact = f"{hooks_dir.as_posix()}/{hook_type}"
        if hook_type in _RECORDING_HOOK_TYPES:
            emit_advisory(
                f"session-green-gate: declared '{hook_type}' hook is not delivered — "
                f"{reason} at {artifact}. It records and gates nothing, so this does not "
                f"block; its record is lost until it is installed. {recovery}"
            )
            continue
        errors.append(
            ValidationError(
                type="session_green_gate",
                artifact=artifact,
                message=(
                    f"Declared '{hook_type}' hook is not delivered — {reason} at {artifact}, "
                    f"so the checks it runs are unenforced. {_delivery_recovery(hook_types)}"
                ),
            )
        )
    return errors


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
    return _delivery_errors(project_root, _declared_hook_types(config)) if check_delivery else []
