"""Every ``gz <verb>`` string in a behave feature or operator doc must resolve (GHI #198).

During ADR-0.0.16 closeout, ``features/gates.feature`` asserted against
``"gz chore run"`` (singular) after GHI #189 had renamed the recovery hint
to ``"gz chores run"`` (plural). The scenario was stale for weeks and no
mechanical guard caught the drift. The same class of failure lives in
``docs/user/runbook.md``, command docs, and manpages — the closeout session
also found a stale ``gz arb step --name typecheck -- uvx ty check . --exclude
'features/**'`` line in the runbook (fixed under GHI #199).

This scan walks every behave ``.feature`` file, the operator runbook, the
per-command docs under ``docs/user/commands/``, and the manpages under
``docs/user/manpages/``. It extracts each ``gz <verb>`` substring from
backticked invocations, double-quoted invocations, and the step-def fixture
form, then verifies the top-level verb resolves through the CLI parser.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FEATURES_ROOT = _PROJECT_ROOT / "features"
_DOCS_SCAN_TARGETS: tuple[Path, ...] = (
    _PROJECT_ROOT / "docs" / "user" / "runbook.md",
    *sorted((_PROJECT_ROOT / "docs" / "user" / "commands").rglob("*.md")),
    *sorted((_PROJECT_ROOT / "docs" / "user" / "manpages").rglob("*.md")),
)

# Verbs that appear in prose/templates but are intentionally placeholders or
# example skeletons, not real invocations. Keep this list tight.
_DOC_PROSE_VERBS: frozenset[str] = frozenset(
    {
        # Placeholder tokens used as templated examples in manpages / runbook
        # prose (e.g. `gz <verb>` in a description paragraph, not an invocation).
    }
)

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
    """No stale ``gz <verb>`` invocations may appear in behave features or operator docs."""

    def test_every_gz_verb_in_features_resolves(self) -> None:
        self._assert_all_verbs_resolve(
            sources=list(_FEATURES_ROOT.rglob("*.feature")),
            label="Behave features",
        )

    def test_every_gz_verb_in_operator_docs_resolves(self) -> None:
        self._assert_all_verbs_resolve(
            sources=list(_DOCS_SCAN_TARGETS),
            label="Operator docs",
        )

    def _assert_all_verbs_resolve(self, *, sources: list[Path], label: str) -> None:
        offenders: list[str] = []
        runner = CliRunner()
        verbs_seen: dict[str, list[str]] = {}

        for source in sources:
            if not source.exists():
                continue
            for lineno, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
                rel = f"{source.relative_to(_PROJECT_ROOT)}:{lineno}"
                for pattern in (
                    _BACKTICKED_INVOCATION,
                    _QUOTED_INVOCATION,
                    _STEP_DEF_FIXTURE,
                ):
                    for match in pattern.finditer(line):
                        verbs_seen.setdefault(match.group(1), []).append(rel)

        for verb, locations in sorted(verbs_seen.items()):
            if verb in _DOC_PROSE_VERBS:
                continue
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
                f"{label} cite `gz <verb>` strings that do not resolve through "
                "the CLI parser. Fix the assertion or add the verb to the CLI "
                "before landing.\n" + "\n".join(offenders)
            ),
        )


if __name__ == "__main__":
    unittest.main()
