"""Acceptance evidence for the approved big-picture R&D publication contract."""

import hashlib
import json

from behave import given, then


@given("a draft big-picture assessment with configured publication paths")
def step_report_draft(context):
    root = context.project_root
    (root / ".gzkit.json").write_text(
        json.dumps({"paths": {"docs_root": "manual", "ledger": "state/events.jsonl"}}),
        encoding="utf-8",
    )
    (root / "draft.md").write_bytes(b"# Perspective\n\nValue with uncertainty.\n")


@then("the assessment is retained exactly with one publication witness")
def step_report_retained(context):
    root = context.project_root
    content = (root / "draft.md").read_bytes()
    directory = root / "manual/reports/big-picture"
    assert (directory / "2026-09-19-assessment.md").read_bytes() == content
    assert (directory / "current.md").read_bytes() == content
    events = [
        json.loads(line)
        for line in (root / "state/events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(events) == 1
    assert events[0]["event"] == "report_published"
    assert events[0]["sha256"] == hashlib.sha256(content).hexdigest()
