---
id: OBPI-0.35.0-20-pipeline-skill-cutover
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 20
lane: Heavy
status: Draft
allowlist:
  - .gzkit/skills/gz-obpi-pipeline/SKILL.md
  - .gzkit/skills/gz-obpi-pipeline/references/**
  - src/gzkit/skills/gz-obpi-pipeline/**
  - .claude/skills/gz-obpi-pipeline/**
  - .agents/skills/gz-obpi-pipeline/**
  - src/gzkit/governance/trust_audits/cli.py
  - src/gzkit/skill_body_grandfather.json
  - data/obpi_pipeline_control_inventory.json
  - data/mandated_tier1_dispatch.json
  - tests/governance/test_pipeline_control_inventory.py
  - tests/governance/test_cli_alignment_scope.py
  - tests/governance/test_audit_skill_alignment_seam.py
  - tests/governance/test_skill_code_citations.py
  - tests/test_obpi_skill_migration.py
  - tests/skills/test_skill_surface_sync_justify.py
  - tests/governance/test_skill_self_close_drift.py
  - tests/governance/test_agent_contract_fold.py
  - tests/governance/test_mandated_tier1_dispatch.py
  - docs/user/manpages/obpi-pipeline.md
  - docs/user/runbook.md
  - docs/user/concepts/subagent-pipeline.md
  - docs/user/skills/gz-obpi-pipeline.md
  - docs/governance/governance_runbook.md
  - docs/governance/obpi-pipeline-control-rationale.md
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-20-pipeline-skill-cutover.md
reqs:
  - REQ-0.35.0-20-01
  - REQ-0.35.0-20-02
  - REQ-0.35.0-20-03
  - REQ-0.35.0-20-04
  - REQ-0.35.0-20-05
  - REQ-0.35.0-20-06
verification:
  - uv run -m unittest tests.governance.test_pipeline_control_inventory tests.test_pipeline_procedure
  - uv run -m unittest tests.governance.test_cli_alignment_scope tests.governance.test_audit_skill_alignment_seam tests.governance.test_skill_code_citations
  - uv run -m unittest tests.test_obpi_skill_migration tests.skills.test_skill_surface_sync_justify tests.governance.test_skill_self_close_drift tests.governance.test_agent_contract_fold tests.governance.test_mandated_tier1_dispatch tests.test_skill_body_audit
  - uv run -m behave features/obpi_pipeline_stage_procedure.feature
  - uv run gz skill audit
  - uv run gz validate --cli-alignment --skill-alignment --distribution --wheel-path-literals --config-registry --req-kind-discipline
  - uv run gz cli audit
  - uv run mkdocs build --strict
---

# OBPI-0.35.0-20-pipeline-skill-cutover: Pipeline Skill Cutover

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #20 - "Pipeline skill cutover to the served procedure -- the skill body keeps its invocation text only, with every control in the item 17 inventory still delivered at its stage, every reader and audit of the skill body following the text to where it is served, and the incident history kept in a rationale record. Repair assignment against `ADR-0.13.0` (GHI #1174, split from item 17 by amendment 2026-10-04 (2))"
- **Decision Item:** § Decision item 13, verbatim - "THE PIPELINE SKILL'S STAGE PROCEDURE IS SERVED BY THE RUNTIME, ONE STAGE AT A TIME (operator-ruled 2026-10-04, GHI #1174; repair assignment). The procedure an agent follows for a stage is delivered when that stage is entered. Every control the skill states today is still delivered at the stage where it applies; this is a change of delivery, never a shortening. Obligation repaired: `ADR-0.13.0` § Decision, "Make skills, hooks, and future agent control surfaces call into the same runtime engine instead of re-implementing stage logic in prose". Depends on item 12. AMENDED 2026-10-04 (operator-ruled, `OBPI-0.35.0-17` Q6): delivered as checklist items 17 and 20. Item 17 makes the control inventory and the runtime serving with the skill body untouched; item 20 performs the cutover, after the operator has attested the inventory."

**Status:** Draft

**Split 2026-10-04 (operator-ruled).** This brief is the second of two that deliver § Decision item 13. `OBPI-0.35.0-17-stage-procedure-served-by-runtime` makes the control inventory and the runtime serving and leaves the skill body untouched. This brief performs the cutover, and only after that brief is attested. Asked whether brief 17 is split in two, the operator answered, verbatim: "A".

**This is a repair assignment.** It repairs an obligation that `ADR-0.13.0-obpi-pipeline-runtime-surface` stated and its shipped surface does not meet. That ADR is `Validated` and is not reopened or edited. The obligation keeps its original identity:

- `ADR-0.13.0` § Decision: "Make skills, hooks, and future agent control surfaces call into the same runtime engine instead of re-implementing stage logic in prose" (carried there as checklist item `OBPI-0.13.0-05`).
- `ADR-0.13.0` § Promotion Criteria, item 4: "Skill text and hook adapters are reduced to thin wrappers over the runtime surface."

The REQs below (`REQ-0.35.0-20-NN`) are this brief's local acceptance criteria. They do not replace or renumber any `REQ-0.13.0-*`. Criteria 01, 03, 04, 05 and 06 were drafted in `OBPI-0.35.0-17` before the split, as that brief's former criteria 04, 07, 08, 09 (in part) and 10; criterion 02 is new.

## Objective

The text loaded when the `gz-obpi-pipeline` skill is invoked carries no stage's procedure: the skill body holds its invocation text only, and each stage's procedure reaches the agent from the runtime at stage entry, as `OBPI-0.35.0-17` landed it. Every control in that brief's attested inventory is still delivered at every stage where it applies. None is dropped and none is shortened.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

The contract changes are the content of the wheel-delivered `gz-obpi-pipeline` skill package that adopters receive, and the set of files that `gz validate --cli-alignment`, `gz validate --skill-alignment` and the source-path citation audit read.

## Allowed Paths

The path marked (Q2) follows the ruling on that question in § Open Design Questions. Two paths are created by `OBPI-0.35.0-17` and do not exist until it lands; each says so.

- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — the canonical skill body: after this OBPI it holds the invocation text only
- `.gzkit/skills/gz-obpi-pipeline/references/**` — the per-stage procedure files `OBPI-0.35.0-17` created: a passage classed `rationale` leaves for the rationale record, and each control that had one gains a pointer to its entry
- `src/gzkit/skills/gz-obpi-pipeline/**`, `.claude/skills/gz-obpi-pipeline/**`, `.agents/skills/gz-obpi-pipeline/**` — the wheel copy and the vendor mirrors, written only by the control-surface sync, never hand-edited
- `src/gzkit/governance/trust_audits/cli.py` — the three audits that read skill text from the skill body file only (verb resolution, wielding skill, source-path citations); they read the served procedure text too
- `src/gzkit/skill_body_grandfather.json` — the fixed body ceiling for this skill: lowered or removed, never raised
- `data/obpi_pipeline_control_inventory.json` — **CREATE** in `OBPI-0.35.0-17`, which must be completed first; this OBPI updates a row's delivered span only where Requirement 4 allows it, and never the pinned baseline
- `data/mandated_tier1_dispatch.json` — its two directive paths name the skill body as the file that carries the Step 4b dispatch; they follow that text to where it is delivered
- `tests/governance/test_pipeline_control_inventory.py` — **CREATE** in `OBPI-0.35.0-17`, which must be completed first; this OBPI adds the two checks that have no subject until the cutover
- `tests/governance/test_cli_alignment_scope.py`, `tests/governance/test_audit_skill_alignment_seam.py`, `tests/governance/test_skill_code_citations.py` — the audits' source sets
- `tests/test_obpi_skill_migration.py`, `tests/skills/test_skill_surface_sync_justify.py`, `tests/governance/test_skill_self_close_drift.py`, `tests/governance/test_agent_contract_fold.py`, `tests/governance/test_mandated_tier1_dispatch.py` — existing tests that read the skill body for stage text, most of them proofs of attested REQs (Requirement 6)
- `docs/user/manpages/obpi-pipeline.md` — it stops saying the skill body still carries each stage's procedure
- `docs/user/runbook.md`, `docs/governance/governance_runbook.md` — the operator and governance flows where they describe the skill
- `docs/user/concepts/subagent-pipeline.md`, `docs/user/skills/gz-obpi-pipeline.md` — where they say the skill body is the execution contract
- `docs/governance/obpi-pipeline-control-rationale.md` — **CREATE** (Q2), sibling of the skill-surface-sync rationale in the same directory: the rationale record keyed by control
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-20-pipeline-skill-cutover.md`

## Denied Paths

- The inventory checker, the procedure resolver and the stage runners that `OBPI-0.35.0-17` landed — used as landed and never changed here. A defect found in one of them is surfaced to the operator, not repaired inside the cutover.
- `src/gzkit/commands/obpi_cmd.py`, `src/gzkit/pipeline_markers.py`, `src/gzkit/cli/parser_obpi.py` — no verb, flag or marker field is added. The first two are registered security surfaces (`data/security_surfaces.json`).
- `.claude/hooks/**`, `src/gzkit/hooks/**` — no hook is changed. The hooks are the hard enforcement the skill's own design notes name, and changing one is a change to a control.
- `src/gzkit/skill_contract.py`, `src/gzkit/skills_audit.py` — the body limits and the audit stay as they are. Only this skill's grandfather entry moves, and only downward.
- `src/gzkit/sync_skills.py`, `src/gzkit/sync_surfaces.py`, `src/gzkit/skills_mirror.py`, `pyproject.toml` — the delivery machinery is unchanged.
- `src/gzkit/ledger_events.py`, `src/gzkit/schemas/ledger.json` — no ledger event is added.
- `.gzkit/skills/**` outside `gz-obpi-pipeline` — no other skill is converted. The catalog-wide form is `ADR-pool.skill-runtime-authority-inversion`, which stays in the pool.
- `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/**`, `docs/design/adr/pool/**` — the repaired ADR is `Validated` and is not reopened; the pool ADR is not promoted or edited.
- `AGENTS.md`, `.gzkit/corpus/**`, `.gzkit/rules/**` — no canon or rule changes. The rule conflict in Q5 is ruled as an exception for this OBPI, not edited away.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: This OBPI repairs `ADR-0.13.0` § Decision and § Promotion Criteria item 4, as quoted under § ADR Item. It does not edit `ADR-0.13.0`, does not reopen `OBPI-0.13.0-05`, and does not claim any `REQ-0.13.0-*`.
2. REQUIREMENT: Nothing starts before `OBPI-0.35.0-17` is completed in the ledger and attested. The inventory that brief pinned is the fence for this one: its baseline (commit, skill version and body digest) is never edited here, and no control row is removed or merged.
3. REQUIREMENT: Nothing is dropped. After the cutover every control in the inventory is delivered at every position in its `applies_at`: a control that applies at `invocation` is in the skill body, and a control that applies at a stage is in the procedure the runtime serves for that stage. Two controls that contradict each other are both carried as written and put to the operator; a correction is made only by a ruling recorded in the Change Log.
4. REQUIREMENT: Delivery is verbatim. A control's delivered span equals its baseline quote byte for byte. A row may differ only when it declares the rewording with a reason (a cross-reference that no longer resolves, or a ruled correction), and every reworded row id is named in the operator's attestation text. Operator quotations and the blocks the skill marks as verbatim canon (§ Work selection) are never reworded.
5. REQUIREMENT: The skill body holds the invocation text only: what the skill is for, when to use it, how the runtime is launched, and the controls that apply before any stage or at every stage. It states that each stage's procedure is served by the runtime on entry. Its body length is at or below the new ceiling, and the ceiling is lowered to that length or removed.
6. REQUIREMENT: Every existing reader of the skill body is repaired in the same change. The known readers are the five test modules and the registry named in Allowed Paths; the plan searches for others before the body is edited. Where a reader proves an attested REQ of a terminal ADR (`REQ-0.0.14-03-*`, `REQ-0.0.19-04-06`, `REQ-0.0.36-05-06`), `docs/governance/attested-req-subject-retirement.md` governs: read what the REQ literally asserts, repoint the proof at the place the text is now delivered, keep the `@covers` binding, and record the amendment in the test. A REQ that literally asserts the text lives in the skill body file is escalated to the operator, not rewritten.
7. REQUIREMENT: The audits read what the agent is served, and they do so before any text leaves the skill body. `gz validate --cli-alignment`, `gz validate --skill-alignment` and the source-path citation audit read every served stage procedure. The plan orders the audit change ahead of the body edit. A check that stays green because it no longer reads the moved text is a failure of this OBPI.
8. REQUIREMENT: Incident history moves to the rationale record, verbatim, under the id of the control it explains, and each delivered control that had such a passage carries a pointer to its entry. Only text the inventory classes `rationale` moves. A sentence that binds behaviour is a control row and stays delivered at its stage.
9. REQUIREMENT: Skill edits are made in `.gzkit/skills/` only. The skill version and `last_reviewed` move in the same edit, and `uv run gz agent sync control-surfaces` regenerates the wheel copy and the mirrors (`.gzkit/rules/skill-surface-sync.md`).
10. REQUIREMENT: This OBPI's own pipeline run is the real run. It is executed from Stage 1 under the delivery `OBPI-0.35.0-17` landed, and Key Proof records each stage-entry output the run received. Its Stages 3 to 5 run after the cutover, so they are served with the skill body already reduced.
11. NEVER change, disable or weaken a hook, a validator, a gate, a `gz check` step or a runtime refusal. No control of the pipeline is removed (campaign § Amendments 2026-10-04 (2): "none is removed by this entry").
12. NEVER compress, merge, summarize or reword to save length. This is a change of delivery, never a shortening (§ Decision item 13; operator under GHI #460: "i don't trust shortening though"). By the ruling on Q5 the Decision governs over the compress-before-lifting rules for this OBPI, and the commit states that nothing was compressed.
13. NEVER record a run's position or derive its next command here. Those are items 15 and 16.
14. ALWAYS disclose the residual. The inventory proves that a control's text is present in what a stage is served. It does not prove that an agent reads or follows it, that extraction caught every sub-clause, or that one run generalizes.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Open Design Questions (operator rules before plan)

Both questions were drafted in `OBPI-0.35.0-17` and moved here with the cutover on the 2026-10-04 split. The brief is written to the recommended option so that it is checkable, and names what a different ruling changes.

- **Q2. Where the incident history goes.** (a) `docs/governance/obpi-pipeline-control-rationale.md`, keyed by control id, following the existing rationale documents. (b) A reference file beside the skill, which the mirrors and the wheel carry. (c) Inside the inventory rows. **Recommended: (a)**, with each delivered control gaining a pointer to its entry. `.gzkit/rules/skill-authoring.md` § Parsimony clause 1 also asks for "one sentence of reason" in the body; where the control's own sentence already gives its reason it stays, and no new summary sentence is written, because a summary is a rewording (Requirement 12). (a) is not delivered to adopters; (b) is, at the cost of loading history beside the procedure again.
  - **RULED 2026-10-05: (a).** Asked where the incident history goes, the operator answered, verbatim: "A". The history moves verbatim to `docs/governance/obpi-pipeline-control-rationale.md`, keyed by control id, and each delivered control that had such a passage gains a pointer to its entry. The inventory in `OBPI-0.35.0-17` keeps the shape that brief states, so its Q2 prerequisite is met.
- **Q5. A rule and a directive conflict; both are quoted.** `.gzkit/rules/skill-authoring.md` § Parsimony clause 6: "Lifting to `references/` is the move after that search, not instead of it, and the commit says what was compressed as well as what was lifted." `AGENTS.md` § Behavior Rules: "A size limit triggers a compress-and-merge pass before any growth or extraction; say what was compressed." Against them, § Decision item 13: "this is a change of delivery, never a shortening." **Recommended:** the Decision governs this OBPI, as the later and surface-specific ruling. Nothing is compressed, and the commit says so. Any compression of the served procedures is later work, fenced by the inventory.
  - **RULED 2026-10-05: the Decision governs.** With both rules and § Decision item 13 quoted, the operator answered, verbatim: "A". Nothing is compressed in this OBPI, and the commit says so in plain words. The two rules are not edited; this is an exception for this OBPI alone. Requirement 12 stands as written.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary: § Decision item 13, "THE PIPELINE SKILL'S STAGE PROCEDURE IS SERVED BY THE RUNTIME, ONE STAGE AT A TIME", as quoted in full under § ADR Item, with its 2026-10-04 amendment.
- [ ] Parent ADR § Intent — the two paragraphs "AMENDED 2026-10-04": what the repair assignments are, that none removes a control, and why item 17 is delivered as items 17 and 20.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] `docs/governance/attested-req-subject-retirement.md` - governs Requirement 6

**Context:**

- [ ] `OBPI-0.35.0-17-stage-procedure-served-by-runtime` as landed: § Control Inventory Contract, the inventory it committed, and its attestation text
- [ ] GHI #1174 in full: its closure contract is the source of these requirements
- [ ] GHI #1091 and `docs/evals/compression-sweep-2026-09-24.md`: a rewrite with no condition-level accounting dropped 23 binding conditions. Requirements 2 to 4 exist because of it.
- [ ] `docs/design/adr/pool/ADR-pool.skill-runtime-authority-inversion.md`: the catalog-wide form of this finding, and its refusal of a shortening pass that leaves the skill as the authority
- [ ] `.gzkit/chores/instructions-files-diet/proofs/pipeline-review-2026-09-19/README.md`: the earlier lift of six incident passages

**Prerequisites (check existence, STOP if missing):**

- [ ] `OBPI-0.35.0-17-stage-procedure-served-by-runtime` is completed in the ledger and attested: `uv run gz obpi status OBPI-0.35.0-17-stage-procedure-served-by-runtime`. STOP if it is not.
- [ ] The operator's rulings on Q2 and Q5 are recorded in this brief, and Allowed Paths, Verification and Demo are reconciled with them and with what `OBPI-0.35.0-17` landed (`uv run gz obpi validate --authored` on this brief passes after the reconcile).
- [ ] Required path exists: `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, with a body digest equal to the inventory's pinned baseline
- [ ] Required path exists: `src/gzkit/governance/trust_audits/cli.py`
- [ ] Required path is intentionally created in this OBPI: `docs/governance/obpi-pipeline-control-rationale.md`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `.gzkit/skills/gz-obpi-pipeline/SKILL.md` in full, and the per-stage procedure files beside it
- [ ] `src/gzkit/governance/trust_audits/cli.py` — `_cli_alignment_sources`, `audit_skill_code_citations` and `_collect_skill_verb_refs`: each globs for the skill body file by name
- [ ] `src/gzkit/skills_audit.py` and `src/gzkit/skill_contract.py` — the body line count, the ceiling lookup, and the test that lets a ceiling only shrink (`tests/test_skill_body_audit.py`)
- [ ] The five test modules of Requirement 6 and the REQ each one covers, read against `docs/governance/attested-req-subject-retirement.md`
- [ ] `data/mandated_tier1_dispatch.json` and `tests/governance/test_mandated_tier1_dispatch.py` — the two directive paths that name the skill body
- [ ] `docs/user/concepts/subagent-pipeline.md`, `docs/user/skills/gz-obpi-pipeline.md`, `docs/user/runbook.md` and `docs/governance/governance_runbook.md` — every statement that the skill body is the execution contract for a stage
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated: the pipeline manpage, both runbooks, the subagent-pipeline concept page, the skill's user page and the rationale record

### Gate 4: BDD (Heavy only)

- [ ] The stage-entry scenarios `OBPI-0.35.0-17` landed still pass after the cutover: `uv run -m behave features/obpi_pipeline_stage_procedure.feature`. This OBPI adds no operator-visible command behaviour of its own; its BEHAVIOR REQs are proven by `@covers` unit tests.

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded, naming every reworded row id (Requirement 4)

## Verification

```bash
uv run -m unittest tests.governance.test_pipeline_control_inventory tests.test_pipeline_procedure
uv run -m unittest tests.governance.test_cli_alignment_scope tests.governance.test_audit_skill_alignment_seam tests.governance.test_skill_code_citations
uv run -m unittest tests.test_obpi_skill_migration tests.skills.test_skill_surface_sync_justify tests.governance.test_skill_self_close_drift tests.governance.test_agent_contract_fold tests.governance.test_mandated_tier1_dispatch tests.test_skill_body_audit
uv run -m behave features/obpi_pipeline_stage_procedure.feature
uv run gz skill audit
uv run gz validate --cli-alignment --skill-alignment --distribution --wheel-path-literals --config-registry --req-kind-discipline
uv run gz cli audit
uv run mkdocs build --strict
```

## Demo

The command is self-contained and exits non-zero on a bad state. It runs the inventory checker over the committed inventory against the reduced skill body and what the runtime serves in this tree: every control is delivered at each position it applies to, no stage's control sits in the invocation text, and every `rationale` passage is in the rationale record under its control's id.

```bash
uv run -m unittest tests.governance.test_pipeline_control_inventory -v
```

The real run of Requirement 10 is recorded in Key Proof.

## Acceptance Criteria

<!-- REQ kinds per ADR-0.0.59; enforced by gz validate --req-kind-discipline. -->

- [ ] REQ-0.35.0-20-01 [BEHAVIOR]: Given the committed inventory, when the invocation text and each stage's served procedure are examined, then no control whose `applies_at` omits `invocation` has its delivered span in the invocation text, and no control has its delivered span in the procedure of a stage outside its `applies_at`. Copying one Stage 4 control into the skill body makes the check fail.
- [ ] REQ-0.35.0-20-02 [BEHAVIOR]: Given the committed inventory with the baseline `OBPI-0.35.0-17` pinned, when the checker runs against the reduced skill body and the procedure the runtime serves for each stage, then the baseline is unchanged, every control's delivered span is present at every position in its `applies_at`, every span equals its baseline quote unless the row declares a rewording with a reason, and no violation is returned. Deleting one control's text from the skill body or from a served procedure makes the check fail and name that control's id.
- [ ] REQ-0.35.0-20-03 [BEHAVIOR]: Given a served stage procedure that names an unregistered `gz` verb or cites a source path that does not exist, when the verb-resolution audit and the citation audit run, then each reports it against that file; and given a verb named only in a served stage procedure, when the wielding-skill audit runs, then the verb counts as wielded.
- [ ] REQ-0.35.0-20-04 [SUPPORT]: The skill body is edited in canon only, with its skill version and `last_reviewed` moved in the same edit. The wheel copy and every enabled vendor mirror, supporting files included, are regenerated by the control-surface sync. `uv run gz skill audit` reports no mirror, asset or body finding for this skill, and the skill's entry in `src/gzkit/skill_body_grandfather.json` is lowered to the new body length or removed. Witnessed by `artifact_edited` citing `.gzkit/skills/gz-obpi-pipeline/SKILL.md` + `gz validate --distribution`.
- [ ] REQ-0.35.0-20-05 [SUPPORT]: The two runbooks, the subagent-pipeline concept page and the skill's user page say that each stage's procedure is served by the runtime on entry, and none says the skill body is the execution contract for a stage. The pipeline manpage no longer says the skill body still carries each stage's procedure. Witnessed by `artifact_edited` citing `docs/user/skills/gz-obpi-pipeline.md` + `gz validate --cli-alignment`.
- [ ] REQ-0.35.0-20-06 [SUPPORT]: The rationale record holds, under the id of the control it explains, every baseline passage the inventory classes as `rationale`, verbatim, and each delivered control that had such a passage carries a pointer to its entry. Witnessed by `artifact_edited` citing `docs/governance/obpi-pipeline-control-rationale.md` + `gz validate --cli-alignment`.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Change Log

<!-- Keep substantive implementation, test, documentation, and evidence
     corrections within this OBPI. Reuse existing finding identities and cite
     the affected REQ or contract clause, change, and proof/closure references.
     Group related repairs; do not log every edit or duplicate transcripts.
     This is an index to evidence, not a second acceptance ledger. Record approved
     amendments in their normative sections and reference the ruling here.
     Create a GHI only when independent work or disposition is needed, or the
     operator explicitly requests an issue; link it back to the owning work.
     Keep this subsection under Evidence so history is not treated as contract. -->

_No substantive adjustments recorded yet._

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Link independently routed GitHub defects, one bullet per issue so status
     surfaces preserve traceability. Within-OBPI corrections belong in the
     Change Log above; they do not need a GHI. An issue link does not discharge
     an unmet acceptance obligation. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
