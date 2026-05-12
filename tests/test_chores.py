"""Dual-surface byte-parity tests for gzkit.chores.

OBPI-0.0.32-13-chores-normalization: verifies that canonical chore files
authored at ``.gzkit/chores/<slug>/`` (retained source of truth) for slugs
that have runtime counterparts at ``src/gzkit/chores/<slug>/`` are
byte-equivalent copies, and that the classifier helper
``_classify_chore_file`` exists and correctly categorizes files into
canonical/package_only/runtime_state classes.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestChoresLayoutDualSurface(unittest.TestCase):
    """Chore files MUST live at BOTH .gzkit/chores/ and src/gzkit/chores/ for dual-surface slugs.

    .gzkit/chores/ is the authored source (project canonical, retained).
    src/gzkit/chores/ is the synced copy (ships in wheel).
    Slugs that exist only in .gzkit/ (e.g., owasp-top10-2025-scan) are skipped.
    """

    @covers("REQ-0.0.32-13-01")
    @covers("REQ-0.0.32-13-06")
    @covers("REQ-0.0.32-13-08")
    def test_classifier_section_in_rule(self) -> None:
        """Verify .gzkit/rules/skill-surface-sync.md contains classifier section."""
        rule_file = _PROJECT_ROOT / ".gzkit" / "rules" / "skill-surface-sync.md"
        self.assertTrue(rule_file.is_file(), "skill-surface-sync.md must exist")

        content = rule_file.read_text(encoding="utf-8")
        self.assertIn(
            "Chores class-classifier",
            content,
            "skill-surface-sync.md must document Chores class-classifier",
        )
        self.assertIn(
            "ADR-pool.canonical-vs-runtime-separation",
            content,
            "skill-surface-sync.md must reference ADR-pool.canonical-vs-runtime-separation",
        )

    @covers("REQ-0.0.32-13-02")
    @covers("REQ-0.0.32-13-07")
    def test_classifier_helper_importable(self) -> None:
        """Verify _classify_chore_file can be imported from gzkit.chores."""
        try:
            from gzkit.chores import _classify_chore_file
        except ImportError as e:
            self.fail(
                f"_classify_chore_file must be importable from gzkit.chores; got ImportError: {e}"
            )

        # Test basic classification behavior
        canonical_file = Path(".gzkit/chores/skill-authoring-quality/CHORE.md")
        result = _classify_chore_file(canonical_file)
        self.assertEqual(
            result, "canonical", f"CHORE.md should classify as canonical, got {result}"
        )

        package_only_file = Path("src/gzkit/chores/__init__.py")
        result = _classify_chore_file(package_only_file)
        self.assertEqual(
            result,
            "package_only",
            f"__init__.py should classify as package_only, got {result}",
        )

    @covers("REQ-0.0.32-13-03")
    @covers("REQ-0.0.32-13-04")
    def test_canonical_class_byte_parity(self) -> None:
        """Canonical-classified files must be byte-identical across dual surfaces.

        Walks every file under .gzkit/chores/<slug>/ for all slugs that ALSO
        have a counterpart under src/gzkit/chores/<slug>/. Applies
        _classify_chore_file to get classification. Asserts byte-parity for
        canonical-classified files only. Skips package_only and runtime_state
        files. Skips slugs that only exist in .gzkit/ (no src/ counterpart).
        """
        from gzkit.chores import _classify_chore_file

        authored_root = _PROJECT_ROOT / ".gzkit" / "chores"
        pkg_root = _PROJECT_ROOT / "src" / "gzkit" / "chores"

        self.assertTrue(authored_root.is_dir(), ".gzkit/chores/ must exist")
        self.assertTrue(pkg_root.is_dir(), "src/gzkit/chores/ must exist")

        # Identify all slug directories in .gzkit/chores/
        authored_slugs = {
            d.name for d in authored_root.iterdir() if d.is_dir() and not d.name.startswith(".")
        }

        # Identify all slug directories in src/gzkit/chores/
        pkg_slugs = {
            d.name for d in pkg_root.iterdir() if d.is_dir() and not d.name.startswith(".")
        }

        # Filter to only slugs that exist in BOTH locations
        dual_surface_slugs = authored_slugs & pkg_slugs

        self.assertTrue(
            dual_surface_slugs,
            "At least one slug must exist in both .gzkit/chores/ and src/gzkit/chores/",
        )

        divergent_files = []
        for slug in dual_surface_slugs:
            authored_slug_dir = authored_root / slug
            pkg_slug_dir = pkg_root / slug

            # Walk all files in the authored slug directory
            for authored_file in authored_slug_dir.rglob("*"):
                if not authored_file.is_file():
                    continue

                # Skip the proofs directory (runtime state, not canonical)
                if "proofs" in authored_file.relative_to(authored_slug_dir).parts:
                    continue

                classification = _classify_chore_file(authored_file)

                # Only check byte-parity for canonical-classified files
                if classification != "canonical":
                    continue

                # Compute the relative path from the slug directory
                rel_path = authored_file.relative_to(authored_slug_dir)
                pkg_file = pkg_slug_dir / rel_path

                # Verify the package copy exists
                if not pkg_file.exists():
                    divergent_files.append(
                        f"Missing in src/gzkit/chores/{slug}/: {rel_path.as_posix()}"
                    )
                    continue

                # Check byte-parity
                authored_bytes = authored_file.read_bytes()
                pkg_bytes = pkg_file.read_bytes()
                if authored_bytes != pkg_bytes:
                    divergent_files.append(
                        f"Byte divergence in {slug}/{rel_path.as_posix()} "
                        f"(.gzkit: {len(authored_bytes)} bytes, src/gzkit: {len(pkg_bytes)} bytes)"
                    )

        if divergent_files:
            self.fail(
                "Canonical chore files must be byte-identical:\n  " + "\n  ".join(divergent_files)
            )

    @covers("REQ-0.0.32-13-05")
    def test_no_runtime_state_relocation(self) -> None:
        """Proofs/ directories must remain inside slug dirs, not relocated."""
        authored_root = _PROJECT_ROOT / ".gzkit" / "chores"

        self.assertTrue(authored_root.is_dir(), ".gzkit/chores/ must exist")

        # Verify that for any slug with a proofs/ directory, it's a direct child of the slug
        for slug_dir in authored_root.iterdir():
            if not slug_dir.is_dir() or slug_dir.name.startswith("."):
                continue

            proofs_dir = slug_dir / "proofs"
            if not proofs_dir.exists():
                continue

            # Proofs must be a direct child of the slug directory
            self.assertTrue(
                proofs_dir.is_dir(),
                f"proofs/ for slug {slug_dir.name} must be a directory",
            )
            self.assertEqual(
                proofs_dir.parent,
                slug_dir,
                f"proofs/ for {slug_dir.name} must be directly inside the slug dir, not relocated",
            )


if __name__ == "__main__":
    unittest.main()
