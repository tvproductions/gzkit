"""Anchor resolvers for gzkit.justify.

`resolve_anchor` accepts three input shapes:

- ``"GHI-<N>"`` or ``"#<N>"`` — resolves via ``gh issue view <N>`` subprocess
- ``"OBPI-<X.Y.Z>-<NN>"`` — resolves by filename glob under ``docs/design/adr/``
- ``raw=None`` with ``draft_text`` and ``draft_slug`` — literal draft passthrough

The resolver is pure: it reads the filesystem or invokes ``gh``/``git`` via
the canonical :func:`gzkit.utils.run_exec` wrapper, but emits nothing to
stdout/stderr and never mutates the filesystem.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from gzkit.justify.models import AnchorRef, AnchorResolutionError
from gzkit.utils import run_exec

_GHI_PATTERN = re.compile(r"^(?:GHI-|#)(\d+)$")
_OBPI_PATTERN = re.compile(r"^OBPI-\d+\.\d+\.\d+-\d+$")
_SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")

_ACCEPTED_SHAPES = (
    "accepted anchor shapes: "
    "'GHI-<N>' or '#<N>' (GHI), "
    "'OBPI-<X.Y.Z>-<NN>' (OBPI brief), "
    "or raw=None with draft_text+draft_slug (draft)"
)


def resolve_anchor(
    raw: str | None,
    *,
    draft_text: str | None = None,
    draft_slug: str | None = None,
    project_root: Path | None = None,
) -> AnchorRef:
    """Resolve a raw anchor string into a populated :class:`AnchorRef`.

    Raises:
        ValueError: if the input shape is malformed (for any of the three
            accepted kinds), or for invalid draft inputs.
        AnchorResolutionError: if a structurally-valid anchor cannot be
            resolved to a concrete artifact (e.g. missing brief, ``gh``
            unavailable, zero/multiple filename matches).

    """
    root = project_root if project_root is not None else Path.cwd()

    if raw is None:
        if draft_text is None or not draft_text.strip():
            raise ValueError(f"draft anchor requires non-empty draft_text; {_ACCEPTED_SHAPES}")
        if draft_slug is None or not _SLUG_PATTERN.match(draft_slug):
            raise ValueError(
                "draft anchor requires a kebab-case draft_slug matching "
                f"^[a-z][a-z0-9-]*$; got {draft_slug!r}; {_ACCEPTED_SHAPES}"
            )
        return _resolve_draft(draft_text=draft_text, draft_slug=draft_slug)

    ghi_match = _GHI_PATTERN.match(raw)
    if ghi_match:
        return _resolve_ghi(number=ghi_match.group(1), project_root=root)

    if _OBPI_PATTERN.match(raw):
        return _resolve_obpi(identifier=raw, project_root=root)

    raise ValueError(f"malformed anchor {raw!r}; {_ACCEPTED_SHAPES}")


def _resolve_ghi(*, number: str, project_root: Path) -> AnchorRef:
    rc, stdout, stderr = run_exec(
        ["gh", "issue", "view", number, "--json", "number,title,body,labels,author"],
        cwd=project_root,
    )
    if rc != 0 or not stdout.strip():
        raise AnchorResolutionError(f"gh issue view {number} failed (rc={rc}); stderr={stderr!r}")
    try:
        data: dict[str, Any] = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise AnchorResolutionError(
            f"gh issue view {number} returned non-JSON output: {exc}"
        ) from exc

    labels_raw = data.get("labels") or []
    labels = tuple(
        label["name"] if isinstance(label, dict) and "name" in label else str(label)
        for label in labels_raw
    )
    author_raw = data.get("author")
    author = author_raw.get("login") if isinstance(author_raw, dict) else author_raw

    return AnchorRef(
        kind="ghi",
        identifier=f"GHI-{number}",
        title=data.get("title"),
        body=data.get("body"),
        labels=labels,
        author=author,
    )


def _resolve_obpi(*, identifier: str, project_root: Path) -> AnchorRef:
    matches = sorted(project_root.glob(f"docs/design/adr/**/obpis/{identifier}-*.md"))
    if not matches:
        raise AnchorResolutionError(
            f"no OBPI brief found matching 'docs/design/adr/**/obpis/{identifier}-*.md' "
            f"under {project_root}"
        )
    if len(matches) > 1:
        joined = ", ".join(str(p) for p in matches)
        raise AnchorResolutionError(f"multiple OBPI briefs match {identifier}: {joined}")
    brief = matches[0]
    try:
        body = brief.read_text(encoding="utf-8")
    except OSError as exc:
        raise AnchorResolutionError(
            f"OBPI brief for {identifier} at {brief} unreadable: {exc}"
        ) from exc
    return AnchorRef(
        kind="obpi",
        identifier=identifier,
        body=body,
        source_path=str(brief),
    )


def _resolve_draft(*, draft_text: str, draft_slug: str) -> AnchorRef:
    return AnchorRef(
        kind="draft",
        draft_text=draft_text,
        draft_slug=draft_slug,
        body=draft_text,
    )
