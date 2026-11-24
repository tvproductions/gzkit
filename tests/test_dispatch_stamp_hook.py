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
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, override
from unittest.mock import patch

from gzkit.config import GzkitConfig
from gzkit.dispatch_stamp import (
    STAMP_ID_ENV,
    STAMP_ROOT_ENV,
    claim_hook_output,
    end_hook_output,
    names_gz,
    stamp_hook_output,
)
from gzkit.executables import find_executable
from gzkit.hooks.claude import generate_claude_settings
from gzkit.hooks.scripts.dispatch import dispatch_stamp_script

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractContextManager

_AGENT = "a0123456789abcdef"
_DISPATCH = "D-0123456789abcdef"


def _raised(act: Callable[[], object]) -> Exception | None:
    """Run *act* and return what it raised, so a crash fails an assertion rather than erroring.

    The generated hook suppresses what these functions raise, so a crash reaches no
    harness; it drops the booking instead, which is why each call asserts none (RP-12
    rulings 100 and 156).

    Returns:
        The exception *act* raised, or ``None`` when it returned.

    """
    try:
        act()
    except Exception as exc:  # a crash in place of the behaviour must fail, not error
        return exc
    return None


class _Session(unittest.TestCase):
    """A project with a ledger, and a parent session whose subagent was prompted."""

    @override
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

    def _book(self, dispatch_id: str = _DISPATCH, role: str = "Implementer") -> None:
        row = {
            "schema": "gzkit.ledger.v1",
            "event": "work_package_dispatched",
            "id": "WP-01-loop",
            "ts": "2026-11-05T00:00:00+00:00",
            "work_package": "WP-01-loop",
            "role": role,
            "model": "sonnet",
            "subject": "#1200",
            "dispatch_id": dispatch_id,
            "intended_root": self.intended.as_posix(),
        }
        with self.ledger.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row) + "\n")

    def _move(self, to_state: str, work_package: str = "WP-01-loop") -> None:
        row = {
            "schema": "gzkit.ledger.v1",
            "event": "work_package_transitioned",
            "id": work_package,
            "ts": "2026-11-05T00:00:00+00:00",
            "work_package": work_package,
            "from_state": None,
            "to_state": to_state,
            "evidence": "e",
        }
        with self.ledger.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row) + "\n")

    def _returned(self, prompt: str, agent: str = _AGENT) -> dict[str, Any]:
        return {
            "hook_event_name": "PostToolUse",
            "tool_name": "Agent",
            "tool_input": {"prompt": prompt, "description": "work"},
            "tool_response": {"agentId": agent, "status": "completed"},
        }

    def _claims(self) -> list[dict[str, Any]]:
        return self._events("dispatch_claimed")

    def _events(self, event: str) -> list[dict[str, Any]]:
        rows = [json.loads(line) for line in self.ledger.read_text(encoding="utf-8").splitlines()]
        return [row for row in rows if row.get("event") == event]

    def _end(self, payload: dict[str, Any]) -> None:
        """Run the end hook, asserting it books or does nothing and never raises."""
        self.assertIsNone(_raised(lambda: end_hook_output(payload, self.project)))

    def _stopped(self, agent: str = _AGENT) -> dict[str, Any]:
        """Return a ``SubagentStop`` payload as the probe measured it (ruling 115).

        Returns:
            The payload, its transcript the subagent's own.

        """
        return {
            "hook_event_name": "SubagentStop",
            "agent_id": agent,
            "agent_type": "general-purpose",
            "agent_transcript_path": (self.subagents / f"agent-{_AGENT}.jsonl").as_posix(),
            "transcript_path": self.parent.as_posix(),
            "cwd": self.project.as_posix(),
        }

    def _void(self, dispatch_id: str = _DISPATCH) -> None:
        row = {
            "schema": "gzkit.ledger.v1",
            "event": "dispatch_voided",
            "id": dispatch_id,
            "ts": "2026-11-05T00:00:00+00:00",
            "dispatch_id": dispatch_id,
            "work_package": "WP-01-loop",
            "reason": "killed by TaskStop",
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

    def _payload(self, command: str, *, agent: str | None = _AGENT) -> dict[str, Any]:
        payload: dict[str, Any] = {
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
        outputs: list[dict[str, Any] | None] = []
        payload = self._payload(command)
        self.assertIsNone(_raised(lambda: outputs.append(stamp_hook_output(payload, self.project))))
        (output,) = outputs
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
        for command in ("echo hi", "ls src/gzkit", "gzip -d x.gz", "cat docs/gz.md"):
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
            "bash -c 'gz status'",
            "x=$(gz status)",
            'echo "$(uv run gz status)"',
            "echo `gz status`",
            "X=1 gz status",
            "env -u FOO gz status",
            "uvx --from py-gzkit gz status",
            "{ gz status; }",
            "time gz status",
            "sudo gz status",
            "! gz status",
            "echo 'unbalanced; gz status",
            "uv run --project /x gz status",
            "if uv run gz status; then echo ok; fi",
            "for x in a; do gz status; done",
            "while true; do gz status; break; done",
            "if true\nthen gz status\nfi",
            "eval 'gz status'",
            "eval uv run gz status",
            "watch gz status",
            "stdbuf -oL gz status",
            "coproc gz status",
            "builtin command gz status",
            "find . -exec gz status \\;",
            "bash -lc 'gz status'",
            "sh -ec 'gz status'",
            "python -mgzkit status",
            "python3 - <<'EOF'\nfrom gzkit.cli.main import main\nmain()\nEOF",
            "py -m gzkit status",
            ">log gz status",
            "2>/dev/null uv run gz status",
            "echo a#b; gz status",
            "git log --format=%h#%s -1; uv run gz status",
            "uv tool run gz status",
            "uv --directory /r run gz status",
            "uv run python -I -m gzkit status",
            "[ -d x ] || gz status",
            "f() { gz status; }; f",
            "uv run 'gz' status",
            "gz status #note",
            "timeout 60 gz status",
            "env -C /x gz status",
            "nice -n 5 gz status",
            "sudo -u me gz status",
            "time -p gz status",
            "python -X utf8 -m gzkit status",
            "python -W ignore -m gzkit status",
            "bash -o pipefail -c 'gz status'",
            "bash -e -o pipefail -c 'uv run gz check'",
            "bash --login -c 'gz status'",
            "uv run --exclude-newer 2026-01-01 gz status",
            "uv run --no-group dev gz status",
            "uv --color never run gz status",
            "uv run --link-mode copy gz status",
            "xargs --max-args 1 gz",
            "cat <(gz status)",
            "env -S 'gz status'",
            "GZ.EXE status",
            "uv run gz.EXE status",
            "direnv exec . gz status",
            "caffeinate -i gz status",
            "flock /tmp/l gz status",
            "ionice -c3 gz status",
            "script -q /dev/null gz status",
            "parallel gz ::: a",
            "watch -n5 'gz status'",
            "watch 'uv run gz status'",
            "script -qc 'gz status' /dev/null",
            "flock /tmp/l -c 'gz status'",
            "parallel 'gz {}' ::: a",
            'cmd /c "gz status"',
            "cmd.exe /c 'uv run gz status'",
            "bash <<< 'gz status'",
            "bash -s <<< 'gz status'",
            "echo 'gz status' | bash",
            "su -c 'gz status' me",
            "busybox sh -c 'gz status'",
            "tmux new -d 'gz status'",
            "hyperfine 'gz status'",
            "git rebase -x 'gz check' HEAD~3",
            "git bisect run gz test",
            "watchexec -- gz test",
            "entr gz status",
            "fd -x gz",
            "python -Im gzkit status",
            "python3 -Bm gzkit",
            "uv run python -Im gzkit",
            "poetry run gz status",
            "pdm run gz status",
            "hatch run gz status",
            "pixi run gz status",
            "conda run -n env gz status",
            "mise exec -- gz status",
            "pipx run --spec py-gzkit gz status",
            "pyenv exec python -m gzkit status",
            ". gz",
            "$(which gz) status",
            '"$(which gz)" status',
            "`command -v gz` status",
        )
        unnamed = (
            "ls src/gzkit",
            "ls src/gzkit/",
            "gzip f",
            "zgz",
            "cat gz-notes",
            "git log",
            "echo $GZIP",
            "cd /Users/jeff/Documents/Code/gzkit && git status",
            "git -C /x/gzkit log",
            "ruff check src/gzkit",
            "cat docs/gz.md",
            "echo 'gz status'",
            "grep -rn gzkit docs",
            "python -m unittest tests.test_gzkit",
            "uv run --project /Users/jeff/Documents/Code/gzkit python -m unittest tests.x",
            "uv --directory /Users/jeff/Documents/Code/gzkit run ruff check .",
            "uvx ruff check src/gzkit",
            "env -C /Users/jeff/Documents/Code/gzkit git status",
            "timeout 60 git -C /Users/jeff/Documents/Code/gzkit log",
            "nohup ls src/gzkit",
            "sudo ls /opt/gzkit",
            "uv pip show gzkit",
            "uv run --with gzkit python x.py",
            "xargs grep -l gz",
            "time grep -rn gz src",
            "command -v gz",
            "git commit -m 'gz: fix'",
            "uv pip show py-gzkit",
            "uv run --frozen python -m unittest tests.test_gzkit",
            "uv run --exclude-newer 2026-01-01 ruff check src/gzkit",
            "which gz",
            "find . -name gz -print",
            "watch -n 5 ls src/gzkit",
            "python -m pip install gzkit",
            "git ls-files -z | xargs -0 grep -l gzkit",
            "find . -print0 | xargs -0 grep -n gzkit",
            "xargs -r rg gz < files.txt",
            "uv run --frozen pytest -k gz",
            "uv run --locked python -m unittest -k gzkit",
            "timeout --foreground 60 rg gzkit",
            "sudo -E grep -r gzkit /etc",
            (
                "git commit -m \"$(cat <<'EOF'\nfix the subagent's hook in src/gzkit\n\n"
                '(ruling 40) gz verbs refuse\nuv run gz check passed\nEOF\n)"'
            ),
            "gh pr create --body \"$(cat <<'EOF'\nIt's the gzkit hook\nEOF\n)\"",
            "python3 -c \"import json; json.load(open('.gzkit.json'))\"",
            "uv run python -c \"print(open('.gzkit/ledger.jsonl').readline())\"",
            "python3 - <<'EOF'\nprint(open('.gzkit/ledger.jsonl').readline())\nEOF",
            "python3 - <<'EOF'\nopen('/Users/jeff/Documents/Code/gzkit/x.txt')\nEOF",
            "ls\n# gz status is slow\nls -la",
            "ls; #gz notes",
            'echo "$(date) gz done"',
            "fd gz",
            "poetry run pytest -k gz",
        )
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


class PowerShell(_Session):
    """Ruling 39: a subagent's PowerShell gz call is denied, never rewritten unprobed."""

    def _powershell(self, command: str, *, agent: str | None = _AGENT) -> dict[str, Any]:
        return {**self._payload(command, agent=agent), "tool_name": "PowerShell"}

    def test_a_subagents_powershell_gz_call_is_denied_with_recovery_prose(self) -> None:
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        output = stamp_hook_output(self._powershell("uv run gz status"), self.project)
        assert output is not None
        specific = output["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertNotIn("updatedInput", specific)
        reason = specific["permissionDecisionReason"]
        # guardrail-feedback-prose: what failed, why (the ruling), the next step.
        self.assertIn("PowerShell", reason)
        self.assertIn("ruling 39", reason)
        self.assertIn("Bash", reason)

    def test_windows_paths_and_wrappers_are_denied(self) -> None:
        for command in (
            ".venv\\Scripts\\gz.exe status",
            ".\\.venv\\Scripts\\gz status",
            "C:\\r\\.venv\\Scripts\\gz.exe status",
            "Invoke-Expression 'gz status'",
            "cmd /c gz status",
            "& 'C:\\r\\.venv\\Scripts\\gz.exe' status",
            "uv run gz status",
            "GZ status",
            "Start-Process gz -ArgumentList status",
            ". .venv\\Scripts\\gz.exe status",
            "& (Get-Command gz) status",
            "pwsh -EncodedCommand ZwB6ACAAcwB0AGEAdAB1AHMA",
            'cmd /c "gz status"',
        ):
            with self.subTest(command=command):
                output = stamp_hook_output(self._powershell(command), self.project)
                assert output is not None
                self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_other_powershell_calls_pass_untouched(self) -> None:
        for command in (
            "Get-ChildItem",
            "Set-Location C:\\code\\gzkit; git status",
            "Get-ChildItem C:\\code\\gzkit\\src",
            "git -C C:\\code\\gzkit log",
            "tar -xzf file.tar.gz",
            "Expand-Archive x.gz",
            "Get-Content docs/gz.md",
            "Select-String -Pattern gz *.md",
            "$gz = 1",
            "python -c \"import json; json.load(open('.gzkit.json'))\"",
            "git commit -m @'\nfix the subagent's gzkit hook\n'@",
            "<# run gz later #> Get-ChildItem",
        ):
            with self.subTest(command=command):
                self.assertIsNone(stamp_hook_output(self._powershell(command), self.project))
        main = self._powershell("uv run gz status", agent=None)
        self.assertIsNone(stamp_hook_output(main, self.project))


class TheClaim(_Session):
    """Ruling 40: a subagent's binding to its dispatch is booked, at two points."""

    def test_a_dispatched_subagents_gz_call_books_its_claim_once(self) -> None:
        self._move("commenced")
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        self._stamped()
        self._stamped()
        (claim,) = self._claims()
        self.assertEqual(
            (claim["dispatch_id"], claim["agent_id"], claim["source"]),
            (_DISPATCH, _AGENT, "stamp"),
        )

    def test_the_agent_tools_return_books_the_claim(self) -> None:
        self._move("commenced")
        self._book()
        self.assertIsNone(
            claim_hook_output(self._returned(f"GZKIT-DISPATCH: {_DISPATCH}"), self.project)
        )
        (claim,) = self._claims()
        self.assertEqual((claim["agent_id"], claim["source"]), (_AGENT, "agent_returned"))

    def test_no_claim_for_a_prompt_naming_no_booked_dispatch(self) -> None:
        self._book()
        for prompt in ("no line here", "GZKIT-DISPATCH: D-fedcba9876543210"):
            with self.subTest(prompt=prompt):
                self.assertIsNone(claim_hook_output(self._returned(prompt), self.project))
        self.assertEqual(self._claims(), [])


class TheEnd(_Session):
    """Ruling 115: a dispatch's end is booked when its subagent stops."""

    def test_a_stopping_subagent_books_its_dispatchs_end_once(self) -> None:
        """No claim is needed first: a foreground claim is booked after SubagentStop."""
        self._move("commenced")
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        self._end(self._stopped())
        self._end(self._stopped())
        ends = self._events("dispatch_ended")
        self.assertEqual(len(ends), 1)
        self.assertEqual((ends[0]["dispatch_id"], ends[0]["agent_id"]), (_DISPATCH, _AGENT))
        self.assertEqual(self._claims(), [])

    def test_a_resumed_subagent_whose_dispatch_ended_is_stamped_no_root(self) -> None:
        """Ruling 160: an end holds like a void, though SendMessage resumes the subagent.

        The probe of ruling 158 measured a stopped subagent resumed through SendMessage
        running gz under its ended dispatch's stamp; its first record still names it.
        """
        self._move("commenced")
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        self._end(self._stopped())
        self.assertEqual(self._stamped(), {STAMP_ROOT_ENV: "", STAMP_ID_ENV: _DISPATCH})
        # ruling 161: the claim records what happened; the stamp alone holds it
        self.assertEqual(
            [(c["dispatch_id"], c["agent_id"]) for c in self._claims()], [(_DISPATCH, _AGENT)]
        )

    def test_only_the_first_claimants_stop_ends_the_dispatch(self) -> None:
        """Ruling 162: another agent prompted with the same line cannot end a claimed dispatch.

        The inspection's probe: agent B's stop ended the dispatch and stripped A's root.
        """
        self._move("commenced")
        self._book()
        line = f"GZKIT-DISPATCH: {_DISPATCH}"
        self._prompt(line)
        root = self._stamped()[STAMP_ROOT_ENV]  # A claims by its stamp
        self._prompt(line, agent="a-helper")
        self._end(self._stopped(agent="a-helper"))
        self.assertEqual(self._events("dispatch_ended"), [])
        self._prompt(line)
        self.assertEqual(self._stamped()[STAMP_ROOT_ENV], root)  # A keeps its root
        self._end(self._stopped())
        self.assertEqual([e["agent_id"] for e in self._events("dispatch_ended")], [_AGENT])

    def test_another_dispatchs_earlier_claim_does_not_bar_this_ones_end(self) -> None:
        """Ruling 162 reads the first claimant of this dispatch, not of the ledger.

        The O3 re-sweep's survivor: a claimant filter forced true read another
        dispatch's claim as this one's, and a claimed subagent's stop booked no end.
        """
        self._move("commenced")
        other = "D-fedcba9876543210"
        self._book(other)
        self._book()
        returned = self._returned(f"GZKIT-DISPATCH: {other}", agent="b-agent")
        self.assertIsNone(_raised(lambda: claim_hook_output(returned, self.project)))
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        self._stamped()  # this dispatch is claimed by its own subagent
        self.assertEqual(
            [(c["dispatch_id"], c["agent_id"]) for c in self._claims()],
            [(other, "b-agent"), (_DISPATCH, _AGENT)],
        )
        self._end(self._stopped())
        self.assertEqual(
            [(e["dispatch_id"], e["agent_id"]) for e in self._events("dispatch_ended")],
            [(_DISPATCH, _AGENT)],
        )

    def test_a_foreground_return_after_its_end_still_books_the_claim(self) -> None:
        """Ruling 161: a foreground subagent's stop books its end before the Agent tool returns.

        The return's claim is booked all the same (ruling 40), so the dispatch reads
        claimed, as it did before ruling 160 (§ The `SubagentStop` probe, run 2).
        """
        self._move("commenced")
        self._book()
        line = f"GZKIT-DISPATCH: {_DISPATCH}"
        self._prompt(line)
        self._end(self._stopped())
        self.assertIsNone(_raised(lambda: claim_hook_output(self._returned(line), self.project)))
        self.assertEqual(
            [(c["dispatch_id"], c["agent_id"], c["source"]) for c in self._claims()],
            [(_DISPATCH, _AGENT, "agent_returned")],
        )

    def test_a_voided_dispatch_is_stamped_no_root(self) -> None:
        """Ruling 118: a killed dispatch ends by its void, and its subagent stamps no root."""
        self._book()
        self._void()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        self.assertEqual(self._stamped(), {STAMP_ROOT_ENV: "", STAMP_ID_ENV: _DISPATCH})

    def test_a_prompt_in_content_blocks_reads_its_text_blocks_alone(self) -> None:
        """A block that is not an object, or carries no text, is passed over, not read."""
        self._move("commenced")
        self._book()
        self._prompt(
            ["stray", {"type": "image"}, {"type": "text", "text": f"GZKIT-DISPATCH: {_DISPATCH}"}]
        )
        self._end(self._stopped())
        ends = self._events("dispatch_ended")
        self.assertEqual([end["dispatch_id"] for end in ends], [_DISPATCH])

    def test_no_end_from_a_first_record_or_message_that_is_not_an_object(self) -> None:
        self._book()
        transcript = self.subagents / f"agent-{_AGENT}.jsonl"
        message = {"agentId": _AGENT, "type": "user", "message": f"GZKIT-DISPATCH: {_DISPATCH}"}
        for first in ([f"GZKIT-DISPATCH: {_DISPATCH}"], message):
            with self.subTest(first=first):
                transcript.write_text(json.dumps(first) + "\n", encoding="utf-8")
                self._end(self._stopped())
        self.assertEqual(self._events("dispatch_ended"), [])

    def test_no_end_for_a_prompt_naming_no_live_dispatch(self) -> None:
        """Ruling 118: a voided dispatch has ended by its void; none booked, none to end."""
        self._book()
        self._book("D-1111111111111111")
        self._void("D-1111111111111111")
        for prompt in (
            "no line here",
            "GZKIT-DISPATCH: D-fedcba9876543210",
            "GZKIT-DISPATCH: D-1111111111111111",
        ):
            with self.subTest(prompt=prompt):
                self._prompt(prompt)
                self._end(self._stopped())
        self.assertEqual(self._events("dispatch_ended"), [])

    def test_no_end_from_a_payload_missing_its_agent_or_transcript(self) -> None:
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        for field in ("agent_id", "agent_transcript_path"):
            for value in (None, ""):
                with self.subTest(field=field, value=value):
                    self._end({**self._stopped(), field: value})
        self.assertEqual(self._events("dispatch_ended"), [])

    def test_no_end_from_a_transcript_that_is_not_the_stopping_agents(self) -> None:
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}", agent="a-someone-else")
        self._end(self._stopped())
        missing = {
            **self._stopped(),
            "agent_transcript_path": (self.subagents / "x.jsonl").as_posix(),
        }
        self._end(missing)
        self.assertEqual(self._events("dispatch_ended"), [])

    def test_only_subagent_stop_books_an_end(self) -> None:
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        for event in ("Stop", "PostToolUse", "PreToolUse"):
            with self.subTest(event=event):
                self._end({**self._stopped(), "hook_event_name": event})
        self.assertEqual(self._events("dispatch_ended"), [])


def drydock() -> AbstractContextManager[object]:
    """Hold the safe-mode condition on at the drydock level, at its source.

    Returns:
        A patch of ``gzkit.mx.marker.condition``, which ``alarms_off`` consults
        however it was imported; a reader binding ``condition`` itself at import
        would escape it.

    """
    held = SimpleNamespace(on=True, marker=SimpleNamespace(level="drydock"), cause=None)
    return patch("gzkit.mx.marker.condition", return_value=held)


class OutOfService(_Session):
    """Ruling 28: a kit control is on at every level, out of service included."""

    def test_the_stamp_holds_with_the_alarms_off(self) -> None:
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        with drydock():
            self.assertEqual(self._stamped()[STAMP_ROOT_ENV], self.intended.as_posix())

    def test_no_dispatch_stamp_hook_is_routed_through_the_alarm_switch(self) -> None:
        """The switch that turns slow alarms off in the drydock never wraps the stamp."""
        settings = generate_claude_settings(GzkitConfig())
        commands = [
            hook["command"]
            for phase in settings["hooks"].values()
            for entry in phase
            for hook in entry["hooks"]
            if "dispatch-stamp" in hook["command"]
        ]
        self.assertEqual(len(commands), 4)
        for command in commands:
            self.assertNotIn("gzkit.mx.alarms", command)


class TheUndispatchedSubagent(_Session):
    """Ruling 38: a prompt with no dispatch line is held to this project's root.

    Ruling 40: not while an unclaimed dispatch for another root is open, since
    that subagent may be the dispatched one whose line was lost.
    """

    def test_an_open_unclaimed_dispatch_elsewhere_stamps_no_root(self) -> None:
        self._move("commenced")
        self._book()
        self._prompt("Review this commit; no dispatch line.")
        self.assertEqual(self._stamped(), {STAMP_ROOT_ENV: "", STAMP_ID_ENV: ""})

    def test_once_claimed_the_undispatched_subagent_is_held_to_the_project(self) -> None:
        self._move("commenced")
        self._book()
        claim_hook_output(
            self._returned(f"GZKIT-DISPATCH: {_DISPATCH}", agent="a-implementer"),
            self.project,
        )
        self._prompt("Review this commit; no dispatch line.")
        self.assertEqual(self._stamped()[STAMP_ROOT_ENV], self.project.as_posix())

    def test_an_ended_dispatch_no_longer_holds_the_undispatched_subagent(self) -> None:
        """Ruling 161: an ended dispatch is closed to ruling 40, as a voided one is.

        No new subagent can take a dispatch whose subagent has stopped, so it no longer
        holds an undispatched subagent at no root, whether or not its claim was booked.
        """
        self._move("commenced")
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        self._end(self._stopped())
        self._prompt("Review this commit; no dispatch line.")
        self.assertEqual(self._claims(), [])
        self.assertEqual(self._stamped()[STAMP_ROOT_ENV], self.project.as_posix())

    def test_an_accepted_package_is_still_in_flight(self) -> None:
        self._move("commenced")
        self._book()
        self._move("accepted")
        self._prompt("Review this commit; no dispatch line.")
        self.assertEqual(self._stamped()[STAMP_ROOT_ENV], "")

    def test_a_dispatch_whose_run_is_not_in_flight_does_not_count(self) -> None:
        self._move("commenced")
        self._book()
        self._move("closed")
        self._prompt("Review this commit; no dispatch line.")
        self.assertEqual(self._stamped()[STAMP_ROOT_ENV], self.project.as_posix())

    def test_an_unclaimed_dispatch_for_this_project_does_not_count(self) -> None:
        self._move("commenced")
        self.intended = self.project
        self._book()
        self._prompt("Review this commit; no dispatch line.")
        self.assertEqual(self._stamped()[STAMP_ROOT_ENV], self.project.as_posix())

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

    def test_a_prompt_that_mentions_the_dispatch_line_in_prose(self) -> None:
        """Fails safe: a mention it cannot read as one dispatch is not an undispatched agent."""
        self._book()
        self._prompt("The runtime puts a GZKIT-DISPATCH: line in a dispatched prompt.")
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

    def test_a_dispatch_booked_twice_with_different_roles(self) -> None:
        """Ruling 1: what the ledger says a dispatch may do must be one thing."""
        self._book()
        self._book(role="SpecReviewer")
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        self._assert_no_root()

    def test_an_unreadable_ledger(self) -> None:
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        self.ledger.write_text("{broken\n", encoding="utf-8")
        self._assert_no_root()


class TheGeneratedHook(_Session):
    """The rendered script, run as Claude Code runs it: JSON on stdin, JSON out."""

    def _run_hook(self, payload: dict[str, Any], *, shadow_gzkit: bool = False) -> str:
        """Run the generated hook on one payload.

        Returns:
            What the hook printed on stdout.

        """
        hook_dir = self.project.parent / "hook"
        hook_dir.mkdir(exist_ok=True)
        script = hook_dir / "dispatch-stamp.py"
        script.write_text(dispatch_stamp_script(), encoding="utf-8")
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

    def test_the_fail_closed_path_denies_a_subagents_powershell_gz_call(self) -> None:
        """Ruling 39 holds when gzkit cannot load."""
        payload = {**self._payload("gz status"), "tool_name": "PowerShell"}
        stdout = self._run_hook(payload, shadow_gzkit=True)
        self.assertEqual(json.loads(stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_the_hook_books_a_claim_on_the_agent_tools_return(self) -> None:
        self._move("commenced")
        self._book()
        stdout = self._run_hook(self._returned(f"GZKIT-DISPATCH: {_DISPATCH}"))
        self.assertEqual(stdout, "")
        self.assertEqual([claim["source"] for claim in self._claims()], ["agent_returned"])

    def test_the_hook_books_an_end_when_a_subagent_stops(self) -> None:
        self._book()
        self._prompt(f"GZKIT-DISPATCH: {_DISPATCH}")
        self.assertEqual(self._run_hook(self._stopped()), "")
        self.assertEqual([end["agent_id"] for end in self._events("dispatch_ended")], [_AGENT])

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
