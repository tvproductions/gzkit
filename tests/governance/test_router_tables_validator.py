"""Tests for `gz validate --router-tables` validator (OBPI-0.27.0-03).

@covers OBPI-0.27.0-03-router-tables-validator
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.router_tables import audit_router_tables

_MINIMAL_FRONTMATTER = "---\nname: {slug}\ndescription: stub.\nmodel: haiku\n---\n\n"

_ROUTER_BODY_TEMPLATE = "# {slug}\n\n| Intent | Skill |\n|---|---|\n{rows}\n"


def _write_skill(skills_root: Path, slug: str, body_suffix: str = "") -> None:
    skill_dir = skills_root / slug
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        _MINIMAL_FRONTMATTER.format(slug=slug) + body_suffix,
        encoding="utf-8",
    )


def _write_router(skills_root: Path, slug: str, routes: list[tuple[str, str]]) -> None:
    rows = "\n".join(f"| {intent} | `{routed}` |" for intent, routed in routes)
    body = _ROUTER_BODY_TEMPLATE.format(slug=slug, rows=rows)
    _write_skill(skills_root, slug, body_suffix=body)


class TestRoutedSlugMustResolve(unittest.TestCase):
    """REQ-0.27.0-03-01: Direction 1 — routed slug must resolve to a real canonical SKILL.md.

    @covers REQ-0.27.0-03-01
    """

    def test_routed_slug_missing_emits_router_tables_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / ".gzkit" / "skills"
            skills.mkdir(parents=True)
            _write_router(skills, "gz-test-router", [("missing-intent", "gz-does-not-exist")])

            errors = audit_router_tables(root)

        broken_routes = [e for e in errors if e.type == "router_tables"]
        self.assertEqual(
            len(broken_routes),
            1,
            f"expected exactly one router_tables error, got {[e.message for e in errors]}",
        )
        self.assertIn("gz-does-not-exist", broken_routes[0].message)
        self.assertIn("gz-test-router", broken_routes[0].message)


class TestConcreteSkillCoverage(unittest.TestCase):
    """REQ-0.27.0-03-02: Direction 2 — concrete skill must be reachable from some router.

    @covers REQ-0.27.0-03-02
    """

    def test_unrouted_concrete_skill_emits_coverage_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / ".gzkit" / "skills"
            skills.mkdir(parents=True)
            _write_router(skills, "gz-test-router", [("foo", "gz-routed")])
            _write_skill(skills, "gz-routed")
            _write_skill(skills, "gz-orphan")

            errors = audit_router_tables(root)

        advisories = [e for e in errors if e.type == "router_tables_coverage"]
        self.assertEqual(
            len(advisories),
            1,
            f"expected exactly one coverage advisory, got {[e.message for e in errors]}",
        )
        self.assertIn("gz-orphan", advisories[0].message)


class TestCleanCanonicalSurface(unittest.TestCase):
    """REQ-0.27.0-03-03: Clean baseline — zero errors when routes resolve and coverage is complete.

    @covers REQ-0.27.0-03-03
    """

    def test_zero_errors_when_routers_cover_every_concrete_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / ".gzkit" / "skills"
            skills.mkdir(parents=True)
            _write_router(
                skills,
                "gz-test-router",
                [("alpha", "gz-alpha"), ("beta", "gz-beta")],
            )
            _write_skill(skills, "gz-alpha")
            _write_skill(skills, "gz-beta")

            errors = audit_router_tables(root)

        self.assertEqual(
            errors,
            [],
            f"expected zero errors on clean surface, got {[(e.type, e.message) for e in errors]}",
        )


if __name__ == "__main__":
    unittest.main()
