---
id: OBPI-0.0.41-04-lock-handoff-coupling-validator
parent: ADR-0.0.41-token-block-lock-discipline
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.41-04-lock-handoff-coupling-validator: Lock-Handoff Coupling Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/ADR-0.0.41-token-block-lock-discipline.md`
- **Checklist Item:** #4 — OBPI-0.0.41-04: Implement `gz validate --lock-handoff-coupling` validator. Replay `.gzkit/ledger.jsonl`; fail-close on any `obpi_lock_released` event lacking a valid `handoff_path` payload, referencing a path whose frontmatter timestamp predates the matching claim, OR whose register entry violates the OBPI-01 minimum-information rule. **Binding wiring:** the validator MUST be added to the default `gz check` chain (not on-demand-only) — an enforcement floor agents can skip is no enforcement floor.

**Status:** Draft

## Objective

Land the `gz validate --lock-handoff-coupling` validator and wire it into the default `gz check` chain so the post-OBPI-03 ledger invariant ("every `obpi_lock_released` event carries a valid `handoff_path`") is mechanically enforced at every quality-check invocation — the structural floor that makes the token-block discipline durable against silent regression.

## Lane

**Heavy** — New `gz validate` scope, new trust-audit module, addition to the default `gz check` pipeline, new schema-bearing structural fence in the parent ADR. All four are runtime-contract surfaces.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/ADR-0.0.41-token-block-lock-discipline.md` — add `## Boundary Invariants` section naming the cross-OBPI invariant this validator enforces (required for STRUCTURAL-FENCE REQ kind per `.gzkit/rules/req-scope-discipline.md`).
- `src/gzkit/governance/trust_audits/lock_handoff_coupling.py` — NEW scope function `validate_lock_handoff_coupling(project_root) -> list[ValidationError]`; mirrors `advisor_proof_binding.py` and `closeout_proof_binding.py` shapes.
- `src/gzkit/governance/trust_audits/__init__.py` — export the new scope.
- `src/gzkit/quality.py` — NEW helper `run_lock_handoff_coupling_audit(project_root) -> CheckResult` wrapping the trust-audit invocation in the standard step shape.
- `src/gzkit/commands/quality.py` — add `("Lock-handoff coupling", run_lock_handoff_coupling_audit)` to `_build_check_steps()` (around line 314).
- `src/gzkit/cli/parser_maintenance.py` — register `--lock-handoff-coupling` flag + `set_defaults` pass-through (mirror `--advisor-proof-binding` at lines 590-596).
- `src/gzkit/commands/validate_cmd.py` — wire the scope at every `advisor_proof_binding` site (signature line 191, dispatch dict line 267, runner mapping, policy-breach list for exit 3, pass-through, final checks dict).
- `docs/user/manpages/validate.md` — document `--lock-handoff-coupling` so `gz cli audit` stays green.
- `docs/user/manpages/check.md` — note the new default step in the pipeline.
- `tests/governance/test_lock_handoff_coupling_validator.py` — NEW REQ-derived `@covers`-decorated tests covering: (a) clean ledger passes; (b) missing `handoff_path` fails; (c) `handoff_path` references nonexistent file fails; (d) handoff frontmatter timestamp predates claim fails; (e) handoff missing any of 4 minimum-info fields fails; (f) validator is fired by `gz check` default pipeline.
- `tests/governance/test_token_block_discipline.py` — boundary-invariant integration test (validator must surface in `_build_check_steps()` output).

## Denied Paths

- `src/gzkit/lock_manager.py`, `src/gzkit/commands/obpi_lock.py`, `src/gzkit/ledger_events.py` — runtime surfaces are owned by OBPI-02/03; this OBPI is read-side enforcement.
- `scripts/session_orientation.py`, `.gzkit/skills/gz-session-handoff/**`, `docs/user/runbook.md`, `docs/governance/governance_runbook.md` — surface updates belong to OBPI-05.
- `.gzkit/handoffs/**` — existing register entries are inputs to the validator; this OBPI does not modify them.
- `src/gzkit/schemas/**` — no schema changes; the validator reads existing ledger JSON shapes.
- New dependencies, CI files, lockfiles.
- Paths not listed in Allowed Paths.

## Requirements (FAIL-CLOSED)

1. **NEVER** ship `--lock-handoff-coupling` without simultaneously wiring it into `_build_check_steps()` — the parent ADR's checklist line names this binding as the load-bearing requirement: "an enforcement floor agents can skip is no enforcement floor." On-demand-only registration is the failure mode this REQ exists to close.
2. **ALWAYS** preserve forward-compatibility — the validator MUST tolerate `obpi_lock_released` events from pre-OBPI-02 history (no `handoff_path` field) by reading their `timestamp` and applying the validator only to events emitted on or after the OBPI-02 cutover timestamp. The cutover timestamp is the OBPI-02 closeout date and is grounded in `.gzkit/ledger.jsonl` (read once at validator init; do not hardcode).
3. **NEVER** read or modify ledger state outside the ledger-replay API — use `gzkit.ledger.Ledger.replay()` (or equivalent existing surface); no direct JSON parsing of `.gzkit/ledger.jsonl` from the validator.
4. **ALWAYS** report each failing event with all four diagnostic dimensions (event timestamp, OBPI id, agent, missing-field name) so operators can act on the validator output without re-grepping the ledger.
5. **NEVER** ship parent ADR `## Boundary Invariants` section without the REQ-04-08 invariant text exactly as named in the Acceptance Criteria — the section is the mechanical anchor that legitimizes the STRUCTURAL-FENCE REQ kind.

> STOP-on-BLOCKERS: if OBPI-03 has not landed, STOP. The validator's correctness assumes the post-OBPI-03 contract is in effect; running it against a ledger where reaping still silently deletes lock files (pre-OBPI-03 reap behavior) will fail the validator on legitimate-at-the-time events.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision items 1, 2, and 5 — quote into Implementation Summary verbatim.** Item 5 ("A new validator scope `gz validate --lock-handoff-coupling` replays the ledger and fail-closes …") IS this OBPI's contract.

> **STOP:** If you cannot quote parent ADR § Decision item 5 into Implementation Summary, STOP and re-read. The validator's authority comes from the Decision; freeform behavior is not authorized.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/token-block-discipline.md` § Sub-Invariants 2 and 5 — minimum-info rule and release fail-closed precondition; the validator enforces both.
- [ ] `.gzkit/rules/req-scope-discipline.md` (ADR-0.0.59) — STRUCTURAL-FENCE REQ requires the parent ADR to have a `## Boundary Invariants` section naming the invariant.
- [ ] `src/gzkit/governance/trust_audits/advisor_proof_binding.py` — reference implementation for trust-audit shape (validator function signature, error type, runner-wrapping pattern).
- [ ] `src/gzkit/governance/trust_audits/closeout_proof_binding.py` — second reference for the same shape.

**Context:**

- [ ] OBPI-02 and OBPI-03 briefs + landed implementations — the `handoff_path` payload, fail-closed release, and `abandoned_by_reaper` reaping behavior this validator audits.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-03 brief is at `attested_completed` state.
- [ ] `.gzkit/ledger.jsonl` is readable and contains at least one post-OBPI-02 `obpi_lock_released` event.
- [ ] `src/gzkit/governance/trust_audits/__init__.py` exists and exports existing audits.

**Existing Code (understand current state):**

- [ ] Read `src/gzkit/governance/trust_audits/advisor_proof_binding.py` end-to-end — reference shape.
- [ ] Read `src/gzkit/governance/trust_audits/closeout_proof_binding.py` — second reference.
- [ ] Read `src/gzkit/cli/parser_maintenance.py:590-596` — `--advisor-proof-binding` registration pattern.
- [ ] Read `src/gzkit/commands/validate_cmd.py:191, 267, 1160, 1333, 1422` — wiring sites.
- [ ] Read `src/gzkit/commands/quality.py:283-341` — default `gz check` step composition.
- [ ] Read `src/gzkit/ledger.py` for the canonical replay API.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 5 quoted into Implementation Summary
- [ ] Parent ADR `## Boundary Invariants` section authored with the REQ-04-08 invariant text

### Gate 2: TDD (Red-Green-Refactor)

- [ ] All 6 validator behaviors authored RED first (missing `handoff_path`; nonexistent file; predated frontmatter timestamp; missing minimum-info; pre-OBPI-02 grandfather; default-pipeline membership)
- [ ] Tests pass: `uv run gz test`
- [ ] Coverage maintained or improved

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/validate.md` documents `--lock-handoff-coupling`
- [ ] `docs/user/manpages/check.md` notes the new default step
- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `uv run gz cli audit` clean

### Gate 4: BDD (Heavy)

- [ ] `features/` scenario covering `gz validate --lock-handoff-coupling` on a clean ledger (exit 0) and on a seeded broken-event ledger (exit 3)
- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded via `gz obpi complete --attestation-text "…"`

## Verification

```bash
uv run gz validate --documents
uv run gz validate --lock-handoff-coupling
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz cli audit
```

## Demo

```bash
# (a) Clean ledger — validator passes.
uv run gz validate --lock-handoff-coupling

# (b) Default check pipeline now includes the validator.
uv run gz check --json

# (c) State surface reflects the new invariant.
uv run gz adr status ADR-0.0.41-token-block-lock-discipline --json
```

## Acceptance Criteria

- [ ] REQ-0.0.41-04-01 [BEHAVIOR]: `gz validate --lock-handoff-coupling` is registered as a CLI flag on `gz validate`; running it on a clean ledger exits 0. Covering test: `tests/governance/test_lock_handoff_coupling_validator.py::test_clean_ledger_passes`.
- [ ] REQ-0.0.41-04-02 [BEHAVIOR]: An `obpi_lock_released` event (post-OBPI-02 cutover) lacking a `handoff_path` payload causes the validator to exit 3 (policy breach); the failing event's timestamp, OBPI id, and agent are surfaced in the error message. Covering test: `tests/governance/test_lock_handoff_coupling_validator.py::test_missing_handoff_path_fails`.
- [ ] REQ-0.0.41-04-03 [BEHAVIOR]: An `obpi_lock_released` event whose `handoff_path` references a path not on disk causes the validator to exit 3; the error names the missing path. Covering test: `tests/governance/test_lock_handoff_coupling_validator.py::test_nonexistent_handoff_path_fails`.
- [ ] REQ-0.0.41-04-04 [BEHAVIOR]: An `obpi_lock_released` event whose handoff document's frontmatter timestamp predates the matching `obpi_lock_claimed` event for the same `(obpi_id, agent)` pair causes the validator to exit 3. Covering test: `tests/governance/test_lock_handoff_coupling_validator.py::test_predated_handoff_fails`.
- [ ] REQ-0.0.41-04-05 [BEHAVIOR]: A handoff document missing any of the four minimum-information fields per Sub-Invariant 2 (last lock-event timestamp, last commit SHA, named decision context, branch state) causes the validator to exit 3; the error names the missing field. Covering test: `tests/governance/test_lock_handoff_coupling_validator.py::test_missing_minimum_info_field_fails`.
- [ ] REQ-0.0.41-04-06 [BEHAVIOR]: `obpi_lock_released` events emitted BEFORE the OBPI-02 closeout cutover are exempt from `handoff_path` enforcement; the cutover timestamp is derived from `.gzkit/ledger.jsonl` at validator init (not hardcoded). Covering test: `tests/governance/test_lock_handoff_coupling_validator.py::test_pre_cutover_events_grandfathered`.
- [ ] REQ-0.0.41-04-07 [BEHAVIOR]: `_build_check_steps()` in `src/gzkit/commands/quality.py` includes the `("Lock-handoff coupling", run_lock_handoff_coupling_audit)` tuple; `gz check` invokes the validator without requiring `--lock-handoff-coupling` to be passed on the command line. Covering test: `tests/governance/test_token_block_discipline.py::test_lock_handoff_coupling_in_default_check_pipeline`.
- [ ] REQ-0.0.41-04-08 [STRUCTURAL-FENCE]: The parent ADR `## Boundary Invariants` section names the invariant: "Every `obpi_lock_released` event in `.gzkit/ledger.jsonl` emitted on or after the OBPI-02 closeout cutover carries a valid `handoff_path` payload; the referenced handoff exists on disk, postdates its matching `obpi_lock_claimed` event, and satisfies the Sub-Invariant 2 minimum-information rule." This invariant binds OBPI-02 (additive field), OBPI-03 (mandatory at emission), and OBPI-04 (mechanical enforcement) into the single audit-coupling guarantee.
- [ ] REQ-0.0.41-04-09 [SUPPORT]: `docs/user/manpages/validate.md` documents the `--lock-handoff-coupling` flag (description, exit codes, example); `docs/user/manpages/check.md` notes the new default step. `uv run gz cli audit` stays clean. Verified by `gz validate --documents` + `artifact_edited` ledger event.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent and Decision quote recorded; parent ADR § Boundary Invariants section authored
- [ ] **Gate 2 (TDD):** RGR cycle; 6 validator behaviors authored RED before implementation; tests pass
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Manpages updated; mkdocs --strict clean; cli audit clean
- [ ] **Gate 4 (BDD):** behave scenarios cover clean + broken ledger cases
- [ ] **Gate 5 (Human):** Heavy lane — human attestation required before `gz obpi complete`
- [ ] **Value Narrative:** Audit-coupling invariant before vs. after mechanical enforcement
- [ ] **Key Proof:** Validator output transcripts for clean + broken ledger cases
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded; Decision item 5 quoted; parent ADR § Boundary Invariants authored

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint / type-check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build + cli-audit output here
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

<!-- Before OBPI-04: OBPI-02/03 close the runtime contract loops (warning then fail-closed),
     but the audit-coupling invariant ("every released event has handoff_path") relies on
     code-path discipline alone. Future regressions could silently re-open the asymmetry
     GHI #410 surfaced. After OBPI-04: the invariant is mechanically enforced at every
     gz check invocation; no agent can ship a regression that bypasses the audit floor
     without that regression also failing the check pipeline. -->

### Key Proof

<!-- Validator transcripts (clean ledger pass; seeded broken event fail with exit 3 and
     diagnostic message); gz check JSON output showing the new step. -->

### Implementation Summary

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
