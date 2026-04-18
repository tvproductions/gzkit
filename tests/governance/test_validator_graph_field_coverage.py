"""Every artifact-graph field the validator reads must be populated by the graph builder.

GHI #193 was the canonical instance of this class: the validator read
``info.get("attested")`` but nothing in the graph builder wrote that field on
the single event path (``obpi_receipt_emitted``) that actually carried the
attestation signal. The graph silently returned ``False`` for every attested
OBPI and the validator's downstream derivation went with it.

This test enumerates every ``info.get("<field>")`` call in
``src/gzkit/commands/validate_frontmatter.py`` and asserts each field is
written somewhere under ``src/gzkit/ledger.py`` — either as a key in the
artifact creation entry or via ``graph[id]["<field>"] = ...`` in a
``_apply_*`` handler. Any unmapped field is either a bug (silent blind-spot)
or a read that should be removed.
"""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_VALIDATOR = _PROJECT_ROOT / "src" / "gzkit" / "commands" / "validate_frontmatter.py"
_LEDGER = _PROJECT_ROOT / "src" / "gzkit" / "ledger.py"

# Waivers: fields the validator reads that intentionally do not need
# graph-level population (e.g., fields supplied by computation elsewhere
# before the validator sees them). Keep this set empty unless truly needed.
NO_POPULATION_REQUIRED: dict[str, str] = {}


class ValidatorGraphFieldCoverage(unittest.TestCase):
    """Every ``info.get(...)`` field the validator reads must be written by the graph builder."""

    def test_every_field_is_populated_or_waived(self) -> None:
        read_fields = _collect_info_get_fields(_VALIDATOR)
        written_fields = _collect_ledger_written_fields(_LEDGER)

        unpopulated = sorted(read_fields - written_fields - NO_POPULATION_REQUIRED.keys())
        self.assertFalse(
            unpopulated,
            msg=(
                "Validator reads artifact-graph fields that are never written "
                "by src/gzkit/ledger.py. Either add population in a "
                "_apply_*_metadata handler (or the creation entry), or remove "
                "the read. This exact pattern produced GHI #193 — don't repeat "
                "it.\nUnpopulated reads: " + ", ".join(unpopulated)
            ),
        )


def _collect_info_get_fields(source: Path) -> set[str]:
    """Return every string literal key passed to ``info.get("...")``."""
    tree = ast.parse(source.read_text(encoding="utf-8"))
    fields: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != "get":
            continue
        caller = func.value
        if not isinstance(caller, ast.Name) or caller.id != "info":
            continue
        if not node.args:
            continue
        key = node.args[0]
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            fields.add(key.value)
    return fields


_GRAPH_WRITE_PATTERN = re.compile(r'graph\[[^\]]+\]\["([^"]+)"\]')
_ENTRY_KEY_PATTERN = re.compile(r'\bentry\["([^"]+)"\]')


def _collect_ledger_written_fields(source: Path) -> set[str]:
    """Return every graph-entry key the ledger writes.

    Two forms are recognized:

    * ``graph[canonical_id]["<field>"] = value`` — direct writes in
      ``_apply_*_metadata`` handlers.
    * ``entry["<field>"] = value`` and initializer dicts in
      ``_artifact_creation_entry``.
    """
    text = source.read_text(encoding="utf-8")
    written: set[str] = set()
    written.update(_GRAPH_WRITE_PATTERN.findall(text))
    written.update(_ENTRY_KEY_PATTERN.findall(text))

    # Also scan the dict literal inside _artifact_creation_entry — its keys
    # are set at node creation and constitute the authoritative baseline.
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name != "_artifact_creation_entry":
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Dict):
                for key in sub.keys:
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        written.add(key.value)
    return written


if __name__ == "__main__":
    unittest.main()
