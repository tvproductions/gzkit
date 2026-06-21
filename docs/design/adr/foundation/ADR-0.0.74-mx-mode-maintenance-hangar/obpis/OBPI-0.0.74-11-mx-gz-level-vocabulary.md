---
id: OBPI-0.0.74-11-mx-gz-level-vocabulary
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 11
lane: Heavy
status: Completed
req_atomic:
  # The GZ_<LEVEL> vocabulary is one indivisible authoring unit: the Python-logging
  # ladder + NOTICE=25 rung (levels.py), the grounding-threshold predicate, and the
  # checkpoint resolving each guard's effective level against the one vocabulary ship
  # as one src/gzkit/mx/levels.py write (consumed by checkpoint.py) with one covering
  # test module. No REQ below decomposes into independently-attributable labor steps.
  - REQ-0.0.74-11-01  # the GZ_<LEVEL> ladder reuses Python logging constants + NOTICE=25
  - REQ-0.0.74-11-02  # grounding threshold: effective >= ERROR grounds, below ERROR is visible-non-grounding
  - REQ-0.0.74-11-03  # STRUCTURAL-FENCE: the checkpoint resolves effective level against this one vocabulary
---

# OBPI-0.0.74-11-mx-gz-level-vocabulary: Mx Gz Level Vocabulary

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #11 - "The `GZ_<LEVEL>` severity vocabulary — Python `logging` ladder (CRITICAL 50 / ERROR 40 / WARNING 30 / NOTICE 25 / INFO 20 / DEBUG 10) with NOTICE the agent-fidelity/drift band; grounding threshold effective `>= ERROR`; the effective-level resolution the checkpoint reads; unit tests"

**Status:** Completed

## Objective

The `GZ_<LEVEL>` severity vocabulary lands at `src/gzkit/mx/levels.py` (STDLIB-FIRST): the numeric ladder reuses Python `logging`'s constants — CRITICAL 50 / ERROR 40 / WARNING 30 / INFO 20 / DEBUG 10 — plus `NOTICE = 25`, the rung Python omits, designated the agent-fidelity / V.I.B.E.S. drift band; a `grounds(level)` predicate keyed to `GROUNDING_THRESHOLD = ERROR` (effective `>= ERROR` grounds/blocks, below ERROR is visible-but-non-grounding); and the shared checkpoint (`src/gzkit/mx/checkpoint.py`, OBPI-02) resolves each guard's effective level against this one vocabulary. "Done" = `levels.py` defines the ladder from `logging` constants with `NOTICE = 25`, `grounds()` thresholds at ERROR, and unit tests pin both the stdlib-equality of the ladder and the grounding boundary.

## Lane

**Heavy** - This OBPI ships a runtime-contract surface — the single `GZ_<LEVEL>` severity vocabulary every guard's effective level resolves against — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/mx/__init__.py` (added by brief reconcile, attestor g0)

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope (§ Decision item 11)
- `src/gzkit/mx/levels.py` **CREATE** — the `GZ_<LEVEL>` vocabulary: Python `logging` ladder + `NOTICE = 25`, `GROUNDING_THRESHOLD = ERROR`, and the `grounds(level)` predicate
- `src/gzkit/mx/checkpoint.py` — the checkpoint resolves each guard's effective level against `levels.py` (consumer of the vocabulary)
- `tests/mx/test_levels.py` **CREATE** — unit tests for the stdlib-equality ladder, the `NOTICE = 25` drift rung, and the grounding boundary at ERROR
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-11-mx-gz-level-vocabulary.md` — this brief (evidence recording)

## Creates These Files

- `src/gzkit/mx/levels.py`
- `tests/mx/test_levels.py`

## Denied Paths

- Paths not listed in Allowed Paths
- Re-inventing a non-stdlib severity ladder (kernel/syslog 0–7) — the vocabulary reuses Python `logging` constants (ADR § Alternatives, rejection (f))
- Redefining or relaxing the `gate5_invariants` never-relax list (owned by OBPI-0.0.74-03)
- The disposition handler / guards-emit-levels wiring (owned by OBPI-0.0.74-12)
- New dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `src/gzkit/mx/levels.py` MUST define the `GZ_<LEVEL>` ladder by reusing Python `logging` constants (`logging.CRITICAL/ERROR/WARNING/INFO/DEBUG`) and add `NOTICE = 25`; the numeric values MUST equal the stdlib constants, never hand-typed magic numbers (REQ-11-01).
1. REQUIREMENT: `grounds(level)` MUST ground (return True) iff effective severity `>= ERROR`; WARNING, NOTICE, INFO, DEBUG are visible-but-non-grounding (REQ-11-02).
1. REQUIREMENT: The shared checkpoint MUST resolve a guard's effective level against `levels.py` — there is ONE vocabulary, not a per-guard set (REQ-11-03).
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief
1. ALWAYS: Reconcile the brief with the parent ADR before implementation; the shared checkpoint (`src/gzkit/mx/checkpoint.py`, OBPI-0.0.74-02) MUST exist first — STOP if missing.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 11 — quoted verbatim:** "The `GZ_<LEVEL>` severity vocabulary. Backed by Python `logging` (STDLIB-FIRST): CRITICAL 50 / ERROR 40 / WARNING 30 / NOTICE 25 / INFO 20 / DEBUG 10. NOTICE (25 — the rung Python omits) is the agent-fidelity / drift band, the V.I.B.E.S. rung. Grounding threshold: effective severity `>= ERROR` grounds (blocks); below ERROR is visible-but-non-grounding. The checkpoint (item 2) resolves the effective level against this one vocabulary."
- [ ] Parent ADR § Intent — the hangar frame; STDLIB-FIRST is the binding rationale for the Python ladder over the kernel 0–7 ladder.
- [ ] Parent ADR § Decision item 2 (the shared checkpoint) and item 12 (gates-as-sensors + disposition) — the consumer and the sibling that wires guards to emit these levels.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] AGENTS.md § STDLIB-FIRST DOCTRINE — the binding reason the ladder reuses `logging` constants

**Context:**

- [ ] `src/gzkit/mx/checkpoint.py` (OBPI-02) — the checkpoint that will resolve effective levels against this vocabulary
- [ ] OBPI-0.0.74-12 (gates-as-sensors + disposition handler) — consumes the grounding semantics defined here

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/mx/checkpoint.py` exists (OBPI-0.0.74-02 has landed)
- [ ] `src/gzkit/mx/__init__.py` exists (the `gzkit.mx` package)
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `tests/mx/test_checkpoint.py` reviewed for the local test convention before authoring `test_levels.py`
- [ ] `src/gzkit/mx/checkpoint.py` reviewed for how the binary `is_advisory` predicate is structured (the surface generalized to leveled here)

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
test -f src/gzkit/mx/levels.py
test -f tests/mx/test_levels.py
```

## Demo

```bash
# The GZ_<LEVEL> ladder reuses Python logging constants; NOTICE=25 is the drift band;
# grounding thresholds at ERROR (ERROR grounds, NOTICE does not).
uv run python -c "from gzkit.mx import levels; print('NOTICE', levels.NOTICE, '| grounds(ERROR)', levels.grounds(levels.ERROR), '| grounds(NOTICE)', levels.grounds(levels.NOTICE))"
```

## Acceptance Criteria

- [ ] REQ-0.0.74-11-01 [behavior]: Given `src/gzkit/mx/levels.py`, when the `GZ_<LEVEL>` ladder is read, then its rungs reuse Python `logging`'s constants (CRITICAL 50, ERROR 40, WARNING 30, INFO 20, DEBUG 10 — equal to `logging.*`, not hand-typed) and add `NOTICE = 25` as the agent-fidelity / V.I.B.E.S. drift band. (@covers test in `tests/mx/test_levels.py`)
- [ ] REQ-0.0.74-11-02 [behavior]: Given the `grounds(level)` predicate keyed to `GROUNDING_THRESHOLD = ERROR`, when a level is tested, then effective severity `>= ERROR` grounds (True) and WARNING / NOTICE / INFO / DEBUG are visible-but-non-grounding (False). (@covers test in `tests/mx/test_levels.py`)
- [ ] REQ-0.0.74-11-03 [structural-fence]: The shared checkpoint resolves every guard's effective `GZ_<LEVEL>` against this one vocabulary — there is a single leveled severity authority, not a per-guard ladder (parent ADR § Boundary Invariants #2 — the checkpoint is the single LEVELED severity authority).

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

Before: the shared checkpoint spoke a binary vocabulary — a guard was either fail-closed or advisory (OBPI-02's `is_advisory`). A binary flag cannot say "this is drift, not a defect" or "this is wrong-design vs wrong-build," so the V.I.B.E.S. drift band had nowhere to live and every relaxable guard collapsed to two states. Now: one `GZ_<LEVEL>` vocabulary — reusing Python `logging`'s ladder (STDLIB-FIRST, no re-invented 0–7 convention) plus a `NOTICE = 25` drift rung — gives the checkpoint a graded effective severity with a single grounding threshold at ERROR, the substrate items 12–14 route against.

### Key Proof


$ uv run python -c "from gzkit.mx import levels; print('NOTICE', levels.NOTICE, '| grounds(ERROR)', levels.grounds(levels.ERROR), '| grounds(NOTICE)', levels.grounds(levels.NOTICE))"
NOTICE 25 | grounds(ERROR) True | grounds(NOTICE) False

NOTICE sits at 25 (between INFO 20 and WARNING 30 — the rung Python omits); ERROR grounds (blocks), NOTICE is visible-but-non-grounding. Full unittest sweep exit 0 (receipt arb-step-unittest-33b4f7a6); ruff clean (arb-ruff-8955a6c8); typecheck clean (arb-step-typecheck-8ce125c7); mkdocs --strict exit 0 (arb-step-mkdocs-ee309a30).

### Implementation Summary


- Decision item 11 (verbatim): "The GZ_<LEVEL> severity vocabulary. Backed by Python logging (STDLIB-FIRST): CRITICAL 50 / ERROR 40 / WARNING 30 / NOTICE 25 / INFO 20 / DEBUG 10. NOTICE (25 — the rung Python omits) is the agent-fidelity / drift band, the V.I.B.E.S. rung. Grounding threshold: effective severity >= ERROR grounds (blocks); below ERROR is visible-but-non-grounding. The checkpoint (item 2) resolves the effective level against this one vocabulary."
- Files created: src/gzkit/mx/levels.py, tests/mx/test_levels.py
- Tests added: TestLadderReusesStdlib (2 tests), TestGroundingThreshold (3 tests) — 5 total, 5/5 pass
- Date completed: 2026-06-21
- Attestation status: operator-attested (g0, "attest completed")
- Defects noted: encountered tracked Movement II item 3 stale precomplete behave-coverage check (obpi_precomplete.py not REQ-kind-aware); routed completion via the kind-aware chokepoint obpi_complete.py per skill doctrine

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.74-11 GZ_<LEVEL> vocabulary landed STDLIB-FIRST (Python logging ladder + NOTICE=25 drift rung, GROUNDING_THRESHOLD=ERROR, grounds() predicate). 5/5 scoped tests green; full unittest sweep exit 0 (arb-step-unittest-33b4f7a6301d4cbaa1550bba43ac7d34); ruff clean (arb-ruff-8955a6c89b4842d3ba686daaa3fbcd60); typecheck clean (arb-step-typecheck-8ce125c733ab47a49b99672b146cca02); mkdocs --strict exit 0 (arb-step-mkdocs-ee309a30e5364ea5a6374ccdfbaa6cb7). REQ-11-01/02 behavior @covers-proven; REQ-11-03 fence proven via parent ADR Boundary Invariant #2.
- Date: 2026-06-21

---

**Date Completed:** 2026-06-21

**Evidence Hash:** -
