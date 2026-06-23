---
id: OBPI-0.0.74-16-meta-validator-runner
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 16
lane: Heavy
status: Draft
# req_atomic: each REQ is one coherent increment of the single runner surface —
# discovery + run + strict fail-close (01), the read-only receipt (02), the
# FACADE-vs-TEST-BUG guardrail-feedback (03), the engine lift + 33-NC un-forced
# re-authoring (04), and the two cross-OBPI fences (05, 06). None decomposes
# into parallel seq=02+ sub-tasks (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.74-16-01  # runner discovers every claim, runs entrypoint(fixture()), asserts failure, strict fail-close
  - REQ-0.0.74-16-02  # emits enforcement_claim_verified receipt per claim; READ-ONLY on a clean run
  - REQ-0.0.74-16-03  # on failure emits per-claim FACADE-vs-TEST-BUG guardrail-feedback + single-NC repro command
  - REQ-0.0.74-16-04  # lift engine out of audit_qc_binding; re-author 33 qc_binding NCs un-forced; behavior preserved
  - REQ-0.0.74-16-05  # STRUCTURAL-FENCE: forcing impossible by construction, pinned at two seams (BI#7)
  - REQ-0.0.74-16-06  # STRUCTURAL-FENCE: strict no-debt — no _NEGATIVE_CONTROL_DEBT escape (BI#8)
---

# OBPI-0.0.74-16-meta-validator-runner: Meta Validator Runner

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #16 - "The meta-validator runner — discovers every `@enforces` claim, runs `entrypoint(fixture())` in production configuration, asserts failure, fail-closes strict with per-claim FACADE-vs-TEST-BUG guardrail-feedback and a single-NC repro command, emits an `enforcement_claim_verified` receipt, READ-ONLY on a clean run; lifts the engine out of `audit_qc_binding` and re-authors the 33 qc_binding negative controls un-forced; unit tests"

**Status:** Draft

## Objective

The meta-validator RUNNER lands at `src/gzkit/enforcement.py` (alongside the OBPI-15 registry): it discovers every `@enforces` claim, builds each NC's violation `fixture()`, invokes the production `entrypoint(fixture())` in production configuration, and asserts that it fails — the NC NEVER calls the validator itself, so forced-mode counterfactuals are impossible by construction (Boundary Invariant #7), not merely detected. It fail-closes STRICT: any enrolled claim lacking a passing un-forced NC fails the runner, with NO `_NEGATIVE_CONTROL_DEBT`-style escape (Boundary Invariant #8). On a clean run it is READ-ONLY (no ledger mutation) and emits one `enforcement_claim_verified` ledger receipt per claim; on failure it emits per-claim guardrail-feedback three-part prose (`.claude/rules/guardrail-feedback-prose.md`) distinguishing FACADE (the entrypoint did not fail on the violation — a claim adopted by nothing) from TEST-BUG (the fixture did not build), naming the single-NC repro command, not a bare failing count. It LIFTS the run-NC-in-production engine out of `audit_qc_binding` so qc_binding and the meta-validator share one engine, and re-authors the 33 qc_binding negative controls UN-FORCED (D1 — genuineness is absolute; forcing kwargs such as `fail_closed=True` are removed). "Done" = the runner discovers + runs + strict-fails as specified, the receipt/guardrail-feedback behavior is pinned, the engine is shared (not duplicated), and the 33 NCs pass un-forced with qc_binding's existing `gz check` behavior preserved.

## Lane

**Heavy** - This OBPI ships runtime-contract surfaces — the meta-validator runner, a new `enforcement_claim_verified` ledger event, and the re-authored shared NC engine — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope (§ Decision item 16, § Boundary Invariants #6, #7, #8)
- `src/gzkit/enforcement.py` **CREATE** — the runner (discovery, `entrypoint(fixture())` invocation, strict fail-close, read-only receipt, guardrail-feedback); net-new module introduced by OBPI-0.0.74-15 and extended here with the runner (CREATE-marked so the authoring-time existence gap is suppressed per GHI #419, since 15 lands before 16 per the strict-no-debt land order)
- `src/gzkit/events.py` — add the `enforcement_claim_verified` ledger event class to the `TypedLedgerEvent` union (the per-claim receipt)
- `src/gzkit/governance/trust_audits/qc_binding.py` — lift the run-NC-in-production engine out of `audit_qc_binding` into the shared runner; `audit_qc_binding` now calls the shared engine (behavior preserved)
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — re-author the 33 negative controls UN-FORCED (remove `fail_closed=True`-style forcing kwargs so each NC fails through the real production path)
- `tests/governance/test_enforcement_meta_validator.py` **CREATE** — unit tests for discovery/run/strict-fail, the read-only-on-clean receipt, the FACADE-vs-TEST-BUG guardrail-feedback, and the un-forced re-authoring
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-16-meta-validator-runner.md` — this brief (evidence recording)

(Security overlap check: no Allowed Path matches a glob in `data/security_surfaces.json` — `src/gzkit/events.py` is NOT in the `ledger_integrity` set (`ledger.py`/`ledger_events.py`/`ledger_proof.py`/`ledger_semantics.py`); `qc_binding.py` and `_qc_negative_controls.py` are under `governance/trust_audits/`, not a registered surface; `src/gzkit/enforcement.py` is the new metadata/runner module. `sensitivity: security` is not declared. The floor-wiring step that touches `src/gzkit/quality.py` is OBPI-0.0.74-19, which declares it.)

## Creates These Files

- `tests/governance/test_enforcement_meta_validator.py`

## Denied Paths

- Paths not listed in Allowed Paths
- The `@enforces` decorator / registry declaration surface (OBPI-0.0.74-15) — this OBPI consumes the registry, it does not redefine the decorator
- Wiring the runner into `gz check` / pre-push (`src/gzkit/quality.py`, `src/gzkit/commands/quality.py`, hooks) — that is OBPI-0.0.74-19 and lands LAST per strict-no-debt
- The gate5 floor NCs (OBPI-0.0.74-17) and the fence-proof upgrade (OBPI-0.0.74-18) — separate claim sources
- Re-introducing a forcing kwarg path (`fail_closed=True`, `force=...`) anywhere in the re-authored NCs — D1 forbids it; an NC must fail through the real path
- Adding a `_NEGATIVE_CONTROL_DEBT`-style escape to the enforcement-claim registry — strict no-debt (§ Boundary Invariants #8)
- Editing ledger internals (`ledger.py`, `ledger_events.py`, `ledger_proof.py`, `ledger_semantics.py`) — the receipt is emitted via the existing public event-append path; only the event CLASS is added to `events.py`
- New dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The runner MUST discover every `@enforces` claim, build each `fixture()`, invoke `entrypoint(fixture())` in production configuration, and assert it fails; the runner MUST fail closed STRICT if ANY enrolled claim lacks a passing un-forced NC (REQ-16-01).
1. REQUIREMENT: On a clean (all-pass) run the runner MUST be READ-ONLY (no ledger mutation) AND emit one `enforcement_claim_verified` receipt per claim through the existing public event-append path (REQ-16-02).
1. REQUIREMENT: On failure the runner MUST emit per-claim guardrail-feedback three-part prose distinguishing FACADE (entrypoint did not fail on the violation) from TEST-BUG (fixture did not build) and MUST name the single-NC repro command — never a bare failing count (REQ-16-03).
1. REQUIREMENT: The run-NC-in-production engine MUST be LIFTED out of `audit_qc_binding` into the shared runner so qc_binding and the meta-validator share one engine; the 33 qc_binding negative controls MUST be re-authored UN-FORCED (no forcing kwargs), and `audit_qc_binding`'s existing `gz check` behavior MUST be preserved (REQ-16-04).
1. NEVER: Let an NC call the validator it proves, or pre-bind a forcing kwarg into an entrypoint — forcing is impossible by construction, decided by the RUNNER via one uniform failure signal, not an author-supplied predicate (REQ-16-05).
1. ALWAYS: Reconcile the brief with the parent ADR before implementation; the `@enforces` registry (`src/gzkit/enforcement.py`, OBPI-0.0.74-15) MUST exist first — STOP if missing.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 16 — quoted verbatim:** "The meta-validator RUNNER — discovers every `@enforces` claim, runs each NC's `fixture()` through its production `entrypoint`, asserts failure; strict fail-close; emits an `enforcement_claim_verified` ledger receipt per claim; READ-ONLY on a clean run; on failure emits per-claim guardrail-feedback three-part prose ... distinguishing FACADE (entrypoint did not fail on the violation) from TEST-BUG (fixture did not build) plus the single-NC repro command; lifts the engine out of `audit_qc_binding` and re-authors the 33 qc_binding NCs un-forced. (OBPI-16)"
- [ ] Parent ADR § Decision § "The enforcement-claim meta-validator" — D1 (genuineness absolute, un-forced), D2 (runner-driven contract), D3 (strict no-debt).
- [ ] Parent ADR § Boundary Invariants #6 (one surface, not two), #7 (forcing impossible — two seam-pins), #8 (strict no-debt).
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] `.claude/rules/guardrail-feedback-prose.md` — the three-part prose contract the failure path emits
- [ ] `.claude/rules/tests.md` § REQ Scope Discipline — the BEHAVIOR / STRUCTURAL-FENCE proof channels this brief uses

**Context:**

- [ ] `src/gzkit/enforcement.py` (OBPI-15) — the registry the runner discovers
- [ ] `src/gzkit/governance/trust_audits/qc_binding.py` — `audit_qc_binding` (line ~179), `_NEGATIVE_CONTROL_DEBT` (line ~91); the engine to lift and the debt escape NOT to inherit
- [ ] `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — `_PRODUCTION_NEGATIVE_CONTROLS` and the forced `fail_closed=True` callsites (e.g. `_rendition_freshness_negative_control`) to re-author un-forced
- [ ] `src/gzkit/events.py` — `_EventBase` and the `TypedLedgerEvent` union the `enforcement_claim_verified` class joins; the existing public event-append path for the read-only-on-clean receipt

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/enforcement.py` exists with the `@enforces` decorator + registry (OBPI-0.0.74-15 has landed)
- [ ] `src/gzkit/governance/trust_audits/qc_binding.py` and `_qc_negative_controls.py` exist (the engine + 33 NCs to lift/re-author)
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `tests/governance/test_enforces_registry.py` (OBPI-15) reviewed for the local test convention
- [ ] `_qc_negative_controls.py` reviewed for the construct-violation / run-real-path / assert-caught shape and every forcing-kwarg callsite that must be re-authored un-forced
- [ ] `audit_qc_binding` reviewed for the engine boundary so the lift preserves its `gz check` step behavior

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
test -f tests/governance/test_enforcement_meta_validator.py
```

## Demo

```bash
# The runner reports coverage manually (before floor-wiring in OBPI-19): every
# discovered @enforces claim is run entrypoint(fixture()) and asserted to fail.
uv run python -c "from gzkit import enforcement; r = enforcement.run_meta_validator(); print('claims verified:', r.verified_count, 'facades:', r.facade_count)"
```

## Acceptance Criteria

- [ ] REQ-0.0.74-16-01 [behavior]: Given the `@enforces` registry, when `run_meta_validator()` runs, then it builds each `fixture()`, invokes `entrypoint(fixture())` in production configuration, asserts failure, and fail-closes STRICT if any enrolled claim lacks a passing un-forced NC. (@covers test in `tests/governance/test_enforcement_meta_validator.py`)
- [ ] REQ-0.0.74-16-02 [behavior]: Given an all-pass run, when the runner completes, then it mutates no ledger state (READ-ONLY on a clean run) and emits one `enforcement_claim_verified` receipt per claim through the existing public event-append path. (@covers test in `tests/governance/test_enforcement_meta_validator.py`)
- [ ] REQ-0.0.74-16-03 [behavior]: Given a failing claim, when the runner reports, then it emits per-claim guardrail-feedback three-part prose distinguishing FACADE (entrypoint did not fail on the violation) from TEST-BUG (fixture did not build) and names the single-NC repro command — not a bare failing count. (@covers test in `tests/governance/test_enforcement_meta_validator.py`)
- [ ] REQ-0.0.74-16-04 [behavior]: Given the lifted shared engine, when `audit_qc_binding` runs, then it uses the shared runner (one engine, not two) and all 33 qc_binding negative controls pass UN-FORCED (no forcing kwarg), with `audit_qc_binding`'s existing `gz check` step behavior preserved. (@covers test in `tests/governance/test_enforcement_meta_validator.py`)
- [ ] REQ-0.0.74-16-05 [structural-fence]: Forcing is impossible by construction — the runner invokes `entrypoint(fixture())`, the NC never calls the validator, the entrypoint is a direct production-callable reference, and catch/no-catch is decided by the runner via one uniform signal (parent ADR § Boundary Invariants #7 — forcing impossible by construction, pinned at two seams).
- [ ] REQ-0.0.74-16-06 [structural-fence]: The enforcement-claim registry has no `_NEGATIVE_CONTROL_DEBT`-style escape; the runner fail-closes if any enrolled claim lacks a passing un-forced NC (parent ADR § Boundary Invariants #8 — strict no-debt).

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

Before: the run-NC-in-production engine lived inside `audit_qc_binding`, scoped to `gz check` steps only, and several qc_binding NCs were FORCED (`fail_closed=True`) — a forced counterfactual proves nothing, the exact defeat ADR-0.0.73's antibody suffered. Now: one shared runner discovers every `@enforces` claim and runs `entrypoint(fixture())` un-forced, so a claim adopted by nothing (the GHI #637 facade class) cannot be made to fail and is reported as a FACADE with its single-NC repro command — and the 33 lifted NCs prove themselves through the real path, not a forced flag.

### Key Proof

### Implementation Summary

- **Decision item 16 (verbatim):** "The meta-validator RUNNER — discovers every `@enforces` claim, runs each NC's `fixture()` through its production `entrypoint`, asserts failure; strict fail-close; emits an `enforcement_claim_verified` ledger receipt per claim; READ-ONLY on a clean run; on failure emits per-claim guardrail-feedback three-part prose ... distinguishing FACADE (entrypoint did not fail on the violation) from TEST-BUG (fixture did not build) plus the single-NC repro command; lifts the engine out of `audit_qc_binding` and re-authors the 33 qc_binding NCs un-forced. (OBPI-16)"
- Coupled surfaces (behavior-preservation, AGENTS.md Rule 1a): `qc_binding.audit_qc_binding` (engine extracted, step behavior preserved); `_qc_negative_controls._PRODUCTION_NEGATIVE_CONTROLS` (33 NCs re-authored un-forced); `events.TypedLedgerEvent` (new `enforcement_claim_verified` member).
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
