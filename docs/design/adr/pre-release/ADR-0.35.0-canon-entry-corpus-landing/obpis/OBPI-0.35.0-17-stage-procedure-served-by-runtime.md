---
id: OBPI-0.35.0-17-stage-procedure-served-by-runtime
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 17
lane: Heavy
status: Draft
allowlist:
  - .gzkit/skills/gz-obpi-pipeline/SKILL.md
  - .gzkit/skills/gz-obpi-pipeline/references/**
  - src/gzkit/skills/gz-obpi-pipeline/**
  - .claude/skills/gz-obpi-pipeline/**
  - .agents/skills/gz-obpi-pipeline/**
  - src/gzkit/pipeline_procedure.py
  - src/gzkit/governance/pipeline_control_inventory.py
  - src/gzkit/commands/obpi_stages.py
  - src/gzkit/pipeline_runtime.py
  - src/gzkit/registries.py
  - src/gzkit/content/retention.py
  - data/obpi_pipeline_control_inventory.json
  - data/config_registry.json
  - tests/governance/test_pipeline_control_inventory.py
  - tests/test_pipeline_procedure.py
  - tests/commands/test_obpi_stages.py
  - tests/commands/test_obpi_pipeline.py
  - features/obpi_pipeline_stage_procedure.feature
  - features/steps/obpi_pipeline_stage_procedure_steps.py
  - docs/user/manpages/obpi-pipeline.md
  - docs/user/runbook.md
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-17-stage-procedure-served-by-runtime.md
reqs:
  - REQ-0.35.0-17-01
  - REQ-0.35.0-17-02
  - REQ-0.35.0-17-03
  - REQ-0.35.0-17-04
  - REQ-0.35.0-17-05
  - REQ-0.35.0-17-06
  - REQ-0.35.0-17-07
verification:
  - uv run -m unittest tests.governance.test_pipeline_control_inventory tests.test_pipeline_procedure
  - uv run -m unittest tests.commands.test_obpi_stages tests.commands.test_obpi_pipeline
  - uv run -m unittest tests.governance.test_cli_alignment_scope tests.governance.test_audit_skill_alignment_seam tests.governance.test_skill_code_citations
  - uv run -m unittest tests.test_obpi_skill_migration tests.skills.test_skill_surface_sync_justify tests.governance.test_skill_self_close_drift tests.governance.test_agent_contract_fold tests.governance.test_mandated_tier1_dispatch tests.test_skill_body_audit
  - uv run -m behave features/obpi_pipeline_stage_procedure.feature
  - uv run gz skill audit
  - uv run gz validate --cli-alignment --skill-alignment --distribution --wheel-path-literals --config-registry --req-kind-discipline
  - uv run gz cli audit
  - uv run mkdocs build --strict
---

# OBPI-0.35.0-17-stage-procedure-served-by-runtime: Stage Procedure Served By Runtime

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #17 - "Stage procedure served by the runtime -- a control inventory of the pipeline skill's body is made first, and each stage's procedure is delivered when that stage is entered, with the skill body untouched. Repair assignment against `ADR-0.13.0` (GHI #1174, amendment 2026-10-04; split 2026-10-04, see item 20)"
- **Decision Item:** § Decision item 13, verbatim - "THE PIPELINE SKILL'S STAGE PROCEDURE IS SERVED BY THE RUNTIME, ONE STAGE AT A TIME (operator-ruled 2026-10-04, GHI #1174; repair assignment). The procedure an agent follows for a stage is delivered when that stage is entered. Every control the skill states today is still delivered at the stage where it applies; this is a change of delivery, never a shortening. Obligation repaired: `ADR-0.13.0` § Decision, "Make skills, hooks, and future agent control surfaces call into the same runtime engine instead of re-implementing stage logic in prose". Depends on item 12."

**Status:** Draft

**Split 2026-10-04 (operator-ruled, Q6).** This brief is the first of two that deliver § Decision item 13. It makes the control inventory and the runtime serving, and it leaves the skill body untouched. `OBPI-0.35.0-20-pipeline-skill-cutover` performs the cutover after this brief is attested.

**This is a repair assignment.** It repairs an obligation that `ADR-0.13.0-obpi-pipeline-runtime-surface` stated and its shipped surface does not meet. That ADR is `Validated` and is not reopened or edited. The obligation keeps its original identity:

- `ADR-0.13.0` § Decision: "Make skills, hooks, and future agent control surfaces call into the same runtime engine instead of re-implementing stage logic in prose" (carried there as checklist item `OBPI-0.13.0-05`).
- `ADR-0.13.0` § Promotion Criteria, item 4: "Skill text and hook adapters are reduced to thin wrappers over the runtime surface."

The REQs below (`REQ-0.35.0-17-NN`) are this brief's local acceptance criteria. They do not replace or renumber any `REQ-0.13.0-*`.

Numbering: the Decision item's "Depends on item 12" names § Decision item 12, which is Feature Checklist item 16 and brief `OBPI-0.35.0-16-next-command-for-position`.

## Objective

When a pipeline run enters a stage, the runtime delivers that stage's procedure, copied verbatim from the `gz-obpi-pipeline` skill body, which this OBPI does not edit. A control inventory, made first, lists every control the skill states today and shows each one delivered at every stage where it applies. Nothing is removed here, so nothing can be dropped or shortened; the cutover that reduces the skill body to its invocation text is `OBPI-0.35.0-20`.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

The contract changes are the stage-entry output of `gz obpi pipeline` (it now delivers the entered stage's procedure, and refuses the entry when it cannot) and the content of the wheel-delivered `gz-obpi-pipeline` skill package that adopters receive.

## Allowed Paths

Paths marked (Q1) or (Q4) follow the recommended option of that question in § Open Design Questions. A different ruling changes those paths by an operator-ratified allowlist amendment before the plan is audited.

- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — the `skill-version` and `last_reviewed` frontmatter only, which move because the package gains files; the body is not edited (Requirement 8)
- `.gzkit/skills/gz-obpi-pipeline/references/**` — (Q1) the per-stage procedure files are created here, beside the three reference files the skill already has; **CREATE** for each new stage file
- `src/gzkit/skills/gz-obpi-pipeline/**`, `.claude/skills/gz-obpi-pipeline/**`, `.agents/skills/gz-obpi-pipeline/**` — the wheel copy and the vendor mirrors, written only by the control-surface sync, never hand-edited
- `src/gzkit/pipeline_procedure.py` — **CREATE**, sibling of the existing pipeline stage-fence module in the same directory: resolves the procedure for a stage and reports when it cannot
- `src/gzkit/governance/pipeline_control_inventory.py` — **CREATE**, sibling of the brief-path-validity module in the same directory: the inventory model and the pure, total checker
- `src/gzkit/commands/obpi_stages.py` — the stage runners and the full-launch handoff printer, where stage-entry output is produced
- `src/gzkit/pipeline_runtime.py` — the shared engine the CLI and the generated hooks read
- `src/gzkit/registries.py` — READ-ONLY: the single read seam for a registry under the data directory, imported by the inventory loader
- `src/gzkit/content/retention.py` — READ-ONLY: (Q4) the block splitter and coverage primitives of OBPI-0.35.0-14, imported if the ruling is to reuse them
- `data/obpi_pipeline_control_inventory.json` — **CREATE** (Q4), sibling of the mandated-dispatch registry in the same directory: the control inventory
- `data/config_registry.json` — declares the new registry and its code owner; without the entry the config-registry gate fails closed
- `tests/governance/test_pipeline_control_inventory.py` — **CREATE**, sibling of the mandated-dispatch test in the same directory
- `tests/test_pipeline_procedure.py` — **CREATE**, sibling of the pipeline stage-fence test in the same directory
- `tests/commands/test_obpi_stages.py`, `tests/commands/test_obpi_pipeline.py` — stage-entry output through the command layer
- `features/obpi_pipeline_stage_procedure.feature` — **CREATE**, sibling of the subagent-pipeline feature in the same directory
- `features/steps/obpi_pipeline_stage_procedure_steps.py` — **CREATE**, sibling of the subagent-pipeline steps in the same directory
- `docs/user/manpages/obpi-pipeline.md` — the command contract: what stage entry delivers, the refusal and its recovery
- `docs/user/runbook.md` — the operator flow where it describes what a stage entry prints
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-17-stage-procedure-served-by-runtime.md`

## Denied Paths

- `src/gzkit/commands/obpi_cmd.py`, `src/gzkit/pipeline_markers.py` — both are registered security surfaces (`data/security_surfaces.json`: `auth_boundaries`, `subprocess_user_input`), and both belong to the position and next-command work of items 15 and 16. This OBPI consumes what those items land. If the surface OBPI-0.35.0-16 lands can only be extended inside one of these files, that is an allowlist amendment and a `sensitivity: security` declaration by operator ruling, not an in-flight edit.
- `src/gzkit/cli/parser_obpi.py` — no verb and no flag is added here. The stage-entry surface is OBPI-0.35.0-16's.
- `.claude/hooks/**`, `src/gzkit/hooks/**` — no hook is changed. The hooks are the hard enforcement the skill's own design notes name, and changing one is a change to a control.
- The body text of `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, `src/gzkit/governance/trust_audits/cli.py`, `src/gzkit/skill_body_grandfather.json`, `data/mandated_tier1_dispatch.json`, every test that reads the skill body for stage text, and the rationale record — the cutover is `OBPI-0.35.0-20`. This OBPI removes nothing from the skill body and repoints no reader of it.
- `src/gzkit/skill_contract.py`, `src/gzkit/skills_audit.py` — the body limits and the audit stay as they are.
- `src/gzkit/sync_skills.py`, `src/gzkit/sync_surfaces.py`, `src/gzkit/skills_mirror.py`, `pyproject.toml` — the delivery machinery is unchanged under the recommended Q1 option. The wheel already ships every Markdown file of a skill package, and the sync already mirrors a skill's supporting files.
- `src/gzkit/ledger_events.py`, `src/gzkit/schemas/ledger.json` — no ledger event is added. Recording a run's position is item 15's.
- `.gzkit/skills/**` outside `gz-obpi-pipeline` — no other skill is converted. The catalog-wide form is `ADR-pool.skill-runtime-authority-inversion`, which stays in the pool.
- `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/**`, `docs/design/adr/pool/**` — the repaired ADR is `Validated` and is not reopened; the pool ADR is not promoted or edited.
- `AGENTS.md`, `.gzkit/corpus/**`, `.gzkit/rules/**` — no canon or rule changes. The rule conflict in Q5 is put to the operator, not edited away.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: This OBPI repairs `ADR-0.13.0` § Decision and § Promotion Criteria item 4, as quoted under § ADR Item. Its evidence is cited against those quotes. It does not edit `ADR-0.13.0`, does not reopen `OBPI-0.13.0-05`, and does not claim any `REQ-0.13.0-*`.
2. REQUIREMENT: The inventory is made BEFORE any edit to the skill body. The first plan task pins the baseline (the commit, the skill version and the SHA-256 of the body) and produces the complete before-state. No later task may edit the pinned baseline. No task of this OBPI edits the skill body at all; the first edit to it is OBPI-0.35.0-20's, after this OBPI is attested.
3. REQUIREMENT: Nothing is dropped. The inventory model has no "removed" or "dropped" disposition for a control. Every control row is delivered at every position in its `applies_at`. Two controls that contradict each other are both carried as written and put to the operator; a correction is made only by a ruling recorded in the Change Log. Three are already known: `SKILL.md:1549` prescribes native plan mode where `SKILL.md:88-98` prescribes the plan-audit skill first; `SKILL.md:1654` names an abort release with `--force` where `SKILL.md:1562-1575` requires an abandon category; and the `--from` table at `SKILL.md:163-167` lists two entry points where the parser registers three (`verify`, `ceremony`, `sync`).
4. REQUIREMENT: Delivery is verbatim. A control's delivered span equals its baseline quote byte for byte. A row may differ only when it declares the rewording with a reason (a cross-reference that no longer resolves, or a ruled correction), and every reworded row id is named in the operator's attestation text. Operator quotations and the blocks the skill marks as verbatim canon (§ Work selection) are never reworded.
5. REQUIREMENT: Incident history is inventoried like every other block. A sentence inside a history paragraph that binds behaviour is a control row and is delivered at its stage. Text that binds nothing is classed `rationale` under the id of the control it explains. It stays in the served copy in this OBPI and moves to the rationale record, verbatim, in OBPI-0.35.0-20. Classifying a block as history never removes it from coverage. This is the fence against the hazard GHI #1091 records.
6. REQUIREMENT: A stage's procedure is delivered when the stage is entered, through the surface OBPI-0.35.0-16 lands. A stage entered through `--from` receives the same bytes as the same stage reached in sequence. This holds for every `--from` value the parser registers, not only the two the skill's table lists.
7. REQUIREMENT: Delivery fails closed. When a stage's procedure is missing, unreadable, empty or (if delivered by pointer) not the bytes the runtime expects, stage entry exits non-zero, enters nothing, and prints three-part recovery prose per `.gzkit/rules/guardrail-feedback-prose.md`. The covering test asserts the prose.
8. REQUIREMENT: The skill body is not edited. Its digest at completion equals the `body_sha256` the inventory pins. Each stage's procedure is COPIED into the served text, so between this OBPI and OBPI-0.35.0-20 a stage's procedure loads twice, once from the body and once from the runtime. The split ruling accepts that cost.
9. REQUIREMENT: No reader of the skill body is changed. The tests and the registry that read it for stage text pass unchanged, which is the control that the body was not touched. Repointing them is OBPI-0.35.0-20's.
10. REQUIREMENT: Nothing served is unaudited. The audits keep reading the skill body, which still carries every stage's text, and each served procedure equals baseline text those audits already read (Requirement 4). Widening `gz validate --cli-alignment`, `gz validate --skill-alignment` and the source-path citation audit to the served files is OBPI-0.35.0-20's, and lands there before any text leaves the body.
11. REQUIREMENT: Skill edits are made in `.gzkit/skills/` only. The skill version and `last_reviewed` move in the same edit, and `uv run gz agent sync control-surfaces` regenerates the wheel copy and the mirrors (`.gzkit/rules/skill-surface-sync.md`).
12. REQUIREMENT: The stage-entry output is observed on a real run and recorded in Key Proof: this OBPI's own Stages 3 to 5, entered after the serving is in the tree. The full run under the new delivery, from Stage 1, is OBPI-0.35.0-20's own run (Q6, ruled).
13. NEVER change, disable or weaken a hook, a validator, a gate, a `gz check` step or a runtime refusal. No control of the pipeline is removed (campaign § Amendments 2026-10-04 (2): "none is removed by this entry").
14. NEVER compress, merge, summarize or reword to save length. This is a change of delivery, never a shortening (§ Decision item 13; operator under GHI #460: "i don't trust shortening though"). The rule this sets aside is Q5, which now sits in OBPI-0.35.0-20 with the cutover.
15. NEVER record a run's position or derive its next command here. Those are items 15 and 16. This OBPI adds the procedure to the surface they land.
16. ALWAYS disclose the residual. The inventory proves that a control's text is present in what a stage is served. It does not prove that an agent reads or follows it, that extraction caught every sub-clause, or that one run generalizes.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Control Inventory Contract

The inventory is `data/obpi_pipeline_control_inventory.json` (Q4). It is a complete partition of the baseline skill body, so it needs no git history to check.

```json
{
  "baseline": {
    "path": ".gzkit/skills/gz-obpi-pipeline/SKILL.md",
    "commit": "<sha of the commit the baseline was read from>",
    "skill_version": "<metadata.skill-version at that commit>",
    "body_sha256": "<digest of the body, frontmatter excluded>"
  },
  "extracted_by": "<reviewer agent identity>",
  "mapped_by": "<author agent identity>",
  "blocks": [
    {
      "text": "<one baseline block, verbatim>",
      "controls": [
        {
          "id": "S4-017",
          "quote": "<substring of text>",
          "applies_at": ["stage4"],
          "cause": "<GHI or ruling the skill cites, or null>",
          "delivered_span": "<the text delivered at every applies_at position>",
          "reworded": null
        }
      ],
      "non_control": [
        {"quote": "<substring of text>", "class": "rationale", "explains": "S4-017", "reason": "<why it binds nothing>"}
      ]
    }
  ]
}
```

- **Block.** A heading, paragraph, list item or table row; a fenced block counts as one. The same unit as OBPI-0.35.0-14 Requirement 2. The blocks in order reproduce the baseline body, and their digest equals `body_sha256`.
- **Control.** One statement that binds what the agent does: a required action or its order, a prohibition, a stop or abort condition, a pass condition, or a required output form. A restatement of a control elsewhere in the body is its own row and may share `delivered_span` with the row it restates.
- **`applies_at`.** One or more of `invocation`, `stage1`, `stage2`, `stage3`, `stage4`, `stage5`. `invocation` means the text loaded when the skill is invoked. A control that applies at every stage (the rule against stopping between stages, abort surrender) lists each position it applies at.
- **`non_control`.** Class `rationale` (incident history and reasons; `explains` names a control id and the quote must be present verbatim in the rationale record under that id) or `structure` (a heading, a navigation line, a pointer). Each carries a reason.
- **Coverage.** Every meaningful character of every block lies inside a control quote or a non-control quote, as OBPI-0.35.0-14 defines coverage. Overlap is not coverage.

The checker is pure and total: given the inventory, the baseline body, the invocation text, the text served per stage and the rationale record, it returns every violation, never the first only. Violations: the blocks do not reproduce the baseline digest; a block has an uncovered meaningful character; a quote is not a substring of its block; a control has an empty or unknown `applies_at`; a control's `delivered_span` is absent from the text delivered at one of its positions; a `delivered_span` differs from its quote without a declared rewording and reason; a `non_control` entry has no class or an empty reason; a `rationale` quote is absent from the rationale record under the id it explains; two rows share an id; `extracted_by` or `mapped_by` is empty, or the two are equal after case-folding and trimming.

Phasing after the split (Q6, ruled). This OBPI runs every check on the real tree except two that have no subject until the cutover: the rationale-record check, and the placement check that no stage's control sits in the invocation text. Both are proven here on synthetic fixtures (REQ-0.35.0-17-01) and applied to the real tree by OBPI-0.35.0-20. Until then the invocation text is the untouched skill body, which carries every control.

Dated record, 2026-10-04, skill version 6.64.3, re-measure before relying on it: the body is 1,697 lines as the skill audit counts them, against a ceiling of 1,710 in `src/gzkit/skill_body_grandfather.json`; the five stage sections hold 93,677 of the file's 123,582 characters, and Stage 4 alone holds 44,456. One reader's hand count found about 224 distinct binding statements, with a restatement counted once (22 before any stage, 19 in Stage 1, 48 in Stage 2, 30 in Stage 3, 67 in Stage 4, 18 in Stage 5, 20 in the cross-stage sections after Stage 5). That count is a sizing estimate. It is not the inventory, and the inventory's extraction is independent of it.

## Open Design Questions (operator rules before plan)

The GHI leaves each of these open. The brief is written to the recommended option so that it is checkable, and names what a different ruling changes.

- **Q1. Where the stage procedures live once they leave the skill body.** (a) Per-stage Markdown files inside the skill package, read and served by the runtime. (b) Package data under `src/gzkit/`, read through `importlib.resources`. (c) Text held in runtime code. **Recommended: (a).** The procedures stay operator-authored canon under `.gzkit/skills/` with the existing version, mirror, wheel and audit machinery, and the verbs they name keep a wielding skill. (b) ties the procedure to the runtime version an adopter has installed, which is its real advantage, but creates a canonical surface outside `.gzkit/` and needs the sync, the distribution audit and `pyproject.toml`. Under (a) or (b) the audits in Requirement 10 must be widened either way: today they read the skill body file only (`src/gzkit/governance/trust_audits/cli.py:163`, `:364`, `:521`).
- **Q2. Where the incident history goes.** Moved with the cutover: the question and its ruling are in `OBPI-0.35.0-20` § Open Design Questions.
- **Q3. Whether the runtime prints the procedure or points at it, and in what unit.** (a) Print the stage's text at entry. (b) Print a path and a digest; the agent reads the file. (c) Serve by sub-stage position (4a, 4a-v, 4b), which needs the positions item 15 records. **Recommended: (b), with (c) considered once item 15 has landed.** Stage 4 is 44,456 characters today. A harness that truncates long command output would cut that text with no marker, and a control lost in transport is a dropped control. Measure the harness limit before choosing (a). The cost of (b) is one more step the agent must take; REQ-0.35.0-17-05 covers the missing file, not the unread one.
- **Q4. The inventory's home, its independence rule and its standing check.** The brief puts it in `data/` (declared in `data/config_registry.json`), requires that the agent who extracts controls is not the agent who maps and moves them (the rule § Decision item 10 set for retention maps), and keeps the check as a unit test that runs in `gz check`. Alternatives: the inventory beside the skill (it would then be mirrored into every vendor surface); no independence rule (cheaper, and the shape GHI #1091 records); a new `gz validate` scope instead of a test (a standing gate with its own flag, manpage row and registry entries). A ruling against independence removes that violation from REQ-0.35.0-17-01. Also ruled here: whether the checker reuses the block splitter and coverage check of `src/gzkit/content/retention.py` (recommended, read-only) or carries its own.
- **Q5. A rule and a directive conflict.** Moved with the cutover: the question and its ruling are in `OBPI-0.35.0-20` § Open Design Questions. Nothing is lifted out of the skill body in this OBPI.
- **Q6. Proposed split, and which run is the real run.** Authored as one brief, as assigned. It carries ten REQs over four surfaces, and it asks one pass to make the before-inventory and then remove the text the inventory protects, so no gate can fire between "inventory accepted" and "text removed". **Proposed:** two briefs. The first adds the inventory's before-state and the runtime serving, with each stage's procedure copied verbatim and the skill body untouched; nothing can be lost, and the operator attests the inventory. The second performs the cutover (REQ-04 and REQ-07 to REQ-10, Requirement 9) and is itself executed, from Stage 1, under the delivery the first one landed, which makes it the real run. The cost is one more checklist item and scorecard amendment on the ADR, and each stage's procedure loading twice between the two. If the brief stays whole, the real run can only be this OBPI's own Stages 3 to 5 re-entered after the cutover, with the first full run being the next operator-initiated OBPI, and GHI #1174 stays open until that run is cited.
  - **RULED 2026-10-04: split.** Asked "is brief 17 split in two?", the operator answered, verbatim: "A". This brief keeps the inventory and the runtime serving. `OBPI-0.35.0-20-pipeline-skill-cutover` carries the cutover as parent checklist item 20 (§ Intent amendment 2026-10-04 (2)). REQ numbers changed with the split. The text above uses the old ones: the former `-05` and `-06` are now `REQ-0.35.0-17-04` and `-05`; the former `-04` and `-07` to `-10` are `REQ-0.35.0-20-01` and `REQ-0.35.0-20-03` to `-06`; `REQ-0.35.0-17-06` and `-07` are new.
  - **CONFIRMED 2026-10-04: the six split details.** Each was the agent's choice when the split was written. Each was put to the operator on its own, with the alternatives, and the operator answered each, verbatim: "A". (1) The parent ADR's scorecard records the split as a State Anchor split adder, 16 + 4 = 20, and the baseline is not raised. (2) The three criteria the question did not name are kept: `REQ-0.35.0-20-02`, `REQ-0.35.0-17-06` and `REQ-0.35.0-17-07`. (3) The audit widening stays in `OBPI-0.35.0-20` and lands there before any text leaves the skill body. (4) This brief's criteria stay numbered 01 to 07, with the mapping above. (5) Q2 and Q5 stay in `OBPI-0.35.0-20`, and this brief gains a prerequisite that Q2 is ruled before this brief is planned, because Q2's option (c) changes the inventory this brief builds. (6) The parent ADR's delivery plan keeps item 17 at 2–3 engineering days and item 20 at 1–2, which divide the 3–5 that item 17 carried before the split.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary: § Decision item 13, "THE PIPELINE SKILL'S STAGE PROCEDURE IS SERVED BY THE RUNTIME, ONE STAGE AT A TIME", as quoted in full under § ADR Item.
- [ ] Parent ADR § Intent — the paragraph "AMENDED 2026-10-04": what the five repair assignments are, why this ADR carries them, and that none removes a control.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] GHI #1174 in full: its closure contract is the source of these requirements. One correction: it cites "checklist, item 4" of `ADR-0.13.0`; the quoted sentence is § Promotion Criteria item 4 (`ADR-0.13.0` lines 114-120). § Checklist item 4 is the Stage 4 attestation boundary.
- [ ] GHI #1091 and `docs/evals/compression-sweep-2026-09-24.md`: a rewrite with no condition-level accounting dropped 23 binding conditions. Requirements 2 to 5 exist because of it.
- [ ] `docs/design/adr/pool/ADR-pool.skill-runtime-authority-inversion.md`: the catalog-wide form of this finding, and its refusal of a shortening pass that leaves the skill as the authority.
- [ ] `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md` § Decision, § Promotion Criteria and `OBPI-0.13.0-05`.
- [ ] `docs/governance/context-phase-review-2026-10-04-evidence/README.md` finding 3 and proposal 7, and the campaign plan § Amendments 2026-10-04 (2).
- [ ] `.gzkit/chores/instructions-files-diet/proofs/pipeline-review-2026-09-19/README.md`: the earlier lift of six incident passages. It preserved text and declined to claim semantic equivalence, and it recorded the plan-mode contradiction Requirement 3 lists.
- [ ] OBPI-0.35.0-14 brief, § Retention Map Contract: the accounting form this inventory follows.
- [ ] OBPI-0.35.0-15 and OBPI-0.35.0-16 briefs as landed: the positions and the surface this OBPI delivers through.

**Prerequisites (check existence, STOP if missing):**

- [ ] `OBPI-0.35.0-16-next-command-for-position` is completed in the ledger, and with it `OBPI-0.35.0-15-pipeline-run-position`. This OBPI extends the surface they land and duplicates none of it. STOP if either is not completed.
- [ ] The operator's rulings on Q1, Q3 and Q4 are recorded in this brief (Q6 is ruled; Q2 and Q5 moved to OBPI-0.35.0-20), and the Allowed Paths, Verification and Demo are reconciled with them and with OBPI-16's landed surface (`uv run gz obpi validate --authored` on this brief passes after the reconcile).
- [ ] The operator's ruling on Q2 is recorded in `OBPI-0.35.0-20-pipeline-skill-cutover` § Open Design Questions. Its option (c) holds the incident history inside the inventory rows, which changes the § Control Inventory Contract this brief builds, so Q2 is ruled before this brief is planned (operator-ruled 2026-10-04, Q6 confirmation 5). STOP if it is not.
- [ ] Required path exists: `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, read whole, with its version and body digest recorded as the baseline
- [ ] Required path exists or is intentionally created in this OBPI: `data/obpi_pipeline_control_inventory.json`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `.gzkit/skills/gz-obpi-pipeline/SKILL.md` in full: the section structure, where each stage's procedure sits, the cross-stage sections after Stage 5, and which paragraphs are incident history carrying a binding sentence
- [ ] `src/gzkit/commands/obpi_stages.py` — the full-launch handoff printer and the verify, ceremony and sync stage runners: what each prints on entry today
- [ ] `src/gzkit/commands/obpi_cmd.py` — `obpi_pipeline_cmd`: the order of checks before a stage runner is called, read only
- [ ] `src/gzkit/pipeline_markers.py` — `pipeline_stage_output` and `pipeline_stage_labels`, read only, together with what OBPI-15 and OBPI-16 changed there
- [ ] `src/gzkit/governance/trust_audits/cli.py` — `_cli_alignment_sources`, `audit_skill_code_citations` and `_collect_skill_verb_refs`: each globs for the skill body file by name
- [ ] `src/gzkit/skills_mirror.py` and `src/gzkit/sync_surfaces.py` — how a skill's supporting files are mirrored and checked for parity, and the wheel's include block in `pyproject.toml`
- [ ] `src/gzkit/registries.py` and `data/config_registry.json` — the read seam and the ownership declaration a new registry needs
- [ ] `src/gzkit/content/retention.py` — the block splitter and coverage check, for the Q4 reuse decision
- [ ] The test modules that read the skill body for stage text, listed in `OBPI-0.35.0-20` § Allowed Paths: they pass unchanged in this OBPI (Requirement 9)
- [ ] `features/subagent_pipeline.feature` and its steps — fixture and step conventions
- [ ] `docs/user/manpages/obpi-pipeline.md` lines 33-34 ("thin alias") and lines 55 and 85, which still describe attestation as lane-dependent against the universal Gate 5 of ADR-0.0.36; the file is in scope, so the statements are corrected in this OBPI's docs pass
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
- [ ] Relevant docs updated: the pipeline manpage and the operator runbook

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/obpi_pipeline_stage_procedure.feature`, each scenario tagged with the REQ it proves (`@REQ-0.35.0-17-04`, `@REQ-0.35.0-17-05`) so Stage 3 can scope the run

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run -m unittest tests.governance.test_pipeline_control_inventory tests.test_pipeline_procedure
uv run -m unittest tests.commands.test_obpi_stages tests.commands.test_obpi_pipeline
uv run -m unittest tests.governance.test_cli_alignment_scope tests.governance.test_audit_skill_alignment_seam tests.governance.test_skill_code_citations
uv run -m unittest tests.test_obpi_skill_migration tests.skills.test_skill_surface_sync_justify tests.governance.test_skill_self_close_drift tests.governance.test_agent_contract_fold tests.governance.test_mandated_tier1_dispatch tests.test_skill_body_audit
uv run -m behave features/obpi_pipeline_stage_procedure.feature
uv run gz skill audit
uv run gz validate --cli-alignment --skill-alignment --distribution --wheel-path-literals --config-registry --req-kind-discipline
uv run gz cli audit
uv run mkdocs build --strict
```

## Demo

Both commands are self-contained and exit non-zero on a bad state. The first runs the checker over the committed inventory against what the runtime serves in this tree: the before-state reproduces the pinned baseline, every control is delivered at each stage it applies to, and the skill body still equals the pinned baseline. The second drives the runtime through every stage entry in a throwaway project, in sequence and through each `--from` value, and compares the procedure each entry received.

```bash
uv run -m unittest tests.governance.test_pipeline_control_inventory -v
uv run -m behave features/obpi_pipeline_stage_procedure.feature
```

The stage-entry command line itself is fixed by OBPI-0.35.0-16. When that brief has landed, this section gains the concrete invocation and its observed output for one stage, and the real run of Requirement 12 is recorded in Key Proof.

## Acceptance Criteria

<!-- REQ kinds per ADR-0.0.59; enforced by gz validate --req-kind-discipline. -->

- [ ] REQ-0.35.0-17-01 [BEHAVIOR]: Given an inventory, a baseline body, an invocation text, a served text per stage and a rationale record, when the checker runs, then it returns every violation the § Control Inventory Contract lists and not only the first, and it returns none for a complete inventory. Each violation kind is proven on a synthetic fixture by a case that fails when that check is removed.
- [ ] REQ-0.35.0-17-02 [BEHAVIOR]: Given the committed inventory and the baseline it pins, when the checker runs the before-state checks, then the blocks reproduce the baseline body digest, every block is fully covered, and no violation is returned. Removing one control row or one covered sentence from the inventory makes the check fail and name the uncovered text.
- [ ] REQ-0.35.0-17-03 [BEHAVIOR]: Given the committed inventory, when the checker runs against the invocation text and the procedure the runtime serves for each stage in this repository, then every control's delivered span is present at every position in its `applies_at`, every span equals its baseline quote unless the row declares a rewording with a reason, and no violation is returned. Deleting one control's text from a served procedure makes the check fail and name that control's id.
- [ ] REQ-0.35.0-17-04 [BEHAVIOR]: Given a pipeline run, when it enters a stage in sequence or through any `--from` value the parser registers, then the runtime's stage-entry output delivers that stage's procedure and no other stage's, and the procedure delivered through `--from` is byte-identical to the one delivered for the same stage in sequence.
- [ ] REQ-0.35.0-17-05 [BEHAVIOR]: Given a stage whose procedure is missing, unreadable, empty or not the bytes the runtime expects, when the run enters that stage, then the command exits non-zero, the stage is not entered, and the output names what failed, the rule it breaks and the command that recovers.
- [ ] REQ-0.35.0-17-06 [SUPPORT]: Each stage's procedure file is created in canon under the skill package, and the skill body is not edited: its digest equals the baseline the inventory pins. The skill version and `last_reviewed` move in the same edit, and the wheel copy and every enabled vendor mirror, supporting files included, are regenerated by the control-surface sync. `uv run gz skill audit` reports no mirror or asset finding for this skill. Witnessed by `artifact_edited` citing `.gzkit/skills/gz-obpi-pipeline/SKILL.md` + `gz validate --distribution`.
- [ ] REQ-0.35.0-17-07 [SUPPORT]: The pipeline manpage states what stage entry delivers, the refusal of Requirement 7 and its recovery, and that the skill body carries the same procedure until `OBPI-0.35.0-20` lands; it no longer states that attestation depends on lane. `docs/user/runbook.md` agrees with it. Witnessed by `artifact_edited` citing `docs/user/manpages/obpi-pipeline.md` + `gz validate --cli-alignment`.

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
