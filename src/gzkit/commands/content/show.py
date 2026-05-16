"""gz content show command handler — ADR-0.0.34 § Decision item #4 (OBPI-0.0.34-04)."""

from __future__ import annotations

import sys
from pathlib import Path

from pydantic import ValidationError

from gzkit.content.models import CONTENT_MODELS
from gzkit.content.parse import parse


def content_show_cmd(*, file: str, as_type: str, as_json: bool) -> None:
    """Handle ``gz content show <file> --as <type> [--json]``.

    Default output: prose summary (Type, Title, field list).
    --json: model.model_dump_json(indent=2).
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

    try:
        text = file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Error reading {file_path}: {exc}", file=sys.stderr)
        sys.exit(2)

    try:
        model = parse(text, as_type, file_path=str(file_path))
    except ValueError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValidationError as exc:
        print(f"Validation error for {as_type} in {file_path}:\n{exc}", file=sys.stderr)
        sys.exit(1)

    if as_json:
        print(model.model_dump_json(indent=2))
        return

    # Prose summary
    data = model.model_dump()
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
    for field_name in sorted(data):
        value = data[field_name]
        if isinstance(value, list):
            print(f"  - {field_name}: <list, {len(value)} item(s)>")
        elif isinstance(value, dict):
            print(f"  - {field_name}: <dict, {len(value)} key(s)>")
        elif value is None:
            print(f"  - {field_name}: <none>")
        else:
            text_value = str(value)
            if len(text_value) > 60:
                text_value = text_value[:60] + "..."
            print(f"  - {field_name}: {text_value}")
