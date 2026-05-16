"""gz content list command handler — ADR-0.0.34 § Decision item #4 (OBPI-0.0.34-04)."""

from __future__ import annotations

import json
import sys

from gzkit.content.models import CONTENT_MODELS


def content_list_cmd(*, type_filter: str | None, as_json: bool) -> None:
    """Handle ``gz content list [--type <type>] [--json]``.

    Default output: human-readable two-column table (Type | Description).
    --json: array of {type, description} objects.
    Exit 0 on success, 1 on unknown --type filter.
    """
    if type_filter is not None and type_filter not in CONTENT_MODELS:
        print(
            f"Error: unknown content type {type_filter!r}. "
            f"Valid types: {', '.join(sorted(CONTENT_MODELS))}",
            file=sys.stderr,
        )
        sys.exit(1)

    types = sorted(CONTENT_MODELS)
    if type_filter is not None:
        types = [type_filter]

    rows: list[dict[str, str]] = []
    for type_name in types:
        model_cls = CONTENT_MODELS[type_name]
        # First line of docstring as description; fallback to class name
        description = (model_cls.__doc__ or type_name).strip().split("\n", 1)[0]
        rows.append({"type": type_name, "description": description})

    if as_json:
        print(json.dumps(rows, indent=2))
        return

    # Human-readable table
    type_col_width = max(len("Type"), max((len(r["type"]) for r in rows), default=0))
    print(f"{'Type'.ljust(type_col_width)}  Description")
    print(f"{'-' * type_col_width}  {'-' * len('Description')}")
    for row in rows:
        print(f"{row['type'].ljust(type_col_width)}  {row['description']}")
