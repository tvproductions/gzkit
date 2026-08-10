"""Behave step definitions for ``gz complexity advise`` (OBPI-0.0.29-03).

Reuses the canonical ``When I run the gz command "..."`` /
``Then the command exits with code N`` step set in ``features/steps/gz_steps.py``.
This module provides only the synthetic-environment Given steps that build
the same fixture shape ``tests/commands/test_complexity_advise.py`` uses
(distilled-characteristics document under ``docs/governance/complexity/`` +
threshold rule body in CWD), which the engine requires because the
production distilled doc has an empty practitioner-eye section.

@covers REQ-0.0.29-03-01
@covers REQ-0.0.29-03-02
@covers REQ-0.0.29-03-03
"""

from __future__ import annotations

import json
from pathlib import Path

from behave import given

_PRACTITIONER_EYE_SENTINEL = "Refactor signal: extract the responsibility seam and re-test."

CLEAN_SOURCE = """\
def add(a, b):
    return a + b


def double(x):
    return x * 2
"""

WARN_SOURCE = """\
def warn_band(x):
    if x > 0:
        if x > 1:
            return 1
        elif x > 2:
            return 2
        elif x > 3:
            return 3
        elif x > 4:
            return 4
        else:
            return 5
    return 0
"""

BLOCK_SOURCE = """\
def block_band(x):
    if x > 0:
        if x > 1:
            return 1
        elif x > 2:
            return 2
        elif x > 3:
            return 3
        elif x > 4:
            return 4
        elif x > 5:
            return 5
        elif x > 6:
            return 6
        elif x > 7:
            return 7
        elif x > 8:
            return 8
        elif x > 9:
            return 9
        elif x > 10:
            return 10
        else:
            return 11
    return 0
"""


def _distilled_characteristics(metric: str = "radon_cc") -> str:
    return "\n".join(
        [
            "---",
            "corpus_revision: 1",
            "---",
            "",
            "# Distilled complexity characteristics — synthetic fixture",
            "",
            f"## Metric: `{metric}`",
            "",
            "Across the corpus, synthetic distribution applies.",
            "",
            "**Doctrinal frame:** Martin (Clean Code) — function decomposition signal.",
            "",
            "### Practitioner-eye observation",
            "",
            _PRACTITIONER_EYE_SENTINEL,
            "",
        ]
    )


def _rule_data(metric: str, distilled_path: Path, anchor: str) -> str:
    """Synthesize the JSON data payload (GHI #426 — data is JSON, narrative .md)."""
    return json.dumps(
        {
            "corpus_revision": 1,
            "citation": {
                "distilled_characteristics_path": distilled_path.as_posix(),
                "section_anchor": anchor,
                "corpus_revision": 1,
            },
            "bands": [
                {
                    "metric": metric,
                    "corpus_percentile": 75,
                    "absolute_number": 4.0,
                    "trigger_semantic": "advise",
                },
                {
                    "metric": metric,
                    "corpus_percentile": 90,
                    "absolute_number": 7.0,
                    "trigger_semantic": "warn",
                },
                {
                    "metric": metric,
                    "corpus_percentile": 95,
                    "absolute_number": 11.0,
                    "trigger_semantic": "block",
                },
            ],
        }
    )


def _build_synthetic_environment(source: str) -> None:
    """Materialize distilled doc + threshold data + subject.py in CWD."""
    cwd = Path.cwd()
    complexity_dir = cwd / "docs" / "governance" / "complexity"
    complexity_dir.mkdir(parents=True, exist_ok=True)
    distilled_path = complexity_dir / "distilled-characteristics-synthetic.md"
    distilled_path.write_text(_distilled_characteristics(), encoding="utf-8")
    rule_path = cwd / "complexity-thresholds.json"
    anchor = "radon-cc"
    rule_path.write_text(
        _rule_data("radon_cc", distilled_path.relative_to(cwd), anchor),
        encoding="utf-8",
    )
    subject = cwd / "subject.py"
    subject.write_text(source, encoding="utf-8")


@given("a synthetic complexity-advise environment with a clean Python source")
def step_synthetic_clean_env(_context) -> None:
    _build_synthetic_environment(CLEAN_SOURCE)


@given("a synthetic complexity-advise environment with a warn-band Python source")
def step_synthetic_warn_env(_context) -> None:
    _build_synthetic_environment(WARN_SOURCE)


@given("a synthetic complexity-advise environment with a block-band Python source")
def step_synthetic_block_env(_context) -> None:
    _build_synthetic_environment(BLOCK_SOURCE)
