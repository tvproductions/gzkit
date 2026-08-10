"""REQ-derived tests for the ThresholdTable loader (OBPI-0.0.28-02).

The loader at ``src/gzkit/complexity/thresholds.py`` parses
``.gzkit/rules/complexity-thresholds.json`` (data) into a frozen Pydantic
``ThresholdTable`` consumed by ADR-0.0.29 advisor and ADR-0.0.30
authoring-guidance. The sibling ``.gzkit/rules/complexity-thresholds.md``
carries doctrine narrative only (GHI #426 — data is JSON, narrative is
markdown). These tests pin the operator-facing contract: model
immutability, schema validation, parser fail-closed behavior, lookup
method semantics, and JSON Schema mirror parity.

Coverage:
    REQ-0.0.28-02-01 — well-formed data file parses to frozen
        ``ThresholdTable`` with bands and citation populated.
    REQ-0.0.28-02-02 — data where any metric lacks a ``block`` band
        fails with ``ValidationError`` naming the metric.
    REQ-0.0.28-02-03 — band with trigger-semantic outside
        ``{block, warn, advise}`` fails with ``ValidationError``.
    REQ-0.0.28-02-04 — band missing ``corpus_percentile`` or
        ``absolute_number`` fails with ``ValidationError``.
    REQ-0.0.28-02-05 — ``band_for("radon_cc", 13)`` against bands
        ``(p75=4=advise, p90=7=warn, p95=11=block)`` returns the block
        band (highest severity crossed).
    REQ-0.0.28-02-06 — ``band_for("radon_cc", 5)`` returns the advise
        band (5 >= 4 but < 7).
    REQ-0.0.28-02-07 — mutation attempt on ``ThresholdTable`` instance
        raises ``ValidationError``.
    REQ-0.0.28-02-08 — JSON Schema validates a known-good loaded table
        dict and rejects an unknown trigger-semantic.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from gzkit.complexity.thresholds import (
    CANONICAL_PERCENTILES,
    TRIGGER_VOCABULARY,
    ThresholdBand,
    ThresholdTable,
    load_threshold_table,
)
from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_REAL_DATA_PATH = _PROJECT_ROOT / ".gzkit" / "rules" / "complexity-thresholds.json"
_SCHEMA_PATH = _PROJECT_ROOT / "src" / "gzkit" / "schemas" / "complexity_thresholds.json"


def _well_formed_data() -> dict[str, Any]:
    """Synthetic well-formed data payload covering all 12 canonical metrics."""
    metrics_with_bands = [
        ("radon_cc", 4.0, 7.0, 11.0, 95),
        ("radon_mi", 85.0, 70.0, 50.0, 95),
        ("radon_hal_volume", 946.89, 2740.93, 5549.80, 95),
        ("radon_hal_difficulty", 8.13, 11.54, 12.46, 95),
        ("radon_hal_effort", 7975.79, 30805.01, 74805.40, 95),
        ("radon_raw_nloc", 311.75, 733.20, 1031.90, 95),
        ("radon_raw_lloc", 238.25, 518.00, 811.70, 95),
        ("lizard_nloc", 13.0, 25.0, 37.0, 95),
        ("lizard_param_count", 3.0, 4.0, 5.0, 95),
        ("lizard_nesting_depth", 2.0, 3.0, 4.0, 99),
        ("lizard_ccn", 4.0, 8.0, 11.0, 95),
        ("cohesion_lcom4", 2.0, 4.0, 8.0, 99),
    ]
    bands: list[dict[str, Any]] = []
    for metric, advise, warn, block, block_pct in metrics_with_bands:
        bands.extend(
            [
                {
                    "metric": metric,
                    "corpus_percentile": 75,
                    "absolute_number": advise,
                    "trigger_semantic": "advise",
                },
                {
                    "metric": metric,
                    "corpus_percentile": 90,
                    "absolute_number": warn,
                    "trigger_semantic": "warn",
                },
                {
                    "metric": metric,
                    "corpus_percentile": block_pct,
                    "absolute_number": block,
                    "trigger_semantic": "block",
                },
            ]
        )
    return {
        "corpus_revision": 1,
        "citation": {
            "distilled_characteristics_path": (
                "docs/governance/complexity/distilled-characteristics-2026-05-04.md"
            ),
            "section_anchor": "radon-cc",
            "corpus_revision": 1,
        },
        "bands": bands,
    }


def _write_data_fixture(payload: dict[str, Any]) -> Path:
    """Write a fixture data payload to a tempfile and return the Path."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    ) as handle:
        json.dump(payload, handle)
        return Path(handle.name)


class ThresholdBandModel(unittest.TestCase):
    """Pin the ThresholdBand Pydantic model contract."""

    @covers("REQ-0.0.28-02-01")
    def test_well_formed_band_instantiates(self) -> None:
        band = ThresholdBand(
            metric="radon_cc",
            corpus_percentile=90,
            absolute_number=7.0,
            trigger_semantic="warn",
        )
        self.assertEqual(band.metric, "radon_cc")
        self.assertEqual(band.corpus_percentile, 90)
        self.assertEqual(band.absolute_number, 7.0)
        self.assertEqual(band.trigger_semantic, "warn")

    @covers("REQ-0.0.28-02-03")
    def test_unknown_trigger_semantic_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            ThresholdBand(
                metric="radon_cc",
                corpus_percentile=90,
                absolute_number=7.0,
                trigger_semantic="info",
            )

    @covers("REQ-0.0.28-02-04")
    def test_out_of_enum_percentile_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            ThresholdBand(
                metric="radon_cc",
                corpus_percentile=80,
                absolute_number=7.0,
                trigger_semantic="warn",
            )

    @covers("REQ-0.0.28-02-04")
    def test_missing_absolute_number_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            ThresholdBand.model_validate(
                {
                    "metric": "radon_cc",
                    "corpus_percentile": 90,
                    "trigger_semantic": "warn",
                }
            )

    @covers("REQ-0.0.28-02-07")
    def test_band_is_frozen(self) -> None:
        band = ThresholdBand(
            metric="radon_cc",
            corpus_percentile=90,
            absolute_number=7.0,
            trigger_semantic="warn",
        )
        with self.assertRaises(ValidationError):
            band.metric = "radon_mi"  # ty: ignore[invalid-assignment]


class ThresholdTableModel(unittest.TestCase):
    """Pin the ThresholdTable Pydantic model contract."""

    def _make_radon_cc_table(self) -> ThresholdTable:
        from gzkit.complexity.citation import Citation

        bands = (
            ThresholdBand(
                metric="radon_cc",
                corpus_percentile=75,
                absolute_number=4.0,
                trigger_semantic="advise",
            ),
            ThresholdBand(
                metric="radon_cc",
                corpus_percentile=90,
                absolute_number=7.0,
                trigger_semantic="warn",
            ),
            ThresholdBand(
                metric="radon_cc",
                corpus_percentile=95,
                absolute_number=11.0,
                trigger_semantic="block",
            ),
        )
        return ThresholdTable(
            corpus_revision=1,
            bands=bands,
            citation=Citation(
                distilled_characteristics_path=(
                    "docs/governance/complexity/distilled-characteristics-2026-05-04.md"
                ),
                section_anchor="radon-cc",
                corpus_revision=1,
            ),
        )

    @covers("REQ-0.0.28-02-05")
    def test_band_for_returns_highest_severity_band_crossed(self) -> None:
        table = self._make_radon_cc_table()
        result = table.band_for("radon_cc", 13.0)
        self.assertIsNotNone(result)
        if result is not None:
            self.assertEqual(result.trigger_semantic, "block")

    @covers("REQ-0.0.28-02-05")
    def test_band_for_returns_warn_when_value_between_bands(self) -> None:
        table = self._make_radon_cc_table()
        result = table.band_for("radon_cc", 8.0)
        self.assertIsNotNone(result)
        if result is not None:
            self.assertEqual(result.trigger_semantic, "warn")

    @covers("REQ-0.0.28-02-06")
    def test_band_for_returns_advise_when_value_only_crosses_lowest(self) -> None:
        table = self._make_radon_cc_table()
        result = table.band_for("radon_cc", 5.0)
        self.assertIsNotNone(result)
        if result is not None:
            self.assertEqual(result.trigger_semantic, "advise")

    @covers("REQ-0.0.28-02-06")
    def test_band_for_returns_none_below_all_bands(self) -> None:
        table = self._make_radon_cc_table()
        self.assertIsNone(table.band_for("radon_cc", 2.0))

    @covers("REQ-0.0.28-02-05")
    def test_bands_for_metric_sorted_ascending_by_percentile(self) -> None:
        table = self._make_radon_cc_table()
        bands = table.bands_for_metric("radon_cc")
        percentiles = [b.corpus_percentile for b in bands]
        self.assertEqual(percentiles, sorted(percentiles))

    @covers("REQ-0.0.28-02-07")
    def test_table_is_frozen(self) -> None:
        table = self._make_radon_cc_table()
        with self.assertRaises(ValidationError):
            table.corpus_revision = 2  # ty: ignore[invalid-assignment]

    @covers("REQ-0.0.28-02-07")
    def test_bands_is_immutable_tuple(self) -> None:
        table = self._make_radon_cc_table()
        with self.assertRaises(ValidationError):
            table.bands = ()  # ty: ignore[invalid-assignment]


class LoaderParser(unittest.TestCase):
    """Pin the load_threshold_table parser contract (JSON source)."""

    @covers("REQ-0.0.28-02-01")
    def test_well_formed_data_file_parses(self) -> None:
        data_path = _write_data_fixture(_well_formed_data())
        try:
            table = load_threshold_table(data_path)
            self.assertEqual(table.corpus_revision, 1)
            metrics_in_table = {b.metric for b in table.bands}
            from gzkit.complexity.measurement import CANONICAL_METRICS

            for canonical in CANONICAL_METRICS:
                with self.subTest(metric=canonical):
                    self.assertIn(canonical, metrics_in_table)
        finally:
            data_path.unlink(missing_ok=True)

    @covers("REQ-0.0.28-02-02")
    def test_metric_missing_block_band_rejected(self) -> None:
        payload = _well_formed_data()
        payload["bands"] = [
            band
            for band in payload["bands"]
            if not (band["metric"] == "radon_cc" and band["trigger_semantic"] == "block")
        ]
        data_path = _write_data_fixture(payload)
        try:
            with self.assertRaises(ValidationError) as ctx:
                load_threshold_table(data_path)
            self.assertIn("radon_cc", str(ctx.exception))
        finally:
            data_path.unlink(missing_ok=True)

    @covers("REQ-0.0.28-02-03")
    def test_unknown_trigger_semantic_in_data_rejected(self) -> None:
        payload = _well_formed_data()
        payload["bands"][0]["trigger_semantic"] = "info"
        data_path = _write_data_fixture(payload)
        try:
            with self.assertRaises(ValidationError):
                load_threshold_table(data_path)
        finally:
            data_path.unlink(missing_ok=True)

    @covers("REQ-0.0.28-02-04")
    def test_malformed_citation_rejected(self) -> None:
        payload = _well_formed_data()
        payload["citation"] = {
            "distilled_characteristics_path": "not/a/valid/governance/path.md",
            "section_anchor": "radon-cc",
            "corpus_revision": 1,
        }
        data_path = _write_data_fixture(payload)
        try:
            with self.assertRaises(ValidationError):
                load_threshold_table(data_path)
        finally:
            data_path.unlink(missing_ok=True)

    def test_non_json_suffix_rejected(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".md",
            delete=False,
            encoding="utf-8",
        ) as handle:
            handle.write("# narrative is not data")
            md_path = Path(handle.name)
        try:
            with self.assertRaises(ValueError) as ctx:
                load_threshold_table(md_path)
            self.assertIn(".json", str(ctx.exception))
        finally:
            md_path.unlink(missing_ok=True)


class LoaderIntegration(unittest.TestCase):
    """Pin the loader against the real landed data file."""

    @covers("REQ-0.0.28-02-01")
    def test_real_data_file_parses_with_twelve_metrics(self) -> None:
        from gzkit.complexity.measurement import CANONICAL_METRICS

        self.assertTrue(_REAL_DATA_PATH.is_file(), f"missing real data: {_REAL_DATA_PATH}")
        table = load_threshold_table(_REAL_DATA_PATH)
        self.assertEqual(table.corpus_revision, 1)
        metrics_seen = {b.metric for b in table.bands}
        self.assertEqual(metrics_seen, set(CANONICAL_METRICS))

    @covers("REQ-0.0.28-02-02")
    def test_real_data_has_block_band_per_metric(self) -> None:
        from gzkit.complexity.measurement import CANONICAL_METRICS

        table = load_threshold_table(_REAL_DATA_PATH)
        for metric in CANONICAL_METRICS:
            with self.subTest(metric=metric):
                bands = table.bands_for_metric(metric)
                triggers = {b.trigger_semantic for b in bands}
                self.assertIn(
                    "block",
                    triggers,
                    f"metric {metric!r} must have a block band",
                )

    @covers("REQ-0.0.28-01-04")
    def test_every_real_band_pairs_percentile_with_absolute_number(self) -> None:
        """REQ-0.0.28-01-04 — semantic check: every band has both fields populated.

        Loader validation already enforces this via Pydantic ``Field`` constraints
        on ``ThresholdBand``; this test pins the operator-facing contract that
        the real landed data carries the pairing for every band."""
        table = load_threshold_table(_REAL_DATA_PATH)
        self.assertGreater(len(table.bands), 0)
        for band in table.bands:
            with self.subTest(metric=band.metric, trigger=band.trigger_semantic):
                self.assertIn(band.corpus_percentile, CANONICAL_PERCENTILES)
                self.assertGreaterEqual(band.absolute_number, 0.0)


class JsonSchemaMirror(unittest.TestCase):
    """Pin the JSON Schema mirror parity with the Pydantic model."""

    @covers("REQ-0.0.28-02-08")
    def test_schema_file_exists_and_loads(self) -> None:
        self.assertTrue(_SCHEMA_PATH.is_file(), f"missing JSON schema: {_SCHEMA_PATH}")
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema.get("type"), "object")
        self.assertFalse(schema.get("additionalProperties", True))

    @covers("REQ-0.0.28-02-08")
    def test_schema_enforces_trigger_semantic_enum(self) -> None:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        bands_schema = schema["properties"]["bands"]["items"]
        trigger_schema = bands_schema["properties"]["trigger_semantic"]
        self.assertEqual(set(trigger_schema["enum"]), set(TRIGGER_VOCABULARY))

    @covers("REQ-0.0.28-02-08")
    def test_schema_enforces_canonical_percentile_enum(self) -> None:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        bands_schema = schema["properties"]["bands"]["items"]
        percentile_schema = bands_schema["properties"]["corpus_percentile"]
        self.assertEqual(set(percentile_schema["enum"]), set(CANONICAL_PERCENTILES))


if __name__ == "__main__":
    unittest.main()
