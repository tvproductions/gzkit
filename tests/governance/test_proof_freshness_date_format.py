"""Date-rendering semantics for the control-surface proof-freshness gate.

GHI #743 surfaced the gate; this module pins the defect found while running it.
``_iso`` rendered a commit epoch by asking git for
``git show -s --format=%cs @{<epoch>}``. ``@{<n>}`` is git's *reflog-relative*
revision syntax, not an epoch formatter: it resolves against the local reflog
and clamps to the reflog floor for anything older, so every pre-reflog epoch
rendered as the same wrong date. Three separate chores reported proofs "last
committed 2026-06-25" — the reflog floor, not a commit date. The true dates
were 2026-05-10, making the reported staleness ~5 weeks against an actual ~12.

The exit code was never wrong (``main`` compares raw epochs), which is what
made this survivable and therefore worth a regression test: a gate that judges
correctly while explaining itself falsely gets its remediation planned off the
explanation.

Both assertions below fail against the reflog implementation — the mapping
because it clamped, and the no-subprocess check because it shelled out.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch


def _load_freshness_gate() -> Any:
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "check_proof_freshness.py"
    spec = importlib.util.spec_from_file_location("check_proof_freshness", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_proof_freshness"] = module
    spec.loader.exec_module(module)
    return module


GATE = _load_freshness_gate()


class TestProofFreshnessDateRendering(unittest.TestCase):
    """``_iso`` renders the epoch's own UTC date, never a reflog-relative one."""

    def test_epoch_renders_its_own_utc_date(self) -> None:
        """Each epoch maps to its true UTC calendar date.

        The 1746000000 row is the observed defect: it is 2025-04-30, and the
        reflog implementation returned 2026-06-25 (the floor) for it.
        """
        cases = [
            (0, "1970-01-01"),
            (1746000000, "2025-04-30"),
            (1778000000, "2026-05-05"),
        ]
        for epoch, expected in cases:
            with self.subTest(epoch=epoch):
                self.assertEqual(GATE._iso(epoch), expected)

    def test_rendering_does_not_consult_git(self) -> None:
        """No subprocess is spawned to format a date.

        Asking git to format an epoch is what introduced the reflog
        dependency: the answer became a property of the local clone's reflog
        depth rather than of the epoch. Rendering must stay pure so a shallow
        clone, a fresh checkout, and CI all agree.
        """
        with patch.object(GATE.subprocess, "run") as run:
            rendered = GATE._iso(1746000000)
        self.assertEqual(rendered, "2025-04-30")
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
