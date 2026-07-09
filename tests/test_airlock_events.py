"""Advisory round-trip coverage for the airlock L2 ledger event types.

This file is NOT a REQ proof: REQ-0.33.0-01-06 is tagged [SUPPORT], whose proof
channel is a ledger event + `gz validate --documents`, never `@covers`. These
tests are advisory behavioral coverage of discriminator resolution and
serialize -> parse round-tripping for `airlock_in` / `airlock_out`.

@covers is intentionally absent (see .gzkit/rules/tests.md § REQ Scope Discipline).
"""

import unittest

from gzkit.events import AirlockInEvent, AirlockOutEvent, parse_typed_event


class TestAirlockEventParsing(unittest.TestCase):
    """parse_typed_event resolves airlock discriminators to the right model."""

    def test_airlock_in_resolves_to_model(self) -> None:
        event = parse_typed_event(
            {"event": "airlock_in", "id": "AIR-1", "ts": "2026-07-08T00:00:00Z"}
        )
        self.assertIsInstance(event, AirlockInEvent)
        self.assertEqual(event.event, "airlock_in")

    def test_airlock_out_resolves_to_model(self) -> None:
        event = parse_typed_event(
            {"event": "airlock_out", "id": "AIR-2", "ts": "2026-07-08T00:00:00Z"}
        )
        self.assertIsInstance(event, AirlockOutEvent)
        self.assertEqual(event.event, "airlock_out")

    def test_airlock_in_round_trip_preserves_event_name(self) -> None:
        original = parse_typed_event(
            {"event": "airlock_in", "id": "AIR-3", "ts": "2026-07-08T00:00:00Z"}
        )
        reparsed = parse_typed_event(original.model_dump(by_alias=True))
        self.assertEqual(reparsed.event, "airlock_in")

    def test_airlock_out_round_trip_preserves_event_name(self) -> None:
        original = parse_typed_event(
            {"event": "airlock_out", "id": "AIR-4", "ts": "2026-07-08T00:00:00Z"}
        )
        reparsed = parse_typed_event(original.model_dump(by_alias=True))
        self.assertEqual(reparsed.event, "airlock_out")


if __name__ == "__main__":
    unittest.main()
