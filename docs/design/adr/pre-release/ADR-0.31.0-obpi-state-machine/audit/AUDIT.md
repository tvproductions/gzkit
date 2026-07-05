# AUDIT (Gate-5) — ADR-0.31.0

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.31.0-obpi-state-machine |
| ADR Title | OBPI State Machine and Runtime Invariant Monitor |
| ADR Dir | docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine |
| Audit Date | 2026-07-05 |
| Auditor(s) | g0 (operator, attesting); pipeline-orchestrator driver; spec-reviewer + quality-reviewer (independent, read-only) |

## Fidelity Gate (Step 3 — bound, `gz adr fidelity ADR-0.31.0`)

The audit runs the ADR's `## Fidelity Assertions` against the running system. **2/2 pass** (proof: `audit/proofs/fidelity-post-classfix.txt`).

| Claim | Command | Expected | Observed |
|-------|---------|:--------:|:--------:|
| Withdrawal is a witnessed transition validated against `CANONICAL_TRANSITIONS` (legal predecessor passes, non-mutating dry-run) | `gz obpi withdraw OBPI-0.31.0-01-... --reason ... --attestor g0 --dry-run` | 0 | 0 ✓ |
| Witness requirement is transport-agnostic + fail-closed (empty attestor rejected, no ledger write) | `gz obpi withdraw ... --attestor "" --dry-run` | 1 | 1 ✓ |

## Execution Log

| Check | Command / Method | Result | Notes |
|-------|------------------|:------:|-------|
| Ledger completeness (L2) | `gz adr audit-check ADR-0.31.0` | ✓ | exit 0; all 3 OBPIs PASS. `audit/proofs/audit-check-post-classfix.txt` |
| Fidelity gate (bound) | `gz adr fidelity ADR-0.31.0` | ✓ | 2/2 pass; exit 0 |
| Independent REQ trace | spec-reviewer | ✓ | 18/18 REQs genuine; REQ-03-03 semantic; no cosmetic proofs. `audit/proofs/reviewer-verdicts.md` |
| Independent structural coherence | quality-reviewer | ✓ | FINAL: COHERENT (2 shortfalls found + resolved en route) |
| Full unit suite | `uv run -m unittest -q` | ✓ | 6779 pass. ARB receipt `arb-step-unittest-bfa0cd356e414362937425bac3e7a33a` (exit_status=0) |
| Lint / format / typecheck | `ruff check` · `ruff format` · `uvx ty check` | ✓ | clean on all touched files |

## Shortfalls Identified & Remediated

The audit's independent review surfaced two real, code-confirmed shortfalls that every per-OBPI gate had passed — the ADR-level integration defects the audit ceremony exists to catch. Both were remediated before VALIDATED (operator-directed).

### Shortfall 1 — covers-backfill false-positive blocked audit-check (GHI #667, commit `68149232`)

`gz adr audit-check` failed (exit 3) on REQ-0.31.0-03-03: the GHI #309 receipt-coupling guard suppressed the legitimate same-commit block-creation exemption because OBPI-03's completion receipt anchors to its implementation commit `d864140`. Diagnosed as a genuine heuristic false-positive (spec-reviewer independently confirmed the flagged test is semantic, not cosmetic). Fix: the guard now couples only when the receipt was emitted contemporaneously with the intro commit (not merely anchored to it from a later ceremony). Preserves GHI #309 protection. Direct fix, TDD (RED→GREEN).

### Shortfall 2 — GHI #348 clobber class reproducible via governed-status writers outside the monitor (GHI #668, commits `155cd16a` + `7fb44884`)

The runtime monitor guarded only `reconcile_frontmatter`. Independent review found the GHI #348 terminal-status clobber class reproducible via **three** other governed OBPI-status writers: `auto_fix_obpi_brief_frontmatter` (`gz attest`/`closeout`/`obpi reconcile`), `gz state` sync, and `gz obpi complete` (the primary verb). Operator ruled *correct-before-validate*, then *full class-fix*. Remediation: a single `guarded_obpi_status_write` chokepoint + the shared `obpi_status_is_terminal` predicate (sourced from OBPI-01's `OBPIState`/`OBPI_STATES` model) now govern every clobber-capable writer; `obpi_cmd.py` repudiation reset is documented-exempt (safe by construction). Terminal-origin gate (not full `is_allowed`) to preserve legitimate multi-hop catch-up syncs. TDD landing falsifiers for each newly-guarded path.

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | ✓ 3/3 OBPIs attested_completed; 18/18 REQs proven on correct channels |
| Integration Coherence | ✓ COHERENT — single terminal rule consulted by every governed-status writer |
| Fidelity (thesis vs running system) | ✓ 2/2 assertions pass |
| Documentation Alignment | ✓ — attested-brief "single chokepoint" premise annotated forward (GHIs), not rewritten |
| Shortfalls Resolved | ✓ 2/2 (GHI #667, GHI #668) |
| Residual (non-blocking) | ⚠ writer-coverage convention not yet mechanically enforced → GHI #669 (Promotable) |

## Evidence Index

- `audit/proofs/audit-check-post-classfix.txt` — L2 ledger proof, exit 0
- `audit/proofs/fidelity-post-classfix.txt` — bound fidelity gate, 2/2 pass
- `audit/proofs/reviewer-verdicts.md` — spec-reviewer + quality-reviewer independent verdicts
- `audit/proofs/report-before.txt` — pre-audit lifecycle snapshot (Completed)
- ARB receipt: `artifacts/receipts/arb-step-unittest-bfa0cd356e414362937425bac3e7a33a.json`
- Commits: `68149232` (GHI #667), `155cd16a` + `7fb44884` (GHI #668)

## Recommendations

- **GHI #669** (non-blocking): add a mechanical `gz validate` writer-coverage audit so future OBPI-status writers cannot bypass the terminal rule — promoting the now-convention to a fail-closed guard. Candidate for the ADR's deferred-in-keel (BI #3-gated) breadth work.

## Attestation

- **Agent (audit driver):** pipeline-orchestrator — audit executed to completion; all shortfalls resolved; ledger proof complete; fidelity gate green; both independent reviewers cleared VALIDATED. Signed on the evidence above.
- **Human (Gate-5):** g0 — operator verbal audit attestation relayed into the `validated` receipt (below), the Gate-5 human moment for the COMPLETED→VALIDATED transition. OBPI-level Gate-5 was attested at each OBPI's completion (2026-07-04).
