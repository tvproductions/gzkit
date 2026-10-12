# gz state

Query ledger artifact relationships and derived ADR semantics.

---

## Usage

```bash
gz state [--json] [--blocked] [--ready] [--include-withdrawn] [--repair] [--full]
```

---

## Filters

- `--blocked`: show unattested artifacts.
- `--ready`: show ADRs that are genuinely ready for attestation.
- `--include-withdrawn`: include withdrawn OBPIs (hidden by default).
- `--full`: preserve full IDs (no ellipsis truncation) and fold long table cells so the entire artifact graph remains readable on wide terminals.

`--ready` means:

- ADR is unattested, and
- prerequisite gates required by lane are satisfied.

It is not just "pending attestation".

### Withdrawn OBPI filtering

By default, `gz state` omits OBPIs marked `withdrawn` from the emitted
graph and scrubs their IDs from each parent ADR's `children` list so
derived status surfaces (e.g. `gz state --json`, `gz adr status`) do not
conflate withdrawn ceremonies with active decomposition. The ledger is
never mutated — `obpi_withdrawn` events remain as legitimate append-only
history and `--include-withdrawn` restores the full view for audits.
This implements the preferred resolution in GHI #221.

---

## Repair Mode

`--repair` makes two repairs, both from ledger-derived state. It
force-reconciles every OBPI brief's frontmatter status, and it rebuilds the
pipeline marker of a run in flight whose marker file is gone. It is the
operator recovery tool for drift between the L3 caches (frontmatter, pipeline
markers) and the ledger (L2 authority).

### Frontmatter reconciliation

- Scans all OBPI brief files under the design root.
- Compares each brief's frontmatter `status` to ledger-derived state.
- Updates frontmatter where it disagrees with the ledger:
    - Ledger says completed -> frontmatter set to `Completed`.
    - Ledger says withdrawn -> frontmatter set to `Abandoned`.
    - No definitive ledger state -> frontmatter left unchanged.
- Idempotent: running twice produces no changes on the second run.
- Works after `git clone` with no dependency on L3 caches or markers.

### Pipeline marker rebuild

`gz state --repair` is the one command that rebuilds a missing or deleted
pipeline marker. Nothing else does: the pipeline launcher, the hooks and the
commands that record a run's position all leave a missing marker missing.

A run is in flight from its latest `pipeline_launched` event until its
completion receipt, or until its OBPI is parked or withdrawn. For each run in
flight whose per-OBPI marker file is not on disk, the repair writes both marker
files (`.claude/plans/.pipeline-active-<OBPI-ID>.json` and
`.claude/plans/.pipeline-active.json`) from the ledger alone:

- `obpi_id`, `parent_adr`, `lane`, `entry`, `nonce` and `started_at` come from
  the `pipeline_launched` event.
- `current_stage`, `position`, `blockers`, `required_human_action`,
  `next_command` and `resume_point` come from the last
  `pipeline_stage_transition` event after that launch. A launch with nothing
  after it rebuilds to its launch values and carries no `position`.
- `updated_at` is the time of that last recorded crossing, never the time of
  the repair, so a rebuild cannot make an abandoned run look live.
- `receipt_state` is read back from the plan-audit receipt file, and is
  `missing` when there is none.

**Not restored.** The `dispatch_state` and `single_driver_declaration` keys are
caches of ledger records and are not rebuilt. Stage 2 dispatch credit and the
single-driver declaration are read from the ledger, so no gate depends on them.

**Never moved.** A marker file that is on disk is left exactly as it is. A run
whose per-OBPI marker is on disk is not touched, even when only the legacy
marker is gone.

**Declined, and reported with the reason.** The repair names each run in flight
that it does not rebuild:

- The run's last recorded crossing is older than the stale-marker bound. Its
  marker would be stale on arrival, and a resurrected marker would block every
  other OBPI's launch. Launch the run again with `gz obpi pipeline` to resume it.
- The legacy marker is on disk and names another OBPI, or cannot be read. A
  rebuild writes both files and overwrites no other run's marker. When two runs
  are in flight with no markers, the one launched last is rebuilt.
- The run's own marker file is on disk and cannot be read. Clear it with
  `gz obpi pipeline --clear-stale`, then repair again.

A run that has ended, an OBPI that was parked and later unparked but not
launched again, and an ADR audit ceremony are not runs in flight; they are
neither rebuilt nor reported.

### Output

Human-readable by default: a table of the frontmatter fields changed, then one
line for each marker rebuilt and each run declined. `--json` prints one object.
`changes` and `total` describe the frontmatter reconciliation; `markers` lists
the runs rebuilt and the runs declined.

```json
{
  "changes": [
    {
      "obpi_id": "OBPI-0.1.0-01",
      "file": "docs/design/adr/ADR-0.1.0/obpis/OBPI-0.1.0-01-feature.md",
      "old_status": "Draft",
      "new_status": "Completed"
    }
  ],
  "total": 1,
  "markers": {
    "rebuilt": [
      {
        "obpi_id": "OBPI-0.1.0-02-in-flight",
        "current_stage": "verify",
        "position": {
          "kind": "phase",
          "label": "verification",
          "boundary": "gz obpi pipeline"
        },
        "updated_at": "2026-10-12T00:51:51.180096+00:00"
      }
    ],
    "declined": [
      {
        "obpi_id": "OBPI-0.1.0-01-abandoned",
        "reason": "its last recorded crossing (2026-10-10T18:51:51.179191+00:00) is older than 24 hours, so its marker would be stale on arrival; launch the run again to resume it"
      }
    ]
  }
}
```

**Exit codes:**

- `0`: Success (repairs applied, already aligned, or runs declined and reported).
- `1`: Configuration or initialization error.

---

## Derived ADR Fields

ADR entries include additive derived semantics (for example `lifecycle_status`, `closeout_phase`, `attestation_term`) based on ledger events.

---

## Task Data in JSON Output

When tasks exist for an OBPI, `--json` output includes a `task_summary` object
on that OBPI's entry with counts by status and the lane's tracing policy:

```json
{
  "OBPI-0.20.0-01": {
    "type": "obpi",
    "parent": "ADR-0.20.0",
    "task_summary": {
      "total": 3,
      "pending": 0,
      "in_progress": 1,
      "completed": 1,
      "blocked": 0,
      "escalated": 1,
      "tracing_policy": "required"
    }
  }
}
```

Task data does not appear when no tasks exist (backward compatible).

---

## Example

```bash
uv run gz state --ready
uv run gz state --ready --json
uv run gz state --include-withdrawn --json
uv run gz state --repair
uv run gz state --repair --json
```
