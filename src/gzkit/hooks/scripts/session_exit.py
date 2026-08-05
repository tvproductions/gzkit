"""Session-exit bookmark hook script source (GHI #756).

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
