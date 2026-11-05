"""The dispatch stamp hook's script generator (RP-12 rulings 17, 34, 35)."""

from textwrap import dedent, wrap

from gzkit.dispatch_stamp import POWERSHELL_DENIAL, STAMP_ID_ENV, STAMP_ROOT_ENV


def _wrapped_literal(text: str) -> str:
    """Render text as adjacent string literals, one per line, that join back to it.

    Returns:
        The literal lines, the first unindented, for a parenthesized assignment.

    """
    chunks = wrap(text, 72, drop_whitespace=False, break_on_hyphens=False)
    return "\n    ".join(repr(chunk) for chunk in chunks)


def _dispatch_stamp_script() -> str:
    """Return the PreToolUse Bash hook that stamps a subagent's ``gz`` command.

    Thin adapter: the decision is :func:`gzkit.dispatch_stamp.stamp_hook_output`,
    so the hook stays unit-testable. Unlike the guards, it reads no safe-mode
    marker: it is a kit control, on at every level (ruling 28).

    Fail-CLOSED, unlike the guards, as far as the script reaches: once a payload
    is read, gzkit failing to import or the decision raising still stamps a
    subagent's Bash call naming ``gz``, with no root, so every verb refuses it
    (rulings 17, 35). A hook that cannot run at all, ``uv`` failing, a timeout, or
    a payload that is not JSON, leaves the call unstamped, since Claude Code
    proceeds past a failing hook; that limit is stated in the contract kit. The
    stamp's variable names are written in from
    :mod:`gzkit.dispatch_stamp` here, their one home.

    Returns:
        The hook script's source.

    """
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"Dispatch Stamp Hook (RP-12 rulings 17, 34 and 35).

            PreToolUse hook on Bash. On a subagent's call (the payload carries
            `agent_id`) whose command names `gz` or `gzkit`, reads the subagent's
            dispatch line from its own transcript, the root that dispatch intends
            from the ledger, and rewrites the command through `updatedInput` to
            carry both in its environment, with no permission decision. `gz` then
            refuses the call before any write unless it runs in that root. Every
            other call passes untouched; the main session's carry no `agent_id`.
            On PostToolUse for the Agent tool it books the returned subagent's
            claim of the dispatch its prompt names (ruling 40), deciding nothing.

            Thin adapter only: the decision is
            `gzkit.dispatch_stamp.stamp_hook_output`.

            Exit codes:
              0 - Always; the rewrite, when there is one, is on stdout
            \"\"\"

            import contextlib
            import json
            import os
            import sys
            from pathlib import Path

            STAMP_ROOT_ENV = "@ROOT@"
            STAMP_ID_ENV = "@ID@"
            POWERSHELL_DENIAL = (
            @DENIAL@
            )


            def _no_root(payload: dict) -> dict | None:
                \"\"\"Stamp no root on a subagent Bash call mentioning gz; deny PowerShell.

                Returns:
                    The rewrite, or None for a call it leaves alone.

                \"\"\"
                tool_input = payload.get("tool_input")
                tool_name = payload.get("tool_name")
                if tool_name not in {"Bash", "PowerShell"} or not payload.get("agent_id"):
                    return None
                if not isinstance(tool_input, dict):
                    return None
                command = tool_input.get("command")
                if not isinstance(command, str) or "gz" not in command.lower():
                    return None
                if tool_name == "PowerShell":
                    return {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": POWERSHELL_DENIAL,
                        }
                    }
                prefix = f"export {STAMP_ROOT_ENV}='' {STAMP_ID_ENV}=''; "
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "updatedInput": {**tool_input, "command": prefix + command},
                    }
                }


            def main() -> None:
                try:
                    payload = json.load(sys.stdin)
                except (json.JSONDecodeError, UnicodeDecodeError, OSError):
                    sys.exit(0)  # no payload, no command to stamp
                if not isinstance(payload, dict):
                    sys.exit(0)

                if payload.get("hook_event_name") == "PostToolUse":
                    # A claim unbooked leaves its dispatch open, which errs toward refusal.
                    with contextlib.suppress(Exception):
                        from gzkit.dispatch_stamp import claim_hook_output  # noqa: PLC0415

                        root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or str(payload.get("cwd") or "."))
                        claim_hook_output(payload, root)
                    sys.exit(0)

                try:
                    from gzkit.dispatch_stamp import stamp_hook_output  # noqa: PLC0415

                    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or str(payload.get("cwd") or "."))
                    output = stamp_hook_output(payload, root)
                except Exception:  # fail closed: stamp no root
                    output = _no_root(payload)

                if output is not None:
                    sys.stdout.write(json.dumps(output) + "\\n")
                sys.exit(0)


            if __name__ == "__main__":
                main()
            """
        )
        .replace("@ROOT@", STAMP_ROOT_ENV)
        .replace("@ID@", STAMP_ID_ENV)
        .replace("@DENIAL@", _wrapped_literal(POWERSHELL_DENIAL))
    )
