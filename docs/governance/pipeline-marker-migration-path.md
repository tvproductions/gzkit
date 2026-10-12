<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Pipeline Marker Migration Path — From Layer 3 to Layer 2

**Source ADR:** [ADR-0.0.9 — State Doctrine and Source-of-Truth Hierarchy](../design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md)

**Related:** [State Doctrine — Three-Layer Model](state-doctrine.md) | [ADR-0.13.0 — OBPI Pipeline Runtime Surface](../design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md)

**Purpose:** State where a pipeline run's stage and position are recorded on the ledger (Layer 2), how the pipeline markers (Layer 3) are written from that record, and how a deleted marker is rebuilt from it.

**Status:** Ruled and built. This document was written under `OBPI-0.0.9-06` as a plan for a future migration. The operator ruled the Layer-2 source and the rebuilding verb on 2026-10-04, and `OBPI-0.35.0-15-pipeline-run-position` built them. The sections below describe the runtime as it is; [What the first plan proposed](#what-the-first-plan-proposed) records where the built design departs from that plan. Dates in this document are records of when a ruling was made.

---

## The Ruling

`ADR-0.0.9` deferred "ledger events for stage transitions" to a later ADR. The question was put to the operator in the `OBPI-0.35.0-15` brief as Open Design Question 2, with three options: infer position from events the ledger already held, append one transition event per recorded boundary, or mix the two. Ruled 2026-10-04:

- **Each recorded boundary appends one stage-transition event to the ledger before the marker is written.** A position is declared, never inferred from another event's side effect.
- **`uv run gz state --repair` rebuilds a missing or deleted marker from those events.** Nothing else rebuilds one.
- **No second state file.** Position lives in the two existing marker files, and the ledger is the system of record (Open Design Question 3).

`OBPI-0.35.0-15` is Decision item 11 of `ADR-0.35.0`, a repair assignment against `ADR-0.13.0` (GHI #1172). Later rulings on that brief, made on 2026-10-11 and 2026-10-12, fixed which boundaries move the stage, where a run ends and what the repair declines; they are carried in the sections below.

---

## Markers Are Layer 3

Pipeline markers are JSON files written by `src/gzkit/pipeline_markers.py`. They record which OBPI pipeline is active and what the run has reached.

### Marker Files

| File | Purpose |
|------|---------|
| `.claude/plans/.pipeline-active-{OBPI-ID}.json` | Per-OBPI active pipeline state |
| `.claude/plans/.pipeline-active.json` | Legacy compatibility marker (same payload); one file for the whole project, naming the run launched last |

### Marker Payload

Each marker records:

- `obpi_id`, `parent_adr`, `lane` — identity
- `entry` — how the run was launched (full, verify, ceremony, sync)
- `nonce` — pairs the marker with its `pipeline_launched` ledger event
- `current_stage` — the stage the run has reached (implement, verify, ceremony, sync)
- `position` — the last recorded boundary the run crossed inside that stage: `kind`, `label` and `boundary`. Absent until a boundary is recorded after the launch
- `execution_mode` — the launcher's constant, `normal`
- `started_at`, `updated_at` — the time of the launch and the time of the last recorded boundary
- `receipt_state` — plan-audit receipt verdict
- `blockers` — what the last failed verification found
- `required_human_action` — what the operator must do before the pipeline can continue
- `next_command`, `resume_point` — the canonical next step for the stage reached
- `dispatch_state`, `single_driver_declaration` — optional caches of dispatch records the ledger holds

### Layer 3 Characteristics

Pipeline markers have the Layer 3 properties defined in the [State Doctrine](state-doctrine.md):

- **Ephemeral:** Delete both markers and no governance state is lost. The stage and position are on the ledger.
- **Rebuildable:** `uv run gz state --repair` writes them back from the ledger. See [The Rebuild](#the-rebuild) for what it restores and what it declines.
- **Cannot block gates:** No gate reads a position. A missing or wrong position may warn and never fails a check closed. Stage 2 dispatch credit and the single-driver declaration are read from the ledger, never from the marker's caches.
- **Stale-prone:** A marker can be orphaned when a session is interrupted. Stale detection reads the marker's own `updated_at` against `STALE_MARKER_HOURS` (`find_stale_pipeline_markers` in `src/gzkit/pipeline_markers.py`); `clear_stale_pipeline_markers()` removes what it finds.

---

## The Layer 2 Source

Two ledger event types carry a run's stage and position. The run-position concept lives in one module, `src/gzkit/pipeline_position.py`, which reads and appends through the ledger it is handed and leaves every marker file write to `src/gzkit/pipeline_markers.py`.

| Event type | Appended by | Payload |
|------------|-------------|---------|
| `pipeline_launched` | `gz obpi pipeline`, on a full launch and on each `--from` entry | `id` (the OBPI), `parent`, `lane`, `nonce`, `marker_path`, `entry` |
| `pipeline_stage_transition` | The command that marks a recorded boundary | `id` (the OBPI), `parent`, `stage` (implement, verify, ceremony, sync), `position_kind` (task, phase, round, step), `position_label`, `boundary` (the command), and `blockers` when a verification result set any |

### Order of Writes

Ledger first, marker second. `record_position` appends the `pipeline_stage_transition` event, replays the ledger, and only then advances both marker files to what the replay says. A marker therefore never holds a position the ledger lacks, and its `updated_at` is the event's own time.

### Which Boundaries Are Recorded

The set is `RULED_BOUNDARIES` in `src/gzkit/pipeline_position.py`. It is the one place that says which boundaries move the stage.

- **A command that begins a stage's work moves the stage:** `gz obpi dispatch` and `gz task start` (to `implement`), the verify stage of `gz obpi pipeline` (to `verify`), the ceremony stage of `gz obpi pipeline` and `gz obpi present-evidence` (to `ceremony`), and `gz obpi complete` (to `sync`). A launch moves it too, through its `pipeline_launched` event.
- **A check or a bookkeeping event records in place:** `gz task complete`, `gz task block`, `gz task escalate`, a verification pass or fail, `gz obpi precomplete`, `gz obpi verify-packet`, and an adversarial or human review recorded through `gz obpi acceptance`. Its stage is the one the ledger replay says the run has reached.
- **Not recorded:** a spec or quality review recorded through `gz obpi acceptance`, and `gz obpi sync`, which runs after the receipt that ends the run.

The operator-facing tables are in [`gz obpi pipeline`](../user/manpages/obpi-pipeline.md#where-the-run-is-stage-and-position).

### When a Run Is in Flight

A run is in flight from its latest `pipeline_launched` event until an event that ends it follows under an id whose current name is the current name of the launch's id: an `obpi_receipt_emitted` event whose `receipt_event` is `completed`, or an `obpi_parked`, `obpi_withdrawn` or `obpi_superseded` event. An id's current name is the id taken through the ledger's `artifact_renamed` rows by the ledger's one fold (`fold_renames` in `src/gzkit/obpi_lifecycle.py`), and an id never renamed is its own current name, so a rename ends no run and a rename that is later reversed leaves both ids with the one name the OBPI has. A later launch under an id with that current name starts a new run in its place. The marker is not consulted for this, so a deleted marker drops no crossing and a stale one invents no run. A boundary is recorded only for a run in flight, and the rebuild considers exactly the same runs (`_launches_in_flight`).

A `pipeline_launched` event with the entry `audit`, which `gz adr audit-begin` writes under an ADR's id, starts no pipeline run.

### Reading Position Back

`replay_pipeline_position` takes the latest `pipeline_launched` event for the OBPI and the last well-formed `pipeline_stage_transition` event after it. With no transition after the launch, the run reads the launch stage and has no position. A transition row that lacks a required field is skipped: a position with no Layer-2 source is never invented.

---

## The Rebuild

`uv run gz state --repair` keeps its frontmatter reconciliation and also repairs the marker files of the run in flight that was launched last. It is the only writer of a missing marker. A launch writes fresh markers for the run it starts. The one other writer is `gz adr audit-begin`, whose file is an audit ceremony's marker and no run's. No other command or hook writes a marker that is missing.

| Files on disk for the run | What the repair does |
|---------------------------|----------------------|
| Both, each reading as the run's marker | Nothing, and nothing is reported |
| Exactly one | Restores the missing file as a byte-for-byte copy of its twin (`restore_pipeline_marker_twin`). Nothing is read from the ledger, and the file on disk is not moved |
| Neither | Rebuilds both from the ledger (`rebuild_marker`) |

A rebuilt marker takes `obpi_id`, `parent_adr`, `lane`, `entry`, `nonce` and `started_at` from the `pipeline_launched` event, and `current_stage`, `position` and `blockers` from the last transition after it. Its `updated_at` is the time of that last crossing and never the time of the repair, so a rebuild cannot make an abandoned run look live.

### What a Rebuild Does Not Take From the Ledger

- `receipt_state` is read back from the plan-audit receipt file at the time of the repair, and is `missing` when there is none.
- `execution_mode` is the launcher's constant.
- `dispatch_state` and `single_driver_declaration` are not rebuilt. A copy from a twin keeps them; a rebuild from the ledger omits them. No gate depends on them.

### What the Repair Declines

Each declined run is reported with its reason.

- **A run idle past the stale bound.** With neither file on disk, a run whose last recorded crossing is older than `STALE_MARKER_HOURS`, or whose time cannot be read, is not rebuilt: its marker would be stale on arrival, and a resurrected marker would block every other OBPI's launch (ruled 2026-10-12, Open Design Question 15). Launch the run again to resume it.
- **An older run while a later one is in flight.** The legacy marker belongs to the run launched last, so no file is restored or written for an older run.
- **A launch with no nonce.** With neither file on disk, a run whose `pipeline_launched` event records no nonce is not rebuilt: a rebuild invents none. With one file on disk the missing one is restored as a copy of it, nonce and all.
- **A file in the way.** A marker file on disk that does not read as the run's marker is never overwritten.

The command contract, with its output, is in [`gz state`](../user/manpages/state.md#repair-mode).

---

## What the First Plan Proposed

The plan this document first carried differs from what was ruled and built in these ways. They are recorded so that a reader who met the earlier text is not misled.

| First plan | As built |
|------------|----------|
| Seven `pipeline-*` event types (`pipeline-started`, `pipeline-stage-entered`, `pipeline-stage-completed`, `pipeline-blocked`, `pipeline-resumed`, `pipeline-aborted`, `pipeline-completed`) | Two event types. `pipeline_launched` records a launch and each `--from` re-entry. `pipeline_stage_transition` records every boundary, a verification result and its blockers included. A run's end is read from the completion receipt or from the event that parks, withdraws or supersedes its OBPI |
| `ADR-0.13.0` OBPIs carry the migration in four phases | One OBPI, `OBPI-0.35.0-15`, assigned as a repair against `ADR-0.13.0` |
| The runtime rebuilds a missing marker before proceeding | Only `uv run gz state --repair` restores or rebuilds one. A launch writes fresh markers, and `uv run gz adr audit-begin` writes an audit ceremony's marker, which is no run's; every other command leaves a missing marker missing |
| Hooks fall back to the ledger when a marker is absent | Not built |
| Stale detection compares markers against ledger events in place of a time bound | Not built. Stale detection, `--clear-stale` and the launcher's purge of a marker whose OBPI is `attested_completed` are unchanged, and `updated_at` moves only when the run crosses a recorded boundary |
| `gz state --json` exposes a `pipeline` key | Not built. `gz state --json` prints the artifact graph; the repair's report is the `markers` object of `gz state --repair --json` |

One limit of the built design: a launch that is abandoned with no ledger event (no receipt, park, withdrawal or supersede) still reads as a run in flight on the ledger. Once its last recorded crossing is older than the stale bound and neither of its marker files is on disk, the repair declines it; while one file is on disk the repair restores the other as a copy of it.

---

## Verification

To observe the rebuild on a run in flight:

```bash
# 1. Delete both pipeline markers of the run launched last
rm -f .claude/plans/.pipeline-active*.json

# 2. Rebuild from the ledger
uv run gz state --repair --json
```

The `markers.rebuilt` list of the report names the run with its `current_stage`, `position` and `updated_at`, and both marker files are back on disk with one payload. `markers.declined` names any run the repair did not rebuild, with the reason.

The behaviour is proved by `tests/test_pipeline_position.py`, by the repair tests in `tests/adr/test_state_doctrine.py`, and by the scenarios in `features/pipeline_run_position.feature`.

---

## References

- [State Doctrine — Three-Layer Model](state-doctrine.md) — Layer definitions and authority rules
- [ADR-0.0.9 — State Doctrine](../design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md) — Source ADR
- [ADR-0.13.0 — OBPI Pipeline Runtime Surface](../design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md) — The runtime surface the repair was assigned against
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-15-pipeline-run-position.md` — The brief that carries the rulings
- `src/gzkit/pipeline_position.py` — Position model, ledger replay, recorder and rebuild decision
- `src/gzkit/pipeline_markers.py` — Every marker file write
- `src/gzkit/commands/state.py` — `gz state --repair`
