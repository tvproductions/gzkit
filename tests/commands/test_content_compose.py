"""gz content compose command tests — OBPI-0.0.37-21 (BEHAVIOR REQ proofs).

REQ-derived from the brief's Acceptance Criteria, not from implementation:
compose produces a candidate rendition + byte evidence, is fail-closed on
absent corpus / undeclared setpoint / invariant-floor violation, and NEVER
modifies rendered surfaces.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli.main import main
from gzkit.content.corpus_store import append_entry
from gzkit.content.models import CorpusEntry
from gzkit.traceability import covers
from tests.commands.common import CliRunner

_VENDOR_MANIFEST = {
    "content_type_routes": {"AgentContract": ["claude", "codex"]},
    "content_type_temperatures": {"AgentContract": {"codex": "lite", "claude": "heavy"}},
}

_INVARIANT_TEXT = "YOU OWN THE WORK COMPLETELY."
_COMPRESSIBLE_TEXT = "Prefer stdlib JSONL for append-only stores."


def _make_entry(
    entry_id: str, *, tier: str = "compressible", text: str = _COMPRESSIBLE_TEXT
) -> CorpusEntry:
    return CorpusEntry(
        id=entry_id,
        surface="AGENTS.md",
        section="behavior-rules",
        tier=tier,  # type: ignore
        classification="Ambiguous",
        text=text,
        origin="test",
        ts="2026-06-14T00:00:00Z",
    )


def _setup_project() -> None:
    """Seed the minimal project structure in the current isolated filesystem."""
    Path("data").mkdir()
    (Path("data") / "vendor-manifest.json").write_text(
        json.dumps(_VENDOR_MANIFEST), encoding="utf-8"
    )
    Path(".gzkit").mkdir()
    Path(".gzkit", "corpus").mkdir()
    root = Path(".")
    append_entry(root, "AGENTS.md", _make_entry("e-inv", tier="invariant", text=_INVARIANT_TEXT))
    append_entry(root, "AGENTS.md", _make_entry("e-compressible"))


class TestContentComposeCmd(unittest.TestCase):
    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.0.37-21-01")
    def test_compose_produces_candidate_and_byte_evidence(self) -> None:
        """Success path: candidate file written + byte evidence printed; exit 0."""
        with self._runner.isolated_filesystem():
            _setup_project()
            candidate_text = f"{_INVARIANT_TEXT}\nsome compressed content"
            Path("candidate.md").write_text(candidate_text, encoding="utf-8")

            args = [
                "content",
                "compose",
                "AGENTS.md",
                "--consumer",
                "codex",
                "--candidate",
                "candidate.md",
            ]
            result = self._runner.invoke(main, args)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            candidate_path = Path(".gzkit") / "renditions" / "AGENTS.md" / "codex.candidate.md"
            self.assertTrue(candidate_path.exists(), "Candidate file should be written")
            self.assertEqual(candidate_path.read_text(encoding="utf-8"), candidate_text)
            self.assertIn("Byte evidence", result.output)
            self.assertIn("setpoint=lite", result.output)

    @covers("REQ-0.0.37-21-04")
    def test_compose_exits_nonzero_on_absent_corpus(self) -> None:
        """Absent corpus → exit 1, no candidate written."""
        with self._runner.isolated_filesystem():
            Path("data").mkdir()
            (Path("data") / "vendor-manifest.json").write_text(
                json.dumps(_VENDOR_MANIFEST), encoding="utf-8"
            )
            Path(".gzkit").mkdir()
            Path("candidate.md").write_text("some text", encoding="utf-8")

            args = [
                "content",
                "compose",
                "AGENTS.md",
                "--consumer",
                "codex",
                "--candidate",
                "candidate.md",
            ]
            result = self._runner.invoke(main, args)

            self.assertNotEqual(result.exit_code, 0)
            candidate_path = Path(".gzkit") / "renditions" / "AGENTS.md" / "codex.candidate.md"
            self.assertFalse(candidate_path.exists(), "No candidate should be written on error")

    @covers("REQ-0.0.37-21-04")
    def test_compose_exits_nonzero_on_undeclared_setpoint(self) -> None:
        """Undeclared (surface, consumer) setpoint → exit 1, no candidate written."""
        with self._runner.isolated_filesystem():
            _setup_project()
            candidate_text = f"{_INVARIANT_TEXT}\nsome content"
            Path("candidate.md").write_text(candidate_text, encoding="utf-8")

            args = [
                "content",
                "compose",
                "AGENTS.md",
                "--consumer",
                "unknown-vendor",
                "--candidate",
                "candidate.md",
            ]
            result = self._runner.invoke(main, args)

            self.assertNotEqual(result.exit_code, 0)
            rend_dir = Path(".gzkit") / "renditions" / "AGENTS.md"
            self.assertFalse(
                (rend_dir / "unknown-vendor.candidate.md").exists(),
                "No candidate should be written on error",
            )

    @covers("REQ-0.0.37-21-03")
    @covers("REQ-0.0.37-21-04")
    def test_compose_refuses_invariant_floor_violation(self) -> None:
        """Candidate dropping an invariant-tier entry → exit 1, no candidate written."""
        with self._runner.isolated_filesystem():
            _setup_project()
            # Candidate text does NOT contain the invariant entry
            Path("candidate.md").write_text("some compressed content only", encoding="utf-8")

            args = [
                "content",
                "compose",
                "AGENTS.md",
                "--consumer",
                "codex",
                "--candidate",
                "candidate.md",
            ]
            result = self._runner.invoke(main, args)

            self.assertNotEqual(result.exit_code, 0)
            candidate_path = Path(".gzkit") / "renditions" / "AGENTS.md" / "codex.candidate.md"
            self.assertFalse(candidate_path.exists(), "No candidate on invariant violation")

    @covers("REQ-0.0.37-21-05")
    def test_compose_does_not_modify_rendered_surfaces(self) -> None:
        """After compose, AGENTS.md and CLAUDE.md are byte-unchanged."""
        with self._runner.isolated_filesystem():
            _setup_project()
            agents_text = "# AGENTS\nsome content"
            claude_text = "# CLAUDE\nsome content"
            Path("AGENTS.md").write_text(agents_text, encoding="utf-8")
            Path("CLAUDE.md").write_text(claude_text, encoding="utf-8")

            candidate_text = f"{_INVARIANT_TEXT}\nsome compressed content"
            Path("candidate.md").write_text(candidate_text, encoding="utf-8")

            args = [
                "content",
                "compose",
                "AGENTS.md",
                "--consumer",
                "codex",
                "--candidate",
                "candidate.md",
            ]
            result = self._runner.invoke(main, args)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(Path("AGENTS.md").read_text(encoding="utf-8"), agents_text)
            self.assertEqual(Path("CLAUDE.md").read_text(encoding="utf-8"), claude_text)
