# Operator Runbook

This runbook is a proof surface and must match executable runtime behavior.
For governance-maintainer procedures (parity scans, reconciliation sequencing, closeout/audit operations), use [`docs/governance/governance_runbook.md`](../governance/governance_runbook.md).
Legacy parity note: when external docs mention `/gz-adr-manager`, use `/gz-adr-create` (or the `gz-adr-manager` compatibility alias skill).

---

## Operating Model (OBPI-First)

- The atomic unit of delivery is the OBPI (One Brief Per Item).
- ADRs are planning and attestation containers that roll up many OBPIs.
- Daily execution should iterate OBPI-by-OBPI, not wait for end-of-ADR batching.

---

## Loop A: OBPI Increment (Primary Daily Loop)

```bash
# 1) Orientation + parent ADR context
uv run gz status
uv run gz status --table
uv run gz adr status ADR-<X.Y.Z> --json

# 1b) Validate OBPI briefs before pipeline (catches template stubs)
uv run gz obpi validate --adr ADR-<X.Y.Z>

# 1c) Evaluate ADR quality (NO GO verdict blocks pipeline)
uv run gz adr evaluate ADR-<X.Y.Z>

# 2) Execute the OBPI through the staged pipeline
uv run gz obpi pipeline OBPI-<X.Y.Z-NN>

#    Thin wrapper skill remains available:
#    /gz-obpi-pipeline OBPI-<X.Y.Z-NN>
#
#    Compatibility entry points:
#    uv run gz obpi pipeline OBPI-<X.Y.Z-NN> --from=verify
#    uv run gz obpi pipeline OBPI-<X.Y.Z-NN> --from=ceremony
#
#    The CLI and generated Claude hooks share the same runtime engine in
#    src/gzkit/pipeline_runtime.py. Treat active pipeline markers as
#    runtime-managed state; do not clear them by hand.

# 2b) Inspect pipeline roles and dispatch history
uv run gz roles
uv run gz roles --pipeline OBPI-<X.Y.Z-NN>

# 2c) Subagent dispatch operation
#    Stage 2 dispatches fresh implementer subagents per plan task by default.
#    Each task is classified by complexity (simple/standard/complex) and
#    routed to the appropriate model tier (haiku/sonnet/opus).
#
#    --no-subagents flag disables dispatch and runs Stage 2 inline (single
#    session, current behavior preserved as fallback for debugging).
#
#    If a task returns BLOCKED after retry, Stage 2 halts and creates a
#    handoff. Inspect dispatch state in the pipeline marker:
#      cat .claude/plans/.pipeline-active-OBPI-<X.Y.Z-NN>.json | python -m json.tool
#
#    Dispatch records show: task_id, role, model, timestamps, status, result.
#
# 2d) Two-stage review dispatch
#    After each implementer task completes (DONE or DONE_WITH_CONCERNS),
#    two independent reviewer subagents are dispatched concurrently:
#      - Spec reviewer: verifies code matches brief requirements
#      - Quality reviewer: evaluates SOLID, size limits, test coverage
#
#    Reviews use sonnet (simple/standard tasks) or opus (complex tasks).
#    Critical review findings trigger a fix cycle — the implementer is
#    redispatched with the finding as context, then re-reviewed.
#    Maximum 2 fix cycles per task before escalating to the user.
#
#    --no-subagents skips review dispatch (inline mode has no independent review).
#
#    Review findings are recorded in the dispatch state alongside
#    implementer records for the Stage 4 ceremony.

# 3) Verify this increment
uv run gz implement --adr ADR-<X.Y.Z>
uv run gz gates --gate 3 --adr ADR-<X.Y.Z>   # when docs changed
uv run gz lint
#
# 3b) REQ-level parallel verification dispatch (Stage 3 Phase 2)
#    After baseline checks pass, Stage 3 analyzes brief requirements for
#    non-overlapping test paths and dispatches parallel verification
#    subagents using worktree isolation.
#
#    Requirements with overlapping test paths run sequentially within a
#    single subagent. Requirements with non-overlapping paths dispatch
#    concurrently via `isolation: worktree` + `run_in_background: true`.
#
#    --no-subagents skips parallel verification dispatch and runs all
#    verification sequentially inline (same as pre-0.18.0 behavior).
#
#    Wall-clock timing metrics are recorded for parallel vs sequential
#    comparison. Inspect via the pipeline marker:
#      cat .claude/plans/.pipeline-active-OBPI-<X.Y.Z-NN>.json | python -m json.tool

# 4) Present the OBPI ceremony and only then update the brief
#    (status Completed only after attestation when required)
#    Use parser-safe inline bullets in "Implementation Summary":
#      - Files created/modified: <paths>
#      - Tests added: <files or (none)>
#      - Date completed: YYYY-MM-DD
#    (Do not split values onto nested bullet lines.)

# 5) Run guarded sync before final completion accounting
uv run gz git-sync --apply --lint --test

# 6) Emit and reconcile final OBPI completion from the synced state
uv run gz obpi emit-receipt OBPI-<X.Y.Z-NN>-<slug> --event completed --attestor "human:<name>" --evidence-json '{...}'
uv run gz obpi reconcile OBPI-<X.Y.Z-NN>-<slug>
uv run gz adr status ADR-<X.Y.Z> --json
```

---

## Drift Control (Required Before Closeout)

Until ledger-derived brief sync is automated, treat OBPI brief status/date fields as drift-prone and
always recompute truth from `gz` status surfaces before closeout:

```bash
# 1) Ledger-first recompute view
uv run gz adr status ADR-<X.Y.Z> --json
uv run gz status --table

# 2) Fail-closed audit of linked OBPIs
uv run gz adr audit-check ADR-<X.Y.Z>
```

If `gz adr audit-check` reports missing or placeholder implementation evidence:

1. Fix the OBPI brief `### Implementation Summary` with inline `- key: value` entries.
2. Re-run `uv run gz adr status ADR-<X.Y.Z> --json`.
3. Re-run `uv run gz adr audit-check ADR-<X.Y.Z>` until PASS.

Tracked automation defect: `https://github.com/tvproductions/gzkit/issues/3`.

---

## Loop B: ADR Closeout (After OBPI Batch Completion)

Run this only when linked OBPIs are complete and evidenced.

```bash
# 1) Reconcile ADR <-> OBPI completeness
uv run gz adr audit-check ADR-<X.Y.Z>

# 2) Closeout presentation (paths/commands only)
uv run gz closeout ADR-<X.Y.Z>

# 3) Human attestation (prerequisites enforced by default)
uv run gz attest ADR-<X.Y.Z> --status completed

# 4) Post-attestation audit (strict)
uv run gz audit ADR-<X.Y.Z>

# 5) Receipt/accounting at ADR scope
uv run gz adr emit-receipt ADR-<X.Y.Z> --event validated --attestor "<Human Name>" --evidence-json '{"scope":"ADR-<X.Y.Z>","date":"YYYY-MM-DD"}'
```

---

## Normal Use Flows (Concrete Example, Captured 2026-02-22)

These are copy/paste examples from this repository using real IDs and current CLI output.

### Flow 1: Daily OBPI Work (In-Progress ADR)

Use an active ADR with incomplete OBPIs:

```bash
uv run gz adr status ADR-0.5.0-skill-lifecycle-governance --json
uv run gz status --table
```

Output excerpt:

```json
{
  "adr": "ADR-0.5.0-skill-lifecycle-governance",
  "lifecycle_status": "Pending",
  "gates": {
    "1": "pass",
    "2": "pending",
    "3": "pending",
    "4": "n/a",
    "5": "pending"
  },
  "obpi_summary": {
    "total": 5,
    "completed": 0,
    "incomplete": 5,
    "unit_status": "pending"
  }
}
```

Run implementation and verification for one increment:

```bash
uv run gz implement --adr ADR-0.5.0-skill-lifecycle-governance
uv run gz gates --gate 3 --adr ADR-0.5.0-skill-lifecycle-governance
uv run gz lint
```

After brief evidence is updated and the Heavy-lane ceremony is accepted, run guarded sync first and only then emit the OBPI receipt:

```bash
uv run gz git-sync --apply --lint --test
uv run gz obpi emit-receipt OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity --event completed --attestor "Jeffry Babb" --evidence-json '{"attestation":"I attest I understand the completion of OBPI-0.5.0-05.","date":"2026-02-22"}'
uv run gz obpi reconcile OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity
```

### Flow 2: ADR Closeout (OBPIs Completed)

Use an ADR whose OBPIs are completed:

```bash
uv run gz adr audit-check ADR-0.6.0-pool-promotion-protocol
```

Output:

```text
ADR audit-check: ADR-0.6.0-pool-promotion-protocol
PASS All linked OBPIs are completed with evidence.
  - OBPI-0.6.0-01-pool-source-contract
  - OBPI-0.6.0-02-promotion-command-lineage
  - OBPI-0.6.0-03-operator-narratives-and-auditability
```

Dry-run closeout and attestation first:

```bash
uv run gz closeout ADR-0.6.0-pool-promotion-protocol --dry-run
uv run gz attest ADR-0.6.0-pool-promotion-protocol --status completed --dry-run
```

Closeout dry-run excerpt:

```text
Dry run: no ledger event will be written.
  Would initiate closeout for: ADR-0.6.0-pool-promotion-protocol
  Gate 2 (TDD): uv run gz test
  Gate 3 (Docs): uv run mkdocs build --strict
  Gate 4 (BDD): uv run -m behave features/
  Gate 5 (Human): Awaiting explicit attestation
```

Then run non-dry commands and record receipts:

```bash
uv run gz closeout ADR-0.6.0-pool-promotion-protocol
uv run gz attest ADR-0.6.0-pool-promotion-protocol --status completed
uv run gz audit ADR-0.6.0-pool-promotion-protocol
uv run gz adr emit-receipt ADR-0.6.0-pool-promotion-protocol --event validated --attestor "Jeffry Babb" --evidence-json '{"scope":"ADR-0.6.0-pool-promotion-protocol","date":"2026-02-22"}'
```

If you want to inspect receipt payloads before writing events:

```bash
uv run gz obpi emit-receipt OBPI-0.6.0-03-operator-narratives-and-auditability --event completed --attestor "Jeffry Babb" --evidence-json '{"attestation":"I attest I understand the completion of OBPI-0.6.0-03.","date":"2026-02-22"}' --dry-run
uv run gz adr emit-receipt ADR-0.6.0-pool-promotion-protocol --event validated --attestor "Jeffry Babb" --evidence-json '{"scope":"ADR-0.6.0-pool-promotion-protocol","date":"2026-02-22"}' --dry-run
```

---

## Verification Checklist (OBPI + ADR)

- `uv run gz test`
- `uv run -m behave features/` (heavy lane)
- `uv run gz lint`
- `uv run gz format` (auto-fix formatting)
- `uv run gz typecheck`
- `uv run gz tidy`
- `uv run mkdocs build --strict`
- `uv run gz validate --documents`
- `uv run gz cli audit`
- `uv run gz check-config-paths`
- `uv run gz drift` (detect spec-test-code governance drift)
- `uv run gz check` (all quality checks + advisory drift)
- `uv run gz check --json` (machine-readable output with advisory drift section)
- `uv run gz adr audit-check ADR-<X.Y.Z>`
- `uv run gz adr covers-check ADR-<X.Y.Z>`
- `uv run gz adr report`
- `uv run gz adr status ADR-<X.Y.Z> --json`
- `uv run gz adr promote ADR-pool.<slug> --semver X.Y.Z`
- `uv run gz status --json`
- `uv run gz state --json`
- `uv run gz readiness audit`
- `uv run gz readiness evaluate`
- `uv run gz parity check`
- `uv run gz obpi status OBPI-<X.Y.Z-NN>`
- `uv run gz agent sync control-surfaces`

---

## Governance Planning Commands

```bash
# Create governance artifacts
uv run gz init                     # Initialize gzkit in a repository
uv run gz prd                      # Create a Product Requirements Document
uv run gz constitute               # Create a constitution artifact
uv run gz plan                     # Create an ADR
uv run gz specify                  # Create an implementation brief (OBPI)
uv run gz interview                # Run interactive governance interviews
uv run gz migrate-semver           # Record SemVer ID rename events
uv run gz register-adrs            # Register existing ADR packages into ledger
```

---

## Chores Commands

```bash
uv run gz chores list              # List declared chores
uv run gz chores show <slug>       # Display CHORE.md for one chore
uv run gz chores advise <slug>     # Dry-run criteria and report status
uv run gz chores plan <slug>       # Show plan details for one chore
uv run gz chores run <slug>        # Execute and log one chore
uv run gz chores audit --all       # Audit log presence for all chores
```

---

## Skill Commands

```bash
uv run gz skill new <name>         # Create a new skill scaffold
uv run gz skill list               # List all discovered skills
uv run gz skill audit              # Audit skill lifecycle metadata
```

---

## AirlineOps Parity Scan Canonical-Root Rules

When running parity scans, canonical root resolution is deterministic and fail-closed:

1. explicit override (if provided)
2. sibling path `../airlineops`
3. absolute fallback `/Users/jeff/Documents/Code/airlineops`

If none resolve, stop and report blockers. Do not claim parity completion without canonical-root evidence.

---

## Notes

- Do not run `gz audit` pre-attestation.
- Do not use OBPI-scoped receipt emission as a substitute for ADR completion attestation.
- Do not capture final OBPI completion receipts before `uv run gz git-sync --apply --lint --test` succeeds.
- `gz adr emit-receipt` remains available for ADR-level accounting and legacy scoped payload flows.
- For heavy lane, Gate 4 must pass before attestation.
- Historical files under `docs/user/reference/**` are archival and may contain legacy command examples; active operator command contracts are in `docs/user/commands/**` and CLI help output.
