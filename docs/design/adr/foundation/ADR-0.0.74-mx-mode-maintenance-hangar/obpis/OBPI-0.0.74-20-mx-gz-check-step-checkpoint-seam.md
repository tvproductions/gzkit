---
id: OBPI-0.0.74-20-mx-gz-check-step-checkpoint-seam
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 20
lane: Heavy
status: Draft
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

**Status:** Draft

## Objective

Route the `gz check` audit-step layer and the five solo `gz validate` governance paths through the MX checkpoint at **one** seam in `check()`, so every MX-demotable governance guard resolves its disposition through `checkpoint.resolve` instead of self-deciding `returncode=3`/`SystemExit(3)` — closing the GHI #638 half of "every live guard" that OBPI-09/12 under-scoped, and extending ADR-0.0.74 BI#2 to the `gz check` surface.

## Lane

**Heavy** - changes the runtime fatality-decision contract of the `gz check` step layer (which guards block vs. demote, and under what marker state). No new CLI verb or flag; the `gz check`/`gz validate` surfaces already exist.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/commands/quality.py` — `_build_check_steps()` step list + the `check()` loop; this is where the seam lives (each step carries `guard_name` + emitted `GZ_<LEVEL>`; one wrapper resolves disposition via `checkpoint.resolve`)
- `src/gzkit/quality.py` — the `run_*_audit` wrappers that currently self-decide `returncode=3` (e.g. `run_handoff_document_audit`, `run_dispatch_attestation_audit`); stop self-deciding fatality, emit a level
- `src/gzkit/commands/validate_cmd.py` — the five solo handlers wired into `gz check` that `raise SystemExit(3)`: `--qc-binding`, `--fidelity-presence`, `--waiver-ratchet`, `--unscoped-rules`, `--evaluation-justify-binding`
- `tests/mx/test_check_step_checkpoint_seam.py` **CREATE** — the live-NC unit tests (marker-fixture demotion, full-strength-outside, floor-pin, excluded-path regression)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-20-mx-gz-check-step-checkpoint-seam.md` — this brief (evidence recording)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope

## Denied Paths

- `src/gzkit/mx/checkpoint.py`, `src/gzkit/mx/disposition.py`, `src/gzkit/mx/invariants.py` — the seam **routes through** the existing `checkpoint.resolve` authority; it does not modify it
- `src/gzkit/attestation_receipts.py` — the Gate-5 lane/kind pin (`fail_closed = lane==heavy or kind==foundation`) is a floor policy, NOT an MX-demotable sensor; out of scope
- The `--sensitivity` solo handler in `validate_cmd.py` (security floor/lane policy) — present in an allowed file but MUST NOT be routed through the demotable checkpoint (see Requirements #3)
- New dependencies, CI files, lockfiles
- Paths not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. ALWAYS: every MX-demotable `gz check` audit step and the five named solo `gz validate` paths declare a `guard_name` + emitted `GZ_<LEVEL>` and resolve disposition through `checkpoint.resolve` via **one** wrapper in `check()`.
2. NEVER: add ~30 inline `checkpoint.resolve` calls or a per-`run_*_audit` decorator — ADR-0.0.74 § Alternatives (a)/(b) rejected per-surface opt-in as the vibing surface. One seam, one firing point.
3. NEVER: route the excluded policy paths through the demotable checkpoint — `--sensitivity` (`validate_cmd.py`, security floor/lane) and the `attestation_receipts.py` lane/kind pin keep self-deciding. Their disposition under an active marker MUST be unchanged.
4. ALWAYS: a `gz check` step mapped to a `gate5_invariants` member (`{gate5-attestation, secrets, operator-pii, ledger, grader-gaming}`) pins CRITICAL and never demotes, in or out of the hangar.
5. ALWAYS: behavior-preserving outside the marker — every migrated step still returns `returncode=3` / exits 3 on a real violation when no marker is active.
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
# Live NC: a non-floor gz check step demotes to advisory under an active marker
# fixture, and exits 3 on the same known violation with no marker. The
# operator-facing hangar-entry -> advisory-check demo lands with the MX lean
# kernel (ADR-0.0.74 item 3); until then the seam is proven by the NC test.
uv run -m unittest tests.mx.test_check_step_checkpoint_seam -v

# Full check still green outside the hangar (behavior-preserving).
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

<!-- Filled at Gate 2: the live-NC pair (REQ-01 demote-under-marker / REQ-02 fatal-outside) output. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #638 — `mx: gz check step layer self-decides fatality outside the checkpoint (gates-as-sensors residual)`. This OBPI closes it; close `fixed` citing the implementing commit SHA at completion.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
