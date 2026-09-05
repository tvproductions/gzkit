---
anchor_id: OBPI-0.35.0-04
anchor_kind: obpi
generated_at: 2026-09-05T12:16:13.565159+00:00
scaffold_version: 1.0
---

# Walkthrough: OBPI-0.35.0-04

## 1. What I see (the problem)

**Prompt:** *What did I observe that motivates this change? What hurts if nothing happens?*

**Evidence:**

- OBPI-0.35.0-04-section-ownership-and-ratchet
- OBPI-0.35.0-05
- OBPI-0.35.0-06-validate-rendition-lineage
- OBPI-0.35.0-06
- OBPI-0.35.0-01
- OBPI-0.35.0-02
- ADR-0.35.0
- ADR-0.0.36
- ADR-0.0.59

The operator explicitly asked Codex to assess this OBPI, chart a path, and assist execution after repeated local correction cycles. A stable snapshot was captured at commit `397301c629bf3007943c43295f0adaafbd8c7fa8` plus dirty patch SHA `f040de323773f553abfcca642bd81669ca5fef522abcc2e53a9d8d659b6966b2`; `snapshot.json` records every principal file SHA and confirms stability during capture. The implementation already passes 170 scoped ownership/unown/declaration-validation tests. The remaining problem is lifecycle closure: journal absence must be durable before required recovery bytes are deleted or reused, cleanup inspection failure must not masquerade as an empty directory, and user instructions must describe only established state. These are the existing plan's constraints 5–9, not a new feature. See `contract-assessment.md`, `test-evidence.md`, and the snapshot plan lines 180–257.

## 2. Per-instance severity

**Prompt:** *How bad is each occurrence? One incident, a pattern, or a class of failure?*

**Evidence:**

- _(no citations for this section)_

The cleanup ordering gap can destroy material required by a journal that returns after a crash under the declared failure model; it is a potential integrity/recoverability failure established by code reasoning, not an observed power-loss experiment. The staging-enumeration probe actually observed exit 0 with a real producer-created recovery temporary file still present, so that is a demonstrated false-cleanup-success case. The parent-directory test survives a wrong-directory mutation, an observed proof defect with a correct production writer. Source decoding and contradictory recovery prose are delivery gaps until an actual unrecoverable state is shown; retaining a documented snapshot prevents a claim of proved data loss. See `test-evidence.md` and its preserved probe scripts.

## 3. Why this scope

**Prompt:** *Why is the change boundary drawn here and not wider or narrower?*

**Evidence:**

- _(no citations for this section)_

Keep the existing OBPI04 scope and ledger exceptions. The governing brief already allows `src/gzkit/commands/content/unown.py`, `src/gzkit/content/ownership.py`, their tests, `.gitignore`, and `docs/user/manpages/content.md`; its plan explicitly owns cleanup barriers and orphan classification. No ledger redesign, no new dependency, no source auto-rewrite, and no scope split is required. The assessment runs against an isolated snapshot because Claude has active dispatches in the live checkout. Execution assistance consists of a complete contract, runnable missing acceptance cases, and a correction route that the active writer can integrate without parallel writes to the same production files. Source: snapshot brief Allowed Paths and plan 227–257.

## 4. What it proposes

**Prompt:** *In one paragraph, what is the change?*

**Evidence:**

- _(no citations for this section)_

Use the existing journal protocol with one dependency order: retain measured bytes before publishing the journal; publish and durably establish the declaration before witnessing it; validate source reconciliation at the defined final observation; establish durable journal absence before deleting or reusing dependents; finish or truthfully report cleanup. Apply the absence boundary both after unlink and on journal-absent entry. Distinguish the current transaction's required cleanup from unrelated orphan warnings through finalization. Report failed residue enumeration as failed observation, not an empty result. Keep the current fixed identity and idempotent witness logic. Correct recovery instructions to end at restored measured source plus canonical-loader acceptance, with newer ratchet-invalid edits safely preserved outside the governed surface. See current contract and plan 156–257.

Execution update after Claude was directed to pause: the immediate reviewable patch in `correction/` is limited to restoring the existing plan234–236 preserve-and-refuse disposition for unsupported required directory-barrier operations. `PLATFORM-FINDING.md` and `unsupported-barrier-observations.json` demonstrate that the newly added warning exception leaves fresh work unusable and permits cleanup to discard its snapshot with exit 0. The correction adds no new platform guarantee, exit code, recovery state, or exception. Existing transient-fault behavior and exact-witness replay remain binding. Semantic tests cover repeated refusal followed by healed progress; coupled diagnostic/manpage text must match that behavior.

## 5. Routing decision

**Prompt:** *Direct fix, OBPI ceremony, or new ADR? Cite the threshold that routed it.*

**Evidence:**

- _(no citations for this section)_

This is operator-requested assessment and execution assistance for the already-live OBPI04 pipeline, not a new work order. The user explicitly named the work and asked us to assess, chart a path, and assist execution. Existing canonical pipeline ownership, scope, reviews, and human attestation remain with the active execution stream. This isolated diagnostic package does not launch a second pipeline, claim completion, change a verdict, or supply human attestation. Any production correction must be integrated by the active owner through the existing implementer and two-stage review path, then required verification and Step 4b. Source: AGENTS.md operator-initiation and pipeline rules; `.gzkit/skills/gz-obpi-pipeline/SKILL.md` Stage 2 and Step 4b.

## 6. Why this design is right-sized

**Prompt:** *Why isn't this bigger or smaller? What does this shape defend against?*

**Evidence:**

- _(no citations for this section)_

The contract is bounded by concrete resources, logical write/read/deletion boundaries, and disclosed ledger assumptions. Its three independent obligations are witnessed transition, source reconciliation, and cleanup. A final source observation establishes what was observed then; no CLI holding only its own advisory lock can forbid a later external editor save, and this assessment does not add that guarantee. A retry must converge once ordinary faults are repaired and the operator restores a valid measured source. A transaction manager rewrite or generic filesystem recovery framework would introduce additional work with no demonstrated necessity. The complete read/write obligation map and finite existing-plus-missing test matrix define the correction boundary.

The current patch is a proposed correction for the existing paused OBPI, prepared through an implementer and bounded independent review in an isolated copy. It is not a resumed live pipeline or completed OBPI. No source, index, ledger, marker or lock in Claude's checkout is changed by it. Integration and the remaining OBPI stages are separate from proving this one correction.

## 7. What convinces me (evidence)

**Prompt:** *Which rules, ledger events, and commits ground this decision?*

**Evidence:**

- adr-audit (.gzkit/rules/adr-audit.md)
- brief-heading-conventions (.gzkit/rules/brief-heading-conventions.md)
- cli (.gzkit/rules/cli.md)
- cross-platform (.gzkit/rules/cross-platform.md)
- gate5-runbook-code-covenant (.gzkit/rules/gate5-runbook-code-covenant.md)
- gh-cli (.gzkit/rules/gh-cli.md)
- governance-core (.gzkit/rules/governance-core.md)
- guardrail-feedback-prose (.gzkit/rules/guardrail-feedback-prose.md)
- hexagonal-architecture (.gzkit/rules/hexagonal-architecture.md)
- models (.gzkit/rules/models.md)
- pythonic (.gzkit/rules/pythonic.md)
- security-sensitivity (.gzkit/rules/security-sensitivity.md)
- task-discovery (.gzkit/rules/task-discovery.md)
- tests (.gzkit/rules/tests.md)
- tool-skill-runbook-alignment (.gzkit/rules/tool-skill-runbook-alignment.md)
- 397301c chore(handoff): author the OBPI-0.35.0-04 handoff prioritizing Step 4b round 9
- 204e8c2 chore(locks): reclaim the OBPI-0.35.0-04 lock, clearing the orphaned-implementation finding
- 1c21a89 chore(locks): book the OBPI-0.35.0-04 TTL reap and its register entry
- e43c55c fix(codex-config): record the cap Codex actually applies, not the one gzkit wished for (GHI #962)
- bf9bf0c chore(governance): book two session-exit bookmarks and the resumed-handoff ruling
- edbab5a fix(obpi-complete): a refutation loops, it never completes (GHI #960)
- 44c01b4 chore(pipeline): clear stale OBPI-0.35.0-04 pipeline markers (>24h TTL)
- 7e64804 chore(governance): record the resumed-handoff ruling on OBPI-0.35.0-04
- cc942ee fix(ownership-fixtures): mint the genesis witness, write the surface as bytes (GHI #957, #958)
- 68074e6 chore: update .gzkit (gz git-sync)
- c834fcf chore: update .gzkit (2 files) (gz git-sync)
- 5fbc5b3 fix(content): give the advisory-lock primitive a neutral public home (GHI #945)
- bc2a55e chore(handoff): record OBPI-0.35.0-04 with the Step-4b stance corrected and rounds 7-8 unrecorded
- 6da6cf1 docs(obpi-pipeline): Step 4b confirms correctness, it does not refute it
- 84d6eb8 chore(handoff): correct a claim the skill promotion made false
- db201f2 docs(obpi-pipeline): promote the three Step-4b convergence rules into the skill
- c332e56 chore(handoff): record OBPI-0.35.0-04 with its threat model declared and a bounded round owed
- a592be2 docs(obpi-0.35.0-04): declare the threat model Step 4b was missing
- 5108d7c chore(handoff): record the OBPI-0.35.0-04 state awaiting a clean Step 4b
- 0488f8f fix(ownership): anchor the ratchet to ledger state, and harden journal replay
- e962b01 chore(insights): record the GHI-queue course correction
- 8f60248 chore: update .gzkit (2 files) (gz git-sync)
- 58e4e46 perf(check): scope the pre-push gate, and raise the marker TTL to 24h
- 714c283 chore: update .gzkit (gz git-sync)
- 72bbb9a chore: update .gzkit (gz git-sync)
- 6d40228 fix(content): close Step-4b findings 2, 3 and 5 on the section-ownership plane
- 600f7fd chore: update .claude (4 files), .gzkit (9 files), docs/design/adr (gz git-sync)
- 8fab92d chore: update .claude (2 files), .gzkit (6 files), docs/design/adr (2 files) (gz git-sync)
- 4ea6cdb chore: update .gzkit (3 files) (gz git-sync)
- 6bfa8d5 chore: update .gzkit (3 files) (gz git-sync)
- 95cc95f chore: update .claude, .gzkit (6 files), docs/governance/uncovered-req-inventory-2026-08-22.md (gz git-sync)
- 4a919af feat(content): render two operator rulings into AGENTS.md; fence Stage-2 in the generator
- 7009d02 chore: update .gzkit (gz git-sync)
- c3b6449 chore: update .claude (2 files), .gzkit (3 files), docs/design/adr (2 files), commands (3 files) +4 more (gz git-sync)
- c924619 chore: update .agents (2 files), .claude (2 files), .github (2 files), .gzkit (3 files) +3 more (gz git-sync)
- 85c5d92 chore: update .gzkit (2 files), docs/design/adr (13 files), docs/governance/GovZero (gz git-sync)

Observed baseline receipt: `repo/artifacts/receipts/arb-step-obpibaseline-0608f3b81cd945d9a4fc6e0976f1958d.json`: 170 tests, exit 0. Runtime import checks confirmed both production modules and test fixtures came from the isolated snapshot, not the live editable install. `probe_residue_enumeration.py` observed an actual retained staging file after a falsely successful retry. `probe_wrong_directory_test.py` observed the existing test passing after redirecting the directory open. The full contract review read the 1,396-line brief and 312-line plan; the protocol review read the complete 2,294-line command and 1,323-line ownership module. These are bounded diagnostic results, not final Gate 2/4b attestation. The final source and its proof must be measured again after correction.

## 8. Residual uncertainty

**Prompt:** *What am I not sure about? What would change my mind?*

**Evidence:**

- _(no citations for this section)_

The active checkout continues changing, so snapshot findings must be rechecked before applying any correction. The plan declares the conditional orphan-warning policy as an operator ruling; this chat directly observed the recommendation, not a separate user attestation of that clause. That provenance limitation is disclosed rather than used to invent another approval blocker. The accepted #952/#953 ledger limitations remain outside the ownership guarantee. POSIX fsync ordering tests and deterministic fault injection do not demonstrate physical power-loss behavior on every filesystem or Windows. No test or static review proves absence of all defects; the existing gate remains positive demonstrations plus no in-scope critical/high finding. This package supplies bounded engineering evidence and a route, not OBPI completion.

The subsequent platform assessment found a concrete unresolved obligation: the Windows no-op does not prove the mandatory durability boundary, and co-equal platform support has no recorded waiver here. The present patch does not resolve that architecture/evidence gap. Confidence is high in restoring the explicitly ruled refusal for observed POSIX barrier failures; that confidence must not be reported as confidence that the complete cross-platform OBPI is ready to close.


### Authoring-time complexity hints

- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/content/ownership.py:442-442** — long_parameter_list (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/content/ownership.py:586-586** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/content/ownership.py:860-860** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/content/ownership.py:1296-1296** — long_parameter_list (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/commands/content/unown.py:58-58** — long_parameter_list (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/commands/content/unown.py:146-146** — long_parameter_list (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/commands/content/unown.py:354-354** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/commands/content/unown.py:443-443** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/commands/content/unown.py:486-486** — long_parameter_list (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/commands/content/unown.py:839-917** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/commands/content/unown.py:920-1009** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/commands/content/unown.py:1220-1220** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/commands/content/unown.py:1430-1551** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/commands/content/unown.py:2065-2117** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/tests/content/test_tui_affordances.py:75-75** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/tests/content/test_tui_affordances.py:125-125** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/tests/content/test_tui_affordances.py:254-254** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
