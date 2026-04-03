---
name: gz-specify
description: Create and semantically author OBPI briefs linked to parent ADR items. Use when decomposing implementation into OBPI increments.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-03
---

# gz-specify

Decompose an ADR's Feature Checklist into implementable OBPI briefs. The CLI
scaffolds the file (frontmatter, lane, ledger event). The model authors the
content (reading the ADR deeply and composing each load-bearing section with
semantic substance). The CLI validates the result.

---

## The Iron Law

```
THE BRIEF IS NOT DONE UNTIL VALIDATION PASSES AND THE USER REVIEWS IT.
```

A scaffolded brief is not an authored brief. Regex extraction is not
interpretation. Structural completeness is not semantic substance. The OBPI
brief is the most critical artifact in the governance pipeline — it carries
domain requirements, architectural fitness functions, and execution scope that
the pipeline grounds against during implementation, verification, and ceremony.

If the brief is thin, the pipeline produces thin work.

### Rationalization Prevention

| Thought | Reality |
|---------|---------|
| "The scaffolded brief has all sections filled" | Filled is not authored. Regex output needs semantic rewriting. |
| "I extracted requirements from the ADR" | Extraction is mechanical. Requirements must be OBPI-specific, not ADR-wide. |
| "Allowed Paths match the Integration Points" | Integration Points are ADR-wide. Narrow to THIS checklist item's scope. |
| "The acceptance criteria have REQ IDs" | Having IDs is structural. The criteria must be specific to THIS deliverable. |
| "Validation passes so the brief is ready" | Validation checks structure. Quality requires semantic substance. |
| "I can batch all 7 briefs for efficiency" | Batching encourages pattern-matching across items. Author one brief at a time with depth. |
| "The ADR Decision bullets are good requirements" | ADR decisions are architectural rationale. OBPI requirements are executable constraints an implementer can verify compliance against. |

---

## When to Use

- After an ADR is authored and its Decomposition Scorecard is valid
- When the Feature Checklist and WBS table are aligned (same count, same ordering)
- To create one OBPI brief per checklist item
- When the user says "specify OBPI for ADR-X.Y.Z item N"
- When the user says "author the brief for OBPI-X.Y.Z-NN"

## When NOT to Use

- For pool ADRs (they cannot receive OBPIs until promoted)
- If the ADR has no Feature Checklist or Decomposition Scorecard
- If the WBS table and Feature Checklist are misaligned (fix the ADR first)

---

## Invocation

```text
/gz-specify ADR-0.0.12 --item 3
/gz-specify ADR-0.0.12 --item 3 --lane heavy
/gz-specify ADR-0.0.12 --all          # author all briefs sequentially
```

**One brief at a time.** Each brief requires deep reasoning about a specific
checklist item's scope. Depth over throughput. The `--all` variant processes
items sequentially, presenting each to the user before continuing.

---

## Pipeline Contract: What the Brief Must Carry

The OBPI pipeline parses and enforces these sections. They are the authoring
targets — everything else is ceremony or documentation.

| Brief Section | Pipeline Stage | What the Pipeline Does With It |
|---|---|---|
| Frontmatter (`id`, `parent`, `lane`, `status`) | Stage 1 | Schema validation, ADR lookup, lane resolution |
| **Objective** | Stage 4 | Value narrative in acceptance ceremony |
| **Allowed Paths** | Stage 2 + hooks | Scope enforcement — blocks out-of-scope file changes |
| **Denied Paths** | Authored readiness gate | Scope boundary definition |
| **Requirements (FAIL-CLOSED)** | Stage 3 | Each numbered item becomes a verification scope dispatched to subagents |
| **Discovery Checklist** | Authored readiness gate | Prerequisites and existing-code context for implementers |
| **Verification** | Stage 3 | Commands executed sequentially; outputs become ceremony evidence |
| **Acceptance Criteria** | Stage 4 | REQ-ID-backed checkboxes mapped to requirements in ceremony |

If any load-bearing section is thin, the corresponding pipeline stage
produces thin work. The brief is the execution contract.

---

## Procedure

### Phase 1: Load ADR Context

Read the parent ADR **thoroughly** — not just the checklist item. The model
must understand the full architectural intent to scope the brief correctly.

**Read these ADR sections and extract:**

| ADR Section | What to Extract | Brief Section It Feeds |
|---|---|---|
| Intent | Before/after state, problem definition, target outcome | Objective |
| Decision | Numbered decisions with per-item rationale | Requirements |
| Non-Goals | Explicit exclusions with handoff references | Denied Paths |
| Interfaces | New/modified artifacts with paths | Allowed Paths |
| Integration Points | Connected systems with paths | Discovery Prerequisites |
| Feature Checklist | The specific item text for this OBPI | Objective, scope boundary |
| WBS Table | Specification summary, lane, status | Objective, Lane |
| Alternatives Considered | Rejected approaches and why | Requirements (what NOT to do) |
| Consequences | Positive/negative outcomes | Verification targets |
| Agent Context Frame | Critical Constraint, Anti-Pattern Warning | Requirements |
| Rationale | Research grounding, evidence citations | Acceptance Criteria framing |

**Also read:**

- **Adjacent OBPIs** — if other briefs exist for the same ADR, read their
  Allowed Paths to understand scope boundaries between items
- **Actual source files** — read the files referenced in Integration Points
  and Interfaces to understand current codebase state. This informs Discovery
  Checklist prerequisites and existing-code entries with real paths, not
  inferred ones.

### Phase 2: CLI Scaffold

Run the CLI to create the brief file with correct frontmatter, lane, and
ledger event:

```bash
uv run gz specify <slug> --parent ADR-X.Y.Z --item N
```

Read the generated file. The CLI produces a structural scaffold with
regex-extracted content. Some sections will have substantive content; others
will have fallback defaults. The model's job is to replace ALL mechanical
content with semantically authored content.

### Phase 3: Semantic Authoring

For each load-bearing section, compose content using the ADR context loaded
in Phase 1. The protocol below specifies what to read, what the pipeline
expects, and what quality looks like for each section.

**Write the complete brief as a single atomic Write operation** — the
`obpi-completion-validator.py` hook fires on edits and checks structural
coherence. Incremental edits risk hook rejection.

---

#### 3a. Objective

**Read:** WBS specification summary + Feature Checklist item text + ADR Intent

**Pipeline expects:** One sentence that answers "what does done look like?"
Used as the value narrative in Stage 4 ceremony — the human reads this to
decide whether to attest.

**Thin (anti-pattern):**
> TBD

> Implement the feature described in the ADR.

> Main session persona frame (Python craftsperson identity).

**Rich (quality target):**
> Create `.gzkit/personas/main-session.md` containing the "Python craftsperson"
> behavioral identity frame for the main Claude Code session, following the
> PersonaFrontmatter schema established by ADR-0.0.11.

The objective must name the concrete artifact or behavior change, not restate
the process.

---

#### 3b. Allowed Paths

**Read:** ADR Interfaces section + Integration Points + actual filesystem

**Pipeline expects:** Markdown bullet list of paths. Each path becomes a glob
pattern in the scope enforcement hook. Out-of-allowlist changes are BLOCKED.

**Compose by:**
1. Start with the ADR Interfaces for THIS checklist item (not the whole ADR)
2. Add test files adjacent to the implementation paths
3. Add the parent ADR package directory
4. Verify each path exists (or note it will be created)
5. Annotate each path with WHY it is in scope for this specific item

**Thin:**
> - `src/module/` — scope TBD
> - `tests/test_module.py` — scope TBD

**Rich:**
> - `.gzkit/personas/main-session.md` — primary deliverable (new persona file)
> - `tests/test_persona_schema.py` — structural validation tests for the new persona
> - `docs/design/adr/foundation/ADR-0.0.12-*/` — parent ADR package

---

#### 3c. Denied Paths

**Read:** ADR Non-Goals + other OBPIs' Allowed Paths

**Pipeline expects:** Bullet list of exclusions. Validates presence and
substantiveness for authored readiness.

**Compose by:**
1. Convert Non-Goals to path exclusions (e.g., "Persona versioning" → the
   versioning infrastructure paths)
2. List paths that belong to OTHER OBPIs in the same ADR (scope isolation)
3. Add standard exclusions (CI, lockfiles, dependencies)

**Thin:**
> - Paths not listed in Allowed Paths

**Rich:**
> - `.gzkit/personas/implementer.md` — owned by OBPI-02
> - `src/gzkit/pipeline_runtime.py` — owned by OBPI-06 (dispatch integration)
> - `AGENTS.md` — owned by OBPI-07 (contract surface change)
> - New dependencies, CI files, lockfiles

---

#### 3d. Requirements (FAIL-CLOSED)

**Read:** ADR Decision + Critical Constraint + Anti-Pattern Warning +
Alternatives Considered (rejected approaches become NEVER rules)

**Pipeline expects:** Numbered list with `REQUIREMENT:`, `NEVER:`, or
`ALWAYS:` prefix. Each numbered requirement becomes a **verification scope**
in Stage 3 — the pipeline dispatches a verification subagent per requirement.

**Compose by:**
1. Start with the ADR's Critical Constraint — this is the highest-priority
   requirement
2. Derive OBPI-specific rules from the Decision items that apply to THIS
   checklist item (not all decisions)
3. Convert rejected Alternatives into NEVER rules (what the implementer must
   not do)
4. Add scope discipline rules (stay inside Allowed Paths, STOP on blockers)

**Thin (copying ADR Decision bullets verbatim):**
> 1. REQUIREMENT: Each agent role gets a dedicated persona file
> 2. REQUIREMENT: Persona frames follow the ADR-0.0.11 schema

**Rich (OBPI-specific, actionable, verifiable):**
> 1. REQUIREMENT: Persona file MUST validate against PersonaFrontmatter schema
>    (name, traits, anti-traits, grounding fields)
> 2. REQUIREMENT: Persona MUST use virtue-ethics behavioral identity framing,
>    NOT expertise claims (PRISM constraint)
> 3. NEVER: Frame persona as "You are an expert X developer" or any
>    expertise-claim variant
> 4. ALWAYS: Grounding statement describes relationship to work, values, and
>    craftsmanship standards — behavioral identity, not job description

---

#### 3e. Discovery Checklist

**Read:** ADR Integration Points + actual codebase (read the files)

**Pipeline expects:** Two subsections under `## Discovery Checklist`:
- `**Prerequisites (check existence, STOP if missing):**` — real paths that
  must exist before implementation starts
- `**Existing Code (understand current state):**` — actual modules and test
  files the implementer should read first

**Compose by:**
1. For Prerequisites: check whether each Integration Point path actually
   exists. If it does, list it. If it does not, note that it will be created.
2. For Existing Code: read the files adjacent to Allowed Paths. Identify the
   patterns the implementer should follow (exemplars, test conventions).

**Thin:**
> - [ ] Required file/module exists: `path/to/prerequisite`

**Rich:**
> - [ ] Persona control surface exists: `.gzkit/personas/`
> - [ ] Persona model exists: `src/gzkit/models/persona.py` (PersonaFrontmatter)
> - [ ] Exemplar persona exists: `.gzkit/personas/implementer.md`

---

#### 3f. Verification

**Read:** The artifacts this OBPI creates or modifies

**Pipeline expects:** Bash code block with commands executed in Stage 3.
Baseline commands (`gz lint`, `gz typecheck`, `gz test`) always run.
OBPI-specific commands must prove THIS item specifically.

**Compose by:**
1. What file(s) does this OBPI create? → `test -f <path>`
2. What test module covers this OBPI? → `uv run -m unittest <module> -v`
3. What CLI command exercises this OBPI? → `uv run gz <command>`
4. For Heavy lane: docs build + BDD feature commands

**Thin:**
> ```bash
> command --to --verify
> ```

**Rich:**
> ```bash
> uv run gz personas list
> uv run -m unittest tests/test_persona_schema.py -v
> test -f .gzkit/personas/main-session.md
> ```

---

#### 3g. Acceptance Criteria

**Read:** ADR Decision + Rationale + the specific deliverable

**Pipeline expects:** Checkbox list with `REQ-X.Y.Z-NN-##` IDs in
Given/When/Then format. Mapped to Requirements in Stage 4 ceremony.

**Compose by:**
1. Each criterion must map to a specific Requirement from section 3d
2. Each criterion must be deterministically verifiable (not subjective)
3. Each criterion must name the specific artifact or behavior being tested
4. Use Given/When/Then structure grounded in the domain

**Thin:**
> - [ ] REQ-0.0.12-01-01: Given/When/Then behavior criterion 1

**Rich:**
> - [ ] REQ-0.0.12-01-01: Given the PersonaFrontmatter schema, when
>   `.gzkit/personas/main-session.md` is parsed, then validation passes with
>   name matching filename stem and non-empty traits, anti-traits, and grounding
> - [ ] REQ-0.0.12-01-02: Given the PRISM constraint, when the persona
>   grounding and body are reviewed, then NO expertise claims appear — only
>   behavioral identity framing

---

### Phase 4: Validation Loop

Run the authored-readiness validation:

```bash
uv run gz obpi validate --authored <path-to-brief>
```

If validation fails:
1. Read the specific error messages
2. Fix the failing sections
3. Re-run validation
4. Iterate until PASS

Present the validation output to the user.

### Phase 5: Self-Evaluation

Score the authored brief against 5 quality dimensions (1-4 scale):

| Dimension | Question |
|-----------|----------|
| Independence | Can this OBPI be completed without waiting for others except declared dependencies? |
| Testability | Can completion be verified with the stated Verification commands? |
| Value | What concrete capability would be lost if this OBPI were removed? |
| Size | Is this a 1-3 day work unit? |
| Clarity | Could a different agent implement this without ambiguity? |

**Threshold:** All dimensions >= 3. Any dimension scoring 1 requires revision
before presenting.

Present the authored brief with dimension scores. The user reviews the brief
itself — the model's job is to produce a brief worth reviewing.

---

## Validation Commands

```bash
# Validate one brief
uv run gz obpi validate --authored <path-to-brief>

# Validate all briefs for an ADR
uv run gz obpi validate --adr ADR-X.Y.Z --authored

# Verify lane assignments match WBS
grep "^lane:" docs/design/adr/**/ADR-X.Y.Z-*/obpis/*.md

# Run evaluation to check OBPI scores
uv run gz adr evaluate ADR-X.Y.Z
```

---

## Pre-Conditions

- Parent ADR must have a valid Decomposition Scorecard
- Feature Checklist item count must match scorecard `Final Target OBPI Count`
- Parent ADR must not be a pool ADR
- Parent ADR evaluation should be CONDITIONAL GO or GO (warn if NO GO)

## Post-Conditions

- OBPI brief file created with correct frontmatter, lane, and ledger event
- All load-bearing sections authored with semantic substance (not regex output)
- `uv run gz obpi validate --authored` passes
- All 5 quality dimensions score >= 3
- User has reviewed and accepted the brief

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `gz-adr-create` | Creates the parent ADR that specify decomposes |
| `gz-design` | Design dialogue that produces the ADR intent specify interprets |
| `gz-obpi-pipeline` | Executes briefs created by specify — the downstream consumer |
| `gz-adr-evaluate` | Evaluates ADR+OBPI quality (run after specify to verify scores) |
| `gz-plan-audit` | Pre-flight alignment audit between plan and brief (downstream) |
