"""Config-registry declaration gate (GHI #929).

``data/`` accumulated 41 top-level registries read from 93 source modules with
no owner, no loader and no coherence gate. The waiver/grandfather family
already had all three via ``data/waiver_ratchet_registry.json``; this module is
its companion for the remaining policy/threshold family, and the two are
EXHAUSTIVE over ``data/*.json`` — a registry matching neither is fail-closed as
the silent bypass an unowned config surface is.

Four arms, all mechanical:

1. **exhaustiveness** — every top-level ``data/*.json`` is either matched by
   ``waiver_ratchet``'s filename globs or declared here.
2. **no phantoms** — every declared registry exists on disk.
3. **verified owner** — the declared owner is read and confirmed to reference
   the registry. A registry that merely LISTED owners would be a presence check
   standing in for a state check, which ``AGENTS.md`` § DO IT RIGHT forbids:
   *"Do not build or trust a gate whose only witness is that an artifact
   exists."* ``kind`` selects the channel — ``code`` verifies a module under
   ``src/``, ``doc`` verifies a markdown surface.
4. **symmetric relation** — ``relates_to`` must be declared from both sides, so
   two registries encoding one concept carry a machine-checked relation rather
   than a reconciliation buried in a ``_doc`` string no parser reads.

The waiver globs are IMPORTED from ``waiver_ratchet`` rather than restated:
two definitions of one concept is the precise defect family GHI #929 names, and
this module must not open a second instance of it while closing the first.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.waiver_ratchet import (
    _WAIVER_GLOBS,
    _registered_data_files,
)

_REGISTRY_REL = Path("data") / "config_registry.json"
_DATA_REL = Path("data")
_VALID_KINDS = frozenset({"code", "doc"})
_RECOVER = "uv run gz validate --config-registry"


def _err(artifact: str, message: str) -> ValidationError:
    return ValidationError(type="config-registry", artifact=artifact, message=message)


def _load_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _waiver_owned(project_root: Path, data_root: Path) -> set[str]:
    """Names under ``data/`` that the waiver-ratchet registry owns.

    Both channels, because neither alone is complete: the filename globs are
    waiver_ratchet's own discovery heuristic, while its ``data_file`` entries
    are its DECLARATIONS — and declarations win. ``distribution_baseline_manifest.json``
    is declared there but matches no glob, so a glob-only reading would claim it
    here and put one file under two owners.
    """
    owned: set[str] = set()
    for glob in _WAIVER_GLOBS:
        owned.update(f.name for f in data_root.glob(glob))
    payload = _load_json(project_root / "data" / "waiver_ratchet_registry.json")
    if isinstance(payload, dict):
        surfaces = payload.get("surfaces")
        if isinstance(surfaces, list):
            dicts = [s for s in surfaces if isinstance(s, dict)]
            owned.update(Path(f).name for f in _registered_data_files(dicts))
    return owned


def _references(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def _verify_owner(project_root: Path, name: str, owner: str, kind: str) -> list[ValidationError]:
    """Confirm the declared owner exists AND actually references ``name``."""
    if kind not in _VALID_KINDS:
        return [
            _err(
                name,
                f"Registry {name} declares kind '{kind}', which is not one of "
                f"{sorted(_VALID_KINDS)}. The kind selects which consumer channel is "
                f"verified; an unknown kind verifies nothing. Re-run `{_RECOVER}`.",
            )
        ]
    prefix = Path("src") if kind == "code" else Path()
    owner_path = project_root / prefix / owner
    if not owner_path.is_file():
        shown = (prefix / owner).as_posix()
        return [
            _err(
                name,
                f"Registry {name} declares owner '{owner}', which does not exist at "
                f"{shown}. An owner that is not on disk cannot be a verified "
                f"consumer. Re-run `{_RECOVER}`.",
            )
        ]
    if not _references(owner_path, name):
        return [
            _err(
                name,
                f"Registry {name} declares owner '{owner}', but that file never references "
                f"{name}. The owner claim is ASSERTED, not verified — a registry that only "
                f"lists owners is a presence check standing in for a state check (AGENTS.md "
                f"§ DO IT RIGHT). Name the module that actually reads it, or change `kind`. "
                f"Re-run `{_RECOVER}`.",
            )
        ]
    return []


def _relates_to(entry: dict[str, object]) -> list[str]:
    """Narrow ``relates_to`` to a list of names; anything else reads as empty."""
    raw = entry.get("relates_to")
    return [str(x) for x in raw] if isinstance(raw, list) else []


def _check_relation_symmetry(
    entries: dict[str, dict[str, object]],
) -> list[ValidationError]:
    """Every ``relates_to`` edge must be declared from both sides."""
    errors: list[ValidationError] = []
    for name, entry in sorted(entries.items()):
        for sib in _relates_to(entry):
            back = entries.get(sib)
            if back is None:
                errors.append(
                    _err(
                        name,
                        f"Registry {name} declares relates_to '{sib}', which is not declared "
                        f"in {_REGISTRY_REL.as_posix()}. A relation to an unowned registry "
                        f"cannot be checked. Re-run `{_RECOVER}`.",
                    )
                )
                continue
            if name not in _relates_to(back):
                errors.append(
                    _err(
                        name,
                        f"Registry {name} declares relates_to '{sib}', but {sib} does not "
                        f"declare {name} back. A one-way relation leaves the sibling unaware "
                        f"that it encodes a shared concept, which is the prose-reconciliation "
                        f"failure this field replaces. Re-run `{_RECOVER}`.",
                    )
                )
    return errors


def audit_config_registry(project_root: Path) -> list[ValidationError]:
    """Flag any config registry that is undeclared, phantom, unowned, or asymmetric.

    Returns one ``ValidationError`` per finding (non-empty → caller exits 3).
    """
    registry_path = project_root / _REGISTRY_REL
    payload = _load_json(registry_path)
    if not isinstance(payload, dict) or not isinstance(payload.get("registries"), dict):
        return [
            _err(
                "config_registry",
                f"The config registry {_REGISTRY_REL.as_posix()} is missing or unparseable. "
                f"Without it no policy/threshold registry has a declared owner, so every one "
                f"of them is a silent bypass (GHI #929). Author the registry. "
                f"Re-run `{_RECOVER}`.",
            )
        ]

    entries: dict[str, dict[str, object]] = {
        str(k): v for k, v in payload["registries"].items() if isinstance(v, dict)
    }
    data_root = project_root / _DATA_REL
    errors: list[ValidationError] = []

    for name, entry in sorted(entries.items()):
        if not (data_root / name).is_file():
            errors.append(
                _err(
                    name,
                    f"Registry {name} is declared in {_REGISTRY_REL.as_posix()} but no such "
                    f"file exists under data/. A phantom declaration claims ownership of "
                    f"nothing. Remove the entry or restore the file. Re-run `{_RECOVER}`.",
                )
            )
            continue
        errors.extend(
            _verify_owner(
                project_root, name, str(entry.get("owner", "")), str(entry.get("kind", ""))
            )
        )

    errors.extend(_check_relation_symmetry(entries))

    if data_root.is_dir():
        waiver_owned = _waiver_owned(project_root, data_root)
        for found in sorted(data_root.glob("*.json")):
            if found.name in entries or found.name in waiver_owned:
                continue
            errors.append(
                _err(
                    found.name,
                    f"Config registry data/{found.name} exists on disk but is declared in "
                    f"neither {_REGISTRY_REL.as_posix()} nor the waiver-ratchet registry. "
                    f"An unowned config surface is a silent bypass: nothing names who reads "
                    f"it, nothing relates it to a sibling encoding the same concept, and "
                    f"drift in it is caught by no gate (GHI #929). Declare it with an owner "
                    f"and a kind. Re-run `{_RECOVER}`.",
                )
            )
    return errors
