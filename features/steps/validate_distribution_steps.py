"""BDD steps for gz validate --distribution scenarios (OBPI-0.0.32-07).

@covers REQ-0.0.32-07-01
@covers REQ-0.0.32-07-02
@covers REQ-0.0.32-07-03
@covers REQ-0.0.32-07-05
@covers REQ-0.0.32-07-11
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from behave import given

#: A uv_build project whose wheel is ``src/gzkit`` minus the given excludes.
_UV_BUILD = (
    '[project]\nname = "py-gzkit"\n\n'
    '[build-system]\nbuild-backend = "uv_build"\n\n'
    '[tool.uv.build-backend]\nmodule-name = "gzkit"\nmodule-root = "src"\n'
    "wheel-exclude = [{wheel_exclude}]\n"
)


@given("a minimal project with a skills surface file the wheel excludes")
def step_minimal_project_on_disk_not_included(context) -> None:
    """Set up a temp project where a skill file exists but a wheel-exclude removes it."""
    root: Path = context._tmpdir

    skill = root / "src" / "gzkit" / "skills" / "test-skill" / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text("# Test\n", encoding="utf-8")

    (root / "pyproject.toml").write_text(
        _UV_BUILD.format(wheel_exclude='"skills/test-skill"'),
        encoding="utf-8",
    )

    data_dir = root / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "distribution_baseline_manifest.json").write_text(
        json.dumps({"schema_version": "1.0", "surfaces": {"skills": []}}),
        encoding="utf-8",
    )

    # gz_steps.py's _invoke uses the cwd; set it to the temp project root
    os.chdir(root)


@given("a minimal clean distribution baseline project")
def step_minimal_clean_distribution_project(context) -> None:
    """Set up a temp project where --distribution --regenerate has valid inputs."""
    root: Path = context._tmpdir

    skill = root / "src" / "gzkit" / "skills" / "test-skill" / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text("# Test\n", encoding="utf-8")

    (root / "pyproject.toml").write_text(
        _UV_BUILD.format(wheel_exclude=""),
        encoding="utf-8",
    )

    data_dir = root / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "distribution_baseline_manifest.json").write_text(
        json.dumps({"schema_version": "1.0", "surfaces": {"skills": []}}),
        encoding="utf-8",
    )

    (root / ".gzkit").mkdir(exist_ok=True)
    os.chdir(root)
