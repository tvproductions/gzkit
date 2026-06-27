"""Ceremony demo discovery: only documented ``gz`` commands reach the walkthrough.

Two coupled contracts are pinned here:

- GHI #539 / REQ-0.0.63-02-01: a multi-line fenced construct is parsed as ONE
  logical command, never shredded per-physical-line. (The multi-line *parsing*
  guard proper lives in ``tests/test_brief_commands.py``; here it is observed
  through the discovery layer's registered-``gz``-verb filter.)
- Ceremony Rule #4 enforcement (ADR-0.0.74 demo-compliance class-fix):
  ``_commands_from_demo_sections`` REJECTS any command that is not a registered
  ``gz`` invocation — non-``gz`` commands (``python -c``, raw ``unittest``,
  shell pipes) and unregistered ``gz`` verbs alike. The walkthrough is the
  operator's product-demonstration surface and never a place for improvised
  invocations; the doctrine (Rule #4) ships with coupled enforcement at the
  discovery layer rather than relying on brief authors to self-police.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.ceremony_data import _commands_from_demo_sections
from gzkit.traceability import covers

_FIXTURE = Path(__file__).parent / "fixtures" / "ceremony_demos" / "multiline_demo.md"


class TestCeremonyDemoDiscovery(unittest.TestCase):
    @covers("REQ-0.0.63-02-01")
    def test_registered_gz_verb_validation_preserved(self) -> None:
        commands = _commands_from_demo_sections([_FIXTURE])
        self.assertTrue(any(c.startswith("uv run gz status") for c in commands))

    def test_non_gz_demo_command_is_rejected(self) -> None:
        # The fixture's ``## Demo`` holds a registered ``gz status`` command and
        # a multi-line ``python -c`` construct. Only the gz command may surface —
        # the non-gz construct is rejected (Ceremony Rule #4), not passed through
        # and not shredded into per-line fragments.
        commands = _commands_from_demo_sections([_FIXTURE])
        self.assertEqual(commands, ["uv run gz status --json"], f"got {commands!r}")
        self.assertFalse(
            any("python -c" in c for c in commands),
            f"non-gz python -c leaked into the walkthrough: {commands!r}",
        )

    def test_non_gz_and_unregistered_gz_both_rejected(self) -> None:
        # A registered gz verb survives; a non-gz command and a ``gz`` whose verb
        # is not registered in the parser are both dropped — no improvised or
        # stale invocations reach the walkthrough.
        brief = (
            "---\nid: OBPI-FIXTURE\n---\n\n## Demo\n\n```bash\n"
            "uv run gz check\n"
            "uv run gz definitely-not-a-real-verb --json\n"
            "ls -la\n"
            "```\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            brief_path = Path(tmp) / "OBPI-FIXTURE.md"
            brief_path.write_text(brief, encoding="utf-8")
            commands = _commands_from_demo_sections([brief_path])
        self.assertEqual(commands, ["uv run gz check"], f"got {commands!r}")


if __name__ == "__main__":
    unittest.main()
