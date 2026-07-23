"""Tests for gz validate --req-kind-discipline (OBPI-0.0.59-02).

Covers:
    REQ-0.0.59-02-01 — mixed-state brief (tagged + untagged) → exits 3
    REQ-0.0.59-02-02 — per-kind proof-citation gap detection
    REQ-0.0.59-02-03 — ReqKind/ProofChannel/ReqClassification Pydantic models
    REQ-0.0.59-02-04 — step in _build_check_steps()
    REQ-0.0.59-02-05 — gz-obpi-specify skill has REQ Kind Authoring section
    REQ-0.0.59-02-06 — docs/governance/req-scope-discipline.md has Brief-time validation section
"""

from __future__ import annotations

import pathlib
import tempfile
import unittest

from gzkit.traceability import covers


class TestReqKindModels(unittest.TestCase):
    """REQ-0.0.59-02-03: ReqKind/ProofChannel/ReqClassification Pydantic models."""

    @covers("REQ-0.0.59-02-03")
    def test_req_kind_enum_values(self) -> None:
        from gzkit.req_kind import ReqKind

        self.assertEqual(ReqKind.BEHAVIOR, "BEHAVIOR")
        self.assertEqual(ReqKind.SUPPORT, "SUPPORT")
        self.assertEqual(ReqKind.STRUCTURAL_FENCE, "STRUCTURAL-FENCE")

    @covers("REQ-0.0.59-02-03")
    def test_proof_channel_enum_values(self) -> None:
        from gzkit.req_kind import ProofChannel

        self.assertEqual(ProofChannel.TEST_COVERS, "TEST_COVERS")
        self.assertEqual(ProofChannel.LEDGER_PLUS_VALIDATOR, "LEDGER_PLUS_VALIDATOR")
        self.assertEqual(ProofChannel.PARENT_ADR_INVARIANT, "PARENT_ADR_INVARIANT")

    @covers("REQ-0.0.59-02-03")
    def test_req_classification_frozen(self) -> None:
        from pydantic import ValidationError

        from gzkit.req_kind import ProofChannel, ReqClassification, ReqKind

        r = ReqClassification(
            req_id="REQ-0.0.59-02-01",
            kind=ReqKind.BEHAVIOR,
            proof_channel=ProofChannel.TEST_COVERS,
            proof_status="pass",
        )
        # Pydantic v2 frozen models raise ValidationError on direct assignment
        with self.assertRaises((TypeError, ValidationError)):
            r.req_id = "other"  # type: ignore

    @covers("REQ-0.0.59-02-03")
    def test_req_classification_extra_forbidden(self) -> None:
        from pydantic import ValidationError

        from gzkit.req_kind import ProofChannel, ReqClassification, ReqKind

        with self.assertRaises(ValidationError):
            ReqClassification(
                req_id="REQ-0.0.59-02-01",
                kind=ReqKind.BEHAVIOR,
                proof_channel=ProofChannel.TEST_COVERS,
                proof_status="pass",
                unknown_field="forbidden",
            )

    @covers("REQ-0.0.59-02-03")
    def test_kind_to_channel_mapping(self) -> None:
        from gzkit.req_kind import ProofChannel, ReqClassification, ReqKind

        self.assertEqual(
            ReqClassification.kind_to_channel(ReqKind.BEHAVIOR),
            ProofChannel.TEST_COVERS,
        )
        self.assertEqual(
            ReqClassification.kind_to_channel(ReqKind.SUPPORT),
            ProofChannel.LEDGER_PLUS_VALIDATOR,
        )
        self.assertEqual(
            ReqClassification.kind_to_channel(ReqKind.STRUCTURAL_FENCE),
            ProofChannel.PARENT_ADR_INVARIANT,
        )


class TestReqKindDisciplineValidator(unittest.TestCase):
    """REQ-0.0.59-02-01 and -02: validator behavior for tagged/untagged REQs."""

    def _adr_dir(self, tmpdir: pathlib.Path) -> pathlib.Path:
        adr_dir = tmpdir / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.59-test"
        adr_dir.mkdir(parents=True, exist_ok=True)
        return adr_dir

    def _obpis_dir(self, tmpdir: pathlib.Path) -> pathlib.Path:
        obpis = self._adr_dir(tmpdir) / "obpis"
        obpis.mkdir(parents=True, exist_ok=True)
        return obpis

    def _make_brief(
        self, tmpdir: pathlib.Path, content: str, filename: str = "OBPI-0.0.59-99-test.md"
    ) -> pathlib.Path:
        brief = self._obpis_dir(tmpdir) / filename
        brief.write_text(content, encoding="utf-8")
        return brief

    def _make_parent_adr(
        self, tmpdir: pathlib.Path, with_boundary_invariants: bool = False
    ) -> pathlib.Path:
        content = "# ADR-0.0.59-test\n\n## Intent\n\nTest ADR.\n"
        if with_boundary_invariants:
            content += "\n## Boundary Invariants\n\n- Invariant 1: test holds.\n"
        adr = self._adr_dir(tmpdir) / "ADR-0.0.59-test.md"
        adr.write_text(content, encoding="utf-8")
        return adr

    @covers("REQ-0.0.59-02-01")
    def test_mixed_state_fails_with_untagged_req_ids_reported(self) -> None:
        """Mixed-state brief (tagged + untagged) exits 3 and reports untagged IDs."""
        from gzkit.commands.validate_cmd import _validate_req_kind_discipline

        content = (
            "---\nid: OBPI-0.0.59-99-test\nparent: ADR-0.0.59-test\n---\n\n"
            "## Allowed Paths\n\n- tests/governance/test_req.py\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] REQ-0.0.59-99-01 [BEHAVIOR]: first req is tagged\n"
            "- [ ] REQ-0.0.59-99-02: second req is NOT tagged\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = pathlib.Path(tmp)
            self._make_brief(tmpdir, content)
            errors = _validate_req_kind_discipline(tmpdir)

        untagged_errors = [e for e in errors if "REQ-0.0.59-99-02" in e.message]
        self.assertTrue(len(untagged_errors) >= 1, "Should report untagged REQ ID")

    @covers("REQ-0.0.59-02-01")
    def test_all_untagged_brief_passes_in_legacy_mode(self) -> None:
        """All-untagged brief (no kind tags) passes — legacy briefs are grandfathered."""
        from gzkit.commands.validate_cmd import _validate_req_kind_discipline

        content = (
            "---\nid: OBPI-0.0.59-99-test\nparent: ADR-0.0.59-test\n---\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] REQ-0.0.59-99-01: untagged\n"
            "- [ ] REQ-0.0.59-99-02: also untagged\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = pathlib.Path(tmp)
            self._make_brief(tmpdir, content)
            errors = _validate_req_kind_discipline(tmpdir)

        self.assertEqual([], errors, "All-untagged brief should pass in legacy mode")

    @covers("REQ-0.0.59-02-02")
    def test_behavior_req_fails_when_no_tests_in_allowed_paths(self) -> None:
        """BEHAVIOR REQ fails if tests/** absent from Allowed Paths."""
        from gzkit.commands.validate_cmd import _validate_req_kind_discipline

        content = (
            "---\nid: OBPI-0.0.59-99-test\nparent: ADR-0.0.59-test\n---\n\n"
            "## Allowed Paths\n\n- src/gzkit/something.py\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] REQ-0.0.59-99-01 [BEHAVIOR]: validator rejects missing tests path\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = pathlib.Path(tmp)
            self._make_brief(tmpdir, content)
            errors = _validate_req_kind_discipline(tmpdir)

        behavior_errors = [e for e in errors if "BEHAVIOR" in e.message and "tests/**" in e.message]
        self.assertTrue(
            len(behavior_errors) >= 1, "Should report missing tests/** for BEHAVIOR REQ"
        )

    @covers("REQ-0.0.59-02-02")
    def test_behavior_req_passes_when_tests_in_allowed_paths(self) -> None:
        """BEHAVIOR REQ passes when tests/** present in Allowed Paths."""
        from gzkit.commands.validate_cmd import _validate_req_kind_discipline

        content = (
            "---\nid: OBPI-0.0.59-99-test\nparent: ADR-0.0.59-test\n---\n\n"
            "## Allowed Paths\n\n- tests/governance/test_something.py\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] REQ-0.0.59-99-01 [BEHAVIOR]: validator accepts tests path\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = pathlib.Path(tmp)
            self._make_brief(tmpdir, content)
            errors = _validate_req_kind_discipline(tmpdir)

        behavior_errors = [e for e in errors if "REQ-0.0.59-99-01" in e.message]
        self.assertEqual([], behavior_errors, "BEHAVIOR REQ with tests/** should have no errors")

    @covers("REQ-0.0.59-02-02")
    def test_support_req_fails_when_no_citation(self) -> None:
        """SUPPORT REQ fails when no gz validate scope or ledger event keyword in text."""
        from gzkit.commands.validate_cmd import _validate_req_kind_discipline

        content = (
            "---\nid: OBPI-0.0.59-99-test\nparent: ADR-0.0.59-test\n---\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] REQ-0.0.59-99-01 [SUPPORT]: rule file exists and is correct\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = pathlib.Path(tmp)
            self._make_brief(tmpdir, content)
            errors = _validate_req_kind_discipline(tmpdir)

        support_errors = [
            e for e in errors if "SUPPORT" in e.message and "REQ-0.0.59-99-01" in e.message
        ]
        self.assertTrue(len(support_errors) >= 1, "Should report missing citation for SUPPORT REQ")

    @covers("REQ-0.0.59-02-02")
    def test_support_req_passes_with_validator_and_ledger_citation(self) -> None:
        """SUPPORT REQ passes when gz validate scope + ledger event type present."""
        from gzkit.commands.validate_cmd import _validate_req_kind_discipline

        req_line = (
            "- [ ] REQ-0.0.59-99-01 [SUPPORT]: rule file"
            " — gz validate --documents + artifact_edited"
        )
        content = (
            "---\nid: OBPI-0.0.59-99-test\nparent: ADR-0.0.59-test\n---\n\n"
            f"## Acceptance Criteria\n\n{req_line}\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = pathlib.Path(tmp)
            self._make_brief(tmpdir, content)
            errors = _validate_req_kind_discipline(tmpdir)

        support_errors = [e for e in errors if "REQ-0.0.59-99-01" in e.message]
        self.assertEqual([], support_errors, "SUPPORT REQ with citations should have no errors")

    @covers("REQ-0.0.59-02-02")
    def test_structural_fence_req_fails_when_parent_adr_lacks_boundary_invariants(self) -> None:
        """STRUCTURAL-FENCE REQ fails when parent ADR has no ## Boundary Invariants."""
        from gzkit.commands.validate_cmd import _validate_req_kind_discipline

        content = (
            "---\nid: OBPI-0.0.59-99-test\nparent: ADR-0.0.59-test\n---\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] REQ-0.0.59-99-01 [STRUCTURAL-FENCE]: boundary invariant holds\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = pathlib.Path(tmp)
            self._make_parent_adr(tmpdir, with_boundary_invariants=False)
            self._make_brief(tmpdir, content)
            errors = _validate_req_kind_discipline(tmpdir)

        fence_errors = [
            e
            for e in errors
            if "STRUCTURAL-FENCE" in e.message or "Boundary Invariants" in e.message
        ]
        self.assertTrue(len(fence_errors) >= 1, "Should report missing Boundary Invariants")

    @covers("REQ-0.0.59-02-02")
    def test_fully_clean_brief_has_no_errors(self) -> None:
        """A brief with properly tagged REQs and all citations passes the validator."""
        from gzkit.commands.validate_cmd import _validate_req_kind_discipline

        content = (
            "---\nid: OBPI-0.0.59-99-test\nparent: ADR-0.0.59-test\n---\n\n"
            "## Allowed Paths\n\n- tests/governance/test_req.py\n\n"
            "## Acceptance Criteria\n\n"
            "- [ ] REQ-0.0.59-99-01 [BEHAVIOR]: code behavior check\n"
            "- [ ] REQ-0.0.59-99-02 [SUPPORT]:"
            " docs updated — gz validate --documents + artifact_edited event\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = pathlib.Path(tmp)
            self._make_brief(tmpdir, content)
            errors = _validate_req_kind_discipline(tmpdir)

        self.assertEqual([], errors, "Clean brief with all citations should have no errors")


class TestReqKindDisciplineInGzCheck(unittest.TestCase):
    """REQ-0.0.59-02-04: step wired into gz check pipeline."""

    @covers("REQ-0.0.59-02-04")
    def test_req_kind_discipline_step_in_build_check_steps(self) -> None:
        """run_req_kind_discipline_audit is in the _build_check_steps roster."""
        from gzkit.commands.quality import _build_check_steps

        step_names = [name.lower() for name, _ in _build_check_steps()]
        self.assertTrue(
            any("req kind" in name or "req_kind" in name for name in step_names),
            f"Expected 'REQ kind' step in _build_check_steps. Got: {step_names}",
        )


class TestReqKindSpecifySkillSection(unittest.TestCase):
    """REQ-0.0.59-02-05: gz-obpi-specify skill has REQ Kind Authoring section."""

    @covers("REQ-0.0.59-02-05")
    def test_obpi_specify_skill_has_req_kind_authoring_section(self) -> None:
        """The gz-obpi-specify canonical SKILL.md has a REQ Kind Authoring section."""
        skill_path = pathlib.Path(".gzkit/skills/gz-obpi-specify/SKILL.md")
        self.assertTrue(skill_path.exists(), f"Skill file missing: {skill_path}")
        content = skill_path.read_text(encoding="utf-8")
        self.assertIn("REQ Kind", content, "Skill should contain REQ Kind Authoring section")
        self.assertIn("[BEHAVIOR]", content, "Skill should document [BEHAVIOR] tag syntax")
        self.assertIn("[SUPPORT]", content, "Skill should document [SUPPORT] tag syntax")
        self.assertIn(
            "[STRUCTURAL-FENCE]", content, "Skill should document [STRUCTURAL-FENCE] tag syntax"
        )


class TestReqScopeDisciplineDocsBriefTimeSection(unittest.TestCase):
    """REQ-0.0.59-02-06: req-scope-discipline.md has Brief-time validation section."""
