#!/usr/bin/env python3
"""Verification Exit-Code Integrity Hook (GHI #589).

PreToolUse hook on Bash. Refuses a command that pipes a verifier
(`unittest`, `behave`, `mkdocs --strict`, `gz check`, any ARB-wrapped
verifier) into another process: the shell reports the LAST stage's exit
status, so a failing suite reads back as a green run.

The mechanical form of `.gzkit/rules/tests.md` § Verification exit-code
integrity, which was binding prose enforced by nothing since rule 0.8.0
(`docs/governance/advisory-rules-audit.md` row 66).

Thin adapter only: the decision is `gzkit.verifier_pipe_gate.decide`.

Exit codes:
  0 - Allow operation
  2 - Block operation (a verifier's exit status would be discarded)
"""

from __future__ import annotations

import json
import sys


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        sys.exit(0)

    try:
        from gzkit.verifier_pipe_gate import decide
    except ImportError:
        # Fail-open: gzkit unavailable is a plumbing failure, not a
        # governance signal.
        sys.exit(0)

    verdict = decide(
        str(payload.get("tool_name") or ""),
        payload.get("tool_input") or {},
    )
    if verdict.blocked:
        print(verdict.reason, file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
