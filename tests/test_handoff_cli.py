"""Tests for the ``gz handoff`` CLI adapter (OBPI-0.0.65-03).

Assertions derive from the brief's Acceptance Criteria (REQ-0.0.65-03-01 through
REQ-0.0.65-03-03), not from a run of the implementation. Each command is driven
against a real temp ``.gzkit/handoffs/`` corpus seeded through the shipped
``gzkit.handoff_api`` (OBPI-02), so the adapter exercises real domain code.

The ``--json`` payloads are asserted as parsed structured data (list length,
domain-object fields), never as rendered substrings — the discriminator per
``.gzkit/rules/tests.md`` § The discriminator.
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from gzkit.commands.handoff import (
    handoff_create_cmd,
    handoff_list_cmd,
    handoff_resume_cmd,
)
from gzkit.handoff_api import create_handoff, validate_handoff_document
from gzkit.traceability import covers

_NEXT_STEPS = "## Immediate Next Steps\n\n1. Land the adapter and its unit tests.\n"


class _HandoffCliCase(unittest.TestCase):
    def setUp(self) -> None:
        self.base = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def _seed(
        self,
        *,
        adr_id: str,
        slug: str,
        timestamp: str,
        obpi_id: str | None = None,
        next_steps: str = "",
    ) -> Path:
        """Author a valid handoff on disk through the real API (OBPI-02)."""
        sections = {"Decisions Made": "Chose the thin-adapter shape."}
        if next_steps:
            sections["Immediate Next Steps"] = next_steps
        return create_handoff(
            adr_id=adr_id,
            branch="main",
            agent="g0",
            slug=slug,
            sections=sections,
            obpi_id=obpi_id,
            base_path=self.base,
            timestamp=timestamp,
        )

    @staticmethod
    def _capture_json(fn) -> object:
        buf = io.StringIO()
        with redirect_stdout(buf):
            fn()
        return json.loads(buf.getvalue())


class TestHandoffList(_HandoffCliCase):
    @covers("REQ-0.0.65-03-01")
    def test_list_json_returns_seeded_handoffs_newest_first(self) -> None:
        self._seed(adr_id="ADR-0.0.65", slug="older", timestamp="2026-07-10T09:00:00Z")
        self._seed(adr_id="ADR-0.0.65", slug="newer", timestamp="2026-07-14T09:00:00Z")

        payload = self._capture_json(lambda: handoff_list_cmd(as_json=True, base_path=self.base))

        self.assertIsInstance(payload, list)
        self.assertEqual(len(payload), 2, "both seeded handoffs must surface in the listing")
        self.assertEqual(
            [row["timestamp"] for row in payload],
            ["2026-07-14T09:00:00Z", "2026-07-10T09:00:00Z"],
            "the listing must be newest-first (a read-only projection of list_handoffs)",
        )
        self.assertTrue(
            all(row["adr_id"] == "ADR-0.0.65" for row in payload),
            "each row carries the frontmatter-derived adr_id",
        )

    @covers("REQ-0.0.65-03-01")
    def test_list_json_scopes_to_the_requested_adr(self) -> None:
        self._seed(adr_id="ADR-0.0.65", slug="in-scope", timestamp="2026-07-14T09:00:00Z")
        self._seed(adr_id="ADR-0.0.66", slug="out-of-scope", timestamp="2026-07-14T10:00:00Z")

        payload = self._capture_json(
            lambda: handoff_list_cmd(adr="ADR-0.0.65", as_json=True, base_path=self.base)
        )

        self.assertEqual(len(payload), 1, "--adr filters the listing to the named ADR")
        self.assertEqual(payload[0]["adr_id"], "ADR-0.0.65")


class TestHandoffResume(_HandoffCliCase):
    @covers("REQ-0.0.65-03-02")
    def test_resume_json_reports_newest_handoff_and_next_step(self) -> None:
        self._seed(adr_id="ADR-0.0.65", slug="stale", timestamp="2026-07-01T09:00:00Z")
        newest = self._seed(
            adr_id="ADR-0.0.65",
            slug="current",
            timestamp="2026-07-14T09:00:00Z",
            next_steps="1. Land the adapter and its unit tests.",
        )

        # Inject `now` so staleness is a DETERMINISTIC function of the seeded
        # age, not the wall clock — the newest handoff is 2h old => Fresh
        # (< 24h). Asserting the exact value (not set-membership) makes the
        # test bite a wrong-but-legal staleness, which a membership check
        # would silently accept.
        payload = self._capture_json(
            lambda: handoff_resume_cmd(
                adr="ADR-0.0.65",
                as_json=True,
                now="2026-07-14T11:00:00Z",
                base_path=self.base,
            )
        )

        self.assertEqual(
            payload["path"],
            newest.as_posix(),
            "resume selects the NEWEST handoff for the ADR, not the oldest",
        )
        self.assertEqual(
            payload["first_next_step"],
            "Land the adapter and its unit tests.",
            "resume surfaces the extracted first Immediate Next Step",
        )
        self.assertEqual(
            payload["staleness"],
            "Fresh",
            "a 2h-old handoff classifies exactly as Fresh (< 24h), not merely a legal value",
        )

    @covers("REQ-0.0.65-03-02")
    def test_resume_json_classifies_ancient_handoff_as_very_stale(self) -> None:
        # A second controlled age at the opposite end of the enum: > 7 days old
        # => Very-Stale. Two exact-value cases together mean no single hard-coded
        # constant can satisfy both — the classification logic must actually run.
        self._seed(
            adr_id="ADR-0.0.65",
            slug="ancient",
            timestamp="2026-06-01T09:00:00Z",
            next_steps="1. Reconstruct the lost context.",
        )

        payload = self._capture_json(
            lambda: handoff_resume_cmd(
                adr="ADR-0.0.65",
                as_json=True,
                now="2026-07-14T09:00:00Z",
                base_path=self.base,
            )
        )

        self.assertEqual(
            payload["staleness"],
            "Very-Stale",
            "a ~6-week-old handoff classifies exactly as Very-Stale (> 7 days)",
        )
        self.assertTrue(
            payload["requires_human_verification"],
            "a Very-Stale handoff flags requires_human_verification",
        )


class TestHandoffCreate(_HandoffCliCase):
    def _handoff_files(self) -> list[Path]:
        return list((self.base / ".gzkit" / "handoffs").glob("*.md"))

    @covers("REQ-0.0.65-03-03")
    def test_create_invalid_input_fails_closed_writes_no_file(self) -> None:
        # A malformed ADR id fails the frontmatter gate; the API must refuse to
        # write and the adapter must translate that refusal into a non-zero exit.
        with self.assertRaises(SystemExit) as ctx:
            handoff_create_cmd(
                adr="ADR-BOGUS",
                slug="rejected",
                agent="g0",
                decisions="Chose X over Y.",
                branch="main",
                base_path=self.base,
            )

        self.assertEqual(ctx.exception.code, 1, "a validation refusal exits 1 (user error)")
        self.assertEqual(
            self._handoff_files(),
            [],
            "fail-closed: no handoff file is written when validation refuses",
        )

    @covers("REQ-0.0.65-03-03")
    def test_create_valid_input_writes_handoff_through_the_gate(self) -> None:
        handoff_create_cmd(
            adr="ADR-0.0.65",
            slug="my-work",
            agent="g0",
            decisions="Chose the thin-adapter shape over new domain logic.",
            branch="main",
            base_path=self.base,
        )

        written = self._handoff_files()
        self.assertEqual(len(written), 1, "a valid create writes exactly one handoff on disk")
        self.assertTrue(
            written[0].name.endswith("-my-work.md"),
            "the written file carries the requested slug",
        )
        # The written document must itself PASS validate_handoff_document. This
        # binds REQ-03's "routes through the validation gate": an implementation
        # that wrote a document WITHOUT running the validator could emit an
        # invalid file and still satisfy the existence checks above — this
        # re-validation refuses that, because the gate the adapter must route
        # through would never have let an invalid document reach disk.
        content = written[0].read_text(encoding="utf-8")
        self.assertEqual(
            validate_handoff_document(content, self.base),
            [],
            "the on-disk handoff is valid per the same gate create must route through",
        )


if __name__ == "__main__":
    unittest.main()
