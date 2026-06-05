"""gz content remember command tests — OBPI-0.0.37-19 (BEHAVIOR REQ proofs).

REQ-derived from the brief's Acceptance Criteria, not from the implementation:
capture appends one addressed entry to the per-surface corpus store, emits a
corpus_entry_appended ledger event, NEVER edits a rendered surface, and fails
closed on an unknown surface or an unaddressable section.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli.main import main
from gzkit.content.models import Corpus
from gzkit.traceability import covers
from tests.commands.common import CliRunner

_SURFACE = """# Test Agent Contract

Purpose line.

## Behavior Rules

- Do the thing.

## Prime Directive

- Own it.
"""


def _seed_surface(name: str = "AGENTS.md") -> Path:
    """Write a minimal parseable AgentContract surface into the cwd; return its path."""
    path = Path(name)
    path.write_text(_SURFACE, encoding="utf-8")
    return path


def _ledger_events() -> list[dict]:
    """Return the parsed ledger events from the cwd project, or [] when none."""
    ledger_path = Path(".gzkit") / "ledger.jsonl"
    if not ledger_path.exists():
        return []
    return [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class TestContentRemember(unittest.TestCase):
    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.0.37-19-01")
    def test_appends_one_entry_with_all_addressed_fields(self) -> None:
        """A known surface + resolvable section appends one fully-populated entry; exit 0."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            result = self._runner.invoke(
                main,
                [
                    "content",
                    "remember",
                    "AGENTS.md",
                    "--section",
                    "Behavior Rules",
                    "--text",
                    "Prefer stdlib JSONL for append-only stores.",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            corpus = Corpus.loads(
                (Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").read_text(encoding="utf-8")
            )
            self.assertEqual(len(corpus.entries), 1)
            entry = corpus.entries[0]
            self.assertEqual(entry.surface, "AGENTS.md")
            self.assertEqual(entry.section, "behavior-rules")
            self.assertEqual(entry.tier, "compressible")
            self.assertEqual(entry.classification, "Ambiguous")
            self.assertTrue(entry.id)
            self.assertTrue(entry.ts)
            self.assertEqual(entry.text, "Prefer stdlib JSONL for append-only stores.")

    @covers("REQ-0.0.37-19-02")
    def test_does_not_modify_the_rendered_surface(self) -> None:
        """Capturing against AGENTS.md leaves it byte-unchanged — only the corpus store changes."""
        with self._runner.isolated_filesystem():
            surface = _seed_surface()
            before = surface.read_bytes()
            result = self._runner.invoke(
                main,
                [
                    "content",
                    "remember",
                    "AGENTS.md",
                    "--section",
                    "Prime Directive",
                    "--text",
                    "Own the work.",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(surface.read_bytes(), before)
            self.assertTrue((Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").exists())

    @covers("REQ-0.0.37-19-03")
    def test_emits_corpus_entry_appended_ledger_event(self) -> None:
        """A successful append emits corpus_entry_appended with surface/section/entry_id/tier."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            result = self._runner.invoke(
                main,
                [
                    "content",
                    "remember",
                    "AGENTS.md",
                    "--section",
                    "behavior-rules",
                    "--text",
                    "x",
                    "--tier",
                    "invariant",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            events = [e for e in _ledger_events() if e.get("event") == "corpus_entry_appended"]
            self.assertEqual(len(events), 1, msg=_ledger_events())
            event = events[0]
            self.assertEqual(event["surface"], "AGENTS.md")
            self.assertEqual(event["section"], "behavior-rules")
            self.assertEqual(event["tier"], "invariant")
            self.assertTrue(event["entry_id"])

    @covers("REQ-0.0.37-19-04")
    def test_fails_closed_on_unknown_surface(self) -> None:
        """An unknown surface (no file) aborts non-zero and writes no corpus entry."""
        with self._runner.isolated_filesystem():
            result = self._runner.invoke(
                main,
                ["content", "remember", "NOPE.md", "--section", "behavior-rules", "--text", "x"],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertFalse((Path(".gzkit") / "corpus" / "NOPE.md.jsonl").exists())

    @covers("REQ-0.0.37-19-04")
    def test_fails_closed_on_unaddressable_section(self) -> None:
        """A section that resolves to no Pillar aborts non-zero and writes no corpus entry."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            result = self._runner.invoke(
                main,
                ["content", "remember", "AGENTS.md", "--section", "no-such-section", "--text", "x"],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertFalse((Path(".gzkit") / "corpus" / "AGENTS.md.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
