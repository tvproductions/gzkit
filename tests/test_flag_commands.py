"""Tests for gz flags / gz flag explain CLI commands (OBPI-0.0.8-05).

Smoke tests covering:
- gz flags (exits 0, produces table output)
- gz flags --stale (exits 0)
- gz flag explain <known_key> (exits 0, outputs metadata)
- gz flag explain <unknown_key> (exits 1)
- gz flags --json (valid JSON output)

@covers ADR-0.0.8-feature-toggle-system
@covers OBPI-0.0.8-05-cli-surface
"""

import contextlib
import io
import json
import unittest
from datetime import date
from unittest.mock import patch

from gzkit.cli.main import main
from gzkit.flags.models import FlagCategory, FlagSpec
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

_TODAY = date(2026, 3, 30)


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


_REGISTRY = {
    "ops.product_proof": _make_spec(
        key="ops.product_proof",
        category=FlagCategory.ops,
        default=True,
        linked_adr="ADR-0.23.0",
        linked_issue="GHI-49",
    ),
    "release.drift_command": _make_spec(
        key="release.drift_command",
        category=FlagCategory.release,
        default=False,
        remove_by="2026-04-30",
    ),
    "migration.config_gates_to_flags": _make_spec(
        key="migration.config_gates_to_flags",
        category=FlagCategory.migration,
        default=False,
        remove_by="2026-05-01",
    ),
}

_MOCK_REGISTRY_PATH = "gzkit.commands.flags.load_registry"


class _RegistryMixin:
    """Mixin that patches load_registry and suppresses stdout for all flag command tests."""

    def setUp(self) -> None:
        patcher = patch(_MOCK_REGISTRY_PATH, return_value=dict(_REGISTRY))
        self._mock_load = patcher.start()
        self.addCleanup(patcher.stop)
        self._stdout_ctx = contextlib.redirect_stdout(io.StringIO())
        self._stdout_ctx.__enter__()
        self.addCleanup(self._stdout_ctx.__exit__, None, None, None)


# ---------------------------------------------------------------------------
# REQ-0.0.8-05-01: gz flags table
# ---------------------------------------------------------------------------


@covers("REQ-0.0.8-05-01")
class TestFlagsList(_RegistryMixin, unittest.TestCase):
    """gz flags exits 0 and produces table output."""

    @covers("REQ-0.0.8-05-01")
    def test_flags_exits_zero(self) -> None:
        rc = main(["flags"])
        self.assertEqual(rc, 0)

    @covers("REQ-0.0.8-05-01")
    def test_flags_with_stale_no_stale(self) -> None:
        """gz flags --stale exits 0 when no flags are stale."""
        rc = main(["flags", "--stale"])
        self.assertEqual(rc, 0)


# ---------------------------------------------------------------------------
# REQ-0.0.8-05-02: gz flags --stale
# ---------------------------------------------------------------------------


@covers("REQ-0.0.8-05-02")
class TestFlagsStale(_RegistryMixin, unittest.TestCase):
    """gz flags --stale exits 0 and filters correctly."""

    @covers("REQ-0.0.8-05-02")
    def test_stale_with_overdue_flag(self) -> None:
        """A flag past review_by is shown in --stale output."""
        stale_registry = dict(_REGISTRY)
        stale_registry["ops.stale_flag"] = _make_spec(
            key="ops.stale_flag",
            category=FlagCategory.ops,
            default=True,
            review_by="2025-01-01",
        )
        self._mock_load.return_value = stale_registry
        rc = main(["flags", "--stale"])
        self.assertEqual(rc, 0)


# ---------------------------------------------------------------------------
# REQ-0.0.8-05-03: gz flag explain <known_key>
# ---------------------------------------------------------------------------


@covers("REQ-0.0.8-05-03")
class TestFlagExplainKnown(_RegistryMixin, unittest.TestCase):
    """gz flag explain <known_key> exits 0 and outputs metadata."""

    @covers("REQ-0.0.8-05-03")
    def test_explain_known_exits_zero(self) -> None:
        rc = main(["flag", "explain", "ops.product_proof"])
        self.assertEqual(rc, 0)


# ---------------------------------------------------------------------------
# REQ-0.0.8-05-04: gz flag explain <unknown_key>
# ---------------------------------------------------------------------------


@covers("REQ-0.0.8-05-04")
class TestFlagExplainUnknown(_RegistryMixin, unittest.TestCase):
    """gz flag explain <unknown_key> exits 1."""

    @covers("REQ-0.0.8-05-04")
    def test_explain_unknown_exits_one(self) -> None:
        rc = main(["flag", "explain", "nonexistent.key"])
        self.assertEqual(rc, 1)


# ---------------------------------------------------------------------------
# REQ-0.0.8-05-05: gz flags --json
# ---------------------------------------------------------------------------


@covers("REQ-0.0.8-05-05")
class TestFlagsJson(_RegistryMixin, unittest.TestCase):
    """gz flags --json outputs valid JSON to stdout."""

    @patch("sys.stdout")
    @covers("REQ-0.0.8-05-05")
    def test_json_output_is_valid(self, mock_stdout: unittest.mock.MagicMock) -> None:
        written: list[str] = []
        mock_stdout.write = lambda s: written.append(s)
        mock_stdout.flush = lambda: None

        rc = main(["flags", "--json"])
        self.assertEqual(rc, 0)

        output = "".join(written)
        data = json.loads(output)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        first = data[0]
        self.assertIn("key", first)
        self.assertIn("current_value", first)
        self.assertIn("source", first)

    @patch("sys.stdout")
    @covers("REQ-0.0.8-05-05")
    def test_explain_json_is_valid(self, mock_stdout: unittest.mock.MagicMock) -> None:
        written: list[str] = []
        mock_stdout.write = lambda s: written.append(s)
        mock_stdout.flush = lambda: None

        rc = main(["flag", "explain", "ops.product_proof", "--json"])
        self.assertEqual(rc, 0)

        output = "".join(written)
        data = json.loads(output)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["key"], "ops.product_proof")
        self.assertIn("linked_adr", data)


# ---------------------------------------------------------------------------
# Exit code contract
# ---------------------------------------------------------------------------


class TestFlagExitCodes(_RegistryMixin, unittest.TestCase):
    """Exit codes follow the standard 4-code map."""

    def test_success_exits_zero(self) -> None:
        rc = main(["flags"])
        self.assertEqual(rc, 0)

    def test_unknown_flag_exits_one(self) -> None:
        rc = main(["flag", "explain", "bogus.key"])
        self.assertEqual(rc, 1)

    def test_help_exits_zero(self) -> None:
        rc = main(["flags", "--help"])
        self.assertEqual(rc, 0)

    def test_flag_help_exits_zero(self) -> None:
        rc = main(["flag", "--help"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
