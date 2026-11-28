"""The handoff's picture and the computed position a resume opens with.

`docs/design/briefs/SPEC-session-handoff-picture.md` (accepted 2026-10-31), built
2026-11-28 on the operator's word: *"build it now so every resume shows the
position - this should cut down on vibe coding."*, choosing *"Both
(Recommended)"*: the agent-written picture, in the order *"left to right: tactical
| operational | strategic"*, beside position facts computed from the record.

Assertions follow the spec's § 11 acceptance rows 1, 2 and 4 and the facts each
position line must carry, over temporary projects.
"""

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import override

from gzkit.commands.common import console
from gzkit.commands.handoff import handoff_create_cmd, handoff_resume_cmd
from gzkit.handoff_api import create_handoff, resume_handoff
from gzkit.handoff_validation import (
    PICTURE_LEVELS,
    PICTURE_SECTION,
    REQUIRED_SECTIONS,
    parse_picture,
    render_picture,
    validate_handoff_document,
)
from gzkit.mx.position import (
    commit_position,
    contract_lines,
    drydock_position,
    last_log_entry,
)
from tests.commands.common import SilencedConsoleTestCase, gh_stand_in

_PICTURE = {
    "tactical": "Closed #1367; the board is up.",
    "operational": "RP-12 is in progress; O5 is next.",
    "strategic": "The 1.0 campaign waits on the drydock.",
}

_CONTRACT = """# Contract

## List of discrepancies

### RP-0 — the drydock itself

- `open` **blocks return to service** — the alarms are off.
- `open` **due by a named event** — the brief is missing.
  A wrapped line that says blocks return to service is not a grade.
- `cleared` **blocks return to service** — the lint debt.

## Passage log

| Date | Act | Before | After |
|---|---|---|---|
| 2026-11-02 | an act | a | b |
| 2026-11-19 | the last act | c | d |

## After
"""


class _Project(unittest.TestCase):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.base = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(gh_stand_in({}))

    def _create(
        self,
        tactical: str | None = None,
        operational: str | None = None,
        strategic: str | None = None,
    ) -> None:
        handoff_create_cmd(
            slug="work",
            agent="g0",
            summary="Landed the picture.",
            context="The picture is for the operator.",
            decisions="- [agent-chose] Built the picture.",
            next_steps="1. Read the picture.",
            pending="None.",
            verification="uv run -m unittest tests.test_handoff_position",
            evidence="The commit that lands the picture.",
            branch="main",
            base_path=self.base,
            tactical=tactical,
            operational=operational,
            strategic=strategic,
        )

    def _handoffs(self) -> list[Path]:
        return sorted((self.base / ".gzkit" / "handoffs").glob("*.md"))


class TestPictureAtCreate(_Project, SilencedConsoleTestCase):
    """Acceptance rows 1 and 2: CREATE needs all three levels; nothing else does."""

    def test_create_without_any_one_level_is_refused_and_writes_nothing(self) -> None:
        for missing in _PICTURE:
            given = {level: text for level, text in _PICTURE.items() if level != missing}
            with self.subTest(missing=missing), self.assertRaises(SystemExit) as ctx:
                self._create(**given)
            self.assertEqual(ctx.exception.code, 1)
        self.assertEqual(self._handoffs(), [])

    def test_create_with_all_three_levels_writes_them_in_operator_order(self) -> None:
        self._create(**_PICTURE)
        (path,) = self._handoffs()
        content = path.read_text(encoding="utf-8")
        self.assertEqual(validate_handoff_document(content, self.base), [])
        self.assertEqual(list(parse_picture(content)), list(PICTURE_LEVELS))
        self.assertEqual(parse_picture(content)["Operational"], _PICTURE["operational"])
        self.assertLess(
            content.index(f"## {PICTURE_SECTION}"), content.index("## Current State Summary")
        )

    def test_checkpoint_needs_no_picture(self) -> None:
        handoff_create_cmd(
            slug="pause",
            agent="g0",
            summary="Paused.",
            context="Mid-flight.",
            decisions="- [agent-chose] Paused here.",
            next_steps="1. Resume.",
            pending="None.",
            verification="None.",
            evidence="None.",
            branch="main",
            mode="CHECKPOINT",
            base_path=self.base,
        )
        self.assertEqual(len(self._handoffs()), 1)

    def test_a_partial_picture_is_refused_in_any_mode(self) -> None:
        with self.assertRaises(SystemExit):
            handoff_create_cmd(
                slug="pause",
                agent="g0",
                summary="Paused.",
                context="Mid-flight.",
                decisions="- [agent-chose] Paused here.",
                next_steps="1. Resume.",
                pending="None.",
                verification="None.",
                evidence="None.",
                branch="main",
                mode="CHECKPOINT",
                tactical="Only one level.",
                base_path=self.base,
            )
        self.assertEqual(self._handoffs(), [])

    def test_the_mechanical_writer_needs_no_picture(self) -> None:
        sections = {section: f"Seeded {section}." for section in REQUIRED_SECTIONS}
        create_handoff(
            branch="main", agent="g0", slug="mechanical", sections=sections, base_path=self.base
        )
        self.assertEqual(len(self._handoffs()), 1)


class TestPictureAtResume(_Project, SilencedConsoleTestCase):
    """Acceptance row 4: `gz handoff resume` returns the picture."""

    def test_resume_returns_the_three_levels(self) -> None:
        self._create(**_PICTURE)
        result = resume_handoff(base_path=self.base, now=datetime.now(UTC).isoformat())
        self.assertEqual(list(result.picture), list(PICTURE_LEVELS))
        self.assertEqual(result.picture["Strategic"], _PICTURE["strategic"])

    def test_a_handoff_without_a_picture_resumes_with_none(self) -> None:
        sections = {section: f"Seeded {section}." for section in REQUIRED_SECTIONS}
        create_handoff(
            branch="main", agent="g0", slug="old", sections=sections, base_path=self.base
        )
        result = resume_handoff(base_path=self.base, now=datetime.now(UTC).isoformat())
        self.assertEqual(result.picture, {})

    def test_render_and_parse_round_trip(self) -> None:
        levels = {"Tactical": "t", "Operational": "o", "Strategic": "s"}
        body = f"## {PICTURE_SECTION}\n\n{render_picture(levels)}\n\n## Next\n"
        self.assertEqual(parse_picture(body), levels)


class TestContractReading(unittest.TestCase):
    """The drydock facts read the contract's own list and log, by their grammar."""

    def test_open_and_blocking_lines_are_counted_by_their_first_line(self) -> None:
        self.assertEqual(contract_lines(_CONTRACT), (2, 1))

    def test_the_passage_log_reports_its_latest_date(self) -> None:
        self.assertEqual(last_log_entry(_CONTRACT), "2026-11-19")

    def test_a_contract_without_the_sections_reads_nothing(self) -> None:
        self.assertEqual(contract_lines("# Contract\n"), (0, 0))
        self.assertIsNone(last_log_entry("# Contract\n"))


class TestDrydockPosition(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.base = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (self.base / ".gzkit").mkdir()

    def _open(self, *, contract: str = "docs/contract.md") -> None:
        (self.base / ".gzkit" / "mx.json").write_text(
            json.dumps(
                {
                    "session_id": "s-1",
                    "opened_at": "2026-10-20T00:00:00+00:00",
                    "mode": "safe",
                    "contract": contract,
                }
            ),
            encoding="utf-8",
        )
        event = {
            "schema": "gzkit.ledger.v1",
            "event": "mx_session_opened",
            "id": "s-1",
            "session_id": "s-1",
            "ts": "2026-10-20T00:00:00+00:00",
        }
        (self.base / ".gzkit" / "ledger.jsonl").write_text(json.dumps(event) + "\n", "utf-8")

    def _facts(self) -> dict[str, str]:
        now = datetime(2026, 11, 28, tzinfo=UTC)
        return {fact.label: fact.value for fact in drydock_position(self.base, now=now)}

    def test_an_open_drydock_reports_its_age_lines_and_log(self) -> None:
        self._open()
        (self.base / "docs").mkdir()
        (self.base / "docs" / "contract.md").write_text(_CONTRACT, encoding="utf-8")
        facts = self._facts()
        self.assertIn("2026-10-20", facts["Out of service since"])
        self.assertIn("39 days", facts["Out of service since"])
        self.assertIn("1 blocking", facts["Contract discrepancy lines"])
        self.assertIn("2 open", facts["Contract discrepancy lines"])
        self.assertEqual(facts["Passage log, last entry"], "2026-11-19")
        self.assertIn("0 open", facts["Ledger discrepancy lines"])

    def test_every_fact_names_its_source(self) -> None:
        self._open()
        for fact in drydock_position(self.base, now=datetime(2026, 11, 28, tzinfo=UTC)):
            with self.subTest(fact=fact.label):
                self.assertTrue(fact.source)

    def test_no_hangar_says_so_and_reads_nothing_else(self) -> None:
        facts = self._facts()
        self.assertEqual(list(facts), ["Out of service"])
        self.assertIn("absent", facts["Out of service"])

    def test_a_missing_contract_is_reported_not_invented(self) -> None:
        self._open(contract="docs/gone.md")
        self.assertIn("not found", self._facts()["Contract"])


class TestCommitPosition(unittest.TestCase):
    def test_commits_naming_a_repair_order_are_counted(self) -> None:
        subjects = [
            "fix(mx): an exit refuses at 3 (RP-12 ruling 204)",
            "docs(rnd): RO-5 tranche 5",
            "chore: drydock passage log",
            "fix(validate): the size-limit fence (GHI #1367)",
        ]
        fact = commit_position(subjects, since="2026-11-28T09:20:52Z")
        self.assertEqual(fact.value, "3 of 4 name a repair order or the drydock")
        self.assertIn("2026-11-28T09:20:52Z", fact.source)


class TestResumeRendering(_Project):
    """# output-contract: the operator reads the position, then the picture, first."""

    def test_resume_leads_with_the_position_then_the_picture(self) -> None:
        self._create(**_PICTURE)
        with console.capture() as captured:
            handoff_resume_cmd(base_path=self.base)
        text = captured.get()
        position = text.index("position (computed from the record)")
        picture = text.index("picture (the handoff's author)")
        steps = text.index("next steps")
        self.assertLess(position, picture)
        self.assertLess(picture, steps)
        tactical, operational, strategic = (
            text.index(level) for level in ("Tactical", "Operational", "Strategic")
        )
        self.assertLess(tactical, operational)
        self.assertLess(operational, strategic)


if __name__ == "__main__":
    unittest.main()
