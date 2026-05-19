"""gz governance render command implementation (ADR-0.0.37, OBPI-0.0.37-02)."""

from __future__ import annotations

import difflib
import sys
from pathlib import Path

from gzkit.commands.common import get_project_root
from gzkit.governance.compose import render_agents_md
from gzkit.governance.invariants import load_invariants

_SUPPORTED_TARGETS = frozenset({"agents-md"})
_TEMPLATE_ROOT = Path(__file__).parent.parent / "templates"


def governance_render_cmd(
    *,
    target: str,
    check: bool = False,
    stdout: bool = False,
) -> None:
    """Implement ``gz governance render --target agents-md``.

    --check: byte-compare rendered against committed AGENTS.md; exit 3 on drift.
    --stdout: emit rendered bytes to stdout; do not write file.
    default: write rendered bytes to AGENTS.md at repo root.

    No ledger events are emitted here (composition_rendered is OBPI-03 scope).
    Unsupported targets exit non-zero with "unsupported target" message.
    """
    if target not in _SUPPORTED_TARGETS:
        print(
            f"unsupported target: {target!r}. Supported targets: {sorted(_SUPPORTED_TARGETS)}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    root = get_project_root()
    invariants = load_invariants(root)
    rendered = render_agents_md(invariants, _TEMPLATE_ROOT)

    if stdout:
        stdout_dest = getattr(sys.stdout, "buffer", None)
        if stdout_dest is not None:
            stdout_dest.write(rendered)
        else:
            sys.stdout.write(rendered.decode("utf-8"))
        return

    agents_path = root / "AGENTS.md"

    if check:
        current = agents_path.read_bytes() if agents_path.exists() else b""
        if current == rendered:
            return
        current_lines = current.decode("utf-8", errors="replace").splitlines(keepends=True)
        rendered_lines = rendered.decode("utf-8").splitlines(keepends=True)
        diff_lines = list(
            difflib.unified_diff(
                current_lines,
                rendered_lines,
                fromfile="AGENTS.md",
                tofile="<rendered>",
                n=3,
            )
        )[:50]
        sys.stderr.writelines(diff_lines)
        raise SystemExit(3)

    agents_path.write_bytes(rendered)
    print(f"Wrote {len(rendered)} bytes to {agents_path.as_posix()}")
