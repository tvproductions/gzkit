"""Wire tests for the ADR closeout coverage gate in ``gz adr emit-receipt --event closed``.

OBPI-0.0.25-02 mirrors the REQ-coverage gate into ``adr_emit_receipt_cmd``:
``--event closed`` is refused when any OBPI under the closing ADR has unwaived
REQ gaps. Gaps that carry an ``obpi_completion_uncovered_accept`` ledger event
are considered waived and do not block closeout.

Coverage map:

| REQ              | Test class                                       |
|------------------|--------------------------------------------------|
| REQ-0.0.25-02-04 | TestAdrCloseoutFailsUnwaivedGap (fail path)      |
| REQ-0.0.25-02-04 | TestAdrCloseoutSucceedsAllGapsWaived (pass path) |
|                  | TestAdrCloseoutSucceedsAllCovered (no gaps)      |
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gzkit.commands.adr_audit import adr_emit_receipt_cmd
from gzkit.traceability import covers

_OBPI_BRIEF_TEMPLATE = """\
---
id: {obpi_id}
parent: {parent_adr}
item: 1
lane: heavy
status: Completed
---

# {obpi_id}: fixture

## Objective

Fixture brief for ADR closeout coverage gate tests.

## Acceptance Criteria

{criteria}

## Evidence

### Implementation Summary

- Files created/modified: src/gzkit/commands/adr_audit.py
- Tests added: tests/commands/test_adr_emit_receipt_coverage_gate.py
- Date completed: 2026-05-02

### Key Proof

Fixture brief.

## Human Attestation

- Attestor: g0
- Attestation: fixture
- Date: 2026-05-02
"""

_ADR_TEMPLATE = """\
---
id: {adr_id}
lane: heavy
kind: foundation
status: Active
---

# {adr_id}: fixture ADR
"""


def _make_waiver_event(obpi_id: str, req_id: str) -> str:
    """Render a minimal ``obpi_completion_uncovered_accept`` JSONL line."""
    return json.dumps(
        {
            "event": "obpi_completion_uncovered_accept",
            "id": obpi_id,
            "parent": obpi_id,
            "extra": {
                "obpi_id": obpi_id,
                "req_id": req_id,
                "operator": "g0",
                "rationale": "fixture waiver",
                "acceptance_type": "human",
            },
        }
    )


class _AdrCloseoutFixture(unittest.TestCase):
    """Mock rig for ``adr_emit_receipt_cmd --event closed`` tests.

    Builds a temporary ADR directory with OBPI brief stubs, optionally writes
    waiver events to a JSONL ledger file, and patches the relevant boundaries
    so ``_check_adr_obpi_coverage_gaps`` runs against the fixture data.
    """

    def _run_closed(
        self,
        *,
        adr_id: str,
        obpi_briefs: dict[str, list[str]],
        covers_layout: dict[str, dict[str, str | None]],
        waiver_events: list[str] | None = None,
        dry_run: bool = False,
    ) -> tuple[type[BaseException] | None, int | None]:
        """Drive ``adr_emit_receipt_cmd`` with ``receipt_event="closed"``.

        ``obpi_briefs`` maps ``obpi_id → [req_ids]`` — each OBPI gets a brief
        with those REQs in ``## Acceptance Criteria``.
        ``covers_layout`` maps ``obpi_id → {req_id → file_body | None}``
        (None = no covering test).
        ``waiver_events`` is a list of pre-rendered JSONL lines to seed the ledger.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            # Build ADR package directory tree
            adr_dir = root / "docs" / "design" / "adr" / "foundation" / adr_id
            obpi_dir = adr_dir / "obpis"
            obpi_dir.mkdir(parents=True, exist_ok=True)

            adr_file = adr_dir / f"{adr_id}.md"
            adr_file.write_text(_ADR_TEMPLATE.format(adr_id=adr_id), encoding="utf-8")

            for obpi_id, req_ids in obpi_briefs.items():
                criteria = "\n".join(f"- [ ] {r}: fixture req." for r in req_ids)
                brief_text = _OBPI_BRIEF_TEMPLATE.format(
                    obpi_id=obpi_id,
                    parent_adr=adr_id,
                    criteria=criteria,
                )
                (obpi_dir / f"{obpi_id}.md").write_text(brief_text, encoding="utf-8")

            # Build tests root per covers_layout
            tests_root = root / "tests"
            tests_root.mkdir(parents=True, exist_ok=True)
            for _obpi_id, layout in covers_layout.items():
                for req_id, body in layout.items():
                    if body is None:
                        continue
                    fname = f"test_cov_{req_id.replace('.', '_').replace('-', '_')}.py"
                    (tests_root / fname).write_text(body, encoding="utf-8")

            # Build ledger JSONL
            gzkit_dir = root / ".gzkit"
            gzkit_dir.mkdir(parents=True, exist_ok=True)
            ledger_path = gzkit_dir / "ledger.jsonl"
            if waiver_events:
                ledger_path.write_text("\n".join(waiver_events) + "\n", encoding="utf-8")
            else:
                ledger_path.write_text("", encoding="utf-8")

            mock_config = MagicMock()
            mock_config.paths.ledger = ".gzkit/ledger.jsonl"

            mock_ledger = MagicMock()
            mock_ledger.path = ledger_path
            mock_ledger.canonicalize_id.side_effect = lambda x: x

            patches = [
                patch(
                    "gzkit.commands.adr_audit.ensure_initialized",
                    return_value=mock_config,
                ),
                patch(
                    "gzkit.commands.adr_audit.get_project_root",
                    return_value=root,
                ),
                patch(
                    "gzkit.commands.adr_audit.Ledger",
                    return_value=mock_ledger,
                ),
                patch(
                    "gzkit.commands.adr_audit.resolve_adr_file",
                    return_value=(adr_file, adr_id),
                ),
                patch(
                    "gzkit.commands.adr_audit.resolve_adr_ledger_id",
                    return_value=adr_id,
                ),
                patch("gzkit.commands.adr_audit._reject_pool_adr_for_lifecycle"),
            ]
            for p in patches:
                p.start()
            try:
                exc_type: type[BaseException] | None = None
                code: int | None = None
                try:
                    adr_emit_receipt_cmd(
                        adr=adr_id,
                        receipt_event="closed",
                        attestor="g0",
                        evidence_json=None,
                        dry_run=dry_run,
                    )
                except SystemExit as exc:
                    exc_type = SystemExit
                    code = int(exc.code) if isinstance(exc.code, int) else 1
            finally:
                for p in patches:
                    p.stop()

        return exc_type, code


def _covering_body(req_id: str) -> str:
    return (
        "import unittest\n\n"
        "def covers(req_id):\n"
        "    def deco(fn):\n"
        "        return fn\n"
        "    return deco\n\n"
        "class FixtureTests(unittest.TestCase):\n"
        f'    @covers("{req_id}")\n'
        "    def test_x(self):\n"
        "        pass\n"
    )


# ---------------------------------------------------------------------------
# Background: all OBPIs have full coverage → no error
# ---------------------------------------------------------------------------


class TestAdrCloseoutSucceedsAllCovered(_AdrCloseoutFixture):
    """All OBPIs have covering tests — ``--event closed`` emits the receipt."""

    def test_all_covered_no_exit(self) -> None:
        exc, code = self._run_closed(
            adr_id="ADR-9.9.9-fixture",
            obpi_briefs={
                "OBPI-9.9.9-99-fixture": ["REQ-9.9.9-99-01", "REQ-9.9.9-99-02"],
            },
            covers_layout={
                "OBPI-9.9.9-99-fixture": {
                    "REQ-9.9.9-99-01": _covering_body("REQ-9.9.9-99-01"),
                    "REQ-9.9.9-99-02": _covering_body("REQ-9.9.9-99-02"),
                },
            },
            waiver_events=None,
        )
        self.assertIsNone(exc)
        self.assertIsNone(code)


# ---------------------------------------------------------------------------
# REQ-0.0.25-02-04 — one OBPI has unwaived REQ gap → exit 3
# ---------------------------------------------------------------------------


class TestAdrCloseoutFailsUnwaivedGap(_AdrCloseoutFixture):
    """REQ-0.0.25-02-04 — unwaived REQ gap blocks ADR closeout."""

    @covers("REQ-0.0.25-02-04")
    def test_unwaived_gap_exits_3(self) -> None:
        exc, code = self._run_closed(
            adr_id="ADR-9.9.9-fixture",
            obpi_briefs={
                "OBPI-9.9.9-99-fixture": ["REQ-9.9.9-99-01"],
            },
            covers_layout={
                "OBPI-9.9.9-99-fixture": {"REQ-9.9.9-99-01": None},
            },
            waiver_events=None,
        )
        self.assertIs(exc, SystemExit)
        self.assertEqual(code, 3)


# ---------------------------------------------------------------------------
# REQ-0.0.25-02-04 (pass path) — gaps exist but all waived → no error
# ---------------------------------------------------------------------------


class TestAdrCloseoutSucceedsAllGapsWaived(_AdrCloseoutFixture):
    """REQ-0.0.25-02-04 (pass path) — all REQ gaps carry waiver events → no error."""

    @covers("REQ-0.0.25-02-04")
    def test_all_gaps_waived_no_exit(self) -> None:
        waiver = _make_waiver_event("OBPI-9.9.9-99-fixture", "REQ-9.9.9-99-01")
        exc, code = self._run_closed(
            adr_id="ADR-9.9.9-fixture",
            obpi_briefs={
                "OBPI-9.9.9-99-fixture": ["REQ-9.9.9-99-01"],
            },
            covers_layout={
                "OBPI-9.9.9-99-fixture": {"REQ-9.9.9-99-01": None},
            },
            waiver_events=[waiver],
        )
        self.assertIsNone(exc)
        self.assertIsNone(code)


if __name__ == "__main__":
    unittest.main()
