"""Tests for namespace-router coverage completion (OBPI-0.27.0-04).

@covers OBPI-0.27.0-04-router-coverage-completion
"""

from __future__ import annotations

import datetime as _dt
import re
import unittest
from pathlib import Path

from gzkit.core.models import SkillFrontmatter
from gzkit.core.validation_rules import parse_frontmatter
from gzkit.governance.trust_audits.router_tables import audit_router_tables

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_ROOT = PROJECT_ROOT / ".gzkit" / "skills"
PKG_ROOT = PROJECT_ROOT / "src" / "gzkit" / "skills"
VENDOR_MIRROR_ROOTS = (
    PROJECT_ROOT / ".agents" / "skills",
    PROJECT_ROOT / ".claude" / "skills",
    PROJECT_ROOT / ".github" / "skills",
)

ALL_ROUTER_SLUGS = (
    "gz-workflow",
    "gz-governance",
    "gz-quality",
    "gz-project",
    "gz-context",
    "gz-manage",
    "gz-chores",
)

CHORES_ROUTED_SKILLS = (
    "gz-chore-runner",
    "gz-deps-upgrade",
    "gz-foundation-triage",
    "gz-pythonic-pattern-detect",
    "gz-pythonic-pattern-apply",
    "gz-check-config-paths",
    "gz-cli-audit",
)

PREVIOUSLY_UNROUTED_SKILL_HOMES = {
    "gz-justify": "gz-workflow",
    "gz-plan-audit": "gz-workflow",
    "gz-competitor-radar": "gz-project",
    "gz-adr-evaluate": "gz-governance",
    "gz-migrate-semver": "gz-governance",
    "gz-obpi-lock": "gz-governance",
    "gz-obpi-simplify": "gz-quality",
    "gz-issue-file": "gz-manage",
}

_INTENT_TABLE_HEADER = re.compile(r"\|\s*Intent\s*\|\s*Skill\s*\|", re.IGNORECASE)
_INTENT_ROW = re.compile(r"\|\s*([^|`]+?)\s*\|\s*`([^`]+)`\s*\|")
_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _router_path(slug: str) -> Path:
    return CANONICAL_ROOT / slug / "SKILL.md"


def _read_router(slug: str) -> tuple[dict[str, object], str]:
    return parse_frontmatter(_router_path(slug).read_text(encoding="utf-8"))


def _routed_slugs(slug: str) -> list[str]:
    _frontmatter, body = _read_router(slug)
    return [routed for _intent, routed in _INTENT_ROW.findall(body)]


class TestChoresRouterSkillFile(unittest.TestCase):
    """REQ-0.27.0-04-01.

    @covers REQ-0.27.0-04-01
    """

    def test_gz_chores_file_exists_with_required_frontmatter(self) -> None:
        path = _router_path("gz-chores")
        self.assertTrue(
            path.is_file(),
            f"gz-chores router missing at {path.relative_to(PROJECT_ROOT).as_posix()}",
        )
        frontmatter, _body = _read_router("gz-chores")
        model = SkillFrontmatter.model_validate(frontmatter)
        self.assertEqual(model.name, "gz-chores")
        self.assertEqual(model.lifecycle_state, "active")
        self.assertEqual(model.skill_model, "haiku")
        self.assertIsNotNone(model.owner)
        self.assertIsNotNone(model.last_reviewed)
        self.assertTrue(
            frontmatter.get("skill-version"),
            "gz-chores frontmatter must declare skill-version",
        )
        self.assertTrue(
            frontmatter.get("category"),
            "gz-chores frontmatter must declare category",
        )

    def test_gz_chores_intent_table_routes_all_seven_chore_skills(self) -> None:
        _frontmatter, body = _read_router("gz-chores")
        self.assertRegex(body, _INTENT_TABLE_HEADER)
        routed = set(_routed_slugs("gz-chores"))
        missing = set(CHORES_ROUTED_SKILLS) - routed
        self.assertFalse(
            missing,
            f"gz-chores intent table missing entries for: {sorted(missing)}",
        )


class TestPreviouslyUnroutedSkillsHomed(unittest.TestCase):
    """REQ-0.27.0-04-02.

    @covers REQ-0.27.0-04-02
    """

    def test_each_named_skill_appears_in_its_target_router(self) -> None:
        for skill, target_router in PREVIOUSLY_UNROUTED_SKILL_HOMES.items():
            with self.subTest(skill=skill, router=target_router):
                routed = _routed_slugs(target_router)
                self.assertIn(
                    skill,
                    routed,
                    f"skill '{skill}' is not routed by '{target_router}' (REQ-0.27.0-04-02)",
                )


class TestLiveCanonicalRouterTablesClean(unittest.TestCase):
    """REQ-0.27.0-04-03.

    @covers REQ-0.27.0-04-03
    """

    def test_audit_router_tables_returns_zero_errors_against_live_canonical(self) -> None:
        errors = audit_router_tables(PROJECT_ROOT)
        self.assertEqual(
            errors,
            [],
            f"live canonical surface has router-tables errors: "
            f"{[(e.type, e.message) for e in errors]}",
        )


class TestRouterUniqueness(unittest.TestCase):
    """REQ-0.27.0-04-04.

    @covers REQ-0.27.0-04-04
    """

    def test_no_concrete_skill_routed_by_more_than_one_router(self) -> None:
        ownership: dict[str, list[str]] = {}
        for router in ALL_ROUTER_SLUGS:
            for routed in _routed_slugs(router):
                ownership.setdefault(routed, []).append(router)
        duplicates = {skill: routers for skill, routers in ownership.items() if len(routers) > 1}
        self.assertFalse(
            duplicates,
            f"concrete skills routed by multiple routers (uniqueness violation): {duplicates}",
        )


class TestRouterMetadataPresence(unittest.TestCase):
    """REQ-0.27.0-04-05.

    @covers REQ-0.27.0-04-05
    """

    def test_every_router_carries_skill_version_and_last_reviewed(self) -> None:
        for router in ALL_ROUTER_SLUGS:
            with self.subTest(router=router):
                frontmatter, _body = _read_router(router)
                version = frontmatter.get("skill-version")
                self.assertIsNotNone(
                    version,
                    f"{router}: skill-version missing from frontmatter",
                )
                self.assertRegex(
                    str(version),
                    _SEMVER,
                    f"{router}: skill-version '{version}' is not valid semver",
                )
                last_reviewed = frontmatter.get("last_reviewed")
                self.assertIsNotNone(
                    last_reviewed,
                    f"{router}: last_reviewed missing from frontmatter",
                )
                if isinstance(last_reviewed, _dt.date):
                    parsed = last_reviewed
                else:
                    parsed = _dt.date.fromisoformat(str(last_reviewed))
                self.assertIsInstance(
                    parsed,
                    _dt.date,
                    f"{router}: last_reviewed '{last_reviewed}' is not a valid ISO date",
                )


class TestChoresRouterMirrorParity(unittest.TestCase):
    """REQ-0.27.0-04-06.

    @covers REQ-0.27.0-04-06
    """

    def test_gz_chores_byte_equivalent_in_pkg_and_every_vendor_mirror(self) -> None:
        canonical_bytes = (CANONICAL_ROOT / "gz-chores" / "SKILL.md").read_bytes()
        pkg_path = PKG_ROOT / "gz-chores" / "SKILL.md"
        self.assertTrue(
            pkg_path.is_file(),
            f"gz-chores pkg copy missing: {pkg_path.relative_to(PROJECT_ROOT).as_posix()}",
        )
        self.assertEqual(
            pkg_path.read_bytes(),
            canonical_bytes,
            "gz-chores pkg copy byte-divergent from canonical",
        )
        for mirror_root in VENDOR_MIRROR_ROOTS:
            with self.subTest(mirror=mirror_root.name):
                mirror_path = mirror_root / "gz-chores" / "SKILL.md"
                self.assertTrue(
                    mirror_path.is_file(),
                    f"gz-chores vendor mirror missing: "
                    f"{mirror_path.relative_to(PROJECT_ROOT).as_posix()}",
                )
                self.assertEqual(
                    mirror_path.read_bytes(),
                    canonical_bytes,
                    f"gz-chores vendor mirror byte-divergent: "
                    f"{mirror_path.relative_to(PROJECT_ROOT).as_posix()}",
                )


if __name__ == "__main__":
    unittest.main()
