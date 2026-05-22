# Evaluation Scorecard: ADR-0.0.56-closeout-defect-accounting-invariant

**Evaluated:** 2026-05-22
**Framework:** gz-adr-evaluate v6.0.0 (8 ADR dimensions + 5 OBPI dimensions)
**Method:** CLI deterministic pre-screen + independent persona-dispatched manual scoring (`spec-reviewer` for spec/decomposition dimensions, `quality-reviewer` for architectural dimensions). The manual scorecard supersedes the CLI pre-screen.

## Verdict: **GO** — ready for proposal/defense review

| | Result |
|---|---|
| CLI pre-screen | 3.55/4.0 — **NO GO** (two heuristic misfires: dim 8 scored 1; OBPI-02 independence scored 1) |
| Manual ADR weighted total | **3.90/4.0** — GO (≥ 3.0) |
| OBPI averages | All six ≥ 3.0; no OBPI dimension scored 1 on independent review |

**CLI NO-GO overturned — both causes are heuristic false negatives:**

1. **Dimension 8 (Architectural Alignment), CLI 1 → manual 4.** The CLI heuristic looks for `src/gzkit/...` path references *in the ADR body* and flagged "no source file path references." Foundation-invariant ADRs carry source paths in their OBPI briefs (e.g. `closeout.py:359`, `obpi_stages.py:224`), not the ADR narrative. The `quality-reviewer` read the ADR and verified architectural alignment with path-level evidence — reuses existing surfaces (`gz closeout` event, `gz check --json`), composes with ADR-0.0.36 without overlap, correctly differentiates from `ADR-pool.contract-surface-mechanical-defenses`, cites `.claude/hooks/ghi-triage-chat-silence.py` as the hook exemplar. Manual score: 4.
2. **OBPI-02 independence, CLI 1 → manual 3.** The CLI heuristic conflated *any declared cross-OBPI predecessor* with the rubric's score-1 condition "cannot be started without **most** other OBPIs first." OBPI-02 declares exactly one predecessor (OBPI-01) of five siblings — the rubric maps "depends only on declared predecessors" to score **3**. OBPI-02 is a complete, independently-testable unit once OBPI-01 lands; a sequential dependency within one ADR is normal, on-doctrine decomposition. Manual score: 3. No revision required.

## ADR Dimension Scores

| # | Dimension | Weight | CLI | Manual | Rationale / CLI reconciliation |
|---|-----------|--------|-----|--------|--------------------------------|
| 1 | Problem Clarity | 15% | 3 | **4** | Three dated recurrences named with GHI numbers (#486/#489/#490) and verbatim agent excuses; before/after states explicit. CLI scored 3 ("no after/target-state language in Intent") — false negative: the after-state is the invariant statement in § Decision, which the CLI's Intent-only scan misses. |
| 2 | Decision Justification | 15% | 4 | **4** | Every decision item carries an independent "why"; 8 rejected alternatives with specific dismissals; forcing-function analysis in § Consequences. CLI and manual agree. |
| 3 | Feature Checklist Completeness | 15% | 4 | **4** | Six items, each a distinct necessary capability; 1:1 with six OBPI briefs; contiguous numbering. CLI and manual agree. |
| 4 | OBPI Decomposition Quality | 15% | 4 | **4** | One separable surface per OBPI; acyclic dependency graph with declared `{04,05}` parallelization; conflated-OBPI alternative explicitly rejected (§ Alternatives #6). CLI and manual agree. |
| 5 | Lane Assignment Correctness | 10% | 4 | **3** | ADR-level Heavy correctly justified; 5/6 OBPI lanes unambiguously Heavy. CLI scored 4; manual 3 caught OBPI-06's debatable Heavy lane (docs/scorecard/test only). **Remediated post-evaluation**: OBPI-06 re-marked Lite per AGENTS.md § Lane Rules. |
| 6 | Scope Discipline | 10% | 4 | **4** | Explicit "Scope boundary" subsection with 4 non-goals; per-OBPI enumerated Denied Paths; creep tested against pre-mortem scenarios. CLI and manual agree. |
| 7 | Evidence Requirements | 10% | 4 | **4** | Every OBPI has runnable Verification commands, a Demo section, and REQ-coded Acceptance Criteria. CLI and manual agree. |
| 8 | Architectural Alignment | 10% | 1 | **4** | CLI 1 → manual 4 — heuristic false negative (see verdict §1 above). Reuses existing surfaces; composes with ADR-0.0.36; differentiated from `ADR-pool.contract-surface-mechanical-defenses`; port-vs-adapter framing justifies the one novel pattern. |

**Weighted total: 3.90/4.0** — `(4·0.15)×4 [dims 1–4] + 3·0.10 + 4·0.10 + 4·0.10 + 4·0.10 [dims 5–8]`.

## OBPI Dimension Scores (manual, `spec-reviewer`)

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|:-:|:-:|:-:|:-:|:-:|:-:|
| 01 closeout-defect-baseline-snapshot | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 02 closeout-defect-accounting-reconcile-scope | 3 | 4 | 4 | 3 | 4 | 3.6 |
| 03 routing-receipt-model-completion-gate | 3 | 4 | 4 | 3 | 3 | 3.4 |
| 04 obpi-complete-defect-accounting | 3 | 4 | 3 | 3 | 3 | 3.2 |
| 05 ghi-close-defect-accounting-backstop | 3 | 3 | 3 | 3 | 3 | 3.0 |
| 06 prime-directive-scorecard-reclassification | 3 | 4 | 3 | 4 | 4 | 3.6 |

All six average ≥ 3.0. No OBPI dimension scored 1 on independent review. (The CLI pre-screen scored several OBPI Size/Independence dimensions lower — same heuristic class as the OBPI-02 misfire; the manual scores are authoritative.)

## Findings Remediated Post-Evaluation

All findings were minor (none structural); all corrected before this scorecard was finalized:

1. **OBPI-03 / OBPI-04** — `closeout_defect_accounting.py` Allowed-Path prose said `**CREATE**` while the text read "landed by OBPI-02," an internal contradiction. Reworded: the `CREATE` marker records the path is net-new at brief-authoring time; sequence ownership (OBPI-02 lands, OBPI-03/04 extend) is stated explicitly.
2. **OBPI-04** — a conditional fork ("may add a new OBPI-snapshot event class only if…") was made decisive: the OBPI-completion anchor is a discriminated field on the existing snapshot event; a parallel event class is forbidden, and an infeasible reuse is a STOP-on-BLOCKERS escalation.
3. **OBPI-05** — the PreToolUse hook filename `ghi-close-defect-accounting.py` is now pinned in REQ #1, not only referenced in the Demo.
4. **OBPI-06** — re-marked **Lite** (was Heavy): its surface is documentation, a governance scorecard, and one test file — no command/API/schema/runtime-contract surface — so AGENTS.md § Lane Rules places it Lite.

## Gate Decision

**GO** — ADR-0.0.56 proceeds to proposal/defense review. Parent tracker GHI #514 closes `superseded` against this ADR; implementation lifecycle (per-OBPI gates, attestation) belongs to the ADR thereafter.
