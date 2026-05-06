"""ADR-0.0.28 complexity-threshold-doctrine validator (OBPI-0.0.28-03).

Loads ``.gzkit/rules/complexity-thresholds.md`` via OBPI-0.0.28-02's
``load_threshold_table``, asserts every canonical metric has at least one
band, asserts the citation tuple parses, and prints a "Bootstrap-mode"
informational notice to stdout when the rule body declares the
bootstrap-absolutes carve-out section.

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
from pathlib import Path

from pydantic import ValidationError as PydanticValidationError

from gzkit.complexity.measurement import CANONICAL_METRICS
from gzkit.complexity.thresholds import load_threshold_table
from gzkit.core.validation_rules import ValidationError

_RULE_RELATIVE_PATH = Path(".gzkit") / "rules" / "complexity-thresholds.md"
BOOTSTRAP_MODE_NOTICE_PREFIX = "Bootstrap-mode"
_LOADER_FAILURE_TYPE = "complexity_thresholds"
_MISSING_RULE_TYPE = "complexity_thresholds"
_MISSING_METRIC_TYPE = "complexity_thresholds"
_BOOTSTRAP_HEADING_PATTERN = re.compile(
    r"^##\s+Bootstrap\s+absolutes",
    re.MULTILINE | re.IGNORECASE,
)


def validate_complexity_thresholds(project_root: Path) -> list[ValidationError]:
    """Validate the canonical complexity-thresholds rule body.

    Returns a list of ``ValidationError`` entries. Empty list = clean.
    The bootstrap-mode notice is printed as a side effect via
    ``_emit_bootstrap_mode_notice`` and does not appear in the returned
    list (so the CLI exits 0 when the rule body declares the carve-out
    and is otherwise well-formed).
    """
    rule_path = project_root / _RULE_RELATIVE_PATH
    if not rule_path.is_file():
        return [_missing_rule_error(rule_path)]

    errors: list[ValidationError] = []
    try:
        table = load_threshold_table(rule_path)
    except PydanticValidationError as exc:
        errors.append(_loader_failure_error(rule_path, exc))
        return errors

    errors.extend(_check_canonical_metric_coverage(table, rule_path))
    if _has_bootstrap_section(rule_path):
        _emit_bootstrap_mode_notice(rule_path)

    return errors


def _missing_rule_error(rule_path: Path) -> ValidationError:
    return ValidationError(
        type=_MISSING_RULE_TYPE,
        artifact=rule_path.as_posix(),
        message=(
            "complexity-thresholds rule body not found at "
            f"{rule_path.as_posix()}; OBPI-0.0.28-01 must land before "
            "the validator can run"
        ),
    )


def _loader_failure_error(rule_path: Path, exc: PydanticValidationError) -> ValidationError:
    return ValidationError(
        type=_LOADER_FAILURE_TYPE,
        artifact=rule_path.as_posix(),
        message=(
            "complexity-thresholds rule body failed to parse into "
            f"ThresholdTable: {exc.error_count()} validation error(s); "
            f"first: {exc.errors()[0]['msg']}"
        ),
    )


def _check_canonical_metric_coverage(table, rule_path: Path) -> list[ValidationError]:
    metrics_in_table = {band.metric for band in table.bands}
    missing = sorted(set(CANONICAL_METRICS) - metrics_in_table)
    if not missing:
        return []
    return [
        ValidationError(
            type=_MISSING_METRIC_TYPE,
            artifact=rule_path.as_posix(),
            message=(
                "complexity-thresholds rule body is missing per-metric "
                f"sections for canonical metric(s): {', '.join(missing)}"
            ),
        )
    ]


def _has_bootstrap_section(rule_path: Path) -> bool:
    body = rule_path.read_text(encoding="utf-8")
    return _BOOTSTRAP_HEADING_PATTERN.search(body) is not None


def _emit_bootstrap_mode_notice(rule_path: Path) -> None:
    """Print the bootstrap-mode notice to stdout (informational only)."""
    print(
        f"{BOOTSTRAP_MODE_NOTICE_PREFIX}: "
        f"{rule_path.as_posix()} declares a Bootstrap absolutes carve-out "
        "section; portability checks against bootstrap rows are skipped per "
        "ADR-0.0.28 § Bootstrap absolutes (REQ-11). This is informational, "
        "not a policy breach — review tracked GHIs (#404 parser zeros, "
        "#405 polarity-aware model) for resolution."
    )
