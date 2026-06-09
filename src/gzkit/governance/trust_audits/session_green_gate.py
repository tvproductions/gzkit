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


def _runs_gz_check(entry: str) -> bool:
    """Return True when *entry* invokes ``gz check`` as a command, not a prefix.

    Token-adjacency match: ``gz`` immediately followed by the bare ``check``
    token. Rejects check-prefixed sibling verbs (e.g. ``gz check-config-paths``)
    that an unbounded substring match would false-pass (#600).
    """
    tokens = entry.split()
    return any(tokens[i] == "gz" and tokens[i + 1] == "check" for i in range(len(tokens) - 1))


def audit_session_green_gate(project_root: Path) -> list[ValidationError]:
    """Return errors if no stages: [pre-push] hook running gz check is declared.

    Fails closed when .pre-commit-config.yaml is missing, unparseable, or
    contains no hook with stages: [pre-push] and entry containing 'gz check'.
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
    return []
