"""Register and migrate-semver command implementations."""

from pathlib import Path
from typing import Any

from gzkit.commands.common import (
    ADR_SEMVER_ID_RE,
    _is_pool_adr_id,
    console,
    ensure_initialized,
    get_project_root,
)
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    artifact_renamed_event,
    obpi_created_event,
)
from gzkit.sync import parse_artifact_metadata, scan_existing_artifacts

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
    for old_id, new_id in SEMVER_ID_RENAMES:
        if (old_id, new_id) in existing_renames:
            continue
        if old_id not in touched_ids:
            continue
        pending.append((old_id, new_id))

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
    for adr_file in artifacts.get("adrs", []):
        metadata = parse_artifact_metadata(adr_file)
        resolved = _adr_register_identity(ledger, adr_file, metadata)
        if resolved is None:
            continue
        adr_id, canonical_candidates, is_pool_adr = resolved
        if target_ids and canonical_candidates.isdisjoint(target_ids):
            continue
        if pool_only and not is_pool_adr:
            continue

        canonical_adr_id = ledger.canonicalize_id(adr_id)
        eligible_parent_ids.add(canonical_adr_id)
        if known_adrs.intersection(canonical_candidates):
            if is_pool_adr and canonical_adr_id != adr_id:
                stale_pool_files.append((adr_id, canonical_adr_id))
            continue

        parent = metadata.get("parent", "")
        raw_lane = metadata.get("lane", default_lane).lower()
        resolved_lane = raw_lane if raw_lane in {"lite", "heavy"} else default_lane
        to_register.append((adr_id, parent, resolved_lane))
    to_register.sort(key=lambda item: item[0])
    stale_pool_files.sort(key=lambda item: item[0])
    return to_register, eligible_parent_ids, stale_pool_files


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

    Returns a list of orphaned OBPI IDs (non-withdrawn, under eligible parents,
    with no matching file on disk).  GHI #67.
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
        if info.get("withdrawn"):
            continue
        parent = info.get("parent", "")
        canonical_parent = ledger.canonicalize_id(parent) if parent else ""
        if canonical_parent not in eligible_parent_ids:
            continue
        if artifact_id not in on_disk_ids:
            orphans.append(artifact_id)

    orphans.sort()
    return orphans


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
        return

    for adr_id, parent, adr_lane in to_register:
        ledger.append(adr_created_event(adr_id, parent, adr_lane))
        known_adrs.add(ledger.canonicalize_id(adr_id))
        parent_display = parent or "(none)"
        console.print(f"Registered ADR: {adr_id} (parent: {parent_display}, lane: {adr_lane})")

    for obpi_id, parent in to_register_obpis:
        ledger.append(obpi_created_event(obpi_id, parent))
        known_obpis.add(ledger.canonicalize_id(obpi_id))
        console.print(f"Registered OBPI: {obpi_id} (parent: {parent})")

    console.print(
        f"\n[green]ADR registration complete:[/green] "
        f"{len(to_register)} adr_created event(s), "
        f"{len(to_register_obpis)} obpi_created event(s) recorded."
    )
