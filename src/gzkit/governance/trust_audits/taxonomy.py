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

    forbidden_events = {
        "gate_checked",
        "attestation",
        "obpi_completed",
        "adr_attested",
        "adr_audit",
        "adr_closeout",
        "lifecycle_transition",
    }
    errors: list[ValidationError] = []
    seen: set[tuple[str, str]] = set()
    for lineno, raw in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        event_type = event.get("event")
        artifact_id = event.get("id") or event.get("adr_id") or ""
        if not isinstance(artifact_id, str) or not artifact_id.startswith("ADR-pool."):
            continue
        if event_type not in forbidden_events:
            continue
        key = (artifact_id, event_type)
        if key in seen:
            continue
        seen.add(key)
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
        # Skip nested obpi / brief / audit artefacts — same convention as
        # _validate_decomposition in validate_cmd.py.
        if "obpis" in adr_md.parts or "briefs" in adr_md.parts or "audit" in adr_md.parts:
            continue
        frontmatter = _parse_adr_frontmatter(adr_md)
        if frontmatter is None:
            continue
        rel = adr_md.relative_to(project_root).as_posix()
        adr_id = frontmatter.get("id", "")
        kind = frontmatter.get("kind")
        semver = frontmatter.get("semver")
        is_pool = isinstance(adr_id, str) and adr_id.startswith(_POOL_ID_PREFIX)

        if is_pool:
            if kind is not None:
                errors.append(
                    ValidationError(
                        type="taxonomy",
                        artifact=rel,
                        message=(
                            "Pool ADRs derive kind from the `ADR-pool.*` id "
                            "prefix; remove the `kind:` frontmatter field."
                        ),
                    )
                )
            continue

        if kind is None:
            errors.append(
                ValidationError(
                    type="taxonomy",
                    artifact=rel,
                    message=(
                        "Non-pool ADR is missing `kind:` frontmatter. Add "
                        "`kind: foundation` for an app/system invariant ADR "
                        "(semver `0.0.x`) or `kind: feature` for a capability "
                        "ADR (semver `0.y.z` and up). See ADR-0.0.17 / ADR-0.0.18."
                    ),
                )
            )
            continue

        if kind not in ("foundation", "feature"):
            errors.append(
                ValidationError(
                    type="taxonomy",
                    artifact=rel,
                    message=(
                        f"Unknown `kind: {kind}`. Expected `foundation` or "
                        "`feature` (pool kind is id-derived, not frontmatter)."
                    ),
                )
            )
            continue

        if kind == "foundation" and not (
            isinstance(semver, str) and _FOUNDATION_SEMVER_RE.match(semver)
        ):
            errors.append(
                ValidationError(
                    type="taxonomy",
                    artifact=rel,
                    message=(
                        f"`kind: foundation` requires semver `0.0.x`; got "
                        f"`{semver}`. Foundation ADRs are app/system invariants "
                        "and never impact release versioning."
                    ),
                )
            )
        elif kind == "feature" and isinstance(semver, str) and _FOUNDATION_SEMVER_RE.match(semver):
            errors.append(
                ValidationError(
                    type="taxonomy",
                    artifact=rel,
                    message=(
                        f"`kind: feature` forbids semver `0.0.x`; got `{semver}`. "
                        "Feature ADRs carry release-impacting semver (`0.y.z` and up)."
                    ),
                )
            )
    return errors


def _parse_adr_frontmatter(path: Path) -> dict[str, str] | None:
    """Read a flat YAML frontmatter block as a ``str -> str`` mapping.

    Stdlib-only to match every sibling audit in this package (no PyYAML
    import widens the trust surface for a flat key/value block).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None
    fields: dict[str, str] = {}
    for raw in lines[1:end]:
        if ":" not in raw:
            continue
        key, _, value = raw.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            value = value[1:-1]
        fields[key] = value
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
