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

import inspect
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from gzkit.commands.handoff import (
    SECTION_PARAMS,
    handoff_create_cmd,
    handoff_list_cmd,
    handoff_resume_cmd,
)
from gzkit.handoff_api import (
    ReferenceState,
    create_handoff,
    settled_rulings,
    validate_handoff_document,
)
from gzkit.handoff_validation import REQUIRED_SECTIONS
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
        """Author a valid handoff on disk through the real API (OBPI-02).

        Every required section carries a body: a handoff with empty sections is
        refused at authoring (GHI #692), so a seed that supplied only Decisions
        Made would no longer reach disk.
        """
        sections: dict[str, str] = {section: f"Seeded {section}." for section in REQUIRED_SECTIONS}
        sections["Decisions Made"] = "Chose the thin-adapter shape."
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


class TestHandoffResumeReferenceRendering(_HandoffCliCase):
    """The resume report marks a step whose cited precondition is settled.

    Output-form assertions are the named contract here: the operator reads this
    rendering to decide what is still actionable, so the CITES SETTLED marker and the
    per-step ``refs:`` line ARE the behavior (GHI #696 defect 2). The ``gh``
    boundary is mocked per the unit-tier contract — no network, no live issue.
    """

    def _capture_console(self, fn) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            fn()
        return buf.getvalue()

    def _resume_with_states(self, next_steps: str, states: dict[str, ReferenceState]) -> str:
        self._seed(
            adr_id="ADR-0.0.65",
            slug="refs",
            timestamp="2026-07-14T09:00:00Z",
            next_steps=next_steps,
        )
        with mock.patch(
            "gzkit.commands.handoff._gh_issue_state",
            side_effect=lambda number, _root: states.get(number, ReferenceState.UNKNOWN),
        ):
            return self._capture_console(
                lambda: handoff_resume_cmd(
                    adr="ADR-0.0.65", now="2026-07-14T11:00:00Z", base_path=self.base
                )
            )

    def test_step_citing_a_closed_ghi_renders_void(self) -> None:
        # output-contract: the CITES SETTLED marker is what prompts the operator to
        # adjudicate; its absence is the GHI #693 re-adjudication.
        out = self._resume_with_states(
            "1. Rule on GHI #693 (cli audit presence-vs-truth).",
            {"693": ReferenceState.SETTLED},
        )

        self.assertIn("CITES SETTLED", out)
        self.assertIn("settled", out)
        self.assertIn("cite a settled reference", out)

    def test_step_citing_an_open_ghi_renders_live_without_void(self) -> None:
        # output-contract: a live precondition must not be decorated as void.
        out = self._resume_with_states(
            "1. Rule on GHI #691 (rules have no aging clock).",
            {"691": ReferenceState.LIVE},
        )

        self.assertIn("live", out)
        self.assertNotIn("CITES SETTLED", out)

    def test_unreachable_gh_renders_unknown_not_live(self) -> None:
        # output-contract: an unresolvable reference must read as unknown, never
        # as verified — the operator must be able to see the check did not run.
        out = self._resume_with_states("1. Rule on GHI #693.", {})

        self.assertIn("unknown", out)
        self.assertNotIn("CITES SETTLED", out)


class TestHandoffResumeDecisionRendering(_HandoffCliCase):
    """An operator ruling must not arrive looking like an agent preference.

    GHI #696 defect 4: `Decisions Made` rendered operator rulings and unilateral
    agent choices with identical structure and weight, so both reached the next
    session equally re-arguable. Operator canon is verbatim — "MY WORD IS
    AUTHORITY IN ALL CASES" — so the rendering IS the contract here.
    """

    def _resume_output(self, decisions: str, *, slug: str = "d") -> str:
        sections = {section: f"Seeded {section}." for section in REQUIRED_SECTIONS}
        sections["Decisions Made"] = decisions
        create_handoff(
            adr_id="ADR-0.0.65",
            branch="main",
            agent="g0",
            slug=slug,
            sections=sections,
            base_path=self.base,
            timestamp="2026-07-14T09:00:00Z",
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            handoff_resume_cmd(adr="ADR-0.0.65", now="2026-07-14T11:00:00Z", base_path=self.base)
        return buf.getvalue()

    def test_operator_ruling_renders_as_authority(self) -> None:
        # output-contract: the AUTHORITY label is what stops a booked ruling from
        # reading as one more agent preference on resume.
        out = self._resume_output("- [operator-ruled] Defer #641 to Movement IV.")

        self.assertIn("AUTHORITY", out)
        self.assertIn("Defer #641 to Movement IV.", out)

    def test_agent_choice_is_not_labelled_authority(self) -> None:
        # output-contract: agent choices must stay visibly re-arguable.
        out = self._resume_output("- [agent-chose] Widened the glob.")

        self.assertNotIn("AUTHORITY", out)
        self.assertIn("agent-chose", out)

    def test_unattributed_decision_renders_as_unattributed(self) -> None:
        # output-contract: an unmarked decision is neither promoted nor demoted.
        out = self._resume_output("- Chose to wrap the validator.")

        self.assertIn("unattributed", out)
        self.assertNotIn("AUTHORITY", out)

    def test_carried_settled_rulings_render_as_do_not_reopen(self) -> None:
        # output-contract: the settled channel only cures re-adjudication if the
        # resuming agent can see the ruling is closed.
        sections = {section: f"Seeded {section}." for section in REQUIRED_SECTIONS}
        sections["Decisions Made"] = "- [operator-ruled] Do NOT promote sensitivity into GATE5."
        # Strictly EARLIER than the resumed handoff: the carry-forward under test
        # is chronological (a prior session's ruling reaching the next one), so
        # the fixture must not lean on the equal-timestamp tie-break to decide
        # which of the two `resume` selects.
        create_handoff(
            adr_id="ADR-0.0.65",
            branch="main",
            agent="g0",
            slug="first",
            sections=sections,
            base_path=self.base,
            timestamp="2026-07-14T08:00:00Z",
        )
        out = self._resume_output("- [agent-chose] Nothing settled here.", slug="second")

        self.assertIn("settled — do NOT re-open", out)
        self.assertIn("Do NOT promote sensitivity into GATE5.", out)


class TestHandoffCreateSeatsLateRulings(_HandoffCliCase):
    """`--settled` seats a ruling that arrived after the prior handoff was authored.

    The carry-forward mechanism composes Settled Rulings at authoring time, so a
    ruling the operator issues AFTER a session's handoff is committed has no home
    in that handoff — the next one is the only seat. `--settled` is that seat, and
    it must UNION with the carried set: replacing would drop every ruling booked
    before it, turning the cure into a fresh instance of the same decay.
    """

    def _create(self, *, slug: str, timestamp: str, decisions: str, settled=None) -> Path:
        handoff_create_cmd(
            adr="ADR-0.0.65",
            slug=slug,
            agent="g0",
            decisions=decisions,
            summary="Seeded summary.",
            context="Seeded context.",
            next_steps="1. Continue.",
            pending="Seeded pending.",
            verification="- [ ] Tests pass.",
            evidence="Seeded evidence.",
            settled=settled,
            base_path=self.base,
        )
        written = (self.base / ".gzkit" / "handoffs").glob("*.md")
        return next(p for p in written if p.name.endswith(f"{slug}.md"))

    def test_seated_ruling_is_recorded_alongside_carried_ones(self) -> None:
        self._create(
            slug="first",
            timestamp="2026-07-14T09:00:00Z",
            decisions="- [operator-ruled] Earlier ruling holds.",
        )

        second = self._create(
            slug="second",
            timestamp="2026-07-14T10:00:00Z",
            decisions="- [agent-chose] Nothing new.",
            settled=["Reframe #580 to truncation survival."],
        )

        settled = settled_rulings(second.read_text(encoding="utf-8"))
        self.assertIn("Earlier ruling holds.", settled, "carried rulings must not be dropped")
        self.assertIn("Reframe #580 to truncation survival.", settled)

    def test_no_settled_flag_still_self_populates(self) -> None:
        """The flag is an escape hatch, not a requirement — inheritance is default."""
        self._create(
            slug="first",
            timestamp="2026-07-14T09:00:00Z",
            decisions="- [operator-ruled] Earlier ruling holds.",
        )

        second = self._create(
            slug="second",
            timestamp="2026-07-14T10:00:00Z",
            decisions="- [agent-chose] Nothing new.",
        )

        self.assertEqual(
            settled_rulings(second.read_text(encoding="utf-8")), ["Earlier ruling holds."]
        )


class TestHandoffCreate(_HandoffCliCase):
    def _handoff_files(self) -> list[Path]:
        return list((self.base / ".gzkit" / "handoffs").glob("*.md"))

    def test_every_required_section_is_reachable_from_the_cli(self) -> None:
        """Coupled-surface coherence: a section with no flag is an unfillable hollow.

        GHI #692's root was this coupling breaking silently — REQUIRED_SECTIONS
        grew to seven while `gz handoff create` kept parameters for two, so the
        default invocation could only ever emit empty headings. Now that the
        validator refuses those, an unmapped section would make the verb unusable
        rather than merely hollow. Bind the surfaces so the regression is a
        failing test, not a discovery (AGENTS.md § DO IT RIGHT 1a).
        """
        self.assertEqual(
            set(SECTION_PARAMS),
            set(REQUIRED_SECTIONS),
            "SECTION_PARAMS must map exactly the required sections",
        )
        params = set(inspect.signature(handoff_create_cmd).parameters)
        self.assertEqual(
            [p for p in SECTION_PARAMS.values() if p not in params],
            [],
            "every mapped section parameter must exist on handoff_create_cmd",
        )

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
            summary="Landed the thin adapter over the OBPI-02 API.",
            context="The API is the only writer; the adapter carries no domain logic.",
            decisions="Chose the thin-adapter shape over new domain logic.",
            next_steps="1. Land the adapter unit tests.",
            pending="None; the adapter surface is complete.",
            verification="uv run -m unittest tests.test_handoff_cli",
            evidence="The ledger completion receipt for this adapter.",
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
