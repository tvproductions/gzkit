"""Register and migrate-semver command implementations."""

from pathlib import Path
from typing import Any

from rich.markup import escape

from gzkit.commands.common import (
    ADR_SEMVER_ID_RE,
    _is_pool_adr_id,
    console,
    ensure_initialized,
    get_project_root,
)
from gzkit.frontmatter import read_frontmatter_bytes
from gzkit.governance.adr_status_index import regenerate_adr_status_md
from gzkit.ledger import (
    Ledger,
    _extract_bare_adr_semver,
    adr_created_event,
    artifact_renamed_event,
    extract_bare_obpi_id,
    obpi_created_event,
)
from gzkit.models.foundation_grandfather import (
    GRANDFATHER_MANIFEST_REL,
    foundation_kind_is_closed,
    load_manifest,
)
from gzkit.sync import parse_artifact_metadata, scan_existing_artifacts

_GRANDFATHER_MANIFEST_REL = GRANDFATHER_MANIFEST_REL


def grandfathered_foundation_ids(project_root: Path) -> frozenset[str]:
    """Return the ADR ids in the closed foundation grandfather manifest (ADR-0.34.0)."""
    manifest_path = project_root / _GRANDFATHER_MANIFEST_REL
    if not manifest_path.is_file():
        return frozenset()
    try:
        return frozenset(entry.id for entry in load_manifest(manifest_path))
    except (OSError, ValueError):
        return frozenset()


def is_unreadable_adr(adr_file: Path) -> bool:
    """Return True when the package's frontmatter cannot be READ.

    Checked BEFORE `parse_artifact_metadata`, which reads UTF-8 and catches only
    `OSError`: a UTF-16/32 package would otherwise raise `UnicodeDecodeError` and
    abort the whole registration pass rather than being refused in a controlled way.

    Widened from "undecodable" to "unreadable" (GHI #736), which is why the name
    changed: decodability is too narrow a predicate. A BOM-less UTF-16/32
    rendering of ASCII markdown decodes as UTF-8 *successfully* into a string
    full of NUL, and an invisible line separator (VT/FF/NEL/U+2028) decodes
    perfectly while hiding the block from `splitlines()`-based readers. Both
    were "decodable" and both defeated `kind:` detection, which every guard
    downstream reads as permission.
    """
    try:
        return read_frontmatter_bytes(adr_file.read_bytes()).state == "malformed"
    except OSError:
        return True


def unreadable_reason(adr_file: Path) -> str | None:
    """Return why the package is unreadable, or None when it reads cleanly."""
    try:
        return read_frontmatter_bytes(adr_file.read_bytes()).reason
    except OSError as exc:
        return str(exc)


def warn_unreadable_refused(adr_file: Path) -> None:
    """Print the membrane refusal for a package whose frontmatter cannot be read."""
    reason = unreadable_reason(adr_file) or "its frontmatter block could not be read"
    console.print(
        f"[red]Refused:[/red] {adr_file.as_posix()} — {escape(reason)}.\n"
        "  Why: an unreadable package must not collapse into 'no kind' — every "
        "guard downstream reads that as permission (ADR-0.34.0 Foundation Sunset).\n"
        "  Fix: re-save the file as UTF-8 without a BOM and without invisible line "
        "separators, then re-run `uv run gz register-adrs`."
    )


def is_ungrandfathered_foundation(
    adr_file: Path, adr_id: str, grandfathered: frozenset[str], *, kind_is_closed: bool
) -> bool:
    """Return True when a package declares `kind: foundation` but is not grandfathered.

    Manifest-aware by contract, never a bare `kind` refusal: refusing on kind
    alone would reject the whole grandfathered roster and contradict the closure
    it enforces (GHI #706, brief Requirement 5).

    *kind_is_closed* carries the project-local closure decision and is keyword-only
    with no default: a new caller must state which project's decision it is
    enforcing rather than silently inheriting gzkit's. Defaulting it to ``True``
    would reopen GHI #740 for the next call site — an adopter who never sunset
    the kind has an empty roster because they have no manifest, not because
    every foundation package they hold is illegitimate.

    Reads through the shared tri-state reader (GHI #736), so a package this
    guard cannot READ is refused rather than reported as kind-less. `absent`
    and `malformed` are different answers: the first is an ordinary
    frontmatter-less document, the second is an artifact whose block exists but
    is hidden — by an invisible line separator or a BOM-less UTF-16/32
    rendering that decodes as UTF-8 "successfully". Both previously returned
    the same permissive "no kind".
    """
    if not kind_is_closed:
        return False
    try:
        read = read_frontmatter_bytes(adr_file.read_bytes())
    except OSError:
        return True
    if read.state == "malformed":
        # Unreadable never collapses into "no kind", which every guard
        # downstream reads as permission.
        return True
    if read.fields.get("kind") != "foundation":
        return False
    return adr_id not in grandfathered


def warn_foundation_refused(adr_id: str) -> None:
    """Print the membrane refusal for an un-grandfathered foundation package."""
    console.print(
        f"[red]Refused:[/red] {adr_id} declares `kind: foundation` but is absent "
        f"from {_GRANDFATHER_MANIFEST_REL.as_posix()}.\n"
        "  Why: the foundation kind is CLOSED (ADR-0.34.0 Foundation Sunset); only the "
        "grandfathered roster may enter Layer-2.\n"
        "  Fix: author this ADR as `kind: feature`, or promote it via `gz adr promote`."
    )


SEMVER_ID_RENAMES: tuple[tuple[str, str], ...] = (
    # Historical OBPI relabeling migration.
    ("OBPI-0.2.1-01-chores-system-core", "OBPI-0.6.0-01-chores-system-core"),
    # Pool ADR migration: semver-labeled IDs -> non-semver ADR-pool.* IDs.
    (
        "ADR-0.2.0-pool.airlineops-canon-reconciliation",
        "ADR-pool.airlineops-canon-reconciliation",
    ),
    (
        "ADR-0.3.0-pool.airlineops-canon-reconciliation",
        "ADR-pool.airlineops-canon-reconciliation",
    ),
    ("ADR-0.3.0-pool.heavy-lane", "ADR-pool.heavy-lane"),
    ("ADR-0.4.0-pool.heavy-lane", "ADR-pool.heavy-lane"),
    ("ADR-0.4.0-pool.audit-system", "ADR-pool.audit-system"),
    ("ADR-0.5.0-pool.audit-system", "ADR-pool.audit-system"),
    ("ADR-0.2.1-pool.gz-chores-system", "ADR-pool.gz-chores-system"),
    ("ADR-0.6.0-pool.gz-chores-system", "ADR-pool.gz-chores-system"),
    ("ADR-1.0.0-pool.release-hardening", "ADR-pool.release-hardening"),
    ("ADR-0.7.0-pool.release-hardening", "ADR-pool.release-hardening"),
    # Pool promotion migrations.
    ("ADR-pool.skill-capability-mirroring", "ADR-0.4.0-skill-capability-mirroring"),
    (
        "OBPI-pool.skill-01-skill-source-centralization",
        "OBPI-0.4.0-01-skill-source-centralization",
    ),
    ("OBPI-0.8.0-01-skill-source-centralization", "OBPI-0.4.0-01-skill-source-centralization"),
    # Foundation ADR scaffold -> full-slug migration.
    ("ADR-0.0.4", "ADR-0.0.4-cli-standards-presentation-foundation"),
    # Legacy ADRs registered without slugs.
    ("ADR-0.1.0", "ADR-0.1.0-enforced-governance-foundation"),
    ("ADR-0.2.0", "ADR-0.2.0-gate-verification"),
    ("ADR-0.3.0", "ADR-0.3.0-airlineops-canon-reconciliation"),
    ("ADR-0.24.0", "ADR-0.24.0-skill-documentation-contract"),
    ("ADR-0.0.16", "ADR-0.0.16-frontmatter-ledger-coherence-guard"),
    ("ADR-0.0.20", "ADR-0.0.20-agent-rule-placement-invariant"),
    # GHI #279 regression: bare-ID adr_created landed at 2026-04-25T00:14:04Z before
    # the slugged form was determined. The slug "security-sensitivity-doctrine"
    # was established in a second adr_created emission four minutes later.
    ("ADR-0.0.22", "ADR-0.0.22-security-sensitivity-doctrine"),
    # Same GHI #279 regression class recurred for the complexity-doctrine
    # cluster created on 2026-04-25; bare-ID adr_created events landed
    # before the slugged form was determined.
    ("ADR-0.0.27", "ADR-0.0.27-exemplar-corpus-doctrine"),
    ("ADR-0.0.28", "ADR-0.0.28-complexity-threshold-doctrine"),
    ("ADR-0.0.29", "ADR-0.0.29-complexity-advisor"),
    ("ADR-0.0.30", "ADR-0.0.30-complexity-authoring-guidance"),
    ("ADR-0.41.0", "ADR-0.41.0-tdd-emission-and-graph-rot-remediation"),
    # ADR-0.20.0 promotion slug → brief slug reconciliation.
    (
        "OBPI-0.20.0-01-define-triangle-sync-semantics-for-spec-tests-code-spec",
        "OBPI-0.20.0-01-req-entity-and-triangle-data-model",
    ),
    (
        "OBPI-0.20.0-02-capture-implementation-decisions-as-first-class-governance-artifacts",
        "OBPI-0.20.0-02-brief-req-extraction",
    ),
    (
        "OBPI-0.20.0-03-add-drift-surfaces-that-detect",
        "OBPI-0.20.0-03-drift-detection-engine",
    ),
    (
        "OBPI-0.20.0-04-provide-lightweight-command-checkpoints-suitable-for-fast-ai-assisted-loops",
        "OBPI-0.20.0-04-gz-drift-cli-surface",
    ),
    (
        "OBPI-0.20.0-05-keep-deterministic-checks-as-default-use-llm-inference-only-where-structured-signals-are-absent",
        "OBPI-0.20.0-05-advisory-gate-integration",
    ),
    # Legacy OBPIs for ADR-0.1.0 registered without slugs.
    ("OBPI-0.1.0-01", "OBPI-0.1.0-01-gz-init"),
    ("OBPI-0.1.0-02", "OBPI-0.1.0-02-gz-prd"),
    ("OBPI-0.1.0-03", "OBPI-0.1.0-03-gz-constitute"),
    ("OBPI-0.1.0-04", "OBPI-0.1.0-04-gz-specify"),
    ("OBPI-0.1.0-05", "OBPI-0.1.0-05-gz-plan"),
    ("OBPI-0.1.0-06", "OBPI-0.1.0-06-gz-state"),
    ("OBPI-0.1.0-07", "OBPI-0.1.0-07-gz-status"),
    ("OBPI-0.1.0-08", "OBPI-0.1.0-08-gz-attest"),
    ("OBPI-0.1.0-09", "OBPI-0.1.0-09-ledger-writer-hook"),
    ("OBPI-0.1.0-10", "OBPI-0.1.0-10-templates"),
)


def _collect_disk_drift_renames(
    *,
    ledger: Ledger,
    artifacts: dict[str, list[Path]],
    touched_ids: set[str],
    existing_renames: set[tuple[str, str]],
) -> list[tuple[str, str]]:
    """Walk on-disk ADR/OBPI canon and emit bare→slug rename candidates.

    GHI #345: replaces the recurring maintenance-chore loop on
    ``SEMVER_ID_RENAMES`` for the bare→slug drift class. For each on-disk
    artifact whose filename stem is the slug form, propose a rename
    whenever the ledger holds an event for the bare form and that bare id
    has not already been canonicalized away. Honors AGENTS.md
    § Architectural Boundaries #4 (reconciliation as a continuous gated
    operation, not a maintenance chore) and #6 (Layer-1 canon + Layer-2
    ledger as joint truth, never the hand-curated tuple alone).
    """
    candidates: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def _consider(stem: str, bare: str | None) -> None:
        if bare is None or bare == stem:
            return
        if bare not in touched_ids:
            return
        if (bare, stem) in existing_renames or (bare, stem) in seen:
            return
        if ledger.canonicalize_id(bare) != bare:
            return
        candidates.append((bare, stem))
        seen.add((bare, stem))

    for adr_file in artifacts.get("adrs", []):
        stem = adr_file.stem
        _consider(stem, _extract_bare_adr_semver(stem))

    for obpi_file in artifacts.get("obpis", []):
        stem = obpi_file.stem
        _consider(stem, extract_bare_obpi_id(stem))

    candidates.sort(key=lambda item: item[0])
    return candidates


def migrate_semver(dry_run: bool) -> None:
    """Record SemVer artifact ID renames in the append-only ledger."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)
    events = ledger.read_all()

    existing_renames: set[tuple[str, str]] = set()
    touched_ids: set[str] = set()
    for event in events:
        touched_ids.add(event.id)
        if event.parent:
            touched_ids.add(event.parent)
        if event.event != "artifact_renamed":
            continue
        new_id = event.extra.get("new_id")
        if isinstance(new_id, str):
            existing_renames.add((event.id, new_id))

    pending: list[tuple[str, str]] = []
    pending_seen: set[tuple[str, str]] = set()
    for old_id, new_id in SEMVER_ID_RENAMES:
        if (old_id, new_id) in existing_renames:
            continue
        if old_id not in touched_ids:
            continue
        if (old_id, new_id) in pending_seen:
            continue
        pending.append((old_id, new_id))
        pending_seen.add((old_id, new_id))

    artifacts = scan_existing_artifacts(project_root, config.paths.design_root)
    for old_id, new_id in _collect_disk_drift_renames(
        ledger=ledger,
        artifacts=artifacts,
        touched_ids=touched_ids,
        existing_renames=existing_renames,
    ):
        if (old_id, new_id) in pending_seen:
            continue
        pending.append((old_id, new_id))
        pending_seen.add((old_id, new_id))

    if not pending:
        console.print("No applicable SemVer ID migrations found.")
        return

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger events will be written.")
        for old_id, new_id in pending:
            console.print(f"  Would append artifact_renamed: {old_id} -> {new_id}")
        return

    for old_id, new_id in pending:
        ledger.append(
            artifact_renamed_event(
                old_id=old_id,
                new_id=new_id,
                reason="semver_minor_sequence_migration",
            )
        )
        console.print(f"Renamed {old_id} -> {new_id}")

    console.print(
        f"\n[green]SemVer migration complete:[/green] {len(pending)} rename event(s) recorded."
    )


def _normalize_register_targets(ledger: Ledger, targets: list[str] | None) -> set[str]:
    """Expand target ADR ids to canonical and prefixed forms."""
    normalized_targets = {
        target if target.startswith("ADR-") else f"ADR-{target}" for target in (targets or [])
    }
    return normalized_targets | {ledger.canonicalize_id(target) for target in normalized_targets}


def _adr_register_identity(
    ledger: Ledger,
    adr_file: Path,
    metadata: dict[str, str],
) -> tuple[str, set[str], bool] | None:
    """Resolve operator-facing and canonical ADR ids for registration."""
    stem_id = adr_file.stem
    parsed_id = metadata.get("id", stem_id)
    canonical_candidates = {
        ledger.canonicalize_id(parsed_id),
        ledger.canonicalize_id(stem_id),
    }
    adr_id = parsed_id
    if parsed_id != stem_id and stem_id.startswith(f"{parsed_id}-"):
        adr_id = stem_id
    is_pool_adr = _is_pool_adr_id(adr_id)
    is_semver_adr = ADR_SEMVER_ID_RE.match(adr_id) is not None
    if not (is_semver_adr or is_pool_adr):
        return None
    return adr_id, canonical_candidates, is_pool_adr


def _is_pool_archived(metadata: dict[str, str]) -> bool:
    """Return True when a pool ADR file carries doctrine archive markers (GHI #352).

    Pool source files are preserved post-promotion as historical intake context
    per docs/governance/GovZero/adr-lifecycle.md. The archive state is signalled by
    `status: Superseded` plus `promoted_to: ADR-X.Y.Z-...` frontmatter, written by
    `_mark_pool_adr_promoted` in adr_promote_utils.py. Either marker alone is
    insufficient — both must be present for the file to count as archived.
    """
    return metadata.get("status", "").lower() == "superseded" and metadata.get(
        "promoted_to", ""
    ).startswith("ADR-")


def _collect_adrs_to_register(
    *,
    ledger: Ledger,
    artifacts: dict[str, list[Path]],
    known_adrs: set[str],
    target_ids: set[str],
    pool_only: bool,
    default_lane: str,
) -> tuple[list[tuple[str, str, str]], set[str], list[tuple[str, str]]]:
    """Collect missing ADR packages, eligible parent ids, and stale pool warnings."""
    to_register: list[tuple[str, str, str]] = []
    eligible_parent_ids: set[str] = set()
    stale_pool_files: list[tuple[str, str]] = []
    grandfathered = grandfathered_foundation_ids(get_project_root())
    kind_is_closed = foundation_kind_is_closed(get_project_root())
    for adr_file in artifacts.get("adrs", []):
        # Before parse_artifact_metadata, which decodes UTF-8 and catches only
        # OSError — an undecodable package would abort the whole pass.
        if is_unreadable_adr(adr_file):
            warn_unreadable_refused(adr_file)
            continue
        metadata = parse_artifact_metadata(adr_file)
        resolved = _adr_register_identity(ledger, adr_file, metadata)
        if resolved is None:
            continue
        adr_id, canonical_candidates, is_pool_adr = resolved
        if target_ids and canonical_candidates.isdisjoint(target_ids):
            continue
        if pool_only and not is_pool_adr:
            continue
        # Registration membrane (GHI #706): a hand-placed foundation package
        # absent from the closed manifest never reaches the adr_created ingress,
        # and neither do its children.
        if is_ungrandfathered_foundation(
            adr_file, adr_id, grandfathered, kind_is_closed=kind_is_closed
        ):
            warn_foundation_refused(adr_id)
            continue

        canonical_adr_id = ledger.canonicalize_id(adr_id)
        eligible_parent_ids.add(canonical_adr_id)
        if known_adrs.intersection(canonical_candidates):
            if is_pool_adr and canonical_adr_id != adr_id and not _is_pool_archived(metadata):
                stale_pool_files.append((adr_id, canonical_adr_id))
            continue

        parent = metadata.get("parent", "")
        raw_lane = metadata.get("lane", default_lane).lower()
        resolved_lane = raw_lane if raw_lane in {"lite", "heavy"} else default_lane
        to_register.append((adr_id, parent, resolved_lane))

    # GHI #222: canonicalize ADR parent refs against the full pool of on-disk
    # and already-registered ADRs. If an ADR declares `parent: ADR-X.Y.Z` but
    # the registered form is `ADR-X.Y.Z-slug`, resolve to the long form so the
    # ledger stores the canonical identifier — matching the id-storage
    # convention and preventing frontmatter/ledger drift.
    all_adr_ids = eligible_parent_ids | known_adrs
    resolved_to_register: list[tuple[str, str, str]] = []
    for adr_id, parent, adr_lane in to_register:
        if parent.startswith("ADR-") and parent not in all_adr_ids:
            resolved = _resolve_short_form_parent(parent, all_adr_ids)
            if resolved:
                console.print(
                    f"[yellow]Warning:[/yellow] {adr_id} uses short-form "
                    f"parent '{parent}', resolved to '{resolved}'"
                )
                parent = resolved
        resolved_to_register.append((adr_id, parent, adr_lane))

    resolved_to_register.sort(key=lambda item: item[0])
    stale_pool_files.sort(key=lambda item: item[0])
    return resolved_to_register, eligible_parent_ids, stale_pool_files


def _resolve_short_form_parent(
    parent_id: str,
    eligible_parent_ids: set[str],
) -> str | None:
    """Resolve a short-form parent ID (e.g. ADR-0.0.9) to full slug via prefix match."""
    prefix = f"{parent_id}-"
    matches = [eid for eid in eligible_parent_ids if eid.startswith(prefix)]
    if len(matches) == 1:
        return matches[0]
    return None


def _collect_obpis_to_register(
    *,
    ledger: Ledger,
    artifacts: dict[str, list[Path]],
    known_obpis: set[str],
    eligible_parent_ids: set[str],
) -> list[tuple[str, str]]:
    """Collect missing OBPI ledger entries for eligible ADR packages."""
    to_register_obpis: list[tuple[str, str]] = []
    for obpi_file in artifacts.get("obpis", []):
        metadata = parse_artifact_metadata(obpi_file)
        stem_id = obpi_file.stem
        parsed_id = metadata.get("id", stem_id)
        canonical_candidates = {
            ledger.canonicalize_id(parsed_id),
            ledger.canonicalize_id(stem_id),
        }
        if known_obpis.intersection(canonical_candidates):
            continue

        parent = metadata.get("parent", "")
        if not parent:
            continue
        parent_id = parent if parent.startswith("ADR-") else f"ADR-{parent}"
        canonical_parent = ledger.canonicalize_id(parent_id)
        if canonical_parent not in eligible_parent_ids:
            resolved = _resolve_short_form_parent(canonical_parent, eligible_parent_ids)
            if resolved:
                console.print(
                    f"[yellow]Warning:[/yellow] {obpi_file.name} uses short-form "
                    f"parent '{parent}', resolved to '{resolved}'"
                )
                canonical_parent = resolved
            else:
                console.print(
                    f"[yellow]Warning:[/yellow] Skipping {obpi_file.name} — "
                    f"parent '{parent}' does not match any eligible ADR"
                )
                continue

        obpi_id = parsed_id
        if parsed_id != stem_id and stem_id.startswith(f"{parsed_id}-"):
            console.print(
                f"[yellow]Warning:[/yellow] {obpi_file.name} frontmatter id "
                f"'{parsed_id}' does not match filename stem '{stem_id}'. "
                f"Using slugified stem as canonical id."
            )
            obpi_id = stem_id
        to_register_obpis.append((obpi_id, canonical_parent))
    to_register_obpis.sort(key=lambda item: item[0])
    return to_register_obpis


def _detect_orphan_obpis(
    ledger: Ledger,
    existing_graph: dict[str, dict[str, Any]],
    artifacts: dict[str, list[Path]],
    eligible_parent_ids: set[str],
) -> list[str]:
    """Detect ledger OBPIs with no on-disk brief file.

    Returns a list of orphaned OBPI IDs (neither withdrawn nor parked, under
    eligible parents, with no matching file on disk).  GHI #67.

    Parked OBPIs are excluded for the same reason withdrawn ones are: the brief
    is *intentionally* absent. Park is the reversible counterpart to withdraw
    (GHI #584) and preserves lineage via ``parked_to``, so a parked OBPI is
    already correctly dispositioned — reporting it under advice to "withdraw or
    rename to fix" would invite re-dispositioning work the Foundation Sunset
    deliberately parked. ``parked`` is two-way, so ``obpi_unparked`` returns an
    OBPI to orphan reporting when its brief is genuinely missing again.
    """
    on_disk_ids: set[str] = set()
    for obpi_file in artifacts.get("obpis", []):
        metadata = parse_artifact_metadata(obpi_file)
        stem_id = obpi_file.stem
        parsed_id = metadata.get("id", stem_id)
        on_disk_ids.add(ledger.canonicalize_id(parsed_id))
        on_disk_ids.add(ledger.canonicalize_id(stem_id))

    orphans: list[str] = []
    for artifact_id, info in existing_graph.items():
        if info.get("type") != "obpi":
            continue
        if info.get("withdrawn") or info.get("parked"):
            continue
        parent = info.get("parent", "")
        canonical_parent = ledger.canonicalize_id(parent) if parent else ""
        if canonical_parent not in eligible_parent_ids:
            continue
        if artifact_id not in on_disk_ids:
            orphans.append(artifact_id)

    orphans.sort()
    return orphans


def _emit_adr_created_or_skip(
    ledger: Ledger,
    adr_id: str,
    parent: str,
    adr_lane: str,
    known_adrs: set[str],
) -> None:
    """Append `adr_created` for this ADR unless an existing event already covers it.

    GHI #279: the rename-aware bridge in `Ledger.has_adr_created` collapses
    bare `ADR-X.Y.Z` and slugged `ADR-X.Y.Z-<slug>` forms for the same semver,
    so a prior bare-ID emission blocks the slugged-form duplicate that
    produced the ADR-0.0.22 shadow row.
    """
    if ledger.has_adr_created(adr_id):
        console.print(
            f"[yellow]WARNING:[/yellow] {adr_id} already has an adr_created event; "
            "skipping duplicate emission."
        )
        known_adrs.add(ledger.canonicalize_id(adr_id))
        return
    ledger.append(adr_created_event(adr_id, parent, adr_lane))
    known_adrs.add(ledger.canonicalize_id(adr_id))
    parent_display = parent or "(none)"
    console.print(f"Registered ADR: {adr_id} (parent: {parent_display}, lane: {adr_lane})")


def register_adrs(
    lane: str | None,
    pool_only: bool = False,
    dry_run: bool = False,
    targets: list[str] | None = None,
) -> None:
    """Register ADR packages that exist in canon but are missing from ledger state."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    artifacts: dict[str, Any] = scan_existing_artifacts(project_root, config.paths.design_root)
    existing_graph = ledger.get_artifact_graph()
    known_adrs = {
        artifact_id for artifact_id, info in existing_graph.items() if info.get("type") == "adr"
    }
    known_obpis = {
        artifact_id for artifact_id, info in existing_graph.items() if info.get("type") == "obpi"
    }

    target_ids = _normalize_register_targets(ledger, targets)
    default_lane = lane or config.mode
    to_register, eligible_parent_ids, stale_pool_files = _collect_adrs_to_register(
        ledger=ledger,
        artifacts=artifacts,
        known_adrs=known_adrs,
        target_ids=target_ids,
        pool_only=pool_only,
        default_lane=default_lane,
    )

    if stale_pool_files:
        console.print(
            f"[yellow]Warning:[/yellow] {len(stale_pool_files)} stale pool file(s) "
            f"detected (promoted but not cleaned up):"
        )
        for pool_id, promoted_id in stale_pool_files:
            console.print(f"  [yellow]stale:[/yellow] {pool_id} → promoted to {promoted_id}")

    to_register_obpis = _collect_obpis_to_register(
        ledger=ledger,
        artifacts=artifacts,
        known_obpis=known_obpis,
        eligible_parent_ids=eligible_parent_ids,
    )

    # GHI #67: Detect ledger OBPIs whose brief files no longer exist on disk.
    orphans = _detect_orphan_obpis(ledger, existing_graph, artifacts, eligible_parent_ids)
    if orphans:
        console.print(
            f"[yellow]Warning:[/yellow] {len(orphans)} ledger OBPI(s) have no "
            f"file on disk (withdraw or rename to fix):"
        )
        for orphan_id in orphans:
            console.print(f"  [yellow]orphan:[/yellow] {orphan_id}")

    if not to_register and not to_register_obpis:
        if not orphans:
            console.print("No unregistered ADRs or OBPIs found.")
        _regenerate_adr_status_index(project_root, dry_run=dry_run)
        return

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger events will be written.")
        for adr_id, parent, adr_lane in to_register:
            parent_display = parent or "(none)"
            console.print(
                f"  Would append adr_created: {adr_id} (parent: {parent_display}, lane: {adr_lane})"
            )
        for obpi_id, parent in to_register_obpis:
            console.print(f"  Would append obpi_created: {obpi_id} (parent: {parent})")
        _regenerate_adr_status_index(project_root, dry_run=True)
        return

    for adr_id, parent, adr_lane in to_register:
        _emit_adr_created_or_skip(ledger, adr_id, parent, adr_lane, known_adrs)

    for obpi_id, parent in to_register_obpis:
        ledger.append(obpi_created_event(obpi_id, parent))
        known_obpis.add(ledger.canonicalize_id(obpi_id))
        console.print(f"Registered OBPI: {obpi_id} (parent: {parent})")

    console.print(
        f"\n[green]ADR registration complete:[/green] "
        f"{len(to_register)} adr_created event(s), "
        f"{len(to_register_obpis)} obpi_created event(s) recorded."
    )

    _regenerate_adr_status_index(project_root, dry_run=False)


def _regenerate_adr_status_index(project_root: Path, *, dry_run: bool) -> None:
    """Regenerate `docs/governance/GovZero/adr-status.md` from on-disk truth.

    GHI #322: the index is a Layer 3 derived view of the same canon
    `register-adrs` reconciles against. Riding alongside reconciliation
    gives the table a single ceremony, single source of truth.
    """
    if dry_run:
        console.print(
            "[yellow]Dry run:[/yellow] would regenerate docs/governance/GovZero/adr-status.md"
        )
        return
    content = regenerate_adr_status_md(project_root, write=True)
    row_count = content.count("\n| [")
    console.print(f"Regenerated adr-status.md ({row_count} ADRs).")
