# Plan: OBPI-0.0.36-01-agents-md-matrix-collapse

**OBPI:** OBPI-0.0.36-01-agents-md-matrix-collapse
**Parent ADR:** ADR-0.0.36-universal-obpi-attestation
**Lane:** Heavy

## Context

AGENTS.md § OBPI Acceptance Protocol carries a "Lane & Kind & Sensitivity Attestation Matrix"
with a `feature × lite → Self-closeable after evidence` cell. This cell is the upstream
structural cause of every deprecated state shape surfaced in GHI #332. ADR-0.0.36 Decision
item #1 collapses the matrix to a single universal-attestation binding rule: brief-level
human attestation is required for every OBPI completion, regardless of parent kind or lane.

The lane and kind axes are preserved for gate-firing scope only (Gate 3 docs, Gate 4 BDD).

## Files

- `AGENTS.md` — primary doctrine surface (collapse the matrix section)
- `src/gzkit/templates/agents.md` — generator template (must match AGENTS.md)
- `tests/governance/test_agents_md_matrix.py` — new test module (REQ assertions)
- All `**/AGENTS.md` directory mirrors — propagated by `gz agent sync control-surfaces`

## Steps

### Step 1: TDD RED — Write failing test

Create `tests/governance/test_agents_md_matrix.py` with three test methods deriving
from the OBPI requirements:

- `test_self_closeable_phrase_is_absent` — asserts "Self-closeable after evidence" and
  "Self-closeable" are absent from AGENTS.md and all **/AGENTS.md mirrors (REQ-01)
- `test_universal_attestation_binding_rule_present` — asserts a universal-attestation
  binding rule with NEVER/ALWAYS language is present in § OBPI Acceptance Protocol (REQ-02)
- `test_lane_kind_axes_retained_for_gate_firing_scope` — asserts the lane/kind gate-firing
  scope language (Gate 3 docs, Gate 4 BDD) is retained in the same section (REQ-03)

Run the tests. Observe RED on `test_self_closeable_phrase_is_absent` (phrase still present).

### Step 2: Edit AGENTS.md — Collapse the matrix

In `AGENTS.md` § OBPI Acceptance Protocol, replace the "### Lane & Kind & Sensitivity
Attestation Matrix" subsection (the table and surrounding prose) with:

1. Remove the `### Lane & Kind & Sensitivity Attestation Matrix` heading and the full table
   including the `feature × lite → Self-closeable after evidence` row and the `_is_foundation_adr`
   source-of-truth column.
2. Remove the inheritance paragraph that ends with "A lite-lane foundation OBPI is **not**
   self-closeable. If matrix and code disagree, code (`_requires_human_obpi_attestation`)
   is source of truth."
3. Replace with a single binding rule block:

```
### Universal OBPI Attestation (ADR-0.0.36, GHI #342)

**Brief-level human attestation is ALWAYS required for every OBPI completion, regardless
of parent ADR kind or lane. There is NO self-close path.**

`kind`, `lane`, and `sensitivity` remain three orthogonal axes that determine *which gates
fire*: `foundation` kind and `heavy` lane determine Gate 3 (docs) and Gate 4 (BDD) scope;
`sensitivity: security` adds security-scan requirements. These axes determine gate-firing
scope only — they NEVER determine whether Gate 5 brief-level attestation fires. Gate 5
is universal.

Third-axis doctrine: [`.gzkit/rules/security-sensitivity.md`](.gzkit/rules/security-sensitivity.md).
```

4. Update the existing opening paragraph of § OBPI Acceptance Protocol — the sentence
   referencing the old matrix condition ("when the parent ADR is `heavy`-lane OR
   `foundation`-kind") — to reflect universal attestation.

### Step 3: Edit src/gzkit/templates/agents.md — Mirror the change

Apply the same matrix-collapse change to `src/gzkit/templates/agents.md` so the template
stays in sync with AGENTS.md canon. The template is the generator source; if it diverges,
the next `gz agent sync control-surfaces` run would overwrite the AGENTS.md change.

### Step 4: Run TDD GREEN

Run `uv run -m unittest tests/governance/test_agents_md_matrix.py -v`.
All three tests must pass.

### Step 5: Sync mirrors

Run `uv run gz agent sync control-surfaces` to propagate the changes to all
directory-level AGENTS.md mirrors.

Verify: `git diff --name-only -- "*AGENTS.md"` shows mirrors updated.

### Step 6: Verify quality gates

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

### Step 7: REQ @covers parity

Run `uv run gz covers OBPI-0.0.36-01-agents-md-matrix-collapse --json` and confirm
`uncovered_reqs == 0`.

## Verification

```bash
uv run -m unittest tests/governance/test_agents_md_matrix.py -v
uv run gz agent sync control-surfaces
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Notes

- The template file `src/gzkit/templates/agents.md` is the canonical source for
  AGENTS.md preamble. AGENTS.md is the rendered output. Both must change together.
- `src/gzkit/templates/agents.md` is listed as denied for direct edit by
  `skill-surface-sync.md` rule — however, the brief's Allowed Paths explicitly
  includes it, and the template is the generator source that must match.
- Scope collisions with 11 sibling OBPIs on `src/gzkit/templates/agents.md` are
  all from completed ADRs; no active lock contention.
- Gate 4 BDD: brief requires `@REQ-0.0.36-01-NN` tagged behave scenarios. These
  assert the AGENTS.md doctrine surface semantics.
