"""BDD fixtures for generated and operator-owned Codex configuration."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from behave import given, then


@given("an unmarked operator Codex config exists")
def step_unmarked_operator_codex_config(_context) -> None:
    target = Path(".codex/config.toml")
    target.parent.mkdir(parents=True, exist_ok=True)
    content = b'# operator config\nmodel = "gpt-5.4"\napproval_policy = "on-request"\n'
    target.write_bytes(content)
    _context.operator_codex_config = content


@given('the Codex config path is configured as "{configured_path}"')
def step_configure_codex_path(_context, configured_path: str) -> None:
    config_path = Path(".gzkit.json")
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload.setdefault("paths", {})["codex_config"] = configured_path
    config_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


@given("the managed Codex config has operator settings")
def step_customize_managed_codex_config(_context) -> None:
    target = Path(".codex/config.toml")
    content = target.read_bytes() + b'\nmodel = "gpt-5.4"\n'
    target.write_bytes(content)
    _context.operator_codex_config = content


@given("the managed Codex config has drifted")
def step_drift_managed_codex_config(_context) -> None:
    config_path = Path(".codex/config.toml")
    content = config_path.read_text(encoding="utf-8")
    assert "# gzkit-managed-codex-config: v1" in content, content
    drifted = content.replace("network_access = true", "network_access = false")
    assert drifted != content, "Codex config fixture did not contain the managed baseline"
    config_path.write_text(drifted, encoding="utf-8")


@given("the managed Codex config is missing")
def step_remove_managed_codex_config(_context) -> None:
    Path(".codex/config.toml").unlink()


@then("the Codex config equals the original operator bytes")
def step_operator_codex_config_preserved(context) -> None:
    assert Path(".codex/config.toml").read_bytes() == context.operator_codex_config


@then("the managed Codex baseline is parseable and complete")
def step_managed_codex_config_complete(_context) -> None:
    payload = tomllib.loads(Path(".codex/config.toml").read_text(encoding="utf-8"))
    assert payload["sandbox_mode"] == "workspace-write", payload
    assert payload["features"]["hooks"] is True, payload
    assert payload["sandbox_workspace_write"]["network_access"] is True, payload


@then('the manifest Codex config path equals "{expected}"')
def step_manifest_codex_config_path(_context, expected: str) -> None:
    payload = json.loads(Path(".gzkit/manifest.json").read_text(encoding="utf-8"))
    assert payload["control_surfaces"]["codex_config"] == expected, payload
