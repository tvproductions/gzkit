"""Tests for flag diagnostics (OBPI-0.0.8-04).

Covers stale detection, flag health summary, and explain output.
"""

import unittest
from datetime import date

from gzkit.flags.diagnostics import (
    FlagExplanation,
    FlagHealthSummary,
    explain_flag,
    get_flag_health,
    get_stale_flags,
)
from gzkit.flags.models import FlagCategory, FlagSpec
from gzkit.flags.service import FlagService
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Stale detection tests
# ---------------------------------------------------------------------------


class TestGetStaleFlags(unittest.TestCase):
    """Validate get_stale_flags detection logic."""

    @covers("REQ-0.0.8-04-01")
    def test_flag_past_remove_by_is_stale(self) -> None:
        """A flag with remove_by in the past appears in the stale list."""
        spec = _make_spec(
            key="release.old_feature",
            category=FlagCategory.release,
            remove_by="2026-03-01",
        )
        registry = _registry(spec)
        stale = get_stale_flags(registry, as_of=date(2026, 3, 30))
        self.assertEqual(len(stale), 1)
        self.assertEqual(stale[0].key, "release.old_feature")

    @covers("REQ-0.0.8-04-01")
    def test_flag_past_review_by_is_stale(self) -> None:
        """An ops flag with review_by in the past appears in the stale list."""
        spec = _make_spec(
            key="ops.old_switch",
            category=FlagCategory.ops,
            review_by="2026-02-01",
        )
        registry = _registry(spec)
        stale = get_stale_flags(registry, as_of=date(2026, 3, 30))
        self.assertEqual(len(stale), 1)
        self.assertEqual(stale[0].key, "ops.old_switch")

    @covers("REQ-0.0.8-04-01")
    def test_non_stale_flags_excluded(self) -> None:
        """Flags with future deadlines are not stale."""
        spec = _make_spec(
            key="ops.active",
            category=FlagCategory.ops,
            review_by="2027-01-01",
        )
        registry = _registry(spec)
        stale = get_stale_flags(registry, as_of=date(2026, 3, 30))
        self.assertEqual(len(stale), 0)

    @covers("REQ-0.0.8-04-01")
    def test_flag_on_exact_date_not_stale(self) -> None:
        """A flag whose deadline is today is not stale (< not <=)."""
        spec = _make_spec(
            key="release.today",
            category=FlagCategory.release,
            remove_by="2026-03-30",
        )
        registry = _registry(spec)
        stale = get_stale_flags(registry, as_of=date(2026, 3, 30))
        self.assertEqual(len(stale), 0)

    @covers("REQ-0.0.8-04-01")
    def test_multiple_stale_flags_sorted(self) -> None:
        """Multiple stale flags are returned sorted by key."""
        spec_b = _make_spec(
            key="release.beta",
            category=FlagCategory.release,
            remove_by="2026-01-01",
        )
        spec_a = _make_spec(
            key="migration.alpha",
            category=FlagCategory.migration,
            remove_by="2026-02-01",
        )
        registry = _registry(spec_b, spec_a)
        stale = get_stale_flags(registry, as_of=date(2026, 3, 30))
        self.assertEqual(len(stale), 2)
        self.assertEqual(stale[0].key, "migration.alpha")
        self.assertEqual(stale[1].key, "release.beta")

    def test_defaults_to_today(self) -> None:
        """When as_of is omitted, uses today's date."""
        spec = _make_spec(
            key="ops.future",
            category=FlagCategory.ops,
            review_by="2099-01-01",
        )
        registry = _registry(spec)
        stale = get_stale_flags(registry)
        self.assertEqual(len(stale), 0)


# ---------------------------------------------------------------------------
# Health summary tests
# ---------------------------------------------------------------------------


class TestGetFlagHealth(unittest.TestCase):
    """Validate get_flag_health summary computation."""

    @covers("REQ-0.0.8-04-02")
    def test_healthy_registry(self) -> None:
        """No stale or approaching flags yields zero counts."""
        spec = _make_spec(
            key="ops.healthy",
            category=FlagCategory.ops,
            review_by="2027-01-01",
        )
        health = get_flag_health(_registry(spec), as_of=date(2026, 3, 30))
        self.assertIsInstance(health, FlagHealthSummary)
        self.assertEqual(health.total, 1)
        self.assertEqual(health.stale_count, 0)
        self.assertEqual(health.approaching_count, 0)
        self.assertEqual(health.category_counts, {"ops": 1})

    @covers("REQ-0.0.8-04-02")
    def test_stale_counted(self) -> None:
        """Stale flags are counted and listed."""
        spec = _make_spec(
            key="release.expired",
            category=FlagCategory.release,
            remove_by="2026-03-01",
        )
        health = get_flag_health(_registry(spec), as_of=date(2026, 3, 30))
        self.assertEqual(health.stale_count, 1)
        self.assertIn("release.expired", health.stale_keys)

    @covers("REQ-0.0.8-04-02")
    def test_approaching_counted(self) -> None:
        """Flags within 14 days of deadline are flagged as approaching."""
        spec = _make_spec(
            key="release.soon",
            category=FlagCategory.release,
            remove_by="2026-04-10",
        )
        health = get_flag_health(_registry(spec), as_of=date(2026, 3, 30))
        self.assertEqual(health.approaching_count, 1)
        self.assertIn("release.soon", health.approaching_keys)

    @covers("REQ-0.0.8-04-02")
    def test_category_counts(self) -> None:
        """Category counts are correct for mixed categories."""
        specs = [
            _make_spec(key="ops.a", category=FlagCategory.ops, review_by="2027-01-01"),
            _make_spec(key="ops.b", category=FlagCategory.ops, review_by="2027-01-01"),
            _make_spec(key="release.c", category=FlagCategory.release, remove_by="2027-01-01"),
        ]
        health = get_flag_health(_registry(*specs), as_of=date(2026, 3, 30))
        self.assertEqual(health.total, 3)
        self.assertEqual(health.category_counts, {"ops": 2, "release": 1})

    @covers("REQ-0.0.8-04-02")
    def test_stale_not_also_approaching(self) -> None:
        """A stale flag is not double-counted as approaching."""
        spec = _make_spec(
            key="release.expired",
            category=FlagCategory.release,
            remove_by="2026-03-01",
        )
        health = get_flag_health(_registry(spec), as_of=date(2026, 3, 30))
        self.assertEqual(health.stale_count, 1)
        self.assertEqual(health.approaching_count, 0)


# ---------------------------------------------------------------------------
# Explain tests
# ---------------------------------------------------------------------------


class TestExplainFlag(unittest.TestCase):
    """Validate explain_flag output fields."""

    @covers("REQ-0.0.8-04-04")
    def test_explain_includes_all_fields(self) -> None:
        """explain_flag returns key, category, default, value, source, dates."""
        spec = _make_spec(
            key="ops.product_proof",
            category=FlagCategory.ops,
            default=True,
            review_by="2026-06-29",
        )
        svc = FlagService(_registry(spec))
        result = explain_flag("ops.product_proof", svc)

        self.assertIsInstance(result, FlagExplanation)
        self.assertEqual(result.key, "ops.product_proof")
        self.assertEqual(result.category, "ops")
        self.assertTrue(result.default)
        self.assertTrue(result.current_value)
        self.assertEqual(result.source, "registry")
        self.assertEqual(result.owner, "test")
        self.assertEqual(result.review_by, date(2026, 6, 29))
        self.assertIsNotNone(result.days_until_review)

    @covers("REQ-0.0.8-04-04")
    def test_explain_shows_override_source(self) -> None:
        """When overridden, explain shows the override source."""
        spec = _make_spec(key="ops.product_proof", default=True)
        svc = FlagService(_registry(spec))
        svc.set_test_override("ops.product_proof", False)
        result = explain_flag("ops.product_proof", svc)

        self.assertFalse(result.current_value)
        self.assertEqual(result.source, "test")

    @covers("REQ-0.0.8-04-04")
    def test_explain_staleness_detected(self) -> None:
        """A flag past remove_by is marked stale in explain output."""
        spec = _make_spec(
            key="release.old",
            category=FlagCategory.release,
            remove_by="2020-01-01",
        )
        svc = FlagService(_registry(spec))
        result = explain_flag("release.old", svc)

        self.assertTrue(result.is_stale)
        self.assertIsNotNone(result.days_until_removal)
        self.assertLess(result.days_until_removal, 0)  # type: ignore[arg-type]

    @covers("REQ-0.0.8-04-04")
    def test_explain_days_remaining_positive(self) -> None:
        """A flag with future review_by shows positive days remaining."""
        spec = _make_spec(
            key="ops.future",
            category=FlagCategory.ops,
            review_by="2099-12-31",
        )
        svc = FlagService(_registry(spec))
        result = explain_flag("ops.future", svc)

        self.assertFalse(result.is_stale)
        self.assertIsNotNone(result.days_until_review)
        self.assertGreater(result.days_until_review, 0)  # type: ignore[arg-type]

    @covers("REQ-0.0.8-04-04")
    def test_explain_no_dates_when_absent(self) -> None:
        """Flags without review_by/remove_by show None for days fields."""
        spec = _make_spec(
            key="ops.minimal",
            category=FlagCategory.ops,
            review_by="2099-01-01",
        )
        svc = FlagService(_registry(spec))
        result = explain_flag("ops.minimal", svc)

        self.assertIsNone(result.remove_by)
        self.assertIsNone(result.days_until_removal)


if __name__ == "__main__":
    unittest.main()
