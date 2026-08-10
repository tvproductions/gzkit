"""BDD steps for gz adr audit-check covers-backfill heuristic.

ADR-0.0.23 / OBPI-0.0.23-05 — heavy-lane fail-closed end-to-end witness
for the same-commit-window @covers backfill heuristic.

Sets up a real git repo inside the per-scenario tempdir so the heuristic
walks real `git log -L<line>:<file>` and `git rev-list --count` output
against a controlled history shape: a single seed commit that contains
both the @covers decorator AND the OBPI's closing-receipt event. The
heuristic computes 0c / 0d gap and flags as blocking under heavy lane.

Reuses `When I run the gz command "..."` and `Then the command exits
with code N` and `Then the output contains "..."` from gz_steps.py.

@covers REQ-0.0.23-05-09
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from behave import given

from gzkit.config import GzkitConfig
from gzkit.event_evidence import EventAnchor
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    obpi_created_event,
    obpi_receipt_emitted_event,
)


@given('the audit-thresholds file is present at "{path}"')
def step_thresholds_present(_context, path: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {"max_covers_backfill_commits": 3, "max_covers_backfill_days": 7},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


@given("a heavy ADR with a same-commit @covers backfill exists for OBPI-0.1.0-01-demo")
def step_same_commit_backfill_setup(_context) -> None:
    """Author a heavy-lane ADR + OBPI + test decorator, then commit them all
    in a single seed commit and emit the closing-receipt event whose
    ``anchor.commit`` SHA matches that same commit. The heuristic reads the
    decorator's introducing commit (= seed) and the receipt's anchor commit
    (= seed), computes 0c / 0d gap, and flags the decorator as blocking.
    """
    config = GzkitConfig.load(Path(".gzkit.json"))
    adrs_dir = Path(config.paths.adrs)
    adrs_dir.mkdir(parents=True, exist_ok=True)

    # Heavy-lane ADR with kind=foundation so the severity matrix forces
    # blocking regardless of --strict.
    adr_id = "ADR-0.1.0-f"
    adr_path = adrs_dir / f"{adr_id}.md"
    adr_path.write_text(
        "\n".join(
            [
                "---",
                f"id: {adr_id}",
                "status: Completed",
                "kind: foundation",
                "semver: 0.1.0",
                "lane: heavy",
                "parent: PRD-GZKIT-1.0.0",
                "date: 2026-04-02",
                "---",
                "",
                f"# {adr_id}: BDD fixture",
                "",
                "## Decision",
                "",
                "Synthetic ADR for the BDD covers-backfill scenario.",
                "",
                "## Checklist",
                "",
                "- [x] OBPI-0.1.0-01-demo",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    # OBPI with one REQ.
    obpi_path = adrs_dir / "obpis" / "OBPI-0.1.0-01-demo.md"
    obpi_path.parent.mkdir(parents=True, exist_ok=True)
    obpi_path.write_text(
        "\n".join(
            [
                "---",
                "id: OBPI-0.1.0-01-demo",
                f"parent: {adr_id}",
                "item: 1",
                "lane: Heavy",
                "status: Completed",
                "---",
                "",
                "# OBPI-0.1.0-01-demo: BDD fixture",
                "",
                "**Brief Status:** Completed",
                "",
                "## Allowed Paths",
                "- `tests/test_demo.py` - in scope",
                "",
                "## Acceptance Criteria",
                "",
                "- [x] REQ-0.1.0-01-01: synthetic REQ for the BDD scenario.",
                "",
                "## Evidence",
                "",
                "### Implementation Summary",
                "- Files created/modified: tests/test_demo.py",
                "- Validation commands run: uv run gz test",
                "- Date completed: 2026-04-02",
                "",
                "### Key Proof",
                "uv run gz adr audit-check ADR-0.1.0-f",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    # Test file with the @covers decorator at a known line.
    tests_dir = Path("tests")
    tests_dir.mkdir(parents=True, exist_ok=True)
    test_file = tests_dir / "test_demo.py"
    test_file.write_text(
        "\n".join(
            [
                '"""Synthetic test file for the BDD covers-backfill scenario."""',
                "",
                "",
                "# @covers REQ-0.1.0-01-01",
                "def test_demo() -> None:",
                "    assert True",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    # Initialise git, author the SINGLE seed commit holding both the
    # decorator AND (via the ledger receipt below) the closing receipt.
    subprocess.run(["git", "init", "-b", "main"], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.name", "BDD User"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "bdd@example.com"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "seed: same-commit backfill fixture"],
        check=True,
        capture_output=True,
        text=True,
    )
    head = subprocess.run(
        ["git", "rev-parse", "--short=7", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    # Ledger: ADR + OBPI created, closing-receipt event with anchor=head SHA.
    ledger = Ledger(Path(".gzkit/ledger.jsonl"))
    ledger.append(adr_created_event(adr_id, "PRD-GZKIT-1.0.0", "heavy"))
    ledger.append(obpi_created_event("OBPI-0.1.0-01-demo", adr_id))
    ledger.append(
        obpi_receipt_emitted_event(
            obpi_id="OBPI-0.1.0-01-demo",
            parent_adr=adr_id,
            receipt_event="completed",
            attestor="human:bdd",
            obpi_completion="completed",
            evidence={
                "value_narrative": "BDD synthetic — closing receipt anchored at head.",
                "key_proof": "uv run gz adr audit-check ADR-0.1.0-f",
            },
            anchor=EventAnchor(commit=head, semver="0.1.0"),
        )
    )
