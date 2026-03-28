<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Governance Runbook (gzkit)

**Purpose:** Operator procedures for executing GovZero workflows in gzkit: ADR/OBPI lifecycle work, reconciliation, closeout, audit, and parity maintenance.

**Version:** GovZero v6 extraction surface
**Scope:** Governance operations in this repository
**Companion:** [Operator Runbook](../user/runbook.md) (daily execution loop)

This document is procedural ("how to"), not policy ("what the rules are"). Canonical policy remains in `docs/governance/GovZero/**`.

---

## Governance Quick Reference

### Status and health

```bash
uv run gz status --table
uv run gz adr status ADR-<X.Y.Z> --json
uv run gz adr report
uv run gz state --json
uv run gz adr audit-check ADR-<X.Y.Z>
uv run gz adr covers-check ADR-<X.Y.Z>
uv run gz gates --adr ADR-<X.Y.Z>
uv run gz obpi status OBPI-<X.Y.Z-NN>
uv run gz roles
```

### Lifecycle execution

```bash
uv run gz init                        # Initialize governance scaffolding
uv run gz prd                         # Create Product Requirements Document
uv run gz constitute                  # Create constitution artifact
uv run gz plan                        # Create an ADR
uv run gz specify                     # Create implementation brief (OBPI)
uv run gz obpi pipeline OBPI-<X.Y.Z-NN>  # Execute OBPI pipeline
uv run gz obpi reconcile OBPI-<X.Y.Z-NN> # Fail-closed reconciliation
uv run gz obpi withdraw OBPI-<X.Y.Z-NN> --reason "..." # Withdraw OBPI from counts
uv run gz obpi emit-receipt OBPI-<X.Y.Z-NN> --event completed --attestor "<name>" --evidence-json '{...}'
uv run gz migrate-semver              # Record SemVer rename events
uv run gz register-adrs               # Register existing ADR packages
```

Skill-based entry points:

```text
/gz-adr-create
/gz-adr-manager   # compatibility alias for /gz-adr-create
/gz-obpi-brief
/gz-obpi-pipeline OBPI-<X.Y.Z-NN>
/gz-obpi-reconcile ADR-<X.Y.Z>
/gz-adr-recon ADR-<X.Y.Z>
/gz-adr-sync
```

### Validation and proof surfaces

```bash
uv run gz cli audit
uv run gz check-config-paths
uv run gz validate --documents --surfaces
uv run gz preflight                           # Detect stale artifacts
uv run gz obpi validate --adr ADR-<X.Y.Z>
uv run gz adr evaluate ADR-<X.Y.Z>
uv run gz readiness evaluate
uv run gz parity check
uv run mkdocs build --strict
```

---

## Concepts

### Gate system

| Gate | Name | Verification |
|---|---|---|
| 1 | ADR recorded | `uv run gz validate --documents` |
| 2 | TDD | `uv run gz test` |
| 3 | Docs | `uv run gz lint` + `uv run mkdocs build --strict` |
| 4 | BDD | `features/` scenarios if present |
| 5 | Human attestation | `uv run gz attest ADR-<X.Y.Z> --status completed` |

Lane rule: `lite` requires Gates 1-2; `heavy` requires Gates 1-5.

### Layered trust

| Layer | Trust source | Typical tooling |
|---|---|---|
| 1 | Runtime evidence generation | `gz implement`, `gz gates`, `gz adr audit-check` |
| 2 | Ledger-driven reconciliation | `/gz-obpi-reconcile`, `/gz-adr-recon`, `gz audit` |
| 3 | File sync and indexing | `/gz-obpi-sync`, `/gz-adr-sync`, `gz agent sync control-surfaces` |

### OBPI discipline

- OBPI is the atomic implementation unit.
- ADR status is a roll-up of OBPI completion plus attestation.
- **Lane inheritance:** If the parent ADR is Heavy or Foundation (0.0.x), human attestation is required for all OBPIs regardless of their individual lane designation.

### ADR series selection

When creating or promoting an ADR, pick the next available version in the correct series:

- **0.0.x (Foundation):** Infrastructure, governance framework, developer tooling. No GitHub releases.
- **0.x.0+ (Feature):** User-facing capability, external contracts, observable behavior changes. Release tags created on validation.

---

## Workflow: Create or Promote ADR

**When:** New governance work must be planned.

1. Inspect active and pending ADR state.

```bash
uv run gz status --table
```

2. If promoting from pool, use deterministic promotion.

```bash
uv run gz adr promote ADR-pool.<slug> --semver X.Y.Z --status proposed
```

3. Create or update OBPI briefs for checklist items.

```text
/gz-obpi-brief
```

4. Validate briefs are authored (not template stubs).

```bash
uv run gz obpi validate --adr ADR-<X.Y.Z>
```

5. Evaluate ADR and OBPI quality before proceeding.

```bash
uv run gz adr evaluate ADR-<X.Y.Z>
```

A NO GO verdict blocks pipeline execution. Address action items and re-evaluate.

6. Validate artifact and document integrity.

```bash
uv run gz validate --documents
uv run gz check-config-paths
```

---

## Workflow: OBPI Increment

**When:** Implementing one checklist item.

1. Orient on current state and the parent ADR.

```bash
uv run gz adr status ADR-<X.Y.Z> --json
uv run gz status --table
```

2. Validate the target brief is authored (not a template stub).

```bash
uv run gz obpi validate <path-to-brief>
```

3. Plan the OBPI and exit plan mode with an approved plan.
4. Invoke the OBPI execution pipeline.

```text
/gz-obpi-pipeline OBPI-<X.Y.Z-NN>
```

Use compatibility entry points when implementation or verification already
exists:

```text
/gz-obpi-pipeline OBPI-<X.Y.Z-NN> --from=verify
/gz-obpi-pipeline OBPI-<X.Y.Z-NN> --from=ceremony
```

4. Inside the pipeline, implement + verify Gate 2 (+ Gate 3 when docs change).

```bash
uv run gz implement --adr ADR-<X.Y.Z>
uv run gz gates --adr ADR-<X.Y.Z>
uv run gz lint
```

5. Present the OBPI acceptance ceremony before marking the brief `Completed`.
6. Sync audit and ADR table state after the ceremony.

Pipeline rules:

- verify -> ceremony -> sync is mandatory
- Heavy/Foundation work stays fail-closed on human attestation
- if concurrent execution is needed before lock parity exists, stop with
  `BLOCKERS`

---

## Workflow: Reconciliation and Drift Detection

**When:** Before closeout, after multi-session work, or when status drift is suspected.

Run in trust order:

```text
/gz-obpi-reconcile ADR-<X.Y.Z>   # Layer 2
/gz-adr-recon ADR-<X.Y.Z>        # Layer 2
/gz-adr-sync                     # Layer 3
```

Then verify no unresolved evidence gaps:

```bash
uv run gz adr audit-check ADR-<X.Y.Z>
uv run gz adr status ADR-<X.Y.Z> --json
```

If `audit-check` fails, fix the referenced OBPI brief evidence and rerun until PASS.

---

## Workflow: ADR Closeout and Audit

**When:** All linked OBPIs are completed and evidenced.

1. Pre-closeout blocking check.

```bash
uv run gz adr audit-check ADR-<X.Y.Z>
```

2. Closeout ceremony initiation (dry-run first, then live).

```bash
uv run gz closeout ADR-<X.Y.Z> --dry-run
uv run gz closeout ADR-<X.Y.Z>
```

3. Human attestation.

```bash
uv run gz attest ADR-<X.Y.Z> --status completed
```

4. Post-attestation audit and accounting.

```bash
uv run gz audit ADR-<X.Y.Z>
uv run gz adr emit-receipt ADR-<X.Y.Z> --event validated --attestor "<Human Name>" --evidence-json '{"scope":"ADR-<X.Y.Z>","date":"YYYY-MM-DD"}'
```

Rules:

- Do not run `gz audit` before attestation.
- Do not treat passing checks as implied attestation.
- Record attestation terms explicitly (`Completed`, `Completed — Partial: <reason>`, `Dropped — <reason>`).

---

## Workflow: Task-Level Governance

**When:** Managing TASK entities (fourth tier: ADR > OBPI > REQ > TASK).

```bash
uv run gz task list OBPI-<X.Y.Z-NN>              # List tasks for an OBPI
uv run gz task start TASK-<id>                    # Start a pending task
uv run gz task complete TASK-<id>                 # Complete an in-progress task
uv run gz task block TASK-<id> --reason "..."     # Block with reason
uv run gz task escalate TASK-<id> --reason "..."  # Escalate with reason
```

---

## Workflow: Chores and Maintenance

**When:** Running scheduled maintenance, code quality checks, or repository hygiene.

```bash
uv run gz chores list                      # List declared chores
uv run gz chores show <slug>               # Display CHORE.md for one chore
uv run gz chores advise <slug>             # Dry-run criteria and report status
uv run gz chores plan <slug>               # Show plan details for one chore
uv run gz chores run <slug>                # Execute and log one chore
uv run gz chores audit --all               # Audit log presence for all chores
```

Maintenance gate commands:

```bash
uv run gz tidy                             # Run maintenance checks
uv run gz format                           # Auto-format code
uv run gz typecheck                        # Static type checks
uv run gz drift                            # Detect spec-test-code drift
uv run gz covers ADR-<X.Y.Z>              # Trace test-to-requirement coverage
uv run gz skill new <name>                 # Create a new skill scaffold
uv run gz skill list                       # List all discovered skills
uv run gz interview                        # Run interactive governance interviews
```

---

## Workflow: Session Handoffs

**When (MUST):**

- Session ending with incomplete OBPI work
- Scope switch between ADRs
- Explicit human request

**Procedure:**

```text
/gz-session-handoff CREATE
/gz-session-handoff RESUME
```

Staleness handling:

- `Fresh` (<24h) resume directly.
- `Slightly stale` (24-72h) resume with explicit verification.
- `Stale` (>72h) or `Very stale` (>7d) require human re-validation before proceeding.

---

## Workflow: Parity Maintenance Against AirlineOps

**When:** Weekly cadence, before pool ADR promotion, or after canonical governance changes in AirlineOps.

Filter rule:

- Apply the [Parity Intake Rubric](parity-intake-rubric.md) to each candidate import before implementation.

1. Resolve canonical root deterministically and fail closed.

```bash
test -d ../airlineops && test -d .
```

2. Run parity-scan ritual checks.

```bash
uv run gz cli audit
uv run gz check-config-paths
uv run gz adr audit-check ADR-<target>
uv run mkdocs build --strict
```

3. Write dated reports.

- `docs/proposals/REPORT-airlineops-parity-YYYY-MM-DD.md`
- `docs/proposals/REPORT-airlineops-govzero-mining-YYYY-MM-DD.md`

4. Convert each `Missing`, `Divergent`, or high-impact `Partial` item into tracked ADR/OBPI follow-up.

Compatibility note:

- `gz-adr-create` is canonical in gzkit.
- `gz-adr-manager` is retained as a legacy alias for cross-repository parity.

---

## Workflow: Skill Maintenance and Deprecation Operations

**When:** Weekly hygiene cadence, before ADR closeout touching skills, or when deprecating/retiring any skill.

1. Run lifecycle audit with explicit cadence threshold.

```bash
uv run gz skill audit --json --max-review-age-days 90
```

2. If stale review findings exist, update canonical `.gzkit/skills/*/SKILL.md`:

- set `last_reviewed` to current review date,
- confirm `owner` remains accurate,
- re-run audit until stale findings are zero.

3. If a skill is `deprecated` or `retired`, ensure metadata evidence is present:

- `deprecation_replaced_by`
- `deprecation_migration`
- `deprecation_communication`
- `deprecation_announced_on`
- `retired_on` (retired only)

4. Sync mirrors from canonical source of truth.

```bash
uv run gz agent sync control-surfaces
uv run gz skill audit
```

Rules:

- Canonical `.gzkit/skills` is authoritative; mirrors are derived artifacts.
- Do not deprecate/retire without communication and migration evidence.
- Do not bypass stale review failures; they are blocking policy failures.

---

## Workflow: Git Sync Ritual

```bash
uv run gz git-sync
uv run gz git-sync --apply --lint --test
```

Rules:

- No `--no-verify`.
- No force push.
- Keep governance docs, runbook, and command references synchronized in the same change set.

---

## Workflow: Readiness-Driven Design

```bash
uv run gz readiness audit
uv run gz readiness audit --json > docs/proposals/AUDIT-agent-readiness-gzkit-YYYY-MM-DD.json
```

Use readiness as a design input, not a one-time score:

1. Run `gz readiness audit` before parity extraction or major governance edits.
2. Cross-check findings against [`docs/user/reference/agent-input-disciplines.md`](../user/reference/agent-input-disciplines.md) and record which discipline/primitive each gap maps to.
3. Capture a dated audit artifact in `docs/proposals/`.
4. Convert the top three gaps into tracked ADR/OBPI follow-up work.
5. Use Gate 2 (TDD) and Gate 4 (BDD) evidence as primary inputs for acceptance/evaluation improvements.
6. Re-run readiness after implementation and record score delta in the same proposal.
7. Only claim maturity improvements when quality gates (`gz check`) also pass.

---

## Quick Governance Checklist

### Before starting OBPI work

- [ ] `uv run gz status --table`
- [ ] `uv run gz adr status ADR-<X.Y.Z> --json`
- [ ] Brief scope and acceptance criteria reviewed
- [ ] Existing handoff reviewed if present

### Before requesting ADR closeout

- [ ] `/gz-obpi-reconcile ADR-<X.Y.Z>` complete
- [ ] `/gz-adr-recon ADR-<X.Y.Z>` complete
- [ ] `uv run gz adr audit-check ADR-<X.Y.Z>` passes
- [ ] `uv run gz closeout ADR-<X.Y.Z> --dry-run` reviewed

### After closeout

- [ ] `uv run gz attest ADR-<X.Y.Z> --status completed`
- [ ] `uv run gz audit ADR-<X.Y.Z>`
- [ ] ADR-level receipt emitted
- [ ] `/gz-adr-sync` run

---

## Reference Links

- [GovZero Charter](GovZero/charter.md)
- [ADR Lifecycle](GovZero/adr-lifecycle.md)
- [Audit Protocol](GovZero/audit-protocol.md)
- [Agent Readiness Audit Template](GovZero/audits/AUDIT-TEMPLATE-agent-readiness.md)
- [Agent-Era Prompting Summary (Nate B. Jones)](GovZero/agent-era-prompting-summary.md)
- [Agent Input Disciplines: Practitioner Reference](../user/reference/agent-input-disciplines.md)
- [Gate 5 Architecture](GovZero/gate5-architecture.md)
- [Layered Trust](GovZero/layered-trust.md)
- [Session Handoff Obligations](GovZero/session-handoff-obligations.md)
- [Staleness Classification](GovZero/staleness-classification.md)
