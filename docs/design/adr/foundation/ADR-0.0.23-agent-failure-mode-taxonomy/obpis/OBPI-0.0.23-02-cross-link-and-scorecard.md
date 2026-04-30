---
id: OBPI-0.0.23-02-cross-link-and-scorecard
parent: ADR-0.0.23-agent-failure-mode-taxonomy
item: 2
lane: Lite
status: Completed
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

**Governance (read once, cache):**

- [x] `AGENTS.md` § DO IT RIGHT — canonical home for the cross-link pointer; read structure before insertion
- [x] `AGENTS.md` § Lane & Kind & Sensitivity Attestation Matrix — confirms foundation-kind brief-level Gate 5

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/ADR-0.0.23-agent-failure-mode-taxonomy.md`
- [x] Sibling OBPIs (01 rule authorship, 03 mirror sync, 04 cross-repo filing wrapper, 05 covers heuristic)

**Prerequisites (check existence, STOP if missing):**

- [x] OBPI-0.0.23-01 deliverable `.gzkit/rules/agent-failure-modes.md` exists (229 lines, version 0.1.0)
- [x] AGENTS.md § DO IT RIGHT section present at line 60
- [x] `docs/governance/advisory-rules-audit.md` Summary table present at lines 200–205 with a recognized count shape
- [x] Plan-audit receipt for this OBPI at `.claude/plans/.plan-audit-receipt-OBPI-0.0.23-02-cross-link-and-scorecard.json` (verdict PASS)

**Existing Code (understand current state):**

- [x] `docs/governance/advisory-rules-audit.md` § Security Sensitivity row #48 — most recent foundation-rule scorecard precedent for shape consistency
- [x] `.gzkit/rules/cross-platform.md` scorecard row precedent classified Mechanical — contrast pattern for the new Judgment row
- [x] AGENTS.md line 76 `agent-contract-rationale.md` cross-reference — parallel-shape precedent for the new pointer line

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


```
$ grep -n "agent-failure-modes" AGENTS.md docs/governance/advisory-rules-audit.md
AGENTS.md:78:See [`.gzkit/rules/agent-failure-modes.md`](.gzkit/rules/agent-failure-modes.md) for the canonical six-pattern failure-mode taxonomy these invariants backstop ([ADR-0.0.23](docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/ADR-0.0.23-agent-failure-mode-taxonomy.md)).
docs/governance/advisory-rules-audit.md:194:### Agent Failure-Mode Taxonomy (`.gzkit/rules/agent-failure-modes.md`)

$ uv run gz validate --advisory-scorecard
Validated: advisory_scorecard
✓ All validations passed (1 scopes).
```

Receipts: lint `arb-ruff-884764388c404a4b9e3ca12c7338ab6b`; documents validate `arb-step-validate-documents-328bd3667c5743639c91578d3d108c34`; advisory-scorecard validate `arb-step-validate-advisory-scorecard-f42880182c214204a807fdcf485383dd`.

### Implementation Summary


- AGENTS.md: one-line pointer added at line 78 in § DO IT RIGHT, parallel-shape with existing `agent-contract-rationale.md` cross-reference. Pointer cites `.gzkit/rules/agent-failure-modes.md` (relative path) and `ADR-0.0.23` (parent ADR). Satisfies REQ-01 + REQ-02.
- docs/governance/advisory-rules-audit.md: new `### Agent Failure-Mode Taxonomy` section + row #49 classified Judgment; promotion candidate `gz validate --failure-mode-coverage` cited under follow-up GHIs #308–#312 per ADR-0.0.23 § Decision. Summary counts 18→19 Judgment, total 58→59. Satisfies REQ-03 + REQ-04.
- Brief Discovery Checklist extended with Prerequisites and Existing Code subsections to satisfy `gz obpi precomplete brief_readiness` gate.
- Tests added: n/a (REQ→@covers parity gate skipped per operator-decided route B, consolidating into follow-up doctrine-mechanization GHI).
- Date completed: 2026-04-30
- Attestation status: foundation-kind brief, agent-relayed-operator-attestation via `--attestor-present`. Stage-4 phrase: "attest completed".
- Defects: one consolidated GHI to follow naming three gaps — parity gate not CLI-enforced; brief-template Allowed-Paths drift between siblings; `gz covers OBPI-X --json` short-form returns empty entries while parent-ADR view enumerates same OBPI.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Confirm OBPI-0.0.23-02-cross-link-and-scorecard: AGENTS.md § DO IT RIGHT carries one new pointer line (line 78) citing `.gzkit/rules/agent-failure-modes.md` and ADR-0.0.23 (REQ-01, REQ-02); `docs/governance/advisory-rules-audit.md` carries new `### Agent Failure-Mode Taxonomy` section row #49 classified Judgment with `gz validate --failure-mode-coverage` promotion path noted (REQ-03); Summary counts updated 18→19 Judgment, total 58→59. `uv run gz validate --advisory-scorecard` exits 0 (REQ-04). REQ-05 (no inlining) and REQ-06 (no operator PII) honored. Lite lane × foundation kind ⇒ brief-level Gate 5 attested. Receipts: lint arb-ruff-884764388c404a4b9e3ca12c7338ab6b; documents arb-step-validate-documents-328bd3667c5743639c91578d3d108c34; advisory-scorecard arb-step-validate-advisory-scorecard-f42880182c214204a807fdcf485383dd. Parity-gate skip (3 uncovered REQs) consolidated into follow-up GHI per operator-decided route B; mechanical verification via grep + advisory-scorecard validator.
- Date: 2026-04-30

---

**Brief Status:** Completed

**Date Completed:** 2026-04-30

**Evidence Hash:** -
