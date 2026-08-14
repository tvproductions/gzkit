"""Handoff-resume gate hook script source (GHI #574).

The generated-script home for the Operator Authorization Gate's vendor adapter.
The DECISION lives in ``gzkit.handoff_resume_gate``; this module only renders the
thin stdin/exit-code shim around it, so the gate stays unit-testable and
``@enforces``-able (generated text is neither).
"""

from __future__ import annotations

from textwrap import dedent


def _handoff_resume_gate_script() -> str:
    """Return the PreToolUse handoff-resume gate hook script (GHI #574).

    Blocks every mutating tool call (``Write|Edit|NotebookEdit|Bash``) while this
    session has resumed a handoff the operator has not ruled on. Thin adapter:
    reads the harness payload, delegates to :func:`gzkit.handoff_resume_gate.decide`,
    and translates the verdict into the hook exit-code contract.

    Fail-OPEN on infrastructure failure (unreadable stdin, gzkit not importable):
    a gate that bricks the agent when its own plumbing breaks is worse than the
    hole it plugs, and the gate's evidence read already fails CLOSED where it
    matters (a missing ledger never authorizes). A broken import is not a
    governance signal; an absent authorization is.
    """
    return dedent(
        """\
            #!/usr/bin/env python3
            \"\"\"Handoff Resume Gate Hook (GHI #574).

            PreToolUse hook on Write|Edit|NotebookEdit|Bash. Refuses execution while
            this session has resumed a handoff the operator has not yet ruled on —
            the mechanical form of `gz-session-handoff` SKILL.md § RESUME's universal
            Operator Authorization Gate ("no file mutation / gz ceremony / migration
            until the operator rules"), which was prose plus a banner until now.

            Thin adapter only: the decision is `gzkit.handoff_resume_gate.decide`.

            Exit codes:
              0 - Allow operation
              2 - Block operation (no operator authorization booked for this session)
            \"\"\"

            from __future__ import annotations

            import json
            import sys
            from pathlib import Path


            def _find_project_root(start: Path) -> Path:
                current = start
                while current != current.parent:
                    if (current / ".gzkit").is_dir():
                        return current
                    current = current.parent
                return start


            def main() -> None:
                try:
                    payload = json.load(sys.stdin)
                except (json.JSONDecodeError, OSError):
                    sys.exit(0)

                cwd = payload.get("cwd") or ""
                if not cwd:
                    sys.exit(0)

                try:
                    from gzkit.handoff_resume_gate import decide, record_refusal
                except ImportError:
                    # Fail-open: gzkit unavailable is a plumbing failure, not a
                    # governance signal. The gate's evidence read fails CLOSED
                    # where it matters (see is_resume_authorized).
                    sys.exit(0)

                root = _find_project_root(Path(cwd).resolve())
                session_id = str(payload.get("session_id") or "")
                tool_name = str(payload.get("tool_name") or "")
                tool_input = payload.get("tool_input") or {}
                verdict = decide(
                    root,
                    session_id=session_id,
                    tool_name=tool_name,
                    tool_input=tool_input,
                )
                if verdict.blocked:
                    # Layer-2 record of the refusal, by SHAPE only. Before this
                    # the ledger held 160 lift records and zero blocks, so the
                    # gate's dominant failure mode — refusing a read it should
                    # admit — was discoverable only by an operator complaining.
                    # `record_refusal` is fail-open by contract and cannot raise;
                    # the block below runs whatever it returns.
                    record_refusal(
                        root,
                        session_id=session_id,
                        tool_name=tool_name,
                        tool_input=tool_input,
                    )
                    print(verdict.reason, file=sys.stderr)
                    sys.exit(2)
                sys.exit(0)


            if __name__ == "__main__":
                main()
        """
    )
