# gz obpi pipeline

Launch the OBPI pipeline runtime surface for one OBPI.

---

## Usage

```bash
gz obpi pipeline <OBPI-ID> [--from {verify,ceremony}]
```

`<OBPI-ID>` accepts the full canonical identifier or the same identifier
without the `OBPI-` prefix.

---

## Runtime Behavior

`gz obpi pipeline` is the canonical CLI launch surface for the governance
pipeline. The `gz-obpi-pipeline` skill remains available as a thin alias for
agent UX, but it must not redefine stage sequencing or closeout semantics.

`src/gzkit/pipeline_runtime.py` is the shared runtime engine behind the CLI and
the generated Claude pipeline hooks.

Current command contract:

- full launch creates the active pipeline markers, reads the plan-audit receipt
  when present, and prints the implementation handoff with the follow-up
  `--from=verify` command
- `--from=verify` reruns Stage 1, executes verification commands from the OBPI
  brief, adds Heavy-lane docs/BDD checks, clears active markers on success, and
  prints the follow-up `--from=ceremony` command
- `--from=ceremony` reruns Stage 1, prints the ceremony/accounting checklist,
  requires explicit human attestation only for Heavy/Foundation completion
  paths, and clears active markers on exit

The active marker files are also the machine-readable stage-state contract while
the pipeline is running. They are runtime-managed and should not be edited or
cleared manually:

- `.claude/plans/.pipeline-active-<OBPI-ID>.json`
- `.claude/plans/.pipeline-active.json`

Those marker payloads now persist:

- `obpi_id`
- `parent_adr`
- `lane`
- `entry`
- `execution_mode`
- `current_stage`
- `started_at`
- `updated_at`
- `receipt_state`
- `blockers`
- `required_human_action`
- `next_command`
- `resume_point`

`blockers` is a list of active stage blockers.
`required_human_action` is either `null` or a concise summary of the current
required human action. Lite-lane ceremony state keeps this field `null` because
human attestation is optional there.
`next_command` is either `null` or the next canonical operator command.
`resume_point` is either `null` or the stage label the operator should resume
from.

The marker payload is active-state only. It is not authoritative completion
history.

Claude hook surfaces and generated control surfaces should point operators back
to this command contract instead of re-explaining the stage engine in prose.

---

## Failure Modes

The command exits non-zero and prints `BLOCKERS:` when:

- the OBPI brief cannot be resolved
- the OBPI brief is already completed
- the matching plan-audit receipt verdict is `FAIL`
- another OBPI is already active in the pipeline markers
- any verification command fails in `--from=verify`

Missing or unreadable plan-audit receipts are warnings, not blockers.

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
