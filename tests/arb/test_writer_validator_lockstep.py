"""Every ARB receipt gzkit writes must validate under ``gz arb validate`` (GHI #1026).

Measured 2026-09-18: 38 of the 300 newest receipts were rejected by the validator
for shapes gzkit's own writers produce -- 30 ``arb-red-*`` carrying
``base_provenance`` (added to the writer 2026-09-06; the schema last changed
2026-07-09), 6 ``arb-step-judge-*`` advisor verdicts under a schema id the
validator had never heard of, and 2 step receipts whose child died by signal
(``exit_status: -2`` against ``minimum: 0``). A validator that is red on normal
output hides the one finding in that run that was real.

The class is a receipt shape spelled twice -- once by the writer, once by the
schema -- with nothing holding the two together. Each test here builds the
receipt THROUGH THE WRITER and runs it through the validator, so a writer change
that outruns its schema fails here rather than in an operator's terminal. Each
family also keeps a negative control: a schema loosened until everything passes
would satisfy the positive tests alone.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.arb.red_reporter import build_red_receipt
from gzkit.arb.step_reporter import run_step_via_arb
from gzkit.arb.validator import CANONICAL_STEP_COMMANDS, validate_receipts
from gzkit.content.advisor_qc import record_verdict
from gzkit.red_witness import RedWitness


def _write(directory: Path, payload: dict[str, object]) -> None:
    (directory / f"{payload['run_id']}.json").write_text(json.dumps(payload), encoding="utf-8")


def _red_receipt(**overrides: object) -> dict[str, object]:
    witness = RedWitness(
        req_id="REQ-0.0.1-01-01",
        base_commit="abc1234",
        test_names=["tests.test_x.TestX.test_y"],
        exit_status=1,
        failure_class="assertion",
        base_provenance="reconstructed",
        output_tail="AssertionError: 1 != 2",
    )
    receipt = build_red_receipt(witness, duration_ms=5)
    receipt.update(overrides)
    return receipt


class TestRedReceiptsValidate(unittest.TestCase):
    def test_a_receipt_carrying_base_provenance_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(Path(tmp), _red_receipt())
            result = validate_receipts(root=Path(tmp))
        self.assertEqual((result.valid, result.errors), (1, []))

    def test_an_undeclared_property_is_still_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(Path(tmp), _red_receipt(smuggled="x"))
            result = validate_receipts(root=Path(tmp))
        self.assertEqual(result.invalid, 1)

    def test_an_unknown_provenance_value_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(Path(tmp), _red_receipt(base_provenance="somewhere-else"))
            result = validate_receipts(root=Path(tmp))
        self.assertEqual(result.invalid, 1)


class TestAdvisorVerdictReceiptsValidate(unittest.TestCase):
    def test_fresh_import_orders_can_record_and_validate(self) -> None:
        for first in ("gzkit.content.advisor_qc", "gzkit.arb"):
            with self.subTest(first=first):
                code = f"""
import {first}
import json
import tempfile
from pathlib import Path
from gzkit.content.advisor_qc import record_verdict
from gzkit.arb import validate_receipts
with tempfile.TemporaryDirectory() as tmp:
    path = record_verdict(root=Path(tmp), surface="AGENTS.md", consumer=None,
                          explanation="All entries retained.", score=0.9)
    result = validate_receipts(root=path.parent)
    print(json.dumps([result.scanned, result.valid, result.invalid, result.unknown_schema]))
"""
                result = subprocess.run(
                    [sys.executable, "-c", code],
                    capture_output=True,
                    text=True,
                    errors="replace",
                    timeout=30,
                    check=False,
                    env={
                        key: value
                        for key, value in os.environ.items()
                        if key != "GZKIT_ARB_RECEIPTS_ROOT"
                    },
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), [1, 1, 0, 0])

    def _record(self, root: Path) -> Path:
        with mock.patch.dict(os.environ, {"GZKIT_ARB_RECEIPTS_ROOT": str(root)}):
            return record_verdict(
                root=root,
                surface="AGENTS.md",
                consumer="root",
                explanation="Every live entry renders; nothing was compressed.",
                score=0.95,
            )

    def test_a_recorded_verdict_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._record(Path(tmp))
            result = validate_receipts(root=Path(tmp))
        self.assertEqual((result.valid, result.unknown_schema, result.errors), (1, 0, []))

    def test_a_verdict_without_its_explanation_is_rejected(self) -> None:
        """Explanation-before-verdict (ADR-0.0.39) binds the stored shape too."""
        with tempfile.TemporaryDirectory() as tmp:
            path = self._record(Path(tmp))
            payload = json.loads(path.read_text(encoding="utf-8"))
            del payload["explanation"]
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = validate_receipts(root=Path(tmp))
        self.assertEqual((result.invalid, result.unknown_schema), (1, 0))


class TestSignalKilledStepReceiptsValidate(unittest.TestCase):
    """A child terminated by signal N reports ``-N``; the receipt records what ran."""

    def _step(self, root: Path, returncode: int) -> None:
        killed = subprocess.CompletedProcess(["tool"], returncode, "", "")
        with (
            mock.patch.dict(os.environ, {"GZKIT_ARB_RECEIPTS_ROOT": str(root)}),
            mock.patch("gzkit.arb.step_reporter.subprocess.run", return_value=killed),
        ):
            run_step_via_arb(name="probe", cmd=["tool"], quiet=True)

    def test_a_negative_exit_status_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._step(Path(tmp), -2)
            result = validate_receipts(root=Path(tmp))
        self.assertEqual((result.valid, result.errors), (1, []))

    def test_a_non_integer_exit_status_is_still_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._step(Path(tmp), 0)
            path = next(Path(tmp).glob("arb-step-*.json"))
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["exit_status"] = "0"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = validate_receipts(root=Path(tmp))
        self.assertEqual(result.invalid, 1)


class TestProvenanceRemedyIsRunnable(unittest.TestCase):
    """The rejection names a command that exists.

    It used to say "Regenerate the receipt via `gz arb <name>`" -- but only some
    step names are verbs, so for `unittest` it prescribed `gz arb unittest`,
    which the parser does not register. `gz arb step --name <name> -- <argv>` is
    valid for every canonical step.
    """

    def test_the_remedy_is_the_canonical_step_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stale = subprocess.CompletedProcess(["uv"], 0, "", "")
            with (
                mock.patch.dict(os.environ, {"GZKIT_ARB_RECEIPTS_ROOT": tmp}),
                mock.patch("gzkit.arb.step_reporter.subprocess.run", return_value=stale),
            ):
                run_step_via_arb(
                    name="unittest", cmd=["uv", "run", "-m", "unittest", "-q"], quiet=True
                )
            result = validate_receipts(root=Path(tmp))

        self.assertEqual(result.non_canonical_provenance, 1)
        canonical = shlex.join(CANONICAL_STEP_COMMANDS["unittest"])
        self.assertIn(f"`uv run gz arb step --name unittest -- {canonical}`", result.errors[0])
        self.assertNotIn("gz arb unittest", result.errors[0])


if __name__ == "__main__":
    unittest.main()
