---
id: OBPI-0.0.74-20-mx-gz-check-step-checkpoint-seam
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 20
lane: Heavy
status: Completed
# req_atomic: each REQ is one coherent surface authored in a single TDD
# increment — demote-under-marker (01), full-strength-outside (02), floor-pin
# (03), excluded-paths regression (04), and the cross-OBPI structural fence
# (05). None decomposes into parallel seq=02+ sub-tasks (ADR-0.0.64 exemption).
req_atomic:
  - REQ-0.0.74-20-01
  - REQ-0.0.74-20-02
  - REQ-0.0.74-20-03
  - REQ-0.0.74-20-04
  - REQ-0.0.74-20-05
---

# OBPI-0.0.74-20-mx-gz-check-step-checkpoint-seam: Mx Gz Check Step Checkpoint Seam

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #20 - "The `gz check` step-layer checkpoint seam — each `gz check` audit step + solo `gz validate` governance path declares its `guard_name` + emitted `GZ_<LEVEL>`; one wrapper in `check()` resolves disposition via `checkpoint.resolve` (not ~30 inline substitutions); non-floor guards demote to advisory under the hangar marker and run full-strength outside; `gate5_invariants` pin CRITICAL; `--sensitivity` + attestation lane/kind excluded; closes GHI #638; unit tests"

**Status:** Completed

## Objective

Route the `gz check` audit-step layer and the five solo `gz validate` governance paths through the MX checkpoint at **one** seam in `check()`, so every MX-demotable governance guard resolves its disposition through `checkpoint.resolve` instead of self-deciding `returncode=3`/`SystemExit(3)` — closing the GHI #638 half of "every live guard" that OBPI-09/12 under-scoped, and extending ADR-0.0.74 BI#2 to the `gz check` surface.

## Lane

**Heavy** - changes the runtime fatality-decision contract of the `gz check` step layer (which guards block vs. demote, and under what marker state). No new CLI verb or flag; the `gz check`/`gz validate` surfaces already exist.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/commands/quality.py` — `_STEP_GUARD_META` dict + `_apply_mx_seam()` helper + the `check()` loop; this is where the seam lives (each step carries `guard_name` + emitted `GZ_<LEVEL>`; one wrapper resolves disposition via `checkpoint.resolve`)
- `src/gzkit/traceability.py` — imported by the test for the `@covers` decorator (read-only import; not modified)
- `tests/mx/test_check_step_checkpoint_seam.py` **CREATE** — the live-NC unit tests (marker-fixture demotion, full-strength-outside, floor-pin, excluded-path regression)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-20-mx-gz-check-step-checkpoint-seam.md` — this brief (evidence recording)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope

> **Scope narrowing (2026-06-24, attestor g0).** The original draft listed
> `src/gzkit/quality.py` and `src/gzkit/commands/validate_cmd.py` as potentially
> modified, anticipating per-runner edits to the `run_*_audit` wrappers and the
> five solo `gz validate` handlers. The implemented seam is the ADR-mandated
> "ONE wrapper in `check()` — not ~30 inline substitutions" (item 20 / REQ-02):
> within `gz check`, the solo handlers run as subprocesses whose `returncode=3`
> is captured by their `run_*_audit` wrappers into a `QualityResult`, which the
> single `_apply_mx_seam` call in `check()` then routes through `checkpoint.resolve`.
> Neither `src/gzkit/quality.py` (a registered `subprocess_user_input` security
> surface) nor `validate_cmd.py` was modified — `git diff` is the proof — so both
> are removed from Allowed Paths to keep the brief honest and the security-floor
> overlap is genuinely absent, not waived.

## Denied Paths

- `src/gzkit/quality.py` — registered security surface; the seam design (item 20 / REQ-02) does NOT modify the `run_*_audit` wrappers, so this file is untouched
- `src/gzkit/commands/validate_cmd.py` — the five solo handlers are demoted via the subprocess-returncode funnel through `_apply_mx_seam`, not by editing the handlers; untouched
- `src/gzkit/mx/checkpoint.py`, `src/gzkit/mx/disposition.py`, `src/gzkit/mx/invariants.py` — the seam **routes through** the existing `checkpoint.resolve` authority; it does not modify it
- `src/gzkit/attestation_receipts.py` — the Gate-5 lane/kind pin (`fail_closed = lane==heavy or kind==foundation`) is a floor policy, NOT an MX-demotable sensor; out of scope
- The `--sensitivity` solo handler in `validate_cmd.py` (security floor/lane policy) — MUST NOT be routed through the demotable checkpoint (see Requirements #3)
- New dependencies, CI files, lockfiles
- Paths not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT [BEHAVIOR]: every MX-demotable `gz check` audit step resolves disposition through `checkpoint.resolve` via **one** wrapper in `check()`; each step declares a `guard_name` + emitted `GZ_<LEVEL>`. (REQ-0.0.74-20-01, REQ-0.0.74-20-02)
2. REQUIREMENT [BEHAVIOR]: ONE seam only — no ~30 inline `checkpoint.resolve` calls, no per-`run_*_audit` decorator. ADR-0.0.74 § Alternatives (a)/(b) rejected per-surface opt-in as the vibing surface. (REQ-0.0.74-20-01)
3. REQUIREMENT [BEHAVIOR]: excluded policy paths (`--sensitivity`, `attestation_receipts.py` lane/kind pin) MUST NOT be routed through the demotable checkpoint — they keep self-deciding; their disposition under an active marker MUST be unchanged. (REQ-0.0.74-20-04)
4. REQUIREMENT [BEHAVIOR]: a `gz check` step whose `guard_name` is in `gate5_invariants` (`{gate5-attestation, secrets, operator-pii, ledger, grader-gaming}`) pins CRITICAL and never demotes under a marker. (REQ-0.0.74-20-03)
5. REQUIREMENT [FENCE]: BI#2 holds at the `gz check` surface — no migrated step or solo `validate_cmd` path retains a self-deciding `returncode=3`/`SystemExit(3)` outside `checkpoint.resolve`. (REQ-0.0.74-20-05)
6. ALWAYS: reconcile this brief against parent ADR item 20 + BI#2 before implementation begins; work stays inside Allowed Paths.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 20 — quote verbatim** into the Implementation Summary: "The `gz check` step-layer checkpoint seam. Each `gz check` audit step and solo `gz validate` governance path declares its `guard_name` + emitted `GZ_<LEVEL>`; ONE wrapper in `check()` resolves disposition through `checkpoint.resolve` (the seam — not ~30 inline substitutions) …"
- [ ] Parent ADR § Intent + § Decision item 2 + Boundary Invariant #2 — the single-leveled-severity-authority frame this extends.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item 20, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract
- [ ] GHI #638 body — the verified counterexample list (file:line of each self-deciding path) and the "audit-step severity seam, not flat substitution" instruction
- [ ] GHI #637 precedent — `git show b7f2f58c` — how the `gz validate` scope dispatcher + rendition gates were routed through `checkpoint.resolve`; generalize that shape to the step layer

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/mx/checkpoint.py` — `resolve(guard_name, emitted_level, project_root)` and `is_advisory(guard_name, project_root)` (the routing target)
- [ ] `src/gzkit/mx/invariants.py` — `GATE5_INVARIANTS` frozenset (the floor membership the seam reads)
- [ ] `src/gzkit/mx/marker.py` — `Marker`, `write(marker, project_root)`, `is_active(project_root)` (the test fixture sets an active marker via `write`)

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/quality.py` — `_build_check_steps()` (the `(name, runner)` tuple list, ~290–363) and `check()` (~366+); the seam extends the tuple and adds one resolve in the loop
- [ ] `src/gzkit/quality.py` — `run_handoff_document_audit` (~887), `run_dispatch_attestation_audit` (~953/965): the `QualityResult(returncode=3)` self-deciders
- [ ] `src/gzkit/commands/validate_cmd.py` — solo handlers at ~532/551/574/597/653 (`SystemExit(3)`) and the EXCLUDED `--sensitivity` handler (~827) that must stay self-deciding
- [ ] `tests/mx/test_checkpoint.py` — the marker-fixture test convention to mirror

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item 20 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from the REQ acceptance criteria (the live-NC pair), not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] If a checkpoint-coverage note exists in the MX docs, record that the `gz check` step layer now routes through `checkpoint.resolve`

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/` (or record why no BDD scenario applies — the seam is unit-NC-proven and adds no new operator verb)

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded (see § Human Attestation; product-surface commands in § Demo)

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.mx.test_check_step_checkpoint_seam
uv run gz validate --documents
uv run mkdocs build --strict
test -f tests/mx/test_check_step_checkpoint_seam.py
```

## Demo

```bash
# The gz check audit-step seam routes every MX-demotable guard through the
# checkpoint. Seam behavior pinned by tests/mx/test_check_step_checkpoint_seam.py.
uv run gz check
```

## Acceptance Criteria

- [ ] REQ-0.0.74-20-01 [BEHAVIOR]: Given an active MX marker (fixture), when a non-floor `gz check` audit step runs through the seam against a known violation, then its disposition resolves to advisory (non-fatal) instead of `returncode=3`. (@covers test in `tests/mx/test_check_step_checkpoint_seam.py`)
- [ ] REQ-0.0.74-20-02 [BEHAVIOR]: Given NO active marker, when the same non-floor step runs against the same known violation, then it resolves fatal (`returncode=3` / exit 3) — full strength preserved outside the hangar. (@covers test in `tests/mx/test_check_step_checkpoint_seam.py`)
- [ ] REQ-0.0.74-20-03 [BEHAVIOR]: Given a `gz check` step mapped to a `gate5_invariants` member, when it runs under an active marker, then it pins CRITICAL and does not demote. (@covers test in `tests/mx/test_check_step_checkpoint_seam.py`)
- [ ] REQ-0.0.74-20-04 [BEHAVIOR]: Given the excluded policy paths (`--sensitivity`, attestation lane/kind), when the seam is applied, then their disposition under an active marker is unchanged — they are not routed through the demotable checkpoint. (@covers test in `tests/mx/test_check_step_checkpoint_seam.py`)
- [ ] REQ-0.0.74-20-05 [STRUCTURAL-FENCE]: BI#2 (no guard decides its own disposition outside the checkpoint) holds at the `gz check` step layer — no migrated step or solo `validate_cmd` path retains a self-deciding `returncode=3`/`SystemExit(3)` outside `checkpoint.resolve`. (Parent ADR ## Boundary Invariants #2, which cites OBPI-20.)

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

**Before:** ~30 `gz check` audit steps and 5 solo `gz validate` governance paths self-decide fatality (`returncode=3`/`SystemExit(3)`) without consulting the MX checkpoint (GHI #638). They cannot demote under the hangar marker, so BI#2 — "the checkpoint is the single leveled severity authority" — is violated at the `gz check` surface, and the gates-as-sensors capability does not yet fulfil its declared intent of "every live guard."

**Now:** one seam in `check()` routes each MX-demotable step through `checkpoint.resolve`; non-floor guards demote to advisory under an active marker and run full-strength outside, `gate5_invariants` members pin CRITICAL, and the two correctly-self-deciding policy paths stay out.

### Key Proof


The live-NC pair (REQ-01 demote / REQ-02 fatal):

    uv run -m unittest tests.mx.test_check_step_checkpoint_seam -v
    test_non_floor_step_demotes_to_advisory_under_marker ... ok
    test_non_floor_step_stays_fatal_without_marker ... ok
    Ran 7 tests in 0.036s — OK

Under an active MX marker fixture, a non-floor step's returncode=3 result resolves to success=True/returncode=0 via checkpoint.resolve(); with no marker the same result stays returncode=3 (full strength preserved). gate5_invariants members pin fatal regardless of marker (TestFloorPin). ARB receipts: arb-ruff-34f2d3dff84c42998647d08f315a9dfa (exit 0), arb-step-typecheck-19a9f633b6394245838e19d6513715ff (exit 0), arb-step-unittest-01b45b9f484a435a9931f56ddc20068c (exit 0, 6405/6405).

### Implementation Summary


- Files modified: src/gzkit/commands/quality.py — added _STEP_GUARD_META dict (37 step→guard_name/level mappings), _apply_mx_seam() seam helper, and one resolve call in the check() loop
- Files created: tests/mx/test_check_step_checkpoint_seam.py — 7 live-NC unit tests
- Tests added: demote-under-marker (REQ-01), fatal-outside (REQ-02), success-passthrough, floor-pin under+outside marker (REQ-03, 10 subtests over GATE5_INVARIANTS), excluded-paths regression x2 (REQ-04)
- Approach: ONE seam in check() (not ~30 inline substitutions) per ADR-0.0.74 item 20; guard metadata held in a central dict rather than per-runner decoration so the firing point stays single; tuple shape of _build_check_steps() unchanged (preserves 3 consuming tests)
- Date completed: 2026-06-24
- Attestation status: operator-attested
- Defects noted: GHI #638 closed by this OBPI

## Tracked Defects

- REQ-count drift: 4 declared vs 5 acceptance criteria (brief reconcile, attestor g0)

- REQ-count drift: 0 declared vs 5 acceptance criteria (brief reconcile, attestor g0)

- GHI #638 — `mx: gz check step layer self-decides fatality outside the checkpoint (gates-as-sensors residual)`. This OBPI closes it; close `fixed` citing the implementing commit SHA at completion.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.74-20 routes the ~37 gz check audit steps through the MX checkpoint at one seam (_apply_mx_seam in check()); 7 live-NC tests pass (demote-under-marker / fatal-outside / floor-pin / excluded-paths), full suite 6405/6405 green (receipt arb-step-unittest-01b45b9f484a435a9931f56ddc20068c), lint+typecheck clean (arb-ruff-34f2d3dff84c42998647d08f315a9dfa, arb-step-typecheck-19a9f633b6394245838e19d6513715ff); closes GHI #638, satisfies BI#2 at the gz check surface.
- Date: 2026-06-24

---

**Date Completed:** 2026-06-24

**Evidence Hash:** -
