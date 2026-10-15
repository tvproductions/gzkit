"""The served set is rendered from the attested control inventory (OBPI-0.35.0-20).

REQ-0.35.0-20-01: no stage control's span sits in the invocation text, and no
control's span sits in the procedure of a stage outside its ``applies_at``.
REQ-0.35.0-20-02: with the baseline unchanged, every control is delivered
verbatim at every position in its ``applies_at`` and the checker returns no
violation against the reduced body and the served procedures.
REQ-0.35.0-20-06: every passage the inventory classes ``rationale`` is in the
rationale record under the id of the control it explains, and each delivered
control that had such a passage carries a pointer to its entry.

The renderer is what makes the cutover reproducible: the stage files are
derived views of the inventory (Layer 3, `docs/governance/state-doctrine.md`)
and are held to the render by the real-tree test below. The skill body is
canon; the checker holds it to the controls rather than to the render.

Built under the harbor pilotage of 2026-10-15 ("attest the inventory, keep
going with the load cuts").
"""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from gzkit.content.retention import split_blocks
from gzkit.governance.pipeline_control_inventory import (
    Baseline,
    Block,
    Control,
    ControlInventory,
    NonControl,
    body_digest,
    check_delivery,
    check_placement,
    check_rationale_record,
    load_inventory,
    read_skill_body,
)
from gzkit.governance.pipeline_procedure_render import (
    RECORD_PATH,
    SERVED_STATEMENT,
    check_stage_placement,
    read_rationale_record,
    render_served_set,
    stage_ranges,
)
from gzkit.pipeline_procedure import STAGE_PROCEDURES, served_texts

ROOT = Path(__file__).resolve().parents[2]

BODY = """# demo

One line about the skill.

Launch with `gz demo`. Because of an incident in May.

## Stages

### Stage 1: Load

Read the brief. The reason we read it is historical.

A whole paragraph of history about Stage 1.

### Stage 2: Implement

Write the test. Tell Stage 1 something.

## Tail

| Failure | Action |
|---------|--------|
| Tests fail | Fix twice, then stop |

## Related

- A pointer kept as structure.
"""


def _control(id_: str, quote: str, *positions: str) -> Control:
    return Control(id=id_, quote=quote, applies_at=list(positions), delivered_span=quote)


def _structure(quote: str) -> NonControl:
    return NonControl(quote=quote, **{"class": "structure"}, reason="scaffold")


def _rationale(quote: str, explains: str) -> NonControl:
    return NonControl(quote=quote, **{"class": "rationale"}, explains=explains, reason="history")


def _inventory(body: str = BODY) -> ControlInventory:
    b = split_blocks(body)
    stages = ["stage1", "stage2"]
    return ControlInventory(
        baseline=Baseline(
            path=".gzkit/skills/demo/SKILL.md",
            commit="abc1234",
            skill_version="1.0.0",
            body_sha256=body_digest(body),
        ),
        extracted_by="reviewer",
        mapped_by="author",
        blocks=[
            Block(text=b[0], non_control=[_structure("demo")]),
            Block(text=b[1], non_control=[_structure(b[1])]),
            Block(
                text=b[2],
                controls=[_control("I-001", "Launch with `gz demo`.", "invocation", *stages)],
                non_control=[_rationale("Because of an incident in May.", "I-001")],
            ),
            Block(text=b[3], non_control=[_structure("Stages")]),
            Block(text=b[4], non_control=[_structure("Stage 1: Load")]),
            Block(
                text=b[5],
                controls=[_control("S1-001", "Read the brief.", "stage1")],
                non_control=[_rationale("The reason we read it is historical.", "S1-001")],
            ),
            Block(text=b[6], non_control=[_rationale(b[6], "S1-001")]),
            Block(text=b[7], non_control=[_structure("Stage 2: Implement")]),
            Block(
                text=b[8],
                controls=[
                    _control("S2-001", "Write the test.", "stage2"),
                    _control("S2-002", "Tell Stage 1 something.", "stage1"),
                ],
            ),
            Block(text=b[9], non_control=[_structure("Tail")]),
            Block(text=b[10], non_control=[_structure("Failure | Action")]),
            Block(text=b[11], non_control=[_structure(b[11])]),
            Block(text=b[12], controls=[_control("T-001", b[12], "stage2")]),
            Block(text=b[13], non_control=[_structure("Related")]),
            Block(text=b[14], non_control=[_structure("A pointer kept as structure.")]),
        ],
    )


class TestStageRanges(unittest.TestCase):
    def test_ranges_run_from_each_stage_heading_to_the_next_section(self):
        ranges = stage_ranges(_inventory())
        self.assertEqual(ranges, {"stage1": range(4, 7), "stage2": range(7, 9)})


class TestRenderedBody(unittest.TestCase):
    """REQ-0.35.0-20-01 and -05: invocation text only, plus the served-procedure statement."""

    def setUp(self):
        self.inv = _inventory()
        self.rendered = render_served_set(self.inv)

    def test_body_keeps_invocation_controls_and_drops_their_rationale(self):
        self.assertIn("Launch with `gz demo`.", self.rendered.body)
        self.assertNotIn("incident in May", self.rendered.body)

    def test_body_carries_no_stage_control(self):
        self.assertEqual(check_placement(self.inv, self.rendered.body), [])
        self.assertNotIn("Read the brief.", self.rendered.body)
        self.assertNotIn("Tests fail", self.rendered.body)

    def test_body_states_that_stage_procedures_are_served_before_the_first_section(self):
        self.assertIn(SERVED_STATEMENT, self.rendered.body)
        self.assertLess(self.rendered.body.index(SERVED_STATEMENT), self.rendered.body.index("## "))

    def test_body_prunes_headings_and_tables_left_without_content(self):
        # "## Stages" introduces only the stage sections; "## Tail" only a stage row.
        self.assertNotIn("## Stages", self.rendered.body)
        self.assertNotIn("## Tail", self.rendered.body)
        self.assertNotIn("| Failure | Action |", self.rendered.body)
        # "## Related" keeps a structure list item, so it stays.
        self.assertIn("## Related", self.rendered.body)
        self.assertIn("- A pointer kept as structure.", self.rendered.body)

    def test_a_delivered_control_with_rationale_carries_a_pointer_to_its_entry(self):
        self.assertIn(f"> Rationale: {RECORD_PATH} § I-001", self.rendered.body)


class TestRenderedStages(unittest.TestCase):
    """REQ-0.35.0-20-01 and -02 on the served procedures."""

    def setUp(self):
        self.inv = _inventory()
        self.rendered = render_served_set(self.inv)

    def test_each_stage_holds_its_own_controls_and_the_carried_ones_without_rationale(self):
        stage1 = self.rendered.stages["stage1"]
        self.assertIn("Read the brief.", stage1)
        self.assertNotIn("historical", stage1)
        self.assertNotIn("A whole paragraph of history", stage1)
        self.assertIn("Tell Stage 1 something.", stage1)
        self.assertNotIn("Write the test.", stage1)
        self.assertIn("Launch with `gz demo`.", stage1)
        self.assertIn(f"> Rationale: {RECORD_PATH} § S1-001", stage1)

    def test_a_carried_table_row_brings_its_header(self):
        stage2 = self.rendered.stages["stage2"]
        self.assertIn("| Failure | Action |\n|---------|--------|\n| Tests fail", stage2)

    def test_every_control_is_delivered_at_every_position_and_nowhere_else(self):
        served = dict(self.rendered.stages)
        served["invocation"] = self.rendered.body
        self.assertEqual(check_delivery(self.inv, served), [])
        self.assertEqual(check_stage_placement(self.inv, self.rendered.stages), [])

    def test_stage_placement_reports_a_span_served_outside_its_positions(self):
        served = dict(self.rendered.stages)
        served["stage1"] += "\n\nWrite the test.\n"
        violations = check_stage_placement(self.inv, served)
        self.assertEqual([(v.kind, v.where) for v in violations], [("misplaced", "S2-001@stage1")])


class TestRenderEdges(unittest.TestCase):
    """The renderer's edges: no stages, a bad inventory, a rewording, a trailing table."""

    def test_an_inventory_without_stage_headings_renders_a_body_and_no_stages(self):
        body = "# demo\n\nLaunch with `gz demo`.\n"
        b = split_blocks(body)
        inv = ControlInventory(
            baseline=Baseline(
                path="x/SKILL.md",
                commit="abc1234",
                skill_version="1.0.0",
                body_sha256=body_digest(body),
            ),
            extracted_by="r",
            mapped_by="a",
            blocks=[
                Block(text=b[0], non_control=[_structure("demo")]),
                Block(text=b[1], controls=[_control("I-001", b[1], "invocation")]),
            ],
        )
        self.assertEqual(stage_ranges(inv), {})
        rendered = render_served_set(inv)
        self.assertEqual(rendered.stages, {})
        self.assertIn("Launch with `gz demo`.", rendered.body)

    def test_render_refuses_a_rationale_quote_that_is_not_in_its_block(self):
        data = _inventory().model_dump(by_alias=True)
        data["blocks"][2]["non_control"][0]["quote"] = "Not in the block at all."
        with self.assertRaises(ValueError) as ctx:
            render_served_set(ControlInventory.model_validate(data))
        # The refusal names the quote; an unpacking error from the split would not.
        self.assertIn("not in the block", str(ctx.exception))
        self.assertIn("Not in the block at all.", str(ctx.exception))

    def test_a_reworded_control_is_delivered_by_its_rewording(self):
        data = _inventory().model_dump(by_alias=True)
        row = data["blocks"][5]["controls"][0]
        row["delivered_span"] = "Read the brief first."
        row["reworded"] = {"text": "Read the brief first.", "reason": "ruled correction"}
        inv = ControlInventory.model_validate(data)
        rendered = render_served_set(inv)
        self.assertIn("Read the brief first.", rendered.stages["stage1"])
        self.assertNotIn("Read the brief. ", rendered.stages["stage1"])
        served = dict(rendered.stages)
        served["invocation"] = rendered.body
        self.assertEqual(check_delivery(inv, served), [])

    def test_a_pointer_for_a_table_row_follows_the_whole_table(self):
        data = _inventory().model_dump(by_alias=True)
        data["blocks"][12]["non_control"] = [
            {"quote": "", "class": "rationale", "explains": "T-001", "reason": "history"}
        ]
        data["blocks"][6]["non_control"][0]["explains"] = "T-001"
        data["blocks"][12]["non_control"] = []
        inv = ControlInventory.model_validate(data)
        stage2 = render_served_set(inv).stages["stage2"]
        row = "| Tests fail | Fix twice, then stop |"
        pointer = f"> Rationale: {RECORD_PATH} § T-001"
        self.assertIn(f"{row}\n\n{pointer}", stage2)
        self.assertTrue(stage2.rstrip().endswith(pointer))

    def test_stage_placement_skips_the_invocation_text(self):
        inv = _inventory()
        rendered = render_served_set(inv)
        served = dict(rendered.stages)
        served["invocation"] = rendered.body + "\n\nWrite the test.\n"
        self.assertEqual(check_stage_placement(inv, served), [])
        self.assertEqual(
            [v.where for v in check_placement(inv, served["invocation"])], ["S2-001@invocation"]
        )


class TestRenderedRecord(unittest.TestCase):
    """REQ-0.35.0-20-06: every rationale passage, verbatim, under its control's id."""

    def test_record_holds_every_rationale_quote_under_its_control(self):
        inv = _inventory()
        rendered = render_served_set(inv)
        self.assertEqual(check_rationale_record(inv, rendered.record), [])
        self.assertIn("## I-001\n", rendered.record)
        self.assertIn("## S1-001\n", rendered.record)
        self.assertIn("A whole paragraph of history about Stage 1.", rendered.record)

    def test_render_refuses_when_stripping_would_lose_a_control(self):
        inv = _inventory()
        data = inv.model_dump(by_alias=True)
        # Declare the control's own text as rationale: removing it would drop the control.
        data["blocks"][2]["non_control"][0]["quote"] = "Launch with `gz demo`."
        broken = ControlInventory.model_validate(data)
        with self.assertRaises(ValueError):
            render_served_set(broken)


class TestCommittedServedSet(unittest.TestCase):
    """The real tree: the files the runtime serves are the render, and the body is placed."""

    def test_committed_stage_files_are_the_render(self):
        inventory = load_inventory(ROOT)
        rendered = render_served_set(inventory)
        served = served_texts(ROOT)
        for procedure in STAGE_PROCEDURES:
            self.assertEqual(served[procedure.key], rendered.stages[procedure.key], procedure.key)
            self.assertEqual(
                hashlib.sha256(served[procedure.key].encode("utf-8")).hexdigest(),
                procedure.sha256,
                f"{procedure.filename} is not the bytes the runtime pins",
            )

    def test_committed_body_and_procedures_place_every_control_and_no_other(self):
        inventory = load_inventory(ROOT)
        body = read_skill_body(ROOT, inventory)
        served = served_texts(ROOT)
        self.assertEqual(check_placement(inventory, body), [])
        self.assertEqual(check_stage_placement(inventory, served), [])
        served["invocation"] = body
        self.assertEqual(check_delivery(inventory, served), [])

    def test_committed_record_holds_every_rationale_passage(self):
        inventory = load_inventory(ROOT)
        violations = check_rationale_record(inventory, read_rationale_record(ROOT))
        self.assertEqual(
            violations, [], "\n".join(f"{v.where}: {v.detail}" for v in violations[:8])
        )


if __name__ == "__main__":
    unittest.main()
