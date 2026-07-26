---
id: OBPI-0.0.53-01-validator-remediation-payload-port
parent: ADR-0.0.53-validator-remediation-payload-invariant
item: 1
lane: Heavy
status: Draft
allowlist:
- src/gzkit/core/models.py
- src/gzkit/core/exceptions.py
- src/gzkit/__main__.py
- .gzkit/rules/
- .gzkit/rules/validator-remediation.md
- docs/governance/advisory-rules-audit.md
- tests/
- tests/core/test_remediation_payload.py
- docs/design/adr/foundation/ADR-0.0.53-validator-remediation-payload-invariant/**
reqs:
- REQ-0.0.53-01-01
- REQ-0.0.53-01-02
- REQ-0.0.53-01-03
- REQ-0.0.53-01-04
- REQ-0.0.53-01-05
- REQ-0.0.53-01-06
verification:
- uv run python -c "from gzkit.core.models import RemediationPayload; p = RemediationPayload(rule_citation='.gzkit/rules/validator-remediation.md:12', diagnosis='example', recovery='/gz-context-diet'); print(p.render_jsonline()); print(p.render_human())"
- uv run python -c "from gzkit.core.exceptions import RemediationFailure; print(RemediationFailure)"
- uv run gz arb step --name unittest -- uv run -m unittest -q tests.core.test_remediation_payload
- uv run gz validate --documents --advisory-scorecard
- uv run gz arb ruff
- uv run gz arb typecheck
- uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
---

# OBPI-0.0.53-01-validator-remediation-payload-port: Author the `RemediationPayload` Port and Helper

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.53-validator-remediation-payload-invariant/ADR-0.0.53-validator-remediation-payload-invariant.md`
- **Checklist Item:** #1 — "OBPI-0.0.53-01: Author `RemediationPayload` port (Pydantic model + helper + exception type + rule file + scorecard entry)"

**Status:** Draft

## Objective

Author the `RemediationPayload` port: a Pydantic model carrying the three canonical fail-closed fields (`rule_citation`, `diagnosis`, `recovery`), the dual-rendering helper methods that emit it as both an agent-parseable JSON line and an operator-readable block, the `RemediationFailure` exception type every fail-closed surface raises, the `__main__.py` top-level handler that catches it, the `.gzkit/rules/validator-remediation.md` rule file declaring the invariant, and the `advisory-rules-audit.md` scorecard entry. This OBPI ships the contract; the migration OBPIs (02/03/04) consume it.

## Lane

**Heavy** — Adds a new `RemediationPayload` Pydantic model to `src/gzkit/core/models.py`, a new `RemediationFailure` exception type to `gzkit.core.exceptions`, new top-level exception-handler behavior in `__main__.py`, and a new canonical rule surface (`.gzkit/rules/validator-remediation.md`). Per `.gzkit/rules/skill-surface-sync.md` a new canonical rule file is a heavy-lane surface change; the new exception semantics alter the fail-closed contract every downstream OBPI builds on. Foundation-kind parent ADR-0.0.53 triggers universal brief-level Gate 5 attestation per ADR-0.0.36 regardless of lane.

## Allowed Paths

- `src/gzkit/core/models.py` — adds the `RemediationPayload` Pydantic model and its `render_jsonline()` / `render_human()` methods
- `src/gzkit/core/exceptions.py` — adds the `RemediationFailure` exception type wrapping a `RemediationPayload`
- `src/gzkit/__main__.py` — top-level exception handler catches `RemediationFailure`, emits the dual rendering to stderr, exits non-zero
- `.gzkit/rules/` — OBPI creates `.gzkit/rules/validator-remediation.md` (new rule file, version `0.1.0`, the invariant + three-field shape) in this existing directory
- `docs/governance/advisory-rules-audit.md` — scorecard entry classifying the new rule
- `tests/` — OBPI creates `tests/core/test_remediation_payload.py` (new `core/` subdirectory) — REQ-derived unit tests for the model, helper methods, exception, and handler
- `docs/design/adr/foundation/ADR-0.0.53-validator-remediation-payload-invariant/**` — parent ADR package scope

## Denied Paths

- `src/gzkit/governance/trust_audits/**` — validator migration is OBPI-02 scope
- `src/gzkit/arb/**` — ARB migration is OBPI-03 scope
- `src/gzkit/hooks/**` — hook migration is OBPI-04 scope
- `src/gzkit/governance/trust_audits/validate_cli_scopes` and the `--remediation-payload-binding` meta-validator — authored in OBPI-02, scope-extended in OBPI-03/04
- `data/validator_remediation_baseline.json` — the baseline allowlist is authored in OBPI-02 alongside the meta-validator
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles (Pydantic is the already-named departure; no new dependency)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `src/gzkit/core/models.py` defines a `RemediationPayload` Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` per `.claude/rules/models.md`, carrying exactly three fields — `rule_citation: str` validated against pattern `^[^:]+:\d+$` (a `path:LINE` reference), `diagnosis: str` with `max_length=240` and a validator rejecting any newline, and `recovery: str` validated to begin with one of the canonical prefixes `uv run gz `, `gh `, `git `, `python -m `, or `/` (slash-skill invocation).
2. REQUIREMENT: `RemediationPayload` exposes `render_jsonline() -> str` returning a single-line JSON object (the agent-context-injection rendering) and `render_human() -> str` returning a three-line human-readable block (`Rule:` / `Diagnosis:` / `Recovery:`). Both renderings derive from the model's own fields — NO caller hand-formats either rendering.
3. REQUIREMENT: `gzkit.core.exceptions` defines `RemediationFailure`, an exception type whose constructor takes a `RemediationPayload` and exposes it as a `.payload` attribute. Raising `RemediationFailure` is the canonical fail-closed signal; bare `sys.exit()` and ad-hoc `print()`-then-exit are NOT the contract for new code.
4. REQUIREMENT: `src/gzkit/__main__.py`'s top-level exception handler catches `RemediationFailure`, writes `payload.render_jsonline()` as the FIRST stderr line followed by `payload.render_human()`, and exits with a non-zero status. Stack traces remain available only under `--debug`.
5. REQUIREMENT: `.gzkit/rules/validator-remediation.md` exists with rule body version `0.1.0`, a `paths:` frontmatter scoping `src/gzkit/governance/trust_audits/**/*.py`, `src/gzkit/validators/**/*.py`, `src/gzkit/arb/**/*.py`, and `src/gzkit/hooks/**/*.py`, and a body declaring the three-field `RemediationPayload` invariant verbatim from the parent ADR § Decision canonical statement.
6. REQUIREMENT: `docs/governance/advisory-rules-audit.md` gains a scorecard entry for `.gzkit/rules/validator-remediation.md` classifying it **Mechanical** for the helper-existence/payload-shape check, with the entry text noting that the *content* of `diagnosis` and `recovery` remains Judgment-class and is out of scope for mechanical validation.
7. REQUIREMENT: Tests in `tests/core/test_remediation_payload.py` assert REQ-derived semantics — a valid payload round-trips through both renderings; an out-of-pattern `rule_citation` is rejected; a `diagnosis` over 240 chars or containing a newline is rejected; a `recovery` outside the prefix enum is rejected; `RemediationFailure` carries its payload; the `__main__.py` handler emits the JSON line first. Tests assert semantics, not output strings, per `.gzkit/rules/tests.md`.
8. REQUIREMENT: NEVER touch `src/gzkit/governance/trust_audits/`, `src/gzkit/arb/`, or `src/gzkit/hooks/` — those migrations are OBPIs 02/03/04. This OBPI ships only the port; it migrates zero existing fail-closed surfaces.
9. REQUIREMENT: NEVER include the operator's personal email in the model, the exception, the rule file, the scorecard entry, or any test.

> STOP-on-BLOCKERS: if `src/gzkit/core/models.py`, `src/gzkit/core/exceptions.py`, or `src/gzkit/__main__.py` is absent, print BLOCKERS and halt — the port has nowhere to land.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 1 — quote verbatim** into the brief's Implementation Summary. Decision item 1 is the contract.
- [ ] Parent ADR § Decision — the canonical statement of the `RemediationPayload` invariant (three-field shape, dual rendering, single-helper rule).
- [ ] Parent ADR § Intent — the "error string is the next prompt the agent reads" framing.
- [ ] Parent ADR § Consequences — Negative #2 (recovery-prefix enum tradeoff), Negative #3 (240-char diagnosis cap) — these shape the field validators.

**Governance (read once, cache):**

- [ ] `.claude/rules/models.md` — Pydantic `ConfigDict(frozen=True, extra="forbid")` contract for the new model
- [ ] `.gzkit/rules/tests.md` § Tests assert semantics, not strings — the REQ-derivation discipline for the test file
- [ ] `docs/governance/advisory-rules-audit.md` — existing scorecard entries for the entry-shape convention

**Context — the two informal anchor sites this OBPI canonizes:**

- [ ] `src/gzkit/governance/trust_audits/vendor_manifest.py:82` — "canonical recovery hint" comment annotation
- [ ] `src/gzkit/governance/trust_audits/instructions_files_budget.py:14` — "remediation pointer to the `gz-context-diet` skill" docstring

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/core/models.py` present
- [ ] `src/gzkit/core/exceptions.py` present
- [ ] `src/gzkit/__main__.py` present with an existing top-level exception handler

**Existing Code (understand current state):**

- [ ] Existing Pydantic models in `src/gzkit/core/models.py` — match field-declaration and validator conventions
- [ ] Existing exception types in `gzkit.core.exceptions` — match the class hierarchy and constructor shape

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 1 quoted in Implementation Summary

### Gate 2: TDD

- [ ] RED tests for each field validator and each rendering written before implementation
- [ ] Tests pass: `uv run gz arb step --name unittest -- uv run -m unittest -q` (receipt: `arb-step-unittest-*`)
- [ ] No regression in the existing suite

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)
- [ ] `.gzkit/rules/validator-remediation.md` and the scorecard entry render cleanly

### Gate 4: BDD (Heavy)

- [ ] No BDD scenario applies — this OBPI ships a model + exception + rule file, not an operator-facing CLI behavior. The behavior-bearing surface (the meta-validator) lands in OBPI-02 and carries the BDD scope. Waiver noted.

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion

## Verification

```bash
uv run python -c "from gzkit.core.models import RemediationPayload; p = RemediationPayload(rule_citation='.gzkit/rules/validator-remediation.md:12', diagnosis='example', recovery='/gz-context-diet'); print(p.render_jsonline()); print(p.render_human())"
uv run python -c "from gzkit.core.exceptions import RemediationFailure; print(RemediationFailure)"
test -f .gzkit/rules/validator-remediation.md
grep -q "0.1.0" .gzkit/rules/validator-remediation.md
grep -q "validator-remediation" docs/governance/advisory-rules-audit.md
uv run gz arb step --name unittest -- uv run -m unittest -q tests.core.test_remediation_payload
uv run gz validate --documents --advisory-scorecard
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# The dual rendering — one source, two consumers:
uv run python -c "from gzkit.core.models import RemediationPayload; \
p = RemediationPayload(rule_citation='docs/governance/state-doctrine.md:14', \
diagnosis='derived view committed without regeneration', \
recovery='uv run gz register-adrs'); \
print('AGENT:', p.render_jsonline()); print('OPERATOR:'); print(p.render_human())"
```

## Acceptance Criteria

- [ ] REQ-0.0.53-01-01: Given parent ADR § Decision item 1, when this OBPI completes, then `src/gzkit/core/models.py` defines `RemediationPayload` as a frozen, `extra="forbid"` Pydantic model with the three fields `rule_citation`, `diagnosis`, `recovery`.
- [ ] REQ-0.0.53-01-02: Given an invalid field value, when `RemediationPayload` is constructed, then a `rule_citation` not matching `^[^:]+:\d+$`, a `diagnosis` over 240 chars or containing a newline, and a `recovery` outside the canonical prefix enum each raise a Pydantic validation error.
- [ ] REQ-0.0.53-01-03: Given a valid `RemediationPayload`, when `render_jsonline()` and `render_human()` are called, then the first returns a single-line JSON object and the second returns a three-line `Rule:`/`Diagnosis:`/`Recovery:` block, both derived from the model fields with no caller-side formatting.
- [ ] REQ-0.0.53-01-04: Given a fail-closed surface raising `RemediationFailure(payload)`, when `__main__.py`'s top-level handler catches it, then the JSON-line rendering is the first stderr line, the human rendering follows, and the process exits non-zero.
- [ ] REQ-0.0.53-01-05: Given the rule-surface requirement, when the repo is inspected, then `.gzkit/rules/validator-remediation.md` exists at body version `0.1.0` with `paths:` scoping the four migration surfaces, and `docs/governance/advisory-rules-audit.md` carries a Mechanical-classified scorecard entry for it.
- [ ] REQ-0.0.53-01-06: Given the scope boundary, when this OBPI's diff is reviewed, then zero files under `src/gzkit/governance/trust_audits/`, `src/gzkit/arb/`, or `src/gzkit/hooks/` are modified — the port ships without migrating any existing surface.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 1 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** RED-GREEN cycle followed; `test_remediation_payload.py` passes; suite regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (informal ~60/40 ad-hoc remediation split) vs capability-now (declared, enforced three-field port)
- [ ] **Key Proof:** The dual-rendering demo — one model, JSON line + human block
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
