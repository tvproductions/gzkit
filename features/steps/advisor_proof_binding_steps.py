"""Behave step definitions for advisor verdict <-> proof binding (OBPI-0.0.29-08).

Provides Given steps that plant fixtures, ledger events, and a conforming
JSON schema in the per-scenario workspace (see ``features/environment.py``).
The shared ``When I run the gz command`` and ``Then the command exits with
code N`` / ``Then the output contains`` steps live in ``gz_steps.py``.

@covers REQ-0.0.29-08-02
@covers REQ-0.0.29-08-03
"""

from __future__ import annotations

import json
from pathlib import Path

from behave import given  # type: ignore[import-untyped]


def _empty_proof_diagnosis(diag_id: str | None = None) -> dict:
    diag = {
        "metric": "radon_cc",
        "crossing_band": "warn",
        "crossing_value": 8.5,
        "archetype": "long_parameter_list",
        "doctrinal_frame": {
            "authority": "fowler",
            "citation": "Refactoring 2e p.78",
            "excerpt": "Long parameter lists are a code smell.",
        },
        "proof": [],
        "recommended_move": "Extract Parameter Object.",
    }
    if diag_id is not None:
        diag["id"] = diag_id
    return diag


def _conforming_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "proof": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "object"},
            }
        },
    }


@given('an advisor diagnosis fixture "{name}" with empty proof')
def step_empty_proof_fixture(_context, name: str) -> None:  # type: ignore[no-untyped-def]
    fixtures_dir = Path.cwd() / "tests" / "fixtures" / "advisor"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    (fixtures_dir / name).write_text(
        json.dumps(_empty_proof_diagnosis(), indent=2),
        encoding="utf-8",
    )


@given('an advisor diagnosis fixture "{name}" with id "{diag_id}" and empty proof')
def step_empty_proof_fixture_with_id(  # type: ignore[no-untyped-def]
    _context,
    name: str,
    diag_id: str,
) -> None:
    fixtures_dir = Path.cwd() / "tests" / "fixtures" / "advisor"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    (fixtures_dir / name).write_text(
        json.dumps(_empty_proof_diagnosis(diag_id), indent=2),
        encoding="utf-8",
    )


@given('an intrinsic-complexity-attestation event "{event_id}" cites "{diag_id}"')
def step_ica_event_cites(  # type: ignore[no-untyped-def]
    _context,
    event_id: str,
    diag_id: str,
) -> None:
    ledger_path = Path.cwd() / ".gzkit" / "ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "schema": "gzkit.ledger.v1",
        "event": "intrinsic-complexity-attestation",
        "id": event_id,
        "ts": "2026-05-08T00:00:00+00:00",
        "diagnosis_id": diag_id,
    }
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


@given("a conforming advisor diagnosis schema")
def step_conforming_schema(_context) -> None:  # type: ignore[no-untyped-def]
    schema_path = Path.cwd() / "src" / "gzkit" / "schemas" / "advisor_diagnosis.json"
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_text(json.dumps(_conforming_schema(), indent=2), encoding="utf-8")
