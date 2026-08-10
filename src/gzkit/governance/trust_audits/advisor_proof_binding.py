"""Fail-closed audit: advisor diagnosis verdict <-> proof binding (OBPI-0.0.29-08).

Defense-in-depth backstop. Model-layer enforcement (OBPI-0.0.29-01) and
engine-layer enforcement (OBPI-0.0.29-02) prevent empty-proof diagnoses at
runtime; this validator catches any that nonetheless reach fixtures, ledger
events, or the JSON Schema. Three scan scopes:

* Fixture scope: ``tests/fixtures/advisor/*.json``
* Ledger scope: ``intrinsic-complexity-attestation`` events in
  ``.gzkit/ledger.jsonl`` whose payload references a diagnosis id
* Schema scope: ``src/gzkit/schemas/advisor_diagnosis.json`` must require
  ``properties.proof.minItems >= 1``

A speculative-marker escape (``"_negative_case": true`` at the fixture's top
level) skips fixtures explicitly authored as tests of the empty-proof
rejection. Without the escape, the OBPI-0.0.29-01 model test (which asserts
``ValidationError`` on empty proof) would itself trigger the validator.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.core.validation_rules import ValidationError

_NEGATIVE_CASE_KEY = "_negative_case"


def validate_advisor_proof_binding(project_root: Path) -> list[ValidationError]:
    """Return ValidationErrors for any advisor diagnosis surface with empty proof."""
    errors: list[ValidationError] = []
    fixtures_by_id = _index_fixtures_by_id(project_root)
    errors.extend(_scan_fixtures(project_root))
    errors.extend(_scan_ledger(project_root, fixtures_by_id))
    errors.extend(_scan_schema(project_root))
    return errors


def _scan_fixtures(project_root: Path) -> list[ValidationError]:
    fixtures_dir = project_root / "tests" / "fixtures" / "advisor"
    if not fixtures_dir.exists():
        return []
    errors: list[ValidationError] = []
    for path in sorted(fixtures_dir.glob("*.json")):
        data = _read_json_dict(path)
        if data is None:
            continue
        if data.get(_NEGATIVE_CASE_KEY) is True:
            continue
        if not _has_non_empty_proof(data):
            line = _locate_proof_line(path) or 1
            display = _relative(path, project_root)
            errors.append(
                ValidationError(
                    type="advisor_proof_binding",
                    artifact=display,
                    message=(
                        f"Advisor diagnosis fixture {display}:{line}: "
                        "`proof` is empty. Verdict <-> proof binding requires "
                        "non-empty proof: tuple[ProofRange, ...] (ADR-0.0.29)."
                    ),
                )
            )
    return errors


def _scan_ledger(
    project_root: Path,
    fixtures_by_id: dict[str, dict[str, object]],
) -> list[ValidationError]:
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return []
    errors: list[ValidationError] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("event") != "intrinsic-complexity-attestation":
            continue
        diag_ref = ev.get("diagnosis_id") or ev.get("diagnosis_ref")
        if not diag_ref:
            continue
        diag = fixtures_by_id.get(diag_ref)
        if diag is None:
            continue  # OBPI-07 owns event-shape validation; unresolvable refs aren't ours
        if not _has_non_empty_proof(diag):
            event_id = ev.get("id", "<unknown>")
            errors.append(
                ValidationError(
                    type="advisor_proof_binding",
                    artifact=str(event_id),
                    message=(
                        f"intrinsic-complexity-attestation event {event_id!r} "
                        f"cites diagnosis {diag_ref!r} with empty `proof`."
                    ),
                )
            )
    return errors


def _scan_schema(project_root: Path) -> list[ValidationError]:
    schema_path = project_root / "src" / "gzkit" / "schemas" / "advisor_diagnosis.json"
    if not schema_path.exists():
        return []
    display = _relative(schema_path, project_root)
    schema = _read_json_dict(schema_path)
    if schema is None:
        return [
            ValidationError(
                type="advisor_proof_binding",
                artifact=display,
                message=f"{display}: not a JSON object.",
            )
        ]
    proof_node = _nested_dict(schema, "properties", "proof")
    min_items = proof_node.get("minItems")
    if not isinstance(min_items, int) or min_items < 1:
        return [
            ValidationError(
                type="advisor_proof_binding",
                artifact=display,
                message=(
                    f"{display}: properties.proof.minItems must "
                    f"be an integer >= 1; found {min_items!r}."
                ),
            )
        ]
    return []


def _index_fixtures_by_id(project_root: Path) -> dict[str, dict[str, object]]:
    fixtures_dir = project_root / "tests" / "fixtures" / "advisor"
    if not fixtures_dir.exists():
        return {}
    indexed: dict[str, dict[str, object]] = {}
    for path in fixtures_dir.glob("*.json"):
        data = _read_json_dict(path)
        if data is None:
            continue
        diag_id = data.get("id")
        if isinstance(diag_id, str) and diag_id:
            indexed[diag_id] = data
    return indexed


def _nested_dict(root: dict[str, object], *keys: str) -> dict[str, object]:
    """Walk nested dict keys; return ``{}`` if any segment is missing or non-dict."""
    cursor: dict[str, object] = root
    for key in keys:
        value = cursor.get(key)
        if not isinstance(value, dict):
            return {}
        cursor = value
    return cursor


def _has_non_empty_proof(payload: dict[str, object]) -> bool:
    proof = payload.get("proof")
    return isinstance(proof, list) and len(proof) > 0


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _read_json_dict(path: Path) -> dict[str, object] | None:
    """Read a JSON object; return ``None`` for unreadable, malformed, or non-object payloads."""
    payload = _read_json(path)
    if isinstance(payload, dict):
        return payload
    return None


def _relative(path: Path, project_root: Path) -> str:
    """Render ``path`` relative to ``project_root`` if possible (POSIX form)."""
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def _locate_proof_line(path: Path) -> int | None:
    """Best-effort scan for the literal `"proof"` token; returns 1-indexed line."""
    try:
        for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if '"proof"' in line:
                return idx
    except OSError:
        return None
    return None
