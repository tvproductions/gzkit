"""Authoring-time complexity hints integration for gz justify (OBPI-0.0.30-05).

Provides ``gather_hints_markdown`` which reads the allowed-paths section of an
OBPI brief, runs the authoring engine on any ``.py`` files listed, and returns
a markdown string summarising any advise-band crossings.

Fail-open design: engine errors never block justify. When analysis fails,
the function returns ``("", [warning_message])`` and appends a structured
record to ``.gzkit/insights/justify-failures.jsonl``.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from gzkit.complexity.authoring.engine import analyze
from gzkit.complexity.authoring.hint import AuthoringHint
from gzkit.justify.models import AnchorRef

__all__ = ["gather_hints_markdown"]

_FAILURES_LOG_RELPATH = Path(".gzkit/insights/justify-failures.jsonl")


def gather_hints_markdown(
    anchor_ref: AnchorRef,
    *,
    project_root: Path | None = None,
) -> tuple[str, list[str]]:
    """Return ``(markdown, warnings)`` for advise-band complexity hints.

    Returns ``("", [])`` immediately when:

    - ``anchor_ref.source_path`` is ``None``
    - ``anchor_ref.kind != "obpi"``
    - The brief has no ``.py`` paths in ``## Allowed Paths``
    - The engine finds no advise-band crossings

    Returns ``("", [warning])`` and logs to ``.gzkit/insights/justify-failures.jsonl``
    on engine errors (fail-open contract — engine errors never block justify).
    """
    if anchor_ref.source_path is None or anchor_ref.kind != "obpi":
        return "", []

    brief_path = Path(anchor_ref.source_path)
    try:
        content = brief_path.read_text(encoding="utf-8")
    except OSError:
        return "", []

    allowed_paths = _extract_allowed_paths(content)
    py_paths = [p for p in allowed_paths if p.endswith(".py") or p == "**/*.py"]
    if not py_paths:
        return "", []

    root = project_root or Path.cwd()
    all_hints: list[AuthoringHint] = []
    warnings: list[str] = []

    for rel_path in py_paths:
        resolved = root / rel_path
        try:
            hints = analyze(resolved)
            all_hints.extend(hints)
        except Exception as exc:  # noqa: BLE001 — fail-open at integration boundary
            msg = f"justify-hints: engine error: {exc}"
            warnings.append(msg)
            _log_failure(
                obpi_id=anchor_ref.identifier or "",
                reason=str(exc),
                paths=py_paths,
                project_root=root,
            )

    if not all_hints:
        return "", warnings

    markdown = _format_hints(all_hints)
    return markdown, warnings


def _extract_allowed_paths(content: str) -> list[str]:
    """Parse the ``## Allowed Paths`` section and return bare path tokens."""
    in_section = False
    paths: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Allowed Paths"):
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section and stripped.startswith("- "):
            token = stripped[2:].strip()
            if "—" in token:
                token = token.split("—", 1)[0].strip()
            token = token.strip("`").strip()
            if token:
                paths.append(token)
    return paths


def _format_hints(hints: list[AuthoringHint]) -> str:
    """Format hints as a markdown bullet list."""
    lines: list[str] = []
    for hint in hints:
        lines.append(
            f"- **{hint.file_path}:{hint.start_line}-{hint.end_line}**"
            f" — {hint.archetype} ({hint.precedence_band})"
        )
        lines.append(f"  Guidance: {hint.doctrinal_frame_headline}")
        lines.append(f"  Move: {hint.recommended_move}")
    return "\n".join(lines)


def _log_failure(*, obpi_id: str, reason: str, paths: list[str], project_root: Path) -> None:
    """Append a structured failure record to the justify-failures log."""
    record = {
        "ts": datetime.now(UTC).isoformat(),
        "event": "justify_hints_failure",
        "obpi_id": obpi_id,
        "reason": reason,
        "paths": [Path(p).as_posix() for p in paths],
    }
    log_path = project_root / _FAILURES_LOG_RELPATH
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open(mode="a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError:
        pass
