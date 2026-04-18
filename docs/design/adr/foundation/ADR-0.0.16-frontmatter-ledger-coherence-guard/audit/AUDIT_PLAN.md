# AUDIT PLAN (Gate-5) — ADR-0.0.16

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.16 |
| ADR Title | Frontmatter-ledger coherence guard and chore audit |
| SemVer | 0.0.16 |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard |
| Audit Date | 2026-04-18 |
| Auditor(s) | agent:claude-opus-4-7[1m] (post-attestation validation) |

## Purpose

Confirm ADR-0.0.16 implementation is complete by validating its claims with reproducible CLI evidence. The five OBPIs are attested-complete; this audit promotes the ADR from `Completed` to `Validated` by verifying ledger proof, demonstrating the delivered capabilities, and triaging any remaining shortfalls.

**Audit Trigger:** Post-attestation Gate 5 validation — all 5 OBPIs attested_completed (see `gz adr status ADR-0.0.16`), closeout phase = `attested`, closeout QC = `READY`.

## Scope & Inputs

**Primary contract surfaces introduced or modified:**

- `uv run gz validate --frontmatter` — new guard (OBPI-01)
- `uv run gz validate --frontmatter --explain <ADR-ID>` — remediation mode (OBPI-01)
- `uv run gz gates` — wired frontmatter coherence into Gate 1 (OBPI-02)
- `uv run gz frontmatter reconcile [--dry-run]` — chore surface (OBPI-03)
- `uv run gz chores show frontmatter-ledger-coherence` — chore registration (OBPI-03)
- `src/gzkit/governance/status_vocab.py` — STATUS_VOCAB_MAPPING constant (OBPI-05)
- `docs/governance/state-doctrine.md` — status-vocabulary mapping addendum (OBPI-05)
- `config/chores/frontmatter-ledger-coherence.toml` — chore config (OBPI-03)
- `data/schemas/frontmatter_coherence_receipt.schema.json` — receipt schema (OBPI-03)

**System health surfaces used:**

- `uv run gz adr audit-check ADR-0.0.16` — Layer-2 ledger proof
- `uv run gz adr report ADR-0.0.16` — lifecycle confirmation
- `uv run gz adr status ADR-0.0.16` — closeout phase + OBPI roll-up
- `uv run -m unittest -q` — full unit suite
- `uv run mkdocs build --strict` — docs gate
- `uv run gz gates --adr ADR-0.0.16` — heavy-lane gates

## Planned Checks

| # | Check | Command / Method | Expected Signal |
|---|-------|------------------|-----------------|
| 1 | Ledger proof (Layer 2) | `uv run gz adr audit-check ADR-0.0.16 --json` | 5/5 OBPIs PASS; coverage ≥ 80% |
| 2 | Lifecycle snapshot | `uv run gz adr status ADR-0.0.16` | 5/5 attested_completed; closeout phase `attested` |
| 3 | Unit tests | `uv run -m unittest -q` | OK; ≥ 3000 tests; coverage ≥ 40% |
| 4 | Frontmatter guard clean | `uv run gz validate --frontmatter` | Exit 0 |
| 5 | Chore idempotence | `uv run gz frontmatter reconcile --dry-run --json` | `files_rewritten: []` |
| 6 | Heavy gates | `uv run gz gates --adr ADR-0.0.16` | All gates PASS |
| 7 | Docs build | `uv run mkdocs build --strict` | Zero warnings, zero errors |
| 8 | Governance lint | `uv run gz lint` | Lint passed |
| 9 | Config path coherence | `uv run gz check-config-paths` | No drift |
| 10 | CLI governance audit | `uv run gz cli audit` | No surface gaps |
| 11 | Status-vocab coverage | Import `STATUS_VOCAB_MAPPING`; inspect canonical targets | Non-empty; includes all observed frontmatter terms |
| 12 | GHI closures (REQ-06) | `gh issue view 162 167 168 169 170 --json state` | All `CLOSED` |
| 13 | Receipt presence | `ls artifacts/receipts/frontmatter-coherence/` | Three receipts per OBPI-04 evidence |
| 14 | Coverage map (OBPI-04) | `uv run gz adr audit-check ADR-0.0.16 --json` uncovered list | Only advisory-severity entries; no errors |

## Risk Focus

- **OBPI-04 uncovered REQs (REQ-04-01, 02, 03, 06, 07)** — evidence/workflow REQs that do not admit unit-test coverage by construction (one-time backfill receipts, GHI closure artifacts, brief Evidence section contents). Triage during audit — propose either `@covers` doc-annotations, evidence-link mapping, or documented exemption.
- **Chore cadence regression** — `gz tidy` integration / CI dry-run hookup is a Consequences-listed risk (Negative #9). Confirm the chore is registered and inspectable; note cadence integration as a future ADR if missing.
- **Frontmatter rewrite stickiness** — 257 files touched by live backfill; receipts preserve the ledger cursor, but verify the post-backfill state is still clean (no new drift introduced since 2026-04-18T10:04).
- **Validator ↔ chore parity (GHI #192)** — closed via `fix(validator)` commit `4e914dd0`. Re-confirm the pool-skip filter is still in place and tests still pass.

## Findings Placeholder

Captured live in `audit/AUDIT.md`.

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under `audit/proofs/` and referenced in `audit/AUDIT.md`.
- Feature Demonstration (Step 3) present — each capability shown with live output.
- Uncovered-REQ triage decisions recorded (doc-cover, exempt, or follow-up).
- Validation receipt emitted to ledger; lifecycle confirmed `Validated`.
