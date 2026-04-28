---
id: OBPI-0.0.22-03-validate-sensitivity-scope
parent: ADR-0.0.22-security-sensitivity-doctrine
item: 3
lane: Heavy
status: Draft
depends_on:
  - OBPI-0.0.22-01-schema-frontmatter-field
  - OBPI-0.0.22-02-security-surface-registry
---

# OBPI-0.0.22-03-validate-sensitivity-scope: gz validate --sensitivity scope with --explain subform

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md`
- **Checklist Item:** #3 - "`gz validate --sensitivity` scope — `validate_sensitivity_binding` at trust_audits.py; CLI flag registration; `--explain` subform for predictive classification; `--json` machine output; auto-detect floor + escalate-not-escape mechanically enforced; integrates into `gz validate --all` and `gz check`; TDD tests cover floor-fires, escalation-allowed, escape-blocked, registry-missing-fail-closed"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

`gz validate --sensitivity` scope — `validate_sensitivity_binding` at trust_audits.py; CLI flag registration; `--explain` subform for predictive classification; `--json` machine output; auto-detect floor + escalate-not-escape mechanically enforced; integrates into `gz validate --all` and `gz check`; TDD tests cover floor-fires, escalation-allowed, escape-blocked, registry-missing-fail-closed.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md` — parent ADR for intent and scope
- `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/obpis/OBPI-0.0.22-03-validate-sensitivity-scope.md` — this brief
- `src/gzkit/governance/trust_audits.py` — `validate_sensitivity_binding` is added here
- `src/gzkit/cli/parser_validate.py` — `--sensitivity` and `--explain` flag registration
- `src/gzkit/cli/**` — adjacent CLI wiring (e.g. `gz check` integration)
- `tests/governance/**` — validator unit tests (floor-fires, escalation-allowed, escape-blocked, registry-missing)
- `tests/cli/**` — CLI flag and `--json` output tests
- `data/behave_coverage_waivers.json` — waiver if BDD is deferred per existing pattern

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold for THIS brief's scope. Cross-brief invariants
     live in the parent ADR Decision; per-brief requirements assert this brief's
     contract only. -->

1. REQUIREMENT: A function `validate_sensitivity_binding` exists in `src/gzkit/governance/trust_audits.py` and intersects each brief's `## ALLOWED PATHS` glob list with `data/security_surfaces.json` to compute a `detected_sensitivity` value.
1. REQUIREMENT: When path intersection is non-empty, the validator forces `sensitivity: security` regardless of frontmatter (the auto-detect floor).
1. REQUIREMENT: Frontmatter MAY declare `sensitivity: security` when paths don't trigger detection — the validator accepts this as an escalation.
1. REQUIREMENT: Frontmatter MAY NOT declare a value lower than detected — the validator exits 3 on attempted escape with a structured finding naming the brief, declared value, detected value, and intersecting paths.
1. REQUIREMENT: When `data/security_surfaces.json` is missing, malformed, or unparseable, the validator fails closed with exit 3 (registry-missing fail-closed).
1. REQUIREMENT: The CLI flag `--sensitivity` is registered in `src/gzkit/cli/parser_validate.py` and dispatches to `validate_sensitivity_binding`.
1. REQUIREMENT: The subform `gz validate --sensitivity --explain ALLOWED_PATHS_LIST` accepts a path list (one per line or comma-separated, per existing CLI conventions) and prints the predicted classification (`detected_sensitivity` + matching category labels) without modifying any artifact.
1. REQUIREMENT: `--json` produces machine-readable findings on stdout (one record per brief: `file`, `declared_sensitivity`, `detected_sensitivity`, `intersecting_paths`, `registry_categories`). Logs go to stderr per `.claude/rules/cli.md`.
1. REQUIREMENT: `gz validate --all` invokes the sensitivity scope; `gz check` invokes `gz validate --all` per existing pipeline. No regression in either composite command's exit-code semantics.
1. REQUIREMENT: TDD coverage for: floor-fires (path intersection forces detected=security), escalation-allowed (declared=security, detected=null), escape-blocked (declared=null, detected=security → exit 3), malformed-paths-tolerated (skips with structured finding, no crash), registry-missing-fail-closed (exit 3).
1. REQUIREMENT: NEVER author the `_requires_security_review_attestation` predicate, the walkthrough extension, the ARB canonical command slot, the rule file, or the AGENTS.md matrix in this OBPI — those belong to OBPIs 04-06.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/**`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
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
test -f docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.22-03-01: Given a brief whose `## ALLOWED PATHS` intersect a registry glob and whose frontmatter omits `sensitivity`, when `gz validate --sensitivity` runs, then the validator reports `detected_sensitivity: security`, `declared_sensitivity: null`, and forces classification to `security` (auto-detect floor).
- [ ] REQ-0.0.22-03-02: Given a brief with `sensitivity: security` in frontmatter and no intersecting paths, when validated, then the validator accepts the declaration (escalation channel) and exits 0.
- [ ] REQ-0.0.22-03-03: Given a brief with intersecting paths but `sensitivity` declared as anything below `security` (or omitted while paths intersect with `--strict-declared` semantics per the rule file), when validated, then the validator exits 3 with a structured finding naming the file, declared value, detected value, and intersecting paths.
- [ ] REQ-0.0.22-03-04: Given a missing or malformed `data/security_surfaces.json`, when `gz validate --sensitivity` runs, then it exits 3 (registry-missing fail-closed) with a finding identifying the registry path.
- [ ] REQ-0.0.22-03-05: Given `gz validate --sensitivity --explain <paths>`, when invoked with a comma-separated or newline-separated list of glob patterns, then the command prints the predicted `detected_sensitivity` + matching category labels to stdout and exits 0 without writing or modifying any artifact.
- [ ] REQ-0.0.22-03-06: Given `gz validate --sensitivity --json`, when invoked, then stdout contains JSON-parseable records (one per brief) with fields `file`, `declared_sensitivity`, `detected_sensitivity`, `intersecting_paths`, `registry_categories`; logs are emitted on stderr.
- [ ] REQ-0.0.22-03-07: Given `gz validate --all` and `gz check` after this OBPI lands, when invoked, then the sensitivity scope is included in the composite run and a sensitivity violation propagates a non-zero exit code through the composite.

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

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
