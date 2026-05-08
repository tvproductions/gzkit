"""BDD steps for the ADR-0.0.25 OBPI completion REQ-coverage gate.

Covers REQ-0.0.25-01-01..06 (coverage gate in ``gz obpi complete``),
REQ-0.0.25-02-01..05 (override path + ADR emit-receipt mirror), and
REQ-0.0.25-03-01..03 (doc and feature-file self-coverage).

Scenarios run against the real CLI (``from gzkit.cli import main``) with
fixtures staged on disk in the per-scenario tempdir. Fixture test files are
plain Python unittest modules with a local ``covers`` stub so they run via
``uv run -m unittest`` without importing gzkit at test time.

@covers REQ-0.0.25-01-01
@covers REQ-0.0.25-01-02
@covers REQ-0.0.25-01-03
@covers REQ-0.0.25-01-04
@covers REQ-0.0.25-01-05
@covers REQ-0.0.25-01-06
@covers REQ-0.0.25-02-01
@covers REQ-0.0.25-02-02
@covers REQ-0.0.25-02-03
@covers REQ-0.0.25-02-04
@covers REQ-0.0.25-02-05
@covers REQ-0.0.25-03-01
@covers REQ-0.0.25-03-02
@covers REQ-0.0.25-03-03
@covers REQ-0.0.25-03-04
"""

from __future__ import annotations

import io
import json
import os
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from behave import given, then, when

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, adr_created_event, obpi_created_event

# ---------------------------------------------------------------------------
# In-process CLI driver
# ---------------------------------------------------------------------------


def _invoke(args: list[str]) -> tuple[int, str]:
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


# ---------------------------------------------------------------------------
# ARB receipt fixtures
# ---------------------------------------------------------------------------


def _receipts_root(context) -> Path:  # type: ignore[no-untyped-def]
    if not hasattr(context, "_orig_arb_receipts_root"):
        context._orig_arb_receipts_root = os.environ.get("GZKIT_ARB_RECEIPTS_ROOT")
    root = Path.cwd() / "artifacts" / "receipts"
    root.mkdir(parents=True, exist_ok=True)
    os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = str(root)
    return root


def _write_step_receipt(root: Path, run_id: str, *, exit_status: int) -> None:
    name = run_id[len("arb-step-") :].rsplit("-", 1)[0]
    payload = {
        "schema": "gzkit.arb.step_receipt.v1",
        "run_id": run_id,
        "timestamp_utc": "2026-05-03T12:00:00Z",
        "duration_ms": 10,
        "exit_status": exit_status,
        "stdout_tail": "",
        "stdout_truncated": False,
        "stderr_tail": "",
        "stderr_truncated": False,
        "git": {"commit": "abcdef0", "branch": "main", "dirty": False},
        "step": {"name": name, "command": ["uv", "run", "true"]},
    }
    (root / f"{run_id}.json").write_text(json.dumps(payload), encoding="utf-8")


# ---------------------------------------------------------------------------
# ADR + OBPI brief fixture builders
# ---------------------------------------------------------------------------

_ADR_TEMPLATE = """\
---
id: {adr_id}
kind: {kind}
lane: {lane}
status: Draft
---

# {adr_id}: BDD fixture ADR

## Intent

Fixture ADR for REQ-coverage gate BDD scenarios (ADR-0.0.25).

## Checklist

- [ ] {obpi_id}: Fixture brief
"""

_BRIEF_TEMPLATE = """\
---
id: {obpi_id}
parent: {adr_id}
item: 1
lane: {lane}
status: {status}
---

# {obpi_id}: BDD fixture brief

## Objective

Fixture brief for the REQ-coverage gate BDD coverage.

## Allowed Paths

- `src/fixture.py`

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: gate fires before TTY confirmation.

## Acceptance Criteria

{criteria}

## Evidence

### Implementation Summary

- Files created/modified: src/fixture.py
- Tests added: tests/test_fixture.py
- Date completed: 2026-05-03
- Attestation status: Pending
- Defects noted: none

### Key Proof

uv run -m unittest tests.test_fixture -v passes 1/1.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** {status}

**Date Completed:** -

**Evidence Hash:** -
"""


def _seed_brief(
    adr_id: str,
    obpi_id: str,
    *,
    kind: str,
    lane: str,
    req_ids: list[str],
    status: str = "Draft",
    adrs_root: Path | None = None,
) -> None:
    if adrs_root is None:
        config = GzkitConfig.load(Path(".gzkit.json"))
        adrs_root = Path(config.paths.adrs)
    adr_dir = adrs_root / adr_id
    adr_dir.mkdir(parents=True, exist_ok=True)
    (adr_dir / f"{adr_id}.md").write_text(
        _ADR_TEMPLATE.format(adr_id=adr_id, obpi_id=obpi_id, kind=kind, lane=lane),
        encoding="utf-8",
    )
    obpis_dir = adr_dir / "obpis"
    obpis_dir.mkdir(parents=True, exist_ok=True)
    criteria = "\n".join(f"- [ ] {r}: fixture REQ" for r in req_ids)
    (obpis_dir / f"{obpi_id}.md").write_text(
        _BRIEF_TEMPLATE.format(
            obpi_id=obpi_id,
            adr_id=adr_id,
            lane=lane.capitalize(),
            criteria=criteria,
            status=status,
        ),
        encoding="utf-8",
    )
    ledger = Ledger(Path(".gzkit") / "ledger.jsonl")
    ledger.append(adr_created_event(adr_id, "", lane))
    ledger.append(obpi_created_event(obpi_id, adr_id))


def _seed_pipeline_marker(obpi_id: str) -> None:
    """Write a GHI #412-authentic marker + matching ledger event for the seeded brief.

    The parent ADR mirrors the convention used by ``_seed_brief`` callers
    (``ADR-FIXTURE-<obpi_id[-5:]>``); the nonce is fresh per call so the
    marker passes :func:`_validate_active_pipeline_marker`.
    """
    from datetime import UTC, datetime

    marker_dir = Path(".claude") / "plans"
    marker_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    parent_adr = f"ADR-FIXTURE-{obpi_id[-5:]}"
    nonce = "fedcba9876543210fedcba9876543210"
    marker_path = marker_dir / f".pipeline-active-{obpi_id}.json"
    payload = {
        "obpi_id": obpi_id,
        "parent_adr": parent_adr,
        "lane": "heavy",
        "entry": "full",
        "execution_mode": "normal",
        "current_stage": "ceremony",
        "started_at": timestamp,
        "updated_at": timestamp,
        "receipt_state": "pass",
        "nonce": nonce,
        "blockers": [],
    }
    marker_path.write_text(json.dumps(payload), encoding="utf-8")
    ledger_path = Path(".gzkit") / "ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "schema": "gzkit.ledger.v1",
        "event": "pipeline_launched",
        "id": obpi_id,
        "ts": timestamp,
        "parent": parent_adr,
        "nonce": nonce,
        "marker_path": marker_path.as_posix(),
        "lane": "heavy",
        "entry": "full",
    }
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")


# ---------------------------------------------------------------------------
# Fixture test file builders
# ---------------------------------------------------------------------------

_PASSING_TEST_TEMPLATE = """\
import unittest

def covers(req_id: str):
    def decorator(fn):
        return fn
    return decorator

class TestCovFixture(unittest.TestCase):
    @covers("{req_id}")
    def test_passes(self):
        pass
"""

_FAILING_TEST_TEMPLATE = """\
import unittest

def covers(req_id: str):
    def decorator(fn):
        return fn
    return decorator

class TestCovFixtureFail(unittest.TestCase):
    @covers("{req_id}")
    def test_fails(self):
        self.fail("deliberate failure for coverage gate BDD test")
"""

_SECOND_FAILING_TEST_TEMPLATE = """\
import unittest

def covers(req_id: str):
    def decorator(fn):
        return fn
    return decorator

class TestCovFixtureSecondFail(unittest.TestCase):
    @covers("{req_id}")
    def test_second_fails(self):
        self.fail("second deliberate failure for coverage gate BDD test")
"""


def _test_filename(req_id: str, suffix: str = "") -> str:
    safe = req_id.replace(".", "_").replace("-", "_")
    return f"test_cov_{safe}{suffix}.py"


def _ensure_tests_dir() -> Path:
    tests_dir = Path.cwd() / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    return tests_dir


# ---------------------------------------------------------------------------
# Shared completion helpers
# ---------------------------------------------------------------------------

_IMPL_SUMMARY = (
    "- Files created/modified: src/fixture.py\n"
    "- Tests added: tests/test_fixture.py\n"
    "- Date completed: 2026-05-03\n"
    "- Attestation status: Pending\n"
    "- Defects noted: none"
)
_KEY_PROOF = "uv run -m unittest tests.test_fixture -v passes 1/1."


def _complete_args(
    obpi_id: str,
    run_id: str,
    *,
    attestor_present: bool,
    accept_uncovered: list[str] | None = None,
    accept_uncovered_reason: list[str] | None = None,
) -> list[str]:
    args = [
        "obpi",
        "complete",
        obpi_id,
        "--attestor",
        "BDD User",
        "--attestation-text",
        f"attest completed (unittest: receipt {run_id})",
        "--implementation-summary",
        _IMPL_SUMMARY,
        "--key-proof",
        _KEY_PROOF,
    ]
    if attestor_present:
        args.append("--attestor-present")
    if accept_uncovered:
        for req in accept_uncovered:
            args += ["--accept-uncovered", req]
    if accept_uncovered_reason:
        for reason in accept_uncovered_reason:
            args += ["--accept-uncovered-reason", reason]
    return args


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given('a heavy-foundation OBPI "{obpi_id}" with REQ "{req_id}" exists')
def step_seed_heavy_foundation_single_req(context, obpi_id: str, req_id: str) -> None:  # type: ignore[no-untyped-def]
    adr_id = f"ADR-FIXTURE-{obpi_id[-5:]}"
    _seed_brief(adr_id, obpi_id, kind="foundation", lane="heavy", req_ids=[req_id])
    context._last_obpi_req = req_id


@given('a heavy-foundation OBPI "{obpi_id}" with REQs "{req_a}" and "{req_b}" exists')
def step_seed_heavy_foundation_two_reqs(context, obpi_id: str, req_a: str, req_b: str) -> None:  # type: ignore[no-untyped-def]
    adr_id = f"ADR-FIXTURE-{obpi_id[-5:]}"
    _seed_brief(adr_id, obpi_id, kind="foundation", lane="heavy", req_ids=[req_a, req_b])


@given('a foundation-lite OBPI "{obpi_id}" with REQ "{req_id}" exists')
def step_seed_foundation_lite_single_req(context, obpi_id: str, req_id: str) -> None:  # type: ignore[no-untyped-def]
    adr_id = f"ADR-FIXTURE-{obpi_id[-5:]}"
    _seed_brief(adr_id, obpi_id, kind="foundation", lane="lite", req_ids=[req_id])


@given('a lite-feature OBPI "{obpi_id}" with REQ "{req_id}" exists')
def step_seed_lite_feature_single_req(context, obpi_id: str, req_id: str) -> None:  # type: ignore[no-untyped-def]
    adr_id = f"ADR-FIXTURE-{obpi_id[-5:]}"
    _seed_brief(adr_id, obpi_id, kind="feature", lane="lite", req_ids=[req_id])


@given('a heavy-feature OBPI "{obpi_id}" with REQ "{req_id}" exists')
def step_seed_heavy_feature_single_req(context, obpi_id: str, req_id: str) -> None:  # type: ignore[no-untyped-def]
    """Heavy-feature brief: lane=heavy still triggers fail-closed REQ-coverage,
    but parent_kind=feature lets ``--attestor-present`` pass the GHI #412
    narrowing (foundation/security must use TTY)."""
    adr_id = f"ADR-FIXTURE-{obpi_id[-5:]}"
    _seed_brief(adr_id, obpi_id, kind="feature", lane="heavy", req_ids=[req_id])


@given('a covering test for "{req_id}" that passes exists')
def step_seed_passing_test(context, req_id: str) -> None:  # type: ignore[no-untyped-def]
    tests_dir = _ensure_tests_dir()
    fname = _test_filename(req_id)
    (tests_dir / fname).write_text(_PASSING_TEST_TEMPLATE.format(req_id=req_id), encoding="utf-8")


@given('a covering test for "{req_id}" that fails exists')
def step_seed_failing_test(context, req_id: str) -> None:  # type: ignore[no-untyped-def]
    tests_dir = _ensure_tests_dir()
    fname = _test_filename(req_id)
    (tests_dir / fname).write_text(_FAILING_TEST_TEMPLATE.format(req_id=req_id), encoding="utf-8")


@given('a second covering test for "{req_id}" that fails exists')
def step_seed_second_failing_test(context, req_id: str) -> None:  # type: ignore[no-untyped-def]
    tests_dir = _ensure_tests_dir()
    fname = _test_filename(req_id, suffix="_second")
    (tests_dir / fname).write_text(
        _SECOND_FAILING_TEST_TEMPLATE.format(req_id=req_id), encoding="utf-8"
    )


@given('a valid arb step receipt "{run_id}" exists')
def step_valid_arb_receipt(context, run_id: str) -> None:  # type: ignore[no-untyped-def]
    root = _receipts_root(context)
    _write_step_receipt(root, run_id, exit_status=0)


@given(
    'a heavy ADR "{adr_id}" with a completed OBPI "{obpi_id}" carrying unwaived REQ "{req_id}" exists'  # noqa: E501
)
def step_seed_completed_obpi_with_gap(context, adr_id: str, obpi_id: str, req_id: str) -> None:  # type: ignore[no-untyped-def]
    # resolve_adr_file uses config.paths.adrs (design/adr in _quick_init).
    # _check_adr_obpi_coverage_gaps hardcodes docs/design/adr/** in the search.
    # Write once for ledger and config-based path; mirror brief for closeout check.
    _seed_brief(adr_id, obpi_id, kind="foundation", lane="heavy", req_ids=[req_id])
    # Mirror the brief to docs/design/adr/ so _check_adr_obpi_coverage_gaps finds it.
    criteria = f"- [ ] {req_id}: fixture REQ"
    docs_obpis_dir = Path("docs") / "design" / "adr" / adr_id / "obpis"
    docs_obpis_dir.mkdir(parents=True, exist_ok=True)
    (docs_obpis_dir / f"{obpi_id}.md").write_text(
        _BRIEF_TEMPLATE.format(
            obpi_id=obpi_id, adr_id=adr_id, lane="Heavy", criteria=criteria, status="Draft"
        ),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when('I complete coverage-gate OBPI "{obpi_id}" citing receipt "{run_id}" using attestor-present')
def step_complete_with_attestor_present(context, obpi_id: str, run_id: str) -> None:  # type: ignore[no-untyped-def]
    args = _complete_args(obpi_id, run_id, attestor_present=True)
    context.exit_code, context.output = _invoke(args)


@when(
    'I complete coverage-gate OBPI "{obpi_id}" accepting "{req_id}" reason "{reason}" citing "{run_id}" using attestor-present'  # noqa: E501
)
def step_complete_accept_uncovered_with_marker(  # type: ignore[no-untyped-def]
    context, obpi_id: str, req_id: str, reason: str, run_id: str
) -> None:
    args = _complete_args(
        obpi_id,
        run_id,
        attestor_present=True,
        accept_uncovered=[req_id],
        accept_uncovered_reason=[reason],
    )
    context.exit_code, context.output = _invoke(args)


@when(
    'I complete coverage-gate OBPI "{obpi_id}" accepting "{req_id}" reason "{reason}" citing "{run_id}" without attestor-present'  # noqa: E501
)
def step_complete_accept_uncovered_headless(  # type: ignore[no-untyped-def]
    context, obpi_id: str, req_id: str, reason: str, run_id: str
) -> None:
    args = _complete_args(
        obpi_id,
        run_id,
        attestor_present=False,
        accept_uncovered=[req_id],
        accept_uncovered_reason=[reason],
    )
    context.exit_code, context.output = _invoke(args)


@when(
    'I complete coverage-gate OBPI "{obpi_id}" accepting only "{req_id}" reason "{reason}" citing "{run_id}" using attestor-present'  # noqa: E501
)
def step_complete_partial_accept(  # type: ignore[no-untyped-def]
    context, obpi_id: str, req_id: str, reason: str, run_id: str
) -> None:
    args = _complete_args(
        obpi_id,
        run_id,
        attestor_present=True,
        accept_uncovered=[req_id],
        accept_uncovered_reason=[reason],
    )
    context.exit_code, context.output = _invoke(args)


@when(
    'I complete coverage-gate OBPI "{obpi_id}" accepting "{req_id}" without reason citing "{run_id}" using attestor-present'  # noqa: E501
)
def step_complete_accept_no_reason(  # type: ignore[no-untyped-def]
    context, obpi_id: str, req_id: str, run_id: str
) -> None:
    args = [
        "obpi",
        "complete",
        obpi_id,
        "--attestor",
        "BDD User",
        "--attestation-text",
        f"attest completed (unittest: receipt {run_id})",
        "--implementation-summary",
        _IMPL_SUMMARY,
        "--key-proof",
        _KEY_PROOF,
        "--accept-uncovered",
        req_id,
        "--attestor-present",
    ]
    context.exit_code, context.output = _invoke(args)


@when('I emit ADR receipt for "{adr_id}" event "{event}" attestor "{attestor}" text "{text}"')
def step_emit_adr_receipt(  # type: ignore[no-untyped-def]
    context, adr_id: str, event: str, attestor: str, text: str
) -> None:
    args = [
        "adr",
        "emit-receipt",
        adr_id,
        "--event",
        event,
        "--attestor",
        attestor,
    ]
    context.exit_code, context.output = _invoke(args)


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------


@then("the exit code is {code:d}")
def step_exit_code(context, code: int) -> None:  # type: ignore[no-untyped-def]
    actual = getattr(context, "exit_code", None)
    assert actual == code, (
        f"Expected exit code {code}, got {actual}.\nOutput:\n{getattr(context, 'output', '')}"
    )


@then('the output mentions "{text}"')
def step_output_mentions(context, text: str) -> None:  # type: ignore[no-untyped-def]
    output = getattr(context, "output", "")
    assert text in output, f"Expected {text!r} in output.\nOutput:\n{output}"


@then('the ledger contains an "{event_name}" event')
def step_ledger_event(context, event_name: str) -> None:  # type: ignore[no-untyped-def]
    ledger_path = Path(".gzkit") / "ledger.jsonl"
    assert ledger_path.is_file(), "Ledger file not found"
    events = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    names = [e.get("event") for e in events]
    assert event_name in names, f"Expected event {event_name!r} in ledger.\nEvents: {names}"


@then('AGENTS.md "{section}" section mentions "{text}"')
def step_agents_md_section_mentions(context, section: str, text: str) -> None:  # type: ignore[no-untyped-def]
    agents_path = Path("AGENTS.md")
    assert agents_path.is_file(), "AGENTS.md not found"
    content = agents_path.read_text(encoding="utf-8")
    # Find the section heading
    section_marker = f"## {section}"
    idx = content.find(section_marker)
    assert idx >= 0, f"Section {section!r} not found in AGENTS.md"
    # Read content until next H2
    section_body = content[idx:]
    next_h2 = section_body.find("\n## ", 1)
    if next_h2 >= 0:
        section_body = section_body[:next_h2]
    assert text in section_body, (
        f"Expected {text!r} in AGENTS.md section {section!r}.\n"
        f"Section content:\n{section_body[:500]}"
    )
