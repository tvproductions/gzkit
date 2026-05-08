"""Unit tests for the ghi-triage chat-silence backstop hook (GHI #424).

The hook is the structural backstop on the chat-text surface: when a Bash
command invokes ``triage.py --format rank``, the assistant's most recent
turn is scanned for the prose-preamble shape (multiple GHI numbers each
near a severity token) that duplicates the rank renderer's deliverable
into chat. Tests pin the detection rule and the no-op paths so a future
edit cannot silently regress either side.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_HOOK_PATH = (
    Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "ghi-triage-chat-silence.py"
)


def _load_hook_module():
    spec = importlib.util.spec_from_file_location("ghi_triage_chat_silence_hook", _HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_HOOK = _load_hook_module()


def _write_transcript(tmpdir: Path, assistant_text: str) -> Path:
    transcript = tmpdir / "session.jsonl"
    line = json.dumps(
        {
            "type": "assistant",
            "message": {"content": [{"type": "text", "text": assistant_text}]},
        }
    )
    transcript.write_text(line + "\n", encoding="utf-8")
    return transcript


def _run_hook(tool_input: dict, transcript_path: Path) -> tuple[int, str]:
    payload = {
        "tool_name": "Bash",
        "tool_input": tool_input,
        "transcript_path": str(transcript_path),
    }
    stdin_buf = io.StringIO(json.dumps(payload))
    stderr_buf = io.StringIO()
    with patch.object(sys, "stdin", stdin_buf), patch.object(sys, "stderr", stderr_buf):
        rc = _HOOK.main()
    return rc, stderr_buf.getvalue()


class TestFindViolationPairs(unittest.TestCase):
    """Pin the proximity rule that powers the hook's detection."""

    def test_two_ghis_near_severity_flags(self) -> None:
        text = "#419 brief drift is degrading. #418 manpages split is degrading too."
        pairs = _HOOK.find_violation_pairs(text)
        self.assertEqual(len(pairs), 2)

    def test_single_ghi_near_severity_does_not_flag(self) -> None:
        text = "Reopened #424 because it was blocking the pipeline."
        pairs = _HOOK.find_violation_pairs(text)
        self.assertEqual(len(pairs), 1)

    def test_ghi_far_from_severity_does_not_flag(self) -> None:
        text = "#100 something benign here.\n" + "x" * 500 + "\nseverity blocking later"
        pairs = _HOOK.find_violation_pairs(text)
        self.assertEqual(pairs, [])

    def test_severity_match_is_case_insensitive(self) -> None:
        text = "#419 BLOCKING. #418 Latent."
        pairs = _HOOK.find_violation_pairs(text)
        self.assertEqual(len(pairs), 2)

    def test_repeated_same_ghi_counts_once(self) -> None:
        text = "#419 blocking. #419 blocking again. #419 still blocking."
        pairs = _HOOK.find_violation_pairs(text)
        self.assertEqual(len(pairs), 1)


class TestHookGating(unittest.TestCase):
    """Hook only fires for the precise tool + command shape it guards."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp = Path(self._tmpdir.name)

    def test_non_bash_tool_passes(self) -> None:
        transcript = _write_transcript(self.tmp, "#419 blocking. #418 degrading.")
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": "x", "old_string": "a", "new_string": "b"},
            "transcript_path": str(transcript),
        }
        with patch.object(sys, "stdin", io.StringIO(json.dumps(payload))):
            rc = _HOOK.main()
        self.assertEqual(rc, 0)

    def test_bash_without_triage_rank_passes(self) -> None:
        transcript = _write_transcript(self.tmp, "#419 blocking. #418 degrading.")
        rc, _err = _run_hook({"command": "ls -la"}, transcript)
        self.assertEqual(rc, 0)

    def test_triage_other_format_passes(self) -> None:
        transcript = _write_transcript(self.tmp, "#419 blocking. #418 degrading.")
        rc, _err = _run_hook({"command": "uv run python triage.py --format json"}, transcript)
        self.assertEqual(rc, 0)

    def test_triage_rank_with_violation_blocks(self) -> None:
        transcript = _write_transcript(
            self.tmp,
            "Step 2 complete. Reading bodies now.\n"
            "- #419 (brief path drift): degrading.\n"
            "- #418 (manpages split): degrading.\n"
            "- #409 (model selection): latent.\n",
        )
        rc, err = _run_hook(
            {
                "command": (
                    "uv run python triage.py --format rank "
                    "--rank-input .gzkit/cache/triage/rank.json"
                )
            },
            transcript,
        )
        self.assertEqual(rc, 2)
        self.assertIn("GHI #424", err)
        self.assertIn("chat-silence", err)

    def test_triage_rank_without_violation_passes(self) -> None:
        transcript = _write_transcript(
            self.tmp,
            "Step 2 complete. Wrote rank input to cache.",
        )
        rc, _err = _run_hook(
            {
                "command": (
                    "uv run python triage.py --format rank "
                    "--rank-input .gzkit/cache/triage/rank.json"
                )
            },
            transcript,
        )
        self.assertEqual(rc, 0)

    def test_missing_transcript_path_passes_silently(self) -> None:
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "triage.py --format rank --rank-input p"},
        }
        with patch.object(sys, "stdin", io.StringIO(json.dumps(payload))):
            rc = _HOOK.main()
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
