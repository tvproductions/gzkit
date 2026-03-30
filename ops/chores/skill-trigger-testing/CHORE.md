# CHORE: Skill Trigger & Output Testing

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `skill-trigger-testing`

---

## Overview

Measure whether skills trigger correctly on agent goal statements and produce outputs matching their declared contracts. Structural quality (checked by `skill-authoring-quality`) is necessary but not sufficient — a well-formatted description that doesn't match real agent goals is a skill that never fires. This chore closes the gap between structural lint and functional quality.

## Policy and Guardrails

- **Lane:** Lite — read-only analysis, no skill modifications
- Tests use synthetic goal statements, not live agent runs
- Results are tracked per-skill per-version for regression detection
- This chore does NOT modify skills — it produces a diagnostic report

## Workflow

### 1. Build Goal Basket

For each skill, create 3-5 synthetic goal statements that represent:

- **True positive:** A goal the skill SHOULD trigger on (based on its description)
- **True negative:** A goal the skill should NOT trigger on (adjacent skill's domain)
- **Edge case:** A goal at the boundary of the skill's scope

Source goal language from:

- Actual agent invocation patterns in `.claude/plans/`
- OBPI brief objectives
- User-facing runbook workflows

### 2. Description-Goal Alignment Scoring

For each skill, assess whether the description text contains enough signal to match its true-positive goals:

| Score | Meaning |
|-------|---------|
| **Strong** | Description keywords directly overlap with goal language |
| **Weak** | Description is accurate but uses different vocabulary than goals |
| **Miss** | Description doesn't mention the outcome the goal seeks |

Flag skills scoring Weak or Miss — these undertrigger in agent contexts.

### 3. Output Contract Verification

For skills that declare an output format:

- Does the skill body contain enough instruction to produce that format?
- Are required fields/sections named explicitly?
- Would a downstream agent/skill be able to parse the output?

For skills that don't declare an output format:

- Flag as **contract-missing** if the skill produces artifacts

### 4. Regression Tracking

Save results to `ops/chores/skill-trigger-testing/proofs/trigger-report-{date}.md` with:

```markdown
| Skill | Version | Goals Tested | Alignment | Contract | Regression |
|-------|---------|-------------|-----------|----------|------------|
```

Compare against previous report to detect regressions (skill description changed but alignment score dropped).

### 5. Validate

```bash
uv run -m unittest -q
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |

## Evidence Commands

```bash
# Report saved during workflow step 4
ls ops/chores/skill-trigger-testing/proofs/trigger-report-*.md
```

## Relationship to Other Chores

| Chore | What it checks | Gap this chore fills |
|-------|---------------|---------------------|
| `skill-authoring-quality` | Structural quality (frontmatter, size, stubs) | Functional quality (does it trigger? does it produce?) |
| `skill-command-doc-parity` | Documentation coverage | Runtime accuracy |
| `skill-manifest-sync` | Directory sync | N/A (orthogonal) |

---

**End of CHORE: Skill Trigger & Output Testing**
