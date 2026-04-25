---
id: OBPI-0.0.23-02-cross-link-and-scorecard
parent: ADR-0.0.23-agent-failure-mode-taxonomy
item: 2
lane: Lite
status: Draft
---

# OBPI-0.0.23-02-cross-link-and-scorecard: Cross-link from AGENTS.md + scorecard entry

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/ADR-0.0.23-agent-failure-mode-taxonomy.md`
- **Checklist Item:** #2 — "Cross-link from AGENTS.md § DO IT RIGHT and add scorecard entry to `docs/governance/advisory-rules-audit.md`"

**Status:** Draft

## Objective

Wire the new rule into the always-loaded contract surface (AGENTS.md) with a one-line pointer, and register it in the advisory-rules audit scorecard so `gz validate --advisory-scorecard` surfaces it.

## Lane

**Lite** — Documentation cross-linking + scorecard registration. Foundation-kind triggers brief-level Gate 5 attestation.

## Allowed Paths

- `AGENTS.md` — one-line pointer added to § DO IT RIGHT
- `docs/governance/advisory-rules-audit.md` — scorecard entry for the new rule
- `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/**` — parent ADR package scope

## Denied Paths

- `.gzkit/rules/agent-failure-modes.md` — authored in OBPI-01; not edited here
- `.claude/rules/**`, `.github/instructions/**` — vendor mirrors, regenerated in OBPI-03
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `AGENTS.md` § DO IT RIGHT carries one new line referencing `.gzkit/rules/agent-failure-modes.md` as the canonical home for the failure-mode vocabulary.
2. REQUIREMENT: The pointer line cites the rule by relative path AND links to the ADR (`ADR-0.0.23`) so `gz validate --advisory-scorecard` can resolve the cross-reference.
3. REQUIREMENT: `docs/governance/advisory-rules-audit.md` gains a scorecard row for `agent-failure-modes` with classification (Mechanical / Promotable / Judgment / Ambiguous) — start at **Judgment** since the rule is a vocabulary, not a mechanical check.
4. REQUIREMENT: `uv run gz validate --advisory-scorecard` exits 0 after the scorecard entry is added.
5. REQUIREMENT: NEVER inline the failure-mode taxonomy into AGENTS.md — the pointer is one line, not a duplication.
6. REQUIREMENT: NEVER include the operator's personal email in any edit.

> STOP-on-BLOCKERS: if OBPI-01 has not landed (the rule file does not exist), STOP — the cross-link cannot resolve.

## Discovery Checklist

- [ ] OBPI-0.0.23-01 evidence — confirm `.gzkit/rules/agent-failure-modes.md` exists
- [ ] AGENTS.md § DO IT RIGHT — read existing structure to find correct insertion point
- [ ] `docs/governance/advisory-rules-audit.md` — read existing scorecard rows for shape consistency
- [ ] `.gzkit/rules/cross-platform.md` for an example scorecard row classified Mechanical

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] `gz validate --advisory-scorecard` exits 0
- [ ] `gz validate --documents` clean

### Code Quality

- [ ] Lint clean: `uv run gz lint`

### Gate 5: Human

- [ ] Foundation-kind brief: TTY + `ATTEST` required at completion

## Verification

```bash
uv run gz validate --advisory-scorecard
uv run gz validate --documents
uv run gz lint
grep -n "agent-failure-modes" AGENTS.md
grep -n "agent-failure-modes" docs/governance/advisory-rules-audit.md
```

## Acceptance Criteria

- [ ] REQ-0.0.23-02-01: Given AGENTS.md § DO IT RIGHT, when this OBPI completes, then a single new line references `.gzkit/rules/agent-failure-modes.md` and ADR-0.0.23.
- [ ] REQ-0.0.23-02-02: Given `docs/governance/advisory-rules-audit.md`, when this OBPI completes, then a new scorecard row for `agent-failure-modes` exists with a classification.
- [ ] REQ-0.0.23-02-03: Given the new scorecard row, when `gz validate --advisory-scorecard` runs, then it exits 0.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** validate scopes clean
- [ ] **Code Quality:** Lint clean
- [ ] **Value Narrative:** Documented
- [ ] **Key Proof:** Pointer line and scorecard row shown
- [ ] **OBPI Acceptance:** Foundation-kind requires TTY + `ATTEST`

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste validate output here
```

### Code Quality

```text
# Paste lint output here
```

### Gate 5 (Human)

```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added: n/a
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` (foundation-kind requires human)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
