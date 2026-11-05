"""The stamp hook of RP-12 rulings 34 and 35, decided by ``gzkit.dispatch_stamp``.

On a subagent's Bash call (the payload carries ``agent_id``) whose command names
``gz`` or ``gzkit``, the hook reads the subagent's own transcript, beside the
parent's as ``<session>/subagents/agent-<agent_id>.jsonl``; its first record is
the prompt, where the dispatch line names the dispatch. The ledger says which root
that dispatch intends, and the command is rewritten through ``updatedInput`` to
carry the root and the id in its environment, with no permission decision. A
transcript or dispatch that cannot be read stamps no root, so every verb refuses
(ruling 17); the main session's calls and every other command pass untouched.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gzkit.dispatch_stamp import (
    STAMP_ID_ENV,
    STAMP_ROOT_ENV,
    names_gz,
    stamp_hook_output,
)
from gzkit.executables import find_executable
from gzkit.hooks.scripts.dispatch import _dispatch_stamp_script

_AGENT = "a0123456789abcdef"
_DISPATCH = "D-0123456789abcdef"


class _Session(unittest.TestCase):
    """A project with a ledger, and a parent session whose subagent was prompted."""

    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        base = Path(directory.name).resolve()
        self.project = base / "project"
        self.intended = base / "throwaway"
        (self.project / ".gzkit").mkdir(parents=True)
        self.intended.mkdir()
        self.ledger = self.project / ".gzkit" / "ledger.jsonl"
        self.ledger.write_text("", encoding="utf-8")
        self.parent = base / "sessions" / "s-1.jsonl"
        self.subagents = base / "sessions" / "s-1" / "subagents"
        self.subagents.mkdir(parents=True)

    def _book(self, dispatch_id: str = _DISPATCH) -> None:
        row = {
            "schema": "gzkit.ledger.v1",
            "event": "work_package_dispatched",
            "id": "WP-01-loop",
            "ts": "2026-11-05T00:00:00+00:00",
            "work_package": "WP-01-loop",
            "role": "Implementer",
            "model": "sonnet",
            "subject": "#1200",
            "dispatch_id": dispatch_id,
            "intended_root": self.intended.as_posix(),
        }
        with self.ledger.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row) + "\n")

    def _prompt(self, content: object, agent: str = _AGENT) -> None:
        first = {
            "parentUuid": None,
            "isSidechain": True,
            "agentId": agent,
            "type": "user",
            "message": {"role": "user", "content": content},
        }
        later = {"agentId": agent, "type": "assistant", "message": {"content": "ok"}}
        text = json.dumps(first) + "\n" + json.dumps(later) + "\n"
        (self.subagents / f"agent-{_AGENT}.jsonl").write_text(text, encoding="utf-8")

    def _payload(self, command: str, *, agent: str | None = _AGENT) -> dict:
        payload: dict = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command, "description": "run it"},
            "transcript_path": self.parent.as_posix(),
            "cwd": self.project.as_posix(),
        }
        if agent is not None:
            payload["agent_id"] = agent
            payload["agent_type"] = "general-purpose"
        return payload

    def _stamped(self, command: str = "uv run gz status") -> dict[str, str]:
        """Run the hook, then the rewritten command's prefix, and read the stamp back.

        Returns:
            The two stamp variables as the rewritten command's shell sees them.

        """
        output = stamp_hook_output(self._payload(command), self.project)
        self.assertIsNotNone(output)
        assert output is not None
        rewritten = output["hookSpecificOutput"]["updatedInput"]["command"]
        self.assertTrue(rewritten.endswith(command))
        prefix = rewritten.removesuffix(command)
        return _environment_of(prefix)


def _environment_of(prefix: str) -> dict[str, str]:
    """Read the stamp a prefix sets, by running it in a POSIX shell.

    Returns:
        The two stamp variables as that shell sees them.

    Raises:
        unittest.SkipTest: the host has no POSIX shell.

    """
    shell = find_executable("sh")
    if shell is None:
        reason = "no POSIX shell on this host"
        raise unittest.SkipTest(reason)
    probe = f'{prefix}printf "%s\\n%s" "${STAMP_ROOT_ENV}" "${STAMP_ID_ENV}"'
    result = subprocess.run(  # noqa: S603 -- an absolute shell, a literal argv
        [shell, "-c", probe],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
        timeout=60,
    )
    root, _, dispatch = result.stdout.partition("\n")
    return {STAMP_ROOT_ENV: root, STAMP_ID_ENV: dispatch}


class WhatIsStamped(_Session):
    def test_the_main_sessions_call_passes_untouched(self) -> None:
        """#1296 case 3 by construction: the main session's payload has no agent_id."""
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        self.assertIsNone(stamp_hook_output(self._payload("gz status", agent=None), self.project))

    def test_a_subagent_command_naming_no_gz_passes_untouched(self) -> None:
        """Ruling 34: its allow rules keep matching."""
        for command in ("echo hi", "ls src/gzkit/", "gzip -d x.gz", "cat docs/gz-notes.md"):
            with self.subTest(command=command):
                self.assertIsNone(stamp_hook_output(self._payload(command), self.project))

    def test_another_tool_passes_untouched(self) -> None:
        payload = {**self._payload("gz status"), "tool_name": "Read"}
        self.assertIsNone(stamp_hook_output(payload, self.project))

    def test_which_commands_name_gz(self) -> None:
        named = (
            "gz status",
            "uv run gz check",
            "cd /tmp && gz wp dispatch WP-01-x",
            "python -m gzkit status",
            "uv run -m gzkit justify x",
            "(gz status)",
            "echo; gz test",
            ".venv/bin/gz status",
            "/x/.venv/bin/gz status",
            "./.venv/bin/gzkit",
            "$HOME/bin/gz",
            "\\gz status",
            "gz>out.txt",
            "gz<in",
            "python -m gzkit.cli.main status",
            "python -c 'from gzkit.cli.main import main; main()'",
            "GZ status",
        )
        unnamed = ("ls src/gzkit/", "gzip f", "zgz", "cat gz-notes", "git log", "echo $GZIP")
        for command in named:
            with self.subTest(named=command):
                self.assertTrue(names_gz(command))
        for command in unnamed:
            with self.subTest(unnamed=command):
                self.assertFalse(names_gz(command))


class TheStamp(_Session):
    def test_a_booked_dispatch_stamps_its_intended_root(self) -> None:
        self._book()
        self._prompt(f"Do the work.\nGZKIT-DISPATCH: {_DISPATCH}\n")
        self.assertEqual(
            self._stamped(),
            {STAMP_ROOT_ENV: self.intended.as_posix(), STAMP_ID_ENV: _DISPATCH},
        )

    def test_the_rewrite_keeps_the_input_and_makes_no_permission_decision(self) -> None:
        """Ruling 34: no permissionDecision, so the operator's settings still rule."""
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        output = stamp_hook_output(self._payload("gz status"), self.project)
        assert output is not None
        specific = output["hookSpecificOutput"]
        self.assertEqual(specific["hookEventName"], "PreToolUse")
        self.assertNotIn("permissionDecision", specific)
        self.assertEqual(specific["updatedInput"]["description"], "run it")

    def test_a_prompt_given_as_content_blocks_is_read(self) -> None:
        self._book()
        self._prompt([{"type": "text", "text": f"GZKIT-DISPATCH: {_DISPATCH}"}])
        self.assertEqual(self._stamped()[STAMP_ROOT_ENV], self.intended.as_posix())

    def test_a_root_with_shell_characters_survives_the_prefix(self) -> None:
        self.intended = self.intended.parent / "it's $HOME; a dir"
        self.intended.mkdir()
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        self.assertEqual(self._stamped()[STAMP_ROOT_ENV], self.intended.as_posix())


class TheUndispatchedSubagent(_Session):
    """Ruling 38: a prompt with no dispatch line is held to this project's root."""

    def test_it_is_stamped_with_the_project_root(self) -> None:
        self._book()
        self._prompt("Review this commit; no dispatch line.")
        self.assertEqual(
            self._stamped(), {STAMP_ROOT_ENV: self.project.as_posix(), STAMP_ID_ENV: ""}
        )


class NoRootIsStamped(_Session):
    """Ruling 35: what cannot be read stamps no root, so a breakage shows as refusals."""

    def _assert_no_root(self) -> None:
        self.assertEqual(self._stamped()[STAMP_ROOT_ENV], "")

    def test_a_dispatch_line_that_does_not_parse(self) -> None:
        """A prompt that mentions a dispatch it cannot name is not an undispatched one."""
        self._book()
        self._prompt("GZKIT-DISPATCH: D-not-an-id")
        self._assert_no_root()

    def test_two_different_dispatch_lines(self) -> None:
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}\nGZKIT-DISPATCH: D-fedcba9876543210")
        self._assert_no_root()

    def test_a_dispatch_the_ledger_does_not_hold(self) -> None:
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        stamp = self._stamped()
        self.assertEqual(stamp, {STAMP_ROOT_ENV: "", STAMP_ID_ENV: _DISPATCH})

    def test_a_missing_transcript(self) -> None:
        self._book()
        self._assert_no_root()

    def test_an_unreadable_first_record(self) -> None:
        self._book()
        (self.subagents / f"agent-{_AGENT}.jsonl").write_text("{not json\n", encoding="utf-8")
        self._assert_no_root()

    def test_a_first_record_of_another_agent(self) -> None:
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}", agent="a-someone-else")
        self._assert_no_root()

    def test_a_payload_with_no_transcript_path(self) -> None:
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        payload = self._payload("gz status")
        del payload["transcript_path"]
        output = stamp_hook_output(payload, self.project)
        assert output is not None
        prefix = output["hookSpecificOutput"]["updatedInput"]["command"].removesuffix("gz status")
        self.assertEqual(_environment_of(prefix)[STAMP_ROOT_ENV], "")

    def test_a_first_record_that_is_not_the_prompt(self) -> None:
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        path = self.subagents / f"agent-{_AGENT}.jsonl"
        record = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
        record["type"] = "assistant"
        path.write_text(json.dumps(record) + "\n", encoding="utf-8")
        self._assert_no_root()

    def test_a_dispatch_booked_twice_with_different_roots(self) -> None:
        """Ids are minted unique; a ledger that disagrees with itself names no root."""
        self._book()
        first = self.intended
        self.intended = first.parent / "other"
        self.intended.mkdir()
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        self._assert_no_root()

    def test_an_unreadable_ledger(self) -> None:
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        self.ledger.write_text("{broken\n", encoding="utf-8")
        self._assert_no_root()


class TheGeneratedHook(_Session):
    """The rendered script, run as Claude Code runs it: JSON on stdin, JSON out."""

    def _run_hook(self, payload: dict, *, shadow_gzkit: bool = False) -> str:
        """Run the generated hook on one payload.

        Returns:
            What the hook printed on stdout.

        """
        hook_dir = self.project.parent / "hook"
        hook_dir.mkdir(exist_ok=True)
        script = hook_dir / "dispatch-stamp.py"
        script.write_text(_dispatch_stamp_script(), encoding="utf-8")
        if shadow_gzkit:
            # A package beside the script shadows the installed one and cannot load.
            broken = hook_dir / "gzkit"
            broken.mkdir()
            (broken / "__init__.py").write_text("raise ImportError('gone')\n", encoding="utf-8")
        environ = {**os.environ, "CLAUDE_PROJECT_DIR": self.project.as_posix()}
        result = subprocess.run(  # noqa: S603 -- the running interpreter, a literal argv
            [sys.executable, str(script)],
            input=json.dumps(payload),
            env=environ,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            timeout=60,
        )
        return result.stdout

    def _prefix(self, stdout: str, command: str) -> str:
        rewritten = json.loads(stdout)["hookSpecificOutput"]["updatedInput"]["command"]
        return rewritten.removesuffix(command)

    def test_the_hook_stamps_a_booked_dispatch(self) -> None:
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        stdout = self._run_hook(self._payload("gz status"))
        stamp = _environment_of(self._prefix(stdout, "gz status"))
        self.assertEqual(stamp[STAMP_ROOT_ENV], self.intended.as_posix())

    def test_the_hook_prints_nothing_for_the_main_session(self) -> None:
        self.assertEqual(self._run_hook(self._payload("gz status", agent=None)), "")

    def test_the_fail_closed_path_leaves_the_main_session_alone(self) -> None:
        payload = self._payload("gz status", agent=None)
        self.assertEqual(self._run_hook(payload, shadow_gzkit=True), "")

    def test_the_ledger_is_the_project_dirs_not_the_calls_cwd(self) -> None:
        """The dispatch was booked in the coordinator's project, whatever the shell's cwd."""
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        payload = {**self._payload("gz status"), "cwd": self.intended.as_posix()}
        stamp = _environment_of(self._prefix(self._run_hook(payload), "gz status"))
        self.assertEqual(stamp[STAMP_ROOT_ENV], self.intended.as_posix())

    def test_the_hook_fails_closed_when_gzkit_cannot_load(self) -> None:
        """Ruling 35: a breakage shows as refusals, never as an unstamped call."""
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        stdout = self._run_hook(self._payload("gz status"), shadow_gzkit=True)
        stamp = _environment_of(self._prefix(stdout, "gz status"))
        self.assertEqual(stamp, {STAMP_ROOT_ENV: "", STAMP_ID_ENV: ""})


if __name__ == "__main__":
    unittest.main()
