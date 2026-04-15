"""GHI-156: demo command discovery must validate derived verbs against the CLI.

The closeout ceremony's ``discover_demo_commands`` synthesizes ``uv run gz ...``
invocations from three sources in OBPI briefs:

1. ``## Demo`` fenced code blocks
2. ``docs/user/commands/*.md`` link patterns
3. Brief titles containing ``gz <verb>``

Before this fix, none of the three strategies validated the derived verb
against the registered CLI parser. Any slug that looked plausible got
emitted. OBPI-0.25.0-33 legitimately references ``docs/user/commands/
index.md`` (the docs-directory ToC page), and Strategy 2 derived
``uv run gz index --help`` from that filename — a verb that does not exist
in the parser at all. The ceremony walkthrough failed in production with
exit code 2: "invalid choice: 'index'".

These tests assert that every strategy validates derived verbs against
the real parser tree and drops anything unregistered. They exercise the
end-to-end path (brief file → discovery → registered-verb check) rather
than mocking the registered set, because the whole point of the fix is
that the registered set must be computed from the real parser at call
time.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.ceremony_data import (
    _collect_registered_invocations,
    _commands_from_brief_titles,
    _commands_from_command_doc_links,
    _commands_from_demo_sections,
    check_doc_alignment,
    discover_demo_commands,
)

# A brief fixture that reproduces the OBPI-0.25.0-33 pattern: a real
# command-doc link (arb.md), a shared-line mention of index.md, AND a
# standalone ``index.md`` line that the regex in ``check_doc_alignment``
# actually captures as a slug. The real OBPI-0.25.0-33 brief has
# ``docs/user/commands/index.md`` on its own bullet at line 255, which is
# how the Step 3 alignment table picked up ``gz index``.
OBPI_33_STYLE_BRIEF = """\
---
id: OBPI-0.25.0-33-arb-analysis-pattern
status: Completed
lane: heavy
---

# OBPI-0.25.0-33: ARB Analysis Pattern

## OBJECTIVE

Evaluate airlineops opsdev/arb module against gzkit's ARB surface.

## Allowed Paths

- `docs/user/commands/arb.md`, `docs/user/commands/index.md` — operator command reference
- `src/gzkit/arb/` — the ARB package surface

## Evidence

- `docs/user/commands/index.md` — new "ARB (Agent Self-Reporting)" section added
"""


class TestCollectRegisteredInvocations(unittest.TestCase):
    """The registered-invocations set is computed from the live parser tree."""

    def test_includes_known_top_level_verbs(self) -> None:
        invocations = _collect_registered_invocations()
        self.assertIn("arb", invocations)
        self.assertIn("adr", invocations)
        self.assertIn("status", invocations)

    def test_excludes_nonexistent_verbs(self) -> None:
        invocations = _collect_registered_invocations()
        self.assertNotIn("index", invocations)
        self.assertNotIn("frobnicate", invocations)
        self.assertNotIn("nonexistent-command", invocations)

    def test_includes_nested_subcommand_chains(self) -> None:
        """Commands like `gz adr status` must be discoverable at full depth."""
        invocations = _collect_registered_invocations()
        nested_chains = [inv for inv in invocations if " " in inv]
        self.assertTrue(
            len(nested_chains) > 0,
            "Parser walk must surface at least one nested verb chain (e.g. 'adr status')",
        )


class TestCommandDocLinkDiscoveryValidation(unittest.TestCase):
    """Strategy 2 — ``docs/user/commands/*.md`` links validated against parser."""

    def _write_brief(self, temp_dir: Path, content: str) -> Path:
        brief = temp_dir / "OBPI.md"
        brief.write_text(content, encoding="utf-8")
        return brief

    def _seed_command_doc(self, temp_dir: Path, slug: str) -> None:
        cmd_dir = temp_dir / "docs" / "user" / "commands"
        cmd_dir.mkdir(parents=True, exist_ok=True)
        (cmd_dir / f"{slug}.md").write_text(f"# {slug}\n", encoding="utf-8")

    def test_skips_index_md_because_gz_index_is_not_registered(self) -> None:
        """The triggering case: OBPI-33 references index.md as a real docs file.

        The discovery function must not emit `uv run gz index --help` because
        `gz index` is not a registered verb — even though the .md file exists.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._seed_command_doc(root, "arb")
            self._seed_command_doc(root, "index")
            brief = self._write_brief(root, OBPI_33_STYLE_BRIEF)

            commands = _commands_from_command_doc_links(root, [brief])

        self.assertIn("uv run gz arb --help", commands)
        self.assertNotIn("uv run gz index --help", commands)
        for cmd in commands:
            self.assertNotIn(" index ", f" {cmd} ")

    def test_skips_unregistered_slug_even_when_md_file_exists(self) -> None:
        """A .md file under commands/ does not imply the verb is registered."""
        brief_content = """\
---
id: OBPI-fake-01
status: Completed
lane: lite
---

# OBPI-fake

## Allowed Paths

- `docs/user/commands/frobnicate.md` — fake command reference
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._seed_command_doc(root, "frobnicate")
            brief = self._write_brief(root, brief_content)

            commands = _commands_from_command_doc_links(root, [brief])

        self.assertEqual(commands, [])

    def test_includes_registered_verb_slug(self) -> None:
        brief_content = """\
---
id: OBPI-valid-01
status: Completed
lane: lite
---

# OBPI-valid

## Allowed Paths

- `docs/user/commands/arb.md` — ARB manpage
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._seed_command_doc(root, "arb")
            brief = self._write_brief(root, brief_content)

            commands = _commands_from_command_doc_links(root, [brief])

        self.assertEqual(commands, ["uv run gz arb --help"])


class TestBriefTitleDiscoveryValidation(unittest.TestCase):
    """Strategy 3 — brief titles validated against parser."""

    def test_skips_unregistered_verb_in_title(self) -> None:
        brief_content = """\
---
id: OBPI-fake-02
status: Completed
lane: lite
---

# OBPI-fake-02: gz nonexistent

## OBJECTIVE

Does not correspond to a real verb.
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            brief = Path(temp_dir) / "OBPI.md"
            brief.write_text(brief_content, encoding="utf-8")

            commands = _commands_from_brief_titles([brief])

        self.assertEqual(commands, [])

    def test_includes_registered_verb_in_title(self) -> None:
        brief_content = """\
---
id: OBPI-valid-02
status: Completed
lane: lite
---

# OBPI-valid-02: gz arb surface

## OBJECTIVE

Touches the ARB verb.
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            brief = Path(temp_dir) / "OBPI.md"
            brief.write_text(brief_content, encoding="utf-8")

            commands = _commands_from_brief_titles([brief])

        self.assertIn("uv run gz arb --help", commands)


class TestDemoSectionDiscoveryValidation(unittest.TestCase):
    """Strategy 1 — ``## Demo`` fenced blocks validated against parser."""

    def test_skips_unregistered_verb_in_demo_block(self) -> None:
        brief_content = """\
---
id: OBPI-demo-01
status: Completed
lane: lite
---

# OBPI-demo-01

## Demo

```bash
uv run gz arb --help
uv run gz nonexistent --help
```
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            brief = Path(temp_dir) / "OBPI.md"
            brief.write_text(brief_content, encoding="utf-8")

            commands = _commands_from_demo_sections([brief])

        self.assertIn("uv run gz arb --help", commands)
        self.assertNotIn("uv run gz nonexistent --help", commands)

    def test_passes_through_non_gz_commands_unchanged(self) -> None:
        """Non-gz shell commands in a Demo block are operator-authored and
        should pass through without verb validation — validation only applies
        to ``uv run gz ...`` lines, which are the ones the ceremony promises
        to run against the gzkit CLI.
        """
        brief_content = """\
---
id: OBPI-demo-02
status: Completed
lane: lite
---

# OBPI-demo-02

## Demo

```bash
uv run gz arb --help
ls docs/user/commands/
```
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            brief = Path(temp_dir) / "OBPI.md"
            brief.write_text(brief_content, encoding="utf-8")

            commands = _commands_from_demo_sections([brief])

        self.assertIn("uv run gz arb --help", commands)
        self.assertIn("ls docs/user/commands/", commands)


class TestDiscoverDemoCommandsEndToEnd(unittest.TestCase):
    """Full `discover_demo_commands` pathway against the live parser."""

    def test_obpi_33_pattern_does_not_emit_gz_index(self) -> None:
        """Reproduce the exact production failure: OBPI-0.25.0-33 brief shape.

        The brief references both docs/user/commands/arb.md and
        docs/user/commands/index.md. Before the fix, discovery emitted both
        `uv run gz arb --help` and `uv run gz index --help`, and the ceremony
        walkthrough failed at the second command with exit code 2.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            cmd_dir = root / "docs" / "user" / "commands"
            cmd_dir.mkdir(parents=True)
            (cmd_dir / "arb.md").write_text("# arb\n", encoding="utf-8")
            (cmd_dir / "index.md").write_text("# commands index\n", encoding="utf-8")

            brief = root / "OBPI-0.25.0-33.md"
            brief.write_text(OBPI_33_STYLE_BRIEF, encoding="utf-8")

            commands = discover_demo_commands(root, "ADR-0.25.0", [brief])

        self.assertIn("uv run gz arb --help", commands)
        for cmd in commands:
            self.assertNotIn("gz index", cmd, f"Discovered unregistered verb in: {cmd}")


class TestCheckDocAlignmentValidation(unittest.TestCase):
    """GHI-156 follow-up: check_doc_alignment had the same class of failure.

    The Step 3 (Docs Alignment Check) renderer derives a ``gz <slug>`` command
    name from every ``docs/user/commands/*.md`` link it finds in a brief and
    emits a row in the alignment table. It had the *exact same* missing
    validation layer as the Step 5 demo discovery: ``index.md`` is the
    commands-directory ToC page, not a manpage for a verb named ``gz index``,
    so emitting a row with command=``gz index`` was drift-by-omission.

    These tests were written when the initial GHI-156 fix landed incomplete —
    discover_demo_commands was patched but check_doc_alignment was missed,
    and the Step 3 table continued to render ``gz index`` through a fresh
    ceremony. That is the failure the DO IT RIGHT maxim (added in the same
    commit as the incomplete fix) explicitly warns against: fixing one
    instance of a class of failure and leaving the sibling instance intact.
    """

    def _write_brief(self, temp_dir: Path, content: str) -> Path:
        brief = temp_dir / "OBPI.md"
        brief.write_text(content, encoding="utf-8")
        return brief

    def _seed_command_doc(self, temp_dir: Path, slug: str) -> None:
        cmd_dir = temp_dir / "docs" / "user" / "commands"
        cmd_dir.mkdir(parents=True, exist_ok=True)
        (cmd_dir / f"{slug}.md").write_text(f"# {slug}\n", encoding="utf-8")

    def test_excludes_index_md_row_from_alignment_table(self) -> None:
        """The triggering case: OBPI-33 pattern must not emit gz index row."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._seed_command_doc(root, "arb")
            self._seed_command_doc(root, "index")
            brief = self._write_brief(root, OBPI_33_STYLE_BRIEF)

            results = check_doc_alignment(root, [brief])

        commands = [r["command"] for r in results]
        self.assertIn("gz arb", commands)
        self.assertNotIn("gz index", commands)

    def test_excludes_unregistered_slug_even_when_md_file_exists(self) -> None:
        brief_content = """\
---
id: OBPI-fake-03
status: Completed
lane: lite
---

# OBPI-fake-03

## Allowed Paths

- `docs/user/commands/frobnicate.md` — fake
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._seed_command_doc(root, "frobnicate")
            brief = self._write_brief(root, brief_content)

            results = check_doc_alignment(root, [brief])

        commands = [r["command"] for r in results]
        self.assertEqual(commands, [])

    def test_includes_registered_slug_row(self) -> None:
        brief_content = """\
---
id: OBPI-valid-03
status: Completed
lane: lite
---

# OBPI-valid-03

## Allowed Paths

- `docs/user/commands/arb.md` — the arb manpage
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._seed_command_doc(root, "arb")
            brief = self._write_brief(root, brief_content)

            results = check_doc_alignment(root, [brief])

        commands = [r["command"] for r in results]
        self.assertIn("gz arb", commands)
        self.assertEqual(len(commands), 1)


if __name__ == "__main__":
    unittest.main()
