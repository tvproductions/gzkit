"""GHI #1155 — the back-pointer match (GHI #932) and reverse arm (GHI #933) carry claims.

The validator once discharged every pointer into a destination with any one
``lifted-from`` comment, and implemented only one direction of Invariant 3. These tests
weaken it the way those defects did, and the ways their repairs could regress, and require
the matching control to fail.
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
    REVERSE_ADMIT_CLAIM_ID,
    REVERSE_REFUSE_CLAIM_ID,
    orphan_shape_population,
    unmatched_shape_population,
)

_GATE = "gzkit.governance.trust_audits.pointer_integrity:validate_pointer_integrity"
_REAL_VALIDATE_POINTER = gate._validate_pointer


_REAL_CHECK_ONE = gate._check_one_back_pointer
_REAL_VALIDATE_BACK = gate._validate_back_pointer


def _outcomes() -> dict[str, str]:
    wanted = {REFUSE_CLAIM_ID, ADMIT_CLAIM_ID, REVERSE_REFUSE_CLAIM_ID, REVERSE_ADMIT_CLAIM_ID}
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
        for claim_id in (
            REFUSE_CLAIM_ID,
            ADMIT_CLAIM_ID,
            REVERSE_REFUSE_CLAIM_ID,
            REVERSE_ADMIT_CLAIM_ID,
        ):
            self.assertIn(_GATE, records[claim_id].gate_targets)
        self.assertEqual(
            _outcomes(),
            {
                REFUSE_CLAIM_ID: "PASS",
                ADMIT_CLAIM_ID: "PASS",
                REVERSE_REFUSE_CLAIM_ID: "PASS",
                REVERSE_ADMIT_CLAIM_ID: "PASS",
            },
        )

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

    def test_the_reverse_population_is_every_way_a_declaration_lacks_a_live_lift(self):
        self.assertEqual(
            set(orphan_shape_population()),
            {
                "origin-missing",
                "anchor-unresolved",
                "origin-carries-no-link",
                "link-to-other-anchor",
                "link-to-other-file",
                "placeholder-lookalike",
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


def _anchor_never_checked(project_root, dest_path, dest_rel, lineno, declaration, dest_slugs):
    """A reverse arm that stops asking whether the anchor resolves in the declaring page."""
    anchor = declaration.partition("#")[2]
    return _REAL_CHECK_ONE(
        project_root, dest_path, dest_rel, lineno, declaration, dest_slugs | {anchor}
    )


def _placeholder_by_shape(project_root, dest_path, dest_rel, lineno, declaration, dest_slugs):
    """An exclusion by shape: anything in angle brackets is a placeholder."""
    if declaration.startswith("<"):
        return []
    return _REAL_VALIDATE_BACK(project_root, dest_path, dest_rel, lineno, declaration, dest_slugs)


def _orphan(message: str) -> list[ValidationError]:
    return [ValidationError(type="pointer_anchors", artifact="x", message=message)]


class TestReverseArmControlsFailWhenTheArmIsWeakened(unittest.TestCase):
    def test_the_933_hole_no_reverse_arm_fails_the_refuse_control(self):
        with mock.patch.object(gate, "_check_back_pointers", lambda project_root: []):
            self.assertEqual(_outcomes()[REVERSE_REFUSE_CLAIM_ID], "FACADE")

    def test_an_origin_that_always_points_back_fails_the_refuse_control(self):
        with mock.patch.object(gate, "_origin_points_at", lambda *args: True):
            self.assertEqual(_outcomes()[REVERSE_REFUSE_CLAIM_ID], "FACADE")

    def test_never_checking_the_anchor_fails_the_refuse_control(self):
        with mock.patch.object(gate, "_check_one_back_pointer", _anchor_never_checked):
            self.assertEqual(_outcomes()[REVERSE_REFUSE_CLAIM_ID], "FACADE")

    def test_excluding_the_placeholder_by_shape_fails_the_refuse_control(self):
        with mock.patch.object(gate, "_validate_back_pointer", _placeholder_by_shape):
            self.assertEqual(_outcomes()[REVERSE_REFUSE_CLAIM_ID], "FACADE")

    def test_an_always_orphaning_arm_fails_the_admit_control(self):
        always = lambda project_root: _orphan("Orphaned back-pointer: x")  # noqa: E731
        with mock.patch.object(gate, "_check_back_pointers", always):
            self.assertEqual(_outcomes()[REVERSE_ADMIT_CLAIM_ID], "FACADE")

    def test_an_arm_that_stops_excluding_the_placeholder_fails_the_admit_control(self):
        with mock.patch.object(gate, "_PLACEHOLDER_DECLARATION", "<never>"):
            self.assertEqual(_outcomes()[REVERSE_ADMIT_CLAIM_ID], "FACADE")

    def test_a_refusal_for_another_reason_does_not_discharge_the_refuse_control(self):
        other = lambda project_root: _orphan("Pointer anchor unresolved: x")  # noqa: E731
        with mock.patch.object(gate, "_check_back_pointers", other):
            self.assertEqual(_outcomes()[REVERSE_REFUSE_CLAIM_ID], "FACADE")


if __name__ == "__main__":
    unittest.main()
