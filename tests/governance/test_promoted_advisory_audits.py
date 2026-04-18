"""Promoted advisory-rule audits (GHIs #202–#214).

Each test is the unit-level entry to an audit that also runs as a ``gz
validate --<scope>`` flag. Keeping these under ``tests/governance/`` locks
the promotion against silent regression — if the audit returns errors on
the current tree, the test fails and the pre-commit suite catches it.

The canonical advisory rules catalogue lives at
``docs/governance/advisory-rules-audit.md``.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.governance.trust_audits import (
    audit_advisory_scorecard,
    audit_behave_req_tags,
    audit_class_size,
    audit_pool_adr_isolation,
    audit_pydantic_models,
    audit_reconcile_freshness,
    audit_skill_alignment,
    audit_test_tiers,
    audit_utf8_prefix,
    audit_version_release,
)

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

    def test_skill_alignment_invariant_1(self) -> None:
        self._assert_clean(audit_skill_alignment(_PROJECT_ROOT), "skill_alignment")

    def test_advisory_scorecard_selftest(self) -> None:
        self._assert_clean(audit_advisory_scorecard(_PROJECT_ROOT), "advisory_scorecard")

    def test_reconcile_freshness_rule_4(self) -> None:
        # Reconcile audit is a no-op when no reconcile events exist; it must
        # never hard-fail on current state until the event types land.
        self._assert_clean(audit_reconcile_freshness(_PROJECT_ROOT), "reconcile_freshness")


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
