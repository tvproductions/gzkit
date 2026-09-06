"""gzkit's two canonical ledger readers must reach the same verdict (GHI #883).

`validate_ledger` (schema-driven, `src/gzkit/validate_pkg/ledger_check.py`) and
`parse_typed_event` (Pydantic models, `src/gzkit/events.py`) both decide whether a
ledger row is valid, from independently-authored declarations. A row that passes
its canonical validator and then fails typed replay is a defect discovered far
from the write that caused it.

Measured 2026-08-28, before this module existed — three holes, none of which
either reader can detect alone:

* **Union-typed fields were unchecked entirely.** `_validate_ledger_field` compared
  `rule["type"] == "string"`, and a declaration of `{"type": ["string", "null"]}`
  is a *list*, so every branch fell through and the field accepted any value at
  all. 14 fields across 12 event types. This is also why the null disagreement
  looked narrower than it was: the fields where null was already legal were the
  fields where nothing was being checked.
* **Array `items` were never descended.** The validator confirmed the outer value
  was a list and stopped, so `floor_moved_ids: [7]` passed the schema and failed
  typed replay. 9 fields across 5 event types.
* **Nullability drifted between the declarations.** 26 fields across 17 event
  types declared a concrete schema type while their model field admitted `None`,
  so an explicit `null` was rejected by one reader and accepted by the other.

The durable fix is the coherence assertion, not the three repairs: these tests
fail whenever the two declarations drift again, which is the property neither
reader has on its own.

**Which reader changed, and why.** The schema was widened to match the models
rather than the models tightened to match the schema. Explicit `null` is already
an established idiom in this ledger — 692 committed rows carry one on a field
where it is legal — so tightening would have made the ledger self-inconsistent
(null legal on 14 fields, illegal on 26 semantically identical optional ones) and
would have risked the replay of any row a writer had already emitted. Widening
cannot break a committed row by construction, and all three repairs were measured
at **zero** newly-failing live rows before landing.
"""

from __future__ import annotations

import json
import tempfile
import typing
import unittest
from pathlib import Path
from typing import Any

from gzkit.events import TypedLedgerEvent, parse_typed_event
from gzkit.validate_pkg.ledger_check import validate_ledger

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_SCHEMA = REPO_ROOT / "src" / "gzkit" / "schemas" / "ledger.json"

#: Schema events with no typed model. EMPTY since GHI #877 was repaired: both
#: former entries (`session_exit_bookmark_skipped`, `surface_weight_recalibrated`)
#: had model classes all along and were simply never added to the
#: `TypedLedgerEvent` union, so the typed reader could not replay 99 committed
#: rows. Kept as an empty waiver rather than deleted: it is the shrink-only
#: ratchet that makes a NEW model-less event fail immediately instead of joining
#: an invisible backlog, and `test_the_unmodelled_waiver_names_only_genuinely_
#: unmodelled_events` fails closed if an entry ever outlives its subject again.
_UNMODELLED_EVENTS: frozenset[str] = frozenset()


def _schema_events() -> dict[str, Any]:
    return json.loads(LEDGER_SCHEMA.read_text(encoding="utf-8"))["events"]


def _typed_models() -> dict[str, Any]:
    """Map each event name to its model, reading the name off the `Literal` annotation.

    The discriminator value lives in the annotation, not in a field default —
    a probe reading `.default` resolves zero models and reports zero drift,
    which is indistinguishable from a clean result.
    """
    union = typing.get_args(typing.get_args(TypedLedgerEvent)[0])
    models: dict[str, Any] = {}
    for model in union:
        names = typing.get_args(model.model_fields["event"].annotation)
        if names and isinstance(names[0], str):
            models[names[0]] = model
    return models


#: JSON-schema type name for each element type a `list[...]` model field uses.
#: Only the shapes this ledger actually declares — a new one fails the mapping
#: rather than silently resolving to "unchecked", which is the state the
#: assertions below exist to refuse.
_ELEMENT_JSON_TYPE: dict[Any, str] = {str: "string", int: "integer", bool: "boolean"}


def _declares_array(rule: dict[str, Any]) -> bool:
    """Report whether a field rule permits an array, in either declaration form."""
    declared = rule.get("type")
    return declared == "array" or (isinstance(declared, list) and "array" in declared)


def _model_item_type(annotation: Any) -> str | None:
    """Return the JSON type name of a `list[...]` annotation's element, if any.

    Unwraps one level of `X | None`, then reads the list's parameter. Returns
    `None` for an unparameterized or non-list annotation, so a field this cannot
    resolve is skipped rather than reported — an assertion is worth only what its
    probe can see, and a false finding here would be as bad as a missed one.
    """
    for candidate in (annotation, *typing.get_args(annotation)):
        if typing.get_origin(candidate) is not list:
            continue
        args = typing.get_args(candidate)
        if not args:
            return None
        element = args[0]
        if typing.get_origin(element) is dict:
            return "object"
        return _ELEMENT_JSON_TYPE.get(element)
    return None


def _ledger_verdict(row: dict[str, Any]) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        path.write_text(json.dumps(row) + "\n", encoding="utf-8")
        return "accepts" if not validate_ledger(path) else "rejects"


def _typed_verdict(row: dict[str, Any]) -> str:
    try:
        parse_typed_event(row)
    except Exception:  # noqa: BLE001 — any parse failure is one verdict: reject
        return "rejects"
    return "accepts"


class LedgerDeclarationCoherence(unittest.TestCase):
    """The two readers' DECLARATIONS must agree, which is where drift starts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = _schema_events()
        cls.models = _typed_models()

    def test_the_model_probe_resolves_the_union(self) -> None:
        """Guards the assertions below against a probe that silently finds nothing.

        Every drift count here is `0` when model resolution fails, which reads
        exactly like a clean tree.
        """
        self.assertGreater(len(self.models), 60, "typed-model resolution collapsed")

    def test_every_schema_event_has_a_typed_model(self) -> None:
        unmodelled = sorted(set(self.schema) - set(self.models) - _UNMODELLED_EVENTS)
        self.assertEqual(
            unmodelled,
            [],
            "schema declares events the typed reader cannot replay at all; add a "
            "model, or record it against GHI #877 in _UNMODELLED_EVENTS with reason.",
        )

    def test_the_unmodelled_waiver_names_only_genuinely_unmodelled_events(self) -> None:
        """A waiver that outlives its subject silently exempts a live model."""
        stale = sorted(name for name in _UNMODELLED_EVENTS if name in self.models)
        self.assertEqual(stale, [], "these events now HAVE typed models; drop them from the waiver")

    def test_every_array_property_declares_its_item_type(self) -> None:
        """An array field with no ``items`` is checked for nothing past `isinstance(list)`.

        GHI #883 descended into ``items`` and fixed "9 fields across 5 event
        types" — every array field that DECLARED items. The residual was the
        fields that declare none: the validator confirms the outer value is a
        list and stops, so ``[7]`` passes the schema and fails typed replay, the
        same defect one layer out. Nine properties were in that state when this
        assertion was written (``unaccounted``, ``drift``, ``routing``,
        ``foundation_summary``, ``ghi_summary``, ``red_team_challenges_fired``,
        ``inspection_scope``, ``test_names``, ``set_aside``) — the review named
        four of them, and the other five were the same defect nobody had counted.

        Asserted as a DECLARATION property rather than per-field verdict parity,
        because a verdict test proves one field and this proves the class.
        """
        undeclared = []
        for event, spec in sorted(self.schema.items()):
            model = self.models.get(event)
            if model is None:
                continue
            for field, rule in sorted((spec.get("properties") or {}).items()):
                if not isinstance(rule, dict) or not _declares_array(rule):
                    continue
                info = model.model_fields.get(field)
                if info is None or not _model_item_type(info.annotation):
                    continue
                if not isinstance(rule.get("items"), dict):
                    undeclared.append(f"{event}.{field}")
        self.assertEqual(
            undeclared,
            [],
            "these array properties declare no `items`, so the schema accepts item "
            "types typed replay refuses; declare `items` matching the model's element "
            "type (GHI #883 class, second pass)",
        )

    def test_declared_item_types_match_the_models_element_type(self) -> None:
        """Declaring `items` is only worth having while it agrees with the model.

        A `{"type": "string"}` items rule under a `list[dict]` field would refuse
        every valid row instead of admitting an invalid one — the same drift,
        pointed the other way.
        """
        mismatched = []
        for event, spec in sorted(self.schema.items()):
            model = self.models.get(event)
            if model is None:
                continue
            for field, rule in sorted((spec.get("properties") or {}).items()):
                if not isinstance(rule, dict) or not _declares_array(rule):
                    continue
                info = model.model_fields.get(field)
                items = rule.get("items")
                if info is None or not isinstance(items, dict):
                    continue
                expected = _model_item_type(info.annotation)
                if expected and items.get("type") != expected:
                    mismatched.append(
                        f"{event}.{field}: schema={items.get('type')!r} model={expected!r}"
                    )
        self.assertEqual(mismatched, [], "schema `items` disagrees with the model element type")

    def test_schema_and_model_agree_on_nullability(self) -> None:
        """An optional field must be nullable on both sides or on neither.

        This is the class GHI #883 named, generalized off its one observed field:
        26 fields across 17 event types disagreed, of which `floor_direction` was
        one.
        """
        drift = []
        for event, spec in sorted(self.schema.items()):
            model = self.models.get(event)
            if model is None:
                continue
            for field, rule in sorted((spec.get("properties") or {}).items()):
                if not isinstance(rule, dict):
                    continue
                declared = rule.get("type")
                schema_nullable = isinstance(declared, list) and "null" in declared
                info = model.model_fields.get(field)
                if info is None:
                    continue
                model_nullable = type(None) in typing.get_args(info.annotation)
                if model_nullable != schema_nullable:
                    drift.append(
                        f"{event}.{field}: schema={declared!r} model_null={model_nullable}"
                    )
        self.assertEqual(drift, [], "schema and typed model disagree on nullability")


class LedgerReaderVerdictParity(unittest.TestCase):
    """Both readers reach the SAME verdict across the matrix GHI #883 measured."""

    BASE = {
        "schema": "gzkit.ledger.v1",
        "event": "corpus_entry_retired",
        "id": "parity-probe",
        "ts": "2026-08-28T00:00:00+00:00",
        "surface": "AGENTS.md",
        "retired_entry_id": "entry-a",
        "retraction_entry_id": "entry-b",
        "reason": "parity probe",
        # Required by the floor-moving conditional rule (GHI #882). Without it a
        # valid enum value is refused for an unrelated reason and the parity
        # result is meaningless.
        "attestor": "g0",
    }

    def _row(self, **overrides: Any) -> dict[str, Any]:
        return {**self.BASE, **overrides}

    def _assert_agree(self, row: dict[str, Any], expected: str) -> None:
        ledger, typed = _ledger_verdict(row), _typed_verdict(row)
        self.assertEqual(
            (ledger, typed),
            (expected, expected),
            f"readers disagree: validate_ledger={ledger} parse_typed_event={typed}",
        )

    def test_absent_optional_field(self) -> None:
        self._assert_agree(self._row(), "accepts")

    def test_valid_enum_value(self) -> None:
        self._assert_agree(self._row(floor_direction="shrank"), "accepts")

    def test_invalid_enum_value_is_refused_by_both(self) -> None:
        """The widening must not cost the enum check it was guarding."""
        self._assert_agree(self._row(floor_direction="BOGUS"), "rejects")

    def test_explicit_null_on_an_optional_field(self) -> None:
        """Null was rejected by the schema and accepted by the model (GHI #883)."""
        self._assert_agree(self._row(floor_direction=None), "accepts")

    def test_array_of_valid_items(self) -> None:
        self._assert_agree(self._row(floor_moved_ids=["entry-a"]), "accepts")

    def test_array_carrying_a_wrongly_typed_item(self) -> None:
        """The schema accepted `[7]` and typed replay refused it (GHI #883)."""
        self._assert_agree(self._row(floor_moved_ids=[7]), "rejects")

    def test_array_carrying_a_null_item(self) -> None:
        """Item nullability is not inherited from the field's own nullability."""
        self._assert_agree(self._row(floor_moved_ids=[None]), "rejects")

    def test_non_list_where_an_array_is_declared(self) -> None:
        self._assert_agree(self._row(floor_moved_ids="not-a-list"), "rejects")


class RepairedArrayFieldsAgreeAcrossTheMatrix(unittest.TestCase):
    """Every field the `items` repair touched, across the full verdict matrix.

    `LedgerReaderVerdictParity` above runs the matrix on `floor_moved_ids`, the
    one field GHI #883 observed. That proved the mechanism and not the fields:
    nine array properties declared no `items` at all, so each accepted `[7]` on
    the schema side and failed typed replay. This class runs the same five
    questions — valid items, a wrongly-typed item, an absent field, an explicit
    null, and a null item — against the four the review named plus the
    `list[dict]` shape, whose element type is different and could not be assumed
    to behave like the `list[str]` ones.
    """

    #: (event, field, base row without the field, a valid element)
    CASES: typing.ClassVar[tuple[tuple[str, str, dict[str, Any], Any], ...]] = (
        (
            "airlock_in",
            "unaccounted",
            {"event": "airlock_in", "id": "OBPI-X", "decision": "GO"},
            "src/gzkit/seam.py",
        ),
        (
            "airlock_out",
            "drift",
            {"event": "airlock_out", "id": "OBPI-X", "verdict": "clean"},
            "src/gzkit/drifted.py",
        ),
        (
            "airlock_out",
            "routing",
            {"event": "airlock_out", "id": "OBPI-X", "verdict": "clean"},
            "GHI #611",
        ),
        (
            "patch-release",
            "foundation_summary",
            {
                "event": "patch-release",
                "id": "v0.1.0",
                "version": "0.1.0",
                "previous_version": "0.0.9",
                "ghi_summary": [],
                "manifest_path": "data/manifest.json",
            },
            {"adr": "ADR-0.0.1"},
        ),
    )

    BASE: typing.ClassVar[dict[str, Any]] = {
        "schema": "gzkit.ledger.v1",
        "ts": "2026-09-06T00:00:00+00:00",
    }

    def _assert_agree(self, row: dict[str, Any], expected: str, label: str) -> None:
        ledger, typed = _ledger_verdict(row), _typed_verdict(row)
        self.assertEqual(
            (ledger, typed),
            (expected, expected),
            f"{label}: validate_ledger={ledger} parse_typed_event={typed}",
        )

    def test_the_matrix_agrees_on_every_repaired_array_field(self) -> None:
        for event, field, base, element in self.CASES:
            row = {**self.BASE, **base}
            with self.subTest(field=f"{event}.{field}"):
                self._assert_agree(row, "accepts", f"{event}.{field} absent")
                self._assert_agree({**row, field: [element]}, "accepts", f"{event}.{field} valid")
                self._assert_agree({**row, field: []}, "accepts", f"{event}.{field} empty")
                self._assert_agree({**row, field: None}, "accepts", f"{event}.{field} null field")
                self._assert_agree({**row, field: [None]}, "rejects", f"{event}.{field} null item")
                self._assert_agree(
                    {**row, field: ["wrong" if not isinstance(element, str) else 7]},
                    "rejects",
                    f"{event}.{field} wrongly-typed item",
                )
                self._assert_agree(
                    {**row, field: "not-a-list"}, "rejects", f"{event}.{field} non-list"
                )

    def test_the_override_fields_agree_across_both_readers(self) -> None:
        """The three fields the airlock override path writes (GHI #877, second pass)."""
        row = {
            **self.BASE,
            "event": "airlock_in",
            "id": "OBPI-X",
            "decision": "GO",
            "override_seam": "src/gzkit/unaccounted.py",
            "override_attestor": "g0",
            "override_revoked": False,
        }
        self._assert_agree(row, "accepts", "override payload")
        self._assert_agree({**row, "override_revoked": "yes"}, "rejects", "override_revoked str")
        self._assert_agree({**row, "override_seam": 7}, "rejects", "override_seam int")


class LedgerValidatorEnforcesDeclaredTypes(unittest.TestCase):
    """Widening the type form must not become a hole of its own.

    A union declaration previously disabled EVERY branch of the type check. The
    repair reads `type` as a set of permitted types, so it must still refuse a
    value matching none of them.
    """

    BASE = {
        "schema": "gzkit.ledger.v1",
        "event": "brief_reconciled",
        "id": "union-probe",
        "ts": "2026-08-28T00:00:00+00:00",
    }

    #: A schema type -> a value of that type, so the fixture row fails only for
    #: the reason under test. Filling every required field with a string made the
    #: refusal assertion below pass for the WRONG reason (`has_drift` is boolean),
    #: which is a green that proves nothing about union handling.
    _SAMPLE: typing.ClassVar[dict[str, Any]] = {
        "string": "x",
        "integer": 0,
        "boolean": False,
        "object": {},
        "array": [],
    }

    @classmethod
    def setUpClass(cls) -> None:
        spec = _schema_events()["brief_reconciled"]
        props = spec.get("properties", {})
        cls.required = {
            field: cls._SAMPLE[props[field]["type"]] for field in spec.get("required", [])
        }
        cls.attestor_rule = props["attestor"]

    def test_the_probe_field_really_is_union_declared(self) -> None:
        """Otherwise the two assertions below prove nothing about union handling."""
        self.assertEqual(self.attestor_rule.get("type"), ["string", "null"])

    def test_a_permitted_member_of_the_union_is_accepted(self) -> None:
        row = {**self.BASE, **self.required, "attestor": None}
        self.assertEqual(_ledger_verdict(row), "accepts")

    def test_a_value_matching_no_member_of_the_union_is_refused(self) -> None:
        """`{"type": ["string", "null"]}` accepted an integer before the repair."""
        row = {**self.BASE, **self.required, "attestor": 7}
        self.assertEqual(_ledger_verdict(row), "rejects")


if __name__ == "__main__":
    unittest.main()
