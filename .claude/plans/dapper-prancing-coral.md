# Plan: OBPI-0.0.13-04 — Vendor-Neutral Persona Loading Adapters

## Context

Persona frames exist in `.gzkit/personas/` with a stable `PersonaFrontmatter` model (OBPI-01) and sync pipeline (OBPI-03), but sync currently copies raw markdown to all vendor mirrors without format translation. Different agent runtimes consume identity context in different native formats — Claude uses system prompt fragments, Codex uses AGENTS.md instruction blocks, Copilot uses `.github/copilot-instructions.md` entries. This OBPI adds pure-function vendor adapters that translate canonical persona frames into each vendor's native format.

## Implementation

### Task 1: Add vendor adapter functions to `src/gzkit/personas.py`

Three pure functions alongside existing `compose_persona_frame()`:

**`render_persona_claude(fm: PersonaFrontmatter, body: str = "") -> str`**
- Delegates to `compose_persona_frame(fm, body)` which already produces Claude's native format (grounding + traits as behavioral instructions + anti-traits as constraints)
- Thin wrapper for adapter registry consistency

**`render_persona_codex(fm: PersonaFrontmatter, body: str = "") -> str`**
- Produces an AGENTS.md-compatible instruction block:
  ```
  # Persona: {name}

  {grounding}

  ## Behavioral Traits
  - {trait}: {description} (or just - {trait})

  ## Anti-Patterns
  - {anti-trait}: {description} (or just - {anti-trait})
  ```
- Uses `_parse_anchors()` for description lookup (same as `compose_persona_frame`)

**`render_persona_copilot(fm: PersonaFrontmatter, body: str = "") -> str`**
- Produces a `.github/copilot-instructions.md`-compatible fragment:
  ```
  ## Persona: {name}

  {grounding}

  Behavioral traits: {trait1}, {trait2}, ...

  Behaviors to avoid: {anti-trait1}, {anti-trait2}, ...
  ```
- Compact single-section format suitable for embedding in copilot instructions

**`VENDOR_ADAPTERS: dict[str, Callable]`** — registry mapping vendor name → adapter function. Used by sync and for fallback logic (unknown vendor → return raw canonical markdown).

**`render_persona_for_vendor(vendor: str, fm: PersonaFrontmatter, body: str = "") -> str`** — dispatcher that looks up adapter in registry, falls back to raw `f"---\n{yaml frontmatter}\n---\n\n{body}"` for unknown vendors.

### Task 2: Wire adapters into persona sync in `src/gzkit/sync_surfaces.py`

Update `sync_persona_mirrors()` to:
1. Parse each canonical persona file via `parse_persona_file()`
2. For each vendor, call `render_persona_for_vendor(vendor, fm, body)`
3. Write the rendered output to the vendor mirror directory
4. Replace the current raw `sync_skill_mirror()` call with this adapter-aware rendering

This follows the exact pattern established by `render_rules_to_dir()` in `rules.py`.

### Task 3: Create `tests/test_persona_loading.py`

Unit tests covering all 8 brief requirements:

| Test | Covers |
|------|--------|
| Claude adapter produces traits as behavioral instructions + anti-traits as constraints | REQ-0.0.13-04-01 |
| Codex adapter produces AGENTS.md instruction block | REQ-0.0.13-04-02 |
| Copilot adapter produces copilot-instructions.md fragment | REQ-0.0.13-04-03 |
| Unknown vendor falls back to raw canonical markdown | REQ-0.0.13-04-04 |
| Same input twice → identical output (determinism) | REQ-0.0.13-04-05 |
| Adapters are pure (no side effects, no file I/O) | Covered by function design |
| Adapters translate format, not meaning | Covered by output assertions |

Test helper: reuse `PersonaFrontmatter(name=..., traits=[...], anti_traits=[...], grounding=...)` construction pattern from `test_persona_composition.py`.

## Files Modified

| File | Change |
|------|--------|
| `src/gzkit/personas.py` | Add 3 adapter functions + registry + dispatcher |
| `src/gzkit/sync_surfaces.py` | Update `sync_persona_mirrors()` to use adapters |
| `tests/test_persona_loading.py` | **New** — adapter unit tests |

## Verification

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest tests.test_persona_loading -v
uv run gz lint
uv run gz typecheck
uv run gz test
python -c "from gzkit.personas import render_persona_claude, render_persona_codex, render_persona_copilot; print('All adapters importable')"
```
