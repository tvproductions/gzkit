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

## Loop 0: First-Time Operator (Empty Repo → First Attested Release)

> **When to use:** you are bootstrapping a new gzkit-governed project from
> an empty directory and need the on-ramp to the daily Loop A and the
> per-release Loop C. Run Loop 0 once per project; thereafter daily
> execution lives in Loop A.

The eight bootstrap stages compose the journey from `mkdir` to a tagged,
attested patch release. Each stage names the skill (preferred) and the
CLI verb. For the narrative account of why these stages compose this way
— what value flows through each — see the storybook arc
[`storybook/from-init-to-first-attested-release.md`](storybook/from-init-to-first-attested-release.md).

| # | Stage | Skill (preferred) | CLI verbs |
|---|-------|-------------------|-----------|
| 1 | Scaffolding | `/gz-init` | `uv tool install py-gzkit`; `gz init` |
| 2 | Intent (PRD → Constitution → Design) | `/gz-prd`, `/gz-constitute`, `/gz-design` | `uv run gz prd`; `uv run gz constitute` |
| 3 | Decomposition (ADR → OBPI) | `/gz-plan`, `/gz-adr-create`, `/gz-obpi-specify` | `uv run gz plan create <name> --semver X.Y.Z`; `uv run gz specify <slug> --parent ADR-<X.Y.Z> --item <N>` |
| 4 | Pre-execution reasoning | `/gz-justify`, `/gz-plan-audit` | `uv run gz justify <anchor> --save`; `uv run gz justify validate <path>` |
| 5 | Implementation | `/gz-obpi-pipeline`, `/gz-arb` | `uv run gz obpi pipeline OBPI-<X.Y.Z-NN>` |
| 6 | Verification (Gates 1–5) | `/gz-check`, `/gz-implement`, `/gz-gates` | `uv run gz check`; `uv run gz gates --adr ADR-<X.Y.Z>` |
| 7 | Closeout | `/gz-adr-closeout-ceremony`, `/gz-adr-audit`, `/gz-adr-emit-receipt` | `uv run gz closeout ADR-<X.Y.Z>`; `uv run gz attest ADR-<X.Y.Z> --status completed`; `uv run gz audit ADR-<X.Y.Z>`; `uv run gz adr emit-receipt ADR-<X.Y.Z> --event validated --attestor "<Name>" --evidence-json '{"scope":"ADR-<X.Y.Z>","date":"YYYY-MM-DD"}'` |
| 8 | Release (GHI-driven patch) | `/gz-patch-release` | `uv run gz patch release --full` |

### First-time setup acceptance

You have completed Loop 0 when:

- `uv run gz status --table` lists at least one validated ADR with Gates 1–5 marked pass
- `uv run gz adr report` shows the ADR in the Foundation or Feature table (not Pool)
- `uv run gz patch release --dry-run` reports a `qualified` GHI count ≥ 1
- A tagged release exists on GitHub (`gh release list`)

After Loop 0, daily iteration moves to [Loop A: OBPI Increment](#loop-a-obpi-increment-primary-daily-loop). End-of-batch release accounting moves to [Loop C: Patch Release (GHI-Driven)](#loop-c-patch-release-ghi-driven).

> **Quickstart vs. Loop 0:** the [Quickstart](quickstart.md) walks a single
> ADR cycle end-to-end as a tutorial. Loop 0 is the runbook anchor that
> classifies the same journey into named stages with skill/CLI parity so
> an operator can return to any stage by reference without re-reading the
> tutorial flow.

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

### Step 1b: Pre-execution reasoning walkthrough (`gz justify`)

When self-reported confidence in the planned implementation is below
the Prime Directive invariant 11 threshold (90% — see
`AGENTS.md` § Behavior Rules — Always, item 7), or when an upstream
quality signal recommends it, scaffold an 8-section reasoning
walkthrough before Step 2 begins. The CLI is deterministic: every byte
of the scaffold comes from the renderer, never from an LLM.

| Anchor type | When to invoke | Example |
|-------------|----------------|---------|
| GHI issue | Defect fix where root cause is uncertain | `uv run gz justify GHI-<N> --save` |
| OBPI brief | Heavy-lane OBPI with ambiguous scope or evidence | `uv run gz justify OBPI-<X.Y.Z-NN> --save` |
| Draft text | Pre-decision exploration before a brief exists | `uv run gz justify --draft "outline" --save --draft-slug <slug>` |

Fill the saved scaffold's `_[To be filled]_` blocks with grounded
reasoning. Before citing the artifact in OBPI Key Proof or ADR
Evidence, validate completeness:

```bash
uv run gz justify validate artifacts/justify/<saved-file>.md
```

Exit 0 confirms every section is filled. Exit 1 lists which sections
remain so the operator can finish before attesting. The pipeline's
Stage 1→2 Confidence Gate routes operators here automatically when
self-reported confidence is low; this section documents the same
operator move outside the pipeline.

See [`commands/justify.md`](commands/justify.md) for the full command
contract and [manpages/gz-justify.md](manpages/gz-justify.md) for the
exit-code matrix and option reference.

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
>
> Stale-marker self-heal (GHI #399): if a previous pipeline run was
> interrupted before Stage 5 cleanup fired, its `.pipeline-active-*`
> marker survives as an orphan. The launcher now auto-purges any
> orphaned marker whose OBPI is `attested_completed` in the ledger
> before running the concurrency check, and records the cleanup as a
> `pipeline_marker_purged` ledger event. Operators no longer need to
> `rm` marker files; just re-invoke `uv run gz obpi pipeline …` and
> the orphan clears itself.

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

# 4b) (Heavy lane only) Produce ARB receipts for attestation evidence
#     — `AGENTS.md` § Attestation requires a receipt ID for every
#     claim category cited in Heavy-lane attestations (lint, typecheck, tests,
#     coverage). Run each wrapped QA step before drafting the attestation text.
#     Citation is mechanically verified by `gz validate --attestation-receipts`
#     inside `gz obpi complete` / `gz adr emit-receipt` on heavy or foundation
#     work (fail-closed; ADR-0.0.24).
uv run gz arb ruff src tests
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb coverage run -m unittest discover -s tests -t .
uv run gz arb validate --limit 20
uv run gz arb advise --limit 10       # optional: review frequent-rule advice
uv run gz arb patterns --compact      # optional: scan for recurring anti-patterns

# 5) Complete OBPI atomically (attestation + brief + receipt in one transaction)
#    Cite the ARB receipt IDs from step 4b in --attestation-text per
#    `AGENTS.md` § Attestation.
uv run gz obpi complete OBPI-<X.Y.Z-NN>-<slug> --attestor "<name>" --attestation-text "<attestation>"
uv run gz obpi lock release OBPI-<X.Y.Z-NN>-<slug>

# 6) Run guarded sync, then reconcile and confirm
uv run gz git-sync --apply --lint --test
uv run gz obpi reconcile OBPI-<X.Y.Z-NN>-<slug>
uv run gz adr status ADR-<X.Y.Z> --json
uv run gz git-sync --apply --lint --test
```

---

## Cross-Repo Defect Filing (gzkit-Owned Surfaces)

When working **inside a gzkit-consuming repository** and you find a defect or
enhancement against a **gzkit-owned surface** — the `gz` CLI itself, schemas in
`src/gzkit/schemas/`, validator scopes (`gz validate --<scope>`), ledger event
semantics, files under `.gzkit/**` or `src/gzkit/**`, or rules under
`.gzkit/rules/**` — file the issue at `tvproductions/gzkit` (not at the
consumer's tracker) using the canonical wrapper:

```bash
# Preview before live filing (recommended for first use)
uv run gz issue file \
  --title "validator scope X mishandles inherited frontmatter" \
  --body "gz validate --documents miscounts adr-status drift in nested OBPIs" \
  --defect \
  --dry-run

# Live file once the body looks right
uv run gz issue file \
  --title "validator scope X mishandles inherited frontmatter" \
  --body "gz validate --documents miscounts adr-status drift in nested OBPIs" \
  --defect
```

The wrapper auto-stamps a `Filed from <consumer-repo-slug> running gz vX.Y.Z`
provenance trailer at the top of the body and routes the issue against
`tvproductions/gzkit` regardless of the consuming repo's `git remote`. Bodies
that reference no gzkit-owned surface marker (`gz <verb>`, `.gzkit/`,
`src/gzkit/`, or `gzkit.<module>`) are **hard-rejected** with exit code 1 — the
misrouting failure class is closed structurally per
`.gzkit/rules/agent-failure-modes.md` § Safeguard circumvention.

Defects in **consumer-repo** code, content, or governance go to the consumer's
own tracker via plain `gh issue create`. The asymmetry is intentional: consumer
repos own their remediation surface; gzkit owns its.

Authoritative routing table: `.gzkit/rules/gh-cli.md` § Cross-repo filing.
Manpage: `docs/user/manpages/gz-issue.md`.

---

## Cross-Version Upgrade (`gz init --update`)

When `pip install --upgrade py-gzkit` brings a newer wheel into an existing
adopter project, the new wheel may carry updated canonical content for
skills, rules, chores, personas, and templates. The adopter's
`.gzkit/<surface>/` (project canonical source-of-truth) is the editing
surface — `gz init --update` is the ceremony that refreshes stale entries
from the wheel while preserving operator edits.

```bash
uv run gz init --update --dry-run    # Preview: per-artifact STALE/EDITED/IDENTICAL
uv run gz init --update              # Execute: refresh STALE entries; report conflicts
```

Three-state detection determines the action per artifact:

- **IDENTICAL** — bytes match the wheel canonical; skipped silently
- **STALE** — bytes differ, no canonical-version marker present; refreshed in place
- **EDITED** — bytes differ AND the file carries a
  `<!-- gzkit-canonical-version: X.Y.Z -->` marker; left untouched and surfaced
  as a conflict in the end-of-run summary

Exit code 3 means at least one EDITED conflict remains unresolved. Two ways
forward per conflict:

1. **Accept canonical:** `rm .gzkit/<surface>/<path>` and re-run `gz init --update`
2. **Keep edits:** no action (conflict persists; rerun continues to surface it)

`--update` is mutually exclusive with `--force` (the wipe-and-recreate path
that destroys operator edits). See `docs/user/manpages/init.md` § Update Mode
for the full contract.

---

## Surface-Only Refresh (`gz upgrade`)

`gz upgrade` is the narrower sibling of `gz init --update`. Use it when you
only need canonical surface content (skills, rules, templates, personas) to
match the installed wheel — without the manifest refresh, scaffolder hooks, or
agent sync that `gz init --update` performs.

```bash
uv run gz upgrade --dry-run          # Preview: per-artifact STALE/EDITED/IDENTICAL
uv run gz upgrade                    # Execute: refresh all surfaces from wheel
uv run gz upgrade --surface skills,rules   # Refresh specific surfaces only
uv run gz upgrade --force            # Overwrite EDITED artifacts (audit trail printed)
```

Three-state detection is identical to `gz init --update`:

- **IDENTICAL** — bytes match; skipped silently
- **STALE** — bytes differ, no version marker; refreshed in place
- **EDITED** — bytes differ, version marker present; conflict reported, left unchanged
  (unless `--force`)

`gz upgrade` also handles the **bootstrap-retrofit** case: when
`.gzkit/<surface>/` does not exist (project was not initialized via `gz init`),
the command creates it and writes canonical content from the wheel. Use
`gz init --update` when you need the full ceremony; use `gz upgrade` when you
only need surface content.

See [`gz upgrade`](manpages/upgrade.md) for the full contract.

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
- [`/gz-adr-sync`](skills/gz-adr-sync.md) — end-to-end ADR governance sync (evidence, reconciliation, registration)
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

If `gz adr audit-check` flags a same-commit-window `@covers` backfill finding
(blocking on heavy/foundation/`--strict`; warning on lite/feature default —
exit 3 / exit 0 respectively):

1. Locate the flagged decorator at the reported `file:line`.
2. Re-derive the test's assertion from the REQ's semantics per
   `.claude/rules/tests.md` § Invariant 6f — pin the operator-facing purpose
   the REQ describes, not the bytes the code currently emits.
3. Commit the rewritten test in a **new commit** (away from the closing
   receipt's commit). Do NOT merely move the `@covers` decorator to a new
   line in the same commit — the heuristic compares introducing-commit SHAs.
4. Tune `data/audit_thresholds.json` (`max_covers_backfill_commits` /
   `max_covers_backfill_days`) only if the legitimate-evolution baseline
   for your project differs from the canon defaults (3 commits / 7 days).
   Threshold edits are a doctrine surface — file a GHI explaining the
   project's evidence for the divergence.
5. Re-run `uv run gz adr audit-check ADR-<X.Y.Z> [--strict]` until PASS.

See `docs/user/manpages/gz-adr-audit-check.md` for the severity matrix and
exit-code semantics.

Tracked automation defect: `https://github.com/tvproductions/gzkit/issues/3`.

---

## Loop C: Patch Release (GHI-Driven)

Run after a batch of qualifying GHIs has been merged and you want to ship them
as a patch release.

| Skill (preferred) | CLI equivalent |
|---|---|
| `/gz-patch-release` | `gz patch release --full` |

### Full ceremony (recommended)

One command does everything: discover GHIs, bump version, author release notes,
commit (with lint/test gates), push, and create the GitHub release. Pauses for
operator confirmation before commit/push/release.

```bash
# Preview what would ship
uv run gz patch release --dry-run

# Execute the full ceremony end-to-end
uv run gz patch release --full
```

### Step-by-step (when you need manual control)

```bash
# 1) Discover qualifying GHIs (does not modify state)
uv run gz patch release --dry-run

# 2) Inspect machine-readable discovery output
uv run gz patch release --dry-run --json

# 3) Bump version and write manifest (no commit/push/release)
uv run gz patch release

# 4) Edit RELEASE_NOTES.md manually

# 5) Sync the staged release manifest and version bumps
uv run gz git-sync --apply --lint --test

# 6) Tag and publish the GitHub release
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
- `uv run gz status --show-gates --full` (every linked OBPI rendered as a Rich-table row, no `... and N more` truncation — use for attestation evidence and bug reports per GHI #319)
- `uv run gz status --table --full` (foundation/feature/pool ADR summary with full IDs, no ellipsis)
- `uv run gz state --json`
- `uv run gz state --blocked --full` (artifact graph with full IDs and parent IDs preserved)
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

## PRD → ADR Derivation

*Traceability: this section and its canonical concepts page are the landed
outputs of `OBPI-0.0.18-02-runbook-prd-to-adr` (runbook PRD→ADR derivation
guidance) and `OBPI-0.0.18-01-concepts-page` (taxonomy concepts page),
respectively, under [ADR-0.0.18](../design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md).*

Given a PRD and a Constitution, how do you decide which ADRs to write, what
kind each one should be, and what to defer into the pool? The PRD names goals
and invariants; the Constitution names the rails those goals run on; ADRs are
the decisions that translate those into concrete architecture. Three kinds
exist — [foundation](concepts/adr-taxonomy.md#foundation),
[feature](concepts/adr-taxonomy.md#feature), and
[pool](concepts/adr-taxonomy.md#pool) — and the heuristic below routes each
decision to the right kind. See
[`docs/user/concepts/adr-taxonomy.md`](concepts/adr-taxonomy.md) for the
canonical definitions, the kind-versus-lane orthogonality, and the kind /
semver binding. For edge cases where the heuristic leaves classification
ambiguous — substrate-vs-port or doctrine-vs-tooling decisions — apply the
one-line invariance test in
[`concepts/foundation-feature-invariance-test.md`](concepts/foundation-feature-invariance-test.md).
When you classify a decision as foundation and run `gz plan create --kind foundation`,
the scaffolded ADR includes a `## Why foundation tier?` section (between `## Persona`
and `## Intent`) pre-populated with author prompts for the invariance-test answer and
port-vs-plug framing. See [Why foundation tier? (the convention)](concepts/foundation-feature-invariance-test.md#why-foundation-tier-the-convention)
for the exact heading and a filled-in example.

### Heuristic

| Question you can answer "yes" to | Kind | Semver |
|----------------------------------|------|--------|
| Does this decision shape what the app **is** — an identity-shaping invariant or load-bearing semantic that later work will rely on? | **foundation** | `0.0.x` |
| Does this decision ship a **named capability** to users (a command, a ceremony, a surface they can point at)? | **feature** | `0.y.z` and up |
| Is this decision **visible but not yet committed** — sponsor unknown, acceptance criteria unclear, dependencies unresolved? | **pool** | (no semver) |

Kind is independent of lane. Any kind can be Lite or Heavy — that axis tracks
external-contract exposure, not decision character. A foundation ADR that
codifies an app invariant is Lite when it touches no external contract, and
Heavy when it reshapes one. See the
[kind / lane orthogonality table](concepts/adr-taxonomy.md#kind-lane-orthogonality)
for the full matrix.

### Worked example: PRD-GZKIT-1.0.0

Take three goals from [`docs/design/prd/PRD-GZKIT-1.0.0.md`](../design/prd/PRD-GZKIT-1.0.0.md)
and run them through the heuristic:

- **"Support Lite (Gates 1-2) and Heavy (Gates 1-5) lanes"** — the Gate model
  and the state tiers that feed it shape what gzkit *is* as a governance
  tool; every ADR downstream inherits the distinction. This is a **foundation**
  concern, landed in
  [`ADR-0.0.9-state-doctrine-source-of-truth`](../design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md)
  at semver `0.0.9` — no release-versioning impact, but feature work across
  the system depends on the invariant it names.
- **"Scaffold and validate governance artifacts"** — this is a named capability
  shipping to users. The GHI-driven patch release ceremony (`uv run gz patch
  release --full`) is a **feature** ADR, landed in
  [`ADR-0.0.15-ghi-driven-patch-release-ceremony`](../design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md).
  Note: the `ADR-0.0.15` identifier uses foundation-range semver only because
  this ceremony landed pre-1.0 without forcing a minor bump; the frontmatter
  `kind:` field is the canonical signal, not the semver range alone.
  Post-1.0, a capability like this would bind to a non-`0.0.x` feature range.
- **"AI runtime foundations for future agent control"** — the concern is
  visible (future agent runtime needs governance surfaces) but the shape,
  owner, and acceptance are not. This is a **pool** entry,
  [`ADR-pool.ai-runtime-foundations`](../design/adr/pool/ADR-pool.ai-runtime-foundations.md),
  documented intent awaiting a sponsor who will attest completion. An
  operator reading the pool entry alone knows the concern exists without
  being forced to commit to a shape.

An adopter reading the three entries above should be able to trace the
decomposition from the PRD alone: each goal has a home, each home has a
named kind, each kind carries a semver expectation. If the trace breaks —
you cannot point to the ADR that grounds a PRD goal, or the ADR's kind
does not match the goal's character — the decomposition is incomplete.

### Anti-pattern: foundation-first, features-on-top

Foundation ADRs should not be created defensively or speculatively to
"establish the layer." A foundation ADR earns its place by naming an
invariant that actual feature or pool work needs to rely on. If nothing
downstream consults the invariant you are about to codify, you do not have
a foundation decision — you have a preference.
See also the [Foundation/Feature Invariance Test](concepts/foundation-feature-invariance-test.md) for the one-line test that distinguishes this anti-pattern from legitimate foundation authoring.

Foundation-first drift produces ADRs that declare invariants nobody
violates and that no feature consults. The cost compounds: every adopter
reading the foundation layer parses decisions that never shaped anything
downstream, and the doctrine surface grows faster than the intent beneath
it. Write foundation ADRs when the feature or pool layer forces one — not
before.

The inverse is not a virtue either: shipping a feature that tacitly
depends on an unstated invariant is a foundation ADR you failed to author.
When a feature ADR's Consequences section keeps reaching for "this assumes
X" without a foundation ADR to point at, X is the foundation decision that
wants to be named.

### The pool's role

The [pool](concepts/adr-taxonomy.md#pool) is the answer to "I can see the
concern but I can't commit to it yet." Pooling is cheap; promotion is
deliberate. Not every pool entry will be promoted, and that is fine — a
pool entry that sat for a year is documented intent that had not yet
earned promotion. It is not a defect; it is the system behaving as
intended.

Pool promotion criteria, retirement criteria, and curation cadence are
authored separately in the forthcoming pool curation policy (at
`docs/governance/pool-curation.md`, authored under OBPI-0.0.18-03). The
short version: promotion requires a sponsor (an operator willing to attest
completion), clear acceptance criteria, and no dependency on unresolved
foundation ADRs. Pool entries that cannot meet those criteria stay in the
pool — which is the point of having a pool.

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

## Rules Surface

Canonical rules live at `.gzkit/rules/<slug>.md` (authored source-of-truth).
`gz init` scaffolds all canonical rules from the wheel's package surface
(`importlib.resources.files("gzkit.rules")`) into `.gzkit/rules/`. Once
written, `.gzkit/rules/` is the project canonical surface — edit files there.

Run `gz agent sync control-surfaces` to propagate edits to vendor mirrors
(`.claude/rules/`, `.github/instructions/`). Re-running `gz init` on an existing
project adds new canonical rules without overwriting operator-edited files
(`skip_existing=True`).

See [`gz init`](manpages/init.md#rules-scaffolding) for rules scaffolding details
and [`.claude/rules/skill-surface-sync.md`](../../../.gzkit/rules/skill-surface-sync.md)
for the "Edit `.gzkit/` first" editing invariant.

---

## Chores Commands

Use [`/gz-chore-runner`](skills/gz-chore-runner.md) to run a chore end-to-end (show, plan, advise, execute, validate) through a guided workflow.

Chores resolve project-first → package-fallback (ADR-0.0.21): each slug is
sought under `<project_root>/.gzkit/chores/<slug>/` first, then falls back to
the canonical package resource at `importlib.resources.files("gzkit.chores")`.
Project-local execution evidence is written to `.gzkit/chores/<slug>/proofs/`.
See [`gz-chores`](manpages/gz-chores.md) for the full manpage.

```bash
uv run gz chores list                # List declared chores
uv run gz chores list --explain      # Annotate each row with resolution source (project/package/missing)
uv run gz chores show <slug>         # Display CHORE.md for one chore
uv run gz chores advise <slug>       # Dry-run criteria and report status
uv run gz chores plan <slug>         # Show plan details for one chore
uv run gz chores run <slug>          # Execute and log one chore
uv run gz chores audit --all         # Audit log presence for all chores
uv run gz chores doctor              # Repair missing canonical scaffold under .gzkit/chores/
uv run gz chores doctor --dry-run    # Report-only; no file changes
uv run gz chores propose-ghi <slug>  # File GHIs for unfiled cluster proposals in proofs/
uv run gz validate --chores-layout   # Fail closed (exit 3) on stray CHORE.md or acceptance.json
```

### Governance Doctrine Surfaces

```bash
uv run gz validate --complexity-doctrine-links  # ADR-0.0.27 citation link integrity
uv run gz validate --complexity-thresholds       # ADR-0.0.28 threshold table shape audit
uv run gz complexity distill                     # Run a distillation pass against the corpus
uv run gz complexity distill --no-prior          # Cold-start invocation
uv run gz complexity distill --allow-dated-sibling # Same-date sibling on collision
uv run gz complexity guide <path>                # Preview authoring-time hints on a file (advise-band, never blocks)
uv run gz complexity guide <path> --json         # Machine-readable AuthoringHint JSON array
uv run gz complexity advise <path>               # Preview advisor diagnosis on a file before commit
uv run gz complexity advise <path> --json        # Machine-readable AdvisorDiagnosis JSON
uv run gz complexity advise <file>:<qualname> --attest-intrinsic --reason "..." --attestor "Name"
uv run gz validate --intrinsic-attestation      # Audit intrinsic attestation event shapes
uv run gz validate --advisor-proof-binding      # Verdict <-> proof binding audit (OBPI-0.0.29-08)
```

Fail-closed (exit 3) audit of every citation in cluster ADRs (0.0.27 / 0.0.28 / 0.0.29 / 0.0.30) plus `.gzkit/rules/complexity-doctrine.md` and any document under `docs/governance/complexity/`. Recovery on a flagged citation: re-author the citation against the current `corpus_revision` and `distilled-characteristics-*.md` file, or amend the citing ADR through its own ceremony per `ADR-pool.doctrine-amendment-protocol`. Closes the 2am-Scenario-2 failure mode (advisor diagnosis references missing artifact). Included in `gz check`. See [`gz validate --complexity-doctrine-links`](commands/validate.md#-complexity-doctrine-links) for the speculative-citation marker (used when an ADR forward-references a planned-but-unlanded distillation).

`gz validate --complexity-thresholds` (ADR-0.0.28, OBPI-0.0.28-03) audits the per-metric threshold table at `.gzkit/rules/complexity-thresholds.json`: every canonical metric must have at least one band; the loader's Pydantic model fail-closes on missing block bands, off-enum percentiles, off-enum trigger semantics, missing percentile + absolute pairing, or unparseable citation tuples. When the rule body declares the `## Bootstrap absolutes` carve-out, the validator emits a non-policy-breach `complexity_thresholds_bootstrap_mode` warning naming the upstream-defect GHIs (#404 parser zeros, #405 polarity-aware threshold model). Included in `gz check` (step "Complexity-thresholds"). See [`gz validate --complexity-thresholds`](commands/validate.md#-complexity-thresholds) for the full surface.

`gz complexity distill` is the destination CLI verb for the [`gz-complexity-distill`](../../.gzkit/skills/gz-complexity-distill/SKILL.md) skill (parent ADR-0.0.27, OBPI-0.0.27-06). It composes the OBPI-03 measurement pipeline with the OBPI-04 distillation render and emits a dated `distilled-characteristics-{YYYY-MM-DD}.md` under `docs/governance/complexity/`. Operator follow-up at Gate 5 fills the per-metric Practitioner-eye observation blocks the verb leaves as placeholders (REQ-0.0.27-04-10, the OEE seam). See [`gz complexity distill`](commands/complexity-distill.md) for full options and exit codes.

**Intrinsic complexity attestation** (ADR-0.0.29, OBPI-0.0.29-07) provides two escape paths for functions whose cyclomatic complexity is irreducibly intrinsic — neither path is a silent bypass; both require human attestation:

- **Decorator path** (pre-known irreducible; persists in code): annotate the function with `@intrinsic_complexity(reason="...", attestor="Name")` from `gzkit.complexity.advisor.intrinsic`. The advisor skips the refactor recommendation and prints the attestation message at diagnosis time.
- **Commit-time path** (in-flight discovery; persists in ledger): run `gz complexity advise <file>:<qualname> --attest-intrinsic --reason "..." --attestor "Name"`. Requires an interactive TTY and the word `ATTEST` to confirm. Emits one `intrinsic-complexity-attestation` ledger event; auditable via `gz validate --intrinsic-attestation`.

**gz justify complexity hints** (ADR-0.0.30, OBPI-0.0.30-05): When `gz justify` is invoked on an OBPI whose `## Allowed Paths` section lists `.py` files, authoring-time complexity hints are automatically injected into the scaffold's evidence section under the heading `### Authoring-time complexity hints`. Each hint block shows metric, precedence band, archetype, doctrinal-frame headline, recommended-move headline, and `file:line` range — the same fields emitted by `gz complexity guide` in prose form.

**When the heading appears:** The OBPI brief has at least one `.py` allowed-path AND the OBPI-03 authoring engine finds at least one advise-band crossing in those files.

**When the heading is absent:** No `.py` allowed-paths, no advise-band crossings, or engine failure. All three are silent absence — the scaffold renders normally without the sub-heading.

**Fail-open:** If the authoring engine raises (e.g., `.gzkit/rules/complexity-thresholds.json` missing), `gz justify` completes normally with exit 0. The hints heading is omitted and a structured failure record is appended to `.gzkit/insights/justify-failures.jsonl`. The failure never blocks pre-execution reasoning.

`gz complexity guide` (ADR-0.0.30, OBPI-0.0.30-01) is the authoring-time preview surface. It wraps the OBPI-0.0.30-03 hint engine and emits one `AuthoringHint` per `advise`-band crossing — functions approaching the warn threshold, surfaced while editing before reaching gate time. Exit 3 is NOT used; this verb never blocks. Default output is one prose block per hint (archetype, guidance headline, recommended move); `--json` emits the canonical `AuthoringHint` array. See [`gz-complexity-guide`](manpages/complexity-guide.md) for the full manpage.

`gz complexity guide --server` (ADR-0.0.30, OBPI-0.0.30-04) starts the JSON-over-stdio protocol server for editor/IDE integration. Editors communicate via LSP-style Content-Length–framed JSON envelopes (`initialize` → `analyze*` → `shutdown`). Protocol specification: [`docs/governance/complexity/authoring-guide-protocol.md`](governance/complexity/authoring-guide-protocol.md).

`gz complexity advise` (ADR-0.0.29, OBPI-0.0.29-03) is the trigger-time advisor surface. It runs the OBPI-0.0.29-02 diagnosis engine against `<path>`, measures per-function `radon_cc` via radon's Python API, and emits an `AdvisorDiagnosis` (canonical refactor archetype, doctrinal authority, non-empty proof tuple linking to AST nodes, recommended-move excerpt) for every band crossing in the threshold table at `.gzkit/rules/complexity-thresholds.json`. Operator moment: preview advisor diagnosis on a file before commit. Default output is structured prose; `--json` emits the canonical Pydantic serialization. Exit codes follow the four-code map: `0` clean or warn-band, `3` block-band crossing. See [`gz-complexity-advise`](manpages/gz-complexity-advise.md) for the full manpage.

**Verdict <-> proof binding audit** (ADR-0.0.29, OBPI-0.0.29-08): `gz validate --advisor-proof-binding` is the gate-time defense-in-depth backstop for the verdict <-> proof binding. Model-layer enforcement (OBPI-01: `Field(min_length=1)` on `AdvisorDiagnosis.proof`) and engine-layer enforcement (OBPI-02: `EngineError` raised before model instantiation when proof is unavailable) prevent empty-proof diagnoses at runtime; this validator catches any regression of either lower layer by scanning `tests/fixtures/advisor/*.json`, `intrinsic-complexity-attestation` ledger events that cite a diagnosis id, and `src/gzkit/schemas/advisor_diagnosis.json` (must require `properties.proof.minItems >= 1`). Negative-case fixtures (the OBPI-01 model test that asserts `ValidationError` on empty proof) are skipped via the `"_negative_case": true` speculative-marker escape. Included in `gz validate --all` and `gz check`. See [`gz validate --advisor-proof-binding`](commands/validate.md#-advisor-proof-binding) for the full surface.

**Advisor timeout primitive** (ADR-0.0.29, OBPI-0.0.29-09): The `run_with_timeout` primitive at `src/gzkit/complexity/advisor/timeout.py` wraps advisor invocations with a configurable timeout (default 30s). On timeout, the primitive returns `TimeoutTimedOut` (fail-open — commit proceeds) and logs a JSONL entry to `.gzkit/insights/advisor-failures.jsonl`. The auto-chain hook (OBPI-05) consumes this primitive; the hook never blocks a commit indefinitely. Config override: set `advisor_timeout_seconds` in `.gzkit.json` (e.g. `{"advisor_timeout_seconds": 15}`). The SKIP environment variable (inherited from the `complexity-reduction-xenon` chore) bypasses both xenon and the advisor entirely — the timeout only governs the non-SKIP path.

**Auto-chain hook** (ADR-0.0.29, OBPI-0.0.29-05): The pre-commit hook at `.gzkit/hooks/pre-commit-complexity-advisor` fires `gz complexity advise --auto-chain` when xenon-as-gate exits non-zero. The hook is **opt-in** — it is not installed by `gz init` (rationale: pre-commit hook interaction is fragile per ADR § Negative #6). Install it by running:

```bash
python -m gzkit.hooks.install_complexity_advisor --install
```

This replaces the `xenon-complexity` entry in `.pre-commit-config.yaml` with a composite `complexity-advisor-auto-chain` hook that runs xenon first, then chains to the advisor on failure. The advisor invocation is wrapped in the OBPI-09 timeout primitive (default 30s, fail-open with logged warning). Exit codes: block-band crossing exits 1 (commit blocked); warn-band crossing exits 0 with diagnosis printed to stderr. To skip both xenon and the advisor: `SKIP=complexity-advisor-auto-chain git commit`. To revert: restore the original `xenon-complexity` entry in `.pre-commit-config.yaml` (the installer prints what it replaced).

### Frontmatter-Ledger Reconciliation

```bash
uv run gz frontmatter reconcile --dry-run   # Preview drifted frontmatter rewrites
uv run gz frontmatter reconcile             # Apply ledger-wins reconciliation
uv run gz frontmatter reconcile --json      # Emit receipt JSON to stdout
```

Rewrites drifted ADR/OBPI `id`/`parent`/`lane`/`status` to match the ledger; ungoverned keys preserved byte-identically. See [`gz frontmatter reconcile`](commands/frontmatter-reconcile.md) and ADR-0.0.16 for details.

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
surface (ADR-0.0.11). As of OBPI-0.0.32-10, `gz init` scaffolds the 6
canonical gzkit personas (`implementer`, `main-session`, `narrator`,
`pipeline-orchestrator`, `quality-reviewer`, `spec-reviewer`) from the wheel's
package surface (`importlib.resources.files("gzkit.personas")`) into
`.gzkit/personas/`. Once written, `.gzkit/personas/` is the project canonical
source-of-truth per ADR-0.0.32 § Decision's binding canonical-routing
invariant. Personas are operator identity files and are never silently
overwritten — even by `gz init --force`.

Re-running `gz init` (repair mode) adds any new canonical personas shipped in
newer gzkit versions without touching existing ones. The `CORE_PERSONAS`
registry (importable from `gzkit.personas`) lists all 6 canonical slugs.

The persona research synthesis
(`docs/design/research-persona-selection-agent-identity.md`) distills five
mechanistic studies into design principles that ground trait composition.

```bash
uv run gz personas list              # List loaded persona definitions
uv run gz personas list --json       # Machine-readable persona output
```

---

## Templates Commands

As of OBPI-0.0.32-12, `gz init` scaffolds canonical template `.md` content from
the wheel's package surface (`importlib.resources.files("gzkit.templates")`) into
the project's `.gzkit/templates/` directory. Once written, `.gzkit/templates/` is
the project canonical source-of-truth — `render_template()` uses project-first →
package-fallback resolution. Operators customize templates there.

The 11 canonical template slugs are: `adr`, `adr_pool`, `agents`, `audit`,
`audit_plan`, `claude`, `closeout`, `constitution`, `copilot`, `obpi`, `prd`.

```bash
# Scaffold canonical templates (done automatically by gz init)
gz init

# List templates written to .gzkit/templates/
ls .gzkit/templates/

# Templates are operator-editable; project-first resolution means
# operator-edited .gzkit/templates/<name>.md takes precedence over
# the package default when render_template(<name>) is invoked.
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
- **REQ-coverage gate (ADR-0.0.25):** `gz obpi complete` exits 3 when any REQ in the closing brief's `## Acceptance Criteria` section lacks a passing `@covers`-decorated test. Heavy-lane and foundation-kind briefs are fail-closed; lite-non-foundation briefs warn and proceed. If a REQ genuinely cannot have a unit-test harness, use `--accept-uncovered REQ-ID --accept-uncovered-reason REASON` (requires `--attestor-present` with a structurally-authentic active pipeline marker — see GHI #412 hardening; refused entirely for `sensitivity:security` and foundation-kind scopes which require live TTY confirmation); each waiver records an `obpi_completion_uncovered_accept` ledger event. `gz adr emit-receipt --event closed` mirrors the same gate: an ADR cannot close while any of its OBPIs has an unwaived REQ gap.
- Historical files under `docs/user/reference/**` are archival and may contain legacy command examples; active operator command contracts are in `docs/user/manpages/**` and CLI help output.
