"""gz content render command handler — ADR-0.0.34 § Decision item #4 (OBPI-0.0.34-04)."""

from __future__ import annotations

import sys
from pathlib import Path

from pydantic import ValidationError

from gzkit.content.models import CONTENT_MODELS
from gzkit.content.parse import parse
from gzkit.content.render import render


def content_render_cmd(*, file: str, as_type: str, vendor: str) -> None:
    """Handle ``gz content render <file> --as <type> [--vendor <vendor>]``.

    Parse the input file into a canonical model, then render and emit to stdout.
    Output is byte-identical to ``gzkit.content.render.render(model, vendor)``.

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

    rendered = render(model, vendor)
    if sys.stdout.isatty():
        from gzkit.content.tui.status import render_status_line  # noqa: PLC0415

        render_status_line(
            operation="rendered",
            source=file_path.name,
            result=vendor,
            byte_count=len(rendered),
        )
    print(rendered.decode("utf-8"), end="")
