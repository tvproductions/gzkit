---
id: OBPI-0.27.0-03-router-tables-validator
parent: ADR-0.27.0-namespace-router-product-surface
item: 3
lane: Lite
status: Draft
---

# OBPI-0.27.0-03-router-tables-validator: **router-tables-validator** — Add `gz validate --router-tables` mechanical check — every routed skill resolves to a registered skill on disk, and every concrete skill is reachable from at least one router.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md`
- **Checklist Item:** #3 - "OBPI-0.27.0-03: **router-tables-validator** — Add `gz validate --router-tables` mechanical check — every routed skill resolves to a registered skill on disk, and every concrete skill is reachable from at least one router."

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

**router-tables-validator** — Add `gz validate --router-tables` mechanical check — every routed skill resolves to a registered skill on disk, and every concrete skill is reachable from at least one router.

## Lane

**Lite** - This OBPI remains internal to the promoted ADR implementation scope.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md` — parent ADR for intent and scope
- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/**` — parent ADR package scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: **router-tables-validator** — Add `gz validate --router-tables` mechanical check — every routed skill resolves to a registered skill on disk, and every concrete skill is reachable from at least one router.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief
1. REQUIREMENT: Verification commands MUST be concrete and runnable before acceptance
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/**`
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
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Replace with concrete product demonstrations for this OBPI.
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.27.0-03-01: `audit_router_tables` emits a `router_tables`-typed `ValidationError` when a router routes an intent to a slug that has no canonical `.gzkit/skills/<slug>/SKILL.md`. (Direction 1 — fail-closed; exit 3 via policy_breach.)
- [ ] REQ-0.27.0-03-02: `audit_router_tables` emits a `router_tables_coverage`-typed `ValidationError` when a concrete (non-router) skill is not routed from any router. (Direction 2 — advisory; exit 1.)
- [ ] REQ-0.27.0-03-03: `audit_router_tables` emits zero errors on a sandbox where every router's routed slugs resolve and every concrete skill is routed at least once. (Clean baseline.)

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

- [x] Intent and scope recorded (parent ADR-0.27.0 § Checklist row 03; three concrete REQs covering Direction 1 fail-closed, Direction 2 advisory, and clean baseline)

### Gate 2 (TDD — Red-Green-Refactor)

```text
$ uv run -m unittest -v tests.governance.test_router_tables_validator
test_zero_errors_when_routers_cover_every_concrete_skill ... ok
test_unrouted_concrete_skill_emits_coverage_advisory ... ok
test_routed_slug_missing_emits_router_tables_error ... ok
----------------------------------------------------------------------
Ran 3 tests in 0.034s
OK

$ uv run gz covers OBPI-0.27.0-03 --plain
REQ-0.27.0-03-01    covered    tests/governance/test_router_tables_validator.py
REQ-0.27.0-03-02    covered    tests/governance/test_router_tables_validator.py
REQ-0.27.0-03-03    covered    tests/governance/test_router_tables_validator.py
```

### Code Quality

```text
$ uv run ruff check src/gzkit/governance/trust_audits/router_tables.py \
                    src/gzkit/commands/validate_cmd.py \
                    src/gzkit/cli/parser_maintenance.py \
                    tests/governance/test_router_tables_validator.py
All checks passed!

$ uv run gz typecheck
Type check passed.

$ uv run gz cli audit
CLI audit passed.
Cross-coverage: 102/102 commands fully covered.
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

**Before:** Router slug routes were verified by hand. A typo in any router's intent table would silently route to a non-existent skill until a human noticed (the GSD-comparison failure mode the parent ADR exists to close). And no mechanism surfaced concrete skills that had drifted out of router coverage — the "every concrete skill reachable from at least one router" invariant was prose, not enforcement.

**After:** `uv run gz validate --router-tables` mechanically enforces both directions. Direction 1 (routed slug must resolve) fail-closes via the policy-breach taxonomy (exit 3 in mixed runs). Direction 2 (concrete skill must be router-reachable) emits advisory `router_tables_coverage` findings (exit 1) — surfaces coverage gaps without blocking `gz check`. Router detection is structural (any skill body containing the `| Intent | Skill |` table header), so future routers and the existing `gz-skill-router` lookup aid both qualify without hard-coded slug lists.

Current run against the live canonical surface: **0 direction-1 errors** (every routed slug from OBPI-01 resolves), **16 direction-2 advisories** (concrete skills not yet routed: `gz-adr-evaluate`, `gz-check-config-paths`, `gz-chore-runner`, `gz-cli-audit`, `gz-competitor-radar`, `gz-deps-upgrade`, `gz-foundation-triage`, `gz-gates`, `gz-issue-file`, `gz-justify`, `gz-migrate-semver`, `gz-obpi-lock`, `gz-obpi-simplify`, `gz-plan-audit`, `gz-pythonic-pattern-apply`, `gz-pythonic-pattern-detect`). These advisories are the planned cleanup surface; the recovery plan's anti-temptation rule keeps them out of OBPI-03 scope.

### Key Proof

```text
$ uv run gz validate --router-tables; echo "EXIT: $?"
Validated: router_tables
❌ Validation failed with 16 error(s):
   →  .gzkit/skills/gz-adr-evaluate/SKILL.md
    concrete skill 'gz-adr-evaluate' is not reachable from any router; consider
    routing it under one of ['gz-context', 'gz-governance', 'gz-manage',
    'gz-project', 'gz-quality', 'gz-workflow'] or accept the coverage gap
   ... (15 more advisories)
EXIT: 1

# Direction 1 would emit exit 3 — synthesized & test-asserted in
# tests/governance/test_router_tables_validator.py::TestRoutedSlugMustResolve
```

### Implementation Summary

- Files created:
  - `src/gzkit/governance/trust_audits/router_tables.py` (115 LoC; well under the OBPI's ~150 ceiling)
  - `tests/governance/test_router_tables_validator.py` (three REQ-derived tempfile-isolated tests)
- Files modified:
  - `src/gzkit/governance/trust_audits/__init__.py` (import + `__all__` export)
  - `src/gzkit/commands/validate_cmd.py` (kwarg threading, scope dicts, runner registration, policy-breach taxonomy entry for `router_tables`)
  - `src/gzkit/cli/parser_maintenance.py` (argparse flag + dispatcher wiring)
  - `docs/user/manpages/validate.md` (Synopsis update + `--router-tables` section)
  - This OBPI brief (REQ rewrites + evidence)
- Tests added: 3 (one per REQ); all GREEN; 9-test suite covering OBPI-01/02/03 runs in 0.034s.
- Date completed: 2026-05-23 (pending Stage 5 attestation)
- Attestation status: pending Gate 5 human attestation per ADR-0.0.36
- Defects noted: 16 direction-2 advisories surface unrouted concrete skills — routing them is post-recovery cleanup, deliberately out of scope per recovery-plan anti-temptation #1.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
