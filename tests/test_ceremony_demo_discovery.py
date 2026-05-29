"""Regression: ceremony demo extraction must not shred multi-line constructs.

GHI #539 — ``_commands_from_demo_sections`` split each physical line of a
multi-line ``python -c "…"`` heredoc into its own "demo", producing ~65%
walkthrough noise. After OBPI-0.0.63-02 it delegates per-block parsing to
``brief_commands.extract_fenced_commands`` (BI-1), so a multi-line construct
surfaces as exactly one logical command while the registered-``gz``-verb
validation is preserved.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.commands.ceremony_data import _commands_from_demo_sections
from gzkit.traceability import covers

_FIXTURE = Path(__file__).parent / "fixtures" / "ceremony_demos" / "multiline_demo.md"


class TestCeremonyDemoDiscovery(unittest.TestCase):
    @covers("REQ-0.0.63-02-01")
    def test_multiline_demo_is_one_command_not_shredded(self) -> None:
        commands = _commands_from_demo_sections([_FIXTURE])
        # Two demos survive: the registered `gz adr status` line and the
        # pass-through multi-line `python -c` construct — NOT 5+ shredded fragments.
        self.assertEqual(len(commands), 2, f"got {commands!r}")
        # The continuation body lives inside the python command, never as its own entry.
        self.assertFalse(
            any(c.strip() == "from pathlib import Path" for c in commands),
            f"continuation fragment leaked as its own command: {commands!r}",
        )
        self.assertTrue(
            any("from pathlib import Path" in c and "uv run python -c" in c for c in commands),
            f"multi-line construct was shredded: {commands!r}",
        )

    @covers("REQ-0.0.63-02-01")
    def test_registered_gz_verb_validation_preserved(self) -> None:
        commands = _commands_from_demo_sections([_FIXTURE])
        self.assertTrue(any(c.startswith("uv run gz status") for c in commands))


if __name__ == "__main__":
    unittest.main()
