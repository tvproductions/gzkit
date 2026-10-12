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
force-reconciles every OBPI brief's frontmatter status, and it restores or
rebuilds the pipeline marker files of the run in flight that was launched
last. It is the operator recovery tool for drift between the L3 caches
(frontmatter, pipeline markers) and the ledger (L2 authority).

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

`gz state --repair` is the one command that restores or rebuilds a missing or
deleted pipeline marker. Nothing else does: the pipeline launcher, the hooks
and the commands that record a run's position all leave a missing marker
missing.

A run is in flight from its latest `pipeline_launched` event until its
completion receipt, or until its OBPI is parked, withdrawn or superseded. A run
has two marker files: its own, `.claude/plans/.pipeline-active-<OBPI-ID>.json`,
and the legacy marker, `.claude/plans/.pipeline-active.json`. The legacy marker
is one file for the whole project and names the run launched last. The repair
therefore acts on one run, the run in flight that was launched last, and does
one of two things for it.

**One file missing: restored as a copy.** When exactly one of the run's two
marker files is on disk and reads as that run's marker, the missing one is
created as a copy of it, byte for byte. Everything the file on disk carries
survives, including `dispatch_state`, `single_driver_declaration`, `started_at`
and `updated_at`, and the file on disk is not moved. Nothing is read from the
ledger for a copy, so a marker that is behind the ledger stays behind it.

**Both files missing: rebuilt.** When neither file is on disk, the repair
writes both. Most keys come from the ledger, and two do not:

- `obpi_id`, `parent_adr`, `lane`, `entry`, `nonce` and `started_at` come from
  the `pipeline_launched` event. `started_at` is that event's own time, which
  the launcher records a moment after it writes the marker, so it can differ
  from the deleted marker's `started_at` by that moment.
- `current_stage`, `position` and `blockers` come from the last
  `pipeline_stage_transition` event after that launch, and
  `required_human_action`, `next_command` and `resume_point` are what the
  runtime derives for that stage and those blockers. A launch with nothing
  after it rebuilds to its launch values and carries no `position`.
- `updated_at` is the time of that last recorded crossing, never the time of
  the repair, so a rebuild cannot make an abandoned run look live.
- `receipt_state` is not on the ledger. It is read back from the plan-audit
  receipt file at the time of the repair, and is `missing` when there is none.
- `execution_mode` is not on the ledger either. It is the launcher's constant.

**Not restored by a rebuild.** The `dispatch_state` and
`single_driver_declaration` keys are caches of ledger records and are not
rebuilt from the ledger; a copy keeps them. Stage 2 dispatch credit and the
single-driver declaration are read from the ledger, so no gate depends on them.

**Never overwritten.** A marker file that is on disk is never rewritten. When
both of the run's files are on disk and read as its marker, the repair does
nothing for it and reports nothing.

**Declined, and reported with the reason.** The repair names each run in flight
that it does not repair:

- A later run is in flight. The legacy marker belongs to the run launched
  last, so no file is restored or written for an older run, whatever files are
  on disk. An older run can then never take the legacy marker and block the
  live one.
- Neither file is on disk and the run's last recorded crossing is older than
  the stale-marker bound, or its time cannot be read. Its marker would be stale
  on arrival, and a resurrected marker would block every other OBPI's launch.
  Launch the run again with `gz obpi pipeline` to resume it.
- Neither file is on disk and the run's `pipeline_launched` event records no
  nonce. A rebuild invents none.
- The legacy marker is on disk and names another OBPI, or cannot be read. A
  repair overwrites no file and no other run's marker.
- The run's own marker file is on disk and cannot be read. Clear it with
  `gz obpi pipeline --clear-stale`, then repair again.

A run that has ended, an OBPI that was parked and later unparked but not
launched again, and an ADR audit ceremony are not runs in flight; they are
neither repaired nor reported.

The boundaries a run records, and which of them move its stage, are listed in
[gz obpi pipeline](obpi-pipeline.md#where-the-run-is-stage-and-position).

### Output

Human-readable by default: a table of the frontmatter fields changed, then one
line for each marker file restored, each marker rebuilt and each run declined.
A repair that found the frontmatter aligned and rebuilt one deleted marker
prints:

```text
All frontmatter is aligned with ledger state. No changes.
Rebuilt pipeline marker: OBPI-0.1.0-02-in-flight at stage ceremony (round present-evidence), last crossing 2026-10-12T02:04:04.075795+00:00
```

A repair that restored the legacy marker from the run's own file prints:

```text
All frontmatter is aligned with ledger state. No changes.
Restored pipeline marker file: .pipeline-active.json for OBPI-0.1.0-02-in-flight, a copy of .pipeline-active-OBPI-0.1.0-02-in-flight.json
```

`--json` prints one object. `changes` and `total` describe the frontmatter
reconciliation; `markers` lists the runs rebuilt, the files restored and the
runs declined. A `restored` entry carries `obpi_id`, `file` (the marker file
created) and `copied_from` (the marker file it copies). Only the run launched
last is repaired, so one report holds at most one entry across `rebuilt` and
`restored`.

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
    "restored": [],
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
