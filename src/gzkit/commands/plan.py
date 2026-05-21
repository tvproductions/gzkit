"""Plan command implementation."""

import re
import sys
from datetime import date
from pathlib import Path

from gzkit.commands.common import console, ensure_initialized, get_project_root
from gzkit.decomposition import build_checklist_seed, compute_scorecard, default_dimension_scores
from gzkit.ledger import Ledger, adr_created_event
from gzkit.templates import render_template

FOUNDATION_SEMVER_RE = re.compile(r"^0\.0\.\d+$")
_SEMVER_LITERAL_RE = re.compile(r"^\d+\.\d+\.\d+$")
# Canonical non-pool ADR id: ADR-<semver>-<slug>. Mirrors the non-pool branch
# of the schema `id` pattern in src/gzkit/schemas/adr.json (GHI #346). A bare
# `ADR-X.Y.Z` (no slug suffix) does NOT match — emitting it produced the
# GHI #494 bare-id `adr_created` regression.
CANONICAL_ADR_ID_RE = re.compile(r"^ADR-[0-9]+\.[0-9]+\.[0-9]+-[a-z0-9-]+$")

# ADR-0.0.35 § Decision item #6 — every foundation-kind ADR scaffolds with a
# `## Why foundation tier?` section between `## Persona` and `## Intent`,
# pre-populated with two author prompts: the invariance-test answer and the
# port-vs-adapter framing. The heading is byte-identical (sentence case,
# trailing question mark) so OBPI-04's validator can pin it. Feature- and
# pool-kind ADRs MUST NOT scaffold this section.
WHY_FOUNDATION_TIER_SECTION = """\
## Why foundation tier?

_[Author: Answer the invariance test in one sentence: "Without this ADR, would \
the project still be the project?" State yes and name the invariance.]_

_[Port-vs-adapter framing: Is this ADR a port (an abstract contract every \
implementation must honor) or an adapter (one implementation behind an existing port)?]_

"""


def _compose_canonical_adr_id(name: str, semver: str) -> str:
    """Compose the canonical ADR id from a CLI `name` argument and `semver`.

    Two shapes of `name` are accepted:

    - Already-prefixed (``name.startswith("ADR-")``): use verbatim.
    - Real slug (e.g. ``"agent-rule-placement-invariant"``): compose
      ``ADR-<semver>-<name>`` so the ledger, the on-disk directory, and
      the file name all share the same canonical slugged form.

    Bare-semver names (e.g. ``"0.0.27"``) and bare ``ADR-`` ids (e.g.
    ``"ADR-0.0.49"``) are rejected with ``ValueError``. Bare-id emission
    produced the GHI #279 / GHI #344 / GHI #494 shadow-row defect: a bare
    ``adr_created`` event diverges from the slugged on-disk directory and
    renders as two rows in ``gz adr report``. Closing the class requires
    fail-fast at composition time, not catch-up renames.
    """
    if name.startswith("ADR-"):
        if not CANONICAL_ADR_ID_RE.match(name):
            raise ValueError(
                f"name argument is a bare ADR id without a slug suffix "
                f"(got {name!r}). Non-pool ADR ids require the canonical "
                f"slug-form ADR-<semver>-<slug>; a bare id emits an "
                f"unslugged adr_created event and produces shadow rows in "
                f"`gz adr report` (GHI #279 / GHI #344 / GHI #494). Pass a "
                f"descriptive slug instead, e.g. "
                f"`gz plan create my-doctrine-name --semver {semver}`."
            )
        return name
    if _SEMVER_LITERAL_RE.match(name):
        raise ValueError(
            f"name argument must be a descriptive slug, not a bare semver "
            f"literal (got {name!r}). Bare-semver names emit unslugged "
            f"adr_created events and produce shadow rows in `gz adr report` "
            f"(GHI #279 / GHI #344). Pass a slug instead, e.g. "
            f"`gz plan create my-doctrine-name --semver {semver}`."
        )
    return f"ADR-{semver}-{name}"


def _reject_noncanonical_name(name: str, kind: str) -> None:
    """Reject non-canonical positional `name` for non-pool ADRs.

    Two non-canonical shapes are rejected fail-fast before any file or
    ledger write:

    - Bare semver literal (e.g. ``0.0.27``) — GHI #344.
    - Bare ``ADR-`` id with no slug suffix (e.g. ``ADR-0.0.49``) — GHI #494.

    Both silently discarded the slug under the prior contract and emitted a
    bare-ID ``adr_created`` event whose ledger row diverged from the slugged
    on-disk directory. Pool ADRs route through ``ADR-pool.<slug>``
    composition and are not affected.
    """
    if kind == "pool":
        return
    is_bare_semver = bool(_SEMVER_LITERAL_RE.match(name))
    is_bare_adr_id = name.startswith("ADR-") and not CANONICAL_ADR_ID_RE.match(name)
    if not (is_bare_semver or is_bare_adr_id):
        return
    shape = "ADR id" if is_bare_adr_id else "semver literal"
    console.print(
        f"[red]ERROR:[/red] name argument must be a descriptive slug, not a "
        f"bare {shape} (got {name!r}). Bare-id names emit unslugged "
        "adr_created events and produce shadow rows in `gz adr report` "
        "(GHI #279 / GHI #344 / GHI #494)."
    )
    console.print(
        "Pass a descriptive slug, e.g. "
        "[bold]gz plan create my-doctrine-name --semver <X.Y.Z>[/bold]."
    )
    sys.exit(1)


def _next_available_foundation_semver(foundation_root: Path) -> str:
    """Scan existing foundation/<id>/ dirs and return next available 0.0.N."""
    if not foundation_root.exists():
        return "0.0.1"
    max_n = -1
    for entry in foundation_root.iterdir():
        if not entry.is_dir():
            continue
        match = re.match(r"^ADR-0\.0\.(\d+)(?:-.*)?$", entry.name)
        if match:
            n = int(match.group(1))
            max_n = max(max_n, n)
    return f"0.0.{max_n + 1}" if max_n >= 0 else "0.0.1"


def _render_pool_adr(*, name: str, title: str, parent: str, lane: str) -> tuple[str, str, str]:
    """Render a pool ADR. Returns (adr_id, relative_dir, content)."""
    slug = name if name.startswith("ADR-pool.") else f"ADR-pool.{name}"
    content = render_template(
        "adr_pool",
        id=slug,
        title=title,
        parent=parent or "PRD-GZKIT-1.0.0",
        lane=lane,
        intent="",
        decision="",
        alternatives="",
    )
    return slug, "pool", content


def _validate_kind_and_semver(kind: str | None, semver: str, adrs_root: Path) -> None:
    """Enforce --kind required + kind/semver consistency. Exit 1 on violation.

    Covers REQ-0.0.17-02-01 (kind required), -02/-03/-06 (kind/semver binding).
    """
    if kind is None:
        console.print("[red]ERROR:[/red] --kind is required. Choose one of:")
        console.print("  [bold]foundation[/bold] — infrastructure ADR; requires --semver 0.0.x")
        console.print(
            "  [bold]feature[/bold]    — release-carrying end-user capability; "
            "requires --semver NOT matching 0.0.x"
        )
        console.print("  [bold]pool[/bold]       — backlog ADR; no semver required")
        sys.exit(1)

    if kind == "foundation" and not FOUNDATION_SEMVER_RE.match(semver):
        next_available = _next_available_foundation_semver(adrs_root / "foundation")
        console.print(
            f"[red]ERROR:[/red] --kind foundation requires --semver matching 0.0.x "
            f"(got {semver!r}). Next available foundation semver: "
            f"[bold]{next_available}[/bold]."
        )
        sys.exit(1)
    if kind == "feature" and FOUNDATION_SEMVER_RE.match(semver):
        console.print(
            f"[red]ERROR:[/red] --kind feature rejects 0.0.x semver (got {semver!r}). "
            "Feature ADRs carry release-carrying semver (0.y.z and up). "
            "If this is infrastructure work, use --kind foundation; "
            "if it is a backlog item, use --kind pool."
        )
        sys.exit(1)


def _build_scorecard_and_checklist(
    *,
    lane: str,
    semver: str,
    score_data_state: int | None,
    score_logic_engine: int | None,
    score_interface: int | None,
    score_observability: int | None,
    score_lineage: int | None,
    split_single_narrative: bool,
    split_surface_boundary: bool,
    split_state_anchor: bool,
    split_testability_ceiling: bool,
    baseline_selected: int | None,
) -> tuple[object, str]:
    """Compute the scorecard from CLI flags, defaulting any score left as None."""
    defaults = default_dimension_scores(lane, semver)
    scorecard = compute_scorecard(
        data_state=(defaults["data_state"] if score_data_state is None else score_data_state),
        logic_engine=(
            defaults["logic_engine"] if score_logic_engine is None else score_logic_engine
        ),
        interface=defaults["interface"] if score_interface is None else score_interface,
        observability=(
            defaults["observability"] if score_observability is None else score_observability
        ),
        lineage=defaults["lineage"] if score_lineage is None else score_lineage,
        split_single_narrative=1 if split_single_narrative else 0,
        split_surface_boundary=1 if split_surface_boundary else 0,
        split_state_anchor=1 if split_state_anchor else 0,
        split_testability_ceiling=1 if split_testability_ceiling else 0,
        baseline_selected=baseline_selected,
    )
    checklist_seed = build_checklist_seed(semver, scorecard.final_target_obpi_count)
    return scorecard, checklist_seed


def _render_adr_by_kind(
    *,
    kind: str,
    name: str,
    adr_title: str,
    semver: str,
    lane: str,
    canonical_parent: str,
    scorecard: object,
    checklist_seed: str,
    adrs_root: Path,
) -> tuple[str, Path]:
    """Render the ADR markdown and resolve its on-disk path. Returns (adr_id, adr_file)."""
    if kind == "pool":
        adr_id, rel_dir, content = _render_pool_adr(
            name=name, title=adr_title, parent=canonical_parent, lane=lane
        )
        adr_dir = adrs_root / rel_dir
    else:
        adr_id = _compose_canonical_adr_id(name, semver)
        # ADR-0.0.35 § Decision item #6 — only foundation-kind ADRs scaffold
        # the `## Why foundation tier?` section; feature-kind ADRs render an
        # empty string for the placeholder so no spurious heading appears.
        why_foundation_tier = WHY_FOUNDATION_TIER_SECTION if kind == "foundation" else ""
        content = render_template(
            "adr",
            id=adr_id,
            title=adr_title,
            semver=semver,
            lane=lane,
            parent=canonical_parent,
            kind=kind,
            status="Draft",
            date=date.today().isoformat(),
            decomposition_scorecard=scorecard.to_markdown(),  # ty: ignore[unresolved-attribute]
            checklist=checklist_seed,
            why_foundation_tier=why_foundation_tier,
        )
        sub = "foundation" if kind == "foundation" else "pre-release"
        adr_dir = adrs_root / sub / adr_id

    adr_file = adr_dir / f"{adr_id}.md"
    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file.write_text(content, encoding="utf-8")
    return adr_id, adr_file


def register_adr_in_ledger(
    *, canonical_parent: str, lane: str, adr_file: Path, ledger_path: Path
) -> None:
    """Append adr_created event and verify registration. Exit 2 on failure.

    Shared canonical-ADR ledger-registration helper: wielded by ``plan_cmd``
    (``gz plan create``) and by the ``gz interview adr`` scaffolder. Both
    non-pool ADR-creation surfaces emit ``adr_created`` through this single
    on-disk-derived path so neither can regress the bare-id class on its own
    (GHI #494 closed the scaffolder; GHI #505 routed the interview path here).

    GHI #494: the ``adr_created`` id is derived from the on-disk directory
    name (T1) rather than from an intermediate id variable, so the ledger
    event (T2) provably matches canonical on-disk truth. A directory name
    that is not canonical slug-form is refused fail-closed (exit 3) rather
    than recorded as a bare-id event that diverges from the directory.

    Idempotent: if an ``adr_created`` event already resolves to the id
    (via the ledger's rename-aware ``has_adr_created``), the append is
    skipped with a warning. Prevents the duplicate-emission class surfaced
    in GHI #279.
    """
    canonical_id = adr_file.parent.name
    if not CANONICAL_ADR_ID_RE.match(canonical_id):
        console.print(
            f"[red]ERROR:[/red] ADR file written at {adr_file} but its on-disk "
            f"directory name {canonical_id!r} is not a canonical ADR id; "
            "refusing to emit a bare-id adr_created event (GHI #494)."
        )
        console.print(
            "Rename the directory to ADR-<semver>-<slug> and run "
            "[bold]gz register-adrs --all[/bold] to recover."
        )
        sys.exit(3)
    ledger = Ledger(ledger_path)
    if ledger.has_adr_created(canonical_id):
        console.print(
            f"[yellow]WARNING:[/yellow] {canonical_id} already has an adr_created "
            "event; skipping duplicate emission."
        )
        return
    try:
        ledger.append(adr_created_event(canonical_id, canonical_parent, lane))
    except OSError as exc:
        console.print(
            f"[red]ERROR:[/red] ADR file created at {adr_file} but ledger write failed: {exc}"
        )
        console.print("Run [bold]gz register-adrs --all[/bold] to recover.")
        sys.exit(2)

    graph = ledger.get_artifact_graph()
    if canonical_id in graph:
        return
    if ledger.canonicalize_id(canonical_id) in graph:
        return
    console.print(
        f"[yellow]WARNING:[/yellow] ADR file written but {canonical_id} not found in ledger."
    )
    console.print("Run [bold]gz register-adrs --all[/bold] to recover.")
    sys.exit(2)


def plan_cmd(
    name: str,
    parent_obpi: str | None,
    semver: str,
    lane: str,
    title: str | None,
    score_data_state: int | None,
    score_logic_engine: int | None,
    score_interface: int | None,
    score_observability: int | None,
    score_lineage: int | None,
    split_single_narrative: bool,
    split_surface_boundary: bool,
    split_state_anchor: bool,
    split_testability_ceiling: bool,
    baseline_selected: int | None,
    kind: str | None,
    dry_run: bool,
) -> None:
    """Create a new ADR (optionally linked to an OBPI)."""
    config = ensure_initialized()
    project_root = get_project_root()
    adrs_root = project_root / config.paths.adrs

    _validate_kind_and_semver(kind, semver, adrs_root)
    # After _validate_kind_and_semver, kind is guaranteed non-None.
    assert kind is not None
    _reject_noncanonical_name(name, kind)

    adr_title = title or name.replace("-", " ").title()

    canonical_parent = parent_obpi or ""
    if canonical_parent:
        ledger_for_resolve = Ledger(project_root / config.paths.ledger)
        canonical_parent = ledger_for_resolve.resolve_artifact_id(canonical_parent)

    scorecard, checklist_seed = _build_scorecard_and_checklist(
        lane=lane,
        semver=semver,
        score_data_state=score_data_state,
        score_logic_engine=score_logic_engine,
        score_interface=score_interface,
        score_observability=score_observability,
        score_lineage=score_lineage,
        split_single_narrative=split_single_narrative,
        split_surface_boundary=split_surface_boundary,
        split_state_anchor=split_state_anchor,
        split_testability_ceiling=split_testability_ceiling,
        baseline_selected=baseline_selected,
    )

    if dry_run:
        if kind == "pool":
            sub = "pool"
        elif kind == "foundation":
            sub = "foundation"
        else:
            sub = "pre-release"
        adr_id_preview = (
            (name if name.startswith("ADR-pool.") else f"ADR-pool.{name}")
            if kind == "pool"
            else _compose_canonical_adr_id(name, semver)
        )
        adr_file_preview = (
            adrs_root
            / sub
            / (
                f"{adr_id_preview}.md"
                if kind == "pool"
                else f"{adr_id_preview}/{adr_id_preview}.md"
            )
        )
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create ADR: {adr_file_preview}")
        if kind != "pool":
            console.print(f"  Would append ledger event: adr_created ({adr_id_preview})")
        return

    _, adr_file = _render_adr_by_kind(
        kind=kind,
        name=name,
        adr_title=adr_title,
        semver=semver,
        lane=lane,
        canonical_parent=canonical_parent,
        scorecard=scorecard,
        checklist_seed=checklist_seed,
        adrs_root=adrs_root,
    )

    if kind == "pool":
        console.print(f"Created pool ADR: {adr_file}")
        return

    register_adr_in_ledger(
        canonical_parent=canonical_parent,
        lane=lane,
        adr_file=adr_file,
        ledger_path=project_root / config.paths.ledger,
    )
    console.print(f"Created ADR: {adr_file}")
