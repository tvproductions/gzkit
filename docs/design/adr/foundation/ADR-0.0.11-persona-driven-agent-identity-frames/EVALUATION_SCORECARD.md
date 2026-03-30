<!-- markdownlint-disable-file MD013 MD041 -->

ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.11 -- Persona-Driven Agent Identity Frames
Evaluator: Claude Opus 4.6 (1M context) -- Adversarial Red-Team Mode
Date: 2026-03-30

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 |
| 2 | Decision Justification | 15% | 4 | 0.60 |
| 3 | Feature Checklist | 15% | 3 | 0.45 |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 |
| 5 | Lane Assignment | 10% | 2 | 0.20 |
| 6 | Scope Discipline | 10% | 2 | 0.20 |
| 7 | Evidence Requirements | 10% | 2 | 0.20 |
| 8 | Architectural Alignment | 10% | 3 | 0.30 |

WEIGHTED TOTAL: 3.00/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- ADR-Level Scoring Rationale ---

### Dimension 1: Problem Clarity -- 4/4

The problem is exceptionally well articulated. The ADR identifies a concrete,
repeated failure mode (agents splitting imports across edits despite rules and
hooks), explains the mechanistic cause (default Assistant persona activates
minimum-viable-effort trait clusters), and grounds the entire argument in five
published research sources. The before state (rules exist, hooks enforce, agent
still fails) and after state (persona frames activate the correct trait cluster
at the identity level) are both concrete and testable. The "so what?" is
immediately obvious: this is not theoretical -- it addresses observed production
failures with a mechanistic explanation.

### Dimension 2: Decision Justification -- 4/4

Each of the six decisions in the Decision section is independently justified:
- Control surface in `.gzkit/personas/` follows the established pattern of
  `.gzkit/rules/`, `.gzkit/schemas/`, `.gzkit/skills/`
- Virtue-ethics framing is backed by PRISM study data (3.6pp accuracy degradation
  from generic expert claims)
- Orthogonal trait composition cites PERSONA/ICLR 2026 (91% win rates)
- Operating system view is explicitly justified by PSM research
- AGENTS.md template change is justified by the "identity gap" argument
- Pool ADR supersession is justified as a subset relationship

The ADR cites five specific research papers with URLs, publication venues, and
quantified findings. This is the strongest evidence base of any foundation ADR
reviewed. Counterarguments are addressed via the anti-pattern warning and the
PRISM accuracy/alignment tradeoff.

### Dimension 3: Feature Checklist -- 3/4

All six items map to testable deliverables. Each item removed would leave a
visible capability gap. Items are at consistent granularity and logically
ordered (research first, then schema, then composition, then template, then
cleanup, then validation). However, one weakness: there is no explicit checklist
item for "CLI read surface" (`gz personas list`), which is mentioned in the
Interfaces section. The CLI surface may be trivial, but it is an interface
contract and deserves its own item or explicit exclusion note.

### Dimension 4: OBPI Decomposition -- 3/4

Six OBPIs is reasonable for the decomposition scorecard (target 6, actual 6).
Each OBPI maps cleanly to one checklist item. Domain boundaries are mostly
sensible -- research, schema, composition, template, lifecycle, validation are
distinct concerns. However, OBPI-03 (trait composition model) and OBPI-06
(schema validation) have significant overlap: schema validation must understand
the trait composition rules to validate persona files. These could arguably be
one OBPI. Additionally, OBPI-05 (supersede pool ADR) is a lifecycle operation
that could be a sub-task of OBPI-02 (control surface definition) rather than a
standalone brief.

### Dimension 5: Lane Assignment -- 2/4

There is a material contradiction between the ADR and the OBPI briefs:

- The ADR OBPI table declares OBPI-02 (control surface) as Heavy and OBPI-04
  (AGENTS.md template) as Heavy
- All six OBPI brief files have `lane: Lite` in their frontmatter
- The ADR's own Feature Checklist says the new control surface and AGENTS.md
  template change are both Heavy lane

This is a structural defect. OBPI-02 creates a new governed directory
(`.gzkit/personas/`) which is an external contract change. OBPI-04 modifies
AGENTS.md, an external governance contract. Both MUST be Heavy per AGENTS.md
doctrine. The briefs are wrong.

Furthermore, OBPI-06 creates `tests/test_persona_schema.py` and possibly
`features/persona.feature` -- if the BDD feature file is part of this OBPI,
it should be Heavy (BDD is Gate 4, Heavy-only). The ADR's Evidence section
mentions BDD as Heavy lane evidence but does not clearly assign which OBPI
owns the feature file.

### Dimension 6: Scope Discipline -- 2/4

The ADR has no explicit Non-Goals section. Non-goals are implied but not stated.
Three plausible scope creep vectors are unaddressed:

1. Runtime persona selection (dynamic switching based on task type) -- is this
   in scope or deferred to ADR-0.0.12/0.0.13?
2. Persona performance measurement (how do you know the persona works?) -- the
   ADR describes the mechanism but not how to validate it produces better output
3. CLI mutation surfaces (`gz personas create`, `gz personas edit`) -- only
   `gz personas list` is mentioned; are write surfaces deferred?

The lineage note (ADR-0.0.11 -> 0.0.12 -> 0.0.13) implies awareness of
downstream work, but the boundary between "what this ADR delivers" and "what
the next ADR delivers" is not explicitly drawn.

### Dimension 7: Evidence Requirements -- 2/4

The ADR-level Evidence section lists test files and document paths, which is
good. However:

- The OBPI briefs are entirely template-default -- every brief has "TBD" for
  Objective, placeholder Allowed/Denied Paths, placeholder Requirements, and
  placeholder Acceptance Criteria
- No OBPI has concrete verification commands beyond the generic template stubs
- The specific verification command for every OBPI is literally
  `command --to --verify`
- Without authored briefs, "done" is not operationally defined for any OBPI

This is expected for scaffolded templates but it means the evidence layer is
currently non-functional. No agent could implement from these briefs.

### Dimension 8: Architectural Alignment -- 3/4

The ADR follows established codebase patterns well:
- New governed directory follows `.gzkit/{surface}/` convention
- YAML frontmatter + markdown body matches existing schema patterns
- Integration points are listed with specific file paths
- Anti-patterns are named with concrete "what wrong looks like" examples
  (the job-description anti-pattern is excellent)

The CLI surface (`gz personas list`) introduces a new command, which should
reference the CLI doctrine and manpage requirements. This is mentioned in the
Feature Checklist ("Scope and surface") but not fully traced through the CLI
contract doctrine (e.g., where is the manpage OBPI?).

--- OBPI-Level Scores ---

All six OBPIs are unmodified scaffolded templates. They contain no authored
content -- Objectives are "TBD", Requirements are placeholder text, Acceptance
Criteria use generic Given/When/Then stubs, and Verification commands are
`command --to --verify`. Scoring reflects the template-default state.

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01   | 4           | 1           | 3     | 3    | 1       | 2.4 |
| 02   | 3           | 1           | 4     | 3    | 1       | 2.4 |
| 03   | 2           | 1           | 3     | 3    | 1       | 2.0 |
| 04   | 3           | 1           | 4     | 3    | 1       | 2.4 |
| 05   | 2           | 1           | 2     | 2    | 1       | 1.6 |
| 06   | 2           | 1           | 3     | 3    | 1       | 2.0 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. ALL OBPIs FAIL. Every OBPI scores 1
on Testability and Clarity (structural defect requiring revision).

### OBPI Scoring Rationale

**OBPI-01 (Research Synthesis):** Independence 4 -- no dependencies, can start
immediately. Testability 1 -- no verification commands, "TBD" objective. Value 3
-- removing research synthesis removes the evidence foundation. Size 3 --
reasonable 1-3 day scope. Clarity 1 -- "TBD" objective, placeholder everything.

**OBPI-02 (Control Surface):** Independence 3 -- logically depends on OBPI-01
(needs research principles to inform schema design). Testability 1 -- no
verification commands. Value 4 -- this IS the primary deliverable. Size 3 --
schema + storage + loading is a reasonable unit. Clarity 1 -- placeholder.

**OBPI-03 (Composition Model):** Independence 2 -- depends on OBPI-02 (needs
the schema to define composition rules against) AND the dependency is undeclared.
Testability 1 -- placeholder. Value 3 -- composition rules are needed but could
be part of OBPI-02. Size 3 -- reasonable. Clarity 1 -- placeholder.

**OBPI-04 (AGENTS.md Update):** Independence 3 -- depends on OBPI-02 for schema
to reference. Testability 1 -- placeholder. Value 4 -- AGENTS.md is the primary
agent contract; without the persona section the surface exists but is not
integrated. Size 3 -- template change is focused. Clarity 1 -- placeholder.

**OBPI-05 (Supersede Pool ADR):** Independence 2 -- cannot supersede until the
replacement surface is built (OBPI-02). Testability 1 -- placeholder. Value 2 --
this is lifecycle bookkeeping, not capability delivery. Removing it leaves a
stale pool ADR but no functional gap. Size 2 -- too small for a standalone OBPI;
this is a single file status change. Clarity 1 -- placeholder.

**OBPI-06 (Schema Validation):** Independence 2 -- requires OBPI-02 schema and
OBPI-03 composition rules. Testability 1 -- placeholder. Value 3 -- validation
infrastructure is needed but overlaps with OBPI-03. Size 3 -- test file +
possible BDD feature. Clarity 1 -- placeholder.

--- Red-Team Challenges ---

### Challenge 1: The "So What?" Test -- PASS

For each Feature Checklist item, the removal consequence:

1. **Research synthesis**: Without it, persona design is ungrounded prompt
   engineering. The entire rationale collapses to "persona feels like it should
   work" without mechanistic evidence. Concrete.
2. **Control surface definition**: Without it, there is no storage location,
   schema, or loading mechanism. The ADR has no deliverable. Concrete.
3. **Trait composition model**: Without it, personas cannot combine traits
   safely. Multi-trait personas degrade unpredictably. Concrete.
4. **AGENTS.md template update**: Without it, the persona surface exists but
   no agent context frame references it. It is a dead surface. Concrete.
5. **Supersede pool ADR**: Without it, `ADR-pool.per-command-persona-context`
   remains active and competes with the new surface. Concrete -- but weak.
   The pool ADR could be marked superseded as a sub-task of OBPI-02 without
   its own brief.
6. **Schema validation**: Without it, persona files are unvalidated markdown.
   Invalid files could silently degrade agent behavior. Concrete.

Verdict: 5/6 items have strong independent justification. Item 5 is marginal --
it could be a sub-task rather than a standalone OBPI. Overall PASS.

### Challenge 2: The Scope Challenge -- FAIL

**Not in scope that arguably should be:**

1. **Persona effectiveness measurement** -- The ADR claims personas produce
   "measurably different behavioral outcomes" (line 135) but includes no
   mechanism to measure those outcomes. How will the operator know if the
   persona actually reduced import-splitting failures? Without measurement,
   the ADR's own success claim is unfalsifiable.
2. **Runtime persona dispatch** -- The Interfaces section says persona files
   are "loaded at dispatch time for subagents, at session start for main agent"
   but no OBPI covers the loading mechanism implementation. Schema and storage
   are covered; the actual loading code is not.
3. **Persona drift detection** -- The rationale cites Anthropic's persona
   vectors research on monitoring drift, but no OBPI addresses drift detection
   or monitoring.

**In scope that arguably should not be:**

1. **OBPI-05 (Supersede pool ADR)** -- This is a governance lifecycle operation,
   not a capability delivery. It could be a checklist item on OBPI-02 rather
   than consuming a full OBPI slot.

**Why it fails:** The ADR has no explicit Non-Goals section. The three exclusions
above (measurement, dispatch loading, drift detection) are not documented as
deferred. The reader cannot distinguish "we thought about it and excluded it"
from "we did not think about it."

### Challenge 3: The Alternative Challenge -- PASS (marginal)

**Fewer OBPIs:** OBPI-05 (supersede) could merge into OBPI-02 (control surface)
as a sub-task. OBPI-03 (composition) and OBPI-06 (validation) could merge --
validation tests inherently encode composition rules. This would reduce from 6
to 4 OBPIs without losing capability.

**More OBPIs:** OBPI-02 (control surface) bundles three concerns -- storage
directory, YAML schema, and loading mechanism. The loading mechanism alone is a
substantial piece (referenced in Interfaces but not clearly owned by any OBPI).
This could split into schema + loading.

**Defense:** The decomposition scorecard produced target 6 from the scoring
formula. The current 6 are logically defensible even if some merges are
plausible. The ADR's checklist items provide clear 1:1 mapping. Marginal pass
because the formula-driven decomposition is reasonable, but the merge arguments
are legitimate.

### Challenge 4: The Dependency Challenge -- PASS

Dependency graph analysis:

```
OBPI-01 (research) -> no dependencies, can start immediately
OBPI-02 (surface)  -> soft dependency on OBPI-01 (needs principles)
OBPI-03 (compose)  -> depends on OBPI-02 (needs schema)
OBPI-04 (template) -> depends on OBPI-02 (needs schema to reference)
OBPI-05 (supersede)-> depends on OBPI-02 (replacement must exist first)
OBPI-06 (validate) -> depends on OBPI-02 and OBPI-03 (needs schema + rules)
```

OBPI-02 is a single point of convergence -- all downstream work depends on it.
If OBPI-02 blocks, OBPIs 03-06 all stall. This is not a defect per se (schema
must exist before composition, template, or validation), but it IS a risk
concentration. The dependency graph is acyclic and the convergence point is
architecturally necessary. Pass.

### Challenge 5: The Gold Standard Challenge -- PASS

Compared to ADR-0.0.9 (State Doctrine) and ADR-0.0.10 (Storage Tiers), which
both achieved GO status:

**What ADR-0.0.11 does better:**
- Research evidence is significantly stronger -- five cited papers with
  quantified findings vs. zero external citations in ADR-0.0.9/0.0.10
- Anti-pattern warnings are more specific and grounded (the job-description
  example is excellent)
- Agent Context Frame is more detailed and prescriptive
- The "operating system view" framing is a novel architectural contribution

**What the exemplars have that ADR-0.0.11 lacks:**
- ADR-0.0.9 has a clear Non-Goals implied in scope (no SQLite changes,
  no Tier C introduction)
- ADR-0.0.10 has authored OBPI briefs (not template stubs)
- Both exemplars have tighter lane consistency (no ADR-table vs brief
  contradictions)

**Structural comparison:** ADR-0.0.11 is structurally stronger than
ADR-0.0.10 at the ADR level but weaker at the OBPI level due to
unauthored briefs.

### Challenge 6: The Timeline Challenge -- PASS

Critical path: OBPI-01 -> OBPI-02 -> OBPI-03 -> OBPI-06
                                   -> OBPI-04 (parallel with 03)
                                   -> OBPI-05 (parallel with 03)

Parallelization stages:
- Stage 1: OBPI-01 (research) -- 1-2 days
- Stage 2: OBPI-02 (surface) -- 2-3 days
- Stage 3: OBPI-03 + OBPI-04 + OBPI-05 in parallel -- 1-2 days
- Stage 4: OBPI-06 (validation, needs 02+03 complete) -- 1-2 days

Theoretical minimum wall-clock: 5-9 days.
Maximum parallelism: 3 OBPIs in Stage 3.

The critical path is OBPI-01 -> OBPI-02 -> OBPI-03 -> OBPI-06 (4 serial
OBPIs). This is explicit and understood.

### Challenge 7: The Evidence Challenge -- FAIL

Attempting to write concrete verification commands for each OBPI:

**OBPI-01:** `test -f docs/design/research-persona-selection-agent-identity.md`
-- can verify file exists, but no command verifies the document is actually a
research synthesis vs. an empty file. Partial.

**OBPI-02:** `ls .gzkit/personas/` + schema validation command -- the ADR
mentions `tests/test_persona_schema.py` but that test is in OBPI-06, not
OBPI-02. How is OBPI-02 "done" verified independently? No command specified.

**OBPI-03:** No verification command can be written. "Orthogonal combination
rules" are a design document. What command proves composition rules are correct?
Only OBPI-06's tests could verify this, but OBPI-03 claims Lite lane (no tests
required beyond Gate 2).

**OBPI-04:** `grep -c "## Persona" AGENTS.md` -- verifiable but not specified.

**OBPI-05:** `grep "Superseded" docs/design/adr/pool/ADR-pool.per-command-persona-context.md`
-- verifiable but not specified.

**OBPI-06:** `uv run -m unittest tests/test_persona_schema.py -v` -- this one
is actually verifiable from the ADR's Evidence section, but the OBPI brief
itself has only placeholder commands.

Verdict: FAIL. Only 2 of 6 OBPIs have obviously writable verification commands.
The briefs specify none. The ADR-level evidence section names test files but
does not assign them to specific OBPIs.

### Challenge 8: The Consumer Challenge -- FAIL

A maintainer reading this ADR would still ask:

1. **"How do I write a persona file?"** -- The schema is described abstractly
   (YAML frontmatter with `name`, `traits`, `anti-traits`, `grounding`) but
   there is no example persona file. No exemplar. The maintainer knows the
   shape but not the content.

2. **"How do I know my persona is working?"** -- No measurement, monitoring,
   or feedback mechanism is described. The research says persona activates
   trait clusters, but the operator has no way to verify this is happening.

3. **"What happens if I write a bad persona?"** -- The anti-pattern warning
   describes what NOT to write, but does not describe validation feedback.
   Does the schema validator reject bad personas? Does it just check YAML
   structure?

4. **"Where does persona loading code live?"** -- The Interfaces section says
   "loaded at dispatch time" but no module path is given for the loader.
   `src/gzkit/` integration points are listed for AGENTS.md and research but
   not for the runtime loading mechanism.

Verdict: FAIL. The ADR is strong on "why" but weak on "how to use it." An
operator could not start writing persona files from this ADR alone.

### Challenge 9: The Regression Challenge -- PASS (marginal)

Six months after validation, what could silently break:

1. **Persona files drift from schema** -- Mitigated by OBPI-06 (schema
   validation tests). As long as tests run in CI, invalid persona files
   are caught.

2. **Research papers retracted or updated** -- The Tidy First Plan explicitly
   lists this as a STOP/BLOCKER condition. Good.

3. **AGENTS.md template updated without persona section** -- No hook or test
   enforces the persona section in AGENTS.md. A future ADR could modify the
   template and silently drop the persona section. Risk acknowledged in the
   Consequences section but no contract prevents it.

4. **New skills/agents added without persona assignment** -- No enforcement
   mechanism requires new agents to have personas. The ADR makes it mandatory
   but provides no gate or hook to enforce it.

Marginal pass: items 1-2 are addressed; items 3-4 are real regression risks
without enforcement contracts.

### Challenge 10: The Parity Challenge -- FAIL

The ADR claims: "Traits compose orthogonally per the PERSONA/ICLR 2026
framework -- multiple behavioral traits combine without interference."

**Weakest claim analysis:** The PERSONA paper demonstrates orthogonal
composition via activation-space vector algebra on a specific model
(likely research-grade). The claim that this transfers to prompt-level
persona specification (YAML traits in a system prompt) is a leap.
PERSONA uses direct activation intervention; this ADR uses system prompt
text. These are different mechanisms:

- PERSONA: modify activation vectors at inference time (mechanistic control)
- This ADR: write trait names in a markdown file loaded into context window
  (prompt engineering)

The ADR adopts the "operating system view" from PSM, which supports prompt-level
persona activation. But the orthogonality claim specifically comes from PERSONA,
which operates at a different level of the stack. The ADR conflates two research
findings that operate at different mechanistic levels.

**Counter-defense:** The ADR could argue that prompt-based trait specification
triggers the same activation-space directions that PERSONA manipulates directly,
per the Assistant Axis paper (persona corresponds to a linear direction in
activation space, and system prompts reliably trigger persona vectors per
Anthropic's persona vectors research). This is a defensible position but the
ADR does not make this bridging argument explicitly. It presents the
orthogonality claim as settled when it requires a bridging inference.

Verdict: FAIL. The orthogonality claim requires a bridging argument between
activation-level intervention and prompt-level specification that the ADR
does not make.

--- Red-Team Summary ---

| # | Challenge | Result | Notes |
|---|-----------|--------|-------|
| 1 | So What? | PASS | 5/6 strong, OBPI-05 marginal |
| 2 | Scope | FAIL | No Non-Goals section; measurement/dispatch/drift not addressed |
| 3 | Alternative | PASS | Marginal; merge arguments acknowledged but decomposition defensible |
| 4 | Dependency | PASS | OBPI-02 convergence understood |
| 5 | Gold Standard | PASS | Stronger than exemplars at ADR level |
| 6 | Timeline | PASS | Critical path explicit |
| 7 | Evidence | FAIL | Only 2/6 OBPIs have writable verification commands |
| 8 | Consumer | FAIL | No example persona, no usage guidance, no loader path |
| 9 | Regression | PASS | Marginal; enforcement gaps for items 3-4 |
| 10 | Parity | FAIL | Orthogonality claim bridges two research levels without argument |

RED-TEAM RESULT: 4 failures
RED-TEAM THRESHOLD: <=2 failures = GO, 3-4 = CONDITIONAL GO, >=5 = NO GO

--- Overall Verdict ---

[ ] GO - Ready for proposal/defense review
[x] CONDITIONAL GO - Address items below, then re-evaluate
[ ] NO GO - Structural revision required

**ADR weighted score: 3.00/4.0 -- meets GO threshold.**
**OBPI scores: all below 3.0 -- all fail threshold (expected for templates).**
**Red-team: 4 failures -- CONDITIONAL GO.**

Combined verdict: CONDITIONAL GO. The ADR itself is strong (3.00 weighted, with
two exemplary dimensions at 4/4). The OBPI briefs are entirely scaffolded
templates and cannot be implemented as-is. The red-team identified four
structural gaps that should be addressed before the ADR moves to Proposed.

--- Top 3 Action Items (Priority Ordered) ---

1. **FIX LANE CONTRADICTIONS (blocking):** The ADR OBPI table declares
   OBPI-02 and OBPI-04 as Heavy, but all six OBPI brief files have
   `lane: Lite` in frontmatter. Resolve the contradiction. At minimum,
   OBPI-02 (new control surface) and OBPI-04 (AGENTS.md contract change)
   MUST be Heavy per AGENTS.md doctrine. Update the brief frontmatter to
   match the ADR table.

2. **ADD NON-GOALS SECTION (high priority):** Add an explicit Non-Goals
   section addressing: (a) runtime persona selection/dispatch is deferred
   to ADR-0.0.12, (b) persona effectiveness measurement is out of scope,
   (c) persona drift detection/monitoring is out of scope, (d) CLI mutation
   surfaces are deferred. Without this, scope creep is unguarded.

3. **AUTHOR OBPI BRIEFS (required before Proposed):** Every brief is a
   template stub. Before moving to Proposed, each brief needs: (a) a
   concrete Objective sentence, (b) real Allowed/Denied Paths, (c) authored
   Requirements with NEVER/ALWAYS constraints, (d) specific Acceptance
   Criteria in Given/When/Then form, (e) concrete Verification commands.

--- Secondary Action Items ---

4. **Bridge the orthogonality argument:** Explicitly connect the PERSONA
   paper's activation-level orthogonality finding to prompt-level trait
   specification, using the Assistant Axis and persona vectors research
   as the bridge. The current text implies the connection but does not
   make it.

5. **Add an example persona file:** Include a concrete exemplar persona
   file (even as a draft) in the ADR or research document so that
   consumers can see what "virtue-ethics-based behavioral identity"
   looks like in practice.

6. **Assign BDD feature ownership:** The ADR Evidence section lists
   `features/persona.feature` but no OBPI claims ownership. Assign it
   to OBPI-06 (validation) or create a dedicated OBPI for BDD scenarios.

7. **Consider merging OBPI-05 into OBPI-02:** Superseding the pool ADR
   is a sub-task of establishing the control surface, not an independent
   capability delivery.
