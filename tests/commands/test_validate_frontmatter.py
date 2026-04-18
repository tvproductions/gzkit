"""Tests for ``gz validate --frontmatter`` guard (OBPI-0.0.16-01).

Each test asserts one REQ from the brief's acceptance criteria. Coverage
markers are recorded via the ``@covers`` decorator so ``gz covers`` can
derive the REQ → test graph.
"""

import json
import time
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, adr_created_event
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _quick_init


def _scaffold_adr(project_root: Path, adr_id: str, frontmatter: str) -> Path:
    """Create an ADR file with the given frontmatter content."""
    config = GzkitConfig.load(project_root / ".gzkit.json")
    adr_dir = project_root / config.paths.design_root / "adr" / "pre-release" / f"{adr_id}-test"
    adr_dir.mkdir(parents=True, exist_ok=True)
    path = adr_dir / f"{adr_id}-test.md"
    path.write_text(frontmatter, encoding="utf-8")
    return path


def _scaffold_obpi(project_root: Path, adr_id: str, obpi_id: str, frontmatter: str) -> Path:
    """Create an OBPI file with the given frontmatter content."""
    config = GzkitConfig.load(project_root / ".gzkit.json")
    adr_dir = project_root / config.paths.design_root / "adr" / "pre-release" / f"{adr_id}-test"
    obpi_dir = adr_dir / "obpis"
    obpi_dir.mkdir(parents=True, exist_ok=True)
    path = obpi_dir / f"{obpi_id}-test.md"
    path.write_text(frontmatter, encoding="utf-8")
    return path


def _scaffold_pool_adr(project_root: Path, adr_id: str, frontmatter: str) -> Path:
    """Create a pool ADR file under docs/design/adr/pool/.

    Pool ADRs live outside the active ADR tree and have no per-artifact
    lifecycle. The chore library's ``_is_pool_artifact`` skips them; the
    validator must agree (GHI #192).
    """
    config = GzkitConfig.load(project_root / ".gzkit.json")
    pool_dir = project_root / config.paths.design_root / "adr" / "pool"
    pool_dir.mkdir(parents=True, exist_ok=True)
    path = pool_dir / f"{adr_id}.md"
    path.write_text(frontmatter, encoding="utf-8")
    return path


class TestFrontmatterGuard(unittest.TestCase):
    """REQ-level acceptance tests for the frontmatter coherence guard."""

    @covers("REQ-0.0.16-01-01")
    def test_coherent_repo_exits_0_and_empty_body(self) -> None:
        """Clean repo → exit 0 and no drift prose in output body."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: lite\n---\n# ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter"])
            self.assertEqual(result.exit_code, 0)
            # REQ-01: empty body on coherent repo — no "drift" prose
            self.assertNotIn("drift", result.output.lower())

    @covers("REQ-0.0.16-01-02")
    def test_status_drift_exits_3_reports_drift_line(self) -> None:
        """ADR with drifted ``status:`` → exit 3 + drift line naming field and values."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            # Seed a frontmatter status that does not match what the ledger
            # derives. Ledger has only adr_created — lifecycle should be
            # "Pending". Frontmatter claims "Completed" which is drift.
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: lite\n"
                "status: Completed\n---\n# ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter"])
            self.assertEqual(result.exit_code, 3)
            self.assertIn("status", result.output.lower())

    @covers("REQ-0.0.16-01-02")
    def test_lane_drift_exits_3(self) -> None:
        """ADR with drifted ``lane:`` → exit 3 (policy breach)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter"])
            self.assertEqual(result.exit_code, 3)
            self.assertIn("lane", result.output)

    @covers("REQ-0.0.16-01-02")
    def test_parent_drift_exits_3(self) -> None:
        """ADR with drifted ``parent:`` → exit 3."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-WRONG-1.0.0\nlane: lite\n---\n# ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter"])
            self.assertEqual(result.exit_code, 3)
            self.assertIn("parent", result.output)

    @covers("REQ-0.0.16-01-03")
    def test_id_drift_resolves_via_path_not_fm_id(self) -> None:
        """Frontmatter ``id:`` is rewritten but filename is canonical — resolve via path.

        Seeds the ADR on disk with a drifted ``id:`` frontmatter value while
        the filename still encodes the real ledger ID. The resolver must
        key on the filesystem stem, never on the frontmatter ``id:``, and
        must report ``id`` drift (never silently trust the rewritten value).
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            # Filename encodes ADR-0.1.0; frontmatter claims ADR-9.9.9
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-9.9.9\nparent: PRD-TEST-1.0.0\nlane: lite\n---\n# ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter"])
            self.assertEqual(result.exit_code, 3)
            self.assertIn("id", result.output)
            # Ledger value for id should be the canonical path-keyed ID
            self.assertIn("ADR-0.1.0", result.output)
            self.assertIn("ADR-9.9.9", result.output)

    @covers("REQ-0.0.16-01-04")
    def test_ungoverned_key_does_not_trigger_drift(self) -> None:
        """Ungoverned frontmatter keys (tags:, related:) are ignored."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: lite\n"
                "tags: [anything, goes]\nrelated: ADR-0.0.1\n"
                "random_key: whatever\n---\n# ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter"])
            self.assertEqual(result.exit_code, 0)

    @covers("REQ-0.0.16-01-05")
    def test_json_output_emits_drift_array(self) -> None:
        """--json mode emits ``drift[]`` entries with required keys."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter", "--json"])
            payload = json.loads(result.output)
            self.assertIn("drift", payload)
            self.assertIsInstance(payload["drift"], list)
            self.assertGreaterEqual(len(payload["drift"]), 1)
            entry = payload["drift"][0]
            for key in ("path", "field", "ledger_value", "frontmatter_value"):
                self.assertIn(key, entry)

    @covers("REQ-0.0.16-01-06")
    def test_explain_emits_recovery_command_per_field(self) -> None:
        """--explain <ADR-ID> prints one recovery command per drifted field."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-WRONG-1.0.0\nlane: heavy\n---\n# ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter", "--explain", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 3)
            # Every drifted field gets at least one gz recovery command line;
            # we expect multiple "gz " command references in the output.
            self.assertGreaterEqual(result.output.count("gz "), 2)
            # Never suggests hand-editing
            self.assertNotIn("hand-edit", result.output.lower())
            self.assertNotIn("edit the frontmatter", result.output.lower())

    @covers("REQ-0.0.16-01-07")
    def test_adr_scope_restricts_output_to_one_artifact(self) -> None:
        """--adr <ID> scopes output to one artifact; other drift is not mentioned."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            ledger.append(adr_created_event("ADR-0.2.0", "PRD-TEST-1.0.0", "lite"))
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
            )
            _scaffold_adr(
                root,
                "ADR-0.2.0",
                "---\nid: ADR-0.2.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter", "--adr", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 3)
            self.assertIn("ADR-0.1.0", result.output)
            # Non-scoped ADR should NOT appear in output
            self.assertNotIn("ADR-0.2.0", result.output)

    @covers("REQ-0.0.16-01-08")
    def test_runtime_budget_under_one_second_on_real_repo(self) -> None:
        """Real repo runtime < 1.0s (~80 ADRs / ~200 OBPIs scale)."""
        from gzkit.commands.common import get_project_root  # noqa: PLC0415
        from gzkit.commands.validate_frontmatter import (
            validate_frontmatter_coherence,  # noqa: PLC0415
        )

        project_root = get_project_root()
        # Skip if this test runner is not inside the gzkit project
        if not (project_root / ".gzkit" / "ledger.jsonl").is_file():
            self.skipTest("No gzkit ledger present — not inside the gzkit repo")

        start = time.perf_counter()
        validate_frontmatter_coherence(project_root)
        elapsed = time.perf_counter() - start
        self.assertLess(
            elapsed,
            1.0,
            f"Frontmatter guard exceeded 1.0s budget (took {elapsed:.2f}s)",
        )


class TestPoolAdrSkipParity(unittest.TestCase):
    """GHI #192: validator must skip pool ADRs in parity with the chore library.

    The chore library ``frontmatter_coherence.py`` skips pool ADRs (and its
    line-300 source comment names this exact contract: "validator should not
    emit errors for pool ADRs"). Pool ADRs are an authoring backlog with no
    per-artifact ledger lifecycle, so frontmatter-vs-ledger comparison is
    structurally meaningless.
    """

    def test_pool_adr_with_drift_is_skipped_silently(self) -> None:
        """Pool ADR with drifted status MUST NOT appear in validator output.

        Pre-fix: validator emits an error for pool ADRs whose frontmatter
        status disagrees with the ledger's derived 'Pending'. Post-fix: pool
        ADRs are excluded from the iteration set.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            # Register a pool ADR in the ledger so it appears in the graph
            # with derived status 'Pending'. Frontmatter says 'Pool', which
            # before the fix would emit a drift error.
            ledger.append(adr_created_event("ADR-pool.test-feature", "PRD-TEST-1.0.0", "lite"))
            _scaffold_pool_adr(
                root,
                "ADR-pool.test-feature",
                "---\nid: ADR-pool.test-feature\nparent: PRD-TEST-1.0.0\n"
                "lane: lite\nstatus: Pool\n---\n# Pool ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertNotIn("ADR-pool.test-feature", result.output)
            self.assertNotIn("/adr/pool/", result.output)

    def test_active_adr_drift_still_reported_when_pool_present(self) -> None:
        """Pool-skip must NOT over-broaden — active ADR drift remains reported.

        Regression guard: the fix filters only pool/ paths and pool ids,
        leaving the active ADR tree fully validated.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            ledger.append(adr_created_event("ADR-pool.test-feature", "PRD-TEST-1.0.0", "lite"))
            # Active ADR with drifted status (lane disagreement)
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
            )
            # Pool ADR with drift — must not be reported (skipped)
            _scaffold_pool_adr(
                root,
                "ADR-pool.test-feature",
                "---\nid: ADR-pool.test-feature\nparent: PRD-TEST-1.0.0\n"
                "lane: lite\nstatus: Pool\n---\n# Pool ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter"])
            self.assertEqual(result.exit_code, 3, msg=result.output)
            # Active drift IS reported
            self.assertIn("ADR-0.1.0", result.output)
            self.assertIn("lane", result.output)
            # Pool drift IS NOT reported
            self.assertNotIn("ADR-pool.test-feature", result.output)

    def test_explain_on_pool_adr_emits_pool_aware_message(self) -> None:
        """`--explain ADR-pool.X` returns exit 0 with an informational pool note.

        Pre-fix: --explain prints "No frontmatter drift detected" which
        misleads operators (it's not "no drift", it's "out of scope").
        Post-fix: the renderer detects pool ids and prints an honest line.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-pool.test-feature", "PRD-TEST-1.0.0", "lite"))
            _scaffold_pool_adr(
                root,
                "ADR-pool.test-feature",
                "---\nid: ADR-pool.test-feature\nparent: PRD-TEST-1.0.0\n"
                "lane: lite\nstatus: Pool\n---\n# Pool ADR\n",
            )
            result = runner.invoke(
                main, ["validate", "--frontmatter", "--explain", "ADR-pool.test-feature"]
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("pool", result.output.lower())


class TestRecoveryCommandsResolveToCli(unittest.TestCase):
    """Mechanical guard for ``_RECOVERY_COMMANDS`` (GHI #189).

    Each recovery hint printed to operators on frontmatter drift must invoke
    a registered CLI subcommand. A typo in a hint silently shipped (singular
    ``gz chore run`` vs. plural ``gz chores run``) because nothing
    mechanically checked the dict's verbs against the parser. This test
    closes the class of failure.
    """

    def _verb_chain(self, hint: str) -> list[str]:
        """Walk hint tokens after ``gz`` until first placeholder / flag."""
        import shlex  # noqa: PLC0415

        tokens = shlex.split(hint)
        if not tokens or tokens[0] != "gz":
            self.fail(f"Recovery hint must start with 'gz': {hint!r}")
        chain: list[str] = []
        for tok in tokens[1:]:
            if tok.startswith(("<", "-")):
                break
            chain.append(tok)
        return chain

    def test_every_recovery_hint_resolves_to_a_registered_cli_verb(self) -> None:
        """Every ``_RECOVERY_COMMANDS`` value invokes a registered subcommand."""
        from gzkit.commands.validate_frontmatter import (
            _RECOVERY_COMMANDS,  # noqa: PLC0415
        )

        runner = CliRunner()
        for field, hint in _RECOVERY_COMMANDS.items():
            verbs = self._verb_chain(hint)
            with self.subTest(field=field, hint=hint):
                result = runner.invoke(main, [*verbs, "--help"])
                self.assertEqual(
                    result.exit_code,
                    0,
                    msg=(
                        f"Recovery hint for field '{field}' uses an unregistered "
                        f"verb chain {verbs!r}. Hint: {hint!r}\nOutput:\n{result.output}"
                    ),
                )


if __name__ == "__main__":
    unittest.main()
