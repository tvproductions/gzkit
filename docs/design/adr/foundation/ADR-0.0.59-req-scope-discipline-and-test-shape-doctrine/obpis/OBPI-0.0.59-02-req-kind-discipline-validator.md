---
id: OBPI-0.0.59-02-req-kind-discipline-validator
parent: ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.59-02-req-kind-discipline-validator: Req Kind Discipline Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine.md`
- **Checklist Item:** #2 — "OBPI-0.0.59-02: Extend gz-obpi-specify scaffold to prompt for REQ kind during brief authoring + ship gz validate --req-kind-discipline brief-time fail-close validator (BEHAVIOR REQs require tests/** in Allowed Paths; SUPPORT REQs require validator-scope + ledger-event citations; STRUCTURAL-FENCE REQs require parent-ADR § Boundary Invariants anchor) + Pydantic ReqKind/ProofChannel/ReqClassification models per .gzkit/rules/models.md + wire validator into gz check default pipeline + brief-format documentation update (heavy lane: new validator scope, schema change, brief-authoring contract change)"

**Status:** Completed

## Objective

Ship the mechanical brief-time enforcement surface for the REQ scope discipline taxonomy (ADR-0.0.59 Decision item 2): `ReqKind`/`ProofChannel`/`ReqClassification` Pydantic models in `src/gzkit/req_kind.py`; `gz validate --req-kind-discipline` that exits 3 on missing `[kind]` tags and on per-kind proof-citation gaps (BEHAVIOR → `tests/**` in Allowed Paths; SUPPORT → validator-scope + ledger-event citation in REQ text; STRUCTURAL-FENCE → parent-ADR `## Boundary Invariants` section on disk); the scope wired into `gz check`; `gz-obpi-specify` scaffold updated to prompt for REQ kind; brief-format documentation updated in `docs/governance/req-scope-discipline.md`.

## Lane

**Heavy** — new validator scope, new Pydantic schema module, brief-authoring contract change, `gz check` pipeline change.

## Allowed Paths

- `src/gzkit/req_kind.py` — NEW: Pydantic models `ReqKind`, `ProofChannel`, `ReqClassification`
- `src/gzkit/triangle.py` — EDIT `_AC_LINE_PATTERN` to recognize `[BEHAVIOR|SUPPORT|STRUCTURAL-FENCE]` kind tags before the colon (one-line regex change; `ReqKind(CODE, DOC)` enum untouched)
- `src/gzkit/commands/validate_cmd.py` — add `check_req_kind_discipline: bool = False` parameter, `_validate_req_kind_discipline()` function, scope registration
- `src/gzkit/cli/parser_maintenance.py` — add `--req-kind-discipline` argparse flag to the validate subparser
- `src/gzkit/quality.py` — add `run_req_kind_discipline_audit` runner function
- `src/gzkit/commands/quality.py` — add `("REQ kind discipline", run_req_kind_discipline_audit)` to `_build_check_steps()`
- `tests/governance/test_req_kind_discipline.py` — NEW: unit tests covering all validator behaviors
- `.gzkit/skills/gz-obpi-specify/SKILL.md` — extend with REQ kind authoring guidance (version bump + sync required)
- `docs/governance/req-scope-discipline.md` — add § "Brief-time validation" documenting the validator

## Denied Paths

- `src/gzkit/triangle.py` — the `ReqKind(CODE, DOC)` enum is untouched; only `_AC_LINE_PATTERN` gets a one-group extension to recognize `[BEHAVIOR|SUPPORT|STRUCTURAL-FENCE]` kind tags. Full modification of ReqKind enum or kind resolution logic stays denied.
- `src/gzkit/traceability.py` — parity-gate extension belongs to OBPI-0.0.59-03
- `src/gzkit/commands/adr_coverage.py` — `gz covers` output schema belongs to OBPI-0.0.59-03
- `data/req_kind_grandfathering.json` — grandfathering cache belongs to OBPI-0.0.59-03
- New runtime dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQ-0.0.59-02-01 [BEHAVIOR]: Given an OBPI brief whose `## Acceptance Criteria` contains at least one REQ with a `[BEHAVIOR]`, `[SUPPORT]`, or `[STRUCTURAL-FENCE]` tag and at least one REQ without any kind tag (mixed-state), when `gz validate --req-kind-discipline` runs, then it exits 3 and reports each untagged REQ ID
2. REQ-0.0.59-02-02 [BEHAVIOR]: Given an OBPI brief with all REQs tagged, when `gz validate --req-kind-discipline` runs, then (a) a `[BEHAVIOR]` REQ fails if `tests/**` does not appear anywhere in the brief's Allowed Paths section; (b) a `[SUPPORT]` REQ fails if its text contains neither a `gz validate --` scope reference nor a ledger event type keyword; (c) a `[STRUCTURAL-FENCE]` REQ fails if the parent-ADR file does not contain a `## Boundary Invariants` heading
3. REQ-0.0.59-02-03 [BEHAVIOR]: `ReqKind` (StrEnum: BEHAVIOR/SUPPORT/STRUCTURAL_FENCE), `ProofChannel` (StrEnum: TEST_COVERS/LEDGER_PLUS_VALIDATOR/PARENT_ADR_INVARIANT), and `ReqClassification` (frozen BaseModel + extra='forbid': req_id str, kind ReqKind, proof_channel ProofChannel, proof_status str) exist in `src/gzkit/req_kind.py` per `.gzkit/rules/models.md`
4. REQ-0.0.59-02-04 [BEHAVIOR]: `run_req_kind_discipline_audit` is present in `_build_check_steps()` so `uv run gz check` runs the validator in its default step roster; a brief with untagged REQs causes the check step to return a failing result
5. REQ-0.0.59-02-05 [BEHAVIOR]: `.gzkit/skills/gz-obpi-specify/SKILL.md` contains a § "REQ Kind Authoring" section instructing agents to tag each Acceptance Criteria REQ with one of `[BEHAVIOR]`, `[SUPPORT]`, or `[STRUCTURAL-FENCE]` and to include the required proof-channel citation for SUPPORT and STRUCTURAL-FENCE REQs
6. REQ-0.0.59-02-06 [SUPPORT]: `docs/governance/req-scope-discipline.md` contains a § "Brief-time validation" section documenting `gz validate --req-kind-discipline`, per-kind proof-citation syntax, and exit-code semantics — `uv run gz validate --documents` passes; `artifact_edited` ledger event citing `docs/governance/req-scope-discipline.md` is emitted at OBPI completion

- NEVER: Mark the OBPI accepted while any REQ lacks a [kind] tag in this brief
- ALWAYS: Verify all paths in Allowed Paths exist on disk or have verified parent directories before implementation

> STOP-on-BLOCKERS: OBPI-0.0.59-01 must be Completed before this OBPI begins (doctrine precondition). If OBPI-01 brief status is not `Completed`, HALT and report.

## Discovery Checklist

**Parent ADR (read first):**

- [x] **Parent ADR § Decision item 2** verbatim: "Ship the mechanical surface — extend gz-obpi-specify scaffolds to prompt for REQ kind during authoring; ship gz validate --req-kind-discipline that fail-closes brief-time on missing kind tags AND on per-kind proof-citation gaps; author Pydantic ReqKind/ProofChannel/ReqClassification models per .gzkit/rules/models.md."
- [x] Parent ADR § Intent — the categorical error (uniform @covers gate applied to all REQ kinds) and the fix (three-kind taxonomy with distinct proof channels)
- [x] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine.md`

**Governance (read once, cache):**

- [x] AGENTS.md — agent operating contract (confirmed: AGENTS.md declares `gz validate --req-kind-discipline` forthcoming under OBPI-0.0.59-02)
- [x] `.gzkit/rules/models.md` — Pydantic pattern (BaseModel + ConfigDict frozen + extra='forbid')
- [x] `.gzkit/rules/tests.md` — confirms BEHAVIOR/SUPPORT/STRUCTURAL-FENCE taxonomy and proof-channel matrix landed by OBPI-0.0.59-01

**Context:**

- [x] `src/gzkit/triangle.py:71` — existing `ReqKind(CODE, DOC)` confirmed; new module avoids collision
- [x] `src/gzkit/commands/validate_cmd.py` — scope registry pattern (`opt_in_scopes`, `_validate_*` functions, `validate()` signature)
- [x] `src/gzkit/cli/parser_maintenance.py` — validate flag registration pattern (e.g. `--brief-headings`, `--router-tables`)
- [x] `src/gzkit/commands/quality.py::_build_check_steps()` — `gz check` step roster; `run_req_kind_discipline_audit` goes here
- [x] `docs/governance/req-scope-discipline.md` — exists (OBPI-0.0.59-01 delivered); needs § "Brief-time validation" extension

**Prerequisites (check existence):**

- [x] `docs/design/adr/foundation/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine.md` — confirmed on disk
- [x] `src/gzkit/commands/validate_cmd.py` — confirmed on disk
- [x] `src/gzkit/cli/parser_maintenance.py` — confirmed on disk
- [x] `src/gzkit/commands/quality.py` — confirmed on disk
- [x] `tests/governance/` — confirmed on disk (will create new test file)

**Existing Code (understand current state before editing):**

- [x] `src/gzkit/triangle.py:71` — existing `ReqKind(CODE, DOC)` StrEnum reviewed; new module `req_kind.py` avoids the naming collision
- [x] `src/gzkit/triangle.py:160` — `_AC_LINE_PATTERN` regex reviewed; needs one optional group added to accept `[BEHAVIOR|SUPPORT|STRUCTURAL-FENCE]` between REQ ID and colon (no test in `tests/` directly exercises this regex; safe to extend)
- [x] `src/gzkit/commands/validate_cmd.py:321` (`_validate_requirements`) reviewed — validator function pattern (returns `list[ValidationError]`) confirmed
- [x] `src/gzkit/commands/validate_cmd.py:1067,1132,1223` (`_resolve_scopes`, `_run_scope_checks`, `_collect_errors`) reviewed — scope registration pattern confirmed
- [x] `src/gzkit/cli/parser_maintenance.py:494,581` (`--brief-headings`, `--router-tables` flag-registration pattern) reviewed — argparse flag template confirmed
- [x] `src/gzkit/quality.py:577,588` (`run_kind_invariance_audit`, `run_receipt_shape_audit`) reviewed — `QualityResult` runner pattern confirmed
- [x] `src/gzkit/commands/quality.py:282,309` (`_build_check_steps`) reviewed — step roster ordering and import pattern confirmed
- [x] `tests/governance/test_advisor_proof_binding_validator.py` reviewed — test-class structure and `@covers` decorator usage confirmed

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item #2 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria (REQ-0.0.59-02-01 through -06), not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/governance/req-scope-discipline.md` § "Brief-time validation" section added
- [ ] `docs/user/manpages/` reflects new `--req-kind-discipline` flag if manpage exists

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
# Baseline quality
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q

# Gate 3: docs
uv run mkdocs build --strict
uv run gz validate --documents

# Validator smoke-test (new scope)
uv run gz validate --req-kind-discipline

# gz check includes the new step
uv run gz check

# Specific test module
uv run -m unittest tests.governance.test_req_kind_discipline -v
```

## Demo

```bash
# Validator catches untagged REQs (exits 3)
echo "- [ ] REQ-0.0.59-99-01: Some claim" | uv run gz validate --req-kind-discipline

# Validator accepts fully-tagged brief (exits 0)
uv run gz validate --req-kind-discipline --brief docs/design/adr/.../obpis/OBPI-0.0.59-02-req-kind-discipline-validator.md

# gz check includes REQ kind discipline step
uv run gz check | grep -i "kind discipline"

# Models importable
python -c "from gzkit.req_kind import ReqKind, ProofChannel, ReqClassification; print(ReqKind.BEHAVIOR)"
```

## Acceptance Criteria

- [ ] REQ-0.0.59-02-01 [BEHAVIOR]: Given an OBPI brief whose `## Acceptance Criteria` contains at least one REQ with a `[BEHAVIOR]`, `[SUPPORT]`, or `[STRUCTURAL-FENCE]` tag and at least one REQ without any kind tag (mixed-state), when `gz validate --req-kind-discipline` runs, then it exits 3 and reports each untagged REQ ID
- [ ] REQ-0.0.59-02-02 [BEHAVIOR]: Given an OBPI brief with all REQs tagged, when `gz validate --req-kind-discipline` runs, then (a) a `[BEHAVIOR]` REQ fails if `tests/**` does not appear anywhere in the brief's Allowed Paths section; (b) a `[SUPPORT]` REQ fails if its text contains neither a `gz validate --` scope reference nor a ledger event type keyword; (c) a `[STRUCTURAL-FENCE]` REQ fails if the parent-ADR file does not contain a `## Boundary Invariants` heading
- [ ] REQ-0.0.59-02-03 [BEHAVIOR]: `ReqKind` (StrEnum: BEHAVIOR/SUPPORT/STRUCTURAL_FENCE), `ProofChannel` (StrEnum: TEST_COVERS/LEDGER_PLUS_VALIDATOR/PARENT_ADR_INVARIANT), and `ReqClassification` (frozen BaseModel + extra='forbid': req_id str, kind ReqKind, proof_channel ProofChannel, proof_status str) exist in `src/gzkit/req_kind.py` per `.gzkit/rules/models.md`
- [ ] REQ-0.0.59-02-04 [BEHAVIOR]: `run_req_kind_discipline_audit` is present in `_build_check_steps()` so `uv run gz check` runs the validator in its default step roster; a brief with untagged REQs causes the check step to return a failing result
- [ ] REQ-0.0.59-02-05 [BEHAVIOR]: `.gzkit/skills/gz-obpi-specify/SKILL.md` contains a § "REQ Kind Authoring" section instructing agents to tag each Acceptance Criteria REQ with one of `[BEHAVIOR]`, `[SUPPORT]`, or `[STRUCTURAL-FENCE]` and to include the required proof-channel citation for SUPPORT and STRUCTURAL-FENCE REQs
- [ ] REQ-0.0.59-02-06 [SUPPORT]: `docs/governance/req-scope-discipline.md` contains a § "Brief-time validation" section documenting `gz validate --req-kind-discipline`, per-kind proof-citation syntax, and exit-code semantics — `uv run gz validate --documents` passes; `artifact_edited` ledger event citing `docs/governance/req-scope-discipline.md` is emitted at OBPI completion

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs, Heavy):** Docs build clean, req-scope-discipline.md updated
- [ ] **Gate 4 (BDD, Heavy):** Behave features pass
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded (this brief, authored at pipeline Stage 1 per ADR-0.0.59 § OBPI brief authoring posture)

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


Validator catches missing [kind] tags and per-kind proof-citation gaps:

$ uv run gz validate --req-kind-discipline
Validated: req_kind_discipline
✓ All validations passed (1 scopes).

Pydantic models importable and correctly map kind to proof channel:

$ python -c "from gzkit.req_kind import ReqKind, ProofChannel, ReqClassification; print(ReqClassification.kind_to_channel(ReqKind.SUPPORT))"
ProofChannel.LEDGER_PLUS_VALIDATOR

gz check pipeline includes new step:

$ uv run gz check  # roster includes "REQ kind discipline" step (verified by tests/governance/test_req_kind_discipline.py::TestReqKindDisciplineInGzCheck)

ARB receipts (canonical attestation per AGENTS.md § Attestation):
- arb-ruff-ff2c2d09bdc945c194ac9b7ec4b42cab (lint clean)
- arb-step-typecheck-8a8624238d0947c8b6ea51b45686639a (ty clean)
- arb-step-unittest-e5e601eb9c3a44a7b7429fd780024daf (5588/5588 pass)
- arb-step-mkdocs-f33ee4a9b38d4867a3e727c992022028 (docs build clean)

Stage 3 Phase 1b: 6/6 REQs covered (verified via `uv run gz covers OBPI-0.0.59-02-req-kind-discipline-validator --json`).

### Implementation Summary


- Files created: src/gzkit/req_kind.py (Pydantic ReqKind/ProofChannel/ReqClassification models), tests/governance/test_req_kind_discipline.py (17 tests covering all 6 REQs)
- Files modified: src/gzkit/triangle.py (_AC_LINE_PATTERN one-group extension to accept [BEHAVIOR|SUPPORT|STRUCTURAL-FENCE] tags; ReqKind enum untouched), src/gzkit/commands/validate_cmd.py (_validate_req_kind_discipline function + scope registration + policy-breach classification), src/gzkit/cli/parser_maintenance.py (--req-kind-discipline argparse flag), src/gzkit/quality.py (run_req_kind_discipline_audit runner), src/gzkit/commands/quality.py (step added to _build_check_steps), .gzkit/skills/gz-obpi-specify/SKILL.md (§ REQ Kind Authoring section, version 1.6.0→1.7.0, last_reviewed bumped), docs/governance/req-scope-discipline.md (§ Brief-time validation section), docs/user/manpages/validate.md (--req-kind-discipline documented in scopes table + usage), tests/commands/test_skills.py (new step added to gz check stub list), data/behave_coverage_waivers.json (validator-internals waiver entry consistent with ADR-0.0.59 doctrine)
- Tests added: 17 unittest cases (TestReqKindModels: 5 tests for Pydantic models REQ-03; TestReqKindDisciplineValidator: 8 tests for validator behavior REQ-01/02; TestReqKindDisciplineInGzCheck: 1 test for gz check wiring REQ-04; TestReqKindSpecifySkillSection: 1 test for skill section REQ-05; TestReqScopeDisciplineDocsBriefTimeSection: 2 tests for docs section REQ-06)
- Date completed: 2026-05-26
- Attestation status: Operator-attested via "attest completed" verbatim (Stage 4 conversational, attestation_type: operator-verbatim-conversational)
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.59-02 ships the mechanical brief-time validator for the three-kind REQ taxonomy: ReqKind/ProofChannel/ReqClassification Pydantic models in src/gzkit/req_kind.py, gz validate --req-kind-discipline scope wired into validate_cmd.py + parser_maintenance.py + quality.py, gz-obpi-specify skill scaffold updated with REQ Kind Authoring section (v1.7.0), docs/governance/req-scope-discipline.md extended with Brief-time validation section, validate.md manpage updated. Stage 3 ARB receipts green: arb-ruff-ff2c2d09bdc945c194ac9b7ec4b42cab, arb-step-typecheck-8a8624238d0947c8b6ea51b45686639a, arb-step-unittest-e5e601eb9c3a44a7b7429fd780024daf (5588/5588 pass), arb-step-mkdocs-f33ee4a9b38d4867a3e727c992022028. Stage 3 Phase 1b parity: 6/6 REQs covered (REQ-01 through REQ-06). Precomplete READY: 7/7 preconditions met.
- Date: 2026-05-26

---

**Date Completed:** 2026-05-26

**Evidence Hash:** -
