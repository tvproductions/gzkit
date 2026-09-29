---
anchor_id: OBPI-0.35.0-08
anchor_kind: obpi
generated_at: 2026-09-29T08:27:57.783543+00:00
scaffold_version: 1.0
---

# Walkthrough: OBPI-0.35.0-08

## 1. What I see (the problem)

**Prompt:** *What did I observe that motivates this change? What hurts if nothing happens?*

**Evidence:**

- OBPI-0.35.0-08-remember-post-append-advisory
- OBPI-0.35.0-03
- OBPI-0.35.0-01
- OBPI-0.35.0-07
- OBPI-0.35.0-09
- OBPI-0.35.0-02
- OBPI-0.35.0-06
- ADR-0.35.0
- ADR-0.0.41
- ADR-0.0.37
- ADR-0.0.36
- ADR-0.0.59

The launch gate `gz validate --evaluation-justify-binding` refuses ADR-0.35.0 (exit 3, measured 2026-09-29) because the 2026-09-06 machine evaluation scored dimension 3 "Feature Checklist" at 1 (`EVALUATION_SCORECARD.md:21`: *"Checklist items not prefixed with OBPI-; Checklist items have inconsistent granularity"*), and no walkthrough postdates it. Since GHI #1014 the pipeline walks the ADR Draft→Proposed→Accepted at launch, so OBPI-0.35.0-08 — the lowest in-flight OBPI (brief `status: Active`) — cannot be resumed until this reasoning exists. If nothing happens, the TOPMOST ADR of the active campaign cannot draw its next OBPI.

## 2. Per-instance severity

**Prompt:** *How bad is each occurrence? One incident, a pattern, or a class of failure?*

**Evidence:**

- _(no citations for this section)_

A single gate instance on one ADR, not a class of defect in the OBPI. The finding is a formatting lint: the human substance review scored the same dimension **3** — *"All thirteen items earn their place and map 1:1; prefix/granularity lint understates substantive coverage"* (`EVALUATION_SUBSTANCE.md:55`) — with a GO at 3.25. The granularity point is real and already named there: items 07 and 12 are *"broad transactions, which count heuristics miss"* (`EVALUATION_SUBSTANCE.md:56`). OBPI-08 itself is not one of them.

## 3. Why this scope

**Prompt:** *Why is the change boundary drawn here and not wider or narrower?*

**Evidence:**

- _(no citations for this section)_

The walkthrough anchors on OBPI-0.35.0-08 because it is the next OBPI the pipeline would resume in ascending order (the ADR's in-flight OBPI; its two stale `task_blocked` rows for TASK-0.35.0-08-05-01/06-01 were discharged 2026-09-29 under GHI #611 (b)(c), and both TASKs now read `in_progress`). Its boundary is the brief's allowlist — `remember.py`, `_drift.py`, `retire.py`, `vendors.py`, `rendition_store.py`, `tier_policy.py`, their tests, `features/**`, the `content` manpage. It is not widened to re-litigate the checklist's granularity; the substance review already ruled that GO.

## 4. What it proposes

**Prompt:** *In one paragraph, what is the change?*

**Evidence:**

- _(no citations for this section)_

Resume OBPI-0.35.0-08: `gz content remember` emits a post-append advisory naming the committed renditions the append drifted (routed consumers only, via the shared `is_graded_rendition` predicate), citing the corpus→rendition seam and a runnable `gz content land` — while the append itself stays unconditional and exit 0. Remaining open work per the brief: REQ-0.35.0-08-06 has no covering test for *byte-identical corpus rows and identical exit code with and without drift*, and REQ-0.35.0-08-08's predicate-sharing is to be proven against the gates' enumeration.

## 5. Routing decision

**Prompt:** *Direct fix, OBPI ceremony, or new ADR? Cite the threshold that routed it.*

**Evidence:**

- _(no citations for this section)_

OBPI ceremony, already routed: the brief exists under ADR-0.35.0 checklist item 8 and changes a CLI's observable output on a heavy-lane runtime contract (`AGENTS.md` § Defect-fix routing: *"Work that crosses briefs, changes a CLI, schema or runtime contract … is OBPI work, which the operator initiates"*). No new ADR, no direct fix. Only the operator initiates it through `gz-obpi-pipeline`; this walkthrough does not initiate it.

## 6. Why this design is right-sized

**Prompt:** *Why isn't this bigger or smaller? What does this shape defend against?*

**Evidence:**

- _(no citations for this section)_

Smaller would drop the fail-open ordering (append before advise, REQ-02) or the specificity (REQ-03/08), which is the whole value — a generic "renditions are stale" string sends the operator to recompose consumers no gate grades. Larger would give `remember` a precondition, which REQ-0.35.0-08-07 fences off for the whole ADR: capture is unblockable (`gz-content-remember` skill: *"losing the operator's words is strictly worse than a red tree"*). The shape defends exactly that asymmetry: advise loudly, refuse never.

## 7. What convinces me (evidence)

**Prompt:** *Which rules, ledger events, and commits ground this decision?*

**Evidence:**

- adr-audit (.gzkit/rules/adr-audit.md)
- brief-heading-conventions (.gzkit/rules/brief-heading-conventions.md)
- cli (.gzkit/rules/cli.md)
- cross-platform (.gzkit/rules/cross-platform.md)
- gate5-runbook-code-covenant (.gzkit/rules/gate5-runbook-code-covenant.md)
- gh-cli (.gzkit/rules/gh-cli.md)
- hexagonal-architecture (.gzkit/rules/hexagonal-architecture.md)
- models (.gzkit/rules/models.md)
- pythonic (.gzkit/rules/pythonic.md)
- security-sensitivity (.gzkit/rules/security-sensitivity.md)
- task-discovery (.gzkit/rules/task-discovery.md)
- tests (.gzkit/rules/tests.md)
- tool-skill-runbook-alignment (.gzkit/rules/tool-skill-runbook-alignment.md)
- eddae75 chore: update .gzkit (2 files) (gz git-sync)
- 78373d2 chore: update .gzkit (gz git-sync)
- 59ed354 fix(ledger): attestor witness asserts the retire gate's named predicate (GHI #894)
- 2e24cbc chore: update .gzkit (3 files) (gz git-sync)
- f58f27f fix(git-sync): resolve commit anchors against the graph, and stop matching short (GHI #1081)
- e8e7956 chore: update .gzkit (5 files), docs/governance/ieee (5 files) (gz git-sync)
- feac933 chore: update .gzkit, docs/governance/ieee (4 files) (gz git-sync)
- 77b9b78 chore: update .gzkit (3 files), docs/design/requirements (2 files) (gz git-sync)
- 6a0e524 chore: update .gzkit (3 files), docs/design/requirements (gz git-sync)
- b100117 fix(handoff): resolve citations as the prose writes them, not as graph keys (GHI #1079)
- cc5fc40 chore: update .gzkit (gz git-sync)
- e12acc2 chore: update .gzkit (2 files) (gz git-sync)
- f55624e fix(handoff): resolve OBPI citations from the ledger, not a derived view (GHI #1076)
- a624481 chore: update .gzkit (2 files) (gz git-sync)
- 64e7120 chore: update .gzkit (2 files) (gz git-sync)
- 1c59a53 chore: update .gzkit (4 files) (gz git-sync)
- 8e66aae chore: update .gzkit (gz git-sync)
- c6b7359 chore: update .gzkit (2 files) (gz git-sync)
- c358297 chore: update .agents (5 files), .claude (5 files), .codex (6 files), .gzkit (39 files) +9 more (gz git-sync)
- 4074451 chore: update .gzkit (3 files) (gz git-sync)
- 663bb88 chore: update .gzkit (2 files) (gz git-sync)
- b6fab60 docs(obpi): seat the render-order attestation ruling in OBPI-0.35.0-13 (GHI #815)
- 31cbf96 chore: update .gzkit (2 files) (gz git-sync)
- 3412273 docs(adr): absorb render-order scope into ADR-0.35.0 as item 13 (GHI #815)
- 8037fb6 chore: update .gzkit (2 files) (gz git-sync)
- 6210ae7 chore: update .gzkit (3 files) (gz git-sync)
- 2c81cb7 chore: update .gzkit (2 files) (gz git-sync)
- 5412b7c chore: update .gzkit (2 files) (gz git-sync)
- cf7938d chore: update .gzkit (2 files) (gz git-sync)
- d2029dd chore: update .gzkit (gz git-sync)
- 18ce89c chore: update .claude (2 files), .gzkit (6 files), docs/design/adr (gz git-sync)
- 16484fd chore: update .gzkit (11 files) (gz git-sync)
- 3ff7bc1 chore: update .gzkit (3 files) (gz git-sync)
- 479bc09 chore: update .claude, .gzkit (2 files), docs/design/adr (3 files), docs/user/manpages (gz git-sync)
- 0ac92c5 chore: update .claude (4 files), .gzkit (5 files), docs/design/adr, docs/user/manpages (gz git-sync)
- b976178 chore: update .gzkit, docs/design/adr (gz git-sync)
- 4ea6cdb chore: update .gzkit (3 files) (gz git-sync)
- 6bfa8d5 chore: update .gzkit (3 files) (gz git-sync)
- f55edfb chore: update .gzkit (gz git-sync)
- 2f2482b chore: update .gzkit (3 files) (gz git-sync)
- 5dcb96f chore: update .gzkit (3 files) (gz git-sync)
- 38bb66e chore: update .gzkit (4 files) (gz git-sync)
- eea2f5d docs(handoff): session close — the iron law, two canon adds, GHI #867/#868/#869
- aabc5cd chore: update .gzkit (gz git-sync)
- aea8e82 chore: update .gzkit (4 files) (gz git-sync)
- fe19fdc test(content): bind @covers for REQ-0.35.0-08-01/-02/-05, retire one false binding
- 4203b04 docs(handoff): session close — brief-ownership precondition and the route filter
- 57d28f2 chore: update .gzkit (gz git-sync)
- 809f137 fix(content): enumerate drifted renditions by route, not by directory glob (REQ-0.35.0-08-03, -08-08)
- e51427f docs(obpi): amend OBPI-0.35.0-08 for the post-collapse route set (GHI #864 follow-on)
- 95cc95f chore: update .claude, .gzkit (6 files), docs/governance/uncovered-req-inventory-2026-08-22.md (gz git-sync)
- 22d737f fix(content): gate the corpus delta, not the re-render; expose witness (GHI #821)
- 32d5a42 chore: update .gzkit, docs/governance/advisory-rules-audit.md, docs/governance/build-to-1.0-campaign-2026-07-18.md (gz git-sync)
- 5d50e9a chore: update .gzkit, docs/design/adr (4 files) (gz git-sync)
- 241a100 chore: update .gzkit, docs/design/adr (3 files) (gz git-sync)
- 296aacc chore: update .gzkit, docs/design/adr, docs/governance/build-to-1.0-campaign-2026-07-18.md (gz git-sync)
- 4b1ae4f chore: update .gzkit, docs/design/adr (7 files), docs/governance/GovZero, docs/governance/build-to-1.0-campaign-2026-07-18.md (gz git-sync)
- f9565c7 chore: update .gzkit (2 files), docs/governance/build-to-1.0-campaign-2026-07-18.md (gz git-sync)
- c3b6449 chore: update .claude (2 files), .gzkit (3 files), docs/design/adr (2 files), commands (3 files) +4 more (gz git-sync)

- Evaluation: `EVALUATION_SCORECARD.md:21` (machine 1) vs `EVALUATION_SUBSTANCE.md:55` (substance 3, GO 3.25).
- Gate: `gz validate --evaluation-justify-binding` exit 3, 2026-09-29, citing ADR-0.0.26 Decision 2.
- Brief: `OBPI-0.35.0-08-remember-post-append-advisory.md` Acceptance Criteria (REQ-01..08) and its 2026-08-23/24 operator-ruled amendments.
- Ledger: the two `ledger_event_corrected` rows (discharged, condition-resolved) for TASK-0.35.0-08-05-01 and -06-01, 2026-09-29.
- Commits from the gathered list touching this OBPI: `809f137` (route-based drift enumeration, REQ-03/-08), `fe19fdc` (@covers for REQ-01/-02/-05), `e51427f` (post-collapse brief amendment), `22d737f` (gate the corpus delta, GHI #821).
- Rules: `tests.md` (REQ-derived assertions, exit-code integrity), `cli.md` (CLI output contract), `gate5-runbook-code-covenant.md` (heavy-lane evidence).

## 8. Residual uncertainty

**Prompt:** *What am I not sure about? What would change my mind?*

**Evidence:**

- _(no citations for this section)_

(a) The brief records that *stderr-only* routing is proven nowhere after the 2026-08-24 reword; if the operator wants that property back, the test runner must split streams, which is outside this allowlist. (b) The held GHI #611 item (a) — voiding OBPI-08's 2026-08-23 `pipeline_launched` row — stays held as #930's live reproduction; a resume may interact with that latch. (c) The complexity hints flag `_drift.py:28-127` and `vendors.py` as approaching the CC ceiling; if REQ-08's predicate change adds branches there, extraction may be needed. (d) Brief frontmatter says `status: Active` while its REQ amendments say *"Brief is Draft"* — a stale phrase, not a state claim; the ledger is authoritative. What would change my mind: a finding that items 07/12's breadth blocks OBPI-08's dependency order — the substance review found the prerequisites acyclic.


### Authoring-time complexity hints

- **/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/_drift.py:28-65** — unclassified (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/_drift.py:68-127** — unclassified (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/content/vendors.py:57-84** — unclassified (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/content/vendors.py:87-95** — unclassified (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/content/vendors.py:140-152** — unclassified (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/content/vendors.py:176-197** — unclassified (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/content/rendition_store.py:105-148** — unclassified (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/retire.py:61-73** — unclassified (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/retire.py:76-93** — unclassified (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/core/attestor_names.py:92-122** — unclassified (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:110-118** — unclassified (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:208-265** — unclassified (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:647-688** — unclassified (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:711-741** — unclassified (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:907-954** — unclassified (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1224-1258** — unclassified (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1597-1644** — unclassified (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1647-1680** — unclassified (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1683-1721** — unclassified (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_remember.py:47-56** — unclassified (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
