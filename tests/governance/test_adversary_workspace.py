"""The Step-4b adversary's disposable writable checkout and replay bar (GHI #961).

Two claims are under test, and they are different claims:

* the checkout REPRODUCES the reviewed source (uncommitted changes included)
  and ISOLATES the active tree from anything the reviewer does to it; and
* a claimed replay is credited only when it actually replayed -- a green
  baseline, an assertion-class kill, a byte-identical restore, a green restored
  run. An execution error, a skipped selector, or an inspected record is
  refused by name.

The second half is the half that matters for the gate. Enabling execution does
not establish that execution happened, and #961's own history is the argument:
its first close asserted a mechanism beyond what the observation supported, and
only running the thing surfaced it.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.adversary_workspace import (
    ReplayRecord,
    ReplayRun,
    materialize_adversary_workspace,
    remove_adversary_workspace,
    validate_replay_records,
)
from tests.commands.common import _isolated_git_env

_ASSERTION_TAIL = """\
FAIL: test_guard_refuses (tests.test_guard.TestGuard.test_guard_refuses)
----------------------------------------------------------------------
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
"""

_ERROR_TAIL = """\
ERROR: test_guard_refuses (tests.test_guard.TestGuard.test_guard_refuses)
----------------------------------------------------------------------
ImportError: cannot import name 'refuse' from 'pkg.guard'

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
"""

_DIGEST_A = "a" * 64
_DIGEST_B = "b" * 64
_WORKSPACE = "w" * 64


def _seed_repository(root: Path) -> None:
    """A minimal committed repo with one tracked file, plus an uncommitted edit."""
    env = _isolated_git_env()
    for args in (
        ["init", "-q"],
        ["config", "user.email", "g0@users.noreply.github.com"],
        ["config", "user.name", "g0"],
    ):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=env)
    (root / "src").mkdir()
    (root / "src" / "guard.py").write_text("LIMIT = 1\n", encoding="utf-8")
    (root / "committed.txt").write_text("committed\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True, env=env)
    subprocess.run(
        ["git", "commit", "-q", "-m", "seed"], cwd=root, check=True, capture_output=True, env=env
    )
    # The reviewed source is the WORKING TREE, not the last commit.
    (root / "src" / "guard.py").write_text("LIMIT = 2\n", encoding="utf-8")


def _valid_record(**overrides: object) -> ReplayRecord:
    fields: dict[str, object] = {
        "obligation_id": "REQ-0.1.0-01-01",
        "proof_id": "proof-abc",
        "workspace_digest": _WORKSPACE,
        "selectors": ("tests.test_guard.TestGuard.test_guard_refuses",),
        "mutation_label": "disable-the-guard",
        "baseline": ReplayRun(exit_status=0, tests_run=1, output_tail="OK"),
        "mutated": ReplayRun(exit_status=1, tests_run=1, output_tail=_ASSERTION_TAIL),
        "restored": ReplayRun(exit_status=0, tests_run=1, output_tail="OK"),
        "source_digest_before": _DIGEST_A,
        "source_digest_after": _DIGEST_A,
    }
    fields.update(overrides)
    return ReplayRecord(**fields)


class TestWorkspaceReproducesReviewedSource(unittest.TestCase):
    """The checkout is the reviewed source, uncommitted changes included."""

    def test_uncommitted_changes_reach_the_disposable_checkout(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            _seed_repository(root)
            destination = Path(tmp) / "ws"

            workspace = materialize_adversary_workspace(root, destination)

            # The committed value is 1; the reviewed working tree says 2. A checkout
            # carrying HEAD alone hands the reviewer source nobody reviewed.
            self.assertEqual(
                (destination / "src" / "guard.py").read_text(encoding="utf-8"),
                "LIMIT = 2\n",
            )
            self.assertTrue(workspace.dirty)
            self.assertEqual(
                (destination / "committed.txt").read_text(encoding="utf-8"),
                "committed\n",
            )

    def test_mutating_the_checkout_leaves_the_active_tree_untouched(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            _seed_repository(root)
            destination = Path(tmp) / "ws"
            workspace = materialize_adversary_workspace(root, destination)

            (destination / "src" / "guard.py").write_text("LIMIT = 999\n", encoding="utf-8")

            self.assertEqual(
                (root / "src" / "guard.py").read_text(encoding="utf-8"),
                "LIMIT = 2\n",
                "a review mutation reached the active checkout",
            )
            remove_adversary_workspace(workspace)
            self.assertFalse(destination.exists())


class TestValidReplayIsCredited(unittest.TestCase):
    """The positive case: a real replay is accepted, so the bar is reachable."""

    def test_complete_replay_produces_no_rejection(self) -> None:
        reasons = validate_replay_records(
            [_valid_record()],
            workspace_digest=_WORKSPACE,
            expected_obligations=["REQ-0.1.0-01-01"],
        )
        self.assertEqual(reasons, [])


class TestInadequateEvidenceIsRefused(unittest.TestCase):
    """Each rejection names a distinct way a non-replay could be read as one."""

    def test_an_error_class_failure_is_not_an_expected_assertion_failure(self) -> None:
        mutated = ReplayRun(exit_status=1, tests_run=1, output_tail=_ERROR_TAIL)
        reasons = validate_replay_records(
            [_valid_record(mutated=mutated)], workspace_digest=_WORKSPACE
        )
        self.assertTrue(
            any("failure_class='error'" in reason for reason in reasons),
            f"an ImportError was credited as a kill: {reasons}",
        )

    def test_a_substitution_that_never_failed_is_refused(self) -> None:
        mutated = ReplayRun(exit_status=0, tests_run=1, output_tail="OK")
        reasons = validate_replay_records(
            [_valid_record(mutated=mutated)], workspace_digest=_WORKSPACE
        )
        self.assertTrue(
            any("failure_class='none'" in reason for reason in reasons),
            f"a test that passed under mutation was credited: {reasons}",
        )

    def test_a_skipped_selector_is_refused(self) -> None:
        baseline = ReplayRun(exit_status=0, tests_run=0, output_tail="OK")
        reasons = validate_replay_records(
            [_valid_record(baseline=baseline)], workspace_digest=_WORKSPACE
        )
        self.assertTrue(
            any("selector was skipped" in reason for reason in reasons),
            f"a run that executed zero tests was credited: {reasons}",
        )

    def test_an_inspected_record_without_a_substitution_is_refused(self) -> None:
        reasons = validate_replay_records(
            [_valid_record(mutation_label="   ")], workspace_digest=_WORKSPACE
        )
        self.assertTrue(
            any("no substitution" in reason for reason in reasons),
            f"an inspection was credited as a replay: {reasons}",
        )

    def test_an_unrestored_source_is_refused(self) -> None:
        reasons = validate_replay_records(
            [_valid_record(source_digest_after=_DIGEST_B)], workspace_digest=_WORKSPACE
        )
        self.assertTrue(
            any("not restored byte-identically" in reason for reason in reasons),
            f"a workspace left mutated was credited: {reasons}",
        )

    def test_a_replay_against_another_tree_is_refused(self) -> None:
        reasons = validate_replay_records(
            [_valid_record(workspace_digest=_DIGEST_B)], workspace_digest=_WORKSPACE
        )
        self.assertTrue(
            any("another tree" in reason for reason in reasons),
            f"a replay against an unrelated tree was credited: {reasons}",
        )

    def test_a_missing_run_is_refused(self) -> None:
        reasons = validate_replay_records(
            [_valid_record(restored=None)], workspace_digest=_WORKSPACE
        )
        self.assertTrue(
            any("missing a baseline, mutated or restored run" in reason for reason in reasons),
            f"a partial replay was credited: {reasons}",
        )

    def test_an_obligation_with_no_replay_at_all_is_reported(self) -> None:
        reasons = validate_replay_records(
            [], workspace_digest=_WORKSPACE, expected_obligations=["REQ-0.1.0-01-02"]
        )
        self.assertEqual(reasons, ["REQ-0.1.0-01-02: no independent replay record"])


if __name__ == "__main__":
    unittest.main()
