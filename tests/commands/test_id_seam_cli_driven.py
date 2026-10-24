"""The CLI entry points RO-2 tranche 5 moved onto the identity seam, each driven end to end.

`gz arb red --commit 94edfb495` graded these readers `survived`: each command takes
an operator-typed id and normalizes it through `gzkit.core.models`, and no test in
that commit ran the command. Each test below types the bare form an operator types
(`0.1.0-f`, `0.1.0-01`) and asserts the command acted on the canonical id the
grammar names (`ADR-0.1.0-f`, `OBPI-0.1.0-01-thing`), so dropping the seam call
fails here.
"""

import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, adr_created_event
from tests.commands.common import CliResult, CliRunner, _quick_init

_ADR = "ADR-0.1.0-f"
_OBPI = "OBPI-0.1.0-01-thing"


class _SeededRepo(unittest.TestCase):
    """A fresh repo holding feature ADR-0.1.0-f, optionally with OBPI-0.1.0-01-thing."""

    with_obpi = False

    def setUp(self) -> None:
        self.runner = CliRunner()
        self._fs = self.runner.isolated_filesystem()
        self._fs.__enter__()
        self.addCleanup(self._fs.__exit__, None, None, None)
        _quick_init()
        created = self.gz("plan", "create", "f", "--kind", "feature")
        self.assertEqual(created.exit_code, 0, created.output)
        if self.with_obpi:
            spec = self.gz("specify", "thing", "--parent", "0.1.0-f", "--item", "1")
            self.assertEqual(spec.exit_code, 0, spec.output)

    def gz(self, *args: str) -> CliResult:
        return self.runner.invoke(main, list(args))


class TestAdrCommandsNormalizeABareSemver(_SeededRepo):
    def test_attest_reaches_the_gate_check_of_the_named_adr(self) -> None:
        result = self.gz("attest", "0.1.0-f", "--status", "completed")
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Gate 2 must pass", result.output)

    def test_audit_names_the_canonical_adr_in_its_recovery(self) -> None:
        result = self.gz("audit", "0.1.0-f", "--dry-run")
        self.assertIn(f"gz attest {_ADR} --status completed", result.output)

    def test_closeout_plans_the_canonical_adr(self) -> None:
        result = self.gz("closeout", "0.1.0-f", "--dry-run")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Gate 5 (Human)", result.output)

    def test_the_ceremony_resolves_the_canonical_adr(self) -> None:
        result = self.gz("closeout", "0.1.0-f", "--ceremony")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn(f"gz closeout {_ADR} --ceremony --next", result.output)

    def test_adr_status_reports_the_short_adr_id(self) -> None:
        result = self.gz("adr", "status", "0.1.0-f")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("ADR-0.1.0 ", result.output)

    def test_adr_evaluate_scores_the_canonical_adr(self) -> None:
        result = self.gz("adr", "evaluate", "0.1.0-f")
        self.assertIn(f"ADR structural completeness: {_ADR}", result.output)


class TestObpiCommandsNormalizeABareId(_SeededRepo):
    with_obpi = True

    def test_obpi_status_resolves_a_bare_short_id(self) -> None:
        result = self.gz("obpi", "status", "0.1.0-01")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn(f"Parent ADR: {_ADR}", result.output)

    def test_obpi_validate_finds_the_briefs_of_a_bare_adr(self) -> None:
        result = self.gz("obpi", "validate", "--adr", "0.1.0-f")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn(f"PASS {_OBPI}.md", result.output)

    def test_adr_demote_composes_the_pool_id(self) -> None:
        result = self.gz("adr", "demote", _ADR, "--ghi", "1", "--dry-run")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Target pool ID: ADR-pool.f", result.output)

    def test_task_start_and_fanout_read_the_req_through_the_seam(self) -> None:
        req = "REQ-0.1.0-01-01"
        started = self.gz("task", "start", "--req", req, "--seq", "next", "--json")
        self.assertEqual(started.exit_code, 0, started.output)
        self.assertIn("TASK-0.1.0-01-01-01", started.output)
        fanout = self.gz("task", "fanout", req, "--json")
        self.assertEqual(fanout.exit_code, 0, fanout.output)
        rows = json.loads(fanout.output[fanout.output.index("[") :])
        self.assertEqual([row["task_id"] for row in rows], ["TASK-0.1.0-01-01-01"])

    def test_register_adrs_scopes_a_bare_target_to_its_adr(self) -> None:
        # An unregistered brief under ADR-0.1.0-f; a bare target must still reach it.
        brief = next(Path("design").rglob(f"{_OBPI}.md"))
        brief.with_name("OBPI-0.1.0-02-other.md").write_text(
            brief.read_text(encoding="utf-8").replace(_OBPI, "OBPI-0.1.0-02-other"),
            encoding="utf-8",
        )
        targeted = self.gz("register-adrs", "0.1.0-f", "--dry-run")
        self.assertEqual(targeted.exit_code, 0, targeted.output)
        self.assertIn("OBPI-0.1.0-02-other", targeted.output)
        elsewhere = self.gz("register-adrs", "0.2.0-g", "--dry-run")
        self.assertNotIn("Would append obpi_created: OBPI-0.1.0-02-other", elsewhere.output)


class TestInterviewNormalizesTheParent(_SeededRepo):
    def test_an_obpi_interview_resolves_a_bare_parent(self) -> None:
        answers = {
            "id": "OBPI-0.9.9-01-x",
            "title": "T",
            "parent": "0.9.9-nope",
            "item": "1",
            "lane": "lite",
            "objective": "o",
            "allowed_paths": "src",
            "denied_paths": "none",
            "acceptance_criteria": "x",
        }
        Path("answers.json").write_text(json.dumps(answers), encoding="utf-8")
        result = self.gz("interview", "obpi", "--from", "answers.json")
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("ADR-0.9.9-nope", result.output)


class TestPromoteComposesTheFullId(unittest.TestCase):
    def test_a_promotion_names_its_target_by_semver_and_slug(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pool = Path(config.paths.adrs) / "pool" / "ADR-pool.sample-work.md"
            pool.parent.mkdir(parents=True, exist_ok=True)
            pool.write_text(
                "---\nid: ADR-pool.sample-work\nstatus: Pool\nparent: PRD-GZKIT-1.0.0\n"
                "lane: lite\n---\n\n# ADR-pool.sample-work: Sample Work\n\n## Status\n\nPool\n\n"
                "## Intent\n\nSample.\n\n## Target Scope\n\n- One thing\n\n"
                "## Non-Goals\n\n- None\n",
                encoding="utf-8",
            )
            Ledger(Path(".gzkit/ledger.jsonl")).append(
                adr_created_event("ADR-pool.sample-work", "", "lite")
            )
            args = ["adr", "promote", "ADR-pool.sample-work", "--semver", "0.6.0"]
            result = runner.invoke(main, [*args, "--kind", "feature", "--dry-run"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("ADR-pool.sample-work -> ADR-0.6.0-sample-work", result.output)


if __name__ == "__main__":
    unittest.main()
