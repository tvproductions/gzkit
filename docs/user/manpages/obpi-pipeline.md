# gz obpi pipeline

Launch the OBPI pipeline runtime surface for one OBPI.

---

## Usage

```bash
gz obpi pipeline <OBPI-ID> [--from {verify,ceremony,sync}] [--attestor NAME]
                           [--evidence-json JSON] [--clear-stale]
```

`<OBPI-ID>` accepts the full canonical identifier or the same identifier
without the `OBPI-` prefix.

---

## Options

| Option | Description |
|--------|-------------|
| `--from {verify,ceremony,sync}` | Resume the pipeline from the named stage (default: full launch) |
| `--attestor NAME` | Attestor identity for Stage 5 (e.g. `g0` or `agent:<name>`); used by ceremony and sync stages when relaying the human attestation. Defaults to `authorship.attestor_handle` in `.gzkit.json` when set (GHI #1036) |
| `--evidence-json JSON` | Inline evidence payload for Stage 5. **Required key**: `attestation_text` (forwarded to `gz obpi complete --attestation-text`). **Optional keys**: `implementation_summary`, `key_proof`, `value_narrative`, paired `accept_uncovered` + `accept_uncovered_reason` arrays for REQ waivers. The pipeline translates the JSON into the discrete flags `gz obpi complete` consumes; a missing `attestation_text` fails closed at the pipeline boundary (GHI #435). |
| `--clear-stale` | Remove stale pipeline markers and exit without launching (recovery path for crashed sessions). A marker is stale when its `updated_at` is older than `STALE_MARKER_HOURS` (`src/gzkit/pipeline_markers.py`), or when the file or its `updated_at` cannot be read |

---

## Runtime Behavior

`gz obpi pipeline` is the canonical CLI launch surface for the governance
pipeline. The `gz-obpi-pipeline` skill remains available as a thin alias for
agent UX, but it must not redefine stage sequencing or closeout semantics.

`src/gzkit/pipeline_runtime.py` is the shared runtime engine behind the CLI and
the generated Claude pipeline hooks.

Current command contract:

- every launch records the parent ADR as `Accepted` before writing markers: a
  `Proposed` ADR transitions `Proposed -> Accepted`, and a `Draft` ADR walks
  `Draft -> Proposed -> Accepted` through the lifecycle state machine, whose
  evaluation-justify-binding gate on `Draft -> Proposed` can refuse the launch
  (exit `3`, nothing written). The ADR's frontmatter `status:` follows the
  ledger. An ADR already `Accepted` or later is left alone (GHI #1014)
- every launch, full or `--from`, writes both active pipeline markers afresh
  and appends one `pipeline_launched` event to the ledger. The markers then
  read the launch stage, carry a new `nonce` and `started_at`, and hold no
  `position` until the run crosses its next recorded boundary
- full launch reads the plan-audit receipt when present, advances the brief's
  frontmatter `status:` out of `Draft` to `Active`, and prints the
  implementation handoff with the follow-up `--from=verify` command
- `--from=verify` reruns Stage 1, executes the baseline checks and the
  verification commands from the OBPI brief, adds Heavy-lane docs/BDD checks,
  and ends with `gz obpi precomplete`. A failed verification command records
  its blockers in the markers and exits `1`. A pass chains into the ceremony
  stage in the same invocation. Both markers stay in place either way
- `--from=ceremony` reruns Stage 1 and records the run's entry into the
  ceremony. While acceptance obligations are still open, it prints the
  commands that prepare the evidence packet and report those obligations.
  Otherwise it prints the `--from=sync` command to run once the human has
  attested; human attestation is required for every OBPI completion
  (ADR-0.0.36). Both markers stay in place
- `--from=sync` requires `--attestor` and `--evidence-json`. It runs
  `gz obpi complete`, the guarded repository sync, `gz obpi sync` and the
  parent ADR status refresh, and removes both markers and the OBPI's plan-audit
  receipt once every one of those steps has passed. A failed step exits `1`
  and leaves the markers in place

No stage before Stage 5 removes a marker. Apart from that removal, the runtime
removes a marker only as cleanup: `--clear-stale` and `gz preflight --apply`
remove stale markers, and the launcher purges a marker whose OBPI the ledger
already reads as `attested_completed`.

The active marker files are also the machine-readable stage-state contract while
the pipeline is running. They are runtime-managed and should not be edited or
cleared manually:

- `.claude/plans/.pipeline-active-<OBPI-ID>.json`
- `.claude/plans/.pipeline-active.json`

The two files carry one payload. The launch and every later write go to both,
so they agree after each recorded boundary and after each dispatch.

Those marker payloads persist:

- `obpi_id`
- `parent_adr`
- `lane`
- `entry`
- `execution_mode`
- `current_stage`
- `position`
- `started_at`
- `updated_at`
- `receipt_state`
- `nonce`
- `blockers`
- `required_human_action`
- `next_command`
- `resume_point`

`entry` is how the run was launched: `full`, `verify`, `ceremony` or `sync`. It
does not change while the run advances.
`current_stage` is the stage the run has reached: `implement`, `verify`,
`ceremony` or `sync`.
`position` is where the run is inside that stage; see the next section. A
launch with nothing recorded after it carries no `position` key.
`updated_at` is the time of the last recorded boundary, or of the launch when
nothing follows it. Reading a marker never moves it.
`nonce` pairs the marker with its `pipeline_launched` ledger event.
`blockers` is a list of active stage blockers: what the last failed
verification found. A passed verification, or a command that begins a stage's
work, clears it.
`required_human_action` is either `null` or a concise summary of the current
required human action. It is set while the run is at `ceremony` and `null` at
every other stage.
`next_command` is either `null` or the next canonical operator command for the
stage reached.
`resume_point` is either `null` or the stage label the operator should resume
from.

A marker may also carry `dispatch_state` and `single_driver_declaration`. Both
are caches of records the ledger holds: Stage 2 dispatch credit and the
single-driver declaration are read from the ledger, never from the marker.

The marker payload is active-state only. It is not authoritative completion
history.

### Where the run is: stage and position

The markers record what the run has reached, never merely what the launch
command named. As the run crosses each recorded boundary, the command that
marks the boundary appends one `pipeline_stage_transition` event to the ledger
and then writes `current_stage`, `position`, `updated_at` and the stage-output
fields (`blockers`, `required_human_action`, `next_command`, `resume_point`) to
both marker files. Every other key is kept as it was.

`position` names the last recorded boundary the run crossed. It has three
fields:

| Field | Meaning |
|-------|---------|
| `kind` | What a position is called in the stage reached: `task` at `implement`, `phase` at `verify`, `round` at `ceremony`, `step` at `sync` |
| `label` | The task the boundary marked (`task <n>` for a dispatch, the TASK id for a `gz task` verb), otherwise the boundary's name |
| `boundary` | The command that marked the crossing |

A position is never written as a `current_stage` value: `current_stage` is
always one of the four stages above.

A command that begins a stage's work moves the run to that stage:

| Boundary | Marked by | Stage entered |
|----------|-----------|---------------|
| `dispatch` | `gz obpi dispatch` (a recorded dispatch) | `implement` |
| `task-start` | `gz task start` | `implement` |
| `verification` | `gz obpi pipeline`, when the verify stage starts | `verify` |
| `ceremony` | `gz obpi pipeline`, when the ceremony stage is entered | `ceremony` |
| `present-evidence` | `gz obpi present-evidence` | `ceremony` |
| `complete` | `gz obpi complete`, as its transaction starts | `sync` |

A check or a bookkeeping event records its position inside the stage the run
has already reached and never changes that stage:

| Boundary | Marked by |
|----------|-----------|
| `task-complete`, `task-block`, `task-escalate` | `gz task complete`, `gz task block`, `gz task escalate` |
| `verification-passed`, `verification-failed` | `gz obpi pipeline`, when the verification commands finish |
| `precomplete` | `gz obpi precomplete` |
| `verify-packet` | `gz obpi verify-packet` |
| `acceptance-review` | `gz obpi acceptance`, when it records an adversarial review or a human review |

These record nothing: a spec or quality review recorded through
`gz obpi acceptance`, `gz obpi sync`, a `gz obpi dispatch --single-driver`
declaration, and the TASKs the launch starts and the completion closes on the
run's behalf. A position recorded at `complete` says the run reached that
step, not that completion succeeded; the outcome is the completion receipt.

A boundary is recorded only for a run in flight. A run is in flight from its
latest `pipeline_launched` event until its completion receipt, or until its
OBPI is parked, withdrawn or superseded; a later launch starts a new run.
An I/O failure while recording a position warns and leaves the outcome of the
command that marked the boundary as it was. No gate reads a position: it is
orientation, not evidence.

One rule says which OBPI an id names, the rule this command launches by: the
ledger's id for it, reached from the full id, from a short
`OBPI-<semver>-<item>` id or a longer prefix that ends on a whole word of the
id, or from an id the ledger renamed. `gz obpi precomplete` and
`gz obpi present-evidence` name the OBPI that way once, at entry, and run
their checks, write their report and record their boundary under that one id.
They exit `1`, check nothing and record nothing for an id that names no OBPI,
names two, or names one with no brief on disk. `gz obpi verify-packet` and a
review recorded through `gz obpi acceptance` record their boundary under the
same id.

### Re-entering `implement`

The post-Stage-2 fence reads `current_stage`. It refuses a production write
(`src/**`) while the stage is `verify`, `ceremony` or `sync`, and refuses a
commit carrying one while the stage is `verify` or `ceremony`. The stage
advances on every run, so the fence binds after a full launch as it does after
a `--from` entry.

A repair that needs production code after Stage 2 re-enters `implement`
through the runtime, which is what the fence's refusal prescribes:
`gz task start` and `gz obpi dispatch` each begin Stage 2 work, so each moves
the run back to `implement` and records the re-entry on the ledger.
`gz task complete`, `gz task block` and `gz task escalate` are bookkeeping and
do not move the stage. Do not edit the marker by hand.

### A deleted marker

`gz state --repair` is the one command that restores or rebuilds a missing
pipeline marker. A launch writes fresh markers for the run it starts; every
other command, the hooks and the commands that record a position among them,
leaves a missing marker missing. The repair acts on the run in flight that was
launched last:

- When one of the run's two marker files is on disk, the missing one is
  restored as a byte-for-byte copy of it.
- When neither is on disk, both are rebuilt from the ledger: the run's
  `pipeline_launched` event and the last `pipeline_stage_transition` event
  after it. The rebuilt marker reads the same `current_stage` and `position`,
  and its `updated_at` is the time of that last crossing, never the time of the
  repair. The `dispatch_state` and `single_driver_declaration` caches are not
  rebuilt from the ledger.
- With neither file on disk, a run whose last recorded crossing is older than
  `STALE_MARKER_HOURS` is declined, because its marker would be stale on
  arrival; launch it again to resume it. The stale bound applies only then:
  with one file on disk the missing one is restored as a copy of it, however
  old that copy is. An older run is declined while a later one is in flight,
  because the legacy marker belongs to the run launched last. Each declined
  run is reported with its reason.

`gz state --repair --json` reports this in a `markers` object with three
lists, `rebuilt`, `restored` and `declined`. See [gz state](state.md) for the
whole contract.

Claude hook surfaces and generated control surfaces should point operators back
to this command contract instead of re-explaining the stage engine in prose.

---

## Failure Modes

The command exits non-zero and prints `BLOCKERS:` when:

- the OBPI brief cannot be resolved
- the OBPI brief is already completed
- the OBPI brief fails authored-readiness validation (including scaffold placeholders) before execution
- the parent ADR evaluation scorecard has a NO GO verdict (detected by `check_adr_evaluation_verdict`)
- the matching plan-audit receipt verdict is `FAIL`
- another OBPI is already active in the pipeline markers
- any verification command fails in `--from=verify`

Missing or unreadable plan-audit receipts are warnings, not blockers.
Missing evaluation scorecards are not blockers (evaluation is advisory until run).

---

## Examples

```bash
uv run gz obpi pipeline OBPI-0.13.0-01-runtime-command-contract
```

```text
OBPI pipeline: OBPI-0.13.0-01-runtime-command-contract
  Parent ADR: ADR-0.13.0-obpi-pipeline-runtime-surface
  Brief: docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-01-runtime-command-contract.md
  Lane: heavy
  Entry: full
  Receipt: MISSING
  Stages: 1. Load Context -> 2. Implement -> 3. Verify -> 4. Present Evidence -> 5. Sync And Account
  Marker: .claude/plans/.pipeline-active-OBPI-0.13.0-01-runtime-command-contract.json
  Legacy Marker: .claude/plans/.pipeline-active.json
  Warning: plan-audit receipt is missing; proceeding with an explicit gap

Next:
- Implement the approved OBPI within the brief allowlist.
- When implementation is ready, run: uv run gz obpi pipeline OBPI-0.13.0-01-runtime-command-contract --from=verify
- Keep the active pipeline markers in place during implementation.
```

```bash
uv run gz obpi pipeline OBPI-0.13.0-01-runtime-command-contract --from=verify
uv run gz obpi pipeline 0.13.0-01-runtime-command-contract --from=ceremony
```
