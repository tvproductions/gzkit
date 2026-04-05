import json
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    obpi_created_event,
    obpi_receipt_emitted_event,
)
from gzkit.quality import QualityResult
from gzkit.traceability import covers  # noqa: F401
from tests.commands.common import CliRunner, _quick_init


class TestObpiPipelineCommand(unittest.TestCase):
    """Tests for the OBPI pipeline runtime command surface."""

    @staticmethod
    def _load_json(path: Path) -> dict[str, str]:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _seed_parent_adr(
        config: GzkitConfig,
        adr_id: str,
        *,
        semver: str = "0.13.0",
        lane: str = "heavy",
    ) -> Path:
        adr_dir = Path(config.paths.adrs) / "pre-release" / adr_id
        adr_dir.mkdir(parents=True, exist_ok=True)
        adr_file = adr_dir / f"{adr_id}.md"
        adr_file.write_text(
            "---\n"
            f"id: {adr_id}\n"
            "status: Proposed\n"
            f"semver: {semver}\n"
            f"lane: {lane}\n"
            "parent: PRD-GZKIT-1.0.0\n"
            "date: 2026-03-13\n"
            "---\n\n"
            f"# {adr_id}: Demo Pipeline ADR\n",
            encoding="utf-8",
        )
        return adr_file

    @staticmethod
    def _seed_obpi(
        config: GzkitConfig,
        parent_adr: str,
        *,
        obpi_id: str = "OBPI-0.13.0-01-runtime-command-contract",
        completed: bool = False,
    ) -> Path:
        obpi_dir = Path(config.paths.adrs) / "pre-release" / parent_adr / "obpis"
        obpi_dir.mkdir(parents=True, exist_ok=True)
        obpi_file = obpi_dir / f"{obpi_id}.md"
        brief_status = "Completed" if completed else "Draft"
        frontmatter_status = "Completed" if completed else "Draft"
        obpi_file.write_text(
            "---\n"
            f"id: {obpi_id}\n"
            f"parent: {parent_adr}\n"
            "item: 1\n"
            "lane: Heavy\n"
            f"status: {frontmatter_status}\n"
            "---\n\n"
            f"# {obpi_id}: Runtime Command Contract\n\n"
            f"**Brief Status:** {brief_status}\n\n"
            "## Verification\n\n"
            "```bash\n"
            "uv run gz validate --documents\n"
            "uv run gz lint\n"
            "uv run gz typecheck\n"
            "uv run gz test\n"
            "python -c \"print('verify ok')\"\n"
            "```\n",
            encoding="utf-8",
        )
        return obpi_file

    @staticmethod
    def _write_receipt(project_root: Path, *, obpi_id: str, verdict: str) -> None:
        plans_dir = project_root / ".claude" / "plans"
        plans_dir.mkdir(parents=True, exist_ok=True)
        (plans_dir / ".plan-audit-receipt.json").write_text(
            json.dumps(
                {
                    "obpi_id": obpi_id,
                    "timestamp": "2026-03-13T12:00:00Z",
                    "verdict": verdict,
                }
            )
            + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _pipeline_paths(
        project_root: Path, obpi_id: str = "OBPI-0.13.0-01-runtime-command-contract"
    ) -> tuple[Path, Path]:
        plans_dir = project_root / ".claude" / "plans"
        return (
            plans_dir / f".pipeline-active-{obpi_id}.json",
            plans_dir / ".pipeline-active.json",
        )

    def _seed_runtime(
        self,
        runner: CliRunner,
        *,
        parent_adr: str = "ADR-0.13.0-obpi-pipeline-runtime-surface",
        parent_semver: str = "0.13.0",
        parent_lane: str = "heavy",
        config_mode: str = "heavy",
        obpi_id: str = "OBPI-0.13.0-01-runtime-command-contract",
    ) -> None:
        runner.invoke(main, ["init", "--mode", config_mode])
        config = GzkitConfig.load(Path(".gzkit.json"))
        self._seed_parent_adr(config, parent_adr, semver=parent_semver, lane=parent_lane)
        self._seed_obpi(config, parent_adr, obpi_id=obpi_id)
        ledger = Ledger(Path(".gzkit/ledger.jsonl"))
        ledger.append(adr_created_event(parent_adr, "PRD-GZKIT-1.0.0", config_mode))
        ledger.append(obpi_created_event(obpi_id, parent_adr))

    def test_full_launch_accepts_short_id_and_creates_markers(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_runtime(runner)

            result = runner.invoke(main, ["obpi", "pipeline", "0.13.0-01-runtime-command-contract"])

            self.assertEqual(result.exit_code, 0)
            self.assertIn("OBPI pipeline: OBPI-0.13.0-01-runtime-command-contract", result.output)
            self.assertIn("Stages: 1. Load Context -> 2. Implement -> 3. Verify", result.output)
            self.assertIn("5. Sync And Account", result.output)
            self.assertIn("OBPI-0.13.0-01-runtime-command-contract --from=verify", result.output)
            marker_path, legacy_path = self._pipeline_paths(Path.cwd())
            self.assertTrue(marker_path.exists())
            self.assertTrue(legacy_path.exists())
            payload = self._load_json(marker_path)
            self.assertEqual(payload["obpi_id"], "OBPI-0.13.0-01-runtime-command-contract")
            self.assertEqual(payload["parent_adr"], "ADR-0.13.0-obpi-pipeline-runtime-surface")
            self.assertEqual(payload["lane"], "heavy")
            self.assertEqual(payload["entry"], "full")
            self.assertEqual(payload["execution_mode"], "normal")
            self.assertEqual(payload["current_stage"], "implement")
            self.assertEqual(payload["receipt_state"], "missing")
            self.assertEqual(payload["blockers"], [])
            self.assertIsNone(payload["required_human_action"])
            self.assertEqual(
                payload["next_command"],
                "uv run gz obpi pipeline OBPI-0.13.0-01-runtime-command-contract --from=verify",
            )
            self.assertEqual(payload["resume_point"], "verify")
            self.assertIn("started_at", payload)
            self.assertIn("updated_at", payload)
            self.assertEqual(payload, self._load_json(legacy_path))

    def test_blocks_when_matching_receipt_verdict_is_fail(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_runtime(runner)
            self._write_receipt(
                Path.cwd(),
                obpi_id="OBPI-0.13.0-01-runtime-command-contract",
                verdict="FAIL",
            )

            result = runner.invoke(
                main,
                ["obpi", "pipeline", "OBPI-0.13.0-01-runtime-command-contract"],
            )

            self.assertEqual(result.exit_code, 1)
            self.assertIn("BLOCKERS:", result.output)
            self.assertIn("plan-audit receipt verdict is FAIL", result.output)
            marker_path, legacy_path = self._pipeline_paths(Path.cwd())
            self.assertFalse(marker_path.exists())
            self.assertFalse(legacy_path.exists())

    @patch("gzkit.cli.main.run_command")
    @covers("REQ-0.13.0-03-02")
    def test_verify_runs_commands_and_preserves_markers(self, run_command_mock) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_runtime(runner)
            run_command_mock.return_value = QualityResult(
                success=True,
                command="ok",
                stdout="ok",
                stderr="",
                returncode=0,
            )

            result = runner.invoke(
                main,
                ["obpi", "pipeline", "OBPI-0.13.0-01-runtime-command-contract", "--from=verify"],
            )

            self.assertEqual(result.exit_code, 0)
            self.assertIn("Verification passed. Chaining into ceremony.", result.output)
            self.assertIn("Stage 4: Ceremony", result.output)
            self.assertIn("Human attestation required.", result.output)
            self.assertIn("--from=sync", result.output)
            # Verify the verification commands were executed (first 7 calls)
            verify_commands = [call.args[0] for call in run_command_mock.call_args_list[:7]]
            self.assertEqual(
                verify_commands,
                [
                    "uv run gz lint",
                    "uv run gz typecheck",
                    "uv run gz test",
                    "uv run gz validate --documents",
                    "python -c \"print('verify ok')\"",
                    "uv run mkdocs build --strict",
                    "uv run -m behave features/",
                ],
            )
            marker_path, legacy_path = self._pipeline_paths(Path.cwd())
            self.assertTrue(marker_path.exists())
            self.assertTrue(legacy_path.exists())

    @patch("gzkit.cli.main.run_command")
    def test_verify_rewrites_markers_with_verify_stage_state(self, run_command_mock) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_runtime(runner)
            run_command_mock.return_value = QualityResult(
                success=True,
                command="ok",
                stdout="ok",
                stderr="",
                returncode=0,
            )

            result = runner.invoke(
                main,
                ["obpi", "pipeline", "OBPI-0.13.0-01-runtime-command-contract", "--from=verify"],
            )

            self.assertEqual(result.exit_code, 0)
            marker_path, legacy_path = self._pipeline_paths(Path.cwd())
            payload = self._load_json(marker_path)
            self.assertEqual(payload["entry"], "verify")
            self.assertEqual(payload["current_stage"], "verify")
            self.assertEqual(payload["receipt_state"], "missing")
            self.assertEqual(payload["blockers"], [])
            self.assertIsNone(payload["required_human_action"])
            self.assertEqual(
                payload["next_command"],
                "uv run gz obpi pipeline OBPI-0.13.0-01-runtime-command-contract --from=ceremony",
            )
            self.assertEqual(payload["resume_point"], "ceremony")
            self.assertEqual(payload["parent_adr"], "ADR-0.13.0-obpi-pipeline-runtime-surface")
            self.assertEqual(payload["lane"], "heavy")
            self.assertEqual(payload, self._load_json(legacy_path))

    @patch("gzkit.cli.main.run_command")
    def test_verify_failure_persists_blockers_and_resume_point(self, run_command_mock) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_runtime(runner)

            def command_result(command: str, cwd: Path) -> QualityResult:
                if command == "uv run gz lint":
                    return QualityResult(
                        success=False,
                        command=command,
                        stdout="",
                        stderr="lint failed",
                        returncode=1,
                    )
                return QualityResult(
                    success=True,
                    command=command,
                    stdout="ok",
                    stderr="",
                    returncode=0,
                )

            run_command_mock.side_effect = command_result

            result = runner.invoke(
                main,
                ["obpi", "pipeline", "OBPI-0.13.0-01-runtime-command-contract", "--from=verify"],
            )

            self.assertEqual(result.exit_code, 1)
            self.assertIn("BLOCKERS:", result.output)
            self.assertIn("uv run gz lint: lint failed", result.output)
            marker_path, legacy_path = self._pipeline_paths(Path.cwd())
            self.assertTrue(marker_path.exists())
            self.assertTrue(legacy_path.exists())
            payload = self._load_json(marker_path)
            self.assertEqual(payload["entry"], "verify")
            self.assertEqual(payload["current_stage"], "verify")
            self.assertEqual(payload["blockers"], ["uv run gz lint: lint failed"])
            self.assertIsNone(payload["required_human_action"])
            self.assertIsNone(payload["next_command"])
            self.assertEqual(payload["resume_point"], "verify")
            self.assertEqual(payload, self._load_json(legacy_path))

    @covers("REQ-0.13.0-03-02")
    def test_ceremony_prints_next_steps_and_preserves_markers(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_runtime(runner)

            result = runner.invoke(
                main,
                ["obpi", "pipeline", "OBPI-0.13.0-01-runtime-command-contract", "--from=ceremony"],
            )

            self.assertEqual(result.exit_code, 0)
            self.assertIn("Stage 4: Ceremony", result.output)
            self.assertIn("Human attestation required.", result.output)
            self.assertIn("--from=sync", result.output)
            self.assertIn("--attestor <name>", result.output)
            marker_path, legacy_path = self._pipeline_paths(Path.cwd())
            self.assertTrue(marker_path.exists())
            self.assertTrue(legacy_path.exists())

    @covers("REQ-0.13.0-03-04")
    def test_ceremony_rewrites_markers_with_ceremony_stage_state(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_runtime(runner)

            result = runner.invoke(
                main,
                ["obpi", "pipeline", "OBPI-0.13.0-01-runtime-command-contract", "--from=ceremony"],
            )

            self.assertEqual(result.exit_code, 0)
            marker_path, legacy_path = self._pipeline_paths(Path.cwd())
            payload = self._load_json(marker_path)
            self.assertEqual(payload["entry"], "ceremony")
            self.assertEqual(payload["current_stage"], "ceremony")
            self.assertEqual(payload["receipt_state"], "missing")
            self.assertEqual(payload["blockers"], [])
            self.assertEqual(
                payload["required_human_action"],
                "Present evidence and obtain explicit human attestation before "
                "completion accounting.",
            )
            self.assertEqual(
                payload["next_command"],
                "uv run gz obpi pipeline OBPI-0.13.0-01-runtime-command-contract --from=sync",
            )
            self.assertEqual(payload["resume_point"], "sync")
            self.assertEqual(payload["parent_adr"], "ADR-0.13.0-obpi-pipeline-runtime-surface")
            self.assertEqual(payload["lane"], "heavy")
            self.assertEqual(payload, self._load_json(legacy_path))

    @patch("gzkit.cli.main.run_command")
    @covers("REQ-0.13.0-04-02")
    def test_ceremony_lite_parent_self_closes_and_chains_sync(self, run_command_mock) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_runtime(
                runner,
                parent_adr="ADR-1.2.3-lite-obpi-demo",
                parent_semver="1.2.3",
                parent_lane="lite",
                config_mode="lite",
            )
            run_command_mock.return_value = QualityResult(
                success=True,
                command="ok",
                stdout="ok",
                stderr="",
                returncode=0,
            )

            result = runner.invoke(
                main,
                ["obpi", "pipeline", "OBPI-0.13.0-01-runtime-command-contract", "--from=ceremony"],
            )

            self.assertEqual(result.exit_code, 0)
            self.assertIn("Self-closing and chaining into sync.", result.output)
            self.assertIn("Stage 5: Sync And Account", result.output)
            self.assertIn("Pipeline complete.", result.output)
            marker_path, legacy_path = self._pipeline_paths(Path.cwd())
            self.assertFalse(marker_path.exists())
            self.assertFalse(legacy_path.exists())

    @covers("REQ-0.13.0-04-01")
    @covers("REQ-0.13.0-04-03")
    def test_ceremony_foundation_parent_requires_human_attestation(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_runtime(
                runner,
                parent_adr="ADR-0.0.5-foundation-obpi-demo",
                parent_semver="0.0.5",
                parent_lane="lite",
                config_mode="lite",
                obpi_id="OBPI-0.0.5-01-runtime-command-contract",
            )

            result = runner.invoke(
                main,
                ["obpi", "pipeline", "OBPI-0.0.5-01-runtime-command-contract", "--from=ceremony"],
            )

            self.assertEqual(result.exit_code, 0)
            self.assertIn("Human attestation required.", result.output)
            self.assertIn("--from=sync", result.output)
            self.assertIn("--attestor <name>", result.output)
            marker_path, legacy_path = self._pipeline_paths(
                Path.cwd(), "OBPI-0.0.5-01-runtime-command-contract"
            )
            payload = self._load_json(marker_path)
            self.assertEqual(
                payload["required_human_action"],
                "Present evidence and obtain explicit human attestation before "
                "completion accounting.",
            )
            self.assertEqual(payload["lane"], "lite")
            self.assertEqual(payload["parent_adr"], "ADR-0.0.5-foundation-obpi-demo")
            self.assertEqual(payload, self._load_json(legacy_path))

    def test_sync_stage_requires_attestor(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_runtime(runner)

            result = runner.invoke(
                main,
                ["obpi", "pipeline", "OBPI-0.13.0-01-runtime-command-contract", "--from=sync"],
            )

            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("--attestor is required", result.output)

    @patch("gzkit.cli.main.run_command")
    def test_sync_stage_executes_and_clears_markers(self, run_command_mock) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_runtime(runner)
            run_command_mock.return_value = QualityResult(
                success=True,
                command="ok",
                stdout="ok",
                stderr="",
                returncode=0,
            )
            evidence = json.dumps({"value_narrative": "test", "key_proof": "proof"})

            result = runner.invoke(
                main,
                [
                    "obpi",
                    "pipeline",
                    "OBPI-0.13.0-01-runtime-command-contract",
                    "--from=sync",
                    "--attestor",
                    "human:tester",
                    "--evidence-json",
                    evidence,
                ],
            )

            self.assertEqual(result.exit_code, 0)
            self.assertIn("Stage 5: Sync And Account", result.output)
            self.assertIn("Pipeline complete.", result.output)
            marker_path, legacy_path = self._pipeline_paths(Path.cwd())
            self.assertFalse(marker_path.exists())
            self.assertFalse(legacy_path.exists())
            # Verify sync commands were executed in correct order (GHI #36):
            # git-sync BEFORE emit-receipt, accounting commit AFTER reconcile
            executed = [call.args[0] for call in run_command_mock.call_args_list]
            self.assertTrue(any("emit-receipt" in cmd for cmd in executed))
            self.assertTrue(any("reconcile" in cmd for cmd in executed))
            self.assertTrue(any("git-sync" in cmd for cmd in executed))
            sync_idx = next(i for i, c in enumerate(executed) if "git-sync" in c)
            emit_idx = next(i for i, c in enumerate(executed) if "emit-receipt" in c)
            self.assertLess(sync_idx, emit_idx, "git-sync must run before emit-receipt")
            # Accounting commit should appear after the core steps
            self.assertTrue(any("git add" in cmd for cmd in executed))
            self.assertTrue(any("git commit" in cmd for cmd in executed))
            self.assertTrue(any("git push" in cmd for cmd in executed))

    @patch("gzkit.cli.main.run_command")
    def test_sync_stage_accounting_commit_failure_is_nonfatal(self, run_command_mock) -> None:
        """Accounting commit failure should warn, not block pipeline completion."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_runtime(runner)

            def side_effect(command: str, **_kwargs: object) -> QualityResult:
                if any(kw in command for kw in ("git add", "git commit", "git push")):
                    return QualityResult(
                        success=False,
                        command=command,
                        stdout="",
                        stderr="nothing to commit",
                        returncode=1,
                    )
                return QualityResult(
                    success=True, command=command, stdout="ok", stderr="", returncode=0
                )

            run_command_mock.side_effect = side_effect
            evidence = json.dumps({"value_narrative": "test", "key_proof": "proof"})

            result = runner.invoke(
                main,
                [
                    "obpi",
                    "pipeline",
                    "OBPI-0.13.0-01-runtime-command-contract",
                    "--from=sync",
                    "--attestor",
                    "human:tester",
                    "--evidence-json",
                    evidence,
                ],
            )

            self.assertEqual(result.exit_code, 0)
            self.assertIn("Pipeline complete.", result.output)
            self.assertIn("WARN", result.output)

    @covers("REQ-0.0.9-02-01")
    def test_blocks_when_obpi_is_ledger_completed(self) -> None:
        """Pipeline blocks when ledger has completion proof, regardless of frontmatter."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            config = GzkitConfig.load(Path(".gzkit.json"))
            parent_adr = "ADR-0.13.0-obpi-pipeline-runtime-surface"
            obpi_id = "OBPI-0.13.0-01-runtime-command-contract"
            self._seed_parent_adr(config, parent_adr)
            self._seed_obpi(config, parent_adr, completed=True)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event(parent_adr, "PRD-GZKIT-1.0.0", "heavy"))
            ledger.append(obpi_created_event(obpi_id, parent_adr))
            ledger.append(
                obpi_receipt_emitted_event(
                    obpi_id,
                    receipt_event="completed",
                    attestor="test",
                    obpi_completion="completed",
                    parent_adr=parent_adr,
                )
            )

            result = runner.invoke(
                main,
                ["obpi", "pipeline", obpi_id],
            )

            self.assertEqual(result.exit_code, 1)
            self.assertIn("BLOCKERS:", result.output)
            self.assertIn("already completed", result.output)
