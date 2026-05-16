---
id: OBPI-0.0.33-05-surface-fidelity-composite
parent: ADR-0.0.33-agent-control-surface-fidelity
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.0.33-05-surface-fidelity-composite: Surface Fidelity Composite

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`
- **Checklist Item:** #5 - "OBPI-0.0.33-05: Composite scope + CI wiring — `gz validate --surface-fidelity` runs all four; wired into `gz check`; cheap subset (1, 2, 3) in pre-commit; tests under `tests/governance/` per per-rule-file naming and the eval-awareness corollary"

**Status:** Completed

## Objective

Composite scope + CI wiring — `gz validate --surface-fidelity` runs all four; wired into `gz check`; cheap subset (1, 2, 3) in pre-commit; tests under `tests/governance/` per per-rule-file naming and the eval-awareness corollary.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Dependencies

This OBPI is the integration layer for OBPI-01 through OBPI-04. It MUST NOT
begin implementation until all four predecessor validators are landed and
re-exporting from `gzkit.governance.trust_audits`:

- OBPI-0.0.33-01-bullet-retention-validator → `validate_bullet_retention`
- OBPI-0.0.33-02-surface-weight-validator → `validate_surface_weight`
- OBPI-0.0.33-03-pointer-integrity-validator → `validate_pointer_integrity`
- OBPI-0.0.33-04-scenario-reachability-validator → `validate_scenario_reachability`

The composite is sequentially last on the dependency graph. Predecessors 01–04
are mutually independent and may be implemented in parallel.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/**` — parent ADR package scope
- `src/gzkit/governance/trust_audits/__init__.py` — composite scope dispatch wiring (`validate_surface_fidelity` runs all four)
- `src/gzkit/cli/parser_maintenance.py` — `gz validate --surface-fidelity` flag registration and dispatch; `gz check` integration
- `tests/governance/test_surface_fidelity_composite.py` — Gate-2 TDD asset for composite behavior
- `.pre-commit-config.yaml` — pre-commit hook registration for the cheap subset (invariants 1, 2, 3)
- `docs/user/manpages/validate.md` — manpage entry for `--surface-fidelity`
- `docs/user/manpages/check.md` — note that `gz check` now includes the surface-fidelity composite

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- The four predecessor validator modules (already landed by OBPIs 01–04)
- `docs/governance/advisory-rules-audit.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/rules/**` (content edits are not in scope; only the validator wiring)
- New runtime dependencies
- CI files outside `.pre-commit-config.yaml`, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

This OBPI implements the composite scope and CI wiring. It does NOT re-implement
the four invariants; it integrates them.

1. REQUIREMENT: **Composite runs all four.** `gz validate --surface-fidelity` MUST invoke `validate_bullet_retention`, `validate_surface_weight`, `validate_pointer_integrity`, and `validate_scenario_reachability` in that order and aggregate their `ValidationError` lists. Skipping any of the four is fail-closed at the test layer.
2. REQUIREMENT: **Exit code is the worst of the four.** If any constituent validator exits 3, the composite exits 3. The composite exit MUST NEVER be lower than the highest constituent exit code (no masking).
3. REQUIREMENT: **`gz check` integration.** `gz check` MUST invoke `--surface-fidelity` as part of its default pipeline. The wiring follows the established pattern for other composite validators (e.g., `--advisor-proof-binding` registered in `parser_maintenance.py`).
4. REQUIREMENT: **Pre-commit runs the cheap subset.** `.pre-commit-config.yaml` MUST register a hook that runs invariants 1, 2, and 3 (`--bullet-retention`, `--surface-weight`, `--pointer-anchors`). Invariant 4 (scenario reachability) is CI-only in Era 1 and MUST NOT be in pre-commit (its registry-absent advisory would be noise on every commit).
5. REQUIREMENT: **No new pre-commit dependency.** The hook MUST invoke `uv run gz validate --bullet-retention --surface-weight --pointer-anchors` (a single CLI call passing all three flags), not three separate hooks, so the per-commit overhead is one parser bootstrap, not three.
6. REQUIREMENT: **Tests live under `tests/governance/`.** The composite test file follows the per-rule-file naming convention; integration tests assert (a) all four constituents fire, (b) exit code aggregation, (c) `gz check` includes the scope, (d) pre-commit registration text is present.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing — sequential dependency on OBPIs 01–04):**

- [ ] Parent ADR file exists: `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`
- [ ] `src/gzkit/governance/trust_audits/bullet_retention.py` exists and re-exports `validate_bullet_retention` (OBPI-01 landed)
- [ ] `src/gzkit/governance/trust_audits/surface_weight.py` exists and re-exports `validate_surface_weight` (OBPI-02 landed)
- [ ] `src/gzkit/governance/trust_audits/pointer_integrity.py` exists and re-exports `validate_pointer_integrity` (OBPI-03 landed)
- [ ] `src/gzkit/governance/trust_audits/scenario_reachability.py` exists and re-exports `validate_scenario_reachability` (OBPI-04 landed)
- [ ] `.pre-commit-config.yaml` exists at repo root

**Existing Code (understand current state):**

- [ ] Test patterns: `tests/governance/`
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run gz validate --surface-fidelity                 # composite must exit 0 on a clean tree
uv run gz check                                        # must invoke surface-fidelity as part of pipeline
uv run -m unittest tests.governance.test_surface_fidelity_composite -v
grep -q "gz validate --bullet-retention" .pre-commit-config.yaml
test -d tests/governance
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.33-05-01: Given the four predecessor validators are importable from `gzkit.governance.trust_audits`, when `gz validate --surface-fidelity` runs, then it invokes all four in declared order (`bullet_retention`, `surface_weight`, `pointer_integrity`, `scenario_reachability`) and aggregates their errors.
- [ ] REQ-0.0.33-05-02: Given one constituent validator returns a fail-closed error (exit 3) and the others return clean, when `gz validate --surface-fidelity` runs, then the composite exits 3 and the aggregated error list contains the failing constituent's `ValidationError`.
- [ ] REQ-0.0.33-05-03: Given `gz check` is invoked, when its pipeline runs, then `validate_surface_fidelity` is one of the executed steps (assert via test-doubles on the check dispatch table).
- [ ] REQ-0.0.33-05-04: Given `.pre-commit-config.yaml`, when read, then it contains a hook entry invoking `uv run gz validate --bullet-retention --surface-weight --pointer-anchors` as a single CLI call. NEVER includes `--scenario-reachability` in the pre-commit subset.
- [ ] REQ-0.0.33-05-05: Given the manpage `docs/user/manpages/gz-validate.md`, when read, then `--surface-fidelity` is documented with a description matching the composite scope behavior.
- [ ] REQ-0.0.33-05-06: Given the composite is implemented, when `gzkit.governance.trust_audits.validate_surface_fidelity` is imported, then it resolves and matches the established re-export pattern.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

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
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


```bash
$ uv run gz validate --surface-fidelity
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
Validated: surface_fidelity
```

The composite invokes all four validators in declared order, aggregates their ValidationError lists, and exits with the worst-of-four exit code — confirmed by test_all_four_validators_fire_in_order and test_exit_code_worst_of_four (receipt arb-step-unittest-e8e473571f264b8eaf2f877e09a2b9ba). gz check includes the new "Surface fidelity" step (receipt arb-step-mkdocs-329cddd5e26249d78ba317fef5ca8f71 validates docs build clean). All 5083 unit tests pass; 6/6 OBPI tests pass.

### Implementation Summary


- Composite function: validate_surface_fidelity in src/gzkit/governance/trust_audits/__init__.py invokes validate_bullet_retention, validate_surface_weight, validate_pointer_integrity, validate_scenario_reachability in declared order and aggregates ValidationError lists
- CLI flag: --surface-fidelity registered in src/gzkit/cli/parser_maintenance.py; wired through 6 locations in src/gzkit/commands/validate_cmd.py
- gz check integration: run_surface_fidelity_audit in src/gzkit/quality.py; ("Surface fidelity", run_surface_fidelity_audit) appended to _build_check_steps() in src/gzkit/commands/quality.py
- Pre-commit hook: surface-fidelity-cheap in .pre-commit-config.yaml runs uv run gz validate --bullet-retention --surface-weight --pointer-anchors (single CLI call, no --scenario-reachability per REQ-04)
- Docs: --surface-fidelity documented in docs/user/manpages/validate.md (usage line, dedicated section, scopes table); Surface fidelity step documented in docs/user/manpages/check.md
- Tests added: tests/governance/test_surface_fidelity_composite.py with 6 unit tests; all 6 REQs covered via @covers decorators (uncovered_reqs: 0 per gz covers)
- Regression fix: added run_surface_fidelity_audit mock patch to tests/commands/test_skills.py:377 so the existing gz check test continues to pass
- Behave waiver: registered adr-0.0.33-05-composite-bdd-deferred-to-unit-tests in data/behave_coverage_waivers.json — composite wiring REQs are internal-mechanics naturally covered by Python unit tests; per-invariant operator-runnable behavior is owned by OBPI-01..04
- Date completed: 2026-05-15
- Attestation status: operator-verbatim-conversational
- Defects noted: none

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — composite validator validate_surface_fidelity lands in trust_audits/__init__.py invoking all four predecessors in declared order; --surface-fidelity CLI flag registered; "Surface fidelity" step wired into gz check via run_surface_fidelity_audit; pre-commit hook surface-fidelity-cheap registers the 3-invariant subset (no --scenario-reachability); manpages updated; 6/6 REQs covered by tests/governance/test_surface_fidelity_composite.py (uncovered_reqs: 0); 5083/5083 unit tests pass; ARB receipts arb-ruff-0479b27bb3b6481ba69049a94e93fe15, arb-step-typecheck-dc1b5f6de9bb423faa6b685c6f30cb7f, arb-step-unittest-e8e473571f264b8eaf2f877e09a2b9ba, arb-step-mkdocs-329cddd5e26249d78ba317fef5ca8f71.
- Date: 2026-05-16

---

**Brief Status:** Draft

**Date Completed:** 2026-05-16

**Evidence Hash:** -
