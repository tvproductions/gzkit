"""CLI dispatch for ``gz justify``.

Internal orchestration layer composed by ``gzkit.commands.justify_cmd``:
applies user-input policy checks (ADR rejection, draft-slug precondition,
output-path conflict), resolves the anchor, gathers evidence, renders the
scaffold, and routes output to stdout, the ``artifacts/justify/`` auto-path,
or an explicit ``--output`` path — returning exit codes per the CLI 4-code
doctrine (0 success, 1 user/config, 2 system/IO).
"""

from __future__ import annotations

import re
import sys
from datetime import UTC, datetime
from pathlib import Path

from gzkit.cli.helpers.exit_codes import (
    EXIT_SUCCESS,
    EXIT_SYSTEM_ERROR,
    EXIT_USER_ERROR,
)
from gzkit.justify.anchors import resolve_anchor
from gzkit.justify.complexity_hints import gather_hints_markdown
from gzkit.justify.evidence import gather_evidence
from gzkit.justify.models import AnchorResolutionError
from gzkit.justify.parser import (
    ValidateResult,
    WalkthroughParseError,
    parse_walkthrough,
)
from gzkit.justify.walkthrough import render_markdown, render_scaffold

ADR_REJECTION_MESSAGE = (
    "justify reasons about change instances (GHIs, OBPIs, drafts), "
    "not governance packages. Invoke on the tracking GHI or an OBPI under the ADR."
)

DRAFT_SLUG_REQUIRED_MESSAGE = "--draft-slug is required when --save is combined with --draft"

ANCHOR_OR_DRAFT_REQUIRED_MESSAGE = "justify: anchor or --draft is required"

_ADR_PATTERN = re.compile(r"^ADR-\d+\.\d+\.\d+$", re.IGNORECASE)


def handle_justify(
    *,
    anchor: str | None,
    save: bool,
    output: str | None,
    related: str | None,
    draft: str | None,
    draft_slug: str | None,
    now: datetime | None = None,
    project_root: Path | None = None,
) -> int:
    """Exit-code-returning dispatch for the ``justify`` subcommand."""
    if anchor is not None and _ADR_PATTERN.match(anchor.strip()):
        print(ADR_REJECTION_MESSAGE, file=sys.stderr)
        return EXIT_USER_ERROR

    if draft is not None and save and not draft_slug:
        print(DRAFT_SLUG_REQUIRED_MESSAGE, file=sys.stderr)
        return EXIT_USER_ERROR

    if output is not None and Path(output).exists():
        print(
            f"justify: output path already exists: {output}",
            file=sys.stderr,
        )
        return EXIT_USER_ERROR

    if anchor is None and draft is None:
        print(ANCHOR_OR_DRAFT_REQUIRED_MESSAGE, file=sys.stderr)
        return EXIT_USER_ERROR

    try:
        anchor_ref = resolve_anchor(
            anchor if draft is None else None,
            draft_text=draft,
            draft_slug=draft_slug,
            project_root=project_root,
        )
    except ValueError as exc:
        print(f"justify: {exc}", file=sys.stderr)
        return EXIT_USER_ERROR
    except AnchorResolutionError as exc:
        print(f"justify: {exc}", file=sys.stderr)
        return EXIT_SYSTEM_ERROR

    related_list = (
        [token.strip() for token in related.split(",") if token.strip()] if related else None
    )
    evidence = gather_evidence(
        anchor_ref,
        related=related_list,
        project_root=project_root,
    )
    hints_md, _hints_warnings = gather_hints_markdown(anchor_ref, project_root=project_root)
    walkthrough = render_scaffold(
        anchor_ref,
        evidence,
        now=now,
        complexity_hints_md=hints_md or None,
    )
    markdown = render_markdown(walkthrough)

    if output is not None:
        return _write_to_path(Path(output), markdown)
    if save:
        return _write_to_auto_path(
            markdown=markdown,
            anchor_ref_identifier=anchor_ref.identifier,
            draft_slug=draft_slug,
            now=now,
            project_root=project_root,
        )

    print(markdown)
    return EXIT_SUCCESS


def handle_validate(*, file: str | None, json_output: bool) -> int:
    """Validate a filled walkthrough markdown file (OBPI-0.0.19-03).

    Exit code doctrine:

    * 0 — parseable AND structurally complete (every section filled).
    * 1 — parseable but incomplete (lists unfilled ordinals) OR missing
      ``<file>`` argument / file-not-found.
    * 2 — parseable-level failure (malformed walkthrough markdown).

    ``--json`` emits a :class:`gzkit.justify.parser.ValidateResult` JSON
    payload to stdout instead of the human-readable sentence.
    """
    if not file:
        print("justify validate: <file> is required", file=sys.stderr)
        return EXIT_USER_ERROR

    path = Path(file)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"justify validate: file not found: {file}", file=sys.stderr)
        return EXIT_USER_ERROR
    except OSError as exc:
        result = ValidateResult(
            file_path=file,
            is_parseable=False,
            is_complete=False,
            unfilled_ordinals=[],
            parse_error=str(exc),
        )
        _emit_validate_output(result, json_output)
        return EXIT_SYSTEM_ERROR

    try:
        walkthrough = parse_walkthrough(text)
    except WalkthroughParseError as exc:
        result = ValidateResult(
            file_path=file,
            is_parseable=False,
            is_complete=False,
            unfilled_ordinals=[],
            parse_error=str(exc),
        )
        _emit_validate_output(result, json_output)
        return EXIT_SYSTEM_ERROR

    unfilled = sorted(s.ordinal for s in walkthrough.sections if not s.is_filled)
    is_complete = not unfilled
    result = ValidateResult(
        file_path=file,
        is_parseable=True,
        is_complete=is_complete,
        unfilled_ordinals=unfilled,
        parse_error=None,
    )
    _emit_validate_output(result, json_output)
    return EXIT_SUCCESS if is_complete else EXIT_USER_ERROR


def _emit_validate_output(result: ValidateResult, json_output: bool) -> None:
    if json_output:
        print(result.model_dump_json())
        return
    if not result.is_parseable:
        print(f"Walkthrough {result.file_path} could not be parsed: {result.parse_error}")
        return
    if result.is_complete:
        print(f"Walkthrough {result.file_path} is complete")
        return
    ordinals = ", ".join(str(o) for o in result.unfilled_ordinals)
    print(f"Walkthrough {result.file_path} is incomplete. Unfilled sections: {ordinals}")


def _write_to_path(path: Path, markdown: str) -> int:
    try:
        path.write_text(markdown, encoding="utf-8")
    except OSError as exc:
        print(f"justify: failed to write {path}: {exc}", file=sys.stderr)
        return EXIT_SYSTEM_ERROR
    return EXIT_SUCCESS


def _write_to_auto_path(
    *,
    markdown: str,
    anchor_ref_identifier: str | None,
    draft_slug: str | None,
    now: datetime | None,
    project_root: Path | None,
) -> int:
    slug_source = draft_slug or anchor_ref_identifier or "draft"
    slug = slug_source.strip("/").replace("/", "-")
    stamp = (now or datetime.now(UTC)).strftime("%Y%m%dT%H%M%SZ")
    root = project_root or Path.cwd()
    target = root / "artifacts" / "justify" / f"{slug}-{stamp}.md"
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(markdown, encoding="utf-8")
    except OSError as exc:
        print(f"justify: failed to write {target}: {exc}", file=sys.stderr)
        return EXIT_SYSTEM_ERROR
    return EXIT_SUCCESS
