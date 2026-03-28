"""BDD steps for closeout ceremony enforcement (ADR-0.23.0 / OBPI-0.23.0-04)."""

from __future__ import annotations

from pathlib import Path

from behave import given

from gzkit.config import GzkitConfig


@given("the OBPI brief has a closing argument")
def step_obpi_has_closing_argument(_context) -> None:  # type: ignore[no-untyped-def]
    config = GzkitConfig.load(Path(".gzkit.json"))
    obpi_dir = Path(config.paths.adrs) / "obpis"
    brief_path = obpi_dir / "OBPI-0.1.0-01-demo-feature.md"
    content = brief_path.read_text(encoding="utf-8")

    # Insert Closing Argument section before Evidence section
    closing_arg = (
        "\n## Closing Argument\n\n"
        "1. **What was built** -- Demo feature with docstring proof.\n\n"
        "2. **What it enables** -- Product proof gate validation.\n\n"
        "3. **Why it matters** -- `uv run gz test` proves the gate.\n\n"
    )
    # Insert before the Evidence section if it exists
    evidence_marker = "## Evidence"
    if evidence_marker in content:
        content = content.replace(evidence_marker, closing_arg + evidence_marker)
    else:
        content = content.rstrip() + "\n" + closing_arg
    brief_path.write_text(content, encoding="utf-8")


@given("a reviewer assessment exists for the OBPI")
def step_reviewer_assessment_exists(_context) -> None:  # type: ignore[no-untyped-def]
    config = GzkitConfig.load(Path(".gzkit.json"))
    adr_dir = Path(config.paths.adrs)

    # Create review artifact in the obpis/ directory (same as brief location)
    obpis_dir = adr_dir / "obpis"
    obpis_dir.mkdir(parents=True, exist_ok=True)
    review_path = obpis_dir / "REVIEW-OBPI-0.1.0-01-demo-feature.md"
    review_path.write_text(
        "\n".join(
            [
                "# Reviewer Assessment: OBPI-0.1.0-01-demo-feature",
                "",
                "**Date:** 2026-03-28",
                "**Verdict:** PASS",
                "",
                "## Promises Met",
                "",
                "1. **[YES]** Demo feature works",
                "",
                "## Documentation Quality",
                "",
                "**Assessment:** substantive",
                "",
                "## Closing Argument Quality",
                "",
                "**Assessment:** earned",
                "",
                "## Summary",
                "",
                "All requirements met.",
                "",
            ]
        ),
        encoding="utf-8",
    )
