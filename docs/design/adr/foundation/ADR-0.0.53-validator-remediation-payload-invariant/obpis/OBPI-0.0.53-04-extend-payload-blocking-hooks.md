---
id: OBPI-0.0.53-04-extend-payload-blocking-hooks
parent: ADR-0.0.53-validator-remediation-payload-invariant
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.53-04-extend-payload-blocking-hooks: Extend the Payload Contract to Blocking Hooks + Finalize the Meta-Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.53-validator-remediation-payload-invariant/ADR-0.0.53-validator-remediation-payload-invariant.md`
- **Checklist Item:** #4 — "OBPI-0.0.53-04: Extend payload contract to blocking hooks + runbook updates + finalize meta-validator scope (allowlist empty)"

**Status:** Draft

## Objective

Extend the `RemediationPayload` contract to the final agent-context-injection surface: every blocking hook (SessionStart, PreToolUse, PreCommit, PostToolUse-if-blocking) under `src/gzkit/hooks/` emits the structured payload on a non-success exit — JSON-line rendering first so the agent's automatic context injection sees the parseable form, human rendering after for the operator terminal. Extend the meta-validator scope to `src/gzkit/hooks/**/*.py`, drain the baseline allowlist to empty, and update both runbooks. This OBPI closes the invariant: every fail-closed exit in the harness now speaks the payload.

## Lane

**Heavy** — Behavior change across every blocking-hook exit, the final extension of the `gz validate --remediation-payload-binding` meta-validator scope, the empty-allowlist finalization, and updates to both runbooks. Per `.claude/rules/cli.md` hook exit semantics are an external contract — hook blocks are the first turn agents see. Foundation-kind parent ADR-0.0.53 triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `src/gzkit/hooks/` — every blocking hook migrates its non-success exit path to emit a `RemediationPayload` (JSON line first)
- `src/gzkit/governance/trust_audits/` — the `remediation-payload-binding` meta-validator's scope is extended to cover `src/gzkit/hooks/**/*.py` (final monotonic scope growth)
- `data/` — the baseline allowlist `data/validator_remediation_baseline.json` (created by OBPI-02) is drained to empty here; this OBPI's attestation requires zero entries
- `tests/hooks/` — OBPI creates `tests/hooks/test_remediation_payload.py`
- `docs/governance/governance_runbook.md` — § Hook outputs names the three-field contract
- `docs/user/runbook.md` — § Recovery flows names the canonical recovery-command pattern
- `docs/design/adr/foundation/ADR-0.0.53-validator-remediation-payload-invariant/**` — parent ADR package scope

## Denied Paths

- `src/gzkit/core/models.py`, `src/gzkit/core/exceptions.py`, `src/gzkit/__main__.py` — the port is OBPI-01 scope
- `.gzkit/rules/validator-remediation.md` — authored in OBPI-01
- `src/gzkit/arb/**` — migrated in OBPI-03
- Validator-scope bodies under `trust_audits/` beyond the meta-validator scope extension — OBPI-02 owns them
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Every blocking hook under `src/gzkit/hooks/` (SessionStart, PreToolUse, PreCommit, and any PostToolUse hook that can block) emits a `RemediationPayload` when it returns a non-success status — via `RemediationFailure`, never an ad-hoc multi-line string, banner, or version dump.
2. REQUIREMENT: The first line of a blocking hook's failure output is the JSON-line rendering (`render_jsonline()`) so the agent's automatic context injection reads the parseable form first; the human-readable rendering (`render_human()`) follows on subsequent lines for the operator terminal.
3. REQUIREMENT: The `gz validate --remediation-payload-binding` meta-validator's scope is extended to import and assert against `src/gzkit/hooks/**/*.py` — every blocking-hook fail path raises `RemediationFailure`; every emitted payload validates the model.
4. REQUIREMENT: `data/validator_remediation_baseline.json` is drained to empty — zero exempt surfaces. This OBPI's Gate 5 attestation requires the empty-allowlist state; a non-empty allowlist at completion is a fail-closed blocker.
5. REQUIREMENT: `docs/governance/governance_runbook.md` § Hook outputs documents the three-field `RemediationPayload` contract; `docs/user/runbook.md` § Recovery flows documents the canonical recovery-command pattern. Both updates land in the same patch set as the code change per `.claude/rules/gate5-runbook-code-covenant.md`.
6. REQUIREMENT: Tests in `tests/hooks/test_remediation_payload.py` assert REQ-derived semantics — every registered blocking hook's failure path emits a valid payload; the JSON-line rendering is the first output line; the meta-validator covers the hook surface; the baseline is empty. Tests assert semantics, not output strings.
7. REQUIREMENT: NEVER edit OBPI-01's port files and NEVER touch `src/gzkit/arb/` — migrated in OBPI-03.
8. REQUIREMENT: NEVER include the operator's personal email in any hook code, the runbooks, the baseline file, or any test.

> STOP-on-BLOCKERS: if OBPI-01's port or OBPI-02's meta-validator is absent, or OBPI-03 left ARB entries in the baseline, print BLOCKERS and halt — this OBPI requires the prior three to have landed.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 4 — quote verbatim** into the brief's Implementation Summary. Decision item 4 is the contract.
- [ ] Parent ADR § Decision — the canonical `RemediationPayload` invariant statement.
- [ ] Parent ADR § Consequences — Positive #7 (hook output becomes agent-prompt-injection-friendly), Negative #5 (baseline-allowlist monotonic drain).
- [ ] Parent ADR § Sequencing — OBPI-04 lands fourth; the meta-validator scope finalizes here.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/validator-remediation.md` — the invariant this OBPI extends to hooks
- [ ] `.claude/rules/gate5-runbook-code-covenant.md` — runbook updates land in the same patch as the code change
- [ ] `docs/governance/governance_runbook.md` § Hook outputs — the section to update

**Context — the hook surface:**

- [ ] `src/gzkit/hooks/` — enumerate `claude.py`, `copilot.py`, `core.py`, `guards.py`, `obpi.py` and the blocking exit paths
- [ ] `src/gzkit/hooks/scripts/` — any hook entry scripts that produce blocking output
- [ ] `src/gzkit/governance/trust_audits/` — the OBPI-02 meta-validator file whose scope this OBPI finalizes

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-01 landed: `RemediationPayload` / `RemediationFailure` importable
- [ ] OBPI-02 landed: `gz validate --remediation-payload-binding` is a registered scope
- [ ] OBPI-03 landed: `data/validator_remediation_baseline.json` carries zero ARB entries

**Existing Code (understand current state):**

- [ ] Existing blocking-hook output format (the ad-hoc multi-line / banner shape this OBPI replaces)
- [ ] SessionStart hook output — the first-turn context surface

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 4 quoted in Implementation Summary

### Gate 2: TDD

- [ ] RED test asserting a blocking hook emits the JSON line first, written before implementation
- [ ] Tests pass: `uv run gz arb step --name unittest -- uv run -m unittest -q` (receipt: `arb-step-unittest-*`)
- [ ] No regression in the existing suite

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] `docs/governance/governance_runbook.md` § Hook outputs and `docs/user/runbook.md` § Recovery flows updated
- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] BDD scenario covers a blocking hook emitting the JSON-line-first structured payload

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion
- [ ] Attestation confirms the baseline allowlist is empty (the invariant is fully landed)

## Verification

```bash
uv run gz validate --remediation-payload-binding
uv run python -c "import json; b = json.load(open('data/validator_remediation_baseline.json')); assert not b or all(not v for v in b.values()) if isinstance(b, dict) else len(b) == 0, 'baseline not empty'; print('baseline empty — invariant fully landed')"
uv run gz arb step --name unittest -- uv run -m unittest -q tests.hooks.test_remediation_payload
grep -q "Hook outputs" docs/governance/governance_runbook.md
uv run gz validate --documents --surfaces
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# A blocking hook now emits the JSON line first, then the human block:
uv run gz validate --remediation-payload-binding
# Every fail-closed surface — validators, ARB, hooks — now speaks the payload;
# the baseline allowlist is empty.
```

## Acceptance Criteria

- [ ] REQ-0.0.53-04-01: Given parent ADR § Decision item 4, when a blocking hook returns a non-success status, then it emits a `RemediationPayload` via `RemediationFailure`, never an ad-hoc banner or multi-line dump.
- [ ] REQ-0.0.53-04-02: Given a blocking hook failure, when the output is read, then the first line is the `render_jsonline()` rendering and the human-readable block follows.
- [ ] REQ-0.0.53-04-03: Given the meta-validator scope extension, when `gz validate --remediation-payload-binding` runs, then it imports and asserts against `src/gzkit/hooks/**/*.py` and passes for every blocking hook.
- [ ] REQ-0.0.53-04-04: Given the baseline allowlist, when this OBPI completes, then `data/validator_remediation_baseline.json` is empty — zero exempt surfaces remain.
- [ ] REQ-0.0.53-04-05: Given `.claude/rules/gate5-runbook-code-covenant.md`, when this OBPI's patch set is reviewed, then `docs/governance/governance_runbook.md` § Hook outputs and `docs/user/runbook.md` § Recovery flows are updated in the same commit window as the code change.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 4 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** RED-GREEN cycle followed; hook payload tests pass; suite regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (hook blocks emit banners/version strings into first-turn context) vs capability-now (every harness refusal — validator, ARB, hook — is a structured prompt; baseline empty)
- [ ] **Key Proof:** Meta-validator green over the full surface; empty baseline allowlist
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
