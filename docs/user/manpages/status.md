# gz status

Display OBPI progress, lifecycle status, and gate readiness across ADRs.

---

## Usage

```bash
gz status [--json] [--table] [--show-gates] [--epic SLUG] [--full]
```

`--full` renders every OBPI as its own Rich-table row and preserves full IDs (no ellipsis truncation), trading screen-width compactness for an unabridged view of the artifact graph.

---

## Runtime Behavior

`gz status` derives ADR lifecycle from ledger events and treats OBPI completion as the primary progress unit.
For single-OBPI drilldown, use `gz obpi status` or `gz obpi sync`.

Per ADR it reports:

- OBPI summary (`total`, `completed`, `incomplete`, `unit_status`)
- OBPI rows (linked file presence, `runtime_state`, proof/attestation state, anchor state, and issues)
- Closeout readiness fields (`closeout_ready`, `closeout_blockers`)
- QC readiness summary (`READY` / `PENDING` with pending checkpoints)
- Canonical lifecycle (`Pending`, `Completed`, `Validated`, `Abandoned`)
- Canonical attestation term when attested
- Gate summaries (`1..5` where lane-applicable) only when `--show-gates` is supplied

`--table` renders a stable summary table with one row per ADR:
- ADR id
- lifecycle status
- lane
- OBPI completion ratio
- OBPI unit status
- QC readiness
- pending check categories (compact codes in `Checks`)

QC readiness is fail-closed for OBPI-first delivery:
- when linked OBPIs exist and OBPI unit is not `completed`, `QC` reports `PENDING`
- `Checks` includes `O` (`OBPI completion`) even if gate checks are otherwise passing

`Validated` applies to ADR-level validation receipts. OBPI-scoped receipts marked with
`adr_completion: not_completed` do not mark the parent ADR as validated.

When linked OBPIs exist and the OBPI unit is not `completed`, lifecycle is reported as `Pending`
even if ledger attestation/receipt events indicate `Completed` or `Validated`.
Anchor freshness stays fail-closed in `closeout_blockers`, but a completed OBPI
keeps its completed runtime state unless non-anchor proof/evidence drift is
present.

### `--epic SLUG` (pool-ADR filter)

`--epic <slug>` restricts output to pool ADRs (`ADR-pool.*`) that belong to the named epic.
Matching is OR'd across two paths:

- **Filename-derived.** The first hyphen-delimited token after `ADR-pool.` is the epic-slug.
  `ADR-pool.auth-login.md` matches `--epic auth`.
- **Frontmatter-derived.** A pool ADR may set an optional `epic: <slug>` field in its YAML
  frontmatter. `ADR-pool.claude-code.md` with `epic: vendor-alignment` matches
  `--epic vendor-alignment` (useful for multi-token epic names that the single-token filename
  convention cannot express).

When both paths are present and disagree, `gz status --epic <slug>` emits a non-fatal warning
(stderr in human mode; populated `warnings: []` in `--json` mode). Non-pool ADRs are always
excluded when `--epic` is set. An epic with no members exits 0 with an empty `adrs` map.

---

## JSON Output

`--json` includes the existing top-level shape plus enriched per-ADR data:
- `obpis`
- `obpi_summary`
- `gates`
- `lane`
- `lifecycle_status`
- `attestation_term`
- `closeout_phase`
- `closeout_ready`
- `closeout_blockers`
- additive per-OBPI runtime fields such as `runtime_state`, `proof_state`,
  `attestation_requirement`, `attestation_state`, `req_proof_state`, `req_proof_inputs`,
  `anchor_state`, `anchor_commit`, `current_head`, `anchor_issues`,
  `anchor_drift_files`, `tracked_defects`, and `issue_details`
- `observed_post_validation_gate_failures`: sorted list of gate ids whose latest
  raw `gate_checked` event is `fail` after the validated lifecycle epoch began.
  The lifecycle-authoritative `gates` cell still shows `pass` for those gates
  (state-doctrine — lifecycle is authority), but the sidecar surfaces the
  underlying observation so display layers can annotate it and QC readiness
  blocks on it instead of silently reporting `READY`. Empty when raw and
  effective views agree.
- related additive fields

If an OBPI brief records a `## Tracked Defects` section, the corresponding
closeout blockers carry those linked `GHI-*` refs so summary drilldowns keep
defect-level traceability without requiring live GitHub access.

---

## Example

```bash
uv run gz status
uv run gz status --table
uv run gz status --show-gates
uv run gz status --json
uv run gz status --epic auth
uv run gz status --epic vendor-alignment --json
```

When tasks exist for active OBPIs, a task summary row appears showing counts
by status (done, active, pending, blocked, escalated) and whether task tracing
is advisory (Lite lane) or required (Heavy lane). The task summary does not
appear when no tasks exist (backward compatible).

JSON output includes a `task_summary` object per ADR when tasks are present:

```json
{
  "task_summary": {
    "total": 5,
    "pending": 1,
    "in_progress": 2,
    "completed": 1,
    "blocked": 0,
    "escalated": 1,
    "tracing_policy": "required"
  }
}
```

Table output excerpt (captured 2026-03-08):

```text
ADR Status
+------------------------------------------------------------------------------+
|ADR                         |Life     |Lane | OBPI|Unit     |QC     |Checks   |
|----------------------------+---------+-----+-----+---------+-------+---------|
|ADR-0.1.0                   |Pending  |LITE |  0/1|PENDING  |PENDING|O,T      |
|ADR-0.2.0                   |Completed|HEAVY|  3/3|COMPLETED|READY  |-        |
+------------------------------------------------------------------------------+
Checks legend: O=OBPI completion, T=TDD, D=Docs, B=BDD, H=Human attestation, X=Observed post-validation gate fail
```

`X` (observed post-validation gate fail) appears when an ADR has a `gate_checked: fail` event in the ledger that landed after its lifecycle transitioned to `Completed` / `Validated` (with no rollback). Lifecycle remains the authoritative source for the `Gates` cell, but the `Checks` column surfaces the underlying observation so the failing evidence is not silently smoothed away (GHI #411).

The table uses compact cell padding so more ADR identifier text stays visible in the default terminal width. If an identifier still exceeds the available width, the `ADR` column folds it across lines instead of truncating it with an ellipsis.
