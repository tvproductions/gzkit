"""``CANONICAL_STEP_COMMANDS`` must be reachable without the ARB validator chain.

The ``verifier-pipe-gate`` PreToolUse hook fires on **every** ``Bash`` tool call
and reads this table to decide whether a verifier is being piped. Sourcing it
from :mod:`gzkit.arb.validator` dragged ``jsonschema``, ``pydantic`` and
``gzkit.commands.common`` (which itself pulls ``gzkit.sync`` and
``gzkit.content.render``) into that hot path — measured 2026-08-22 at ~95ms of
import time to read one dependency-free dict.

These tests pin the two properties that keep the cost gone. They fail if the
leaf module regrows a heavy import, and they fail if the table is ever
duplicated rather than re-exported — a copy would let the hook and the gate
disagree about what "an ARB-wrapped verifier" is, which is the drift the
locked table exists to prevent.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest

# Modules whose presence proves the heavy chain was loaded. Each is a real
# transitive cost of ``gzkit.arb.validator``, not a proxy for one.
FORBIDDEN_ON_LEAF_IMPORT = (
    "jsonschema",
    "pydantic",
    "gzkit.arb.validator",
    "gzkit.commands.common",
    "gzkit.sync",
)


class CanonicalStepsLeafImportTests(unittest.TestCase):
    def test_leaf_import_pulls_no_heavy_dependency(self) -> None:
        """Importing the leaf module must not load the ARB validator chain."""
        probe = (
            "import sys, json;"
            "import gzkit.canonical_steps as m;"
            "print(json.dumps(sorted(k for k in sys.modules)))"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            # `.claude/rules/cross-platform.md` § Subprocess reads — non-UTF-8
            # output would raise UnicodeDecodeError and abort the probe.
            errors="replace",
            check=True,
        )
        loaded = set(json.loads(result.stdout))
        leaked = sorted(name for name in FORBIDDEN_ON_LEAF_IMPORT if name in loaded)
        self.assertEqual(
            leaked,
            [],
            f"leaf import leaked heavy modules {leaked}; the hot-path hook pays for each",
        )

    def test_validator_reexports_the_same_object(self) -> None:
        """The validator must re-export, never copy — one authority, no drift."""
        from gzkit.arb.validator import CANONICAL_STEP_COMMANDS as viavalidator
        from gzkit.canonical_steps import CANONICAL_STEP_COMMANDS as leaf

        self.assertIs(
            viavalidator,
            leaf,
            "validator holds a copy, not the leaf table; hook and gate can now disagree",
        )

    def test_verifier_pipe_gate_reads_the_same_object(self) -> None:
        """The hot-path consumer must read the same table the gate enforces."""
        from gzkit.canonical_steps import CANONICAL_STEP_COMMANDS as leaf
        from gzkit.verifier_pipe_gate import CANONICAL_STEP_COMMANDS as viagate

        self.assertIs(viagate, leaf)


if __name__ == "__main__":
    unittest.main()
