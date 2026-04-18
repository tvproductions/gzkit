"""BDD steps for gates frontmatter integration (OBPI-0.0.16-02).

Seeds drifted frontmatter on an existing ADR so Gate 1's coherence check
fires. Reuses the inline-filesystem-write pattern from
``state_repair_steps.py:14-26``.
"""

from __future__ import annotations

from pathlib import Path

from behave import given

from gzkit.config import GzkitConfig


@given('ADR-{adr_id} has drifted status frontmatter "{drifted_status}"')
def step_drift_adr_status(context, adr_id: str, drifted_status: str) -> None:  # type: ignore[no-untyped-def]
    """Overwrite an existing ADR's frontmatter to include a drifted status value."""
    _ = context
    config = GzkitConfig.load(Path(".gzkit.json"))
    adr_dir = Path(config.paths.design_root) / "adr"
    # `gz plan create` lands ADR-X.Y.Z.md at the top of the adr/ tree; deeper
    # folder layouts use ADR-X.Y.Z-slug.md. Match both.
    matches = list(adr_dir.rglob(f"ADR-{adr_id}.md")) + list(adr_dir.rglob(f"ADR-{adr_id}-*.md"))
    assert matches, f"Expected an ADR file matching ADR-{adr_id}*.md under {adr_dir}"
    adr_path = matches[0]
    original = adr_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    assert lines and lines[0] == "---", (
        f"Expected YAML frontmatter at top of {adr_path}, got:\n{original[:200]}"
    )
    # Find the frontmatter closing delimiter.
    close_idx = next(
        (idx for idx, line in enumerate(lines[1:], start=1) if line == "---"),
        None,
    )
    assert close_idx is not None, f"Unclosed frontmatter in {adr_path}"
    # Replace any existing status: line inside frontmatter, else append before close.
    fm_lines = lines[1:close_idx]
    status_line = f"status: {drifted_status}"
    updated_fm: list[str] = []
    replaced = False
    for fm_line in fm_lines:
        if fm_line.strip().startswith("status:"):
            updated_fm.append(status_line)
            replaced = True
        else:
            updated_fm.append(fm_line)
    if not replaced:
        updated_fm.append(status_line)
    new_lines = ["---", *updated_fm, "---", *lines[close_idx + 1 :]]
    adr_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
