"""Tests for the gz plan-audit CLI command."""

from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from gzkit.commands.plan_audit_cmd import (
    _derive_adr_id,
    _extract_allowed_paths,
    _extract_plan_paths,
    _find_adr_dir,
    _find_brief,
    _find_plan_file,
    _path_within_allowed,
    _paths_overlap,
    _scan_sibling_adr_collisions,
    plan_audit_cmd,
)


class TestDeriveAdrId(unittest.TestCase):
    """Test OBPI-to-ADR derivation."""

    def test_standard_obpi(self) -> None:
        self.assertEqual(_derive_adr_id("OBPI-0.1.0-01"), "ADR-0.1.0")

    def test_obpi_with_suffix(self) -> None:
        self.assertEqual(_derive_adr_id("OBPI-0.10.0-05"), "ADR-0.10.0")

    def test_invalid_prefix(self) -> None:
        self.assertIsNone(_derive_adr_id("ADR-0.1.0"))

    def test_no_item_number(self) -> None:
        # "OBPI-0.1.0" has no trailing -NN, derivation should fail cleanly
        self.assertIsNone(_derive_adr_id("OBPI-0.1.0"))

    def test_full_slug_obpi(self) -> None:
        """@covers GHI #187 — full slug must still resolve to the same ADR."""
        self.assertEqual(
            _derive_adr_id("OBPI-0.0.16-05-status-vocab-mapping"),
            "ADR-0.0.16",
        )

    def test_full_slug_with_multi_segment_tail(self) -> None:
        """@covers GHI #187 — multi-hyphen slug tails do not leak into the ADR ID."""
        self.assertEqual(
            _derive_adr_id("OBPI-0.14.0-03-implementer-agent-persona"),
            "ADR-0.14.0",
        )


class TestCanonicalizeObpiId(unittest.TestCase):
    """@covers GHI #187 — receipt writer must canonicalize short-form input."""

    def test_canonicalization_falls_back_to_input_when_ungraphable(self) -> None:
        """In a temp project with no ledger, canonicalization returns input unchanged."""
        from gzkit.commands.plan_audit_cmd import _canonicalize_obpi_id

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # No .gzkit.json, no ledger — helper must not raise.
            result = _canonicalize_obpi_id(root, "OBPI-0.1.0-01")
            self.assertEqual(result, "OBPI-0.1.0-01")

    def test_receipt_uses_canonical_full_slug_when_graph_resolves(self) -> None:
        """@covers GHI #187 — canonicalizer returns full slug when graph resolves."""
        from gzkit.commands.plan_audit_cmd import _canonicalize_obpi_id

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit.json").write_text("{}", encoding="utf-8")

            fake_canonical = "OBPI-0.1.0-01-scaffold"

            def _fake_resolve_obpi(
                project_root: Path,
                config: object,
                ledger: object,
                obpi: str,
            ) -> tuple[str, None]:
                return fake_canonical, None

            with patch(
                "gzkit.commands.common.resolve_obpi",
                new=_fake_resolve_obpi,
            ):
                result = _canonicalize_obpi_id(root, "OBPI-0.1.0-01")

            self.assertEqual(result, fake_canonical)

    def test_plan_audit_cmd_writes_canonical_obpi_id_to_receipt(self) -> None:
        """@covers GHI #187 — the receipt's obpi_id field is the full slug."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.1.0-scaffold"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            brief = obpis_dir / "OBPI-0.1.0-01-scaffold.md"
            brief.write_text("# Brief\n", encoding="utf-8")

            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            plan = plans_dir / "plan.md"
            plan.write_text("# Plan for OBPI-0.1.0-01-scaffold\n", encoding="utf-8")

            (root / ".gzkit.json").write_text("{}", encoding="utf-8")

            fake_canonical = "OBPI-0.1.0-01-scaffold"

            def _fake_resolve_obpi(
                project_root: Path,
                config: object,
                ledger: object,
                obpi: str,
            ) -> tuple[str, None]:
                return fake_canonical, None

            quiet_console = Console(file=StringIO(), quiet=True)
            with (
                patch("gzkit.commands.plan_audit_cmd.console", quiet_console),
                patch("gzkit.commands.common.get_project_root", return_value=root),
                patch("gzkit.commands.common.ensure_initialized"),
                patch("gzkit.commands.common.resolve_obpi", new=_fake_resolve_obpi),
            ):
                plan_audit_cmd(obpi_id="OBPI-0.1.0-01", as_json=False)

            receipt_path = plans_dir / f".plan-audit-receipt-{fake_canonical}.json"
            self.assertTrue(
                receipt_path.exists(),
                f"receipt file should be written at the canonical slug path: {receipt_path}",
            )
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(
                receipt["obpi_id"],
                fake_canonical,
                "receipt obpi_id field must be the full slug — this is the "
                "invariant that prevents the pipeline-gate short-vs-full mismatch",
            )


class TestFindAdrDir(unittest.TestCase):
    """Test ADR directory discovery."""

    def test_finds_matching_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.1.0-my-feature"
            adr_dir.mkdir(parents=True)
            result = _find_adr_dir(root, "ADR-0.1.0")
            self.assertIsNotNone(result)
            self.assertEqual(result, adr_dir)

    def test_returns_none_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "design" / "adr" / "foundation").mkdir(parents=True)
            result = _find_adr_dir(root, "ADR-0.99.0")
            self.assertIsNone(result)

    def test_returns_none_when_no_adr_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = _find_adr_dir(root, "ADR-0.1.0")
            self.assertIsNone(result)


class TestFindBrief(unittest.TestCase):
    """Test OBPI brief file discovery."""

    def test_finds_matching_brief(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir()
            brief = obpis_dir / "OBPI-0.1.0-01-my-feature.md"
            brief.write_text("# Brief", encoding="utf-8")
            result = _find_brief(adr_dir, "OBPI-0.1.0-01")
            self.assertIsNotNone(result)
            self.assertEqual(result, brief)

    def test_returns_none_when_no_obpis_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            result = _find_brief(adr_dir, "OBPI-0.1.0-01")
            self.assertIsNone(result)


class TestFindPlanFile(unittest.TestCase):
    """Test plan file discovery."""

    def test_finds_plan_with_obpi_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plans_dir = Path(tmp)
            plan = plans_dir / "my-plan.md"
            plan.write_text("# Plan for OBPI-0.1.0-01\nDo things.", encoding="utf-8")
            result = _find_plan_file(plans_dir, "OBPI-0.1.0-01")
            self.assertIsNotNone(result)
            self.assertEqual(result, plan)

    def test_returns_none_when_no_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plans_dir = Path(tmp)
            plan = plans_dir / "other.md"
            plan.write_text("# Plan for something else", encoding="utf-8")
            result = _find_plan_file(plans_dir, "OBPI-0.1.0-01")
            self.assertIsNone(result)

    def test_returns_none_when_dir_missing(self) -> None:
        result = _find_plan_file(Path("/nonexistent/plans"), "OBPI-0.1.0-01")
        self.assertIsNone(result)

    def test_skips_dotfiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plans_dir = Path(tmp)
            dotfile = plans_dir / ".hidden-plan.md"
            dotfile.write_text("# Plan for OBPI-0.1.0-01", encoding="utf-8")
            result = _find_plan_file(plans_dir, "OBPI-0.1.0-01")
            self.assertIsNone(result)


class TestExtractAllowedPaths(unittest.TestCase):
    """Test allowed paths extraction from brief."""

    def test_extracts_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(
                "## Allowed Paths\n\n- `src/gzkit/commands/`\n- `tests/`\n\n## Other\n",
                encoding="utf-8",
            )
            result = _extract_allowed_paths(brief)
            self.assertEqual(result, ["src/gzkit/commands/", "tests/"])

    def test_returns_none_when_no_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text("## Something Else\n\n- path\n", encoding="utf-8")
            result = _extract_allowed_paths(brief)
            self.assertIsNone(result)

    def test_uppercase_heading(self) -> None:
        """@covers GHI #152 — the majority of real briefs use ## ALLOWED PATHS."""
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(
                "## ALLOWED PATHS\n\n- `src/gzkit/arb/`\n- `tests/`\n\n## Other\n",
                encoding="utf-8",
            )
            result = _extract_allowed_paths(brief)
            self.assertEqual(result, ["src/gzkit/arb/", "tests/"])

    def test_heading_with_lane_suffix(self) -> None:
        """@covers GHI #152 — ## ALLOWED PATHS (Heavy) variants exist in the tree."""
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(
                "## ALLOWED PATHS (Foundational)\n\n- `src/gzkit/`\n\n## Other\n",
                encoding="utf-8",
            )
            result = _extract_allowed_paths(brief)
            self.assertEqual(result, ["src/gzkit/"])

    def test_strips_em_dash_commentary(self) -> None:
        """@covers GHI #152 — bullets commonly carry ` — comment` trailers."""
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(
                "## ALLOWED PATHS\n\n"
                "- `src/gzkit/arb/` — target for absorbed modules\n"
                "- `tests/` — tests for absorbed modules\n",
                encoding="utf-8",
            )
            result = _extract_allowed_paths(brief)
            self.assertEqual(result, ["src/gzkit/arb/", "tests/"])


class TestPathsOverlap(unittest.TestCase):
    """@covers GHI #152 — directory-prefix overlap semantics for scope collision."""

    def test_equal_paths_overlap(self) -> None:
        self.assertTrue(_paths_overlap("src/gzkit/arb/", "src/gzkit/arb/"))

    def test_trailing_slash_variance_overlaps(self) -> None:
        self.assertTrue(_paths_overlap("src/gzkit/arb/", "src/gzkit/arb"))

    def test_parent_contains_child(self) -> None:
        self.assertTrue(_paths_overlap("src/gzkit/arb/", "src/gzkit/arb/validator.py"))

    def test_child_within_parent(self) -> None:
        self.assertTrue(_paths_overlap("src/gzkit/arb/validator.py", "src/gzkit/arb/"))

    def test_sibling_paths_do_not_overlap(self) -> None:
        self.assertFalse(_paths_overlap("src/gzkit/arb/", "src/gzkit/cli/"))

    def test_spurious_prefix_does_not_overlap(self) -> None:
        # "src/gzkit/a" must not match "src/gzkit/arb" — separator matters.
        self.assertFalse(_paths_overlap("src/gzkit/a", "src/gzkit/arb/"))


class TestScanSiblingAdrCollisions(unittest.TestCase):
    """@covers GHI #152 — sibling-ADR scope-collision detection."""

    def _mk_brief(self, path: Path, allowed: list[str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        body = ["# Brief", "", "## ALLOWED PATHS", ""]
        body.extend(f"- `{p}`" for p in allowed)
        body.append("")
        path.write_text("\n".join(body), encoding="utf-8")

    def test_detects_specific_overlap_across_adrs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sibling_brief = (
                root
                / "docs/design/adr/pre-release/ADR-0.27.0-arb/obpis"
                / "OBPI-0.27.0-03-arb-validate.md"
            )
            self._mk_brief(sibling_brief, ["src/gzkit/arb/validator.py", "tests/"])

            collisions = _scan_sibling_adr_collisions(
                project_root=root,
                target_adr_id="ADR-0.25.0",
                target_obpi_id="OBPI-0.25.0-33-arb-analysis-pattern",
                target_allowed=["src/gzkit/arb/", "tests/"],
            )

            self.assertEqual(len(collisions), 1)
            collision = collisions[0]
            self.assertEqual(collision["sibling_adr"], "ADR-0.27.0")
            self.assertIn("OBPI-0.27.0-03", collision["sibling_obpi"])
            self.assertIn("src/gzkit/arb/validator.py", collision["contested_paths"])

    def test_skips_target_own_adr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            same_adr_brief = (
                root
                / "docs/design/adr/pre-release/ADR-0.25.0-core/obpis"
                / "OBPI-0.25.0-01-attestation.md"
            )
            self._mk_brief(same_adr_brief, ["src/gzkit/arb/"])

            collisions = _scan_sibling_adr_collisions(
                project_root=root,
                target_adr_id="ADR-0.25.0",
                target_obpi_id="OBPI-0.25.0-33-arb-analysis-pattern",
                target_allowed=["src/gzkit/arb/"],
            )

            self.assertEqual(collisions, [])

    def test_filters_non_specific_overlaps(self) -> None:
        """Generic roots like `src/` or `tests/` are too broad to be useful signals."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sibling_brief = (
                root
                / "docs/design/adr/pre-release/ADR-0.27.0-arb/obpis"
                / "OBPI-0.27.0-99-generic.md"
            )
            self._mk_brief(sibling_brief, ["tests/"])

            collisions = _scan_sibling_adr_collisions(
                project_root=root,
                target_adr_id="ADR-0.25.0",
                target_obpi_id="OBPI-0.25.0-33",
                target_allowed=["tests/"],
            )

            self.assertEqual(collisions, [])

    def test_returns_empty_when_no_adr_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            collisions = _scan_sibling_adr_collisions(
                project_root=Path(tmp),
                target_adr_id="ADR-0.25.0",
                target_obpi_id="OBPI-0.25.0-33",
                target_allowed=["src/gzkit/arb/"],
            )
            self.assertEqual(collisions, [])

    def test_skips_when_sibling_path_is_broad_glob(self) -> None:
        """Inverse of GHI #152: target specific, sibling broad → no collision.

        When the target OBPI declares a specific path and the sibling OBPI's
        allowed path is a broad glob (tests/, src/gzkit/), the sibling has not
        made a specific claim on the target's path. The overlap is a
        contract-style allowance, not a real scope collision. Reporting it
        floods plan-audit output with false positives.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sibling_brief = (
                root
                / "docs/design/adr/pre-release/ADR-0.27.0-arb/obpis"
                / "OBPI-0.27.0-99-broad.md"
            )
            self._mk_brief(sibling_brief, ["tests/", "src/gzkit/"])

            collisions = _scan_sibling_adr_collisions(
                project_root=root,
                target_adr_id="ADR-0.0.30",
                target_obpi_id="OBPI-0.0.30-03-authoring-hint-engine",
                target_allowed=[
                    "tests/complexity/authoring/test_hint.py",
                    "src/gzkit/complexity/authoring/hint.py",
                ],
            )

            self.assertEqual(collisions, [])


class TestPlanAuditCmdScopeCollision(unittest.TestCase):
    """@covers GHI #152 — receipt records scope collisions, verdict stays PASS (advisory)."""

    def test_collision_recorded_without_failing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            # Target: OBPI-0.25.0-33 claims src/gzkit/arb/
            target_dir = root / "docs/design/adr/pre-release/ADR-0.25.0-core/obpis"
            target_dir.mkdir(parents=True)
            (target_dir / "OBPI-0.25.0-33-arb-analysis-pattern.md").write_text(
                "# Brief\n## ALLOWED PATHS\n\n- `src/gzkit/arb/` — target for absorbed modules\n",
                encoding="utf-8",
            )

            # Sibling: ADR-0.27.0 brief overlaps on src/gzkit/arb/validator.py
            sibling_dir = root / "docs/design/adr/pre-release/ADR-0.27.0-arb/obpis"
            sibling_dir.mkdir(parents=True)
            (sibling_dir / "OBPI-0.27.0-03-arb-validate.md").write_text(
                "# Brief\n## ALLOWED PATHS\n\n- `src/gzkit/arb/validator.py` — absorbed module\n",
                encoding="utf-8",
            )

            # GHI #393: allowed paths must resolve so the validity scan
            # does not turn this advisory-collision fixture into a FAIL.
            arb_dir = root / "src" / "gzkit" / "arb"
            arb_dir.mkdir(parents=True)
            (arb_dir / "validator.py").write_text("", encoding="utf-8")

            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            (plans_dir / "plan.md").write_text(
                "# Plan for OBPI-0.25.0-33\nModify `src/gzkit/arb/validator.py`\n",
                encoding="utf-8",
            )

            (root / ".gzkit.json").write_text("{}", encoding="utf-8")

            quiet_console = Console(file=StringIO(), quiet=True)
            with (
                patch("gzkit.commands.plan_audit_cmd.console", quiet_console),
                patch("gzkit.commands.common.get_project_root", return_value=root),
                patch("gzkit.commands.common.ensure_initialized"),
            ):
                # Advisory — must not raise SystemExit on collision alone.
                plan_audit_cmd(obpi_id="OBPI-0.25.0-33", as_json=False)

            receipt_path = plans_dir / ".plan-audit-receipt-OBPI-0.25.0-33.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

            self.assertEqual(receipt["verdict"], "PASS")
            self.assertEqual(receipt["gaps_found"], 0)
            self.assertIn("scope_collisions", receipt)
            self.assertEqual(len(receipt["scope_collisions"]), 1)
            collision = receipt["scope_collisions"][0]
            self.assertEqual(collision["sibling_adr"], "ADR-0.27.0")
            self.assertIn("src/gzkit/arb/validator.py", collision["contested_paths"])


class TestExtractPlanPaths(unittest.TestCase):
    """Test plan path extraction."""

    def test_extracts_paths_from_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = Path(tmp) / "plan.md"
            plan.write_text(
                "Modify `src/gzkit/commands/foo.py` and `tests/test_foo.py`\n",
                encoding="utf-8",
            )
            result = _extract_plan_paths(plan)
            self.assertIn("src/gzkit/commands/foo.py", result)
            self.assertIn("tests/test_foo.py", result)


class TestPathWithinAllowed(unittest.TestCase):
    """Test path-within-allowed checking."""

    def test_exact_match(self) -> None:
        self.assertTrue(_path_within_allowed("src/gzkit", ["src/gzkit"]))

    def test_subpath_match(self) -> None:
        self.assertTrue(_path_within_allowed("src/gzkit/commands/foo.py", ["src/gzkit/"]))

    def test_no_match_returns_true(self) -> None:
        # Current implementation returns True when path doesn't match (permissive)
        self.assertTrue(_path_within_allowed("other/path.py", ["src/gzkit/"]))


class TestPlanAuditCmdPass(unittest.TestCase):
    """Test plan_audit_cmd end-to-end PASS scenario."""

    def test_pass_writes_receipt_and_exits_0(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            # Create ADR directory
            adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.1.0-feature"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            brief = obpis_dir / "OBPI-0.1.0-01-feature.md"
            brief.write_text("# Brief\n## Allowed Paths\n- `src/`\n", encoding="utf-8")
            (root / "src").mkdir()  # GHI #393: allowed path must resolve

            # Create plans directory with plan file
            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            plan = plans_dir / "plan-feature.md"
            plan.write_text("# Plan for OBPI-0.1.0-01\nModify `src/foo.py`\n", encoding="utf-8")

            # Create .gzkit.json
            (root / ".gzkit.json").write_text("{}", encoding="utf-8")

            quiet_console = Console(file=StringIO(), quiet=True)
            with (
                patch("gzkit.commands.plan_audit_cmd.console", quiet_console),
                patch("gzkit.commands.common.get_project_root", return_value=root),
                patch("gzkit.commands.common.ensure_initialized"),
            ):
                # Should not raise (exit 0)
                plan_audit_cmd(obpi_id="OBPI-0.1.0-01", as_json=False)

            receipt_path = plans_dir / ".plan-audit-receipt-OBPI-0.1.0-01.json"
            self.assertTrue(receipt_path.exists())
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["verdict"], "PASS")
            self.assertEqual(receipt["obpi_id"], "OBPI-0.1.0-01")
            self.assertEqual(receipt["gaps_found"], 0)


class TestPlanAuditCmdFail(unittest.TestCase):
    """Test plan_audit_cmd end-to-end FAIL scenario."""

    def test_fail_exits_1_when_no_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            # Create ADR directory but NO plan file
            adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.1.0-feature"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            brief = obpis_dir / "OBPI-0.1.0-01-feature.md"
            brief.write_text("# Brief\n", encoding="utf-8")

            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)

            (root / ".gzkit.json").write_text("{}", encoding="utf-8")

            quiet_console = Console(file=StringIO(), quiet=True)
            with (
                patch("gzkit.commands.plan_audit_cmd.console", quiet_console),
                patch("gzkit.commands.common.get_project_root", return_value=root),
                patch("gzkit.commands.common.ensure_initialized"),
                self.assertRaises(SystemExit) as ctx,
            ):
                plan_audit_cmd(obpi_id="OBPI-0.1.0-01", as_json=False)

            self.assertEqual(ctx.exception.code, 1)
            receipt_path = plans_dir / ".plan-audit-receipt-OBPI-0.1.0-01.json"
            self.assertTrue(receipt_path.exists())
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["verdict"], "FAIL")
            self.assertGreater(receipt["gaps_found"], 0)


class TestPlanAuditCmdJson(unittest.TestCase):
    """Test plan_audit_cmd --json output."""

    def test_json_output_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.1.0-feature"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            brief = obpis_dir / "OBPI-0.1.0-01-feature.md"
            brief.write_text("# Brief\n", encoding="utf-8")

            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            plan = plans_dir / "plan.md"
            plan.write_text("# OBPI-0.1.0-01 plan\n", encoding="utf-8")

            (root / ".gzkit.json").write_text("{}", encoding="utf-8")

            with (
                patch("gzkit.commands.common.get_project_root", return_value=root),
                patch("gzkit.commands.common.ensure_initialized"),
                patch("sys.stdout", new_callable=StringIO) as mock_stdout,
            ):
                plan_audit_cmd(obpi_id="OBPI-0.1.0-01", as_json=True)
                output = mock_stdout.getvalue()

            data = json.loads(output)
            self.assertEqual(data["obpi_id"], "OBPI-0.1.0-01")
            self.assertEqual(data["verdict"], "PASS")
            self.assertIn("timestamp", data)
            self.assertIn("gaps_found", data)


class TestVendorMirrorCanonical(unittest.TestCase):
    """@covers GHI #393 — flag vendor-mirror allowed paths and suggest canonical."""

    def test_flags_claude_rules_path(self) -> None:
        from gzkit.commands.plan_audit_cmd import _vendor_mirror_canonical

        self.assertEqual(
            _vendor_mirror_canonical(".claude/rules/tests.md"),
            ".gzkit/rules/tests.md",
        )

    def test_flags_claude_skills_path(self) -> None:
        from gzkit.commands.plan_audit_cmd import _vendor_mirror_canonical

        self.assertEqual(
            _vendor_mirror_canonical(".claude/skills/foo/SKILL.md"),
            ".gzkit/skills/foo/SKILL.md",
        )

    def test_flags_github_instructions_path(self) -> None:
        from gzkit.commands.plan_audit_cmd import _vendor_mirror_canonical

        self.assertEqual(
            _vendor_mirror_canonical(".github/instructions/agents.md"),
            ".gzkit/rules/agents.md",
        )

    def test_flags_github_skills_path(self) -> None:
        from gzkit.commands.plan_audit_cmd import _vendor_mirror_canonical

        self.assertEqual(
            _vendor_mirror_canonical(".github/skills/foo/SKILL.md"),
            ".gzkit/skills/foo/SKILL.md",
        )

    def test_flags_agents_skills_path(self) -> None:
        from gzkit.commands.plan_audit_cmd import _vendor_mirror_canonical

        self.assertEqual(
            _vendor_mirror_canonical(".agents/skills/foo/SKILL.md"),
            ".gzkit/skills/foo/SKILL.md",
        )

    def test_returns_none_for_canonical_path(self) -> None:
        from gzkit.commands.plan_audit_cmd import _vendor_mirror_canonical

        self.assertIsNone(_vendor_mirror_canonical(".gzkit/rules/tests.md"))

    def test_returns_none_for_source_path(self) -> None:
        from gzkit.commands.plan_audit_cmd import _vendor_mirror_canonical

        self.assertIsNone(_vendor_mirror_canonical("src/gzkit/foo.py"))

    def test_returns_none_for_claude_plans_path(self) -> None:
        # .claude/plans/ is the operator-local plan home, not a vendor mirror.
        from gzkit.commands.plan_audit_cmd import _vendor_mirror_canonical

        self.assertIsNone(_vendor_mirror_canonical(".claude/plans/foo.md"))


class TestAllowedPathResolves(unittest.TestCase):
    """@covers GHI #393 — verify allowed paths refer to real files/dirs or glob roots."""

    def test_existing_file_resolves(self) -> None:
        from gzkit.commands.plan_audit_cmd import _allowed_path_resolves

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "foo.py").write_text("", encoding="utf-8")
            self.assertTrue(_allowed_path_resolves(root, "src/foo.py"))

    def test_existing_directory_resolves(self) -> None:
        from gzkit.commands.plan_audit_cmd import _allowed_path_resolves

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "gzkit").mkdir(parents=True)
            self.assertTrue(_allowed_path_resolves(root, "src/gzkit/"))

    def test_glob_with_existing_root_resolves(self) -> None:
        from gzkit.commands.plan_audit_cmd import _allowed_path_resolves

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "gzkit").mkdir(parents=True)
            self.assertTrue(_allowed_path_resolves(root, "src/gzkit/**/*.py"))

    def test_glob_with_missing_root_does_not_resolve(self) -> None:
        from gzkit.commands.plan_audit_cmd import _allowed_path_resolves

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertFalse(_allowed_path_resolves(root, "src/missing/**/*.py"))

    def test_template_placeholder_treated_as_glob(self) -> None:
        from gzkit.commands.plan_audit_cmd import _allowed_path_resolves

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit" / "skills").mkdir(parents=True)
            self.assertTrue(_allowed_path_resolves(root, ".gzkit/skills/<slug>/SKILL.md"))

    def test_missing_file_does_not_resolve(self) -> None:
        from gzkit.commands.plan_audit_cmd import _allowed_path_resolves

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertFalse(_allowed_path_resolves(root, "src/gzkit/governance/trust_audits.py"))

    def test_cli_flag_token_skipped(self) -> None:
        from gzkit.commands.plan_audit_cmd import _allowed_path_resolves

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertTrue(_allowed_path_resolves(root, "--skill"))


class TestPlanAuditCmdBriefPathGaps(unittest.TestCase):
    """@covers GHI #393 — plan-audit FAILs on stale or vendor-mirror allowed paths."""

    def test_fails_on_nonexistent_allowed_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_dir = root / "docs/design/adr/foundation/ADR-0.1.0-feature"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            brief = obpis_dir / "OBPI-0.1.0-01-feature.md"
            brief.write_text(
                "# Brief\n## Allowed Paths\n- `src/missing/ghost.py`\n",
                encoding="utf-8",
            )

            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            (plans_dir / "plan.md").write_text(
                "# Plan for OBPI-0.1.0-01\nModify src/missing/ghost.py\n",
                encoding="utf-8",
            )
            (root / ".gzkit.json").write_text("{}", encoding="utf-8")

            quiet_console = Console(file=StringIO(), quiet=True)
            with (
                patch("gzkit.commands.plan_audit_cmd.console", quiet_console),
                patch("gzkit.commands.common.get_project_root", return_value=root),
                patch("gzkit.commands.common.ensure_initialized"),
                self.assertRaises(SystemExit) as ctx,
            ):
                plan_audit_cmd(obpi_id="OBPI-0.1.0-01", as_json=False)

            self.assertEqual(ctx.exception.code, 1)
            receipt = json.loads(
                (plans_dir / ".plan-audit-receipt-OBPI-0.1.0-01.json").read_text(encoding="utf-8")
            )
            self.assertEqual(receipt["verdict"], "FAIL")
            self.assertTrue(
                any("does not exist" in g and "src/missing/ghost.py" in g for g in receipt["gaps"]),
                f"expected non-existence gap citing the stale path, got {receipt['gaps']}",
            )

    def test_fails_on_vendor_mirror_allowed_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_dir = root / "docs/design/adr/foundation/ADR-0.1.0-feature"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            brief = obpis_dir / "OBPI-0.1.0-01-feature.md"
            brief.write_text(
                "# Brief\n## Allowed Paths\n- `.claude/rules/tests.md`\n",
                encoding="utf-8",
            )
            # Materialize the mirror so the gap fires on the
            # non-canonical-edit-surface signal, not on missing-path.
            (root / ".claude" / "rules").mkdir(parents=True)
            (root / ".claude" / "rules" / "tests.md").write_text("", encoding="utf-8")

            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            (plans_dir / "plan.md").write_text(
                "# Plan for OBPI-0.1.0-01\nEdit .claude/rules/tests.md\n",
                encoding="utf-8",
            )
            (root / ".gzkit.json").write_text("{}", encoding="utf-8")

            quiet_console = Console(file=StringIO(), quiet=True)
            with (
                patch("gzkit.commands.plan_audit_cmd.console", quiet_console),
                patch("gzkit.commands.common.get_project_root", return_value=root),
                patch("gzkit.commands.common.ensure_initialized"),
                self.assertRaises(SystemExit) as ctx,
            ):
                plan_audit_cmd(obpi_id="OBPI-0.1.0-01", as_json=False)

            self.assertEqual(ctx.exception.code, 1)
            receipt = json.loads(
                (plans_dir / ".plan-audit-receipt-OBPI-0.1.0-01.json").read_text(encoding="utf-8")
            )
            self.assertEqual(receipt["verdict"], "FAIL")
            gaps = receipt["gaps"]
            self.assertTrue(
                any("vendor mirror" in g for g in gaps)
                and any(".gzkit/rules/tests.md" in g for g in gaps),
                f"expected vendor-mirror gap citing canonical edit surface, got {gaps}",
            )


class TestPlanCreatesPathsSuppression(unittest.TestCase):
    """@covers GHI #403 — net-new paths declared in the plan are not stale-path defects."""

    def test_extracts_paths_from_create_marker(self) -> None:
        from gzkit.commands.plan_audit_cmd import _extract_plan_creates_paths

        with tempfile.TemporaryDirectory() as tmp:
            plan = Path(tmp) / "plan.md"
            plan.write_text(
                "# Plan: OBPI-0.1.0-01\n"
                "\n"
                "## Allowed Files\n"
                "\n"
                "- **CREATE** `src/gzkit/foo/bar.py` — new package member.\n"
                "- **CREATE** `tests/foo/test_bar.py` — REQ-derived tests.\n",
                encoding="utf-8",
            )
            self.assertEqual(
                _extract_plan_creates_paths(plan),
                {"src/gzkit/foo/bar.py", "tests/foo/test_bar.py"},
            )

    def test_extracts_paths_from_creates_section_heading(self) -> None:
        from gzkit.commands.plan_audit_cmd import _extract_plan_creates_paths

        with tempfile.TemporaryDirectory() as tmp:
            plan = Path(tmp) / "plan.md"
            plan.write_text(
                "# Plan\n"
                "\n"
                "## Files (creates these files)\n"
                "\n"
                "- `src/gzkit/foo/bar.py` — new module.\n"
                "- `src/gzkit/schemas/foo.json` — JSON Schema mirror.\n"
                "\n"
                "## Allowed Files\n"
                "- `src/gzkit/already_existing.py` — pre-existing edit target.\n",
                encoding="utf-8",
            )
            paths = _extract_plan_creates_paths(plan)
            self.assertIn("src/gzkit/foo/bar.py", paths)
            self.assertIn("src/gzkit/schemas/foo.json", paths)
            self.assertNotIn("src/gzkit/already_existing.py", paths)

    def test_returns_empty_when_no_creates_declarations(self) -> None:
        from gzkit.commands.plan_audit_cmd import _extract_plan_creates_paths

        with tempfile.TemporaryDirectory() as tmp:
            plan = Path(tmp) / "plan.md"
            plan.write_text(
                "# Plan: OBPI-0.1.0-01\n## Allowed Files\n- `src/gzkit/foo.py` — edit.\n",
                encoding="utf-8",
            )
            self.assertEqual(_extract_plan_creates_paths(plan), set())

    def test_suppresses_existence_gap_for_declared_net_new_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_dir = root / "docs/design/adr/foundation/ADR-0.1.0-feature"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            brief = obpis_dir / "OBPI-0.1.0-01-feature.md"
            brief.write_text(
                "# Brief\n## Allowed Paths\n- `src/gzkit/newpkg/__init__.py`\n",
                encoding="utf-8",
            )

            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            (plans_dir / "plan.md").write_text(
                "# Plan for OBPI-0.1.0-01\n"
                "## Files (creates these files)\n"
                "- **CREATE** `src/gzkit/newpkg/__init__.py` — new package marker.\n",
                encoding="utf-8",
            )
            (root / ".gzkit.json").write_text("{}", encoding="utf-8")

            quiet_console = Console(file=StringIO(), quiet=True)
            with (
                patch("gzkit.commands.plan_audit_cmd.console", quiet_console),
                patch("gzkit.commands.common.get_project_root", return_value=root),
                patch("gzkit.commands.common.ensure_initialized"),
            ):
                plan_audit_cmd(obpi_id="OBPI-0.1.0-01", as_json=False)

            receipt = json.loads(
                (plans_dir / ".plan-audit-receipt-OBPI-0.1.0-01.json").read_text(encoding="utf-8")
            )
            self.assertEqual(receipt["verdict"], "PASS", receipt.get("gaps"))

    def test_preserves_existence_gap_for_undeclared_stale_path(self) -> None:
        """Regression guard for GHI #393 — undeclared stale paths still FAIL."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_dir = root / "docs/design/adr/foundation/ADR-0.1.0-feature"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            brief = obpis_dir / "OBPI-0.1.0-01-feature.md"
            brief.write_text(
                "# Brief\n## Allowed Paths\n- `src/gzkit/stale/ghost.py`\n",
                encoding="utf-8",
            )

            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            (plans_dir / "plan.md").write_text(
                "# Plan for OBPI-0.1.0-01\n"
                "## Steps\n"
                "Modify src/gzkit/stale/ghost.py to add a method.\n",
                encoding="utf-8",
            )
            (root / ".gzkit.json").write_text("{}", encoding="utf-8")

            quiet_console = Console(file=StringIO(), quiet=True)
            with (
                patch("gzkit.commands.plan_audit_cmd.console", quiet_console),
                patch("gzkit.commands.common.get_project_root", return_value=root),
                patch("gzkit.commands.common.ensure_initialized"),
                self.assertRaises(SystemExit) as ctx,
            ):
                plan_audit_cmd(obpi_id="OBPI-0.1.0-01", as_json=False)

            self.assertEqual(ctx.exception.code, 1)
            receipt = json.loads(
                (plans_dir / ".plan-audit-receipt-OBPI-0.1.0-01.json").read_text(encoding="utf-8")
            )
            self.assertEqual(receipt["verdict"], "FAIL")
            self.assertTrue(
                any(
                    "does not exist" in g and "src/gzkit/stale/ghost.py" in g
                    for g in receipt["gaps"]
                ),
                f"expected non-existence gap citing stale path, got {receipt['gaps']}",
            )


if __name__ == "__main__":
    unittest.main()
