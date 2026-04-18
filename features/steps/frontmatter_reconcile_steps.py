"""BDD steps for gz frontmatter reconcile (OBPI-0.0.16-03).

Seeds drifted frontmatter on an existing ADR, runs the reconciler, and
asserts the resulting file state and receipt emission. Drift-seeding reuses
the pattern from ``gates_frontmatter_steps.py`` so the two step files stay
shape-compatible.
"""

from __future__ import annotations

from pathlib import Path

from behave import given, then

from gzkit.config import GzkitConfig


def _adr_file_for(adr_id: str) -> Path:
    config = GzkitConfig.load(Path(".gzkit.json"))
    adr_dir = Path(config.paths.design_root) / "adr"
    matches = list(adr_dir.rglob(f"ADR-{adr_id}.md")) + list(adr_dir.rglob(f"ADR-{adr_id}-*.md"))
    assert matches, f"No ADR file matches ADR-{adr_id}*.md under {adr_dir}"
    return matches[0]


def _set_frontmatter_field(adr_path: Path, key: str, value: str) -> None:
    """Rewrite or append a single frontmatter field to the given value."""
    original = adr_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    assert lines and lines[0] == "---", f"Expected frontmatter in {adr_path}"
    close_idx = next(
        (idx for idx, line in enumerate(lines[1:], start=1) if line == "---"),
        None,
    )
    assert close_idx is not None, f"Unclosed frontmatter in {adr_path}"
    fm_lines = lines[1:close_idx]
    new_line = f"{key}: {value}"
    updated_fm: list[str] = []
    replaced = False
    for fm_line in fm_lines:
        if fm_line.strip().startswith(f"{key}:"):
            updated_fm.append(new_line)
            replaced = True
        else:
            updated_fm.append(fm_line)
    if not replaced:
        updated_fm.append(new_line)
    new_lines = ["---", *updated_fm, "---", *lines[close_idx + 1 :]]
    adr_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


@given('ADR-{adr_id} has drifted lane frontmatter "{drifted_lane}"')
def step_drift_adr_lane(context, adr_id: str, drifted_lane: str) -> None:  # type: ignore[no-untyped-def]
    _ = context
    _set_frontmatter_field(_adr_file_for(adr_id), "lane", drifted_lane)


@then('ADR-{adr_id} frontmatter "{key}" equals "{expected}"')
def step_assert_fm_equals(context, adr_id: str, key: str, expected: str) -> None:  # type: ignore[no-untyped-def]
    _ = context
    content = _adr_file_for(adr_id).read_text(encoding="utf-8")
    assert f"{key}: {expected}" in content, (
        f"Expected `{key}: {expected}` in frontmatter of ADR-{adr_id}, got:\n{content[:400]}"
    )


@then("a frontmatter-coherence receipt exists")
def step_receipt_exists(context) -> None:  # type: ignore[no-untyped-def]
    _ = context
    receipts_dir = Path("artifacts") / "receipts" / "frontmatter-coherence"
    assert receipts_dir.is_dir(), f"{receipts_dir} must exist after reconcile"
    receipts = list(receipts_dir.glob("*.json"))
    assert receipts, "At least one reconciliation receipt must be emitted"
