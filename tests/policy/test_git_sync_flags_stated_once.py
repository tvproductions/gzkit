"""git-sync's flags are stated once, and no live surface restates the retired ritual (GHI #1390).

The git-sync skill states what every flag runs and which command each moment
uses (operator, 2026-11-26: *"we need to be explicit in all cases for all
combinations"*). Two retired statements must not come back:

- a ceremony or routine surface prescribing `gz git-sync --apply --lint --test`,
  where the skill assigns that moment bare `--apply`;
- the skill, its adopter copy or the sync agent calling an omitted `--lint` /
  `--test` a skipped gate ("I'll skip `--lint --test` to be quick").

Only the statement itself may show `--apply --lint --test`: the skill, its
mirrors and adopter copy, the manpage, and the CLI epilog. A dated record (a
path carrying a YYYY-MM-DD date) and a verbatim record keep their text.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LIVE_ROOTS = tuple(
    REPO / part
    for part in (
        ".gzkit/skills",
        ".gzkit/agents",
        ".gzkit/templates",
        "src/gzkit",
        "docs/user",
        "docs/developer",
        "docs/governance",
        "docs/flighttest",
        "docs/design/adr/pool",
        "features",
    )
)
THE_STATEMENT = frozenset(
    {
        ".gzkit/skills/git-sync/SKILL.md",
        "src/gzkit/skills/git-sync/SKILL.md",
        "src/gzkit/templates/skills/git-sync/SKILL.md",
        "docs/user/manpages/git-sync.md",
        "src/gzkit/cli/parser_maintenance.py",
    }
)
#: Verbatim records of another project's tooling, kept word for word by design.
VERBATIM_RECORDS = frozenset({"docs/user/reference/airlineops-exploration-verbatim.md"})
OMISSION_SURFACES = (
    ".gzkit/skills/git-sync/SKILL.md",
    "src/gzkit/templates/skills/git-sync/SKILL.md",
    ".gzkit/agents/git-sync-repo.md",
)
_RITUAL = re.compile(r"git-sync --apply --lint --test")
_OMISSION_AS_FAILURE = re.compile(r"\bskip\w*\s+`--(?:lint|test)\b", re.IGNORECASE)
_DATED = re.compile(r"\d{4}-\d{2}-\d{2}")
_SUFFIXES = frozenset({".md", ".py", ".feature", ".json", ".toml"})


def ritual_lines(text: str) -> list[int]:
    """Return the 1-based lines of *text* that prescribe `--apply --lint --test`."""
    return [n for n, line in enumerate(text.splitlines(), 1) if _RITUAL.search(line)]


def omission_lines(text: str) -> list[int]:
    """Return the 1-based lines of *text* that call skipping `--lint`/`--test` a lapse."""
    return [n for n, line in enumerate(text.splitlines(), 1) if _OMISSION_AS_FAILURE.search(line)]


def _live_files() -> list[Path]:
    files: list[Path] = []
    for root in LIVE_ROOTS:
        for path in sorted(root.rglob("*")):
            rel = path.relative_to(REPO).as_posix()
            if path.suffix in _SUFFIXES and path.is_file() and not _DATED.search(rel):
                files.append(path)
    return files


def _restating_surfaces() -> list[str]:
    found: list[str] = []
    for path in _live_files():
        rel = path.relative_to(REPO).as_posix()
        if rel in THE_STATEMENT or rel in VERBATIM_RECORDS:
            continue
        found.extend(f"{rel}:{n}" for n in ritual_lines(path.read_text(encoding="utf-8")))
    return found


def _omission_claims() -> list[str]:
    found: list[str] = []
    for rel in OMISSION_SURFACES:
        text = (REPO / rel).read_text(encoding="utf-8")
        found.extend(f"{rel}:{n}" for n in omission_lines(text))
    return found


def _missing_roots() -> list[str]:
    return [root.relative_to(REPO).as_posix() for root in LIVE_ROOTS if not root.is_dir()]


class TestGitSyncFlagsStatedOnce(unittest.TestCase):
    def test_the_fence_roots_are_where_it_reads(self) -> None:
        self.assertEqual(_missing_roots(), [], "a fence root moved; update LIVE_ROOTS")

    def test_no_live_surface_prescribes_the_retired_ritual(self) -> None:
        offenders = _restating_surfaces()
        self.assertEqual(
            offenders,
            [],
            "use the command the git-sync skill's § Which command each moment uses "
            "names for this moment: " + ", ".join(offenders),
        )

    def test_no_surface_calls_an_omitted_flag_a_skipped_gate(self) -> None:
        offenders = _omission_claims()
        self.assertEqual(
            offenders,
            [],
            "--lint and --test default off and no moment requires them "
            "(git-sync skill § Which command each moment uses): " + ", ".join(offenders),
        )


class TestTheFenceCanFail(unittest.TestCase):
    """Negative controls: each detector fires on the text that actually shipped."""

    def test_ritual_detector_fires_on_the_retired_runbook_step(self) -> None:
        shipped = "# 6) Run guarded sync\nuv run gz git-sync --apply --lint --test\n"
        self.assertEqual(ritual_lines(shipped), [2])

    def test_ritual_detector_passes_the_routine_command(self) -> None:
        self.assertEqual(ritual_lines("uv run gz git-sync --apply\n"), [])

    def test_omission_detector_fires_on_both_retired_rows(self) -> None:
        shipped = (
            '| "I\'ll skip `--lint --test` to be quick" | The bare `--apply` exists |\n'
            "| Skipping them is the same anti-pattern as skipping `--lint --test`. |\n"
        )
        self.assertEqual(omission_lines(shipped), [1, 2])

    def test_omission_detector_passes_the_current_statement(self) -> None:
        current = "No moment requires `--lint` or `--test`, and leaving them off is fine.\n"
        self.assertEqual(omission_lines(current), [])


if __name__ == "__main__":
    unittest.main()
