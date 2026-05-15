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
    @covers("REQ-0.0.32-15-10")  # audit-exempt: regression-invariant-overlay OBPI-09 byte parity
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
    """OBPI-09 must NOT add OBPI-06/08 surface changes."""

    @covers("REQ-0.0.32-09-05")
    def test_pyproject_has_personas_wheel_include(self) -> None:
        """pyproject.toml carries src/gzkit/personas wheel-include (landed by OBPI-0.0.32-06)."""
        pyproject = _PROJECT_ROOT / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")
        self.assertIn(
            "src/gzkit/personas/**/*.md",
            content,
            "personas wheel-include expected; OBPI-06 landed wheel manifest extension",
        )

    @covers("REQ-0.0.32-09-06")
    def test_sync_surfaces_has_personas_pkg_sync(self) -> None:
        """sync_pkg_surfaces propagates .gzkit/personas/ to src/gzkit/personas/ (OBPI-08)."""
        import tempfile  # noqa: PLC0415

        from gzkit.config import GzkitConfig  # noqa: PLC0415
        from gzkit.sync_surfaces import sync_pkg_surfaces  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pkg_init = root / "src" / "gzkit" / "personas" / "__init__.py"
            pkg_init.parent.mkdir(parents=True)
            pkg_init.write_text("", encoding="utf-8")
            canonical = root / ".gzkit" / "personas" / "test-persona.md"
            canonical.parent.mkdir(parents=True)
            canonical.write_text("# Test Persona\n", encoding="utf-8")

            sync_pkg_surfaces(root, GzkitConfig(project_name="test"))

            pkg_copy = root / "src" / "gzkit" / "personas" / "test-persona.md"
            self.assertTrue(
                pkg_copy.exists(),
                "OBPI-08 must propagate .gzkit/personas -> src/gzkit/personas",
            )
            self.assertEqual(pkg_copy.read_bytes(), canonical.read_bytes())

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


class TestPersonasScaffolderObpi10(unittest.TestCase):
    """Unit tests for CORE_PERSONAS, _iter_canonical_persona_slugs, scaffold_core_personas."""

    @covers("REQ-0.0.32-10-01")
    def test_core_personas_enumerates_all_6_slugs(self) -> None:
        from gzkit.personas import CORE_PERSONAS  # noqa: PLC0415

        expected = {
            "implementer",
            "main-session",
            "narrator",
            "pipeline-orchestrator",
            "quality-reviewer",
            "spec-reviewer",
        }
        self.assertEqual(set(CORE_PERSONAS), expected)
        self.assertEqual(len(CORE_PERSONAS), 6)

    @covers("REQ-0.0.32-10-02")
    def test_iter_canonical_persona_slugs_returns_6_entries(self) -> None:
        from gzkit.personas import _iter_canonical_persona_slugs  # noqa: PLC0415

        slugs = list(_iter_canonical_persona_slugs())
        self.assertEqual(len(slugs), 6)
        for entry in slugs:
            self.assertTrue(entry.name.endswith(".md"), f"Expected .md file, got {entry.name}")

    @covers("REQ-0.0.32-10-03")
    def test_scaffold_core_personas_writes_byte_identical_content(self) -> None:
        import importlib.resources  # noqa: PLC0415
        import tempfile  # noqa: PLC0415

        from gzkit.personas import scaffold_core_personas  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            created = scaffold_core_personas(project_root)
            self.assertEqual(len(created), 6)
            # Verify byte-identical content from package
            root = importlib.resources.files("gzkit.personas")
            for path in created:
                pkg_entry = root.joinpath(path.name)
                self.assertEqual(path.read_bytes(), pkg_entry.read_bytes())

    @covers("REQ-0.0.32-10-06")
    def test_scaffold_core_personas_skip_existing_preserves_operator_edits(self) -> None:
        import tempfile  # noqa: PLC0415

        from gzkit.personas import scaffold_core_personas  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            # Write a custom persona file
            personas_dir = project_root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            custom_content = b"custom operator content"
            (personas_dir / "main-session.md").write_bytes(custom_content)
            # Scaffold with skip_existing=True
            created = scaffold_core_personas(project_root, skip_existing=True)
            # The pre-existing main-session.md should NOT be in created
            created_names = {p.name for p in created}
            self.assertNotIn("main-session.md", created_names)
            # Content must be preserved
            self.assertEqual((personas_dir / "main-session.md").read_bytes(), custom_content)
            # Other 5 personas must be created
            self.assertEqual(len(created), 5)

    @covers("REQ-0.0.32-10-08")
    def test_manpage_and_runbook_mention_personas_scaffolding(self) -> None:
        manpage = _PROJECT_ROOT / "docs" / "user" / "manpages" / "init.md"
        self.assertTrue(manpage.is_file(), "docs/user/manpages/init.md must exist")
        content = manpage.read_text(encoding="utf-8")
        self.assertIn("Personas Scaffolding", content)
        self.assertIn("scaffold_core_personas", content)

        runbook = _PROJECT_ROOT / "docs" / "user" / "runbook.md"
        self.assertTrue(runbook.is_file(), "docs/user/runbook.md must exist")
        rb_content = runbook.read_text(encoding="utf-8")
        self.assertIn("CORE_PERSONAS", rb_content)
        self.assertIn("OBPI-0.0.32-10", rb_content)

    @covers("REQ-0.0.32-10-09")
    def test_personas_module_exports_scaffold_api(self) -> None:
        """gz check exit 0 invariant — new API symbols import without error.

        REQ-09 says ``uv run gz check`` MUST exit 0 after this OBPI lands.
        The brittle failure mode is a broken import chain. This test asserts
        the underlying invariant: all three new symbols are importable and
        have the correct types, which is what would break gz check lint/typecheck.
        """
        from gzkit.personas import (  # noqa: PLC0415
            CORE_PERSONAS,
            _iter_canonical_persona_slugs,
            scaffold_core_personas,
        )

        self.assertIsInstance(CORE_PERSONAS, list)
        self.assertEqual(len(CORE_PERSONAS), 6)
        self.assertTrue(callable(_iter_canonical_persona_slugs))
        self.assertTrue(callable(scaffold_core_personas))


class TestClassifyPersonaFile(unittest.TestCase):
    """Per-surface classifier for the personas canonical surface (REQ-0.0.32-15-04).

    Signature-compatible with ``gzkit.chores._classify_chore_file``: returns
    one of ``"canonical"``, ``"package_only"``, or ``"runtime_state"``.
    """

    @covers("REQ-0.0.32-15-04")
    def test_importable(self) -> None:
        """``_classify_persona_file`` is importable from ``gzkit.personas``."""
        try:
            from gzkit.personas import _classify_persona_file  # noqa: PLC0415, F401
        except ImportError as e:  # pragma: no cover - failure surfaces in assertion
            self.fail(
                "_classify_persona_file must be importable from gzkit.personas; "
                f"got ImportError: {e}"
            )

    @covers("REQ-0.0.32-15-04")
    def test_package_only_init_py(self) -> None:
        """``__init__.py`` files classify as ``package_only``."""
        from gzkit.personas import _classify_persona_file  # noqa: PLC0415

        result = _classify_persona_file(Path("src/gzkit/personas/__init__.py"))
        self.assertEqual(result, "package_only")

    @covers("REQ-0.0.32-15-04")
    def test_canonical_md(self) -> None:
        """A persona ``*.md`` classifies as ``canonical``."""
        from gzkit.personas import _classify_persona_file  # noqa: PLC0415

        result = _classify_persona_file(Path("src/gzkit/personas/main-session.md"))
        self.assertEqual(result, "canonical")

    @covers("REQ-0.0.32-15-04")
    def test_package_only_pycache(self) -> None:
        """Anything under ``__pycache__`` classifies as ``package_only``."""
        from gzkit.personas import _classify_persona_file  # noqa: PLC0415

        result = _classify_persona_file(
            Path("src/gzkit/personas/__pycache__/something.cpython-313.pyc")
        )
        self.assertEqual(result, "package_only")


if __name__ == "__main__":
    unittest.main()
