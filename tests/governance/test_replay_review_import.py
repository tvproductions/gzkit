"""Dispatch-to-import: a replay claim survives ingestion only if it replayed (GHI #961).

`test_adversary_workspace.py` tests the predicate. This tests the PATH: an ARB
receipt carrying a `gzkit.acceptance.review.v1` object with a `replay` block,
read by the same `review_from_receipt` the acceptance CLI calls.

The distinction matters because the predicate being correct proves nothing about
whether anything consults it. Before this fixture existed the reviewer's replay
evidence had no reader at all, so a claim could be authored, transported, and
recorded without ever being checked.

The receipts here name `codex-companion.mjs` under `node` because that is the
mandated tier-1 argv (`data/mandated_tier1_dispatch.json`), and its `task
--write --cwd <disposable checkout>` form is what makes replay possible at all.
"""

from __future__ import annotations

import json
import unittest

from gzkit.acceptance_store import review_from_receipt

_COMPANION = "/plugins/openai-codex/scripts/codex-companion.mjs"
_WORKSPACE = "w" * 64
_DIGEST = "a" * 64

_ASSERTION_TAIL = (
    "FAIL: test_guard_refuses (tests.test_guard.TestGuard.test_guard_refuses)\n"
    "AssertionError: ValueError not raised\n\n"
    "Ran 1 test in 0.002s\n\nFAILED (failures=1)\n"
)
_ERROR_TAIL = (
    "ERROR: test_guard_refuses (tests.test_guard.TestGuard.test_guard_refuses)\n"
    "ImportError: cannot import name 'refuse'\n\n"
    "Ran 1 test in 0.001s\n\nFAILED (errors=1)\n"
)


def _replay(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "obligation_id": "REQ-0.1.0-01-01",
        "proof_id": "proof-abc",
        "workspace_digest": _WORKSPACE,
        "selectors": ["tests.test_guard.TestGuard.test_guard_refuses"],
        "mutation_label": "disable-the-guard",
        "baseline": {"exit_status": 0, "tests_run": 1, "output_tail": "OK"},
        "mutated": {"exit_status": 1, "tests_run": 1, "output_tail": _ASSERTION_TAIL},
        "restored": {"exit_status": 0, "tests_run": 1, "output_tail": "OK"},
        "source_digest_before": _DIGEST,
        "source_digest_after": _DIGEST,
    }
    record.update(overrides)
    return record


def _receipt(replay: list[dict[str, object]]) -> dict[str, object]:
    """An ARB receipt whose captured output carries the reviewer's review object."""
    review = {
        "schema": "gzkit.acceptance.review.v1",
        "stage": "adversarial",
        "input_digest": "e7e5788",
        "obligation_ids": ["REQ-0.1.0-01-01"],
        "proof_ids": ["proof-abc"],
        "accepted_proof_ids": ["proof-abc"],
        "findings": [],
        "closures": [],
        "reviewer_id": "codex-adversary",
        "verdict": "accepted",
        "replay": replay,
    }
    return {
        "schema": "gzkit.arb.step_receipt.v1",
        "exit_status": 0,
        "run_id": "arb-step-codexadversary-deadbeef",
        "stdout_tail": json.dumps(review),
        "stderr_tail": "",
        "step": {
            "command": [
                "node",
                _COMPANION,
                "task",
                "--write",
                "--cwd",
                "/tmp/adversary-workspace",
                "--prompt-file",
                "/tmp/prompt.md",
            ]
        },
    }


class TestWritableDispatchStillProvesTierOne(unittest.TestCase):
    """The writable path must not cost the cross-vendor property Step 4b requires."""

    def test_task_write_dispatch_imports_as_tier_1(self) -> None:
        review = review_from_receipt(_receipt([_replay()]))

        self.assertEqual(review.tier, 1)
        self.assertEqual(review.receipt_id, "arb-step-codexadversary-deadbeef")


class TestValidReplayIsIngested(unittest.TestCase):
    """A genuine replay reaches the ledger with its observations intact."""

    def test_a_replayed_review_is_imported_and_retains_its_record(self) -> None:
        review = review_from_receipt(_receipt([_replay()]))

        self.assertEqual(len(review.replay), 1)
        self.assertEqual(review.replay[0].obligation_id, "REQ-0.1.0-01-01")
        self.assertEqual(review.replay[0].mutation_label, "disable-the-guard")


class TestInadequateReplayIsRefusedAtImport(unittest.TestCase):
    """Ingestion is where a hollow replay claim has to die."""

    def _assert_refused(self, replay: list[dict[str, object]], expected: str) -> None:
        with self.assertRaises(ValueError) as caught:
            review_from_receipt(_receipt(replay))
        self.assertIn(expected, str(caught.exception))

    def test_an_execution_error_is_not_ingested_as_replay(self) -> None:
        mutated = {"exit_status": 1, "tests_run": 1, "output_tail": _ERROR_TAIL}
        self._assert_refused([_replay(mutated=mutated)], "failure_class='error'")

    def test_a_skipped_selector_is_not_ingested_as_replay(self) -> None:
        baseline = {"exit_status": 0, "tests_run": 0, "output_tail": "OK"}
        self._assert_refused([_replay(baseline=baseline)], "selector was skipped")

    def test_an_inspected_record_is_not_ingested_as_replay(self) -> None:
        self._assert_refused([_replay(mutation_label="")], "no substitution")

    def test_an_unrestored_workspace_is_not_ingested_as_replay(self) -> None:
        self._assert_refused([_replay(source_digest_after="b" * 64)], "not restored")


class TestAbsentReplayClaimsNothing(unittest.TestCase):
    """Silence is honest; only a CLAIM is checked."""

    def test_a_review_without_a_replay_block_still_imports(self) -> None:
        review = review_from_receipt(_receipt([]))

        self.assertEqual(review.replay, ())
        self.assertEqual(review.tier, 1)


if __name__ == "__main__":
    unittest.main()
