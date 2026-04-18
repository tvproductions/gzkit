"""Every ``gz <verb>`` string in a behave feature must reference a real CLI verb (GHI #198).

During ADR-0.0.16 closeout, ``features/gates.feature`` asserted against
``"gz chore run"`` (singular) after GHI #189 had renamed the recovery hint
to ``"gz chores run"`` (plural). The scenario was stale for weeks and no
mechanical guard caught the drift. This scan walks every ``.feature`` file
and extracts each ``gz <verb>`` substring from string literals (both quoted
CLI invocations and ``contains "..."`` assertions), then verifies the
top-level verb resolves through the CLI parser.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FEATURES_ROOT = _PROJECT_ROOT / "features"

# Match ``gz <verb>`` in backticked or double-quoted invocations. These are
# the strings behave scenarios actually execute or assert against — prose
# references (including the step-def fixture ``the gz command "<args>"``)
# are intentionally skipped.
_BACKTICKED_INVOCATION = re.compile(r"`gz\s+([a-z][a-z0-9-]*)[^`]*`")
_QUOTED_INVOCATION = re.compile(r'"gz\s+([a-z][a-z0-9-]*)[^"]*"')
# Step-def syntax: ``When I run the gz command "task --help"``. The first
# word inside the quoted arg is the real verb.
_STEP_DEF_FIXTURE = re.compile(r'the gz command\s+"([a-z][a-z0-9-]*)')


class BehaveCliAlignmentPolicy(unittest.TestCase):
    """No stale ``gz <verb>`` invocations may appear in behave features."""

    def test_every_gz_verb_in_features_resolves(self) -> None:
        offenders: list[str] = []
        runner = CliRunner()
        verbs_seen: dict[str, list[str]] = {}

        for feature_path in _FEATURES_ROOT.rglob("*.feature"):
            for lineno, line in enumerate(feature_path.read_text(encoding="utf-8").splitlines(), 1):
                rel = f"{feature_path.relative_to(_PROJECT_ROOT)}:{lineno}"
                for pattern in (
                    _BACKTICKED_INVOCATION,
                    _QUOTED_INVOCATION,
                    _STEP_DEF_FIXTURE,
                ):
                    for match in pattern.finditer(line):
                        verbs_seen.setdefault(match.group(1), []).append(rel)

        for verb, locations in sorted(verbs_seen.items()):
            result = runner.invoke(main, [verb, "--help"])
            if result.exit_code != 0:
                offenders.append(
                    f"`gz {verb}` resolves with exit {result.exit_code} "
                    f"(seen in {', '.join(locations[:3])}"
                    f"{'...' if len(locations) > 3 else ''})"
                )

        self.assertFalse(
            offenders,
            msg=(
                "Behave features cite `gz <verb>` strings that do not resolve through "
                "the CLI parser. Fix the feature assertion or add the verb to the CLI "
                "before landing.\n" + "\n".join(offenders)
            ),
        )


if __name__ == "__main__":
    unittest.main()
