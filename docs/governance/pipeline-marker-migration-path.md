<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Pipeline Marker Migration Path — From Layer 3 to Layer 2

**Source ADR:** [ADR-0.0.9 — State Doctrine and Source-of-Truth Hierarchy](../design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md)

**Related:** [State Doctrine — Three-Layer Model](state-doctrine.md) | [ADR-0.13.0 — OBPI Pipeline Runtime Surface](../design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md)

**Purpose:** Define how pipeline markers migrate from Layer 3 (derived state) to Layer 2 (ledger events), the ledger event types that replace them, and when migration begins.

---

## Current State: Markers as Layer 3

Pipeline markers are JSON files managed by `src/gzkit/pipeline_markers.py`. They track which OBPI pipeline is active and what stage it has reached.

### Marker Files

| File | Purpose |
|------|---------|
| `.claude/plans/.pipeline-active-{OBPI-ID}.json` | Per-OBPI active pipeline state |
| `.claude/plans/.pipeline-active.json` | Legacy compatibility marker (same payload) |

### Marker Payload

Each marker records:

- `obpi_id`, `parent_adr`, `lane` — identity
- `current_stage` — which pipeline stage is active (implement, verify, ceremony, sync)
- `execution_mode` — normal or exception
- `started_at`, `updated_at` — timestamps
- `receipt_state` — plan-audit receipt verdict
- `blockers` — active blockers preventing stage progression
- `required_human_action` — what the operator must do before the pipeline can continue
- `next_command`, `resume_point` — the canonical next step

### Layer 3 Characteristics

Pipeline markers exhibit all Layer 3 properties defined in the [State Doctrine](state-doctrine.md):

- **Ephemeral:** Delete all markers and no governance state is lost. The pipeline can be re-entered from any stage.
- **Rebuildable:** Given the ledger and brief state, the current pipeline position can be inferred.
- **Cannot block gates:** Markers are used for runtime coordination (hooks, resume hints), not as gate evidence.
- **Stale-prone:** Markers can become orphaned when a session is interrupted. `clear_stale_pipeline_markers()` cleans them up.

---

## Target State: Stage Transitions as Layer 2 Events

After migration, the ledger records stage transitions as first-class events. Markers become a pure rebuildable cache — a convenience layer rebuilt from ledger events on demand.

### Ledger Event Types for Stage Transitions

The following event types will replace marker state:

| Event Type | Replaces | Payload |
|------------|----------|---------|
| `pipeline-started` | Marker creation | `obpi_id`, `parent_adr`, `lane`, `execution_mode`, `entry_point` |
| `pipeline-stage-entered` | `current_stage` field updates | `obpi_id`, `stage` (implement, verify, ceremony, sync), `timestamp` |
| `pipeline-stage-completed` | Implicit (next stage entered) | `obpi_id`, `stage`, `outcome` (passed, failed, skipped), `evidence` |
| `pipeline-blocked` | `blockers` field | `obpi_id`, `stage`, `blocker_reason`, `required_action` |
| `pipeline-resumed` | Marker re-read after session restart | `obpi_id`, `resume_stage`, `previous_session` |
| `pipeline-aborted` | Marker deletion on abort | `obpi_id`, `stage`, `abort_reason`, `handoff_created` |
| `pipeline-completed` | Marker deletion on success | `obpi_id`, `final_stage`, `sync_commit` |

### Event Authority

After migration, the ledger event stream is the authoritative record for:

- Whether a pipeline is active for an OBPI
- Which stage the pipeline has reached
- Why a pipeline was blocked or aborted
- Whether a pipeline completed successfully

This follows Rule 1 of the State Doctrine: the ledger is authoritative for all runtime status.

### Marker Role After Migration

After migration, markers become a **pure rebuildable cache**:

- **Rebuild command:** `uv run gz state --repair` regenerates markers from the latest ledger events for any active pipeline.
- **Purpose:** Markers continue to exist for fast local reads by hooks and the pipeline runtime. Reading the full ledger to determine active pipeline state on every hook invocation would be too slow.
- **Deletable without data loss:** Delete all `.claude/plans/.pipeline-active*.json` files. Run `gz state --repair`. All active pipeline state reconstructs from ledger events. No stage history is lost because every transition was recorded in L2.
- **No behavioral change on deletion:** If a marker is missing but the ledger shows an active pipeline, the runtime rebuilds the marker before proceeding. If the ledger shows no active pipeline, the absence of a marker is correct.

---

## What Changes and What Stays the Same

### Changes

| Before (L3-only) | After (L2 + L3 cache) |
|---|---|
| Stage transitions update marker JSON | Stage transitions emit ledger events AND update marker cache |
| Interrupted session loses stage context | Ledger preserves full stage history; sessions resume from ledger truth |
| Stale markers require TTL-based cleanup | Stale markers are detectable by comparing against ledger events |
| `pipeline_markers.py` is the sole write path | `pipeline_markers.py` writes cache; a new ledger emitter writes L2 events |
| Hook reads marker to decide if pipeline is active | Hook reads marker (fast path) with ledger fallback (authoritative path) |

### Stays the Same

- The pipeline skill (`gz-obpi-pipeline`) orchestrates the same 5-stage sequence.
- The pipeline runtime (`pipeline_runtime.py`) remains the canonical engine.
- Hooks (`pipeline-gate.py`) continue reading markers for fast-path decisions.
- The human attestation gate at Stage 4 (Normal mode) is unchanged.
- Exception mode concurrent execution is unchanged.

---

## Migration Vehicle

**[ADR-0.13.0 — OBPI Pipeline Runtime Surface](../design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md)** is the vehicle for this migration.

ADR-0.13.0 elevates the pipeline from a skill-only workflow into a first-class runtime surface. Its scope includes:

- Persisting pipeline stage state in a repository-local, machine-readable form
- Exposing structured stage outputs for current stage, blockers, required human action, and next command

The marker-to-ledger migration is a natural extension of this work: "repository-local, machine-readable form" becomes ledger events (L2) rather than marker files (L3). The structured stage outputs remain available — they are simply derived from ledger events instead of being the primary storage.

### Migration Scope Within ADR-0.13.0

The following ADR-0.13.0 OBPIs will carry the migration work:

1. **Ledger event schema** — Define the `pipeline-*` event types and validate them against the existing ledger schema.
2. **Dual-write phase** — `pipeline_markers.py` writes both ledger events and marker files. Existing hooks continue reading markers (no behavioral change during migration).
3. **Ledger-authoritative phase** — Hooks fall back to ledger reads when markers are absent. Markers are rebuilt from ledger on `gz state --repair`.
4. **Marker cache phase** — Markers are documented as pure cache. `clear_stale_pipeline_markers()` compares against ledger truth instead of TTL heuristics.

---

## Timeline and Trigger

### Trigger Condition

Migration begins when **ADR-0.13.0 enters active implementation** (status changes from `Proposed` to `In Progress`).

### Prerequisites

Before migration can start:

1. **ADR-0.0.9 complete** — The State Doctrine must be fully ratified so the three-layer model and authority rules are locked. In-progress state doctrine work creates a moving target for migration design.
2. **Ledger schema supports pipeline events** — The global ledger schema (`.gzkit/ledger.jsonl`) must accept `pipeline-*` event types without validation failures.
3. **`gz state --repair` exists** — The force-reconciliation command from OBPI-0.0.9-03 must be implemented so markers can be rebuilt from ledger events during migration.

### Phases

| Phase | Description | Duration | Exit Criteria |
|-------|-------------|----------|---------------|
| **1. Schema** | Define `pipeline-*` event types; add to ledger schema | 1 OBPI | Schema validates all event types |
| **2. Dual-write** | Emit ledger events alongside marker writes; no read-path changes | 1 OBPI | Ledger events appear for all stage transitions |
| **3. Ledger-authoritative** | Hooks and runtime read ledger when markers are absent; `gz state --repair` rebuilds markers | 1-2 OBPIs | Deleting all markers and running repair produces correct state |
| **4. Cache-only** | Markers documented as pure cache; stale detection uses ledger comparison | 1 OBPI | Stale marker cleanup no longer uses TTL heuristics |

### Post-Migration State

After all four phases complete:

- Pipeline markers are **deletable without data loss** — they are pure cache rebuilt from L2
- Every stage transition is **auditable** — the ledger records who, when, and why
- Session interruptions are **recoverable** — the ledger preserves full stage history
- The pipeline runtime has **one source of truth** — the ledger, not a collection of JSON files

---

## Verification

To confirm migration is complete, the following must hold:

```bash
# 1. Delete all pipeline markers
rm -f .claude/plans/.pipeline-active*.json

# 2. Rebuild from ledger
uv run gz state --repair

# 3. Verify markers match ledger-derived state
uv run gz state --json | jq '.pipeline'
# Should show active pipeline state if one exists, empty otherwise

# 4. Run a full pipeline cycle and confirm ledger events
uv run gz obpi pipeline OBPI-X.Y.Z-NN --from=verify
# Ledger should contain pipeline-started, pipeline-stage-entered, etc.
```

---

## References

- [State Doctrine — Three-Layer Model](state-doctrine.md) — Layer definitions and authority rules
- [ADR-0.0.9 — State Doctrine](../design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md) — Parent ADR
- [ADR-0.13.0 — OBPI Pipeline Runtime Surface](../design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md) — Migration vehicle
- `src/gzkit/pipeline_markers.py` — Current marker implementation
- `src/gzkit/pipeline_runtime.py` — Pipeline runtime engine
