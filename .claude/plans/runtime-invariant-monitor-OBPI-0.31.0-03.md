# Plan: OBPI-0.31.0-03-runtime-invariant-monitor

## Context

Parent ADR: `ADR-0.31.0-obpi-state-machine`. OBPI-01 delivered the model
layer (`OBPIState`, `Transition`, `CANONICAL_TRANSITIONS` in
`src/gzkit/core/obpi_state_machine.py`); OBPI-02 delivered the witnessed
withdraw/supersede CLI verbs. This OBPI (item 3) is the pre-registered
landing falsifier: a runtime invariant monitor at the reconciler's write
boundary that refuses any `status:` frontmatter rewrite not backed by a
declared transition — the GHI #348 class (hand-marked `Withdrawn` silently
demoted to `pending` by ledger-wins reconciliation).

**Recovery-mode disclosure (--from=verify):** The implementation landed in
commit `d864140b` ahead of this pipeline run — a process defect per
AGENTS.md § Pipeline mandate (freeform implementation of a contract-bearing
OBPI). This plan is the retroactive governance record of the executed
approach, authored during the `--from=verify` recovery pass so the
plan-audit receipt, REQ traceability, and attestation ceremony can be
completed against verified reality. It does not claim planning preceded
implementation.

**Approach (as executed):**

1. `TransitionMonitor` (new module `src/gzkit/governance/obpi_transition_monitor.py`)
   — pure classifier: `is_allowed(from_state, to_state)` is True iff the
   pair matches a `Transition` in OBPI-01's `CANONICAL_TRANSITIONS`. No I/O.
2. Integration at the confirmed single write chokepoint
   (`src/gzkit/governance/frontmatter_coherence.py`): `reconcile_frontmatter`
   consults the monitor for OBPI artifacts before `rewrite_governed_keys_in_place`;
   a refused edit skips the write entirely and is surfaced in the new
   `ReconciliationReceipt.refused_rewrites` field (schema updated in
   `data/schemas/frontmatter_coherence_receipt.schema.json`).
3. Vocabulary bridge: `_map_vocab_to_obpi_state` maps frontmatter/ledger
   status terms onto `OBPIState`; unmapped states refuse (fail-closed).
   ADRs are not governed by `OBPIState` and bypass the monitor.
4. Landing falsifier regression test reproduces the exact GHI #348 shape
   and asserts refusal (file bytes unchanged, surfaced in receipt).

**Rejected alternatives:**

1. Housing the monitor in `src/gzkit/governance/invariants.py` — REJECTED:
   that module is `ConstitutionalInvariant` (ADR-0.0.37 content-rendering
   registry), an unrelated concept sharing only a filename word (brief
   § Denied Paths correction).
2. Batch/CI-audit shape under `trust_audits/` — REJECTED: ADR Decision
   item 4 requires a live monitor on the write path itself, not a
   periodic read-only scan.

## Files

- `src/gzkit/governance/obpi_transition_monitor.py` — CREATE (pure classifier)
- `src/gzkit/governance/frontmatter_coherence.py` — MODIFY (monitor
  consultation before status writes; `refused_rewrites` receipt field)
- `data/schemas/frontmatter_coherence_receipt.schema.json` — MODIFY
  (require `refused_rewrites`)
- `src/gzkit/core/obpi_state_machine.py` — READ ONLY (Boundary Invariant #1)
- `tests/governance/test_obpi_transition_monitor.py` — CREATE (classifier
  unit tests incl. full-matrix biconditional, `@covers REQ-0.31.0-03-01`)
- `tests/governance/test_frontmatter_coherence.py` — MODIFY (landing
  falsifier `@covers REQ-0.31.0-03-03`; write-boundary contrast test
  `@covers REQ-0.31.0-03-02`)
- `docs/user/manpages/frontmatter-reconcile.md` — MODIFY (refusal path)

## Steps

1. Classifier module + unit tests (REQ-0.31.0-03-01). Full-matrix
   biconditional over `OBPIState x OBPIState` vs `CANONICAL_TRANSITIONS`
   membership.
2. Write-boundary integration (REQ-0.31.0-03-02): refused edit never
   reaches `path.write_text`, surfaced in `refused_rewrites`; declared
   transitions still write (Requirements item 6 accepted-case
   preservation).
3. Landing falsifier regression test (REQ-0.31.0-03-03): GHI #348 shape
   refused live.
4. Manpage refusal-path documentation (REQ-0.31.0-03-05).
5. Verification: `gz arb ruff` / `gz arb typecheck` / full unittest via
   `gz arb step` / `mkdocs build --strict` / `gz covers` BEHAVIOR parity.

## Verification

- `uv run gz covers OBPI-0.31.0-03-runtime-invariant-monitor --json` —
  `behavior_uncovered_reqs == 0`
- `uv run -m unittest tests.governance.test_obpi_transition_monitor tests.governance.test_frontmatter_coherence -v`
- Full Stage 3 baseline: all ARB-wrapped checks PASS (see pipeline run log)
