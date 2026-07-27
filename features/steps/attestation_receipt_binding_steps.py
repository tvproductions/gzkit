"""BDD steps for the ADR-0.0.24 attestation receipt-binding gate.

Covers REQ-0.0.24-01-01..06 (validator scope), REQ-0.0.24-02-01..05 (gate
wiring into ``gz obpi complete`` / ``gz adr emit-receipt``), and
REQ-0.0.24-04-01..03 (this OBPI's own self-coverage of the gate itself).

Scenarios run end-to-end against the registered CLI surfaces (no
subprocess mocking) — fixtures are staged on disk in the per-scenario
tempdir, ARB receipts are routed through the ``GZKIT_ARB_RECEIPTS_ROOT``
env override, and the OBPI brief / parent ADR are written to the
configured ``adrs`` root so ``resolve_adr_file`` / ``resolve_obpi_file``
discover them via the canonical scan.

@covers REQ-0.0.24-01-01
@covers REQ-0.0.24-01-02
@covers REQ-0.0.24-01-03
@covers REQ-0.0.24-01-04
@covers REQ-0.0.24-01-05
@covers REQ-0.0.24-01-06
@covers REQ-0.0.24-02-01
@covers REQ-0.0.24-02-02
@covers REQ-0.0.24-02-03
@covers REQ-0.0.24-02-04
@covers REQ-0.0.24-02-05
@covers REQ-0.0.24-04-01
@covers REQ-0.0.24-04-02
@covers REQ-0.0.24-04-03
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
# Receipt fixture builders
# ---------------------------------------------------------------------------


def _receipts_root(context) -> Path:  # type: ignore[no-untyped-def]
    """Return (creating if needed) the per-scenario ARB receipts root.

    Sets ``GZKIT_ARB_RECEIPTS_ROOT`` so ``gzkit.arb.paths.receipts_root``
    resolves to the tempdir-scoped fixture directory rather than the live
    ``artifacts/receipts/`` tree. Cleanup happens in ``after_scenario`` via
    the ``_orig_arb_receipts_root`` attribute.
    """
    if not hasattr(context, "_orig_arb_receipts_root"):
        context._orig_arb_receipts_root = os.environ.get("GZKIT_ARB_RECEIPTS_ROOT")
    root = Path.cwd() / "artifacts" / "receipts"
    root.mkdir(parents=True, exist_ok=True)
    os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = str(root)
    return root


def _write_step_receipt(root: Path, run_id: str, *, exit_status: int) -> None:
    """Write a fixture step-receipt JSON matching ``gzkit.arb.step_receipt.v1``."""
    name = run_id[len("arb-step-") :].rsplit("-", 1)[0]
    payload = {
        "schema": "gzkit.arb.step_receipt.v1",
        "run_id": run_id,
        "timestamp_utc": "2026-05-02T12:00:00Z",
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


def _write_lint_receipt(root: Path, run_id: str, *, exit_status: int) -> None:
    """Write a fixture lint-receipt JSON matching ``gzkit.arb.lint_receipt.v1``."""
    payload = {
        "schema": "gzkit.arb.lint_receipt.v1",
        "run_id": run_id,
        "timestamp_utc": "2026-05-02T12:00:00Z",
        "exit_status": exit_status,
        "findings": [],
        "findings_total": 0,
        "findings_truncated": False,
        "tool": {"name": "ruff", "version": "ruff 0.15.11"},
        "git": {"commit": "abcdef0", "branch": "main", "dirty": False},
    }
    (root / f"{run_id}.json").write_text(json.dumps(payload), encoding="utf-8")


# ---------------------------------------------------------------------------
# In-process CLI driver (mirrors gz_steps.py:_invoke for env isolation)
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
# Brief and ADR fixture builders
# ---------------------------------------------------------------------------

_ADR_TEMPLATE = """\
---
id: {adr_id}
kind: {kind}
lane: {lane}
status: Draft
---

# {adr_id}: BDD fixture ADR

## Status

Draft

## Intent

Fixture ADR for the receipt-binding gate BDD coverage. Not promoted; not
canon. Lives only inside the per-scenario tempdir so the OBPI complete
flow has a parent to resolve.

## Checklist

- [ ] {obpi_id}: Fixture brief
"""


_BRIEF_TEMPLATE = """\
---
id: {obpi_id}
parent: {adr_id}
item: 1
lane: {lane}
status: Draft
---

# {obpi_id}: BDD fixture brief

## Objective

Fixture brief for the receipt-binding gate BDD coverage.

## Allowed Paths

- `src/fixture.py`

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: gate fires before TTY confirmation.

## Acceptance Criteria

- [ ] {req_id} [SUPPORT]: gate fires.

## Evidence

### Implementation Summary

- Files created/modified: src/fixture.py
- Tests added: tests/test_fixture.py
- Date completed: 2026-05-02
- Attestation status: Pending
- Defects noted: none

### Key Proof

uv run gz validate --attestation-receipts ... resolves the cited receipt.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
"""


def _fixture_req_id(obpi_id: str) -> str:
    """Derive the fixture brief's REQ id from the OBPI it belongs to.

    ``triangle._AC_LINE_PATTERN`` only matches a four-tier numeric id, so the
    previous hard-coded ``REQ-FIXTURE-01-01`` could never parse: every seeded
    brief yielded zero REQs and a ``Malformed REQ line`` warning that escaped
    into committed ADR audit proofs (GHI #726). Deriving the id keeps it correct
    across a rename of the fixture OBPI rather than re-rotting on the next one.
    """
    _, semver, item, *_ = obpi_id.split("-")
    return f"REQ-{semver}-{item}-01"


def _seed_adr_and_brief(adr_id: str, obpi_id: str, *, kind: str, lane: str) -> None:
    """Seed an ADR + OBPI brief on disk and register both in the ledger."""
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
    (obpis_dir / f"{obpi_id}.md").write_text(
        _BRIEF_TEMPLATE.format(
            obpi_id=obpi_id,
            adr_id=adr_id,
            lane=lane.capitalize(),
            req_id=_fixture_req_id(obpi_id),
        ),
        encoding="utf-8",
    )
    ledger = Ledger(Path(".gzkit") / "ledger.jsonl")
    ledger.append(adr_created_event(adr_id, "", lane))
    ledger.append(obpi_created_event(obpi_id, adr_id))
    _seed_reconcile_receipt(obpi_id, obpis_dir / f"{obpi_id}.md")


# 2020-01-01T00:00:00Z: a fixed past mtime so the seeded reconcile receipt
# (stamped "now") is strictly newer than the allowlist domain (mode-2 freshness).
_RECONCILED_ALLOWLIST_MTIME = 1577836800.0


def _seed_reconcile_receipt(obpi_id: str, brief_path: Path) -> None:
    """Seed a fresh, drift-free ``brief_reconciled`` receipt for the fixture.

    OBPI-0.0.37-08 added a Stage-5 reconcile-receipt fail-close gate to
    ``gz obpi complete`` that fires *before* the receipt-binding behaviour these
    scenarios exercise. A ready-to-complete fixture brief is therefore one that
    has been reconciled: its allowed-path files exist on disk (backdated so the
    receipt is strictly newer) and a clean, no-drift receipt sits on the ledger.
    The gate's own fail-closed behaviour is covered by
    ``tests/commands/test_obpi_complete_reconcile_gate.py``, not here.
    """
    from gzkit.ledger_events import brief_reconciled_event  # noqa: PLC0415
    from gzkit.pipeline_runtime import _extract_brief_allowlist  # noqa: PLC0415

    for rel in _extract_brief_allowlist(brief_path):
        if any(ch in rel for ch in "*?["):  # glob pattern — leave unmaterialised
            continue
        target = Path.cwd() / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text("", encoding="utf-8")
        os.utime(target, (_RECONCILED_ALLOWLIST_MTIME, _RECONCILED_ALLOWLIST_MTIME))
    Ledger(Path(".gzkit") / "ledger.jsonl").append(
        brief_reconciled_event(
            obpi_id,
            has_drift=False,
            allowlist_delta_count=0,
            discovery_delta_count=0,
            verification_delta_count=0,
            req_count_delta=0,
            citation_delta_count=0,
        )
    )


def _seed_adr_only(adr_id: str, *, kind: str, lane: str) -> None:
    """Seed an ADR only (used by REQ-02-05 for the emit-receipt path)."""
    config = GzkitConfig.load(Path(".gzkit.json"))
    adrs_root = Path(config.paths.adrs)
    adr_dir = adrs_root / adr_id
    adr_dir.mkdir(parents=True, exist_ok=True)
    (adr_dir / f"{adr_id}.md").write_text(
        _ADR_TEMPLATE.format(adr_id=adr_id, obpi_id="OBPI-FIXTURE", kind=kind, lane=lane),
        encoding="utf-8",
    )
    ledger = Ledger(Path(".gzkit") / "ledger.jsonl")
    ledger.append(adr_created_event(adr_id, "", lane))


# ---------------------------------------------------------------------------
# Pipeline marker (satisfies --attestor-present co-presence proxy, GHI #292)
# ---------------------------------------------------------------------------


def _seed_pipeline_marker(obpi_id: str, parent_adr: str | None = None) -> None:
    """Write a structurally-authentic pipeline marker + matching ledger event.

    The marker satisfies GHI #292 (proxy for operator co-presence) AND
    GHI #412 (structure, freshness, parent_adr, 32-hex nonce, and a
    ``pipeline_launched`` ledger event with the same nonce). When
    ``parent_adr`` is omitted, the brief frontmatter is read from the
    seeded ADR scaffolding to discover the parent — the validator
    cross-checks this field.
    """
    from datetime import UTC, datetime

    marker_dir = Path(".claude") / "plans"
    marker_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if parent_adr is None:
        config = GzkitConfig.load(Path(".gzkit.json"))
        adrs_root = Path(config.paths.adrs)
        parent_adr = ""
        for brief_path in adrs_root.rglob(f"{obpi_id}.md"):
            content = brief_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("parent:"):
                    parent_adr = stripped.split(":", 1)[1].strip()
                    break
            if parent_adr:
                break
    nonce = "abcdef0123456789abcdef0123456789"
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
    ledger_dir = Path(".gzkit")
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = ledger_dir / "ledger.jsonl"
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
# Steps
# ---------------------------------------------------------------------------


@given('an arb step receipt "{run_id}" with exit_status {status:d} exists')
def step_arb_step_receipt(context, run_id: str, status: int) -> None:  # type: ignore[no-untyped-def]
    root = _receipts_root(context)
    if run_id.startswith("arb-step-"):
        _write_step_receipt(root, run_id, exit_status=status)
    elif run_id.startswith("arb-ruff-"):
        _write_lint_receipt(root, run_id, exit_status=status)
    else:
        msg = f"Unknown receipt prefix: {run_id}"
        raise AssertionError(msg)


@given("no arb receipts exist in the receipts root")
def step_no_arb_receipts(context) -> None:  # type: ignore[no-untyped-def]
    root = _receipts_root(context)
    for entry in root.iterdir():
        if entry.is_file():
            entry.unlink()


@given('a heavy-lane brief "{obpi_id}" under feature ADR "{adr_id}" exists on disk')
def step_seed_heavy_feature(context, obpi_id: str, adr_id: str) -> None:  # type: ignore[no-untyped-def]
    _seed_adr_and_brief(adr_id, obpi_id, kind="feature", lane="heavy")


@given('a lite-feature brief "{obpi_id}" under feature ADR "{adr_id}" exists on disk')
def step_seed_lite_feature(context, obpi_id: str, adr_id: str) -> None:  # type: ignore[no-untyped-def]
    _seed_adr_and_brief(adr_id, obpi_id, kind="feature", lane="lite")


@given('a lite-foundation brief "{obpi_id}" under foundation ADR "{adr_id}" exists on disk')
def step_seed_lite_foundation(context, obpi_id: str, adr_id: str) -> None:  # type: ignore[no-untyped-def]
    _seed_adr_and_brief(adr_id, obpi_id, kind="foundation", lane="lite")


@given('a heavy feature ADR "{adr_id}" exists on disk')
def step_seed_heavy_adr_only(context, adr_id: str) -> None:  # type: ignore[no-untyped-def]
    _seed_adr_only(adr_id, kind="feature", lane="heavy")


@given('a pipeline marker for "{obpi_id}" is active')
def step_seed_marker(context, obpi_id: str) -> None:  # type: ignore[no-untyped-def]
    _seed_pipeline_marker(obpi_id)


@given("the workspace is the live repository")
def step_use_live_repo(context) -> None:  # type: ignore[no-untyped-def]
    """Restore cwd to the original repository root for live-surface scenarios.

    The behave environment chdirs into a per-scenario tempdir; the
    ``--behave-req-tags`` validator scans the live ``features/`` and
    ``data/behave_coverage_waivers.json`` so the scenario must run
    against the real repo. ``after_scenario`` will rmtree the tempdir
    as usual.
    """
    os.chdir(context._original_cwd)


_FIXTURE_IMPL_SUMMARY = (
    "- Files created/modified: src/fixture.py\n"
    "- Tests added: tests/test_fixture.py\n"
    "- Date completed: 2026-05-02\n"
    "- Attestation status: Pending\n"
    "- Defects noted: none"
)
_FIXTURE_KEY_PROOF = "uv run -m unittest tests/test_fixture.py -v passes 1/1."

# Heavy-lane completion fails closed without a Step-4b adversary verdict (GHI #676).
# These scenarios are about receipt binding, not Step 4b, so they satisfy the gate
# rather than exercise it — its own behaviour is covered in tests/.
_ADVERSARY_ARGS = ["--adversary-verdict", "not-refuted", "--adversary", "codex/gpt-5.4"]


@when('I complete OBPI "{obpi_id}" with attestation citing "{run_id}" using attestor-present')
def step_complete_with_attestor_present(context, obpi_id: str, run_id: str) -> None:  # type: ignore[no-untyped-def]
    args = [
        "obpi",
        "complete",
        obpi_id,
        "--attestor",
        "BDD User",
        "--attestation-text",
        f"attest completed (unittest: receipt {run_id})",
        "--implementation-summary",
        _FIXTURE_IMPL_SUMMARY,
        "--key-proof",
        _FIXTURE_KEY_PROOF,
        "--attestor-present",
        *_ADVERSARY_ARGS,
    ]
    context.exit_code, context.output = _invoke(args)


@when('I complete OBPI "{obpi_id}" with attestation citing "{run_id}" without attestor-present')
def step_complete_without_attestor_present(context, obpi_id: str, run_id: str) -> None:  # type: ignore[no-untyped-def]
    args = [
        "obpi",
        "complete",
        obpi_id,
        "--attestor",
        "BDD User",
        "--attestation-text",
        f"attest completed (lint: receipt {run_id})",
        "--implementation-summary",
        _FIXTURE_IMPL_SUMMARY,
        "--key-proof",
        _FIXTURE_KEY_PROOF,
        *_ADVERSARY_ARGS,
    ]
    context.exit_code, context.output = _invoke(args)


@when(
    'I emit ADR receipt for "{adr_id}" event "{event}" '
    'attestor "{attestor}" attestation citing "{run_id}"'
)
def step_emit_adr_receipt(  # type: ignore[no-untyped-def]
    context, adr_id: str, event: str, attestor: str, run_id: str
) -> None:
    args = [
        "adr",
        "emit-receipt",
        adr_id,
        "--event",
        event,
        "--attestor",
        attestor,
        "--attestation-text",
        f"attest validated (lint: receipt {run_id})",
        "--evidence-json",
        json.dumps({"scope": adr_id, "date": "2026-05-02"}),
    ]
    context.exit_code, context.output = _invoke(args)


@then(
    'the ledger contains an event with field "event" equal to "{event_name}" '
    'whose extra.receipt_event is "{receipt_event}"'
)
def step_ledger_has_meta_event(  # type: ignore[no-untyped-def]
    context, event_name: str, receipt_event: str
) -> None:
    ledger_path = Path(".gzkit") / "ledger.jsonl"
    text = ledger_path.read_text(encoding="utf-8") if ledger_path.is_file() else ""
    matches = []
    for line in text.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("event") != event_name:
            continue
        if record.get("receipt_event") == receipt_event:
            matches.append(record)
    assert matches, (
        f"No {event_name!r} event with receipt_event=={receipt_event!r}\nLedger:\n{text}"
    )


@then('the ledger contains an event with field "event" equal to "{event_name}"')
def step_ledger_has_event(context, event_name: str) -> None:  # type: ignore[no-untyped-def]
    ledger_path = Path(".gzkit") / "ledger.jsonl"
    text = ledger_path.read_text(encoding="utf-8") if ledger_path.is_file() else ""
    matches = [
        json.loads(line)
        for line in text.splitlines()
        if line.strip() and json.loads(line).get("event") == event_name
    ]
    assert matches, f"No {event_name!r} event in ledger:\n{text}"


@then('the ledger contains an event for "{obpi_id}" with receipt_event "{receipt_event}"')
def step_ledger_has_completion_event(  # type: ignore[no-untyped-def]
    context, obpi_id: str, receipt_event: str
) -> None:
    ledger_path = Path(".gzkit") / "ledger.jsonl"
    text = ledger_path.read_text(encoding="utf-8") if ledger_path.is_file() else ""
    matches = []
    for line in text.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("event") != "obpi_receipt_emitted":
            continue
        if record.get("id") != obpi_id:
            continue
        if record.get("receipt_event") == receipt_event:
            matches.append(record)
    assert matches, (
        f"No obpi_receipt_emitted event for {obpi_id!r} with "
        f"receipt_event=={receipt_event!r}\nLedger:\n{text}"
    )


@then('the ledger does not contain an event for "{obpi_id}" with receipt_event "{receipt_event}"')
def step_ledger_no_completion_event(  # type: ignore[no-untyped-def]
    context, obpi_id: str, receipt_event: str
) -> None:
    ledger_path = Path(".gzkit") / "ledger.jsonl"
    if not ledger_path.is_file():
        return
    text = ledger_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if (
            record.get("event") == "obpi_receipt_emitted"
            and record.get("id") == obpi_id
            and record.get("receipt_event") == receipt_event
        ):
            msg = (
                f"Unexpected obpi_receipt_emitted event for {obpi_id!r} with "
                f"receipt_event=={receipt_event!r}: {record}"
            )
            raise AssertionError(msg)
