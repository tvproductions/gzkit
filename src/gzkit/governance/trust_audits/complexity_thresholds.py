"""ADR-0.0.28 complexity-threshold-doctrine validator (OBPI-0.0.28-03).

Loads ``.gzkit/rules/complexity-thresholds.json`` via OBPI-0.0.28-02's
``load_threshold_table`` (GHI #426 — data is JSON, narrative is markdown),
asserts every canonical metric has at least one band, asserts the citation
tuple parses, and prints a "Bootstrap-mode" informational notice to stdout
when the sibling narrative ``.gzkit/rules/complexity-thresholds.md``
declares the bootstrap-absolutes carve-out section.

The bootstrap-mode notice is intentionally **not** a ``ValidationError``:
the CLI's exit-code logic treats every entry in the returned list as an
error (exit 1 for non-policy types, exit 3 for policy-breach types). A
warning that should surface but not change exit code must be emitted as
a side effect, not as a list entry.

Wired into ``gz validate --complexity-thresholds`` (explicit scope) and the
``gz check`` aggregator under the "Complexity-thresholds" step.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from pydantic import ValidationError as PydanticValidationError

from gzkit.advisory import emit_advisory
from gzkit.complexity.measurement import CANONICAL_METRICS
from gzkit.complexity.thresholds import load_threshold_table
from gzkit.core.validation_rules import ValidationError

_DATA_RELATIVE_PATH = Path(".gzkit") / "rules" / "complexity-thresholds.json"
_NARRATIVE_RELATIVE_PATH = Path(".gzkit") / "rules" / "complexity-thresholds.md"
BOOTSTRAP_MODE_NOTICE_PREFIX = "Bootstrap-mode"
_LOADER_FAILURE_TYPE = "complexity_thresholds"
_MISSING_DATA_TYPE = "complexity_thresholds"
_MISSING_METRIC_TYPE = "complexity_thresholds"
_BOOTSTRAP_HEADING_PATTERN = re.compile(
    r"^##\s+Bootstrap\s+absolutes",
    re.MULTILINE | re.IGNORECASE,
)


def validate_complexity_thresholds(project_root: Path) -> list[ValidationError]:
    """Validate the canonical complexity-thresholds data file.

    Returns a list of ``ValidationError`` entries. Empty list = clean.
    The bootstrap-mode notice is printed as a side effect via
    ``_emit_bootstrap_mode_notice`` and does not appear in the returned
    list (so the CLI exits 0 when the narrative declares the carve-out
    and the data file is otherwise well-formed).
    """
    data_path = project_root / _DATA_RELATIVE_PATH
    if not data_path.is_file():
        return [_missing_data_error(data_path)]

    errors: list[ValidationError] = []
    try:
        table = load_threshold_table(data_path)
    except (PydanticValidationError, ValueError) as exc:
        errors.append(_loader_failure_error(data_path, exc))
        return errors

    errors.extend(_check_canonical_metric_coverage(table, data_path))

    narrative_path = project_root / _NARRATIVE_RELATIVE_PATH
    if narrative_path.is_file() and _has_bootstrap_section(narrative_path):
        _emit_bootstrap_mode_notice(narrative_path)

    return errors


def _missing_data_error(data_path: Path) -> ValidationError:
    return ValidationError(
        type=_MISSING_DATA_TYPE,
        artifact=data_path.as_posix(),
        message=(
            "complexity-thresholds data file not found at "
            f"{data_path.as_posix()}; OBPI-0.0.28-01 must land before "
            "the validator can run (GHI #426 — data is JSON, narrative is .md)"
        ),
    )


def _loader_failure_error(
    data_path: Path, exc: PydanticValidationError | ValueError
) -> ValidationError:
    if isinstance(exc, PydanticValidationError):
        message = (
            f"complexity-thresholds data file failed to parse into "
            f"ThresholdTable: {exc.error_count()} validation error(s); "
            f"first: {exc.errors()[0]['msg']}"
        )
    else:
        message = f"complexity-thresholds data file failed to parse into ThresholdTable: {exc}"
    return ValidationError(
        type=_LOADER_FAILURE_TYPE,
        artifact=data_path.as_posix(),
        message=message,
    )


def _check_canonical_metric_coverage(table, data_path: Path) -> list[ValidationError]:
    metrics_in_table = {band.metric for band in table.bands}
    missing = sorted(set(CANONICAL_METRICS) - metrics_in_table)
    if not missing:
        return []
    return [
        ValidationError(
            type=_MISSING_METRIC_TYPE,
            artifact=data_path.as_posix(),
            message=(
                "complexity-thresholds data file is missing per-metric "
                f"bands for canonical metric(s): {', '.join(missing)}"
            ),
        )
    ]


def _has_bootstrap_section(narrative_path: Path) -> bool:
    body = narrative_path.read_text(encoding="utf-8")
    return _BOOTSTRAP_HEADING_PATTERN.search(body) is not None


def _emit_bootstrap_mode_notice(narrative_path: Path) -> None:
    """Print the bootstrap-mode notice to stdout (informational only)."""
    emit_advisory(
        f"{BOOTSTRAP_MODE_NOTICE_PREFIX}: "
        f"{narrative_path.as_posix()} declares a Bootstrap absolutes carve-out "
        "section; portability checks against bootstrap rows are skipped per "
        "ADR-0.0.28 § Bootstrap absolutes (REQ-11). This is informational, "
        "not a policy breach — review tracked GHIs (#404 parser zeros, "
        "#405 polarity-aware model) for resolution.",
        stream=sys.stdout,
    )
