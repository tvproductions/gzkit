"""Tests for router surface sync parity (OBPI-0.27.0-02).

@covers OBPI-0.27.0-02-router-surface-sync
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.skills import list_skills
from tests.vendor_surfaces import skill_mirror_roots

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_ROOT = PROJECT_ROOT / ".gzkit" / "skills"
PKG_ROOT = PROJECT_ROOT / "src" / "gzkit" / "skills"
VENDOR_MIRROR_ROOTS = skill_mirror_roots()

ROUTER_SLUGS = (
    "gz-workflow",
    "gz-governance",
    "gz-quality",
    "gz-project",
    "gz-context",
    "gz-manage",
)


def _read_bytes(root: Path, slug: str) -> bytes:
    return (root / slug / "SKILL.md").read_bytes()


class TestVendorMirrorByteParity(unittest.TestCase):
    """REQ-0.27.0-02-01.

    @covers REQ-0.27.0-02-01
    """

    def test_each_router_byte_equivalent_in_every_vendor_mirror(self) -> None:
        for slug in ROUTER_SLUGS:
            canonical = _read_bytes(CANONICAL_ROOT, slug)
            for mirror_root in VENDOR_MIRROR_ROOTS:
                with self.subTest(slug=slug, mirror=mirror_root.name):
                    mirror_path = mirror_root / slug / "SKILL.md"
                    self.assertTrue(
                        mirror_path.is_file(),
                        f"vendor mirror missing: "
                        f"{mirror_path.relative_to(PROJECT_ROOT).as_posix()}",
                    )
                    self.assertEqual(
                        _read_bytes(mirror_root, slug),
                        canonical,
                        f"vendor mirror byte-divergent: "
                        f"{mirror_path.relative_to(PROJECT_ROOT).as_posix()} "
                        f"!= .gzkit/skills/{slug}/SKILL.md",
                    )


class TestPkgCopyByteParity(unittest.TestCase):
    """REQ-0.27.0-02-02.

    @covers REQ-0.27.0-02-02
    """

    def test_each_router_byte_equivalent_in_wheel_pkg_copy(self) -> None:
        for slug in ROUTER_SLUGS:
            with self.subTest(slug=slug):
                pkg_path = PKG_ROOT / slug / "SKILL.md"
                self.assertTrue(
                    pkg_path.is_file(),
                    f"pkg copy missing: {pkg_path.relative_to(PROJECT_ROOT).as_posix()}",
                )
                self.assertEqual(
                    _read_bytes(PKG_ROOT, slug),
                    _read_bytes(CANONICAL_ROOT, slug),
                    f"pkg copy byte-divergent: "
                    f"src/gzkit/skills/{slug}/SKILL.md != .gzkit/skills/{slug}/SKILL.md",
                )


class TestRoutersDiscoverableInActiveCatalog(unittest.TestCase):
    """REQ-0.27.0-02-03.

    @covers REQ-0.27.0-02-03
    """

    def test_each_router_listed_active_in_skill_catalog(self) -> None:
        active = {s.name: s for s in list_skills(PROJECT_ROOT)}
        for slug in ROUTER_SLUGS:
            with self.subTest(slug=slug):
                self.assertIn(
                    slug,
                    active,
                    f"router '{slug}' missing from active skill catalog "
                    f"(list_skills did not discover it under .gzkit/skills/)",
                )
                self.assertEqual(
                    active[slug].lifecycle_state,
                    "active",
                    f"router '{slug}' is not in lifecycle_state 'active'",
                )


if __name__ == "__main__":
    unittest.main()
