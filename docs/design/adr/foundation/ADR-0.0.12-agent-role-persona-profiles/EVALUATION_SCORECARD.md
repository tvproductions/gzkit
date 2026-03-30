<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR Evaluation Scorecard

```text
ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.12 — Agent Role Persona Profiles
Evaluator: Claude Opus 4.6 (adversarial red-team)
Date: 2026-03-30
Mode: --red-team (all 10 challenges engaged)
```

---

## Part 1: ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted | Justification |
|---|-----------|--------|-------------|----------|---------------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | The problem is well-stated: default Assistant persona causes trait-cluster failures (import splitting, shallow compliance). Concrete catalyst example given. The "so what?" is clear. Docked from 4 because the before/after states are described qualitatively ("agents default to helpful AI assistant" vs "agents operate from designed identities") without quantitative measurement criteria. How will you measure that persona activation actually changed behavior? No metric is proposed. |
| 2 | Decision Justification | 15% | 3 | 0.45 | Decisions reference PSM, PRISM, PERSONA/ICLR research. The "wrong vs. right" persona framing example (lines 168-172) is excellent. Alternatives are not explicitly enumerated -- the ADR does not name and dismiss alternative approaches (e.g., "why not use system-prompt rules instead of persona files?" or "why not embed persona inline in AGENTS.md rather than separate files?"). The rationale section is strong but the Decision section relies on inherited justification from ADR-0.0.11 rather than independently arguing each choice. |
| 3 | Feature Checklist | 15% | 3 | 0.45 | Seven checklist items, each mapping to a testable deliverable (persona file + dispatch integration). Items are at mostly consistent granularity. However: the checklist lists "quality-reviewer" as a separate item (#4) in the Goals section but bundles spec-reviewer + quality-reviewer into OBPI-03 in the decomposition. The checklist has 7 items, the decomposition has 7 OBPIs, but the mapping between them is misaligned (see OBPI Decomposition critique below). No item is padding -- each delivers a concrete persona file or integration point. |
| 4 | OBPI Decomposition | 15% | 2 | 0.30 | **Serious structural defect.** The OBPI-to-checklist mapping is scrambled: OBPI-04 (named "narrator") references checklist item #4 ("quality-reviewer"), OBPI-05 (named "pipeline orchestrator") references #5 ("narrator"), OBPI-06 (named "dispatch integration") references #6 ("pipeline orchestrator"), and OBPI-07 (named "agents-md reference") references #7 ("dispatch integration"). This is a cascading off-by-one/swap error in the brief scaffolding. Additionally, OBPI-03 bundles two distinct personas (spec-reviewer + quality-reviewer) but the checklist treats them as separate items (#3 and #4). The decomposition scorecard math (baseline 3 + split 4 = 7) is internally consistent but the actual brief contents are entirely template boilerplate with no authored substance. |
| 5 | Lane Assignment | 10% | 2 | 0.20 | **Lane contradiction.** The ADR decomposition table marks OBPI-01 and OBPI-07 as Heavy, but both OBPI brief files have `lane: Lite` in their YAML frontmatter. This is a direct contradiction. Furthermore, the lane rationale is questionable: OBPI-01 (main session persona) is marked Heavy in the table because it touches AGENTS.md (an external contract), which is defensible. But OBPI-06 (dispatch integration modifying pipeline_runtime.py) is marked Lite despite touching runtime behavior -- arguably this changes the subagent contract and should be Heavy. The parent ADR is Heavy lane, so all Lite OBPIs inherit parent-lane attestation floor per project rules. |
| 6 | Scope Discipline | 10% | 2 | 0.20 | No explicit non-goals section exists. The ADR implicitly scopes to "write persona frames and integrate dispatch" but does not state what it excludes. Three plausible scope creep vectors are unaddressed: (1) persona effectiveness measurement/telemetry, (2) persona drift detection at runtime, (3) persona versioning/migration. The ADR mentions persona drift detection in the ADR-0.0.11 rationale but does not explicitly exclude it from 0.0.12. The "Critical Constraint" and "Anti-Pattern Warning" sections partially bound scope but are about content quality, not feature scope. |
| 7 | Evidence Requirements | 10% | 2 | 0.20 | The ADR lists test files (`tests/test_persona_profiles.py`, `features/persona_dispatch.feature`) and the completion checklist has three artifact paths with evidence types. But per-OBPI evidence requirements are entirely absent -- every OBPI brief has placeholder verification commands (`command --to --verify`) and template acceptance criteria (`Given/When/Then behavior criterion 1`). No OBPI has a concrete verification command. The ADR-level evidence section names artifacts but cannot be decomposed to individual OBPI "done" criteria. |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | Integration points are explicitly listed with module paths (pipeline_runtime.py, AGENTS.md, .gzkit/personas/, .claude/agents/*.md). Anti-patterns are named with concrete wrong/right examples. The ADR follows established gzkit patterns (YAML frontmatter, `.gzkit/` storage, schema validation). Persona files follow the control surface pattern from ADR-0.0.11. Docked from 4 because the ADR does not reference a specific exemplar persona file from ADR-0.0.11 that implementers could pattern-match against. |

**WEIGHTED TOTAL: 2.55 / 4.0**

**THRESHOLD ASSESSMENT: CONDITIONAL GO** (2.5 <= 2.55 < 3.0)

---

## Part 2: OBPI-Level Scores

All seven OBPI briefs are unmodified scaffolded templates. They contain:

- `TBD` objectives
- Placeholder allowed/denied paths (`src/module/`, `tests/test_module.py`)
- Boilerplate requirements (`REQUIREMENT: First constraint`)
- Template acceptance criteria (`Given/When/Then behavior criterion 1`)
- Placeholder verification commands (`command --to --verify`)

Scoring reflects this reality.

| OBPI | Independence (A) | Testability (B) | Value (C) | Size (D) | Clarity (E) | Avg |
|------|-----------------|-----------------|-----------|----------|-------------|-----|
| 01 - Main session persona | 3 | 1 | 4 | 3 | 1 | 2.4 |
| 02 - Implementer persona | 3 | 1 | 4 | 3 | 1 | 2.4 |
| 03 - Reviewer personas | 3 | 1 | 3 | 3 | 1 | 2.2 |
| 04 - Narrator persona | 3 | 1 | 3 | 2 | 1 | 2.0 |
| 05 - Orchestrator persona | 3 | 1 | 3 | 2 | 1 | 2.0 |
| 06 - Dispatch integration | 2 | 1 | 4 | 3 | 1 | 2.2 |
| 07 - AGENTS.md reference | 2 | 1 | 3 | 2 | 1 | 1.8 |

### OBPI Score Justifications

**Independence (A):**

- OBPIs 01-05: Score 3. Each persona can be written independently. Declared dependency on ADR-0.0.11 is the only blocker.
- OBPI-06: Score 2. Depends on at least one persona file existing (OBPIs 01-05) to have something to load. Undeclared dependency.
- OBPI-07: Score 2. Depends on main session persona (OBPI-01) to reference. Undeclared dependency.

**Testability (B):**

- All OBPIs: Score 1. Every brief has `command --to --verify` as placeholder. No concrete verification command exists in any brief. The ADR-level evidence mentions `tests/test_persona_profiles.py` but no OBPI specifies what that test validates for its specific scope. An agent implementing any of these OBPIs would have to invent the verification criteria.

**Value (C):**

- OBPIs 01, 02, 06: Score 4. Main session persona, implementer persona, and dispatch integration are the three essential deliverables. Without any one of them, the ADR fails to achieve its stated purpose.
- OBPIs 03, 04, 05, 07: Score 3. Reviewer, narrator, and orchestrator personas strengthen the system but the core value proposition (fixing the import-splitting failure mode) is delivered by the implementer persona + dispatch integration alone.

**Size (D):**

- OBPIs 01, 02, 06: Score 3. Writing a persona frame with research grounding and implementing dispatch loading are each 1-2 day tasks.
- OBPIs 03: Score 3. Bundles two personas but they share enough domain overlap (review) to be reasonable.
- OBPIs 04, 05: Score 2. Individual persona frames without runtime integration are arguably too small for independent OBPIs -- each is a single markdown file with YAML frontmatter. Could be a few hours of work.
- OBPI-07: Score 2. Adding a reference line to AGENTS.md is trivially small.

**Clarity (E):**

- All OBPIs: Score 1. Every brief has `TBD` as its objective. Allowed paths are template placeholders. Requirements are template placeholders. Acceptance criteria are template placeholders. Two different agents given any of these briefs would produce wildly different implementations. The OBPI brief scaffolding provides structural completeness but zero implementation guidance.

**OBPI THRESHOLD: FAIL.** Average across all OBPIs is 2.14. No OBPI reaches 3.0. All OBPIs score 1 on Testability and Clarity, requiring revision.

---

## Part 3: Red-Team Challenges

### Challenge 1: The "So What?" Test

**Result: CONDITIONAL PASS**

For each feature checklist item, can removal be justified with a specific capability loss?

| Checklist Item | If Removed | Verdict |
|---|---|---|
| Main session persona (#1) | Main conversation agent continues using generic Assistant identity. Most visible impact -- every interaction degrades. | Concrete loss |
| Implementer persona (#2) | The documented catalyst failure (import splitting) remains unaddressed. This is the highest-value item. | Concrete loss |
| Spec-reviewer persona (#3) | Reviews default to agreeable/surface-level assessment. Less critical but measurable. | Concrete loss |
| Quality-reviewer persona (#4) | Architectural review lacks rigor traits. Overlaps with #3 -- both are "review" personas. | Concrete but overlapping |
| Narrator persona (#5) | Status narratives default to verbose/unfocused output. Nice-to-have. | Weaker case |
| Pipeline orchestrator (#6) | Dispatch ceremonies might be skipped or shortcuts taken. Moderate value. | Concrete loss |
| Dispatch integration (#7) | Without loading, persona files are inert artifacts. This is essential. | Concrete loss |

Items #3 and #4 are the weakest -- their individual "so what?" answers overlap significantly. The ADR bundles them into one OBPI (03) which partially addresses this, but the checklist still lists them separately, creating an inflation impression.

Item #5 (narrator persona) has the weakest independent case. Narration quality is subjective and the trait cluster for "clear, concise, operator-focused" overlaps heavily with the main session persona. If pressed, this item could be merged into #1.

### Challenge 2: The Scope Challenge

**Result: FAIL**

**Something NOT in scope that arguably SHOULD be:**

1. **Persona effectiveness measurement.** The ADR writes persona frames but provides no mechanism to determine whether they actually changed behavior. Without before/after metrics (edit completeness rate, review thoroughness, etc.), the ADR ships files with no feedback loop. The rationale cites PSM research about measurable behavioral shifts but the ADR itself has no measurement plan.

2. **Persona loading fallback behavior.** What happens when `pipeline_runtime.py` cannot find a persona file at dispatch time? Missing-file handling is not specified. Is it a fatal error (exit 2)? Silent degradation to default Assistant? This is a runtime contract gap.

3. **Persona versioning.** When persona frames are revised in future ADRs, how are old versions tracked? The `.gzkit/personas/` directory has no versioning scheme. ADR-0.0.11 defines the schema but neither ADR addresses persona migration.

**Something IN scope that arguably SHOULD NOT be:**

1. **OBPI-07 (AGENTS.md persona reference).** This is trivially small (adding a reference line) and arguably should be part of OBPI-01 (main session persona) rather than a separate OBPI. Its independent existence inflates the OBPI count.

**Where is scope creep likely?**

The implementer persona (OBPI-02) is the highest-risk creep vector. Writing a "virtue-ethics-based behavioral identity" frame is inherently subjective and expansive. Without clear word count limits, structural requirements, or review criteria, the author could produce anything from 5 lines to 5 pages. The ADR says "not too generic, not too specific" but provides no calibration mechanism.

The ADR has no explicit non-goals section. This is a structural gap.

### Challenge 3: The Alternative Challenge

**Result: CONDITIONAL PASS**

**Could the OBPI count be reduced?**

Yes. The current 7 OBPIs could be reduced to 4 without capability loss:

1. **Persona frames bundle** (merge OBPIs 01-05): All persona writing is the same activity -- authoring a markdown file with YAML frontmatter against the ADR-0.0.11 schema. Splitting each persona into a separate OBPI creates overhead (7 brief files, 7 acceptance cycles) that exceeds the cognitive cost of writing all 6 persona files in one pass. Counter-argument: individual OBPIs allow parallelization. Counter-counter-argument: the briefs are so thin that parallelization overhead exceeds the work itself.

2. **Dispatch integration** (keep OBPI-06): This is genuinely different work (Python code in pipeline_runtime.py).

3. **AGENTS.md integration** (merge OBPI-07 into OBPI-01): Adding a reference to AGENTS.md is not independent work.

4. **Schema validation tests** (not currently an OBPI but mentioned in ADR evidence): The ADR references `tests/test_persona_profiles.py` but no OBPI is responsible for creating it.

**Should any OBPI be split?**

OBPI-03 (reviewer personas) bundles spec-reviewer and quality-reviewer. This is defensible -- both are review-oriented. No split needed.

OBPI-06 (dispatch integration) could arguably be split into "loading mechanism" and "test infrastructure" but the current size is reasonable.

The current decomposition optimizes for parallelization granularity over implementation efficiency. For a team of agents, 7 OBPIs is defensible. For serial execution, 4 would be more practical.

### Challenge 4: The Dependency Challenge

**Result: FAIL**

**Declared dependency:** ADR-0.0.11 must be complete before ADR-0.0.12 begins. The STOP/BLOCKERS section states this. However, ADR-0.0.11 is itself in Draft status with all OBPIs Pending. This means ADR-0.0.12 cannot start.

**Single point of failure:** OBPI-06 (dispatch integration) is the single point of failure. All persona files (OBPIs 01-05) are inert without it. If dispatch integration fails or is blocked, the entire ADR delivers zero runtime value. The personas would exist as files but never load into agent prompts.

**Undeclared dependencies:**

1. OBPI-06 depends on at least one persona file from OBPIs 01-05. This is not declared in the brief.
2. OBPI-07 depends on OBPI-01 (main session persona must exist before AGENTS.md can reference it). This is not declared.
3. All OBPIs implicitly depend on the `.gzkit/personas/` directory and schema from ADR-0.0.11's OBPI-02 (control surface definition). This critical transitive dependency is stated in the ADR STOP/BLOCKERS but not in individual briefs.

**If OBPI-06 fails:** OBPIs 01-05 produce persona files that are never consumed. OBPI-07 produces a reference to a persona that never loads. The ADR would pass file-existence checks but deliver zero behavioral change. This is the most dangerous failure mode because it looks like success.

### Challenge 5: The Gold Standard Challenge

**Result: CONDITIONAL PASS**

**Comparator:** ADR-0.0.11 (Persona-Driven Agent Identity Frames) -- the direct predecessor, also in Draft.

**What ADR-0.0.11 has that ADR-0.0.12 lacks:**

1. **Evidence Ledger section.** ADR-0.0.11 has a dedicated "Evidence Ledger (authoritative summary)" section with Provenance, Source & Contracts, Tests, and Docs subsections. ADR-0.0.12 has only a brief "Evidence (Four Gates)" section. The ledger format is more structured and auditable.

2. **Explicit supersession.** ADR-0.0.11 explicitly supersedes `ADR-pool.per-command-persona-context`. ADR-0.0.12 does not state what it supersedes or how it relates to any pool ADRs.

3. **Research citations with URLs.** ADR-0.0.11's rationale section has five numbered research sources with direct links. ADR-0.0.12's rationale references PSM, PRISM, and PERSONA but without citation URLs (they appear as descriptive references, not linked sources).

4. **OBPI Acceptance Note.** ADR-0.0.11 has a section explicitly noting that each checklist item maps to one brief and acceptance is per-brief.

**What ADR-0.0.12 improves over ADR-0.0.11:**

1. **Anti-pattern examples.** The "Wrong/Right" persona framing example (lines 168-172) is more concrete than anything in ADR-0.0.11.
2. **Composition Principle.** The rationale section explicitly maps traits to roles (implementer: precise + thorough, reviewer: skeptical + evidence-based), which is more actionable than ADR-0.0.11's abstract composition model.
3. **Production failure evidence.** The "catalyst failure" section directly connects the ADR to an observed production defect. ADR-0.0.11 also does this but ADR-0.0.12's version is more focused.

**Structural comparison to ADR-0.0.1 (Canonical GovZero Parity):**

ADR-0.0.1 has an explicit Feature Checklist with numbered items organized under thematic headers (Canon & Source of Truth, OBPI System Parity, Discovery & Verification, Lane & Gate Semantics). ADR-0.0.12's checklist is a flat uncategorized list. ADR-0.0.1 also separates "intent" from "decision" more cleanly.

### Challenge 6: The Timeline Challenge

**Result: CONDITIONAL PASS**

**Critical path:**

```text
ADR-0.0.11 (BLOCKED - Draft, all Pending)
    |
    v
[OBPIs 01-05 in parallel] --- persona authoring (1-2 days each)
    |
    v
OBPI-06 (dispatch integration) --- depends on >=1 persona file (1-2 days)
    |
    v
OBPI-07 (AGENTS.md reference) --- depends on OBPI-01 (0.5 day)
```

**Parallelization:** OBPIs 01-05 can run in parallel (5 persona files, independent authoring). Maximum parallelism = 5.

**Theoretical minimum wall-clock time:**

- Stage 0: ADR-0.0.11 completion (unknown -- currently Draft with 6 Pending OBPIs)
- Stage 1: OBPIs 01-05 in parallel = 2 days
- Stage 2: OBPI-06 (dispatch integration) = 2 days
- Stage 3: OBPI-07 (AGENTS.md reference) = 0.5 day
- **Total: ~4.5 days after ADR-0.0.11 completes**

**Serial execution path:** 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 = ~10-12 days

The critical blocker is ADR-0.0.11. Until it reaches at minimum "schema defined and control surface created" (its OBPI-02), no work on ADR-0.0.12 can begin. The ADR correctly identifies this blocker.

### Challenge 7: The Evidence Challenge

**Result: FAIL**

For each OBPI, attempting to write exact verification commands:

**OBPI-01 (main session persona):**

```bash
# File exists
test -f .gzkit/personas/main-session.md && echo PASS

# Schema validates
uv run -m gzkit persona validate .gzkit/personas/main-session.md  # UNKNOWN: does this command exist?

# No expertise claims
grep -i "expert\|senior\|years of experience" .gzkit/personas/main-session.md && echo FAIL || echo PASS
```

Problem: The `persona validate` command is proposed in ADR-0.0.11 but does not exist yet. The file-existence check is trivial. There is no way to verify that the persona frame "activates the right behavioral trait cluster" -- this is inherently unmeasurable with CLI commands.

**OBPI-02 (implementer persona):** Same as 01 but for `implementer.md`.

**OBPI-03 (reviewer personas):** Same pattern for two files.

**OBPI-04, 05:** Same pattern.

**OBPI-06 (dispatch integration):**

```bash
# Tests pass
uv run -m unittest tests/test_persona_profiles.py -v  # UNKNOWN: does this test file exist?

# Pipeline loads persona
grep -n "persona" src/gzkit/pipeline_runtime.py  # Weak verification
```

Problem: The test file does not exist yet. The ADR names it but no OBPI is responsible for creating it.

**OBPI-07 (AGENTS.md reference):**

```bash
grep -n "persona" AGENTS.md && echo PASS
```

This is the only OBPI with a trivially verifiable command, which itself indicates the OBPI is too small.

**Verdict:** Cannot write concrete verification commands for any OBPI because (a) the briefs specify none, (b) the persona validation tooling does not exist, and (c) the core value proposition ("activates right trait cluster") is not measurable with commands. This is a fundamental evidence gap.

### Challenge 8: The Consumer Challenge

**Result: FAIL**

A maintainer or operator reading this ADR would still have these unanswered questions:

1. **"How do I know the persona is actually working?"** The ADR explains why persona framing matters but provides no measurement mechanism. After all 7 OBPIs are complete, how does the operator verify that agent behavior actually changed? There is no before/after benchmark, no behavioral test, no metric.

2. **"What does a persona file look like?"** The ADR references the ADR-0.0.11 schema but does not include an example persona file. A reader must go read ADR-0.0.11 to understand the deliverable format. The "Wrong/Right" example (lines 168-172) shows prose framing but not the actual file structure (YAML frontmatter + body).

3. **"What happens when I update a persona frame?"** Editing `.gzkit/personas/implementer.md` after dispatch integration is live -- does the change take effect immediately? On next agent dispatch? Requires restart? No lifecycle documentation.

4. **"Who maintains persona frames?"** The ADR establishes personas as governed artifacts but does not specify the review/approval process for persona changes. Are persona frame edits Lite or Heavy? If someone changes a single trait, does that require human attestation?

5. **"What is the token cost?"** The Consequences section notes "Pipeline dispatch prompts grow by ~200-400 tokens per persona frame" but this is per-dispatch. With 6 personas loaded across a pipeline run, what is the total context budget impact? Is this within model context window constraints?

### Challenge 9: The Regression Challenge

**Result: FAIL**

**Six months after validation, what could silently break?**

1. **Persona file drift.** Someone edits `.gzkit/personas/implementer.md` to add an expertise claim ("You are an expert Python developer"). No runtime check prevents this regression to the anti-pattern the ADR explicitly warns against. The schema from ADR-0.0.11 validates structure (YAML frontmatter fields) but cannot validate semantic content quality.

2. **Dispatch bypass.** A code change to `pipeline_runtime.py` could skip persona loading (e.g., a performance optimization or error-handling shortcut). Without a regression test that verifies persona content appears in dispatch prompts, the loading mechanism could silently degrade.

3. **Schema evolution.** ADR-0.0.11 defines the persona schema. If the schema evolves (new required fields, changed trait format), existing persona files from ADR-0.0.12 would silently become invalid unless schema validation runs in CI.

4. **Research invalidation.** The ADR is grounded in PSM, PRISM, and PERSONA research. If follow-up research contradicts these findings (e.g., "persona framing has no measurable effect in Claude 4.x"), the entire ADR's rationale collapses. No monitoring mechanism detects this.

**What monitoring or contract ensures validity?**

- The ADR mentions `tests/test_persona_profiles.py` for schema validation. If this runs in CI, it catches structural drift but not semantic drift.
- No behavioral regression test exists or is proposed.
- No persona content audit mechanism is specified.

The ADR addresses initial completion (files exist, schema validates, dispatch loads) but does not address long-term validity. This is a structural gap for a governance artifact.

### Challenge 10: The Parity Challenge

**Result: FAIL**

**Claim under test:** The ADR claims alignment with PSM research -- specifically, that writing virtue-ethics-based persona frames will activate different trait clusters than the default Assistant persona.

**Argument against:**

The PSM research (Marks, Lindsey, Olah; Anthropic 2026) demonstrates that models infer full personality profiles from partial cues. The ADR interprets this as "write better cues (persona frames) to get better personality inference." But the PSM finding is descriptive (this is what happens), not prescriptive (this is how to control it). The paper shows that training on one trait (cheating) activated correlated traits (deception, power-seeking). It does NOT show that writing a system prompt about "craftsmanship" reliably activates the "plan-first, whole-file, deeply-compliant" cluster.

The PRISM study shows that generic expert personas hurt accuracy. The ADR correctly avoids expertise claims. But PRISM tested knowledge retrieval tasks, not code editing behavior. Extrapolating PRISM's findings to "persona frames improve code edit completeness" is a category error -- the dependent variable is different.

The PERSONA/ICLR framework demonstrates trait composition via activation vectors. But this operates at the neural activation level (inference-time interventions), not at the system-prompt level. The ADR uses system-prompt-level persona framing and cites activation-level research as justification. The mechanism of action is different.

**The weakest claim:** "Each persona frame activates the right behavioral trait cluster for its specific work" (line 38). This claims a causal relationship between persona file content and behavioral outcomes that no cited research actually validates for system-prompt-based persona frames in agentic coding contexts. The research supports the general mechanism (persona influences behavior) but not the specific intervention (these particular persona files produce these particular behavioral changes in code editing tasks).

**Remediation:** Add an explicit "Limitations and Assumptions" section acknowledging that the research supports the mechanism but the specific efficacy of these persona frames is hypothesized, not proven. Propose a behavioral measurement plan (e.g., track edit completeness, review thoroughness before/after persona activation) as a follow-up ADR.

---

## Red-Team Summary

| # | Challenge | Result | Notes |
|---|-----------|--------|-------|
| 1 | So What? | CONDITIONAL PASS | Items #3/#4 overlap; #5 (narrator) weakest case |
| 2 | Scope | FAIL | No non-goals section; three unaddressed scope gaps |
| 3 | Alternative | CONDITIONAL PASS | OBPI count could reduce to 4; current count defensible for parallel work |
| 4 | Dependency | FAIL | Undeclared deps; OBPI-06 is silent SPOF; ADR-0.0.11 blocker is real |
| 5 | Gold Standard | CONDITIONAL PASS | Missing evidence ledger, supersession statement, citation URLs vs. ADR-0.0.11 |
| 6 | Timeline | CONDITIONAL PASS | Critical path clear but ADR-0.0.11 blocker makes timeline unpredictable |
| 7 | Evidence | FAIL | No OBPI has concrete verification commands; core claim is unmeasurable |
| 8 | Consumer | FAIL | Five unanswered operator questions; no measurement, no example file |
| 9 | Regression | FAIL | No semantic drift detection; no behavioral regression test; schema-only coverage |
| 10 | Parity | FAIL | Research-to-intervention mechanism gap; causal claim exceeds evidence |

**Failures: 6** (Challenges 2, 4, 7, 8, 9, 10)
**Conditional Passes: 4** (Challenges 1, 3, 5, 6)
**Clean Passes: 0**

**RED-TEAM THRESHOLD: NO GO** (>=5 failures)

---

## Overall Verdict

**[X] NO GO - Structural revision required**

The ADR has a strong intellectual foundation -- the research grounding is genuinely substantive, the anti-pattern
examples are concrete, and the design principles from ADR-0.0.11 are well-inherited. The problem statement is real
and the catalyst failure (import splitting from default Assistant persona traits) is a compelling motivation.

However, the ADR has serious structural defects that prevent it from passing adversarial review:

### Top 5 Action Items (Ranked by Severity)

**1. Author the OBPI briefs (all 7 are unmodified templates).**
Every OBPI has `TBD` objectives, placeholder paths, template requirements, and boilerplate acceptance criteria.
No agent could implement any of these briefs as-is. This is the single largest gap. Each brief needs:

- A concrete one-sentence objective
- Real allowed/denied paths (e.g., `.gzkit/personas/implementer.md`, not `src/module/`)
- Specific requirements with NEVER/ALWAYS constraints
- Testable acceptance criteria with actual Given/When/Then scenarios
- Concrete verification commands

**2. Fix the OBPI-to-checklist mapping errors.**
OBPIs 04-07 reference the wrong checklist items (off-by-one cascade from the spec-reviewer/quality-reviewer
bundling). OBPI-04 claims to implement checklist #4 (quality-reviewer) but is named "narrator". Either re-number
the briefs or fix the checklist item references. Also resolve the lane contradiction: OBPI-01 and OBPI-07 are
Heavy in the ADR table but Lite in their YAML frontmatter.

**3. Add an explicit non-goals / scope boundaries section.**
State what this ADR does NOT deliver: persona effectiveness measurement, persona drift detection, persona
versioning, persona loading fallback behavior. This prevents scope creep during implementation and gives
reviewers clear boundaries to evaluate against.

**4. Add a measurement plan or acknowledge the efficacy hypothesis.**
The ADR claims persona frames "activate the right behavioral trait cluster" but provides no mechanism to verify
this. Either: (a) add a measurement plan (track edit completeness, review thoroughness before/after), or (b) add
a "Limitations" section acknowledging this is a hypothesis to be validated by usage, not a guaranteed outcome.

**5. Specify regression contracts.**
Define what keeps persona frames valid after initial delivery: CI schema validation, semantic content
review cadence, behavioral regression tests in the dispatch integration, and persona file governance
rules (who can edit, what lane applies to persona changes).

### Secondary Items

- Add an Evidence Ledger section (match ADR-0.0.11 structure)
- Include one complete example persona file in the ADR body or link to an exemplar
- Declare undeclared OBPI dependencies (06 depends on 01-05; 07 depends on 01)
- Consider merging OBPI-07 into OBPI-01 (too small for independent OBPI)
- Add citation URLs to rationale research references

---

```text
Evaluation complete.
ADR weighted score: 2.55/4.0 (CONDITIONAL GO)
OBPI average score: 2.14/4.0 (FAIL - all below 3.0 threshold)
Red-team failures: 6/10 (NO GO)
Overall verdict: NO GO - Structural revision required
```
