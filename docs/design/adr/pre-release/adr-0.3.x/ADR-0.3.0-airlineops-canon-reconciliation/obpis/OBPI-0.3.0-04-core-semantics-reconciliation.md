---
id: OBPI-0.3.0-04-core-semantics-reconciliation
parent: ADR-0.3.0
item: 4
lane: Heavy
status: Completed
---

# OBPI-0.3.0-04-core-semantics-reconciliation: Core Semantics Reconciliation

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/adr-0.3.x/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md`
- **Checklist Item:** #4 — "Reconcile charter/lifecycle/linkage/closeout semantics and relink concept overlays."

**Status:** Completed

## Objective

Reconcile gzkit runtime semantics and all user-surface overlays with canonical GovZero behavior for lifecycle, closeout, attestation, audit, and receipt accounting.

## Decision Lock (OBPI-04)

1. `gz audit` is strict post-attestation.
2. Attestation CLI flags remain stable; output/docs map to canonical terms.
3. Reconciliation scope includes all `docs/user/**` overlays.
4. Lifecycle completion status is ledger-first.
5. `gz attest` enforces prerequisites by default; accountable override requires rationale.

## Lane

**Heavy** — External governance parity surface and operator contract impact.

## Allowed Paths

- `src/gzkit/**`
- `tests/**`
- `docs/user/**`
- `docs/design/adr/pre-release/adr-0.3.x/ADR-0.3.0-airlineops-canon-reconciliation/obpis/**`
- `docs/proposals/**`

## Denied Paths

- `docs/governance/GovZero/**` (canonical mirror mutation)
- `/Users/jeff/Documents/Code/airlineops/**`

## Requirements (FAIL-CLOSED)

1. MUST enforce attestation prerequisites by lane semantics, with explicit `--force` accountability rationale.
2. MUST keep attestation input tokens stable while presenting canonical terms in status/closeout surfaces.
3. MUST block `gz audit` pre-attestation and provide explicit next-step guidance.
4. MUST make `gz closeout` output commands/paths-first and include heavy-lane Gate 4 command or explicit N/A reason.
5. MUST derive lifecycle/phase semantics from ledger events (`attested`, `closeout_initiated`, `audit_receipt_emitted`).
6. MUST align `docs/user/**` overlays with one coherent execution order: orientation -> tool use -> validation/verification -> closeout presentation -> human attestation -> post-attestation audit -> receipts/accounting.

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests pass: `uv run -m unittest discover tests`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Strict docs build passes: `uv run mkdocs build --strict`
- [x] Command docs and runbook sequence align with runtime behavior

### Gate 4: BDD (Heavy only)

- [x] Explicit N/A rationale recorded where no `features/` suite exists

### Gate 5: Human (Heavy only)

- [x] OBPI-level human understanding attested via ADR receipt event with `adr_completion: not_completed`

## Verification

```bash
uv run -m unittest discover tests
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
uv run gz validate --documents
uv run gz cli audit
uv run gz check-config-paths
uv run gz adr audit-check ADR-0.3.0
uv run gz adr status ADR-0.3.0 --json
uv run gz status --json
```

## Acceptance Criteria

- [x] `gz attest` enforces prerequisite gates by default.
- [x] `gz audit` blocks pre-attestation and runs only after attestation.
- [x] `gz closeout` outputs canonical closeout guidance with heavy-lane Gate 4 command or N/A rationale.
- [x] `gz adr status` and `gz status` expose additive ledger-derived lifecycle semantics.
- [x] `gz state --ready` returns genuinely gate-ready, unattested ADRs.
- [x] `docs/user/**` overlays reflect one coherent operator sequence.

## Evidence

### Implementation Summary

- Files created/modified:
  - `src/gzkit/cli.py`
  - `src/gzkit/ledger.py`
  - `tests/test_cli.py`
  - `tests/test_ledger.py`
  - `docs/user/commands/attest.md`
  - `docs/user/commands/closeout.md`
  - `docs/user/commands/audit.md`
  - `docs/user/commands/adr-status.md`
  - `docs/user/commands/status.md`
  - `docs/user/commands/state.md`
  - `docs/user/commands/adr-emit-receipt.md`
  - `docs/user/commands/adr-audit-check.md`
  - `docs/user/commands/index.md`
  - `docs/user/concepts/lifecycle.md`
  - `docs/user/concepts/closeout.md`
  - `docs/user/concepts/obpis.md`
  - `docs/user/concepts/workflow.md`
  - `docs/user/concepts/gates.md`
  - `docs/user/concepts/lanes.md`
  - `docs/user/runbook.md`
  - `docs/user/index.md`
  - `docs/user/quickstart.md`
  - `docs/user/reference/charter.md`
  - `docs/proposals/REPORT-airlineops-habit-parity-2026-02-14-obpi-04.md`
- Runtime semantic closures:
  - Attestation prerequisite enforcement and accountable force override behavior.
  - Canonical attestation-term presentation mapping on status surfaces.
  - Strict post-attestation audit behavior and closeout command-path guidance parity.
  - Ledger-first lifecycle derivation for `Pending`, `Completed`, `Validated`, `Abandoned`.
- Gate 4 rationale:
  - `features/` is absent in this repository; heavy-lane Gate 4 reported as N/A with explicit rationale.
- Validation commands run:
  - `uv run -m unittest discover tests` (PASS, 167 tests)
  - `uv run gz lint` (PASS)
  - `uv run gz typecheck` (PASS)
  - `uv run mkdocs build --strict` (PASS)
  - `uv run gz validate --documents` (PASS)
  - `uv run gz cli audit` (PASS)
  - `uv run gz check-config-paths` (PASS)
  - `uv run gz adr audit-check ADR-0.3.0` (EXPECTED FAIL: OBPI-0.3.0-05 not completed)
  - `uv run gz adr status ADR-0.3.0 --json` (PASS; lifecycle `Pending`, Gate 4 `n/a`)
  - `uv run gz status --json` (PASS; additive lifecycle fields present)
  - `uv run gz state --ready --json` (PASS; `{}` for this repository state)
  - `uv run gz closeout ADR-0.3.0 --dry-run` (PASS; canonical attestation choices + Gate 4 N/A rationale rendered)
  - `uv run gz audit ADR-0.3.0 --dry-run` (EXPECTED FAIL; blocked pre-attestation)
  - `uv run gz attest ADR-0.3.0 --status completed --dry-run` (EXPECTED FAIL; Gate 3 pending)
  - `uv run gz adr emit-receipt ADR-0.3.0 --event validated ...` (PASS; OBPI scope recorded with `adr_completion: not_completed`)
- Date completed:
  - 2026-02-14

---

**Brief Status:** Completed
