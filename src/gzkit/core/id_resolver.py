"""The identity seam's resolver: which artifact an id names, and its parent.

Drydock RO-2 tranche 1 (`docs/governance/harbor-ro2-identity-seam.md` § The seam,
items 2 and 3). The grammar bodies live beside this module in
:mod:`gzkit.core.models`; this module answers the two questions every reader used
to answer for itself from an id's spelling:

- :func:`resolve` names the canonical id, its kind, and whether it is active,
  parked or withdrawn. It follows the rename fold, expands a short id only across
  a ``-`` separator through :func:`gzkit.artifact_prefix.active_prefix_matches`,
  and fails closed with every candidate named when an id stays ambiguous. It never
  takes a first match, and no width enters the match, so ``OBPI-0.1.0-1`` never
  names ``OBPI-0.1.0-10-…``.
- :func:`parent_of` reads stored fields: an ADR's or OBPI's ``parent`` from the
  ledger graph, else an OBPI's brief frontmatter, and a REQ's owning brief.
  Deriving a parent from an id's spelling survives only in
  :func:`_parent_by_spelling`, the one marked fallback, and every link it makes
  says ``source="spelling"`` so it can be counted while RO-3's ``member_of`` lands.

The resolver is pure over an :class:`IdentityContext`; :func:`load_identity_context`
takes the ledger and the project root as parameters and is the only reader of
either (`hexagonal-architecture.md` rule 4).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from gzkit.artifact_prefix import active_prefix_matches
from gzkit.core.models import IdKind, id_kind, spelled_parent
from gzkit.frontmatter import read_frontmatter
from gzkit.obpi_lifecycle import fold_renames
from gzkit.triangle import extract_reqs_from_brief

__all__ = [
    "IdResolutionError",
    "IdentityContext",
    "LedgerReader",
    "ParentLink",
    "Resolution",
    "brief_files",
    "load_identity_context",
    "parent_of",
    "resolve",
    "resolve_full",
]

State = Literal["active", "parked", "withdrawn"]


class IdResolutionError(ValueError):
    """An id names no artifact, or more than one; ``candidates`` names them."""

    def __init__(self, identifier: str, message: str, candidates: Iterable[str] = ()) -> None:
        """Carry the id and the candidates it could name, sorted."""
        self.identifier = identifier
        self.candidates = tuple(sorted(candidates))
        super().__init__(message)


class Resolution(BaseModel):
    """The artifact an id names."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    identifier: str = Field(..., description="The id as the caller gave it")
    canonical_id: str = Field(..., description="The id the artifact is recorded under")
    kind: IdKind = Field(..., description="ADR, OBPI, REQ or TASK")
    state: State = Field(..., description="active, parked or withdrawn")


class ParentLink(BaseModel):
    """An artifact's parent and where the seam read it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    parent_id: str = Field(..., description="The parent's id")
    source: Literal["ledger", "brief", "spelling"] = Field(
        ..., description="A stored field (ledger, brief) or the marked spelling fallback"
    )


class IdentityContext(BaseModel):
    """Everything the resolver reads, gathered once by :func:`load_identity_context`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    graph: dict[str, dict[str, Any]] = Field(..., description="Ledger artifact graph")
    renames: dict[str, str] = Field(default_factory=dict, description="Folded renames")
    brief_parents: dict[str, str] = Field(
        default_factory=dict, description="Brief frontmatter id -> its parent field"
    )
    req_owners: dict[str, tuple[str, ...]] = Field(
        default_factory=dict, description="REQ id -> frontmatter ids of the briefs listing it"
    )
    task_obpis: dict[str, str] = Field(
        default_factory=dict, description="Started TASK id -> its task_started obpi_id"
    )


class LedgerReader(Protocol):
    """The two ledger reads the loader needs."""

    def get_artifact_graph(self) -> Mapping[str, Mapping[str, Any]]:
        """Return the artifact graph keyed by id."""
        ...

    def read_all(self) -> list[Any]:
        """Return the corrected event stream."""
        ...


def _state(info: Mapping[str, Any]) -> State:
    if info.get("withdrawn"):
        return "withdrawn"
    if info.get("parked"):
        return "parked"
    return "active"


def _resolve_artifact(identifier: str, kind: IdKind, context: IdentityContext) -> Resolution:
    canonical = context.renames.get(identifier, identifier)
    graph_type = kind.value.lower()
    info = context.graph.get(canonical)
    if info is not None and info.get("type") == graph_type:
        return Resolution(
            identifier=identifier, canonical_id=canonical, kind=kind, state=_state(info)
        )
    hits = active_prefix_matches(context.graph, canonical, artifact_type=graph_type)
    if len(hits) == 1:
        return Resolution(
            identifier=identifier,
            canonical_id=hits[0],
            kind=kind,
            state=_state(context.graph[hits[0]]),
        )
    if hits:
        named = ", ".join(sorted(hits))
        msg = f"{identifier} is ambiguous: it names {len(hits)} {kind.value}s ({named})"
        raise IdResolutionError(identifier, msg, hits)
    msg = f"{identifier} names no {kind.value} in the ledger"
    raise IdResolutionError(identifier, msg)


def _req_owner(identifier: str, context: IdentityContext) -> tuple[Resolution, ParentLink]:
    """Return the OBPI that owns a REQ, and how the seam found it.

    The owner is the brief that lists the REQ. With no such brief, a parked or
    withdrawn OBPI the REQ's spelling names still owns it: pool demotion removes
    the brief and parks the OBPI, and the REQs it declared stay recorded as such.
    A REQ whose spelled OBPI is live but does not list it names nothing.
    """
    owners: dict[str, Resolution] = {}
    for brief_id in context.req_owners.get(identifier, ()):
        try:
            owner = _resolve_artifact(brief_id, IdKind.OBPI, context)
        except IdResolutionError:
            continue
        owners[owner.canonical_id] = owner
    active = [key for key, owner in owners.items() if owner.state == "active"]
    chosen = active or list(owners)
    if len(chosen) == 1:
        owner = owners[chosen[0]]
        return owner, ParentLink(parent_id=owner.canonical_id, source="brief")
    if chosen:
        msg = f"{identifier} is listed by {len(chosen)} OBPI briefs ({', '.join(sorted(chosen))})"
        raise IdResolutionError(identifier, msg, chosen)
    spelled = _parent_by_spelling(identifier, IdKind.REQ)
    try:
        owner = _resolve_artifact(spelled.parent_id, IdKind.OBPI, context)
    except IdResolutionError:
        owner = None
    if owner is not None and owner.state != "active":
        return owner, ParentLink(parent_id=owner.canonical_id, source="spelling")
    msg = f"{identifier} is listed by no OBPI brief the ledger knows"
    raise IdResolutionError(identifier, msg)


def _resolve_req(identifier: str, context: IdentityContext) -> Resolution:
    owner, _ = _req_owner(identifier, context)
    return Resolution(
        identifier=identifier, canonical_id=identifier, kind=IdKind.REQ, state=owner.state
    )


def resolve(identifier: str, context: IdentityContext) -> Resolution:
    """Return the artifact *identifier* names, or raise :class:`IdResolutionError`."""
    try:
        kind = id_kind(identifier)
    except ValueError as exc:
        raise IdResolutionError(identifier, str(exc)) from exc
    if kind is IdKind.REQ:
        return _resolve_req(identifier, context)
    if kind is IdKind.TASK:
        if identifier in context.task_obpis:
            return Resolution(
                identifier=identifier, canonical_id=identifier, kind=kind, state="active"
            )
        msg = f"{identifier} names no started TASK in the ledger"
        raise IdResolutionError(identifier, msg)
    return _resolve_artifact(identifier, kind, context)


def resolve_full(identifier: str, context: IdentityContext) -> Resolution:
    """Return :func:`resolve`'s artifact under the full slug the pipeline records.

    A short-form record can sit in the graph beside the slug-form record of the
    same OBPI, so :func:`resolve` stops at the short key. A producer that books
    events (``gz task start``, GHI #653) must write the slug, so when exactly one
    active key extends the resolved id across a ``-`` that key is the answer.
    """
    resolution = resolve(identifier, context)
    if resolution.kind not in (IdKind.ADR, IdKind.OBPI):
        return resolution
    hits = active_prefix_matches(
        context.graph, resolution.canonical_id, artifact_type=resolution.kind.value.lower()
    )
    if len(hits) != 1:
        return resolution
    return Resolution(
        identifier=identifier,
        canonical_id=hits[0],
        kind=resolution.kind,
        state=_state(context.graph[hits[0]]),
    )


def _parent_by_spelling(identifier: str, kind: IdKind) -> ParentLink:
    """Derive a parent from an id's spelling: the seam's one marked fallback.

    Only reached for an artifact with no stored parent field, and only for an id
    the seam's grammar parses: ``OBPI-<semver>-…`` → ``ADR-<semver>``;
    ``REQ-<semver>-<NN>-<MM>`` → ``OBPI-<semver>-<NN>``;
    ``TASK-<semver>-<NN>-<MM>-<PP>`` → ``REQ-<semver>-<NN>-<MM>``.
    """
    parent = spelled_parent(identifier) if id_kind(identifier) is kind else None
    if parent is None:
        msg = f"{identifier} is not a well-formed {kind.value} id, so no parent can be read from it"
        raise IdResolutionError(identifier, msg)
    return ParentLink(parent_id=parent, source="spelling")


def parent_of(identifier: str, context: IdentityContext) -> ParentLink | None:
    """Return the parent of the artifact *identifier* names, from stored fields first.

    ``None`` means the artifact has no parent (an ADR the graph records none for).
    Raises :class:`IdResolutionError` when *identifier* names no single artifact.
    """
    resolution = resolve(identifier, context)
    canonical = resolution.canonical_id
    if resolution.kind in (IdKind.ADR, IdKind.OBPI):
        stored = context.graph.get(canonical, {}).get("parent")
        if isinstance(stored, str) and stored:
            return ParentLink(parent_id=stored, source="ledger")
        briefed = context.brief_parents.get(canonical)
        if briefed:
            return ParentLink(parent_id=briefed, source="brief")
        if resolution.kind is IdKind.ADR:
            return None
    if resolution.kind is IdKind.REQ:
        return _req_owner(canonical, context)[1]
    return _parent_by_spelling(canonical, resolution.kind)


def brief_files(project_root: Path, design_root: str) -> list[Path]:
    """Return every OBPI brief under the design root, sorted."""
    base = project_root / design_root / "adr"
    return sorted({*base.glob("**/obpis/*.md"), *base.glob("**/briefs/*.md")})


def load_identity_context(
    ledger: LedgerReader, project_root: Path, design_root: str
) -> IdentityContext:
    """Gather the graph, renames, brief index and started TASKs the resolver reads."""
    events = ledger.read_all()
    renames = fold_renames(
        (event.id, new_id)
        for event in events
        if event.event == "artifact_renamed"
        and isinstance(new_id := event.extra.get("new_id"), str)
    )
    task_obpis = {
        event.id: obpi
        for event in events
        if event.event == "task_started" and isinstance(obpi := event.extra.get("obpi_id"), str)
    }
    brief_parents: dict[str, str] = {}
    req_owners: dict[str, list[str]] = {}
    for path in brief_files(project_root, design_root):
        content = path.read_text(encoding="utf-8")
        fields = read_frontmatter(content).fields
        brief_id = fields.get("id", "")
        if not brief_id.startswith("OBPI-"):
            continue
        if fields.get("parent"):
            brief_parents[brief_id] = fields["parent"]
        for req in extract_reqs_from_brief(content, brief_id):
            req_owners.setdefault(str(req.id), []).append(brief_id)
    return IdentityContext(
        graph={key: dict(info) for key, info in ledger.get_artifact_graph().items()},
        renames=renames,
        brief_parents=brief_parents,
        req_owners={req: tuple(owners) for req, owners in req_owners.items()},
        task_obpis=task_obpis,
    )
