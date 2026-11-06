"""Anchor resolvers for gzkit.justify.

`resolve_anchor` accepts three input shapes:

- ``"GHI-<N>"`` or ``"#<N>"`` — resolves via ``gh issue view <N>`` subprocess
- ``"OBPI-<X.Y.Z>-<NN>"`` — resolves by filename glob under ``docs/design/adr/``
- ``raw=None`` with ``draft_text`` and ``draft_slug`` — literal draft passthrough

The resolver is pure: it reads the filesystem or invokes ``gh``/``git`` via
the canonical :func:`gzkit.utils.run_exec` wrapper, but emits nothing to
stdout/stderr and never mutates the filesystem.
"""

import json
import re
from pathlib import Path
from typing import Any

from gzkit.core.models import OBPI_SHORT_ID_BODY
from gzkit.justify.models import AnchorRef, AnchorResolutionError
from gzkit.utils import run_exec

_GHI_PATTERN = re.compile(r"^(?:GHI-|#)(\d+)$")
_OBPI_PATTERN = re.compile(rf"^{OBPI_SHORT_ID_BODY}$")
_SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")

_ACCEPTED_SHAPES = (
    "accepted anchor shapes: "
    "'GHI-<N>' or '#<N>' (GHI), "
    "'OBPI-<X.Y.Z>-<NN>' (OBPI brief), "
    "or raw=None with draft_text+draft_slug (draft)"
)


class DraftTextRequiredError(ValueError):
    """A draft anchor was given no non-empty draft text."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__(f"draft anchor requires non-empty draft_text; {_ACCEPTED_SHAPES}")


class DraftSlugInvalidError(ValueError):
    """A draft anchor's slug is not kebab-case."""

    def __init__(self, draft_slug: str | None) -> None:
        """Build the message from ``draft_slug``."""
        self.draft_slug = draft_slug
        super().__init__(
            "draft anchor requires a kebab-case draft_slug matching "
            f"^[a-z][a-z0-9-]*$; got {draft_slug!r}; {_ACCEPTED_SHAPES}"
        )


class MalformedAnchorError(ValueError):
    """A raw anchor matches none of the accepted shapes."""

    def __init__(self, raw: str) -> None:
        """Build the message from ``raw``."""
        self.raw = raw
        super().__init__(f"malformed anchor {raw!r}; {_ACCEPTED_SHAPES}")


class GhiViewFailedError(AnchorResolutionError):
    """``gh issue view`` failed or returned nothing."""

    def __init__(self, number: str, rc: int, stderr: str) -> None:
        """Build the message from ``number``, ``rc``, ``stderr``."""
        self.number = number
        self.rc = rc
        super().__init__(f"gh issue view {number} failed (rc={rc}); stderr={stderr!r}")


class GhiNonJsonError(AnchorResolutionError):
    """``gh issue view`` returned output that is not JSON."""

    def __init__(self, number: str, exc: json.JSONDecodeError) -> None:
        """Build the message from ``number``, ``exc``."""
        self.number = number
        super().__init__(f"gh issue view {number} returned non-JSON output: {exc}")


class ObpiBriefNotFoundError(AnchorResolutionError):
    """No OBPI brief file matches the identifier."""

    def __init__(self, identifier: str, project_root: Path) -> None:
        """Build the message from ``identifier``, ``project_root``."""
        self.identifier = identifier
        super().__init__(
            f"no OBPI brief found matching 'docs/design/adr/**/obpis/{identifier}-*.md' "
            f"under {project_root}"
        )


class ObpiBriefAmbiguousError(AnchorResolutionError):
    """More than one OBPI brief file matches the identifier."""

    def __init__(self, identifier: str, matches: list[Path]) -> None:
        """Build the message from ``identifier``, ``matches``."""
        self.identifier = identifier
        joined = ", ".join(str(p) for p in matches)
        super().__init__(f"multiple OBPI briefs match {identifier}: {joined}")


class ObpiBriefUnreadableError(AnchorResolutionError):
    """The matched OBPI brief file cannot be read."""

    def __init__(self, identifier: str, brief: Path, exc: OSError) -> None:
        """Build the message from ``identifier``, ``brief``, ``exc``."""
        self.identifier = identifier
        super().__init__(f"OBPI brief for {identifier} at {brief} unreadable: {exc}")


def resolve_anchor(
    raw: str | None,
    *,
    draft_text: str | None = None,
    draft_slug: str | None = None,
    project_root: Path | None = None,
) -> AnchorRef:
    """Resolve a raw anchor string into a populated :class:`AnchorRef`.

    A structurally-valid anchor that cannot be resolved to a concrete artifact
    (e.g. missing brief, ``gh`` unavailable, zero/multiple filename matches)
    propagates an :class:`AnchorResolutionError` subclass from its resolver.

    Returns:
        The resolved anchor: a draft anchor when ``raw`` is None, else the GHI or OBPI anchor
        ``raw`` names.

    Raises:
        DraftTextRequiredError: if a draft anchor has no non-empty draft text.
        DraftSlugInvalidError: if a draft anchor's slug is not kebab-case.
        MalformedAnchorError: if the input shape matches none of the accepted kinds.

    """
    root = project_root if project_root is not None else Path.cwd()

    if raw is None:
        if draft_text is None or not draft_text.strip():
            raise DraftTextRequiredError
        if draft_slug is None or not _SLUG_PATTERN.match(draft_slug):
            raise DraftSlugInvalidError(draft_slug)
        return _resolve_draft(draft_text=draft_text, draft_slug=draft_slug)

    ghi_match = _GHI_PATTERN.match(raw)
    if ghi_match:
        return _resolve_ghi(number=ghi_match.group(1), project_root=root)

    if _OBPI_PATTERN.match(raw):
        return _resolve_obpi(identifier=raw, project_root=root)

    raise MalformedAnchorError(raw)


def _resolve_ghi(*, number: str, project_root: Path) -> AnchorRef:
    rc, stdout, stderr = run_exec(
        ["gh", "issue", "view", number, "--json", "number,title,body,labels,author"],
        cwd=project_root,
    )
    if rc != 0 or not stdout.strip():
        raise GhiViewFailedError(number, rc, stderr)
    try:
        data: dict[str, Any] = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise GhiNonJsonError(number, exc) from exc

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
        raise ObpiBriefNotFoundError(identifier, project_root)
    if len(matches) > 1:
        raise ObpiBriefAmbiguousError(identifier, matches)
    brief = matches[0]
    try:
        body = brief.read_text(encoding="utf-8")
    except OSError as exc:
        raise ObpiBriefUnreadableError(identifier, brief, exc) from exc
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
