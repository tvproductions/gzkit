"""GHI #1155 — the back-pointer match (GHI #932) carries load-bearing claims.

The validator once discharged every pointer into a destination with any one
``lifted-from`` comment. These tests weaken it the way that defect did, and the ways its
repair could regress, and require the matching control to fail.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from gzkit.core.validation_rules import ValidationError
from gzkit.enforcement import production_enforcement_registry, run_meta_validator
from gzkit.governance.trust_audits import pointer_integrity as gate
from gzkit.governance.trust_audits.pointer_integrity_claims import (
    ADMIT_CLAIM_ID,
    REFUSE_CLAIM_ID,
    unmatched_shape_population,
)

_GATE = "gzkit.governance.trust_audits.pointer_integrity:validate_pointer_integrity"
_REAL_VALIDATE_POINTER = gate._validate_pointer


def _outcomes() -> dict[str, str]:
    wanted = {REFUSE_CLAIM_ID, ADMIT_CLAIM_ID}
    records = [r for r in production_enforcement_registry() if r.claim_id in wanted]
    result = run_meta_validator(registry=records)
    return {r.claim_id: r.outcome for r in result.claim_results}


def _presence_only(project_root, source_rel, lineno, path_part, anchor):
    """The pre-#932 check: any lifted-from comment in the destination discharges the pointer."""
    dest = Path(os.path.normpath((project_root / source_rel).parent / path_part))
    if "<!-- lifted-from:" in dest.read_text(encoding="utf-8"):
        return []
    return [
        ValidationError(
            type="pointer_anchors",
            artifact=source_rel,
            message=f"Missing back-pointer: referenced by {source_rel}:{lineno}#{anchor}",
        )
    ]


def _source_only(project_root, source_rel, lineno, path_part, anchor):
    """A match that names the source but not the anchor, so another section's comment counts."""
    found = _REAL_VALIDATE_POINTER(project_root, source_rel, lineno, path_part, anchor)
    dest = Path(os.path.normpath((project_root / source_rel).parent / path_part))
    named = any(
        f"lifted-from: {source_rel}" in line
        for line in dest.read_text(encoding="utf-8").splitlines()
    )
    return [] if named else found


class TestBackPointerClaims(unittest.TestCase):
    def test_both_claims_name_the_validator_and_pass(self):
        records = {r.claim_id: r for r in production_enforcement_registry()}
        for claim_id in (REFUSE_CLAIM_ID, ADMIT_CLAIM_ID):
            self.assertIn(_GATE, records[claim_id].gate_targets)
        self.assertEqual(_outcomes(), {REFUSE_CLAIM_ID: "PASS", ADMIT_CLAIM_ID: "PASS"})

    def test_the_population_is_every_way_a_comment_fails_to_name_its_pointer(self):
        self.assertEqual(
            set(unmatched_shape_population()),
            {
                "absent",
                "other-source",
                "other-anchor",
                "file-level",
                "one-comment-for-two-pointers",
            },
        )


class TestControlsFailWhenTheValidatorIsWeakened(unittest.TestCase):
    def test_the_932_presence_test_fails_the_refuse_control(self):
        with mock.patch.object(gate, "_validate_pointer", _presence_only):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_matching_the_source_but_not_the_anchor_fails_the_refuse_control(self):
        with mock.patch.object(gate, "_validate_pointer", _source_only):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_an_always_refuse_validator_fails_the_admit_control(self):
        refusal = [ValidationError(type="pointer_anchors", artifact="x", message="Unmatched")]
        with mock.patch.object(gate, "_validate_pointer", lambda *args: refusal):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")

    def test_a_refusal_for_another_reason_does_not_discharge_the_refuse_control(self):
        # The control names the back-pointer; an unresolved anchor is a different finding.
        other = [
            ValidationError(
                type="pointer_anchors", artifact="x", message="Pointer anchor unresolved: AGENTS.md"
            )
        ]
        with mock.patch.object(gate, "_validate_pointer", lambda *args: other):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")


if __name__ == "__main__":
    unittest.main()
