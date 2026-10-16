"""The pipeline control inventory's checker is pure and total (OBPI-0.35.0-17).

REQ-0.35.0-17-01: given an inventory, a baseline body, an invocation text, a
served text per stage and a rationale record, the checker returns every
violation the brief's § Control Inventory Contract lists, never only the
first, and returns none for a complete inventory.

REQ-0.35.0-17-02: removing one control row or one covered sentence from a
complete inventory makes the before-state check fail.

Built under the harbor pilotage of 2026-10-15
(docs/governance/harbor-pilotage-candidate-2026-10-15.md): the operator's
2026-10-04 Q6 ruling puts a gate between "inventory accepted" and "text
removed", so this checker is what makes an extracted inventory verifiable
before any prose leaves the skill body.
"""

from __future__ import annotations

import tempfile
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
    check_before_state,
    check_delivery,
    check_placement,
    check_rationale_record,
    load_inventory,
    read_skill_body,
)

BODY = """## Stage 1: Load Context

1. Read the receipt. If it is missing, STOP.

Measured 2026-10-04: the body is long.

**Abort if:** brief not found.
"""


def _complete_inventory(body: str = BODY) -> ControlInventory:
    blocks = split_blocks(body)
    return ControlInventory(
        baseline=Baseline(
            path=".gzkit/skills/x/SKILL.md",
            commit="abc1234",
            skill_version="1.0.0",
            body_sha256=body_digest(body),
        ),
        extracted_by="reviewer",
        mapped_by="author",
        blocks=[
            Block(
                text=blocks[0],
                non_control=[
                    NonControl(
                        quote="Stage 1: Load Context",
                        **{"class": "structure"},
                        reason="a heading",
                    )
                ],
            ),
            Block(
                text=blocks[1],
                controls=[
                    Control(
                        id="S1-001",
                        quote="Read the receipt. If it is missing, STOP.",
                        applies_at=["stage1"],
                        delivered_span="Read the receipt. If it is missing, STOP.",
                    )
                ],
            ),
            Block(
                text=blocks[2],
                non_control=[
                    NonControl(
                        quote="Measured 2026-10-04: the body is long.",
                        **{"class": "rationale"},
                        explains="S1-001",
                        reason="a dated measurement that binds nothing",
                    )
                ],
            ),
            Block(
                text=blocks[3],
                controls=[
                    Control(
                        id="S1-002",
                        quote="**Abort if:** brief not found.",
                        applies_at=["stage1", "stage5"],
                        delivered_span="**Abort if:** brief not found.",
                    )
                ],
            ),
        ],
    )


def _kinds(violations) -> list[str]:
    return sorted(v.kind for v in violations)


class TestBeforeStateChecks(unittest.TestCase):
    """REQ-0.35.0-17-01 and -02: the partition and its coverage."""

    def test_complete_inventory_returns_no_violations(self):
        self.assertEqual(check_before_state(_complete_inventory(), BODY), [])

    def test_every_violation_is_returned_not_only_the_first(self):
        inv = _complete_inventory()
        data = inv.model_dump(by_alias=True)
        data["baseline"]["body_sha256"] = "0" * 64
        data["blocks"][1]["controls"][0]["quote"] = "Read the receipt and sing."
        data["blocks"][3]["controls"][0]["id"] = "S1-001"
        data["blocks"][3]["controls"][0]["applies_at"] = ["stage9"]
        data["blocks"][2]["non_control"][0]["explains"] = "S9-999"
        broken = ControlInventory.model_validate(data)
        kinds = _kinds(check_before_state(broken, BODY))
        for expected in (
            "digest-mismatch",
            "quote-not-substring",
            "uncovered",
            "duplicate-control-id",
            "unknown-position",
            "explains-unknown",
        ):
            self.assertIn(expected, kinds, f"{expected} missing from {kinds}")

    def test_blocks_must_reproduce_the_baseline_body(self):
        inv = _complete_inventory()
        data = inv.model_dump(by_alias=True)
        data["blocks"].pop(2)
        broken = ControlInventory.model_validate(data)
        kinds = _kinds(check_before_state(broken, BODY))
        self.assertIn("blocks-differ", kinds)

    def test_removing_a_control_row_uncovers_its_characters(self):
        inv = _complete_inventory()
        data = inv.model_dump(by_alias=True)
        data["blocks"][1]["controls"] = []
        broken = ControlInventory.model_validate(data)
        violations = check_before_state(broken, BODY)
        uncovered = [v for v in violations if v.kind == "uncovered"]
        self.assertEqual(len(uncovered), 1)
        self.assertIn("Read the receipt", uncovered[0].detail)

    def test_removing_a_covered_sentence_is_reported(self):
        inv = _complete_inventory()
        data = inv.model_dump(by_alias=True)
        data["blocks"][1]["controls"][0]["quote"] = "Read the receipt."
        data["blocks"][1]["controls"][0]["delivered_span"] = "Read the receipt."
        broken = ControlInventory.model_validate(data)
        kinds = _kinds(check_before_state(broken, BODY))
        self.assertEqual(kinds, ["uncovered"])

    def test_markup_and_list_markers_need_no_coverage(self):
        # Block 1 is a numbered item whose "1. " marker is not quoted, and the
        # heading's hashes are not quoted either: markers and markup need no cover.
        self.assertEqual(check_before_state(_complete_inventory(), BODY), [])

    def test_delivered_span_must_equal_quote_unless_reworded(self):
        inv = _complete_inventory()
        data = inv.model_dump(by_alias=True)
        data["blocks"][1]["controls"][0]["delivered_span"] = "Read the receipt; if missing, stop."
        broken = ControlInventory.model_validate(data)
        self.assertEqual(_kinds(check_before_state(broken, BODY)), ["span-mismatch"])
        data["blocks"][1]["controls"][0]["reworded"] = {
            "text": "Read the receipt; if missing, stop.",
            "reason": "ruled correction",
        }
        reworded = ControlInventory.model_validate(data)
        self.assertEqual(check_before_state(reworded, BODY), [])

    def test_uncovered_detail_runs_over_the_meaningful_characters_a_quote_leaves_out(self):
        """The reported span starts at the first and ends at the last uncovered meaningful char.

        Coverage is read through the retention module's public seam
        (``meaningful_positions``); the list marker, the asterisks and the spaces
        around the quote are not what the detail names.
        """
        body = "- **Go** now, please.\n"
        block_text = split_blocks(body)[0]
        inv = ControlInventory(
            baseline=Baseline(
                path=".gzkit/skills/x/SKILL.md",
                commit="abc1234",
                skill_version="1.0.0",
                body_sha256=body_digest(body),
            ),
            extracted_by="reviewer",
            mapped_by="author",
            blocks=[
                Block(
                    text=block_text,
                    controls=[
                        Control(
                            id="S1-001",
                            quote="**Go**",
                            applies_at=["stage1"],
                            delivered_span="**Go**",
                        )
                    ],
                )
            ],
        )
        uncovered = [v for v in check_before_state(inv, body) if v.kind == "uncovered"]
        self.assertEqual([v.detail for v in uncovered], ["now, please."])

    def test_a_control_with_no_position_is_reported(self):
        inv = _complete_inventory()
        data = inv.model_dump(by_alias=True)
        data["blocks"][1]["controls"][0]["applies_at"] = []
        broken = ControlInventory.model_validate(data)
        self.assertEqual(_kinds(check_before_state(broken, BODY)), ["empty-applies-at"])


class TestDeliveryChecks(unittest.TestCase):
    """REQ-0.35.0-17-03: every control is delivered at every applies_at position."""

    def test_complete_delivery_returns_no_violations(self):
        inv = _complete_inventory()
        served = {
            "stage1": "Read the receipt. If it is missing, STOP.\n**Abort if:** brief not found.",
            "stage5": "**Abort if:** brief not found.",
        }
        self.assertEqual(check_delivery(inv, served), [])

    def test_missing_span_is_reported_at_each_position(self):
        inv = _complete_inventory()
        served = {"stage1": "Read the receipt. If it is missing, STOP.", "stage5": ""}
        violations = check_delivery(inv, served)
        self.assertEqual(
            sorted((v.kind, v.where) for v in violations),
            [("not-delivered", "S1-002@stage1"), ("not-delivered", "S1-002@stage5")],
        )

    def test_unserved_position_is_reported(self):
        inv = _complete_inventory()
        served = {
            "stage1": "Read the receipt. If it is missing, STOP.\n**Abort if:** brief not found."
        }
        violations = check_delivery(inv, served)
        self.assertEqual(
            [(v.kind, v.where) for v in violations], [("position-not-served", "S1-002@stage5")]
        )

    def test_reworded_row_is_delivered_by_its_rewording(self):
        inv = _complete_inventory()
        data = inv.model_dump(by_alias=True)
        data["blocks"][1]["controls"][0]["delivered_span"] = "Read the receipt; if missing, stop."
        data["blocks"][1]["controls"][0]["reworded"] = {
            "text": "Read the receipt; if missing, stop.",
            "reason": "ruled correction",
        }
        reworded = ControlInventory.model_validate(data)
        self.assertEqual(check_before_state(reworded, BODY), [])
        served = {
            "stage1": "Read the receipt; if missing, stop.\n**Abort if:** brief not found.",
            "stage5": "**Abort if:** brief not found.",
        }
        self.assertEqual(check_delivery(reworded, served), [])

    def test_stage_control_in_invocation_text_is_misplaced(self):
        inv = _complete_inventory()
        violations = check_placement(inv, "**Abort if:** brief not found.")
        self.assertEqual(
            [(v.kind, v.where) for v in violations], [("misplaced", "S1-002@invocation")]
        )
        self.assertEqual(check_placement(inv, "Nothing here."), [])

    def test_rationale_quote_must_sit_under_its_control_id(self):
        inv = _complete_inventory()
        record = "## S1-001\n\nMeasured 2026-10-04: the body is long.\n"
        self.assertEqual(check_rationale_record(inv, record), [])
        wrong_home = "## S1-002\n\nMeasured 2026-10-04: the body is long.\n"
        violations = check_rationale_record(inv, wrong_home)
        self.assertEqual([(v.kind, v.where) for v in violations], [("rationale-missing", "S1-001")])


class TestReadSkillBody(unittest.TestCase):
    """The body is what follows the frontmatter; a file without one is its own body."""

    @staticmethod
    def _inventory_for(path: str) -> ControlInventory:
        return ControlInventory(
            baseline=Baseline(path=path, commit="abc1234", skill_version="1.0.0", body_sha256="x"),
            extracted_by="reviewer",
            mapped_by="author",
        )

    def test_body_follows_the_closing_fence(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "SKILL.md").write_text(
                "---\nname: x\n---\n# Body\n\ntext\n", encoding="utf-8"
            )
            body = read_skill_body(Path(tmp), self._inventory_for("SKILL.md"))
        self.assertEqual(body, "# Body\n\ntext\n")

    def test_file_without_frontmatter_is_its_own_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "SKILL.md").write_text("# Body\n\n---\n\ntext\n", encoding="utf-8")
            body = read_skill_body(Path(tmp), self._inventory_for("SKILL.md"))
        # A horizontal rule in the body is not a frontmatter fence.
        self.assertEqual(body, "# Body\n\n---\n\ntext\n")

    def test_unterminated_frontmatter_is_returned_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "SKILL.md").write_text("---\nname: x\n# Body\n", encoding="utf-8")
            body = read_skill_body(Path(tmp), self._inventory_for("SKILL.md"))
        self.assertEqual(body, "---\nname: x\n# Body\n")


def _baseline_body(root: Path, inventory: ControlInventory) -> str | None:
    """Return the skill body at the commit the inventory pins, or None without history.

    AMENDED 2026-10-15 (OBPI-0.35.0-20): the cutover reduced the live body to the
    invocation text, so the before-state checks read the baseline the inventory
    pins (commit, path, digest) from history; the live tree is checked by
    ``tests/governance/test_pipeline_procedure_render.py``.
    """
    import subprocess

    from tests.commands.common import _isolated_git_env

    baseline = inventory.baseline
    shown = subprocess.run(
        ["git", "show", f"{baseline.commit}:{baseline.path}"],
        cwd=root,
        env=_isolated_git_env(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if shown.returncode:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / baseline.path
        copy.parent.mkdir(parents=True)
        copy.write_text(shown.stdout, encoding="utf-8", newline="")
        return read_skill_body(Path(tmp), inventory)


class TestCommittedInventoryPinsTheBody(unittest.TestCase):
    """The committed inventory's blocks reproduce the baseline body it pins."""

    def test_committed_inventory_matches_the_pinned_baseline(self):
        root = Path(__file__).resolve().parents[2]
        inventory = load_inventory(root)
        body = _baseline_body(root, inventory)
        if body is None:
            self.skipTest("the pinned baseline commit is not in this checkout's history")
        kinds = _kinds(check_before_state(inventory, body))
        self.assertNotIn("digest-mismatch", kinds, "the pinned digest no longer matches the body")
        self.assertNotIn(
            "blocks-differ", kinds, "the committed blocks no longer reproduce the body"
        )

    def test_committed_inventory_is_a_complete_partition(self):
        """REQ-0.35.0-17-02: every block fully covered, every row well formed, no violation."""
        root = Path(__file__).resolve().parents[2]
        inventory = load_inventory(root)
        body = _baseline_body(root, inventory)
        if body is None:
            self.skipTest("the pinned baseline commit is not in this checkout's history")
        violations = check_before_state(inventory, body)
        self.assertEqual(
            violations, [], "\n".join(f"{v.kind} {v.where}: {v.detail}" for v in violations[:12])
        )
        self.assertTrue(all(block.controls or block.non_control for block in inventory.blocks))


if __name__ == "__main__":
    unittest.main()
