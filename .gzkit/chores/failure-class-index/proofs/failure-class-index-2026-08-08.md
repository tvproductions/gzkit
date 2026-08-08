# Failure-class index

- GHIs carrying `## Class of failure`: **348**
- Declaring a recurrence of a prior class: **77** (22%)
- Chains: **51** (12 with >= 3 authored diagnoses)
- Deepest chain: **9** authored (spanning 12 GHI numbers)
- Cited-only members across all chains: **26**

## Chains with >= 3 authored diagnoses

### 9 authored of 12 — #358, #371, #377, #502, #516, #537, #538, #543, #551, #552, #553, #554
-   #358 (no class statement indexed)
-   #371 (no class statement indexed)
-   #377 (no class statement indexed)
-   #502 agent-insights.jsonl:75 has invalid type=discovery, fails InsightRecord schema
-   #516 closeout-ceremony: passive-presenter loop lacks REQ-evidence mechanical verification
- * #537 obpi completion: BEHAVIOR-kind cannot-be-uncovered-accepted is not mechanically enforced
-   #538 validate: STRUCTURAL-FENCE REQ kind requires parent-ADR ## Boundary Invariants section but no validator checks parent shape
- * #543 req-kind: SUPPORT proof channel does regex match only; no actual ledger query runs
- * #551 obpi complete: REQ-coverage foundation-trigger undocumented in AGENTS.md
- * #552 TASK governance silently abandoned despite Validated ADR-0.22.0
-   #553 tasks: ADR-0.22.0 envelope intent landed as OBPI-boundary stamps
- * #554 insights: agent-insights.jsonl:114 violates InsightRecord schema (kind/type, evidence shape, extra agent field)

### 5 authored of 7 — #418, #419, #532, #692, #693, #715, #716
-   #418 (no class statement indexed)
-   #419 (no class statement indexed)
- * #532 manpages: 4 brief files reference docs/user/manpages/gz-validate.md (file is validate.md)
-   #692 handoff: validator passes hollow handoffs — checks section presence, not population
- * #693 cli audit: verifies a flag is mentioned, never that its description is true
- * #715 init: pre-commit gate is scaffolded but never installed for adopters
- * #716 scenario-reachability: Era-2 registry dropped between ADR-0.0.33 and ADR-0.0.34

### 5 authored of 7 — #459, #460, #526, #572, #574, #575, #620
-   #459 (no class statement indexed)
-   #460 (no class statement indexed)
- * #526 skill bodies: self-escalation directive drives subagent relay chains
- * #572 gz-session-handoff: handoff schema has validate-time fail-close but no author-time enforcement (vibe-authoring live evidence)
-   #574 gz-session-handoff: resume "advise-not-execute" gate is prose, not mechanized
- * #575 insights: no governed `gz insights` author verb — only a hand-append path
- * #620 claim-grounding: agent prose state-claims have no turn-end gate

### 5 authored of 6 — #607, #669, #691, #727, #728, #740
-   #607 (no class statement indexed)
-   #669 obpi-monitor: no mechanical audit that every OBPI-status writer consults the terminal rule (convention-only)
-   #691 rules: no aging mechanism — skills have last_reviewed, rules have nothing
- * #727 architecture: tech choices and mechanism objectives are unrecorded
-   #728 chores: sync and init export project-local slugs to adopters
- * #740 taxonomy: foundation closure is framework-wide, not project-local as decided

### 5 authored of 5 — #480, #500, #523, #524, #527
-   #480 validate --documents: 3536 errors from schema convention additions not backfilled to pre-convention-era artifacts
- * #500 validate --documents: 3589 schema violations against historical OBPI brief corpus
- * #523 ADR-0.2.0-gate-verification fails gz validate --documents: Validated status enum + missing required sections
- * #524 ADR-0.2.0-gate-verification fails gz validate --documents: Validated status enum + missing required sections
- * #527 ADR-0.0.9-state-doctrine-source-of-truth fails gz validate --documents: Validated status enum + missing required sections

### 4 authored of 6 — #279, #305, #344, #468, #494, #505
-   #279 (no class statement indexed)
-   #305 (no class statement indexed)
-   #344 gz plan create: bare-semver --name still emits unslugged adr_created (GHI #279 class recurrence)
-   #468 gz validate --documents: non-recursive iteration skips nested ADR packages; bare-id frontmatter passes silently
-   #494 scaffolder: bare-id adr_created event re-emerges on ADR-0.0.49 (regression #4 of GHI #279 class)
- * #505 interview adr: flat-dir layout + unvalidated id emits bare adr_created

### 4 authored of 4 — #539, #540, #550, #565
- * #539 closeout-ceremony: brief demo extractor splits multi-line python -c heredocs per-line, ~65% noise in walkthroughs
- * #540 validate: brief ## Examples demos are hand-authored and not executed against the claimed REQ (demos lie)
- * #550 briefs: Verification compound commands fail under shell-less runtime
- * #565 briefs: 40 active-brief Verification compound commands violate shell-less contract

### 4 authored of 4 — #581, #612, #619, #633
-   #581 brief-reconcile: existence-only checks miss dead surfaces & code couplings
- * #612 handoff-model: HandoffFrontmatter rejects fields its own writers emit
- * #619 obpi lock release: completed OBPI has no register path, only handoff/abandon
- * #633 handoff validation: gitignored receipt refs fail validate_handoff_document on clone

### 3 authored of 5 — #323, #380, #495, #499, #530
-   #323 (no class statement indexed)
-   #380 (no class statement indexed)
-   #495 ADR-0.0.37 OBPI briefs in unindividualized scaffold state — 10 briefs need authoring (GHI #485 instance; self-referential CIC-2 failure)
- * #499 OBPI scaffold deferral: ADR-0.0.53/0.0.54/0.0.55 declare 12 briefs in checklists but obpis/ subdirectories empty (GHI #495 class)
- * #530 brief authoring: REQ→test reachability not enforced; briefs can be born unable to satisfy parity gate

### 3 authored of 3 — #533, #752, #753
-   #533 agents-md-budget: 5k recovery target requires ADR-0.0.37 completion + registry-projection migration
-   #752 task-envelope: two of four discovery channels structurally unused (Signature (c) compares 7 of 534)
- * #753 task-envelope: tasks: channel has no schema enforcement; the deferral names an OBPI that never scoped it

### 3 authored of 3 — #729, #730, #733
-   #729 drift: reports SUPPORT/STRUCTURAL-FENCE/doc/terminal REQs as unlinked (1876 of 2020 not drift)
- * #730 tautological-tests: @covers decorator satisfies the production-code exemption (217 of 290 ops masked)
- * #733 taxonomy: terminal-partition reader admits a witnessless grandfather event

### 3 authored of 3 — #758, #760, #761
-   #758 handoff resume: machine floor bookmarks shadow every authored handoff
-   #760 session-exit: skip predicate is defeated by the handoff's own landing commit
- * #761 orientation: SessionStart lists handoff evidence but never assembles the account

`*` = this GHI's own class statement declared the recurrence.
