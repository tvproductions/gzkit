"""BDD steps for gz upgrade surface-only refresh.

@covers REQ-0.0.32-14-03
@covers REQ-0.0.32-14-04
@covers REQ-0.0.32-14-06
@covers REQ-0.0.32-14-07
@covers REQ-0.0.32-14-08
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from behave import given, then


@given("I record the manifest checksum")
def step_record_manifest_checksum(context) -> None:
    manifest_path = Path(".gzkit/manifest.json")
    if manifest_path.exists():
        context.manifest_before = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    else:
        context.manifest_before = None


@then("the manifest checksum is unchanged")
def step_manifest_checksum_unchanged(context) -> None:
    manifest_path = Path(".gzkit/manifest.json")
    if context.manifest_before is None:
        assert not manifest_path.exists(), "upgrade must not create manifest.json"
    else:
        after = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        assert context.manifest_before == after, (
            f"manifest.json was mutated by gz upgrade: {context.manifest_before!r} → {after!r}"
        )


@given('the project has an EDITED skill at "{path}"')
def step_edited_skill(context, path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"# Operator-edited skill\n<!-- gzkit-canonical-version: 0.0.0 -->\nedited\n")


@given("the .gzkit/skills directory is removed")
def step_remove_skills_dir(context) -> None:
    skills = Path(".gzkit/skills")
    if skills.exists():
        shutil.rmtree(skills)


@then('"{path}" exists after the command')
def step_path_exists(context, path: str) -> None:
    assert Path(path).exists(), f"expected {path!r} to exist after the command"
