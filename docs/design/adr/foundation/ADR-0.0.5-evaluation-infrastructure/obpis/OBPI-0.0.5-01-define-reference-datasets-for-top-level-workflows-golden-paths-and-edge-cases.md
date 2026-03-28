---
id: OBPI-0.0.5-01-define-reference-datasets-for-top-level-workflows-golden-paths-and-edge-cases
parent: ADR-0.0.5-evaluation-infrastructure
item: 1
lane: lite
status: Completed
---

# OBPI-0.0.5-01: Define Reference Datasets

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.5-evaluation-infrastructure/ADR-0.0.5-evaluation-infrastructure.md`
- **Checklist Item:** #1 - "Reference datasets for top-level workflows (golden paths and edge cases)"

**Status:** Completed

## Objective

Create versioned JSON fixtures under `data/eval/` containing golden-path
input/output pairs for each AI-sensitive surface so eval harnesses have
deterministic baselines to score against.

**Golden path** means: the expected output for a known-good input that exercises
the primary success path of the surface. **Edge case** means: inputs that test
boundary conditions (empty input, malformed input, maximum-length input).

Per-surface dataset scope:

| Surface | Golden-path examples | Edge-case examples |
|---------|---------------------|-------------------|
| `instruction_eval.py` | Correct agent loading for each vendor | Missing instruction file, empty rules directory |
| `adr_eval.py` | Well-formed ADR scoring all 8 dimensions | ADR with no decisions, ADR with no OBPIs |
| Skills (`SKILL.md`) | Skill with all required sections | Skill missing trigger, skill with empty procedure |
| Rules (`.claude/rules/`) | Rule with correct frontmatter and paths | Rule with no paths glob, rule with stale path |
| `AGENTS.md` | Complete operating contract | Contract missing required sections |

## Lane

**Lite** - Data fixtures and schema definitions only. No CLI, API, or
operator-facing changes.

## Allowed Paths

- `data/eval/` - reference dataset JSON fixtures
- `data/schemas/` - eval dataset JSON schema
- `tests/eval/` - dataset validation tests
- `src/gzkit/eval/` - dataset loader module

## Denied Paths

- `src/gzkit/commands/` - no CLI changes
- `src/gzkit/cli/` - no CLI changes
- `docs/user/` - no operator docs changes
- `.claude/rules/` - no rule changes

## Requirements (FAIL-CLOSED)

1. EVERY dataset MUST be valid JSON with a schema-validated structure.
2. EVERY dataset MUST be reproducible -- no timestamps, random seeds, or
   environment-dependent values in fixture data.
3. Datasets MUST NOT require network access to load or validate.
4. EVERY AI-sensitive surface listed in the ADR MUST have at least one
   golden-path dataset and one edge-case dataset.
5. Dataset files MUST be small enough that the full eval suite runs within the
   60-second smoke test budget.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] `src/gzkit/instruction_eval.py` lines 73-178 - existing 10-case baseline pattern
- [ ] `src/gzkit/adr_eval.py` - ADR scoring dimensions and checklist structure
- [ ] `data/schemas/` - existing schema patterns

**Prerequisites (check existence, STOP if missing):**

- [ ] `data/` directory exists
- [ ] `data/schemas/` directory exists

**Existing Code (understand current state):**

- [ ] `tests/test_instruction_eval.py` - test patterns for eval cases

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification
python -c "import json; json.load(open('data/eval/instruction_eval_golden.json'))"
uv run -m unittest tests/eval/test_datasets.py -v
```

## Acceptance Criteria

- [x] **REQ-0.0.5-01-01:** [doc] `data/eval/` contains at least one golden-path and
  one edge-case fixture per AI-sensitive surface listed in the ADR.
- [x] **REQ-0.0.5-01-02:** [doc] A JSON schema in `data/schemas/` validates the
  dataset structure, and a test loads every fixture and validates it.
- [x] **REQ-0.0.5-01-03:** A dataset loader in `src/gzkit/eval/` loads fixtures
  by surface name and returns typed Pydantic models.
- [x] **REQ-0.0.5-01-04:** [doc] All dataset validation tests pass within 10 seconds.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 17 tests in 0.004s — OK
Coverage: 72% (src/gzkit/eval/datasets.py)
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

### Value Narrative

OBPIs 02-04 in ADR-0.0.5 (eval harnesses, release gates, regression detection) need
deterministic reference data to score against. This OBPI externalizes that data as
versioned JSON fixtures so harnesses can load baselines without hardcoding them inline.

### Key Proof

```python
from gzkit.eval.datasets import load_dataset, list_surfaces
list_surfaces()  # ['adr_eval', 'agents_md', 'instruction_eval', 'rules', 'skills']
ds = load_dataset("instruction_eval")
# EvalDataset(surface='instruction_eval', version='1.0.0', cases=[...3 cases...])
```

### Implementation Summary

- Files created: data/schemas/eval_dataset.schema.json, data/eval/{5 fixtures}, src/gzkit/eval/{__init__,datasets}.py, tests/eval/{__init__,test_datasets}.py
- Tests added: 17 (6 test classes covering schema, fixtures, coverage, loader, reproducibility, custom dirs)
- Date completed: 2026-03-26
- Attestation status: Human attested (Accepted)
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: Jeff
- Attestation: Accepted — foundation data layer for eval infrastructure. OBPIs 02-04 deferred until concrete trigger.
- Date: 2026-03-26

---

**Brief Status:** Completed
**Date Completed:** 2026-03-26
**Evidence Hash:** -
