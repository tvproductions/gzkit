# Plan: OBPI-0.0.37-27-migration-disposition-doctrine-refresh-orientation-index — Migration/Disposition + Doctrine Refresh + Orientation Index

**OBPI:** OBPI-0.0.37-27-migration-disposition-doctrine-refresh-orientation-index
**ADR:** ADR-0.0.37-constitutional-invariant-composition (Checklist item #27)
**Lane:** Heavy
**Status:** Ready for implementation (B.1, sequence 3 of 3 — capstone; takes ADR-0.0.37 closeout-ready)

## Context

The capstone disposition of the 2026-06-03 re-alignment: retire the proven-inert density-dial
mechanism and refresh doctrine to match the landed corpus→compress→rendition→playback pipeline.
On completion this OBPI checks the ADR-0.0.37 closeout box → the ADR closeout ceremony (→ Validated)
is the B.1 exit gate.

## Booked guardrail (correctness, not a decision)

- **REQ-27-02 "render output unchanged" is PROVEN by a RED byte-parity test first, not presumed.**
  `_project_for_temperature` does TWO things: (a) `Bullet.density_min` filtering — empirically inert;
  (b) `Pillar.enabled` / `Pillar.tier` filtering — possibly NOT inert. Removing the function wholesale
  could let disabled/tier-gated pillars leak into render output. Before removal, write a test asserting
  `render()` is byte-identical before/after across the real corpus, AND trace `render()` callers
  (OBPI-22 playback may already make this path dead for AGENTS.md). **If a live pillar is disabled/
  tier-gated, narrow the removal to the `_bullet_renders` half and KEEP the pillar-filter half.**

## Discovery-grounded removal/coupling map

- **`bullet.py`:** `density_min: _Temperature | None` (lines 27–29) + `_enforce_judgment_floor`
  after-validator (lines 31–41); coupled only to `classification` within the model.
- **`render/pipeline.py`:** `_TEMP_RANK` (23), `_bullet_renders` (26–34), `_project_for_temperature`
  (37–48); **zero external callers/imports**; `render()` calls `_project_for_temperature` at line 123.
  (Pillar.tier filtering lives INSIDE `_project_for_temperature` — see guardrail above.)
- **`sync_surfaces.py`:** `render_template("agents")` appears **once** (line 393, the bootstrap-2
  monolith fallback). `claude`/`copilot` calls (407/422) stay. `sync_agents_md` (352–395) already
  reads the committed-rendition store first (OBPI-22 repoint); this retires the residual fallback.
- **Tests touching the removed symbols:** `tests/content/models/test_fields.py`
  (`TestDensityBulletFields` — drop class), `test_round_trip_agent_contract.py`
  (`test_reconcile_assigns_lite_density_min` — drop), `test_vendor_manifest.py` (drop `density_min`
  from fixtures; KEEP per-vendor routing tests — different surface), `test_byte_stability.py`
  (drop `density_min` from fixtures; KEEP temperature param), `test_render_pipeline.py`
  (`TestTemperatureRenderer` — drop; KEEP `TestRenderPipeline` lines 22–68).
- **Substrate doc:** `docs/governance/agent-control-surface-rendering-substrate.md` currently frames
  density-dial / three-static-template; NO Agent Orientation Index section exists yet (new). The
  "nothing hand-authored at the rendered location" binding claim (line ~9) stays load-bearing.
- **Non-inert lookalikes to PRESERVE:** `Pillar.tier` (section-level filtering) and the per-vendor
  temperature routing (`data/vendor-manifest.json` → `vendors.temperature_for()`) — both separate
  from `Bullet.density_min`; the brief denies touching the corpus model / composer / rendition store.

## Files

### Edits (no files created)

- `src/gzkit/content/models/bullet.py` — remove `density_min` + `_enforce_judgment_floor`
- `src/gzkit/content/render/pipeline.py` — remove `_bullet_renders` (+ `_project_for_temperature` /
  `_TEMP_RANK` PENDING the byte-parity guardrail; narrow if pillar-filter is live)
- `src/gzkit/sync_surfaces.py` — retire the `render_template("agents")` monolith fallback
- `tests/content/models/test_fields.py`, `tests/content/test_byte_stability.py`,
  `tests/content/test_render_pipeline.py`, `tests/content/test_round_trip_agent_contract.py`,
  `tests/content/test_vendor_manifest.py` — drop/adjust per the coupling map
- `docs/governance/agent-control-surface-rendering-substrate.md` — refresh mechanism (retire
  density-dial framing; document corpus→compress→rendition→playback + invariant tier) + ADD the
  Agent Orientation Index (surface→model→doctrine→load-command map; "do not re-derive from source")
- `docs/governance/return-to-health-plan-2026-05-30.md` — refresh worklist + #519 relief route (18–27 active)
- `docs/design/adr/.../ADR-0.0.37-constitutional-invariant-composition.md` — finalize checklist
  disposition (confirm 09 + 11–17 withdrawn; 18–27 active) + check item #27 at closeout
- `data/behave_coverage_waivers.json` — OBPI-level behave waiver (no new verb)
- (brief evidence record as usual)

## Steps (TDD-ordered)

### Step 0 — Brief reconcile + seam check
`uv run gz validate --brief-reconcile`. Confirm OBPI-22 (rendition store/playback) + OBPI-23
(invariant tier) landed (this disposition removes the OLD path only after the NEW one is in place).

### Step 1 — RED byte-parity guardrail (REQ-27-02 precondition)
Write the before/after byte-parity assertion + trace `render()` callers. Determine the removal scope
(full `_project_for_temperature` vs `_bullet_renders`-only). Record the finding in the brief evidence.

### Step 2 — Remove `density_min` + validator (REQ-01)
Drop the field + `_enforce_judgment_floor`; update `test_fields.py` / `test_round_trip_*` and strip
`density_min` from `test_vendor_manifest` / `test_byte_stability` fixtures. Model round-trip + byte-
stability tests pass without `density_min` (0-Kelvin floor now lives in corpus `tier: invariant`, OBPI-23).

### Step 3 — Remove the temperature filter (REQ-02)
Per Step-1 scope: remove `_bullet_renders` (+ `_project_for_temperature`/`_TEMP_RANK` iff proven inert);
drop `TestTemperatureRenderer`; assert render output unchanged. Keep `TestRenderPipeline`.

### Step 4 — Retire the monolith sync fallback (REQ-03)
Remove `render_template("agents")` (sync_surfaces.py:393) so `sync_agents_md` reads only the
committed-rendition store. `@covers` assertion + the grep check:
`grep -RIn 'render_template("agents")' src/gzkit/` → none.

### Step 5 — Doctrine refresh + Orientation Index (REQ-04, REQ-05)
Refresh the substrate doc to the corpus→compress→rendition→playback + invariant-tier mechanism; add
the Agent Orientation Index (folds OBPI-16 intent). Coordinate with OBPI-23's invariant-tier subsection.

### Step 6 — Disposition finalize (REQ-06)
Refresh `return-to-health-plan-2026-05-30.md` (18–27 active; #519 route) + finalize the ADR-0.0.37
checklist disposition; check item #27 at closeout.

## Verification (canonical, arb-wrapped)

```bash
uv run gz validate --brief-reconcile
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.content.test_render_pipeline tests.content.test_round_trip_agent_contract tests.content.models.test_fields -v
uv run gz covers OBPI-0.0.37-27-migration-disposition-doctrine-refresh-orientation-index --json
uv run gz validate --documents --invariant-coherence
uv run mkdocs build --strict
uv run python -c "from gzkit.content.models.bullet import Bullet; assert 'density_min' not in Bullet.model_fields; print('density_min removed')"
uv run gz agent sync control-surfaces && git diff --stat AGENTS.md   # playback unchanged
```

## Notes / risks

- **Removal-scope correctness** is the only real risk — handled by the Step-1 byte-parity guardrail.
  This OBPI is otherwise mechanical (zero external coupling for the filter; single fallback call site).
- **Surgical** (DO IT RIGHT 11): remove only the inert code; do not refactor adjacent rendering, the
  corpus model, the composer, the rendition store, or the playback templates.
- **Capstone:** completion takes ADR-0.0.37 to closeout-ready → ADR closeout ceremony (→ Validated)
  is the B.1 exit. Closing #519 (B.2) and the rendered-AGENTS.md playback (B.3) follow.
- **Gate 5** (Heavy/foundation, no self-close): attest the disposition.
