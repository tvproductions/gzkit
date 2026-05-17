"""gz content show command handler — ADR-0.0.34 § Decision item #4 (OBPI-0.0.34-04)."""

from __future__ import annotations

import sys
from pathlib import Path

from pydantic import ValidationError

from gzkit.content.models import CONTENT_MODELS
from gzkit.content.parse import parse


def _format_field_line(field_name: str, value: object) -> str:
    """Format one ``  - field: value`` summary line per type-aware rule."""
    if isinstance(value, list):
        return f"  - {field_name}: <list, {len(value)} item(s)>"
    if isinstance(value, dict):
        return f"  - {field_name}: <dict, {len(value)} key(s)>"
    if value is None:
        return f"  - {field_name}: <none>"
    text_value = str(value)
    if len(text_value) > 60:
        text_value = text_value[:60] + "..."
    return f"  - {field_name}: {text_value}"


def _read_source(file_path: Path) -> str:
    """Read file_path or exit with the canonical IO diagnostic."""
    try:
        return file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Error reading {file_path}: {exc}", file=sys.stderr)
        sys.exit(2)


def _parse_or_exit(text: str, as_type: str, file_path: Path):
    """Parse text into a content model or exit with the canonical diagnostic."""
    try:
        return parse(text, as_type, file_path=str(file_path))
    except ValueError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValidationError as exc:
        print(f"Validation error for {as_type} in {file_path}:\n{exc}", file=sys.stderr)
        sys.exit(1)


def _render_tty(as_type: str, file_path: Path, data: dict) -> None:
    """Render the Rich-panel prose summary on a TTY."""
    from gzkit.content.tui.panels import render_content_panel  # noqa: PLC0415

    lines = [f"Type: {as_type}", f"Source: {file_path}"]
    if "title" in data:
        lines.insert(0, f"Title: {data['title']}")
    lines.append("")
    lines.append("Fields:")
    lines.extend(_format_field_line(name, data[name]) for name in sorted(data))
    title = data.get("title") or data.get("slug") or as_type
    render_content_panel(title=f"{as_type}: {title}", body="\n".join(lines))


def _render_plain(as_type: str, file_path: Path, data: dict) -> None:
    """Render the grep-friendly plain-text prose summary."""
    print(f"Type: {as_type}")
    if "title" in data:
        print(f"Title: {data['title']}")
    if "slug" in data:
        print(f"Slug: {data['slug']}")
    if "version" in data:
        print(f"Version: {data['version']}")
    print(f"Source: {file_path}")
    print()
    print("Fields:")
    for name in sorted(data):
        print(_format_field_line(name, data[name]))


def content_show_cmd(*, file: str, as_type: str, as_json: bool, plain: bool = False) -> None:
    """Handle ``gz content show <file> --as <type> [--json] [--plain]``.

    Default output: prose summary (Type, Title, field list).
    --json: model.model_dump_json(indent=2).
    --plain: suppress Rich panel even on a TTY.
    Exit 0 on success, 1 on parse/validation error, 2 on IO error.
    """
    file_path = Path(file)

    if as_type not in CONTENT_MODELS:
        print(
            f"Error: unknown content type {as_type!r}. "
            f"Valid types: {', '.join(sorted(CONTENT_MODELS))}",
            file=sys.stderr,
        )
        sys.exit(1)

    text = _read_source(file_path)
    model = _parse_or_exit(text, as_type, file_path)

    if as_json:
        print(model.model_dump_json(indent=2))
        return

    data = model.model_dump()
    if sys.stdout.isatty() and not plain:
        _render_tty(as_type, file_path, data)
    else:
        _render_plain(as_type, file_path, data)
