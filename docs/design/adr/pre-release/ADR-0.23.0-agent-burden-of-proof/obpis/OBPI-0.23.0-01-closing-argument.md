---
id: OBPI-0.23.0-01-closing-argument
parent: ADR-0.23.0-agent-burden-of-proof
item: 1
lane: Lite
status: Completed
---
<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.23.0-01 — Value Narrative Becomes Closing Argument

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.23.0-agent-burden-of-proof/ADR-0.23.0-agent-burden-of-proof.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.23.0-01 — "Value narrative becomes closing argument — earned from delivered evidence, not echoed from planning"`

## ADR ALIGNMENT

1. **Critical Constraint:**
   > ADR states: "Implementations MUST ensure the burden of proof falls on the completing agent at the END of the run."
   >
   > In my own words: The value narrative must be written AFTER the work is done, from evidence of what was actually delivered, not copied from the planning brief's intent section.

2. **Integration Points:**
   > This OBPI must integrate with: `.github/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md` (template change), existing OBPI briefs (migration guidance)

3. **Anti-Pattern:**
   > A failed implementation would: rename "Value Narrative" to "Closing Argument" but keep the same mechanical fill-in-the-blank structure that agents can complete without engaging with what was actually delivered.

4. **Alignment Check:**
   > - [x] **YES** — Proceed. Reasoning: Changing the template section from a planning echo to an earned-evidence closing argument directly serves the burden-of-proof constraint.

## OBJECTIVE

Redefine the OBPI brief Value Narrative section as a "Closing Argument" that agents must author at completion time from delivered evidence. The section must articulate: what was built, what it enables for the operator, and why it matters — all substantiated by artifacts, not planning intent.

## ROLE

**Agent Identity:** Governance template architect

**Success Behavior:** Create a Closing Argument template that forces agents to reference specific delivered artifacts and operator-facing documentation.

**Failure Behavior:** Creating a renamed section with the same mechanical structure that agents can fill without thinking about the operator.

## ASSUMPTIONS

- The current "Value Narrative" section exists in recent briefs (confirmed in ADR-0.17.0+ OBPIs)
- Existing completed briefs do not need retroactive migration
- New and in-progress briefs will adopt the updated template

## NON-GOALS

- Retroactive migration of completed OBPIs
- Automated scoring of closing argument quality (that's the reviewer agent's job, OBPI-03)

## CHANGE IMPACT DECLARATION

- [x] **YES** — External contract changes detected: OBPI brief template is an agent-facing contract. This OBPI is Lite because the template change is internal governance tooling, but the parent ADR is Heavy.

## LANE

Lite — Template file change, unit test for template validation.

## ATTESTATION REMINDER

- [ ] **Parent ADR is Heavy/Foundation** → **STOP — Human attestation required**

## ALLOWED PATHS

- `.github/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md`
- `tests/test_obpi_template.py`

## REQUIREMENTS (FAIL-CLOSED)

1. Rename "Value Narrative" section to "Closing Argument" in the OBPI brief template
1. Add guidance: "This section is authored at COMPLETION, not during planning. Write from delivered evidence."
1. Require three elements: (a) what was built (artifact paths), (b) what it enables (operator capability), (c) why it matters (with proof command or documentation link)
1. Add template validation test: Closing Argument section must exist and must not contain planning-phase placeholder text

## EDGE CASES

- Brief started under old template but completed under new: migration guidance in template comments
- Agent copies planning intent verbatim: reviewer agent (OBPI-03) catches this

## QUALITY GATES

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Template validation test written
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Verification Commands (Concrete)

```bash
# Prove template change landed
grep -c "Closing Argument" .github/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md
# Expected: >= 1

# Prove old section name is gone from template
grep -c "Value Narrative" .github/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md
# Expected: 0 (or only in migration comment)

# Prove template validation test exists and passes
uv run -m unittest tests.test_obpi_template -v
# Expected: OK

# Prove guidance text requires completion-time authoring
grep "authored at COMPLETION" .github/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md
# Expected: match found
```

## Closing Argument

1. **What was built** — Added `### Closing Argument (Lite)` and `### Closing Argument (Heavy)` sections to `.github/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md`, with migration comments for briefs started under the old template. Created `tests/test_obpi_template.py` with 6 validation tests.

2. **What it enables** — Agents completing OBPI briefs now have structured guidance requiring them to substantiate their closing argument from delivered artifacts: what was built (paths), what it enables (operator capability), and why it matters (proof command). This replaces the mechanical "Value Narrative" fill-in with an earned-evidence standard.

3. **Why it matters** — `uv run -m unittest tests.test_obpi_template -v` proves the template enforces the new structure: Closing Argument sections exist in both lanes, Value Narrative headings are absent, completion-time authoring guidance is present, and planning-phase placeholders are rejected.

### Implementation Summary

- Files created: `tests/test_obpi_template.py` (6 tests)
- Files modified: `.github/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md` (Lite + Heavy Closing Argument sections)
- Date completed: 2026-03-28
- Attestation status: Human attested
- Defects noted: None

### Key Proof

```text
$ uv run -m unittest tests.test_obpi_template -v
test_authored_at_completion_guidance ... ok
test_closing_argument_in_both_lanes ... ok
test_closing_argument_section_exists ... ok
test_no_planning_phase_placeholders_in_closing_argument ... ok
test_no_value_narrative_heading ... ok
test_three_required_elements ... ok
----------------------------------------------------------------------
Ran 6 tests in 0.001s
OK
```
