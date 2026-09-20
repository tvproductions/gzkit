"""The single read seam for config registries under `data/` (GHI #1067).

Before this module, thirty modules each resolved their own `data/<name>.json`
path and ran their own `json.loads`. That is thirty parallel systems, which
`../airlineops/config/README.md` principle 3 forbids and which
`.gzkit/chores/hardcoded-root-eradication` has declared against since 2026-04
with nothing to enforce it.

`project_root` is a PARAMETER, never resolved here (hexagonal § Operative rule 4,
Cockburn: *"Always take a parameter for any external object or technology you
wish to access"*). Five project-root resolvers already exist in this package;
this seam deliberately adds no sixth, and every trust-audit signature already
threads a root, so callers have one to hand.

Scope is deliberately narrow. This is the READ seam, not the config system:
which registries eventually collapse into one settings file, and what counts as
config rather than an implementation detail, is the mapping reserved for
`ADR-0.39.0` (campaign Movement F). Nothing here decides that, and the seam is
built so the mapping can land behind it without touching callers.
"""

import json
from pathlib import Path
from typing import Any

_DATA_DIR = "data"


class RegistryError(RuntimeError):
    """A config registry is missing, unreadable, or not valid JSON.

    Typed so callers can distinguish a config fault from a domain error. The
    thirty hand-rolled readers this seam replaces raised `OSError`,
    `JSONDecodeError`, or nothing at all, so the same fault surfaced three ways
    depending on which module hit it first.
    """


def registry_path(project_root: Path, name: str) -> Path:
    """Return the on-disk path of a registry, without reading it.

    Exposed because several callers need the path for an error message or a
    freshness check; resolving it here keeps `data/` named in one place.
    """
    if Path(name).name != name:
        raise RegistryError(
            f"Registry name {name!r} is not a bare filename. The seam resolves "
            f"names under {_DATA_DIR}/, so a caller passing a path is reaching "
            f"around it (GHI #1067)."
        )
    return project_root / _DATA_DIR / name


def load_registry(project_root: Path, name: str) -> Any:
    """Read and parse one config registry under `data/`.

    Returns the parsed payload as-is: registries are objects, bare arrays, or
    rosters, and coercing them to one shape here would invent a schema the
    mapping decision has not made yet.

    Raises `RegistryError` on a missing file or malformed JSON, so a config
    fault is one exception type rather than three.
    """
    path = registry_path(project_root, name)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RegistryError(
            f"Config registry {_DATA_DIR}/{name} could not be read: {exc}. "
            f"Every registry is declared in {_DATA_DIR}/config_registry.json or the "
            f"waiver-ratchet registry, so a missing one is a tree defect rather than "
            f"an optional file (GHI #1067)."
        ) from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RegistryError(
            f"Config registry {_DATA_DIR}/{name} is not valid JSON: {exc}. "
            f"Execution reads thresholds from JSON, so an unparseable registry "
            f"silently disarms whatever reads it (GHI #1067)."
        ) from exc


def load_registry_field(project_root: Path, name: str, field: str, default: Any = None) -> Any:
    """Read one top-level field from a registry, with a caller-supplied default.

    The shape most callers actually want. `default` is returned only when the
    registry parses and the field is absent -- a missing or malformed registry
    still raises, because defaulting past a broken file is how a disarmed check
    reports green.
    """
    payload = load_registry(project_root, name)
    if not isinstance(payload, dict):
        raise RegistryError(
            f"Config registry {_DATA_DIR}/{name} is not an object, so it has no "
            f"field {field!r}. Read it with load_registry() and handle its shape "
            f"(GHI #1067)."
        )
    return payload.get(field, default)
