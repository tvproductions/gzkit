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
from unittest.mock import patch

from gzkit.governance.trust_audits import (
    audit_adr_taxonomy,
    audit_advisory_scorecard,
    audit_behave_req_tags,
    audit_brief_cross_references,
    audit_brief_demo_section,
    audit_brief_headings,
    audit_class_size,
    audit_cli_alignment,
    audit_insights_shape,
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

    def test_insights_shape_ghi_358(self) -> None:
        self._assert_clean(audit_insights_shape(_PROJECT_ROOT), "insights_shape")

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
                "---\nid: OBPI-9.9.9-01-uncovered\nlane: Heavy\nstatus: Completed\n---\n\n"
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
                "---\nid: OBPI-9.9.9-01-pool\nlane: Heavy\nstatus: Completed\n---\n\n"
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
                "---\nid: OBPI-9.9.9-01-covered\nlane: Lite\nstatus: Completed\n---\n\n"
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
                "---\nid: OBPI-9.9.9-01-waived\nlane: Heavy\nstatus: Completed\n---\n\n"
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

    def test_behave_req_tags_kind_aware_exempts_covers_and_fence(self) -> None:
        """GHI #636: a heavy OBPI whose REQs are all proof-channel-satisfied
        without behave needs no waiver.

        ADR-0.0.59's three-kind taxonomy assigns each REQ a proof channel:
        BEHAVIOR → ``@covers`` test, SUPPORT → ledger+validator, STRUCTURAL-
        FENCE → parent-ADR invariant. None of those channels is a behave
        scenario. So a BEHAVIOR REQ proven by an ``@covers`` unit test, and a
        STRUCTURAL-FENCE REQ proven by its parent-ADR anchor, must not demand a
        behave scenario or a waiver. Reproduces OBPI-0.0.74-01's exact shape
        (two BEHAVIOR REQs with @covers tests + one STRUCTURAL-FENCE REQ).
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
            brief_dir.mkdir(parents=True)
            (brief_dir / "OBPI-9.9.9-01-unit-only.md").write_text(
                "---\nid: OBPI-9.9.9-01-unit-only\nlane: Heavy\nstatus: Completed\n---\n\n"
                "## Acceptance Criteria\n\n"
                "- [ ] REQ-9.9.9-01-01 [behavior]: library presence rule (@covers test)\n"
                "- [ ] REQ-9.9.9-01-02 [behavior]: library void rule (@covers test)\n"
                "- [ ] REQ-9.9.9-01-03 [structural-fence]: single truth-source\n",
                encoding="utf-8",
            )
            # @covers unit tests prove the two BEHAVIOR REQs — no behave surface.
            test_dir = root / "tests" / "mx"
            test_dir.mkdir(parents=True)
            (test_dir / "test_marker.py").write_text(
                '@covers("REQ-9.9.9-01-01")\n'
                "def test_presence() -> None: ...\n\n"
                "@covers('REQ-9.9.9-01-02')\n"
                "def test_void() -> None: ...\n",
                encoding="utf-8",
            )
            (root / "features").mkdir()  # no feature files, no waiver
            self.assertEqual(
                audit_behave_req_tags(root),
                [],
                "BEHAVIOR-with-@covers and STRUCTURAL-FENCE REQs must be exempt",
            )

    def test_behave_req_tags_behavior_without_any_proof_still_flags(self) -> None:
        """GHI #636: the kind-aware exemption keeps the gate's teeth.

        A BEHAVIOR REQ with neither a behave scenario tag NOR an ``@covers``
        unit test is genuinely uncovered and must still flag — the exemption
        admits unit-proven and non-behave-channel REQs, never proof-absent ones.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
            brief_dir.mkdir(parents=True)
            (brief_dir / "OBPI-9.9.9-02-uncovered.md").write_text(
                "---\nid: OBPI-9.9.9-02-uncovered\nlane: Heavy\nstatus: Completed\n---\n\n"
                "## Acceptance Criteria\n\n"
                "- [ ] REQ-9.9.9-02-01 [behavior]: an uncovered behavior\n",
                encoding="utf-8",
            )
            (root / "features").mkdir()  # no feature files, no @covers, no waiver
            errors = audit_behave_req_tags(root)
            self.assertTrue(errors, "proof-absent BEHAVIOR REQ must still flag")
            self.assertIn("REQ-9.9.9-02-01", errors[0].message)

    def test_behave_req_tags_rule_39_pre_implementation_excluded(self) -> None:
        """GHI #323: heavy OBPI briefs in any pre-implementation status
        (Draft / Pending / Proposed / etc.) are pre-implementation; the CLI
        verbs / engines / hooks they name do not exist yet, so BDD scenarios
        definitionally cannot exist. The validator skips these briefs per
        ``.gzkit/rules/tests.md`` § Red-Green-Refactor (tests at
        implementation time, not at brief-draft time).

        The filter is INVERSE — only Completed/Validated fire — so future-
        added pre-implementation states default to skip and do not silently
        re-introduce the GHI #323 defect.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
            brief_dir.mkdir(parents=True)
            statuses = ("Draft", "Pending", "Proposed", "Withdrawn", "Superseded")
            for idx, status in enumerate(statuses):
                (brief_dir / f"OBPI-9.9.9-{idx + 1:02d}-{status.lower()}.md").write_text(
                    "---\n"
                    f"id: OBPI-9.9.9-{idx + 1:02d}-{status.lower()}\n"
                    "lane: Heavy\n"
                    f"status: {status}\n"
                    "---\n\n"
                    f"## Acceptance Criteria\n\n- [ ] REQ-9.9.9-{idx + 1:02d}-01: something\n",
                    encoding="utf-8",
                )
            (root / "features").mkdir()  # no feature files
            self.assertEqual(
                audit_behave_req_tags(root),
                [],
                "Pre-implementation briefs must NOT trigger the validator",
            )

    def test_behave_req_tags_rule_39_gz_specify_born_compliant(self) -> None:
        """GHI #323 acceptance criterion #2: a brief authored via the
        ``gz specify`` template is born compliant — passes
        ``gz validate --behave-req-tags`` immediately, without manual
        waiver edits.

        ``gz specify`` emits new briefs with ``status: Draft`` (verified
        against the 5 ADR-0.0.30 OBPI scaffolds produced 2026-04-25); the
        lifecycle filter excludes Draft, so any brief-authoring session
        produces an artifact that passes the validator on commit. This
        test pins that contract programmatically by reproducing the
        ``gz specify`` template shape and asserting validator-clean output.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
            brief_dir.mkdir(parents=True)
            # Mirror the canonical gz specify template shape: heavy-lane,
            # status: Draft, REQ-IDs in Acceptance Criteria.
            (brief_dir / "OBPI-9.9.9-01-fresh-scaffold.md").write_text(
                "---\n"
                "id: OBPI-9.9.9-01-fresh-scaffold\n"
                "parent: ADR-9.9.9\n"
                "item: 1\n"
                "lane: Heavy\n"
                "status: Draft\n"
                "---\n\n"
                "## Acceptance Criteria\n\n"
                "- [ ] REQ-9.9.9-01-01: scaffolded contract holds\n"
                "- [ ] REQ-9.9.9-01-02: another requirement\n",
                encoding="utf-8",
            )
            (root / "features").mkdir()  # no feature files yet
            self.assertEqual(
                audit_behave_req_tags(root),
                [],
                "gz specify-scaffolded brief must be born compliant — no waiver "
                "edit required, no validator failure on commit (GHI #323 ac #2)",
            )

    def test_behave_req_tags_rule_39_unknown_status_defaults_skip(self) -> None:
        """GHI #323: a brief with an unrecognized status (e.g. a hypothetical
        future-added state) defaults to skip — the inverse filter is the
        structural defense against re-introducing the pre-implementation
        flagging defect."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
            brief_dir.mkdir(parents=True)
            (brief_dir / "OBPI-9.9.9-01-future.md").write_text(
                "---\n"
                "id: OBPI-9.9.9-01-future\n"
                "lane: Heavy\n"
                "status: ImplementationActive\n"
                "---\n\n"
                "## Acceptance Criteria\n\n- [ ] REQ-9.9.9-01-01: something\n",
                encoding="utf-8",
            )
            (root / "features").mkdir()
            self.assertEqual(audit_behave_req_tags(root), [])

    def test_behave_req_tags_rule_39_missing_status_defaults_skip(self) -> None:
        """GHI #323: a brief without any ``status:`` field defaults to skip.
        Briefs predating the lifecycle convention should not silently flag."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
            brief_dir.mkdir(parents=True)
            (brief_dir / "OBPI-9.9.9-01-no-status.md").write_text(
                "---\nid: OBPI-9.9.9-01-no-status\nlane: Heavy\n---\n\n"
                "## Acceptance Criteria\n\n- [ ] REQ-9.9.9-01-01: something\n",
                encoding="utf-8",
            )
            (root / "features").mkdir()
            self.assertEqual(audit_behave_req_tags(root), [])

    def test_behave_req_tags_rule_39_completed_and_validated_enforced(self) -> None:
        """GHI #323: the lifecycle filter is narrow — Completed and
        Validated briefs without BDD coverage still flag. The two post-
        implementation states are the only ones the validator fires on."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
            brief_dir.mkdir(parents=True)
            for idx, status in enumerate(("Completed", "Validated")):
                (brief_dir / f"OBPI-9.9.9-{idx + 1:02d}-{status.lower()}.md").write_text(
                    "---\n"
                    f"id: OBPI-9.9.9-{idx + 1:02d}-{status.lower()}\n"
                    "lane: Heavy\n"
                    f"status: {status}\n"
                    "---\n\n"
                    f"## Acceptance Criteria\n\n- [ ] REQ-9.9.9-{idx + 1:02d}-01: something\n",
                    encoding="utf-8",
                )
            (root / "features").mkdir()
            errors = audit_behave_req_tags(root)
            self.assertEqual(len(errors), 2, "both Completed and Validated must flag")
            error_ids = {e.message.split("`")[1] for e in errors}
            self.assertEqual(
                error_ids,
                {"OBPI-9.9.9-01-completed", "OBPI-9.9.9-02-validated"},
            )

    def test_behave_req_tags_rule_39_covered_passes(self) -> None:
        """Heavy OBPI with every REQ tagged at scenario level must pass."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-x" / "obpis"
            brief_dir.mkdir(parents=True)
            (brief_dir / "OBPI-x-01.md").write_text(
                "---\nid: OBPI-9.9.9-01-covered\nlane: Heavy\nstatus: Completed\n---\n\n"
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

    @covers("REQ-0.0.67-01-01")
    def test_skill_alignment_enumerates_multiword_subcommands(self) -> None:
        """Invariant 1 must cover multi-word subcommands, not just top-level verbs.

        Regression guard for the top-level-only enumeration defect (GHI #588):
        ``_known_cli_verbs`` walked only the top-level subparser choices, so
        ``gz obpi complete`` / ``gz adr status`` style verbs were structurally
        invisible to the orphan check and passed green by invisibility rather
        than by a wielding skill or an attested waiver. The path enumerator
        must reach nested subparsers, and every enumerated verb must be either
        wielded or waived (audit clean on the live tree).
        """
        from gzkit.governance.trust_audits.cli import _known_cli_verb_paths

        paths = _known_cli_verb_paths()
        for verb in ("obpi complete", "adr status", "obpi lock claim"):
            self.assertIn(verb, paths, f"multi-word verb `gz {verb}` not enumerated")
        self._assert_clean(audit_skill_alignment(_PROJECT_ROOT), "skill_alignment")

    @covers("REQ-0.0.67-01-02")
    def test_skill_alignment_non_vacuous(self) -> None:
        """An unwielded, unwaived multi-word verb produces exactly one skill_alignment error.

        Proves the audit is non-vacuous: removing coverage for a multi-word verb
        causes the orphan check to fire with the right artifact (GHI #588 keystone).
        """
        from gzkit.governance.trust_audits.cli import _known_cli_verb_paths

        real_paths = _known_cli_verb_paths()
        synthetic = "fake synthetic audit-test-verb"
        patched_paths = real_paths | frozenset([synthetic])

        with patch(
            "gzkit.governance.trust_audits.cli._known_cli_verb_paths",
            return_value=patched_paths,
        ):
            errors = audit_skill_alignment(_PROJECT_ROOT)

        flagged = [e for e in errors if e.type == "skill_alignment"]
        self.assertEqual(
            len(flagged),
            1,
            f"expected exactly 1 skill_alignment error for the synthetic verb; got {flagged}",
        )
        self.assertEqual(flagged[0].artifact, f"gz {synthetic}")

    @covers("REQ-0.0.67-01-03")
    def test_skill_alignment_cascade_and_stale(self) -> None:
        """Group-cascade waivers cover subcommands; stale waivers are detected.

        Verifies _verb_path_waived accepts an exact key or its top-level group prefix,
        and _waiver_targets_live_verb flags keys not present in the registered tree.
        """
        from gzkit.governance.trust_audits.cli import (
            _NO_SKILL_VERBS,
            _known_cli_verb_paths,
            _verb_path_waived,
            _waiver_targets_live_verb,
        )

        # Exact key and group-prefix cascade
        self.assertTrue(_verb_path_waived("task"), "exact key must be waived")
        self.assertTrue(_verb_path_waived("task start"), "group cascade must waive subcommand")
        self.assertFalse(_verb_path_waived("gz-fake-unregistered"), "non-entry must not be waived")

        # Stale waiver detection
        dummy_paths: frozenset[str] = frozenset(["task start", "task complete"])
        self.assertTrue(
            _waiver_targets_live_verb("task", dummy_paths), "live group key must be recognized"
        )
        self.assertFalse(
            _waiver_targets_live_verb("orphan-key", dummy_paths), "stale key must not be recognized"
        )

        # Live tree carries no stale _NO_SKILL_VERBS entries
        verb_paths = _known_cli_verb_paths()
        stale = [k for k in _NO_SKILL_VERBS if not _waiver_targets_live_verb(k, verb_paths)]
        self.assertFalse(stale, f"stale _NO_SKILL_VERBS entries found: {stale}")

    @covers("REQ-0.0.67-01-04")
    def test_skill_alignment_cli_verbs_top_level_only(self) -> None:
        """_known_cli_verbs() returns top-level-only tokens; cli-alignment stays green.

        Coupled-surface coherence guard: OBPI-0.0.67-01 must not alter
        _known_cli_verbs() semantics, which audit_cli_alignment depends on.
        """
        from gzkit.governance.trust_audits.cli import _known_cli_verbs

        top_level = _known_cli_verbs()
        multi_word = [v for v in top_level if " " in v]
        self.assertFalse(
            multi_word,
            f"_known_cli_verbs() must return top-level-only tokens; got multi-word: {multi_word}",
        )
        self._assert_clean(audit_cli_alignment(_PROJECT_ROOT), "cli_alignment")

    def test_advisory_scorecard_selftest(self) -> None:
        self._assert_clean(audit_advisory_scorecard(_PROJECT_ROOT), "advisory_scorecard")

    def test_reconcile_freshness_rule_4(self) -> None:
        # Reconcile audit is a no-op when no reconcile events exist; it must
        # never hard-fail on current state until the event types land.
        self._assert_clean(audit_reconcile_freshness(_PROJECT_ROOT), "reconcile_freshness")

    @covers("REQ-0.0.17-04-09")
    def test_adr_taxonomy_rule_X(self) -> None:
        # REQ-0.0.17-04-09: lock-in passes on the live tree (backfill landed).
        self._assert_clean(audit_adr_taxonomy(_PROJECT_ROOT), "taxonomy")

    def test_brief_headings_ghi_238(self) -> None:
        """GHI #238: live tree has no H2 drift for evidence sections."""
        self._assert_clean(audit_brief_headings(_PROJECT_ROOT), "brief_headings")

    def test_brief_cross_references_ghi_436(self) -> None:
        """GHI #436: live tree has no unresolvable brief identifier references."""
        self._assert_clean(audit_brief_cross_references(_PROJECT_ROOT), "brief_cross_references")

    def test_brief_demo_section_ghi_431(self) -> None:
        """GHI #431: live tree has no active heavy-lane CLI brief missing Demo."""
        self._assert_clean(audit_brief_demo_section(_PROJECT_ROOT), "brief_demo_section")


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


class BriefCrossReferencesAuditNegativeCases(unittest.TestCase):
    """GHI #436: unresolvable brief cross-references are flagged."""

    @staticmethod
    def _scaffold_adr(root: Path) -> Path:
        """Create one ADR + one OBPI so resolvable identifiers exist."""
        adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.1-anchor"
        obpi_dir = adr_dir / "obpis"
        obpi_dir.mkdir(parents=True)
        (adr_dir / "ADR-0.0.1-anchor.md").write_text("# Anchor\n", encoding="utf-8")
        return obpi_dir

    def test_unresolvable_obpi_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpi_dir = self._scaffold_adr(root)
            brief = obpi_dir / "OBPI-0.0.1-01-driver.md"
            brief.write_text(
                "# OBPI-0.0.1-01\n\n"
                "## Objective\n\n"
                "Stage references OBPI-0.0.99-05 which does not exist.\n",
                encoding="utf-8",
            )
            errors = audit_brief_cross_references(root)
            self.assertTrue(errors, "Unresolvable OBPI reference must flag")
            self.assertEqual(errors[0].type, "brief_cross_references")
            self.assertIn("OBPI-0.0.99-05", errors[0].message)

    def test_resolvable_obpi_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpi_dir = self._scaffold_adr(root)
            sibling = obpi_dir / "OBPI-0.0.1-02-sibling.md"
            sibling.write_text("# OBPI-0.0.1-02\n", encoding="utf-8")
            brief = obpi_dir / "OBPI-0.0.1-01-driver.md"
            brief.write_text(
                "# OBPI-0.0.1-01\n\n## Objective\n\nReferences OBPI-0.0.1-02 sibling.\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_brief_cross_references(root), [])

    def test_prefix_match_accepted(self) -> None:
        """GHI #436: bare prefix `OBPI-0.0.1-02` resolves to suffix-extended file."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpi_dir = self._scaffold_adr(root)
            (obpi_dir / "OBPI-0.0.1-02-real-slug.md").write_text(
                "# OBPI-0.0.1-02\n", encoding="utf-8"
            )
            brief = obpi_dir / "OBPI-0.0.1-01-driver.md"
            brief.write_text(
                "# OBPI-0.0.1-01\n\n## Objective\n\nReferences OBPI-0.0.1-02 bare prefix.\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_brief_cross_references(root), [])

    def test_unresolvable_adr_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpi_dir = self._scaffold_adr(root)
            brief = obpi_dir / "OBPI-0.0.1-01-driver.md"
            brief.write_text(
                "# OBPI-0.0.1-01\n\n## Objective\n\nFollows ADR-0.99.0 doctrine.\n",
                encoding="utf-8",
            )
            errors = audit_brief_cross_references(root)
            self.assertTrue(errors)
            self.assertIn("ADR-0.99.0", errors[0].message)

    def test_skip_marker_suppresses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpi_dir = self._scaffold_adr(root)
            brief = obpi_dir / "OBPI-0.0.1-01-driver.md"
            brief.write_text(
                "# OBPI-0.0.1-01\n\n"
                "## Objective\n\n"
                "<!-- gz-validate-skip: brief-cross-references -->\n"
                "Forward-references OBPI-0.0.99-05 (will land later).\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_brief_cross_references(root), [])

    def test_fenced_code_block_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpi_dir = self._scaffold_adr(root)
            brief = obpi_dir / "OBPI-0.0.1-01-driver.md"
            brief.write_text(
                "# OBPI-0.0.1-01\n\n"
                "## Objective\n\n"
                "```bash\n"
                "$ ls docs/design/adr/foundation/ADR-0.99.0-example/\n"
                "```\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_brief_cross_references(root), [])

    def test_self_reference_accepted(self) -> None:
        """Brief self-references in frontmatter / heading must not flag."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpi_dir = self._scaffold_adr(root)
            brief = obpi_dir / "OBPI-0.0.1-07-fresh.md"
            brief.write_text(
                "# OBPI-0.0.1-07-fresh\n\n"
                "id: OBPI-0.0.1-07-fresh\n\n"
                "## Objective\n\nAuthored as OBPI-0.0.1-07.\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_brief_cross_references(root), [])

    def test_bare_obpi_prose_reference_resolves_to_adr(self) -> None:
        """Bare ``OBPI-X.Y.Z`` (no sequence) is prose for the ADR family."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpi_dir = self._scaffold_adr(root)
            brief = obpi_dir / "OBPI-0.0.1-01-driver.md"
            brief.write_text(
                "# OBPI-0.0.1-01\n\n## Objective\n\nThe OBPI-0.0.1 series.\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_brief_cross_references(root), [])

    def test_no_adr_dir_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(audit_brief_cross_references(Path(tmp)), [])


class BriefDemoSectionAuditNegativeCases(unittest.TestCase):
    """GHI #431: heavy-lane CLI-shipping briefs without ## Demo are flagged."""

    @staticmethod
    def _brief_dir(root: Path) -> Path:
        path = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.1-anchor" / "obpis"
        path.mkdir(parents=True)
        return path

    @staticmethod
    def _heavy_cli_brief_text(*, status: str = "Draft", with_demo: bool = False) -> str:
        demo = "\n## Demo\n\n```bash\nuv run gz example --json\n```\n" if with_demo else ""
        return (
            "---\n"
            "id: OBPI-0.0.1-01-driver\n"
            "parent: ADR-0.0.1\n"
            "item: 1\n"
            "lane: Heavy\n"
            f"status: {status}\n"
            "---\n\n"
            "# OBPI-0.0.1-01-driver\n\n"
            "## Allowed Paths\n\n"
            "- `src/gzkit/commands/example_cmd.py`\n"
            "- `tests/commands/test_example_cmd.py`\n\n"
            f"## Verification\n\n```bash\nuv run gz lint\n```\n{demo}\n"
            "## Acceptance Criteria\n\n- REQ-0.0.1-01-01\n"
        )

    def test_heavy_cli_draft_without_demo_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = self._brief_dir(root) / "OBPI-0.0.1-01-driver.md"
            brief.write_text(self._heavy_cli_brief_text(status="Draft"), encoding="utf-8")
            errors = audit_brief_demo_section(root)
            self.assertEqual(len(errors), 1, msg=str(errors))
            self.assertEqual(errors[0].type, "brief_demo_section")
            self.assertIn("`## Demo`", errors[0].message)

    def test_heavy_cli_in_progress_without_demo_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = self._brief_dir(root) / "OBPI-0.0.1-01-driver.md"
            brief.write_text(self._heavy_cli_brief_text(status="in_progress"), encoding="utf-8")
            self.assertTrue(audit_brief_demo_section(root))

    def test_heavy_cli_with_demo_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = self._brief_dir(root) / "OBPI-0.0.1-01-driver.md"
            brief.write_text(
                self._heavy_cli_brief_text(status="Draft", with_demo=True),
                encoding="utf-8",
            )
            self.assertEqual(audit_brief_demo_section(root), [])

    def test_completed_status_grandfathered(self) -> None:
        """Terminal-status briefs predate the rule and are not re-audited."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = self._brief_dir(root) / "OBPI-0.0.1-01-driver.md"
            brief.write_text(
                self._heavy_cli_brief_text(status="attested_completed"),
                encoding="utf-8",
            )
            self.assertEqual(audit_brief_demo_section(root), [])

    def test_pending_backlog_not_gated(self) -> None:
        """Backlog (pending) briefs carry queued scope; gate fires when activated."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = self._brief_dir(root) / "OBPI-0.0.1-01-driver.md"
            brief.write_text(self._heavy_cli_brief_text(status="Pending"), encoding="utf-8")
            self.assertEqual(audit_brief_demo_section(root), [])

    def test_lite_lane_not_gated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = self._brief_dir(root) / "OBPI-0.0.1-01-driver.md"
            text = self._heavy_cli_brief_text(status="Draft").replace("lane: Heavy", "lane: Lite")
            brief.write_text(text, encoding="utf-8")
            self.assertEqual(audit_brief_demo_section(root), [])

    def test_no_cli_surface_not_gated(self) -> None:
        """Heavy-lane brief without CLI surface in Allowed Paths is not gated."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = self._brief_dir(root) / "OBPI-0.0.1-01-driver.md"
            text = self._heavy_cli_brief_text(status="Draft").replace(
                "- `src/gzkit/commands/example_cmd.py`",
                "- `src/gzkit/governance/example.py`",
            )
            brief.write_text(text, encoding="utf-8")
            self.assertEqual(audit_brief_demo_section(root), [])

    def test_parser_artifacts_surface_gated(self) -> None:
        """Allowed-paths touching parser_artifacts.py triggers the gate."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = self._brief_dir(root) / "OBPI-0.0.1-01-driver.md"
            text = self._heavy_cli_brief_text(status="Draft").replace(
                "- `src/gzkit/commands/example_cmd.py`",
                "- `src/gzkit/cli/parser_artifacts.py`",
            )
            brief.write_text(text, encoding="utf-8")
            self.assertTrue(audit_brief_demo_section(root))

    def test_skip_marker_suppresses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = self._brief_dir(root) / "OBPI-0.0.1-01-driver.md"
            text = (
                self._heavy_cli_brief_text(status="Draft").rstrip()
                + "\n\n<!-- gz-validate-skip: brief-demo-section -->\n"
            )
            brief.write_text(text, encoding="utf-8")
            self.assertEqual(audit_brief_demo_section(root), [])

    def test_no_adr_dir_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(audit_brief_demo_section(Path(tmp)), [])


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

    def test_release_prefixed_manifest_satisfies_audit(self) -> None:
        """GHI #739: a minor release from `gz closeout` files RELEASE-v{version}.md.

        The escape was hardcoded to a ``PATCH-`` prefix, which forced every
        minor release to file an artifact mislabelled as a patch
        (``PATCH-v0.30.0.md``, ``PATCH-v0.34.0.md`` are both minor). Both
        prefixes are in-flight evidence for the same window.
        """
        import tempfile  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._init_empty_git(root)
            self._write_pyproject(root, "9.9.0")
            manifest_dir = root / "docs" / "releases"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "RELEASE-v9.9.0.md").write_text(
                "# Minor Release: v9.9.0\n", encoding="utf-8"
            )
            self.assertEqual(
                audit_version_release(root),
                [],
                msg="RELEASE-v{version}.md must be equivalent in-flight evidence",
            )

    def test_release_prefixed_manifest_for_different_version_does_not_satisfy(self) -> None:
        """Version matching binds on the RELEASE- arm exactly as on the PATCH- arm."""
        import tempfile  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._init_empty_git(root)
            self._write_pyproject(root, "9.9.0")
            manifest_dir = root / "docs" / "releases"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "RELEASE-v9.8.0.md").write_text(
                "# Minor Release: v9.8.0\n", encoding="utf-8"
            )
            errors = audit_version_release(root)
            self.assertEqual(len(errors), 1, msg=f"expected one violation, got {errors}")


if __name__ == "__main__":
    unittest.main()
