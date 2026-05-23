# Plan: OBPI-0.0.57-05-docs-runbook-fixtures

**OBPI:** `OBPI-0.0.57-05-docs-runbook-fixtures`
**ADR:** `ADR-0.0.57-foundation-adr-nominal-id-triage`
**Lane:** Heavy (Gates 2, 3, 4, 5)
**Brief:** `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/obpis/OBPI-0.0.57-05-docs-runbook-fixtures.md`

---

## ADR Decision Item (verbatim)

> OBPI-0.0.57-05: **docs-runbook-fixtures** — Update gz-adr-create manpage and governance runbook for nominal-ID allocation; add examples and fixtures for Foundation Triage invocation.

---

## Context

### What already exists (from sibling OBPIs)

- `docs/user/manpages/plan-create.md` — exists; `--kind` option already mentions nominal allocation in one sentence (OBPI-02 added this). Does NOT yet have a worked gap-allocation example.
- `.gzkit/skills/gz-foundation-triage/SKILL.md` — full skill body with 3-step triage procedure (OBPI-03 surface).
- `.gzkit/skills/gz-foundation-triage/scripts/triage.py` — deterministic script for Step 1 (json) and Step 3 (rank) output.
- `src/gzkit/foundation/rubric.py` — rubric scoring module: `EvidenceRef`, `FoundationTriageRankEntry`, priority_score formula `insights×3 + ghi_occurrence×2 + feature_unblocking×5` (OBPI-04 surface).
- `features/plan_create_nominal.feature` — BDD scenarios for nominal allocator CLI behavior (OBPI-02 surface). Do not modify.
- `tests/test_foundation_triage_rubric.py` — rubric unit tests (OBPI-04 surface). Do not modify.

### What does NOT exist yet (this OBPI creates)

- `docs/user/manpages/foundation-triage.md` — **CREATE**
- `features/foundation_triage.feature` — **CREATE**
- `tests/fixtures/foundation_triage_e2e/` — **CREATE**
- `tests/test_foundation_triage_e2e.py` — **CREATE**

### Key constraints

- REQ-7: EXAMPLES sections in manpages MUST contain real CLI output captured from a fixture run — no placeholders.
- REQ-3: `features/foundation_triage.feature` MUST encode at least two scenarios: nominal-allocator gap-allocation AND foundation-triage skill invocation; `uv run -m behave features/foundation_triage.feature` MUST pass.
- REQ-6: Both runbooks MUST be updated in same OBPI per three-layer documentation covenant.
- `gz validate --cli-alignment` MUST exit 0 — foundation-triage is a skill (invoked via `/gz-foundation-triage`), not a CLI verb; no `gz foundation-triage` references in docs.

---

## Files

### Modified
- `docs/user/manpages/plan-create.md` — add worked nominal-allocator gap-allocation example section with real output
- `docs/user/runbook.md` — add `## Foundation Triage` section under Governance Planning Commands
- `docs/governance/governance_runbook.md` — add nominal allocation guidance to "Create or Promote ADR" workflow; add foundation-triage to governance maintainer planning workflow

### Created
- `docs/user/manpages/foundation-triage.md` — skill-level manpage (not CLI command)
- `features/foundation_triage.feature` — 2 BDD scenarios
- `features/steps/foundation_triage_steps.py` — BDD steps for triage script invocation
- `tests/fixtures/foundation_triage_e2e/` — e2e fixture directory
  - `tests/fixtures/foundation_triage_e2e/insights.jsonl` — agent-insights records mentioning specific foundation ADRs
  - `tests/fixtures/foundation_triage_e2e/pool_adrs/ADR-pool.unblocked-by-0.0.2.md` — pool ADR with `depends_on: [ADR-0.0.2]`
  - `tests/fixtures/foundation_triage_e2e/pool_adrs/ADR-pool.port-adapter-candidate.md` — pool ADR that's a reclassification candidate
  - `tests/fixtures/foundation_triage_e2e/foundation_adrs/ADR-0.0.1-fixture-one/ADR-0.0.1-fixture-one.md` — Draft, high signals
  - `tests/fixtures/foundation_triage_e2e/foundation_adrs/ADR-0.0.2-fixture-two/ADR-0.0.2-fixture-two.md` — Draft, medium signals
  - `tests/fixtures/foundation_triage_e2e/foundation_adrs/ADR-0.0.4-fixture-four/ADR-0.0.4-fixture-four.md` — Proposed, low signals (gap at 3)
- `tests/test_foundation_triage_e2e.py` — E2E integration tests

---

## Steps

### Step 1: Create E2E fixture (`tests/fixtures/foundation_triage_e2e/`)

Create the fixture directory structure with:

**Foundation ADR stubs** (IDs 1, 2, 4 — gap at 3):
- `ADR-0.0.1-fixture-one`: status Draft, title "Fixture Foundation One"
- `ADR-0.0.2-fixture-two`: status Draft, title "Fixture Foundation Two"
- `ADR-0.0.4-fixture-four`: status Proposed, title "Fixture Foundation Four"

Each ADR file must have YAML frontmatter with `id`, `status`, `title`.

**Insights file** (`insights.jsonl`):
- Several records mentioning `ADR-0.0.1` (2 records, with GHI #100)
- One record mentioning `ADR-0.0.2` (1 record, no GHI)
- No records mentioning `ADR-0.0.4`

**Pool ADR with depends_on** (`pool_adrs/ADR-pool.unblocked-by-0.0.2.md`):
- frontmatter: `depends_on: [ADR-0.0.2]`
- This drives feature_unblocking=1 for ADR-0.0.2

**Pool ADR reclassification candidate** (`pool_adrs/ADR-pool.port-adapter-candidate.md`):
- A pool ADR whose intent describes an invariant (suitable for foundation reclassification)

Expected priority scores (weights: insights×3 + ghi_occurrence×2 + feature_unblocking×5):
- ADR-0.0.1: insights=2, ghi=1, unblocking=0 → score=8
- ADR-0.0.2: insights=1, ghi=0, unblocking=1 → score=8
- ADR-0.0.4: insights=0, ghi=0, unblocking=0 → score=0

### Step 2: Create `tests/test_foundation_triage_e2e.py`

TDD: write tests derived from brief requirements, using the fixture from Step 1.

Three test classes:

**`TestRubricScoringE2E`** (@covers REQ-0.0.57-05-04):
- `test_priority_score_formula`: calls `rubric.score_foundation(adr_id, repo_root)` against fixture dir, verifies scores for ADR-0.0.1 (expected ≥ score for ADR-0.0.4).
- Use `src/gzkit/foundation/rubric.py`'s scoring logic directly (not via subprocess).

**`TestNominalAllocatorE2E`** (@covers REQ-0.0.57-05-04):
- `test_gap_fill_suggests_0_0_3`: creates a temp workspace with foundation ADRs for IDs 1, 2, 4; invokes `gz plan create fixture --kind foundation --semver 99.0.0 --dry-run` via `gzkit.cli.main`; asserts output/error mentions "0.0.3".
- Reuses pattern from `tests/commands/test_plan.py` or similar.

**`TestTriageScriptE2E`** (@covers REQ-0.0.57-05-04):
- `test_json_output_shape`: runs triage.py `--format json` against fixture dir (via subprocess), parses output as JSON, asserts it's a list of records each with `id`, `status`, `title`, `insight_count`, `ghi_count`, `invariant_mentions`.
- `test_fixture_adr_ids_present`: verifies ADR-0.0.1 and ADR-0.0.2 appear in the JSON records.

Test file must NOT import from `pytest` — stdlib `unittest` only per STDLIB-FIRST doctrine.

### Step 3: Update `docs/user/manpages/plan-create.md`

Add a new subsection **"## Nominal Allocator — Gap-Filling Example"** after the existing `## Example` section.

Content requirements:
- Explain that foundation IDs are nominal (not sequential); the allocator finds the lowest free integer.
- Show what happens when you specify a semver that's already taken: error with the gap hint.
- Show the correct invocation using the suggested gap ID.
- EXAMPLES MUST contain real CLI output: run `gz plan create` commands in a temp workspace matching the fixture (IDs 1, 2, 4 present → gap at 3) and capture actual output.

To get real output, run this in a temp gzkit-initialized workspace:
```bash
# Create temp workspace with IDs 1,2,4
# Then:
gz plan create my-adr --kind foundation --semver 0.0.5 --dry-run 2>&1
# Should show error with "0.0.3" hint
```

Capture actual output and embed verbatim.

### Step 4: Create `docs/user/manpages/foundation-triage.md`

New manpage following the skill-manpage template (not CLI verb template). Structure:

```
# gz-foundation-triage

[description paragraph]

## Invocation

[invocation as skill]

## Description

[what it does, three steps, ephemeral output]

## Signal Dimensions

[table of rubric dimensions: insights_signal, ghi_occurrence, feature_unblocking — weights cross-referencing OBPI-04]

## Steps

[the three steps from SKILL.md condensed]

## Example

[real output from running triage.py --format json against the e2e fixture]

## Notes

[ephemeral property, diagnosis-only note]
```

For real output: run `uv run python .gzkit/skills/gz-foundation-triage/scripts/triage.py --format json` against a workspace containing the e2e fixture data, capture actual JSON output, embed a representative excerpt.

Add `foundation-triage.md` entry to `docs/user/manpages/index.md` under a "Skills" or "Governance Planning" section.

### Step 5: Update `docs/user/runbook.md`

Add a new `## Foundation Triage` section. Best location: after `## Governance Planning Commands` subsection near line 860, or near the end of the "Skill Commands" section (~line 1076).

Content:
- When to run (quarterly or when prioritizing foundation backlog)
- The three steps (invoke skill `/gz-foundation-triage`)
- What to do with the ephemeral ranked output (operator decision, not auto-promotion)
- Cross-reference to `foundation-triage.md` manpage

### Step 6: Update `docs/governance/governance_runbook.md`

Two additions:

**In "Workflow: Create or Promote ADR" (~line 330):**
Add a note after the `gz plan create --kind foundation` steps explaining nominal ID allocation semantics and how to interpret the gap-allocation error hint.

**New "## Foundation-Triage Planning Workflow" subsection** (add near `## Workflow: Readiness-Driven Design`):
- When a governance maintainer runs foundation triage
- How to interpret the ranked output
- Promotion decision remains manual (`gz adr promote`, operator-driven)
- Cross-reference to operator runbook section

### Step 7: Create `features/foundation_triage.feature`

Two scenarios, using `@REQ-0.0.57-05-03` tag:

**Scenario 1: nominal-allocator gap allocation**
```gherkin
@REQ-0.0.57-05-03
Scenario: nominal-allocator gap-allocation suggests lowest free integer
  Given the workspace is initialized in heavy mode
  And foundation ADRs exist for IDs "1,2,4"
  When I run the gz command "plan create gap-test --kind foundation --semver 0.0.5 --dry-run"
  Then the command exits with code 1
  And the output contains "0.0.3"
```

(Reuses existing steps from `plan_create_nominal_steps.py` — no new steps needed for this scenario.)

**Scenario 2: foundation-triage skill invocation**
```gherkin
@REQ-0.0.57-05-03
Scenario: foundation-triage script produces structured JSON from in-flight foundations
  Given a foundation-triage fixture with ADRs "ADR-0.0.1,ADR-0.0.2" and insights mentioning "ADR-0.0.1"
  When I run the foundation-triage script with format "json"
  Then the output is valid JSON
  And the JSON contains an entry with id containing "ADR-0.0.1"
```

(Needs new steps in `features/steps/foundation_triage_steps.py`.)

### Step 8: Create `features/steps/foundation_triage_steps.py`

New step definition file for the foundation-triage BDD scenario. Steps needed:

- `Given a foundation-triage fixture with ADRs "{adr_ids}" and insights mentioning "{mention_id}"` — creates a temp workspace with stub foundation ADRs and minimal insights.jsonl, wires it up so the triage script can find it.
- `When I run the foundation-triage script with format "{format}"` — runs `python .gzkit/skills/gz-foundation-triage/scripts/triage.py --format {format} --root {tmp_path}` via subprocess; stores stdout in `context.triage_output`.
- `Then the output is valid JSON` — parses `context.triage_output` as JSON.
- `Then the JSON contains an entry with id containing "{pattern}"` — asserts at least one record's `id` matches.

The step implementation must pass a `--root` flag to the triage script (or set CWD) so it scans the test workspace, not the live repo. Check whether `triage.py` supports a root override or CWD-based resolution.

### Step 9: Verify gates (run in sequence)

```bash
# Gate 2: tests
uv run gz arb step --name unittest -- uv run -m unittest tests.test_foundation_triage_e2e -v
uv run gz arb step --name unittest -- uv run -m unittest -q

# Code quality
uv run gz arb ruff
uv run gz arb typecheck

# REQ parity
uv run gz covers OBPI-0.0.57-05-docs-runbook-fixtures --json

# Gate 3: docs
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --cli-alignment
uv run gz cli audit

# Gate 4: BDD
uv run -m behave features/foundation_triage.feature --no-capture

# Existence checks
test -f docs/user/manpages/plan-create.md
test -f docs/user/manpages/foundation-triage.md
grep -q "foundation-triage" docs/user/runbook.md
grep -q "foundation-triage" docs/governance/governance_runbook.md
grep -q "nominal" docs/user/manpages/plan-create.md
ls tests/fixtures/foundation_triage_e2e/ > /dev/null
uv run gz validate --documents
```

---

## Verification

Same as Step 9 above.

---

## Notes

- **Step 8 triage.py root flag**: The triage script currently resolves repo root from `_project_root_from_script()` (its own location). To use it against a test fixture, the step definition must either (a) patch the root resolution, (b) check if the script accepts a `--root` CLI arg, or (c) set up the fixture in a structure the script can discover from a temp CWD. Inspect `triage.py` at time of step authoring.
- **Scope-collision advisories** are informational only — 89 sibling OBPI collisions for shared docs surfaces like `runbook.md`. All are from completed OBPIs; no active locks contesting these paths.
- **REQ-1 manpage template compliance**: plan-create.md already has description, usage, options, examples, exit codes per `.claude/rules/cli.md`. The update only adds a new subsection; template compliance is maintained.
