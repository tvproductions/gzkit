"""BDD steps for OBPI reviewer agent dispatch (ADR-0.23.0 / OBPI-0.23.0-03)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from behave import given, then, when

from gzkit.commands.pipeline import (
    ClosingArgumentQuality,
    DocsQuality,
    PromiseAssessment,
    ReviewerAssessment,
    compose_reviewer_prompt,
    format_reviewer_for_ceremony,
    parse_reviewer_assessment,
    store_reviewer_assessment,
)
from gzkit.roles import ReviewVerdict

# ---------------------------------------------------------------------------
# Prompt composition steps
# ---------------------------------------------------------------------------


@given("an OBPI brief with {count:d} requirements")
def step_brief_with_requirements(context, count):
    reqs = "\n".join(f"1. REQUIREMENT: Deliver feature {i}" for i in range(1, count + 1))
    context.brief_content = f"# OBPI Brief\n\n## REQUIREMENTS (FAIL-CLOSED)\n\n{reqs}\n"
    context.obpi_id = "OBPI-0.23.0-03"


@given('a closing argument "{text}"')
def step_closing_argument(context, text):
    context.closing_argument = text


@given("no closing argument")
def step_no_closing_argument(context):
    context.closing_argument = ""


@given("{changed:d} changed files and {docs:d} doc file")
@given("{changed:d} changed files and {docs:d} doc files")
def step_changed_and_doc_files(context, changed, docs):
    context.files_changed = [f"src/file{i}.py" for i in range(1, changed + 1)]
    context.doc_files = [f"docs/doc{i}.md" for i in range(1, docs + 1)]


@when("I compose the reviewer prompt")
def step_compose_prompt(context):
    context.prompt = compose_reviewer_prompt(
        context.obpi_id,
        context.brief_content,
        context.closing_argument,
        context.files_changed,
        context.doc_files,
    )


@then("the prompt contains the OBPI identifier")
def step_prompt_has_obpi_id(context):
    assert context.obpi_id in context.prompt, "OBPI ID not found in prompt"


@then("the prompt contains the brief content")
def step_prompt_has_brief(context):
    assert "OBPI Brief" in context.prompt, "Brief content not found in prompt"


@then("the prompt contains the closing argument")
def step_prompt_has_closing_argument(context):
    assert context.closing_argument in context.prompt, "Closing argument not found"


@then("the prompt contains all changed files")
def step_prompt_has_changed_files(context):
    for f in context.files_changed:
        assert f"`{f}`" in context.prompt, f"Changed file {f} not found in prompt"


@then("the prompt contains the doc file")
def step_prompt_has_doc_file(context):
    for f in context.doc_files:
        assert f"`{f}`" in context.prompt, f"Doc file {f} not found in prompt"


@then("the prompt contains the assessment JSON schema")
def step_prompt_has_json_schema(context):
    assert "promises_met" in context.prompt, "JSON schema missing promises_met"
    assert "docs_quality" in context.prompt, "JSON schema missing docs_quality"
    assert "closing_argument_quality" in context.prompt, (
        "JSON schema missing closing_argument_quality"
    )


@then('the reviewer prompt contains "{text}"')
def step_reviewer_prompt_contains(context, text):
    assert text in context.prompt, f"'{text}' not found in prompt"


# ---------------------------------------------------------------------------
# Parse assessment steps
# ---------------------------------------------------------------------------


def _wrap_assessment(data: dict) -> str:
    return f"Review complete.\n```json\n{json.dumps(data)}\n```\nEnd of review."


@given("agent output with a valid PASS assessment for {count:d} requirements")
def step_pass_assessment(context, count):
    promises = [
        {"requirement": f"Deliver feature {i}", "met": True, "evidence": f"Found in code {i}"}
        for i in range(1, count + 1)
    ]
    context.agent_output = _wrap_assessment(
        {
            "promises_met": promises,
            "docs_quality": "substantive",
            "docs_evidence": "Good docs",
            "closing_argument_quality": "earned",
            "closing_argument_evidence": "Real evidence",
            "summary": "All good",
            "verdict": "PASS",
        }
    )
    context.obpi_id = "OBPI-0.23.0-03"


@given("agent output with a valid FAIL assessment")
def step_fail_assessment(context):
    context.agent_output = _wrap_assessment(
        {
            "promises_met": [{"requirement": "REQ-1", "met": False}],
            "docs_quality": "missing",
            "closing_argument_quality": "missing",
            "summary": "Nothing delivered",
            "verdict": "FAIL",
        }
    )
    context.obpi_id = "OBPI-0.23.0-03"


@given("agent output with a CONCERNS assessment and mixed promises")
def step_concerns_assessment(context):
    context.agent_output = _wrap_assessment(
        {
            "promises_met": [
                {"requirement": "REQ-1", "met": True, "evidence": "ok"},
                {"requirement": "REQ-2", "met": False, "evidence": "partial"},
            ],
            "docs_quality": "boilerplate",
            "closing_argument_quality": "echoed",
            "summary": "Minor gaps",
            "verdict": "CONCERNS",
        }
    )
    context.obpi_id = "OBPI-0.23.0-03"


@given("agent output with no JSON block")
def step_no_json_output(context):
    context.agent_output = "No structured output here."
    context.obpi_id = "OBPI-0.23.0-03"


@when("I parse the reviewer assessment")
def step_parse_assessment(context):
    context.assessment = parse_reviewer_assessment(context.agent_output, context.obpi_id)


@then('the assessment verdict is "{verdict}"')
def step_assessment_verdict(context, verdict):
    assert context.assessment is not None, "Assessment is None"
    assert context.assessment.verdict.value == verdict, (
        f"Expected {verdict}, got {context.assessment.verdict.value}"
    )


@then("{count:d} promise assessments are returned")
def step_promise_count(context, count):
    assert context.assessment is not None, "Assessment is None"
    assert len(context.assessment.promises_met) == count, (
        f"Expected {count} promises, got {len(context.assessment.promises_met)}"
    )


@then('docs quality is "{quality}"')
def step_docs_quality(context, quality):
    assert context.assessment is not None, "Assessment is None"
    assert context.assessment.docs_quality.value == quality, (
        f"Expected {quality}, got {context.assessment.docs_quality.value}"
    )


@then('closing argument quality is "{quality}"')
def step_closing_argument_quality(context, quality):
    assert context.assessment is not None, "Assessment is None"
    assert context.assessment.closing_argument_quality.value == quality, (
        f"Expected {quality}, got {context.assessment.closing_argument_quality.value}"
    )


@then("promise {idx:d} is met")
def step_promise_met(context, idx):
    assert context.assessment is not None, "Assessment is None"
    promise = context.assessment.promises_met[idx - 1]
    assert promise.met, f"Promise {idx} was not met"


@then("promise {idx:d} is not met")
def step_promise_not_met(context, idx):
    assert context.assessment is not None, "Assessment is None"
    promise = context.assessment.promises_met[idx - 1]
    assert not promise.met, f"Promise {idx} was met"


@then("no assessment is returned")
def step_no_assessment(context):
    assert context.assessment is None, "Expected None assessment"


# ---------------------------------------------------------------------------
# Artifact storage steps
# ---------------------------------------------------------------------------


@given("a parsed PASS reviewer assessment")
def step_parsed_pass_assessment(context):
    context.assessment = ReviewerAssessment(
        obpi_id="OBPI-0.23.0-03",
        promises_met=[
            PromiseAssessment(requirement="Define reviewer role", met=True, evidence="In roles.py"),
        ],
        docs_quality=DocsQuality.SUBSTANTIVE,
        docs_evidence="Runbook updated",
        closing_argument_quality=ClosingArgumentQuality.EARNED,
        closing_argument_evidence="Cites test output",
        summary="Complete with strong evidence",
        verdict=ReviewVerdict.PASS,
    )


@given("a temporary ADR package directory")
def step_temp_adr_dir(context):
    context.temp_dir = tempfile.TemporaryDirectory()
    context.adr_package_dir = Path(context.temp_dir.name)


@when("I store the reviewer assessment")
def step_store_assessment(context):
    context.artifact_path = store_reviewer_assessment(context.assessment, context.adr_package_dir)


@then("a REVIEW artifact file exists in the briefs directory")
def step_artifact_exists(context):
    assert context.artifact_path.exists(), f"Artifact not found at {context.artifact_path}"
    assert context.artifact_path.name.startswith("REVIEW-"), "Filename must start with REVIEW-"
    assert context.artifact_path.parent.name == "briefs", "Must be in briefs/ directory"


@then("the artifact contains the verdict")
def step_artifact_has_verdict(context):
    content = context.artifact_path.read_text(encoding="utf-8")
    assert "PASS" in content, "Verdict not found in artifact"


@then("the artifact contains promise assessments")
def step_artifact_has_promises(context):
    content = context.artifact_path.read_text(encoding="utf-8")
    assert "Define reviewer role" in content, "Promise not found in artifact"


# ---------------------------------------------------------------------------
# Ceremony formatting steps
# ---------------------------------------------------------------------------


@given("a parsed CONCERNS reviewer assessment with {count:d} promises")
def step_concerns_assessment_for_ceremony(context, count):
    promises = [
        PromiseAssessment(requirement=f"REQ-{i}", met=(i % 2 == 1), evidence=f"Evidence {i}")
        for i in range(1, count + 1)
    ]
    context.assessment = ReviewerAssessment(
        obpi_id="OBPI-0.23.0-03",
        promises_met=promises,
        docs_quality=DocsQuality.BOILERPLATE,
        closing_argument_quality=ClosingArgumentQuality.ECHOED,
        summary="Needs work",
        verdict=ReviewVerdict.CONCERNS,
    )


@when("I format the assessment for ceremony")
def step_format_for_ceremony(context):
    context.ceremony_output = format_reviewer_for_ceremony(context.assessment)


@then("the output contains a promise table with {count:d} rows")
def step_ceremony_has_table_rows(context, count):
    lines = context.ceremony_output.splitlines()
    data_rows = [
        line
        for line in lines
        if line.startswith("| ") and not line.startswith("| #") and not line.startswith("|---")
    ]
    assert len(data_rows) == count, f"Expected {count} data rows, got {len(data_rows)}"


@then("the output contains the docs quality")
def step_ceremony_has_docs_quality(context):
    assert "boilerplate" in context.ceremony_output, "Docs quality not found"


@then("the output contains the closing argument quality")
def step_ceremony_has_closing_quality(context):
    assert "echoed" in context.ceremony_output, "Closing argument quality not found"


@then("the output contains the verdict")
def step_ceremony_has_verdict(context):
    assert "CONCERNS" in context.ceremony_output, "Verdict not found"
