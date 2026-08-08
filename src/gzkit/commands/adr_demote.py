"""ADR demote command — inverse of ``gz adr promote``.

Demotes a feature or foundation ADR back to the pool bucket: strips
``kind``/``semver`` frontmatter, rewrites ``id`` and ``status`` (and the body
H1's id token, which states that same identity a second time — GHI #776), moves
the file from ``pre-release/`` or ``foundation/`` to ``pool/``, deletes the
source package directory (briefs, closeout form, etc. per Q1=b of the
2026-05-23 get-out-of-jail prequel), and emits an ``artifact_renamed``
ledger event with ``reason="pool_demotion"`` (per Q5=a — reuses the
existing event factory rather than introducing a new event type).

Authored under GHI #521 as the Day-0 tooling prerequisite for the GHI #520
prequel sweep (24-deep Pending feature queue → pool).
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from gzkit.commands.common import (
    GzCliError,
    _is_pool_adr_id,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
)
from gzkit.ledger import Ledger, parse_frontmatter_value
from gzkit.ledger_events import artifact_renamed_event, obpi_parked_event
from gzkit.obpi_lifecycle import parkable_children
from gzkit.sync import parse_artifact_metadata

_DEMOTABLE_KINDS = {"feature", "foundation"}
#: Frontmatter keys a pool ADR must not carry. ``promoted_from`` joined the set
#: because a pool ADR is an *origin* — carrying it left the demoted file claiming
#: it was promoted from itself, since demotion reuses the very slug the promotion
#: came from (observed on the first `take-demoted` run, GHI #775).
_FRONTMATTER_STRIP_KEYS = ("kind", "semver", "date", "promoted_from")
_CANONICAL_ID_RE = re.compile(r"^ADR-\d+\.\d+\.\d+-(?P<slug>.+)$")
#: First-H1 identity claim. The id token stops at whitespace or ``:`` so both
#: ``# ADR-0.27.0: Title`` and the bare ``# ADR-0.27.0`` are matched, and the
#: separator (``:``, em dash, or nothing) rides along in ``rest`` untouched.
_H1_ID_RE = re.compile(r"^(?P<prefix>#[ \t]+)(?P<id>ADR-[^\s:]+)(?P<rest>.*)$")
#: Pool-slug collision policies. ``take-demoted`` was added under GHI #775: a
#: promote/demote round trip ALWAYS collides, because ``gz adr promote`` retains
#: the pool file as historical intake by design — and neither original policy
#: could return an ADR that had been worked. ``fail`` refuses; ``keep-pool``
#: preserves the pre-promotion intake while ``rmtree`` deletes the evolved
#: package, exit 0, discarding every decision recorded after promotion.
_ON_COLLISION_CHOICES = ("fail", "keep-pool", "take-demoted")


def _derive_pool_slug_from_adr_id(adr_id: str) -> str:
    """Derive a pool slug from a feature/foundation ADR id.

    ``ADR-0.27.0-arb-receipt-system-absorption`` → ``arb-receipt-system-absorption``.
    """
    match = _CANONICAL_ID_RE.match(adr_id)
    if not match:
        msg = (
            f"Cannot derive pool slug from non-canonical ADR id: {adr_id!r}. "
            "Expected form ADR-<X.Y.Z>-<slug>."
        )
        raise GzCliError(msg)
    return match.group("slug")


def _strip_frontmatter_keys(content: str, keys: tuple[str, ...]) -> str:
    """Remove the named keys from a YAML frontmatter block."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return content
    end_idx: int | None = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return content
    kept: list[str] = [lines[0]]
    for idx in range(1, end_idx):
        raw_key, sep, _raw_value = lines[idx].partition(":")
        if sep and raw_key.strip() in keys:
            continue
        kept.append(lines[idx])
    kept.extend(lines[end_idx:])
    trailing = "\n" if content.endswith("\n") else ""
    return "\n".join(kept) + trailing


def _set_frontmatter_value(content: str, key: str, value: str) -> str:
    """Set a top-level frontmatter key (insert if absent, replace if present)."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return content
    end_idx: int | None = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return content
    for idx in range(1, end_idx):
        raw_key, sep, _raw_value = lines[idx].partition(":")
        if sep and raw_key.strip() == key:
            lines[idx] = f"{key}: {value}"
            break
    else:
        lines.insert(end_idx, f"{key}: {value}")
    trailing = "\n" if content.endswith("\n") else ""
    return "\n".join(lines) + trailing


def _body_start_index(lines: list[str]) -> int:
    """Index of the first body line, skipping any leading frontmatter block."""
    if not lines or lines[0].strip() != "---":
        return 0
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return idx + 1
    return 0


def _rewrite_h1_id_prefix(content: str, new_id: str) -> str:
    """Retitle the first body H1 so its id token names ``new_id`` (GHI #776).

    Demotion rewrites ``id:`` frontmatter, and the H1 is a second statement of
    that same fact — leaving it behind made the artifact assert two disagreeing
    identities. Latent only until the freed number was reissued: 8 of 38 stale
    pool H1s named an id belonging to a *different* live ADR, so
    ``ADR-pool.pre-commit-hook-absorption`` announced itself as ``# ADR-0.35.0``
    while that id was the in-flight ``canon-entry-corpus-landing``.

    Only the id token of the *first* body H1 moves. Everything after it on the
    line survives, so both corpus shapes are handled — ``# <id>: <Title>`` and
    the bare ``# <id>`` that 8 of the demoted files carry. Body prose naming the
    old id is design history (supersession notes, decision records) and is left
    alone: ``REQ-0.34.0-04-01`` makes demotion a re-homing, not a rewrite.
    """
    lines = content.splitlines()
    for idx in range(_body_start_index(lines), len(lines)):
        match = _H1_ID_RE.match(lines[idx])
        if match is None:
            continue
        lines[idx] = f"{match.group('prefix')}{new_id}{match.group('rest')}"
        break
    else:
        return content
    trailing = "\n" if content.endswith("\n") else ""
    return "\n".join(lines) + trailing


def _reverse_pool_promotion_markers(content: str, demoted_id: str) -> str:
    """Reverse the promote-side markers ``_mark_pool_adr_promoted`` writes.

    No-op unless the pool file's ``promoted_to:`` still names the ADR now being
    demoted — guards against mutating an unrelated pool ADR that happens to
    collide on slug (GHI #558).
    """
    if parse_frontmatter_value(content, "promoted_to") != demoted_id:
        return content
    updated = _set_frontmatter_value(content, "status", "Pool")
    updated = _strip_frontmatter_keys(updated, ("promoted_to",))
    updated = updated.replace("\n## Status\n\nSuperseded\n", "\n## Status\n\nPool\n", 1)
    lines = updated.splitlines()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("> Promoted to `") and stripped.endswith(
            "This pool file is retained as historical intake context."
        ):
            del lines[idx]
            if idx < len(lines) and lines[idx].strip() == "":
                del lines[idx]
            break
    trailing = "\n" if updated.endswith("\n") else ""
    return "\n".join(lines) + trailing


def _live_covers_into_deleted_briefs(project_root: Path, source_id: str) -> list[str]:
    """Return ``@covers`` REQ ids under ``tests/`` belonging to *source_id*'s briefs.

    Demotion deletes the whole ADR package, briefs included, and pool ADRs carry
    no OBPIs by doctrine — so there is nowhere for those briefs to go. Meanwhile
    ``@covers`` validates its REQ id at **import** time against the brief corpus:
    delete the briefs and every test module holding one of those decorators
    raises ``ValueError: Unknown REQ identifier`` and the suite stops loading.

    Nothing coupled the two before (GHI #773). Demoting
    ``ADR-0.44.0-vendor-alignment-codex`` broke 36 decorators across four test
    modules — all of them covering an OBPI that was *attested complete* — and the
    only signal was the suite failing to import afterwards.
    """
    semver = _CANONICAL_ID_RE.match(source_id)
    prefix = source_id.split("-")[1] if not semver else source_id.split("-")[1]
    tests_root = project_root / "tests"
    if not tests_root.is_dir():
        return []
    pattern = re.compile(rf'@covers\(\s*["\'](REQ-{re.escape(prefix)}-[^"\']*)["\']')
    found: dict[str, None] = {}
    for path in tests_root.rglob("*.py"):
        for match in pattern.finditer(path.read_text(encoding="utf-8", errors="replace")):
            found.setdefault(match.group(1), None)
    return sorted(found)


def _find_dependent_children(project_root: Path, config: Any, demoted_id: str) -> list[str]:
    """Return ADR ids whose ``parent:`` frontmatter references the demoted id.

    Demoting a parent would orphan its children. Detection is policy-breach
    (exit 3) per .claude/rules/cli.md unless --force is set.
    """
    adr_root = project_root / config.paths.adrs
    if not adr_root.is_dir():
        return []
    children: list[str] = []
    for adr_file in adr_root.rglob("ADR-*.md"):
        if "pool" in adr_file.parts:
            continue
        meta = parse_artifact_metadata(adr_file)
        parent = meta.get("parent", "")
        if parent == demoted_id and meta.get("id") != demoted_id:
            children.append(meta.get("id", adr_file.stem))
    return children


def _resolve_demote_source(
    project_root: Path,
    config: Any,
    adr_id: str,
) -> tuple[Path, str, dict[str, str], str]:
    """Resolve the source ADR, validate it is demotable, and return state."""
    if _is_pool_adr_id(adr_id):
        msg = f"ADR is already in pool, nothing to demote: {adr_id}"
        raise GzCliError(msg)
    adr_file, _resolved = resolve_adr_file(project_root, config, adr_id)
    if "pool" in adr_file.parts:
        msg = f"Resolved ADR lives under pool/, refusing to demote: {adr_file}"
        raise GzCliError(msg)
    content = adr_file.read_text(encoding="utf-8")
    base_metadata = parse_artifact_metadata(adr_file)
    metadata: dict[str, str] = dict(base_metadata)
    # parse_artifact_metadata is selective; pull kind/semver/date directly.
    for key in ("kind", "semver", "date"):
        if key not in metadata:
            value = parse_frontmatter_value(content, key)
            if value is not None:
                metadata[key] = value
    resolved_id = metadata.get("id") or adr_file.stem
    kind = metadata.get("kind", "")
    if kind not in _DEMOTABLE_KINDS:
        msg = (
            f"ADR {resolved_id} has kind={kind!r}; only "
            f"{sorted(_DEMOTABLE_KINDS)} kinds are demotable."
        )
        raise GzCliError(msg)
    if not metadata.get("semver"):
        msg = f"ADR {resolved_id} is missing semver in frontmatter; cannot demote."
        raise GzCliError(msg)
    return adr_file, resolved_id, metadata, content


def _build_demote_plan(
    project_root: Path,
    config: Any,
    adr_id: str,
    ghi: int,
    note: str | None,
    operator: str | None,
    on_collision: str = "fail",
    ledger: Ledger | None = None,
) -> dict[str, Any]:
    """Compute every action and target path before any write."""
    if on_collision not in _ON_COLLISION_CHOICES:
        msg = f"on_collision must be one of {_ON_COLLISION_CHOICES}, got {on_collision!r}"
        raise GzCliError(msg)
    source_file, source_id, metadata, source_content = _resolve_demote_source(
        project_root, config, adr_id
    )
    source_slug = _derive_pool_slug_from_adr_id(source_id)
    new_id = f"ADR-pool.{source_slug}"
    pool_dir = project_root / config.paths.adrs / "pool"
    target_file = pool_dir / f"{new_id}.md"
    collision_keep_pool = False
    reversed_pool_content: str | None = None
    if target_file.exists():
        if on_collision == "fail":
            rel = target_file.relative_to(project_root).as_posix()
            msg = (
                f"Pool slug collision: target file already exists: {rel}. "
                "Choose --on-collision keep-pool (preserve the existing pool file; the "
                "demoted package is deleted) or --on-collision take-demoted (the demoted "
                "ADR's current content becomes the pool file). Prefer take-demoted when "
                "the ADR was worked after promotion — keep-pool would discard that work."
            )
            raise GzCliError(msg)
        # `take-demoted` leaves `collision_keep_pool` False so the normal
        # (non-collision) write path puts the demoted content at the pool slug,
        # overwriting the retained intake. That intake is `status: Superseded`
        # and stays in git history, which is where an artifact whose own
        # frontmatter says so belongs (GHI #775).
        collision_keep_pool = on_collision == "keep-pool"
        if collision_keep_pool:
            existing_target_content = target_file.read_text(encoding="utf-8")
            candidate = _reverse_pool_promotion_markers(existing_target_content, source_id)
            if candidate != existing_target_content:
                reversed_pool_content = candidate
    source_dir = source_file.parent
    if source_dir == project_root / config.paths.adrs:
        # Defensive: a top-level loose .md should not have a parent dir to remove.
        source_dir = source_file
    pool_content = _strip_frontmatter_keys(source_content, _FRONTMATTER_STRIP_KEYS)
    pool_content = _set_frontmatter_value(pool_content, "id", new_id)
    pool_content = _set_frontmatter_value(pool_content, "status", "Pool")
    pool_content = _rewrite_h1_id_prefix(pool_content, new_id)
    children = _find_dependent_children(project_root, config, source_id)
    # Demoting a parent must transact over its OBPI children too: renaming the
    # ADR without disposing of them is what stranded 237 records at GHI #520.
    parked_obpis = (
        parkable_children([event.model_dump() for event in ledger.read_all()], source_id)
        if ledger is not None
        else []
    )
    extras: dict[str, Any] = {
        "prior_kind": metadata.get("kind", ""),
        "prior_semver": metadata.get("semver", ""),
        "demoted_at": datetime.now(UTC).isoformat(),
        "ghi": ghi,
    }
    if collision_keep_pool:
        extras["collision_resolution"] = "keep-pool"
    if operator:
        extras["operator"] = operator
    if note:
        extras["note"] = note
    return {
        "source_file": source_file,
        "source_dir": source_dir,
        "source_id": source_id,
        "source_content": source_content,
        "target_file": target_file,
        "new_id": new_id,
        "pool_content": pool_content,
        "extras": extras,
        "children": children,
        "parked_obpis": parked_obpis,
        "collision_keep_pool": collision_keep_pool,
        "reversed_pool_content": reversed_pool_content,
    }


def _demote_result_payload(
    project_root: Path, plan: dict[str, Any], dry_run: bool
) -> dict[str, Any]:
    """Build a JSON-safe result payload for ``--json`` output."""
    source_file = cast(Path, plan["source_file"])
    target_file = cast(Path, plan["target_file"])
    return {
        "source_id": plan["source_id"],
        "new_id": plan["new_id"],
        "source_file": source_file.relative_to(project_root).as_posix(),
        "target_file": target_file.relative_to(project_root).as_posix(),
        "extras": plan["extras"],
        "children": plan["children"],
        "parked_obpis": plan.get("parked_obpis", []),
        "dry_run": dry_run,
    }


def _print_demote_dry_run(project_root: Path, plan: dict[str, Any]) -> None:
    """Print the dry-run summary for a demote plan."""
    source_file = cast(Path, plan["source_file"])
    target_file = cast(Path, plan["target_file"])
    source_dir = cast(Path, plan["source_dir"])
    collision_keep_pool = cast(bool, plan.get("collision_keep_pool", False))
    console.print("[yellow]Dry run:[/yellow] no files or ledger events will be written.")
    console.print(f"  Source ADR: {plan['source_id']}")
    console.print(f"  Target pool ID: {plan['new_id']}")
    if collision_keep_pool:
        console.print(
            f"  [yellow]Pool collision — keeping existing pool:[/yellow] "
            f"{target_file.relative_to(project_root).as_posix()}"
        )
        if plan.get("reversed_pool_content") is not None:
            console.print(
                "  [yellow]Would reverse stale promotion markers[/yellow] "
                "(status: Pool, strip promoted_to, remove promoted-to note)"
            )
    else:
        console.print(f"  Would write: {target_file.relative_to(project_root).as_posix()}")
    if source_dir.is_dir():
        console.print(f"  Would remove dir: {source_dir.relative_to(project_root).as_posix()}")
    else:
        console.print(f"  Would remove file: {source_file.relative_to(project_root).as_posix()}")
    extras = cast(dict[str, Any], plan["extras"])
    console.print(
        "  Would append artifact_renamed: "
        f"{plan['source_id']} -> {plan['new_id']} "
        f"(reason: pool_demotion, ghi: {extras['ghi']})"
    )
    parked_obpis = cast(list[str], plan.get("parked_obpis", []))
    if parked_obpis:
        noun = "OBPI" if len(parked_obpis) == 1 else "OBPIs"
        console.print(f"  Would park {len(parked_obpis)} child {noun}: {', '.join(parked_obpis)}")
    children = cast(list[str], plan["children"])
    if children:
        console.print(f"  [red]Dependent children:[/red] {', '.join(children)}")


def _apply_demote(ledger: Ledger, plan: dict[str, Any], task_id: str | None = None) -> None:
    """Write the pool file, remove the source package, append the ledger event.

    ``task_id`` attributes the emitted ``artifact_renamed`` to the TASK the
    demotion is labor under. ``artifact_renamed`` is a TASK worklog type, so a
    demotion run inside an active TASK envelope without it fails Signature (a) of
    ``gz validate --task-envelope-coherence`` (ADR-0.34.0 OBPI-04). Optional: the
    CLI path demotes outside any TASK envelope.
    """
    target_file = cast(Path, plan["target_file"])
    source_file = cast(Path, plan["source_file"])
    source_dir = cast(Path, plan["source_dir"])
    collision_keep_pool = cast(bool, plan.get("collision_keep_pool", False))
    if collision_keep_pool:
        reversed_pool_content = cast(str | None, plan.get("reversed_pool_content"))
        if reversed_pool_content is not None:
            target_file.write_text(reversed_pool_content, encoding="utf-8")
    else:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(cast(str, plan["pool_content"]), encoding="utf-8")
    if source_dir.is_dir() and source_dir != source_file:
        shutil.rmtree(source_dir)
    elif source_file.exists():
        source_file.unlink()
    event = artifact_renamed_event(
        old_id=cast(str, plan["source_id"]),
        new_id=cast(str, plan["new_id"]),
        reason="pool_demotion",
        task_id=task_id,
    )
    for key, value in cast(dict[str, Any], plan["extras"]).items():
        event.extra[key] = value
    ledger.append(event)
    new_id = cast(str, plan["new_id"])
    for obpi_id in cast(list[str], plan.get("parked_obpis", [])):
        ledger.append(
            obpi_parked_event(
                obpi_id,
                parent=cast(str, plan["source_id"]),
                parked_to=new_id,
                reason="pool_demotion",
            )
        )


def _print_demote_applied(project_root: Path, plan: dict[str, Any]) -> None:
    """Print the post-apply summary."""
    target_file = cast(Path, plan["target_file"])
    source_dir = cast(Path, plan["source_dir"])
    collision_keep_pool = cast(bool, plan.get("collision_keep_pool", False))
    console.print(f"[green]Demoted ADR:[/green] {plan['source_id']} -> {plan['new_id']}")
    if collision_keep_pool:
        console.print(f"  Kept existing pool: {target_file.relative_to(project_root).as_posix()}")
        if plan.get("reversed_pool_content") is not None:
            console.print("  Reversed stale promotion markers on kept pool file")
    else:
        console.print(f"  Created: {target_file.relative_to(project_root).as_posix()}")
    if source_dir.is_dir():
        console.print(f"  Removed dir: {source_dir.relative_to(project_root).as_posix()}")
    extras = cast(dict[str, Any], plan["extras"])
    console.print(f"  Ledger event: artifact_renamed (reason=pool_demotion, ghi={extras['ghi']})")
    parked_obpis = cast(list[str], plan.get("parked_obpis", []))
    if parked_obpis:
        noun = "OBPI" if len(parked_obpis) == 1 else "OBPIs"
        console.print(f"  Parked {len(parked_obpis)} child {noun} (reversible on re-promotion)")


def adr_demote_cmd(
    adr_id: str,
    ghi: int,
    note: str | None,
    operator: str | None,
    as_json: bool,
    dry_run: bool,
    force: bool,
    on_collision: str = "fail",
) -> None:
    """Demote a feature/foundation ADR back to pool (inverse of ``adr promote``)."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)
    plan = _build_demote_plan(
        project_root=project_root,
        config=config,
        adr_id=adr_id,
        ghi=ghi,
        note=note,
        operator=operator,
        on_collision=on_collision,
        ledger=ledger,
    )
    children = cast(list[str], plan["children"])
    if children and not force:
        rel = ", ".join(children)
        console.print(
            f"\n[red]Demotion blocked:[/red] {len(children)} ADR(s) reference this as parent: {rel}"
        )
        console.print("  Pass --force to override (orphans the children).")
        raise SystemExit(3)
    covered = _live_covers_into_deleted_briefs(project_root, cast(str, plan["source_id"]))
    if covered and not force:
        shown = ", ".join(covered[:5]) + ("…" if len(covered) > 5 else "")
        console.print(
            f"\n[red]Demotion blocked:[/red] {len(covered)} @covers decorator(s) under "
            f"tests/ name REQs from briefs this demotion deletes: {shown}"
        )
        console.print(
            "  Why: @covers validates its REQ id at IMPORT time against the brief corpus, "
            "so deleting the briefs makes every one of those test modules raise "
            "ValueError and the suite fails to load. Pool ADRs carry no OBPIs by "
            "doctrine, so the briefs have no home to move to."
        )
        console.print(
            "  Next step: remove or retarget those decorators, then re-run — or pass "
            "--force if the REQ traceability is deliberately being discarded."
        )
        raise SystemExit(3)
    result = _demote_result_payload(project_root, plan, dry_run)
    if as_json:
        print(json.dumps(result, indent=2))  # noqa: T201
        if dry_run:
            return
    if dry_run:
        _print_demote_dry_run(project_root, plan)
        return
    _apply_demote(ledger, plan)
    _print_demote_applied(project_root, plan)
