---
id: ADR-pool.cloud-agent-routines
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
promoted_to: ADR-0.0.62-afk-diagnosis-cloud-routines
---

# ADR-pool.cloud-agent-routines: Cloud Agent Routines for Governance Automation
> Promoted to `ADR-0.0.62-afk-diagnosis-cloud-routines` on 2026-05-25. This pool file is retained as historical intake context.


## Status

Superseded

## Date

2026-05-07

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Use Claude Code routines — cloud-scheduled agents running on Anthropic
infrastructure — to automate recurring governance hygiene that currently
depends on operator memory or in-session discovery. Each routine runs
autonomously (no interactive approval prompts), persists results to the
ledger or issue tracker, and fires on a schedule or GitHub event without
requiring a local machine.

gzkit already has mechanical validators (`gz validate`, `gz check`,
`gz state`) and operational skills (`ghi-triage`, `gz-tech-debt-review`).
What is missing is a scheduling substrate that runs them between operator
sessions so drift is caught before it compounds.

---

## Problem Statement

Governance drift is silent. ADR status indexes go stale, ledger state
diverges from on-disk canon, trust audit violations accumulate, control
surface mirrors fall out of sync, session handoffs age past usefulness,
and technical debt accrues unreviewed. Today these are caught reactively —
when an operator lands on the drift during a session — rather than
proactively. The cost is context burn (diagnosing the drift) and
confidence erosion (the operator cannot trust derived views).

Claude Code routines provide the mechanical backstop: a cloud agent that
runs validators on a schedule, files GHIs for drift, and keeps derived
state fresh.

---

## Target Scope

### R-1. Dependency Freshness Sweep (weekly)

Parse `pyproject.toml` + `uv.lock`, check PyPI ages, flag stale or
deprecated dependencies. Emit findings as a GHI or append to
`.gzkit/insights/agent-insights.jsonl`. Already planned as S-6 in
the harness engineering improvement handoff; this ADR provides the
scheduling substrate.

### R-2. Ledger Reconciliation (daily)

Run `uv run gz validate --reconcile-freshness` and
`uv run gz register-adrs --all`. Detect Layer 2/3 drift before it
compounds across sessions. File a GHI if reconciliation surfaces
unresolvable divergence.

### R-3. Trust Audit Suite (daily)

Run `uv run gz validate --documents --surfaces --advisory-scorecard
--cli-alignment`. Catch rule/doc/surface drift that nobody notices
until a session hits it. Report violations as a GHI with the full
validator output.

### R-4. Control Surface Sync Check (on PR merge to main)

Verify `.gzkit/manifest.json` to mirror consistency. Flag if
`gz agent sync control-surfaces` is needed. Triggered by GitHub PR
merge event — skill/rule edits that skip the sync step are a recurring
failure mode.

### R-5. Stale Handoff Cleanup (weekly)

Flag handoffs in `.gzkit/handoffs/` older than 7 days. Close resolved
session-handoff GHIs. The session orientation hook already reads
freshness; the routine acts on it.

### R-6. Tech Debt Review (weekly)

Run `gz-tech-debt-review` scoped to commits since last review. Surface
debt before it becomes architectural. Emit findings to insights or
file as a GHI.

---

## Proposed OBPI Decomposition

Inaugural routine for promotion: **R-3 Trust Audit Suite** (parallels ADR-0.0.60's
choice of `lane-latency` as inaugural surface). Framing refined at promotion
time from "cloud agent routines for governance automation" to **"AFK-diagnosis
via cloud routines"** — read-only / surface findings / never remediate. Architecture:
pluggable `ROUTINE_REGISTRY` (content-addressable by `.gzkit/routines/<name>.yaml`);
future routines (R-1, R-2, R-4, R-5, R-6) plug in via separate ADRs without
restructuring this ADR.

| # | Slug | Description | Lane |
|---|------|-------------|------|
| 01 | routine-models-registry-and-canonical-surface | Pydantic `Routine` models (`diagnosis_only: Literal[True]`) + `RoutineExecEvent` with `recorder_source` field + `.gzkit/routines/` canonical-surface class + `_classify_routine_file` + schema export + `ROUTINE_REGISTRY` loader. | heavy |
| 02 | gz-routine-exec-with-enforcement | `gz routine exec <name>` CLI with subprocess wrapper whitelist (`gz validate`/`check`/`status`/`state`/`routine results`/`issue file` prefixes only); `GZKIT_ROUTINE_CONTEXT=1` env injection; `--json` emits one `RoutineExecEvent` line; new `forbid-routine-mutation` pre-commit hook (defense-in-depth). | heavy |
| 03 | gz-routine-read-only-commands | `gz routine list`, `gz routine show <name>`, `gz routine validate <name>`; `RoutineListReport` + `RoutineSummary` models; read-only surface. | heavy |
| 04 | gz-routine-deploy | `gz routine deploy <name>` generates Claude Code routine config to `.gzkit/routines/.deployed/`; prints operator-action handoff text; explicitly does NOT push to Anthropic infrastructure. | heavy |
| 05 | gz-routine-reconcile-and-issue-idempotency | `gz routine reconcile [--apply] [--since] [--dry-run]` queries routine-finding GHIs, parses embedded `RoutineExecEvent`, dedups, appends with `local_reconciled_at`/`local_reconciled_by`; `gz issue file --idempotency-key` extension. | heavy |
| 06 | gz-routine-results-and-status-integration | `gz routine results <name>` Layer-3 derived view + 30-day rollup; `gz status --table` "Most recent AFK-routine activity" line with STALE detection. | heavy |
| 07 | trust-audit-suite-inaugural-routine | `.gzkit/routines/trust-audit-suite.yaml` (4 validator scopes) + headless-executability tests + GHI template tests + budget assertion. | heavy |
| 08 | afk-routines-docs-and-attestation | Runbook section, manpages for 7 routine subcommands, threshold/cadence doc, Gate 4 BDD, Gate 5 attestation evidence bundle (incl. beta-tier-acceptance attestation). | heavy |

OBPIs 02, 03, 04, 05 can execute in parallel once 01 lands. 06 gates on 05. 07 gates on 02. 08 closes the docs/attestation gates.

## Non-Goals

- No custom routine runtime — this uses Claude Code's native routine
  infrastructure (`claude.ai/code/routines`), not a self-hosted scheduler.
- No routine-triggered code changes — routines detect and report; humans
  (or governed OBPI sessions) remediate.
- No GHI triage routine in this scope — triage requires operator judgment
  on severity classification that a headless routine cannot attest.

---

## Dependencies

- **Requires**: Claude Code routines feature (currently research preview,
  `experimental-cc-routine-2026-04-01` beta header).
- **Related**: `dependency-freshness-sweep` chore (S-6, harness improvement
  handoff) — R-1 is the scheduling wrapper.
- **Related**: ADR-pool.agent-reliability-framework — routine-produced
  evidence feeds into AR level computation if ARF lands.

---

## Open Questions

1. **Routine-to-ledger provenance** — routines run headless on Anthropic
   infrastructure. Should routine-emitted ledger events carry a distinct
   `recorder_source` (e.g. `routine:trust-audit-suite`) to distinguish
   them from interactive session events?

2. **Failure notification** — when a routine's validator exits non-zero,
   should the routine file a GHI, post to a notification channel, or both?
   GHI is durable and auditable; notification is faster but ephemeral.

3. **ADR status index regen** — **resolved.** Wired into
   `_complete_closeout_pipeline` in `src/gzkit/commands/closeout.py` as a
   direct code change (Option A). `regenerate_adr_status_md` now runs after
   OBPI auto-fix, matching airlineops parity. No routine needed.

4. **AirlineOps parity scan** — currently exists as a skill
   (`airlineops-parity-scan`) but is expected to fall away as gzkit
   innovations flow downstream rather than gzkit chasing airlineops
   patches (Architectural Boundary 5). Not in scope for routine
   scheduling.

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Claude Code routines feature exits research preview (or operator
   accepts preview-tier stability).
2. At least R-2 (ledger reconciliation) and R-3 (trust audit suite)
   have working `gz validate` invocations that exit cleanly in a
   headless environment.
3. Routine-to-ledger provenance question (Open Question 1) is resolved.
4. Human assigns a SemVer ADR ID for active implementation.

---

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
