---
id: OBPI-0.0.73-08-fidelity-presence-enforcement
parent: ADR-0.0.73-verification-layer-binding-audit
item: 8
lane: heavy
sensitivity: security
status: Completed
req_atomic:
  - REQ-0.0.73-08-01  # one detection behavior (block-less ADR → exit 3 + name) + its tests/behave — single indivisible TDD unit
  - REQ-0.0.73-08-02  # one clean-path behavior + the coupled gz-check wiring (wrapper+step+classification+registry fail-closed on each other) — single indivisible unit
  - REQ-0.0.73-08-03  # one grandfather mechanism (load set, skip grandfathered, fail NEW) + data file — single indivisible unit
  - REQ-0.0.73-08-04  # one SUPPORT bundle (template stub + genuine NC + manpage) delivered with the scope, not separable labor tracked as distinct TASKs
  - REQ-0.0.73-08-05  # one STRUCTURAL-FENCE assertion (parent-ADR BI #7); no labor below the REQ
---

# OBPI-0.0.73-08-fidelity-presence-enforcement: Fidelity-Presence Enforcement

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- **Checklist Item:** #8 — "Fidelity-presence enforcement (mechanizes Boundary Invariant #4) — `gz validate --fidelity-presence` fails closed (exit 3) on any non-pool ADR Decision lacking a parseable `## Fidelity Assertions` block; wired into `gz check`; pre-existing block-less ADRs grandfathered in an explicit data file; ADR template seeds the block stub; the ADR's own `## Fidelity Assertions` gains a row for the new verb; manpage + `gz cli audit` green; unit tests."

**Status:** Completed

## Objective

Boundary Invariant #4 ("every ADR Decision carries a runnable `## Fidelity Assertions`
block") was prose-only — the OBPI-04 adversarial audit proved an ADR with no block
reaches VALIDATED through both closeout and audit on a stderr warning, so
"VALIDATED = thesis exercised" was false for every block-less ADR. This OBPI
mechanizes BI #4: a new `gz validate --fidelity-presence` scope fails closed
(exit 3) on any non-pool ADR Decision lacking a parseable block, wired into
`gz check`. Pre-existing block-less ADRs are enumerated as explicit grandfathered
debt (fail-closed on NEW ADRs only — the `sensitivity_floor_grandfather.json`
cutover precedent), so the check goes green today without silently exempting the
backlog, and a new ADR cannot be authored block-less. The ADR template seeds the
stub so new ADRs carry the block by construction.

"Done" = `gz validate --fidelity-presence` exits 3 on a block-less non-pool ADR
and 0 on the grandfathered/compliant corpus; it runs inside `gz check`; the
grandfather file enumerates today's block-less ADRs; the ADR template carries a
`## Fidelity Assertions` stub; the new gz-check step is classified and carries a
genuine negative control (not parked in debt); manpage + `gz cli audit` green.

## Lane

**Heavy** — adds a new `gz validate --fidelity-presence` CLI/contract surface used
by humans and `gz check`. Gates 1–5 all apply; Gate 3 (manpage + mkdocs) and
Gate 4 (BDD scenario) are in scope.

## Sensitivity

**security** — the allowlist touches `src/gzkit/commands/quality.py` and
`src/gzkit/commands/validate_cmd.py`, registered security surfaces (the auto-detect
floor fail-closes on a new brief overlapping them). The change is additive (a new
scope + a new gz-check step), not a modification of existing security logic; if the
floor flags a false positive at completion, discharge via
`gz obpi complete --accept-security-floor` with the additive-only rationale
(precedent: OBPI-0.0.73-02 insight, 2026-06-17).

## Allowed Paths

- `src/gzkit/governance/trust_audits/fidelity_presence.py` **CREATE** — the validator: walk non-pool ADR Decisions, flag any lacking a parseable `## Fidelity Assertions` block, minus grandfathered ids
- `src/gzkit/cli/parser_maintenance.py` — register the `--fidelity-presence` argparse flag + `validate()` pass-through, mirroring `--qc-binding` (the argparse home; the plan mis-located this in validate_cmd.py)
- `src/gzkit/commands/validate_cmd.py` — `_run_fidelity_presence_scope` handler + dispatch (fail-closed exit 3), mirroring `--qc-binding`
- `src/gzkit/quality.py` — the `run_fidelity_presence_audit` QualityResult wrapper that shells the scope (the wrapper home; coupled to `_build_check_steps()`)
- `src/gzkit/commands/quality.py` — wire the scope into `gz check` via `_build_check_steps()`
- `tests/commands/test_skills.py` — add the new step's runner to the `gz check` mock-list (coupled surface: the aggregate-check test enumerates every step runner; DO IT RIGHT 1a)
- `src/gzkit/qc_binding.py` — classify the new gz-check step in `_STEP_CLASSIFICATION` (coupled: a new check step is unclassified → `build_qc_registry()` KeyError until added)
- `src/gzkit/governance/trust_audits/qc_binding.py` — register a genuine negative control for the new bound step (a block-less fixture ADR it MUST flag); it is NOT parked in `_NEGATIVE_CONTROL_DEBT`
- `data/fidelity_presence_grandfather.json` **CREATE** — enumerates pre-existing block-less non-pool ADR ids (the acknowledged back-fill debt)
- `.gzkit/templates/adr.md` — seed a `## Fidelity Assertions` stub so new ADRs carry the block
- `src/gzkit/templates/adr.md` — generated package mirror of the canonical stub (written by `gz agent sync control-surfaces`, not hand-edited)
- `docs/user/manpages/validate.md` — document the `--fidelity-presence` scope
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md` — add a `## Fidelity Assertions` row for `gz validate --fidelity-presence` (verb + assertion land together so the gate stays green)
- `tests/governance/test_fidelity_presence.py` **CREATE** — unit tests (fails-on-block-less, passes-on-compliant, grandfather honored, new-ADR fails closed, NC genuine)
- `src/gzkit/traceability.py` — shared `@covers` decorator imported read-only by the REQ test (added by brief reconcile, attestor g0; matches sibling OBPI-0.0.73-02/04 convention)
- `features/` **CREATE/EXTEND** — one `@REQ-0.0.73-08-01` behave scenario for the Heavy-lane BDD gate
- `data/behave_coverage_waivers.json` — waiver entry for the non-`@REQ-08-01` REQs (08-02/03 unit-proven BEHAVIOR; 08-04 SUPPORT; 08-05 STRUCTURAL-FENCE), mirroring sibling OBPI-0.0.73-02/03; required by the `behave-req-tags` completion gate
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/obpis/OBPI-0.0.73-08-fidelity-presence-enforcement.md` — this brief (evidence recording)

## Denied Paths

- Paths not listed in Allowed Paths
- The closeout/audit ceremony code (OBPI-04's surface) — this OBPI adds the `gz check` presence gate, it does NOT re-touch the ceremonies
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz validate --fidelity-presence` MUST exit 3 on a non-pool ADR Decision lacking a parseable `## Fidelity Assertions` block (maps to REQ-0.0.73-08-01).
2. REQUIREMENT: `gz validate --fidelity-presence` MUST exit 0 when every non-pool, non-grandfathered ADR carries a parseable block, and MUST be wired into `gz check` (maps to REQ-0.0.73-08-02).
3. REQUIREMENT: pre-existing block-less ADRs in `data/fidelity_presence_grandfather.json` MUST NOT fail; a NEW block-less ADR (not grandfathered) MUST fail closed (maps to REQ-0.0.73-08-03).
4. REQUIREMENT: the ADR template MUST seed a `## Fidelity Assertions` stub, the scope MUST carry a genuine negative control (not `_NEGATIVE_CONTROL_DEBT`), and the manpage MUST document it (maps to REQ-0.0.73-08-04).
5. REQUIREMENT: presence enforcement MUST satisfy parent-ADR Boundary Invariant #7 — no block-less ADR can reach VALIDATED unchecked (maps to REQ-0.0.73-08-05).
6. NEVER: grandfather a NEW block-less ADR to silence a fresh failure (the cutover-escape the precedent forbids).
7. ALWAYS: reconcile the brief with the parent ADR before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary.
- [ ] Parent ADR § Boundary Invariants #4 (the prose invariant this OBPI mechanizes) and #7 (the new fence).
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`

> **STOP:** If you cannot quote the parent ADR § Decision item / BI #4 that this OBPI mechanizes, STOP and re-read.

**Governance (read once, cache):**

- [ ] `data/sensitivity_floor_grandfather.json` — the grandfather-file precedent to mirror
- [ ] `src/gzkit/governance/trust_audits/qc_binding.py` (`--qc-binding`) — the sibling scope pattern (validator → validate_cmd dispatch → quality.py wiring → classification → NC)
- [ ] `src/gzkit/fidelity.py` — `parse_fidelity_assertions` / `_extract_fidelity_block` (reuse the parser; "parseable block" = it returns ≥1 assertion without raising)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/fidelity.py` parser is importable and returns assertions for a block-bearing ADR
- [ ] `.gzkit/templates/adr.md` exists
- [ ] `docs/user/manpages/validate.md` exists

**Existing Code (understand current state):**

- [ ] `_build_check_steps()` in `src/gzkit/commands/quality.py` — how a step is added and classified
- [ ] `_run_qc_binding_scope` / `--qc-binding` registration in `src/gzkit/commands/validate_cmd.py` — the dispatch pattern to mirror

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item #8 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/user/manpages/validate.md` documents `--fidelity-presence`; `gz cli audit` green

### Gate 4: BDD (Heavy)

- [ ] `@REQ-0.0.73-08-01` scenario passes: `uv run -m behave --tags=@REQ-0.0.73-08-01 features/`

### Gate 5: Human

- [ ] Human attestation recorded (universal per ADR-0.0.36; security walkthrough per sensitivity)

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

uv run gz validate --fidelity-presence
uv run gz validate --qc-binding
uv run gz cli audit
test -f data/fidelity_presence_grandfather.json
test -f src/gzkit/governance/trust_audits/fidelity_presence.py
```

## Demo

<!-- gz-validate-skip: command-shape -->
``bash
# A block-less non-pool ADR fails closed; the compliant/grandfathered corpus passes.
uv run gz validate --fidelity-presence
``

## Acceptance Criteria

- [ ] REQ-0.0.73-08-01 [BEHAVIOR]: Given a non-pool ADR Decision with no parseable `## Fidelity Assertions` block, when `gz validate --fidelity-presence` runs, then it exits 3 and names the offending ADR. (@covers test in `tests/governance/test_fidelity_presence.py`)
- [ ] REQ-0.0.73-08-02 [BEHAVIOR]: Given a corpus where every non-pool non-grandfathered ADR has a parseable block, when `gz validate --fidelity-presence` runs (and when `gz check` runs), then it exits 0. (@covers test in `tests/governance/test_fidelity_presence.py`)
- [ ] REQ-0.0.73-08-03 [BEHAVIOR]: Given `data/fidelity_presence_grandfather.json` listing pre-existing block-less ADRs, when the scope runs, then those ADRs pass but a NEW block-less ADR (absent from the file) fails closed. (@covers test in `tests/governance/test_fidelity_presence.py`)
- [ ] REQ-0.0.73-08-04 [SUPPORT]: The ADR template seeds a `## Fidelity Assertions` stub, the new gz-check step carries a genuine negative control, and the manpage documents the scope. Proof: `gz validate --documents` exit 0 + `gz cli audit` exit 0 + `artifact_edited` ledger events for `.gzkit/templates/adr.md` and `docs/user/manpages/validate.md`.
- [ ] REQ-0.0.73-08-05 [STRUCTURAL-FENCE]: No block-less ADR can reach VALIDATED unchecked — `## Fidelity Assertions` presence is mechanically enforced (parent ADR § Boundary Invariants #7).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** manpage + mkdocs --strict green
- [ ] **Gate 4 (BDD):** scenario passes
- [ ] **Value Narrative / Key Proof:** documented
- [ ] **OBPI Acceptance:** Evidence recorded below

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
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


`uv run gz validate --fidelity-presence` exits 0 over the live corpus (101 grandfathered + ADR-0.0.73 compliant). An empty-grandfather run flags all 101 block-less ADRs, proving the gate fails closed; a NEW block-less ADR absent from the grandfather file fails closed (test_new_block_less_adr_not_in_grandfather_fails_closed). `gz adr fidelity ADR-0.0.73-verification-layer-binding-audit` now reports the OBPI-08 row PASS. Receipts: arb-step-unittest-051f37313b744c0ca4d326bba0405deb, arb-ruff-80b0098448304e6e88c698b768a364d5, arb-step-typecheck-91a92b89d83d44de901f845d2a8d71ac, arb-step-mkdocs-441a0d3bd41f47739a97821fbcb84621, arb-step-behave-15f623d63948408fbf0a6f80bffaa57c.

### Implementation Summary


- Mechanism: new `gz validate --fidelity-presence` scope walks non-pool ADR Decisions and fails closed (exit 3) on any lacking a parseable `## Fidelity Assertions` block, minus a grandfathered cutover set; wired into `gz check` via `_build_check_steps()`
- Files created: src/gzkit/governance/trust_audits/fidelity_presence.py (validator); data/fidelity_presence_grandfather.json (101 grandfathered block-less ADRs); tests/governance/test_fidelity_presence.py (13 tests); features/fidelity_presence.feature + features/steps/fidelity_presence_steps.py (3 @REQ-0.0.73-08-01 scenarios)
- Files modified: src/gzkit/cli/parser_maintenance.py (flag); src/gzkit/commands/validate_cmd.py (scope handler); src/gzkit/quality.py (wrapper); src/gzkit/commands/quality.py (gz-check step); src/gzkit/qc_binding.py (classification); src/gzkit/governance/trust_audits/qc_binding.py (genuine NC); .gzkit/templates/adr.md + src/gzkit/templates/adr.md mirror (stub); docs/user/manpages/validate.md; tests/commands/test_skills.py (coupled mock-list, DO IT RIGHT 1a); data/behave_coverage_waivers.json (waiver for non-@REQ-08-01 REQs)
- Tests added: 13 unit + 3 behave; all green; coverage non-regressing
- Date completed: 2026-06-19
- Attestation status: operator-attested
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — operator-attested at Stage 4 after reviewing the evidence packet: gz validate --fidelity-presence mechanizes ADR-0.0.73 Boundary Invariant #4, failing closed (exit 3) on any non-pool ADR Decision lacking a parseable ## Fidelity Assertions block, wired into gz check; 101 pre-existing block-less ADRs grandfathered (sensitivity-floor cutover precedent), ADR-0.0.73 compliant, new block-less ADRs fail closed; 13 unit tests + 3 @REQ-0.0.73-08-01 behave scenarios, 8/8 REQ coverage (behavior_uncovered_reqs=0), genuine negative control (not in _NEGATIVE_CONTROL_DEBT). Security-sensitivity: additive scope only, no existing security logic modified. All quality gates green (arb-ruff-80b0098448304e6e88c698b768a364d5, arb-step-typecheck-91a92b89d83d44de901f845d2a8d71ac, arb-step-unittest-051f37313b744c0ca4d326bba0405deb, arb-step-mkdocs-441a0d3bd41f47739a97821fbcb84621, arb-step-behave-15f623d63948408fbf0a6f80bffaa57c).
- Date: 2026-06-19

---

**Date Completed:** 2026-06-19

**Evidence Hash:** -
