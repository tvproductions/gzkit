---
id: OBPI-0.0.74-19-floor-wiring
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 19
lane: Heavy
sensitivity: security
# req_atomic: each REQ is one coherent wiring increment — the gz check step (01),
# the pre-push wiring (02), the floor step's own qc NC (03) — plus the
# strict-no-debt sequencing fence (04). None decomposes into parallel seq=02+
# sub-tasks (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.74-19-01  # meta-validator wired into gz check; READ-ONLY on a clean run
  - REQ-0.0.74-19-02  # meta-validator wired into pre-push; READ-ONLY on a clean run
  - REQ-0.0.74-19-03  # the new gz check step registers its OWN qc negative control
  - REQ-0.0.74-19-04  # STRUCTURAL-FENCE: strict-no-debt sequencing — wiring lands LAST (BI#8)
status: Draft
---

# OBPI-0.0.74-19-floor-wiring: Floor Wiring

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #19 - "Floor wiring — wire the meta-validator into `gz check` and pre-push, read-only on a clean run, landing LAST only after the floor coverage is complete per the strict-no-debt sequence; registers the new `gz check` step's own qc negative control; unit tests"

**Status:** Draft

## Objective

Wire the meta-validator runner (OBPI-16) into the floor: register it as a `gz check` step (a `QualityResult`-returning wrapper in `src/gzkit/quality.py`, registered in the check assembly in `src/gzkit/commands/quality.py`, mirroring `run_qc_binding_audit`) and into the pre-push guard (`src/gzkit/hooks/guards.py`), READ-ONLY on a clean run (no ledger mutation when green). Register the new `gz check` step's OWN qc negative control in `_qc_negative_controls.py` so the floor step is itself enforcement-claim-covered (the floor that proves enforcement claims must itself have a live NC). This is the LAST organ and lands ONLY after OBPI-17 (gate5 floor migration) and OBPI-18 (fence-proof upgrade) complete — strict-no-debt: the teeth land last, when coverage is complete, because a partial floor that silently tolerates uncovered claims would itself be the facade this mechanism exists to kill. "Done" = `gz check` and pre-push run the meta-validator, both READ-ONLY on a clean run, the floor step carries its own qc NC, and unit tests pin the wiring + read-only behavior.

## Lane

**Heavy** - This OBPI changes runtime-contract surfaces — the `gz check` step registry and the pre-push guard — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Sensitivity

**security** — the Allowed Paths overlap registered security surfaces in `data/security_surfaces.json`: `src/gzkit/quality.py` and `src/gzkit/hooks/scripts/quality.py` (`subprocess_user_input`) and `src/gzkit/hooks/guards.py` (`subprocess_user_input`). Wiring a check step / pre-push guard touches the subprocess-spawning surface, so `sensitivity: security` is declared per `.claude/rules/security-sensitivity.md` (the auto-detect floor fails closed on an omitted declaration over a registered overlap). The change is additive (registering an existing read-only audit); the security walkthrough at completion enumerates the surface.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope (§ Decision item 19, § Boundary Invariants #8, § Consequences/Negative #8)
- `src/gzkit/quality.py` — add the `run_enforcement_floor_audit(project_root) -> QualityResult` wrapper around the OBPI-16 runner (mirrors `run_qc_binding_audit`), READ-ONLY on a clean run
- `src/gzkit/commands/quality.py` — register the floor step in the `gz check` step assembly (mirrors the `("QC binding", run_qc_binding_audit)` entry)
- `src/gzkit/hooks/guards.py` — wire the meta-validator into the pre-push guard, READ-ONLY on a clean run
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — register the new `gz check` step's OWN qc negative control (the floor step is itself enforcement-claim-covered)
- `tests/governance/test_enforcement_floor_wiring.py` **CREATE** — unit tests for the `gz check` step + pre-push wiring and the read-only-on-clean behavior
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-19-floor-wiring.md` — this brief (evidence recording)

## Creates These Files

- `tests/governance/test_enforcement_floor_wiring.py`

## Denied Paths

- Paths not listed in Allowed Paths
- Landing this OBPI BEFORE OBPI-0.0.74-17 and OBPI-0.0.74-18 complete — strict-no-debt sequences the floor wiring LAST, only when coverage is complete (§ Boundary Invariants #8)
- The meta-validator runner internals (`src/gzkit/enforcement.py`, OBPI-16) — this OBPI wires the existing runner in, it does not change its logic
- Adding a `_NEGATIVE_CONTROL_DEBT`-style escape, or making the floor step advisory/non-grounding, or mutating the ledger on a clean run — the floor is strict and read-only-on-clean
- Editing ledger internals (`ledger.py`, `ledger_events.py`, …)
- New dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The meta-validator MUST be registered as a `gz check` step (a `QualityResult` wrapper in `quality.py`, registered in `commands/quality.py`) and MUST be READ-ONLY on a clean run — no ledger mutation when green (REQ-19-01).
1. REQUIREMENT: The meta-validator MUST be wired into the pre-push guard (`hooks/guards.py`) and MUST be READ-ONLY on a clean run (REQ-19-02).
1. REQUIREMENT: The new `gz check` step MUST register its OWN qc negative control in `_qc_negative_controls.py` — the floor step that proves enforcement claims is itself covered by a live NC (REQ-19-03).
1. NEVER: Land this OBPI before OBPI-17 + OBPI-18 complete, or wire a floor that tolerates an uncovered enrolled claim — strict-no-debt; the teeth land last when coverage is complete (REQ-19-04).
1. ALWAYS: Reconcile the brief with the parent ADR before implementation; the runner (`src/gzkit/enforcement.py`, OBPI-16), the gate5 floor migration (OBPI-17), and the fence-proof upgrade (OBPI-18) MUST be complete first — STOP if missing.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 19 — quoted verbatim:** "Floor wiring — join the meta-validator to `gz check` / pre-push, READ-ONLY on a clean run; lands LAST (after 17 + 18) per strict-no-debt; registers the new `gz check` step's OWN qc NC. (OBPI-19)"
- [ ] Parent ADR § Boundary Invariants #8 (strict no-debt — the floor wires in only when coverage is complete) and § Consequences/Negative #8 (sequencing / blast-radius — the teeth do not exist during the migration window; accepted).
- [ ] Parent ADR § Decision § "The enforcement-claim meta-validator" — D3 (strict, no debt) and the land order 15 → 16 → 17 + 18 → 19.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] `.claude/rules/security-sensitivity.md` — the `sensitivity: security` walkthrough this brief's surface overlap triggers
- [ ] `data/security_surfaces.json` — the `subprocess_user_input` globs (`quality.py`, `hooks/guards.py`, `hooks/scripts/quality.py`) this brief overlaps

**Context:**

- [ ] `src/gzkit/quality.py` — `run_qc_binding_audit` (line ~783) and the `QualityResult` model; the wrapper shape to mirror for the floor step
- [ ] `src/gzkit/commands/quality.py` — the check step assembly (the `("QC binding", run_qc_binding_audit)` entry, line ~355) the floor step joins
- [ ] `src/gzkit/hooks/guards.py` — the pre-push guard surface the meta-validator wires into
- [ ] `src/gzkit/enforcement.py` (OBPI-16) — the runner this OBPI wires in; its read-only-on-clean contract
- [ ] `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — `_PRODUCTION_NEGATIVE_CONTROLS` (where the new step's own qc NC registers)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/enforcement.py` exists with the runner (OBPI-0.0.74-16 has landed)
- [ ] OBPI-0.0.74-17 (gate5 floor migration) and OBPI-0.0.74-18 (fence-proof upgrade) are complete — coverage is complete before the floor wires in
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `tests/governance/` reviewed for the local check-wiring test convention
- [ ] `run_qc_binding_audit` + its `commands/quality.py` registration reviewed as the parallel to mirror
- [ ] `hooks/guards.py` reviewed for how an existing guard is wired and runs read-only

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
- [ ] Security walkthrough recorded (surface enumeration + `arb-step-security-scan-*` receipt) per `sensitivity: security`

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f src/gzkit/quality.py
test -f tests/governance/test_enforcement_floor_wiring.py
```

## Demo

```bash
# The meta-validator runs as a gz check step, read-only on a clean run.
uv run gz check
```

## Acceptance Criteria

- [ ] REQ-0.0.74-19-01 [behavior]: Given the meta-validator runner, when `gz check` runs, then the meta-validator runs as a registered step and is READ-ONLY on a clean run (no ledger mutation when green). (@covers test in `tests/governance/test_enforcement_floor_wiring.py`)
- [ ] REQ-0.0.74-19-02 [behavior]: Given the pre-push guard, when it runs, then the meta-validator runs as part of the guard and is READ-ONLY on a clean run. (@covers test in `tests/governance/test_enforcement_floor_wiring.py`)
- [ ] REQ-0.0.74-19-03 [behavior]: Given the new `gz check` floor step, when the qc-binding audit runs, then the floor step carries its OWN registered qc negative control (the floor that proves enforcement claims is itself enforcement-claim-covered). (@covers test in `tests/governance/test_enforcement_floor_wiring.py`)
- [ ] REQ-0.0.74-19-04 [structural-fence]: The floor wiring lands LAST — only after OBPI-17 + OBPI-18 complete and the enrolled-claim coverage is complete; no `_NEGATIVE_CONTROL_DEBT`-style escape exists (parent ADR § Boundary Invariants #8 — strict no-debt; the floor wires in only when coverage is complete).

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
# Record attestation text + security walkthrough here when required by parent lane
```

### Value Narrative

Before: the meta-validator could be RUN manually (OBPI-16) to report coverage, but nothing made it a floor — `gz check` and pre-push did not run it, so an enforcement claim with no live NC could still ship. Now: the meta-validator is a `gz check` step and a pre-push guard, READ-ONLY on a clean run, and the floor step carries its own qc negative control — and because it lands LAST (after the gate5 floor migration and the fence-proof upgrade), the teeth bite only when coverage is complete, never as a partial floor that silently tolerates uncovered claims.

### Key Proof

### Implementation Summary

- **Decision item 19 (verbatim):** "Floor wiring — join the meta-validator to `gz check` / pre-push, READ-ONLY on a clean run; lands LAST (after 17 + 18) per strict-no-debt; registers the new `gz check` step's OWN qc NC. (OBPI-19)"
- Security surface (sensitivity: security): `src/gzkit/quality.py`, `src/gzkit/hooks/guards.py`, `src/gzkit/hooks/scripts/quality.py` (subprocess_user_input).
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
