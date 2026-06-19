# AUDIT — ADR-0.0.73-verification-layer-binding-audit

**Lane:** heavy · **Kind:** foundation · **Audit date:** 2026-06-19
**Transition:** COMPLETED → VALIDATED
**Driver persona:** pipeline-orchestrator

## What the operator gets

A verification layer that is itself verified. Every QC step now carries a
negative control it must fail on, and every ADR thesis is run against the
running system before it is trusted. This audit holds ADR-0.0.73 to its own
standard — and the standard held: the audit surfaced three real
verification-layer defects (all fixed) and one backfill flag against the
audit's own evidence (resolved by operator-attested exemption). The ADR does
not become the facade it was built to prevent.

## 1. Fidelity Gate (bound — `gz adr fidelity ADR-0.0.73`)

`Summary: 8 pass, 0 fail` (proof: `proofs/fidelity.txt`). The gate parses the
ADR Decision's `## Fidelity Assertions` block and RUNS each command against the
running system, comparing observed vs expected exit. Representative rows:

| Claim | Command | Expected | Observed | Result |
|-------|---------|:--------:|:--------:|:------:|
| ADR evaluator bound to substance, no shape-graded mismatch | `gz validate --qc-binding` | 0 | 0 | PASS |
| Every bound QC step has a genuine negative control; `_NEGATIVE_CONTROL_DEBT` empty | `python -c "...len(_NEGATIVE_CONTROL_DEBT)==0..."` | 0 | 0 | PASS |
| Fidelity-presence enforcement green over corpus | `gz validate --fidelity-presence` | 0 | 0 | PASS |
| Waiver-ratchet honesty green over registered surfaces | `gz validate --waiver-ratchet` | 0 | 0 | PASS |

All 8 assertions pass (Boundary Invariant #5 — the meta-audit ADR passes the
very check it introduces).

## 2. Execution Log

| Check | Command | Result | Proof |
|-------|---------|:------:|-------|
| Ledger proof (L2) | `gz adr audit-check ADR-0.0.73` | ✓ PASS (9/9 OBPIs evidenced; 12 advisory non-blocking SUPPORT/FENCE) | `proofs/audit-check.txt` |
| Fidelity gate | `gz adr fidelity ADR-0.0.73` | ✓ 8 pass / 0 fail | `proofs/fidelity.txt` |
| Heavy gates | `gz gates --adr ADR-0.0.73` | ✓ Gates 1–4 PASS; Gate 5 manual (this ceremony) | `proofs/gates.txt` |
| CLI governance | `gz cli audit` | ✓ 108/108 commands covered | `proofs/cli-audit.txt` |
| Scoped unit tests | `unittest test_qc_binding_self_check + _scope` | ✓ OK | `proofs/unittest-scoped.txt` |
| Full suite (closeout) | `arb-step-unittest-4611588c` | ✓ exit 0, 0 BEHAVIOR-uncovered | ledger |

## 3. Independent Verification (fresh-context subagents)

- **spec-reviewer → VALIDATE-OK.** Per-OBPI REQ coverage REAL across all 9 (no
  tautologies); 4-part thesis genuinely in code (registry derived from
  `gz check`; 36 bound steps each exercise a real negative control;
  `gz adr fidelity` RUNS the assertions; closeout + audit invoke the SAME
  `assert_fidelity_for_ceremony` — one gate, two consumers). Repaired OBPI-02/07
  now carry real binding, not the green-by-construction facade that caused their
  repudiation. Minor non-blocking note: static `theater_flags` is `[]` in the
  live registry — consistent with the behavioral-not-static doctrine (the
  negative-control channel is the live guard and is wired for all 36 steps).
- **quality-reviewer → COHERENT-CAPABILITY** (closeout ceremony, same unchanged
  artifacts). The 9 OBPIs compose into one self-verifying loop; no dead code
  (the OBPI-0.0.37 repudiation signature is absent). Non-blocking maintainability
  flag: `trust_audits/qc_binding.py` is 833 lines (>600 limit) — extract the ~36
  negative-control fixtures.

## 4. Shortfalls & Remediation

| # | Shortfall | Severity | Resolution |
|---|-----------|----------|------------|
| 1 | `audit-check` covers-backfill flag on REQ-06-01/06-03 (`@covers` re-anchored at closeout, post-receipt) | Blocking | Operator-attested inline `# audit-exempt: regression-invariant-overlay` markers added (the designed mechanism per `.claude/rules/adr-audit.md`); both tests structurally ARE their REQs (spec-reviewer confirmed). audit-check re-run → exit 0. |

Three verification-layer defects surfaced earlier in the closeout (GHI #629 hook
full-slug match, GHI #630 closeout-proof early-return dispatch, OBPI-06 `@covers`
drift) were all fixed and committed before this audit.

## 5. Summary

| Dimension | Status |
|-----------|--------|
| Completeness | 9/9 OBPIs completed with evidence |
| Integrity | Fidelity gate 8/8; no unresolved ✗ |
| Alignment | Code ⇄ docs ⇄ tests coherent; `mkdocs --strict` clean |
| Value | The ADR passes its own check; the audit exercised its thesis |

## 6. Attestation

- **Agent (audit):** pipeline-orchestrator driver — all mechanical checks green,
  fidelity gate bound and passing, independent spec/quality review VALIDATE-OK /
  COHERENT-CAPABILITY, sole shortfall resolved via operator-attested exemption.
- **Human (Gate 5):** each linked OBPI was attested at completion (g0); ADR-level
  audit acceptance recorded via `gz adr emit-receipt --event validated`.
