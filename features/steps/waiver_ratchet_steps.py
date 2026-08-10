"""BDD fixture steps for gz validate --waiver-ratchet scenarios (OBPI-0.0.73-09).

The shared When/Then steps (``When I run``, ``Then it exits with code``,
``And the output contains``) live in features/steps/gz_steps.py; only the
registry-fixture Given steps are defined here.

@covers REQ-0.0.73-09-01
@covers REQ-0.0.73-09-02
@covers REQ-0.0.73-09-03
@covers REQ-0.0.73-09-06
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from behave import given


def _write(root: Path, rel: str, payload: object) -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload), encoding="utf-8")


def _registry(
    root: Path, surfaces: list[dict[str, object]], excluded: list[str] | None = None
) -> None:
    _write(
        root,
        "data/waiver_ratchet_registry.json",
        {"schema_version": 1, "surfaces": surfaces, "excluded": excluded or []},
    )


@given("a project where every registered waiver surface is ratcheted")
def step_ratcheted(context) -> None:
    root: Path = context._tmpdir
    _registry(
        root,
        [
            {
                "data_file": "data/example_waivers.json",
                "mechanism": "shrink-ratchet",
                "entries_path": "waivers",
                "baseline_count": 2,
            }
        ],
    )
    _write(root, "data/example_waivers.json", {"waivers": ["a", "b"]})
    os.chdir(root)


@given("a project with a waiver surface grown past its committed baseline")
def step_grown(context) -> None:
    root: Path = context._tmpdir
    _registry(
        root,
        [
            {
                "data_file": "data/example_waivers.json",
                "mechanism": "shrink-ratchet",
                "entries_path": "waivers",
                "baseline_count": 0,
            }
        ],
    )
    _write(root, "data/example_waivers.json", {"waivers": ["grew", "past", "baseline"]})
    os.chdir(root)


@given("a project with an unregistered waiver data file")
def step_unregistered(context) -> None:
    root: Path = context._tmpdir
    _registry(root, [])
    _write(root, "data/sneaky_waivers.json", {"waivers": ["a"]})
    os.chdir(root)
