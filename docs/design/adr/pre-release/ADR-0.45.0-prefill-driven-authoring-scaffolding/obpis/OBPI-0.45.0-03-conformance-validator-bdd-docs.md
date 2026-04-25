---
id: OBPI-0.45.0-03-conformance-validator-bdd-docs
parent: ADR-0.45.0-prefill-driven-authoring-scaffolding
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.45.0-03-conformance-validator-bdd-docs: `--prefill-conformance` validator + BDD + docs

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.45.0-prefill-driven-authoring-scaffolding/ADR-0.45.0-prefill-driven-authoring-scaffolding.md`
- **Checklist Item:** #3 — "Implement `gz validate --prefill-conformance` scope (validate canonical opening lines, fail 3 on drift); BDD scenarios cover brief authoring + attestation authoring + grandfathered-waiver behavior"

**Status:** Draft

## Objective

Author the `gz validate --prefill-conformance` mechanical check that asserts authored briefs and attestation texts include the canonical opening lines exactly; ship BDD coverage and docs.

## Lane

**Heavy** — New validate scope + Gate 3 docs + Gate 4 BDD.

## Allowed Paths

- `src/gzkit/governance/trust_audits.py` — new `validate_prefill_conformance`
- `src/gzkit/cli/parser_artifacts.py` — register `--prefill-conformance` flag
- `tests/governance/test_prefill_conformance.py`
- `features/prefill_conformance.feature`
- `features/steps/prefill_conformance_steps.py`
- `AGENTS.md` — § Behavior Rules — Always (one-line addition referencing prefill conformance)
- `docs/user/manpages/gz-validate.md` — document the new flag
- `docs/user/runbook.md` — brief-authoring flow updated
- `docs/design/adr/pre-release/ADR-0.45.0-prefill-driven-authoring-scaffolding/**`

## Denied Paths

- `src/gzkit/skills/**` — owned by OBPI-01
- `src/gzkit/commands/obpi.py`, `src/gzkit/commands/adr_emit_receipt.py` — owned by OBPI-02
- Any path not listed

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: New function `validate_prefill_conformance(target: Path, kind: Literal["brief", "attestation"]) -> ValidationResult`.
2. REQUIREMENT: For `kind="brief"`: parse the file, assert every canonical section heading is present (`## ADR Item`, `## Objective`, `## Lane`, `## Allowed Paths`, `## Denied Paths`, `## Requirements (FAIL-CLOSED)`, `## Discovery Checklist`, `## Acceptance Criteria`, `## Completion Checklist`, `## Evidence`, `## Tracked Defects`, `## Human Attestation`), and assert the Discovery Checklist's first item is the parent-ADR-Decision-quote pin.
3. REQUIREMENT: For `kind="attestation"`: parse the attestation string, assert it contains the em-dash separator (` — `) and at least one `arb-` receipt citation slot.
4. REQUIREMENT: Briefs catalogued in `data/prefill_conformance_waivers.json` are skipped (corpus-freeze grandfathering).
5. REQUIREMENT: `gz validate --prefill-conformance` exits 3 on drift, 0 on conformance.
6. REQUIREMENT: BDD scenarios cover: brief with canonical openers passes; brief missing parent-ADR pin fails 3; attestation with em-dash + receipt passes; attestation without em-dash fails 3; grandfathered brief in waiver list passes despite drift.
7. REQUIREMENT: AGENTS.md § Behavior Rules — Always gains one item referencing the conformance check.
8. REQUIREMENT: Manpage updated with EXAMPLES showing real CLI output (no placeholders per AGENTS.md item 2).
9. REQUIREMENT: `gz cli audit` exits 0; `mkdocs build --strict` exits 0; `gz validate --behave-req-tags` exits 0.
10. REQUIREMENT: NEVER include the operator's personal email.

> STOP-on-BLOCKERS: if OBPI-01 and OBPI-02 have not landed, STOP.

## Discovery Checklist

- [ ] Parent ADR § Decision item 4 (mechanical check)
- [ ] OBPI-0.45.0-01 evidence — confirm brief skeleton stable
- [ ] OBPI-0.45.0-02 evidence — confirm attestation prefill stable
- [ ] `.claude/rules/tests.md` § Behave scenario tagging
- [ ] `.claude/rules/gate5-runbook-code-covenant.md`

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded
### Gate 2: TDD
- [ ] RGR; tests pass
### Code Quality
- [ ] Lint, type clean
### Gate 3: Docs (Heavy)
- [ ] mkdocs strict + cli audit pass
### Gate 4: BDD (Heavy)
- [ ] All scenarios pass; req-tags clean
### Gate 5: Human (Heavy)
- [ ] Required

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz cli audit
uv run mkdocs build --strict
uv run -m behave features/prefill_conformance.feature
uv run gz validate --behave-req-tags
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_prefill_conformance.py -v
```

## Acceptance Criteria

- [ ] REQ-0.45.0-03-01: Given a brief with all canonical section headings and the parent-ADR pin at Discovery Checklist item #1, when `gz validate --prefill-conformance` runs, then exit 0.
- [ ] REQ-0.45.0-03-02: Given a brief missing the parent-ADR pin, when the validator runs, then exit 3.
- [ ] REQ-0.45.0-03-03: Given an attestation containing em-dash + receipt, when the validator runs, then exit 0.
- [ ] REQ-0.45.0-03-04: Given an attestation without em-dash, when the validator runs, then exit 3.
- [ ] REQ-0.45.0-03-05: Given a brief catalogued in the waiver list, when the validator runs, then exit 0 despite drift.
- [ ] REQ-0.45.0-03-06: Given the post-edit repo state, when `gz cli audit` and `mkdocs build --strict` run, then both exit 0.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** RGR; tests pass
- [ ] **Gate 3:** mkdocs strict + cli audit pass
- [ ] **Gate 4 (BDD):** scenarios pass
- [ ] **Code Quality:** clean
- [ ] **OBPI Acceptance:** Heavy = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD)
```text
# RGR + unittest output
```

### Code Quality
```text
# lint/typecheck output
```

### Gate 3 (Docs)
```text
# mkdocs build --strict, gz cli audit
```

### Gate 4 (BDD)
```text
# behave + req-tags
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
- BDD scenarios added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` (heavy lane requires human)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
