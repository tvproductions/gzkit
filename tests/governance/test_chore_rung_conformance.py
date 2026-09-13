"""A chore's workflow may not reach past its declared rung (GHI #999 step 3).

`rung` is a chore's writing license: where it stops. A `CHORE.md` that declares
itself audit-only and then remediates contradicts that license, and nothing
caught it — `repository-structure-normalization` says "Audit only; document
deviations before making changes" and its step 3 is Remediate.

Operator ruling 2026-09-13, verbatim "Declared step stages (Recommended)": each
Workflow step heading declares a stage from the rung vocabulary, and a step may
not exceed the chore's rung. A declaration is compared with a declaration; the
check never infers posture from prose, which the design record measured
misfiling four chores (`docs/governance/chore-class-system.md` § The measured
state).
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_chore_rung_conformance

_DECLARATION = {
    "class": "conformance",
    "idempotent": True,
    "staleness": {"signal": "content-delta", "graceDays": 7},
    "remediation": {"category": "vendor_fix", "details": "The chore repairs the subject."},
    "nonAuthority": "Never edits canon.",
    "governingRule": "none",
}


def _tree(root: Path, workflow: str, *, rung: str | None) -> None:
    """Write one registered chore; ``rung=None`` leaves it undeclared."""
    chores = root / ".gzkit" / "chores"
    (chores / "demo").mkdir(parents=True)
    (root / ".gzkit.json").write_text("{}", encoding="utf-8")
    entry: dict[str, object] = {"slug": "demo", "path": ".gzkit/chores/demo", "lane": "lite"}
    if rung is not None:
        entry.update(_DECLARATION, rung=rung)
    (chores / "registry.json").write_text(json.dumps({"chores": [entry]}), encoding="utf-8")
    (chores / "demo" / "CHORE.md").write_text(
        "# Demo\n\n## Workflow\n\n" + workflow + "\n## Acceptance Criteria\n\nSee JSON.\n",
        encoding="utf-8",
    )


def _audit(workflow: str, *, rung: str | None) -> list:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _tree(root, workflow, rung=rung)
        return audit_chore_rung_conformance(root)


class TestLiveTree(unittest.TestCase):
    def test_no_declared_chore_reaches_past_its_rung(self) -> None:
        # Binds each chore from the moment it is declared (step 5); until then
        # an undeclared chore has no rung to contradict.
        root = Path(__file__).resolve().parents[2]
        errors = audit_chore_rung_conformance(root)
        self.assertEqual(errors, [], "\n".join(f"{e.artifact}: {e.message}" for e in errors))


class TestStageAgainstRung(unittest.TestCase):
    def test_an_audit_only_chore_that_remediates_fails(self) -> None:
        # The repository-structure-normalization shape, stages declared honestly.
        workflow = (
            "### 1. Baseline — observe\n### 2. Analyze — observe\n"
            "### 3. Remediate — repair\n### 4. Validate — observe\n"
        )
        errors = _audit(workflow, rung="observe")
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("3. Remediate", errors[0].message)
        self.assertIn("observe", errors[0].message)

    def test_stages_at_or_below_the_rung_pass(self) -> None:
        workflow = "### 1. Scan — observe\n### 2. Plan — propose\n### 3. Fix — repair\n"
        self.assertEqual(_audit(workflow, rung="repair"), [])

    def test_the_ladder_is_ordered(self) -> None:
        # Each rung admits every stage below it and refuses every stage above it.
        ladder = ("observe", "propose", "repair", "operator-only-repair")
        for r_index, rung in enumerate(ladder):
            for s_index, stage in enumerate(ladder):
                with self.subTest(rung=rung, stage=stage):
                    errors = _audit(f"### 1. Step — {stage}\n", rung=rung)
                    self.assertEqual(bool(errors), s_index > r_index, errors)


class TestUndeclaredStages(unittest.TestCase):
    def test_a_step_without_a_stage_fails_on_a_declared_chore(self) -> None:
        errors = _audit("### 1. Scan — observe\n### 2. Tidy up\n", rung="propose")
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("2. Tidy up", errors[0].message)
        # output-contract: a missing stage and an unknown stage need different
        # repairs, so the finding must name the one that applies (guardrail prose).
        self.assertIn("declares no stage", errors[0].message)
        self.assertNotIn("None", errors[0].message)

    def test_a_stage_outside_the_vocabulary_fails(self) -> None:
        errors = _audit("### 1. Scan — inspect\n", rung="repair")
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("inspect", errors[0].message)

    def test_a_declared_chore_with_no_workflow_steps_fails(self) -> None:
        # No steps is not conformance by default: there is nothing to hold.
        errors = _audit("Run the scan and report.\n", rung="observe")
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("Workflow", errors[0].message)

    def test_an_undeclared_chore_is_not_judged(self) -> None:
        # Rollout ruling "Warn, flip at step 5": absence is announced elsewhere.
        self.assertEqual(_audit("### 1. Remediate\n", rung=None), [])


if __name__ == "__main__":
    unittest.main()
