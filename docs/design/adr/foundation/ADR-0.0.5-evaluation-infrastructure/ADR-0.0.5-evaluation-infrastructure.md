---
id: ADR-0.0.5-evaluation-infrastructure
status: Pending
semver: 0.0.5
parent: PRD-GZKIT-1.0.0
lane: lite
---

# ADR-0.0.5: Evaluation Infrastructure

## Status

Pending

## Date

2026-02-11 (authored), 2026-03-26 (revised)

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Phase 8: Evaluation Infrastructure

---

## Problem Statement

gzkit's quality stack is entirely deterministic: ruff, ty, unittest, mkdocs, and
structural gate checks verify *code correctness* but cannot detect regressions in
*non-deterministic AI-assisted behavior*. When a model changes, a prompt is
updated, or an instruction surface is modified, there is no systematic way to
measure whether the quality of AI-assisted workflows improved or regressed.

**Before:** Model/prompt/instruction changes ship with code-level QA only (lint,
type, test). Non-deterministic behavior regressions are discovered post-deployment
by operators through manual observation.

**After:** Reference datasets define expected behavior for AI-sensitive surfaces.
Offline eval harnesses measure quality before merge. Eval deltas gate releases.
Regressions are caught before they reach operators.

**So what:** Without eval infrastructure, every instruction surface change, skill
update, or model migration is a blind deployment. The existing `instruction_eval.py`
10-case baseline proves the concept works at small scale -- this ADR scales it to
cover all AI-sensitive surfaces with regression detection.

---

## Decisions

### Decision 1: Reference datasets as versioned JSON fixtures

Store expected input/output pairs as versioned JSON fixtures under `data/eval/`.

**Why:** Deterministic baselines enable before/after comparison without network
calls or LLM invocations. Fixtures are fast, reproducible, and auditable.

**Alternatives considered:**
- *Live API calls per eval run* -- rejected: introduces flakiness, network
  dependency, and cost. Violates test policy (no external services).
- *Inline test expectations* -- rejected: cannot be shared across harnesses or
  versioned independently of code.

**Precedent:** `instruction_eval.py` (lines 73-178) already defines 10 baseline
cases as structured Python objects. This decision externalizes and scales that
pattern.

### Decision 2: Eval harnesses as unittest extensions

Build eval harnesses using stdlib `unittest`, consistent with test policy.

**Why:** No new framework needed. Eval results feed into Gate 2 (TDD) through
the existing `quality.py` runner infrastructure. Agents already know how to run
`uv run gz test`.

**Alternatives considered:**
- *Custom eval framework* -- rejected: over-engineering. unittest with
  table-driven cases provides everything needed.
- *pytest* -- rejected: violates test policy (stdlib unittest only).

**Precedent:** `tests/test_instruction_eval.py` already uses this pattern.

### Decision 3: Delta-based scoring for regression detection

Eval results produce numeric scores per dimension. A regression detector compares
current scores against a stored baseline and flags regressions beyond a
configurable threshold.

**Why:** Absolute thresholds are fragile and require constant tuning. Delta-based
comparison is resilient to baseline drift and naturally adapts as the system
improves.

**Alternatives considered:**
- *Binary pass/fail per case* -- rejected: doesn't capture partial regressions.
  A surface could degrade 30% and still pass all individual cases.
- *LLM-as-judge scoring* -- rejected: introduces non-determinism into the eval
  itself. Out of scope (see Non-Goals).

### Decision 4: Integrate into Gate 2, not a new gate

Eval results flow through the existing Gate 2 (TDD) pipeline as specialized test
suites, not as a new Gate 6.

**Why:** Adding a gate would require updating every gate consumer (gates.py,
ledger events, status rendering, skill templates, runbooks). Evals are tests for
non-deterministic behavior -- they belong in the test gate.

**Precedent:** `gates.py` Gate 2 (lines 57-82) already runs `uv run -m unittest`
and captures pass/fail. Eval harnesses produce unittest results.

---

## Feature Checklist

1. **Reference datasets** for top-level workflows (golden paths and edge cases)
2. **Offline eval harnesses** as first-class quality checks
3. **Eval-delta release gates** for AI-sensitive surfaces
4. **Regression detection** for model/prompt changes before high-agency rollout

---

## AI-Sensitive Surfaces (Target Coverage)

These are the surfaces where changes affect non-deterministic AI behavior:

| Surface | Current coverage | Gap |
|---------|-----------------|-----|
| `instruction_eval.py` baseline (10 cases) | 4-dimension readiness scoring | No regression detection across commits |
| `adr_eval.py` ADR scoring (8 dimensions) | Deterministic keyword/structural | No golden-path validation |
| Skills (`SKILL.md` content) | Structural validation only | No behavioral eval |
| Rules (`.claude/rules/`) | Drift detection via `instruction_audit.py` | No quality scoring |
| `AGENTS.md` operating contract | None | No eval coverage |

---

## Non-Goals

- **Real-time production monitoring** -- runtime observability is a separate
  concern (ADR-pool.ai-runtime-foundations). This ADR covers pre-release quality
  measurement only.
- **LLM-as-judge evaluation** -- all scoring in this ADR is deterministic
  (structural, keyword, delta comparison). LLM-powered evaluation (like the
  existing red-team challenge system) is out of scope.
- **Cost or latency tracking** -- performance metrics are not quality metrics.
- **Model training or fine-tuning** -- gzkit consumes models, it does not
  train them.
- **Expanding the gate model** -- no new gates. Eval integrates into Gate 2.

---

## OBPI Decomposition

| # | OBPI | Lane | Dependencies |
|---|------|------|-------------|
| 01 | Reference datasets | Lite | None |
| 02 | Eval harnesses | Lite | None (uses test fixtures; production data from 01) |
| 03 | Eval-delta release gates | Lite | 02 (needs scoring output). Lite because it adds signals within existing Gate 2, not a new gate or CLI command. If gate output format changes become operator-visible, reassess to Heavy. |
| 04 | Regression detection | Lite | 02 (needs scoring output) |

**Critical path:** 2 stages deep. OBPIs 01 and 02 run in parallel. OBPIs 03
and 04 run in parallel after 02 completes.

**Parallelization:** 2 agents can work simultaneously at each stage.

---

## Dependencies

None. The existing quality infrastructure provides all required integration points:

- `quality.py` -- quality runners and `QualityResult` model
- `gates.py` -- Gate 2 (TDD) integration
- `instruction_eval.py` -- pattern exemplar for eval case design
- `adr_eval.py` -- pattern exemplar for dimension scoring

---

## Architectural Integration Points

| Integration | Module | Purpose |
|------------|--------|---------|
| Quality runners | `src/gzkit/quality.py` | Add `run_eval()` alongside `run_tests()` |
| Gate 2 | `src/gzkit/commands/gates.py` | Eval harness feeds into TDD gate |
| ARB receipts | `src/gzkit/commands/arb_cmd.py` | Eval runs produce structured receipts |
| Scoring models | `src/gzkit/core/scoring.py` | Extend with eval-specific scorecard |
| Test infrastructure | `tests/eval/` | New test directory for eval harnesses |
| Data fixtures | `data/eval/` | Reference datasets as versioned JSON |

---

## Notes

- This phase treats evals as tests for non-deterministic behavior, not as
  optional analytics.
- Dataset curation and rubric versioning should be traceable in governance
  artifacts.
- The existing `instruction_eval.py` 10-case baseline is the proof of concept.
  This ADR scales that pattern to all AI-sensitive surfaces.
