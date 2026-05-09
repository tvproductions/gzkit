"""Handler for ``gz complexity guide`` (OBPI-0.0.30-01).

Authoring-time complexity hint surface wrapping the OBPI-0.0.30-03 engine.
Emits ``AuthoringHint`` blocks for ``advise``-band crossings only; exit 3
is NOT used by this verb — the authoring surface never blocks. That is
``gz complexity advise``'s responsibility.

Exit codes (binding, REQ-0.0.30-01-02):

* ``0`` — success (no advise-band crossings) or hints emitted.
* ``1`` — user/config error (bad path, malformed flags).
* ``2`` — system/IO error (missing threshold table, AST parse error).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from gzkit.complexity.advisor.engine import EngineError
from gzkit.complexity.authoring.engine import (
    DEFAULT_RULE_PATH,
)
from gzkit.complexity.authoring.engine import (
    analyze as _engine_analyze,
)
from gzkit.complexity.authoring.hint import AuthoringHint

__all__ = [
    "DEFAULT_RULE_PATH",
    "complexity_guide_cmd",
]


def complexity_guide_cmd(
    *,
    path: str,
    json_output: bool = False,
    quiet: bool = False,  # noqa: ARG001
    verbose: bool = False,  # noqa: ARG001
) -> int:
    """Run authoring-time hint engine against ``path``; return exit code."""
    target = Path(path)
    if not target.exists():
        print(f"error: path does not exist: {path}", file=sys.stderr)
        raise SystemExit(1)

    if not DEFAULT_RULE_PATH.exists():
        print(
            f"error: threshold rule not found: {DEFAULT_RULE_PATH.as_posix()}",
            file=sys.stderr,
        )
        raise SystemExit(2)

    try:
        hints = _engine_analyze(target)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except PermissionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except EngineError as exc:
        print(f"error: engine: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if json_output:
        _render_json_output(hints)
    else:
        _render_hints_prose(hints)
    return 0


def _render_hints_prose(hints: tuple[AuthoringHint, ...]) -> None:
    """Emit one prose block per hint to stdout."""
    if not hints:
        print("No advise-band hints found.")
        return
    for hint in hints:
        print(f"── {hint.file_path}:{hint.start_line}-{hint.end_line} ──")
        print(f"Archetype : {hint.archetype}")
        print(f"Band      : {hint.precedence_band}")
        print(f"Guidance  : {hint.doctrinal_frame_headline}")
        print(f"Move      : {hint.recommended_move}")
        print()


def _render_json_output(hints: tuple[AuthoringHint, ...]) -> None:
    """Emit canonical AuthoringHint JSON array to stdout."""
    payload = [h.model_dump(mode="json") for h in hints]
    print(json.dumps(payload, indent=2))
