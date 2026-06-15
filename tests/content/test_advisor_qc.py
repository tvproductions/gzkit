"""Engine-level tests for the deterministic advisor-QC verdict recorder.

Covers (OBPI-0.0.37-24):
  REQ-0.0.37-24-01 — any score → receipt written, tool stays advisory (no raise)
  REQ-0.0.37-24-02 — empty/absent explanation → fail closed, NO receipt written
  REQ-0.0.37-24-03 — identical input → byte-identical receipt; no in-code LLM/network

The engine is the deterministic record half of the advisor-QC loop: the
judgment (the LLM-as-judge read of info-retained-per-byte) is the wielding
skill's; the engine only validates receipt shape (explanation-before-verdict),
assembles the ARB receipt payload, and writes it. It never blocks on the
verdict value — only a structurally malformed (explanation-less) receipt fails
closed (ADR-0.0.39 Evidentiary invariant).
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.content import advisor_qc
from gzkit.traceability import covers

_RUN_ID = "arb-step-judge-0123456789abcdef0123456789abcdef"
_TS = "2026-06-15T00:00:00Z"


class TestRecordVerdictAdvisory(unittest.TestCase):
    """The engine records any score and stays advisory (REQ-01)."""

    @covers("REQ-0.0.37-24-01")
    def test_records_receipt_for_any_score_without_raising(self) -> None:
        """A low retention score is evidence, not a gate — the engine never raises on value."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for score in (0.0, 0.12, 0.94, 1.0):
                path = advisor_qc.record_verdict(
                    root=root,
                    surface="AGENTS.md",
                    consumer="codex",
                    explanation="All Mechanical bullets retained; two Promotable bullets combined.",
                    score=score,
                    run_id=f"arb-step-judge-{'a' * 31}{int(score * 9)}",
                    timestamp=_TS,
                )
                self.assertTrue(path.is_file(), f"no receipt written for score={score}")
                receipt = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(receipt["exit_status"], 0)
                self.assertEqual(receipt["verdict"]["score"], score)

    @covers("REQ-0.0.37-24-01")
    def test_receipt_run_id_matches_attestation_regex(self) -> None:
        """The run_id must bind against arb-(?:ruff|step-[a-z][a-z0-9]*)-[a-f0-9]{32}."""
        import re

        pattern = re.compile(r"^arb-(?:ruff|step-[a-z][a-z0-9]*)-[a-f0-9]{32}$")
        with tempfile.TemporaryDirectory() as tmp:
            path = advisor_qc.record_verdict(
                root=Path(tmp),
                surface="AGENTS.md",
                consumer="codex",
                explanation="retained the invariant tier verbatim",
                score=0.9,
            )
            run_id = path.stem
            self.assertRegex(run_id, pattern)


class TestRecordVerdictFailClosed(unittest.TestCase):
    """Malformed receipt shape (empty explanation) fails closed (REQ-02)."""

    @covers("REQ-0.0.37-24-02")
    def test_empty_explanation_raises_and_writes_no_receipt(self) -> None:
        """Empty explanation → ValueError, and the receipts dir gains no file."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                advisor_qc.record_verdict(
                    root=root,
                    surface="AGENTS.md",
                    consumer="codex",
                    explanation="   ",
                    score=0.5,
                    run_id=_RUN_ID,
                    timestamp=_TS,
                )
            # No receipt for this run_id was written — fail-closed-before-write.
            self.assertFalse((root / "artifacts" / "receipts" / f"{_RUN_ID}.json").exists())

    @covers("REQ-0.0.37-24-02")
    def test_explanation_precedes_verdict_in_serialized_receipt(self) -> None:
        """ADR-0.0.39 explanation-before-verdict: explanation key precedes the verdict block."""
        with tempfile.TemporaryDirectory() as tmp:
            path = advisor_qc.record_verdict(
                root=Path(tmp),
                surface="AGENTS.md",
                consumer="codex",
                explanation="reasoning stated before the conclusion",
                score=0.8,
                run_id=_RUN_ID,
                timestamp=_TS,
            )
            raw = path.read_text(encoding="utf-8")
            self.assertLess(
                raw.index('"explanation"'),
                raw.index('"verdict"'),
                "explanation must be serialized before the verdict (anti-anchoring doctrine)",
            )


class TestRecordVerdictDeterministic(unittest.TestCase):
    """Identical input → byte-identical receipt; no LLM/network (REQ-03)."""

    @covers("REQ-0.0.37-24-03")
    def test_identical_input_yields_byte_identical_receipt(self) -> None:
        """Given a pinned run_id + timestamp, two records produce the same bytes."""
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            kwargs = {
                "surface": "AGENTS.md",
                "consumer": "codex",
                "explanation": "deterministic body under pinned seams",
                "score": 0.77,
                "run_id": _RUN_ID,
                "timestamp": _TS,
            }
            p1 = advisor_qc.record_verdict(root=Path(tmp1), **kwargs)
            p2 = advisor_qc.record_verdict(root=Path(tmp2), **kwargs)
            self.assertEqual(
                p1.read_bytes(),
                p2.read_bytes(),
                "identical inputs must yield byte-identical receipts (deterministic, no LLM)",
            )

    @covers("REQ-0.0.37-24-03")
    def test_engine_module_makes_no_network_or_llm_call(self) -> None:
        """The engine source imports no network/LLM client (judgment is the skill's)."""
        import ast

        source = Path(advisor_qc.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        forbidden = {"urllib", "http", "requests", "httpx", "socket", "anthropic", "openai"}
        self.assertEqual(
            imported & forbidden,
            set(),
            f"engine must make no network/LLM call; found {imported & forbidden}",
        )


if __name__ == "__main__":
    unittest.main()
