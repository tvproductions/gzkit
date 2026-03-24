"""Tests for gz gates deprecation warning (OBPI-0.19.0-08).

Verifies that gates_cmd emits a deprecation warning to stderr while
continuing to execute gates normally.
"""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import gates_cmd
from gzkit.config import GzkitConfig


def _scaffold_project(tmp: Path, *, lane: str = "lite") -> Path:
    """Create minimal project scaffolding for gates_cmd."""
    (tmp / ".gzkit").mkdir(exist_ok=True)

    # Ledger with an ADR
    ledger_path = tmp / ".gzkit" / "ledger.jsonl"
    events = [
        {
            "schema": "gzkit.ledger.v1",
            "event": "adr_created",
            "id": "ADR-TEST",
            "ts": "2026-01-01T00:00:00Z",
            "lane": lane,
        },
    ]
    ledger_path.write_text(
        "\n".join(json.dumps(e) for e in events) + "\n",
        encoding="utf-8",
    )

    # Config (.gzkit.json at project root)
    config_path = tmp / ".gzkit.json"
    config_path.write_text(
        json.dumps({"mode": lane, "paths": {"ledger": ".gzkit/ledger.jsonl"}}),
        encoding="utf-8",
    )

    # Manifest
    manifest_path = tmp / ".gzkit" / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "gates": {"lite": [1, 2], "heavy": [1, 2, 3, 4, 5]},
                "verification": {"test": "echo PASS"},
            }
        ),
        encoding="utf-8",
    )

    return tmp


class TestGatesDeprecationWarning(unittest.TestCase):
    """REQ-0.19.0-08-01/02/03: gates_cmd emits deprecation warning."""

    @patch("gzkit.cli.main.get_project_root")
    @patch("gzkit.cli.main.ensure_initialized")
    def test_deprecation_warning_emitted(
        self, mock_init: unittest.mock.MagicMock, mock_root: unittest.mock.MagicMock
    ) -> None:
        """REQ-01: Deprecation warning containing 'deprecated' and 'gz closeout' is printed."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = _scaffold_project(Path(tmp))
            mock_root.return_value = tmp_path

            config = GzkitConfig.load(tmp_path / ".gzkit.json")
            mock_init.return_value = config

            captured_stderr = io.StringIO()
            with patch("sys.stderr", captured_stderr), contextlib.suppress(SystemExit, Exception):
                gates_cmd(gate_number=None, adr="ADR-TEST")

            warning_text = captured_stderr.getvalue().lower()
            self.assertIn("deprecated", warning_text)
            self.assertIn("gz closeout", warning_text)

    @patch("gzkit.cli.main.get_project_root")
    @patch("gzkit.cli.main.ensure_initialized")
    def test_gates_still_execute_after_warning(
        self, mock_init: unittest.mock.MagicMock, mock_root: unittest.mock.MagicMock
    ) -> None:
        """REQ-02/03: After deprecation warning, gates execute normally."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = _scaffold_project(Path(tmp))
            mock_root.return_value = tmp_path

            config = GzkitConfig.load(tmp_path / ".gzkit.json")
            mock_init.return_value = config

            manifest = {"gates": {"lite": [1, 2]}, "verification": {"test": "echo PASS"}}

            with (
                patch("sys.stderr", io.StringIO()),
                patch("gzkit.cli.main.console"),
                patch("gzkit.cli.main.load_manifest", return_value=manifest),
                patch("gzkit.cli.main.resolve_target_adr", return_value="ADR-TEST"),
                patch("gzkit.cli.main.resolve_adr_lane", return_value="lite"),
                patch("gzkit.cli.main._run_gate_1", return_value=True) as mock_gate1,
                patch("gzkit.cli.main._run_gate_2", return_value=True) as mock_gate2,
            ):
                gates_cmd(gate_number=None, adr="ADR-TEST")

                self.assertTrue(
                    mock_gate1.called or mock_gate2.called,
                    "Gates should execute after deprecation warning",
                )

    def test_gate_runners_importable_independently(self) -> None:
        """REQ-04: _run_gate_1 through _run_gate_5 remain importable."""
        from gzkit.cli import (
            _run_gate_1,
            _run_gate_2,
            _run_gate_3,
            _run_gate_4,
            _run_gate_5,
        )

        self.assertTrue(callable(_run_gate_1))
        self.assertTrue(callable(_run_gate_2))
        self.assertTrue(callable(_run_gate_3))
        self.assertTrue(callable(_run_gate_4))
        self.assertTrue(callable(_run_gate_5))


if __name__ == "__main__":
    unittest.main()
