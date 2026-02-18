# Copilot Briefs (GovZero v6)
Status: Active
Last reviewed: 2026-02-04

> **Architecture context added 2026-02-04:** All briefs now require reading
> `docs/design/architecture/system-manifest.md` and `config/architecture.json` before
> implementation to ensure understanding of bounded contexts, contracts, and invariants.

This file contains two briefing templates:

- ✴️ Lite OBPI Brief — default for internal changes (unit + smoke ≤60s).
- 🛡️ Heavy Contract Brief — escalate only when a public CLI/API/schema contract changes (adds Docs + BDD).

## Work Breakdown Structure Context

Each OBPI brief is a **Level 2 WBS element** that elaborates one item from the parent ADR's
OBPI Decomposition table (Level 1 WBS).

> **OBPI Etymology:** "One Brief Per Item" — where the "Item" is the OBPI entry in the parent
> ADR's decomposition table (recursive/self-referential). The Level 1 WBS defines *what* work
> exists; this brief defines *how* to deliver it.

**WBS Hierarchy:**

```text
ADR-X.Y.Z (Decision)
  └── OBPI Decomposition Table (Level 1 WBS — "what")
        ├── OBPI-X.Y.Z-01 Brief (Level 2 WBS — "how")
        ├── OBPI-X.Y.Z-02 Brief (Level 2 WBS — "how")
        └── ...
```

**Guardrail:** Each brief targets exactly one OBPI entry. If scope grows, create additional
OBPI entries in the parent ADR's decomposition table first, then create corresponding briefs.

## Discovery Index (read first)

**Before starting work, read:** `.github/discovery-index.json`

This file provides:

- Repository structure (paths, patterns, common files)
- Governance pointers (policies, instructions, agent contract)
- Quality gates definitions (Lite vs Heavy)
- Verification commands (how to run tests/lint/gates)
- Discovery and completion checklists
- Key doctrines and prohibitions

## Discovery Phase

Before planning or execution, read:

- `.github/discovery-index.json`
- the parent ADR for this brief
- any referenced instructions files

Use the `discovery_checklist` in discovery-index.json to structure your evaluation.

## System Architecture Context (MANDATORY)

**Before any implementation, read these architecture documents:**

1. `docs/design/architecture/system-manifest.md` — Human-readable architecture overview
2. `config/architecture.json` — Machine-readable companion

These documents establish:

- **Bounded contexts** — what each context owns and does NOT own
- **Port protocols** — ResolverPort, LoaderPort, DatasetPort contracts
- **Canonical formats** — period formats per cadence (quarterly, monthly, AIRAC, etc.)
- **Key invariants** — single-active contracts, determinism guarantees
- **Responsibility boundaries** — Librarian vs Warehouse vs Registrar

**Why this matters:** Each OBPI must operate within the larger system architecture.
Understanding the bounded contexts and responsibility boundaries prevents scope creep
and ensures implementations don't violate established contracts.

**STOP if you cannot locate these documents or do not understand:**

- Which bounded context your OBPI operates in
- What canonical formats apply to your work
- Which invariants must be preserved

## Policy references

This brief template defers to the canonical repo policies (GovZero v6):

- `.github/copilot-instructions.md` — repo-wide agent guidance and rituals
- `.github/instructions/tests.instructions.md` — canonical tests policy
- `.github/instructions/*.instructions.md` — scoped guardrails (tests, CLI, warehouse, cross-platform)

> SemVer ADR workflow
> Each brief implements or updates exactly one ADR-{semver} checklist item.
> Version movement is human-gated: the ADR flips to **Completed** when
> applicable gates pass and the OBPI brief is completed.
>
> **Quality Gates:**
>
> - **Lite:** Gate 1 (ADR) + Gate 2 (TDD) → brief completion
> - **Heavy:** Gates 1-4 for implementation → Gate 5 required to complete the
>   brief
> - **Gate 5:** Human attestation via ADR closeout ceremony; present
>   paths/commands only (see `docs/governance/GovZero/audit-protocol.md`)
> - **Gate definitions:** `docs/governance/GovZero/charter.md`
>
> **Note:** Foundation/0.0.x ADRs do not use the ADR closeout ceremony.

## Agent Mode (All Lanes)

This brief is read and acted upon by AI agents (Copilot, Claude, Codex). Agents operate under these constraints:

**Role & Authority:**

- Agent is **responsible for all work** — do not defer, rationalize incompleteness, or stop prematurely.
- Agent owns code quality, documentation alignment, and test coverage.
- Agent must complete all applicable gates fully in one session (Lite or Heavy); never leave TODOs or placeholders.

**Execution Mode:**

- **Fail-closed:** If a prerequisite is missing, STOP and enumerate blockers (see BLOCKERS output shape below).
- **No speculation:** Never invent files, config values, test data, or internal designs; only work with actual repository state.
- **Complete all steps:** If a feature requires tests, docs, BDD, or examples, implement them ALL immediately—not in separate future tasks.

**Output Discipline:**

- Use canonical output shapes (BLOCKERS, PLAN, EVIDENCE) to signal status.
- All terminal/CLI output MUST be shown in full; do not truncate or paraphrase.
- When a validation step fails (lint, test, type check), fix it immediately—code quality is shared responsibility.

**Context & Prompt Caching:**

- Discovery phase and context reads must be cached; do not re-read stable files on each turn.
- On subsequent turns, reuse cached context; only refresh if brief or codebase changed.

## Response Format & Canonical Output Shapes (All Lanes)

### BLOCKERS (If Work Cannot Proceed)

Stop execution and emit this shape when a prerequisite is missing:

```text
## BLOCKERS

1. Missing prerequisite: `{exact file path or config key}`
   - Current state: [exists | missing | misconfigured]
   - Unblock command: `{exact command to check or create}`

2. [Additional blocker...]

**Action Required:** Agent cannot proceed until all blockers resolved by human or prior task.
```

### PLAN (Lite Lane, Before Implementation)

For Lite briefs only, emit micro-plan before code changes:

```text
## Implementation Plan (Lite)

**Scope:** {N} files, {M} test additions

**Step-by-step (bounded, reversible):**

1. [What] File: `{path}` — [Why] Modifying {module}, adding {N} lines
2. [What] File: `{path}` — [Why] Adding {N} test cases
3. [Validation] Run: `{verification command}` — Expect {expected output}

**Rollback:** Changes are isolated; revert files {paths} to undo.

**Gate readiness:** After completion, Gates 1-2 will be evaluated via {commands}.
```

### EVIDENCE (Completion Proof)

When gates are passing, emit this shape:

```text
## OBPI Completion Evidence

**Date:** YYYY-MM-DD

**Gate 1 (ADR):**
- ✓ Intent recorded: OBPI-X.Y.Z-NN in ADR-X.Y.Z

**Gate 2 (TDD) — Lite:**
- ✓ Tests pass: {N} tests, 0 failures
  uv run -m unittest -q tests.test_{module}
  # Output: Ran {N} tests in X.XXs — OK

- ✓ Coverage: {X%} ≥ 40% minimum
  uv run coverage report
  # Output: TOTAL ... {X}%

**Code Quality:**
- ✓ Lint: `uv run ruff check .` — OK
- ✓ Format: `uv run ruff format .` — no changes
- ✓ Type check: `uvx ty check .` — OK

**Changed files:** {list of 3-5 file paths}

**OBPI Status:** ✓ **COMPLETED** — All gates green.
```

### Standard Response Format (All Lanes)

Use this structure in agent responses:

- Outcome: 1-2 sentences.
- Changes: list files/areas touched.
- Tests: commands run + results; if not run, say `Not run (reason)`.
- Blockers: explicit list or `None`.
- Questions: ask one at a time, only if blocked.

## Assumptions, Non-Goals, Questions (All Lanes)

Capture these in the brief:

- Assumptions to confirm or reject.
- Non-goals (explicit exclusions).
- Open questions (single question if blocked; otherwise `none`).

## Prompt Structure (All Lanes)

Use clear sectioning and ordering to reduce ambiguity:

- **Identity/Role:** Who the agent is and the goal.
- **Instructions:** Requirements, constraints, forbidden actions.
- **Examples (optional):** Input/output pairs using XML tags for clarity.
- **Context:** Relevant files, config keys, data excerpts; keep variable
  context near the end to align with prompt caching and context window
  limits.

Use Markdown headings for structure and XML tags to delimit examples and
context blocks.

## ✴️ COPILOT BRIEF — LITE (OBPI DEFAULT)

### TITLE (Lite)

`imperative, short` — matches the ADR checklist item slug.

### ADR ITEM (Lite) — Level 1 WBS Reference

- Source ADR: `docs/design/adr/ADR-X.Y.Z-slug.md`
- OBPI Entry (Level 1 WBS): `OBPI-X.Y.Z-NN — "<specification summary from decomposition table>"`

### ADR ALIGNMENT — MANDATORY BEFORE PLANNING

**This section MUST be completed before any planning or implementation.**
**Read the parent ADR's `Agent Context Frame` section, then complete:**

1. **Critical Constraint** (copy from ADR, then restate in your own words):
   > ADR states: "{copy the Critical Constraint from parent ADR}"
   >
   > In my own words: "{agent restates what this means for this OBPI}"

2. **Integration Points** for this OBPI (from ADR's Integration Points, filtered to this OBPI):
   > This OBPI must integrate with: `{specific paths/modules this OBPI works with}`

3. **Anti-Pattern** for this OBPI (from ADR's Anti-Pattern Warning, made specific):
   > A failed implementation would: "{describe what wrong looks like for THIS OBPI}"

4. **Alignment Check** — does this OBPI's objective align with the constraint?
   > - [ ] **YES** — Proceed. Reasoning: "{why this OBPI supports the constraint}"
   > - [ ] **BLOCKER** — Misalignment detected: "{description}"

**STOP if you cannot complete this section from the ADR.**
**STOP if the anti-pattern describes what you were about to do.**

### ARCHITECTURAL CHECKPOINT (Lite — MANDATORY BEFORE CODE)

**Complete this section BEFORE writing any code:**

```text
## Architectural Checkpoint

**Bounded Context:** [Discovery | Planning | Acquisition | Ingestion | Validation | Reporting]

**I am working in the ______ context, which:**
- OWNS: [list what this context owns, from system-manifest.md]
- DOES NOT OWN: [list what this context does NOT own]

**Invariants that apply to this work:**
- [ ] Single-active HOT contract (if contract work)
- [ ] Single-active COLD contract (if contract work)
- [ ] Adapter delegation rule (if adapter work)
- [ ] Manifest determinism (if manifest work)
- [ ] None of the above apply

**Canonical format for this dataset:** [YYYY-Qn | YYYY-MM | YYCC | YYYY | STATIC | N/A]

**I will DELEGATE to:** [list existing modules I will import from and delegate to]
**I will IMPLEMENT:** [list only the thin facade/protocol compliance — should be minimal]

**STOP CONDITIONS (check before proceeding):**
- [ ] I CAN identify my bounded context
- [ ] I CAN find the module(s) to delegate to (or delegation N/A)
- [ ] I am NOT writing >50 lines of business logic
```

**If any STOP condition fails, emit BLOCKERS and ask for human guidance.**

### OBJECTIVE (Lite)

- `"<OBPI specification summary — the deliverable this brief implements>"`

### ROLE — MANDATORY

**Agent Identity:** {specific role from parent ADR's Agent Context Frame, e.g., "Migration implementer",
"Feature developer", "Refactoring architect"}

**Success Behavior:** {what the agent should DO to satisfy the ADR's Critical Constraint}

**Failure Behavior:** {what the agent should AVOID — derived from ADR's Anti-Pattern Warning}

### ASSUMPTIONS (Lite)

- `...`

### NON-GOALS (Lite)

- `...`

### OPEN QUESTION (Lite)

- `none` (or a single question)

### CHANGE IMPACT DECLARATION (Lite — MANDATORY)

**Does this brief change CLI/API/schema/error messages (external contract)?**

- [ ] **NO** — Internal-only changes (code, tests, config). Proceed with Lite lane.
- [ ] **YES** — External contract changes detected. **ESCALATE TO HEAVY** (stop here, reclassify parent ADR OBPI as Heavy).

If YES, create a new Lite OBPI for internal code changes + a separate Heavy OBPI for contract surface changes.

### LANE (Lite)

Lite — ADR note + stdlib unittest + smoke (≤60s). Escalate to Heavy if a CLI/API/schema contract changes.

### ATTESTATION REMINDER (Lite — MANDATORY CHECK)

**Before marking this OBPI as Completed, verify the parent ADR lane:**

- [ ] **Parent ADR is Lite** → Agent may self-close after presenting evidence
- [ ] **Parent ADR is Heavy/Foundation (0.0.x)** → **STOP — Human attestation required**

> **Lane Inheritance Rule:** An OBPI within a Heavy or Foundation ADR inherits the parent's
> attestation rigor, regardless of this OBPI's own lane. Lite lane work ≠ no human oversight.
>
> See `AGENTS.md § OBPI Acceptance Protocol` for ceremony steps.

### ALLOWED PATHS (Lite)

- `explicit repo paths`

### DENIED PATHS (Lite)

- CI files, lockfiles, new dependencies
- Unlisted `src/**`, `docs/**`, or config outside allowed paths

### ANTI-HALLUCINATION CLAUSE (Lite — MANDATORY)

Agent MUST conform to these constraints:

- **No invented files:** Only edit files listed in ALLOWED PATHS; never create undeclared files.
- **No invented config:** Do not assume config keys exist; verify in `config/settings.json` or `config/schema.py`.
- **No invented data:** Do not reference test data, fixtures, or datasets not present in `fixtures/**` or `data/**`.
- **No placeholder code:** Never commit `TODO`, `FIXME`, `@skip`, or incomplete test/function implementations.
- **No private/stashed work:** Work must be complete and visible; no agent-only staging or ledger hiding.

If an assumption is questioned or a file/config is missing, STOP and emit a BLOCKERS output shape.

### REQUIREMENTS (FAIL-CLOSED — Lite)

1. `expected behavior or invariant`
1. `tests or guards to add`

> STOP-on-BLOCKERS: if a prerequisite is missing, print a BLOCKERS list with exact JSON paths/commands.

### EDGE CASES (Lite)

- `edge case to handle/test`

### CONTEXT INPUTS (Lite)

- `relevant files / config keys / data excerpts`

### EXAMPLES (Lite)

- `<example_input>...</example_input>`
- `<example_output>...</example_output>`

### LITE-LANE MICRO-PLAN (Lite — REQUIRED BEFORE CODE CHANGES)

Before implementation, emit the PLAN output shape (see Response Format section above) that lists:

1. **Scope:** How many files? How many tests?
2. **Step-by-step:** Each file modification and why (e.g., "Add 3 test cases for error handling")
3. **Validation:** Exact commands to run (copy from QUALITY GATES section below)
4. **Rollback:** Which files can be reverted to undo?
5. **Gate readiness:** Which gates will be evaluated after completion?

This plan MUST be presented and acknowledged (or refined) **before any code changes are made**.
If the plan is questioned or modified, update it and re-present.

### DISCOVERY CHECKLIST (Lite — complete before implementation)

**Architecture (MANDATORY — read once, understand system context):**

- [ ] `docs/design/architecture/system-manifest.md` — bounded contexts, contracts, invariants
- [ ] `config/architecture.json` — machine-readable architecture manifest

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure and verification commands
- [ ] `.github/copilot-instructions.md` — repo-wide rules
- [ ] `AGENTS.md` — agent operating contract
- [ ] `.github/instructions/{relevant}.instructions.md` — domain-specific rules (if applicable)

**Context:**

- [ ] Parent ADR: `docs/design/adr/ADR-X.Y.Z-slug.md` — understand rationale and bigger picture

**Prerequisites (check existence, STOP if missing):**

- [ ] Registry entry: `data/data_sources.json::{key}` (if dataset-related)
- [ ] Config setting: `config/settings.json::{path}` (if config-related)
- [ ] Config schema: `src/airlineops/config/schema.py` (if schema change needed)
- [ ] Calendar definition: `config/calendars.json::{calendar}` (if period-related)

**Existing Code (understand current state):**

- [ ] Implementation: `{allowed_path}` — what exists now?
- [ ] Tests: `tests/test_{module}.py` — current coverage?
- [ ] Fixtures: `fixtures/{module}/` — test data available?

**Templates/Examples (patterns to follow):**

- [ ] Similar module: `{example_path}` (if applicable)
- [ ] Test patterns: `tests/test_{similar}.py` (for test style)

**STOP if any prerequisite is missing** — list exact BLOCKERS with file paths and commands to unblock.

### QUALITY GATES (Lite)

#### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief (Level 2 WBS)
- [ ] Parent ADR OBPI entry referenced (Level 1 WBS linkage)

#### Gate 2: TDD

- [ ] Unit tests written for new/changed behavior
- [ ] Tests pass: `uv run -m unittest -q tests.test_{module}`
- [ ] All tests pass: `uv run -m unittest -q`
- [ ] Coverage ≥40%: `uv run coverage run -m unittest discover -s tests -t .`
  and `uv run coverage report --fail-under=40`

#### Code Quality

- [ ] Lint clean: `uv run ruff check . --fix`
- [ ] Format clean: `uv run ruff format .`
- [ ] Type check clean: `uvx ty check . --exclude 'features/**'`

### COMPLETION CHECKLIST (Lite)

Use `completion_checklist.{lane}` from `.github/discovery-index.json`
as the baseline for this brief.

Item-specific gates and commands (if any) are listed below.

#### Before marking OBPI completed

- [ ] **Gate 1 (ADR):** ✓ Intent recorded in brief
- [ ] **Gate 2 (TDD):** ✓ Unit tests pass (N tests, 0 failures)
- [ ] **Code Quality:** ✓ Lint, format, type checks clean
- [ ] **Coverage:** ✓ Coverage ≥40% maintained
- [ ] **Lane Inheritance Check:** ✓ Parent ADR lane verified (if Heavy/Foundation → human attestation required)
- [ ] **OBPI Completion:** Record evidence in brief with gate status and test output

#### Evidence to capture

```markdown
## OBPI Completion (YYYY-MM-DD)

**Quality Gates Evidence:**

1. **Gate 1 (ADR):** Intent recorded in OBPI-X.Y.Z-NN; part of ADR-X.Y.Z

2. **Gate 2 (TDD):** ✓ PASSED — {N} tests pass, 0 failures

   ```bash
   $ uv run -m unittest -v
   ...
   Ran {N} tests in {X.XX}s
   OK
   ```

**OBPI Status:** ✓ **COMPLETED** — All applicable gates green; changes tested and verified.

**Brief Status:** Completed (YYYY-MM-DD)

**Note:** Gate 5 attestation is human-only and applies to Heavy lane closeout
per `docs/governance/GovZero/charter.md` and
`docs/governance/GovZero/audit-protocol.md`.

### ACCEPTANCE (Lite)

- Imports pass; smoke green; artifacts (if any) captured.
- No edits outside allowed paths; governance instructions respected.
- Tracking issue / ADR link noted if applicable.

---

## Permitted Status Values (Canonical)

### ADR Statuses

| Status | Meaning |
|--------|---------|
| **Pool** | Planned, awaiting prioritization (pool/ directory ONLY) |
| **Draft** | Being authored, not ready for review |
| **Proposed** | Submitted for review |
| **Accepted** | Approved, implementation may begin |
| **Completed** | Implementation finished, Gate 5 attestation received |
| **Validated** | Post-attestation audit completed (Phase 2) |
| **Superseded** | Replaced by newer ADR |
| **Abandoned** | Work stopped, will not be completed |

**Pool constraint:** ADRs in `docs/design/adr/pool/` may ONLY have status `Pool`. All other
statuses require full ADR folder structure in `adr-X.Y.x/`.

### OBPI Statuses

| Status | Meaning |
|--------|---------|
| **Accepted** | Brief accepted, work may begin |
| **Completed** | All applicable gates pass; for Heavy includes attestation |

**Any other status is a governance violation.**

---

## 🛡️ COPILOT BRIEF — HEAVY (EXTERNAL CONTRACT)

### TITLE (Heavy)

`imperative, short` — reflects exposed contract change.

### ADR ITEM (Heavy) — Level 1 WBS Reference

- Source ADR: `docs/design/adr/ADR-X.Y.Z-slug.md`
- OBPI Entry (Level 1 WBS): `OBPI-X.Y.Z-NN — "<specification summary from decomposition table>"`

### ADR ALIGNMENT — MANDATORY BEFORE PLANNING

**This section MUST be completed before any planning or implementation.**
**Read the parent ADR's `Agent Context Frame` section, then complete:**

1. **Critical Constraint** (copy from ADR, then restate in your own words):
   > ADR states: "{copy the Critical Constraint from parent ADR}"
   >
   > In my own words: "{agent restates what this means for this OBPI}"

2. **Integration Points** for this OBPI (from ADR's Integration Points, filtered to this OBPI):
   > This OBPI must integrate with: `{specific paths/modules this OBPI works with}`

3. **Anti-Pattern** for this OBPI (from ADR's Anti-Pattern Warning, made specific):
   > A failed implementation would: "{describe what wrong looks like for THIS OBPI}"

4. **Alignment Check** — does this OBPI's objective align with the constraint?
   > - [ ] **YES** — Proceed. Reasoning: "{why this OBPI supports the constraint}"
   > - [ ] **BLOCKER** — Misalignment detected: "{description}"

**STOP if you cannot complete this section from the ADR.**
**STOP if the anti-pattern describes what you were about to do.**

### ARCHITECTURAL CHECKPOINT (Heavy — MANDATORY BEFORE CODE)

**Complete this section BEFORE writing any code:**

```text
## Architectural Checkpoint

**Bounded Context:** [Discovery | Planning | Acquisition | Ingestion | Validation | Reporting]

**I am working in the ______ context, which:**
- OWNS: [list what this context owns, from system-manifest.md]
- DOES NOT OWN: [list what this context does NOT own]

**Invariants that apply to this work:**
- [ ] Single-active HOT contract (if contract work)
- [ ] Single-active COLD contract (if contract work)
- [ ] Adapter delegation rule (if adapter work)
- [ ] Manifest determinism (if manifest work)
- [ ] None of the above apply

**Canonical format for this dataset:** [YYYY-Qn | YYYY-MM | YYCC | YYYY | STATIC | N/A]

**I will DELEGATE to:** [list existing modules I will import from and delegate to]
**I will IMPLEMENT:** [list only the thin facade/protocol compliance — should be minimal]

**STOP CONDITIONS (check before proceeding):**
- [ ] I CAN identify my bounded context
- [ ] I CAN find the module(s) to delegate to (or delegation N/A)
- [ ] I am NOT writing >50 lines of business logic
```

**If any STOP condition fails, emit BLOCKERS and ask for human guidance.**

### OBJECTIVE (Heavy)

- `"<OBPI specification summary — the deliverable this brief implements>"`

### ROLE — MANDATORY

**Agent Identity:** {specific role from parent ADR's Agent Context Frame, e.g., "Migration implementer",
"Feature developer", "Refactoring architect"}

**Success Behavior:** {what the agent should DO to satisfy the ADR's Critical Constraint}

**Failure Behavior:** {what the agent should AVOID — derived from ADR's Anti-Pattern Warning}

### ASSUMPTIONS (Heavy)

- `...`

### NON-GOALS (Heavy)

- `...`

### OPEN QUESTION (Heavy)

- `none` (or a single question)

### CHANGE IMPACT DECLARATION (Heavy — INHERENT)

This brief **always** impacts external contracts (by definition of Heavy lane). No escalation needed.

Public surface changes are documented, tested (BDD), and require human attestation (Gate 5).

### LANE (Heavy)

Heavy — extends Lite with docs + BDD for public CLI/API/schema surfaces.

### EXTERNAL CONTRACT

- Surface: `CLI command / API / schema / error messages`
- Impacted audience: `partners / release notes`

### ALLOWED PATHS (Heavy)

- `features/**`, `features/steps/**`
- `tests/**`
- `docs/**`, `mkdocs.yml` (append-only)
- `src/<module>/**` (explicit list)

### DENIED PATHS (Heavy)

- CI workflows, lockfiles, new dependencies (stdlib-first)
- Any path not listed above

### ANTI-HALLUCINATION CLAUSE (Heavy — MANDATORY)

Same as Lite, PLUS:

- **No example-only BDD:** All Behave scenarios must have complete step implementations (not left for later).
- **No placeholder examples:** Documentation examples must be tested and accurate; not generic or simplified for brevity.
- **No deferred docs:** Manpages, runbooks, and help text must be complete before Gate 3 closes; no "update docs separately" deferrals.
- **Complete Gate 5 artifacts:** Present CLI/opsdev commands that **actually work** on the current codebase; never use hypothetical or not-yet-implemented commands.

If an example cannot be tested or a BDD scenario cannot be implemented immediately, STOP and emit a BLOCKERS output.

### REQUIREMENTS (FAIL-CLOSED — Heavy)

1. `behavioral expectation`
1. `BDD scenario to cover`
1. `docs update / nav entry`

> STOP-on-BLOCKERS: enumerate missing assets before proceeding.

### EDGE CASES (Heavy)

- `edge case to cover in BDD/tests`

### CONTEXT INPUTS (Heavy)

- `relevant files / config keys / data excerpts`

### EXAMPLES (Heavy)

- `<example_input>...</example_input>`
- `<example_output>...</example_output>`

### DISCOVERY CHECKLIST (Heavy — complete before implementation)

**Architecture (MANDATORY — read once, understand system context):**

- [ ] `docs/design/architecture/system-manifest.md` — bounded contexts, contracts, invariants
- [ ] `config/architecture.json` — machine-readable architecture manifest

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure and verification commands
- [ ] `.github/copilot-instructions.md` — repo-wide rules
- [ ] `AGENTS.md` — agent operating contract
- [ ] `.github/instructions/{relevant}.instructions.md` — domain-specific rules

**Context:**

- [ ] Parent ADR: `docs/design/adr/ADR-X.Y.Z-slug.md` — understand rationale

**Prerequisites (check existence, STOP if missing):**

- [ ] Same as Lite, plus any BDD step definitions needed

**Plan Template (MANDATORY):**

- [ ] **READ FIRST:** `.github/skills/gz-obpi-brief/assets/HEAVY_LANE_PLAN_TEMPLATE.md`

### QUALITY GATES (Heavy)

#### Gates 1-4: Implementation

- [ ] Gate 1 (ADR): Intent recorded in brief
- [ ] Gate 2 (TDD): Unit tests pass, coverage ≥40%
- [ ] Gate 3 (Docs): Markdown lint clean, mkdocs build clean
- [ ] Gate 4 (BDD): All BDD scenarios pass
- [ ] Code Quality: Lint, format clean

#### Gate 5: Human Attestation (MANDATORY — DO NOT SKIP)

**This gate requires human action. Agent cannot complete it alone.**

**Constraint:** Follow `docs/governance/GovZero/audit-protocol.md`:
paths/commands only; no outcomes or interpretation.

1. [ ] Agent presents CLI commands for product surface verification
2. [ ] **STOP** — Agent waits for human to execute commands
3. [ ] **STOP** — Agent waits for human attestation response
4. [ ] Agent records attestation in brief

**Attestation Commands (fill in for this brief):**

Use CLI commands only (no raw SQL evidence).

```bash
# Primary product surface command
uv run -m airlineops [command]

# Secondary verification (if applicable)
uv run -m airlineops [command]
```

**Awaiting human attestation.** Human must execute above and respond:

- **Completed** — All claims verified
- **Completed — Partial: [reason]** — Subset accepted
- **Dropped — [reason]** — Rejected

### COMPLETION CHECKLIST (Heavy)

- [ ] Gates 1-4 pass
- [ ] Gate 5 attestation commands presented to human
- [ ] Gate 5 attestation RECEIVED from human
- [ ] Attestation recorded in brief
- [ ] OBPI marked completed ONLY AFTER attestation

### ACCEPTANCE (Heavy)

```markdown
## Gate 5 Attestation

**Date:** YYYY-MM-DD
**Attestor:** [human name/handle]
**Response:** [Completed | Completed — Partial | Dropped]
**CLI Commands Executed:**
- `uv run -m airlineops [command]` — [observed behavior]

**OBPI Status:** Completed
**Brief Status:** Completed
```

### PROHIBITION (Heavy)

**NEVER mark a Heavy lane OBPI as completed before receiving human attestation.**

Implementation completion ≠ Brief completion. Gate 5 is mandatory.
