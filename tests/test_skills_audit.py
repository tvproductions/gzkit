"""Tests for skill mirror identity contract enforcement."""

import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.skills import audit_skills
from gzkit.sync import sync_skill_mirrors


def _skill_frontmatter(
    name: str, **overrides: str | dict[str, str]
) -> dict[str, str | dict[str, str]]:
    fields: dict[str, str | dict[str, str]] = {
        "name": name,
        "description": "Demo skill",
        "lifecycle_state": "active",
        "owner": "gzkit-governance",
        "last_reviewed": date.today().isoformat(),
    }
    fields.update(overrides)
    return fields


def _write_skill(
    project_root: Path,
    root_rel: str,
    skill_dir_name: str,
    *,
    frontmatter: dict[str, str | dict[str, str]] | None = None,
    include_frontmatter: bool = True,
) -> None:
    skill_dir = project_root / root_rel / skill_dir_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"

    if not include_frontmatter:
        skill_file.write_text("# SKILL.md\n\nMirror without frontmatter.\n", encoding="utf-8")
        return

    lines = ["---"]
    frontmatter = frontmatter or _skill_frontmatter(skill_dir_name)
    for key, value in frontmatter.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for nested_key, nested_value in value.items():
                lines.append(f"  {nested_key}: {nested_value}")
            continue
        lines.append(f"{key}: {value}")
    lines.extend(
        [
            "---",
            "",
            "# SKILL.md",
            "",
            "Mirror contract test skill.",
            "",
        ]
    )
    skill_file.write_text("\n".join(lines), encoding="utf-8")


class TestSkillAuditMirrorContracts(unittest.TestCase):
    """Validate fail-closed mirror identity contract behavior."""

    def test_mirror_field_drift_blocks_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            _write_skill(project_root, config.paths.skills, "demo-skill")
            _write_skill(project_root, config.paths.codex_skills, "demo-skill")
            _write_skill(
                project_root,
                config.paths.claude_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter("demo-skill", owner="other-owner"),
            )
            _write_skill(project_root, config.paths.copilot_skills, "demo-skill")

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    issue.path.endswith(".claude/skills/demo-skill/SKILL.md")
                    and issue.code == "SKA-MIRROR-FIELD-DRIFT"
                    and issue.blocking
                    and "Mirror field drift for 'owner'" in issue.message
                    for issue in report.issues
                )
            )

    def test_optional_capability_drift_blocks_audit_when_declared_in_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            _write_skill(
                project_root,
                config.paths.skills,
                "demo-skill",
                frontmatter=_skill_frontmatter("demo-skill", compatibility="GovZero v6"),
            )
            _write_skill(
                project_root,
                config.paths.codex_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter("demo-skill", compatibility="Different contract"),
            )
            _write_skill(
                project_root,
                config.paths.claude_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter("demo-skill", compatibility="GovZero v6"),
            )
            _write_skill(
                project_root,
                config.paths.copilot_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter("demo-skill", compatibility="GovZero v6"),
            )

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    "Mirror field drift for 'compatibility'" in issue.message
                    for issue in report.issues
                )
            )

    def test_optional_capability_fields_can_be_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            _write_skill(project_root, config.paths.skills, "demo-skill")
            _write_skill(project_root, config.paths.codex_skills, "demo-skill")
            _write_skill(project_root, config.paths.claude_skills, "demo-skill")
            _write_skill(project_root, config.paths.copilot_skills, "demo-skill")

            report = audit_skills(project_root, config)
            self.assertTrue(report.valid)

    def test_invalid_known_metadata_key_blocks_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            _write_skill(
                project_root,
                config.paths.skills,
                "demo-skill",
                frontmatter=_skill_frontmatter(
                    "demo-skill", metadata={"govzero_layer": "Layer 99 - Unknown"}
                ),
            )
            _write_skill(
                project_root,
                config.paths.codex_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter(
                    "demo-skill", metadata={"govzero_layer": "Layer 99 - Unknown"}
                ),
            )
            _write_skill(
                project_root,
                config.paths.claude_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter(
                    "demo-skill", metadata={"govzero_layer": "Layer 99 - Unknown"}
                ),
            )
            _write_skill(
                project_root,
                config.paths.copilot_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter(
                    "demo-skill", metadata={"govzero_layer": "Layer 99 - Unknown"}
                ),
            )

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any("Invalid metadata.govzero_layer" in issue.message for issue in report.issues)
            )

    def test_unknown_metadata_keys_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            metadata = {
                "govzero_layer": "Layer 1 - Evidence Gathering",
                "custom-key": "custom-value",
            }
            _write_skill(
                project_root,
                config.paths.skills,
                "demo-skill",
                frontmatter=_skill_frontmatter("demo-skill", metadata=metadata),
            )
            _write_skill(
                project_root,
                config.paths.codex_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter("demo-skill", metadata=metadata),
            )
            _write_skill(
                project_root,
                config.paths.claude_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter("demo-skill", metadata=metadata),
            )
            _write_skill(
                project_root,
                config.paths.copilot_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter("demo-skill", metadata=metadata),
            )

            report = audit_skills(project_root, config)
            self.assertTrue(report.valid)

    def test_missing_mirror_directory_blocks_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            _write_skill(project_root, config.paths.skills, "demo-skill")
            _write_skill(project_root, config.paths.codex_skills, "demo-skill")
            _write_skill(project_root, config.paths.copilot_skills, "demo-skill")

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    issue.path.endswith(".claude/skills/demo-skill")
                    and issue.code == "SKA-MIRROR-DIR-MISSING"
                    and issue.blocking
                    and "Missing mirrored skill directory." in issue.message
                    for issue in report.issues
                )
            )

    def test_stale_mirror_directory_is_non_blocking_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            _write_skill(project_root, config.paths.skills, "demo-skill")
            _write_skill(project_root, config.paths.codex_skills, "demo-skill")
            _write_skill(project_root, config.paths.claude_skills, "demo-skill")
            _write_skill(project_root, config.paths.copilot_skills, "demo-skill")
            _write_skill(project_root, config.paths.claude_skills, "stale-skill")

            report = audit_skills(project_root, config)
            self.assertTrue(report.valid)
            self.assertTrue(
                any(
                    issue.path.endswith(".claude/skills/stale-skill")
                    and issue.code == "SKA-MIRROR-DIR-UNEXPECTED"
                    and issue.severity == "warning"
                    and not issue.blocking
                    for issue in report.issues
                )
            )

    def test_issue_codes_are_present_and_order_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            _write_skill(
                project_root,
                config.paths.skills,
                "demo-skill",
                frontmatter=_skill_frontmatter("demo-skill", lifecycle_state="invalid"),
            )
            _write_skill(project_root, config.paths.codex_skills, "demo-skill")
            _write_skill(project_root, config.paths.copilot_skills, "demo-skill")

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(all(issue.code for issue in report.issues))
            ordered = sorted(
                report.issues,
                key=lambda issue: (issue.path, issue.code, issue.message),
            )
            self.assertEqual(
                [(i.path, i.code, i.message) for i in report.issues],
                [(i.path, i.code, i.message) for i in ordered],
            )

    def test_stale_last_reviewed_blocks_audit_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            stale_date = (date.today() - timedelta(days=120)).isoformat()
            stale_frontmatter = _skill_frontmatter("demo-skill", last_reviewed=stale_date)

            _write_skill(
                project_root, config.paths.skills, "demo-skill", frontmatter=stale_frontmatter
            )
            _write_skill(
                project_root, config.paths.codex_skills, "demo-skill", frontmatter=stale_frontmatter
            )
            _write_skill(
                project_root,
                config.paths.claude_skills,
                "demo-skill",
                frontmatter=stale_frontmatter,
            )
            _write_skill(
                project_root,
                config.paths.copilot_skills,
                "demo-skill",
                frontmatter=stale_frontmatter,
            )

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(any(issue.code == "SKA-LAST-REVIEWED-STALE" for issue in report.issues))

    def test_max_review_age_override_allows_older_review_dates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            stale_date = (date.today() - timedelta(days=120)).isoformat()
            stale_frontmatter = _skill_frontmatter("demo-skill", last_reviewed=stale_date)

            _write_skill(
                project_root, config.paths.skills, "demo-skill", frontmatter=stale_frontmatter
            )
            _write_skill(
                project_root, config.paths.codex_skills, "demo-skill", frontmatter=stale_frontmatter
            )
            _write_skill(
                project_root,
                config.paths.claude_skills,
                "demo-skill",
                frontmatter=stale_frontmatter,
            )
            _write_skill(
                project_root,
                config.paths.copilot_skills,
                "demo-skill",
                frontmatter=stale_frontmatter,
            )

            report = audit_skills(project_root, config, max_review_age_days=365)
            self.assertTrue(report.valid)
            self.assertFalse(
                any(issue.code == "SKA-LAST-REVIEWED-STALE" for issue in report.issues)
            )

    def test_deprecated_skill_requires_deprecation_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            frontmatter = _skill_frontmatter("demo-skill", lifecycle_state="deprecated")

            _write_skill(project_root, config.paths.skills, "demo-skill", frontmatter=frontmatter)
            _write_skill(
                project_root, config.paths.codex_skills, "demo-skill", frontmatter=frontmatter
            )
            _write_skill(
                project_root, config.paths.claude_skills, "demo-skill", frontmatter=frontmatter
            )
            _write_skill(
                project_root, config.paths.copilot_skills, "demo-skill", frontmatter=frontmatter
            )

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(issue.code == "SKA-DEPRECATION-FIELD-MISSING" for issue in report.issues)
            )

    def test_valid_lifecycle_transition_metadata_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            frontmatter = _skill_frontmatter(
                "demo-skill",
                lifecycle_state="active",
                lifecycle_transition_from="draft",
                lifecycle_transition_date=date.today().isoformat(),
                lifecycle_transition_reason="Skill reached production readiness.",
                lifecycle_transition_evidence="Reviewed by maintainer; sync + audit passed.",
            )

            _write_skill(project_root, config.paths.skills, "demo-skill", frontmatter=frontmatter)
            _write_skill(
                project_root, config.paths.codex_skills, "demo-skill", frontmatter=frontmatter
            )
            _write_skill(
                project_root, config.paths.claude_skills, "demo-skill", frontmatter=frontmatter
            )
            _write_skill(
                project_root, config.paths.copilot_skills, "demo-skill", frontmatter=frontmatter
            )

            report = audit_skills(project_root, config)
            self.assertTrue(report.valid)

    def test_transition_metadata_missing_fields_blocks_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            frontmatter = _skill_frontmatter(
                "demo-skill",
                lifecycle_state="active",
                lifecycle_transition_from="draft",
            )

            _write_skill(project_root, config.paths.skills, "demo-skill", frontmatter=frontmatter)
            _write_skill(
                project_root, config.paths.codex_skills, "demo-skill", frontmatter=frontmatter
            )
            _write_skill(
                project_root, config.paths.claude_skills, "demo-skill", frontmatter=frontmatter
            )
            _write_skill(
                project_root, config.paths.copilot_skills, "demo-skill", frontmatter=frontmatter
            )

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    issue.code == "SKA-LIFECYCLE-TRANSITION-FIELDS-INCOMPLETE"
                    for issue in report.issues
                )
            )

    def test_unsupported_lifecycle_transition_blocks_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            frontmatter = _skill_frontmatter(
                "demo-skill",
                lifecycle_state="retired",
                lifecycle_transition_from="active",
                lifecycle_transition_date=date.today().isoformat(),
                lifecycle_transition_reason="Retired directly.",
                lifecycle_transition_evidence="No intermediate deprecation stage.",
                deprecation_replaced_by="new-skill",
                deprecation_migration="See migration guide",
                deprecation_communication="Announced in release notes",
                deprecation_announced_on=date.today().isoformat(),
                retired_on=date.today().isoformat(),
            )

            _write_skill(project_root, config.paths.skills, "demo-skill", frontmatter=frontmatter)
            _write_skill(
                project_root, config.paths.codex_skills, "demo-skill", frontmatter=frontmatter
            )
            _write_skill(
                project_root, config.paths.claude_skills, "demo-skill", frontmatter=frontmatter
            )
            _write_skill(
                project_root, config.paths.copilot_skills, "demo-skill", frontmatter=frontmatter
            )

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(issue.code == "SKA-LIFECYCLE-TRANSITION-UNSUPPORTED" for issue in report.issues)
            )

    def test_transition_field_drift_blocks_audit_when_declared_in_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            canonical_frontmatter = _skill_frontmatter(
                "demo-skill",
                lifecycle_state="active",
                lifecycle_transition_from="draft",
                lifecycle_transition_date=date.today().isoformat(),
                lifecycle_transition_reason="Ready",
                lifecycle_transition_evidence="Audit evidence recorded.",
            )

            _write_skill(
                project_root,
                config.paths.skills,
                "demo-skill",
                frontmatter=canonical_frontmatter,
            )
            _write_skill(
                project_root,
                config.paths.codex_skills,
                "demo-skill",
                frontmatter=canonical_frontmatter,
            )
            _write_skill(
                project_root,
                config.paths.claude_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter(
                    "demo-skill",
                    lifecycle_state="active",
                    lifecycle_transition_from="draft",
                    lifecycle_transition_date=date.today().isoformat(),
                    lifecycle_transition_reason="Different reason",
                    lifecycle_transition_evidence="Audit evidence recorded.",
                ),
            )
            _write_skill(
                project_root,
                config.paths.copilot_skills,
                "demo-skill",
                frontmatter=canonical_frontmatter,
            )

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    issue.code == "SKA-MIRROR-FIELD-DRIFT"
                    and "lifecycle_transition_reason" in issue.message
                    for issue in report.issues
                )
            )

    def test_active_skill_forbids_deprecation_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            frontmatter = _skill_frontmatter(
                "demo-skill",
                lifecycle_state="active",
                deprecation_replaced_by="new-skill",
            )

            _write_skill(project_root, config.paths.skills, "demo-skill", frontmatter=frontmatter)
            _write_skill(
                project_root, config.paths.codex_skills, "demo-skill", frontmatter=frontmatter
            )
            _write_skill(
                project_root, config.paths.claude_skills, "demo-skill", frontmatter=frontmatter
            )
            _write_skill(
                project_root, config.paths.copilot_skills, "demo-skill", frontmatter=frontmatter
            )

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(issue.code == "SKA-DEPRECATION-FIELD-FORBIDDEN" for issue in report.issues)
            )

    def test_retired_skill_requires_retired_on(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            frontmatter = _skill_frontmatter(
                "demo-skill",
                lifecycle_state="retired",
                deprecation_replaced_by="new-skill",
                deprecation_migration="See migration guide",
                deprecation_communication="Announced in release notes",
                deprecation_announced_on=date.today().isoformat(),
            )

            _write_skill(project_root, config.paths.skills, "demo-skill", frontmatter=frontmatter)
            _write_skill(
                project_root, config.paths.codex_skills, "demo-skill", frontmatter=frontmatter
            )
            _write_skill(
                project_root, config.paths.claude_skills, "demo-skill", frontmatter=frontmatter
            )
            _write_skill(
                project_root, config.paths.copilot_skills, "demo-skill", frontmatter=frontmatter
            )

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    issue.code == "SKA-DEPRECATION-FIELD-MISSING" and "retired_on" in issue.message
                    for issue in report.issues
                )
            )

    def test_deprecation_field_drift_blocks_audit_when_declared_in_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            canonical_frontmatter = _skill_frontmatter(
                "demo-skill",
                lifecycle_state="deprecated",
                deprecation_replaced_by="new-skill",
                deprecation_migration="See migration guide",
                deprecation_communication="Announced in release notes",
                deprecation_announced_on=date.today().isoformat(),
            )

            _write_skill(
                project_root,
                config.paths.skills,
                "demo-skill",
                frontmatter=canonical_frontmatter,
            )
            _write_skill(
                project_root,
                config.paths.codex_skills,
                "demo-skill",
                frontmatter=canonical_frontmatter,
            )
            _write_skill(
                project_root,
                config.paths.claude_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter(
                    "demo-skill",
                    lifecycle_state="deprecated",
                    deprecation_replaced_by="new-skill",
                    deprecation_migration="Different path",
                    deprecation_communication="Announced in release notes",
                    deprecation_announced_on=date.today().isoformat(),
                ),
            )
            _write_skill(
                project_root,
                config.paths.copilot_skills,
                "demo-skill",
                frontmatter=canonical_frontmatter,
            )

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    issue.code == "SKA-MIRROR-FIELD-DRIFT"
                    and "deprecation_migration" in issue.message
                    for issue in report.issues
                )
            )

    def test_mirror_directory_name_must_be_kebab_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            _write_skill(project_root, config.paths.skills, "demo-skill")
            _write_skill(project_root, config.paths.codex_skills, "demo-skill")
            _write_skill(project_root, config.paths.claude_skills, "demo-skill")
            _write_skill(project_root, config.paths.copilot_skills, "demo-skill")
            _write_skill(project_root, config.paths.claude_skills, "DemoSkill")

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    issue.path.endswith(".claude/skills/DemoSkill")
                    and "Mirrored skill directory name must be kebab-case." in issue.message
                    for issue in report.issues
                )
            )

    def test_missing_mirror_skill_file_blocks_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            _write_skill(project_root, config.paths.skills, "demo-skill")
            _write_skill(project_root, config.paths.codex_skills, "demo-skill")
            _write_skill(project_root, config.paths.claude_skills, "demo-skill")
            (project_root / config.paths.copilot_skills / "demo-skill").mkdir(
                parents=True, exist_ok=True
            )

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    issue.path.endswith(".github/skills/demo-skill")
                    and "Missing mirrored SKILL.md." in issue.message
                    for issue in report.issues
                )
            )

    def test_mirror_frontmatter_name_must_match_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            _write_skill(project_root, config.paths.skills, "demo-skill")
            _write_skill(project_root, config.paths.codex_skills, "demo-skill")
            _write_skill(
                project_root,
                config.paths.claude_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter("wrong-name"),
            )
            _write_skill(project_root, config.paths.copilot_skills, "demo-skill")

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    "Mirror frontmatter name 'wrong-name' must match mirrored directory name"
                    in issue.message
                    for issue in report.issues
                )
            )

    def test_sync_skill_mirrors_remediates_identity_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            _write_skill(project_root, config.paths.skills, "demo-skill")
            _write_skill(
                project_root,
                config.paths.codex_skills,
                "demo-skill",
                frontmatter={"name": "demo-skill", "description": "stale"},
            )
            _write_skill(
                project_root,
                config.paths.claude_skills,
                "demo-skill",
                include_frontmatter=False,
            )
            _write_skill(project_root, config.paths.copilot_skills, "demo-skill")

            before = audit_skills(project_root, config)
            self.assertFalse(before.valid)

            updated = sync_skill_mirrors(project_root, config)
            self.assertIn(".agents/skills/demo-skill/SKILL.md", updated)
            self.assertIn(".claude/skills/demo-skill/SKILL.md", updated)
            canonical = (project_root / config.paths.skills / "demo-skill" / "SKILL.md").read_text(
                encoding="utf-8"
            )
            copilot = (
                project_root / config.paths.copilot_skills / "demo-skill" / "SKILL.md"
            ).read_text(encoding="utf-8")
            self.assertEqual(canonical, copilot)

            after = audit_skills(project_root, config)
            self.assertTrue(after.valid)


def _write_skill_with_body(
    project_root: Path,
    root_rel: str,
    skill_dir_name: str,
    body: str,
) -> Path:
    """Write a canonical-style SKILL.md with a custom body. Returns skill dir."""
    skill_dir = project_root / root_rel / skill_dir_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    frontmatter = _skill_frontmatter(skill_dir_name)
    lines = ["---"]
    for key, value in frontmatter.items():
        lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")
    lines.append(body)
    lines.append("")
    (skill_dir / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")
    return skill_dir


class TestSkillAuditMirrorPackageParity(unittest.TestCase):
    """Mirror parity must verify body and asset parity, not just frontmatter (GHI #132)."""

    def _base_project(self, tmpdir: str) -> tuple[Path, GzkitConfig]:
        project_root = Path(tmpdir)
        config = GzkitConfig(project_name="gzkit-test")
        for root_rel in (
            config.paths.skills,
            config.paths.codex_skills,
            config.paths.claude_skills,
            config.paths.copilot_skills,
        ):
            _write_skill_with_body(project_root, root_rel, "demo-skill", "Canonical body line.")
        return project_root, config

    def test_mirror_body_drift_blocks_audit(self) -> None:
        """When a mirror's SKILL.md body differs from canonical, audit blocks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root, config = self._base_project(tmpdir)
            _write_skill_with_body(
                project_root,
                config.paths.claude_skills,
                "demo-skill",
                "Mirror body has drifted content.",
            )

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    issue.path.endswith(".claude/skills/demo-skill/SKILL.md")
                    and issue.code == "SKA-MIRROR-BODY-DRIFT"
                    and issue.blocking
                    for issue in report.issues
                ),
                f"expected SKA-MIRROR-BODY-DRIFT; got {[i.code for i in report.issues]}",
            )

    def test_mirror_body_identical_passes(self) -> None:
        """Identical bodies must not trigger body-drift findings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root, config = self._base_project(tmpdir)
            report = audit_skills(project_root, config)
            self.assertFalse(any(issue.code == "SKA-MIRROR-BODY-DRIFT" for issue in report.issues))

    def test_mirror_asset_missing_blocks_audit(self) -> None:
        """Canonical asset not present in a mirror is a blocking error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root, config = self._base_project(tmpdir)
            canonical_asset = (
                project_root / config.paths.skills / "demo-skill" / "assets" / "template.md"
            )
            canonical_asset.parent.mkdir(parents=True, exist_ok=True)
            canonical_asset.write_text("canonical asset content", encoding="utf-8")
            for mirror_rel in (
                config.paths.codex_skills,
                config.paths.copilot_skills,
            ):
                mirror_asset = project_root / mirror_rel / "demo-skill" / "assets" / "template.md"
                mirror_asset.parent.mkdir(parents=True, exist_ok=True)
                mirror_asset.write_text("canonical asset content", encoding="utf-8")

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    issue.path.endswith(".claude/skills/demo-skill/assets/template.md")
                    and issue.code == "SKA-MIRROR-ASSET-MISSING"
                    and issue.blocking
                    for issue in report.issues
                )
            )

    def test_mirror_asset_drift_blocks_audit(self) -> None:
        """Shared asset with drifted content is a blocking error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root, config = self._base_project(tmpdir)
            for rel in (
                config.paths.skills,
                config.paths.codex_skills,
                config.paths.claude_skills,
                config.paths.copilot_skills,
            ):
                asset = project_root / rel / "demo-skill" / "assets" / "template.md"
                asset.parent.mkdir(parents=True, exist_ok=True)
                asset.write_text("canonical asset content", encoding="utf-8")
            drifted = (
                project_root / config.paths.claude_skills / "demo-skill" / "assets" / "template.md"
            )
            drifted.write_text("mirror-only drifted content", encoding="utf-8")

            report = audit_skills(project_root, config)
            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    issue.path.endswith(".claude/skills/demo-skill/assets/template.md")
                    and issue.code == "SKA-MIRROR-ASSET-DRIFT"
                    and issue.blocking
                    for issue in report.issues
                )
            )

    def test_mirror_asset_unexpected_is_non_blocking_warning(self) -> None:
        """An asset present in a mirror but absent from canonical is a warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root, config = self._base_project(tmpdir)
            rogue = project_root / config.paths.claude_skills / "demo-skill" / "extras" / "rogue.md"
            rogue.parent.mkdir(parents=True, exist_ok=True)
            rogue.write_text("mirror-only asset", encoding="utf-8")

            report = audit_skills(project_root, config)
            self.assertTrue(
                any(
                    issue.path.endswith(".claude/skills/demo-skill/extras/rogue.md")
                    and issue.code == "SKA-MIRROR-ASSET-UNEXPECTED"
                    and not issue.blocking
                    for issue in report.issues
                )
            )


if __name__ == "__main__":
    unittest.main()
