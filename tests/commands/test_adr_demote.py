"""Unit tests for ``gz adr demote`` — the inverse of ``gz adr promote``.

Derived from the 2026-05-23 get-out-of-jail prequel spec (GHI #521):

- Q1=b: brief files deleted on demotion
- Q2=c: history in ledger event payload, not frontmatter
- Q5=a: ``artifact_renamed`` event with ``reason='pool_demotion'`` (no new event type)
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, adr_created_event
from tests.commands.common import CliRunner, _quick_init

_SAMPLE_FEATURE_ADR_ID = "ADR-0.27.0-arb-receipt-system-absorption"
_SAMPLE_POOL_ID = "ADR-pool.arb-receipt-system-absorption"


def _seed_feature_adr(
    config: GzkitConfig,
    adr_id: str = _SAMPLE_FEATURE_ADR_ID,
    *,
    kind: str = "feature",
    semver: str = "0.27.0",
    parent: str = "PRD-GZKIT-1.0.0",
    extra_briefs: int = 2,
) -> Path:
    """Seed a feature-shaped ADR package with frontmatter + briefs."""
    adr_root = Path(config.paths.adrs) / "pre-release" / adr_id
    adr_root.mkdir(parents=True, exist_ok=True)
    adr_file = adr_root / f"{adr_id}.md"
    adr_file.write_text(
        "---\n"
        f"id: {adr_id}\n"
        "status: Pending\n"
        f"kind: {kind}\n"
        f"semver: {semver}\n"
        "lane: heavy\n"
        f"parent: {parent}\n"
        "date: 2026-03-21\n"
        "---\n\n"
        f"# {adr_id}: Sample\n\n"
        "## Intent\n\nA seeded ADR for testing demotion.\n",
        encoding="utf-8",
    )
    briefs_dir = adr_root / "obpis"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    for idx in range(1, extra_briefs + 1):
        (briefs_dir / f"OBPI-{semver}-{idx:02d}-sample.md").write_text(
            f"# OBPI-{semver}-{idx:02d}\n\nSeeded brief.\n", encoding="utf-8"
        )
    (adr_root / "ADR-CLOSEOUT-FORM.md").write_text("# Closeout form\n", encoding="utf-8")
    return adr_file


class CollisionWithRetainedIntake(unittest.TestCase):
    """Demoting an ADR whose pool intake was retained on promotion (GHI #775).

    `gz adr promote` keeps the pool file as historical intake, so any
    promote/demote round trip collides. Both original policies lost something:
    `fail` refused outright, and `keep-pool` preserved the pre-promotion intake
    while `rmtree` deleted the evolved package -- silently, exit 0, discarding
    every decision recorded after promotion. Observed on
    `ADR-0.44.0-vendor-alignment-codex`, where the two documents had diverged by
    139 insertions / 140 deletions.
    """

    def _seed_with_intake(self, config: GzkitConfig) -> tuple[Path, Path]:
        adr_file = _seed_feature_adr(config)
        pool_file = Path(config.paths.adrs) / "pool" / f"{_SAMPLE_POOL_ID}.md"
        pool_file.parent.mkdir(parents=True, exist_ok=True)
        pool_file.write_text(
            "---\n"
            f"id: {_SAMPLE_POOL_ID}\n"
            "status: Superseded\n"
            f"promoted_to: {_SAMPLE_FEATURE_ADR_ID}\n"
            "---\n\n"
            f"# {_SAMPLE_POOL_ID}: Sample\n\n"
            "STALE INTAKE FROM BEFORE PROMOTION\n",
            encoding="utf-8",
        )
        return adr_file, pool_file

    def test_take_demoted_writes_the_evolved_content_to_pool(self) -> None:
        """The policy the round trip actually needs: current thinking wins."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _adr_file, pool_file = self._seed_with_intake(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    _SAMPLE_FEATURE_ADR_ID,
                    "--ghi",
                    "775",
                    "--on-collision",
                    "take-demoted",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            landed = pool_file.read_text(encoding="utf-8")
            self.assertIn(
                "A seeded ADR for testing demotion.",
                landed,
                "the demoted ADR's body must become the pool file",
            )
            self.assertNotIn(
                "STALE INTAKE FROM BEFORE PROMOTION",
                landed,
                "the superseded intake must not survive over live content",
            )
            self.assertIn(f"id: {_SAMPLE_POOL_ID}", landed)

    def test_keep_pool_still_preserves_the_intake(self) -> None:
        """The existing policy is unchanged -- this adds a third, replaces none.

        Without this pole the new policy could have been implemented by quietly
        redefining `keep-pool`, which would change behaviour for every caller
        that already relies on it.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _adr_file, pool_file = self._seed_with_intake(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    _SAMPLE_FEATURE_ADR_ID,
                    "--ghi",
                    "775",
                    "--on-collision",
                    "keep-pool",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(
                "STALE INTAKE FROM BEFORE PROMOTION",
                pool_file.read_text(encoding="utf-8"),
            )

    def test_fail_is_still_the_default(self) -> None:
        """Refusing remains the default: silent content loss must stay opt-in."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_file, _pool_file = self._seed_with_intake(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            result = runner.invoke(main, ["adr", "demote", _SAMPLE_FEATURE_ADR_ID, "--ghi", "775"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertTrue(adr_file.exists(), "a refused demotion must not delete the source")


class TestAdrDemoteCommand(unittest.TestCase):
    """``gz adr demote`` — universal queue-collapse tooling."""

    def test_dry_run_reports_plan_without_writes(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_file = _seed_feature_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))
            initial_ledger = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")

            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    _SAMPLE_FEATURE_ADR_ID,
                    "--ghi",
                    "520",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(f"Source ADR: {_SAMPLE_FEATURE_ADR_ID}", result.output)
            self.assertIn(f"Target pool ID: {_SAMPLE_POOL_ID}", result.output)
            self.assertIn("reason: pool_demotion", result.output)
            self.assertIn("ghi: 520", result.output)
            self.assertTrue(adr_file.exists(), "Dry-run must not delete source file")
            self.assertEqual(
                Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8"),
                initial_ledger,
                "Dry-run must not append ledger events",
            )

    def test_apply_moves_file_strips_frontmatter_deletes_briefs(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_file = _seed_feature_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    _SAMPLE_FEATURE_ADR_ID,
                    "--ghi",
                    "520",
                    "--note",
                    "prequel queue collapse",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            pool_file = Path(config.paths.adrs) / "pool" / f"{_SAMPLE_POOL_ID}.md"
            self.assertTrue(pool_file.exists(), "Pool file must be created")
            self.assertFalse(adr_file.exists(), "Source ADR file must be removed")
            self.assertFalse(
                adr_file.parent.exists(),
                "Source package directory (briefs + closeout form) must be removed (Q1=b)",
            )
            pool_content = pool_file.read_text(encoding="utf-8")
            self.assertIn(f"id: {_SAMPLE_POOL_ID}", pool_content)
            self.assertIn("status: Pool", pool_content)
            self.assertNotIn("kind: feature", pool_content)
            self.assertNotIn("semver: 0.27.0", pool_content)
            self.assertNotIn("date: 2026-03-21", pool_content)
            self.assertIn("lane: heavy", pool_content)
            self.assertIn("parent: PRD-GZKIT-1.0.0", pool_content)

    def test_apply_emits_artifact_renamed_with_pool_demotion_payload(self) -> None:
        """Q5=a: reuses ``artifact_renamed`` event with extras carrying history."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    _SAMPLE_FEATURE_ADR_ID,
                    "--ghi",
                    "520",
                    "--note",
                    "prequel queue collapse",
                    "--operator",
                    "g0",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            ledger_lines = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8").splitlines()
            rename_events = [
                json.loads(line) for line in ledger_lines if '"event":"artifact_renamed"' in line
            ]
            demote_events = [
                event for event in rename_events if event.get("reason") == "pool_demotion"
            ]
            self.assertEqual(
                len(demote_events), 1, msg=f"Expected one demote event, got {demote_events}"
            )
            event = demote_events[0]
            self.assertEqual(event["id"], _SAMPLE_FEATURE_ADR_ID)
            self.assertEqual(event["new_id"], _SAMPLE_POOL_ID)
            self.assertEqual(event["prior_kind"], "feature")
            self.assertEqual(event["prior_semver"], "0.27.0")
            self.assertEqual(event["ghi"], 520)
            self.assertEqual(event["operator"], "g0")
            self.assertEqual(event["note"], "prequel queue collapse")
            self.assertIn("demoted_at", event)

    def test_json_output_emits_structured_payload(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    _SAMPLE_FEATURE_ADR_ID,
                    "--ghi",
                    "520",
                    "--dry-run",
                    "--json",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            json_start = result.output.find("{")
            self.assertGreaterEqual(json_start, 0, msg="JSON output expected on stdout")
            payload = json.loads(result.output[json_start:].split("\n}", 1)[0] + "\n}")
            self.assertEqual(payload["source_id"], _SAMPLE_FEATURE_ADR_ID)
            self.assertEqual(payload["new_id"], _SAMPLE_POOL_ID)
            self.assertEqual(payload["dry_run"], True)
            self.assertEqual(payload["extras"]["ghi"], 520)
            self.assertEqual(payload["extras"]["prior_kind"], "feature")

    def test_rejects_pool_adr_input(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    "ADR-pool.already-in-pool",
                    "--ghi",
                    "520",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("already in pool", result.output)

    def test_rejects_collision_with_existing_pool_file(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            (pool_dir / f"{_SAMPLE_POOL_ID}.md").write_text(
                "---\nid: pre-existing\n---\n", encoding="utf-8"
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    _SAMPLE_FEATURE_ADR_ID,
                    "--ghi",
                    "520",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("collision", result.output)

    def test_blocks_demotion_when_children_reference_parent(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            # Seed a child ADR referencing the soon-to-be-demoted one as parent.
            child_dir = Path(config.paths.adrs) / "pre-release" / "ADR-0.28.0-child"
            child_dir.mkdir(parents=True, exist_ok=True)
            (child_dir / "ADR-0.28.0-child.md").write_text(
                "---\n"
                "id: ADR-0.28.0-child\n"
                "status: Pending\n"
                "kind: feature\n"
                "semver: 0.28.0\n"
                "lane: lite\n"
                f"parent: {_SAMPLE_FEATURE_ADR_ID}\n"
                "---\n\n# Child\n",
                encoding="utf-8",
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    _SAMPLE_FEATURE_ADR_ID,
                    "--ghi",
                    "520",
                ],
            )
            self.assertEqual(result.exit_code, 3, msg=result.output)
            self.assertIn("Demotion blocked", result.output)
            self.assertIn("ADR-0.28.0-child", result.output)

    def test_force_overrides_children_block(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            child_dir = Path(config.paths.adrs) / "pre-release" / "ADR-0.28.0-child"
            child_dir.mkdir(parents=True, exist_ok=True)
            (child_dir / "ADR-0.28.0-child.md").write_text(
                "---\n"
                "id: ADR-0.28.0-child\n"
                "status: Pending\n"
                "kind: feature\n"
                "semver: 0.28.0\n"
                "lane: lite\n"
                f"parent: {_SAMPLE_FEATURE_ADR_ID}\n"
                "---\n\n# Child\n",
                encoding="utf-8",
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    _SAMPLE_FEATURE_ADR_ID,
                    "--ghi",
                    "520",
                    "--force",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            pool_file = Path(config.paths.adrs) / "pool" / f"{_SAMPLE_POOL_ID}.md"
            self.assertTrue(pool_file.exists())

    def test_on_collision_keep_pool_deletes_source_and_leaves_pool(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_file = pool_dir / f"{_SAMPLE_POOL_ID}.md"
            pre_existing = (
                "---\nid: ADR-pool.arb-receipt-system-absorption\n"
                "status: Pool\n---\n\n# Pre-existing pool\n"
            )
            pool_file.write_text(pre_existing, encoding="utf-8")
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    _SAMPLE_FEATURE_ADR_ID,
                    "--ghi",
                    "520",
                    "--on-collision",
                    "keep-pool",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            # Pool file content unchanged (pre-existing preserved).
            self.assertEqual(pool_file.read_text(encoding="utf-8"), pre_existing)
            # Source feature directory removed.
            source_dir = Path(config.paths.adrs) / "pre-release" / _SAMPLE_FEATURE_ADR_ID
            self.assertFalse(source_dir.exists())
            # Ledger event records the collision resolution.
            events = [
                json.loads(line)
                for line in Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            rename_events = [e for e in events if e.get("event") == "artifact_renamed"]
            self.assertEqual(len(rename_events), 1)
            self.assertEqual(rename_events[0].get("collision_resolution"), "keep-pool")
            self.assertEqual(rename_events[0].get("reason"), "pool_demotion")

    def test_on_collision_keep_pool_reverses_stale_promotion_markers(self) -> None:
        """GHI #558: demoting back through a prior promotion must undo what
        ``gz adr promote`` wrote on the pool side (status/promoted_to/note),
        not just delete the feature package and leave the pool file stale."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_file = pool_dir / f"{_SAMPLE_POOL_ID}.md"
            previously_promoted = (
                "---\n"
                f"id: {_SAMPLE_POOL_ID}\n"
                "status: Superseded\n"
                "parent: PRD-GZKIT-1.0.0\n"
                f"promoted_to: {_SAMPLE_FEATURE_ADR_ID}\n"
                "---\n\n"
                f"# {_SAMPLE_POOL_ID}: Sample\n"
                f"> Promoted to `{_SAMPLE_FEATURE_ADR_ID}` on 2026-03-21. "
                "This pool file is retained as historical intake context.\n\n"
                "## Status\n\nSuperseded\n\n## Intent\n\nSeeded pool ADR.\n"
            )
            pool_file.write_text(previously_promoted, encoding="utf-8")
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    _SAMPLE_FEATURE_ADR_ID,
                    "--ghi",
                    "558",
                    "--on-collision",
                    "keep-pool",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            reversed_content = pool_file.read_text(encoding="utf-8")
            self.assertIn("status: Pool", reversed_content)
            self.assertNotIn("status: Superseded", reversed_content)
            self.assertNotIn("promoted_to:", reversed_content)
            self.assertNotIn("> Promoted to", reversed_content)
            self.assertIn("## Intent\n\nSeeded pool ADR.\n", reversed_content)

    def test_on_collision_keep_pool_ignores_unrelated_promoted_to(self) -> None:
        """A collision with a pool file promoted to a DIFFERENT ADR must not
        be mutated — only a stale record naming the ADR being demoted (right
        now) is reversed (GHI #558 no-op guard)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_file = pool_dir / f"{_SAMPLE_POOL_ID}.md"
            unrelated_promotion = (
                "---\n"
                f"id: {_SAMPLE_POOL_ID}\n"
                "status: Superseded\n"
                "promoted_to: ADR-0.99.0-someone-else\n"
                "---\n\n"
                f"# {_SAMPLE_POOL_ID}: Sample\n"
            )
            pool_file.write_text(unrelated_promotion, encoding="utf-8")
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    _SAMPLE_FEATURE_ADR_ID,
                    "--ghi",
                    "558",
                    "--on-collision",
                    "keep-pool",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(pool_file.read_text(encoding="utf-8"), unrelated_promotion)

    def test_on_collision_fail_is_default(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _seed_feature_adr(config)
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            (pool_dir / f"{_SAMPLE_POOL_ID}.md").write_text(
                "---\nid: pre-existing\n---\n", encoding="utf-8"
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(_SAMPLE_FEATURE_ADR_ID, "", "heavy"))

            # Explicit --on-collision fail behaves identically to default.
            result = runner.invoke(
                main,
                [
                    "adr",
                    "demote",
                    _SAMPLE_FEATURE_ADR_ID,
                    "--ghi",
                    "520",
                    "--on-collision",
                    "fail",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("collision", result.output)

    def test_argparse_requires_ghi(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                ["adr", "demote", _SAMPLE_FEATURE_ADR_ID],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("--ghi", result.output)


if __name__ == "__main__":
    unittest.main()
