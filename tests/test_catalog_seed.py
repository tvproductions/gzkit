"""`gz init` delivers `data/catalog/` (RO-14, the fresh-project discrepancy).

A fresh project could not run a work package: the registry seam refuses a missing
file and no verb creates the store. These tests read the behaviour an adopter
meets, through the real verbs, plus the two properties a copy would lose: the
seed cannot drift from gzkit's own catalog, and the cutover is the project's.
"""

import json
import unittest
from datetime import UTC, datetime
from pathlib import Path

from gzkit.catalog_seed import load_seed, seed_catalog
from gzkit.cli import main
from gzkit.models.catalog import CATALOG_FILES, DELIVERY_EVENTS_FILE, load_catalog
from gzkit.registries import load_registry, registry_path
from tests.commands.common import (
    CliRunner,
    start_init_subprocess_patches,
    stop_init_subprocess_patches,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_INIT = ["init", "--no-skeleton"]


def setUpModule() -> None:
    """Stub the init subprocess boundaries (uv sync + ruff format)."""
    start_init_subprocess_patches()


def tearDownModule() -> None:
    stop_init_subprocess_patches()


class TestFreshProject(unittest.TestCase):
    """A project `gz init` just made can use the work-package surface."""

    def test_wp_runs_and_the_catalog_scope_pass_after_init(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, _INIT).exit_code, 0)
            runs = runner.invoke(main, ["wp", "runs"])
            self.assertEqual(runs.exit_code, 0, runs.output)
            self.assertIn("No work package is in flight", runs.output)
            scope = runner.invoke(main, ["validate", "--catalog"])
            self.assertEqual(scope.exit_code, 0, scope.output)

    def test_every_store_starts_empty(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, _INIT).exit_code, 0)
            catalog = load_catalog(Path())
            self.assertEqual(catalog.work_packages, ())
            self.assertEqual(catalog.outcomes, ())
            self.assertEqual(catalog.reqs, ())
            self.assertEqual(catalog.externals, ())

    def test_repair_restores_a_lost_file_and_keeps_the_others(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, _INIT).exit_code, 0)
            lost = registry_path(Path(), CATALOG_FILES["families"])
            kept = registry_path(Path(), CATALOG_FILES["work_packages"])
            held = kept.read_text(encoding="utf-8").replace('"_doc"', '"_doc"  ')
            kept.write_text(held, encoding="utf-8")
            lost.unlink()
            result = runner.invoke(main, _INIT)
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Seeded 1 data/catalog/ file(s)", result.output)
            self.assertTrue(lost.exists())
            self.assertEqual(kept.read_text(encoding="utf-8"), held)


class TestSeedCatalog(unittest.TestCase):
    """The writer's own contract."""

    def test_the_cutover_is_stamped_at_seeding_not_copied(self) -> None:
        now = datetime(2031, 5, 6, 7, 8, 9, tzinfo=UTC)
        runner = CliRunner()
        with runner.isolated_filesystem():
            seed_catalog(Path(), now=now)
            self.assertEqual(
                load_registry(Path(), DELIVERY_EVENTS_FILE)["cutover"], now.isoformat()
            )

    def test_a_dry_run_writes_nothing_and_says_what_it_would(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            status = seed_catalog(Path(), dry_run=True)
            self.assertEqual(status, f"Would seed {len(load_seed())} data/catalog/ file(s)")
            self.assertFalse(Path("data").exists())

    def test_a_complete_catalog_reports_nothing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            seed_catalog(Path())
            self.assertIsNone(seed_catalog(Path()))


class TestSeedMatchesCanon(unittest.TestCase):
    """The packaged seed cannot drift from gzkit's own `data/catalog/`."""

    def test_the_seed_names_every_catalog_file(self) -> None:
        expected = {*CATALOG_FILES.values(), DELIVERY_EVENTS_FILE}
        self.assertEqual(set(load_seed()), expected)

    def test_the_seed_equals_canon_apart_from_project_state(self) -> None:
        for name, seeded in load_seed().items():
            with self.subTest(name=name):
                path = registry_path(_REPO_ROOT, name)
                canon = json.loads(path.read_text(encoding="utf-8"))
                canon.pop("cutover", None)
                if name in {
                    CATALOG_FILES[kind]
                    for kind in ("outcomes", "reqs", "externals", "work_packages", "orders")
                }:
                    canon[next(key for key in canon if key != "_doc")] = []
                self.assertEqual(seeded, canon)


if __name__ == "__main__":
    unittest.main()
