---
id: OBPI-0.0.74-15-enforces-declaration-and-registry
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 15
lane: Heavy
status: Draft
# req_atomic: each REQ is one coherent authoring increment inside the single new
# enforcement-claim primitive module — the decorator + record (01), the
# decoration-time fail-close (02), the metadata-only guarantee (03), and the
# single-surface boundary fence (04). None decomposes into parallel seq=02+
# sub-tasks (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.74-15-01  # @enforces registers a record at import time; the registry is queryable
  - REQ-0.0.74-15-02  # decoration fail-closes (ValueError at import) on a typo / unknown claim
  - REQ-0.0.74-15-03  # registration is metadata-only — the decorated callable runs unchanged
  - REQ-0.0.74-15-04  # STRUCTURAL-FENCE: one enforcement-claim surface, not two (BI#6)
---

# OBPI-0.0.74-15-enforces-declaration-and-registry: Enforces Declaration And Registry

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #15 - "The `@enforces(claim, fixture, entrypoint)` declaration + import-time registry — fail-closed at decoration on a typo or unknown claim (mirrors the `@covers` / `@advances` precedent), registration metadata-only; unit tests"

**Status:** Draft

## Objective

The `@enforces(claim, fixture=<violation-builder>, entrypoint=<production-callable>)` decorator and one claim-type-agnostic registry land at `src/gzkit/enforcement.py`: decoration registers an `EnforcementClaimRecord` (claim id, the fixture callable, the entrypoint callable) into a module-level registry at import time, and fail-closes at decoration on a typo or unknown claim — exactly the `@covers` (`src/gzkit/traceability.py`) / `@advances` (`src/gzkit/tasks.py`) precedent where typos that would silently pass at runtime instead block at import. Registration is metadata-only: the decorated entrypoint's runtime behavior is unchanged. "Done" = the decorator registers claims discoverable through the registry, an invalid/unknown claim raises at import, the decorated callable is returned untouched, and unit tests pin each behavior. This is the primitive the runner (OBPI-16) discovers; it is the FIRST organ of the enforcement-claim meta-validator and lands first per the strict-no-debt land order (15 → 16 → 17 + 18 → 19).

## Lane

**Heavy** - This OBPI ships a new runtime-contract surface — the `@enforces` decorator and registry that every enforcement claim is declared through — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope (§ Decision item 15, § Boundary Invariants #6, #7)
- `src/gzkit/enforcement.py` **CREATE** — the `@enforces` decorator, the `EnforcementClaimRecord` model, and the import-time registry with its query accessor and decoration-time fail-close
- `tests/governance/test_enforces_registry.py` **CREATE** — unit tests for registration, decoration-time fail-close, and the metadata-only guarantee
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-15-enforces-declaration-and-registry.md` — this brief (evidence recording)

(Security overlap check: no Allowed Path matches a glob in `data/security_surfaces.json` — `src/gzkit/enforcement.py` is a new metadata-registry module, not a `*credential*`/`*token*`/`*secret*`/`*hash*` module, not `quality.py`, not a ledger/arb/auth surface; `sensitivity: security` is not declared.)

## Creates These Files

- `src/gzkit/enforcement.py`
- `tests/governance/test_enforces_registry.py`

## Denied Paths

- Paths not listed in Allowed Paths
- The meta-validator RUNNER (`src/gzkit/enforcement.py` runner logic that invokes `entrypoint(fixture())`) — owned by OBPI-0.0.74-16; this OBPI ships declaration + registry only
- The qc_binding engine and its negative controls (`src/gzkit/governance/trust_audits/qc_binding.py`, `_qc_negative_controls.py`) — the engine lift and the 33 un-forced NC re-authoring are OBPI-0.0.74-16
- A second, parallel negative-control framework — the registry generalizes qc_binding in place (§ Boundary Invariants #6); forking is forbidden
- New dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `@enforces(claim, fixture, entrypoint)` MUST register an `EnforcementClaimRecord` into one claim-type-agnostic module-level registry at import time, discoverable via a query accessor (REQ-15-01).
1. REQUIREMENT: Decoration MUST fail closed (`ValueError` at import) on a malformed/typo claim id or an unknown claim — typos cannot ship, mirroring the `@covers` / `@advances` decoration-time precedent (REQ-15-02).
1. REQUIREMENT: Registration MUST be metadata-only — `@enforces` returns the decorated `entrypoint` callable unchanged; it MUST NOT wrap, alter, or pre-bind any kwarg of the entrypoint (REQ-15-03).
1. NEVER: Pre-bind a forcing kwarg (e.g. `fail_closed=True`) into the registered `entrypoint` via `functools.partial` or a `lambda` at the registration site — the entrypoint MUST be a direct, resolvable reference to a production callable (§ Boundary Invariants #7; the runner in OBPI-16 invokes it).
1. ALWAYS: Reconcile the brief with the parent ADR before implementation; mirror the existing `@covers` decoration-time fail-close pattern in `src/gzkit/traceability.py` rather than inventing a new one.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 15 — quoted verbatim:** "The `@enforces(claim, fixture, entrypoint)` declaration + import-time registry — fail-closed at decoration on a typo / unknown claim (mirrors the `@covers` / `@advances` precedent in `src/gzkit/traceability.py`); registration metadata-only. (OBPI-15)"
- [ ] Parent ADR § Decision § "The enforcement-claim meta-validator (§5 — the floor's teeth)" — D2 (runner-driven contract) the registry feeds.
- [ ] Parent ADR § Boundary Invariants #6 (one enforcement-claim surface, not two) and #7 (forcing impossible by construction — the two seam-pins this OBPI's metadata-only + direct-reference rules close).
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] `.claude/rules/tests.md` § REQ Scope Discipline — the BEHAVIOR / STRUCTURAL-FENCE proof channels this brief's REQs use

**Context:**

- [ ] `src/gzkit/traceability.py` — the `@covers` decorator + `LinkageRecord` registry and its decoration-time `ValueError` fail-close (the precedent to mirror)
- [ ] `src/gzkit/tasks.py` — the `@advances` decorator + registry (the parallel precedent)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/traceability.py` exists with the `@covers` decoration-time fail-close (the pattern source)
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `tests/governance/` reviewed for the local test convention before authoring `test_enforces_registry.py`
- [ ] `src/gzkit/traceability.py` reviewed for the registry shape and the import-time `ValueError` raise

## Quality Gates

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f src/gzkit/enforcement.py
test -f tests/governance/test_enforces_registry.py
```

## Demo

```bash
# A claim registers at import time and is discoverable; an unknown claim fails at decoration.
uv run python -c "from gzkit import enforcement; print('registered claims:', sorted(enforcement.registered_claims()))"
```

## Acceptance Criteria

- [ ] REQ-0.0.74-15-01 [behavior]: Given a `@enforces(claim, fixture, entrypoint)` decoration, when the module is imported, then an `EnforcementClaimRecord` is registered into the single claim-type-agnostic registry and is returned by the query accessor. (@covers test in `tests/governance/test_enforces_registry.py`)
- [ ] REQ-0.0.74-15-02 [behavior]: Given a malformed/typo claim id or an unknown claim, when the decorated module is imported, then decoration raises `ValueError` at import — the typo cannot ship (mirrors `@covers` / `@advances`). (@covers test in `tests/governance/test_enforces_registry.py`)
- [ ] REQ-0.0.74-15-03 [behavior]: Given a `@enforces`-decorated entrypoint, when it is called, then its runtime behavior is unchanged — the decorator returns the callable untouched and does not wrap it or pre-bind a kwarg (registration is metadata-only). (@covers test in `tests/governance/test_enforces_registry.py`)
- [ ] REQ-0.0.74-15-04 [structural-fence]: Every enforcement claim is registered through this single `@enforces` primitive into one registry — no second negative-control framework is forked; the qc_binding engine is generalized in place (parent ADR § Boundary Invariants #6 — one enforcement-claim surface, not two).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

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

Before: gzkit's only run-NC-in-production-and-assert-failure engine (qc_binding, ADR-0.0.73) was scoped to `gz check` STEPS — there was no claim-type-agnostic way to DECLARE "this claim is enforced, here is the violation builder and the production entrypoint" for a gate5 floor member or a structural-fence REQ. Now: `@enforces(claim, fixture, entrypoint)` is the single declaration primitive, fail-closed at decoration like `@covers`/`@advances`, feeding one registry the runner (OBPI-16) discovers — no second NC framework, the generalization §5 demands.

### Key Proof

### Implementation Summary

- **Decision item 15 (verbatim):** "The `@enforces(claim, fixture, entrypoint)` declaration + import-time registry — fail-closed at decoration on a typo / unknown claim (mirrors the `@covers` / `@advances` precedent in `src/gzkit/traceability.py`); registration metadata-only. (OBPI-15)"
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
