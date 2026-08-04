"""Project-local chores stay out of the wheel and out of adopters (GHI #728).

`.gzkit/chores/AGENTS.md` declares the category (REQ-0.0.21-09-06): `doctor`
"never modifies project-local-only slugs". The category was never authorable.
`grep -rn "project_local_only" --include='*.py' src/gzkit/` returned nothing, and
a slug authored only under `.gzkit/chores/` was copied into `src/gzkit/chores/`
by `gz agent sync control-surfaces` and scaffolded into every adopter by
`gz init`.

`gz chores doctor` was credited with honouring the category, but
`_classify_doctor_slug` derives PROJECT-LOCAL from `not in_canonical` — absence
from the wheel. Sync is what puts a slug IN the wheel. So sync did not merely
ignore the category; it destroyed the state doctor reads. The two were
circularly coupled and sync won, which is why the property has to be DECLARED
rather than inferred.

Declared home is the slug's `registry.json` entry (`"projectLocal": true`) —
per-slug metadata beside `lane` and `timeoutSeconds`, the same file the
canonical/local merge already reasons about.

The harm is not tidiness. A chore's acceptance criteria and measured baselines
are gzkit-specific: `test-consolidation-subtest-sweep` records "78 of 497 test
files use subTest", and an adopter inheriting it inherits gzkit's numbers as
their own baseline.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.chores import _classify_chore_file, exportable_registry

_LOCAL = "gzkit-internal-sweep"
_SHIPPED = "coverage-40pct"


def _project(root: Path) -> Path:
    """Build a .gzkit/chores tree with one project-local and one shipped slug."""
    chores = root / ".gzkit" / "chores"
    for slug in (_LOCAL, _SHIPPED):
        (chores / slug).mkdir(parents=True, exist_ok=True)
        (chores / slug / "CHORE.md").write_text(f"# {slug}\n", encoding="utf-8")
        (chores / slug / "acceptance.json").write_text('{"criteria": []}\n', encoding="utf-8")
    (chores / "registry.json").write_text(
        json.dumps(
            {
                "specVersion": "1.0.0",
                "chores": [
                    {
                        "slug": _LOCAL,
                        "title": "Internal sweep",
                        "path": f".gzkit/chores/{_LOCAL}",
                        "lane": "lite",
                        "projectLocal": True,
                    },
                    {
                        "slug": _SHIPPED,
                        "title": "Coverage floor",
                        "path": f".gzkit/chores/{_SHIPPED}",
                        "lane": "lite",
                    },
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return chores


class TestProjectLocalClassification(unittest.TestCase):
    """A declared project-local slug is a distinct content class."""

    def test_marked_slug_files_classify_project_local(self) -> None:
        """Every file under a marked slug is withheld from propagation.

        Per-file, because that is the seam all three consumers share
        (`sync_pkg_surfaces`, `gz init` refresh, `gz validate --distribution`).
        A per-slug check bolted onto one consumer would leave the other two
        exporting — the shape of the original defect.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            chores = _project(root)

            for name in ("CHORE.md", "acceptance.json"):
                with self.subTest(file=name):
                    self.assertEqual(
                        _classify_chore_file(chores / _LOCAL / name, project_root=root),
                        "project_local",
                    )

    def test_unmarked_slug_still_classifies_canonical(self) -> None:
        """Negative control: the fix must not stop shipping real chores.

        A predicate that withheld everything would satisfy "no project-local
        leak" while breaking the surface's whole purpose.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            chores = _project(root)

            self.assertEqual(
                _classify_chore_file(chores / _SHIPPED / "CHORE.md", project_root=root),
                "canonical",
            )

    def test_package_side_path_is_classified_from_the_same_registry(self) -> None:
        """The `src/gzkit/chores/<slug>/...` spelling resolves identically.

        `gz init` and the distribution audit pass the package-side path, while
        sync passes the `.gzkit/` one. If only one spelling resolved, a leaked
        slug would stay invisible to the audit that should catch it.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _project(root)

            self.assertEqual(
                _classify_chore_file(
                    Path("src/gzkit/chores") / _LOCAL / "CHORE.md", project_root=root
                ),
                "project_local",
            )


class TestExportableRegistry(unittest.TestCase):
    """The shipped registry cannot advertise a chore whose files do not ship."""

    def test_project_local_entries_are_dropped(self) -> None:
        """An adopter must never learn the slug exists.

        `merge_chores_registry` is canonical-wins on shipped slugs, so a
        surviving entry would be ADDED to the adopter's registry while its files
        were withheld — a registered chore with no files, which `gz chores
        doctor` reports as MISSING. Withholding the files without withholding
        the entry trades a leak for a broken install.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            chores = _project(root)

            slugs = [c["slug"] for c in exportable_registry(chores / "registry.json")["chores"]]

            self.assertEqual(slugs, [_SHIPPED])

    def test_unmarked_entries_survive_unchanged(self) -> None:
        """Filtering must preserve the shipped entry byte-for-byte in content."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            chores = _project(root)

            exported = exportable_registry(chores / "registry.json")

            self.assertEqual(
                exported["chores"][0],
                {
                    "slug": _SHIPPED,
                    "title": "Coverage floor",
                    "path": f".gzkit/chores/{_SHIPPED}",
                    "lane": "lite",
                },
            )

    def test_sibling_registry_metadata_is_preserved(self) -> None:
        """Filtering touches `chores` only — specVersion/lanes/project survive."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            chores = _project(root)

            self.assertEqual(exportable_registry(chores / "registry.json")["specVersion"], "1.0.0")


class TestSyncWithholdsProjectLocalSlugs(unittest.TestCase):
    """End to end: the propagation that caused the defect no longer carries it."""

    def test_marked_slug_is_not_copied_into_the_package(self) -> None:
        """The observed symptom, inverted.

        GHI #728 recorded `git status` showing three files added under
        `src/gzkit/chores/test-consolidation-subtest-sweep/` after one sync.
        This asserts the package tree instead of the classifier so the wiring —
        not just the predicate — is what is proven.
        """
        from gzkit.config import GzkitConfig
        from gzkit.sync_surfaces import sync_pkg_surfaces

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _project(root)
            pkg_chores = root / "src" / "gzkit" / "chores"
            pkg_chores.mkdir(parents=True)
            (pkg_chores / "__init__.py").write_text("", encoding="utf-8")

            config = GzkitConfig(project_name="t")  # type: ignore[call-arg]
            sync_pkg_surfaces(root, config)

            self.assertFalse(
                (pkg_chores / _LOCAL).exists(),
                "a declared project-local slug was propagated into the wheel",
            )
            self.assertTrue(
                (pkg_chores / _SHIPPED / "CHORE.md").is_file(),
                "the shipped slug must still propagate",
            )


if __name__ == "__main__":
    unittest.main()
