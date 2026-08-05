"""Session boundary hook script sources (GHI #756, #757).

The generated-script home for the exit beat's vendor adapter. The DECISION and
the write live in ``gzkit.session_exit``; this module renders only the thin
stdin shim around it, so the beat stays unit-testable and ``@enforces``-able
(generated text is neither) — the same split ``gzkit.hooks.scripts.handoff``
uses for the entry gate.
"""

from __future__ import annotations

from textwrap import dedent


def _session_exit_bookmark_script() -> str:
    """Return the SessionEnd floor-bookmark hook script (GHI #756).

    Fires on every session end — including reason ``clear``, which is how the
    operator moves between tasks inside one working session and therefore the
    case that loses the most context. Writes a CHECKPOINT bookmark and leaves.

    Always exits 0. ``SessionEnd`` cannot block by platform contract and its
    stdout is not injected, so there is no verdict to report and nobody to
    report it to; the beat's whole contract is that a record exists afterward.
    """
    return dedent(
        """\
            #!/usr/bin/env python3
            \"\"\"Session-Exit Bookmark Hook (GHI #756).

            SessionEnd hook. Writes a CHECKPOINT handoff recording where the
            session stopped, so continuity does not depend on an agent
            remembering to author one — the trigger ADR-0.0.65 never specified.

            Books, never refuses (operator ruling: "DO NOT BLOCK HERE ... write
            them all to the handoff bookmark, and leave"). Runs synchronously so
            the write completes before the process exits; `async` is unsupported
            on the Codex side and unverified here.

            Thin adapter only: the decision is `gzkit.session_exit.book_exit_bookmark`.

            Exit codes:
              0 - always (SessionEnd cannot block; there is no verdict to report)
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
                    from gzkit.session_exit import book_exit_bookmark
                except ImportError:
                    # gzkit unavailable is a plumbing failure, not a governance
                    # signal. Nothing to book and nowhere to report it.
                    sys.exit(0)

                root = _find_project_root(Path(cwd).resolve())
                book_exit_bookmark(
                    root,
                    session_id=str(payload.get("session_id") or ""),
                    exit_reason=str(payload.get("reason") or "unknown"),
                    transcript_path=payload.get("transcript_path") or None,
                )
                sys.exit(0)


            if __name__ == "__main__":
                main()
        """
    )


def _session_start_advisement_script() -> str:
    """Return the SessionStart handoff-advisement hook script (GHI #757).

    Emits the advisement through BOTH channels: ``additionalContext`` (passive,
    universal — the only channel Codex has) and ``initialUserMessage`` (which
    seeds an actual first turn, Claude-only). The passive channel is the
    correctness path; the seeded turn is the upgrade that makes the review
    undismissable where the harness supports it.

    Always exits 0. A SessionStart hook that fails takes orientation down with
    it, and there is no agent yet to read the traceback.
    """
    return dedent(
        """\
            #!/usr/bin/env python3
            \"\"\"Session-Start Handoff Advisement Hook (GHI #757).

            SessionStart hook. Surfaces the newest handoff and its advised steps
            so the review happens without the operator retyping the request each
            session.

            Binds by SEEDING the turn, never by refusing tool calls — the entry
            edge already blocks hard, and the advisement's problem was that it
            was skippable, not that it was unguarded. A handoff ADVISES; this
            hook never authorizes, and says so in the text it injects.

            Dual-channel: `additionalContext` is passive and universal (Codex
            has only this); `initialUserMessage` seeds a real first turn and is
            a Claude-side upgrade, never a correctness dependency.

            Thin adapter only: the decision is `gzkit.session_start.build_advisement`.

            Exit codes:
              0 - always (advisement never blocks)
            \"\"\"

            from __future__ import annotations

            import json
            import sys
            from datetime import UTC, datetime
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
                    from gzkit.session_start import build_advisement
                except ImportError:
                    sys.exit(0)

                root = _find_project_root(Path(cwd).resolve())
                now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
                advisement = build_advisement(root, now=now)
                if not advisement.present:
                    sys.exit(0)

                print(
                    json.dumps(
                        {
                            "hookSpecificOutput": {
                                "hookEventName": "SessionStart",
                                "additionalContext": advisement.text,
                            },
                            "initialUserMessage": advisement.text,
                        }
                    )
                )
                sys.exit(0)


            if __name__ == "__main__":
                main()
        """
    )
