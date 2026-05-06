"""BDD steps for the complexity-thresholds rule body validator.

Covers ``features/complexity_thresholds.feature`` (OBPI-0.0.28-03).

@covers REQ-0.0.28-03-02
@covers REQ-0.0.28-03-03
@covers REQ-0.0.28-03-04
@covers REQ-0.0.28-03-05
"""

from __future__ import annotations

import re
from pathlib import Path

from behave import given, then

_RULE_REL_PATH = Path(".gzkit") / "rules" / "complexity-thresholds.md"
_REPO_ROOT = Path(__file__).resolve().parents[2]


def _well_formed_body(*, include_bootstrap: bool = False) -> str:
    """Synthetic well-formed threshold rule body covering all 12 metrics."""
    metrics_with_bands = [
        ("radon_cc", "radon-cc", 4.0, 7.0, 11.0),
        ("radon_mi", "radon-mi", 85.0, 70.0, 50.0),
        ("radon_hal_volume", "radon-hal-volume", 946.89, 2740.93, 5549.80),
        ("radon_hal_difficulty", "radon-hal-difficulty", 8.13, 11.54, 12.46),
        ("radon_hal_effort", "radon-hal-effort", 7975.79, 30805.01, 74805.40),
        ("radon_raw_nloc", "radon-raw-nloc", 311.75, 733.20, 1031.90),
        ("radon_raw_lloc", "radon-raw-lloc", 238.25, 518.00, 811.70),
        ("lizard_nloc", "lizard-nloc", 13.0, 25.0, 37.0),
        ("lizard_param_count", "lizard-param-count", 3.0, 4.0, 5.0),
        ("lizard_nesting_depth", "lizard-nesting-depth", 2.0, 3.0, 4.0),
        ("lizard_ccn", "lizard-ccn", 4.0, 8.0, 11.0),
        ("cohesion_lcom4", "cohesion-lcom4", 2.0, 4.0, 8.0),
    ]
    sections = []
    for metric, anchor, advise, warn, block in metrics_with_bands:
        sections.append(
            f"### Metric: `{metric}`\n\n"
            f"Citation: `docs/governance/complexity/distilled-characteristics-2026-05-04.md "
            f"§ {anchor} (corpus revision 1)`\n\n"
            "| Trigger | Corpus percentile | Absolute number | Cited section |\n"
            "|---------|-------------------|-----------------|---------------|\n"
            f"| advise  | p75               | {advise}        | {anchor}      |\n"
            f"| warn    | p90               | {warn}          | {anchor}      |\n"
            f"| block   | p95               | {block}         | {anchor}      |\n"
        )
    bootstrap_section = ""
    if include_bootstrap:
        bootstrap_section = (
            "\n## Bootstrap absolutes (REQ-11 carve-out — one-shot)\n\n"
            "- `radon_mi` — bootstrap (GHI #405)\n"
            "- `lizard_nesting_depth` — bootstrap (GHI #404)\n"
            "- `cohesion_lcom4` — bootstrap (GHI #404)\n"
        )
    return (
        "---\n"
        "id: complexity-thresholds\n"
        "paths:\n"
        '  - ".gzkit/rules/complexity-thresholds.md"\n'
        "description: behave fixture\n"
        "---\n\n"
        "<!-- rule-version: 0.1.0 -->\n\n"
        "# Complexity Thresholds\n\n"
        "## Citation\n\n"
        "`docs/governance/complexity/distilled-characteristics-2026-05-04.md "
        "§ radon-cc (corpus revision 1)`\n\n"
        "## Per-metric tables\n\n" + "\n".join(sections) + bootstrap_section
    )


def _write_rule(workspace: Path, body: str) -> None:
    rule_path = workspace / _RULE_REL_PATH
    rule_path.parent.mkdir(parents=True, exist_ok=True)
    rule_path.write_text(body, encoding="utf-8")


def _workspace(_context) -> Path:
    return Path.cwd()


@given("a complexity-thresholds fixture with radon_cc missing its block band")
def step_fixture_missing_block_band(context):
    body = re.sub(
        r"^\|\s*block\s*\|\s*p95\s*\|\s*[\d.]+\s*\|\s*radon-cc\s*\|\s*\n",
        "",
        _well_formed_body(),
        count=1,
        flags=re.MULTILINE,
    )
    _write_rule(_workspace(context), body)


@given("a complexity-thresholds fixture with radon_cc carrying an off-enum percentile")
def step_fixture_off_enum_percentile(context):
    body = _well_formed_body().replace(
        "| advise  | p75               | 4.0        | radon-cc      |",
        "| advise  | p80               | 4.0        | radon-cc      |",
    )
    _write_rule(_workspace(context), body)


@given("a complexity-thresholds fixture with a malformed citation block")
def step_fixture_malformed_citation(context):
    body = _well_formed_body().replace(
        "## Citation\n\n"
        "`docs/governance/complexity/distilled-characteristics-2026-05-04.md "
        "§ radon-cc (corpus revision 1)`\n\n",
        "## Citation\n\n`malformed-citation-no-canonical-form`\n\n",
    )
    _write_rule(_workspace(context), body)


@given("a well-formed complexity-thresholds fixture with the bootstrap section")
def step_fixture_with_bootstrap_section(context):
    _write_rule(_workspace(context), _well_formed_body(include_bootstrap=True))


@given("a well-formed complexity-thresholds fixture")
def step_fixture_well_formed(context):
    _write_rule(_workspace(context), _well_formed_body())


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
