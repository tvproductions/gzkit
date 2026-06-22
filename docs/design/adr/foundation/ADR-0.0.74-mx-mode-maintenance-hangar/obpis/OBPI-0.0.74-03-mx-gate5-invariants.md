---
id: OBPI-0.0.74-03-mx-gate5-invariants
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 3
lane: Heavy
status: Completed
req_atomic:
  # The never-relax floor is one indivisible authoring unit: the gate5_invariants
  # code constant naming the FIVE never-relax guards (incl. grader-gaming) and the
  # structural guarantee that the leveled checkpoint cannot downgrade a member below
  # CRITICAL ship together (src/gzkit/mx/invariants.py plus the guard inside
  # src/gzkit/mx/checkpoint.py) with one covering test module. grader-gaming's
  # membership is made LIVE by OBPI-13 (the proxy-reality detector); this OBPI owns
  # the membership constant and the cannot-downgrade floor. No REQ below decomposes
  # into independently-attributable labor steps.
  - REQ-0.0.74-03-01  # gate5_invariants code constant naming the five never-relax guards (incl. grader-gaming)
  - REQ-0.0.74-03-02  # the leveled checkpoint structurally cannot downgrade a member below CRITICAL — same unit
  - REQ-0.0.74-03-03  # STRUCTURAL-FENCE: membership is the never-relax floor, grader-gaming a member
---

# OBPI-0.0.74-03-mx-gate5-invariants: Mx Gate5 Invariants

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #3 - "gate5_invariants — the never-relax floor as a code constant (faked Gate-5 attestation, secrets, operator-PII, ledger integrity, grader-gaming); structural proof the checkpoint cannot downgrade a member below CRITICAL; unit tests"

**Status:** Completed

## Objective

The never-relax floor lands as a code constant `GATE5_INVARIANTS` at `src/gzkit/mx/invariants.py` (a code constant, NOT config) naming the FIVE integrity-class guards — faked Gate-5 attestation, secrets, operator-PII, ledger integrity, and grader-gaming — and the leveled checkpoint at `src/gzkit/mx/checkpoint.py` is structurally unable to resolve any member below CRITICAL even under an active marker. grader-gaming joins because the observability system is itself a grader; its floor membership is made *live* (not merely named) by the proxy-reality detector (OBPI-13 / BI#5) per the §5 enforcement-claim rule. "Done" = the constant names exactly the five never-relax guards in code and unit tests prove the checkpoint cannot downgrade a member below CRITICAL.

## Lane

**Heavy** - This OBPI ships a runtime-contract surface — the never-relax floor on which airworthiness rests, which the leveled checkpoint reads and can never relax below CRITICAL — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/mx/__init__.py` (added by brief reconcile, attestor g0)
- `src/gzkit/mx/marker.py` (added by brief reconcile, attestor g0)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope (§ Decision item 3, § Boundary Invariants #3)
- `src/gzkit/mx/invariants.py` **CREATE** — the `GATE5_INVARIANTS` code constant naming the five never-relax guards (faked Gate-5 attestation, secrets, operator-PII, ledger integrity, grader-gaming)
- `src/gzkit/mx/checkpoint.py` — the leveled checkpoint reads `GATE5_INVARIANTS` and structurally cannot resolve a member below CRITICAL (consumer of the constant)
- `tests/mx/test_gate5_invariants.py` **CREATE** — unit tests for the constant's five-member set and the cannot-downgrade-below-CRITICAL guarantee
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-03-mx-gate5-invariants.md` — this brief (evidence recording)

## Creates These Files

- `src/gzkit/mx/invariants.py`
- `tests/mx/test_gate5_invariants.py`

## Denied Paths

- Paths not listed in Allowed Paths
- The `GZ_<LEVEL>` vocabulary (owned by OBPI-0.0.74-11) and the proxy-reality live detector that makes grader-gaming's membership live (owned by OBPI-0.0.74-13)
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: This OBPI MUST deliver: gate5_invariants — the never-relax floor as a code constant (faked Gate-5 attestation, secrets, operator-PII, ledger integrity, grader-gaming); structural proof the leveled checkpoint cannot downgrade a member below CRITICAL; unit tests.
1. REQUIREMENT: `GATE5_INVARIANTS` MUST name exactly the five never-relax guards in code (not config); grader-gaming is a member.
1. REQUIREMENT: Verification commands MUST be concrete and runnable before acceptance
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 3 — quoted verbatim:** "gate5_invariants — the never-relax floor. The integrity-class guards as a code constant (not config): faked Gate-5 attestation, secrets, operator-PII, ledger integrity, and grader-gaming. The marker can never downgrade a member below CRITICAL. grader-gaming joins because the observability system is itself a grader and the model games graders increasingly (Opus 4.8 § 6.1.2, named the most concerning training trend); a grader-gaming that could go advisory in the hangar would make MX the safe place to vibe undetected. Its floor membership is bound to a live detector (item 13) per the §5 enforcement-claim rule."
- [ ] Parent ADR § Boundary Invariants #3 — the set `{faked Gate-5 attestation, secrets, operator-PII, ledger integrity, grader-gaming}` is the never-relax floor.
- [ ] Parent ADR § Intent — the why-frame; 'Loose in the bay, hard at the door', the floor is what airworthiness rests on.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] `src/gzkit/mx/checkpoint.py` (OBPI-02) — the checkpoint that reads `GATE5_INVARIANTS` and can never relax a member
- [ ] `src/gzkit/mx/levels.py` (OBPI-11) — the `GZ_<LEVEL>` vocabulary; CRITICAL is the floor a member pins to
- [ ] OBPI-0.0.74-13 (proxy-reality detector) — makes grader-gaming's membership live, not named (BI#5)

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- [ ] `src/gzkit/mx/checkpoint.py` exists (OBPI-0.0.74-02 has landed)
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

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
test -f src/gzkit/mx/invariants.py
test -f tests/mx/test_gate5_invariants.py
```

## Demo

```bash
# The five never-relax guards as a code constant — none can resolve below CRITICAL.
uv run python -c "from gzkit.mx.invariants import GATE5_INVARIANTS; print(sorted(GATE5_INVARIANTS))"
```

## Acceptance Criteria

- [ ] REQ-0.0.74-03-01 [behavior]: Given `GATE5_INVARIANTS`, when it is read, then it is a code constant (defined in `src/gzkit/mx/invariants.py`, not loaded from config) naming exactly the five never-relax guards — faked Gate-5 attestation, secrets, operator-PII, ledger integrity, grader-gaming. (@covers test in `tests/mx/test_gate5_invariants.py`)
- [ ] REQ-0.0.74-03-02 [behavior]: Given an active marker, when the leveled checkpoint resolves a guard that is a member of `GATE5_INVARIANTS`, then the member's effective level stays CRITICAL — the checkpoint structurally cannot downgrade it below CRITICAL. (@covers test in `tests/mx/test_gate5_invariants.py`)
- [ ] REQ-0.0.74-03-03 [structural-fence]: Membership of `GATE5_INVARIANTS` is the never-relax floor on which airworthiness rests, and grader-gaming is a member; no marker, lane, or sensitivity can downgrade a member below CRITICAL. (parent ADR § Boundary Invariants #3 — gate5_invariants is the never-relax floor, grader-gaming a member)

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

Before: the never-relax floor was a four-member integrity set, and grader-gaming — the most concerning training trend (Opus 4.8 § 6.1.2) — had no floor protection, so a grader-gaming guard could go advisory in the hangar and make MX the safe place to vibe undetected. Now: grader-gaming is the fifth `GATE5_INVARIANTS` member, the leveled checkpoint cannot resolve any member below CRITICAL, and the membership is made live (not named) by OBPI-13's proxy-reality detector per the §5 enforcement-claim rule.

### Key Proof


$ uv run python -c "from gzkit.mx.invariants import GATE5_INVARIANTS; print(sorted(GATE5_INVARIANTS))"
['gate5-attestation', 'grader-gaming', 'ledger', 'operator-pii', 'secrets']

Structural proof: every member resolves to Route.AOG_MX_HANGAR (CRITICAL) even when WARNING is emitted, in or out of the hangar — verified by TestCheckpointCannotDowngradeInvariant (4 tests). Full suite 6394/6394 pass (receipt arb-step-unittest-bfe6514e169e4802af5f8c0525c7c6b1); lint clean (arb-ruff-95815aa7e71245a08bbb102886b180f6); typecheck clean (arb-step-typecheck-5310eaf4ca3a405a8827727e63be23f8).

### Implementation Summary


- Decision item 3 (verbatim): "gate5_invariants — the never-relax floor. The integrity-class guards as a code constant (not config): faked Gate-5 attestation, secrets, operator-PII, ledger integrity, and grader-gaming. The marker can never downgrade a member below CRITICAL."
- Created src/gzkit/mx/invariants.py: GATE5_INVARIANTS frozenset naming exactly the five never-relax guards; grader-gaming is the fifth, made live by OBPI-13's proxy-reality detector.
- Updated src/gzkit/mx/checkpoint.py: removed the local 4-member definition; now imports the canonical constant from invariants.py — the never-relax list lives in exactly one place.
- Tests added: tests/mx/test_gate5_invariants.py — 8 tests across two classes (constant shape + cannot-downgrade-below-CRITICAL).
- Date completed: 2026-06-22
- Attestation status: operator-attested ("attest completed")
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.74-03 lands GATE5_INVARIANTS as a 5-member frozenset code constant at src/gzkit/mx/invariants.py (grader-gaming the fifth), checkpoint.py imports the canonical constant so the never-relax list lives in one place, and 8 unit tests prove the leveled checkpoint resolves every member to AOG_MX_HANGAR (CRITICAL) in or out of the hangar. 6394/6394 tests pass (receipt arb-step-unittest-bfe6514e169e4802af5f8c0525c7c6b1), lint clean (arb-ruff-95815aa7e71245a08bbb102886b180f6), typecheck clean (arb-step-typecheck-5310eaf4ca3a405a8827727e63be23f8), docs clean (arb-step-mkdocs-9757904e3dca481eba2b567f76bb3e29).
- Date: 2026-06-22

---

**Date Completed:** 2026-06-22

**Evidence Hash:** -
