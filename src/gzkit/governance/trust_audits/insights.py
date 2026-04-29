"""agent-insights.jsonl record-shape trust audit (GHI #358).

The file is a Layer-2 trust surface — it witnesses course-correction lessons
(AGENTS.md § Behavior Rules — Always #11) and observed defects. The schema
lock (GHI #358) closes the silent-shape-drift vector: any agent appending a
record with a bad timestamp, an unknown ``type``, an unknown extra field, or
a nested-object ``evidence`` payload now fails closed.

Historical drift is preserved via ``_INSIGHTS_SHAPE_WAIVERS`` keyed by SHA-256
content hash (first 16 hex chars) so fixture files in tests cannot
accidentally inherit the waiver. The waiver table is closed: new writes must
conform.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.validate import ValidationError

_INSIGHTS_FILE = Path(".gzkit") / "insights" / "agent-insights.jsonl"

# GHI #358: existing entries authored before the schema lock landed —
# waived by content hash rather than line number so fixture files in
# tests cannot accidentally inherit the waiver. Trust-doctrine T2
# forbids rewriting closed-evidence files; new writes must conform; the
# waiver table never grows. Hash is the first 16 hex chars of
# SHA-256(line_bytes).
_INSIGHTS_SHAPE_WAIVERS: dict[str, str] = {
    "e9213698e88610c7": "Pre-lock: date-only `ts` and `resolution` field (DEFECT-2026-02-22).",
    "ab8d07600f66a550": "Pre-lock: date-only `ts` (DEFECT-2026-02-22 resolution).",
    "c9f902574ff970a3": "Pre-lock: nested-object `evidence` (ADR-0.4.0 closeout connectivity).",
    "729446b01ff3a1fb": "Pre-lock: nested-object `evidence` (ADR-0.4.0 retry).",
    "d824f55ea9de18c7": "Pre-lock: plural `adr_ids` (ADR-0.1.0/ADR-0.2.0 reconciliation).",
    "537315562819f427": "Pre-lock: plural `adr_ids` (ADR-0.1.0/ADR-0.2.0 resolution).",
}


def audit_insights_shape(project_root: Path) -> list[ValidationError]:
    """Validate every record in ``.gzkit/insights/agent-insights.jsonl``."""
    import hashlib  # noqa: PLC0415

    from pydantic import ValidationError as PydanticValidationError  # noqa: PLC0415

    from gzkit.insights import InsightRecord  # noqa: PLC0415

    insights_path = project_root / _INSIGHTS_FILE
    if not insights_path.is_file():
        return []
    errors: list[ValidationError] = []
    artifact_root = _INSIGHTS_FILE.as_posix()
    for lineno, raw in enumerate(insights_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        if digest in _INSIGHTS_SHAPE_WAIVERS:
            continue
        artifact = f"{artifact_root}:{lineno}"
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(
                ValidationError(
                    type="insights_shape",
                    artifact=artifact,
                    message=f"line is not valid JSON: {exc.msg}",
                )
            )
            continue
        if not isinstance(payload, dict):
            errors.append(
                ValidationError(
                    type="insights_shape",
                    artifact=artifact,
                    message="line is JSON but not an object",
                )
            )
            continue
        try:
            InsightRecord.model_validate(payload)
        except PydanticValidationError as exc:
            errors.append(
                ValidationError(
                    type="insights_shape",
                    artifact=artifact,
                    message=(
                        "record fails InsightRecord schema "
                        f"({exc.error_count()} errors): "
                        + "; ".join(
                            f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}"
                            for err in exc.errors()[:3]
                        )
                    ),
                )
            )
    return errors
