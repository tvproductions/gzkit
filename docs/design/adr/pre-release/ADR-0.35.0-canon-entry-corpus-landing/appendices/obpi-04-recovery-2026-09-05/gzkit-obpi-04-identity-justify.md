---
anchor_id: OBPI-0.35.0-04
anchor_kind: obpi
generated_at: 2026-09-05T07:29:11.109009+00:00
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

This is an operator-requested design escalation for the existing ownership OBPI, based on the current working tree, not implementation authorization. The proposed split is rejected; the existing scope and ledger exception remain binding. The requested deliverable is the invariant, read/write inventory, and concrete correction.

The fresh path selects a canonical surface and derives the surface, declaration, and journal paths before taking the declaration lock (`src/gzkit/commands/content/unown.py:1069`). It then loads a declaration again and now uses that object's `surface` for the record (`:1131`, `:1173`) and the serialized successor (`:1192`). This closes the particular record-versus-successor mismatch, but `_landed_sections` derives a new declaration path from the record (`:373`), and finalization derives a new surface path from the record (`:920`). The write destination and the later read destinations are consequently selected through different values.

The lock-entry identity check is a separate disk read (`:240`, `:1095`). It does not bind the snapshot the fresh path later consumes. Recovery checks journal identity (`:732`) but then independently reads the declaration (`:757`); its landed-state check reads it again (`:612`) without checking that snapshot's surface. The canonical loader checks witness identity against declaration identity (`src/gzkit/content/ownership.py:400`), not against the transaction's selected target.

## 2. Per-instance severity

**Prompt:** *How bad is each occurrence? One incident, a pattern, or a class of failure?*

**Evidence:**

- _(no citations for this section)_

The original round-9 case-alias CLI defect is an ordinary-operation defect: a differently spelled argument can resolve to the same declared surface and must not produce a witness with a different identity. The brief records that reproduction in its Round 9 section. The current fresh-path change repairs one pairwise equality.

The NEW identity-change examples do not establish another in-scope failure. `tests/commands/test_content_unown.py:2551` and `:2739` mint a genesis for another spelling and hand-write a changed declaration under `.gzkit/` at injected boundaries. The brief's Threat Model (`:899`, `:942`) excludes the actor capable of those writes; its preserved dispatch instruction (`:989`) explicitly rejects a blocking finding requiring hand-written ledger/declaration/journal content. No ordinary identity-changing writer was established in this inspection: fresh unown preserves declaration identity, and `record_unowned_total` rejects an identity change in `_committed_state` (`src/gzkit/content/ownership.py:1143`).

Therefore this is a demonstrated structural inconsistency and defense-in-depth correction proposal, not a newly established blocking severity against the ratified claim. Calling it a new major solely because an injected test can reach it would repeat the scope error this escalation is meant to stop. Existing in-scope findings and the standing review verdict retain their actual dispositions.

## 3. Why this scope

**Prompt:** *Why is the change boundary drawn here and not wider or narrower?*

**Evidence:**

- _(no citations for this section)_

The correction belongs to the local transaction target and its consumers in `src/gzkit/commands/content/unown.py`, with meaningful regression evidence in `tests/commands/test_content_unown.py`. Both are already allowed by this brief. It requires no new OBPI, schema, public command, dependency, ledger implementation, or transaction framework. Shared path/lock/loader helpers were inspected to establish their existing contracts; changing them is not currently necessary.

The brief's ledger-atomicity precondition remains exactly the recorded conditional claim (`docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md:923`). #952/#953 remain separately routed. This proposal does not extend the claim to defending against arbitrary `.gzkit/` writers, pin files forever by inode, or prevent an editor changing a surface after the final observation.

## 4. What it proposes

**Prompt:** *In one paragraph, what is the change?*

**Evidence:**

- _(no citations for this section)_

Use one immutable transaction target, local to this module, containing the selected canonical identity and its fixed surface, declaration, and journal paths. Pre-lock resolution selects the candidate target; the declaration snapshot consumed under its lock must name that exact target before it can authorize a transition. A mismatch refuses this invocation and leaves restarting at entry to a later retry; it never silently adopts another identity while holding the first target's lock. Pass the target through fresh commit, replay, witness construction, and finalization. Payload identities become values checked against the target, never inputs that route filesystem reads or writes. Preserve the same raw-byte snapshot for span measurement and digest construction, and retain the existing shared post-write surface check and recovery semantics.

The invariant is:

> Every filesystem operation for a transition uses one selected target. The declaration snapshot, journal, serialized successor, and witness all name that target's declared identity. The witness describes the successor actually written at that target's declaration path. Recovery finishes the same target and transition; it cannot select a different target from journal content.

Concrete read/write inventory:

| Phase | Current reads/writes | Correction |
|---|---|---|
| Resolve and lock | Read requested/declared identity and surface alias relation; derive three paths; lock the declaration sidecar (`unown.py:129`, `:1069`; `file_lock.py:83`). | Resolve input aliases before locking; freeze the resulting target and paths. The lock is the existing sidecar, not the replaceable declaration inode. |
| Fresh preparation | Read raw surface bytes; canonical loader reads declaration plus ledger; build record and successor from loaded declaration (`unown.py:1096`, `:1131`, `:1173`). | Check the returned declaration snapshot's identity against the target, then use that very object. Derive successor and witness fields from this bound snapshot. A separate earlier identity peek is insufficient. |
| Journal and declaration commit | Write journal and declaration to earlier supplied paths (`unown.py:799`). | Both writes use target paths; serialized successor must name the target. Preserve existing durable write ordering and failure reporting. |
| Recovery | Read journal; read declaration; possibly derive/write successor; reopen landed state (`unown.py:680`, `:757`, `:470`, `:612`). | Bind parsed journal, parsed successor, and consumed declaration snapshots to the same target in both landed and unlanded branches. Do not use the full ledger-dependent loader before recovery: a legitimate pending declaration may name the event recovery still needs to append. |
| Witness | Re-derive declaration path from record, read its map, look up/append ledger witness (`unown.py:373`, `:384`). | Read the fixed declaration destination, validate the landed snapshot's identity, event pointer, floor, and complete map against the expected transition, and use that same snapshot to derive witness evidence. Keep semantic comparison for an existing event ID. |
| Finalization | Re-derive surface path from record; check raw digest; unlink original journal (`unown.py:892`). | Recheck the fixed target surface path; retain the journal on mismatch. Cleanup and success prose use the same target and transition. |

This changes how evidence is carried through the operation, rather than adding a new independent check before another independent read. A frozen target by itself is not sufficient: paths are immutable values, while their contents remain mutable.

## 5. Routing decision

**Prompt:** *Direct fix, OBPI ceremony, or new ADR? Cite the threshold that routed it.*

**Evidence:**

- _(no citations for this section)_

This is a design proposal under the already active OBPI, presented on explicit operator request. No routing threshold is being used to start a new implementation route. The existing pipeline's repeated-root escalation rule (`.gzkit/skills/gz-obpi-pipeline/SKILL.md:886`) explains the escalation; it does not authorize changing scope. Implementation remains with the operator-initiated workflow. No lock, task, pipeline marker, brief, or production file was changed for this assessment, and no acceptance round was dispatched.

The `gz-justify` CLI generated this scaffold for `OBPI-0.35.0-04`. The canonical skill's Claude-only instruction to spawn `model="opus"` cannot be executed by the native Codex dispatch surface. The fallback was disclosed in the conversation: the primary used the same evidence/validation workflow with two native agents independently inspecting recovery and threat-model/test reachability. This is not a tier-1 acceptance review or a claim of runtime parity.

## 6. Why this design is right-sized

**Prompt:** *Why isn't this bigger or smaller? What does this shape defend against?*

**Evidence:**

- _(no citations for this section)_

The target is justified because the same resource choice must be carried through multiple existing helpers. No generic manager or new persistence format is needed. Passing fixed paths into the existing helpers removes the downstream routing authority currently granted to `record["surface"]`. Binding and then consuming one snapshot removes the separate-read assumption that the recent patches relied on.

Stable alias input remains supported: requests that resolve to the same declared identity choose the same declaration/journal/lock paths before any transition begins. A changed declaration identity after target selection is different from a stable input alias: it refuses rather than implicitly migrating a transaction. Surface-file `samefile` alone never proves ownership sidecars are shared, because declaration, journal and lock helpers derive those names separately (`ownership.py:932`, `:949`; `file_lock.py:83`).

Checks remain appropriate at external-state boundaries. The defect is not that all comparisons are inherently unsafe; it is checking one snapshot and allowing a different snapshot or payload field to choose the resources later used. Existing raw-byte rereads remain necessary for ordinary editor changes. The invariant is scoped to the transaction's observations and effects, not to preventing future edits after it returns.

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

The direct source inventory above grounds this proposal. The recorded brief boundary grounds its scope classification. The current assessed checkout is HEAD `397301c629bf3007943c43295f0adaafbd8c7fa8` plus existing uncommitted changes. SHA-256 at inspection: `unown.py` = `f2cf1237693d6f58aad5c6f418afcd485d2a584a0b8e33aeaf1b95f4fe0d4278`; `test_content_unown.py` = `ea6c53c356c48b575955f7c773832869f873237cbc1be4688e13b061d0cb7695`.

An independent native agent executed four diagnostic tests against this current tree:

```text
uv run --cache-dir /tmp/gzkit-codex-assess-uv --no-sync python -m unittest tests.commands.test_content_unown.TestContentUnownRound9.test_a_second_spelling_of_the_surface_witnesses_the_declared_identity tests.commands.test_content_unown.TestContentUnownRound9.test_a_request_naming_a_different_file_than_the_declaration_is_refused tests.commands.test_content_unown.TestContentUnownRound9.test_an_identity_swapped_between_resolution_and_the_lock_is_refused tests.commands.test_content_unown.TestContentUnownRound9.test_the_witness_carries_the_declaration_the_transition_actually_wrote
....
Ran 4 tests in 0.014s
OK
```

Exit 0. These are diagnostic observations, not ARB gate receipts. The last two tests use the excluded direct-mutation actor described in Section 2. Their passing state does not prove path binding. The reported 9,350-test suite and scanner mutation witnesses were supplied in the user-relayed session report and were not independently rerun here.

Verification obligations for the PROPOSED correction, not completed checks:

- Stable case-alias input succeeds with one declared identity, one correctly incremented floor, one witness, unchanged source bytes, and canonical reload.
- Different-file input refuses before declaration/journal/ledger writes.
- Fresh, unlanded-replay, and landed-replay paths retain the same selected paths and identity through witness and cleanup. Exercise supported failures at journal, declaration, and ledger boundaries; retries preserve the transition/event ID and do not raise twice.
- LF and CRLF measurement, precommit checks, and final checks use raw bytes. Ordinary source edits retain their existing refusal/recovery behavior in both paths.
- Defense-in-depth identity-mismatch tests assert deterministic refusal and no transaction writes after the injected mismatch, rather than forcing success by silently adopting a new target. Keep a separate positive alias test; never weaken assertions to allow either success or failure indiscriminately.
- Mutation witnesses must be executed and retained. Each targeted mutation must fail the intended assertion with otherwise valid setup; explain scope and distinguish these witnesses from an adversarial acceptance verdict.

## 8. Residual uncertainty

**Prompt:** *What am I not sure about? What would change my mind?*

**Evidence:**

- _(no citations for this section)_

This walkthrough is a reviewable correction proposal, not implemented or proven behavior. No normal-operation trace was established for the late declaration-identity change; a concrete such trace would change its blocking classification. Synthetic .gzkit rewrites cannot substitute for that trace. A future implementation must preserve the original stable-alias requirement while changing the synthetic identity-race expectation from target adoption to refusal; this semantic distinction must be explicit to reviewers.

Freezing values cannot make the external filesystem immutable. The proposal does not establish crash durability of the shared ledger, replace the accepted ledger precondition, or add protection against arbitrary metadata writers, symlink retargeting, and filesystem topology attacks. Existing defense-in-depth guards remain, and ordinary source edits remain within the declared boundary.

The `gz justify validate` result only establishes that this eight-section walkthrough is structurally filled. It cannot validate the correctness of the proposed code change or supply an acceptance verdict. This artifact is cited in the operator-facing escalation; seating it in an OBPI brief or plan receipt remains part of the operator-initiated workflow.


### Authoring-time complexity hints

- **/Users/jeff/Documents/Code/gzkit/src/gzkit/content/ownership.py:442-442** — long_parameter_list (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/content/ownership.py:586-586** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/content/ownership.py:835-835** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/content/ownership.py:1247-1247** — long_parameter_list (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/unown.py:54-54** — long_parameter_list (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/unown.py:82-82** — long_parameter_list (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/unown.py:240-240** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/unown.py:286-286** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/unown.py:384-384** — long_parameter_list (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/unown.py:799-799** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/unown.py:892-948** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/unown.py:998-1050** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/unown.py:1053-1053** — long_parameter_list (approaching_warn)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/tests/content/test_tui_affordances.py:75-75** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/tests/content/test_tui_affordances.py:125-125** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
- **/Users/jeff/Documents/Code/gzkit/tests/content/test_tui_affordances.py:254-254** — long_parameter_list (approaching)
  Guidance: cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.
  Move: When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.
