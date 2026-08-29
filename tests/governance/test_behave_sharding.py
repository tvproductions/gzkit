"""Behave shards across processes; the gate's answer must not change (GHI #906).

Behave was single-threaded and cost 47-49s of a ~62s `gz check`. Measured
2026-08-28 at `87e88314` on a 10-core host, with per-shard exit accounting:

    baseline    gate 61.07s / 63.06s   Behave step 47.35s / 49.11s
    sharded x4  gate 50.45s            Behave step 33.85s
    sharded x8  gate 49.83s / 51.25s   Behave step 22.53s / 23.40s

**Four shards buys the same gate time as eight**, which is the finding. Behave
stops being the critical path around 34s, and past that every further shard is
contention with `Test` for no wall-clock return. The declared count is 4 for
that reason, not because 4 is the fastest way to run behave alone.

The shape is only safe because of two facts measured before it was written:

1. `features/environment.py` gives EVERY scenario a fresh `mkdtemp` and
   `chdir`s into it, with no `before_all` and no `before_feature`. `os.chdir`
   is process-global, so scenarios can never be threaded inside one
   interpreter -- and can always be split across processes.
2. Exactly one feature file drives the one path the concurrency declaration
   says Behave writes (`dist/`). Because the planner partitions files, that
   write lands in exactly one shard. `test_only_one_feature_drives_the_declared_write`
   below fails if a second one appears, because two writers in different
   shards WOULD race and the partition alone would not stop them.

GHI #835's ruling governs the risk and is why conservation is the first test
here rather than the speedup: *"A parallel runner over steps with an undeclared
dependency is a flaky gate, which is strictly worse than a slow one."*
"""

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.quality import (
    QualityResult,
    _aggregate_shard_results,
    _behave_shard_count,
    _plan_behave_shards,
)

REPO = Path(__file__).resolve().parents[2]


def _fixture_features(root: Path, sizes: dict[str, int]) -> None:
    features = root / "features"
    features.mkdir(parents=True, exist_ok=True)
    for name, size in sizes.items():
        (features / name).write_text("x" * size, encoding="utf-8")


class TestShardPlanner(unittest.TestCase):
    """The partition is the safety property; the balance is the speedup."""

    def test_every_feature_file_lands_in_exactly_one_shard(self) -> None:
        """Conservation: no scenario is dropped and none is run twice."""
        with tempfile.TemporaryDirectory(prefix="gzkit-shard-") as name:
            root = Path(name)
            _fixture_features(root, {f"f{i}.feature": 100 * (i + 1) for i in range(11)})

            shards = _plan_behave_shards(root, 4)

            planned = [path for shard in shards for path in shard]
            on_disk = sorted((root / "features").glob("*.feature"))
            self.assertEqual(sorted(planned), on_disk, "the partition lost or duplicated a file")
            self.assertEqual(len(planned), len(set(planned)), "a feature file was assigned twice")

    def test_no_shard_is_empty_when_files_outnumber_shards(self) -> None:
        """An empty shard is a process spawned to run nothing."""
        with tempfile.TemporaryDirectory(prefix="gzkit-shard-") as name:
            root = Path(name)
            _fixture_features(root, {f"f{i}.feature": 10 for i in range(9)})

            self.assertTrue(all(_plan_behave_shards(root, 4)))

    def test_fewer_files_than_shards_yields_one_shard_per_file(self) -> None:
        """The planner never emits more shards than there is work for."""
        with tempfile.TemporaryDirectory(prefix="gzkit-shard-") as name:
            root = Path(name)
            _fixture_features(root, {"a.feature": 10, "b.feature": 10})

            self.assertEqual(len(_plan_behave_shards(root, 8)), 2)

    def test_the_heaviest_file_does_not_share_with_the_rest(self) -> None:
        """Longest-processing-time ordering, not arbitrary chunking.

        A naive split keeps list order, so one 10000-byte file and nine tiny
        ones puts the big one in a shard with others and leaves the gate
        waiting on it plus its shard-mates. LPT places it alone.
        """
        with tempfile.TemporaryDirectory(prefix="gzkit-shard-") as name:
            root = Path(name)
            sizes = {"big.feature": 10_000}
            sizes.update({f"small{i}.feature": 10 for i in range(9)})
            _fixture_features(root, sizes)

            shards = _plan_behave_shards(root, 4)

            heaviest = next(s for s in shards if any(p.name == "big.feature" for p in s))
            self.assertEqual([p.name for p in heaviest], ["big.feature"])

    def test_no_features_directory_plans_nothing(self) -> None:
        """A project without features falls back to the single-process path."""
        with tempfile.TemporaryDirectory(prefix="gzkit-shard-") as name:
            self.assertEqual(_plan_behave_shards(Path(name), 4), [])


class TestShardCountDeclaration(unittest.TestCase):
    """The count is read from the declaration, never hard-coded at the call."""

    def test_absent_declaration_means_single_process(self) -> None:
        """Adopter projects have no declaration and keep today's behaviour.

        `_step_concurrency_classes` already returns ``{}`` for the same file and
        the same reason -- the declaration describes gzkit's own step set and is
        project-local. Sharding follows that precedent rather than inventing a
        package-data surface.
        """
        with tempfile.TemporaryDirectory(prefix="gzkit-shard-") as name:
            self.assertEqual(_behave_shard_count(Path(name)), 1)

    def test_declared_count_is_read_from_the_concurrency_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="gzkit-shard-") as name:
            root = Path(name)
            (root / "data").mkdir()
            (root / "data" / "check_step_concurrency.json").write_text(
                json.dumps({"steps": {"Behave": {"class": "writes", "shards": 3}}}),
                encoding="utf-8",
            )
            self.assertEqual(_behave_shard_count(root), 3)

    def test_malformed_declaration_falls_back_to_single_process(self) -> None:
        """A broken declaration must not take the gate down with it."""
        with tempfile.TemporaryDirectory(prefix="gzkit-shard-") as name:
            root = Path(name)
            (root / "data").mkdir()
            (root / "data" / "check_step_concurrency.json").write_text(
                "{ not json", encoding="utf-8"
            )
            self.assertEqual(_behave_shard_count(root), 1)


class TestShardFailureReporting(unittest.TestCase):
    """A failing scenario must stay findable across concurrent outputs."""

    @staticmethod
    def _result(*, success: bool, code: int, stdout: str) -> QualityResult:
        return QualityResult(
            success=success, command="uv run -m behave", stdout=stdout, stderr="", returncode=code
        )

    def test_one_failing_shard_fails_the_step(self) -> None:
        results = [
            self._result(success=True, code=0, stdout="ok a"),
            self._result(success=False, code=1, stdout="FAILED b"),
            self._result(success=True, code=0, stdout="ok c"),
        ]

        aggregate = _aggregate_shard_results(results, [["a.feature"], ["b.feature"], ["c.feature"]])

        self.assertFalse(aggregate.success)
        self.assertNotEqual(aggregate.returncode, 0)

    def test_the_failing_shard_is_reported_first_and_named(self) -> None:
        """Interleaved output is why this exists: the failure goes at the top.

        Four concurrent behave runs produce four summaries. Without ordering and
        attribution the operator scrolls a 400-scenario transcript looking for
        which one broke, and a gate whose failures are hard to read is a gate
        people route around.
        """
        results = [
            self._result(success=True, code=0, stdout="ok a"),
            self._result(success=False, code=1, stdout="FAILED b"),
        ]

        aggregate = _aggregate_shard_results(results, [["a.feature"], ["b.feature"]])

        first, _, rest = aggregate.stdout.partition("ok a")
        self.assertIn("FAILED b", first, "the failing shard's output must precede the passing one")
        self.assertIn("b.feature", first, "the failing shard must name the features it ran")
        self.assertEqual(rest, "", "the passing shard's output must still be present, after")

    def test_all_passing_shards_report_success(self) -> None:
        results = [self._result(success=True, code=0, stdout="ok")] * 2

        aggregate = _aggregate_shard_results(results, [["a.feature"], ["b.feature"]])

        self.assertTrue(aggregate.success)
        self.assertEqual(aggregate.returncode, 0)


class TestDeclaredWriteStaysInOneShard(unittest.TestCase):
    """The partition only protects `dist/` while one feature file writes it."""

    def test_only_one_feature_drives_the_declared_write(self) -> None:
        """Two wheel-building features in different shards would race.

        `data/check_step_concurrency.json` declares Behave a writer of `dist/`.
        The file partition guarantees that write lands in one shard ONLY while a
        single feature file drives it. If this fails, sharding is no longer safe
        as written -- either pin the writing features to the same shard or make
        the build hermetic, the way `tests/test_packaging.py` already does.
        """
        step_modules = sorted(
            path.name
            for path in (REPO / "features" / "steps").glob("*.py")
            if "uv build" in path.read_text(encoding="utf-8")
        )
        # Key on the step a feature INVOKES, never on the filename. Three
        # feature files carry "distribution" in their names and only this one
        # builds anything -- a name-shaped check reports two false writers and
        # would have to be silenced, which is how a fence stops being read.
        builders = sorted(
            path.name
            for path in (REPO / "features").glob("*.feature")
            if "build the wheel with uv build" in path.read_text(encoding="utf-8")
        )

        self.assertEqual(step_modules, ["distribution_invariant_steps.py"])
        self.assertEqual(builders, ["distribution_invariant.feature"])


if __name__ == "__main__":
    unittest.main()
