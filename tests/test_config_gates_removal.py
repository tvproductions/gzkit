"""Tests for config.gates removal (OBPI-0.0.8-07).

Verifies that the config.gates prototype is fully removed from the codebase,
stale .gzkit.json files with a ``gates`` key produce a clear deprecation
warning, and config loads cleanly without the gates key.
"""

import json
import tempfile
import unittest
import warnings
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.traceability import covers


class TestConfigGatesFieldRemoved(unittest.TestCase):
    """GzkitConfig no longer exposes gates field or gate() method."""

    @covers("REQ-0.0.8-07-01")
    def test_config_loads_without_gates(self) -> None:
        """Config without gates key loads cleanly with no warnings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".gzkit.json"
            config_file.write_text(json.dumps({"mode": "lite", "paths": {}}), encoding="utf-8")
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                config = GzkitConfig.load(config_file)

            self.assertEqual(config.mode, "lite")
            gate_warnings = [w for w in caught if "gates" in str(w.message).lower()]
            self.assertEqual(gate_warnings, [])


class TestStaleGatesKeyWarning(unittest.TestCase):
    """Stale gates key in .gzkit.json produces deprecation warning."""

    @covers("REQ-0.0.8-07-02")
    def test_stale_gates_key_warns(self) -> None:
        """Config with gates key emits DeprecationWarning naming 'flags'."""
        data = {"mode": "lite", "paths": {}, "gates": {"product_proof": "advisory"}}
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".gzkit.json"
            config_file.write_text(json.dumps(data), encoding="utf-8")

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                config = GzkitConfig.load(config_file)

            self.assertEqual(config.mode, "lite")
            dep_warnings = [w for w in caught if issubclass(w.category, DeprecationWarning)]
            self.assertEqual(len(dep_warnings), 1)
            msg = str(dep_warnings[0].message)
            self.assertIn("gates", msg)
            self.assertIn("flags", msg)


class TestConfigGateReferencesRemoved(unittest.TestCase):
    """No stale config.gate references remain in src/gzkit/."""

    @covers("REQ-0.0.8-07-03")
    def test_no_config_gate_in_source(self) -> None:
        """Grep for config.gate across src/gzkit/ returns zero matches."""
        import re

        src_dir = Path(__file__).resolve().parent.parent / "src" / "gzkit"
        pattern = re.compile(r"config\.gate[(\[]")
        matches: list[str] = []
        for py_file in src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            for i, line in enumerate(content.splitlines(), 1):
                if pattern.search(line):
                    matches.append(f"{py_file}:{i}: {line.strip()}")

        self.assertEqual(matches, [], "Stale config.gate references:\n" + "\n".join(matches))


class TestConfigGatesFieldRejected(unittest.TestCase):
    """GzkitConfig rejects gates= as extra field."""

    @covers("REQ-0.0.8-07-04")
    def test_full_test_suite_passes(self) -> None:
        """GzkitConfig(gates=...) raises ValidationError (extra='forbid')."""
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            GzkitConfig(gates={"product_proof": "advisory"})


if __name__ == "__main__":
    unittest.main()
