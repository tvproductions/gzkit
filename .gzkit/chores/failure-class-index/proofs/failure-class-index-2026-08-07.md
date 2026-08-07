# Failure-class index

- GHIs carrying `## Class of failure`: **288**
- Declaring a recurrence of a prior class: **71** (25%)
- Chains: **46** (15 of depth >= 3)
- Deepest chain: **12**

## Chains of depth >= 3

### depth 12 — #358, #371, #377, #502, #516, #537, #538, #543, #551, #552, #553, #554
-   #358 (outside the indexed window)
-   #371 (outside the indexed window)
-   #377 (outside the indexed window)
-   #502 agent-insights.jsonl:75 has invalid type=discovery, fails InsightRecord schema
-   #516 closeout-ceremony: passive-presenter loop lacks REQ-evidence mechanical verification
- * #537 obpi completion: BEHAVIOR-kind cannot-be-uncovered-accepted is not mechanically enforced
-   #538 validate: STRUCTURAL-FENCE REQ kind requires parent-ADR ## Boundary Invariants section but no validator checks parent shape
- * #543 req-kind: SUPPORT proof channel does regex match only; no actual ledger query runs
- * #551 obpi complete: REQ-coverage foundation-trigger undocumented in AGENTS.md
- * #552 TASK governance silently abandoned despite Validated ADR-0.22.0
-   #553 tasks: ADR-0.22.0 envelope intent landed as OBPI-boundary stamps
- * #554 insights: agent-insights.jsonl:114 violates InsightRecord schema (kind/type, evidence shape, extra agent field)

### depth 7 — #418, #419, #532, #692, #693, #715, #716
-   #418 (outside the indexed window)
-   #419 (outside the indexed window)
- * #532 manpages: 4 brief files reference docs/user/manpages/gz-validate.md (file is validate.md)
-   #692 handoff: validator passes hollow handoffs — checks section presence, not population
- * #693 cli audit: verifies a flag is mentioned, never that its description is true
- * #715 init: pre-commit gate is scaffolded but never installed for adopters
- * #716 scenario-reachability: Era-2 registry dropped between ADR-0.0.33 and ADR-0.0.34

### depth 7 — #459, #460, #526, #572, #574, #575, #620
-   #459 (outside the indexed window)
-   #460 (outside the indexed window)
- * #526 skill bodies: self-escalation directive drives subagent relay chains
- * #572 gz-session-handoff: handoff schema has validate-time fail-close but no author-time enforcement (vibe-authoring live evidence)
-   #574 gz-session-handoff: resume "advise-not-execute" gate is prose, not mechanized
- * #575 insights: no governed `gz insights` author verb — only a hand-append path
- * #620 claim-grounding: agent prose state-claims have no turn-end gate

### depth 6 — #279, #305, #344, #468, #494, #505
-   #279 (outside the indexed window)
-   #305 (outside the indexed window)
-   #344 (outside the indexed window)
-   #468 gz validate --documents: non-recursive iteration skips nested ADR packages; bare-id frontmatter passes silently
-   #494 scaffolder: bare-id adr_created event re-emerges on ADR-0.0.49 (regression #4 of GHI #279 class)
- * #505 interview adr: flat-dir layout + unvalidated id emits bare adr_created

### depth 6 — #607, #669, #691, #727, #728, #740
-   #607 (outside the indexed window)
-   #669 (outside the indexed window)
-   #691 rules: no aging mechanism — skills have last_reviewed, rules have nothing
- * #727 architecture: tech choices and mechanism objectives are unrecorded
-   #728 chores: sync and init export project-local slugs to adopters
- * #740 taxonomy: foundation closure is framework-wide, not project-local as decided

### depth 5 — #323, #380, #495, #499, #530
-   #323 (outside the indexed window)
-   #380 (outside the indexed window)
-   #495 ADR-0.0.37 OBPI briefs in unindividualized scaffold state — 10 briefs need authoring (GHI #485 instance; self-referential CIC-2 failure)
- * #499 OBPI scaffold deferral: ADR-0.0.53/0.0.54/0.0.55 declare 12 briefs in checklists but obpis/ subdirectories empty (GHI #495 class)
- * #530 brief authoring: REQ→test reachability not enforced; briefs can be born unable to satisfy parity gate

### depth 5 — #480, #500, #523, #524, #527
-   #480 validate --documents: 3536 errors from schema convention additions not backfilled to pre-convention-era artifacts
- * #500 validate --documents: 3589 schema violations against historical OBPI brief corpus
- * #523 ADR-0.2.0-gate-verification fails gz validate --documents: Validated status enum + missing required sections
- * #524 ADR-0.2.0-gate-verification fails gz validate --documents: Validated status enum + missing required sections
- * #527 ADR-0.0.9-state-doctrine-source-of-truth fails gz validate --documents: Validated status enum + missing required sections

### depth 4 — #539, #540, #550, #565
- * #539 closeout-ceremony: brief demo extractor splits multi-line python -c heredocs per-line, ~65% noise in walkthroughs
- * #540 validate: brief ## Examples demos are hand-authored and not executed against the claimed REQ (demos lie)
- * #550 briefs: Verification compound commands fail under shell-less runtime
- * #565 briefs: 40 active-brief Verification compound commands violate shell-less contract

### depth 4 — #581, #612, #619, #633
-   #581 (outside the indexed window)
- * #612 handoff-model: HandoffFrontmatter rejects fields its own writers emit
- * #619 obpi lock release: completed OBPI has no register path, only handoff/abandon
- * #633 handoff validation: gitignored receipt refs fail validate_handoff_document on clone

### depth 3 — #304, #306, #605
-   #304 (outside the indexed window)
-   #306 (outside the indexed window)
- * #605 chores: CHORE.md proof-paths + manifest still cite legacy ops/chores/

### depth 3 — #394, #473, #631
-   #394 (outside the indexed window)
- * #473 validate: pointer_anchors + scenario_reachability exit-3 routing drift
- * #631 eval scorer: _score_architectural_alignment lexicon manufactures false-RED 1.0 scores

### depth 3 — #517, #528, #529
-   #517 (outside the indexed window)
- * #528 gz-session-handoff: skill and orientation hook disagree on location
- * #529 handoff system: not wired into OBPI pipeline; no gz handoff CLI verb

### depth 3 — #533, #752, #753
-   #533 (outside the indexed window)
-   #752 task-envelope: two of four discovery channels structurally unused (Signature (c) compares 7 of 534)
- * #753 task-envelope: tasks: channel has no schema enforcement; the deferral names an OBPI that never scoped it

### depth 3 — #729, #730, #733
-   #729 drift: reports SUPPORT/STRUCTURAL-FENCE/doc/terminal REQs as unlinked (1876 of 2020 not drift)
- * #730 tautological-tests: @covers decorator satisfies the production-code exemption (217 of 290 ops masked)
- * #733 taxonomy: terminal-partition reader admits a witnessless grandfather event

### depth 3 — #758, #760, #761
-   #758 handoff resume: machine floor bookmarks shadow every authored handoff
-   #760 session-exit: skip predicate is defeated by the handoff's own landing commit
- * #761 orientation: SessionStart lists handoff evidence but never assembles the account

`*` = this GHI's own class statement declared the recurrence.
