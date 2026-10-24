"""Drive every REQ and TASK reader RO-2 tranche 2 moved onto the identity seam.

`docs/governance/harbor-ro2-identity-seam.md` § Tranches row 2. Each case feeds a
reader the seam's two-digit id and a width-loose or truncated one: a reader that
spelled its own looser grammar before the move accepts the loose id, so each case
fails when the reader's pattern is put back.
"""

import ast
import json
import tempfile
import unittest
from pathlib import Path

from gzkit.commands import task as task_cmd
from gzkit.commands.adr_audit_covers_backfill import _parent_obpi_id
from gzkit.commands.adr_demote import _live_covers_into_deleted_briefs
from gzkit.commands.specify_cmd import _REQ_ID_IN_SEED_RE
from gzkit.commands.validate_briefs import _REQ_ID_RE as BRIEF_REQ_RE
from gzkit.commands.validate_req_kind import _REQ_KIND_TAG_RE
from gzkit.commands.validate_task_envelope import (
    _is_req_attributed_uncovered_accept_event,
    _obpi_id_for_task,
    _task_matches_obpi,
)
from gzkit.foundation.sunset_migrate import _REQ_ID_RE as SUNSET_REQ_RE
from gzkit.governance.trust_audits.briefs import _COVERS_REQ_TAG, _SCENARIO_REQ_TAG
from gzkit.governance.trust_audits.closeout_proof import _REQ_LINE_RE
from gzkit.ontology.source import _ast_anchor_from_decorator
from gzkit.req_kind_fence import _fence_obpi_anchored, resolve_fence_proof
from gzkit.tasks import next_seq_for_req, parse_task_trailers

STRICT_REQ = "REQ-0.1.0-01-02"
LOOSE_REQ = "REQ-0.1.0-1-2"


class TestReqReaders(unittest.TestCase):
    def test_backfill_parent_obpi_from_the_seam_width_only(self) -> None:
        self.assertEqual(_parent_obpi_id(STRICT_REQ), "OBPI-0.1.0-01")
        self.assertIsNone(_parent_obpi_id(LOOSE_REQ))

    def test_demote_collects_only_seam_width_covers_of_the_semver(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "test_x.py").write_text(
                f'@covers("{STRICT_REQ}")\n@covers("{LOOSE_REQ}")\n@covers("REQ-0.2.0-01-01")\n',
                encoding="utf-8",
            )
            self.assertEqual(
                _live_covers_into_deleted_briefs(root, "ADR-0.1.0-example"), [STRICT_REQ]
            )

    def test_seed_harvest_takes_the_seam_width_only(self) -> None:
        self.assertEqual(
            _REQ_ID_IN_SEED_RE.findall(f"- {STRICT_REQ} and {LOOSE_REQ}"), [STRICT_REQ]
        )

    def test_task_command_splits_only_the_seam_req_id(self) -> None:
        self.assertEqual(task_cmd._REQ_PARTS_RE.match(STRICT_REQ).groups(), ("0.1.0", "01", "02"))
        self.assertIsNone(task_cmd._REQ_PARTS_RE.match(LOOSE_REQ))

    def test_brief_requirement_scan_takes_the_seam_width_only(self) -> None:
        self.assertIsNotNone(BRIEF_REQ_RE.search(f"- [ ] {STRICT_REQ}"))
        self.assertIsNone(BRIEF_REQ_RE.search(f"- [ ] {LOOSE_REQ}"))

    def test_kind_tag_takes_the_seam_width_only(self) -> None:
        self.assertTrue(_REQ_KIND_TAG_RE.findall(f"- [ ] {STRICT_REQ} [BEHAVIOR]: claim"))
        self.assertFalse(_REQ_KIND_TAG_RE.findall(f"- [ ] {LOOSE_REQ} [BEHAVIOR]: claim"))

    def test_sunset_migration_reads_the_semver_of_a_whole_req_id(self) -> None:
        match = SUNSET_REQ_RE.match(STRICT_REQ)
        self.assertEqual(match.group("semver"), "0.1.0")
        self.assertIsNone(SUNSET_REQ_RE.match("REQ-0.1.0-"))
        self.assertIsNone(SUNSET_REQ_RE.match(LOOSE_REQ))

    def test_audit_tags_take_the_seam_width_only(self) -> None:
        self.assertIsNotNone(_SCENARIO_REQ_TAG.search(f"  @{STRICT_REQ}"))
        self.assertIsNone(_SCENARIO_REQ_TAG.search(f"  @{LOOSE_REQ}"))
        self.assertIsNotNone(_COVERS_REQ_TAG.search(f'@covers("{STRICT_REQ}")'))
        self.assertIsNone(_COVERS_REQ_TAG.search(f'@covers("{LOOSE_REQ}")'))

    def test_closeout_proof_reads_only_the_seam_req_line(self) -> None:
        self.assertIsNotNone(_REQ_LINE_RE.match(f"- [x] {STRICT_REQ} [BEHAVIOR]: claim"))
        self.assertIsNone(_REQ_LINE_RE.match(f"- [x] {LOOSE_REQ} [BEHAVIOR]: claim"))

    def test_ontology_anchor_reads_only_the_seam_req_id(self) -> None:
        def anchor(req_id: str):
            tree = ast.parse(f'@covers("{req_id}")\ndef f(): pass\n')
            return _ast_anchor_from_decorator(tree.body[0].decorator_list[0], "x.py")

        self.assertIsNotNone(anchor(STRICT_REQ))
        self.assertIsNone(anchor(LOOSE_REQ))

    def test_fence_readers_parse_only_the_seam_req_id(self) -> None:
        section = "- (OBPI-01) invariant"
        self.assertTrue(_fence_obpi_anchored(section, STRICT_REQ))
        self.assertFalse(_fence_obpi_anchored(section, LOOSE_REQ))
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(resolve_fence_proof(LOOSE_REQ, Path(tmp)), "unproven-fence")

    def test_next_seq_refuses_a_loose_req_id(self) -> None:
        self.assertEqual(next_seq_for_req(STRICT_REQ, existing_task_ids=[]), 1)
        with self.assertRaises(ValueError):
            next_seq_for_req(LOOSE_REQ, existing_task_ids=[])

    def test_uncovered_accept_attribution_needs_the_seam_req_id(self) -> None:
        active = {"OBPI-0.1.0-01-x": {"TASK-0.1.0-01-02-01"}}

        def event(req_id: str) -> dict:
            return {
                "event": "obpi_completion_uncovered_accept",
                "obpi_id": "OBPI-0.1.0-01-x",
                "req_id": req_id,
            }

        self.assertTrue(_is_req_attributed_uncovered_accept_event(event(STRICT_REQ), active))
        self.assertFalse(_is_req_attributed_uncovered_accept_event(event(LOOSE_REQ), active))
        loose_active = {"OBPI-0.1.0-01-x": {"TASK-0.1.0-1-2-1"}}
        self.assertFalse(_is_req_attributed_uncovered_accept_event(event(LOOSE_REQ), loose_active))


class TestTaskReaders(unittest.TestCase):
    def test_trailer_parse_takes_the_seam_width_only(self) -> None:
        self.assertEqual(
            [str(t) for t in parse_task_trailers("fix\n\nTask: TASK-0.1.0-01-02-03")],
            ["TASK-0.1.0-01-02-03"],
        )
        self.assertEqual(parse_task_trailers("fix\n\nTask: TASK-0.1.0-1-2-3"), [])

    def test_ledger_prefix_scan_takes_the_seam_width_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            ids = ["TASK-0.1.0-01-02-03", "TASK-0.1.0-1-2-3", "TASK-0.1-01-02-03"]
            ledger.write_text(
                "\n".join(json.dumps({"event": "task_started", "task_id": t}) for t in ids),
                encoding="utf-8",
            )
            self.assertEqual(
                task_cmd._collect_ledger_task_ids_for_obpi_prefix(ledger, "0.1.0-01"),
                {"TASK-0.1.0-01-02-03"},
            )
            self.assertEqual(
                task_cmd._collect_ledger_task_ids_for_obpi_prefix(ledger, "0.1-01"), set()
            )

    def test_envelope_maps_a_task_to_its_obpi_by_the_seam_id_only(self) -> None:
        self.assertEqual(_obpi_id_for_task("TASK-0.1.0-01-02-03"), "OBPI-0.1.0-01")
        self.assertIsNone(_obpi_id_for_task("TASK-0.1.0-01-02"))
        self.assertTrue(_task_matches_obpi("TASK-0.1.0-01-02-03", "OBPI-0.1.0-01"))
        self.assertFalse(_task_matches_obpi("TASK-0.1.0-01-02", "OBPI-0.1.0-01"))


if __name__ == "__main__":
    unittest.main()
