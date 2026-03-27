---
status: Pool
promotes_to: ADR-0.40.0
date_added: 2026-03-27
---

# ADR-pool.gz-preflight-health-orchestration: Pre-Session Health Orchestration and Governance Design Tooling

## Status

Pool

## Date

2026-03-27

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) — Phase 3: Agentic Reliability

---

## Intent

Eliminate mid-session governance blockers by extending `gz preflight` into a tiered, self-healing
health orchestrator, and establish a GovZero-native design workflow that keeps all design artifacts
inside governance structures instead of parallel product surfaces.

Two capabilities are bundled here because they share a single root cause: agents and operators
encountering preventable friction (stale receipts blocking gates, drift discovered mid-implementation,
design artifacts landing outside GovZero). Both are pre-condition improvements, not feature additions.

---

## Delivered This Session (Already Shipped)

The following item was completed before this pool ADR was booked and requires no additional OBPIs:

- **`gz-design` skill** — GovZero-native collaborative design workflow that produces ADR artifacts
  instead of superpowers/superbook specs. Replaces brainstorming skills globally; superpowers
  disabled. Delivered 2026-03-27.

---

## Target Scope

### gz preflight — Self-Healing Health Orchestrator

Extend the existing `gz preflight` command from a passive reporter into an active pre-session
health orchestrator with tiered auto-repair.

**Check pipeline (ordered):**

1. Stale OBPI receipt detection — receipts from closed/superseded OBPIs blocking active gates
2. Ledger-markdown alignment — ledger is truth; stale markdown auto-corrected
3. ADR table drift — OBPI status rows diverged from brief source files (`gz-obpi-sync`)
4. Orphan briefs — briefs with no parent ADR entry (flag only; no auto-delete)
5. Schema validation — manifests and governance surfaces (`gz validate --documents --surfaces`)
6. Dependency readiness — in-flight ADR dependencies blocking promotion

**Repair tiers:**

| Class | Examples | Action |
|-------|----------|--------|
| Deterministic | Stale receipts, ledger-markdown mismatch | Auto-repair silently |
| Flagged | Orphan briefs, unknown draft OBPIs | Report with recommended fix |
| Human-required | Dependency conflicts, heavy-lane attestation gaps | Block and escalate |

**Output contract:**

- Default: human-readable preflight report with PASS/WARN/BLOCK per check
- `--json`: machine-readable report for CI/agent consumption
- `--fix`: execute deterministic repairs (dry-run by default without this flag)
- `--adr ADR-X.Y.Z`: scope checks to a single ADR (for mid-session use)
- Exit 0: all checks PASS; Exit 1: WARN present; Exit 3: BLOCK present

**Receipt artifact:** `artifacts/receipts/preflight-YYYY-MM-DDTHH-MM-SS.json`

**Integration points:** Consumes `gz-adr-recon`, `gz validate`, `gz-tidy`, `gz-obpi-sync`
outputs. Does not replicate their logic — orchestrates and interprets.

### ADR Overlap with ADR-0.20.0

`gz preflight` will consume `gz drift` (Triangle Sync output from ADR-0.20.0-04) as one of its
check sources. This ADR is a consumer, not a replacement — ADR-0.20.0 delivers the drift signal;
this ADR routes it into the preflight health report. Sequencing: this pool ADR should not be
promoted until ADR-0.20.0 OBPI-04 is complete.

---

## Non-Goals

- Do not replicate `gz validate`, `gz-adr-recon`, or `gz-tidy` logic inside preflight
- Do not add auto-repair for orphan briefs (judgment call, always human-required)
- Do not introduce new governance ledgers or receipt schemas
- Do not add `gz-design` OBPIs (already shipped)

---

## Dependencies

- ADR-0.20.0 OBPI-04 (`gz drift` CLI surface) — preflight consumes drift output
- ADR-0.20.0 OBPI-05 (advisory gate integration) — optional but preferred before promotion

---

## Proposed OBPI Decomposition

| # | Slug | Description | Lane |
|---|------|-------------|------|
| 01 | check-pipeline | Implement ordered check pipeline with CheckResult + PreflightReport models | Lite |
| 02 | auto-repair-tier | Deterministic auto-repair executor (stale receipts, ledger-markdown mismatch) | Lite |
| 03 | cli-surface | `gz preflight --fix / --json / --adr` flag surface and exit code contract | Heavy |
| 04 | receipt-artifact | JSON receipt emission with schema validation | Lite |
| 05 | advisory-gate | Wire preflight as optional pre-session advisory gate in hook chain | Lite |

---

## Design Notes (Session 2026-03-27)

Full design conversation captured in this session. Key decisions:

- **Pydantic models:** `CheckResult(id, label, status, message, repair_action | None)` and
  `PreflightReport(run_at, adr_scope | None, checks, summary)` — both frozen, extra="forbid"
- **Orchestrator pattern:** Preflight does not reimplement checks; it calls existing `gz` commands
  as subprocesses, parses their exit codes and stdout, and maps results to `CheckResult` entries
- **Repair executor:** Isolated function per deterministic repair class; no repair logic inline
  with check logic
- **Stdout rendering:** Rich table (check label | status badge | message); `--json` to stdout,
  logs to stderr — consistent with CLI doctrine
- **Dry-run default:** `--fix` required to execute repairs; without it, repairs are described but
  not applied

---

## Checklist

1. Implement check pipeline with Pydantic models and ordered check execution
1. Implement deterministic auto-repair tier
1. Deliver CLI surface with `--fix`, `--json`, `--adr` flags and exit code contract
1. Emit JSON receipt artifact per run
1. Wire preflight as advisory pre-session gate

---
