"""The validate manpage's Scopes Reference agrees with VALIDATOR_REGISTRY (GHI #1117).

The table restates the registry by hand: one row per scope, its default tier,
and a purpose line. Purpose prose cannot come from the registry, so the table
stays hand-written, and this test is its witness (Architectural Boundary 6). It
had drifted to 28 missing scopes and 8 wrong tiers before anything checked it.
"""

from __future__ import annotations

import argparse
import re
import unittest
from pathlib import Path

from gzkit.cli.main import _build_parser
from gzkit.commands.validate_cmd import VALIDATOR_REGISTRY

_MANPAGE = Path(__file__).resolve().parents[2] / "docs" / "user" / "manpages" / "validate.md"
_ROW_RE = re.compile(r"^\| `--([\w-]+)` \| (yes|opt-in) \|", re.MULTILINE)


def _scopes_reference(text: str) -> str:
    start = text.index("## Scopes Reference\n")
    end = text.find("\n## ", start + 1)
    return text[start : end if end != -1 else len(text)]


def _validate_flags() -> set[str]:
    parser = _build_parser()
    sub = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
    validate = sub.choices["validate"]
    return {s[2:] for a in validate._actions for s in a.option_strings if s.startswith("--")}


def scope_table_findings(text: str, flags: set[str]) -> list[str]:
    """Return every disagreement between the table and the registry."""
    rows = dict(_ROW_RE.findall(_scopes_reference(text)))
    registry = {
        e.stem.replace("_", "-"): "yes" if e.tier == "default" else "opt-in"
        for e in VALIDATOR_REGISTRY
    }
    findings = [f"--{s} has no row" for s in sorted(set(registry) - set(rows))]
    findings += [
        f"--{s} row says {rows[s]}, registry tier is {registry[s]}"
        for s in sorted(set(registry) & set(rows))
        if rows[s] != registry[s]
    ]
    findings += [f"--{s} row names no validate flag" for s in sorted(set(rows) - flags)]
    return findings


class ScopesReferenceTests(unittest.TestCase):
    def test_table_agrees_with_the_registry(self) -> None:
        text = _MANPAGE.read_text(encoding="utf-8")
        self.assertEqual(scope_table_findings(text, _validate_flags()), [])

    def test_a_missing_row_is_reported(self) -> None:
        """Control: dropping one registry scope's row is caught."""
        text = _MANPAGE.read_text(encoding="utf-8")
        stem = VALIDATOR_REGISTRY[0].stem.replace("_", "-")
        pruned = re.sub(rf"^\| `--{stem}` \|.*\n", "", text, flags=re.MULTILINE)
        self.assertIn(f"--{stem} has no row", scope_table_findings(pruned, _validate_flags()))

    def test_a_wrong_tier_is_reported(self) -> None:
        """Control: flipping one row's tier is caught."""
        text = _MANPAGE.read_text(encoding="utf-8")
        entry = VALIDATOR_REGISTRY[0]
        stem = entry.stem.replace("_", "-")
        right, wrong = ("yes", "opt-in") if entry.tier == "default" else ("opt-in", "yes")
        flipped = text.replace(f"| `--{stem}` | {right} |", f"| `--{stem}` | {wrong} |")
        findings = scope_table_findings(flipped, _validate_flags())
        self.assertIn(f"--{stem} row says {wrong}, registry tier is {right}", findings)

    def test_a_row_for_no_flag_is_reported(self) -> None:
        """Control: a row naming a flag the parser does not register is caught."""
        text = _MANPAGE.read_text(encoding="utf-8").replace(
            "| `--audits` |", "| `--not-a-real-scope` | opt-in | x |\n| `--audits` |"
        )
        findings = scope_table_findings(text, _validate_flags())
        self.assertIn("--not-a-real-scope row names no validate flag", findings)


if __name__ == "__main__":
    unittest.main()
