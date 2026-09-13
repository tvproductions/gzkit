"""Files directly under the chores surface belong to no slug (GHI #1005).

`_chore_slug_of` returned the part after `chores` whenever one existed, so
`.gzkit/chores/registry.json` resolved to a slug named `registry.json`. The orphan
guard then found no `CHORE.md` for that "slug" and classified the registry
`package_only`, so sync never exported it: the shipped registry went stale while
two chores' files kept shipping, and README edits never reached the wheel.

The generated nested `AGENTS.md` / `CLAUDE.md` sit at both surface roots with
different title lines by design. They were kept apart only by the same accident,
so they now carry a declared class instead.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.chores import _chore_slug_of, _classify_chore_file, exportable_registry
from gzkit.skills import _skill_slug_of


def _project(root: Path) -> tuple[Path, Path]:
    """Build a project chores surface with one slug and its surface-level files."""
    chores = root / ".gzkit" / "chores"
    (chores / "demo").mkdir(parents=True)
    (chores / "demo" / "CHORE.md").write_text("# demo\n", encoding="utf-8")
    (chores / "demo" / "acceptance.json").write_text('{"criteria": []}\n', encoding="utf-8")
    (chores / "registry.json").write_text(
        json.dumps(
            {
                "chores": [
                    {"slug": "demo", "title": "Demo", "path": ".gzkit/chores/demo", "lane": "lite"},
                    {
                        "slug": "internal",
                        "title": "Internal",
                        "path": ".gzkit/chores/internal",
                        "lane": "lite",
                        "projectLocal": True,
                    },
                ]
            },
            indent=4,
        ),
        encoding="utf-8",
    )
    (chores / "README.md").write_text("# Chores contract, edited\n", encoding="utf-8")
    (chores / "AGENTS.md").write_text("# .gzkit/chores Agent Instructions\n", encoding="utf-8")
    pkg = root / "src" / "gzkit" / "chores"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "AGENTS.md").write_text("# src/gzkit/chores Agent Instructions\n", encoding="utf-8")
    return chores, pkg


def _sync(root: Path) -> None:
    from gzkit.config import GzkitConfig
    from gzkit.sync_surfaces import sync_pkg_surfaces

    sync_pkg_surfaces(root, GzkitConfig(project_name="t"))


class TestSyncDeliversSurfaceLevelFiles(unittest.TestCase):
    def test_the_registry_ships_filtered(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            chores, pkg = _project(root)
            _sync(root)
            shipped = json.loads((pkg / "registry.json").read_text(encoding="utf-8"))
            self.assertEqual(shipped, exportable_registry(chores / "registry.json"))
            self.assertEqual([c["slug"] for c in shipped["chores"]], ["demo"])

    def test_a_readme_edit_reaches_the_package(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            chores, pkg = _project(root)
            _sync(root)
            self.assertEqual((pkg / "README.md").read_bytes(), (chores / "README.md").read_bytes())

    def test_the_package_nested_instructions_are_not_overwritten(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _chores, pkg = _project(root)
            _sync(root)
            self.assertEqual(
                (pkg / "AGENTS.md").read_text(encoding="utf-8"),
                "# src/gzkit/chores Agent Instructions\n",
            )


class TestClassification(unittest.TestCase):
    def test_surface_level_files_classify_by_their_own_kind(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            chores, pkg = _project(root)
            cases = (
                (chores / "registry.json", "canonical"),
                (chores / "README.md", "canonical"),
                (chores / "AGENTS.md", "package_only"),
                (chores / "CLAUDE.md", "package_only"),
                (pkg / "AGENTS.md", "package_only"),
            )
            for path, expected in cases:
                with self.subTest(path=path.relative_to(root).as_posix()):
                    self.assertEqual(_classify_chore_file(path, project_root=root), expected)

    def test_an_orphan_slug_directory_is_still_package_only(self) -> None:
        # The guard 921728abb added must survive: no CHORE.md means no chore.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            chores, _pkg = _project(root)
            orphan = chores / "owasp-top10-2025-scan" / "notes.md"
            orphan.parent.mkdir()
            orphan.write_text("# notes\n", encoding="utf-8")
            self.assertEqual(_classify_chore_file(orphan, project_root=root), "package_only")


class TestSlugResolution(unittest.TestCase):
    def test_a_file_directly_under_the_surface_names_no_slug(self) -> None:
        cases = (
            (_chore_slug_of, Path(".gzkit/chores/registry.json"), None),
            (_chore_slug_of, Path("src/gzkit/chores/README.md"), None),
            (_chore_slug_of, Path(".gzkit/chores/demo/CHORE.md"), "demo"),
            (_skill_slug_of, Path(".gzkit/skills/AGENTS.md"), None),
            (_skill_slug_of, Path("src/gzkit/skills/gz-check/SKILL.md"), "gz-check"),
        )
        for resolver, path, expected in cases:
            with self.subTest(resolver=resolver.__name__, path=path.as_posix()):
                self.assertEqual(resolver(path), expected)


if __name__ == "__main__":
    unittest.main()
