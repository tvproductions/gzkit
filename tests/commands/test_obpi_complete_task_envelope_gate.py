"""Tests for the task-envelope Signature-(b) chokepoint gate in ``gz obpi complete`` (GHI #590).

`gz obpi complete` must refuse to close an OBPI that would land
``seq=01``-only-without-``req_atomic`` residue — the generator of the recurring
``task-envelope-coherence`` ``gz check`` reopenings. The gate is the chokepoint
enforcement of ``gz validate --task-envelope-coherence`` Signature (b): wiring it
into the state-mutating completion command (not only the bypassable
``gz obpi precomplete`` pre-flight) means the residue can never reach ``main`` on
any agent's path.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import yaml

from gzkit.commands.obpi_complete import _enforce_task_envelope_gate

_OBPI_ID = "OBPI-0.0.64-04"
_BASE_FM = {
    "id": _OBPI_ID,
    "parent": "ADR-0.0.64-task-envelope-and-planning-decomposition",
    "lane": "Heavy",
    "status": "Draft",
    "allowlist": ["src/gzkit/commands/validate_cmd.py"],
    "reqs": ["REQ-0.0.64-04-01"],
    "verification": ["uv run gz lint"],
}


def _seed(root: Path, frontmatter: dict) -> Path:
    """Write a minimal brief + a single seq=01 ledger task_started for the OBPI."""
    gzkit_dir = root / ".gzkit"
    gzkit_dir.mkdir(parents=True, exist_ok=True)
    (gzkit_dir / "ledger.jsonl").write_text(
        json.dumps(
            {
                "event": "task_started",
                "task_id": "TASK-0.0.64-04-01-01",
                "obpi_id": _OBPI_ID,
                "id": "evt-1",
                "schema_": "1.0",
                "timestamp": "2026-05-30T15:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.64-fixture" / "obpis"
    brief_dir.mkdir(parents=True, exist_ok=True)
    brief_path = brief_dir / f"{_OBPI_ID}-fixture.md"
    body = "\n# Fixture\n\n## Acceptance Criteria\n\n- [ ] REQ-0.0.64-04-01\n"
    brief_path.write_text(
        f"---\n{yaml.dump(_no_none(frontmatter), default_flow_style=False)}---\n{body}",
        encoding="utf-8",
    )
    return brief_path


def _no_none(fm: dict) -> dict:
    return {k: v for k, v in fm.items() if v is not None}


class TestTaskEnvelopeChokepointGate(unittest.TestCase):
    """`_enforce_task_envelope_gate` fail-closes on Sig(b) residue, passes when exempt."""

    def test_gate_blocks_seq01_only_without_req_atomic(self) -> None:
        """seq=01-only across all REQs + no req_atomic → SystemExit(3) (policy breach)."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brief_path = _seed(root, _BASE_FM)
            with self.assertRaises(SystemExit) as ctx:
                _enforce_task_envelope_gate(
                    obpi_file=brief_path,
                    project_root=root,
                    as_json=False,
                    obpi_id=_OBPI_ID,
                )
            self.assertEqual(ctx.exception.code, 3)

    def test_gate_passes_when_req_atomic_covers_all_reqs(self) -> None:
        """req_atomic covering all REQs → no raise (completion may proceed)."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brief_path = _seed(root, {**_BASE_FM, "req_atomic": ["REQ-0.0.64-04-01"]})
            # Must not raise.
            _enforce_task_envelope_gate(
                obpi_file=brief_path,
                project_root=root,
                as_json=False,
                obpi_id=_OBPI_ID,
            )


if __name__ == "__main__":
    unittest.main()
