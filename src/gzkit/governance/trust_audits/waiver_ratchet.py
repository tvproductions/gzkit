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

**Identity monotonicity (GHI #1154 item 4).** A count ratchet cannot see a swap: drop
one entry, add another, and the count never moved. A registry that declares
``identity_baseline`` also declares, per shrink-ratchet surface, how an entry is
identified (``identity``), and the surface may carry only identities its committed
baseline holds or a reviewed authorization record names. A renamed or moved operation is
a NEW identity, so it fails unless a record in the baseline file names it. The baseline
(``waiver_identity_baseline.json``) is a high-water set, never pruned by this audit: a
removed entry may return (the count bounds growth), a new one may not. Identity kinds:
``strings`` (list of strings), ``keys`` (dict keys), ``fields`` (list of objects, the named
fields joined), and ``count-only`` (a disclosed absence of identity, with a reason).

The verb self-registers as a ``bound`` QC step subject to ``--qc-binding`` (no
facade-of-the-facade): it ships a negative control it must fail on.
"""

from __future__ import annotations

import json
from collections import Counter
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
_IDENTITY_KINDS = frozenset({"strings", "keys", "fields", "count-only"})
#: Every field a reviewed authorization record carries; each must be non-empty.
_AUTHORIZATION_FIELDS = ("data_file", "identity", "reason", "authorized_by", "ruling")
_SEPARATOR = "::"


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


def _keys_of(collection: object, _spec: dict[str, object]) -> Counter[str] | None:
    return Counter(str(k) for k in collection) if isinstance(collection, dict) else None


def _strings_of(collection: object, _spec: dict[str, object]) -> Counter[str] | None:
    readable = isinstance(collection, list) and all(isinstance(e, str) for e in collection)
    return Counter(collection) if readable else None


def _fields_of(collection: object, spec: dict[str, object]) -> Counter[str] | None:
    fields = spec.get("fields")
    if not isinstance(collection, list) or not isinstance(fields, list) or not fields:
        return None
    found: Counter[str] = Counter()
    for entry in collection:
        if not isinstance(entry, dict) or any(f not in entry for f in fields):
            return None
        found[_SEPARATOR.join(str(entry[f]) for f in fields)] += 1
    return found


_IDENTITY_READERS = {"keys": _keys_of, "strings": _strings_of, "fields": _fields_of}


def _identities(collection: object, spec: dict[str, object]) -> Counter[str] | None:
    """Return the identities *collection* holds under *spec*, or ``None`` when unreadable.

    A multiset: two entries may legitimately share an identity, and a second copy of one is
    still growth.
    """
    reader = _IDENTITY_READERS.get(str(spec.get("kind")))
    return reader(collection, spec) if reader else None


def _authorized(baseline: dict[str, object], data_file: str) -> tuple[Counter[str], list[str]]:
    """Return the identities authorized for *data_file* and the records that are malformed."""
    authorized: Counter[str] = Counter()
    malformed: list[str] = []
    records = baseline.get("authorizations", [])
    for record in records if isinstance(records, list) else []:
        if not isinstance(record, dict) or record.get("data_file") != data_file:
            continue
        missing = [f for f in _AUTHORIZATION_FIELDS if not str(record.get(f, "")).strip()]
        if missing:
            malformed.append(f"{record.get('identity', '<unnamed>')} lacks {', '.join(missing)}")
        else:
            authorized[str(record["identity"])] += 1
    return authorized, malformed


def _check_identity(
    artifact: str,
    data_file: str,
    collection: object,
    spec: object,
    baseline: dict[str, object],
) -> list[ValidationError]:
    """Fail an identity the baseline neither holds nor a reviewed record names."""
    if not isinstance(spec, dict) or spec.get("kind") not in _IDENTITY_KINDS:
        return [
            _err(
                artifact,
                f"Waiver surface {data_file} declares 'shrink-ratchet' in a registry that "
                f"declares 'identity_baseline', but its 'identity' ({spec!r}) is not one of "
                f"{sorted(_IDENTITY_KINDS)}. Without it a swap (drop one entry, add another) "
                f"never moves the count (GHI #1154). Declare how an entry is identified. "
                f"Re-run `{_RECOVER}`.",
            )
        ]
    if spec["kind"] == "count-only":
        if str(spec.get("reason", "")).strip():
            return []
        return [
            _err(
                artifact,
                f"Waiver surface {data_file} declares identity 'count-only' with no 'reason'. "
                f"That is a disclosed absence of identity, and a disclosure without a reason "
                f"is silence (GHI #1154). Name why entries here carry no identity. Re-run "
                f"`{_RECOVER}`.",
            )
        ]
    current = _identities(collection, spec)
    if current is None:
        return [
            _err(
                artifact,
                f"Waiver surface {data_file} declares identity {spec!r} but its entries do not "
                f"have that shape, so no identity can be read (GHI #1154). Correct the 'identity' "
                f"declaration. Re-run `{_RECOVER}`.",
            )
        ]
    surfaces = baseline.get("surfaces", {})
    held = surfaces.get(data_file) if isinstance(surfaces, dict) else None
    if not isinstance(held, list):
        return [
            _err(
                artifact,
                f"Waiver surface {data_file} has no identity baseline, so none of its "
                f"{sum(current.values())} entries can be recognised as already accepted "
                f"(GHI #1154). Record its identities under 'surfaces' in the identity baseline. "
                f"Re-run `{_RECOVER}`.",
            )
        ]
    authorized, malformed = _authorized(baseline, data_file)
    new = (current - Counter(str(i) for i in held)) - authorized
    errors: list[ValidationError] = []
    if malformed:
        errors.append(
            _err(
                artifact,
                f"Waiver surface {data_file} carries authorization record(s) that are not "
                f"reviewed: {'; '.join(malformed)}. A record needs {list(_AUTHORIZATION_FIELDS)}, "
                f"each non-empty (GHI #1154). Complete it. Re-run `{_RECOVER}`.",
            )
        )
    if new:
        shown = sorted(new)[:5]
        errors.append(
            _err(
                artifact,
                f"Waiver surface {data_file} carries {sum(new.values())} identit(ies) its "
                f"baseline never accepted, e.g. {shown}. A renamed or moved entry is a NEW "
                f"entry: dropping one and adding another leaves the count unchanged and is how "
                f"a ratchet is swapped (GHI #1154; ADR-0.0.73 Boundary Invariant #8). Revert "
                f"the change, or add a record naming each identity ({list(_AUTHORIZATION_FIELDS)}) "
                f"under 'authorizations' in the identity baseline. Re-run `{_RECOVER}`.",
            )
        )
    return errors


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

    identity_baseline: dict[str, object] | None = None
    baseline_rel = str(payload.get("identity_baseline", "")).strip()
    if baseline_rel:
        loaded = _load_json(project_root / baseline_rel)
        if isinstance(loaded, dict):
            identity_baseline = loaded
        else:
            errors.append(
                _err(
                    baseline_rel,
                    f"The registry declares identity_baseline {baseline_rel} but it is missing "
                    f"or unparseable, so no surface's identities can be checked (GHI #1154). "
                    f"Restore it. Re-run `{_RECOVER}`.",
                )
            )

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
            if identity_baseline is not None:
                errors.extend(
                    _check_identity(
                        artifact, data_file, collection, s.get("identity"), identity_baseline
                    )
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
