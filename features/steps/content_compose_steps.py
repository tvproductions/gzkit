"""BDD steps for gz content compose — OBPI-0.0.37-21.

@covers REQ-0.0.37-21-01
@covers REQ-0.0.37-21-02
@covers REQ-0.0.37-21-03
@covers REQ-0.0.37-21-04
@covers REQ-0.0.37-21-05
"""

from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from behave import given, then, when

from gzkit.cli import main
from gzkit.content.corpus_store import append_entry
from gzkit.content.models import CorpusEntry

_VENDOR_MANIFEST = {
    "content_type_routes": {"AgentContract": ["claude", "codex"]},
    "content_type_temperatures": {"AgentContract": {"codex": "lite", "claude": "heavy"}},
}


def _invoke(args: list[str]) -> tuple[int, str]:
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


def _make_corpus_entry(entry_id: str, *, tier: str, text: str) -> CorpusEntry:
    return CorpusEntry(
        id=entry_id,
        surface="AGENTS.md",
        section="prime-directive" if tier == "invariant" else "behavior-rules",
        tier=tier,
        classification="Mechanical" if tier == "invariant" else "Ambiguous",
        text=text,
        origin="bdd-test",
        ts="2026-06-14T00:00:00Z",
    )


@given("I have initialized a gzkit project")
def step_init_project(context) -> None:
    """Set up minimal project structure: data/ dir + vendor manifest + .gzkit/ dir."""
    root = Path.cwd()
    (root / "data").mkdir(exist_ok=True)
    (root / "data" / "vendor-manifest.json").write_text(
        json.dumps(_VENDOR_MANIFEST), encoding="utf-8"
    )
    (root / ".gzkit").mkdir(exist_ok=True)
    context.root = root
    context.exit_code = None
    context.output = ""
    context.candidate_file = root / "candidate.md"


@given('the vendor manifest declares setpoint "lite" for (AgentContract, codex)')
def step_vendor_manifest_lite(_context) -> None:
    """Already set up in step_init_project via _VENDOR_MANIFEST."""


@given('the corpus for "AGENTS.md" contains an invariant entry "{text}"')
def step_corpus_invariant(context, text: str) -> None:
    entry = _make_corpus_entry("e-inv", tier="invariant", text=text)
    append_entry(context.root, "AGENTS.md", entry)
    context.invariant_text = text


@given('the corpus for "AGENTS.md" contains a compressible entry "{text}"')
def step_corpus_compressible(context, text: str) -> None:
    entry = _make_corpus_entry("e-comp", tier="compressible", text=text)
    append_entry(context.root, "AGENTS.md", entry)


@given("a candidate file containing the invariant entry and compressed compressible content")
def step_candidate_with_invariant_and_compressed(context) -> None:
    text = f"{context.invariant_text}\nsome compressed content"
    context.candidate_file.write_text(text, encoding="utf-8")


@given("a candidate file containing the invariant entry and some content")
def step_candidate_with_invariant_and_content(context) -> None:
    text = f"{context.invariant_text}\nsome content"
    context.candidate_file.write_text(text, encoding="utf-8")


@given("a candidate file containing the invariant entry text")
def step_candidate_with_invariant_text(context) -> None:
    text = f"{context.invariant_text}\nsome other content"
    context.candidate_file.write_text(text, encoding="utf-8")


@given("a candidate file containing the invariant entry text verbatim")
def step_candidate_with_invariant_verbatim(context) -> None:
    text = f"{context.invariant_text}\nsome other content"
    context.candidate_file.write_text(text, encoding="utf-8")


@given("a valid candidate file containing the invariant entry")
def step_valid_candidate(context) -> None:
    text = f"{context.invariant_text}\nsome compressed content"
    context.candidate_file.write_text(text, encoding="utf-8")


@given('no corpus store exists for "{surface}"')
def step_no_corpus(context, surface: str) -> None:
    context.missing_surface = surface


@given("a candidate file with some text")
def step_candidate_any(_context) -> None:
    Path("candidate.md").write_text("some text", encoding="utf-8")


@given('"{filename}" exists with some content')
def step_surface_exists(_context, filename: str) -> None:
    Path(filename).write_text(f"# {filename}\nsome content", encoding="utf-8")


@when('I run "gz content compose AGENTS.md --consumer codex --candidate <file>"')
def step_run_compose(context) -> None:
    code, output = _invoke(
        [
            "content",
            "compose",
            "AGENTS.md",
            "--consumer",
            "codex",
            "--candidate",
            str(context.candidate_file),
        ]
    )
    context.exit_code = code
    context.output = output


@when('I run "gz content compose AGENTS.md --consumer codex --candidate <file>" twice')
def step_run_compose_twice(context) -> None:
    args = [
        "content",
        "compose",
        "AGENTS.md",
        "--consumer",
        "codex",
        "--candidate",
        str(context.candidate_file),
    ]
    code1, output1 = _invoke(args)
    code2, output2 = _invoke(args)
    context.last_exit_code = code2
    context.last_output = output2
    context.compose_outputs = [output1, output2]
    context.exit_code = code2
    context.output = output2


@when('I run "gz content compose AGENTS.md --consumer unknown-vendor --candidate <file>"')
def step_run_compose_unknown_vendor(context) -> None:
    code, output = _invoke(
        [
            "content",
            "compose",
            "AGENTS.md",
            "--consumer",
            "unknown-vendor",
            "--candidate",
            str(context.candidate_file),
        ]
    )
    context.exit_code = code
    context.output = output


@when('I run "gz content compose MISSING.md --consumer codex --candidate <file>"')
def step_run_compose_missing_surface(context) -> None:
    candidate = context.root / "candidate.md"
    if not candidate.exists():
        candidate.write_text("some text", encoding="utf-8")
    code, output = _invoke(
        ["content", "compose", "MISSING.md", "--consumer", "codex", "--candidate", str(candidate)]
    )
    context.exit_code = code
    context.output = output


@then("the command exits 0")
def step_exits_0(context) -> None:
    assert context.exit_code == 0, (
        f"Expected exit 0, got {context.exit_code}. Output: {context.output}"
    )


@then('the candidate file exists at "{path}"')
def step_candidate_exists(_context, path: str) -> None:
    assert Path(path).exists(), f"Expected candidate at {path!r} but it does not exist"


@then('the output includes "{text}"')
def step_output_includes(context, text: str) -> None:
    assert text in context.output, f"Expected {text!r} in output. Got: {context.output}"


@then('the ledger contains a "{event_type}" event for surface "{surface}"')
def step_ledger_has_event(_context, event_type: str, surface: str) -> None:
    ledger_path = Path(".gzkit") / "ledger.jsonl"
    assert ledger_path.exists(), "Ledger not found"
    events = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    matching = [e for e in events if e.get("event") == event_type and e.get("surface") == surface]
    assert matching, (
        f"No {event_type!r} event for surface {surface!r} in ledger. "
        f"Events: {[e.get('event') for e in events]}"
    )


@then("both runs exit 0")
def step_both_exit_0(context) -> None:
    assert context.exit_code == 0, f"Second run failed: {context.output}"


@then("the byte evidence output is identical between runs")
def step_byte_evidence_identical(context) -> None:
    assert context.compose_outputs[0] == context.compose_outputs[1], (
        f"Outputs differ:\n{context.compose_outputs[0]!r}\n{context.compose_outputs[1]!r}"
    )


@then('the candidate at "{path}" contains the invariant text verbatim')
def step_candidate_contains_invariant(context, path: str) -> None:
    text = Path(path).read_text(encoding="utf-8")
    assert context.invariant_text in text, (
        f"Invariant text {context.invariant_text!r} not found in candidate at {path!r}"
    )


@then('no candidate file is written at "{path}"')
def step_no_candidate(context, path: str) -> None:
    assert not Path(path).exists(), f"Expected no candidate at {path!r} but it exists"


@then('no candidate file is written for "{consumer}"')
def step_no_candidate_for_consumer(_context, consumer: str) -> None:
    rend_dir = Path(".gzkit") / "renditions" / "AGENTS.md"
    candidate = rend_dir / f"{consumer}.candidate.md"
    assert not candidate.exists(), f"Expected no candidate at {candidate} but it exists"


@then('"{filename}" is byte-unchanged')
def step_file_unchanged(context, filename: str) -> None:
    expected = f"# {filename}\nsome content"
    actual = Path(filename).read_text(encoding="utf-8")
    assert actual == expected, f"{filename!r} was modified. Expected: {expected!r}, Got: {actual!r}"
