# Plan: OBPI-0.0.37-15-per-vendor-template-selection

## Context

- **ADR:** `ADR-0.0.37-constitutional-invariant-composition`
- **OBPI:** `OBPI-0.0.37-15-per-vendor-template-selection`
- **Lane:** Heavy — Gate 5 human attestation required
- **Decision item (verbatim):** "OBPI-0.0.37-15 — Per-vendor template selection (Codex lite / Claude standard; ends identical mirroring; harness-detection is a forward-reference)."
- **Prerequisites confirmed:** OBPI-12 (temperature renderer) ✓ Completed; OBPI-14 (sync wired) ✓ Completed

## Plan-Before-Exploration Disclosure (Step 6a)

**Destination-in-mind before writing this plan:** Before composing the plan I had already determined that the core change is adding `temperature_for()` to `vendors.py` (fail-closed on missing), un-hardcoding `temperature="heavy"` in `sync_agents_md` to call `temperature_for()`, adding the `content_type_temperatures` sibling block to the manifest and schema, and creating `codex.md.j2` (structurally identical to `claude.md.j2` — projection happens before rendering). The `codex` vendor must also be added to `content_type_routes.AgentContract` so the render pipeline's routing guard accepts it.

**Rejected alternatives:**
- *Only declare temperatures, don't add codex to routes:* Rejected — `render(model, "codex")` fails at the routing guard in `pipeline.py` without a route entry, making REQ-04's "renders differ" test impossible without bypassing the guard.
- *Auto-detect temperature from harness/model:* Rejected — REQ-5 explicitly forbids this ("NEVER: implement harness/model auto-detection in this OBPI").
- *Default to heavy on missing temperature:* Rejected — REQ-2 mandates fail-closed with no silent default to heavy.
- *Change pipeline.py:* Rejected — explicitly in Denied Paths.

## Goals

Declare per-vendor temperatures in `data/vendor-manifest.json` so:
- Codex renders `AgentContract` at `lite` (258K-window relief, GHI #519)
- Claude renders `AgentContract` at `heavy` (current behavior made explicit)
- Unknown/missing per-vendor temperature fails closed — no silent default
- `gz validate --vendor-manifest` enforces the declaration via the schema

## Files

| Path | Change | Purpose |
|------|--------|---------|
| `tests/content/test_vendor_manifest.py` | Extend | RED: add `TestPerVendorTemperatureRouting` for REQs 01–06 |
| `src/gzkit/schemas/vendor_manifest.json` | Extend | Add `content_type_temperatures` optional property, `temperature` enum `{lite,medium,heavy}` |
| `data/vendor-manifest.json` | Extend | Add `content_type_temperatures`; add `codex` to `AgentContract` routes |
| `src/gzkit/content/vendors.py` | Extend | Add `temperature_for()`; update `_FALLBACK_ROUTES`; add `_FALLBACK_TEMPERATURES` |
| `src/gzkit/content/templates/agentcontract/codex.md.j2` | Create | Codex vendor template (same structure as `claude.md.j2`) |
| `src/gzkit/sync_surfaces.py` | Edit (call sites only) | `sync_agents_md`: un-hardcode temperature; `render_content_surface`: add `temperature` param |
| `features/constitutional_invariants.feature` | Extend | BDD scenarios tagged `@REQ-0.0.37-15-*` |
| `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-15-per-vendor-template-selection.md` | Update | Brief evidence sections |

## Steps

### Step 1: RED — Write failing tests

Add `TestPerVendorTemperatureRouting` to `tests/content/test_vendor_manifest.py`:

- `test_temperature_for_resolves_from_manifest` — `@covers("REQ-0.0.37-15-01")`: write a manifest with temperatures, call `temperature_for("AgentContract", "claude", project_root=root)`, assert returns `"heavy"`.
- `test_codex_resolves_to_lite` — `@covers("REQ-0.0.37-15-02")`: manifest with codex→lite; assert `temperature_for("AgentContract", "codex", ...)` == `"lite"`.
- `test_missing_vendor_temperature_fails_closed` — `@covers("REQ-0.0.37-15-02")`: manifest with no temperatures declared for vendor; assert `temperature_for(...)` raises `ValueError`.
- `test_codex_lite_contains_all_judgment_bullets` — `@covers("REQ-0.0.37-15-03")`: build `AgentContract` with one Judgment bullet (`classification="Judgment"`) and one Mechanical/heavy bullet (`density_min="heavy"`); render at codex/lite; assert Judgment text present, Mechanical/heavy text absent.
- `test_codex_and_claude_renders_differ` — `@covers("REQ-0.0.37-15-04")`: render same model at codex/lite and claude/heavy; assert bytes differ.
- `test_manifest_declares_temperatures` — `@covers("REQ-0.0.37-15-05")`: read canonical `data/vendor-manifest.json`; assert `content_type_temperatures` key present; assert `validate_vendor_manifest` returns no errors.
- `test_content_type_routes_unchanged_shape` — `@covers("REQ-0.0.37-15-06")`: `content_type_routes` still `dict[str, list[str]]`; `content_type_temperatures` is the sibling.
- `test_schema_rejects_out_of_enum_temperature` — `@covers("REQ-0.0.37-15-06")`: build manifest with `temperature: "extra-hot"`; assert `validate_vendor_manifest` returns errors.

Run: `uv run -m unittest tests.content.test_vendor_manifest -v` → expect FAIL on the new tests.

### Step 2: Extend vendor manifest schema

In `src/gzkit/schemas/vendor_manifest.json`, add `content_type_temperatures` as an optional property:

```json
"content_type_temperatures": {
  "type": "object",
  "description": "Per-vendor temperature for each content type.",
  "additionalProperties": {
    "type": "object",
    "additionalProperties": {
      "type": "string",
      "enum": ["lite", "medium", "heavy"]
    }
  }
}
```

Remove `additionalProperties: false` restriction on the top-level object so the new sibling is accepted (or add it to `properties`).

### Step 3: Update data/vendor-manifest.json

Add `codex` to `content_type_routes.AgentContract` (additive, shape unchanged):

```json
"content_type_routes": {
  "AgentContract": ["claude", "codex"],
  ...
}
```

Add the `content_type_temperatures` sibling block:

```json
"content_type_temperatures": {
  "AgentContract": {"codex": "lite", "claude": "heavy"}
}
```

Run `uv run gz validate --vendor-manifest` → should pass.

### Step 4: Add temperature_for to vendors.py

In `src/gzkit/content/vendors.py`:

- Update `_FALLBACK_ROUTES["AgentContract"]` to `["claude", "codex"]`.
- Add `_FALLBACK_TEMPERATURES: dict[str, dict[str, str]]` with `{"AgentContract": {"codex": "lite", "claude": "heavy"}}`.
- Add private `_load_temperatures(project_root: Path) -> dict[str, dict[str, str]]` (analogous to `_load_manifest`; reads `content_type_temperatures` from the manifest file; returns `{}` on missing/malformed — fail-closed is in `temperature_for`).
- Add public `temperature_for(content_type: str, vendor: str, *, project_root: Path | None = None) -> str`:
  - When `project_root` is supplied: load temperatures, look up `content_type` then `vendor`.
  - Falls back to `_FALLBACK_TEMPERATURES` when no project_root.
  - Raises `ValueError` when no entry found (fail-closed — no default to heavy).

### Step 5: Add codex.md.j2 template

Create `src/gzkit/content/templates/agentcontract/codex.md.j2` — identical content to `claude.md.j2`. Temperature projection happens before template rendering; the template shape is vendor-neutral at this tier.

### Step 6: Update sync_surfaces.py call sites (two sites only)

**`sync_agents_md` (line 366):**
- Add import: `from gzkit.content.vendors import temperature_for` (lazy inside function — follows the existing lazy pattern for `_parse_content`).
- Replace `temperature="heavy"` with `temperature=temperature_for("AgentContract", "claude", project_root=project_root)`.

**`render_content_surface` (line 552):**
- Add `temperature: str = "heavy"` parameter.
- Pass `temperature=temperature` to `render_content_model(model, vendor, temperature=temperature)`.

No other edits to this module.

### Step 7: GREEN — Run tests and quality checks

```bash
uv run -m unittest tests.content.test_vendor_manifest -v
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --vendor-manifest
```

All REQ-0.0.37-15-* tests must pass.

### Step 8: Add BDD scenarios

In `features/constitutional_invariants.feature`, add:

```gherkin
@REQ-0.0.37-15-01
Scenario: temperature_for resolves per-vendor temperature from manifest
  Given a vendor manifest declaring AgentContract temperatures codex=lite, claude=heavy
  When temperature_for is called for AgentContract and claude
  Then the resolved temperature is heavy

@REQ-0.0.37-15-02
Scenario: missing per-vendor temperature fails closed
  Given a vendor manifest with no temperature declared for a vendor
  When temperature_for is called for that vendor
  Then a ValueError is raised (no silent default)

@REQ-0.0.37-15-03
Scenario: Codex lite mirror contains all Judgment bullets
  Given an AgentContract model with a Judgment bullet and a heavy Mechanical bullet
  When the contract is rendered at codex lite temperature
  Then the Judgment bullet is present and the heavy bullet is absent

@REQ-0.0.37-15-04
Scenario: Codex and Claude AgentContract renders differ
  Given an AgentContract model with bullets at multiple densities
  When rendered for codex at lite and for claude at heavy
  Then the output bytes differ
```

### Step 9: Full validation pass

```bash
uv run gz validate --documents
uv run gz validate --vendor-manifest
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.content.test_vendor_manifest -v
uv run mkdocs build --strict
```

### Step 10: Present OBPI Acceptance Ceremony

Stage 4 of the pipeline — present evidence table and await human attestation.

## Verification

All commands from the brief's Verification section:

```bash
uv run gz validate --documents
uv run gz validate --vendor-manifest
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.content.test_vendor_manifest -v
```

## Notes

- `content_type_routes.AgentContract` changes from `["claude"]` to `["claude", "codex"]` — additive; `dict[str, list[str]]` shape preserved per REQ-6.
- `_FALLBACK_ROUTES` and `_FALLBACK_TEMPERATURES` in vendors.py mirror the manifest per the "update both surfaces together" note in the file.
- `codex.md.j2` is structurally identical to `claude.md.j2` at this stage — temperature differences manifest via model projection before template rendering.
- No changes to `pipeline.py` (Denied Paths); no harness/model detection (REQ-5 NEVER).
- The `render_content_surface` function currently has no callers; the signature change is additive and future-facing.
