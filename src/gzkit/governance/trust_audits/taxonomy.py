"""ADR taxonomy and pool-isolation trust audits.

* ``audit_pool_adr_isolation`` — pool ADRs (id-prefix ``ADR-pool.*``) must
  not receive runtime-track lifecycle/gate events (GHI #208).
* ``audit_adr_taxonomy`` — pool/foundation/feature kind & semver coherence
  per ADR-0.0.17.
* ``audit_adr_status_fresh`` — drift between on-disk ADR canon and the
  derived ``adr-status.md`` index (GHI #322).
* Audit (ADR-0.0.57 OBPI-01): no sequence-position assumptions present —
  nominal-ID semantics are correctly implicit. The validator enforces format
  and kind coherence only; no max-N, consecutive-integer, or gap-detection
  logic exists. Foundation IDs with gaps (e.g. 0.0.54, 0.0.56) return zero
  taxonomy errors by design.

Also exports ``_parse_adr_frontmatter`` — a stdlib YAML reader used here
and re-imported by ``sensitivity.py``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from gzkit.validate import ValidationError

_FOUNDATION_SEMVER_RE = re.compile(r"^0\.0\.\d+$")
_POOL_ID_PREFIX = "ADR-pool."


_POOL_FORBIDDEN_LEDGER_EVENTS: frozenset[str] = frozenset(
    {
        "gate_checked",
        "attestation",
        "obpi_completed",
        "adr_attested",
        "adr_audit",
        "adr_closeout",
        "lifecycle_transition",
    }
)


def _pool_violation_key(event: dict[str, object]) -> tuple[str, str] | None:
    """Return ``(artifact_id, event_type)`` if this event is a pool-isolation breach."""
    event_type = event.get("event")
    artifact_id = event.get("id") or event.get("adr_id") or ""
    if not isinstance(artifact_id, str) or not artifact_id.startswith("ADR-pool."):
        return None
    if event_type not in _POOL_FORBIDDEN_LEDGER_EVENTS:
        return None
    return artifact_id, str(event_type)


def audit_pool_adr_isolation(project_root: Path) -> list[ValidationError]:
    """Fail on pool ADRs receiving runtime-track lifecycle or gate events.

    Pool ADRs (under ``docs/design/adr/pool/`` or id-prefixed ``ADR-pool.*``)
    are architectural backlog. Per architectural-boundaries rules 1–2 they
    must not receive Gate 1+ events; doing so means they were promoted
    without the formal ``gz-adr-promote`` ceremony.
    """
    ledger = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger.is_file():
        return []

    errors: list[ValidationError] = []
    seen: set[tuple[str, str]] = set()
    for lineno, raw in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        key = _pool_violation_key(event)
        if key is None or key in seen:
            continue
        seen.add(key)
        artifact_id, event_type = key
        errors.append(
            ValidationError(
                type="pool_adr_isolation",
                artifact=f".gzkit/ledger.jsonl:{lineno}",
                message=(
                    f"Pool ADR `{artifact_id}` received runtime-track event "
                    f"`{event_type}`. Pool ADRs must not advance through "
                    "gates without promotion via `gz adr promote` "
                    "(CLAUDE.md architectural boundaries 1–2)."
                ),
            )
        )
    return errors


_NESTED_ADR_DIRS: frozenset[str] = frozenset({"obpis", "briefs", "audit"})


def _is_nested_adr_artifact(adr_md: Path) -> bool:
    """Skip nested obpi / brief / audit artefacts — same convention as validate_cmd."""
    return any(part in _NESTED_ADR_DIRS for part in adr_md.parts)


def _foundation_semver_valid(semver: object) -> bool:
    return isinstance(semver, str) and bool(_FOUNDATION_SEMVER_RE.match(semver))


def _taxonomy_error(rel: str, message: str) -> ValidationError:
    return ValidationError(type="taxonomy", artifact=rel, message=message)


def _check_pool_taxonomy(rel: str, kind: object) -> ValidationError | None:
    if kind is None:
        return None
    return _taxonomy_error(
        rel,
        "Pool ADRs derive kind from the `ADR-pool.*` id "
        "prefix; remove the `kind:` frontmatter field.",
    )


def _check_non_pool_kind(rel: str, kind: object) -> ValidationError | None:
    if kind is None:
        return _taxonomy_error(
            rel,
            "Non-pool ADR is missing `kind:` frontmatter. Add "
            "`kind: foundation` for an app/system invariant ADR "
            "(semver `0.0.x`) or `kind: feature` for a capability "
            "ADR (semver `0.y.z` and up). See ADR-0.0.17 / ADR-0.0.18.",
        )
    if kind not in ("foundation", "feature"):
        return _taxonomy_error(
            rel,
            f"Unknown `kind: {kind}`. Expected `foundation` or "
            "`feature` (pool kind is id-derived, not frontmatter).",
        )
    return None


def _check_kind_semver_consistency(rel: str, kind: str, semver: object) -> ValidationError | None:
    if kind == "foundation" and not _foundation_semver_valid(semver):
        return _taxonomy_error(
            rel,
            f"`kind: foundation` requires semver `0.0.x`; got "
            f"`{semver}`. Foundation ADRs are app/system invariants "
            "and never impact release versioning.",
        )
    if kind == "feature" and _foundation_semver_valid(semver):
        return _taxonomy_error(
            rel,
            f"`kind: feature` forbids semver `0.0.x`; got `{semver}`. "
            "Feature ADRs carry release-impacting semver (`0.y.z` and up).",
        )
    return None


def _audit_one_adr_taxonomy(adr_md: Path, project_root: Path) -> list[ValidationError]:
    """Apply the taxonomy decision tree to a single ADR file."""
    frontmatter = _parse_adr_frontmatter(adr_md)
    if frontmatter is None:
        return []
    rel = adr_md.relative_to(project_root).as_posix()
    adr_id = frontmatter.get("id", "")
    kind = frontmatter.get("kind")
    semver = frontmatter.get("semver")
    is_pool = isinstance(adr_id, str) and adr_id.startswith(_POOL_ID_PREFIX)

    if is_pool:
        pool_err = _check_pool_taxonomy(rel, kind)
        return [pool_err] if pool_err else []

    kind_err = _check_non_pool_kind(rel, kind)
    if kind_err is not None:
        return [kind_err]

    consistency_err = _check_kind_semver_consistency(rel, str(kind), semver)
    return [consistency_err] if consistency_err else []


_GRANDFATHER_MANIFEST = ("data", "foundation_grandfather.json")


def _on_disk_foundation_ids(project_root: Path) -> dict[str, str]:
    """Map ``adr_id -> repo-relative path`` for every on-disk ``kind: foundation`` ADR."""
    adr_root = project_root / "docs" / "design" / "adr"
    found: dict[str, str] = {}
    if not adr_root.is_dir():
        return found
    for adr_md in sorted(adr_root.rglob("ADR-*.md")):
        if _is_nested_adr_artifact(adr_md):
            continue
        frontmatter = _parse_adr_frontmatter(adr_md)
        if frontmatter is None or frontmatter.get("kind") != "foundation":
            continue
        adr_id = frontmatter.get("id", "")
        if adr_id:
            found[adr_id] = adr_md.relative_to(project_root).as_posix()
    return found


def _manifest_ids(project_root: Path) -> set[str]:
    """Return the ids declared in the committed grandfather manifest."""
    from gzkit.models.foundation_grandfather import load_manifest  # noqa: PLC0415

    path = project_root.joinpath(*_GRANDFATHER_MANIFEST)
    if not path.is_file():
        return set()
    return {entry.id for entry in load_manifest(path)}


_GRANDFATHERED_EVENT = "foundation_grandfathered"


def _grandfathered_event_ids(project_root: Path) -> set[str]:
    """Return the ADR ids carrying a Layer-2 ``foundation_grandfathered`` event.

    Replays raw ledger lines rather than the typed ``Ledger`` reader: the
    event type is introduced by the sunset migration (ADR-0.34.0 OBPI-04) and
    has no model yet, so a typed read would couple this gate to a schema it
    does not own. Same tolerance as ``_pool_violation_key`` — the id may
    arrive under ``id`` or ``adr_id``.
    """
    ledger = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger.is_file():
        return set()

    witnessed: set[str] = set()
    for raw in ledger.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            # Well-formed JSON that is not an event object (a bare list,
            # string, or number). Decoding succeeded, so JSONDecodeError
            # never fires — without this guard the value reaches `.get` and
            # raises AttributeError, killing the whole audit over one line.
            continue
        if event.get("event") != _GRANDFATHERED_EVENT:
            continue
        adr_id = event.get("id") or event.get("adr_id")
        if isinstance(adr_id, str) and adr_id:
            witnessed.add(adr_id)
    return witnessed


def _limbo_error(adr_id: str, manifest_rel: str) -> ValidationError:
    """Build the ``foundation_limbo`` finding for one non-terminal foundation."""
    return ValidationError(
        type="foundation_limbo",
        artifact=manifest_rel,
        message=(
            f"Grandfathered foundation `{adr_id}` has no `{_GRANDFATHERED_EVENT}` "
            "ledger event, so it is not terminal — it sits in "
            "Pending-with-attested-work limbo. ADR-0.34.0 Foundation Sunset "
            "requires every entry in the closed manifest to be terminal, because "
            "a sealed era with unfinished members is not sealed. This check reads "
            "the Layer-2 ledger, NOT frontmatter: editing the ADR's `status:` to "
            "`Validated` cannot clear it (ADR-0.0.37 proved frontmatter lies about "
            "repudiated OBPIs). Next: finish the foundation and attest it with "
            f"`uv run gz closeout {adr_id}`, or drop it to pool with "
            f"`uv run gz adr demote {adr_id}` and remove it from `{manifest_rel}`."
        ),
    )


def audit_foundation_closure(project_root: Path) -> list[ValidationError]:
    """Fail on foundation-kind membership drift and non-terminal members.

    Enforces ADR-0.34.0 § Decision (INTERFACE): the foundation kind is SEALED,
    and ``data/foundation_grandfather.json`` is its committed closed membership
    set. Containment is asserted in both directions — an on-disk foundation
    absent from the manifest (``foundation_kind_closed``) means the kind was
    reopened without editing the reviewed list; a manifest entry with no
    on-disk package (``grandfather_dangling``) means the manifest names a
    foundation that does not exist.

    The terminal-partition assertion (``foundation_limbo``, OBPI-03) closes the
    remaining hole: membership does not imply completion. It ranges over
    *genuine* members — declared AND on disk — so neither containment breach is
    also reported as non-terminal. One defect, one finding; double-counting
    would make the migration-scale finding census unreadable. Never mutates
    files.
    """
    on_disk = _on_disk_foundation_ids(project_root)
    declared = _manifest_ids(project_root)
    manifest_rel = "/".join(_GRANDFATHER_MANIFEST)

    errors: list[ValidationError] = [
        ValidationError(
            type="foundation_kind_closed",
            artifact=on_disk[adr_id],
            message=(
                f"Foundation ADR `{adr_id}` is not declared in `{manifest_rel}`. "
                "The `foundation` kind is CLOSED to new authoring (ADR-0.34.0 "
                "Foundation Sunset); the on-disk foundation set must be a subset "
                "of the committed grandfather manifest, so a foundation absent "
                "from it is a silently-reopened kind. Next: author the ADR as "
                "`--kind feature` instead, or demote it with `uv run gz adr "
                f"demote {adr_id}`. Reopening the kind deliberately means adding "
                f"the entry to `{manifest_rel}` and its golden fixture together."
            ),
        )
        for adr_id in sorted(set(on_disk) - declared)
    ]
    errors.extend(
        ValidationError(
            type="grandfather_dangling",
            artifact=manifest_rel,
            message=(
                f"Grandfather manifest declares `{adr_id}`, but no on-disk "
                "`kind: foundation` ADR package carries that id. The manifest is "
                "the closed membership set for a kind sealed by ADR-0.34.0; an "
                "entry with no package makes the set unfalsifiable in one "
                f"direction. Next: remove the stale entry from `{manifest_rel}` "
                "and its golden fixture together, or restore the missing ADR "
                "package. Verify with `uv run gz validate --taxonomy`."
            ),
        )
        for adr_id in sorted(declared - set(on_disk))
    )
    members = declared & set(on_disk)
    errors.extend(
        _limbo_error(adr_id, manifest_rel)
        for adr_id in sorted(members - _grandfathered_event_ids(project_root))
    )
    return errors


def audit_adr_taxonomy(project_root: Path) -> list[ValidationError]:
    """Fail on ADRs that violate the pool/foundation/feature taxonomy.

    Enforces ADR-0.0.17 § Decision: pool kind is derived from the
    ``ADR-pool.*`` id prefix; non-pool ADRs carry ``kind: foundation`` or
    ``kind: feature`` in frontmatter; ``foundation`` requires semver
    ``0.0.x``; ``feature`` requires any other semver. Never mutates files.

    Scope-mates, not callees: the ADR-0.34.0 closure assertions
    (``audit_foundation_closure``) run under the same ``--taxonomy`` scope but
    are deliberately NOT folded in here. This function's contract is the
    ADR-0.0.17 decision tree alone; merging the two would make every existing
    caller's result depend on the grandfather manifest's population state.
    """
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    errors: list[ValidationError] = []
    for adr_md in sorted(adr_root.rglob("ADR-*.md")):
        if _is_nested_adr_artifact(adr_md):
            continue
        errors.extend(_audit_one_adr_taxonomy(adr_md, project_root))
    return errors


def _strip_quoted(value: str) -> str:
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return value[1:-1]
    return value


def _frontmatter_block(lines: list[str]) -> list[str] | None:
    """Return the lines between the first two ``---`` markers, or None if absent."""
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return None


def _parse_adr_frontmatter(path: Path) -> dict[str, str] | None:
    """Read a flat YAML frontmatter block as a ``str -> str`` mapping.

    Stdlib-only to match every sibling audit in this package (no PyYAML
    import widens the trust surface for a flat key/value block).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None
    block = _frontmatter_block(text.splitlines())
    if block is None:
        return None
    fields: dict[str, str] = {}
    for raw in block:
        if ":" not in raw:
            continue
        key, _, value = raw.partition(":")
        fields[key.strip()] = _strip_quoted(value.strip())
    return fields


_BARE_ADR_ID_RE = re.compile(r"^(ADR-\d+\.\d+\.\d+)-.+$")


def _live_adr_ids(project_root: Path) -> set[str]:
    """Return every ADR id present on disk (any bucket), in both id forms.

    An ``obpi_created`` record may name its parent in the bare-semver form
    (``ADR-0.0.43``) while the ADR is on disk under its slugged id
    (``ADR-0.0.43-ddd-domain-cascade``). Both forms are registered so a
    resolvable parent is never reported as an orphan — a gate that false-fires
    is worse than no gate, because it teaches operators to skip the finding.
    """
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return set()
    live: set[str] = set()
    for adr_file in adr_root.rglob("ADR-*.md"):
        meta = _parse_adr_frontmatter(adr_file) or {}
        adr_id = str(meta.get("id") or adr_file.stem)
        live.add(adr_id)
        bare = _BARE_ADR_ID_RE.match(adr_id)
        if bare:
            live.add(bare.group(1))
    return live


def audit_obpi_lifecycle_coherence(project_root: Path) -> list[ValidationError]:
    """Flag ``obpi_created`` records with no disposition and no resolvable parent.

    An ``obpi_created`` event asserts a brief artifact exists. When its parent
    ADR is renamed away (pool demotion) without a corresponding child event, the
    assertion survives with nothing behind it — Layer-2 claiming what Layer-1
    cannot show, the incoherence ``docs/governance/state-doctrine.md`` forbids
    and Architectural Boundary 6 names.

    GHI #584: 237 such records accumulated from the GHI #520 Day-0 demotion
    because the demote path transacted over the ADR node but not its children.
    Demotion now parks children in the same ceremony; this audit fail-closes so
    the class cannot recur silently on the next bulk transition.
    """
    from gzkit.ledger import Ledger  # noqa: PLC0415
    from gzkit.obpi_lifecycle import orphaned_obpi_ids  # noqa: PLC0415

    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return []
    events = [event.model_dump() for event in Ledger(ledger_path).read_all()]
    brief_ids = {p.stem for p in (project_root / "docs" / "design" / "adr").rglob("OBPI-*.md")}
    orphans = orphaned_obpi_ids(events, _live_adr_ids(project_root), brief_ids=brief_ids)
    return [
        ValidationError(
            type="obpi_lifecycle_coherence",
            artifact=f".gzkit/ledger.jsonl::{obpi_id}",
            message=(
                "obpi_created asserts a brief that has no disposition and whose parent "
                "ADR no longer resolves. Forbidden by docs/governance/state-doctrine.md "
                "(Layer-2 facts must trace to Layer-1) and Architectural Boundary 6. "
                "Recovery: `uv run python -m gzkit.governance.obpi_park_backfill "
                "--dry-run` to review, then `--apply --attestor <name>` to park it."
            ),
        )
        for obpi_id in orphans
    ]


def audit_adr_status_fresh(project_root: Path) -> list[ValidationError]:
    """Flag drift between on-disk ADR canon and ``adr-status.md``.

    The status table is a Layer 3 derived view per
    ``docs/governance/state-doctrine.md``; it must be regenerable from
    Layer 1 (filesystem). GHI #322: drift across ~5 ADRs went undetected
    because no maintained regenerator existed. Recovery surface is
    ``gz register-adrs`` (which now regenerates the index after ledger
    reconciliation); this audit closes the loop by fail-closing on drift.
    """
    from gzkit.governance.adr_status_index import compute_drift  # noqa: PLC0415

    drift = compute_drift(project_root)
    if not drift:
        return []
    return [
        ValidationError(
            type="adr_status_fresh",
            artifact=f"docs/governance/GovZero/adr-status.md::{entry.adr_id}",
            message=(
                f"[{entry.kind}] {entry.detail}. Recovery: "
                "`uv run gz register-adrs` regenerates the index from on-disk truth."
            ),
        )
        for entry in drift
    ]
