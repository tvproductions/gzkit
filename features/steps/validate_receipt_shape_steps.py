"""BDD steps for gz validate --receipt-shape scenarios (OBPI-0.0.36-03).

@covers REQ-0.0.36-03-02
@covers REQ-0.0.36-03-03
@covers REQ-0.0.36-03-04
@covers REQ-0.0.36-03-05
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from behave import given

_CUTOFF_DATE = "2026-04-26"
_POST_CUTOFF_TS = "2026-04-27T12:00:00+00:00"
_PRE_CUTOFF_TS = "2026-04-25T12:00:00+00:00"

_ADR_REL = (
    "docs/design/adr/foundation"
    "/ADR-0.0.36-universal-obpi-attestation"
    "/ADR-0.0.36-universal-obpi-attestation.md"
)

_ADR_CONTENT = f"""\
---
id: ADR-0.0.36-universal-obpi-attestation
status: Accepted
kind: foundation
lane: heavy
date: {_CUTOFF_DATE}
---

# ADR-0.0.36 Universal OBPI Attestation

## Why foundation tier?

Without this ADR, attestation surface varies by lane/kind.
"""


def _write_minimal_project(root: Path, ledger_events: list[dict]) -> None:
    adr_path = root / _ADR_REL
    adr_path.parent.mkdir(parents=True, exist_ok=True)
    adr_path.write_text(_ADR_CONTENT, encoding="utf-8")

    gzkit_dir = root / ".gzkit"
    gzkit_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = gzkit_dir / "ledger.jsonl"
    ledger_path.write_text(
        "\n".join(json.dumps(e) for e in ledger_events) + "\n",
        encoding="utf-8",
    )

    manifest_path = gzkit_dir / "manifest.json"
    manifest_data = {
        "schema": "gzkit.manifest.v1",
        "id": "test",
        "name": "test",
        "version": "0.1.0",
        "prd": "PRD-TEST-1.0.0",
        "mode": "lite",
    }
    manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")


def _receipt_event(
    receipt_id: str,
    ts: str,
    attestor: str,
    attestation_requirement: str,
    obpi_completion: str,
) -> dict:
    return {
        "schema": "gzkit.ledger.v1",
        "event": "obpi_receipt_emitted",
        "id": receipt_id,
        "ts": ts,
        "attestor": attestor,
        "evidence": {
            "attestation_requirement": attestation_requirement,
            "obpi_completion": obpi_completion,
        },
    }


@given("a minimal project with a post-cutoff receipt having attestation_requirement optional")
def step_post_cutoff_optional(context) -> None:
    """Post-cutoff receipt with deprecated attestation_requirement: optional."""
    root: Path = context._tmpdir
    _write_minimal_project(
        root,
        [
            _receipt_event(
                receipt_id="OBPI-test-optional-01",
                ts=_POST_CUTOFF_TS,
                attestor="g0",
                attestation_requirement="optional",
                obpi_completion="attested_completed",
            )
        ],
    )
    os.chdir(root)


@given("a minimal project with a post-cutoff receipt having obpi_completion completed")
def step_post_cutoff_bare_completed(context) -> None:
    """Post-cutoff receipt with deprecated obpi_completion: completed (no prefix)."""
    root: Path = context._tmpdir
    _write_minimal_project(
        root,
        [
            _receipt_event(
                receipt_id="OBPI-test-bare-completed-01",
                ts=_POST_CUTOFF_TS,
                attestor="g0",
                attestation_requirement="required",
                obpi_completion="completed",
            )
        ],
    )
    os.chdir(root)


@given("a minimal project with a post-cutoff receipt having attestor agent:claude-code")
def step_post_cutoff_agent_attestor(context) -> None:
    """Post-cutoff receipt with deprecated attestor: agent:claude-code."""
    root: Path = context._tmpdir
    _write_minimal_project(
        root,
        [
            _receipt_event(
                receipt_id="OBPI-test-agent-01",
                ts=_POST_CUTOFF_TS,
                attestor="agent:claude-code",
                attestation_requirement="required",
                obpi_completion="attested_completed",
            )
        ],
    )
    os.chdir(root)


@given("a minimal project with a pre-cutoff receipt and a matching waiver entry")
def step_pre_cutoff_waivered(context) -> None:
    """Pre-cutoff receipt with all deprecated shapes, covered by a waiver entry."""
    root: Path = context._tmpdir
    receipt_id = "OBPI-legacy-pre-cutoff-01"
    _write_minimal_project(
        root,
        [
            _receipt_event(
                receipt_id=receipt_id,
                ts=_PRE_CUTOFF_TS,
                attestor="agent:legacy",
                attestation_requirement="optional",
                obpi_completion="completed",
            )
        ],
    )
    waiver_path = root / "data" / "historical_self_close_waivers.json"
    waiver_path.parent.mkdir(parents=True, exist_ok=True)
    waiver_path.write_text(
        json.dumps(
            {
                "waivers": [
                    {
                        "receipt_id": receipt_id,
                        "obpi_id": "OBPI-0.0.36-04",
                        "deprecated_shape": "attestation_requirement: optional",
                        "rationale": "Pre-cutoff self-close receipt.",
                        "added_under": "OBPI-0.0.36-04-historical-self-close-waivers",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    os.chdir(root)


@given("a minimal project with a pre-cutoff receipt and a waiver entry with bad added_under")
def step_pre_cutoff_with_bad_added_under_waiver(context) -> None:
    """Pre-cutoff receipt with waiver entry having invalid added_under value."""
    root: Path = context._tmpdir
    receipt_id = "OBPI-bad-added-under-01"
    _write_minimal_project(
        root,
        [
            _receipt_event(
                receipt_id=receipt_id,
                ts=_PRE_CUTOFF_TS,
                attestor="agent:legacy",
                attestation_requirement="optional",
                obpi_completion="completed",
            )
        ],
    )
    waiver_path = root / "data" / "historical_self_close_waivers.json"
    waiver_path.parent.mkdir(parents=True, exist_ok=True)
    waiver_path.write_text(
        json.dumps(
            {
                "waivers": [
                    {
                        "receipt_id": receipt_id,
                        "obpi_id": "OBPI-0.0.36-04",
                        "deprecated_shape": "attestation_requirement: optional",
                        "rationale": "Pre-cutoff self-close receipt.",
                        # Invalid: should be OBPI-0.0.36-04-historical-self-close-waivers
                        "added_under": "OBPI-0.0.36-03-wrong-obpi",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    os.chdir(root)


@given(
    "a minimal project with a pre-cutoff receipt and a "
    "matching waiver entry having valid added_under"
)
def step_pre_cutoff_with_valid_waiver(context) -> None:
    """Pre-cutoff receipt with waiver entry having valid added_under."""
    root: Path = context._tmpdir
    receipt_id = "OBPI-valid-waiver-01"
    _write_minimal_project(
        root,
        [
            _receipt_event(
                receipt_id=receipt_id,
                ts=_PRE_CUTOFF_TS,
                attestor="agent:legacy",
                attestation_requirement="optional",
                obpi_completion="completed",
            )
        ],
    )
    waiver_path = root / "data" / "historical_self_close_waivers.json"
    waiver_path.parent.mkdir(parents=True, exist_ok=True)
    waiver_path.write_text(
        json.dumps(
            {
                "waivers": [
                    {
                        "receipt_id": receipt_id,
                        "obpi_id": "OBPI-0.0.36-04",
                        "deprecated_shape": "attestation_requirement: optional",
                        "rationale": "Pre-cutoff self-close receipt.",
                        "added_under": "OBPI-0.0.36-04-historical-self-close-waivers",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    os.chdir(root)


@given("a minimal project with a pre-cutoff receipt and a waiver file lacking that receipt")
def step_pre_cutoff_with_waiver_file_missing_receipt(
    context,
) -> None:
    """Unwaivered pre-cutoff receipt (waiver file present but missing this receipt)."""
    root: Path = context._tmpdir
    receipt_id = "OBPI-unwaivered-pre-cutoff-01"
    _write_minimal_project(
        root,
        [
            _receipt_event(
                receipt_id=receipt_id,
                ts=_PRE_CUTOFF_TS,
                attestor="agent:legacy",
                attestation_requirement="optional",
                obpi_completion="completed",
            )
        ],
    )
    waiver_path = root / "data" / "historical_self_close_waivers.json"
    waiver_path.parent.mkdir(parents=True, exist_ok=True)
    # Waiver file exists but has a DIFFERENT receipt_id
    waiver_path.write_text(
        json.dumps(
            {
                "waivers": [
                    {
                        "receipt_id": "OBPI-some-other-receipt-01",
                        "obpi_id": "OBPI-0.0.36-04",
                        "deprecated_shape": "attestation_requirement: optional",
                        "rationale": "Some other pre-cutoff receipt.",
                        "added_under": "OBPI-0.0.36-04-historical-self-close-waivers",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    os.chdir(root)
