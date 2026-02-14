# REPORT: AirlineOps Habit Parity Scan

## Metadata

- Date: 2026-02-14
- Scanner: Human + Agent
- Canonical Source: `/Users/jeff/Documents/Code/airlineops`
- Scope: Operator habit parity for GovZero doctrine and gzkit runtime/doc surfaces

---

## Executive Summary

- Overall habit parity status: Partial
- Highest risk: authority-boundary drift during closeout and receipt/accounting semantics
- Immediate objective: complete OBPI-0.3.0-03/04/05 as one coordinated habit-installation sequence

---

## Habit Parity Matrix (Max Extraction)

| Habit Class | Canonical Source Signal (AirlineOps) | gzkit Surface(s) | Status | Severity | Owning OBPI |
|---|---|---|---|---|---|
| Pre-tool orientation | ADR/OBPI framing, lane + scope + denied paths before execution | OBPI briefs under `docs/design/adr/.../obpis/`, runbook start steps | Partial | P1 | OBPI-0.3.0-04 |
| Tool-use control surfaces | `gz-*` skill procedures + command rituals | `.github/skills/gz-*`, `src/gzkit/cli.py`, command docs | Partial | P1 | OBPI-0.3.0-04 |
| Post-tool accounting | audit artifacts, receipts, explicit lifecycle transitions | `gz audit`, `gz adr emit-receipt`, ledger event stream, ADR audit dirs | Partial | P1 | OBPI-0.3.0-04 |
| Validation | gate commands with evidence capture | `gz gates`, `gz check`, `gz check-config-paths` | Partial | P2 | OBPI-0.3.0-04 |
| Verification | audit-check and closeout-phase verification discipline | `gz adr audit-check`, closeout protocol docs, audit proofs | Partial | P1 | OBPI-0.3.0-04 |
| Presentation for humans | manpages, runbooks, workflow narratives, proof docs | `docs/user/commands/*`, `docs/user/runbook.md`, `docs/user/index.md` | Partial | P1 | OBPI-0.3.0-03 |
| Canonical doctrine surface | GovZero canonical docs available at canonical paths | `docs/governance/GovZero/*.md` | Missing | P1 | OBPI-0.3.0-03 |
| Bidirectional parity discipline | extraction + backport obligations with dated proof | parity reports/plans in `docs/proposals/` and scan skill behavior | Partial | P1 | OBPI-0.3.0-05 |
| Deterministic parity scan execution | reproducible canonical-root resolution across worktrees | `airlineops-parity-scan` skill + execution docs | Partial | P2 | OBPI-0.3.0-05 |

---

## Findings

### H-001: Canonical Doctrine Surface Is Still Missing

- Type: Missing
- Why it matters: without canonical GovZero docs in-repo, operator habits are translated from overlays instead of source documents.
- Evidence: no `docs/governance/GovZero/` file set in gzkit.
- Remediation: execute OBPI-0.3.0-03 with full canonical file import and path parity proof.

### H-002: Runtime Habit Sequence Is Only Partially Installed

- Type: Partial
- Why it matters: orientation, control execution, accounting, verification, and presentation need one continuous procedural chain, not isolated commands.
- Evidence: runtime commands exist, but end-to-end ritual doctrine is not yet fully codified across all semantics pages.
- Remediation: execute OBPI-0.3.0-04 as full habit-sequence reconciliation.

### H-003: Parity Discipline Is Not Yet Deterministic Across Execution Contexts

- Type: Partial
- Why it matters: parity claims weaken when scan behavior depends on local path assumptions.
- Evidence: parity skill references sibling canonical path assumptions; worktree execution can diverge.
- Remediation: execute OBPI-0.3.0-05 with deterministic canonical-root resolution and fail-closed behavior.

---

## Required Next Actions

1. Action: Install canonical GovZero docs and prove file-level parity.
   Parent ADR: `ADR-0.3.0`
   OBPI: `OBPI-0.3.0-03-govzero-canonical-doc-surface`
   Owner: Human + Agent
2. Action: Reconcile lifecycle/linkage/closeout/receipt semantics into one complete operator habit sequence.
   Parent ADR: `ADR-0.3.0`
   OBPI: `OBPI-0.3.0-04-core-semantics-reconciliation`
   Owner: Human + Agent
3. Action: Harden parity scan pathing and mandate habit-matrix output on each scan.
   Parent ADR: `ADR-0.3.0`
   OBPI: `OBPI-0.3.0-05-parity-scan-path-hardening`
   Owner: Human + Agent

---

## Completion Signal

Habit parity for ADR-0.3.0 is complete only when OBPI-0.3.0-03/04/05 are all Completed and `uv run gz adr audit-check ADR-0.3.0` returns PASS.
