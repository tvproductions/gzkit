---
id: ADR-pool.harness-agnostic-plan-capture
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-pool.harness-aware-execution-modes
inspired_by: https://github.com/gsd-build/get-shit-done, https://github.com/github/spec-kit, https://github.com/obra/superpowers
---

# ADR-pool.harness-agnostic-plan-capture: Harness-Agnostic Plan Capture and Normalization

## Status

Pool

## Date

2026-04-14

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Establish `.gzkit/plans/` as the canonical, harness-agnostic storage surface
for OBPI construction-phase plans, backed by a Pydantic-validated schema with
a CLI verifier. Reduce `.claude/plans/` to a Claude Code adapter-written mirror
and provide operator-invoked capture adapters for harnesses that lack native
plan mode (Codex, Copilot). Eliminate the metadata-insertion kludge that
currently embeds OBPI identifiers inside free-form plan prose by elevating
them to schema frontmatter fields.

The current architecture conflates harness output with canonical source —
`.claude/plans/` is both what Claude Code emits and what `gz-obpi-pipeline`
reads as truth. Petname filenames and prose-embedded OBPI IDs are kludges
that only make sense inside Claude Code, and Codex and Copilot have no
answer at all because they lack native plan mode. This ADR scopes the
transition to a harness-agnostic plan layer grounded in deterministic Python,
matching gzkit's broader governance posture.

---

## Current State

### What already exists

- 19 petname plan files in `.claude/plans/` produced by Claude Code plan mode
- `gz plan audit` CLI verb with structural prerequisite checks
- `.claude/plans/.plan-audit-receipt-{OBPI-ID}.json` receipt contract
- `plan-audit-gate.py` hook blocks `ExitPlanMode` without a valid receipt
- `pipeline-router.py` hook routes PASS receipts into `gz-obpi-pipeline`
- `gz-plan-audit` skill conducts semantic alignment review
- `gz-obpi-pipeline` Stage 1 consumes the receipt + plan file to extract tasks

### What is missing

- No machine-readable plan schema — plans are free-form markdown
- Canonical storage lives in a Claude Code harness directory, not gzkit canon
- No adapter path for harnesses without native plan mode
- OBPI identity is embedded in plan prose via grep-matching, not structured
- No parser, no validator, no typed Pydantic model for plan content
- Claude Code's native plan mode output structure is undocumented upstream,
  so the current implicit format cannot be relied on as a contract

### Why now

`gz-design` dialogue (2026-04-13) surfaced three concrete failure modes in
the current design:

1. The metadata-insertion kludge (embedding OBPI IDs in prose) is a
   Claude-Code-specific workaround that does not survive the multi-harness
   expansion already scoped by `ADR-pool.harness-aware-execution-modes`.
2. Codex and Copilot expansion has no plan story at all — the current design
   assumes native plan mode exists, which is only true for Claude Code.
3. Claude Code's plan mode output format is undocumented upstream, so every
   consumer that reads plan files is building on sand. Any reliable plan
   layer has to be owned by gzkit, not inherited from a harness.

---

## Target Scope

### Canonical plan storage

- Location: `.gzkit/plans/OBPI-X.Y.Z-NN/plan-MM.md` (OBPI-scoped directory,
  sequential `plan-MM` index supports replans within a single OBPI)
- Gitignored vs. committed — open decision, depends on state doctrine
  resolution (see Open Decisions)
- OBPI-gated: capture only fires when an OBPI lock is held. Design-phase
  thinking lives in `gz-design` and produces ADR artifacts, not plans

### Plan schema (Pydantic)

- Schema file: `data/schemas/plan.schema.json`
- Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` in
  `src/gzkit/core/models.py`
- Frontmatter fields: `obpi_id`, `parent_adr`, `plan_index`, `lane`,
  `allowed_paths`, `verification_commands`, `constitution_check`,
  `task_type_mix`, `authored_by` (harness identity), `authored_at`
- Body format: YAML frontmatter + XML body, matching GSD's
  `sample-plan.md` fixture pattern
- Body structure:

  ```xml
  <objective>Plain-language objective tied to the OBPI brief.</objective>
  <tasks>
    <task type="mechanical">
      <name>...</name>
      <files>...</files>
      <action>...</action>
      <verify>...</verify>
      <done>...</done>
    </task>
    <task type="decision">
      <name>...</name>
      <evidence_expected>...</evidence_expected>
      <decision_framework>...</decision_framework>
      <outcome_space>...</outcome_space>
    </task>
  </tasks>
  <retained_plan harness="claude-code|codex|copilot" format="petname-md">
    <!-- verbatim original plan prose, preserved for reasoning continuity -->
  </retained_plan>
  ```

### Task type taxonomy

Two task types, one plan model, one validator:

- **Mechanical tasks**: code edits, file creates, test runs. Required
  fields: `name`, `files`, `action`, `verify`, `done`. The `verify` field
  holds an executable check; the `done` field holds a truth predicate.
  Maps to GSD's baseline task model.
- **Decision tasks**: investigations, comparisons, evaluations. Required
  fields: `name`, `evidence_expected`, `decision_framework`,
  `outcome_space`. No `verify` predicate because the output is a
  reasoned decision, not a mechanical check. Evidence is attestable
  at the Stage 4 ceremony, not verifiable at Stage 3.

The taxonomy is motivated by concrete prior work: three of the 19 existing
petname plans (ADR-0.25.0 pattern-absorption OBPIs) are decision tasks whose
central step is "compare airlineops vs gzkit and record Absorb/Confirm/Exclude."
Forcing those into a mechanical task schema produces contrived verify
predicates or splits decision work into fake mechanical chains. Two schemas
recognizes the distinction natively.

### Retention via wrap

Every plan written by a harness adapter MUST include a `<retained_plan>`
section containing the verbatim original prose output from the harness's
native plan mode (or, for Codex/Copilot, the operator-provided prose at
capture time). This reconciles the earlier design tension between
extract-and-normalize (lossy) and wrap-and-attach (unstructured): the
canonical `<tasks>` section is the machine-readable execution contract,
and `<retained_plan>` is the reasoning record preserved verbatim. Both
live in the same file. Neither is dropped.

The `harness` attribute records provenance. The `format` attribute records
the original format (typically `petname-md` for Claude Code). The retention
contract is enforced by the validator: plans with `authored_by` naming a
harness with native plan mode must have a non-empty `<retained_plan>` child.

### Parser and validator

- Body parser: `lxml` preferred, stdlib `xml.etree.ElementTree` fallback
- Pydantic models wrap parsed elements for typed downstream consumption
- CLI: `gz plan verify` (new subcommand under existing `gz plan {create, audit}`)
  runs parser + schema validation, verifies task-type schemas match declared
  type, confirms `<retained_plan>` presence where required, writes verdict
  to `.plan-audit-receipt.json`
- Canonical fixture: `tests/fixtures/plan-canonical.md` teaches the form
  (parallels GSD's `sdk/test-fixtures/sample-plan.md`)

### Harness adapters

- **Claude Code (write-through)**: updated `gz-plan-write` skill teaches
  Claude to emit the full canonical form directly, including its own
  `<retained_plan>` containing its native prose output. The skill provides
  the template and the writing discipline; the hook enforces schema
  compliance via `gz plan verify` on `ExitPlanMode`. The petname file
  remains in `.claude/plans/` as harness-local output; canon lives in
  `.gzkit/plans/`.
- **Codex / Copilot (operator-invoked capture)**: new `gz plan capture`
  verb reads harness prose from stdin, file, or transcript blob and
  produces canonical form via deterministic parsing where possible plus
  operator confirmation where not. Original prose is preserved verbatim
  inside `<retained_plan>`. Same output schema as the Claude Code path.

Both adapters produce the same canonical form. The schema is the contract;
the authoring path is the variable.

### Receipt contract update

- `.plan-audit-receipt.json` continues to exist but points at canonical
  path `.gzkit/plans/OBPI-X.Y.Z-NN/plan-MM.md` rather than petname
- Existing consumers (`plan-audit-gate.py`, `pipeline-router.py`,
  `gz-obpi-pipeline` Stage 1) updated to read canonical paths
- Hook-level backward compatibility for one release cycle — old receipts
  pointing at petname paths resolve via petname → canonical lookup table
  built during migration

---

## Design Referents

Three prior-art projects were evaluated during `gz-design` dialogue. The
decision is to adopt GSD's architecture as primary, Spec Kit's constitution
check pattern as secondary, and Superpowers' writing discipline as tertiary.
None is adopted wholesale; each contributes a specific capability.

### Primary: GSD (Get Shit Done)

- Repository: <https://github.com/gsd-build/get-shit-done>
- What we take: frontmatter + typed parser + CLI validator architecture.
  GSD is the only prior art with a schema-backed plan layer and a
  `gsd-tools verify plan-structure` command. It is the only one that does
  not drift silently — the parser is the contract.
- What we take specifically: the YAML frontmatter + XML body pattern. The
  earlier `gz-design` dialogue initially dismissed XML-in-markdown as
  foreign to a Python/Pydantic/markdown-first ecosystem, but reversed on
  reflection: XML handles typed heterogeneous children (mechanical vs
  decision tasks) more cleanly than YAML discriminated unions, and
  markdown+XML is a mature pattern with `lxml` and stdlib parsers
  available out of the box.
- Reference fixture: `sdk/test-fixtures/sample-plan.md`
- Reference parser: `sdk/src/plan-parser.ts` (gzkit reimplementation in
  Python with Pydantic models)

### Secondary: Spec Kit

- Repository: <https://github.com/github/spec-kit>
- What we take: the constitution check gate pattern. Plans must pass a
  project-level check before execution. Spec Kit places this check
  before research and again after design; gzkit already has the adjacent
  machinery (`gz plan audit`, Gate 5 runbook-code covenant, plan-audit
  receipt). Spec Kit's pattern tells us where in the lifecycle the gate
  fires and what artifact it produces.
- Reference template: `templates/plan-template.md`
- What we explicitly do not take: Spec Kit's separation of plan and
  tasks into two files (`plan.md` + `tasks.md`). gzkit plans carry both
  design context and task list in a single file, because the OBPI brief
  is the separate design-time artifact, and the plan is the execution
  contract.

### Tertiary: Superpowers

- Repository: <https://github.com/obra/superpowers>
- What we take: writing discipline invariants. No placeholders, no
  "similar to task N", exact commands, expected output for every step.
  Red-Green-Refactor rhythm explicit in step granularity. These are
  authorial rules enforced by the `gz-plan-write` skill and, where
  mechanizable, by the validator.
- Reference skill: `skills/writing-plans/SKILL.md`
- What we explicitly do not take: Superpowers' architecture. It has
  none — no schema, no parser, no validator. Superpowers is a writing
  discipline that depends on author cooperation. gzkit requires
  mechanical enforcement, which is why GSD is the architectural
  referent and Superpowers is the writing-rules referent.

---

## Open Decisions

These are decisions the pool ADR deliberately does not resolve. They
depend on state doctrine and harness-aware-execution-modes locking first.

### 1. Enforcement moment

Three candidates for where and when schema validation blocks a
non-conforming plan:

- **Hook-time rejection**: existing pattern. `plan-audit-gate.py` invokes
  `gz plan verify` on `ExitPlanMode` and blocks if schema check fails.
  UX weakness: operator has already invested time in plan-mode dialogue
  before rejection fires.
- **In-plan-mode self-validation**: Claude Code invokes `gz plan verify`
  as a tool call during plan mode, iterates on schema compliance before
  requesting exit. Requires Claude Code to support CLI invocation from
  within plan mode, which is unclear upstream and may not be available.
- **Deterministic transform step**: hook reads the petname, produces
  canonical form via parsing, preserves original in `<retained_plan>`.
  Cheap to implement, matches the Codex/Copilot path, weaker type
  guarantees because extraction may miss structure the author intended.

The retain-via-wrap model softens the "lossy extraction" objection to
the transform path because the raw prose survives inside `<retained_plan>`
regardless. The cross-harness answer probably differs: write-through
on Claude Code if plan-mode CLI support is confirmed, transform-and-wrap
on harnesses that cannot self-validate.

### 2. Cross-harness adapter parity

Claude Code and Codex/Copilot reach the canonical form through different
mechanisms — write-through on Claude Code via the `gz-plan-write` skill,
operator-invoked `gz plan capture` on the others. This is not a defect.
It is the cost of "cooperate with native provisions where they exist."
Both mechanisms produce the same Pydantic-validated output. The schema
is the contract, the authoring path is the variable.

The open question is whether to formalize the adapter interface — e.g.,
define a `PlanAdapter` protocol in `core/plan_adapter.py` that every
harness adapter implements — or leave the two paths as independent
implementations with a shared schema target. The former is cleaner
architecturally; the latter is less code to maintain with only two
adapters in scope.

### 3. L1 vs L2 placement of plan artifacts

Depends on state doctrine lock. Two candidates:

- **Layer 1 (canon, committed to git)**: plans are canonical artifacts
  like OBPI briefs and ADRs. `.gzkit/plans/` is committed. Plans survive
  repo clone and become part of the governance record. The existing
  practice of committing `.claude/plans/` is de facto L1 already.
- **Layer 2 (ledger event + artifact cache)**: plan capture emits a
  `plan_captured` ledger event; the plan file is a derived/cached
  artifact rebuildable from the event. `.gzkit/plans/` is gitignored.
  Cleaner state doctrine but loses the ability to review plans during
  code review on the PR diff.

The pool ADR does not resolve this. State doctrine resolution is
prerequisite.

### 4. OBPI brief linkage

Three candidates for how the OBPI brief references its plan:

- **Receipt-mediated only (current)**: `.plan-audit-receipt.json` holds
  the linkage; the brief has no field for plan path. Minimal schema
  change; linkage is indirect.
- **`plan_ref:` frontmatter field**: the OBPI brief gains a required
  `plan_ref:` field pointing at `.gzkit/plans/OBPI-.../plan-MM.md`.
  Direct linkage; requires brief schema migration for existing briefs.
- **Ledger event linkage**: a `plan_captured` event in the ledger
  binds OBPI-id → plan path. Discovery requires ledger traversal but
  no schema change to briefs. Matches the L2 option above.

The choice depends on L1/L2 resolution in open decision 3.

### 5. Migration path for existing petname plans

The 19 existing files in `.claude/plans/` are all pre-canonical. Two
migration candidates:

- **One-time backfill**: a `gz plan migrate` verb reads each petname,
  matches it to an OBPI, and produces canonical form with the original
  prose in `<retained_plan>`. Plans that cannot be matched (or are for
  completed OBPIs) are archived to `.gzkit/plans/archive/` with
  `status=archived` frontmatter.
- **New-format-only going forward**: canonical form is required for
  new plans only; petname files stay untouched until their OBPIs
  complete. Simpler migration but leaves two formats live for the
  duration of in-flight OBPIs.

### 6. Task-type taxonomy scope

The two-type taxonomy (mechanical / decision) is minimal. Future
extensions are possible — e.g., a `coordination` type for multi-agent
handoff tasks, a `verification` type for Stage 3-style checks. The
pool ADR declines to pre-scope these. Two types cover the observed
work; additional types can be added via minor schema version bumps
without breaking the parser.

---

## Dependencies

- **Blocks on**:
  - `ADR-pool.harness-aware-execution-modes` — must be promoted first.
    This ADR is a concrete instance of that mode architecture and
    depends on the mode detection and adapter boundaries it establishes.
  - State doctrine resolution (already in ADR-0.0.9) must answer
    whether plans are Layer 1 or Layer 2 before `.gzkit/plans/`
    placement is final. The ADR is in place; the open question is
    applying it to plan artifacts specifically.
- **Blocked by**: None
- **Organizes**:
  - No sub-ADRs at this time. The plan capture surface is scoped as a
    single ADR when promoted. Plausibly splits into two ADRs during
    promotion — one for schema + CLI + validator, one for harness
    adapters — if scope becomes too large for a single Heavy lane ADR.
- **Related**:
  - `ADR-pool.vendor-alignment-claude-code` — the `gz-plan-write` skill
    update is a Claude Code vendor alignment concern
  - `ADR-pool.vendor-alignment-codex` — the `gz plan capture` verb is
    a Codex vendor alignment concern
  - `ADR-pool.vendor-alignment-copilot` — same for Copilot
  - `ADR-0.12.0-obpi-pipeline-enforcement-parity` — the plan-audit-gate
    and pipeline-router hooks are current consumers of the plan path
    contract

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. `ADR-pool.harness-aware-execution-modes` is promoted and the mode
   architecture is locked. The plan capture adapters follow the mode
   split established there.
2. State doctrine has explicitly placed plan artifacts in Layer 1 or
   Layer 2, resolving open decision 3.
3. Enforcement moment is decided (open decision 1), at least for Claude
   Code — the cross-harness answer may differ.
4. A canonical fixture file exists at `tests/fixtures/plan-canonical.md`
   that the parser and validator regression-test against. Writing the
   fixture is the forcing function for resolving schema details.
5. Human assigns a SemVer ADR ID for active implementation.

---

## Reference

- [GSD (Get Shit Done) — plan parser and types](https://github.com/gsd-build/get-shit-done/blob/main/sdk/src/plan-parser.ts) — primary architectural referent
- [GSD — sample-plan.md fixture](https://github.com/gsd-build/get-shit-done/blob/main/sdk/test-fixtures/sample-plan.md) — canonical fixture pattern
- [Spec Kit — plan template](https://github.com/github/spec-kit/blob/main/templates/plan-template.md) — constitution check gate pattern
- [Spec Kit — plan command](https://github.com/github/spec-kit/blob/main/templates/commands/plan.md)
- [Superpowers — writing-plans skill](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md) — writing discipline invariants
- [ADR-pool.harness-aware-execution-modes](ADR-pool.harness-aware-execution-modes.md) — parent mode architecture
- [ADR-0.0.9 State Doctrine](../foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md) — L1/L2 placement precedent

---

## Notes

- The `gz-design` dialogue that produced this pool ADR (2026-04-13 to
  2026-04-14) made three reversals worth recording for promotion-time
  review:
  1. Initial framing proposed B (extend the parent with a plan-capture
     section), moved to C (separate pool ADR with explicit dependency
     on `harness-aware-execution-modes`). C was chosen because the
     parent's mode architecture decision stands on its own and should
     not be bloated with instance-level detail.
  2. Initial framing dismissed GSD's XML body syntax as foreign to a
     Python/markdown-first ecosystem. Reversed: XML handles typed
     heterogeneous task children more cleanly than YAML discriminated
     unions, and Python's `lxml` and stdlib parsers handle it
     out of the box. GSD's syntax choice is deliberate and adopted.
  3. Initial framing offered extract-and-normalize vs. wrap-and-attach
     as exclusive alternatives. Reversed: the retain-via-wrap model
     does both — write-through schema AND preserved original prose in
     `<retained_plan>` — in the same file. Neither is dropped, and the
     dichotomy dissolves.
- The three pushback points integrated as open decisions 1, 2, and 6
  came from stress-testing the write-through model during the same
  dialogue. Integrating them prevents the pool ADR from being an
  advocacy document and makes it a real design record with named
  uncertainty.
- Heavy lane classification: this ADR introduces a new CLI subcommand
  (`gz plan verify`) and a new CLI verb (`gz plan capture`), a new
  data schema (`plan.schema.json` + Pydantic models in `core/models.py`),
  and changes the contract of two existing hooks (`plan-audit-gate.py`,
  `pipeline-router.py`) and one existing skill (`gz-plan-audit` or
  its successor). This is not a lite refactor. It is a foundational
  plan-layer change with a multi-harness adapter surface.
- The existing 19 petname plans in `.claude/plans/` are architecturally
  load-bearing for in-flight OBPIs (ADR-0.25.0 and related). Migration
  strategy is deferred to open decision 5 but cannot ignore that the
  current plans are actively consumed by `gz-obpi-pipeline` and must
  not be broken during the transition.
