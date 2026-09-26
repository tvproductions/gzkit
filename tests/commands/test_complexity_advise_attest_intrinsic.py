"""Tests for ``gz complexity advise --attest-intrinsic`` and registry enrichment.

Coverage:
    REQ-0.0.29-07-02 — registry enrichment in complexity_advise_cmd path.
    REQ-0.0.29-07-03 — --attest-intrinsic refuses non-crossing function.
    REQ-0.0.29-07-04 — --attest-intrinsic emits exactly one event with TTY+ATTEST.
    REQ-0.0.29-07-05 — --attest-intrinsic refuses headless invocation; no
        partial state on any pre-emission failure (atomicity sub-claim).
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from gzkit.commands.complexity_advise import complexity_advise_cmd
from gzkit.complexity.advisor.intrinsic import clear_registry
from gzkit.ledger import Ledger
from gzkit.ledger_events import intrinsic_complexity_attestation_event
from gzkit.traceability import covers

_PRACTITIONER_EYE = "Refactor signal: extract the responsibility seam and re-test."


def _distilled_characteristics(metric: str = "radon_cc") -> str:
    return "\n".join(
        [
            "---",
            "corpus_revision: 1",
            "---",
            "",
            "# Distilled complexity characteristics — synthetic fixture",
            "",
            f"## Metric: `{metric}`",
            "",
            "Across the corpus, synthetic distribution applies.",
            "",
            "**Doctrinal frame:** Martin (Clean Code) — function decomposition signal.",
            "",
            "### Practitioner-eye observation",
            "",
            _PRACTITIONER_EYE,
            "",
        ]
    )


def _rule_data(metric: str, distilled_path: Path, anchor: str) -> str:
    """Synthesize the JSON data payload (GHI #426 — data is JSON, narrative .md)."""
    return json.dumps(
        {
            "corpus_revision": 1,
            "citation": {
                "distilled_characteristics_path": distilled_path.as_posix(),
                "section_anchor": anchor,
                "corpus_revision": 1,
            },
            "bands": [
                {
                    "metric": metric,
                    "corpus_percentile": 75,
                    "absolute_number": 4.0,
                    "trigger_semantic": "advise",
                },
                {
                    "metric": metric,
                    "corpus_percentile": 90,
                    "absolute_number": 7.0,
                    "trigger_semantic": "warn",
                },
                {
                    "metric": metric,
                    "corpus_percentile": 95,
                    "absolute_number": 11.0,
                    "trigger_semantic": "block",
                },
            ],
        }
    )


@contextmanager
def _synthetic_environment(metric: str = "radon_cc") -> Iterator[Path]:
    """Yield path to a synthetic threshold rule under a temp project root.

    Changes CWD to the temp dir so the engine resolves the citation path.
    """
    with tempfile.TemporaryDirectory() as raw_root:
        root = Path(raw_root)
        complexity_dir = root / "docs" / "governance" / "complexity"
        complexity_dir.mkdir(parents=True)
        distilled_path = complexity_dir / "distilled-characteristics-synthetic.md"
        distilled_path.write_text(_distilled_characteristics(metric), encoding="utf-8")
        rule_path = root / "complexity-thresholds.json"
        anchor = metric.replace("_", "-")
        rule_path.write_text(
            _rule_data(metric, distilled_path.relative_to(root), anchor),
            encoding="utf-8",
        )
        prior_cwd = Path.cwd()
        os.chdir(root)
        try:
            yield rule_path
        finally:
            os.chdir(prior_cwd)


_DECORATOR = '@intrinsic_complexity(reason="under test", attestor="g0")'


def _ledger_with_attestation(root: Path, *, file_path: str, qualname: str) -> Path:
    """Write a temp ledger holding one intrinsic-complexity-attestation event."""
    ledger = root / ".gzkit" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    event = intrinsic_complexity_attestation_event(
        file_path=file_path,
        qualname=qualname,
        reason="irreducibly complex dispatch",
        attestor="g0",
        attestation_date="2026-09-26",
        metric="radon_cc",
        crossing_band="block",
        crossing_value=13.0,
    )
    Ledger(ledger).append(event)
    return ledger


def _write_complex_function(
    target: Path, *, qualname: str = "complex_fn", decorator: str | None = None
) -> None:
    """Write a Python source file containing a function with cc above the block band."""
    header = (
        ["from gzkit.complexity.advisor.intrinsic import intrinsic_complexity", "", "", decorator]
        if decorator
        else []
    )
    body = "\n".join(
        [
            *header,
            f"def {qualname}(x):",
            "    if x == 1:",
            "        return 1",
            "    if x == 2:",
            "        return 2",
            "    if x == 3:",
            "        return 3",
            "    if x == 4:",
            "        return 4",
            "    if x == 5:",
            "        return 5",
            "    if x == 6:",
            "        return 6",
            "    if x == 7:",
            "        return 7",
            "    if x == 8:",
            "        return 8",
            "    if x == 9:",
            "        return 9",
            "    if x == 10:",
            "        return 10",
            "    if x == 11:",
            "        return 11",
            "    if x == 12:",
            "        return 12",
            "    return 0",
            "",
        ]
    )
    target.write_text(body, encoding="utf-8")


def _write_simple_function(target: Path) -> None:
    """Write a Python source file with a function whose cc is below the advise band."""
    target.write_text(
        "def trivial():\n    return 1\n",
        encoding="utf-8",
    )


class TestComplexityAdviseRegistryEnrichment(unittest.TestCase):
    """Task 2 — REQ-02 — registry enrichment path inside ``complexity_advise_cmd``."""

    def setUp(self) -> None:
        clear_registry()

    def tearDown(self) -> None:
        clear_registry()

    @covers("REQ-0.0.29-07-02")
    def test_ledger_attested_function_renders_attestation_message(self) -> None:
        """A function attested in the ledger emits the attestation message and exits 0.

        The advisor must NOT render a refactor recommendation for an attested
        function, and the run MUST exit 0 (GHI #1102: the event was written and
        never read back).
        """
        with _synthetic_environment() as rule_path:
            source_file = rule_path.parent / "complex.py"
            _write_complex_function(source_file)
            ledger = _ledger_with_attestation(
                rule_path.parent, file_path=str(source_file), qualname="complex_fn"
            )

            buf = io.StringIO()
            with (
                contextlib.redirect_stdout(buf),
                patch(
                    "gzkit.commands.complexity_advise._resolve_ledger_path",
                    return_value=ledger,
                ),
            ):
                exit_code = complexity_advise_cmd(path=str(source_file), rule_path=str(rule_path))

            self.assertEqual(exit_code, 0)
            output = buf.getvalue()
            self.assertIn("intrinsic complexity attested by 'g0'", output)
            self.assertIn("irreducibly complex dispatch", output)
            self.assertNotIn("Recommended", output)

    @covers("REQ-0.0.29-07-02")
    def test_ledger_attestation_of_another_function_does_not_apply(self) -> None:
        with _synthetic_environment() as rule_path:
            source_file = rule_path.parent / "complex.py"
            _write_complex_function(source_file)
            ledger = _ledger_with_attestation(
                rule_path.parent, file_path=str(source_file), qualname="other_fn"
            )

            with (
                contextlib.redirect_stdout(io.StringIO()),
                patch(
                    "gzkit.commands.complexity_advise._resolve_ledger_path",
                    return_value=ledger,
                ),
                self.assertRaises(SystemExit) as ctx,
            ):
                complexity_advise_cmd(path=str(source_file), rule_path=str(rule_path))
            self.assertEqual(ctx.exception.code, 3)

    @covers("REQ-0.0.29-07-02")
    def test_unattested_block_band_still_exits_3(self) -> None:
        """An unattested block-band crossing still produces exit 3."""
        with (
            _synthetic_environment() as rule_path,
            tempfile.TemporaryDirectory() as tmp_str,
        ):
            tmp = Path(tmp_str)
            source_file = tmp / "complex.py"
            _write_complex_function(source_file)

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit) as ctx:
                complexity_advise_cmd(path=str(source_file), rule_path=str(rule_path))
            self.assertEqual(ctx.exception.code, 3)


class TestComplexityAdviseAttestIntrinsic(unittest.TestCase):
    """Task 3 — --attest-intrinsic commit-time path."""

    def setUp(self) -> None:
        clear_registry()
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.ledger_path = self.tmp / ".gzkit" / "ledger.jsonl"
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        clear_registry()
        self._tmp.cleanup()

    def _ledger_events(self) -> list[dict]:
        if not self.ledger_path.exists():
            return []
        return [
            json.loads(line)
            for line in self.ledger_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    @covers("REQ-0.0.29-07-03")
    def test_attest_intrinsic_refuses_non_crossing_function(self) -> None:
        """--attest-intrinsic exits 1 if the function does not cross any band."""
        from gzkit.commands.complexity_advise import _run_attest_intrinsic

        source_file = self.tmp / "trivial.py"
        _write_simple_function(source_file)

        buf_err = io.StringIO()
        with (
            contextlib.redirect_stderr(buf_err),
            patch(
                "gzkit.commands.complexity_advise._resolve_ledger_path",
                return_value=self.ledger_path,
            ),
        ):
            exit_code = _run_attest_intrinsic(
                path=f"{source_file}:trivial",
                reason="should not register",
                attestor="Test Attestor",
                rule_path=None,
            )
        self.assertEqual(exit_code, 1)
        self.assertEqual(self._ledger_events(), [])

    @covers("REQ-0.0.29-07-05")
    def test_attest_intrinsic_refuses_headless_invocation(self) -> None:
        """--attest-intrinsic exits 1 if not attached to a TTY."""
        from gzkit.commands.complexity_advise import _run_attest_intrinsic

        source_file = self.tmp / "complex.py"
        _write_complex_function(source_file)

        buf_err = io.StringIO()
        with (
            contextlib.redirect_stderr(buf_err),
            patch(
                "gzkit.commands.complexity_advise._is_attest_tty_available",
                return_value=False,
            ),
            patch(
                "gzkit.commands.complexity_advise._resolve_ledger_path",
                return_value=self.ledger_path,
            ),
        ):
            exit_code = _run_attest_intrinsic(
                path=f"{source_file}:complex_fn",
                reason="cc=13 dispatch table",
                attestor="Test Attestor",
                rule_path=None,
            )
        self.assertEqual(exit_code, 1)
        self.assertEqual(self._ledger_events(), [])

    @covers("REQ-0.0.29-07-05")
    def test_attest_intrinsic_no_partial_state_on_parse_error(self) -> None:
        """A malformed <path>:<qualname> emits no ledger event."""
        from gzkit.commands.complexity_advise import _run_attest_intrinsic

        buf_err = io.StringIO()
        with (
            contextlib.redirect_stderr(buf_err),
            patch(
                "gzkit.commands.complexity_advise._resolve_ledger_path",
                return_value=self.ledger_path,
            ),
        ):
            # No ":" separator at all — must fail parse, no event.
            exit_code = _run_attest_intrinsic(
                path="malformed_no_colon",
                reason="will not run",
                attestor="Test Attestor",
                rule_path=None,
            )
        self.assertEqual(exit_code, 1)
        self.assertEqual(self._ledger_events(), [])

    @covers("REQ-0.0.29-07-04")
    def test_attest_intrinsic_emits_event_with_tty(self) -> None:
        """--attest-intrinsic emits exactly one event when TTY + ATTEST given."""
        from gzkit.commands.complexity_advise import _run_attest_intrinsic

        source_file = self.tmp / "complex.py"
        _write_complex_function(source_file)

        buf_out = io.StringIO()
        with (
            contextlib.redirect_stdout(buf_out),
            patch(
                "gzkit.commands.complexity_advise._is_attest_tty_available",
                return_value=True,
            ),
            patch(
                "gzkit.commands.complexity_advise._prompt_attest_confirmation",
                return_value="ATTEST",
            ),
            patch(
                "gzkit.commands.complexity_advise._resolve_ledger_path",
                return_value=self.ledger_path,
            ),
        ):
            exit_code = _run_attest_intrinsic(
                path=f"{source_file}:complex_fn",
                reason="cc=13 dispatch table for irreducible state machine",
                attestor="Test Attestor",
                rule_path=None,
            )

        self.assertEqual(exit_code, 0)
        events = self._ledger_events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["event"], "intrinsic-complexity-attestation")
        # Receipt id is "<file_path>::<qualname>"
        expected_id = f"{source_file}::complex_fn"
        self.assertEqual(event["id"], expected_id)
        self.assertEqual(event["attestor"], "Test Attestor")
        self.assertEqual(
            event["reason"],
            "cc=13 dispatch table for irreducible state machine",
        )
        self.assertEqual(event["file_path"], str(source_file))
        self.assertEqual(event["qualname"], "complex_fn")
        self.assertEqual(event["metric"], "radon_cc")
        self.assertEqual(event["crossing_band"], "block")
        # Receipt id should appear in stdout.
        self.assertIn(expected_id, buf_out.getvalue())


class TestIntrinsicComplexityCliPath(unittest.TestCase):
    """Task 2 — CLI-side coverage that decorator + advisor compose end-to-end."""

    def setUp(self) -> None:
        clear_registry()

    def tearDown(self) -> None:
        clear_registry()

    @covers("REQ-0.0.29-07-02")
    def test_decorated_function_takes_attestation_path(self) -> None:
        """A literal @intrinsic_complexity in source is honoured by a CLI run (GHI #1102)."""
        with _synthetic_environment() as rule_path:
            source_file = rule_path.parent / "complex.py"
            _write_complex_function(source_file, decorator=_DECORATOR)

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                exit_code = complexity_advise_cmd(path=str(source_file), rule_path=str(rule_path))

            self.assertEqual(exit_code, 0)
            output = buf.getvalue()
            self.assertIn("intrinsic complexity attested by 'g0'", output)
            self.assertIn("under test", output)
            self.assertNotIn("Recommended", output)

    @covers("REQ-0.0.29-07-02")
    def test_decorator_with_empty_reason_is_not_honoured(self) -> None:
        with _synthetic_environment() as rule_path:
            source_file = rule_path.parent / "complex.py"
            _write_complex_function(
                source_file, decorator='@intrinsic_complexity(reason="", attestor="g0")'
            )

            with (
                contextlib.redirect_stdout(io.StringIO()),
                self.assertRaises(SystemExit) as ctx,
            ):
                complexity_advise_cmd(path=str(source_file), rule_path=str(rule_path))
            self.assertEqual(ctx.exception.code, 3)


if __name__ == "__main__":
    unittest.main()
