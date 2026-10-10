# Failure-class index

- GHIs carrying `## Class of failure`: **751**
- Declaring a recurrence of a prior class: **165** (22%)
- Chains: **114** (19 with >= 3 authored diagnoses)
- Deepest chain: **13** authored (spanning 13 GHI numbers)
- Cited-only members across all chains: **29**

## Chains with >= 3 authored diagnoses

### 13 authored of 13 — #677, #758, #760, #761, #781, #783, #784, #791, #792, #795, #796, #797, #803
- * #677 brief reconcile: --apply cannot clear the drift it reports, and exits 0 anyway
-   #758 handoff resume: machine floor bookmarks shadow every authored handoff
-   #760 session-exit: skip predicate is defeated by the handoff's own landing commit
- * #761 orientation: SessionStart lists handoff evidence but never assembles the account
- * #781 chores advise: exits 0 while its own output reports FAIL
-   #783 chores: runtime_state proofs ship in the wheel and --distribution cannot see them
- * #784 OBPI-0.35.0-02: brief omits sensitivity over a ledger_integrity overlap
- * #791 surface-weight: recalibration event has no producer in any gz verb
-   #792 surface-weight: band constants can drift from their witnessing event
- * #795 resume gate: a ruling booked on the wrong handoff lifts the gate anyway
-   #796 verifier-pipe gate: naming pipefail disarms it; using it is not required
- * #797 enforcement floor: negative controls test the rule, never the exemption
- * #803 docs-build: mkdocs validation downgrades withdraw the dead-link enforcement run_mkdocs claims

### 11 authored of 11 — #589, #879, #889, #940, #942, #969, #970, #971, #988, #1008, #1152
-   #589 gz-obpi-pipeline: Stage 3 verification can be masked by a tail-piped exit code
-   #879 obpi precomplete: adversarial_validation reports READY on a REFUTED verdict
- * #889 obpi precomplete: arb_receipts counts receipts, never reads exit_status
-   #940 verifier-pipe-gate: a trailing statement masks a verifier's exit status
- * #942 obpi-pipeline Stage 4a: pasted command output is unverified, and Step 4b does not check it
-   #969 attestation evidence: a harness aggregate status can report success over a red verifier
- * #970 stage4-packet: a || suffix lets the failure branch's output be omitted
- * #971 verifier-pipe-gate: an && chain is masked by whatever catches it
- * #988 gz obpi acceptance: every blocked or rejected path exits 0, not 3
- * #1008 verifier-pipe-gate: a verifier inside a ( ) or { } group is not recognized
- * #1152 arb red --commit: verdict leaves no receipt, so GHI closes cite nothing

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

### 6 authored of 8 — #418, #419, #532, #692, #693, #715, #716, #1084
-   #418 (no class statement indexed)
-   #419 (no class statement indexed)
- * #532 manpages: 4 brief files reference docs/user/manpages/gz-validate.md (file is validate.md)
-   #692 handoff: validator passes hollow handoffs — checks section presence, not population
- * #693 cli audit: verifies a flag is mentioned, never that its description is true
- * #715 init: pre-commit gate is scaffolded but never installed for adopters
- * #716 scenario-reachability: Era-2 registry dropped between ADR-0.0.33 and ADR-0.0.34
- * #1084 git-sync: an anchor the commit only discusses is emitted as touched

### 6 authored of 6 — #785, #787, #854, #856, #1026, #1027
-   #785 gates: no mechanism asks which gates have no automatic caller
- * #787 gz check: _build_check_steps' coupling checklist names 4 obligations, 8 are required
-   #854 cli doctrine: new-verb obligations described in 3 places, no two agree (4 of 7)
- * #856 arb: canonical unittest invocation is serial while every gate runs it parallel (3.05x)
- * #1026 arb validate: 38 of gzkit's own receipts fail — writers outran the schemas
- * #1027 arb: coverage is the last serial full-suite run — 493 s vs 307 s parallel, same totals

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

### 5 authored of 5 — #383, #788, #1068, #1069, #1071
-   #383 fix(quality): _expand_allowed_paths emitted backslash paths on Windows; sweep other str(relative_to) sites
- * #788 typecheck: --exclude features/** never matches on Windows, so 25 diagnostics reach the gate
-   #1068 test_report_publication: write_text fixture writes CRLF on Windows
-   #1069 line-endings audit: scope excludes the write_text hazard it names
- * #1071 settings.local backup vault resolves INSIDE the repo on Windows

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

### 4 authored of 4 — #654, #863, #976, #978
-   #654 content: gz content remember footgun + no orchestrated canon landing
- * #863 gz content retire: says no recomposition is implied, then blocks the push
- * #976 ownership prose: growth refusal and unown help each prescribe a path that refuses
- * #978 ownership prose: 13 sibling witness-chain refusals prescribe a refused step

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

### 3 authored of 3 — #585, #594, #838
-   #585 gz handoff: governed archive/retention verb for accumulated handoffs
- * #594 arb: no archive/purge half — 1875 receipts accumulate unbounded
- * #838 handoff: Settled Rulings is 85% of the document and re-adjudication still happens

### 3 authored of 3 — #729, #730, #733
-   #729 drift: reports SUPPORT/STRUCTURAL-FENCE/doc/terminal REQs as unlinked (1876 of 2020 not drift)
- * #730 tautological-tests: @covers decorator satisfies the production-code exemption (217 of 290 ops masked)
- * #733 taxonomy: terminal-partition reader admits a witnessless grandfather event

### 3 authored of 3 — #770, #845, #886
-   #770 dispatch-attestation: the audit checks an absorption marker, not dispatch
-   #845 gz-obpi-pipeline: Stage-2 dispatch has a read path, no writer, no fail-close
- * #886 pipeline: Stage-2 dispatch state lives only in the Layer-3 marker, so clear-stale destroys it

### 3 authored of 3 — #1093, #1156, #1157
-   #1093 present-evidence: brief Demo runs in the live checkout and can attest
- * #1156 fidelity gate: closeout demo assertions run in the live checkout
- * #1157 obpi verify-packet: replay runs in and can mutate the live checkout

`*` = this GHI's own class statement declared the recurrence.
