"""Unit tests for gzkit.brief_commands (OBPI-0.0.63-02 / BI-1).

These assert the *semantics* the parent ADR Decision items demand, not the
shape of any one implementation:

- Decision #2 / GHI #539: a multi-line fenced construct extracts as ONE logical
  command, never one-per-physical-line.
- BI-1 / GHI #550: a single shared classifier names what is shell-less-executable
  under the ``shell=False`` runtime (no ``&&``/``|``/``;``/``$()``/redirects as
  shell syntax) — operators *inside a quoted arg* are data, not syntax.
- Decision #2 / GHI #540: re-executing a demo binds a receipt to the *observed*
  exit code + a SHA-256 of observed stdout, and flags an exit-shape mismatch.
- Decision #3: a multi-line command is carried as a single quoted argv element,
  not split on newline.

Per ``.gzkit/rules/tests.md`` § Unit-tier contract, the subprocess boundary in
``reexecute_demo`` is mocked — real-subprocess execution is a behave concern.
"""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path
from unittest import mock

from gzkit.brief_commands import (
    command_argv,
    extract_fenced_commands,
    is_shell_less_executable,
    reexecute_demo,
)
from gzkit.quality import QualityResult
from gzkit.traceability import covers

_FIXTURE = Path(__file__).parent / "fixtures" / "ceremony_demos" / "multiline_demo.md"


def _demo_section(text: str) -> str:
    """Return the ``## Demo`` section body of a brief-shaped markdown string."""
    return text.split("## Demo", 1)[1]


class TestExtractFencedCommands(unittest.TestCase):
    @covers("REQ-0.0.63-02-01")
    def test_multiline_python_dash_c_is_one_command(self) -> None:
        section = _demo_section(_FIXTURE.read_text(encoding="utf-8"))
        commands = extract_fenced_commands(section)
        self.assertEqual(len(commands), 2, f"expected 2 logical commands, got {commands!r}")
        multiline = commands[1]
        self.assertIn("uv run python -c", multiline)
        self.assertIn("from pathlib import Path", multiline)
        self.assertIn("print('multi-line demo body'", multiline)

    @covers("REQ-0.0.63-02-01")
    def test_single_line_commands_stay_separate(self) -> None:
        section = "\n```bash\ngz a\ngz b\n```\n"
        self.assertEqual(extract_fenced_commands(section), ["gz a", "gz b"])

    @covers("REQ-0.0.63-02-01")
    def test_comment_and_blank_lines_skipped_at_command_start(self) -> None:
        section = "\n```bash\n# a comment\n\ngz real\n```\n"
        self.assertEqual(extract_fenced_commands(section), ["gz real"])

    @covers("REQ-0.0.63-02-01")
    def test_text_outside_fences_ignored(self) -> None:
        section = "\nprose line not in a fence\n```bash\ngz only\n```\nmore prose\n"
        self.assertEqual(extract_fenced_commands(section), ["gz only"])


class TestShellLessClassifier(unittest.TestCase):
    @covers("REQ-0.0.63-02-02")
    def test_single_program_is_executable(self) -> None:
        self.assertTrue(is_shell_less_executable("uv run gz adr status ADR-0.0.63 --json"))
        self.assertTrue(is_shell_less_executable("grep -q pattern file.md"))

    @covers("REQ-0.0.63-02-02")
    def test_compound_shell_forms_are_not_executable(self) -> None:
        self.assertFalse(is_shell_less_executable('test -f x && echo "ok"'))
        self.assertFalse(is_shell_less_executable("cat a || cat b"))
        self.assertFalse(is_shell_less_executable("grep x f | wc -l"))
        self.assertFalse(is_shell_less_executable("cmd1 ; cmd2"))
        self.assertFalse(is_shell_less_executable("echo $(date)"))
        self.assertFalse(is_shell_less_executable("cmd > out.txt"))
        self.assertFalse(is_shell_less_executable("cmd < in.txt"))

    @covers("REQ-0.0.63-02-02")
    def test_operator_inside_quoted_arg_is_data_not_syntax(self) -> None:
        self.assertTrue(is_shell_less_executable('python -c "a and b | c"'))
        self.assertTrue(is_shell_less_executable("python -c 'x = 1 && 2'"))

    @covers("REQ-0.0.63-02-02")
    def test_unbalanced_quotes_are_not_executable(self) -> None:
        self.assertFalse(is_shell_less_executable('python -c "unterminated'))


class TestReexecuteDemo(unittest.TestCase):
    @covers("REQ-0.0.63-02-03")
    def test_positive_path_binds_observed_exit_and_stdout_sha(self) -> None:
        stub = QualityResult(
            success=True, command="x", stdout="demo-out\n", stderr="", returncode=0
        )
        with mock.patch("gzkit.brief_commands.run_command", return_value=stub) as run:
            receipt = reexecute_demo(
                "uv run gz adr status ADR-0.0.63 --json", expected_returncode=0
            )
        run.assert_called_once()
        self.assertTrue(receipt.executed)
        self.assertTrue(receipt.shell_less)
        self.assertEqual(receipt.returncode, 0)
        self.assertFalse(receipt.mismatch)
        self.assertEqual(receipt.stdout_sha256, hashlib.sha256(b"demo-out\n").hexdigest())

    @covers("REQ-0.0.63-02-03")
    def test_exit_shape_mismatch_is_flagged(self) -> None:
        stub = QualityResult(success=False, command="x", stdout="", stderr="boom", returncode=3)
        with mock.patch("gzkit.brief_commands.run_command", return_value=stub):
            receipt = reexecute_demo(
                "uv run gz adr status ADR-0.0.63 --json", expected_returncode=0
            )
        self.assertTrue(receipt.executed)
        self.assertEqual(receipt.returncode, 3)
        self.assertTrue(receipt.mismatch)

    @covers("REQ-0.0.63-02-03")
    def test_non_shell_less_demo_is_not_executed_and_flagged(self) -> None:
        # Must short-circuit BEFORE any subprocess: run_command is never called.
        with mock.patch("gzkit.brief_commands.run_command") as run:
            receipt = reexecute_demo('test -f x && echo "ok"', expected_returncode=0)
        run.assert_not_called()
        self.assertFalse(receipt.shell_less)
        self.assertFalse(receipt.executed)
        self.assertTrue(receipt.mismatch)


class TestCommandArgv(unittest.TestCase):
    @covers("REQ-0.0.63-02-04")
    def test_multiline_command_is_single_argv_element(self) -> None:
        argv = command_argv('uv run python -c "line1\nline2"')
        self.assertEqual(argv[:4], ["uv", "run", "python", "-c"])
        self.assertEqual(len(argv), 5)
        self.assertIn("\n", argv[4])  # the -c body is ONE element, newline preserved


if __name__ == "__main__":
    unittest.main()
