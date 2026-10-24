"""The forward rule, its delivery-event registry and cutover: RO-3 tranche 4.

`docs/governance/harbor-ro3-requirements-store.md` § Tranches row 4: an undeclared
delivery event after the cutover is announced; legacy events are not read. Ruling
4 keeps it advisory until RO-5. Rulings of 2026-10-22: the nine measured types,
naming by the identity seam's grammars over the event's values, and the cutover
as a timestamp in `data/catalog/delivery_events.json`.
"""

import io
import json
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from gzkit.governance.trust_audits.catalog import audit_catalog
from gzkit.governance.trust_audits.catalog_forward import (
    forward_rule_reading,
    names_req_or_outcome,
)
from gzkit.models.catalog import (
    DELIVERY_EVENTS_FILE,
    DeliveryEventsFile,
    delivery_events_json_schema,
    load_delivery_events,
)
from gzkit.schemas import load_schema

_REPO = Path(__file__).resolve().parents[2]
_CUTOVER = "2026-10-22T12:00:00+00:00"
_BEFORE = "2026-10-22T11:59:59+00:00"
_AFTER = "2026-10-22T12:00:01+00:00"

_MEASURED_NINE = {
    "task_started",
    "task_completed",
    "obpi_receipt_emitted",
    "gate_checked",
    "attested",
    "acceptance_recorded",
    "red_receipt_emitted",
    "stage2_dispatch_recorded",
    "closeout_initiated",
}


def _registry(*types: str) -> DeliveryEventsFile:
    return DeliveryEventsFile.model_validate(
        {"_doc": "Fixture.", "cutover": _CUTOVER, "event_types": list(types or ["task_started"])}
    )


def _row(event: str, ts: str, **fields: object) -> dict[str, object]:
    return {"schema": "gzkit.ledger.v1", "event": event, "id": "TASK-0.1.0-01-01-01", "ts": ts} | (
        fields
    )


class TestNaming(unittest.TestCase):
    """An event names a REQ by either grammar anywhere in its values, or an outcome it holds."""

    def test_a_legacy_req_in_a_nested_payload_names_one(self):
        row = _row(
            "acceptance_recorded", _AFTER, payload={"obligations": [{"id": "REQ-0.1.0-01-02"}]}
        )
        self.assertTrue(names_req_or_outcome(row, frozenset()))

    def test_a_catalog_req_in_any_field_names_one(self):
        self.assertTrue(
            names_req_or_outcome(_row("gate_checked", _AFTER, evidence="REQ-7"), frozenset())
        )

    def test_an_outcome_field_names_one_only_when_the_catalog_holds_the_code(self):
        self.assertTrue(
            names_req_or_outcome(_row("attested", _AFTER, outcome="H1"), frozenset({"H1"}))
        )
        self.assertFalse(
            names_req_or_outcome(_row("attested", _AFTER, outcome="H9"), frozenset({"H1"}))
        )

    def test_a_task_id_never_names_its_req_by_spelling(self):
        self.assertFalse(names_req_or_outcome(_row("task_started", _AFTER), frozenset()))

    def test_a_req_lookalike_inside_a_longer_token_is_not_a_name(self):
        row = _row("gate_checked", _AFTER, evidence="see PREREQ-12x and REQ-0 and REQ-12a")
        self.assertFalse(names_req_or_outcome(row, frozenset()))


class TestReading(unittest.TestCase):
    """Only listed types after the cutover are read; legacy events never are."""

    def test_an_unnamed_listed_event_after_the_cutover_is_counted(self):
        reading = forward_rule_reading([_row("task_started", _AFTER)], _registry(), frozenset())
        self.assertEqual((reading.read, reading.unnamed), (1, {"task_started": 1}))

    def test_a_legacy_event_is_not_read(self):
        rows = [_row("task_started", _BEFORE), _row("task_started", _CUTOVER)]
        reading = forward_rule_reading(rows, _registry(), frozenset())
        self.assertEqual((reading.read, reading.unnamed), (0, {}))

    def test_an_unlisted_type_and_a_named_event_are_not_counted(self):
        rows = [
            _row("insight_recorded", _AFTER),
            _row("task_started", _AFTER, req_id="REQ-3"),
        ]
        reading = forward_rule_reading(rows, _registry(), frozenset())
        self.assertEqual((reading.read, reading.unnamed), (1, {}))

    def test_an_event_without_a_readable_timestamp_is_not_read(self):
        rows = [_row("task_started", ""), _row("task_started", "not a time")]
        self.assertEqual(forward_rule_reading(rows, _registry(), frozenset()).read, 0)


class TestRegistry(unittest.TestCase):
    """`data/catalog/delivery_events.json` is a declared registry with its committed schema."""

    def test_the_committed_schema_equals_the_model(self):
        self.assertEqual(load_schema("catalog_delivery_events"), delivery_events_json_schema())

    def test_the_cutover_must_carry_a_timezone_and_the_list_is_not_empty(self):
        for cutover, types in (("2026-10-22T12:00:00", ["task_started"]), (_CUTOVER, [])):
            with self.subTest(cutover=cutover, types=types), self.assertRaises(ValueError):
                DeliveryEventsFile.model_validate(
                    {"_doc": "d", "cutover": cutover, "event_types": types}
                )

    def test_the_live_registry_lists_the_nine_ruled_types(self):
        registry = load_delivery_events(_REPO)
        self.assertEqual(set(registry.event_types), _MEASURED_NINE)

    def test_the_registry_is_a_declared_config_registry(self):
        declared = json.loads((_REPO / "data" / "config_registry.json").read_text("utf-8"))
        self.assertIn(DELIVERY_EVENTS_FILE, declared["registries"])


class TestAuditAnnounces(unittest.TestCase):
    """The audit announces the unnamed events as one advisory line and never fails on them."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        catalog = self.root / "data" / "catalog"
        catalog.mkdir(parents=True)
        for kind in ("families", "outcomes", "reqs", "externals"):
            (catalog / f"{kind}.json").write_text(
                json.dumps({"_doc": "Fixture.", kind: []}), encoding="utf-8"
            )
        registry = {"_doc": "Fixture.", "cutover": _CUTOVER, "event_types": ["task_started"]}
        (catalog / "delivery_events.json").write_text(json.dumps(registry), encoding="utf-8")
        ledger = self.root / ".gzkit" / "ledger.jsonl"
        ledger.parent.mkdir()
        rows = [
            _row("task_started", _BEFORE),
            _row("task_started", _AFTER),
            _row("task_started", _AFTER, req_id="REQ-0.1.0-01-01"),
        ]
        ledger.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    def test_one_unnamed_event_of_two_read_is_announced(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            errors = audit_catalog(self.root)
        self.assertEqual(errors, [])
        self.assertIn(
            f"catalog-forward-rule: 1 of 2 delivery events since {_CUTOVER} name no REQ or "
            "outcome (task_started 1)",
            stderr.getvalue(),
        )

    def test_a_project_without_the_registry_reads_no_delivery_events(self):
        (self.root / "data" / "catalog" / "delivery_events.json").unlink()
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            errors = audit_catalog(self.root)
        self.assertEqual(errors, [])
        self.assertNotIn("catalog-forward-rule", stderr.getvalue())

    def test_nothing_is_announced_when_every_event_is_named(self):
        ledger = self.root / ".gzkit" / "ledger.jsonl"
        row = _row("task_started", _AFTER, req_id="REQ-0.1.0-01-01")
        ledger.write_text(json.dumps(row) + "\n", encoding="utf-8")
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            audit_catalog(self.root)
        self.assertNotIn("catalog-forward-rule", stderr.getvalue())


class TestNegativeControl(unittest.TestCase):
    def test_the_control_catches_its_fixture(self):
        from gzkit.enforcement import (
            EXEMPTS_NONE,
            _run_single_claim,
            production_enforcement_registry,
        )

        records = {r.claim_id: r for r in production_enforcement_registry()}
        record = records["requirements-catalog-forward-rule"]
        result = _run_single_claim(record)
        self.assertEqual(result.outcome, "PASS", result.message)
        self.assertEqual(record.exempts, EXEMPTS_NONE)
        self.assertIsNotNone(record.population)

    def test_reading_the_legacy_event_changes_the_count(self):
        """Moving the cutover before the legacy event changes the count the control expects."""
        from gzkit.governance.trust_audits import _qc_nc_entrypoints as ep
        from gzkit.governance.trust_audits import _qc_negative_controls as nc

        tmp = Path(self.enterContext(TemporaryDirectory()))
        with patch.object(nc, "_mkroot", lambda slug: tmp / slug):
            root = nc._build_catalog_forward_rule()
        registry = root / "data" / "catalog" / "delivery_events.json"
        payload = json.loads(registry.read_text(encoding="utf-8"))
        payload["cutover"] = "2000-01-01T00:00:00+00:00"
        registry.write_text(json.dumps(payload), encoding="utf-8")
        lines = ep._ep_catalog_forward_rule(root)
        self.assertEqual(len(lines), 1)
        self.assertIn("2 of 3 delivery events", lines[0])


if __name__ == "__main__":
    unittest.main()
