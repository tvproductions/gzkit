---
id: OBPI-0.0.53-02-migrate-validators-remediation-meta
parent: ADR-0.0.53-validator-remediation-payload-invariant
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.53-02-migrate-validators-remediation-meta: Migrate `gz validate` Validators + Ship the Meta-Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.53-validator-remediation-payload-invariant/ADR-0.0.53-validator-remediation-payload-invariant.md`
- **Checklist Item:** #2 — "OBPI-0.0.53-02: Migrate `gz validate --<scope>` validators + ship `gz validate --remediation-payload-binding` meta-validator"

**Status:** Draft

## Objective

Migrate every fail-closed path in every `gz validate` scope under `src/gzkit/governance/trust_audits/` to raise `RemediationFailure(RemediationPayload(...))` instead of `sys.exit()` or ad-hoc `print()`, promote the two informal anchor sites (`vendor_manifest.py`, `instructions_files_budget.py`) to canonical reference implementations, and ship the `gz validate --remediation-payload-binding` meta-validator with the `data/validator_remediation_baseline.json` allowlist that exempts not-yet-migrated surfaces. This is the structural witness that future validators inherit the payload shape.

## Lane

**Heavy** — Behavior change across every fail-closed exit in `src/gzkit/governance/trust_audits/`, a new `gz validate --remediation-payload-binding` CLI scope, a new baseline-allowlist data file, and a manpage update. Per `.claude/rules/cli.md` a new validator scope is a heavy-lane CLI-contract change. Foundation-kind parent ADR-0.0.53 triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `src/gzkit/governance/trust_audits/` — every validator scope here migrates its fail-closed paths to `RemediationFailure`; `vendor_manifest.py` and `instructions_files_budget.py` become the canonical reference implementations
- `src/gzkit/commands/validate_cmd.py` — registers the `--remediation-payload-binding` scope and dispatches the meta-validator
- `src/gzkit/cli/` — OBPI adds the `--remediation-payload-binding` flag to the `gz validate` parser surface
- `data/` — OBPI creates `data/validator_remediation_baseline.json` (the baseline allowlist; pre-migration surfaces exempt)
- `docs/user/manpages/validate.md` — documents the new `--remediation-payload-binding` scope
- `tests/governance/` — OBPI creates `tests/governance/test_validator_remediation_meta.py`
- `docs/design/adr/foundation/ADR-0.0.53-validator-remediation-payload-invariant/**` — parent ADR package scope

## Denied Paths

- `src/gzkit/core/models.py`, `src/gzkit/core/exceptions.py`, `src/gzkit/__main__.py` — the port is OBPI-01 scope; this OBPI consumes it, never edits it
- `.gzkit/rules/validator-remediation.md` — authored in OBPI-01
- `src/gzkit/arb/**` — ARB migration is OBPI-03 scope
- `src/gzkit/hooks/**` — hook migration is OBPI-04 scope
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Every fail-closed path in every scope under `src/gzkit/governance/trust_audits/` raises `RemediationFailure(RemediationPayload(...))` carrying `rule_citation`, `diagnosis`, and `recovery` — NEVER `sys.exit()` with a bare message, NEVER an ad-hoc `print()`-then-exit. The audit-named scopes (`vendor_manifest.py`, `instructions_files_budget.py`, `adr_status_index`/`reconcile.py`, `briefs.py`, `frontmatter` validation, `req_coverage`, `status_vocab`) are covered at minimum; the meta-validator enumerates the complete set.
2. REQUIREMENT: `src/gzkit/governance/trust_audits/vendor_manifest.py` and `instructions_files_budget.py` are migrated as the canonical reference implementations — their existing comment annotations ("canonical recovery hint", "remediation pointer to the `gz-context-diet` skill") become active code emitting the structured payload.
3. REQUIREMENT: `gz validate --remediation-payload-binding` exists as a registered scope. The meta-validator imports every validator scope and asserts: every fail-closed path raises `RemediationFailure` (not `SystemExit`, not a bare `Exception`); every emitted payload validates the `RemediationPayload` model. The scope is added to the `validate-cli-scopes` audit's required-scope list so the meta-validator's own existence is enforced.
4. REQUIREMENT: `data/validator_remediation_baseline.json` exists as a baseline allowlist enumerating every pre-existing fail-closed surface NOT yet migrated as exempt. Every entry the meta-validator surfaces must be either migrated in this OBPI or recorded in the baseline; the allowlist shrinks monotonically across OBPIs 03/04 and is empty at OBPI-04 completion.
5. REQUIREMENT: `recovery` fields emitted by migrated validators are real — each is a registered `gz` verb (resolving against the same parser surface `gz validate --cli-alignment` uses), a known skill invocation, or a documented external command. NEVER a fabricated or non-invocable command string.
6. REQUIREMENT: `docs/user/manpages/validate.md` documents the `--remediation-payload-binding` scope with a real EXAMPLES entry showing observed CLI output.
7. REQUIREMENT: Tests in `tests/governance/test_validator_remediation_meta.py` assert REQ-derived semantics — every migrated scope's fail-closed path raises `RemediationFailure`; the meta-validator flags a deliberately non-conforming fixture validator; the baseline allowlist suppresses exempt surfaces; a migrated validator's `recovery` resolves. Tests assert semantics, not output strings.
8. REQUIREMENT: NEVER edit OBPI-01's port files (`models.py`, `exceptions.py`, `__main__.py`, `validator-remediation.md`) and NEVER touch `src/gzkit/arb/` or `src/gzkit/hooks/` — those are OBPIs 03/04.
9. REQUIREMENT: NEVER include the operator's personal email in any migrated validator, the meta-validator, the baseline file, the manpage, or any test.

> STOP-on-BLOCKERS: if OBPI-01 has not landed (`RemediationPayload` / `RemediationFailure` not importable from `gzkit.core`), print BLOCKERS and halt — this OBPI consumes the port.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 2 — quote verbatim** into the brief's Implementation Summary. Decision item 2 is the contract.
- [ ] Parent ADR § Decision — the canonical `RemediationPayload` invariant statement.
- [ ] Parent ADR § Consequences — Negative #1 (migration cost), Negative #5 (meta-validator migration-window noise; the baseline-allowlist mitigation).
- [ ] Parent ADR § Sequencing — OBPI-02 lands after OBPI-01; the meta-validator scope grows monotonically across 02/03/04.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/validator-remediation.md` (authored in OBPI-01) — the invariant this OBPI enforces
- [ ] `.gzkit/rules/tests.md` § Tests assert semantics, not strings
- [ ] `docs/governance/trust-doctrine.md` — the promoted-scope catalogue the new scope joins

**Context — the migration surface:**

- [ ] `src/gzkit/governance/trust_audits/` — enumerate every scope file; each carries fail-closed paths to migrate
- [ ] `src/gzkit/governance/trust_audits/vendor_manifest.py` + `instructions_files_budget.py` — the two reference-implementation anchors
- [ ] `src/gzkit/commands/validate_cmd.py` — how existing scopes register and dispatch

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-01 landed: `from gzkit.core.models import RemediationPayload` and `from gzkit.core.exceptions import RemediationFailure` both succeed
- [ ] `src/gzkit/governance/trust_audits/` present with the audited scopes

**Existing Code (understand current state):**

- [ ] Existing `gz validate --<scope>` registration pattern in `validate_cmd.py`
- [ ] Existing `validate-cli-scopes` audit (`cli.py`) — where the required-scope list lives

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 2 quoted in Implementation Summary

### Gate 2: TDD

- [ ] RED test asserting a non-conforming validator fails the meta-validator, written before implementation
- [ ] Tests pass: `uv run gz arb step --name unittest -- uv run -m unittest -q` (receipt: `arb-step-unittest-*`)
- [ ] No regression in the existing suite

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/validate.md` updated with the new scope and a real EXAMPLES entry
- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] BDD scenario covers the `gz validate --remediation-payload-binding` operator-facing behavior — a non-conforming validator triggers a fail-closed exit with a `RemediationPayload`-shaped rejection

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion

## Verification

```bash
uv run gz validate --remediation-payload-binding
test -f data/validator_remediation_baseline.json
grep -q "remediation-payload-binding" docs/user/manpages/validate.md
uv run gz arb step --name unittest -- uv run -m unittest -q tests.governance.test_validator_remediation_meta
uv run gz validate --documents --surfaces
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# The meta-validator reports the migration frontier:
uv run gz validate --remediation-payload-binding
# A migrated validator now fails closed with a structured payload —
# trigger any trust_audits scope against a deliberately-broken fixture
# and observe the JSON-line-first stderr rendering.
```

## Acceptance Criteria

- [ ] REQ-0.0.53-02-01: Given parent ADR § Decision item 2, when this OBPI completes, then every fail-closed path under `src/gzkit/governance/trust_audits/` raises `RemediationFailure` carrying a valid `RemediationPayload`, never `sys.exit()` with a bare message.
- [ ] REQ-0.0.53-02-02: Given the two informal anchor sites, when `vendor_manifest.py` and `instructions_files_budget.py` are inspected, then their prior comment annotations are active code emitting the structured payload.
- [ ] REQ-0.0.53-02-03: Given a deliberately non-conforming fixture validator, when `gz validate --remediation-payload-binding` runs, then the meta-validator flags it (raises rather than passes) — and passes for every migrated scope.
- [ ] REQ-0.0.53-02-04: Given `data/validator_remediation_baseline.json`, when the meta-validator runs, then every not-yet-migrated surface is exempt via a baseline entry and no exempt surface produces a failure.
- [ ] REQ-0.0.53-02-05: Given a migrated validator's emitted `recovery` field, when it is resolved, then it is a registered `gz` verb, a known skill invocation, or a documented external command — never a fabricated string.
- [ ] REQ-0.0.53-02-06: Given the `validate-cli-scopes` audit, when it runs, then `--remediation-payload-binding` appears in its required-scope list, so the meta-validator's own existence is mechanically enforced.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 2 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** RED-GREEN cycle followed; meta-validator tests pass; suite regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (ad-hoc `~60/40` validator rejection split) vs capability-now (every validator fail-closed exit speaks the payload; meta-validator binds it)
- [ ] **Key Proof:** `gz validate --remediation-payload-binding` green; a migrated validator's structured fail-closed output
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste unittest output + arb-step-unittest receipt ID here
```

### Code Quality

```text
# Paste lint + typecheck + mkdocs output here with ARB receipt IDs
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

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
