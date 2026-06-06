---
id: OBPI-0.0.37-20-setpoint-declaration-coherence-validator
parent: ADR-0.0.37-constitutional-invariant-composition
item: 20
lane: Heavy
status: Completed
# req_atomic: each REQ is a single indivisible labor unit — REQ-01/02/03 are the
# three exit-code facets of one validator scope (uncovered-pair, illegal-token,
# coherent-pass), REQ-04 the accessor fail-closed contract, REQ-05 the manpage
# SUPPORT doc; none decomposes into parallel seq=02+ sub-tasks (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.37-20-01
  - REQ-0.0.37-20-02
  - REQ-0.0.37-20-03
  - REQ-0.0.37-20-04
  - REQ-0.0.37-20-05
---

# OBPI-0.0.37-20-setpoint-declaration-coherence-validator: Setpoint Declaration Coherence Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #20 - "OBPI-0.0.37-20 — Setpoint declaration + coherence validator (compression target per surface×consumer in `data/vendor-manifest.json` `content_type_temperatures`; `gz validate` scope asserts every (surface×consumer) has a declared setpoint; re-homes prior 13/15 substrate)"

**Status:** Completed

## Objective

Deliver the **setpoint thermostat** half of the re-aligned CMS pipeline: (a) formalize the declared-setpoint accessor on `src/gzkit/content/vendors.py` (`temperature_for`, already fail-closed on undeclared pairs) as the canonical read path, and (b) add a new fail-closed `gz validate --setpoint-coherence` scope that asserts every `(content_type × consumer)` pair present in `content_type_routes` has a legal declared setpoint in `content_type_temperatures`. The setpoint is the compression *target* the OBPI-21 composer drives toward; this OBPI delivers only the declaration surface and its coherence gate — no composer, no rendition store, no playback.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

The new `gz validate --setpoint-coherence` CLI flag is a runtime-contract addition → Heavy. Gate 5 human attestation is mandatory (foundation/heavy; no self-close).

## Allowed Paths

- `src/gzkit/content/vendors.py` — formalize `temperature_for` as the canonical declared-setpoint accessor (fail-closed on undeclared pair, already present at line 119); add legal-token + coherence helpers consumed by the validator scope
- `src/gzkit/governance/trust_audits/setpoint_coherence.py` — **NEW** validator module (one-scope-per-module convention, cf. `sensitivity.py`, `vendor_manifest.py`)
- `src/gzkit/governance/trust_audits/__init__.py` — export the new audit function (re-export convention)
- `src/gzkit/cli/parser_maintenance.py` — register the `--setpoint-coherence` argparse flag (cf. `--sensitivity`, `--invariant-coherence`, `--vendor-manifest` registrations)
- `src/gzkit/commands/validate_cmd.py` — wire the scope into the dispatch table and the scope-name registry (cf. `_invariant_coherence_runner`)
- `data/vendor-manifest.json` — declare the missing setpoints so the coherence gate passes against real canon (see § Open Implementation Decision)
- `data/behave_coverage_waivers.json` — OBPI-level behave-coverage waiver for REQ-04 (pure accessor, no CLI surface → unit-proven) and REQ-05 (SUPPORT → ledger+validator); the behave_req_coverage gate is REQ-kind-agnostic
- `tests/governance/test_setpoint_coherence.py` — **NEW** unit tests for the validator scope (REQ-01/02/03)
- `tests/content/test_vendor_manifest.py` — accessor fail-closed test (REQ-04; existing file where `temperature_for` is already exercised)
- `features/setpoint_coherence.feature` — **NEW** BDD scenario (Gate 4, Heavy)
- `features/steps/setpoint_coherence_steps.py` — **NEW** step definitions
- `docs/user/manpages/validate.md` — document the new scope (Gate 3, Heavy; REQ-05)
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (evidence/checklist read only; no structural edit beyond checklist checkbox at closeout)
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-20-setpoint-declaration-coherence-validator.md` — this brief (evidence)

## Denied Paths

- Paths not listed in Allowed Paths
- New runtime dependencies (stdlib-first; the manifest read is stdlib `json` already in `vendors.py`)
- CI files, lockfiles
- `src/gzkit/schemas/vendor_manifest.json` — the legal-token enum `["lite","medium","heavy"]` already exists there; this OBPI reads it, does not edit it
- The composer / rendition store / playback surfaces (OBPI-21/22) — out of scope for the setpoint declaration + coherence gate
- Adding `--setpoint-coherence` to the default `gz check` scope — a new always-on gate during recovery is a separate operator decision (see § Open Implementation Decision)

## Creates These Files

Net-new paths this OBPI creates (exempt from the brief-path existence gate per GHI #419; they exist in contract before they exist on disk):

- `src/gzkit/governance/trust_audits/setpoint_coherence.py` — the validator scope module
- `tests/governance/test_setpoint_coherence.py` — unit tests for the scope (REQ-01/02/03)
- `features/setpoint_coherence.feature` — BDD scenario (Gate 4)
- `features/steps/setpoint_coherence_steps.py` — step definitions

All other Allowed Paths reference existing files modified in place.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz validate --setpoint-coherence` MUST exit 3 (fail-closed) when any `(content_type, vendor)` pair present in `content_type_routes` has no entry in `content_type_temperatures`.
1. REQUIREMENT: the scope MUST exit 3 when a declared setpoint token is not one of `{lite, medium, heavy}`.
1. REQUIREMENT: the scope MUST exit 0 only when every routed pair has a legal declared setpoint.
1. REQUIREMENT: `temperature_for(content_type, vendor, *, project_root)` MUST raise `ValueError` (fail-closed) on an undeclared pair — no baked-in vendor-locked default (re-affirms the prior fail-closed accessor contract established under OBPI-0.0.37-15, operator directive 2026-06-03).
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.
1. NEVER: add `--setpoint-coherence` to the default `gz check` scope without a separate operator decision.
1. NEVER: edit the legal-token enum in `src/gzkit/schemas/vendor_manifest.json` under this OBPI.
1. NEVER: mark this OBPI completed without explicit Gate 5 human attestation (foundation/heavy).
1. ALWAYS: reconcile this brief with the parent ADR before implementation begins (`gz brief reconcile`).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Open Implementation Decision (operator confirmation at Gate 5)

The current `data/vendor-manifest.json` declares setpoints for **only** `AgentContract` (`{codex: lite, claude: heavy}`), but `content_type_routes` routes **8** content types — `Bullet`, `Chore`, `Handoff`, `Persona`, `Rule`, `Scenario`, `Skill` all route to `claude` with **no** declared setpoint. Under the forward-coherence rule (REQ-01) the validator fails-closed against current canon until those 7 pairs are declared. Two readings, surfaced rather than resolved unilaterally (Behavior Rule Always #9):

- **(A) Declare all routed pairs (faithful to the captured spec).** Add a setpoint for each routed pair. The AGENTS.md composer (OBPI-21) compresses only `AgentContract`; non-`AgentContract` surfaces are not yet compression targets, so the natural token is `heavy` (fullest-retention tier, closest to verbatim — a no-compression sentinel). Coherence domain = `content_type_routes`.
- **(B) Narrow the coherence domain.** `content_type_routes` (vendor mirroring) and `content_type_temperatures` (compression setpoints) are arguably orthogonal axes that share a key shape; coherence could be scoped to surfaces that ARE compression targets (today: `AgentContract` only).

**Recommendation: (A)** — it matches the checklist item's "every (surface×consumer) has a declared setpoint" wording and the captured operator spec, with `heavy` as the non-compressed sentinel. Confirm or redirect at Gate 5 before the manifest edit lands.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [x] **Parent ADR § Decision item — quoted verbatim** into § Implementation Summary below (Discovery Order Pin). The re-aimed mechanism part 2 (Temperature = compression setpoint / thermostat) is the contract this OBPI implements.
- [x] Parent ADR § Decision Re-Alignment (2026-06-03) § "The re-aimed mechanism — four parts + one pipeline" — the why-frame.
- [x] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. (Quote is in § Implementation Summary.)

**Governance (read once, cache):**

- [x] `AGENTS.md` — agent operating contract; § Defect-fix routing, § OBPI Acceptance Protocol, § Attestation
- [x] `.claude/rules/governance-core.md` — operator-doc verb resolution (`gz validate --cli-alignment` binds REQ-05)

**Context:**

- [x] Related OBPIs in same ADR: OBPI-21 (composer, consumes the setpoint), OBPI-22 (rendition store + playback), OBPI-26 (#519 Codex-root setpoint application — consumes this declaration surface)
- [x] `src/gzkit/schemas/vendor_manifest.json` — legal-token enum `["lite","medium","heavy"]`; `content_type_temperatures` optional, `content_type_routes` required

**Prerequisites (check existence, STOP if missing):**

- [x] `data/vendor-manifest.json` exists with `content_type_routes` (8 types) + `content_type_temperatures` (AgentContract only)
- [x] `src/gzkit/content/vendors.py` `temperature_for` accessor present (line 119, fail-closed)
- [x] `src/gzkit/governance/trust_audits/` is a one-scope-per-module package (`setpoint_coherence.py` is green-field, convention-consistent with `.py` siblings)
- [x] `features/` + `features/steps/` host `.feature` + `*_steps.py` pairs (convention confirmed; `setpoint_coherence` files are green-field)

**Existing Code (understand current state):**

- [x] `src/gzkit/commands/validate_cmd.py` dispatch pattern for `invariant_coherence` (lines 309/320–324) and `sensitivity` is the template for the new runner
- [x] `src/gzkit/cli/parser_maintenance.py` flag-registration pattern (`--invariant-coherence` line 601, `--sensitivity` line 545, `--vendor-manifest` line 657)
- [x] `tests/content/test_vendor_manifest.py` reviewed for existing `temperature_for` coverage before adding REQ-04 assertion (avoid cosmetic `@covers` backfill — re-derive if a drifted assertion exists)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted (§ Implementation Summary)

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from this brief's REQ acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment (RED first for each of REQ-01/02/03/04)
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/user/manpages/validate.md` documents `--setpoint-coherence`; `gz validate --cli-alignment` resolves it (REQ-05)

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenario passes: `uv run -m behave features/setpoint_coherence.feature`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded (mandatory; foundation/heavy; no self-close)
- [ ] § Open Implementation Decision confirmed or redirected by operator

## Verification

```bash
# Coherence gate — exits 0 on coherent canon, 3 on a gap or illegal token
uv run gz validate --setpoint-coherence

# Doc reference resolves (REQ-05)
uv run gz validate --cli-alignment

# Standard quality bundle
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/setpoint_coherence.feature

# Specific surface checks for this OBPI
test -f src/gzkit/governance/trust_audits/setpoint_coherence.py
test -f tests/governance/test_setpoint_coherence.py
test -f features/setpoint_coherence.feature
```

## Demo

```bash
# 1. Coherent manifest → exit 0
uv run gz validate --setpoint-coherence
# → "Validated: setpoint-coherence" (exit 0)

# 2. Introduce a routed pair with no setpoint (temporarily) → exit 3
#    (e.g. add "NewType": ["claude"] to content_type_routes with no temperature)
uv run gz validate --setpoint-coherence
# → exit 3, error: (NewType, claude) routed but no declared setpoint

# 3. Accessor fail-closed on an undeclared pair
uv run python -c "from pathlib import Path; from gzkit.content.vendors import temperature_for; temperature_for('NoSuch','claude',project_root=Path('.'))"
# → ValueError: No temperature declared for ('NoSuch', 'claude') ...
```

## Acceptance Criteria

- [ ] REQ-0.0.37-20-01 [BEHAVIOR]: Given a manifest where a `(content_type, vendor)` pair in `content_type_routes` has no entry in `content_type_temperatures`, when `gz validate --setpoint-coherence` runs, then it exits 3 with an error naming the uncovered pair. Proof: `@covers`-decorated test in `tests/governance/test_setpoint_coherence.py`.
- [ ] REQ-0.0.37-20-02 [BEHAVIOR]: Given a manifest with a declared setpoint token outside `{lite, medium, heavy}`, when `gz validate --setpoint-coherence` runs, then it exits 3 with an illegal-token error. Proof: `@covers`-decorated test.
- [ ] REQ-0.0.37-20-03 [BEHAVIOR]: Given a manifest where every routed pair has a legal declared setpoint, when `gz validate --setpoint-coherence` runs, then it exits 0. Proof: `@covers`-decorated test.
- [ ] REQ-0.0.37-20-04 [BEHAVIOR]: Given an undeclared `(content_type, vendor)` pair, when `temperature_for` is called, then it raises `ValueError` (fail-closed) rather than resolving a baked-in default. Proof: `@covers`-decorated test in `tests/content/test_vendor_manifest.py`.
- [ ] REQ-0.0.37-20-05 [SUPPORT]: `docs/user/manpages/validate.md` documents the `--setpoint-coherence` scope and the reference resolves — proof `gz validate --cli-alignment` (exit 0) + `artifact_edited` ledger event on the manpage edit.

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

**Problem before:** The setpoint thermostat (parent ADR § Decision Re-Alignment, re-aimed mechanism part 2) is declared in `data/vendor-manifest.json` but nothing asserts that every surface the system mirrors actually has a declared compression target. A routed `(surface × consumer)` pair could silently lack a setpoint, and the composer (OBPI-21) would have no target to drive toward — a hollow, drift-prone substrate.

**Capability now:** A fail-closed `gz validate --setpoint-coherence` gate makes the declaration surface coherent: every routed pair must carry a legal setpoint, and the canonical accessor (`temperature_for`) raises rather than resolving a baked-in default. The thermostat now has a structural witness before the composer that consumes it is built.

### Key Proof


```text
$ uv run gz validate --setpoint-coherence
Validated: setpoint_coherence
✓ All validations passed (1 scopes).        # exit 0 on the fully-declared manifest
```

A routed `(content_type, vendor)` pair lacking a declared setpoint, or an illegal token, exits 3 — proven by `TestSetpointCoherence.test_routed_pair_without_setpoint_is_flagged` / `test_illegal_setpoint_token_is_flagged` and the BDD scenarios in `features/setpoint_coherence.feature`. The `temperature_for` accessor raises `ValueError` on an undeclared pair (`TestTemperatureAccessorFailClosed`).

ARB receipts: `arb-step-unittest-87dafd5e7bca4e73b3011300a59fda93`, `arb-ruff-a672da842df64da1bd821917d9922051`, `arb-step-typecheck-4704815cca33475a9e0ed5e98089c5f8`, `arb-step-behave-8bb6c34e50524d79a0f4029cd56ba2ea`, `arb-step-mkdocs-d01b2e676bac4b1ca31740caa34f361b`. `gz covers` reports behavior_uncovered_reqs=0.
```

### Implementation Summary


- Files created: `src/gzkit/governance/trust_audits/setpoint_coherence.py` (validator scope); `tests/governance/test_setpoint_coherence.py`; `features/setpoint_coherence.feature` + `features/steps/setpoint_coherence_steps.py`.
- Files modified: `src/gzkit/content/vendors.py` (`SETPOINT_TOKENS` constant); `src/gzkit/governance/trust_audits/__init__.py` (re-export); `src/gzkit/cli/parser_maintenance.py` (`--setpoint-coherence` flag + dispatch); `src/gzkit/commands/validate_cmd.py` (runner + wiring + policy-breach type); `data/vendor-manifest.json` (7 heavy sentinel setpoints — decision A); `docs/user/manpages/validate.md` (scope docs); `data/behave_coverage_waivers.json` (REQ-04/05 OBPI-level waiver).
- Tests added: `TestSetpointCoherence` (REQ-01/02/03 + missing-manifest fail-closed) and `TestTemperatureAccessorFailClosed` (REQ-04) in tests/governance/test_setpoint_coherence.py; 4 BDD scenarios in features/setpoint_coherence.feature.
- Decision A ratified by operator: `heavy` (fullest-retention / no-compression) sentinel setpoint for the 7 non-AgentContract routed surfaces (Bullet, Chore, Handoff, Persona, Rule, Scenario, Skill -> claude).
- Date completed: 2026-06-06.
- Attestation status: operator-attested (g0).
- Defects noted: none in OBPI scope; the reconcile-gate net-new-file deadlock surfaced in flight was fixed and committed separately (commit a4519e4f).

## Tracked Defects

- **Coherence-domain orthogonality (flagged, not a defect to suppress):** `content_type_routes` (vendor mirroring) and `content_type_temperatures` (compression setpoints) share a `(content_type, vendor)` key shape but model different axes. The forward-coherence rule couples them. Resolution routed to operator at Gate 5 via § Open Implementation Decision (recommendation A: declare all routed pairs, `heavy` sentinel for non-compressed surfaces). Not silently resolved.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.37-20: fail-closed `gz validate --setpoint-coherence` scope added; every content_type_routes pair must carry a legal declared setpoint (REQ-01/02/03 BEHAVIOR — exit 3 on uncovered pair or illegal token, exit 0 coherent); temperature_for accessor pinned fail-closed on undeclared pairs (REQ-04); manpage documents the scope and cli-alignment resolves it (REQ-05 SUPPORT). Decision A ratified: heavy sentinel setpoints for the 7 non-AgentContract routed surfaces. Evidence: arb-ruff-a672da842df64da1bd821917d9922051, arb-step-typecheck-4704815cca33475a9e0ed5e98089c5f8, arb-step-unittest-87dafd5e7bca4e73b3011300a59fda93, arb-step-behave-8bb6c34e50524d79a0f4029cd56ba2ea, arb-step-mkdocs-d01b2e676bac4b1ca31740caa34f361b; behavior_uncovered_reqs=0; 4/4 BDD scenarios pass.
- Date: 2026-06-06

---

**Date Completed:** 2026-06-06

**Evidence Hash:** -
