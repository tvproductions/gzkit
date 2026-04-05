"""BDD steps for persona control surface scenarios."""

from __future__ import annotations

import json
from pathlib import Path

from behave import given


@given('a persona file "{name}" exists')
def step_persona_file_exists(_context, name: str) -> None:  # type: ignore[no-untyped-def]
    personas_dir = Path(".gzkit/personas")
    personas_dir.mkdir(parents=True, exist_ok=True)
    persona_file = personas_dir / f"{name}.md"
    persona_file.write_text(
        "---\n"
        f"name: {name}\n"
        "traits:\n"
        "  - methodical\n"
        "  - test-first\n"
        "anti-traits:\n"
        "  - minimum-viable-effort\n"
        "grounding: Behavioral anchor text.\n"
        "---\n\n"
        f"# {name.title()} Persona\n\nBehavioral identity frame.\n",
        encoding="utf-8",
    )


@given("the ledger contains governance events")
def step_ledger_governance_events(_context) -> None:  # type: ignore[no-untyped-def]
    ledger = Path(".gzkit/ledger.jsonl")
    events = [
        {"schema": "gzkit.ledger.v1", "event": "gate_checked", "ts": "2026-01-01T00:00:00Z"},
        {"schema": "gzkit.ledger.v1", "event": "attested", "ts": "2026-01-02T00:00:00Z"},
        {"schema": "gzkit.ledger.v1", "event": "adr_created", "ts": "2025-12-01T00:00:00Z"},
    ]
    with ledger.open("a", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")
