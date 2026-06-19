---
id: ADR-0.0.68-green-between-sessions-gate
status: Validated
kind: foundation
semver: 0.0.68
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-06-09
---

# ADR-0.0.68-green-between-sessions-gate: Green-Between-Sessions Gate

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.
Treats governance not as overhead but as the discipline that keeps work honest.
The operative stance for this ADR: **a floor, not a habit** — a green-between-sessions
property that any one session could let lapse is not a floor. The work here is to make
the gate un-removable, so the silent-red treadmill cannot re-form.

## Why foundation tier?

Without a standing green-between-sessions floor, gzkit re-enters the silent-red
treadmill: coupled-surface red (BDD scenarios, manpages, schemas, the
closeout-proof-binding / `ln` surface) accumulates undetected between sessions and
surfaces only as closeout archaeology. The invariance test resolves **yes** —
gzkit's identity **is** governance integrity / anti-vibe enforcement; a project that
cannot guarantee its own tree is verified green before work leaves the machine is not
the project. The floor is identity-shaping, not a feature.

Port-vs-adapter: this ADR is a **port**. "A verified-green floor that cannot silently
regress" is the abstract contract every working tree must honor; the specific pre-push
declaration in `.pre-commit-config.yaml` and the yaml-parsing `--session-green-gate`
validator are adapters behind it. Defining the gate as `gz check` *delegation* (not a
frozen validator list) is what keeps the port stable as the adapter set behind
`gz check` evolves — the forthcoming ln-sunset ADR retires one such adapter with zero
rewiring of this port.

## Intent

A working tree's `gz check` status MUST be verified green before work leaves the machine, and the gate that enforces this cannot be silently removed. Without this invariant, coupled-surface red (BDD scenarios, manpages, schemas, the closeout-proof-binding / `ln` surface) accumulates undetected between sessions — the named single root cause of the operator's restore-health / closeout-archaeology fatigue. This ADR establishes a standing green-between-sessions floor: a permanent, un-removable property of the project rather than a habit any one session can let lapse.

**Target state (after this lands).** Today a coupled-surface edit can leave the tree red, and that red travels silently across the session boundary — surfacing only as archaeology at the next ADR closeout, often weeks later. After this ADR lands, the target state is: no push leaves the machine without `gz check` having been verified green, and the gate enforcing that is itself asserted by `gz check`, so it cannot be deleted without the next run going red. The before-state is "red discovered at closeout, expensively"; the after-state is "red caught at push, the same session it was introduced." That shift — from late, costly discovery to immediate, cheap discovery — is the entire value of the invariant, and it is what converts every subsequent closeout from an archaeology dig into a routine attestation.

## Decision

Establish the green-between-sessions floor as three coupled parts — self-referential by design so the floor enforces its own wiring — decomposed into exactly two OBPIs (the surface boundary splits the version-controlled hook config from the validator runtime surface):

1. **Pre-push hook (OBPI-0.0.68-01, Lite).** A `pre-push` hook stage is declared in `.pre-commit-config.yaml` (version-controlled) running `gz check`, and installed locally via `pre-commit install --hook-type pre-push`. The stage catches red at the *session boundary* (push) — not at every commit — and the setup/runbook doc records the install step so a fresh clone is enforcing.

2. **Fail-closed declaration validator (OBPI-0.0.68-02, Heavy).** A new `gz validate --session-green-gate` scope parses `.pre-commit-config.yaml` and fails closed (exit 3) if no `stages: [pre-push]` hook running `gz check` is declared. The new validator scope is a runtime-contract surface (heavy lane): manpage + docs + a fail-close regression test.

3. **Self-referential wiring (OBPI-0.0.68-02, Heavy).** That validator is itself part of the `gz check` default scope, so deleting the pre-push declaration makes the NEXT `gz check` (next session, or CI) go red and surface it — the floor enforces its own wiring. The gate is defined as `gz check` DELEGATION, not a hardcoded validator list, so the forthcoming ln-sunset ADR (which retires the closeout-proof-binding surface `gz check` runs) needs ZERO rewiring of this gate.

**Rationale (why this shape).** The floor is justified because the operator's fatigue is specifically about *silent* regression: a hook alone is silently removable / `--no-verify`-skippable, which is the same failure class the ADR exists to kill, so the fail-closed validator is what earns the design. Numbered parts 1–3 are sequenced deliberately — the hook delivers catch-at-push value first, the validator makes it un-removable, and the self-referential wiring makes the validator enforce its own presence. The full per-alternative rationale (why not hook-only, SessionStart, pre-commit, or a hardcoded list) is recorded in § Alternatives Considered.

**Precedent and integration points (established codebase pattern):** this is not a novel mechanism — `--adr-status-fresh` is the existing exemplar of a fail-closed validator wired into `gz check` that detects drift in its own surface (`run_adr_status_fresh_audit` in `src/gzkit/quality.py`, listed in the `check()` default-scope audit set in `src/gzkit/commands/quality.py`, recovered by `gz register-adrs`). The new `--session-green-gate` scope follows that precedent exactly: a `run_*_audit` function in `src/gzkit/quality.py`, registered as a `--session-green-gate` flag in `src/gzkit/cli/parser_maintenance.py`, dispatched in `src/gzkit/commands/validate_cmd.py`, and added to the same `check()` audit set. The anti-pattern this guards against — a hardcoded validator list that couples the gate to today's scope set — is named and rejected in § Alternatives Considered (Alternative 4).

Lane: heavy (new `gz validate` scope = new runtime contract; new manpage; pre-commit config surface). Foundation kind per the invariance test: without a standing green-between-sessions floor the project re-enters the silent-red treadmill — identity-shaping, not a feature. Hexagonal lens: this is a **port** ("a verified-green floor that cannot silently regress" is the abstract contract); the specific pre-push declaration and the yaml-parsing validator are adapters behind it. Reversibility: two-way door (revert = delete the pre-push stage + the validator scope; low cost). Essential core is OBPI-01 (catch-at-push delivers value immediately); OBPI-02 makes the floor un-removable.

## Boundary Invariants

These are the structural fences this ADR establishes. They are audited at ADR closeout
(STRUCTURAL-FENCE proof channel), not by per-OBPI behavior tests.

1. **The session-green-gate asserts `gz check` DELEGATION, never a hardcoded validator
   list** (REQ-0.0.68-02-04). The `--session-green-gate` scope checks only the *declaration*
   of a `stages: [pre-push]` hook running `gz check` in `.pre-commit-config.yaml`; it never
   enumerates which validator scopes `gz check` runs. This is the fence that keeps the port
   ("a verified-green floor that cannot silently regress") stable as the adapter set behind
   `gz check` evolves: the forthcoming ln-sunset ADR (which retires the closeout-proof-binding
   surface `gz check` runs) requires ZERO rewiring of this gate. A future edit that couples the
   gate to a frozen scope list — re-introducing parent ADR § Alternatives Considered #4 — is a
   fail-close drift-back signal verified at this ADR's closeout.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| The fail-closed session-green gate confirms a pre-push gz-check hook is declared, so the green-between-sessions floor cannot be silently removed. | uv run gz validate --session-green-gate | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.0.68-green-between-sessions-gate --check | 0 |

## Consequences

### Positive

1. A **permanent green floor**: the tree's `gz check` status is verified green at every session boundary, so work never leaves the machine silently red.
2. Coupled-surface red (BDD scenarios, manpages, schemas, the closeout-proof-binding / `ln` surface) is caught at **push**, not discovered at closeout — every closeout after this gets cheaper.
3. The fail-closed declaration validator makes the gate **un-removable**: deleting the pre-push declaration turns the next `gz check` red and surfaces the removal, killing the silent-regression class the ADR exists to fight.
4. Defining the gate as **`gz check` delegation** (not a frozen validator list) means coverage grows automatically with `gz check`, and the forthcoming ln-sunset ADR retires the closeout-proof-binding surface with zero rewiring of this gate.
5. Exits the operator's restore-health / closeout-archaeology treadmill at its named single root cause — silent inter-session regression — rather than treating each instance.
6. Per the anti-vibing mantra, the floor is the steering-and-accountability surface that earns the foundation-ADR weight; "lighter ceremony" is explicitly not the tradeoff axis here.

### Negative

1. **Honest scope of guarantee:** the floor makes red UN-PERSISTABLE-UNDETECTED, NOT push IMPOSSIBLE-WHILE-RED. `git push --no-verify` can skip the hook once, but the declaration-validator + `gz check` delegation mean the red is caught at the next gate rather than buried until closeout. The `--no-verify` escape is a documented feature (the 2am emergency-hotfix path), not a hole.
2. **Documented residual risk (from the pre-mortem):** if `gz check` grows slow over time, operators may habitually `--no-verify`, and the declaration-only validator cannot detect skipped real runs. Mitigation: watch `gz check` wall-time and, if it creeps, split a fast pre-push subset from a full CI gate.
3. **Explicit NON-GOAL (operator decision, local-first):** a server-side CI `gz check` on `main` would close even the `--no-verify` gap, but is deliberately out of scope for this ADR and noted as a future follow-up.
4. New authoring/runbook surface: the pre-push install step (`pre-commit install --hook-type pre-push`) must be documented and followed on fresh clones, or the local hook is absent (the validator still fail-closes on a missing *declaration*, but a present declaration with an uninstalled hook is the residual-risk case in (2)).
5. The validator's yaml parse is coupled to the pre-commit config schema; a pre-commit upgrade that changed that schema could false-fail the validator — mitigated by parsing defensively (presence of a `pre-push`-staged `gz check` hook) rather than over-fitting the schema.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 0
- Logic/Engine: 1
- Interface: 2
- Observability: 0
- Lineage: 0
- Dimension Total: 3
- Baseline Range: 1-2
- Baseline Selected: 1
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 2

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.68-01: Declare and install the pre-push `gz check` hook — add a `pre-push` stage to `.pre-commit-config.yaml` running `gz check`, document `pre-commit install --hook-type pre-push` in the setup/runbook doc, and install it locally so the gate enforces immediately (Lite)
- [ ] OBPI-0.0.68-02: Implement `gz validate --session-green-gate` as a fail-closed floor — parse `.pre-commit-config.yaml`, exit 3 if no `stages: [pre-push]` hook running `gz check` is declared, wire the scope into the `gz check` default scope, add the manpage/docs and a fail-close regression test (Heavy)

## Q&A Transcript

<!-- Interview conducted 2026-06-09; answers ratified by operator (kind: foundation). Full design content lives in the sections above; this transcript records pointers. -->

**Problem / Intent:** see § Intent — coupled-surface red accumulates undetected between sessions; the named single root cause of restore-health / closeout-archaeology fatigue.

**Decision:** see § Decision — pre-push `gz check` hook (OBPI-01) + fail-closed `gz validate --session-green-gate` declaration validator wired into `gz check` itself (OBPI-02); gate defined as `gz check` delegation so it is self-enforcing and ln-sunset-stable.

**Consequences:** see § Consequences — permanent green floor; red caught at push not closeout; honest scope (un-persistable-undetected, not push-impossible-while-red); local-first CI gap is an explicit NON-GOAL.

**Alternatives:** see § Alternatives Considered — hook-only / SessionStart / pre-commit-stage / hardcoded-validator-list, each rejected.

**Forcing functions (load-bearing):** see § Stress-test forcing functions (Tier 2). Shakiest condition (WWHTBT): `gz check` stays fast enough that operators don't habitually `--no-verify`. Reversibility: two-way door. Scope-min essential core: OBPI-01.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Config (OBPI-01): `.pre-commit-config.yaml` gains a `stages: [pre-push]` hook running `gz check`
- [ ] Docs (OBPI-01): setup/runbook records `pre-commit install --hook-type pre-push`
- [ ] Validator (OBPI-02): `gz validate --session-green-gate` scope wired into the `gz check` default scope
- [ ] Tests (OBPI-02): fail-close regression test asserting exit 3 when no `pre-push` `gz check` hook is declared
- [ ] Docs (OBPI-02): manpage entry for the new `--session-green-gate` scope; `gz cli audit` + `mkdocs build --strict` green
- [ ] Four Gates: Gate 1 (this ADR), Gate 2 (TDD), Gate 3 (docs, heavy), Gate 4 (BDD scope per OBPI), Gate 5 (human attestation)

## Alternatives Considered

1. **Hook-only (no validator floor).** A pre-push hook with no fail-closed validator backing it is silently removable / `--no-verify`-able / never-installed with nobody noticing — the same silent-regression class this ADR exists to kill. REJECTED: no fail-close; the floor would not be a floor.

2. **SessionStart gate.** Running the suite at session boot taxes every session with a multi-minute run; SessionStart is read-only orientation and should not run tests; and it catches red late (at boot) rather than at push. REJECTED: wrong frequency, wrong responsibility, wrong timing.

3. **pre-commit stage (flip the manual unittest hook to `pre-commit`).** A full-suite + behave gate at per-commit frequency is far too high a tax for the commit cadence. REJECTED: catches at the wrong (too-frequent) boundary.

4. **Hardcoded validator list instead of `gz check` delegation.** Coupling the gate to the current validator set means the ln-sunset ADR (which retires the closeout-proof-binding surface) would require rewiring this gate. REJECTED for coupling; delegation to `gz check` is the decoupled shape.

## Stress-test forcing functions (Tier 2)

**Pre-mortem (failed in 18 months, why):** (1) `gz check` grew slow → habitual `git push --no-verify` → the gate became declared-but-bypassed theater; the declaration-only validator cannot detect skipped runs. (2) behave non-determinism made the gate flap red → trust eroded → disabled. (3) the validator's yaml-parse was over-coupled to pre-commit's config schema; a pre-commit upgrade changed the schema → validator false-failed → noise.

**What-would-have-to-be-true:** `gz check` stays fast enough (~couple of minutes) that operators don't habitually bypass — this is the SHAKIEST condition and the biggest risk; and the committed declaration is a faithful proxy for actual enforcement. For hook-only to have been the better choice, operators would have to be self-disciplined and un-removability never tested — contradicted by the documented fatigue that motivated this ADR.

**Constraint archaeology:** "sessions are push-bounded" — REAL, observed this session (ahead=0/behind=0 at boot, handoff-mediated continuity); not an inherited assumption.

**Assumption surfacing:** the implicit assumption that `gz check` green ≈ tree healthy. If real inter-session red lives in a surface `gz check` does not run, the gate gives false confidence — mitigated by defining the gate as `gz check` delegation (coverage grows with `gz check`) rather than a frozen list.

**2am operator:** the gate blocks an emergency hotfix push; the operator needs an intentional, documented escape (`git push --no-verify`), which the design already acknowledges; the next `gz check` catches anything slipped. The escape is a feature, not a hole.

**Reversibility:** two-way door. Revert = delete the pre-push stage + the validator scope; low cost; favors adoption.

**Scope minimization:** the smallest valuable version is OBPI-01 (pre-push hook) alone — it delivers catch-at-push immediately. OBPI-02 (validator floor) makes it un-removable. The operator chose both; the essential core is OBPI-01.

**Closing — downstream ADRs forced:** (a) the ln-sunset ADR is now implemented UNDER this gate; (b) a possible future CI-gate ADR to close the `--no-verify` gap; (c) a possible "gz check performance budget" concern if `gz check` slows.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.68 | Completed | Jeffry | 2026-06-09 | Completed — green-between-sessions gate verified live: pre-push gz-check hook Passed (exit 0), gz validate --session-green-gate exit 0, gz check 27/27 incl ✓ Session green gate; 6 REQs ledger-bound (arb receipts 0202269a/41bf3d47/69a321fc for OBPI-01, b33f1ba8/a0d3ff4e/0faf68d7/a610c061 for OBPI-02); spec-reviewer PASS, quality-reviewer COHERENT |
