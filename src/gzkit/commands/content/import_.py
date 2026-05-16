"""gz content import command handler — ADR-0.0.34 § Decision item #3."""

from __future__ import annotations

import sys
from pathlib import Path

from pydantic import ValidationError

from gzkit.content.models import CONTENT_MODELS
from gzkit.content.parse import parse
from gzkit.content.render import render


def content_import_cmd(*, file: str, as_type: str, write_path: str | None) -> None:
    """Handle ``gz content import <file> --as <type>``."""
    file_path = Path(file)

    # Validate type before reading file (fast-fail for unknown type)
    if as_type not in CONTENT_MODELS:
        print(
            f"Error: unknown content type {as_type!r}. "
            f"Valid types: {', '.join(sorted(CONTENT_MODELS))}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Read input file
    try:
        text = file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Error reading {file_path}: {exc}", file=sys.stderr)
        sys.exit(2)

    # Parse into model
    try:
        model = parse(text, as_type, file_path=str(file_path))
    except ValueError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValidationError as exc:
        print(f"Validation error for {as_type} in {file_path}:\n{exc}", file=sys.stderr)
        sys.exit(1)

    # Emit JSON to stdout
    print(model.model_dump_json(indent=2))

    # Optionally write re-rendered canonical form
    if write_path is not None:
        out_path = Path(write_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        rendered = render(model, "claude")
        out_path.write_bytes(rendered)
