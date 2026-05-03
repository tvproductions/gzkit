---
id: OBPI-0.0.25-03-bdd-and-doc
parent: ADR-0.0.25-obpi-completion-req-coverage-gate
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.25-03-bdd-and-doc: BDD scenarios + AGENTS.md update

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.25-obpi-completion-req-coverage-gate/ADR-0.0.25-obpi-completion-req-coverage-gate.md`
- **Checklist Item:** #3 — "BDD scenarios in `features/` covering the gate firing, the override path, and the interactive-confirmation requirement; update AGENTS.md § OBPI Acceptance Protocol"

**Status:** Draft

## Objective

Author behave scenarios exercising the REQ-coverage gate end-to-end, the override path with TTY + `ACCEPT`, and the headless-refuse semantics; update AGENTS.md § OBPI Acceptance Protocol and the manpage to reflect the new contract.

## Lane

**Heavy** — Heavy-lane OBPIs require Gate 4 BDD coverage and Gate 3 docs.

## Allowed Paths

- `features/obpi_completion_coverage_gate.feature` — new feature file
- `features/steps/obpi_completion_coverage_gate_steps.py` (or extend existing) — step implementations
- `AGENTS.md` — § OBPI Acceptance Protocol updated to name the new gate and the override path
- `docs/user/manpages/gz-obpi.md` (or wherever the manpage lives) — `complete --accept-uncovered` documented
- `docs/user/runbook.md` — completion flow narrative updated
- `docs/governance/governance_runbook.md` — closeout flow updated for `gz adr emit-receipt --event closed` mirror behavior
- `docs/design/adr/foundation/ADR-0.0.25-obpi-completion-req-coverage-gate/**` — parent ADR package scope

## Denied Paths

- `src/**` — no source changes in this OBPI
- `tests/**` (unit tier) — coverage in OBPI-01 and OBPI-02
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `features/obpi_completion_coverage_gate.feature` exists with `@REQ-0.0.25-NN-MM` scenario tags covering REQs from OBPI-01 and OBPI-02.
2. REQUIREMENT: Scenarios run against real `gz obpi complete` and `gz adr emit-receipt --event closed` (no subprocess mocking — end-to-end tier).
3. REQUIREMENT: At least one scenario exercises the TTY + `ACCEPT` confirmation path (use behave's pseudo-TTY support or document a waiver in `data/behave_coverage_waivers.json` if a stable TTY harness does not exist yet).
4. REQUIREMENT: At least one scenario exercises the headless override-refuse path.
5. REQUIREMENT: AGENTS.md § OBPI Acceptance Protocol replaces the existing prose about "completed transition" with explicit gate language naming the REQ-coverage gate and the `--accept-uncovered` override.
6. REQUIREMENT: `gz obpi --help` and the manpage show `--accept-uncovered` and `--accept-uncovered-reason` with a real CLI EXAMPLES block.
7. REQUIREMENT: `uv run gz cli audit` exits 0 — manpage parity preserved.
8. REQUIREMENT: `uv run mkdocs build --strict` exits 0.
9. REQUIREMENT: `uv run gz validate --behave-req-tags` exits 0 — every REQ in OBPI-01/02 covered or waived with rationale in `data/behave_coverage_waivers.json`.
10. REQUIREMENT: NEVER include the operator's personal email in scenarios, manpages, or doc edits.
11. REQUIREMENT: NEVER leave placeholder output examples in the manpage; paste real CLI output.

> STOP-on-BLOCKERS: if OBPI-01 and OBPI-02 have not landed, STOP.

## Discovery Checklist

- [ ] OBPI-0.0.25-01 + -02 evidence
- [ ] AGENTS.md § OBPI Acceptance Protocol — read existing structure
- [ ] `.claude/rules/tests.md` § Behave scenario tagging
- [ ] `.claude/rules/gate5-runbook-code-covenant.md` § Required updates when behavior changes

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] No new code in this OBPI; Gate 2 satisfied via behave run + validate clean
- [ ] `uv run gz test` (full suite) passes

### Code Quality

- [ ] Lint clean

### Gate 3: Docs (Heavy)

- [ ] `uv run mkdocs build --strict` exits 0
- [ ] `uv run gz cli audit` exits 0

### Gate 4: BDD (Heavy)

- [ ] All scenarios pass
- [ ] `gz validate --behave-req-tags` exits 0

### Gate 5: Human (Heavy + Foundation)

- [ ] TTY + `ATTEST` required

## Verification

```bash
uv run gz lint
uv run gz cli audit
uv run mkdocs build --strict
uv run -m behave features/obpi_completion_coverage_gate.feature
uv run gz validate --behave-req-tags
```

## Acceptance Criteria

- [ ] REQ-0.0.25-03-01: Given the gate landed in OBPI-01 and override path landed in OBPI-02, when behave runs the new feature file, then every REQ from OBPI-01/02 has at least one passing tagged scenario (or a registered waiver).
- [ ] REQ-0.0.25-03-02: Given AGENTS.md § OBPI Acceptance Protocol, when this OBPI completes, then prose names the new gate and override path explicitly.
- [ ] REQ-0.0.25-03-03: Given the `gz obpi` manpage, when this OBPI completes, then `--accept-uncovered` and `--accept-uncovered-reason` are documented with real EXAMPLES.
- [ ] REQ-0.0.25-03-04: Given the post-edit repo state, when `gz cli audit` and `mkdocs build --strict` run, then both exit 0.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** behave + test passes
- [ ] **Code Quality:** Lint clean
- [ ] **Gate 3 (Docs):** mkdocs strict + cli audit pass
- [ ] **Gate 4 (BDD):** All scenarios pass; req-tags validate exits 0
- [ ] **Value Narrative:** Documented
- [ ] **Key Proof:** Behave + manpage outputs pasted
- [ ] **OBPI Acceptance:** Heavy + foundation = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Behave run output
```

### Code Quality

```text
# Lint output
```

### Gate 3 (Docs)

```text
# mkdocs build --strict output
# gz cli audit output
```

### Gate 4 (BDD)

```text
# Behave full output
# gz validate --behave-req-tags output
```

### Gate 5 (Human)

```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof


gz covers OBPI-0.0.25-03: 4/4 REQs covered (100.0%); gz adr audit-check ADR-0.0.25: 15/15 REQs covered; behave features/obpi_completion_coverage_gate.feature: 15 passed 0 failed; arb-step-mkdocs-2d2c3a321d6144f095d45bf3f68cf014 exit 0

### Implementation Summary


- features/obpi_completion_coverage_gate.feature: 15 BDD scenarios tagged @REQ-0.0.25-01-NN through @REQ-0.0.25-03-NN covering all gate behaviors
- features/steps/obpi_completion_coverage_gate_steps.py: step definitions with fixture seeding, gz obpi complete dispatch, ledger assertion, ADR receipt emission
- AGENTS.md: REQ-coverage gate paragraph added to OBPI Acceptance Protocol section
- docs/user/commands/obpi-complete.md: exit code 3 added, --accept-uncovered example added
- docs/user/runbook.md: REQ-coverage gate note added to Notes section
- docs/governance/governance_runbook.md: REQ-coverage gate note added to ADR closeout Notes

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed — 15 BDD scenarios pass covering all 15 REQs across ADR-0.0.25 (OBPI-01 6/6, OBPI-02 5/5, OBPI-03 4/4); AGENTS.md OBPI Acceptance Protocol updated naming REQ-coverage gate; obpi-complete.md, runbook.md, governance_runbook.md updated with gate semantics and override path; lint/typecheck/unittest/mkdocs all exit 0 (receipts: arb-ruff-cda7089ae57c4ef1aafc4e4ba851bdf4, arb-step-typecheck-b0f339231ba04aa58362acf0ac733c97, arb-step-unittest-e4aa649c9fd94e18bc0515edec48adff, arb-step-mkdocs-2d2c3a321d6144f095d45bf3f68cf014); pre-existing behave failure tracked at GHI #388
- Date: 2026-05-03

---

**Brief Status:** Completed

**Date Completed:** 2026-05-03

**Evidence Hash:** -
