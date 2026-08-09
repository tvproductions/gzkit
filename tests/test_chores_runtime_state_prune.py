"""Sync CONVERGES the package chores tree; it does not only add to it (GHI #783).

71 ``runtime_state`` files across 29 slugs sat committed under
``src/gzkit/chores/*/proofs/`` while ``gz validate --distribution`` reported clean
and every doctrine surface declared them unshippable.

The classifier was never wrong. The defect is that both consumers of the class are
ONE-DIRECTIONAL: ``sync_pkg_surfaces`` walked the canonical side and copied
``canonical`` files, so it could never remove a package-side file it declines to
touch; and ``--distribution`` exempts ``runtime_state`` from both error classes, so
the exemption that stops it demanding these files be in the baseline manifest is
the same exemption that stops it noticing they are on disk in the wheel path.

**A class enforced by "skip it" converges only for files that do not yet exist.**
For files already present, "skip" and "exempt" compose into "invisible". These
tests pin the missing direction: a package-side file whose class must never ship
is REMOVED, not merely not-added.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.config import GzkitConfig
from gzkit.sync_surfaces import sync_pkg_surfaces

_SHIPPED = "coverage-40pct"
_LOCAL = "gzkit-internal-sweep"


def _project(root: Path) -> tuple[Path, Path]:
    """Build a canonical chores tree plus a package tree, and return both."""
    chores = root / ".gzkit" / "chores"
    for slug in (_SHIPPED, _LOCAL):
        (chores / slug).mkdir(parents=True, exist_ok=True)
        (chores / slug / "CHORE.md").write_text(f"# {slug}\n", encoding="utf-8")
    (chores / "registry.json").write_text(
        json.dumps(
            {
                "specVersion": "1.0.0",
                "chores": [
                    {
                        "slug": _SHIPPED,
                        "title": "Coverage floor",
                        "path": f".gzkit/chores/{_SHIPPED}",
                        "lane": "lite",
                    },
                    {
                        "slug": _LOCAL,
                        "title": "Internal sweep",
                        "path": f".gzkit/chores/{_LOCAL}",
                        "lane": "lite",
                        "projectLocal": True,
                    },
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    pkg_chores = root / "src" / "gzkit" / "chores"
    pkg_chores.mkdir(parents=True, exist_ok=True)
    (pkg_chores / "__init__.py").write_text("", encoding="utf-8")
    return chores, pkg_chores


def _sync(root: Path) -> list[str]:
    """Run the production sync and return the paths it reports changing."""
    return sync_pkg_surfaces(root, GzkitConfig(project_name="t"))  # type: ignore[call-arg]


def _pkg_files(root: Path) -> set[str]:
    """Every file under the package chores tree, relative and slash-normalised.

    Assertions target this computed set rather than ``path.exists()`` per
    `.gzkit/rules/tests.md` § Prefer structured assertion targets: a membership
    check on a collection states WHICH tree is being claimed, and a failure prints
    the whole tree instead of a bare ``True is not false``.
    """
    base = root / "src" / "gzkit" / "chores"
    return {
        p.relative_to(base).as_posix()
        for p in base.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }


def _pkg_dirs(root: Path) -> set[str]:
    """Every directory under the package chores tree, relative."""
    base = root / "src" / "gzkit" / "chores"
    return {
        p.relative_to(base).as_posix()
        for p in base.rglob("*")
        if p.is_dir() and "__pycache__" not in p.parts
    }


class TestRuntimeStateIsPruned(unittest.TestCase):
    """The observed symptom, inverted: proofs already in the wheel path are removed."""

    def test_existing_proofs_are_removed_from_the_package_tree(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, pkg_chores = _project(root)
            proofs = pkg_chores / _SHIPPED / "proofs"
            proofs.mkdir(parents=True)
            (proofs / "CHORE-LOG.md").write_text("run log\n", encoding="utf-8")
            (proofs / ".gitkeep").write_text("", encoding="utf-8")

            _sync(root)

            self.assertEqual(
                {f for f in _pkg_files(root) if "/proofs/" in f},
                set(),
                "runtime_state files survived sync in the wheel path",
            )

    def test_the_prune_reports_what_it_removed(self) -> None:
        """The removal is in sync's RETURN value, not only on disk.

        ``sync_pkg_surfaces`` reports every path it changed. A prune that deleted
        silently would leave an operator's sync output claiming nothing happened.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, pkg_chores = _project(root)
            proofs = pkg_chores / _SHIPPED / "proofs"
            proofs.mkdir(parents=True)
            (proofs / "CHORE-LOG.md").write_text("run log\n", encoding="utf-8")

            reported = _sync(root)

            self.assertIn(
                f"src/gzkit/chores/{_SHIPPED}/proofs/CHORE-LOG.md",
                reported,
                f"the prune did not report the file it removed: {reported}",
            )

    def test_emptied_proofs_directory_is_removed_too(self) -> None:
        """An empty ``proofs/`` still ships a directory the doctrine forbids."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, pkg_chores = _project(root)
            proofs = pkg_chores / _SHIPPED / "proofs"
            proofs.mkdir(parents=True)
            (proofs / "CHORE-LOG.md").write_text("run log\n", encoding="utf-8")

            _sync(root)

            self.assertNotIn(
                f"{_SHIPPED}/proofs",
                _pkg_dirs(root),
                "the emptied proofs/ directory was left behind",
            )

    def test_prune_is_idempotent(self) -> None:
        """A second sync over an already-clean tree changes nothing and does not raise."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, pkg_chores = _project(root)
            (pkg_chores / _SHIPPED / "proofs").mkdir(parents=True)
            (pkg_chores / _SHIPPED / "proofs" / "CHORE-LOG.md").write_text("x", encoding="utf-8")

            _sync(root)
            after_first = _pkg_files(root)
            second = _sync(root)

            self.assertEqual(second, [], f"a converged tree still reported changes: {second}")
            self.assertEqual(after_first, _pkg_files(root))


class TestProjectLocalResidueIsPruned(unittest.TestCase):
    """The same one-directional hole on the sibling class (GHI #728's residue).

    #728 stopped project-local slugs PROPAGATING; it could not remove one already
    committed, for exactly the reason this issue names. There is no such residue on
    disk today, which is why it never surfaced — the property is asserted so it
    cannot appear later.
    """

    def test_existing_project_local_slug_is_removed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, pkg_chores = _project(root)
            stale = pkg_chores / _LOCAL
            stale.mkdir(parents=True)
            (stale / "CHORE.md").write_text("# stale\n", encoding="utf-8")

            _sync(root)

            self.assertEqual(
                {f for f in _pkg_files(root) if f.startswith(f"{_LOCAL}/")},
                set(),
                "a project-local slug already in the wheel path survived sync",
            )


class TestPruneDoesNotOverreach(unittest.TestCase):
    """Negative controls: a prune that removed everything would satisfy the above.

    These are the reason the prune keys on the classifier rather than on a path
    glob — ``package_only`` files legitimately live on the package side with no
    ``.gzkit/`` counterpart, and deleting them would break the wheel.
    """

    def test_canonical_files_still_propagate(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _project(root)

            _sync(root)

            self.assertIn(
                f"{_SHIPPED}/CHORE.md",
                _pkg_files(root),
                "the shipped chore stopped propagating",
            )

    def test_package_only_files_survive(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, pkg_chores = _project(root)
            (pkg_chores / "_scaffolder.py").write_text("# package-only helper\n", encoding="utf-8")

            _sync(root)

            self.assertLessEqual(
                {"_scaffolder.py", "__init__.py"},
                _pkg_files(root),
                "a package_only module was pruned",
            )


class TestCommittedTreeIsClean(unittest.TestCase):
    """The instance: no runtime_state remains under the real package tree.

    Asserted through the production classifier rather than a path glob, so it
    tracks the class definition instead of restating one shape of it.
    """

    def test_no_runtime_state_under_src_gzkit_chores(self) -> None:
        from gzkit.chores import _classify_chore_file

        root = Path.cwd()
        pkg_chores = root / "src" / "gzkit" / "chores"
        if not pkg_chores.is_dir():  # pragma: no cover - source checkout only
            self.skipTest("package chores tree absent")
        offenders = [
            f.relative_to(root).as_posix()
            for f in sorted(pkg_chores.rglob("*"))
            if f.is_file()
            and "__pycache__" not in f.parts
            and _classify_chore_file(f, project_root=root) == "runtime_state"
        ]
        self.assertEqual(offenders, [], f"runtime_state files ship in the wheel: {offenders}")


if __name__ == "__main__":
    unittest.main()
