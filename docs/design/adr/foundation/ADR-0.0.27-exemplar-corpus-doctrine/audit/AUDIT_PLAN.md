# AUDIT PLAN — ADR-0.0.27 Exemplar-Corpus Doctrine

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.27-exemplar-corpus-doctrine |
| ADR Title | Exemplar-Corpus Doctrine |
| SemVer | 0.0.27 |
| Kind / Lane | foundation / heavy |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine |
| Audit Date | 2026-05-05 |
| Auditor(s) | agent (Claude Opus 4.7) drafting; operator attesting |

## Purpose

Confirm ADR-0.0.27 implementation is complete by validating each of the seven landed invariants against reproducible CLI evidence. Authority of this audit is the **Layer 2 trust model** — Layer 1 ARB receipts and `obpi-audit.jsonl` proof per OBPI are inherited; this audit verifies presence of proof, integrated value demonstration, and lifecycle propagation, not re-verification of unit-level claims.

**Audit Trigger:** Final OBPI (`OBPI-0.0.27-07-link-integrity-validator`) attested at `2026-05-05T12:10:05Z`; ADR closeout phase = `pre_closeout`, QC Readiness = PENDING (Gate 5). Standard pre-closeout audit gate.

## Scope & Inputs

**Primary contract surfaces:**

- `gz validate --complexity-doctrine-links` (new validator scope, OBPI-07)
- `gz validate --advisory-scorecard` (Mechanical scorecard entry for the new rule, OBPI-01)
- `gz adr audit-check ADR-0.0.27` (Layer-2 ledger proof aggregator)
- `gz closeout ADR-0.0.27 --dry-run` (closeout-readiness preview)
- `data/exemplar_corpus.json` (pinned 13-project corpus, OBPI-02)
- `src/gzkit/complexity/measurement.py` (measurement pipeline, OBPI-03)
- `docs/governance/complexity/baselines/2026-05-04/` (raw distribution baseline, OBPI-03)
- `docs/governance/complexity/distilled-characteristics-2026-05-04.md` (distilled doctrine, OBPI-04)
- `src/gzkit/complexity/citation.py` + `src/gzkit/schemas/complexity_citation.json` (citation contract, OBPI-05)
- `.gzkit/skills/gz-complexity-distill/SKILL.md` (distill ceremony skill, OBPI-06)
- `.gzkit/rules/complexity-doctrine.md` (canonical rule, OBPI-01 + OBPI-05 amendments)

**System health surfaces:**

- `uv run gz cli audit` (CLI cross-coverage)
- `uv run gz adr report 0.0.27` (lifecycle table)

## Planned Checks

| Check | Command / Method | Expected Signal | Status (Planned) |
|-------|------------------|-----------------|------------------|
| Layer-2 ledger proof aggregation | `uv run gz adr audit-check ADR-0.0.27 --json` | `passed: true`, 7/7 OBPIs, 50/50 REQs | Pending |
| New validator scope wired | `uv run gz validate --complexity-doctrine-links` | Exit 0, "All validations passed (1 scopes)" | Pending |
| Advisory scorecard entry honored | `uv run gz validate --advisory-scorecard` | Exit 0, no violations | Pending |
| Pinned corpus shape | inspect `data/exemplar_corpus.json` | 13 projects, all 10 archetypal cells, 40-char SHAs | Pending |
| Baseline artifacts present | list `docs/governance/complexity/baselines/2026-05-04/` | `baseline.json`, `baseline.summary.md` | Pending |
| Distilled-characteristics document present | list `docs/governance/complexity/` | dated distilled-characteristics file | Pending |
| Distill skill present and synced | list `.gzkit/skills/gz-complexity-distill/` + `.claude/skills/gz-complexity-distill/` | both contain `SKILL.md` | Pending |
| Heavy-lane gate aggregate | `uv run gz gates --adr ADR-0.0.27` | Gates 1-4 PASS, Gate 5 PENDING manual | Pending |
| CLI cross-coverage | `uv run gz cli audit` | "CLI audit passed", 91/91 commands | Pending |
| Closeout readiness preview | `uv run gz closeout ADR-0.0.27 --dry-run` | 7/7 OBPI complete, all proof FOUND | Pending |
| Pre-attestation lifecycle | `uv run gz adr report 0.0.27` | Lifecycle: Pending, Closeout: READY | Pending |
| Post-attestation lifecycle | `uv run gz adr report 0.0.27` after receipt emit | Lifecycle: Validated | Pending |

## Risk Focus

- **Foundation-kind cluster citations.** ADRs 0.0.28 / 0.0.29 / 0.0.30 are pool stubs that will cite the distilled-characteristics document; the link-integrity validator must correctly flag broken citations once those ADRs land. This audit confirms the validator runs clean on the *current* (no-citing-ADR-yet) state, with the exit-3 contract preserved for future drift.
- **Corpus contamination.** Per-project path filters (declared in OBPI-02) protect the corpus from strategically-complex modules pulling distributions toward leniency. This audit confirms the pinned corpus shape and SHA-pinning discipline; full path-filter coverage was witnessed at OBPI-02 attestation.
- **Distillation cold-start.** The first distilled-characteristics document (`2026-05-04`) has no prior-distillation diff — diff-narration is no-op on first run. Documented in OBPI-04 brief; not a regression.
- **Vendor-mirror drift on the distill skill.** OBPI-06 amended Allowed Paths to remove vendor mirrors per `skill-surface-sync.md` Rule #4; this audit confirms canonical-only edit shape under `.gzkit/skills/`.

## Findings Placeholder

Captured in `AUDIT.md`.

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under `audit/proofs/` and referenced in `audit/AUDIT.md`.
- ADR present in lifecycle index with correct state; `gz adr report 0.0.27` shows `Validated` after receipt emit.
- No edits to accepted ADR prose; remediation via follow-up ADR if required.
- Operator's verbal `accept audit` / `verify audit` ack relayed into ledger receipt under the `agent-relayed-operator-attestation` branch.

## Attestation Placeholder

Operator completes in `AUDIT.md` § Attestation with verbatim ack + agent enrichment.
