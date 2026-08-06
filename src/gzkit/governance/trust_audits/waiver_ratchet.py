"""Waiver-ratchet honesty contract (ADR-0.0.73 / OBPI-0.0.73-09).

Mechanizes Boundary Invariant #8: every registered waiver/grandfather/baseline
surface that gates a ``gz check`` step MUST carry exactly one honesty mechanism,
so a waiver list cannot silently launder "not built yet" into "attested green":

1. **closed-set lock** — every entry carries a non-empty lock field (e.g.
   ``added_under``); the set is frozen and new entries are forbidden. Proven by
   ``data/historical_self_close_waivers.json``.
2. **dated cutover** — a cutover date (ISO ``YYYY-MM-DD``) that is in the past;
   after it the waiver no longer applies. Proven by ``lock_exchange_coupling``.
3. **monotonic shrink-ratchet** — a committed baseline count the live list can
   only decrease against. Proven by ``tautological_test_baseline``.

``gz validate --waiver-ratchet`` reads ``data/waiver_ratchet_registry.json`` and
fails closed (exit 3) on any registered surface that lacks or violates its
declared mechanism. It ALSO fails closed on a waiver/grandfather data file on
disk that is NOT registered (the silent-bypass an unratcheted surface is): the
registry is the closed set, and a new ``data/*_waivers.json`` /
``*_grandfather*.json`` that escapes it is the exact hole this law closes.

The verb self-registers as a ``bound`` QC step subject to ``--qc-binding`` (no
facade-of-the-facade): it ships a negative control it must fail on.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import cast

from gzkit.core.validation_rules import ValidationError

_REGISTRY_REL = Path("data") / "waiver_ratchet_registry.json"
_DATA_REL = Path("data")
# Filename globs that denote a debt-waiver surface. A file matching one of these
# that is absent from the registry is a fail-closed silent-bypass finding.
_WAIVER_GLOBS = ("*_waivers.json", "*_grandfather*.json", "*_grandfathering.json")
_VALID_MECHANISMS = frozenset({"closed-set-lock", "dated-cutover", "shrink-ratchet"})
_RECOVER = "uv run gz validate --waiver-ratchet"


def _err(artifact: str, message: str) -> ValidationError:
    return ValidationError(type="waiver-ratchet", artifact=artifact, message=message)


def _load_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _collection_at(payload: object, entries_path: str) -> object | None:
    """Resolve the entries collection at ``entries_path`` (top key, or '')."""
    if entries_path == "":
        return payload
    if isinstance(payload, dict):
        return payload.get(entries_path)
    return None


def _count_entries(collection: object) -> int | None:
    if isinstance(collection, (list, dict)):
        return len(collection)
    return None


def _iter_entries(collection: object) -> list[dict[str, object]]:
    if isinstance(collection, list):
        items: list[object] = list(collection)
    elif isinstance(collection, dict):
        items = list(collection.values())
    else:
        return []
    return [cast("dict[str, object]", e) for e in items if isinstance(e, dict)]


def _check_closed_set_lock(
    artifact: str, data_file: str, collection: object, lock_field: str
) -> list[ValidationError]:
    entries = _iter_entries(collection)
    count = _count_entries(collection)
    if count and not entries:
        return [
            _err(
                artifact,
                f"Waiver surface {data_file} declares mechanism 'closed-set-lock' but its "
                f"entries are not lock-bearing objects, so no '{lock_field}' lock can be "
                f"verified. ADR-0.0.73 Boundary Invariant #8 requires a real honesty "
                f"mechanism; switch this surface to 'shrink-ratchet' with a committed "
                f"baseline_count, or restructure entries to carry '{lock_field}'. Re-run "
                f"`{_RECOVER}`.",
            )
        ]
    unlocked = [e for e in entries if not str(e.get(lock_field, "")).strip()]
    if unlocked:
        return [
            _err(
                artifact,
                f"Waiver surface {data_file} declares 'closed-set-lock' but {len(unlocked)} "
                f"of {len(entries)} entries lack a non-empty '{lock_field}'. An unlocked "
                f"entry can be appended silently, which launders 'not built' into 'attested "
                f"green' (ADR-0.0.73 Boundary Invariant #8). Add '{lock_field}' to every "
                f"entry (freezing the set) or move the surface to 'shrink-ratchet'. Re-run "
                f"`{_RECOVER}`.",
            )
        ]
    return []


def _check_dated_cutover(
    artifact: str, data_file: str, cutover_raw: object, today: date
) -> list[ValidationError]:
    cutover_str = str(cutover_raw or "").strip()
    parsed: date | None = None
    if cutover_str:
        try:
            parsed = date.fromisoformat(cutover_str[:10])
        except ValueError:
            parsed = None
    if parsed is None:
        return [
            _err(
                artifact,
                f"Waiver surface {data_file} declares 'dated-cutover' but its 'cutover_date' "
                f"({cutover_str!r}) is missing or not an ISO YYYY-MM-DD date. A cutover with "
                f"no real date never closes, so the waiver is unbounded (ADR-0.0.73 Boundary "
                f"Invariant #8). Set a real past 'cutover_date'. Re-run `{_RECOVER}`.",
            )
        ]
    if parsed > today:
        return [
            _err(
                artifact,
                f"Waiver surface {data_file} declares 'dated-cutover' {parsed.isoformat()}, "
                f"which is in the future ({today.isoformat()}): the cutover has not closed, so "
                f"the waiver is still open-ended (ADR-0.0.73 Boundary Invariant #8). Use a past "
                f"cutover date. Re-run `{_RECOVER}`.",
            )
        ]
    return []


def _check_shrink_ratchet(
    artifact: str, data_file: str, collection: object, baseline_raw: object
) -> list[ValidationError]:
    count = _count_entries(collection)
    if count is None:
        return [
            _err(
                artifact,
                f"Waiver surface {data_file} declares 'shrink-ratchet' but its entries "
                f"collection is not a list/dict, so its size cannot be ratcheted. Point "
                f"'entries_path' at the collection. Re-run `{_RECOVER}`.",
            )
        ]
    if not isinstance(baseline_raw, int) or isinstance(baseline_raw, bool) or baseline_raw < 0:
        return [
            _err(
                artifact,
                f"Waiver surface {data_file} declares 'shrink-ratchet' but its registry "
                f"'baseline_count' ({baseline_raw!r}) is not a non-negative integer. The "
                f"baseline is the committed high-water mark the list may only decrease against "
                f"(ADR-0.0.73 Boundary Invariant #8). Set baseline_count to the current entry "
                f"count ({count}). Re-run `{_RECOVER}`.",
            )
        ]
    if count > baseline_raw:
        return [
            _err(
                artifact,
                f"Waiver surface {data_file} grew to {count} entries, above its committed "
                f"shrink-ratchet baseline of {baseline_raw}: a waiver list may only shrink, "
                f"never grow (ADR-0.0.73 Boundary Invariant #8 — growth launders new 'not "
                f"built' debt into 'attested green'). Remove the added waiver(s), or fix the "
                f"underlying gate so the waiver is unnecessary. Re-run `{_RECOVER}`.",
            )
        ]
    return []


def _registered_data_files(surfaces: list[dict[str, object]]) -> set[str]:
    files: set[str] = set()
    for s in surfaces:
        df = str(s.get("data_file", "")).strip()
        if df:
            files.add(Path(df).as_posix())
    return files


def _unregistered_waiver_files(
    project_root: Path, registered: set[str], excluded: set[str]
) -> list[str]:
    data_root = project_root / _DATA_REL
    if not data_root.is_dir():
        return []
    found: set[str] = set()
    for glob in _WAIVER_GLOBS:
        for f in data_root.glob(glob):
            found.add(f.relative_to(project_root).as_posix())
    return sorted(found - registered - excluded)


def audit_waiver_ratchet(
    project_root: Path,
    *,
    today: date | None = None,
) -> list[ValidationError]:
    """Flag any registered waiver surface lacking/violating its honesty mechanism.

    Returns one ``ValidationError`` per offending surface (non-empty → caller
    exits 3). Also flags an on-disk waiver/grandfather data file that is not in
    the registry (the silent-bypass). ``today`` overrides the cutover clock for
    deterministic tests.
    """
    clock = today if today is not None else date.today()
    registry_path = project_root / _REGISTRY_REL
    payload = _load_json(registry_path)
    if not isinstance(payload, dict):
        return [
            _err(
                "waiver_ratchet_registry",
                f"The waiver-ratchet registry {_REGISTRY_REL.as_posix()} is missing or "
                f"unparseable. ADR-0.0.73 Boundary Invariant #8 requires every gate-bearing "
                f"waiver surface to declare an honesty mechanism in this registry; an absent "
                f"registry means no surface is ratcheted (every waiver is a silent bypass). "
                f"Author the registry. Re-run `{_RECOVER}`.",
            )
        ]

    raw_surfaces = payload.get("surfaces", [])
    surface_dicts: list[dict[str, object]] = (
        [cast("dict[str, object]", s) for s in raw_surfaces if isinstance(s, dict)]
        if isinstance(raw_surfaces, list)
        else []
    )
    raw_excluded = payload.get("excluded", [])
    excluded = {
        Path(str(x)).as_posix() for x in (raw_excluded if isinstance(raw_excluded, list) else [])
    }

    errors: list[ValidationError] = []

    for s in surface_dicts:
        data_file = str(s.get("data_file", "")).strip()
        artifact = data_file or "<unnamed-surface>"
        mechanism = str(s.get("mechanism", "")).strip()
        if mechanism not in _VALID_MECHANISMS:
            errors.append(
                _err(
                    artifact,
                    f"Waiver surface {artifact} declares mechanism {mechanism!r}, not one of "
                    f"{sorted(_VALID_MECHANISMS)}. ADR-0.0.73 Boundary Invariant #8 requires "
                    f"exactly one honesty mechanism. Re-run `{_RECOVER}`.",
                )
            )
            continue
        data_payload = _load_json(project_root / data_file)
        if data_payload is None:
            errors.append(
                _err(
                    artifact,
                    f"Waiver surface {artifact} is registered but its data file is missing or "
                    f"unparseable. A registered surface must resolve to a real file so its "
                    f"mechanism can be verified (ADR-0.0.73 Boundary Invariant #8). Re-run "
                    f"`{_RECOVER}`.",
                )
            )
            continue
        collection = _collection_at(data_payload, str(s.get("entries_path", "")))
        if mechanism == "closed-set-lock":
            errors.extend(
                _check_closed_set_lock(
                    artifact, data_file, collection, str(s.get("lock_field", "added_under"))
                )
            )
        elif mechanism == "dated-cutover":
            errors.extend(_check_dated_cutover(artifact, data_file, s.get("cutover_date"), clock))
        else:  # shrink-ratchet
            errors.extend(
                _check_shrink_ratchet(artifact, data_file, collection, s.get("baseline_count"))
            )

    # Silent-bypass guard: any waiver/grandfather data file not registered.
    registered = _registered_data_files(surface_dicts)
    for rel in _unregistered_waiver_files(project_root, registered, excluded):
        errors.append(
            _err(
                rel,
                f"Waiver/grandfather data file {rel} exists on disk but is not declared in "
                f"{_REGISTRY_REL.as_posix()}. An unregistered waiver surface is a silent "
                f"bypass — it gates work without an honesty mechanism (ADR-0.0.73 Boundary "
                f"Invariant #8). Add it to the registry with one of "
                f"{sorted(_VALID_MECHANISMS)}, or list it under 'excluded' with a rationale "
                f"if it is genuinely not a gate-bearing waiver. Re-run `{_RECOVER}`.",
            )
        )
    return errors
