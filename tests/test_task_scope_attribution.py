"""Worklog events carry the TASK in their own scope (GHI #950).

Four of the task-envelope roster's worklog types -- ``attested``,
``gate_checked``, ``audit_receipt_emitted`` and
``obpi_completion_uncovered_accept`` -- had constructors with no ``task_id``
parameter, so the roster's membership criterion ("carries an optional task_id")
was false for them and a row emitted under an active TASK could never be
repaired. Operator rulings 2026-09-28, verbatim: "Wire task_id through
(Recommended)" and "Infer in scope; unset if ambiguous (Recommended)".
"""

from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path

from gzkit.ledger import (
    attested_event,
    audit_receipt_emitted_event,
    gate_checked_event,
    obpi_completion_uncovered_accept_event,
)
from gzkit.ledger_events import composition_rendered_event, intrinsic_complexity_attestation_event
from gzkit.tasks import in_scope_task_id

_SRC = Path(__file__).resolve().parents[1] / "src" / "gzkit"
_CONSTRUCTORS = {
    "attested_event",
    "gate_checked_event",
    "audit_receipt_emitted_event",
    "obpi_completion_uncovered_accept_event",
}


def _ledger(tmp: str, rows: list[tuple[str, str]]) -> Path:
    path = Path(tmp) / "ledger.jsonl"
    path.write_text(
        "".join(json.dumps({"event": ev, "task_id": tid}) + "\n" for ev, tid in rows),
        encoding="utf-8",
    )
    return path


class TestInScopeTaskId(unittest.TestCase):
    """Exactly one in-progress TASK in the event's scope, or None."""

    def _resolve(self, rows: list[tuple[str, str]], scope: str | None) -> str | None:
        with tempfile.TemporaryDirectory() as tmp:
            return in_scope_task_id(_ledger(tmp, rows), scope)

    def test_single_task_in_obpi_scope(self) -> None:
        rows = [("task_started", "TASK-0.35.0-08-01-01")]
        self.assertEqual(
            self._resolve(rows, "OBPI-0.35.0-08-remember-post-append-advisory"),
            "TASK-0.35.0-08-01-01",
        )

    def test_single_task_in_adr_scope(self) -> None:
        rows = [("task_started", "TASK-0.35.0-08-01-01")]
        self.assertEqual(
            self._resolve(rows, "ADR-0.35.0-canon-entry-corpus-landing"), "TASK-0.35.0-08-01-01"
        )

    def test_unrelated_task_is_never_attributed(self) -> None:
        rows = [("task_started", "TASK-0.37.0-04-01-01")]
        self.assertIsNone(self._resolve(rows, "ADR-0.35.0-canon-entry-corpus-landing"))
        self.assertIsNone(self._resolve(rows, "OBPI-0.37.0-05-other"))

    def test_two_in_scope_tasks_are_ambiguous(self) -> None:
        rows = [
            ("task_started", "TASK-0.35.0-08-01-01"),
            ("task_started", "TASK-0.35.0-09-01-01"),
        ]
        self.assertIsNone(self._resolve(rows, "ADR-0.35.0-canon-entry-corpus-landing"))
        self.assertEqual(self._resolve(rows, "OBPI-0.35.0-09-x"), "TASK-0.35.0-09-01-01")

    def test_closed_task_is_not_active(self) -> None:
        rows = [
            ("task_started", "TASK-0.35.0-08-01-01"),
            ("task_completed", "TASK-0.35.0-08-01-01"),
        ]
        self.assertIsNone(self._resolve(rows, "OBPI-0.35.0-08-x"))

    def test_slug_task_has_no_artifact_scope(self) -> None:
        rows = [("task_started", "TASK-tidy-verdict-#1124")]
        self.assertIsNone(self._resolve(rows, "ADR-0.35.0-x"))

    def test_missing_scope_resolves_none(self) -> None:
        rows = [("task_started", "TASK-0.35.0-08-01-01")]
        self.assertIsNone(self._resolve(rows, None))

    def test_absent_ledger_resolves_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(in_scope_task_id(Path(tmp) / "missing.jsonl", "ADR-0.35.0-x"))


class TestConstructorsCarryTaskId(unittest.TestCase):
    """Each constructor writes task_id when given and omits it when not."""

    def _pairs(self, task_id: str | None) -> list:
        return [
            attested_event("ADR-0.1.0", "completed", "g0", task_id=task_id),
            gate_checked_event("ADR-0.1.0", 2, "pass", "gz test", 0, task_id=task_id),
            audit_receipt_emitted_event("ADR-0.1.0", "completed", "g0", task_id=task_id),
            obpi_completion_uncovered_accept_event(
                obpi_id="OBPI-0.1.0-01",
                req_id="REQ-0.1.0-01-01",
                operator="g0",
                rationale="r",
                acceptance_type="t",
                task_id=task_id,
            ),
            # Unscoped roster members: the channel exists, producers leave it unset.
            composition_rendered_event(3, "AGENTS.md", 10, task_id=task_id),
            intrinsic_complexity_attestation_event(
                file_path="src/x.py",
                qualname="f",
                reason="r",
                attestor="g0",
                attestation_date="2026-09-28",
                metric="radon_cc",
                crossing_band="warn",
                crossing_value=11.0,
                task_id=task_id,
            ),
        ]

    def test_task_id_is_recorded(self) -> None:
        for event in self._pairs("TASK-0.1.0-01-01-01"):
            with self.subTest(event=event.event):
                self.assertEqual(event.extra.get("task_id"), "TASK-0.1.0-01-01-01")

    def test_task_id_is_omitted_when_unset(self) -> None:
        for event in self._pairs(None):
            with self.subTest(event=event.event):
                self.assertNotIn("task_id", event.extra)


class TestEveryProducerPassesTaskId(unittest.TestCase):
    """No call site of the four constructors may drop the channel."""

    def test_every_call_site_passes_task_id(self) -> None:
        missing: list[str] = []
        for path in sorted(_SRC.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                if name in _CONSTRUCTORS and not any(k.arg == "task_id" for k in node.keywords):
                    missing.append(f"{path.relative_to(_SRC).as_posix()}:{node.lineno} {name}")
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
