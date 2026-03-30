"""Tests for FlagService (OBPI-0.0.8-02).

Covers the five-layer precedence chain, override API, unknown/malformed flag
detection, env var naming, FlagEvaluation source attribution, and list_flags.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from gzkit.flags.models import (
    FlagCategory,
    FlagSpec,
    InvalidFlagValueError,
    UnknownFlagError,
)
from gzkit.flags.registry import load_registry
from gzkit.flags.service import FlagService
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

_SCHEMA_STUB = json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema"})


def _make_spec(
    key: str = "ops.product_proof",
    category: FlagCategory = FlagCategory.ops,
    default: bool = True,
    **kwargs: object,
) -> FlagSpec:
    """Build a minimal FlagSpec for tests."""
    base: dict[str, object] = {
        "key": key,
        "category": category,
        "default": default,
        "description": "Test flag.",
        "owner": "test",
        "introduced_on": "2026-03-29",
    }
    if category == FlagCategory.ops and "review_by" not in kwargs:
        base["review_by"] = "2026-06-29"
    if (
        category in (FlagCategory.release, FlagCategory.migration, FlagCategory.development)
        and "remove_by" not in kwargs
    ):
        base["remove_by"] = "2026-06-29"
    return FlagSpec.model_validate({**base, **kwargs})


def _registry(*specs: FlagSpec) -> dict[str, FlagSpec]:
    """Return a registry dict from spec instances."""
    return {s.key: s for s in specs}


def _service(
    specs: dict[str, FlagSpec] | None = None,
    config_flags: dict[str, bool] | None = None,
) -> FlagService:
    """Build a FlagService with sensible defaults."""
    if specs is None:
        specs = _registry(_make_spec())
    return FlagService(specs, config_flags=config_flags)


class _EnvPatch:
    """Context manager that sets an env var and restores on exit."""

    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value
        self._old: str | None = None

    def __enter__(self) -> None:
        self._old = os.environ.get(self.name)
        os.environ[self.name] = self.value

    def __exit__(self, *_: object) -> None:
        if self._old is None:
            os.environ.pop(self.name, None)
        else:
            os.environ[self.name] = self._old


# ---------------------------------------------------------------------------
# Precedence tests
# ---------------------------------------------------------------------------


class TestPrecedenceChain(unittest.TestCase):
    """Validate each layer of the five-layer precedence chain."""

    @covers("REQ-0.0.8-02-01")
    def test_registry_default_wins_when_no_overrides(self) -> None:
        svc = _service()
        self.assertTrue(svc.is_enabled("ops.product_proof"))

    @covers("REQ-0.0.8-02-01")
    def test_registry_default_false(self) -> None:
        spec = _make_spec(default=False)
        svc = _service(_registry(spec))
        self.assertFalse(svc.is_enabled("ops.product_proof"))

    @covers("REQ-0.0.8-02-02")
    def test_env_var_overrides_registry_default(self) -> None:
        svc = _service()
        with _EnvPatch("GZKIT_FLAG_OPS_PRODUCT_PROOF", "false"):
            self.assertFalse(svc.is_enabled("ops.product_proof"))

    @covers("REQ-0.0.8-02-03")
    def test_config_overrides_env_var(self) -> None:
        svc = _service(config_flags={"ops.product_proof": True})
        with _EnvPatch("GZKIT_FLAG_OPS_PRODUCT_PROOF", "false"):
            self.assertTrue(svc.is_enabled("ops.product_proof"))

    @covers("REQ-0.0.8-02-04")
    def test_test_override_wins_over_config(self) -> None:
        svc = _service(config_flags={"ops.product_proof": True})
        svc.set_test_override("ops.product_proof", False)
        self.assertFalse(svc.is_enabled("ops.product_proof"))

    def test_runtime_override_wins_over_test_override(self) -> None:
        svc = _service()
        svc.set_test_override("ops.product_proof", False)
        svc.set_runtime_override("ops.product_proof", True)
        self.assertTrue(svc.is_enabled("ops.product_proof"))


class TestEnvVarNaming(unittest.TestCase):
    """Validate GZKIT_FLAG_<KEY> naming convention."""

    def test_dots_replaced_with_underscores_and_uppercased(self) -> None:
        self.assertEqual(
            FlagService._env_var_name("ops.product_proof"),
            "GZKIT_FLAG_OPS_PRODUCT_PROOF",
        )

    def test_nested_dots(self) -> None:
        self.assertEqual(
            FlagService._env_var_name("migration.config_gates_to_flags"),
            "GZKIT_FLAG_MIGRATION_CONFIG_GATES_TO_FLAGS",
        )


class TestEnvVarBooleanParsing(unittest.TestCase):
    """Validate boolean parsing for env var values."""

    TRUE_VALUES = ["true", "True", "TRUE", "1", "yes", "Yes", "YES"]
    FALSE_VALUES = ["false", "False", "FALSE", "0", "no", "No", "NO"]

    def test_true_strings(self) -> None:
        for val in self.TRUE_VALUES:
            with self.subTest(val=val):
                svc = _service()
                # Registry default is True, set env to confirm parsing works
                spec_false = _make_spec(default=False)
                svc = _service(_registry(spec_false))
                with _EnvPatch("GZKIT_FLAG_OPS_PRODUCT_PROOF", val):
                    self.assertTrue(svc.is_enabled("ops.product_proof"))

    def test_false_strings(self) -> None:
        for val in self.FALSE_VALUES:
            with self.subTest(val=val):
                svc = _service()
                with _EnvPatch("GZKIT_FLAG_OPS_PRODUCT_PROOF", val):
                    self.assertFalse(svc.is_enabled("ops.product_proof"))

    @covers("REQ-0.0.8-02-06")
    def test_invalid_env_value_raises(self) -> None:
        svc = _service()
        with (
            _EnvPatch("GZKIT_FLAG_OPS_PRODUCT_PROOF", "maybe"),
            self.assertRaises(InvalidFlagValueError),
        ):
            svc.is_enabled("ops.product_proof")


# ---------------------------------------------------------------------------
# Unknown flag tests
# ---------------------------------------------------------------------------


class TestUnknownFlag(unittest.TestCase):
    """Validate that unknown keys are hard errors."""

    @covers("REQ-0.0.8-02-05")
    def test_is_enabled_unknown_raises(self) -> None:
        svc = _service()
        with self.assertRaises(UnknownFlagError):
            svc.is_enabled("nonexistent.flag")

    def test_evaluate_unknown_raises(self) -> None:
        svc = _service()
        with self.assertRaises(UnknownFlagError):
            svc.evaluate("nonexistent.flag")

    def test_set_test_override_unknown_raises(self) -> None:
        svc = _service()
        with self.assertRaises(UnknownFlagError):
            svc.set_test_override("nonexistent.flag", True)

    def test_set_runtime_override_unknown_raises(self) -> None:
        svc = _service()
        with self.assertRaises(UnknownFlagError):
            svc.set_runtime_override("nonexistent.flag", True)


# ---------------------------------------------------------------------------
# Override lifecycle tests
# ---------------------------------------------------------------------------


class TestOverrideLifecycle(unittest.TestCase):
    """Validate test and runtime override set/clear semantics."""

    @covers("REQ-0.0.8-02-04")
    def test_clear_test_overrides_restores_prior_resolution(self) -> None:
        svc = _service()  # default True
        svc.set_test_override("ops.product_proof", False)
        self.assertFalse(svc.is_enabled("ops.product_proof"))
        svc.clear_test_overrides()
        self.assertTrue(svc.is_enabled("ops.product_proof"))

    def test_multiple_test_overrides_independent(self) -> None:
        spec_a = _make_spec("ops.product_proof")
        spec_b = _make_spec(
            "migration.config_gates_to_flags",
            category=FlagCategory.migration,
            default=False,
        )
        svc = _service(_registry(spec_a, spec_b))
        svc.set_test_override("ops.product_proof", False)
        svc.set_test_override("migration.config_gates_to_flags", True)
        self.assertFalse(svc.is_enabled("ops.product_proof"))
        self.assertTrue(svc.is_enabled("migration.config_gates_to_flags"))
        svc.clear_test_overrides()
        self.assertTrue(svc.is_enabled("ops.product_proof"))
        self.assertFalse(svc.is_enabled("migration.config_gates_to_flags"))

    def test_runtime_override_persists_after_clear_test(self) -> None:
        svc = _service()
        svc.set_test_override("ops.product_proof", False)
        svc.set_runtime_override("ops.product_proof", True)
        svc.clear_test_overrides()
        # Runtime override still active
        self.assertTrue(svc.is_enabled("ops.product_proof"))


# ---------------------------------------------------------------------------
# FlagEvaluation source attribution
# ---------------------------------------------------------------------------


class TestEvaluation(unittest.TestCase):
    """Validate evaluate() returns correct source attribution."""

    @covers("REQ-0.0.8-02-07")
    def test_source_env_when_env_set(self) -> None:
        spec = _make_spec(default=True)
        svc = _service(_registry(spec))
        with _EnvPatch("GZKIT_FLAG_OPS_PRODUCT_PROOF", "false"):
            ev = svc.evaluate("ops.product_proof")
            self.assertEqual(ev.source, "env")
            self.assertFalse(ev.value)
            self.assertEqual(ev.key, "ops.product_proof")

    def test_source_registry(self) -> None:
        svc = _service()
        ev = svc.evaluate("ops.product_proof")
        self.assertEqual(ev.source, "registry")

    def test_source_config(self) -> None:
        svc = _service(config_flags={"ops.product_proof": False})
        ev = svc.evaluate("ops.product_proof")
        self.assertEqual(ev.source, "config")

    def test_source_test_override(self) -> None:
        svc = _service()
        svc.set_test_override("ops.product_proof", False)
        ev = svc.evaluate("ops.product_proof")
        self.assertEqual(ev.source, "test")

    def test_source_runtime_override(self) -> None:
        svc = _service()
        svc.set_runtime_override("ops.product_proof", False)
        ev = svc.evaluate("ops.product_proof")
        self.assertEqual(ev.source, "runtime")


# ---------------------------------------------------------------------------
# list_flags
# ---------------------------------------------------------------------------


class TestListFlags(unittest.TestCase):
    """Validate list_flags returns all flags sorted by key."""

    def test_list_flags_returns_all_sorted(self) -> None:
        spec_a = _make_spec("ops.product_proof")
        spec_b = _make_spec(
            "migration.config_gates_to_flags",
            category=FlagCategory.migration,
            default=False,
        )
        svc = _service(_registry(spec_a, spec_b))
        results = svc.list_flags()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].key, "migration.config_gates_to_flags")
        self.assertEqual(results[1].key, "ops.product_proof")

    def test_list_flags_reflects_overrides(self) -> None:
        svc = _service()
        svc.set_test_override("ops.product_proof", False)
        results = svc.list_flags()
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].value)
        self.assertEqual(results[0].source, "test")


# ---------------------------------------------------------------------------
# Integration: service constructed from real registry
# ---------------------------------------------------------------------------


class TestRegistryIntegration(unittest.TestCase):
    """Verify FlagService works with the registry loader."""

    def test_service_from_load_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            registry_path = tmp_path / "flags.json"
            schema_path = tmp_path / "flags.schema.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "flags": [
                            {
                                "key": "ops.test_flag",
                                "category": "ops",
                                "default": True,
                                "description": "Integration test flag.",
                                "owner": "test",
                                "introduced_on": "2026-03-29",
                                "review_by": "2026-06-29",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            schema_path.write_text(_SCHEMA_STUB, encoding="utf-8")

            reg = load_registry(registry_path, schema_path=schema_path)
            svc = FlagService(reg)
            self.assertTrue(svc.is_enabled("ops.test_flag"))


if __name__ == "__main__":
    unittest.main()
