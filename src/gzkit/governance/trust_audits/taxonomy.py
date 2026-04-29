"""ADR taxonomy and pool-isolation trust audits.

* ``audit_pool_adr_isolation`` — pool ADRs (id-prefix ``ADR-pool.*``) must
  not receive runtime-track lifecycle/gate events (GHI #208).
* ``audit_adr_taxonomy`` — pool/foundation/feature kind & semver coherence
  per ADR-0.0.17.
* ``audit_adr_status_fresh`` — drift between on-disk ADR canon and the
  derived ``adr-status.md`` index (GHI #322).

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


def audit_adr_taxonomy(project_root: Path) -> list[ValidationError]:
    """Fail on ADRs that violate the pool/foundation/feature taxonomy.

    Enforces ADR-0.0.17 § Decision: pool kind is derived from the
    ``ADR-pool.*`` id prefix; non-pool ADRs carry ``kind: foundation`` or
    ``kind: feature`` in frontmatter; ``foundation`` requires semver
    ``0.0.x``; ``feature`` requires any other semver. Never mutates files.
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
