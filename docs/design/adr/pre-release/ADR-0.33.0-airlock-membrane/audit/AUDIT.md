# ADR-0.33.0-airlock-membrane — Validation Audit

**Lifecycle transition:** COMPLETED → VALIDATED
**Lane:** heavy · **Kind:** feature (0.33.0) · **Release:** [v0.33.0](https://github.com/tvproductions/gzkit/releases/tag/v0.33.0)
**Audit date:** 2026-07-12 · **Driver persona:** pipeline-orchestrator

---

## 1. Fidelity Gate (bound — Step 3)

`uv run gz adr fidelity ADR-0.33.0-airlock-membrane` — **4 pass, 0 fail** (re-run fresh after the #679 code change).

| Claim | Command | Expected | Observed |
|-------|---------|:--------:|:--------:|
| Airlock-IN's ping consumes the HULL reach | `gz ontology reach ADR-0.32.0-gzkit-ontology` | 0 | 0 ✓ |
| Airlock-IN computes seam-map + reaches go/no-go | `gz airlock in --target OBPI-0.33.0-01 --phase build --dry-run` | 0 | 0 ✓ |
| §5 enforcement floor verifies the live NC | `gz validate --qc-binding` | 0 | 0 ✓ |
| Airlock-OUT emits drift-diff + logs to L2 | `gz airlock out --target OBPI-0.33.0-01 --dry-run` | 0 | 0 ✓ |

The gate RUNS the ADR's thesis against the running system — not prose. Proof: `audit/proofs/fidelity.txt`.

## 2. Execution Log (mechanical checks)

| Check | Command | Result |
|-------|---------|:------:|
| Gate 1 (ADR) | `gz gates --adr ADR-0.33.0` | ✓ PASS |
| Gate 2 (TDD) | `gz test` | ✓ PASS |
| Gate 3 (Docs) | `mkdocs build --strict` | ✓ PASS |
| Gate 4 (BDD) | `behave features/` | ✓ PASS |
| Full unit suite | `gz arb step --name unittest` | ✓ 7014 tests, exit 0 (`arb-step-unittest-6ec9218a`) |
| Lint | `gz arb ruff` | ✓ exit 0 (`arb-ruff-478d5327`) |
| Typecheck | `gz arb typecheck` | ✓ exit 0 (`arb-step-typecheck-4770e2af`) |
| CLI audit | `gz cli audit` | ✓ 125/125 commands covered |
| qc-binding | `gz validate --qc-binding` | ✓ no QC theater |

Gate 5 (Human): this audit acceptance.

## 3. REQ Coverage — REQ-kind-aware (ADR-0.0.59)

`gz adr audit-check` reports 25/33 raw `@covers`. Independently traced by spec-reviewer: the 8 "uncovered" REQs are all SUPPORT or STRUCTURAL-FENCE by kind — the raw figure reflects **correct kind routing, not a coverage gap**.

| OBPI | REQs | BEHAVIOR | SUPPORT | STRUCTURAL-FENCE |
|------|:----:|:--------:|:-------:|:----------------:|
| 01 data-model+events | 6 | 4 | 2 | — |
| 02 airlock-in tracer | 7 | 6 | 1 | — |
| 03 airlock-out tracer | 5 | 5 | — | — |
| 04 mx door | 4 | 4 | — | — |
| 05 permitted-entry door | 7 | 6 | — | 1 |
| 06 doctrine-lawful | 4 | — | 2 | 2 |
| **Total** | **33** | **25** | **5** | **3** |

- **All 25 BEHAVIOR REQs** carry real, semantically-derived `@covers` tests (spec-reviewer spot-confirmed non-tautological — assertions break if behavior changes).
- **5 SUPPORT REQs** proven by ledger event + structural validator; channel evidence on disk (seam_map.json; `AirlockInEvent`/`AirlockOutEvent` in events.py; `airlock-in-unaccounted-seam` registered + wired, not orphaned).
- **3 STRUCTURAL-FENCE REQs** proven by parent-ADR `## Boundary Invariants` #2/#3/#4.

## 4. Independent Review (persona dispatch)

**spec-reviewer — PASS.** Every BEHAVIOR REQ (25/25) has genuine semantic coverage; all 8 raw-uncovered REQs correctly non-`@covers` by kind with existing proof channels. No false "all covered"; no red `validated` thesis masked.

**quality-reviewer — COHERENT.** The six OBPIs compose into ONE symmetric airlock membrane:
- **BI #3 (one primitive, never fork)** — exactly one `airlock_enter`/`airlock_exit`; pipeline (`pipeline_runtime.py:546/582`), mx (`mx_cmd.py:105/135`), permitted-entry (`permitted_entry.py:241/278`) all CALL it, none forks.
- **Symmetry** — airlock-OUT is a first-class co-equal mirror, not a stub.
- **BI #1 (never writes L1)** — every write is `ledger.append` (L2-only); corrections surface as `LawProposal`, never applied.
- **BI #3 (gate ≠ completion attestation)** — no Gate-5 emission in the package.

## 5. #679 Follow-up (post-attestation corrective fix)

Commit `89c5ee9a` (`fix(airlock): make exit-side L2 booking failure-atomic`) landed after OBPI attestation. Both reviewers independently confirmed it **strengthens** the ADR: the `try/finally` books a terminal `airlock_out` (`Verdict.ABORTED`) if the exit's fallible work raises, keeping every transit paired on both edges, within the L2-only fence, re-propagating the exception (failure-atomic, not swallowing). Added `test_failed_exit_still_books_paired_aborted_airlock_out` under `@covers("REQ-0.33.0-03-04")` — coverage strengthened, none orphaned. GHI #679 CLOSED.

## 6. Shortfalls

**None.** No incomplete implementations, no code≠docs≠tests misalignment, no missing value demonstration, no unresolved anomalies. The fidelity gate exercises the thesis live; both independent reviews pass.

## 7. Attestation

- **Mechanical + fidelity + independent review:** all pass (this document).
- **Human attestation:** OBPI-level Gate 5 attested per-OBPI (6/6 `attested_completed`, g0) + ADR closeout `Completed` (g0, 2026-07-12). ADR-validation acceptance recorded via `gz adr emit-receipt --event validated` on operator verbal audit acceptance.

**Agent audit sign-off:** evidence verified, fidelity gate green, two independent reviews pass, zero shortfalls — recommend VALIDATED.
