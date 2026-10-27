#!/usr/bin/env python3
"""MX Awareness Hook (ADR-0.0.74, OBPI-0.0.74-07).

UserPromptSubmit hook — injects the MX banner to stdout on every agent turn
while the MX marker is present. Stdout content is injected as agent context
by the Claude Code harness on each turn.

Per-turn guarantee (not agent memory): an agent drifting across edit/read
turns still receives the hangar reminder every turn. The hook reads the
marker via a stdlib-only fallback so the banner fires even when gz itself
is broken (the MX premise).

Fail-open contract: hook failure must NOT block agent turns — always exits 0.

Exit codes:
  0 - Always (fail-open; turn must always begin)
"""

import json
import os
import sys


def _banner_stdlib(cwd: str | None) -> str:
    """Stdlib-only marker read — the gzkit-import-free fallback."""
    from pathlib import Path

    _BANNER = (
        "MX MODE ACTIVE — most guards advisory; gate5_invariants and the PRIME DIRECTIVE still bind"
    )
    _MARKER = (".gzkit", "mx.json")

    start = Path(cwd).resolve() if cwd else Path.cwd()
    for candidate in (start, *start.parents):
        if not (candidate / ".gzkit").is_dir():
            continue
        path = candidate.joinpath(*_MARKER)
        if not path.is_file():
            return ""
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except OSError, ValueError:
            return _BANNER
        if isinstance(raw, dict) and raw.get("mode") == "safe":
            contract = str(raw.get("contract") or "<no contract recorded>")
            return (
                "SAFE MODE ACTIVE — OBPI initiation and brief "
                f"ceremony are suspended under {contract}; most guards "
                "advisory; slow alarms off, lint and fast static checks on; "
                "gate5_invariants, the ledger through gz verbs and operator PII "
                "still bind; every act is one commit with its trailer; what it "
                "breaks goes on the punch list"
            )
        return _BANNER
    return ""


def main() -> int:
    """Run the awareness hook; always exits 0 (fail-open)."""
    cwd: str | None = None
    try:
        payload = json.load(sys.stdin)
        cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR")
    except Exception:
        pass

    banner = ""
    try:
        from pathlib import Path

        from gzkit.mx.awareness import _find_project_root, get_banner

        root = _find_project_root(Path(cwd).resolve() if cwd else None)
        banner = get_banner(root)
    except Exception:
        banner = _banner_stdlib(cwd)

    if banner:
        sys.stdout.write(banner + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
