"""BDD fixture steps for gz validate --setpoint-coherence scenarios (OBPI-0.0.37-20).

The shared When/Then steps (``When I run``, ``Then it exits with code``,
``And the output contains``) live in features/steps/gz_steps.py; only the
manifest-fixture Given steps are defined here.

@covers REQ-0.0.37-20-01
@covers REQ-0.0.37-20-02
@covers REQ-0.0.37-20-03
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from behave import given


def _write_manifest(root: Path, payload: dict) -> None:
    """Write a vendor-manifest fixture under ``root/data`` and chdir to root."""
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "vendor-manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.chdir(root)


@given("a project whose vendor manifest declares a setpoint for every routed pair")
def step_manifest_coherent(context) -> None:
    """Every (content_type, vendor) pair in routes has a legal setpoint."""
    _write_manifest(
        context._tmpdir,
        {
            "content_type_routes": {"AgentContract": ["claude", "codex"]},
            "content_type_temperatures": {"AgentContract": {"claude": "heavy", "codex": "lite"}},
        },
    )


@given("a project whose vendor manifest routes a pair with no declared setpoint")
def step_manifest_missing_setpoint(context) -> None:
    """A routed pair (AgentContract, codex) has no setpoint declared."""
    _write_manifest(
        context._tmpdir,
        {
            "content_type_routes": {"AgentContract": ["claude", "codex"]},
            "content_type_temperatures": {"AgentContract": {"claude": "heavy"}},
        },
    )


@given("a project whose vendor manifest declares an illegal setpoint token")
def step_manifest_illegal_token(context) -> None:
    """A declared setpoint token is outside {lite, medium, heavy}."""
    _write_manifest(
        context._tmpdir,
        {
            "content_type_routes": {"AgentContract": ["claude"]},
            "content_type_temperatures": {"AgentContract": {"claude": "frozen"}},
        },
    )
