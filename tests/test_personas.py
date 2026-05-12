"""Dual-surface byte-parity tests for gzkit.personas.

OBPI-0.0.32-09-personas-physical-migration: verifies that the 6 canonical
persona files are authored at ``.gzkit/personas/<slug>.md`` (retained source
of truth) AND ship as byte-equivalent copies at
``src/gzkit/personas/<slug>.md``, and that ``src/gzkit/personas/__init__.py``
exists as a thin package marker that preserves the pre-existing
``gzkit.personas`` API (module-to-package conversion) without adding new
package-discovery symbols (CORE_PERSONAS, scaffold_core_personas,
_iter_canonical_persona_slugs) — those belong to OBPI-10.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[1]

_CANONICAL_PERSONA_SLUGS = (
    "implementer",
    "main-session",
    "narrator",
    "pipeline-orchestrator",
    "quality-reviewer",
    "spec-reviewer",
)


class TestPersonasLayoutDualSurface(unittest.TestCase):
    """Persona files MUST live at BOTH .gzkit/personas/ and src/gzkit/personas/.

    .gzkit/personas/ is the authored source (project canonical, retained).
    src/gzkit/personas/ is the synced copy (ships in wheel).
    """

    @covers("REQ-0.0.32-09-01")
    def test_persona_files_retained_at_authored_source(self) -> None:
        authored_root = _PROJECT_ROOT / ".gzkit" / "personas"
        self.assertTrue(authored_root.is_dir(), ".gzkit/personas/ must remain in place")
        for slug in _CANONICAL_PERSONA_SLUGS:
            authored = authored_root / f"{slug}.md"
            self.assertTrue(
                authored.is_file(),
                f".gzkit/personas/{slug}.md must remain as authored canonical",
            )

    @covers("REQ-0.0.32-09-01")
    def test_persona_files_present_in_package_surface(self) -> None:
        pkg_root = _PROJECT_ROOT / "src" / "gzkit" / "personas"
        self.assertTrue(pkg_root.is_dir(), "src/gzkit/personas/ must exist as package")
        for slug in _CANONICAL_PERSONA_SLUGS:
            pkg_copy = pkg_root / f"{slug}.md"
            self.assertTrue(
                pkg_copy.is_file(),
                f"src/gzkit/personas/{slug}.md must exist as wheel-shipping copy",
            )

    @covers("REQ-0.0.32-09-01")
    @covers("REQ-0.0.32-09-02")
    def test_dual_surface_byte_parity(self) -> None:
        """Authored .gzkit/personas/<slug>.md must be byte-identical to src/gzkit copy."""
        authored_root = _PROJECT_ROOT / ".gzkit" / "personas"
        pkg_root = _PROJECT_ROOT / "src" / "gzkit" / "personas"
        for slug in _CANONICAL_PERSONA_SLUGS:
            authored = authored_root / f"{slug}.md"
            pkg_copy = pkg_root / f"{slug}.md"
            self.assertEqual(
                authored.read_bytes(),
                pkg_copy.read_bytes(),
                f"Drift between .gzkit/ and src/gzkit/ for personas/{slug}.md",
            )

    @covers("REQ-0.0.32-09-02")
    def test_package_init_exists(self) -> None:
        init_file = _PROJECT_ROOT / "src" / "gzkit" / "personas" / "__init__.py"
        self.assertTrue(
            init_file.is_file(),
            "src/gzkit/personas/__init__.py must exist (package marker)",
        )


class TestPersonasScopeNegative(unittest.TestCase):
    """OBPI-09 must NOT add OBPI-10 symbols or OBPI-06/08 surface changes."""

    @covers("REQ-0.0.32-09-03")
    def test_no_core_personas_registry(self) -> None:
        """CORE_PERSONAS registry must not be added in this OBPI (OBPI-10 scope)."""
        import gzkit.personas as personas_module

        self.assertFalse(
            hasattr(personas_module, "CORE_PERSONAS"),
            "CORE_PERSONAS belongs to OBPI-10, not this OBPI",
        )

    @covers("REQ-0.0.32-09-03")
    def test_no_scaffold_core_personas(self) -> None:
        """scaffold_core_personas must not be added in this OBPI (OBPI-10 scope)."""
        import gzkit.personas as personas_module

        self.assertFalse(
            hasattr(personas_module, "scaffold_core_personas"),
            "scaffold_core_personas belongs to OBPI-10, not this OBPI",
        )

    @covers("REQ-0.0.32-09-03")
    def test_no_iter_canonical_persona_slugs(self) -> None:
        """_iter_canonical_persona_slugs must not be added in this OBPI (OBPI-10 scope)."""
        import gzkit.personas as personas_module

        self.assertFalse(
            hasattr(personas_module, "_iter_canonical_persona_slugs"),
            "_iter_canonical_persona_slugs belongs to OBPI-10, not this OBPI",
        )

    @covers("REQ-0.0.32-09-04")
    def test_init_cmd_has_no_scaffold_core_personas_call(self) -> None:
        """src/gzkit/commands/init_cmd.py must not call scaffold_core_personas (OBPI-10 scope)."""
        init_cmd = _PROJECT_ROOT / "src" / "gzkit" / "commands" / "init_cmd.py"
        content = init_cmd.read_text(encoding="utf-8")
        self.assertNotIn(
            "scaffold_core_personas",
            content,
            "init_cmd.py integration belongs to OBPI-10, not this OBPI",
        )

    @covers("REQ-0.0.32-09-05")
    def test_pyproject_has_no_personas_wheel_include(self) -> None:
        """pyproject.toml must not include src/gzkit/personas pattern (OBPI-06 scope)."""
        pyproject = _PROJECT_ROOT / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")
        self.assertNotIn(
            "src/gzkit/personas/**/*.md",
            content,
            "personas wheel-include extension belongs to OBPI-06, not this OBPI",
        )

    @covers("REQ-0.0.32-09-06")
    def test_sync_surfaces_has_no_personas_byte_copy(self) -> None:
        """sync_surfaces.py must not byte-copy .gzkit/personas to package (OBPI-08 scope)."""
        sync_module = _PROJECT_ROOT / "src" / "gzkit" / "sync_surfaces.py"
        content = sync_module.read_text(encoding="utf-8")
        self.assertNotIn(
            "src/gzkit/personas",
            content,
            "Dual-surface personas byte-copy step belongs to OBPI-08, not this OBPI",
        )

    @covers("REQ-0.0.32-09-07")
    def test_vendor_mirrors_remain_transformed_renders(self) -> None:
        """Vendor mirrors at .claude/personas/ must NOT be byte-equivalent to .gzkit/personas/."""
        authored_root = _PROJECT_ROOT / ".gzkit" / "personas"
        claude_root = _PROJECT_ROOT / ".claude" / "personas"
        for slug in _CANONICAL_PERSONA_SLUGS:
            authored = authored_root / f"{slug}.md"
            claude_mirror = claude_root / f"{slug}.md"
            if not claude_mirror.is_file():
                continue
            self.assertNotEqual(
                authored.read_bytes(),
                claude_mirror.read_bytes(),
                (
                    f".claude/personas/{slug}.md must remain a transformed render "
                    "(NOT byte-equivalent to .gzkit/personas/) — vendor-mirror "
                    "transformation is intentional per ADR-0.0.32 § Named exceptions"
                ),
            )

    @covers("REQ-0.0.32-09-08")
    def test_personas_module_preserves_existing_api(self) -> None:
        """The module-to-package conversion must preserve the pre-existing personas API."""
        from gzkit.personas import (
            DEFAULT_PERSONAS,
            VENDOR_ADAPTERS,
            compose_persona_frame,
            evaluate_persona_drift,
            render_persona_for_vendor,
            scaffold_default_personas,
        )

        self.assertIsInstance(DEFAULT_PERSONAS, dict)
        self.assertIsInstance(VENDOR_ADAPTERS, dict)
        self.assertTrue(callable(compose_persona_frame))
        self.assertTrue(callable(evaluate_persona_drift))
        self.assertTrue(callable(render_persona_for_vendor))
        self.assertTrue(callable(scaffold_default_personas))


if __name__ == "__main__":
    unittest.main()
