---
id: OBPI-0.0.37-07-pipeline-stage1-gate
parent: ADR-0.0.37-constitutional-invariant-composition
item: 7
lane: Heavy
status: Draft
---

# OBPI-0.0.37-07-pipeline-stage1-gate: Pipeline Stage 1 Gate

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #7 — "OBPI-0.0.37-07 — Pipeline Stage 1 fail-close gate (refuses Stage 2 entry without fresh reconciliation receipt)"

**Status:** Draft

## Objective

Extend `gz obpi pipeline` Stage 1 to refuse Stage 2 entry unless the active OBPI has a fresh `brief_reconciled` ledger receipt — where "fresh" means newer than the most recent mutation timestamp of any file in the brief's Allowed Paths domain. This is the authoring-time half of CIC-2's fail-closed enforcement.

## Lane

**Heavy** — Modifies pipeline-runtime behavior (a runtime contract surface used by every pipeline run). Operator-observable.

## Allowed Paths

- `src/gzkit/pipeline_runtime.py` (modify) — extend Stage 1 entry-check with reconcile-receipt freshness
- `src/gzkit/governance/reconcile_freshness.py` (new) — pure helper: `is_receipt_fresh(receipt_ts, brief_allowed_paths, project_root) -> bool` (compares receipt timestamp against `os.path.getmtime` of each Allowed Path)
- `tests/test_pipeline_runtime.py` (modify or new test file) — Stage 1 gate tests
- `tests/governance/test_reconcile_freshness.py` (new) — freshness helper tests
- `features/brief_reconcile.feature` (modify) — add Stage 1 gate scenarios tagged `@REQ-0.0.37-07-*`; file created by OBPI-05
- `docs/user/runbook.md` (modify) — operator runbook entry: "When Stage 1 blocks: run `gz brief reconcile <OBPI-ID>` to refresh the receipt"
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-07-pipeline-stage1-gate.md` (this brief)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/commands/obpi_complete.py` (Stage 5 — OBPI-08)
- Reconcile engine / CLI / schema (OBPI-04/05/06 — consume only)
- New CLI verbs or ledger event types (this OBPI consumes existing receipts; it does not emit new event types)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `is_receipt_fresh(receipt_ts: datetime, allowed_paths: list[str], project_root: Path) -> bool` returns True when `receipt_ts` is later than `max(getmtime(p)) for p in allowed_paths` (expanding any globs). Missing path returns False (forces re-reconcile). Pure function.
2. REQUIREMENT: Stage 1 entry in `pipeline_runtime.py` queries the ledger for the most recent `brief_reconciled` event whose `brief_id` matches the active OBPI. If absent, Stage 1 fail-closes with exit code 3 and message: "Stage 2 entry blocked: no `brief_reconciled` receipt for <OBPI-ID>. Run `gz brief reconcile <OBPI-ID>` then retry."
3. REQUIREMENT: If a `brief_reconciled` receipt exists but `is_receipt_fresh` returns False, Stage 1 fail-closes with exit code 3 and message: "Stage 2 entry blocked: receipt for <OBPI-ID> stale (receipt_ts=<ts>, max_allowed_path_mtime=<mtime>, drifted path=<path>). Run `gz brief reconcile <OBPI-ID>` to refresh."
4. REQUIREMENT: If receipt exists AND is fresh AND `has_drift` payload is False, Stage 1 passes; Stage 2 entry permitted; existing Stage 1 behavior preserved.
5. REQUIREMENT: If receipt exists, is fresh, but `has_drift` payload is True, Stage 1 fail-closes with exit code 3 and message naming the drifted dimensions.
6. REQUIREMENT: This OBPI does NOT introduce an escape hatch — Stage 1 is fail-closed-no-bypass. The escape hatch is at Stage 5 (OBPI-08's `--accept-stale-reconciliation`) where 2am-operator recovery is unavoidable.
7. REQUIREMENT: Existing Stage 1 behaviors (REQ coverage gate, brief validation) are preserved. The reconciliation check is additive, not a replacement.

> STOP-on-BLOCKERS: OBPI-06's `brief_reconciled` ledger event type must be registered.

## Discovery Checklist

**Parent ADR:**

- [ ] Quote ADR § Decision item #7 (Stage 1 gate) verbatim
- [ ] ADR § Decision Rationale point 5 (freshness defined by mutation-timestamp comparison) — the freshness semantics
- [ ] ADR § Decision Rationale point 6 (fail-closed at both Stage 1 and Stage 5)

**Governance:**

- [ ] `.gzkit/rules/governance-core.md` § Required workflow order — Stage 1 sits between brief validation and implementation start
- [ ] `.claude/rules/governance-core.md` § ADR status index regeneration — example of "fail-closed in `gz check`" pattern

**Context (exemplars):**

- [ ] `src/gzkit/pipeline_runtime.py` — current Stage 1 implementation; understand the entry-check hook
- [ ] `src/gzkit/governance/ledger.py` (or wherever ledger queries live) — receipt-query pattern
- [ ] `src/gzkit/commands/adr_emit_receipt_coverage_gate.py` or similar — existing fail-closed gate pattern in tests

**Prerequisites:**

- [ ] OBPI-04/05/06 landed (engine + CLI + event types)
- [ ] `src/gzkit/pipeline_runtime.py` exposes Stage 1 entry hook

## Quality Gates

- [ ] Gate 1: Stage-1-gate paragraph quoted
- [ ] Gate 2: Tests for: missing receipt, stale receipt, fresh-but-drifted receipt, fresh-no-drift receipt (4 cases minimum); RGR followed
- [ ] Code Quality: lint + typecheck
- [ ] Gate 3: Runbook entry; mkdocs strict
- [ ] Gate 4: `features/brief_reconcile.feature` includes Stage 1 gate scenarios tagged `@REQ-0.0.37-07-*`; behave passes
- [ ] Gate 5: Foundation-kind attestation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.test_pipeline_runtime tests.governance.test_reconcile_freshness -v
uv run mkdocs build --strict
uv run -m behave features/brief_reconcile.feature --tags=REQ-0.0.37-07

# REQ-02: missing receipt fail-closes
# (exercised in tests against a fixture project)

# REQ-04: fresh + no-drift passes
uv run gz brief reconcile OBPI-0.0.37-07-pipeline-stage1-gate
uv run gz obpi pipeline OBPI-0.0.37-07-pipeline-stage1-gate --stage 1 --dry-run && echo "REQ-04 OK: fresh receipt admits Stage 2"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-07-01: `is_receipt_fresh(ts, allowed_paths, root)` is a pure function returning True iff `ts > max(getmtime(p))` over expanded allowed_paths; returns False if any allowed path is missing
- [ ] REQ-0.0.37-07-02: Stage 1 fail-closes (exit 3) with explicit message when no `brief_reconciled` receipt exists for the active OBPI
- [ ] REQ-0.0.37-07-03: Stage 1 fail-closes (exit 3) when the most recent `brief_reconciled` receipt's timestamp is older than the max mtime of any Allowed Path; error names the drifted path
- [ ] REQ-0.0.37-07-04: Stage 1 fail-closes (exit 3) when a fresh receipt's `has_drift` payload is True; error names the drifted dimensions
- [ ] REQ-0.0.37-07-05: Stage 1 admits Stage 2 only when a `brief_reconciled` receipt is both fresh (per REQ-01) AND drift-free
- [ ] REQ-0.0.37-07-06: Existing Stage 1 behaviors (REQ-coverage gate, brief schema validation) are preserved — additive check, not replacement

## Completion Checklist

- [ ] All gates satisfied
- [ ] `gz brief reconcile OBPI-0.0.37-07-pipeline-stage1-gate` reports zero drift

## Evidence

```text
# Per-gate outputs
```

### Value Narrative

<!-- Before: an OBPI could enter Stage 2 implementation with a brief whose Allowed Paths no longer matched the project tree (the ADR-0.0.37 scaffold defect itself). After: Stage 1 mechanically refuses entry without a fresh reconciliation receipt. -->

### Key Proof

<!-- Demonstrate: edit a file in the brief's Allowed Paths after the receipt timestamp, run `gz obpi pipeline --stage 1`, observe fail-close with named drifted path. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #495, GHI #485

## Human Attestation

- Attestor: `<name>`
- Attestation: substantive text grounded in stale-receipt fail-close demonstration
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
