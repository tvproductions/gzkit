# Summary

Pass A audit of rule-pair conflicts across 21 files in scope (19 under
`.gzkit/rules/`, plus `AGENTS.md` and `CLAUDE.md`). Derivative vendor
mirrors out of scope.

## Counts

- Blocking (monthly+, multiple GHI hits in the #141–#268 window): **4**
- Episodic (class-specific; observed once in the GHI trail or limited to a
  specific lane/kind combination): **6**
- Theoretical (latent contradiction with no observed GHI hit): **2**
- Total conflicts: **12**

## Severity classification

- Row 1 (`tests.md` § Red-Green-Refactor vs `tool-skill-runbook-alignment.md` § Invariant 3): **blocking** — GHI #227 (6f relocation), GHI #230 (anchor output-form claims to locking tests), GHI #229 (cross-surface contradictions), GHI #149/#150/#151 (original Invariant 3 plumbing). Conflict fired across at least 5 commits in the #141–#268 window.
- Row 2 (`arb.md` § When to Use ARB vs `attestation-enrichment.md` § Lane behavior): **blocking** — GHI #225 (align arb.md example), GHI #229 (scope contradiction explicitly named in `arb.md` header). The file's own "Last reviewed" note marks this as a repeat defect.
- Row 3 (Invariants 2/4 vs scope boundary + `defect-fix-routing.md`): **blocking** — GHI #195 rule authored to close the OBPI-0.0.16-04 → OBPI-06 → revert drift; the class is named "default failure mode" in the rule itself.
- Row 4 (`brief-heading-conventions.md` § Canonical vs § "if present, is H3" exception): **episodic** — GHI #238 landed the mechanical check after silent hook failures; only one confirmed fire in the trail.
- Row 5 (`cross-platform.md` § Console Output vs § Scope boundary): **blocking** — GHI #234 (runtime UTF-8 guard scope clarification); conflict fired on the first cross-platform helper-script-pipe session and the scorecard still lists row 45a as Promotable.
- Row 6 (Invariant 10a vs Invariants 11/13): **theoretical** — no observed GHI hit; latent pairing of recent (10a) and older (11/13) invariants with no precedence declared.
- Row 7 (`defect-fix-routing.md` direct-fix vs `cli.md` Heavy-lane trigger): **episodic** — the rule cites GHI #189 as direct-fix precedent; `cli.md` wording would have routed it to Heavy. Class resolved only by precedent citation, not by rule-text reconciliation.
- Row 8 (`arb.md` Mandatory for defect GHI vs RED-receipt prohibition in `tests.md` + `attestation-enrichment.md`): **episodic** — tracked under GHI #157 pending the RED/GREEN receipt stream; observable when a failing-test captures a real defect for filing.
- Row 9 (Never edit vendor mirrors vs Mirror version > canonical → promote): **theoretical** — conflict-resolution recovery text contradicts the non-negotiable rule but an operator following either path reaches a consistent state; no observed GHI hit.
- Row 10 (Commit-message discipline Option 2 vs `tests.md` tests-assert-semantics): **episodic** — same class-of-failure as Row 1; tied to the same GHIs (#227/#230) but observable at commit-message review time rather than at test-authoring time.
- Row 11 (Gate-5 lane rule vs Lite-lane foundation-kind walkthrough): **episodic** — post-ADR-0.0.18 class; observable once per foundation-kind OBPI. The Lite/foundation combination is rare enough that this fires on-demand rather than monthly.
- Row 12 (Unit-tier mock-everything vs behave exception + `_init_git_repo`): **episodic** — silent drift at `tests/commands/test_closeout_ceremony.py`; no GHI hit but the exception clause is openly used without documented justification.

## Top 5 blocking rows

1. **Row 1** — `tests.md` § "Tests assert semantics" vs `tool-skill-runbook-alignment.md` § Invariant 3. Single test file (`tests/commands/test_status.py`) sits at the collision point; repeated GHI hits (#227/#230/#229/#149/#150/#151) confirm the class of failure is live. Promoting the output-form check to a separate fixture closes the class.
2. **Row 2** — `arb.md` lane matrix vs `attestation-enrichment.md` § Lane behavior. The rule file's header ("Last reviewed: 2026-04-19 … resolve scope contradiction with attestation-enrichment.md; GHI #229") is itself evidence that the contradiction keeps surfacing. Collapsing to a single canonical cell eliminates drift.
3. **Row 3** — Invariants 2/4 "complete all work fully" vs the scope-boundary subsection + `defect-fix-routing.md`. Observed as "default failure mode" by the rule authors. Folding the test-for-scope into each invariant row closes the class.
4. **Row 5** — `cross-platform.md` runtime guard headline vs scope boundary. Fresh-interpreter helper scripts crash on UTF-8 codepoints despite agents following the headline rule. Scorecard already marks this row as Promotable; mechanical promotion closes the class.
5. **Row 10** — Commit-message discipline Option 2 (cite a test) vs `tests.md` tests-assert-semantics. Same source-class as Row 1 but observable at a different pipeline stage; same fixture-split resolution applies.

## Prioritized follow-up list

Each entry is sized for either a direct-fix GHI (10-line edit reconciling
rule wording in a single file) or a mechanical-promotion GHI (adds a
`gz validate --<scope>` check that distinguishes the two rules mechanically).

| Priority | Row(s) | Size | Type | Suggested GHI title |
|---|---|---|---|---|
| P0 | 1, 10 | Mechanical-promotion | Spin up `gz validate --skill-output-contract` with per-skill output-form fixtures. Unit tests retain semantic assertions; fixture owns string-shape check. | `feat(validate): add --skill-output-contract scope to split semantic tests from output-form fixtures (closes row 1 + row 10 of control-surface-rule-conflicts Pass A)` |
| P0 | 2 | Direct-fix | Remove the Lite/Heavy matrix duplication between `arb.md` and `attestation-enrichment.md` — cite one canonical table by reference. | `fix(rules): collapse arb.md lane matrix into attestation-enrichment.md canon (completes GHI #229 scope fix)` |
| P1 | 3 | Direct-fix | Inline the scope-boundary test into Invariant 2 and Invariant 4 row cells in `behavioral-invariants.md`. | `fix(rules): fold scope-boundary test into Invariants 2/4 row cells to prevent compact-table reading drift` |
| P1 | 5 | Mechanical-promotion | Promote row 45a of the advisory scorecard (helper-script UTF-8 reconfigure) to `gz validate --utf8-helper-scripts`. | `feat(validate): add --utf8-helper-scripts scope for ad-hoc python/jq invocations (promote scorecard row 45a)` |
| P1 | 11 | Direct-fix | Add a "Kind" column to the Lane Inheritance Rule table in `AGENTS.md`; retire the separate Foundation-kind rigor subsection. | `fix(rules): add Kind column to Lane Inheritance Rule table; eliminate foundation-kind subsection` |
| P2 | 4 | Direct-fix | Rename the per-pass evidence `### ACCEPTANCE` sub-block in `brief-heading-conventions.md` to avoid lexical collision with the top-level `## Acceptance Criteria`. | `fix(rules): rename per-pass ### ACCEPTANCE to ### Acceptance Evidence to prevent heading overload` |
| P2 | 7 | Direct-fix | Add a worked-example cross-reference in `cli.md` § Adding CLI Features distinguishing trivial string fixes (direct-fix per GHI #189) from schema/contract changes (Heavy per GHI #194). | `fix(rules): cross-reference defect-fix-routing.md from cli.md § Adding CLI Features with worked examples` |
| P2 | 8 | Direct-fix (interim) → Mechanical-promotion (long) | Split `arb.md` "defect GHI with QA evidence" row by passing vs failing QA; cite `tests.md` § RED evidence for the failing-QA case. Long-term: close via `ADR-pool.tdd-receipt-stream` (GHI #157). | `fix(rules): disambiguate arb.md "defect GHI" row for passing vs failing QA runs (interim until GHI #157 RED/GREEN receipts)` |
| P3 | 6 | Direct-fix | Declare a precedence ordering for invariants in `behavioral-invariants.md` — either ordered-list semantics ("lower-numbered wins") or per-row "defers to" cells. | `fix(rules): declare precedence ordering for behavioral invariants to resolve 10a vs 11/13 latent conflict` |
| P3 | 9 | Direct-fix | Re-word `skill-surface-sync.md` § Non-negotiable rule 4 to cite the § Conflict resolution recovery path as the canonical response when a mirror edit is discovered. | `fix(rules): reconcile skill-surface-sync.md non-negotiable rule 4 with § Conflict resolution recovery` |
| P3 | 12 | Mechanical-promotion | Require an inline justification comment (`# real-git-required: <REQ> — <reason>`) at every `_init_git_repo` callsite; AST scan fails closed. | `feat(validate): extend --test-tiers (GHI #209) to enforce real-git-required justification comments` |

---

Pass A is complete when these three files exist under
`ops/chores/control-surface-rule-conflicts/proofs/`: `rule-inventory.md`,
`conflict-matrix.md`, `summary.md`. No rule files were modified.
