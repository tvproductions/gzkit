---
id: OBPI-0.0.55-02-import-direction-validator-warn-only
parent: ADR-0.0.55-package-import-direction-invariant
item: 2
lane: Heavy
status: Draft
allowlist:
- src/gzkit/governance/trust_audits/
- src/gzkit/governance/trust_audits/import_direction.py
- src/gzkit/commands/validate_cmd.py
- src/gzkit/cli/
- src/gzkit/commands/
- docs/user/manpages/validate.md
- tests/governance/
- tests/governance/test_import_direction_validator.py
- docs/design/adr/foundation/ADR-0.0.55-package-import-direction-invariant/**
reqs:
- REQ-0.0.55-02-01
- REQ-0.0.55-02-02
- REQ-0.0.55-02-03
- REQ-0.0.55-02-04
- REQ-0.0.55-02-05
- REQ-0.0.55-02-06
verification:
- uv run gz validate --import-direction
- uv run python -c "import subprocess; r = subprocess.run(['uv','run','gz','validate','--import-direction']); assert r.returncode == 0, 'warn-only must exit 0'"
- uv run gz arb step --name unittest -- uv run -m unittest -q tests.governance.test_import_direction_validator
- uv run gz check
- uv run gz arb ruff
- uv run gz arb typecheck
- uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
---

# OBPI-0.0.55-02-import-direction-validator-warn-only: Ship `gz validate --import-direction` in Warn-Only Mode

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.55-package-import-direction-invariant/ADR-0.0.55-package-import-direction-invariant.md`
- **Checklist Item:** #2 — "OBPI-0.0.55-02: Ship `gz validate --import-direction` in warn-only mode + `gz check` integration + manpage"

**Status:** Draft

## Objective

Ship the `gz validate --import-direction` validator scope in warn-only mode: it consumes the OBPI-01 helper, computes predicate violations across the `src/gzkit/` import graph, suppresses baseline-allowlisted edges, prints warnings for the rest, and exits `0` regardless. Add the scope to the `gz check` default pipeline as a warning-only step and document it in the manpage. This OBPI is the phased-rollout's first stage — the tooling lands; no migration is required yet.

## Lane

**Heavy** — A new `gz validate --import-direction` CLI scope added to the `gz check` default pipeline. Per `.claude/rules/cli.md` a new validator scope is a heavy-lane CLI-contract change. Foundation-kind parent ADR-0.0.55 triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `src/gzkit/governance/trust_audits/` — OBPI creates `import_direction.py` (the validator scope consuming the OBPI-01 helper)
- `src/gzkit/governance/trust_audits/import_direction.py` — the validator module this OBPI creates, named explicitly so OBPI-04 resolves it as pending-upstream rather than a dead citation
- `src/gzkit/commands/validate_cmd.py` — registers the `--import-direction` scope and dispatches the validator
- `src/gzkit/cli/` — OBPI adds the `--import-direction` flag to the `gz validate` parser surface
- `src/gzkit/commands/` — the `gz check` default-pipeline list gains `--import-direction` as a warning-only step
- `docs/user/manpages/validate.md` — documents the new `--import-direction` scope and its warn-only phase
- `tests/governance/` — OBPI creates `tests/governance/test_import_direction_validator.py`
- `docs/design/adr/foundation/ADR-0.0.55-package-import-direction-invariant/**` — parent ADR package scope

## Denied Paths

- `data/package_layer_order.json`, `src/gzkit/governance/import_direction.py`, `.gzkit/rules/package-import-direction.md` — the manifest, helper, and rule are OBPI-01 scope; this OBPI consumes them
- `data/package_import_direction_baseline.json` — read by the validator; drained in OBPI-03
- Any `src/gzkit/**` import-graph relocation — OBPI-03 scope
- The validator's exit-code flip to fail-closed and the rule-version bump — OBPI-04 scope
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `src/gzkit/governance/trust_audits/import_direction.py` defines the `gz validate --import-direction` scope, consuming the OBPI-01 helper (`compute_import_edges`, `violates_predicate`) and the `data/package_layer_order.json` manifest.
2. REQUIREMENT: In warn-only mode the validator exits `0` regardless of how many predicate violations it finds — it NEVER raises a non-zero status during this phase.
3. REQUIREMENT: Violations are printed to stderr in the `RemediationPayload` shape (per ADR-0.0.53). If ADR-0.0.53's port has not yet attested, the validator uses a forward-compatible shape that becomes payload-conformant under ADR-0.0.53's migration; the dependency is recorded in the Implementation Summary.
4. REQUIREMENT: Edges enumerated in `data/package_import_direction_baseline.json` are suppressed — a baseline-allowlisted violation produces no warning.
5. REQUIREMENT: Any NEW back-edge introduced after this OBPI lands (a predicate violation not in the baseline) surfaces as a warning during `gz check`.
6. REQUIREMENT: `--import-direction` is added to the `gz check` default pipeline as a warning-only step — it contributes warnings to `gz check` output but never fails the pipeline during the warn-only phase.
7. REQUIREMENT: `docs/user/manpages/validate.md` documents the `--import-direction` scope, names its warn-only phase, and carries a real EXAMPLES entry showing observed CLI output.
8. REQUIREMENT: Tests in `tests/governance/test_import_direction_validator.py` assert REQ-derived semantics — (a) warn-only mode never returns non-zero even with violations present; (b) the baseline allowlist suppresses warnings for exempted edges; (c) a synthetic new back-edge surfaces as a warning. Tests assert semantics, not output strings.
9. REQUIREMENT: This OBPI relocates ZERO source files and modifies ZERO `src/gzkit/**` import statements — it ships the validator only.
10. REQUIREMENT: NEVER include the operator's personal email in the validator, the manpage, or any test.

> STOP-on-BLOCKERS: if OBPI-01 has not landed (`data/package_layer_order.json` or `src/gzkit/governance/import_direction.py` absent), print BLOCKERS and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 2 — quote verbatim** into the brief's Implementation Summary. Decision item 2 is the contract.
- [ ] Parent ADR § Intent — the phased-rollout rationale (warn-only first; doctrine debt, not doctrine).
- [ ] Parent ADR § Consequences — Positive #4 (phased rollout prevents doctrine debt), Negative #5 (baseline-as-escape-hatch pre-mortem).
- [ ] Parent ADR § Sequencing — OBPI-02 lands after OBPI-01; it requires the helper but no migration work.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/package-import-direction.md` (OBPI-01) — the invariant this validator surfaces
- [ ] `.gzkit/rules/tests.md` § Tests assert semantics, not strings
- [ ] `docs/governance/trust-doctrine.md` — the promoted-scope catalogue; note `gz validate --reconcile-freshness` for the bootstrap-vs-drift pattern this mirrors

**Context — the validator surface:**

- [ ] `src/gzkit/governance/import_direction.py` (OBPI-01) — the helper functions this validator calls
- [ ] `src/gzkit/commands/validate_cmd.py` — the scope registration + dispatch convention; the `gz check` default-pipeline list
- [ ] `gzkit.core.models.RemediationPayload` (ADR-0.0.53) — the warning shape

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-01 landed: `data/package_layer_order.json`, `src/gzkit/governance/import_direction.py`, `data/package_import_direction_baseline.json` present
- [ ] `src/gzkit/governance/trust_audits/` present

**Existing Code (understand current state):**

- [ ] An existing warning-only `gz check` step (if any) for the warn-only integration pattern
- [ ] The existing `gz validate` scope registration shape

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 2 quoted in Implementation Summary

### Gate 2: TDD

- [ ] RED test asserting warn-only mode never returns non-zero, written before implementation
- [ ] Tests pass: `uv run gz arb step --name unittest -- uv run -m unittest -q` (receipt: `arb-step-unittest-*`)
- [ ] No regression in the existing suite

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/validate.md` updated with the new scope, its warn-only phase, and a real EXAMPLES entry
- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] BDD scenario covers `gz validate --import-direction` in warn-only mode — violations present, exit code `0`, warnings emitted

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion

## Verification

```bash
uv run gz validate --import-direction
uv run python -c "import subprocess; r = subprocess.run(['uv','run','gz','validate','--import-direction']); assert r.returncode == 0, 'warn-only must exit 0'"
uv run gz arb step --name unittest -- uv run -m unittest -q tests.governance.test_import_direction_validator
grep -q "import-direction" docs/user/manpages/validate.md
uv run gz check
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# The warn-only validator surfaces every back-edge without blocking:
uv run gz validate --import-direction
echo "exit: $?"   # 0 — warn-only phase
# It is part of the default check pipeline as a warning-only step:
uv run gz check
```

## Acceptance Criteria

- [ ] REQ-0.0.55-02-01: Given parent ADR § Decision item 2, when `gz validate --import-direction` runs, then it consumes the OBPI-01 helper and manifest to compute predicate violations across `src/gzkit/`.
- [ ] REQ-0.0.55-02-02: Given predicate violations present in the graph, when the warn-only validator runs, then it exits `0` and never raises a non-zero status.
- [ ] REQ-0.0.55-02-03: Given an edge enumerated in `data/package_import_direction_baseline.json`, when the validator runs, then that edge produces no warning.
- [ ] REQ-0.0.55-02-04: Given a synthetic new back-edge not in the baseline, when the validator runs, then it surfaces as a warning.
- [ ] REQ-0.0.55-02-05: Given the `gz check` default pipeline, when `gz check` runs, then `--import-direction` executes as a warning-only step that contributes warnings but never fails the pipeline.
- [ ] REQ-0.0.55-02-06: Given the scope boundary, when this OBPI's diff is reviewed, then zero `src/gzkit/**` import statements are modified and zero source files relocated.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 2 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** RED-GREEN cycle followed; validator tests pass; suite regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (back-edges accumulate uninspected) vs capability-now (every new back-edge surfaces at `gz check` time, warn-only)
- [ ] **Key Proof:** `gz validate --import-direction` exit `0` with warnings; `gz check` runs the step
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste unittest output + arb-step-unittest receipt ID here
```

### Code Quality

```text
# Paste lint + typecheck + mkdocs output here with ARB receipt IDs
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

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
