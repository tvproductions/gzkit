"""The stale rule, said once (GHI #1205).

A marker file is a cache anyone can write, and the sweep exists to clear a bad
one, so no marker's content may stop it. A time that cannot be compared is
treated as a time that cannot be read: OBPI-0.35.0-15 Requirement 6.
"""

import io
import json
import sys
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from gzkit.cli import main
from gzkit.cli.main import _ensure_utf8_console
from gzkit.pipeline_markers import (
    STALE_MARKER_HOURS,
    clear_stale_pipeline_markers,
    find_stale_pipeline_markers,
    marker_time_is_stale,
)
from tests.commands.common import CliRunner, _quick_init

_NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)
_OBPI = "OBPI-0.99.0-01-probe"


def _hours_ago(hours: int) -> str:
    return (datetime.now(UTC) - timedelta(hours=hours)).isoformat()


def _marker_bytes(updated_at: object) -> bytes:
    return json.dumps({"obpi_id": _OBPI, "updated_at": updated_at}).encode("utf-8")


def _marker_bytes_named(obpi_id: str) -> bytes:
    return json.dumps({"obpi_id": obpi_id, "updated_at": "2026-01-01T00:00:00"}).encode("utf-8")


#: Every malformed shape the closure contract names, each of which must read as stale.
_MALFORMED: dict[str, bytes] = {
    "a zoneless time": _marker_bytes("2026-01-01T00:00:00"),
    "a date with no time": _marker_bytes("2026-01-01"),
    "a time that is no time": _marker_bytes("yesterday"),
    "a time that is no text": _marker_bytes(1234),
    "no updated_at": json.dumps({"obpi_id": _OBPI}).encode("utf-8"),
    "JSON that is not an object": b"[1, 2]",
    "bytes that are not UTF-8": b"\xff\xfe\x00",
    "an integer past the conversion limit": b'{"updated_at": ' + b"1" * 5000 + b"}",
    "nesting past the decoder's depth": b"[" * 200_000,
}


class TestTheRule(unittest.TestCase):
    def test_times_that_cannot_be_compared_are_stale(self) -> None:
        for text in ("2026-11-01T11:59:00", "2026-11-01", "yesterday", ""):
            with self.subTest(text):
                try:
                    stale = marker_time_is_stale(text, _NOW)
                except TypeError as raised:
                    self.fail(f"the time stopped the sweep: {raised}")
                self.assertTrue(stale)

    def test_a_zoned_time_is_judged_by_its_age(self) -> None:
        inside = _NOW - timedelta(hours=STALE_MARKER_HOURS - 1)
        past = _NOW - timedelta(hours=STALE_MARKER_HOURS + 1)
        self.assertFalse(marker_time_is_stale(inside.isoformat(), _NOW))
        self.assertTrue(marker_time_is_stale(past.isoformat(), _NOW))

    def test_the_trailing_z_form_is_a_zoned_time(self) -> None:
        recent = (_NOW - timedelta(hours=1)).isoformat().replace("+00:00", "Z")
        self.assertFalse(marker_time_is_stale(recent, _NOW))

    def test_the_bound_is_the_callers_to_narrow(self) -> None:
        recent = (_NOW - timedelta(hours=3)).isoformat()
        self.assertTrue(marker_time_is_stale(recent, _NOW, max_age_hours=2))


class TestTheConsoleTakesAnyText(unittest.TestCase):
    def test_a_lone_surrogate_is_printed_and_stops_nothing(self) -> None:
        """A marker's JSON may decode to text strict UTF-8 cannot encode."""
        out = io.TextIOWrapper(io.BytesIO(), encoding="ascii")
        with patch.object(sys, "stdout", out), patch.object(sys, "stderr", out):
            _ensure_utf8_console()
            try:
                print("\ud800")  # noqa: T201
                out.flush()
            except UnicodeEncodeError as raised:
                self.fail(f"the text stopped the command: {raised}")
        self.assertIn(b"\\ud800", out.buffer.getvalue())


class TestTheSweep(unittest.TestCase):
    def setUp(self) -> None:
        self.held = TemporaryDirectory()
        self.addCleanup(self.held.cleanup)
        self.plans = Path(self.held.name)
        self.marker = self.plans / f".pipeline-active-{_OBPI}.json"

    def test_every_malformed_marker_is_flagged_and_removed(self) -> None:
        for name, content in _MALFORMED.items():
            with self.subTest(name):
                self.marker.write_bytes(content)
                try:
                    flagged = find_stale_pipeline_markers(self.plans)
                except (ValueError, RecursionError) as raised:
                    self.fail(f"the content stopped the sweep: {raised}")
                self.assertEqual(len(flagged), 1)
                self.assertEqual(len(clear_stale_pipeline_markers(self.plans)), 1)
                self.assertFalse(self.marker.exists())

    def test_one_bad_marker_does_not_stop_the_sweep_for_the_others(self) -> None:
        self.marker.write_bytes(_MALFORMED["a zoneless time"])
        other = self.plans / ".pipeline-active-OBPI-0.99.0-02-old.json"
        other.write_bytes(_marker_bytes(_hours_ago(STALE_MARKER_HOURS + 1)))
        self.assertEqual(len(clear_stale_pipeline_markers(self.plans)), 2)

    def test_a_live_zoned_marker_is_left_alone(self) -> None:
        self.marker.write_bytes(_marker_bytes(_hours_ago(1)))
        self.assertEqual(find_stale_pipeline_markers(self.plans), [])
        self.assertEqual(clear_stale_pipeline_markers(self.plans), [])
        self.assertTrue(self.marker.exists())


class TestThroughTheCommands(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        self.marker = Path(".claude/plans") / f".pipeline-active-{_OBPI}.json"
        self.marker.parent.mkdir(parents=True, exist_ok=True)
        self.marker.write_bytes(_MALFORMED["a zoneless time"])

    def test_clear_stale_removes_the_zoneless_marker(self) -> None:
        result = self.runner.invoke(main, ["obpi", "pipeline", _OBPI, "--clear-stale"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertNotIn("Traceback", result.output)
        self.assertFalse(self.marker.exists())

    def test_a_marker_naming_markup_is_cleared_and_never_read_as_markup(self) -> None:
        """A marker's text is data: Rich would refuse this id as a closing tag."""
        self.marker.write_bytes(_marker_bytes_named("[/x]"))
        result = self.runner.invoke(main, ["preflight", "--apply"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertFalse(self.marker.exists())
        self.marker.write_bytes(_marker_bytes_named("[/x]"))
        result = self.runner.invoke(main, ["obpi", "pipeline", _OBPI, "--clear-stale"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("[/x]", result.output)

    def test_a_marker_past_the_decoder_is_cleared_through_both_commands(self) -> None:
        for args in (["preflight", "--apply"], ["obpi", "pipeline", _OBPI, "--clear-stale"]):
            with self.subTest(args[0]):
                self.marker.write_bytes(_MALFORMED["an integer past the conversion limit"])
                result = self.runner.invoke(main, args)
                self.assertEqual(result.exit_code, 0, msg=result.output)
                self.assertFalse(self.marker.exists())

    def test_preflight_reports_the_zoneless_marker_with_no_traceback(self) -> None:
        result = self.runner.invoke(main, ["preflight"])
        self.assertEqual(result.exit_code, 1, msg=result.output)
        self.assertNotIn("Traceback", result.output)
        self.assertIn(self.marker.name, result.output)
