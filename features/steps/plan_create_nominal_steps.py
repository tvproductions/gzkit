"""BDD step definitions for plan_create_nominal.feature.

@covers REQ-0.0.57-02-01, REQ-0.0.57-02-03
"""

from __future__ import annotations

from pathlib import Path

from behave import given


@given('foundation ADRs exist for IDs "{ids}"')
def step_create_foundation_adrs(context, ids: str) -> None:  # type: ignore[no-untyped-def]
    """Create stub foundation ADR directories under the test workspace.

    `ids` is a comma-separated list of integer N values; each creates
    `design/adr/foundation/ADR-0.0.{N}-fixture-{N}/.gitkeep` so the
    nominal allocator can scan the tree. The path matches the default
    `paths.adrs` value in `gzkit.config.GzkitConfig` (`design/adr`).
    """
    foundation = Path("design/adr/foundation")
    foundation.mkdir(parents=True, exist_ok=True)
    for n_str in ids.split(","):
        n = n_str.strip()
        adr_dir = foundation / f"ADR-0.0.{n}-fixture-{n}"
        adr_dir.mkdir(parents=True, exist_ok=True)
        (adr_dir / ".gitkeep").write_text("", encoding="utf-8")
