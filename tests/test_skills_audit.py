"""Tests for skill mirror identity contract enforcement."""

import tempfile
import unittest
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
        "last_reviewed": "2026-02-21",
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
                    "demo-skill", metadata={"govzero_layer": "Layer 99 — Unknown"}
                ),
            )
            _write_skill(
                project_root,
                config.paths.codex_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter(
                    "demo-skill", metadata={"govzero_layer": "Layer 99 — Unknown"}
                ),
            )
            _write_skill(
                project_root,
                config.paths.claude_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter(
                    "demo-skill", metadata={"govzero_layer": "Layer 99 — Unknown"}
                ),
            )
            _write_skill(
                project_root,
                config.paths.copilot_skills,
                "demo-skill",
                frontmatter=_skill_frontmatter(
                    "demo-skill", metadata={"govzero_layer": "Layer 99 — Unknown"}
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
                "govzero_layer": "Layer 1 — Evidence Gathering",
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


if __name__ == "__main__":
    unittest.main()
