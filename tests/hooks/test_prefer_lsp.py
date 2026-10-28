"""Prefer-LSP hook: which searches it routes to the LSP tool (GHI #1286).

The hook's contract (`src/gzkit/hooks/scripts/lsp.py`): the first text search
for a Python symbol over Python files in a session is denied with a pointer to
the ty-backed LSP tool, and repeating the same search lets it through. These
cases derive from that contract and from the GHI #1286 closure contract: a
search is a search wherever it sits in the command line, and plain words, data
keys and filenames are not Python symbols.
"""

import io
import json
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from gzkit.hooks.scripts.lsp import _prefer_lsp_script


def _load_hook() -> types.ModuleType:
    module = types.ModuleType("prefer_lsp_hook")
    exec(compile(_prefer_lsp_script(), "prefer-lsp.py", "exec"), module.__dict__)  # noqa: S102
    return module


class _HookCase(unittest.TestCase):
    def setUp(self) -> None:
        self.hook = _load_hook()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        seen_dir = Path(self._tmp.name)
        patcher = mock.patch.object(
            self.hook, "seen_file", lambda session_id: seen_dir / f"{session_id}.json"
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def decide(
        self, tool_input: dict, tool_name: str = "Bash", session_id: str = "s1"
    ) -> dict | None:
        """Run the hook once.

        Returns:
            Its deny decision, or None when it allows the call.

        """
        payload = {"tool_name": tool_name, "session_id": session_id, "tool_input": tool_input}
        stdout = io.StringIO()
        with (
            mock.patch.object(self.hook.sys, "stdin", io.StringIO(json.dumps(payload))),
            mock.patch.object(self.hook.sys, "stdout", stdout),
            self.assertRaises(SystemExit) as exit_info,
        ):
            self.hook.main()
        self.assertEqual(exit_info.exception.code, 0)
        text = stdout.getvalue().strip()
        return json.loads(text)["hookSpecificOutput"] if text else None

    def denied(self, command: str, session_id: str = "s1") -> bool:
        decision = self.decide({"command": command}, session_id=session_id)
        return decision is not None and decision["permissionDecision"] == "deny"


class TestSearchesAnywhereInTheCommandLine(_HookCase):
    def test_a_search_in_any_position_is_routed(self) -> None:
        commands = (
            "grep -rn AdvisorDiagnosis .",
            "cd /repo && grep -rn AdvisorDiagnosis .",
            "git status; rg AdvisorDiagnosis src",
            "git log -1 || grep -rn AdvisorDiagnosis src",
            "echo $(grep -rn AdvisorDiagnosis .)",
            "echo `grep -rn AdvisorDiagnosis .`",
            "FOO=1 grep -rn AdvisorDiagnosis .",
            "git status\ngit grep AdvisorDiagnosis",
        )
        for index, command in enumerate(commands):
            with self.subTest(command=command):
                self.assertTrue(self.denied(command, session_id=f"position-{index}"))

    def test_a_search_word_inside_quoted_data_is_not_a_command(self) -> None:
        self.assertFalse(self.denied('echo "grep -rn AdvisorDiagnosis ."'))

    def test_a_heredoc_body_is_not_scanned_as_commands(self) -> None:
        command = "cat > notes.md <<'EOF'\ngrep -rn AdvisorDiagnosis .\nEOF"
        self.assertFalse(self.denied(command))

    def test_a_quoted_alternation_does_not_split_the_command(self) -> None:
        self.assertFalse(self.denied('grep -rnE "AdvisorDiagnosis|Verdict" src'))

    def test_repeating_the_same_search_lets_it_through(self) -> None:
        command = "cd /repo && grep -rn AdvisorDiagnosis ."
        self.assertTrue(self.denied(command))
        self.assertFalse(self.denied(command))


class TestWhatCountsAsAPythonSymbol(_HookCase):
    def test_python_names_are_symbols(self) -> None:
        for pattern in (
            "advisor_diagnosis",
            "_plain",
            "__init__",
            "CANONICAL_STEP_COMMANDS",
            "AdvisorDiagnosis",
            "gzkit.hooks.claude",
            "def deny",
            "class Verdict",
            r"\bAdvisorDiagnosis\b",
        ):
            with self.subTest(pattern=pattern):
                self.assertIsNotNone(self.hook.symbol_of(pattern))

    def test_words_keys_and_filenames_are_not_symbols(self) -> None:
        for pattern in (
            "agents",
            "maxTurns",
            "TODO",
            "settings.json",
            "prefer_lsp.py",
            "README.md",
            "Foo|Bar",
        ):
            with self.subTest(pattern=pattern):
                self.assertIsNone(self.hook.symbol_of(pattern))

    def test_a_plain_word_search_runs_first_time(self) -> None:
        self.assertFalse(self.denied("grep -rn 'agents' src/gzkit/sync_surfaces.py"))
        self.assertFalse(self.denied("grep -rln 'maxTurns' src/gzkit data .gzkit"))


class TestNonPythonSearchesPass(_HookCase):
    def test_a_search_filtered_to_other_files_runs(self) -> None:
        self.assertFalse(self.denied("grep -rn AdvisorDiagnosis --include=*.md docs"))
        self.assertIsNone(
            self.decide({"pattern": "AdvisorDiagnosis", "glob": "*.md"}, tool_name="Grep")
        )

    def test_the_grep_tool_over_python_is_routed(self) -> None:
        decision = self.decide({"pattern": "AdvisorDiagnosis", "type": "py"}, tool_name="Grep")
        self.assertIsNotNone(decision)


class TestDenyProseRendering(_HookCase):
    """The refusal carries what failed, why, and the next step.

    # output-contract: the deny reason is the hook's agent-facing contract
    # (`.claude/rules/guardrail-feedback-prose.md`).
    """

    def test_the_reason_names_symbol_rule_and_recovery(self) -> None:
        decision = self.decide({"command": "grep -rn AdvisorDiagnosis ."})
        if decision is None:
            self.fail("a symbol search over Python files was not denied")
        reason = decision["permissionDecisionReason"]
        self.assertIn("'AdvisorDiagnosis'", reason)
        self.assertIn("CLAUDE.md", reason)
        self.assertIn("workspaceSymbol", reason)
        self.assertIn("server is starting", reason)
        self.assertIn("repeat the same", reason)


if __name__ == "__main__":
    unittest.main()
