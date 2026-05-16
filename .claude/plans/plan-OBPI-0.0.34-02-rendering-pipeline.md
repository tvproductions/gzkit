# Plan: OBPI-0.0.34-02-rendering-pipeline

**OBPI:** OBPI-0.0.34-02-rendering-pipeline
**Parent ADR:** ADR-0.0.34-agent-control-surface-rendering-substrate
**Brief:** `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/obpis/OBPI-0.0.34-02-rendering-pipeline.md`

## Destination-in-Mind Disclosure (Step 6a)

**Conclusion formed before planning:** Build a thin `render(model, vendor)` dispatcher
that resolves templates by convention path `content/templates/{type_name}/{vendor}.md.j2`
from the package, raises `TemplateNotFound` on missing templates, and produces
deterministic byte-stable output from Jinja2 with sorted dict iteration.

**Rejected alternatives:**
- A: Pass template path explicitly — rejected; convention-based lookup is the ADR substrate pattern
- B: stdlib `string.Template` — rejected; stdlib-first doctrine applies but Jinja2 is a named
  departure (already available transitively, canonical precedent in `gz justify`)
- C: Build a registry class for template dispatch — rejected; a dict-based routing table
  is sufficient; premature abstraction
- D: Defer sync_surfaces.py integration to OBPI-03 — rejected; brief explicitly lists
  `sync_surfaces.py` in allowed paths and REQ-03 requires render() wired into the sync path

## Context

- OBPI-01 prerequisite met: `CONTENT_MODELS` has 8 entries (AgentContract, Rule, Skill,
  Chore, Persona, Handoff, Scenario, Bullet)
- Jinja2 3.1.6 available transitively (no new dependency needed)
- `sync_surfaces.py` currently uses `_copy_if_changed` (not `shutil.copy`) for
  canonical → pkg propagation; REQ-03's literal grep check already passes
- `sync_skills.py` has no `shutil.copy` usage
- OBPI-08 (vendor manifest) lags; fallback to minimal in-code routing table

## Files

**Create:**
- `src/gzkit/content/render/__init__.py`
- `src/gzkit/content/render/pipeline.py`
- `src/gzkit/content/templates/rule/claude.md.j2`
- `src/gzkit/content/templates/skill/claude.md.j2`
- `src/gzkit/content/templates/persona/claude.md.j2`
- `src/gzkit/content/templates/agent_contract/claude.md.j2`
- `src/gzkit/content/templates/chore/claude.md.j2`
- `src/gzkit/content/templates/handoff/claude.md.j2`
- `src/gzkit/content/templates/scenario/claude.md.j2`
- `src/gzkit/content/templates/bullet/claude.md.j2`
- `tests/content/test_render_pipeline.py`
- `tests/content/test_byte_stability.py`

**Modify:**
- `src/gzkit/sync_surfaces.py` — add `render_content_surface()` helper and wire into sync
- `docs/design/adr/.../obpis/OBPI-0.0.34-02-rendering-pipeline.md` — update evidence

## Steps

### Step 1: Write failing tests (TDD RED)

Create `tests/content/test_render_pipeline.py`:
- `@covers("REQ-0.0.34-02-05")` — `test_template_not_found_raises()`: call `render()` with
  a valid model but unregistered vendor; assert `TemplateNotFound` raised
- `@covers("REQ-0.0.34-02-02")` — `test_all_registered_pairs_render_nonempty()`: for each
  (content_type, vendor) in the minimal routing table, render a stub model and assert
  non-empty bytes returned
- `@covers("REQ-0.0.34-02-03")` — `test_sync_surfaces_render_path_present()`: assert
  `sync_surfaces` module imports `render` from `gzkit.content.render`

Create `tests/content/test_byte_stability.py`:
- `@covers("REQ-0.0.34-02-01")` — `test_render_twice_byte_equal()`: for each
  (content_type, vendor), render the same stub model twice; assert bytes equal
- `@covers("REQ-0.0.34-02-04")` — `test_existing_byte_parity_tests_pass()`: verify the
  existing `tests/content/models/` tests continue to pass (no import breakage)

Run `uv run -m unittest tests.content.test_render_pipeline tests.content.test_byte_stability -v`
→ must FAIL at this step (modules not yet created)

### Step 2: Create render package skeleton (GREEN)

Create `src/gzkit/content/render/__init__.py`:
```python
"""Public render entrypoint — ADR-0.0.34 § Decision item #2."""
from .pipeline import render, TemplateNotFound

__all__ = ["render", "TemplateNotFound"]
```

Create `src/gzkit/content/render/pipeline.py`:
- `TemplateNotFound(content_type, vendor)` typed exception
- `_VENDOR_ROUTING: dict[tuple[str, str], str]` — minimal in-code routing table
  mapping `(content_type_name, vendor)` → template path relative to package templates dir
- `render(model: BaseContentModel, vendor: str) -> bytes` — loads Jinja2 Environment
  with `PackageLoader("gzkit.content", "templates")`, resolves template by
  `{model.__class__.__name__.lower()}/{vendor}.md.j2`, renders with sorted model dict,
  returns UTF-8 bytes
- Determinism invariants: `keep_trailing_newline=True`, `autoescape=False`,
  sorted Jinja2 dict filters where needed; no `undefined` stochastic fallback

Minimal routing table covers all 8 content types × claude vendor:
```
("AgentContract", "claude"), ("Rule", "claude"), ("Skill", "claude"),
("Chore", "claude"), ("Persona", "claude"), ("Handoff", "claude"),
("Scenario", "claude"), ("Bullet", "claude")
```

Run tests → should GREEN.

### Step 3: Create Jinja2 templates

Create one `.md.j2` template per content type under
`src/gzkit/content/templates/<content_type>/<vendor>.md.j2`:
- Each template renders the model fields in a deterministic format
- Use `{{ items | sort }}` and `{% for k, v in fields.items() | sort %}` for any
  dict/set iteration
- No timestamps, no insertion-order dict access without explicit sort key
- Templates produce minimal but non-empty markdown output for any valid model instance

Content type → field mapping from models (OBPI-01):
- Rule: title, version, paths (sorted list), body (Bullet list)
- Skill: slug, title, purpose, steps (Bullet list)
- AgentContract: (check agent_contract.py for fields)
- Persona, Chore, Handoff, Scenario, Bullet: (check each model for fields)

Run byte-stability tests → all GREEN.

### Step 4: Wire render() into sync_surfaces.py

Modify `src/gzkit/sync_surfaces.py`:
- Add import: `from gzkit.content.render import render`
- Add helper `render_content_surface(model, dest_path: Path, vendor: str,
  project_root: Path, updated: list[str]) -> None` that calls `render(model, vendor)`,
  writes bytes if changed, appends dest rel-path to `updated`
- Document that future content-type sync (post-OBPI-03) routes through this helper
  rather than `_copy_if_changed`
- No existing sync calls changed (backward-compatible; OBPI-03 will complete the migration)

Run `rg "shutil\.copy" src/gzkit/sync_surfaces.py` → no output (already true).
Run `uv run gz agent sync control-surfaces` → exits 0.

### Step 5: Verify all gates

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run -m unittest tests.content.test_render_pipeline tests.content.test_byte_stability -v
rg "shutil\.copy" src/gzkit/sync_surfaces.py
uv run gz agent sync control-surfaces
```

All checks must pass. Add `@covers` decorators to every test per the REQ IDs above.

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run python -m unittest tests.content.test_render_pipeline -v
uv run python -m unittest tests.content.test_byte_stability -v
uv run gz agent sync control-surfaces
rg -n "shutil\.copy" src/gzkit/sync_surfaces.py
```

## Notes

- OBPI-08 soft dependency: routing table in pipeline.py is replaced by vendor manifest
  lookup when OBPI-08 lands. The fallback dict is designed to be a drop-in replacement.
- Round-trip contract (parse → render) is NOT in scope; that is OBPI-03. This OBPI
  builds the render half only.
- No parse logic, no validation hooks, no schema migration in scope.
