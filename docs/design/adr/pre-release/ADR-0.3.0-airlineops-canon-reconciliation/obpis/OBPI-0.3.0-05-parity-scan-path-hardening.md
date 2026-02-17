---
id: OBPI-0.3.0-05-parity-scan-path-hardening
parent: ADR-0.3.0
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.3.0-05-parity-scan-path-hardening: Parity Scan Path Hardening

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md`
- **Checklist Item:** #5 — "Harden parity scan path resolution for worktree and non-worktree execution contexts."

**Status:** Completed

## Objective

Make parity scan execution deterministic across worktree layouts by adding canonical path fallback/resolution rules and requiring each scan to emit habit-parity classification output.

## Lane

**Heavy** — External governance parity surface and operator contract impact.

## Allowed Paths

- `.github/skills/airlineops-parity-scan/SKILL.md`
- `docs/proposals/REPORT-TEMPLATE-airlineops-parity.md`
- `docs/proposals/REPORT-airlineops-habit-parity-*.md`
- `docs/proposals/REPORT-airlineops-parity-*.md`
- `docs/user/runbook.md`
- `src/gzkit/cli.py`
- `tests/test_cli.py`

## Denied Paths

- `/Users/jeff/Documents/Code/airlineops/**`
- `.gzkit/ledger.jsonl (manual edits)`
- `Non-parity unrelated CLI behavior`

## Requirements (FAIL-CLOSED)

1. MUST support deterministic canonical-root resolution using ordered strategy (explicit override, sibling-path, absolute fallback).
1. MUST fail closed with explicit blocker output when canonical source cannot be resolved.
1. MUST document resolution behavior in skill instructions and operator docs.
1. MUST require parity output to include habit-class status rows (not only artifact-count deltas).
1. NEVER claim scan completion without path-level canonical evidence.
1. ALWAYS keep parity reports reproducible in automation contexts.

> STOP-on-BLOCKERS: if canonical source, required paths, or baseline artifacts are unavailable, stop and report blockers.

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests pass: `uv run -m unittest discover tests`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Format clean: `uv run gz format --check` (or equivalent non-mutating check)
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs lint/build checks pass for changed docs
- [x] Parity report template includes habit-class matrix expectations

### Gate 4: BDD (Heavy only)

- [x] Contract-level behavior checks executed or explicitly marked N/A with rationale

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded after observing deterministic scan behavior in at least one non-sibling context

## Verification

```bash
test -d ../airlineops || echo "sibling missing in this cwd"
test -d /Users/jeff/Documents/Code/airlineops && echo "absolute fallback present"
rg -n "Habit Parity Matrix|canonical-root|fail closed" .github/skills/airlineops-parity-scan/SKILL.md docs/proposals/REPORT-TEMPLATE-airlineops-parity.md docs/proposals/REPORT-airlineops-habit-parity-*.md
uv run mkdocs build --strict
uv run gz validate --documents
```

## Acceptance Criteria

- [x] Parity scan instructions document robust canonical path discovery.
- [x] Automation runs no longer block solely due to worktree-relative path assumptions.
- [x] Parity report generation remains dated, repeatable, and evidence-based.
- [x] Each parity report includes habit-class status and required follow-up linkage.

## Evidence

### Implementation Summary

- Files created/modified:
  - `.github/skills/airlineops-parity-scan/SKILL.md`
  - `docs/proposals/REPORT-TEMPLATE-airlineops-parity.md`
  - `docs/proposals/REPORT-airlineops-parity-2026-02-15-obpi-05.md`
  - `docs/proposals/REPORT-airlineops-habit-parity-2026-02-15-obpi-05.md`
  - `docs/user/runbook.md`
  - `docs/design/adr/pre-release/ADR-0.3.0-airlineops-canon-reconciliation/obpis/OBPI-0.3.0-05-parity-scan-path-hardening.md`
- Validation commands run:
  - `test -d ../airlineops && echo "sibling present"`
  - `test -d /Users/jeff/Documents/Code/airlineops && echo "absolute fallback present"`
  - `rg -n "Habit Parity Matrix|canonical-root|fail closed" .github/skills/airlineops-parity-scan/SKILL.md docs/proposals/REPORT-TEMPLATE-airlineops-parity.md docs/proposals/REPORT-airlineops-habit-parity-*.md`
  - `uv run -m unittest discover tests`
  - `uv run gz lint`
  - `uv run gz typecheck`
  - `uv run mkdocs build --strict`
  - `uv run gz validate --documents`
  - `uv run gz adr audit-check ADR-0.3.0`
  - `uv run gz adr status ADR-0.3.0 --json`
  - `uv run gz status`
  - `uv run gz adr emit-receipt ADR-0.3.0 --event validated --attestor "Jeffry Babb" --evidence-json '{"scope":"OBPI-0.3.0-05","adr_completion":"not_completed","obpi_completion":"attested_completed","attestation":"I attest I understand the completion of OBPI-0.3.0-05.","date":"2026-02-15"}'`
- Date completed:
  - 2026-02-15

---

**Brief Status:** Completed
