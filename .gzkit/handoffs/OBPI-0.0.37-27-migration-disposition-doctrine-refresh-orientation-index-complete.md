---
mode: CREATE
adr_id: ADR-0.0.37
branch: main
timestamp: "2026-06-15T23:40:00+00:00"
agent: claude-code
obpi_id: OBPI-0.0.37-27-migration-disposition-doctrine-refresh-orientation-index
session_id: main-2026-06-15
last_lock_event_timestamp: "2026-06-15T23:00:52.540070+00:00"
last_commit_sha: f0c442111bbebe4b88777c1ff50a83077f0eb87e
---

# OBPI-0.0.37-27 Handoff — Migration/Disposition + Doctrine Refresh + Orientation Index (complete)

## Current State Summary

OBPI-0.0.37-27 is **completed and operator-attested** ("attest completed", g0, 2026-06-15; foundation/heavy, operator-verbatim conversational Gate-5). The capstone disposition of the 2026-06-03 re-alignment landed: the proven-inert density-dial mechanism is retired (Bullet.density_min field + `_enforce_judgment_floor` validator + `_project_for_temperature`/`_bullet_renders` render filter + coupled `invariants.py` kwarg / dead JSON-schema property), the residual monolith `render_template("agents")` sync fallback is retired (sync now routes every bootstrap path through the deterministic model pipeline), the substrate doctrine is refreshed to corpus→compress→rendition→playback + invariant-tier with a new Agent Orientation Index, and the items-18-27-active / 09+11-17-withdrawn disposition is recorded on the active build-to-1.0-campaign. Branch `main`, even with origin/main; governance edits (brief Completed status, ADR-level audit ledger, completion receipt) pending git-sync #1.

## Important Context

Removal was guarded by a byte-parity proof: `render()` WITH vs WITHOUT the projection filter = 28176 B identical on the real AGENTS.md model (all 20 pillars enabled, tier=lite, already ordered), so wholesale filter removal is byte-safe. AGENTS.md playback verified unchanged post-removal (empty `git diff` after `gz agent sync control-surfaces`). The `temperature` parameter survives on `render()` for per-vendor routing parity (`vendors.temperature_for`) but no longer projects the model.

## Decisions Made

- **Full-removal scope confirmed** (not narrow): the byte-parity guardrail proved `_project_for_temperature` (density filter + pillar enabled/tier filter + order sort) inert for the real corpus, sanctioning wholesale removal per REQ-27-02.
- **Two operator-approved allowlist amendments via the Gate Friction loop:** added the density_min-coupled surfaces `src/gzkit/governance/invariants.py` + `src/gzkit/schemas/constitutional_invariant.json` (Stage 2); added `tests/commands/test_sync_cmds.py` + `.gzkit/insights/agent-insights.jsonl` (Stage 5 reconcile).
- **REQ-06 operator-redirect:** the brief's `return-to-health-plan-2026-05-30.md` target was frozen "retained unmodified for audit" on 2026-06-10 (after this 2026-06-03 brief) and already states 18-27 active; the disposition refresh was redirected to the active `build-to-1.0-campaign-2026-06-10.md`.
- **Sibling-REQ test rework (operator-ratified):** `test_codex_and_claude_renders_differ` (REQ-0.0.37-15-04) asserted differentiation delivered solely by the (now-retired) temperature dial — the two `.j2` templates are byte-identical. At operator prompting it was retightened to assert temperature-inertness-PER-VENDOR (`render(codex, lite) == render(codex, heavy)`), NOT cross-harness byte-identity, leaving per-harness behavioral tuning an open, undesigned design space.
- **Completion reconcile override (operator-approved):** 6 `missing_in_brief` allowlist deltas were read-only `@covers`/registry test imports (traceability.py, tasks.py, config.py, two `__init__.py`, agent_contract.py), each verified UNMODIFIED via git; completed with `--accept-stale-reconciliation` + documented reason rather than polluting the write-allowlist with read-only imports.

## Immediate Next Steps

- Release the OBPI lock (this handoff is the register entry that unblocks it).
- Git-sync #1 (commit governance edits), `gz obpi reconcile`, `gz adr status ADR-0.0.37`, git-sync #2.
- **ADR-0.0.37 closeout:** this OBPI is the capstone ("sequence 3 of 3", takes the ADR to closeout-ready). The ADR closeout ceremony checks item #27's box and runs Gate-5 ADR attestation. The ADR-file checklist box is a closeout-ceremony edit, not this OBPI's.

## Pending Work / Open Loops

- **ADR-0.0.37 closeout-ready** (Magna Carta campaign B.1). Verify remaining active OBPIs (01–10, 18–27) status via `gz adr report ADR-0.0.37` before launching the closeout ceremony; #27 was the capstone disposition.
- **#519 (sole open emergency)** remains open — closed by B.2 (registry-projected <15k surface, GHI #533), not this OBPI.
- Per-harness behavioral tuning (codex vs claude rendition divergence) is an explicitly-undesigned space surfaced this session; no action queued.

## Verification Checklist

- Full unittest 6170/6170 (`arb-step-unittest-df7824927c664f9b834875edb5d9a568`)
- Lint (`arb-ruff-87c0389a14a647a49747af0eab315e3f`), typecheck (`arb-step-typecheck-354c407751cc4cea80fe455efd85d750`), mkdocs --strict (`arb-step-mkdocs-7c996eccbeb746f78394d9aae2c3b6cb`) all exit 0
- `gz validate --documents / --invariant-coherence / --cli-alignment / --brief-reconcile` clean
- `gz covers` behavior_uncovered_reqs=0; AGENTS.md playback byte-unchanged; monolith grep clean; `density_min` removed

## Evidence / Artifacts

- Code: `src/gzkit/content/models/bullet.py`, `src/gzkit/content/render/pipeline.py`, `src/gzkit/governance/invariants.py`, `src/gzkit/schemas/constitutional_invariant.json`, `src/gzkit/sync_surfaces.py`
- Tests: `tests/content/{models/test_fields,test_render_pipeline,test_round_trip_agent_contract,test_byte_stability,test_vendor_manifest}.py`, `tests/commands/test_sync_cmds.py`
- Docs/data: `docs/governance/agent-control-surface-rendering-substrate.md` (mechanism refresh + Agent Orientation Index), `docs/governance/build-to-1.0-campaign-2026-06-10.md` (disposition), `data/behave_coverage_waivers.json`
- Completion receipt + ADR-level audit ledger entry for OBPI-0.0.37-27 (attested_completed)
