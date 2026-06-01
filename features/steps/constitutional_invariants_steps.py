"""Behave step definitions for constitutional invariant composition (OBPI-0.0.37-02/03/04/13).

@covers REQ-0.0.37-02-01
@covers REQ-0.0.37-02-02
@covers REQ-0.0.37-02-04
@covers REQ-0.0.37-04-01
@covers REQ-0.0.37-04-02
@covers REQ-0.0.37-04-03
@covers REQ-0.0.37-04-04
@covers REQ-0.0.37-04-05
@covers REQ-0.0.37-13-01
@covers REQ-0.0.37-13-02
@covers REQ-0.0.37-13-03
@covers REQ-0.0.37-13-04
@covers REQ-0.0.37-13-05
"""

from __future__ import annotations

import io
import json
import warnings
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import jsonschema
from behave import given, then, when  # type: ignore[import-untyped]
from pydantic import ValidationError

from gzkit.cli import main
from gzkit.governance.brief_structure import BriefStructure, LegacyBriefShape, parse_brief


def _invoke_capture(*args: str) -> tuple[int, str]:
    """Invoke gz CLI, return (exit_code, combined_stdout_stderr)."""
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(list(args))
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


def _seed_registry(root: Path) -> None:
    """Write one minimal valid invariant JSON to the registry directory.

    Also copies the canonical agents.md template into the workspace so the
    drift validator's bootstrap-safe guard (template-present check) is
    satisfied (OBPI-0.0.37-03).
    """
    inv_dir = root / ".gzkit" / "invariants"
    inv_dir.mkdir(parents=True, exist_ok=True)
    entry = {
        "id": "CIC-test-seed",
        "claim": "Seed invariant for BDD test.",
        "structural_witness": ["gz validate --test"],
        "composition_targets": ["AGENTS.md"],
    }
    (inv_dir / "CIC-test-seed.json").write_text(json.dumps(entry), encoding="utf-8")

    template_src = Path(__file__).parent.parent.parent / "src" / "gzkit" / "templates" / "agents.md"
    if template_src.exists():
        template_dst_dir = root / ".gzkit" / "templates"
        template_dst_dir.mkdir(parents=True, exist_ok=True)
        (template_dst_dir / "agents.md").write_bytes(template_src.read_bytes())


def _render_bytes(root: Path) -> bytes:
    """Render agents-md to bytes without writing file, patching project root."""

    from gzkit.governance.compose import render_agents_md
    from gzkit.governance.invariants import load_invariants

    template_root = Path(__file__).parent.parent.parent / "src" / "gzkit" / "templates"
    invariants = load_invariants(root)
    return render_agents_md(invariants, template_root, root)


@given("the constitutional invariant registry has at least one entry")
def step_seed_registry(context) -> None:  # type: ignore[no-untyped-def]
    _seed_registry(Path.cwd())


@given("AGENTS.md contains the current rendered output")
def step_agents_md_matches(context) -> None:  # type: ignore[no-untyped-def]
    rendered = _render_bytes(Path.cwd())
    (Path.cwd() / "AGENTS.md").write_bytes(rendered)


@given("AGENTS.md contains stale content")
def step_agents_md_stale(context) -> None:  # type: ignore[no-untyped-def]
    (Path.cwd() / "AGENTS.md").write_text(
        "stale content — does not match rendered output", encoding="utf-8"
    )


@when('I run "gz governance render --target agents-md --stdout" twice')
def step_run_stdout_twice(context) -> None:  # type: ignore[no-untyped-def]
    code1, out1 = _invoke_capture("governance", "render", "--target", "agents-md", "--stdout")
    code2, out2 = _invoke_capture("governance", "render", "--target", "agents-md", "--stdout")
    context.stdout_run1 = out1
    context.stdout_run2 = out2
    context.exit_code = code1


@when('I run "gz governance render --target agents-md --check"')
def step_run_check(context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke_capture("governance", "render", "--target", "agents-md", "--check")
    context.exit_code = code
    context.output = output


@when('I run "gz governance render --target agents-md"')
def step_run_write(context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke_capture("governance", "render", "--target", "agents-md")
    context.exit_code = code
    context.output = output


@when('I run "gz governance render --target skill-readme"')
def step_run_unsupported_target(context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke_capture("governance", "render", "--target", "skill-readme")
    context.exit_code = code
    context.output = output


@when('I run "gz governance render --help"')
def step_run_help(context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke_capture("governance", "render", "--help")
    context.exit_code = code
    context.output = output


@then("AGENTS.md exists in the workspace")
def step_agents_md_exists(context) -> None:  # type: ignore[no-untyped-def]
    assert (Path.cwd() / "AGENTS.md").exists(), "AGENTS.md was not written"


@then("the two outputs are byte-identical")
def step_outputs_byte_identical(context) -> None:  # type: ignore[no-untyped-def]
    assert context.stdout_run1 == context.stdout_run2, (
        f"Outputs are not byte-identical. Run 1 length={len(context.stdout_run1)}, "
        f"Run 2 length={len(context.stdout_run2)}"
    )


# Note: the following shared steps are defined in gz_steps.py and reused here:
# - @then("the command exits with code {expected:d}")
# - @then("the command exits non-zero") / @then("the command exits with a non-zero code")
# - @then('the output contains "{text}"')
# The constitutional invariant steps below are scenario-specific only.


# -- OBPI-0.0.37-03 — Composition drift validator steps --


@given("AGENTS.md matches the rendered registry output")
def step_agents_md_matches_registry(context) -> None:  # type: ignore[no-untyped-def]
    rendered = _render_bytes(Path.cwd())
    (Path.cwd() / "AGENTS.md").write_bytes(rendered)


@given("AGENTS.md differs from the rendered registry output")
def step_agents_md_differs_registry(context) -> None:  # type: ignore[no-untyped-def]
    (Path.cwd() / "AGENTS.md").write_text(
        "drifted content — does not match rendered output", encoding="utf-8"
    )


@when('I run "gz validate --invariant-coherence"')
def step_run_invariant_coherence(context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke_capture("validate", "--invariant-coherence")
    context.exit_code = code
    context.output = output


@then('a "composition_rendered" event is appended to the ledger')
def step_composition_rendered_in_ledger(context) -> None:  # type: ignore[no-untyped-def]
    ledger_path = Path.cwd() / ".gzkit" / "ledger.jsonl"
    assert ledger_path.exists(), "ledger.jsonl does not exist"
    found = False
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("event") == "composition_rendered":
            found = True
            break
    assert found, "no composition_rendered event found in ledger.jsonl"


# -- OBPI-0.0.37-04 — Brief structural schema (BriefStructure / parse_brief) --
#
# These steps wrap the already-landed src/gzkit/governance/brief_structure.py
# API; the scenarios were authored by OBPI-0.0.37-04 without step definitions
# (GHI #513). Assertions derive from the REQ semantics, mirroring
# tests/governance/test_brief_structure.py.

_BRIEF_FIXTURES = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "brief_structure"
_BRIEF_SCHEMA = (
    Path(__file__).parent.parent.parent / "src" / "gzkit" / "schemas" / "obpi_brief_structure.json"
)
_OBPI_0_0_37_04_BRIEF = (
    Path(__file__).parent.parent.parent
    / "docs"
    / "design"
    / "adr"
    / "foundation"
    / "ADR-0.0.37-constitutional-invariant-composition"
    / "obpis"
    / "OBPI-0.0.37-04-brief-structural-schema.md"
)

_VALID_BRIEF_FIELDS = {
    "id": "OBPI-0.0.37-04-brief-structural-schema",
    "parent": "ADR-0.0.37-constitutional-invariant-composition",
    "lane": "Heavy",
    "status": "Draft",
    "allowlist": ["src/x.py"],
    "reqs": ["REQ-0.0.37-04-01"],
    "verification": ["uv run gz lint"],
    "citations": [],
}


@given("a valid BriefStructure field set")
def step_valid_brief_field_set(context) -> None:  # type: ignore[no-untyped-def]
    context.brief_fields = dict(_VALID_BRIEF_FIELDS)


@when("I construct a BriefStructure instance")
def step_construct_brief_structure(context) -> None:  # type: ignore[no-untyped-def]
    context.brief = BriefStructure(**context.brief_fields)


@then("the model is frozen and mutation raises an error")
def step_brief_is_frozen(context) -> None:  # type: ignore[no-untyped-def]
    try:
        context.brief.id = "MUTATED"
    except (ValueError, TypeError):
        return
    raise AssertionError("BriefStructure mutation did not raise — model is not frozen")


@then("constructing with an empty allowlist raises ValidationError")
def step_empty_allowlist_rejected(context) -> None:  # type: ignore[no-untyped-def]
    try:
        BriefStructure(**{**_VALID_BRIEF_FIELDS, "allowlist": []})
    except ValidationError:
        return
    raise AssertionError("empty allowlist did not raise ValidationError")


@then("constructing with an empty reqs list raises ValidationError")
def step_empty_reqs_rejected(context) -> None:  # type: ignore[no-untyped-def]
    try:
        BriefStructure(**{**_VALID_BRIEF_FIELDS, "reqs": []})
    except ValidationError:
        return
    raise AssertionError("empty reqs list did not raise ValidationError")


@given("the obpi_brief_structure.json schema file")
def step_brief_schema_file(context) -> None:  # type: ignore[no-untyped-def]
    context.brief_schema = json.loads(_BRIEF_SCHEMA.read_text(encoding="utf-8"))


@when("I validate a compliant brief instance against it")
def step_validate_compliant_instance(context) -> None:  # type: ignore[no-untyped-def]
    context.schema_error = None
    try:
        jsonschema.validate(dict(_VALID_BRIEF_FIELDS), context.brief_schema)
    except jsonschema.ValidationError as exc:
        context.schema_error = exc


@then("validation succeeds")
def step_schema_validation_succeeds(context) -> None:  # type: ignore[no-untyped-def]
    assert context.schema_error is None, (
        f"compliant instance failed schema validation: {context.schema_error}"
    )


@then("an instance missing the reqs field fails validation")
def step_schema_rejects_missing_reqs(context) -> None:  # type: ignore[no-untyped-def]
    incomplete = {k: v for k, v in _VALID_BRIEF_FIELDS.items() if k != "reqs"}
    try:
        jsonschema.validate(incomplete, context.brief_schema)
    except jsonschema.ValidationError:
        return
    raise AssertionError("instance missing 'reqs' did not fail schema validation")


@given("a legacy OBPI brief file without structured frontmatter fields")
def step_legacy_brief_file(context) -> None:  # type: ignore[no-untyped-def]
    context.brief_path = _BRIEF_FIXTURES / "legacy.md"
    assert context.brief_path.is_file(), f"missing fixture: {context.brief_path}"


@when("I call parse_brief on it in permissive mode")
def step_parse_brief_permissive(context) -> None:  # type: ignore[no-untyped-def]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        context.parsed = parse_brief(context.brief_path)
    context.warnings = list(caught)


@then("the result is a LegacyBriefShape instance")
def step_result_is_legacy_shape(context) -> None:  # type: ignore[no-untyped-def]
    assert isinstance(context.parsed, LegacyBriefShape), (
        f"expected LegacyBriefShape, got {type(context.parsed).__name__}"
    )


@then("a DeprecationWarning is emitted")
def step_deprecation_warning_emitted(context) -> None:  # type: ignore[no-untyped-def]
    deprecations = [w for w in context.warnings if issubclass(w.category, DeprecationWarning)]
    assert deprecations, "parse_brief emitted no DeprecationWarning for a legacy brief"


@when("I call parse_brief on it with strict=True")
def step_parse_brief_strict(context) -> None:  # type: ignore[no-untyped-def]
    context.parse_error = None
    try:
        parse_brief(context.brief_path, strict=True)
    except ValueError as exc:
        context.parse_error = exc


@then("a ValueError is raised")
def step_value_error_raised(context) -> None:  # type: ignore[no-untyped-def]
    assert isinstance(context.parse_error, ValueError), (
        "parse_brief(strict=True) did not raise ValueError on a legacy brief"
    )


@given("the OBPI-0.0.37-04 brief file with structured frontmatter")
def step_obpi_0_0_37_04_brief(context) -> None:  # type: ignore[no-untyped-def]
    context.brief_path = _OBPI_0_0_37_04_BRIEF
    assert context.brief_path.is_file(), f"missing brief: {context.brief_path}"


@when("I call parse_brief on it")
def step_parse_brief_default(context) -> None:  # type: ignore[no-untyped-def]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        context.parsed = parse_brief(context.brief_path)
    context.warnings = list(caught)


@then("the result is a BriefStructure instance")
def step_result_is_brief_structure(context) -> None:  # type: ignore[no-untyped-def]
    assert isinstance(context.parsed, BriefStructure), (
        f"expected BriefStructure, got {type(context.parsed).__name__}"
    )


@then("no DeprecationWarning is emitted")
def step_no_deprecation_warning(context) -> None:  # type: ignore[no-untyped-def]
    deprecations = [w for w in context.warnings if issubclass(w.category, DeprecationWarning)]
    assert not deprecations, f"unexpected DeprecationWarning(s): {deprecations}"


# -- OBPI-0.0.37-13 — Reverse-parse migration steps --

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_AGENTS_MD_PATH = _PROJECT_ROOT / "AGENTS.md"


@given("the AGENTS.md file in the project root")
def step_agents_md_from_project_root(context) -> None:  # type: ignore[no-untyped-def]
    context.parse_source_path = str(_AGENTS_MD_PATH)
    context.parse_source_text = _AGENTS_MD_PATH.read_text(encoding="utf-8")


@when("I parse the file as AgentContract")
def step_parse_file_as_agent_contract(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.content.parse import parse  # noqa: PLC0415

    context.agent_contract = parse(
        context.parse_source_text, "AgentContract", file_path=context.parse_source_path
    )


@then("the model has more than 5 pillars")
def step_model_has_more_than_5_pillars(context) -> None:  # type: ignore[no-untyped-def]
    count = len(context.agent_contract.pillars)
    assert count > 5, f"expected > 5 pillars, got {count}"


@then('a pillar with title "Behavior Rules" exists with non-empty bullets')
def step_behavior_rules_pillar_has_bullets(context) -> None:  # type: ignore[no-untyped-def]
    titles = {p.title for p in context.agent_contract.pillars}
    assert "Behavior Rules" in titles, f"Behavior Rules pillar missing; found: {sorted(titles)}"
    behavior = next(p for p in context.agent_contract.pillars if p.title == "Behavior Rules")
    assert behavior.bullets, "Behavior Rules pillar has no bullets"


@then('a bullet containing "{text1}" and "{text2}" has classification "{classification}"')
def step_bullet_has_classification(context, text1, text2, classification) -> None:  # type: ignore[no-untyped-def]
    bullets = [b for p in context.agent_contract.pillars for b in p.bullets]
    match = next((b for b in bullets if text1 in b.text and text2 in b.text), None)
    assert match is not None, f"no bullet containing both {text1!r} and {text2!r}"
    assert match.classification == classification, (
        f"expected {classification!r}, got {match.classification!r}"
    )


@then('a pillar line containing "{text}" is present in the model')
def step_pillar_line_present(context, text) -> None:  # type: ignore[no-untyped-def]
    rows = "\n".join(line for p in context.agent_contract.pillars for line in p.lines)
    assert text in rows, f"no pillar line containing {text!r} in the imported model"


@then("the model round-trips losslessly through JSON serialization")
def step_model_json_round_trip_lossless(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.content.models.agent_contract import AgentContract  # noqa: PLC0415

    model = context.agent_contract
    rebuilt = AgentContract.model_validate_json(model.model_dump_json())
    assert rebuilt == model, "model↔JSON round-trip is not lossless"


@given("a minimal markdown document with an unmatchable rule")
def step_minimal_doc_with_unmatchable_rule(context) -> None:  # type: ignore[no-untyped-def]
    context.parse_source_text = (
        "# Contract\n\nPurpose line.\n\n## Custom Section\n\n- zzz unmatchable qpwoeiruty rule\n"
    )
    context.parse_source_path = None


@when("I parse it as AgentContract via the content API")
def step_parse_minimal_as_agent_contract(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.content.parse import parse  # noqa: PLC0415

    context.agent_contract = parse(context.parse_source_text, "AgentContract")


@then('the custom-section bullet classification is "{classification}"')
def step_custom_section_bullet_classification(context, classification) -> None:  # type: ignore[no-untyped-def]
    custom = next((p for p in context.agent_contract.pillars if p.title == "Custom Section"), None)
    assert custom is not None, "Custom Section pillar not found"
    assert len(custom.bullets) == 1, f"expected 1 bullet, got {len(custom.bullets)}"
    assert custom.bullets[0].classification == classification, (
        f"expected {classification!r}, got {custom.bullets[0].classification!r}"
    )
