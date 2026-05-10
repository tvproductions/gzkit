# Plan: OBPI-0.0.30-05 — gz justify Complexity-Hints Integration

## Context

OBPI-0.0.30-05 amends the `gz justify` rendering pipeline to inject authoring-time
complexity hints (from OBPI-03's `engine.analyze`) into the justification scaffold's
evidence section when the active OBPI's Allowed Paths include `.py` files.

`engine.analyze` is landed (OBPI-03 Completed). The rendering lives in
`src/gzkit/justify/cli.py` + `walkthrough.py` + `templates/walkthrough.md.j2`,
not in `src/gzkit/commands/justify.py` (brief path corrected in plan-audit).

## Files

**New:**
- `src/gzkit/justify/complexity_hints.py`
- `tests/commands/test_justify_authoring_hints.py`
- `tests/skills/test_gz_justify_complexity_amendment.py`
- `features/justify_complexity_hints.feature`

**Modified:**
- `src/gzkit/justify/walkthrough.py` — add `complexity_hints_md: str | None = None`
- `src/gzkit/justify/templates/walkthrough.md.j2` — conditional hints block
- `src/gzkit/justify/cli.py` — invoke hints integration after scaffold render
- `.gzkit/skills/gz-justify/SKILL.md` — skill-version bump + new section
- `docs/user/runbook.md` — entry under "Complexity doctrine surfaces"
- `docs/design/adr/.../OBPI-0.0.30-05-justify-integration.md` — evidence only

## Steps

### Step 1: Write tests first (TDD RED)

Write `tests/commands/test_justify_authoring_hints.py` with `@covers` for REQs 01–04.
Write `tests/skills/test_gz_justify_complexity_amendment.py` with `@covers` for REQs 05–06.
Confirm all RED before implementing.

### Step 2: Implement `src/gzkit/justify/complexity_hints.py`

- `extract_py_allowed_paths(anchor_ref, project_root)` — parse brief Allowed Paths for `.py` globs
- `gather_hints_markdown(anchor_ref, *, project_root)` — call `engine.analyze`, format markdown, fail open
- `_format_hint_block(hint)` — per-hint rendering: metric, band, archetype, frame headline, move, file:line
- `_log_failure(reason, project_root)` — append JSON record to `.gzkit/insights/justify-failures.jsonl`

### Step 3: Amend `src/gzkit/justify/walkthrough.py`

Add `complexity_hints_md: str | None = None` field to `Walkthrough`. No change to model_validator.

### Step 4: Amend `src/gzkit/justify/templates/walkthrough.md.j2`

Add conditional block at template end:
```
{% if walkthrough.complexity_hints_md %}

### Authoring-time complexity hints

{{ walkthrough.complexity_hints_md }}
{% endif %}
```

### Step 5: Amend `src/gzkit/justify/cli.py`

In `handle_justify`, after `render_scaffold` call:
1. Call `gather_hints_markdown(anchor_ref, project_root=project_root)` → `(hints_md, warnings)`
2. If `hints_md`, rebuild walkthrough with `complexity_hints_md=hints_md`
3. Re-render markdown from updated walkthrough

### Step 6: Run tests to GREEN

`uv run -m unittest tests/commands/test_justify_authoring_hints.py tests/skills/test_gz_justify_complexity_amendment.py -v`

### Step 7: Amend `.gzkit/skills/gz-justify/SKILL.md`

- Bump `skill-version: "6.0.1"` → `"6.1.0"`
- Add "Authoring-time complexity hints (ADR-0.0.30-05)" section after Purpose

### Step 8: Run `uv run gz agent sync control-surfaces`

Sync vendor mirrors; verify diff empty after sync.

### Step 9: Write `features/justify_complexity_hints.feature`

Three scenarios: hints injected (REQ-01), no .py paths (REQ-02), engine failure (REQ-03).

### Step 10: Update `docs/user/runbook.md`

Add entry under "Complexity doctrine surfaces": when it fires, where hints land, fail-open behavior.

### Step 11: Full quality checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run mkdocs build --strict
uv run gz validate --documents --surfaces
```

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_justify_authoring_hints.py tests/skills/test_gz_justify_complexity_amendment.py -v
uv run -m behave features/justify_complexity_hints.feature
uv run mkdocs build --strict
uv run gz validate --documents --surfaces
uv run gz agent sync control-surfaces
```

## Destination-in-Mind (Step 6a Disclosure)

Approach chosen before writing this plan: add `complexity_hints.py` integration module,
extend `Walkthrough` with optional `complexity_hints_md`, update template, inject from
`handle_justify`.

**Rejected alternatives:**
1. Modify section 7's `evidence_citations` list — rejected; hint format is multi-line prose,
   not a citation string; would break the model contract.
2. Post-process markdown string — rejected; fragile string manipulation, harder to test.
3. Extend `gather_evidence` to include hints — rejected; conflates IO-bound five-source gather
   with CPU-bound analysis; complicates timeout logic.

## Notes

- `Walkthrough.model_validator` only checks section ordinals/headings; `complexity_hints_md`
  is an optional field and is backward-compatible.
- Vendor mirrors are generated via `gz agent sync control-surfaces`, not hand-edited.
- REQ-0.0.30-05-06 (vendor mirrors byte-identical) verified by diffing after sync.
