---
id: OBPI-0.0.52-02-pydantic-models-and-schema-deltas
parent: ADR-0.0.52-artifact-staleness-propagation
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.52-02-pydantic-models-and-schema-deltas: Pydantic models and schema deltas

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md`
- **Checklist Item:** #2 — "Pydantic models + ledger event JSON Schema registration + frontmatter schema delta (`evaluation_stale`) + threshold config model (`data/staleness_propagation_thresholds.json`)"

**Status:** Draft

## Objective

Author the Pydantic v2 model surface for the propagation pipeline (four ledger event types, frontmatter `StalenessEntry`, threshold config), register the four new ledger event JSON Schemas, and add the `evaluation_stale` frontmatter delta to ADR/OBPI schemas. This OBPI is the data-layer foundation — every other OBPI in the package consumes these models.

## Lane

**Heavy** — Adds Pydantic models for a new ledger event family, schema registrations, frontmatter schema delta, and a new threshold config file (all runtime contract).

## Allowed Paths

- `src/gzkit/governance/propagation/__init__.py` — new package
- `src/gzkit/governance/propagation/models.py` — **PRIMARY:** Pydantic models per ADR § Section 3
- `src/gzkit/schemas/staleness_event.schema.json` — JSON Schema for the four new ledger event types
- `src/gzkit/schemas/adr.json` — add `evaluation_stale` to ADR frontmatter schema
- `src/gzkit/schemas/obpi.json` — add `evaluation_stale` to OBPI frontmatter schema (OBPI-01 already adds `actual_paths_touched`; coordinate hunks)
- `src/gzkit/schemas/staleness_propagation_thresholds.schema.json` — schema for the threshold config
- `data/staleness_propagation_thresholds.json` — threshold config with notional defaults
- `src/gzkit/governance/trust_audits/documents.py` — register the four new event kinds with `gz validate --documents`
- `tests/governance/test_propagation_models.py` — model unit tests
- `tests/test_schema_validation.py` — schema-level tests for new event kinds and frontmatter delta
- `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- Detection logic (deferred to OBPI-03)
- Trigger wiring (deferred to OBPI-04)
- New runtime dependencies (Pydantic v2 already present)

## Creates These Files

- `src/gzkit/governance/propagation/__init__.py` — **CREATE** new package
- `src/gzkit/governance/propagation/models.py` — **CREATE** Pydantic models per ADR § Section 3
- `src/gzkit/schemas/staleness_event.schema.json` — **CREATE** JSON Schema for the four new ledger event types
- `src/gzkit/schemas/staleness_propagation_thresholds.schema.json` — **CREATE** schema for the threshold config
- `data/staleness_propagation_thresholds.json` — **CREATE** threshold config with notional defaults
- `src/gzkit/governance/trust_audits/documents.py` — **CREATE** registration helper if not present (else modify)
- `tests/governance/test_propagation_models.py` — **CREATE** model unit tests
- `tests/test_schema_validation.py` — **CREATE** schema-level tests for new event kinds and frontmatter delta

Existing files modified: `src/gzkit/schemas/adr.json`, `src/gzkit/schemas/obpi.json`.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `models.py` MUST define `StalenessSource` enum (`mechanical`, `semantic_scan`), `ClearanceKind` enum (`confirmed_unchanged`, `amended`), `CandidateDecision` enum (`promoted`, `rejected`).
2. REQUIREMENT: All models MUST use `ConfigDict(extra="forbid", frozen=True)` per `.claude/rules/models.md`.
3. REQUIREMENT: Four ledger event models MUST exist with the exact field shapes specified in parent ADR § Decision: `ArtifactStalenessFlaggedEvent`, `ArtifactStalenessClearedEvent`, `PropagationEvaluatedEvent`, `PropagationCandidatesReviewedEvent`. All MUST inherit `PropagationEventBase` (with `id`, `ts`, `trigger_event_id`, `trigger_artifact_id`, `tx_id`).
4. REQUIREMENT: `tx_id` MUST be present on `PropagationEventBase` for atomic-transaction pairing (consumed by OBPI-04).
5. REQUIREMENT: `ArtifactStalenessClearedEvent` MUST require `amendment_ref` when `clearance_kind == ClearanceKind.AMENDED` (model-level validator); `ArtifactStalenessFlaggedEvent` MUST require `attested_by` when `source == StalenessSource.SEMANTIC_SCAN`.
6. REQUIREMENT: `PropagationCandidatesReviewedEvent` MUST allow `reviews: list = []`, `judge_unreachable_reason: str | None`, `operator_attestation: str`; model-level validator MUST enforce mutual exclusivity (judge_unreachable_reason set implies operator_attestation empty, vice versa).
7. REQUIREMENT: `evaluation_stale` frontmatter delta MUST validate at JSON Schema level: `source == "semantic_scan"` implies `attested_by` is present (cross-field invariant).
8. REQUIREMENT: `data/staleness_propagation_thresholds.json` MUST contain `fan_in_downweight_threshold: 5`, `tier_2_prefilter_top_k: 10`, `tier_2_judge_promotion_score_floor: 0.4` as notional defaults; threshold schema MUST exist and validate the file.
9. REQUIREMENT: `gz validate --documents` MUST recognize all four new event kinds without false-positive failures.
10. REQUIREMENT: Type checking MUST pass cleanly under `uvx ty check .` for the new models per `.claude/rules/pythonic.md`.

> STOP-on-BLOCKERS: if Pydantic v2 patterns are unfamiliar, read `.claude/rules/models.md` and an existing model file.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item** — Quote: *"Pydantic models + ledger event JSON Schema registration + frontmatter schema delta (`evaluation_stale`) + threshold config model"*. This OBPI delivers the entire data layer.
- [ ] Parent ADR § Decision / "Tier 1 — Mechanical detection (fail-closed)" — event-type semantics.
- [ ] Parent ADR § Decision / "2am operational discipline" — `tx_id` atomic pairing requirement.
- [ ] Parent ADR § Decision / "Tier 2 anti-theatre defenses" — `judge_unreachable_reason` semantic.

**Governance:**

- [ ] `.claude/rules/models.md` — Pydantic BaseModel discipline, frozen=True/extra=forbid.
- [ ] `.claude/rules/pythonic.md` — type-ignore syntax, error-handling patterns.

**Prerequisites:**

- [ ] OBPI-0.0.52-01 has landed or coordinates schema hunks in `obpi.json`.
- [ ] Existing OBPI schema readable: `src/gzkit/schemas/obpi.json`.

**Existing Code:**

- [ ] An existing event Pydantic model in `src/gzkit/governance/` reviewed for envelope-shape conventions.
- [ ] `src/gzkit/governance/trust_audits/documents.py` reviewed for event-kind registration pattern.

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
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_propagation_models tests.test_schema_validation -v
```

## Demo

```bash
python -c "
from gzkit.governance.propagation.models import (
    ArtifactStalenessFlaggedEvent, StalenessSource
)
ev = ArtifactStalenessFlaggedEvent(
    id='01HXXX', ts='2026-05-19T00:00:00Z',
    trigger_event_id='trig01', trigger_artifact_id='ADR-0.0.A',
    tx_id='tx01',
    artifact_id='ADR-0.0.B', upstream_id='ADR-0.0.A',
    source=StalenessSource.MECHANICAL,
    detection_signal='declared_edge:cites',
)
print(ev.model_dump_json(indent=2))
"
uv run python -m json.tool data/staleness_propagation_thresholds.json
```

## Acceptance Criteria

- [ ] REQ-0.0.52-02-01: Given Pydantic v2, when models use `ConfigDict(extra="forbid", frozen=True)`, then instances reject unknown fields and disallow mutation.
- [ ] REQ-0.0.52-02-02: Given an `ArtifactStalenessClearedEvent` with `clearance_kind=AMENDED`, when constructed without `amendment_ref`, then validation fails with a model-level error.
- [ ] REQ-0.0.52-02-03: Given an `ArtifactStalenessFlaggedEvent` with `source=SEMANTIC_SCAN`, when constructed without `attested_by`, then validation fails.
- [ ] REQ-0.0.52-02-04: Given a `PropagationCandidatesReviewedEvent`, when both `judge_unreachable_reason` and non-empty `operator_attestation` are set, then validation fails (mutual exclusivity).
- [ ] REQ-0.0.52-02-05: Given the new `evaluation_stale` JSON Schema, when an entry has `source: "semantic_scan"` without `attested_by`, then `gz validate --documents` rejects it.
- [ ] REQ-0.0.52-02-06: Given `data/staleness_propagation_thresholds.json`, when loaded via `StalenessPropagationThresholds`, then notional defaults parse cleanly and reject out-of-range values.
- [ ] REQ-0.0.52-02-07: Given `gz validate --documents`, when ledger entries with the four new event kinds are present, then validation passes without false-positive failures.

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

Before: no Pydantic models for propagation; no JSON Schema registration for the four new event kinds; no frontmatter contract for the `evaluation_stale` flag. Now: every downstream OBPI consumes a typed, frozen, extra-forbidden model surface with cross-field invariants enforced at both Pydantic and JSON Schema layers.

### Key Proof

```python
>>> from gzkit.governance.propagation.models import ArtifactStalenessClearedEvent, ClearanceKind
>>> ArtifactStalenessClearedEvent(clearance_kind=ClearanceKind.AMENDED, ...)
ValidationError: amendment_ref is required when clearance_kind == AMENDED
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
