"""Negative control for the session-green gate's delivery arm (GHI #851, GHI #1007).

The arm checked one hook type while ``.pre-commit-config.yaml`` declared four, and
the claim covering the gate never reached the arm: its entrypoint ran the audit
without ``check_delivery`` against a tree carrying no ``.git``. This control plants
an undelivered hook at every type the project declares.

The population is read from the declaring surface by this module's own parser,
never through ``session_green_gate._declared_hook_types``. A population derived
from the witness's reader narrows whenever the witness does, and proves nothing.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from gzkit.enforcement import create_fixture_tempdir

_CONFIG_NAME = ".pre-commit-config.yaml"

#: pre-commit's own default plus the gate's hook, used when the project declares no
#: list — the set a plain `pre-commit install` and the gate together require.
_UNDECLARED_TYPES = ("pre-commit", "pre-push")

_SHIM = "#!/usr/bin/env bash\nexec pre-commit hook-impl --hook-type={}\n"


def hook_type_population() -> list[str]:
    """Return every hook type the working project's config declares.

    Reads the project the floor runs in (``gz check`` runs at the project root), so
    a type added to ``default_install_hook_types`` joins the population the moment
    it is declared — the growth the witness failed to follow.
    """
    config = Path.cwd() / _CONFIG_NAME
    # A project with no config still owes the pair the gate requires; its absence is
    # the declaration arm's finding, never a reason this control cannot run.
    raw = yaml.safe_load(config.read_text(encoding="utf-8")) if config.is_file() else None
    declared = raw.get("default_install_hook_types") if isinstance(raw, dict) else None
    types = [t for t in declared if isinstance(t, str)] if isinstance(declared, list) else []
    return list(dict.fromkeys([*(types or _UNDECLARED_TYPES), "pre-push"]))


def build_undelivered_hook(member: str) -> Path:
    """Declare every population type and install all but *member*."""
    population = hook_type_population()
    root = create_fixture_tempdir(prefix="gzkit-qc-nc-session-green-gate-delivery-")
    (root / _CONFIG_NAME).write_text(
        f"default_install_hook_types: [{', '.join(population)}]\n"
        "repos:\n"
        "  - repo: local\n"
        "    hooks:\n"
        "      - id: gz-check-pre-push\n"
        "        name: gz check (pre-push gate)\n"
        "        entry: uv run gz check\n"
        "        language: system\n"
        "        pass_filenames: false\n"
        "        stages: [pre-push]\n",
        encoding="utf-8",
    )
    hooks = root / ".git" / "hooks"
    hooks.mkdir(parents=True)
    for hook_type in population:
        if hook_type != member:
            (hooks / hook_type).write_text(_SHIM.format(hook_type), encoding="utf-8")
    return root
