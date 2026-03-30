"""Flag registry loader and validator.

Reads ``data/flags.json``, validates entries against the JSON Schema contract
(via Pydantic model parsing), detects duplicate keys, and returns a typed
mapping of flag keys to FlagSpec instances.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.flags.models import FlagSpec, InvalidFlagValueError

# Default registry path relative to project root.
DEFAULT_REGISTRY_PATH = Path("data") / "flags.json"
DEFAULT_SCHEMA_PATH = Path("data") / "schemas" / "flags.schema.json"


def _validate_schema_structure(data: dict[str, object], schema_path: Path) -> None:
    """Validate registry JSON structure against the schema contract.

    Uses lightweight structural checks (no jsonschema dependency).
    The schema file at *schema_path* is the contract definition; Pydantic
    models provide the actual field-level validation.
    """
    if not isinstance(data, dict):
        msg = "Registry must be a JSON object"
        raise InvalidFlagValueError(msg)

    if "flags" not in data:
        msg = "Registry must contain a 'flags' key"
        raise InvalidFlagValueError(msg)

    if not isinstance(data["flags"], list):
        msg = "Registry 'flags' must be an array"
        raise InvalidFlagValueError(msg)

    extra_keys = set(data.keys()) - {"flags"}
    if extra_keys:
        msg = f"Registry contains unexpected keys: {sorted(extra_keys)}"
        raise InvalidFlagValueError(msg)

    # Validate schema file exists (contract artifact)
    if not schema_path.is_file():
        msg = f"Schema file not found: {schema_path}"
        raise InvalidFlagValueError(msg)


def load_registry(
    path: Path | None = None,
    *,
    schema_path: Path | None = None,
) -> dict[str, FlagSpec]:
    """Load and validate the flag registry.

    Args:
        path: Path to the registry JSON file. Defaults to ``data/flags.json``.
        schema_path: Path to the JSON Schema file. Defaults to
            ``data/schemas/flags.schema.json``.

    Returns:
        Mapping of flag key strings to validated FlagSpec instances.

    Raises:
        InvalidFlagValueError: If the file is missing, malformed, or fails
            structural validation.
        pydantic.ValidationError: If any flag entry fails model validation
            (category rules, missing fields).
        InvalidFlagValueError: If duplicate keys are found.

    """
    registry_path = path or DEFAULT_REGISTRY_PATH
    schema = schema_path or DEFAULT_SCHEMA_PATH

    if not registry_path.is_file():
        msg = f"Registry file not found: {registry_path}"
        raise InvalidFlagValueError(msg)

    raw = registry_path.read_text(encoding="utf-8")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        msg = f"Registry is not valid JSON: {exc}"
        raise InvalidFlagValueError(msg) from exc

    _validate_schema_structure(data, schema)

    flags: dict[str, FlagSpec] = {}
    for i, entry in enumerate(data["flags"]):
        if not isinstance(entry, dict):
            msg = f"Flag entry {i} must be a JSON object"
            raise InvalidFlagValueError(msg)

        spec = FlagSpec.model_validate(entry)

        if spec.key in flags:
            msg = f"Duplicate flag key: {spec.key!r}"
            raise InvalidFlagValueError(msg)

        flags[spec.key] = spec

    return flags
