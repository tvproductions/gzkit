# Plan: OBPI-0.0.35-03-why-foundation-tier-convention

**OBPI:** OBPI-0.0.35-03-why-foundation-tier-convention
**ADR:** ADR-0.0.35-foundation-feature-invariance-test
**Lane:** Lite

## Context

ADR-0.0.35 Decision #6 states: "Every foundation ADR's body answers the invariance test
affirmatively, in plain language, under a `## Why foundation tier?` section the validator
can find." OBPI-03 introduces that convention: section heading, position, two prompts,
template scaffolding, concept-page documentation, and runbook cross-reference.

`render_template()` uses stdlib `str.format_map(SafeDict(...))` — a `{why_foundation_tier}`
placeholder in `adr.md` is conditionally populated by the renderer (foundation → full
section body; feature → empty string → section absent).

## Files

- `src/gzkit/templates/adr.md` — add `{why_foundation_tier}` placeholder between `## Persona` and `## Intent`
- `src/gzkit/commands/plan.py` — compute `why_foundation_tier` str in `_render_adr_by_kind`, pass to `render_template`
- `tests/commands/test_plan.py` — add RED→GREEN tests for foundation/feature scaffolding behavior
- `docs/user/concepts/foundation-feature-invariance-test.md` — add `## Why foundation tier? (the convention)` section
- `docs/user/runbook.md` — add cross-reference at `gz plan create --kind foundation`
- `docs/user/manpages/plan-create.md` — update "What It Does" to describe the new section

## Steps

### Step 1: Write RED test (TDD Red)

In `tests/commands/test_plan.py`, add:
- `test_foundation_adr_scaffolds_why_foundation_tier_section` — assert `## Why foundation tier?` is present in foundation output
- `test_feature_adr_does_not_scaffold_why_foundation_tier_section` — assert it is absent in feature output
- Use `gz plan create <slug> --kind foundation --semver 0.0.99 --lane lite --dry-run` or direct `_render_adr_by_kind` call to get the rendered content

Run `uv run -m unittest tests.commands.test_plan -v` — expect RED (section missing).

### Step 2: Update `src/gzkit/templates/adr.md`

Between `## Persona` and `## Intent`, insert:

```
{why_foundation_tier}
```

The placeholder resolves to either the full section block (foundation) or empty string (feature).

### Step 3: Update `src/gzkit/commands/plan.py` — `_render_adr_by_kind`

Add computation of `why_foundation_tier` before the `render_template` call:

```python
WHY_FOUNDATION_TIER_SECTION = """\
## Why foundation tier?

_[Answer the invariance test in one sentence: "Without this ADR, would the project \
still be the project?" Answer yes or no and state why.]_

_[Port-vs-plug framing: Is this ADR a port (an abstract contract every implementation \
must honor) or a plug (one implementation behind an existing port)?]_
"""

# In _render_adr_by_kind:
why_foundation_tier = WHY_FOUNDATION_TIER_SECTION if kind == "foundation" else ""
content = render_template(
    "adr",
    ...
    why_foundation_tier=why_foundation_tier,
)
```

Constant declared at module level so the template text is not buried in a function body.

### Step 4: Verify GREEN

Run `uv run -m unittest tests.commands.test_plan -v` — expect GREEN.

### Step 5: Update concept page `docs/user/concepts/foundation-feature-invariance-test.md`

Add a `## Why foundation tier? (the convention)` section documenting:
- The exact heading `## Why foundation tier?` (byte-identical)
- That it sits between `## Persona` and `## Intent` in foundation ADRs only
- One filled-in example (e.g. from ADR-0.0.35 itself)
- Cross-reference to OBPI-04 validator (when shipped, it enforces the section non-empty)

### Step 6: Update `docs/user/runbook.md`

At the `gz plan create --kind foundation` section, add a one-line cross-reference:
> Foundation ADRs scaffold a `## Why foundation tier?` section — see the [convention docs](../concepts/foundation-feature-invariance-test.md#why-foundation-tier-the-convention).

### Step 7: Update `docs/user/manpages/plan-create.md`

In "What It Does" item #2 or #4 (foundation path), note that foundation scaffolding
includes the `## Why foundation tier?` section pre-populated with author prompts.

### Step 8: Run full verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Verification

```bash
grep -F "## Why foundation tier?" src/gzkit/templates/adr.md
grep -F "## Why foundation tier?" src/gzkit/templates/adr_pool.md && echo "DEFECT" || echo "OK"
uv run gz plan create test-foundation-scaffold-check --kind foundation --semver 0.0.99 --lane lite --score-data-state 0 --score-logic-engine 0 --score-interface 0 --score-observability 0 --score-lineage 1 --dry-run
uv run gz plan create test-feature-scaffold-check --kind feature --semver 0.99.0 --lane lite --score-data-state 0 --score-logic-engine 0 --score-interface 0 --score-observability 0 --score-lineage 1 --dry-run
grep -F "Why foundation tier?" docs/user/concepts/foundation-feature-invariance-test.md
grep -F "Why foundation tier?" docs/user/runbook.md
uv run gz test
```

## Notes

- `{why_foundation_tier}` resolves to empty string for feature ADRs — no section rendered (REQ-02)
- Position: placeholder between `## Persona` and `## Intent` → second H2 in foundation scaffolding (REQ-09)
- The section body must contain exactly two operator-facing prompts (REQ-03)
- No template engine dependency — stdlib `str.format_map` (REQ-10)
- `adr_pool.md` must not be touched (REQ-06 equivalent; pool has no `kind:`)
- Destination-in-mind: `{placeholder}` approach in single template + renderer branch
- Rejected alternatives: two-template approach (duplication), Jinja2 conditional (third-party dep)
