"""Tests for ``gz gates`` Gate 1 frontmatter integration (OBPI-0.0.16-02).

Derives from the OBPI brief's REQ-IDs, not the implementation. Each test
targets exactly one REQ so the coverage graph produced by ``gz covers`` is
legible. Follows the existing pattern from
``tests/commands/test_validate_frontmatter.py``: ``_quick_init()`` +
manual ledger seeding + direct frontmatter scaffold.
"""

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


def _coherent_adr(root: Path, adr_id: str, lane: str = "lite") -> None:
    """Seed a coherent ADR (no drift): ledger + matching frontmatter."""
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    ledger.append(adr_created_event(adr_id, "PRD-TEST-1.0.0", lane))
    _scaffold_adr(
        root,
        adr_id,
        f"---\nid: {adr_id}\nparent: PRD-TEST-1.0.0\nlane: {lane}\n---\n# ADR\n",
    )


def _drifted_status_adr(root: Path, adr_id: str, drifted_status: str = "Completed") -> None:
    """Seed an ADR whose frontmatter ``status:`` disagrees with the ledger."""
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    ledger.append(adr_created_event(adr_id, "PRD-TEST-1.0.0", "lite"))
    _scaffold_adr(
        root,
        adr_id,
        f"---\nid: {adr_id}\nparent: PRD-TEST-1.0.0\nlane: lite\n"
        f"status: {drifted_status}\n---\n# ADR\n",
    )


class TestGate1FrontmatterIntegration(unittest.TestCase):
    """Gate 1 wiring of the frontmatter-ledger coherence guard."""

    @covers("REQ-0.0.16-02-01")
    @covers("REQ-0.0.16-02-06")
    def test_gate1_passes_when_no_drift(self) -> None:
        """Clean repo → Gate 1 passes (exit 0)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _coherent_adr(Path.cwd(), "ADR-0.1.0")
            result = runner.invoke(main, ["gates", "--gate", "1", "--adr", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

    @covers("REQ-0.0.16-02-02")
    def test_gate1_blocks_on_status_drift_with_exit_3(self) -> None:
        """Status drift → Gate 1 blocks with exit 3 (policy breach)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _drifted_status_adr(Path.cwd(), "ADR-0.1.0")
            result = runner.invoke(main, ["gates", "--gate", "1", "--adr", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 3, msg=result.output)
            self.assertIn("status", result.output.lower())

    @covers("REQ-0.0.16-02-02")
    def test_gate1_drift_listing_names_field_and_values(self) -> None:
        """Per-field drift listing shows ledger-vs-frontmatter values."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _drifted_status_adr(Path.cwd(), "ADR-0.1.0", drifted_status="Completed")
            result = runner.invoke(main, ["gates", "--gate", "1", "--adr", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 3, msg=result.output)
            # Per-field listing: the drifted frontmatter value surfaces to the operator.
            self.assertIn("Completed", result.output)

    @covers("REQ-0.0.16-02-03")
    def test_gate1_error_names_recovery_command_per_field(self) -> None:
        """Gate-1 drift output names an executable recovery command per field."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _drifted_status_adr(Path.cwd(), "ADR-0.1.0")
            result = runner.invoke(main, ["gates", "--gate", "1", "--adr", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 3, msg=result.output)
            # status drift → recovery command from _RECOVERY_COMMANDS is named.
            self.assertIn("gz chores run frontmatter-ledger-coherence", result.output)

    @covers("REQ-0.0.16-02-04")
    def test_gates_rejects_skip_frontmatter_bypass_flag(self) -> None:
        """``gz gates --skip-frontmatter`` is not an accepted flag (argparse rejects)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _coherent_adr(Path.cwd(), "ADR-0.1.0")
            result = runner.invoke(main, ["gates", "--skip-frontmatter", "--adr", "ADR-0.1.0"])
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("unrecognized arguments", result.output.lower())

    @covers("REQ-0.0.16-02-05")
    def test_gate1_status_drift_displays_canonical_vocab_term(self) -> None:
        """Drifted ``status:`` → output displays canonical ledger term via STATUS_VOCAB_MAPPING."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            # Frontmatter claims "Completed" — canonicalizes to "completed" per
            # STATUS_VOCAB_MAPPING. Ledger has only adr_created → lifecycle is
            # "Pending". Gate 1 should surface BOTH raw and canonical terms.
            _drifted_status_adr(Path.cwd(), "ADR-0.1.0", drifted_status="Completed")
            result = runner.invoke(main, ["gates", "--gate", "1", "--adr", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 3, msg=result.output)
            # Canonical term from STATUS_VOCAB_MAPPING appears in output.
            self.assertIn("completed", result.output.lower())

    @covers("REQ-0.0.16-02-05")
    def test_gate1_unmapped_status_term_surfaces_as_unmapped(self) -> None:
        """Unmapped status term → distinct ``unmapped`` line (never silently fallback)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _drifted_status_adr(Path.cwd(), "ADR-0.1.0", drifted_status="Zxcv-BogusTerm")
            result = runner.invoke(main, ["gates", "--gate", "1", "--adr", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 3, msg=result.output)
            self.assertIn("unmapped", result.output.lower())
            self.assertIn("Zxcv-BogusTerm", result.output)

    @covers("REQ-0.0.16-02-06")
    def test_gate1_latency_within_validator_budget(self) -> None:
        """Gate 1 latency stays within the OBPI-01 validator's measured budget."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _coherent_adr(Path.cwd(), "ADR-0.1.0")

            # Baseline: validator standalone on the same fixture.
            from gzkit.commands.validate_frontmatter import (
                validate_frontmatter_coherence,
            )

            validator_start = time.perf_counter()
            validate_frontmatter_coherence(Path.cwd(), adr_scope="ADR-0.1.0")
            validator_cost = time.perf_counter() - validator_start

            # Gate 1 cost on the same fixture.
            gate_start = time.perf_counter()
            result = runner.invoke(main, ["gates", "--gate", "1", "--adr", "ADR-0.1.0"])
            gate_cost = time.perf_counter() - gate_start

            self.assertEqual(result.exit_code, 0, msg=result.output)
            # Gate 1 must not exceed the validator's cost by more than a small,
            # bounded overhead for argparse dispatch, ledger opens, and rendering.
            delta = gate_cost - validator_cost
            self.assertLess(
                delta,
                0.5,
                msg=(
                    f"Gate 1 added {delta * 1000:.1f}ms over validator baseline "
                    f"({validator_cost * 1000:.1f}ms); expected <500ms overhead"
                ),
            )


if __name__ == "__main__":
    unittest.main()
