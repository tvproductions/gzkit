"""Behave step definitions for ``gz complexity guide`` (OBPI-0.0.30-01).

Reuses the canonical ``When I run the gz command "..."`` /
``Then the command exits with code N`` step set in ``features/steps/gz_steps.py``.
This module provides only the synthetic-environment Given steps that build
a fixture with the canonical threshold table at ``.gzkit/rules/complexity-thresholds.json``
and a distilled-characteristics document, which the authoring engine requires.

@covers REQ-0.0.30-01-01
@covers REQ-0.0.30-01-02
@covers REQ-0.0.30-01-03
"""

from __future__ import annotations

import json
from pathlib import Path

from behave import given  # type: ignore[import-untyped]

_PRACTITIONER_EYE_SENTINEL = "Refactor signal: extract the responsibility seam and re-test."

CLEAN_SOURCE = """\
def add(a, b):
    return a + b


def double(x):
    return x * 2
"""

# CC = 5 — crosses advise (>=4) but not warn (>=7) or block (>=11)
ADVISE_SOURCE = """\
def advise_band(x):
    if x > 0:
        if x > 1:
            return 1
        elif x > 2:
            return 2
        elif x > 3:
            return 3
        else:
            return 4
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
    """Synthesize the JSON threshold data payload."""
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
    """Materialize distilled doc + threshold data (at canonical path) + subject.py in CWD."""
    cwd = Path.cwd()
    complexity_dir = cwd / "docs" / "governance" / "complexity"
    complexity_dir.mkdir(parents=True, exist_ok=True)
    distilled_path = complexity_dir / "distilled-characteristics-synthetic.md"
    distilled_path.write_text(_distilled_characteristics(), encoding="utf-8")

    # Guide uses DEFAULT_RULE_PATH = ".gzkit/rules/complexity-thresholds.json"
    rule_dir = cwd / ".gzkit" / "rules"
    rule_dir.mkdir(parents=True, exist_ok=True)
    rule_path = rule_dir / "complexity-thresholds.json"
    anchor = "radon-cc"
    rule_path.write_text(
        _rule_data("radon_cc", distilled_path.relative_to(cwd), anchor),
        encoding="utf-8",
    )

    subject = cwd / "subject.py"
    subject.write_text(source, encoding="utf-8")


@given("a synthetic complexity-guide environment with a clean Python source")
def step_synthetic_clean_env(_context) -> None:  # type: ignore[no-untyped-def]
    _build_synthetic_environment(CLEAN_SOURCE)


@given("a synthetic complexity-guide environment with an advise-band Python source")
def step_synthetic_advise_env(_context) -> None:  # type: ignore[no-untyped-def]
    _build_synthetic_environment(ADVISE_SOURCE)
