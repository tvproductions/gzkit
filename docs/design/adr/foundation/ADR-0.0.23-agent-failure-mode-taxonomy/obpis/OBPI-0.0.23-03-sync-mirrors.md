---
id: OBPI-0.0.23-03-sync-mirrors
parent: ADR-0.0.23-agent-failure-mode-taxonomy
item: 3
lane: Lite
status: Draft
---

# OBPI-0.0.23-03-sync-mirrors: Sync vendor mirrors and verify load

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/ADR-0.0.23-agent-failure-mode-taxonomy.md`
- **Checklist Item:** #3 — "Sync vendor mirrors and verify the rule loads correctly under each agent harness"

**Status:** Draft

## Objective

Run `gz agent sync control-surfaces` to propagate `.gzkit/rules/agent-failure-modes.md` to `.claude/rules/`, `.github/instructions/`, and any other registered mirror; verify the rule loads under each harness's contextual loading rules.

## Lane

**Lite** — Surface-sync work; no contract change. Foundation-kind triggers brief-level Gate 5 attestation.

## Allowed Paths

- `.claude/rules/agent-failure-modes.md` — generated mirror
- `.github/instructions/agent-failure-modes.md` — generated mirror
- `.gzkit/manifest.json` — surface registration may update
- `.gzkit/ledger.jsonl` — receipt event for the sync run
- `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/**` — parent ADR package scope

## Denied Paths

- `.gzkit/rules/agent-failure-modes.md` — canonical source, edited only in OBPI-01
- `AGENTS.md`, `docs/governance/advisory-rules-audit.md` — edited in OBPI-02
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `uv run gz agent sync control-surfaces` runs to completion (exit 0) with the new rule propagated to every registered vendor mirror.
2. REQUIREMENT: After sync, `.claude/rules/agent-failure-modes.md` is byte-equivalent to the canonical (modulo any vendor-specific frontmatter rendering) per the skill-surface-sync § Conflict resolution rules.
3. REQUIREMENT: `gz validate --surfaces` exits 0 — no stale or divergent mirrors.
4. REQUIREMENT: A canonical `agent-sync` ledger event is recorded for this run.
5. REQUIREMENT: NEVER hand-edit a vendor mirror to make sync pass — sync is the contract; if the mirror diverges, fix the canonical and re-sync.
6. REQUIREMENT: NEVER include the operator's personal email in any edited file.
7. REQUIREMENT: STOP if `gz validate --surfaces` reports drift after sync — escalate to operator before declaring completion.

> STOP-on-BLOCKERS: if OBPI-01 and OBPI-02 have not landed, STOP — the canonical rule must exist before mirrors can be generated.

## Discovery Checklist

- [ ] OBPI-0.0.23-01 evidence — confirm canonical rule exists
- [ ] OBPI-0.0.23-02 evidence — confirm AGENTS.md cross-link and scorecard entry exist
- [ ] `.claude/rules/skill-surface-sync.md` § Procedure
- [ ] `.gzkit/manifest.json` — confirm rule registration shape

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] `gz validate --surfaces` exits 0
- [ ] `gz validate --documents` exits 0

### Code Quality

- [ ] Lint clean: `uv run gz lint`

### Gate 5: Human

- [ ] Foundation-kind brief: TTY + `ATTEST` required at completion

## Verification

```bash
uv run gz agent sync control-surfaces
uv run gz validate --surfaces
uv run gz validate --documents
test -f .claude/rules/agent-failure-modes.md
test -f .github/instructions/agent-failure-modes.md
diff .gzkit/rules/agent-failure-modes.md .claude/rules/agent-failure-modes.md  # should match modulo frontmatter
```

## Acceptance Criteria

- [ ] REQ-0.0.23-03-01: Given the canonical rule file from OBPI-01, when `gz agent sync control-surfaces` runs, then mirror files exist under `.claude/rules/` and `.github/instructions/`.
- [ ] REQ-0.0.23-03-02: Given the post-sync repository state, when `gz validate --surfaces` runs, then exit 0 with no stale or divergent mirrors reported.
- [ ] REQ-0.0.23-03-03: Given the sync run, when the ledger is read, then a canonical `agent-sync` event records the propagation.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** validate --surfaces exits 0
- [ ] **Code Quality:** Lint clean
- [ ] **Value Narrative:** Documented
- [ ] **Key Proof:** Mirror diff equivalence shown
- [ ] **OBPI Acceptance:** Foundation-kind requires TTY + `ATTEST`

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste validate --surfaces output here
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
- Tests added: n/a (sync work)
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
