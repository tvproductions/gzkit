"""BDD step definitions for foundation_triage.feature.

@covers REQ-0.0.57-05-03
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from behave import given, then, when

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TRIAGE_SCRIPT = _REPO_ROOT / ".gzkit" / "skills" / "gz-foundation-triage" / "scripts" / "triage.py"


@given('a foundation-triage fixture with ADRs "{adr_ids}" and insights mentioning "{mention_id}"')
def step_setup_triage_fixture(context: object, adr_ids: str, mention_id: str) -> None:
    """Create a minimal fixture tree for the triage script to scan."""
    tmp = Path(tempfile.mkdtemp())
    context.triage_project_root = tmp  # type: ignore

    foundation_root = tmp / "docs" / "design" / "adr" / "foundation"
    for adr_id in (a.strip() for a in adr_ids.split(",")):
        # Use -foundation- infix so the triage script's ID extraction works:
        # "ADR-0.0.1-foundation-fixture".split("-foundation-", 1)[0] == "ADR-0.0.1"
        slug = f"{adr_id}-foundation-fixture"
        adr_dir = foundation_root / slug
        adr_dir.mkdir(parents=True, exist_ok=True)
        (adr_dir / f"{slug}.md").write_text(
            f"---\nid: {slug}\nstatus: Draft\ntitle: Fixture {adr_id}\n---\n\n# {adr_id}\n",
            encoding="utf-8",
        )

    insights_dir = tmp / ".gzkit" / "insights"
    insights_dir.mkdir(parents=True, exist_ok=True)
    (insights_dir / "agent-insights.jsonl").write_text(
        f'{{"scope": "{mention_id}", "summary": "signal for {mention_id}", '
        f'"evidence": "test", "next_action": "review"}}\n',
        encoding="utf-8",
    )


@when('I run the foundation-triage script with format "{fmt}"')
def step_run_triage_script(context: object, fmt: str) -> None:
    """Run the triage script against the fixture and store stdout in context."""
    result = subprocess.run(
        [
            sys.executable,
            str(_TRIAGE_SCRIPT),
            "--format",
            fmt,
            "--project-root",
            str(context.triage_project_root),  # type: ignore
        ],
        capture_output=True,
        text=True,
    )
    context.output = result.stdout  # type: ignore
    context.triage_output = result.stdout  # type: ignore
    context.triage_returncode = result.returncode  # type: ignore


@then('the JSON contains an entry with id containing "{pattern}"')
def step_json_contains_id(context: object, pattern: str) -> None:
    records: list[dict[str, object]] = json.loads(context.triage_output)  # type: ignore
    ids = [r.get("id", "") for r in records]
    assert any(pattern in str(i) for i in ids), (
        f"No entry with id containing '{pattern}'. Got: {ids}"
    )
