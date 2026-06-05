"""Behave step definitions for constitutional invariant composition (OBPI-0.0.37-02/03/04/13/14/15).

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
@covers REQ-0.0.37-14-01
@covers REQ-0.0.37-14-02
@covers REQ-0.0.37-14-03
@covers REQ-0.0.37-14-04
@covers REQ-0.0.37-15-01
@covers REQ-0.0.37-15-02
@covers REQ-0.0.37-15-03
@covers REQ-0.0.37-15-04
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


# OBPI-0.0.37-14 — Wire sync through the renderer; retire the monolith


def _sync_agents_md_via_model(root: Path) -> None:
    """Render AGENTS.md through the model pipeline (sync_agents_md)."""
    from gzkit.config import GzkitConfig  # noqa: PLC0415
    from gzkit.sync_surfaces import sync_agents_md  # noqa: PLC0415

    config = GzkitConfig.load(root / ".gzkit.json")
    sync_agents_md(root, config)


@when("I sync AGENTS.md via the model pipeline")
def step_sync_agents_md_via_model(context) -> None:  # type: ignore[no-untyped-def]
    _sync_agents_md_via_model(Path.cwd())


@given("AGENTS.md has been synced via the model pipeline")
def step_agents_md_synced_via_model(context) -> None:  # type: ignore[no-untyped-def]
    _sync_agents_md_via_model(Path.cwd())


@then("the committed AGENTS.md matches the model render")
def step_committed_agents_md_matches_model(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.governance.trust_audits.invariant_coherence import (  # noqa: PLC0415
        validate_invariant_coherence,
    )

    errors = validate_invariant_coherence(Path.cwd())
    assert errors == [], f"expected no coherence drift, got: {errors}"


@then("the rendered AGENTS.md contains the project purpose value")
def step_rendered_contains_purpose(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.config import GzkitConfig  # noqa: PLC0415
    from gzkit.sync_surfaces import get_project_context  # noqa: PLC0415

    root = Path.cwd()
    config = GzkitConfig.load(root / ".gzkit.json")
    purpose = get_project_context(root, config)["project_purpose"]
    rendered = (root / "AGENTS.md").read_text(encoding="utf-8")
    assert purpose in rendered, f"purpose {purpose!r} not found in rendered AGENTS.md"


@when("I hand-edit AGENTS.md outside the render path")
def step_hand_edit_agents_md(context) -> None:  # type: ignore[no-untyped-def]
    agents_path = Path.cwd() / "AGENTS.md"
    original = agents_path.read_bytes()
    agents_path.write_bytes(original + b"\n\nHAND_EDITED_MARKER_SHOULD_NOT_SURVIVE\n")


@then('"gz validate --invariant-coherence" reports a coherence error')
def step_invariant_coherence_reports_error(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.governance.trust_audits.invariant_coherence import (  # noqa: PLC0415
        validate_invariant_coherence,
    )

    errors = validate_invariant_coherence(Path.cwd())
    assert len(errors) > 0, "expected a coherence error after hand-edit, got none"
    assert errors[0].type == "invariant_coherence", f"unexpected error type: {errors[0].type}"


@then('the rendered AGENTS.md contains the section "{section}"')
def step_rendered_contains_section(context, section) -> None:  # type: ignore[no-untyped-def]
    rendered = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")
    assert section in rendered, f"section {section!r} not found in rendered AGENTS.md"


# ---------------------------------------------------------------------------
# OBPI-0.0.37-15 — Per-vendor template selection
# ---------------------------------------------------------------------------


@given("a vendor manifest declaring AgentContract temperatures codex=lite, claude=heavy")
def step_manifest_with_temperatures(context) -> None:  # type: ignore[no-untyped-def]
    import json
    import tempfile

    tmp = tempfile.mkdtemp()
    context.add_cleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
    root = Path(tmp)
    (root / "data").mkdir()
    manifest = {
        "content_type_routes": {"AgentContract": ["claude", "codex"]},
        "content_type_temperatures": {"AgentContract": {"codex": "lite", "claude": "heavy"}},
    }
    (root / "data" / "vendor-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    context.temp_project_root = root


@when("I call temperature_for for AgentContract and claude")
def step_call_temperature_for_claude(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.content.vendors import temperature_for

    context.temperature_result = temperature_for(
        "AgentContract", "claude", project_root=context.temp_project_root
    )
    context.temperature_error = None


@when("I call temperature_for for AgentContract and an unknown vendor")
def step_call_temperature_for_unknown(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.content.vendors import temperature_for

    context.temperature_result = None
    try:
        temperature_for("AgentContract", "__unknown__", project_root=context.temp_project_root)
        context.temperature_error = None
    except ValueError as exc:
        context.temperature_error = exc


@then('the resolved temperature is "{temperature}"')
def step_resolved_temperature(context, temperature) -> None:  # type: ignore[no-untyped-def]
    assert context.temperature_result == temperature, (
        f"expected {temperature!r}, got {context.temperature_result!r}"
    )


@then("a temperature ValueError is raised")
def step_temperature_value_error_raised(context) -> None:  # type: ignore[no-untyped-def]
    assert context.temperature_error is not None, "expected ValueError but none was raised"
    assert isinstance(context.temperature_error, ValueError)


@given("an AgentContract with a Judgment bullet and a heavy-only bullet")
def step_agent_contract_with_mixed_bullets(context) -> None:  # type: ignore[no-untyped-def]
    import json
    import tempfile

    from gzkit.content.models import AgentContract, Bullet

    context.mixed_contract = AgentContract(
        name="Test",
        purpose="Test contract",
        rules=[
            Bullet(text="judgment-bullet", classification="Judgment", density_min="lite"),
            Bullet(text="heavy-only-bullet", density_min="heavy"),
        ],
    )
    tmp = tempfile.mkdtemp()
    context.add_cleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
    root = Path(tmp)
    (root / "data").mkdir()
    manifest = {
        "content_type_routes": {"AgentContract": ["claude", "codex"]},
        "content_type_temperatures": {"AgentContract": {"codex": "lite", "claude": "heavy"}},
    }
    (root / "data" / "vendor-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    context.temp_project_root = root


@when("I render the contract for codex at lite temperature")
def step_render_codex_lite(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.content.render import render

    context.codex_render = render(
        context.mixed_contract, "codex", temperature="lite", project_root=context.temp_project_root
    )


@then("the Judgment bullet is present in the rendered output")
def step_judgment_bullet_present(context) -> None:  # type: ignore[no-untyped-def]
    assert b"judgment-bullet" in context.codex_render, (
        "Judgment bullet must appear in codex lite render (0-Kelvin floor)"
    )


@then("the heavy-only bullet is absent from the rendered output")
def step_heavy_bullet_absent(context) -> None:  # type: ignore[no-untyped-def]
    assert b"heavy-only-bullet" not in context.codex_render, (
        "Heavy-only bullet must not appear in codex lite render"
    )


@when("I render the contract for codex at lite and claude at heavy")
def step_render_both_vendors(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.content.render import render

    context.codex_render = render(
        context.mixed_contract, "codex", temperature="lite", project_root=context.temp_project_root
    )
    context.claude_render = render(
        context.mixed_contract,
        "claude",
        temperature="heavy",
        project_root=context.temp_project_root,
    )


@then("the two rendered outputs differ")
def step_renders_differ(context) -> None:  # type: ignore[no-untyped-def]
    assert context.codex_render != context.claude_render, (
        "Codex lite and claude heavy renders must differ (identical mirroring ended)"
    )


# ---------------------------------------------------------------------------
# OBPI-0.0.37-18 — append-only corpus model (Gate 4 BDD)
# @covers REQ-0.0.37-18-01
# @covers REQ-0.0.37-18-02
# @covers REQ-0.0.37-18-03
# @covers REQ-0.0.37-18-04
# ---------------------------------------------------------------------------

_CORPUS_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "src" / "gzkit" / "schemas" / "corpus_entry.json"
)


def _corpus_entry(**overrides):  # type: ignore[no-untyped-def]
    """Build a conformant CorpusEntry for the corpus scenarios."""
    from gzkit.content.models import CorpusEntry  # noqa: PLC0415

    base = {
        "id": "c1",
        "surface": "AGENTS.md",
        "section": "prime-directive",
        "tier": "invariant",
        "classification": "Mechanical",
        "text": "YOU OWN THE WORK COMPLETELY.",
        "origin": "GHI#519",
        "ts": "2026-06-05T00:00:00Z",
    }
    base.update(overrides)
    return CorpusEntry(**base)


@given("a corpus entry with all ten addressed fields populated")
def step_corpus_entry_full(context) -> None:  # type: ignore[no-untyped-def]
    context.corpus_entry = _corpus_entry(anchor="a1", witness="gz validate --foo")


@then("the corpus entry model has exactly the ten addressed fields")
def step_corpus_entry_ten_fields(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.content.models import CorpusEntry  # noqa: PLC0415

    assert set(CorpusEntry.model_fields) == {
        "id",
        "surface",
        "section",
        "anchor",
        "tier",
        "classification",
        "witness",
        "text",
        "origin",
        "ts",
    }


@then("constructing a corpus entry with an unknown field fails closed")
def step_corpus_entry_extra_forbidden(context) -> None:  # type: ignore[no-untyped-def]
    try:
        _corpus_entry(unexpected="x")
    except ValidationError:
        return
    raise AssertionError("expected ValidationError for an unknown corpus-entry field")


@given("an empty corpus")
def step_empty_corpus(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.content.models import Corpus  # noqa: PLC0415

    context.corpus = Corpus()


@when("two corpus entries are appended")
def step_corpus_append_two(context) -> None:  # type: ignore[no-untyped-def]
    context.corpus_appended = context.corpus.append(_corpus_entry(id="a")).append(
        _corpus_entry(id="b")
    )


@then("the corpus holds two entries and the original empty corpus is unchanged")
def step_corpus_append_immutability(context) -> None:  # type: ignore[no-untyped-def]
    assert len(context.corpus_appended.entries) == 2
    assert len(context.corpus.entries) == 0


@then("the corpus round-trips losslessly through JSONL")
def step_corpus_round_trip(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.content.models import Corpus  # noqa: PLC0415

    assert Corpus.loads(context.corpus_appended.dumps()) == context.corpus_appended


@given('an agent contract whose only section is "prime-directive"')
def step_corpus_contract(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.content.models import AgentContract, Pillar  # noqa: PLC0415

    context.corpus_contract = AgentContract(
        name="Test",
        purpose="corpus conformance fixture",
        pillars=[Pillar(id="prime-directive", title="Prime Directive", order=1)],
    )


@then('a corpus entry in section "prime-directive" validates against the contract')
def step_corpus_conformant(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.content.models import Corpus  # noqa: PLC0415

    Corpus().append(_corpus_entry(section="prime-directive")).validate_against(
        context.corpus_contract
    )


@then('a corpus entry in section "no-such-section" fails validation')
def step_corpus_nonconformant(context) -> None:  # type: ignore[no-untyped-def]
    from gzkit.content.models import Corpus  # noqa: PLC0415

    try:
        Corpus().append(_corpus_entry(section="no-such-section")).validate_against(
            context.corpus_contract
        )
    except ValueError:
        return
    raise AssertionError("expected ValueError for a section resolving to no Pillar")


@given("the corpus_entry JSON Schema")
def step_corpus_schema(context) -> None:  # type: ignore[no-untyped-def]
    context.corpus_schema = json.loads(_CORPUS_SCHEMA_PATH.read_text(encoding="utf-8"))


@then("the schema accepts a conformant corpus entry")
def step_corpus_schema_accepts(context) -> None:  # type: ignore[no-untyped-def]
    jsonschema.validate(_corpus_entry().model_dump(), context.corpus_schema)


@then("the schema rejects a corpus entry with an out-of-enum tier")
def step_corpus_schema_rejects(context) -> None:  # type: ignore[no-untyped-def]
    bad = _corpus_entry().model_dump()
    bad["tier"] = "ephemeral"
    try:
        jsonschema.validate(bad, context.corpus_schema)
    except jsonschema.ValidationError:
        return
    raise AssertionError("expected schema rejection for an out-of-enum tier")
