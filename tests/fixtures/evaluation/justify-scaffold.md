---
anchor_id: ADR-0.99.0-fixture
anchor_kind: ADR
generated_at: 2026-05-03T22:00:00+00:00
scaffold_version: 1
---

# Walkthrough: ADR-0.99.0-fixture

## 1. Decision Statement

**Prompt:** *State the decision in one sentence.*

**Evidence:**

- Fixture justify scaffold for OBPI-0.0.26-05 binding-gate behave coverage.

Fixture decision: pin a deterministic evaluation-feedback loop fixture so
behave scenarios can satisfy the binding gate without authoring a fresh
justify artifact in every run.

## 2. Context

**Prompt:** *Why is this decision being made now?*

**Evidence:**

- ADR-0.0.26 binding gate fires when a dimension scores < 3.0 or ≥3
  red-team challenges fire.

The binding gate at `src/gzkit/governance/trust_audits/evaluation_justify_binding.py`
requires a justify artifact whose name matches the artifact slug. This
fixture is the canonical artifact-present case for the gate.

## 3. Constraints

**Prompt:** *What constraints shape the decision?*

**Evidence:**

- Heavy lane requires Gate 4 BDD coverage.

Constraints: scenario must run in <30s, must not touch live ledger, must
mock `gh` boundary.

## 4. Alternatives Considered

**Prompt:** *What other approaches were rejected and why?*

**Evidence:**

- Scenario could synthesize a fresh justify artifact per-run.

Rejected: per-run authoring inflates step complexity and obscures the
gate's pass-condition logic.

## 5. Risks and Mitigations

**Prompt:** *What could go wrong and how is it addressed?*

**Evidence:**

- Stale fixture could mask validator regressions.

Mitigation: scenario asserts both the failure and the success branch
against the same artifact, so a stale fixture fails closed.

## 6. Verification

**Prompt:** *How will the decision be verified?*

**Evidence:**

- Behave scenario in `features/evaluation_feedback_loop.feature`.

Verified by running `uv run -m behave features/evaluation_feedback_loop.feature`
and asserting exit 0.

## 7. Rollback

**Prompt:** *How is the decision unwound if it fails?*

**Evidence:**

- Delete the fixture file and re-author per real ADR.

Rollback: this fixture is bdd-only; no production surface depends on it.

## 8. Decision Owner

**Prompt:** *Who owns the decision and accepts its consequences?*

**Evidence:**

- OBPI-0.0.26-05-bdd-coverage owns the fixture.

Owner: brief author at completion time.
