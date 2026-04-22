"""Promoted advisory-rule audits (GHIs #202–#214).

Each test is the unit-level entry to an audit that also runs as a ``gz
validate --<scope>`` flag. Keeping these under ``tests/governance/`` locks
the promotion against silent regression — if the audit returns errors on
the current tree, the test fails and the pre-commit suite catches it.

The canonical advisory rules catalogue lives at
``docs/governance/advisory-rules-audit.md``.
"""

from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import (
    audit_adr_taxonomy,
    audit_advisory_scorecard,
    audit_behave_req_tags,
    audit_brief_headings,
    audit_class_size,
    audit_pool_adr_isolation,
    audit_pydantic_models,
    audit_reconcile_freshness,
    audit_skill_alignment,
    audit_test_tiers,
    audit_utf8_prefix,
    audit_version_release,
)
from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class PromotedAdvisoryAudits(unittest.TestCase):
    """Lock-in for every advisory rule promoted to mechanical enforcement."""

    def _assert_clean(self, errors, label: str) -> None:
        self.assertFalse(
            errors,
            msg=f"{label} violations:\n"
            + "\n".join(f"  {e.artifact}: {e.message}" for e in errors),
        )

    def test_utf8_prefix_rule_9(self) -> None:
        self._assert_clean(audit_utf8_prefix(_PROJECT_ROOT), "utf8_prefix")

    def test_test_tiers_rule_37(self) -> None:
        self._assert_clean(audit_test_tiers(_PROJECT_ROOT), "test_tiers")

    def test_pydantic_models_rules_25_26(self) -> None:
        self._assert_clean(audit_pydantic_models(_PROJECT_ROOT), "pydantic_models")

    def test_class_size_rule_21(self) -> None:
        self._assert_clean(audit_class_size(_PROJECT_ROOT), "class_size")

    def test_version_release_rule_11(self) -> None:
        self._assert_clean(audit_version_release(_PROJECT_ROOT), "version_release")

    def test_pool_adr_isolation_rules_1_2(self) -> None:
        self._assert_clean(audit_pool_adr_isolation(_PROJECT_ROOT), "pool_adr_isolation")

    def test_behave_req_tags_rule_39(self) -> None:
        self._assert_clean(audit_behave_req_tags(_PROJECT_ROOT), "behave_req_tags")

    def test_behave_req_tags_rule_39_uses_reversed_direction(self) -> None:
        """GHI #276: audit enumerates heavy OBPIs (not feature files)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # A heavy OBPI with REQs and no feature coverage at all — the
            # shape GHI #276 added enforcement for.
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
            brief_dir.mkdir(parents=True)
            (brief_dir / "OBPI-9.9.9-01-uncovered.md").write_text(
                "---\nid: OBPI-9.9.9-01-uncovered\nlane: Heavy\n---\n\n"
                "## Acceptance Criteria\n\n- [ ] REQ-9.9.9-01-01: something\n",
                encoding="utf-8",
            )
            (root / "features").mkdir()  # no feature files
            errors = audit_behave_req_tags(root)
            self.assertTrue(errors, "heavy OBPI with zero BDD coverage must flag")
            self.assertIn("OBPI-9.9.9-01-uncovered", errors[0].message)
            self.assertIn("REQ-9.9.9-01-01", errors[0].message)

    def test_behave_req_tags_rule_39_pool_excluded(self) -> None:
        """Pool-ADR briefs do not carry gate obligations — must not flag."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "pool" / "ADR-pool.x" / "obpis"
            brief_dir.mkdir(parents=True)
            (brief_dir / "OBPI-9.9.9-01-pool.md").write_text(
                "---\nid: OBPI-9.9.9-01-pool\nlane: Heavy\n---\n\n"
                "## Acceptance Criteria\n\n- [ ] REQ-9.9.9-01-01: something\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_behave_req_tags(root), [])

    def test_behave_req_tags_rule_39_lite_skipped(self) -> None:
        """Lite-lane OBPIs are outside the rule's scope."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
            brief_dir.mkdir(parents=True)
            (brief_dir / "OBPI-x-01.md").write_text(
                "---\nid: OBPI-9.9.9-01-covered\nlane: Lite\n---\n\n"
                "## Acceptance Criteria\n\n- [ ] REQ-9.9.9-01-01: something\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_behave_req_tags(root), [])

    def test_behave_req_tags_rule_39_waiver_respected(self) -> None:
        """Sidecar waiver silences a heavy OBPI's missing-coverage violation."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
            brief_dir.mkdir(parents=True)
            (brief_dir / "OBPI-9.9.9-01-waived.md").write_text(
                "---\nid: OBPI-9.9.9-01-waived\nlane: Heavy\n---\n\n"
                "## Acceptance Criteria\n\n- [ ] REQ-9.9.9-01-01: something\n",
                encoding="utf-8",
            )
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "behave_coverage_waivers.json").write_text(
                '{"schema_version": 1, "default_rationale": {"t": "test"}, '
                '"waivers": {"OBPI-9.9.9-01-waived": {"rationale": "t"}}}',
                encoding="utf-8",
            )
            self.assertEqual(audit_behave_req_tags(root), [])

    def test_behave_req_tags_rule_39_covered_passes(self) -> None:
        """Heavy OBPI with every REQ tagged at scenario level must pass."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
            brief_dir.mkdir(parents=True)
            (brief_dir / "OBPI-x-01.md").write_text(
                "---\nid: OBPI-9.9.9-01-covered\nlane: Heavy\n---\n\n"
                "## Acceptance Criteria\n\n- [ ] REQ-9.9.9-01-01: something\n",
                encoding="utf-8",
            )
            features_dir = root / "features"
            features_dir.mkdir()
            (features_dir / "x.feature").write_text(
                "Feature: x\n\n  @REQ-9.9.9-01-01\n  Scenario: covers it\n"
                "    Given nothing\n    Then nothing\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_behave_req_tags(root), [])

    def test_skill_alignment_invariant_1(self) -> None:
        self._assert_clean(audit_skill_alignment(_PROJECT_ROOT), "skill_alignment")

    def test_advisory_scorecard_selftest(self) -> None:
        self._assert_clean(audit_advisory_scorecard(_PROJECT_ROOT), "advisory_scorecard")

    def test_reconcile_freshness_rule_4(self) -> None:
        # Reconcile audit is a no-op when no reconcile events exist; it must
        # never hard-fail on current state until the event types land.
        self._assert_clean(audit_reconcile_freshness(_PROJECT_ROOT), "reconcile_freshness")

    @covers("REQ-0.0.17-04-09")
    @unittest.skip("unskip after ADR-0.0.17 backfill lands")
    def test_adr_taxonomy_rule_X(self) -> None:
        # REQ-0.0.17-04-09: lock-in passes on live tree only after backfill.
        self._assert_clean(audit_adr_taxonomy(_PROJECT_ROOT), "taxonomy")

    @covers("REQ-0.0.17-04-10")
    def test_taxonomy_scorecard_entry_exists(self) -> None:
        """REQ-0.0.17-04-10: advisory scorecard cites gz validate --taxonomy."""
        scorecard = _PROJECT_ROOT / "docs" / "governance" / "advisory-rules-audit.md"
        text = scorecard.read_text(encoding="utf-8")
        self.assertIn("gz validate --taxonomy", text)
        self.assertIn("ADR-0.0.17", text)

    def test_brief_headings_ghi_238(self) -> None:
        """GHI #238: live tree has no H2 drift for evidence sections."""
        self._assert_clean(audit_brief_headings(_PROJECT_ROOT), "brief_headings")

    def test_brief_headings_scorecard_entry_exists(self) -> None:
        """GHI #238: advisory scorecard cites gz validate --brief-headings."""
        scorecard = _PROJECT_ROOT / "docs" / "governance" / "advisory-rules-audit.md"
        text = scorecard.read_text(encoding="utf-8")
        self.assertIn("gz validate --brief-headings", text)


class BriefHeadingsAuditNegativeCases(unittest.TestCase):
    """GHI #238: H2 evidence heading drift is flagged."""

    def test_h2_implementation_summary_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
            brief_dir.mkdir(parents=True)
            brief = brief_dir / "OBPI-x-01.md"
            brief.write_text(
                "# OBPI-x-01\n\n"
                "## Objective\n\nDo things.\n\n"
                "## Implementation Summary\n\n"
                "- did things\n",
                encoding="utf-8",
            )
            errors = audit_brief_headings(root)
            self.assertTrue(errors, "H2 Implementation Summary must flag")
            self.assertTrue(
                any("Implementation Summary" in e.message for e in errors),
                f"error message should name the heading; got {[e.message for e in errors]}",
            )

    def test_h2_key_proof_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "pool" / "ADR-y" / "obpis"
            brief_dir.mkdir(parents=True)
            brief = brief_dir / "OBPI-y-01.md"
            brief.write_text(
                "# OBPI-y-01\n\n## Objective\n\nx\n\n## Key Proof\n\nproof\n",
                encoding="utf-8",
            )
            errors = audit_brief_headings(root)
            self.assertTrue(errors)
            self.assertTrue(any("Key Proof" in e.message for e in errors))

    def test_h3_implementation_summary_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "ADR-z" / "obpis"
            brief_dir.mkdir(parents=True)
            brief = brief_dir / "OBPI-z-01.md"
            brief.write_text(
                "# OBPI-z-01\n\n"
                "## Objective\n\nDo things.\n\n"
                "### Implementation Summary\n\n- did things\n\n"
                "### Key Proof\n\nproof text\n",
                encoding="utf-8",
            )
            errors = audit_brief_headings(root)
            self.assertEqual(errors, [])

    def test_no_briefs_dir_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(audit_brief_headings(Path(tmp)), [])


def _write_adr(root: Path, rel_path: str, frontmatter: dict[str, str]) -> Path:
    """Write a minimal ADR stub with the given frontmatter fields."""
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    for key, value in frontmatter.items():
        lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")
    lines.append("# Stub ADR")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


class TaxonomyAuditNegativeCases(unittest.TestCase):
    """Deterministic fixtures exercising each violation class."""

    @covers("REQ-0.0.17-04-02")
    def test_pool_kind_frontmatter_is_violation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "docs/design/adr/pool/ADR-pool.example.md",
                {"id": "ADR-pool.example", "kind": "foundation"},
            )
            errors = audit_adr_taxonomy(root)
            self.assertEqual(len(errors), 1, msg=str(errors))
            self.assertEqual(errors[0].type, "taxonomy")
            self.assertIn("Pool ADRs derive kind", errors[0].message)

    @covers("REQ-0.0.17-04-03")
    def test_non_pool_missing_kind_is_violation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "docs/design/adr/foundation/ADR-0.0.1-example/ADR-0.0.1-example.md",
                {"id": "ADR-0.0.1", "semver": "0.0.1"},
            )
            errors = audit_adr_taxonomy(root)
            self.assertEqual(len(errors), 1, msg=str(errors))
            self.assertIn("missing `kind:`", errors[0].message)
            self.assertIn("foundation", errors[0].message)
            self.assertIn("feature", errors[0].message)

    @covers("REQ-0.0.17-04-04")
    def test_foundation_with_non_0_0_x_semver_is_violation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "docs/design/adr/foundation/ADR-0.5.0-example/ADR-0.5.0-example.md",
                {"id": "ADR-0.5.0", "kind": "foundation", "semver": "0.5.0"},
            )
            errors = audit_adr_taxonomy(root)
            self.assertEqual(len(errors), 1, msg=str(errors))
            self.assertIn("`kind: foundation` requires semver `0.0.x`", errors[0].message)
            self.assertIn("0.5.0", errors[0].message)

    @covers("REQ-0.0.17-04-05")
    def test_feature_with_0_0_x_semver_is_violation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "docs/design/adr/foundation/ADR-0.0.5-example/ADR-0.0.5-example.md",
                {"id": "ADR-0.0.5", "kind": "feature", "semver": "0.0.5"},
            )
            errors = audit_adr_taxonomy(root)
            self.assertEqual(len(errors), 1, msg=str(errors))
            self.assertIn("`kind: feature` forbids semver `0.0.x`", errors[0].message)
            self.assertIn("0.0.5", errors[0].message)

    @covers("REQ-0.0.17-04-06")
    def test_unknown_kind_value_is_violation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "docs/design/adr/foundation/ADR-0.0.7-example/ADR-0.0.7-example.md",
                {"id": "ADR-0.0.7", "kind": "doctrine", "semver": "0.0.7"},
            )
            errors = audit_adr_taxonomy(root)
            self.assertEqual(len(errors), 1, msg=str(errors))
            self.assertIn("Unknown `kind: doctrine`", errors[0].message)

    @covers("REQ-0.0.17-04-07")
    def test_pool_with_semver_field_is_not_violation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "docs/design/adr/pool/ADR-pool.example.md",
                {"id": "ADR-pool.example", "semver": "0.9.0"},
            )
            self.assertEqual(audit_adr_taxonomy(root), [])

    @covers("REQ-0.0.17-04-07")
    def test_pool_with_lane_field_is_not_violation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "docs/design/adr/pool/ADR-pool.example.md",
                {"id": "ADR-pool.example", "lane": "heavy"},
            )
            self.assertEqual(audit_adr_taxonomy(root), [])

    @covers("REQ-0.0.17-04-01")
    def test_audit_never_mutates_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = [
                _write_adr(
                    root,
                    "docs/design/adr/foundation/ADR-0.0.1-example/ADR-0.0.1-example.md",
                    {"id": "ADR-0.0.1", "kind": "foundation", "semver": "0.0.1"},
                ),
                _write_adr(
                    root,
                    "docs/design/adr/pool/ADR-pool.bad.md",
                    {"id": "ADR-pool.bad", "kind": "foundation"},
                ),
                _write_adr(
                    root,
                    "docs/design/adr/foundation/ADR-0.0.2-example/ADR-0.0.2-example.md",
                    {"id": "ADR-0.0.2", "semver": "0.0.2"},
                ),
            ]
            before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
            audit_adr_taxonomy(root)
            after = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
            self.assertEqual(before, after)

    @covers("REQ-0.0.17-04-01")
    def test_clean_tree_produces_no_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "docs/design/adr/foundation/ADR-0.0.1-example/ADR-0.0.1-example.md",
                {"id": "ADR-0.0.1", "kind": "foundation", "semver": "0.0.1"},
            )
            _write_adr(
                root,
                "docs/design/adr/pre-release/ADR-0.5.0-example/ADR-0.5.0-example.md",
                {"id": "ADR-0.5.0", "kind": "feature", "semver": "0.5.0"},
            )
            _write_adr(
                root,
                "docs/design/adr/pool/ADR-pool.example.md",
                {"id": "ADR-pool.example"},
            )
            self.assertEqual(audit_adr_taxonomy(root), [])


class VersionReleaseAuditChickenAndEgg(unittest.TestCase):
    """GHI #217 — audit must not block the release commit that creates the tag.

    `gz patch release` writes a release manifest at
    ``docs/releases/PATCH-v{version}.md`` BEFORE the bump commit is attempted.
    The manifest is L1 proof that the canonical release ceremony is in flight.
    `audit_version_release` must accept it as equivalent to a git tag for the
    brief window between the bump commit and `gh release create`, otherwise
    the audit and the release pipeline are mutually exclusive.
    """

    def _write_pyproject(self, root: Path, version: str) -> None:
        (root / "pyproject.toml").write_text(
            f'[project]\nname = "demo"\nversion = "{version}"\n',
            encoding="utf-8",
        )

    def _init_empty_git(self, root: Path) -> None:
        import subprocess  # noqa: PLC0415

        subprocess.run(["git", "init", "-q"], cwd=root, check=True)

    def test_naked_bump_still_fails(self) -> None:
        """Bump without manifest and without tag — class of failure the audit catches."""
        import tempfile  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._init_empty_git(root)
            self._write_pyproject(root, "9.9.9")
            errors = audit_version_release(root)
            self.assertEqual(len(errors), 1, msg=f"expected one violation, got {errors}")
            self.assertIn("9.9.9", errors[0].message)

    def test_in_flight_release_manifest_satisfies_audit(self) -> None:
        """Manifest at docs/releases/PATCH-v{version}.md is L1 evidence of release in flight."""
        import tempfile  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._init_empty_git(root)
            self._write_pyproject(root, "9.9.9")
            manifest_dir = root / "docs" / "releases"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "PATCH-v9.9.9.md").write_text(
                "# Patch Release: v9.9.9\n", encoding="utf-8"
            )
            self.assertEqual(
                audit_version_release(root),
                [],
                msg="audit must pass when PATCH-v{version}.md exists (release mid-ceremony)",
            )

    def test_manifest_for_different_version_does_not_satisfy(self) -> None:
        """Only a manifest matching the declared version counts; stale manifests do not."""
        import tempfile  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._init_empty_git(root)
            self._write_pyproject(root, "9.9.9")
            manifest_dir = root / "docs" / "releases"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "PATCH-v9.9.8.md").write_text(
                "# Patch Release: v9.9.8\n", encoding="utf-8"
            )
            errors = audit_version_release(root)
            self.assertEqual(len(errors), 1, msg=f"expected one violation, got {errors}")


if __name__ == "__main__":
    unittest.main()
