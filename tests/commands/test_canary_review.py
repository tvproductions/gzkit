"""``gz canary review`` books the operator's review as the canary's witness (GHI #1161).

Before this verb, a review was recorded by hand-editing ``reviewed_by`` in
``data/guard_canaries.json``: no Layer-2 record carried the operator's words, and the field
could not tell an operator's review from an agent's. These tests drive the verb end to end:
the event it writes, and the refusals that must write nothing.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit import guard_canary as gc
from gzkit.cli import main
from tests.commands.common import CliRunner, _quick_init

_GUARD = "gzkit.guard_canary:binding_hash"
_CLAIM = "tidy-clean-exits-zero"
_TEST = "tests.governance.test_guard_canaries.TestBindingHash.test_the_hash_is_stable"


def _seed(binding: str | None = None) -> str:
    source, _ = gc.resolve_guard(_GUARD) or ("", Path())
    current = gc.binding_hash(source, _CLAIM, _TEST)
    canary = {
        "claim_id": _CLAIM,
        "guard": _GUARD,
        "failing_test": _TEST,
        "mutation": {"find": "payload", "replace": "data", "label": "m"},
        "binding_sha256": binding or current,
        "authority": "test",
        "reviewed_by": None,
    }
    Path("data").mkdir(exist_ok=True)
    Path("data/guard_canaries.json").write_text(
        json.dumps({"canaries": [canary]}), encoding="utf-8"
    )
    return current


def _reviews() -> list[dict]:
    rows = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8").splitlines()
    return [r for r in map(json.loads, rows) if r["event"] == "guard_canary_reviewed"]


class TestCanaryReviewCommand(unittest.TestCase):
    def _review(self, *extra: str):
        return CliRunner().invoke(
            main,
            ["canary", "review", "--claim", _CLAIM, "--attestor", "g0", *extra],
        )

    def test_a_review_books_the_verbatim_words_at_the_current_binding(self) -> None:
        with CliRunner().isolated_filesystem():
            _quick_init()
            binding = _seed()
            result = self._review("--operator-text", "accept all 8", "--json")
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(json.loads(result.output)["claims"], [_CLAIM])
            [row] = _reviews()
            self.assertEqual(
                (row["id"], row["binding_sha256"], row["operator_text"], row["attestor"]),
                (_CLAIM, binding, "accept all 8", "g0"),
            )
            self.assertEqual(gc.unreviewed(Path.cwd()), [])

    def test_a_stale_binding_exits_3_and_writes_nothing(self) -> None:
        with CliRunner().isolated_filesystem():
            _quick_init()
            _seed(binding="e" * 64)
            result = self._review("--operator-text", "accept")
            self.assertEqual(result.exit_code, 3, msg=result.output)
            self.assertEqual(_reviews(), [])

    def test_an_unknown_claim_exits_1_and_writes_nothing(self) -> None:
        with CliRunner().isolated_filesystem():
            _quick_init()
            _seed()
            result = CliRunner().invoke(
                main,
                [
                    "canary",
                    "review",
                    "--claim",
                    "no-such-claim",
                    "--attestor",
                    "g0",
                    "--operator-text",
                    "accept",
                ],
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertEqual(_reviews(), [])

    def test_the_operator_text_is_required(self) -> None:
        with CliRunner().isolated_filesystem():
            _quick_init()
            _seed()
            result = self._review()
            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertEqual(_reviews(), [])


if __name__ == "__main__":
    unittest.main()
