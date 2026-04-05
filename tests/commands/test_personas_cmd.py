"""Tests for gz personas list and drift commands."""

import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _quick_init


def _seed_ledger_events() -> None:
    """Write synthetic governance events to the test ledger."""
    ledger = Path(".gzkit/ledger.jsonl")
    gate = {"schema": "gzkit.ledger.v1", "event": "gate_checked", "ts": "2026-01-01T00:00:00Z"}
    attest = {"schema": "gzkit.ledger.v1", "event": "attested", "ts": "2026-01-02T00:00:00Z"}
    adr = {"schema": "gzkit.ledger.v1", "event": "adr_created", "ts": "2025-12-01T00:00:00Z"}
    events = [json.dumps(gate), json.dumps(attest), json.dumps(adr)]
    with ledger.open("a", encoding="utf-8") as f:
        for line in events:
            f.write(line + "\n")


_VALID_PERSONA = """\
---
name: tester
traits:
  - methodical
  - thorough
anti-traits:
  - shallow-compliance
grounding: Evidence-first.
---

# Tester Persona
"""


class TestPersonasListCmd(unittest.TestCase):
    """Tests for ``gz personas list``."""

    def setUp(self) -> None:
        self.runner = CliRunner()

    @covers("REQ-0.0.11-02-02")
    def test_personas_list_no_dir(self) -> None:
        """With no custom personas, default-scaffolded personas are listed."""
        with self.runner.isolated_filesystem():
            _quick_init()
            result = self.runner.invoke(main, ["personas", "list"])
            self.assertEqual(result.exit_code, 0)
            # _quick_init scaffolds default personas, so they appear in listing
            self.assertIn("default-agent", result.output)

    @covers("REQ-0.0.11-02-02")
    def test_personas_list_empty_dir(self) -> None:
        """With empty personas dir (defaults removed), reports no files."""
        import shutil

        with self.runner.isolated_filesystem():
            _quick_init()
            pdir = Path(".gzkit/personas")
            shutil.rmtree(pdir)
            pdir.mkdir(parents=True)
            result = self.runner.invoke(main, ["personas", "list"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("No persona files", result.output)

    @covers("REQ-0.0.11-02-02")
    def test_personas_list_with_file(self) -> None:
        with self.runner.isolated_filesystem():
            _quick_init()
            pdir = Path(".gzkit/personas")
            (pdir / "tester.md").write_text(_VALID_PERSONA, encoding="utf-8")
            result = self.runner.invoke(main, ["personas", "list"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("tester", result.output)

    @covers("REQ-0.0.11-02-02")
    def test_personas_list_json_mode(self) -> None:
        with self.runner.isolated_filesystem():
            _quick_init()
            pdir = Path(".gzkit/personas")
            (pdir / "tester.md").write_text(_VALID_PERSONA, encoding="utf-8")
            result = self.runner.invoke(main, ["personas", "list", "--json"])
            self.assertEqual(result.exit_code, 0)
            data = json.loads(result.output)
            # Includes default-agent, default-reviewer, and tester
            names = [p["name"] for p in data]
            self.assertIn("tester", names)
            tester = next(p for p in data if p["name"] == "tester")
            self.assertEqual(tester["traits"], ["methodical", "thorough"])

    @covers("REQ-0.0.11-02-02")
    def test_personas_list_malformed_warns(self) -> None:
        with self.runner.isolated_filesystem():
            _quick_init()
            pdir = Path(".gzkit/personas")
            (pdir / "bad.md").write_text("no frontmatter here", encoding="utf-8")
            result = self.runner.invoke(main, ["personas", "list"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("WARNING", result.output)

    @covers("REQ-0.0.11-02-02")
    def test_personas_list_json_empty_dir(self) -> None:
        """With empty personas dir (defaults removed), JSON returns empty list."""
        import shutil

        with self.runner.isolated_filesystem():
            _quick_init()
            pdir = Path(".gzkit/personas")
            shutil.rmtree(pdir)
            pdir.mkdir(parents=True)
            result = self.runner.invoke(main, ["personas", "list", "--json"])
            self.assertEqual(result.exit_code, 0)
            data = json.loads(result.output)
            self.assertEqual(data, [])


class TestPersonasDriftCmd(unittest.TestCase):
    """Tests for ``gz personas drift``."""

    def setUp(self) -> None:
        self.runner = CliRunner()

    @covers("REQ-0.0.13-05-01")
    def test_drift_human_output(self) -> None:
        """Human table includes persona names."""
        with self.runner.isolated_filesystem():
            _quick_init()
            _seed_ledger_events()
            result = self.runner.invoke(main, ["personas", "drift"])
            # Default personas are scaffolded — output includes persona names
            self.assertIn("default-agent", result.output)

    @covers("REQ-0.0.13-05-02")
    def test_drift_json_output(self) -> None:
        """JSON output is valid and contains expected keys."""
        with self.runner.isolated_filesystem():
            _quick_init()
            _seed_ledger_events()
            result = self.runner.invoke(main, ["personas", "drift", "--json"])
            data = json.loads(result.output)
            self.assertIn("personas", data)
            self.assertIn("total_checks", data)
            self.assertIn("drift_count", data)
            self.assertIn("scan_timestamp", data)

    @covers("REQ-0.0.13-05-03")
    def test_drift_single_persona(self) -> None:
        """--persona filter limits to one persona."""
        with self.runner.isolated_filesystem():
            _quick_init()
            _seed_ledger_events()
            result = self.runner.invoke(
                main, ["personas", "drift", "--persona", "default-agent", "--json"]
            )
            data = json.loads(result.output)
            self.assertEqual(len(data["personas"]), 1)
            self.assertEqual(data["personas"][0]["persona"], "default-agent")

    @covers("REQ-0.0.13-05-04")
    def test_drift_exit_0_when_no_drift(self) -> None:
        """Exit 0 when only governance-aware traits and events exist."""
        with self.runner.isolated_filesystem():
            _quick_init()
            _seed_ledger_events()
            # default-agent has governance-aware which should pass with events
            result = self.runner.invoke(
                main, ["personas", "drift", "--persona", "default-agent", "--json"]
            )
            data = json.loads(result.output)
            # Only mapped trait is governance-aware (pass), rest are unmapped (no_evidence)
            self.assertEqual(data["drift_count"], 0)
            self.assertEqual(result.exit_code, 0)

    @covers("REQ-0.0.13-05-05")
    def test_drift_exit_3_on_policy_breach(self) -> None:
        """Exit 3 when drift is detected."""
        with self.runner.isolated_filesystem():
            _quick_init()
            # No ledger events -> governance-aware will fail
            pdir = Path(".gzkit/personas")
            pdir.mkdir(parents=True, exist_ok=True)
            (pdir / "strict.md").write_text(
                "---\nname: strict\ntraits:\n  - governance-aware\n"
                "anti-traits:\n  - scope-creep\ngrounding: Test.\n---\n",
                encoding="utf-8",
            )
            result = self.runner.invoke(
                main, ["personas", "drift", "--persona", "strict", "--json"]
            )
            data = json.loads(result.output)
            self.assertGreater(data["drift_count"], 0)
            self.assertEqual(result.exit_code, 3)

    @covers("REQ-0.0.13-05-06")
    def test_drift_help(self) -> None:
        """Help text includes description and examples."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["personas", "drift", "--help"])
            self.assertEqual(result.exit_code, 0)
            lower = result.output.lower()
            self.assertIn("behavioral proxies", lower)
            self.assertIn("--persona", result.output)
            self.assertIn("--json", result.output)
