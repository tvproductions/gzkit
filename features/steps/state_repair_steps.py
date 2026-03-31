"""BDD steps for state repair feature (OBPI-0.0.9-03)."""

from __future__ import annotations

import json
from pathlib import Path

from behave import given, then

from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, obpi_created_event, obpi_receipt_emitted_event


@given('an OBPI brief exists with frontmatter status "{status}"')
def step_create_obpi_brief(context, status: str) -> None:  # type: ignore[no-untyped-def]
    config = GzkitConfig.load(Path(".gzkit.json"))
    obpi_dir = Path(config.paths.adrs) / "obpis"
    obpi_dir.mkdir(parents=True, exist_ok=True)
    brief = obpi_dir / "OBPI-0.1.0-01-state-repair-test.md"
    brief.write_text(
        f"---\nid: OBPI-0.1.0-01-state-repair-test\nparent: ADR-0.1.0\n"
        f"item: 1\nlane: lite\nstatus: {status}\n---\n\n"
        f"# OBPI-0.1.0-01: State Repair Test\n\n**Brief Status:** {status}\n",
        encoding="utf-8",
    )
    context.obpi_brief_path = brief


@given("the ledger marks OBPI-0.1.0-01 as completed")
def step_ledger_mark_completed(context) -> None:  # type: ignore[no-untyped-def]
    ledger = Ledger(Path(".gzkit/ledger.jsonl"))
    ledger.append(obpi_created_event("OBPI-0.1.0-01", "ADR-0.1.0"))
    ledger.append(
        obpi_receipt_emitted_event(
            obpi_id="OBPI-0.1.0-01",
            parent_adr="ADR-0.1.0",
            receipt_event="completed",
            attestor="bdd-test",
            obpi_completion="completed",
            evidence={
                "value_narrative": "State repair test evidence.",
                "key_proof": "uv run gz state --repair",
            },
        )
    )


@then('the OBPI brief frontmatter status is "{expected}"')
def step_check_brief_status(context, expected: str) -> None:  # type: ignore[no-untyped-def]
    content = context.obpi_brief_path.read_text(encoding="utf-8")
    assert f"status: {expected}" in content, (
        f"Expected 'status: {expected}' in frontmatter, got:\n{content}"
    )


@then('the JSON output field "{field}" equals {expected:d}')
def step_json_field_equals(context, field: str, expected: int) -> None:  # type: ignore[no-untyped-def]
    payload = json.loads(context.output)
    actual = payload[field]
    assert actual == expected, (
        f"Expected {field}={expected}, got {actual}. Output: {context.output}"
    )
