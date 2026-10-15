"""The runtime serves each stage's procedure at stage entry (OBPI-0.35.0-17).

REQ-0.35.0-17-03: every control's delivered span is present in the procedure
served for every position in its ``applies_at``, verbatim.
REQ-0.35.0-17-04: the procedure served through ``--from`` is byte-identical to
the one served for the stage in sequence.
REQ-0.35.0-17-05: a missing, unreadable, empty or altered procedure refuses
stage entry with three-part recovery prose.
REQ-0.35.0-17-06: the stage files are canon under the skill package and the
skill body's digest is the one the inventory pins.

Built under the harbor pilotage of 2026-10-15 after the operator attested the
control inventory ("attest the inventory, keep going with the load cuts").
"""

from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.governance.pipeline_control_inventory import (
    check_delivery,
    load_inventory,
    read_skill_body,
)
from gzkit.pipeline_procedure import (
    STAGE_PROCEDURES,
    ProcedureUnavailable,
    render_pointer,
    resolve_launch_procedures,
    resolve_stage_procedure,
    seed_stage_procedures,
    served_texts,
    stages_for_launch,
)

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = Path(".gzkit/skills/gz-obpi-pipeline/references")


def _seeded_root(tmp: str) -> Path:
    root = Path(tmp)
    seed_stage_procedures(root)
    return root


class TestStagesForLaunch(unittest.TestCase):
    def test_every_entry_visits_stage_one_then_its_own_stages(self):
        self.assertEqual(
            stages_for_launch(None), ["stage1", "stage2", "stage3", "stage4", "stage5"]
        )
        self.assertEqual(stages_for_launch("verify"), ["stage1", "stage3", "stage4", "stage5"])
        self.assertEqual(stages_for_launch("ceremony"), ["stage1", "stage4", "stage5"])
        self.assertEqual(stages_for_launch("sync"), ["stage1", "stage5"])


class TestResolveStageProcedure(unittest.TestCase):
    """REQ-0.35.0-17-05: the resolver fails closed and says why and what to do."""

    def test_resolves_a_seeded_stage_to_its_path_and_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _seeded_root(tmp)
            pointer = resolve_stage_procedure(root, "stage3")
            self.assertEqual(pointer.number, 3)
            self.assertEqual(pointer.path, (REFERENCES / "stage-3-verify.md").as_posix())
            digest = hashlib.sha256((root / pointer.path).read_bytes()).hexdigest()
            self.assertEqual(pointer.sha256, digest)
            line = render_pointer(pointer)
            self.assertIn("Stage 3 procedure:", line)
            self.assertIn(pointer.path, line)
            self.assertIn(pointer.sha256, line)

    def test_missing_file_refuses_with_three_part_prose(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _seeded_root(tmp)
            (root / REFERENCES / "stage-2-implement.md").unlink()
            with self.assertRaises(ProcedureUnavailable) as ctx:
                resolve_stage_procedure(root, "stage2")
            # A full launch visits Stage 2, so the launch-level resolver refuses too;
            # a sync-only launch does not visit it and resolves.
            with self.assertRaises(ProcedureUnavailable):
                resolve_launch_procedures(root, None)
            self.assertEqual(list(resolve_launch_procedures(root, "sync")), ["stage1", "stage5"])
            message = str(ctx.exception)
            self.assertIn("stage-2-implement.md", message)
            self.assertIn("missing", message)
            self.assertIn("WHY:", message)
            self.assertIn("OBPI-0.35.0-17", message)
            self.assertIn("NEXT STEP:", message)
            self.assertIn("gz agent sync control-surfaces", message)

    def test_unreadable_file_refuses_and_names_the_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _seeded_root(tmp)
            with (
                patch.object(Path, "read_bytes", side_effect=OSError("device gone")),
                self.assertRaises(ProcedureUnavailable) as ctx,
            ):
                resolve_stage_procedure(root, "stage1")
            message = str(ctx.exception)
            self.assertIn("unreadable", message)
            self.assertIn("device gone", message)
            self.assertIn("NEXT STEP:", message)

    def test_empty_file_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _seeded_root(tmp)
            (root / REFERENCES / "stage-5-sync-and-account.md").write_text("", encoding="utf-8")
            with self.assertRaises(ProcedureUnavailable) as ctx:
                resolve_stage_procedure(root, "stage5")
            self.assertIn("empty", str(ctx.exception))

    def test_altered_bytes_refuse_with_both_digests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _seeded_root(tmp)
            path = root / REFERENCES / "stage-4-present-evidence.md"
            path.write_text(path.read_text(encoding="utf-8") + "\nextra\n", encoding="utf-8")
            with self.assertRaises(ProcedureUnavailable) as ctx:
                resolve_stage_procedure(root, "stage4")
            message = str(ctx.exception)
            expected = next(p.sha256 for p in STAGE_PROCEDURES if p.key == "stage4")
            self.assertIn(expected, message)
            self.assertIn(hashlib.sha256(path.read_bytes()).hexdigest(), message)

    def test_unknown_stage_key_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _seeded_root(tmp)
            with self.assertRaises(ProcedureUnavailable):
                resolve_stage_procedure(root, "stage9")

    def test_from_entry_serves_the_same_bytes_as_the_sequence(self):
        """REQ-0.35.0-17-04: one file per stage, so --from and sequence agree byte for byte."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _seeded_root(tmp)
            in_sequence = resolve_launch_procedures(root, None)
            self.assertEqual(list(in_sequence), stages_for_launch(None))
            for entry in ("verify", "ceremony", "sync"):
                for key, pointer in resolve_launch_procedures(root, entry).items():
                    self.assertEqual(pointer, in_sequence[key])


class TestServedProceduresInThisRepository(unittest.TestCase):
    """REQ-0.35.0-17-03 and -06 on the real tree."""

    def test_every_control_is_delivered_at_every_position_it_applies_at(self):
        inventory = load_inventory(ROOT)
        served = served_texts(ROOT)
        served["invocation"] = read_skill_body(ROOT, inventory)
        violations = check_delivery(inventory, served)
        self.assertEqual(violations, [], "\n".join(f"{v.kind} {v.where}" for v in violations[:12]))

    def test_pinned_digests_match_the_canonical_files(self):
        for procedure in STAGE_PROCEDURES:
            path = ROOT / REFERENCES / procedure.filename
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                procedure.sha256,
                f"{procedure.filename} differs from the pin the runtime expects",
            )

    def test_seeding_reproduces_the_canonical_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = seed_stage_procedures(root)
            self.assertEqual(
                [path.relative_to(root).as_posix() for path in written],
                [(REFERENCES / procedure.filename).as_posix() for procedure in STAGE_PROCEDURES],
            )
            for procedure in STAGE_PROCEDURES:
                seeded = (root / REFERENCES / procedure.filename).read_bytes()
                canonical = (ROOT / REFERENCES / procedure.filename).read_bytes()
                self.assertEqual(seeded, canonical, procedure.filename)


if __name__ == "__main__":
    unittest.main()
