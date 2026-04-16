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

> Skills add interview logic, forcing functions, and governance validation
> that bare CLI commands do not — **prefer the skill when one exists.**

### Step 1: Orientation + parent ADR context

| Skill (preferred) | CLI equivalent |
|---|---|
| `/gz-adr-status ADR-<X.Y.Z>` | `uv run gz adr status ADR-<X.Y.Z> --json` |
| `/gz-status` | `uv run gz status --table` |
| `/gz-adr-evaluate ADR-<X.Y.Z>` | `uv run gz adr evaluate ADR-<X.Y.Z>` |

```bash
# Validate OBPI briefs before pipeline (authored execution contracts only)
uv run gz obpi validate --adr ADR-<X.Y.Z> --authored
```

### Step 2: Execute the OBPI through the staged pipeline

| Skill (preferred) | CLI equivalent |
|---|---|
| `/gz-obpi-pipeline OBPI-<X.Y.Z-NN>` | `uv run gz obpi pipeline OBPI-<X.Y.Z-NN>` |

Compatibility entry points for partial re-runs:

```bash
uv run gz obpi pipeline OBPI-<X.Y.Z-NN> --from=verify
uv run gz obpi pipeline OBPI-<X.Y.Z-NN> --from=ceremony
```

> The CLI and generated Claude hooks share the same runtime engine in
> `src/gzkit/pipeline_runtime.py`. Treat active pipeline markers as
> runtime-managed state; do not clear them by hand.

```bash

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
#    Skill shortcuts — run all quality checks in one pass or with receipt artifacts:
#
#    | Skill (preferred) | CLI equivalent |
#    |---|---|
#    | /gz-check | uv run gz check |
#    | /gz-arb | uv run gz arb ruff; uv run gz arb step ... |
#    | /gz-implement | uv run gz implement --adr ADR-<X.Y.Z> |
#    | /gz-gates ADR-<X.Y.Z> | uv run gz gates --adr ADR-<X.Y.Z> |
#
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
#    The brief's Closing Argument section is authored at completion time
#    from delivered evidence — not copied from planning intent. It must
#    include: what was built (paths), what it enables (operator capability),
#    and why it matters (proof command or doc link).
#    Use parser-safe inline bullets in "Implementation Summary":
#      - Files created/modified: <paths>
#      - Tests added: <files or (none)>
#      - Date completed: YYYY-MM-DD
#    (Do not split values onto nested bullet lines.)

# 4b) (Heavy lane only) Produce ARB receipts for attestation-enrichment evidence
#     — `.claude/rules/attestation-enrichment.md` requires a receipt ID for every
#     claim category cited in Heavy-lane attestations (lint, typecheck, tests,
#     coverage). Run each wrapped QA step before drafting the attestation text.
uv run gz arb ruff src tests
uv run gz arb step --name typecheck -- uvx ty check . --exclude 'features/**'
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb validate --limit 20

# 5) Complete OBPI atomically (attestation + brief + receipt in one transaction)
#    Cite the ARB receipt IDs from step 4b in --attestation-text per
#    `.claude/rules/attestation-enrichment.md`.
uv run gz obpi complete OBPI-<X.Y.Z-NN>-<slug> --attestor "<name>" --attestation-text "<attestation>"
uv run gz obpi lock release OBPI-<X.Y.Z-NN>-<slug>

# 6) Run guarded sync, then reconcile and confirm
uv run gz git-sync --apply --lint --test
uv run gz obpi reconcile OBPI-<X.Y.Z-NN>-<slug>
uv run gz adr status ADR-<X.Y.Z> --json
uv run gz git-sync --apply --lint --test
```

---

## Storage Tiers and Recovery

The three tier model and pool archive governance is documented in
[`docs/governance/storage-tiers.md`](../governance/storage-tiers.md).
Every on-disk location is classified as Tier A (canonical), Tier B
(derived/rebuildable), or Tier C (external/ADR-required).

The storage catalog and escalation governance rules ensure no external
runtime dependency is introduced without a Heavy-lane ADR. See
`AGENTS.md` for the agent-facing constraint.

Git clone recovery is guaranteed for all Tier A + B state:

```bash
git clone <repo-url>
cd gzkit
uv sync
uv run gz agent sync control-surfaces   # Rebuild Tier B mirrors
uv run gz lint                           # Verify tooling works
uv run gz test                           # Verify tests pass
```

---

## State Repair (Recovery Tool)

The three layer model documentation lives in `docs/governance/state-doctrine.md`. When frontmatter (L3 cache) drifts from
ledger-derived state (L2 authority), use `gz state --repair` to
force-reconcile all OBPI brief frontmatter:

```bash
uv run gz state --repair           # Human-readable diff report
uv run gz state --repair --json    # Machine-readable JSON output
```

The repair command is idempotent (running twice produces no changes on second
run) and works after `git clone` with no dependency on L3 caches or markers.

Pipeline markers are Layer 3 artifacts with a documented marker migration path
to Layer 2 ledger events (see `docs/governance/pipeline-marker-migration-path.md`).

---

## Drift Control (Required Before Closeout)

Until ledger-derived brief sync is automated, treat OBPI brief status/date fields as drift-prone and
always recompute truth from `gz` status surfaces before closeout:

Skill shortcuts for drift detection and reconciliation:

- [`/gz-adr-check`](skills/gz-adr-check.md) — run blocking ADR evidence checks for a target ADR
- [`/gz-adr-recon`](skills/gz-adr-recon.md) — reconcile ADR/OBPI evidence state from ledger outputs
- [`/gz-adr-status`](skills/gz-adr-status.md) — focused ADR drilldown with lifecycle and OBPI detail

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

## Loop C: Patch Release (GHI-Driven)

Run after a batch of qualifying GHIs has been merged and you want to ship them
as a patch release. The ceremony discovers GHIs since the last tag, computes
the next patch version, writes a release manifest, and bumps the version
across `pyproject.toml`, `src/gzkit/__init__.py`, and `RELEASE_NOTES.md`.

Skill shortcut: [`/gz-patch-release`](skills/gz-patch-release.md) — orchestrates
narrative release notes drafting, operator approval, RELEASE_NOTES update,
git-sync, and the GitHub release.

```bash
# 1) Discover qualifying GHIs (does not modify state)
uv run gz patch release --dry-run

# 2) Inspect machine-readable discovery output
uv run gz patch release --dry-run --json

# 3) Execute the release: writes docs/releases/PATCH-vX.Y.Z.md,
#    bumps the version everywhere, appends a ledger event
uv run gz patch release

# 4) Sync the staged release manifest and version bumps
uv run gz git-sync --apply --lint --test

# 5) Tag and publish the GitHub release (skill recommended)
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file RELEASE_NOTES.md
```

The discovery JSON includes `ghi_count`, `qualifications` (per-GHI status:
`qualified`/`label_only`/`diff_only`/`excluded`), `current_version`,
`proposed_version`, and `warnings`. Review the qualification list before
running step 3 — `label_only` and `diff_only` GHIs surface warnings the
operator should resolve before shipping.

---

## Loop B: ADR Closeout (After OBPI Batch Completion)

Run this only when linked OBPIs are complete and evidenced.

Skill shortcuts for the closeout ceremony:

- [`/gz-closeout`](skills/gz-closeout.md) — initiate ADR closeout with evidence context (dry-run first)
- [`/gz-attest`](skills/gz-attest.md) — record human attestation with prerequisite enforcement
- [`/gz-audit`](skills/gz-audit.md) — run strict post-attestation reconciliation audits
- [`/gz-adr-closeout-ceremony`](skills/gz-adr-closeout-ceremony.md) — execute the full closeout ceremony protocol
- [`/gz-adr-emit-receipt`](skills/gz-adr-emit-receipt.md) — emit ADR receipt events with scoped evidence payloads

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

After the Heavy-lane ceremony is accepted, complete the OBPI atomically, then sync and reconcile:

```bash
uv run gz obpi complete OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity --attestor "Jeffry" --attestation-text "I attest I understand the completion of OBPI-0.5.0-05."
uv run gz obpi lock release OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity
uv run gz git-sync --apply --lint --test
uv run gz obpi reconcile OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity
uv run gz git-sync --apply --lint --test
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
uv run gz adr emit-receipt ADR-0.6.0-pool-promotion-protocol --event validated --attestor "Jeffry" --evidence-json '{"scope":"ADR-0.6.0-pool-promotion-protocol","date":"2026-02-22"}'
```

If you want to inspect receipt payloads before writing events:

```bash
uv run gz obpi emit-receipt OBPI-0.6.0-03-operator-narratives-and-auditability --event completed --attestor "Jeffry" --evidence-json '{"attestation":"I attest I understand the completion of OBPI-0.6.0-03.","date":"2026-02-22"}' --dry-run
uv run gz adr emit-receipt ADR-0.6.0-pool-promotion-protocol --event validated --attestor "Jeffry" --evidence-json '{"scope":"ADR-0.6.0-pool-promotion-protocol","date":"2026-02-22"}' --dry-run
```

---

## Test Traceability and Coverage Adoption

Use `@covers` decorators to link tests to governance requirements. Coverage
reporting is informational --- no tests break if annotations are absent.

```bash
# Check current coverage for an ADR
uv run gz covers ADR-<X.Y.Z>

# Check coverage for a single OBPI
uv run gz covers OBPI-<X.Y.Z-NN>

# Full summary across all ADRs
uv run gz covers

# Machine-readable coverage report
uv run gz covers --json
```

### Annotating Tests During OBPI Work

When implementing an OBPI, annotate your tests as you write them:

```python
from gzkit.traceability import covers

@covers("REQ-X.Y.Z-NN-MM")
def test_my_feature(self):
    ...
```

After annotating, verify coverage improved:

```bash
uv run gz covers OBPI-<X.Y.Z-NN>
```

### Non-Python Tests

Non-Python test stacks use comment-based annotations:

```text
// @covers REQ-X.Y.Z-NN-MM
```

These are valid governance proof for manual audits but are not yet
discovered by `gz covers`. See
[Test Traceability concept guide](concepts/test-traceability.md)
for full details and migration guidance.

---

## Verification Checklist (OBPI + ADR)

Use [`/gz-check`](skills/gz-check.md) to run all quality checks in one pass, or [`/gz-arb`](skills/gz-arb.md) for the same checks with structured JSON receipt artifacts.

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
- `uv run gz preflight` (detect stale markers and orphan receipts)
- `uv run gz preflight --apply` (clean up stale artifacts)
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
- `uv run gz obpi withdraw OBPI-<X.Y.Z-NN> --reason "..."` (withdraw an OBPI from counts)
- `uv run gz obpi audit OBPI-<X.Y.Z-NN>` (gather evidence and record in audit ledger)
- `uv run gz obpi lock claim OBPI-<X.Y.Z-NN>` (claim an OBPI work lock)
- `uv run gz obpi lock release OBPI-<X.Y.Z-NN>` (release an OBPI work lock)
- `uv run gz obpi lock check OBPI-<X.Y.Z-NN>` (check if an OBPI is locked)
- `uv run gz obpi lock list` (list active OBPI work locks)
- `uv run gz plan create <name> --semver X.Y.Z` (create a new ADR)
- `uv run gz plan audit OBPI-<X.Y.Z-NN>` (structural prerequisite check for plan-OBPI alignment; scans both `<project>/.claude/plans/` and `~/.claude/plans/` — see #128)
- `uv run gz patch release` (GHI-driven patch release ceremony; writes manifest and bumps version)
- `uv run gz patch release --dry-run` (preview GHI discovery and proposed version without modifying state)
- `uv run gz patch release --dry-run --json` (machine-readable discovery output)
- `uv run gz agent sync control-surfaces`

> **Plan file locations:** Claude Code's plan mode writes new plans to
> `~/.claude/plans/` (the global user directory) by default. `gz plan audit`
> and the plan-audit-gate hook search both `<project>/.claude/plans/` and
> `~/.claude/plans/` and copy a matching global plan into the project-local
> directory so the plan, the audit receipt, and the pipeline marker stay
> co-located. Project-local always wins on a tie.

---

## Governance Planning Commands

Skill shortcuts for governance planning — these provide guided workflows beyond the raw CLI:

- [`/gz-design`](skills/gz-design.md) — collaborative design dialogue that produces GovZero ADR artifacts
- [`/gz-adr-create`](skills/gz-adr-create.md) — create and book a GovZero ADR with its OBPI briefs
- [`/gz-plan`](skills/gz-plan.md) — create ADR artifacts for planned change
- [`/gz-specify`](skills/gz-specify.md) — create OBPI briefs linked to parent ADR items
- [`/gz-adr-promote`](skills/gz-adr-promote.md) — promote a pool ADR into canonical ADR package structure
- [`/gz-interview`](skills/gz-interview.md) — run interactive governance interviews for structured input

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

Use [`/gz-chore-runner`](skills/gz-chore-runner.md) to run a chore end-to-end (show, plan, advise, execute, validate) through a guided workflow.

```bash
uv run gz chores list              # List declared chores
uv run gz chores show <slug>       # Display CHORE.md for one chore
uv run gz chores advise <slug>     # Dry-run criteria and report status
uv run gz chores plan <slug>       # Show plan details for one chore
uv run gz chores run <slug>        # Execute and log one chore
uv run gz chores audit --all       # Audit log presence for all chores
```

---

## Task Commands

```bash
uv run gz task list OBPI-<X.Y.Z-NN>       # List tasks for an OBPI
uv run gz task list OBPI-<X.Y.Z-NN> --json # JSON output
uv run gz task start TASK-<id>             # Start a pending task
uv run gz task complete TASK-<id>          # Complete an in-progress task
uv run gz task block TASK-<id> --reason "..." # Block with reason
uv run gz task escalate TASK-<id> --reason "..." # Escalate with reason
```

---

## Persona Commands

Agent persona definitions live in `.gzkit/personas/` as the canonical control
surface (ADR-0.0.11). The persona research synthesis
(`docs/design/research-persona-selection-agent-identity.md`) distills five
mechanistic studies into design principles that ground trait composition.
The earlier `ADR-pool.per-command-persona-context` has been superseded;
operators should supersede pool persona context references with the
ADR-0.0.11 lineage.

```bash
uv run gz personas list              # List loaded persona definitions
uv run gz personas list --json       # Machine-readable persona output
```

---

## Adopter Feedback

File bug reports, feature requests, or observations via GitHub Issues:

- **Defect:** [File a defect report](https://github.com/tvproductions/gzkit/issues/new?template=defect.yml)
- **Enhancement:** [Request a feature](https://github.com/tvproductions/gzkit/issues/new?template=enhancement.yml)
- **Observation:** [Share an observation](https://github.com/tvproductions/gzkit/issues/new?template=observation.yml)

Include your gzkit version (`gz --version`), Python version, and platform.
The issue templates prompt for this automatically.

---

## Skill Commands

```bash
uv run gz skill new <name>         # Create a new skill scaffold
uv run gz skill list               # List all discovered skills
uv run gz skill audit              # Audit skill lifecycle metadata
```

### Skill Documentation Resources

The [documentation taxonomy](../governance/documentation-taxonomy.md) defines which
artifact types require manpages, runbook skill entries, and docstrings. The
[skill manpage template](skills/_TEMPLATE.md) prescribes 6 required sections for
operator-facing skill manpages. The [skills surface and index](skills/index.md) provides
a categorized catalog of all 52+ skills. Pilot skill manpages validate the template
across 3 categories — see the skills index for the full list.

---

## AirlineOps Parity Scan Canonical-Root Rules

Use [`/airlineops-parity-scan`](skills/airlineops-parity-scan.md) to run the full repeatable governance parity scan between airlineops and gzkit.

When running parity scans, canonical root resolution is deterministic and fail-closed:

1. explicit override (if provided)
2. sibling path `../airlineops`
3. absolute fallback `/Users/jeff/Documents/Code/airlineops`

If none resolve, stop and report blockers. Do not claim parity completion without canonical-root evidence.

---

## Feature Flags

Feature flags control behavior transitions --- phased rollout of new
checks, kill switches for risky behavior, and migration paths between
old and new internals.

See [Feature Flag System](../governance/feature-flags.md) for the full
architecture (categories, lifecycle, precedence, toggle point rules).

### List all flags

```bash
uv run gz flags
uv run gz flags --stale    # only flags past their deadline
uv run gz flags --json     # machine-readable output
```

### Inspect a single flag

```bash
uv run gz flag explain ops.product_proof
```

Shows the resolved value, which precedence layer provided it,
deadlines, and linked ADR/issue.

### Check for stale flags

Stale flags are past their `review_by` (ops) or `remove_by`
(release/migration/development) deadline:

```bash
uv run gz flags --stale
```

A CI time-bomb test fails if any flag is overdue, so stale flags
should be addressed promptly --- either extend the deadline after
review or remove the flag and its code paths.

### Override a flag via `.gzkit.json`

Add a `flags` section to your project config:

```json
{
  "mode": "lite",
  "flags": {
    "ops.product_proof": false
  }
}
```

### Override a flag via environment variable

Replace dots with underscores, uppercase, prefix with `GZKIT_FLAG_`:

```bash
GZKIT_FLAG_OPS_PRODUCT_PROOF=false uv run gz closeout ADR-0.1.0
```

Valid values: `true`, `1`, `yes`, `false`, `0`, `no`
(case-insensitive).

---

## Notes

- Do not run `gz audit` pre-attestation.
- Do not use OBPI-scoped receipt emission as a substitute for ADR completion attestation.
- `gz obpi complete` handles attestation, brief update, and receipt emission atomically — run it before git-sync.
- `gz obpi emit-receipt` remains available for manual non-pipeline use; `gz adr emit-receipt` for ADR-level accounting.
- For heavy lane, Gate 4 must pass before attestation.
- Historical files under `docs/user/reference/**` are archival and may contain legacy command examples; active operator command contracts are in `docs/user/commands/**` and CLI help output.
