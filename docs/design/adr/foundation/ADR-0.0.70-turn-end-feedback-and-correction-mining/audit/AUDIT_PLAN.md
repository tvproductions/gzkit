# AUDIT PLAN (Gate-5) — ADR-0.0.70

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.70-turn-end-feedback-and-correction-mining |
| ADR Title | Turn-End Feedback and Ground-Truth Correction Mining |
| SemVer | 0.0.70 |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining |
| Audit Date | 2026-06-13 |
| Auditor(s) | g0 (operator, Gate 5) + main-session agent (pipeline-orchestrator) |

## Purpose

Confirm ADR-0.0.70 implementation is complete by validating its claims with
reproducible CLI evidence and a live demonstration of each delivered surface,
moving the ADR COMPLETED → VALIDATED.

**Audit Trigger:** Gate-5 validation — standalone `/gz-adr-audit` invocation
following the 2026-06-13 closeout-ready state (all 4 OBPIs `attested_completed`).

## Scope & Inputs

**Primary contract surfaces (one per OBPI):**

- OBPI-01 — Stop-hook turn-end feedback: `.claude/hooks/stop-turn-feedback.py`
  (generated from `src/gzkit/hooks/scripts/quality.py`), `Stop` wiring owned by
  `src/gzkit/hooks/claude.py`, drift coverage in `src/gzkit/sync_surfaces.py`.
- OBPI-02 — Session-correction-mining: `src/gzkit/insights/correction_mining.py`
  + `.gzkit/chores/session-correction-mining/` chore package.
- OBPI-03 — Guardrail-feedback-prose rule: `.gzkit/rules/guardrail-feedback-prose.md`
  (Stop hook is its first enforcement consumer).
- OBPI-04 — Fourth-source triangulation:
  `docs/governance/harness-engineering-appraisal.md` Buetow section + campaign B.0.

**Governance / health surfaces:**

- `uv run gz adr audit-check ADR-0.0.70` — ledger proof (Layer 2)
- `uv run gz cli audit` — CLI doc coverage
- `uv run gz validate --unscoped-rules --advisory-scorecard` — rule surfaces

## Claims extracted from ADR prose → checks

| # | ADR claim | Check |
|---|-----------|-------|
| C1 | Deterministic sensor fires at the turn boundary; blocks with 3-part prose; fails open | `.claude/hooks/stop-turn-feedback.py --demo` |
| C2 | Read-only ground-truth miner over `~/.claude/projects`; candidates-only; fail-soft | `python -m gzkit.insights.correction_mining --dry-run` |
| C3 | Guardrail-feedback-prose rule is binding, versioned, scorecard-classified | `gz validate --unscoped-rules`, `--advisory-scorecard` |
| C4 | Fourth-source Buetow section + campaign B.0 amendment landed | `rg Buetow …appraisal.md`, `rg "B.0 ADR-0.0.70" …campaign.md` |
| C5 | All BEHAVIOR REQs proven; non-BEHAVIOR REQs prove via declared channels | `gz adr audit-check ADR-0.0.70 --json` (`coverage_blocking: []`) |
| C6 | Both scripts stdlib-only (Boundary Invariant 3) | quality-reviewer source read |
| C7 | STRUCTURAL-FENCE REQs trace to parent ADR `## Boundary Invariants` | spec-reviewer trace |

## Planned Checks

| Check | Command / Method | Expected Signal | Status |
|-------|------------------|-----------------|--------|
| Ledger proof | `uv run gz adr audit-check ADR-0.0.70` | PASS, all 4 OBPIs complete | Planned |
| Coverage (blocking) | `uv run gz adr audit-check ADR-0.0.70 --json` | `coverage_blocking: []` | Planned |
| CLI audit | `uv run gz cli audit` | passed; 105/105 covered | Planned |
| C1 Stop hook | `uv run python .claude/hooks/stop-turn-feedback.py --demo` | BLOCKED prose, 3 parts, exit 0 | Planned |
| C2 Miner | `uv run python -m gzkit.insights.correction_mining --dry-run` | cluster summary, no writes | Planned |
| C3 Rule | `uv run gz validate --unscoped-rules` / `--advisory-scorecard` | both green | Planned |
| C4 Docs | `rg Buetow …`, `rg "B.0 ADR-0.0.70" …` | section + B.0 present | Planned |
| Independent spec trace | spec-reviewer subagent | REQ-kind table, no BEHAVIOR uncovered | Planned |
| Independent structural review | quality-reviewer subagent | surfaces cohere | Planned |

## Risk Focus

- **The 60% covers-figure.** Highest-risk seam: is it a real coverage gap or an
  artifact of counting non-BEHAVIOR REQs? Resolved by independent spec-reviewer
  trace + `coverage_blocking: []`.
- **Generated-surface revert.** Could the `Stop` phase be silently reverted by
  settings sync? Resolved by quality-reviewer ownership-chain read.
- **Miner silent decay.** "Fence with no recorded intrusions" — does the miner
  decay invisibly? Flagged by quality-reviewer.

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under `audit/proofs/` and referenced in `audit/AUDIT.md`.
- Value demonstrated (Step 3) with live output for each of the four surfaces.
- No blocking ✗; ADR lifecycle confirmed `Validated` post-receipt.
- No edits to accepted ADR prose.

## Attestation Placeholder

Operator completes in `AUDIT.md` via the verbal audit-acceptance ceremony
(`gz adr audit-begin` → verbal `accept audit` → `gz adr emit-receipt --event
validated` → `gz adr audit-end`).
