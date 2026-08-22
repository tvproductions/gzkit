"""The ledger must see a governance edit whatever tool wrote it (GHI #847).

``.claude/hooks/ledger-writer.py`` is a PostToolUse hook bound to ``Edit|Write``
and keyed on ``tool_input.file_path`` -- a field a Bash payload does not carry.
Measured 2026-08-21 across the three sessions that implemented OBPI-0.35.0-09:
3h38m between ``pipeline_launched`` and ``brief_reconciled`` carrying zero
``artifact_edited`` rows, and exactly one such row in the entire day. The
consumer that goes blind is
``gzkit.governance.trust_audits.orphaned_implementation``, which reads
``(ts, path)`` pairs to detect implementation outside an OBPI's allowed paths;
absence of events there is indistinguishable from absence of work.

The recorder is a BACKSTOP, never a second emitter. It fires only for a
governance artifact the tool locus did not already record since the previous
commit -- the operator's 2026-08-22 ruling, taken against a measurement:
unconditional commit-locus emission would have added 1165 rows over 60 days
(229 commits, median 1 per commit, max 197), roughly doubling the type.

These tests write artifacts with plain filesystem calls and commit them, never
through a tool the hook can see, because that is the bypass. Commit and event
timestamps are pinned explicitly rather than taken from the wall clock: the
window boundary is the semantic under test, and second-granularity commit dates
would otherwise decide it by race.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from gzkit.hooks.commit_ledger import record_committed_artifact_edits

_BRIEF = "docs/design/adr/pre-release/ADR-0.35.0-x/obpis/OBPI-0.35.0-09-playback.md"
_ADR = "docs/design/adr/pre-release/ADR-0.35.0-x/ADR-0.35.0-x.md"
_SRC = "src/gzkit/codex_playback.py"
_LEDGER = ".gzkit/ledger.jsonl"

_T0 = "2026-08-20T00:00:00+00:00"
_T1 = "2026-08-21T00:00:00+00:00"
_T2 = "2026-08-22T00:00:00+00:00"


def _git(args: list[str], cwd: Path, when: str | None = None) -> str:
    env = None
    if when is not None:
        env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return result.stdout


def _repo() -> Path:
    """A repo whose base commit predates every window under test."""
    root = Path(tempfile.mkdtemp(prefix="gzkit-847-ledger-"))
    _git(["init", "-q", "-b", "main"], root)
    _git(["config", "user.email", "g0@users.noreply.github.com"], root)
    _git(["config", "user.name", "g0"], root)
    (root / ".gzkit").mkdir()
    (root / _LEDGER).write_text("", encoding="utf-8")
    (root / "README.md").write_text("base\n", encoding="utf-8")
    _git(["add", "-A"], root, when=_T0)
    _git(["commit", "-qm", "base"], root, when=_T0)
    return root


def _write_and_commit(root: Path, rel: str, *, when: str, body: str = "changed\n") -> None:
    """The bypass: a plain filesystem write, staged and committed by no tool."""
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    _git(["add", "-A"], root, when=when)
    _git(["commit", "-qm", f"touch {rel}"], root, when=when)


def _tool_locus_event(root: Path, rel: str, ts: str) -> None:
    """Simulate what the PostToolUse hook writes when it CAN see the write."""
    row = {
        "schema": "gzkit.ledger.v1",
        "event": "artifact_edited",
        "id": rel,
        "ts": ts,
        "path": rel,
        "session": "sess-1",
    }
    with (root / _LEDGER).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, separators=(",", ":")) + "\n")


def _rows(root: Path) -> list[dict]:
    text = (root / _LEDGER).read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def _recorded_paths(root: Path) -> list[str]:
    return [r["path"] for r in _rows(root) if r.get("event") == "artifact_edited"]


class TestBypassedWritesReachTheLedger(unittest.TestCase):
    """The channel the tool locus cannot see is the one this must record."""

    def test_bash_authored_brief_is_recorded(self) -> None:
        root = _repo()
        _write_and_commit(root, _BRIEF, when=_T1)
        emitted = record_committed_artifact_edits(root)
        self.assertEqual(
            emitted,
            [_BRIEF],
            "a governance brief written by sed/heredoc/inline-python reaches the "
            "commit having emitted nothing; the commit is the locus that sees it",
        )
        self.assertIn(_BRIEF, _recorded_paths(root))

    def test_recorded_event_names_the_commit_it_observed(self) -> None:
        root = _repo()
        _write_and_commit(root, _BRIEF, when=_T1)
        record_committed_artifact_edits(root)
        head = _git(["rev-parse", "HEAD"], root).strip()
        row = next(r for r in _rows(root) if r.get("event") == "artifact_edited")
        self.assertEqual(
            row.get("commit"),
            head,
            "AGENTS.md DO IT RIGHT requires a gate to name the STATE it observes; "
            "the state here is a durable commit, not that some tool ran",
        )

    def test_several_governance_artifacts_in_one_commit_each_get_a_row(self) -> None:
        root = _repo()
        (root / _BRIEF).parent.mkdir(parents=True, exist_ok=True)
        (root / _BRIEF).write_text("brief\n", encoding="utf-8")
        (root / _ADR).write_text("adr\n", encoding="utf-8")
        _git(["add", "-A"], root, when=_T1)
        _git(["commit", "-qm", "two artifacts"], root, when=_T1)
        self.assertEqual(
            sorted(record_committed_artifact_edits(root)),
            sorted([_ADR, _BRIEF]),
            "the unit is the artifact, not the commit -- orphaned-implementation "
            "reads (ts, path) pairs and cannot split a bundled row",
        )


class TestBackstopStaysSilentWhenTheToolLocusSaw(unittest.TestCase):
    """Dedup is the operator's ruling: fire on bypass, never duplicate."""

    def test_edit_already_recorded_in_this_window_is_not_re_recorded(self) -> None:
        root = _repo()
        _tool_locus_event(root, _BRIEF, ts=_T1)
        _write_and_commit(root, _BRIEF, when=_T2)
        self.assertEqual(
            record_committed_artifact_edits(root),
            [],
            "an Edit/Write-authored change already has its row; a second one would "
            "inflate a type another validator counts",
        )
        self.assertEqual(len(_recorded_paths(root)), 1)

    def test_a_row_from_before_the_window_does_not_suppress_this_commit(self) -> None:
        root = _repo()
        _tool_locus_event(root, _BRIEF, ts=_T0)
        _write_and_commit(root, _BRIEF, when=_T1)
        _write_and_commit(root, _BRIEF, when=_T2, body="second change\n")
        self.assertEqual(
            record_committed_artifact_edits(root),
            [_BRIEF],
            "the window is the parent commit, not all of history; suppressing on any "
            "prior row would blind the recorder to every later edit of that file",
        )

    def test_dedup_is_per_path_not_per_commit(self) -> None:
        root = _repo()
        _tool_locus_event(root, _ADR, ts=_T2)
        (root / _BRIEF).parent.mkdir(parents=True, exist_ok=True)
        (root / _BRIEF).write_text("brief\n", encoding="utf-8")
        (root / _ADR).write_text("adr\n", encoding="utf-8")
        _git(["add", "-A"], root, when=_T2)
        _git(["commit", "-qm", "mixed"], root, when=_T2)
        self.assertEqual(
            record_committed_artifact_edits(root),
            [_BRIEF],
            "one recorded sibling must not vouch for an unrecorded one",
        )


class TestScopeMatchesTheToolLocusItBacksUp(unittest.TestCase):
    """A backstop that recorded more than its principal would not be a backstop."""

    def test_production_source_is_never_recorded(self) -> None:
        root = _repo()
        _write_and_commit(root, _SRC, when=_T1)
        self.assertEqual(
            record_committed_artifact_edits(root),
            [],
            "is_governance_artifact scopes this type to governance markdown; widening "
            "it here would make the commit locus emit what the tool locus never did",
        )

    def test_deleting_a_governance_artifact_is_not_an_edit(self) -> None:
        root = _repo()
        _write_and_commit(root, _BRIEF, when=_T1)
        (root / _BRIEF).unlink()
        _git(["add", "-A"], root, when=_T2)
        _git(["commit", "-qm", "remove"], root, when=_T2)
        self.assertEqual(
            record_committed_artifact_edits(root),
            [],
            "the PostToolUse principal fires on Edit|Write and cannot observe a "
            "deletion; a backstop that did would be recording a different claim",
        )


class TestRecorderNeverObstructsACommit(unittest.TestCase):
    """It runs after the commit exists and has nothing to gate."""

    def test_missing_ledger_is_a_no_op_not_an_error(self) -> None:
        root = _repo()
        (root / _LEDGER).unlink()
        _write_and_commit(root, _BRIEF, when=_T1)
        self.assertEqual(
            record_committed_artifact_edits(root),
            [],
            "a project without a ledger is not a project this recorder may fail",
        )

    def test_root_commit_has_no_parent_window_and_still_records(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="gzkit-847-root-"))
        _git(["init", "-q", "-b", "main"], root)
        _git(["config", "user.email", "g0@users.noreply.github.com"], root)
        _git(["config", "user.name", "g0"], root)
        (root / ".gzkit").mkdir()
        (root / _LEDGER).write_text("", encoding="utf-8")
        _write_and_commit(root, _BRIEF, when=_T1)
        self.assertEqual(
            record_committed_artifact_edits(root),
            [_BRIEF],
            "the first commit of a repository has no parent to bound the window; "
            "treating that as an error would silently skip it",
        )

    def test_commit_touching_no_governance_artifact_writes_nothing(self) -> None:
        root = _repo()
        _write_and_commit(root, "README.md", when=_T1, body="edited\n")
        before = len(_rows(root))
        self.assertEqual(record_committed_artifact_edits(root), [])
        self.assertEqual(len(_rows(root)), before)


if __name__ == "__main__":
    unittest.main()
