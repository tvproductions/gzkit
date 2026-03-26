"""Eval dataset loader — loads and validates reference datasets by surface name.

Provides typed Pydantic models for eval dataset fixtures and a loader that
discovers datasets from ``data/eval/`` by surface name. Validates fixtures
against the JSON schema structure on load.
"""

import json
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_DATA_DIR = _PROJECT_ROOT / "data" / "eval"
_SCHEMA_PATH = _PROJECT_ROOT / "data" / "schemas" / "eval_dataset.schema.json"

KNOWN_SURFACES: list[str] = [
    "instruction_eval",
    "adr_eval",
    "skills",
    "rules",
    "agents_md",
]


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class EvalDatasetCase(BaseModel):
    """One eval case within a dataset — golden-path or edge-case fixture."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="Unique case identifier")
    type: str = Field(..., description="golden_path or edge_case")
    description: str = Field(..., description="What this case tests")
    input: dict[str, object] = Field(..., description="Surface-specific input data")
    expected_output: dict[str, object] = Field(..., description="Expected eval result")


class EvalDataset(BaseModel):
    """A reference dataset for one AI-sensitive surface."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., description="AI-sensitive surface identifier")
    version: str = Field(..., description="Dataset version (semver)")
    description: str = Field(..., description="What this dataset covers")
    cases: list[EvalDatasetCase] = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_VALID_CASE_TYPES = {"golden_path", "edge_case"}


def _load_schema() -> dict[str, object]:
    """Load the eval dataset JSON schema."""
    result: dict[str, object] = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    return result


class DatasetValidationError(ValueError):
    """Raised when a dataset fixture fails structural validation."""


def validate_dataset_json(data: dict[str, object]) -> None:
    """Validate raw JSON data against the eval dataset schema.

    Validates required fields, types, semver format, and case structure
    without requiring the ``jsonschema`` package.

    Raises ``DatasetValidationError`` on invalid data.
    """
    required_top = {"surface", "version", "description", "cases"}
    missing = required_top - set(data.keys())
    if missing:
        msg = f"Missing required fields: {sorted(missing)}"
        raise DatasetValidationError(msg)

    extra = set(data.keys()) - required_top
    if extra:
        msg = f"Unexpected fields: {sorted(extra)}"
        raise DatasetValidationError(msg)

    if not isinstance(data["surface"], str):
        msg = "Field 'surface' must be a string"
        raise DatasetValidationError(msg)
    if not isinstance(data["version"], str) or not _SEMVER_RE.match(data["version"]):
        msg = "Field 'version' must be a semver string (e.g. '1.0.0')"
        raise DatasetValidationError(msg)
    if not isinstance(data["description"], str):
        msg = "Field 'description' must be a string"
        raise DatasetValidationError(msg)

    cases = data["cases"]
    if not isinstance(cases, list) or len(cases) < 1:
        msg = "Field 'cases' must be a non-empty array"
        raise DatasetValidationError(msg)

    required_case = {"id", "type", "description", "input", "expected_output"}
    for i, raw_case in enumerate(cases):
        if not isinstance(raw_case, dict):
            msg = f"Case {i} must be an object"
            raise DatasetValidationError(msg)
        case = dict(raw_case)
        case_missing = required_case - set(case.keys())
        if case_missing:
            msg = f"Case {i} missing fields: {sorted(case_missing)}"
            raise DatasetValidationError(msg)
        case_extra = set(case.keys()) - required_case
        if case_extra:
            msg = f"Case {i} has unexpected fields: {sorted(case_extra)}"
            raise DatasetValidationError(msg)
        if case["type"] not in _VALID_CASE_TYPES:
            msg = f"Case {i} type must be 'golden_path' or 'edge_case', got '{case['type']}'"
            raise DatasetValidationError(msg)
        if not isinstance(case["input"], dict):
            msg = f"Case {i} input must be an object"
            raise DatasetValidationError(msg)
        if not isinstance(case["expected_output"], dict):
            msg = f"Case {i} expected_output must be an object"
            raise DatasetValidationError(msg)


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_dataset(surface: str, *, data_dir: Path | None = None) -> EvalDataset:
    """Load an eval dataset by surface name.

    Searches ``data_dir`` (default ``data/eval/``) for JSON files whose
    ``surface`` field matches the requested name. Validates against the
    JSON schema before parsing into the Pydantic model.

    Raises ``FileNotFoundError`` if no dataset matches.
    Raises ``DatasetValidationError`` if the dataset is structurally invalid.
    """
    search_dir = data_dir or _DATA_DIR
    for path in sorted(search_dir.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw.get("surface") == surface:
            validate_dataset_json(raw)
            return EvalDataset.model_validate(raw)

    msg = f"No eval dataset found for surface: {surface}"
    raise FileNotFoundError(msg)


def load_all_datasets(*, data_dir: Path | None = None) -> list[EvalDataset]:
    """Load and validate all eval datasets from ``data_dir``."""
    search_dir = data_dir or _DATA_DIR
    datasets: list[EvalDataset] = []
    for path in sorted(search_dir.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        validate_dataset_json(raw)
        datasets.append(EvalDataset.model_validate(raw))
    return datasets


def list_surfaces(*, data_dir: Path | None = None) -> list[str]:
    """Return surface names for all available datasets."""
    return [ds.surface for ds in load_all_datasets(data_dir=data_dir)]
