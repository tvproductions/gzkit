"""BDD steps for the complexity-thresholds rule body validator.

Covers ``features/complexity_thresholds.feature`` (OBPI-0.0.28-03).

GHI #426 — fixture data writes JSON; the bootstrap-section fixture also
writes the narrative .md so the validator can detect it.

@covers REQ-0.0.28-03-02
@covers REQ-0.0.28-03-03
@covers REQ-0.0.28-03-04
@covers REQ-0.0.28-03-05
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from behave import given, then

_DATA_REL_PATH = Path(".gzkit") / "rules" / "complexity-thresholds.json"
_NARRATIVE_REL_PATH = Path(".gzkit") / "rules" / "complexity-thresholds.md"
_REPO_ROOT = Path(__file__).resolve().parents[2]

_BOOTSTRAP_NARRATIVE = (
    "<!-- rule-version: 0.3.0 -->\n\n"
    "# Complexity Thresholds — narrative fixture\n\n"
    "## Bootstrap absolutes (REQ-11 carve-out -- one-shot)\n\n"
    "- `radon_mi` — bootstrap (GHI #405)\n"
    "- `lizard_nesting_depth` — bootstrap (GHI #404)\n"
    "- `cohesion_lcom4` — bootstrap (GHI #404)\n"
)


def _well_formed_payload() -> dict[str, Any]:
    """Synthetic well-formed data payload covering all 12 canonical metrics."""
    metrics_with_bands = [
        ("radon_cc", 4.0, 7.0, 11.0, 95),
        ("radon_mi", 85.0, 70.0, 50.0, 95),
        ("radon_hal_volume", 946.89, 2740.93, 5549.80, 95),
        ("radon_hal_difficulty", 8.13, 11.54, 12.46, 95),
        ("radon_hal_effort", 7975.79, 30805.01, 74805.40, 95),
        ("radon_raw_nloc", 311.75, 733.20, 1031.90, 95),
        ("radon_raw_lloc", 238.25, 518.00, 811.70, 95),
        ("lizard_nloc", 13.0, 25.0, 37.0, 95),
        ("lizard_param_count", 3.0, 4.0, 5.0, 95),
        ("lizard_nesting_depth", 2.0, 3.0, 4.0, 99),
        ("lizard_ccn", 4.0, 8.0, 11.0, 95),
        ("cohesion_lcom4", 2.0, 4.0, 8.0, 99),
    ]
    bands: list[dict[str, Any]] = []
    for metric, advise, warn, block, block_pct in metrics_with_bands:
        bands.extend(
            [
                {
                    "metric": metric,
                    "corpus_percentile": 75,
                    "absolute_number": advise,
                    "trigger_semantic": "advise",
                },
                {
                    "metric": metric,
                    "corpus_percentile": 90,
                    "absolute_number": warn,
                    "trigger_semantic": "warn",
                },
                {
                    "metric": metric,
                    "corpus_percentile": block_pct,
                    "absolute_number": block,
                    "trigger_semantic": "block",
                },
            ]
        )
    return {
        "corpus_revision": 1,
        "citation": {
            "distilled_characteristics_path": (
                "docs/governance/complexity/distilled-characteristics-2026-05-04.md"
            ),
            "section_anchor": "radon-cc",
            "corpus_revision": 1,
        },
        "bands": bands,
    }


def _write_data(workspace: Path, payload: dict[str, Any]) -> None:
    data_path = workspace / _DATA_REL_PATH
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(payload), encoding="utf-8")


def _write_narrative(workspace: Path, body: str) -> None:
    narrative_path = workspace / _NARRATIVE_REL_PATH
    narrative_path.parent.mkdir(parents=True, exist_ok=True)
    narrative_path.write_text(body, encoding="utf-8")


def _workspace(_context) -> Path:
    return Path.cwd()


@given("a complexity-thresholds fixture with radon_cc missing its block band")
def step_fixture_missing_block_band(context):
    payload = _well_formed_payload()
    payload["bands"] = [
        band
        for band in payload["bands"]
        if not (band["metric"] == "radon_cc" and band["trigger_semantic"] == "block")
    ]
    _write_data(_workspace(context), payload)


@given("a complexity-thresholds fixture with radon_cc carrying an off-enum percentile")
def step_fixture_off_enum_percentile(context):
    payload = _well_formed_payload()
    for band in payload["bands"]:
        if band["metric"] == "radon_cc" and band["trigger_semantic"] == "advise":
            band["corpus_percentile"] = 80
            break
    _write_data(_workspace(context), payload)


@given("a complexity-thresholds fixture with a malformed citation block")
def step_fixture_malformed_citation(context):
    payload = _well_formed_payload()
    payload["citation"]["distilled_characteristics_path"] = "not/a/governance/path.md"
    _write_data(_workspace(context), payload)


@given("a well-formed complexity-thresholds fixture with the bootstrap section")
def step_fixture_with_bootstrap_section(context):
    _write_data(_workspace(context), _well_formed_payload())
    _write_narrative(_workspace(context), _BOOTSTRAP_NARRATIVE)


@given("a well-formed complexity-thresholds fixture")
def step_fixture_well_formed(context):
    _write_data(_workspace(context), _well_formed_payload())


@then('the repo file "{rel_path}" contains "{text}"')
def step_repo_file_contains(_context, rel_path: str, text: str) -> None:
    """Assert a file under the canonical repo root contains the given text.

    Distinct from `gz_steps.py`'s `Then the file "{path}" contains "{text}"`,
    which resolves paths against the behave workspace tempdir. This step
    resolves against the project root so static-doc checks (REQ-0.0.28-03-07)
    don't depend on docs being copied into the workspace.
    """
    target = _REPO_ROOT / rel_path
    assert target.is_file(), f"Expected repo file {rel_path} to exist at {target}"
    content = target.read_text(encoding="utf-8")
    assert text in content, f"Expected {rel_path} to contain {text!r}"
