"""REQ-derived tests for the adversarial_validation ledger event (GHI #676).

Assertions derive from the requirement — Step 4b's verdict must have a durable,
schema-validated home in the ledger — not from a run of the implementation.
"""

from __future__ import annotations

import typing
import unittest

import pydantic

from gzkit.events import AdversarialValidationEvent, parse_typed_event
from gzkit.schemas import load_schema

_VERDICTS = ("refuted", "not-refuted", "refuted-with-caveats", "degraded-human-only")


def _event(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "event": "adversarial_validation",
        "id": "ADV-1",
        "ts": "2026-07-09T00:00:00+00:00",
        "obpi_id": "OBPI-0.33.0-01-airlock-data-model-and-events",
        "verdict": "refuted",
        "adversary": "codex/gpt-5.4",
    }
    payload.update(overrides)
    return payload


class TestAdversarialValidationEvent(unittest.TestCase):
    def test_discriminator_resolves_to_model(self) -> None:
        parsed = parse_typed_event(_event())
        self.assertIsInstance(parsed, AdversarialValidationEvent)

    def test_verdict_vocabulary_is_closed_to_exactly_four_members(self) -> None:
        # The closed-vocabulary claim, asserted directly. Rejecting ONE bad value
        # proves the set lacks that value, never that it lacks every other — a
        # fifth verdict (e.g. "passed") could otherwise be added unnoticed.
        annotation = AdversarialValidationEvent.model_fields["verdict"].annotation
        self.assertEqual(typing.get_args(annotation), _VERDICTS)

    def test_each_declared_verdict_parses(self) -> None:
        for verdict in _VERDICTS:
            with self.subTest(verdict=verdict):
                parsed = parse_typed_event(_event(verdict=verdict))
                self.assertEqual(parsed.verdict, verdict)

    def test_out_of_vocabulary_verdict_is_refused(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            parse_typed_event(_event(verdict="passed"))

    def test_identity_fields_are_required(self) -> None:
        # obpi_id / verdict / adversary carry the whole evidentiary weight: which
        # claim was attacked, what was found, and by whom. None may be omitted.
        for missing in ("obpi_id", "verdict", "adversary"):
            with self.subTest(missing=missing):
                payload = _event()
                del payload[missing]
                with self.assertRaises(pydantic.ValidationError):
                    parse_typed_event(payload)

    def test_refutation_detail_round_trips(self) -> None:
        parsed = parse_typed_event(
            _event(
                job_id="task-mrcrhhaq-dambrd",
                refuted_claim="closed enum vocabularies are not fail-closed",
                resolution="membership assertions added; adversary's mutation now FAILS",
            )
        )
        dumped = parsed.model_dump()
        self.assertEqual(dumped["job_id"], "task-mrcrhhaq-dambrd")
        self.assertEqual(dumped["refuted_claim"], "closed enum vocabularies are not fail-closed")
        self.assertIn("adversary's mutation now FAILS", dumped["resolution"])
        self.assertIsInstance(parse_typed_event(dumped), AdversarialValidationEvent)

    def test_optional_fields_are_omitted_when_unset(self) -> None:
        dumped = parse_typed_event(_event()).model_dump()
        for absent in ("job_id", "refuted_claim", "resolution"):
            self.assertNotIn(absent, dumped)

    def test_ledger_schema_registers_the_event(self) -> None:
        # The events map is a closed registry: an absent name is rejected at emit
        # with "Unknown event type". Registration is what makes the event durable.
        rule = load_schema("ledger")["events"]["adversarial_validation"]
        self.assertEqual(sorted(rule["required"]), ["adversary", "obpi_id", "verdict"])


if __name__ == "__main__":
    unittest.main()
