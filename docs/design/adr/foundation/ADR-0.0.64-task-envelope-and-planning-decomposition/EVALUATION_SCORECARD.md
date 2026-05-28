ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.64-task-envelope-and-planning-decomposition
Kind: foundation | Lane: heavy | Parent: ADR-0.22.0
Evaluator: gz-adr-evaluate (manual, persona-dispatched)
Personas: spec-reviewer (D1/D3/D4/D6, OBPI I/T/C), quality-reviewer (D2/D5/D7/D8, OBPI V/S)
Date: 2026-05-27

--- ADR-Level Scores (manual, authoritative) ---

| # | Dimension | Weight | CLI | Manual | Weighted | Reviewer | Note |
|---|-----------|--------|-----|--------|----------|----------|------|
| 1 | Problem Clarity | 15% | 1 | 3 | 0.45 | spec | CLI false-negative: regex looks for literal "before"/"after" tokens; ADR carries semantic before/after framing (`d70793c4` baseline → validator signatures) in Intent. Quantification present (`7,897` events, 8 worklog types, GHI cluster). Dense paragraph form costs the 4. |
| 2 | Decision Justification | 15% | 3 | 4 | 0.60 | quality | CLI false-negative on numbering heuristic — Decision uses inline `(1)..(5)` paragraph leads rather than top-of-line `1.` markdown lists. 11 rejected alternatives with category-error reasoning, primary-source citations (commits + GHIs), 10 named negative consequences with mitigations. |
| 3 | Feature Checklist | 15% | 4 | 4 | 0.60 | spec | Aligned. Each of 5 items is removable-test-coherent (removing breaks a specific validator signature or channel), names target paths + integration precedent + test obligations + lane justification. |
| 4 | OBPI Decomposition | 15% | 3 | 3 | 0.45 | spec | CLI overlap finding confirmed. OBPIs 02 and 03 both touch `src/gzkit/tasks.py` and `.gzkit/rules/task-discovery.md`. Decomposition is acyclic but 02/03 require strict serial ordering. Honest decomposition scorecard at ADR `:75-89`. Resolvable at /gz-obpi-specify (merge or declare serial). |
| 5 | Lane Assignment | 10% | 4 | 4 | 0.40 | quality | Aligned. New validator, ledger schema field, CLI surfaces, authoring discipline — all external-contract changes per AGENTS.md § Lane Rules. Heavy + foundation correct. |
| 6 | Scope Discipline | 10% | 4 | 3 | 0.30 | spec | CLI false-positive — no explicit `## Non-Goals` section; reader infers from Alternatives (revert `d70793c4`; required `task_id`; uniform `task_id`; pipeline auto-mint; etc.). `req_atomic` exemption is a known scope-expansion surface (Negative #4 names this). Heavy foundation ADR benefits from affirmative non-goals block. |
| 7 | Evidence Requirements | 10% | 4 | 3 | 0.30 | quality | CLI false-positive — checks section presence, not content specificity. ADR-level `## Evidence` is placeholder (`- [ ] Tests: tests/`). Per-OBPI verification uses generic commands rather than enumerating fixture matrix per validator signature. Score-3 advisory, not blocking. |
| 8 | Architectural Alignment | 10% | 4 | 4 | 0.40 | quality | Aligned. Stdlib-first respected (no new runtime deps); hexagonal port-vs-adapter framing explicit; T1/T2 binding correctly identified; restoration-is-additive principle preserved; invariance test applied. |

**WEIGHTED TOTAL: 3.50/4.0** (manual, supersedes CLI 3.25/4.0)
**THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)**

--- Architectural Lens Verdicts ---

| Lens | Verdict | Note |
|------|---------|------|
| Port-not-adapter (hexagonal) | PASS | ADR specifies contract (four-channel discovery + coherence semantics + subdivision sub-invariant); concrete classes are adapters. Port/adapter distinction correctly applied. |
| `@covers` precedent carries | PASS | Verified at `src/gzkit/traceability.py:201-245`. Decoration-time validation, module-level registry, source-location capture all translate one-for-one to `@advances`. |
| T1/T2 binding actual | PASS (1 residual risk) | Layered fail-close (Heavy fail / Lite warn) mechanically binds T1 rule to T2 enforcement. Residual: `req_atomic` exemption is itself a T1 surface depending on cultural attestation-review. Knowingly-accepted; named at ADR `:165` as most plausible 18-month failure. |
| State doctrine compliance | PASS | Validator pulls from Layer-2 ledger; `gz task fanout` and `gz status` render from worklog events. No Layer-3 view treated as source-of-truth. |
| Architectural Boundary 6 | PASS | `gz task fanout` readback is explicitly derived view; `attribution_check` column reflects validator state, not stored. No silent promotion. |

--- OBPI-Level Scores (manual, synthesized) ---

| OBPI | Indep | Test | Value | Size | Clarity | Avg | Verdict |
|------|-------|------|-------|------|---------|-----|---------|
| 01 task-id-worklog-schema-additive | 4 | 4 | 4 | 4 | 4 | 4.0 | GO |
| 02 advances-decorator-and-discovery | 3 | 3 | 4 | 3 | 3 | 3.2 | GO |
| 03 subdivision-driven-seq-advancement | 2 | 3 | 4 | 4 | 3 | 3.2 | GO |
| **04 gz-validate-task-envelope-coherence** | **2** | **2** | **4** | **3** | **2** | **2.6** | **BELOW THRESHOLD — revise via /gz-obpi-specify** |
| 05 gz-task-fanout-readback | 3 | 2 | 4 | 4 | 2 | 3.0 | GO (borderline) |

OBPI-04 root cause: Allowed Paths declare only the ADR package directory; the brief stub omits `src/gzkit/<validator module>`, `src/gzkit/schemas/<brief schema for req_atomic>`, the `gz check` pipeline file, and the `gz task envelope diagnose` subcommand surface. Verification commands run generic `test_persona_schema.py` rather than validator-signature tests. The gap between "ADR package only" Allowed Paths and "new validator + schema + CLI subcommand + pipeline integration" requirements text is by-design stub work that /gz-obpi-specify resolves.

OBPI-05 same gap shape, narrower surface.

OBPI-02/03 overlap on `src/gzkit/tasks.py` + `.gzkit/rules/task-discovery.md` — declared serialization, structurally clean but reduces parallelization.

--- Overall Verdict ---

**[x] GO** — ADR-0.0.64 ready for human proposal/defense review.

**Conditional on /gz-obpi-specify enrichment of OBPI-04 (and OBPI-05) before implementation:**
- OBPI-04 Allowed Paths must list `src/gzkit/<validator module>`, brief schema file, `gz check` integration file, `gz task envelope diagnose` CLI file.
- OBPI-04 Verification must enumerate fixture matrix per validator signature (no-task_id, default-bucket-only, layer-drift × four channels).
- OBPI-05 Allowed Paths must list `gz status` integration file, `gz task fanout` CLI file.
- OBPI-02 and OBPI-03 declare serial order in Discovery Checklist OR merge into single OBPI.

--- Action Items (for /gz-obpi-specify) ---

1. **OBPI-04 Allowed Paths** — list real `src/gzkit/` surfaces; replace placeholder verification commands with signature-specific fixture tests.
2. **OBPI-05 Allowed Paths** — list `gz status` and `gz task fanout` source files; verification must demonstrate table/detail/JSON output and status block.
3. **OBPI-02/03 ordering** — either merge or declare strict serial order on shared surfaces.
4. **Module-level test isolation hook** — OBPI-02 enrichment should specify parallel of `traceability.py:264` `reset_registry()` for `tasks.py`.
5. **Validator false-positive guard** — OBPI-04 signature (b) must spec inverse-bias: legitimately-atomic single-REQ OBPIs with only `seq=01` should not false-positive when `req_atomic` declared.

--- Advisory revision asks (non-blocking, optional polish before promotion) ---

1. Add explicit `## Non-Goals` section (3 items: revert `d70793c4`; plan-mode integration; required `task_id` everywhere). Closes D6 scope-discipline gap and CLI heuristic.
2. Add 2-sentence before/after lede atop Intent. Closes D1 problem-clarity dense-paragraph cost.
3. Fill in ADR-level `## Evidence` section with concrete fixture paths and receipt prefixes. Closes D7 placeholder gap.

--- CLI Reconciliation Summary ---

| Dimension | CLI | Manual | Direction | Heuristic |
|-----------|-----|--------|-----------|-----------|
| 1 | 1 | 3 | ↑ | False-negative: literal-token regex misses semantic before/after framing |
| 2 | 3 | 4 | ↑ | False-negative: numbering regex misses inline `(1)..(5)` paragraph leads |
| 3 | 4 | 4 | = | — |
| 4 | 3 | 3 | = | CLI overlap finding confirmed |
| 5 | 4 | 4 | = | — |
| 6 | 4 | 3 | ↓ | False-positive: no explicit `## Non-Goals` section; CLI infers from prose |
| 7 | 4 | 3 | ↓ | False-positive: section-presence check misses placeholder-content gap |
| 8 | 4 | 4 | = | — |

CLI net 3.25 → Manual net 3.50. Two upward corrections from CLI heuristic misses; two downward corrections from CLI section-presence false-positives.
