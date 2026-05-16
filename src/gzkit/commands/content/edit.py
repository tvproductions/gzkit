"""gz content edit command handler — ADR-0.0.34 § Decision item #4 (OBPI-0.0.34-04)."""

from __future__ import annotations

import contextlib
import os
import subprocess  # noqa: S404 — invoking $EDITOR is intentional
import sys
import tempfile
from pathlib import Path

from pydantic import ValidationError

from gzkit.content.models import CONTENT_MODELS
from gzkit.content.parse import parse
from gzkit.content.render import render


def content_edit_cmd(*, file: str, as_type: str, vendor: str) -> None:
    """Handle ``gz content edit <file> --as <type> [--vendor <vendor>]``.

    Open the file in $EDITOR (or $VISUAL). On editor exit, re-parse the edited
    content and re-validate. On validation failure, abort with the diagnostic
    and NEVER write a partial file. On success, atomically replace the original
    with the re-rendered canonical form.

    Exit 0 on success, 1 on user/config/validation error, 2 on IO error.
    """
    file_path = Path(file)

    if as_type not in CONTENT_MODELS:
        print(
            f"Error: unknown content type {as_type!r}. "
            f"Valid types: {', '.join(sorted(CONTENT_MODELS))}",
            file=sys.stderr,
        )
        sys.exit(1)

    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    if not editor:
        print(
            "Error: neither $VISUAL nor $EDITOR is set. "
            "Set one to your preferred editor (e.g. EDITOR=vim).",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        original_bytes = file_path.read_bytes()
    except FileNotFoundError:
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Error reading {file_path}: {exc}", file=sys.stderr)
        sys.exit(2)

    # Write current bytes to a temp file for editing.
    # Use delete=False so we can close the file and reopen it on Windows.
    with tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=file_path.suffix or ".md",
        prefix=f"gz-content-edit-{file_path.stem}-",
        delete=False,
    ) as tmp:
        tmp.write(original_bytes)
        tmp_path = Path(tmp.name)

    try:
        # Invoke the editor on the temp file
        try:
            result = subprocess.run([editor, str(tmp_path)], check=False)  # noqa: S603
        except OSError as exc:
            print(f"Error launching editor {editor!r}: {exc}", file=sys.stderr)
            sys.exit(1)

        if result.returncode != 0:
            print(
                f"Editor {editor!r} exited non-zero ({result.returncode}); "
                "aborting edit. Original file unchanged.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Re-read and re-validate
        try:
            edited_text = tmp_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Error reading edited content: {exc}", file=sys.stderr)
            sys.exit(2)

        try:
            model = parse(edited_text, as_type, file_path=str(file_path))
        except ValueError as exc:
            print(
                f"Parse error in edited content: {exc}\nOriginal file unchanged.",
                file=sys.stderr,
            )
            sys.exit(1)
        except ValidationError as exc:
            print(
                f"Validation error for {as_type}:\n{exc}\nOriginal file unchanged.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Re-render to canonical form, then atomic replace
        rendered = render(model, vendor)
        staging_path = file_path.with_suffix(file_path.suffix + ".tmp")
        try:
            staging_path.write_bytes(rendered)
            staging_path.replace(file_path)
        except OSError as exc:
            # Clean up staging file if replace failed mid-way
            if staging_path.exists():
                with contextlib.suppress(OSError):
                    staging_path.unlink()
            print(f"Error writing canonical form: {exc}", file=sys.stderr)
            sys.exit(2)
    finally:
        # Always clean up the temp file
        with contextlib.suppress(OSError):
            tmp_path.unlink()
