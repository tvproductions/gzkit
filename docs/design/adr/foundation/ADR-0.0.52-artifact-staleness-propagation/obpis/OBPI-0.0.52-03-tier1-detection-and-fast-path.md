---
id: OBPI-0.0.52-03-tier1-detection-and-fast-path
parent: ADR-0.0.52-artifact-staleness-propagation
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.52-03-tier1-detection-and-fast-path: Tier 1 detection and fast path

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md`
- **Checklist Item:** #3 — "Tier 1 mechanical detection algorithm — declared edges + path overlap + fan-in downweight; fast-path 6-condition check; `propagation_evaluated` and `artifact_staleness_flagged` event emission with `tx_id` pairing"

**Status:** Draft

## Objective

Implement the Tier 1 mechanical detection algorithm (declared edges + path overlap + fan-in downweight) and the 6-condition fast-path check. Produce the affected-set computation that OBPI-04 wires into trigger events. This OBPI is the algorithmic core; OBPI-04 owns when it fires, OBPI-05 owns what gates on its output.

## Lane

**Heavy** — New propagation pipeline logic with cross-corpus reads and emit-side behavior.

## Allowed Paths

- `src/gzkit/governance/propagation/detect.py` — **PRIMARY:** Tier 1 detection algorithm
- `src/gzkit/governance/propagation/fast_path.py` — **PRIMARY:** 6-condition fast-path evaluator
- `src/gzkit/governance/propagation/affected_set.py` — affected-set type and helpers
- `src/gzkit/governance/propagation/__init__.py` — re-export `propagate(trigger_event)` stub
- `tests/governance/test_propagation_detect.py` — Tier 1 algorithm tests
- `tests/governance/test_propagation_fast_path.py` — fast-path condition tests
- `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- Trigger wiring (deferred to OBPI-04)
- Tier 2 surfaces (deferred to OBPI-07)
- Validator scopes (deferred to OBPI-05)

## Creates These Files

- `src/gzkit/governance/propagation/__init__.py` — **CREATE** (or extend) re-exports for `propagate(trigger_event)` stub
- `src/gzkit/governance/propagation/detect.py` — **CREATE** Tier 1 detection algorithm
- `src/gzkit/governance/propagation/fast_path.py` — **CREATE** 6-condition fast-path evaluator
- `src/gzkit/governance/propagation/affected_set.py` — **CREATE** affected-set type and helpers
- `tests/governance/test_propagation_detect.py` — **CREATE** Tier 1 algorithm tests
- `tests/governance/test_propagation_fast_path.py` — **CREATE** fast-path condition tests

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `detect.py` MUST implement `compute_tier1_affected_set(trigger: TriggerEvent, *, thresholds: StalenessPropagationThresholds) -> AffectedSet` returning the union of declared-edge reverse-deps and path-overlap matches (modulo fan-in downweight).
2. REQUIREMENT: Declared-edge walk MUST inspect every artifact's frontmatter `parent:`, `cites:`, `relates_to:` and include artifacts whose declared edges reference the trigger's `trigger_artifact_id` (or, for OBPI triggers, the parent ADR id).
3. REQUIREMENT: Path-overlap match MUST compute set intersection of trigger's `actual_paths_touched` and each candidate's `actual_paths_touched`; non-empty intersection after downweight yields inclusion.
4. REQUIREMENT: Fan-in downweight MUST exclude paths touched by `>= thresholds.fan_in_downweight_threshold` distinct ADRs from path-overlap; threshold from `data/staleness_propagation_thresholds.json`.
5. REQUIREMENT: `fast_path.py` MUST evaluate all 6 conditions: no_new_req, no_req_body_amend, no_new_obpi (ADR closeout only), paths_subset_of_authoring, no_metadata_shift, transitive_no_surprise (ADR closeout only). Returns a `FastPathReason` model.
6. REQUIREMENT: Each fast-path condition MUST be independently testable; per-condition tests exist with positive and negative cases.
7. REQUIREMENT: For OBPI-completion triggers, `transitive_no_surprise` MUST be unset (None) — it is an ADR-closeout-only condition.
8. REQUIREMENT: All algorithm modules MUST type-check cleanly (`uvx ty check .`) and stay within `.claude/rules/pythonic.md` size limits.

> STOP-on-BLOCKERS: if `actual_paths_touched` is absent because OBPI-01 has not landed, pause and surface the dependency.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item** — Quote: *"Tier 1 mechanical detection algorithm — declared edges + path overlap + fan-in downweight; fast-path 6-condition check"*.
- [ ] Parent ADR § Decision / "Tier 1 — Mechanical detection" — full spec.
- [ ] Parent ADR § Decision / "Fast path" — exact 6 conditions.
- [ ] Parent ADR § Consequences/Negative item 8 — assumption #3 (`actual_paths_touched` as coupling proxy).

**Governance:**

- [ ] `.claude/rules/pythonic.md` § Size Limits — module ≤ 600 lines, function ≤ 50 lines.

**Prerequisites:**

- [ ] OBPI-0.0.52-01 (`actual_paths_touched` field) has landed.
- [ ] OBPI-0.0.52-02 (Pydantic models + threshold config) has landed.

**Existing Code:**

- [ ] Adjacent governance modules reviewed for module layout conventions.
- [ ] Any existing ADR-graph walker reviewed for declared-edge traversal patterns.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests derived from brief acceptance criteria
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] BDD scenarios pass (full coverage in OBPI-09)

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_propagation_detect tests.governance.test_propagation_fast_path -v
```

## Demo

```bash
python -c "
from gzkit.governance.propagation.detect import compute_tier1_affected_set
from gzkit.governance.propagation.fast_path import evaluate_fast_path
# fixture trigger event; see tests for full examples
result = compute_tier1_affected_set(fixture_trigger, thresholds=fixture_thresholds)
print('affected:', sorted(result.artifact_ids))
print('signals:', result.detection_signals)
print('fast_path:', evaluate_fast_path(fixture_trigger).model_dump())
"
```

## Acceptance Criteria

- [ ] REQ-0.0.52-03-01: Given two ADRs where B's frontmatter `cites: ADR-A`, when A's closeout trigger fires, then B appears in the Tier 1 affected-set with `detection_signal: declared_edge:cites`.
- [ ] REQ-0.0.52-03-02: Given two OBPIs whose `actual_paths_touched` intersect on a non-fan-in path, when one's completion trigger fires, then the other appears in the affected-set with `detection_signal: path_overlap:<path>`.
- [ ] REQ-0.0.52-03-03: Given a path touched by `>= fan_in_downweight_threshold` ADRs, when a trigger touches that path, then it is excluded from path-overlap matching.
- [ ] REQ-0.0.52-03-04: Given an ADR closeout whose 6 fast-path conditions all hold, when `evaluate_fast_path` runs, then it returns `all_conditions_met=True`.
- [ ] REQ-0.0.52-03-05: Given an ADR closeout with one condition failing, when `evaluate_fast_path` runs, then it returns `all_conditions_met=False` with that specific condition flagged false.
- [ ] REQ-0.0.52-03-06: Given an OBPI-completion trigger, when `evaluate_fast_path` runs, then `transitive_no_surprise` is None (not evaluated).
- [ ] REQ-0.0.52-03-07: Given the detection and fast-path modules, when `uvx ty check .` runs, then no type errors are reported and modules stay under size limits.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR cycle followed
- [ ] **Code Quality:** Lint, type checks clean
- [ ] **Value Narrative:** documented
- [ ] **Key Proof:** included

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before: cross-artifact coupling had no mechanical detection — discovery was honor-system. Now: every trigger produces a Tier 1 affected-set via declared-edge walk + path-overlap (with fan-in noise control), and the 6-condition fast-path captures the implemented-exactly-as-designed common case so per-OBPI-completion cadence stays tolerable.

### Key Proof

```python
>>> compute_tier1_affected_set(trigger=adr_a_closeout).artifact_ids
{'ADR-0.0.B', 'OBPI-0.0.C-04'}
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
