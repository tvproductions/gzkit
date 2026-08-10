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


@given("a minimal project with a skills surface file not covered by any include glob")
def step_minimal_project_on_disk_not_included(context) -> None:
    """Set up a temp project where a skill file exists but no include glob covers it."""
    root: Path = context._tmpdir

    skill = root / "src" / "gzkit" / "skills" / "test-skill" / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text("# Test\n", encoding="utf-8")

    (root / "pyproject.toml").write_text(
        '[tool.hatch.build.targets.wheel]\ninclude = [\n    "src/gzkit/rules/**/*.md",\n]\n',
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
        '[tool.hatch.build.targets.wheel]\ninclude = [\n    "src/gzkit/skills/**/*.md",\n]\n',
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
