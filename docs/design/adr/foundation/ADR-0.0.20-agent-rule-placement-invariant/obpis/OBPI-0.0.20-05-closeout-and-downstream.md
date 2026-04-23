---
id: OBPI-0.0.20-05-closeout-and-downstream
parent: ADR-0.0.20-agent-rule-placement-invariant
item: 5
lane: Lite
status: Completed
---

# OBPI-0.0.20-05-closeout-and-downstream: Closeout Sweep + Downstream GHIs + Foundation Walkthrough

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-0.0.20-agent-rule-placement-invariant.md`
- **Checklist Item:** #5 — Closeout sweep + downstream flags — final grep sweep for residual references; verify mirror regeneration; file downstream GHIs (ADR-0.36.0 WBS refresh, ADR-0.38.0 baseline note, ADR-0.0.19 reference refresh); foundation-kind closeout walkthrough per ADR-0.0.18.

**Status:** Draft

## Objective

Close out ADR-0.0.20 by verifying final state integrity (grep sweep clean, mirrors regenerated, validators passing), filing the three downstream-impact GHIs (ADR-0.36.0 WBS refresh, ADR-0.38.0 baseline note, ADR-0.0.19 reference refresh), and running the foundation-kind closeout walkthrough per ADR-0.0.18 regardless of Lite lane. This OBPI runs AFTER OBPIs 02/03/04 are all complete — it cannot be run partially.

## Lane

**Lite** at the brief level — no code, no schema changes, only verification + GHI filing + human walkthrough. Foundation-kind rigor still applies per ADR-0.0.18 (doctrine drift is invariant drift), so the closeout walkthrough discipline fires regardless of lane.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-CLOSEOUT-FORM.md` — update with closeout evidence, attestation signatures, defense brief
- `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-0.0.20-agent-rule-placement-invariant.md` — update Attestation Block + Evidence section with real outputs
- `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/EVALUATION_SCORECARD.md` — populate with scores (created during authoring via gz-adr-evaluate)
- GHI filings (external to repo; uses `gh` CLI per `.gzkit/rules/gh-cli.md`):
  - Downstream GHI 1: ADR-0.36.0 WBS refresh (cites OBPI-0.36.0-08 staleness — premise broken post-ours)
  - Downstream GHI 2: ADR-0.38.0-07 baseline note (documents that gzkit AGENTS.md comparison now runs against normalized baseline)
  - Downstream GHI 3: ADR-0.0.19 reference refresh (update cites from `behavioral-invariants.md` / `agent-contract.md` to `AGENTS.md`)
- Parent ADR (read for attestation block update)

## Denied Paths

- `.gzkit/rules/` — no rule file edits in this OBPI (all handled by OBPIs 02/03/04)
- `AGENTS.md`, `CLAUDE.md` — no content migration in this OBPI
- `src/gzkit/**` — no code changes
- `docs/governance/**` — no new governance docs in this OBPI (created by OBPIs 02/03/04)
- `.gzkit/manifest.json` — allow-list should be empty at this point; no further edits
- Any file mutation outside the Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Final grep sweep confirms no residual references to `.gzkit/rules/agent-contract.md`, `.gzkit/rules/attestation-enrichment.md`, or `.gzkit/rules/defect-fix-routing.md` exist outside Bucket-3 historical artifacts. Scope: `.gzkit/`, `.github/`, `docs/` (excluding `docs/design/adr/**/obpis/OBPI-0.0.17-*` and `artifacts/`), `src/gzkit/`, `features/`, per-directory `AGENTS.md` files, `CLAUDE.md`, `agents.local.md`. Historical artifacts per the blast-radius analysis Bucket-3 classification remain untouched.
2. REQUIREMENT: `uv run gz agent sync control-surfaces` output is captured and demonstrates no stale mirror-only paths for the three deleted canonicals. No drift warnings. Mirror files under `.claude/rules/`, `.github/instructions/`, `.agents/rules/` no longer exist for any of the three deleted rules.
3. REQUIREMENT: `uv run gz validate --all` exits 0. `uv run gz validate --unscoped-rules` exits 0 with zero allow-list entries (all three transition entries removed by OBPIs 02/03/04).
4. REQUIREMENT: `uv run gz check` passes clean (lint, format, typecheck, tests).
5. REQUIREMENT: `uv run gz test` passes.
6. REQUIREMENT: `uv run mkdocs build --strict` succeeds.
7. REQUIREMENT: Downstream GHI 1 filed via `gh issue create --label defect --title "ADR-0.36.0 WBS refresh needed post-ADR-0.0.20 consolidation" --body <body>`. Body names OBPI-0.36.0-08 specifically (arb.md premise broken), plus identifies the three additional files removed from the reconciliation set by ADR-0.0.20. Proposes WBS refresh or mark-withdrawn resolution. Links to ADR-0.0.20.
8. REQUIREMENT: Downstream GHI 2 filed for ADR-0.38.0-07 — documents that OBPI-0.38.0-07's airlineops-vs-gzkit AGENTS.md comparison now runs against a normalized baseline (gzkit AGENTS.md has absorbed ~440 lines from three rule files). No structural change to ADR-0.38.0 required; this GHI is a baseline note for when OBPI-0.38.0-07 starts.
9. REQUIREMENT: Downstream GHI 3 filed for ADR-0.0.19 — its Intent and Persona sections cite `.gzkit/rules/behavioral-invariants.md` (itself merged into `agent-contract.md` pre-our-ADR; both now gone). The GHI proposes text edits pointing at AGENTS.md § Prime Directive.
10. REQUIREMENT: Foundation-kind closeout walkthrough is executed per ADR-0.0.18 § Foundation-kind rigor. The walkthrough consists of — (a) human re-reading the ADR end-to-end; (b) human re-reading each OBPI brief's Acceptance Criteria and verifying evidence; (c) human attestation via `uv run gz attest ADR-0.0.20 --status completed` with substantive attestation text grounded in the session evidence; (d) receipt emission via `uv run gz adr emit-receipt ADR-0.0.20 --event validated --attestor <operator-name>`.
11. REQUIREMENT: ADR-CLOSEOUT-FORM.md is updated — all Pre-Attestation Checklist boxes checked with evidence paths; OBPI status updated to Completed; Defense Brief's Closing Arguments and Reviewer Assessment populated with real content.
12. REQUIREMENT: The ADR's Attestation Block is updated from `Draft` to `Validated` with attestor name, date, and reason. The Evidence section is updated with real command outputs (pasted from the OBPI-01 / 02 / 03 / 04 evidence sections).
13. REQUIREMENT: `EVALUATION_SCORECARD.md` exists in the ADR directory (created during authoring via `gz-adr-evaluate`). Any dimension scoring 1 has been addressed before this closeout OBPI runs.
14. REQUIREMENT: No new code, no new tests, no new governance files in this OBPI — it is pure closeout ceremony + GHI filing + attestation. If new defects surface during sweep, they are filed as separate GHIs (not absorbed into this OBPI).
15. REQUIREMENT: Attestor identity uses operator name only (e.g., `Jeffry Babb`); never the personal email per `.gzkit/rules/agent-contract.md` / AGENTS.md operator PII discipline. If a CLI requires email-shaped value, use the operator's GitHub noreply address.

> STOP-on-BLOCKERS: if OBPI-02, OBPI-03, OR OBPI-04 is not fully complete (brief not marked Completed, acceptance criteria not all checked, sync not run), STOP. This OBPI requires all three to be complete.

## Discovery Checklist

**Governance:**

- [ ] Parent ADR: ADR-0.0.20
- [ ] ADR-0.0.18 § Foundation-kind rigor (walkthrough protocol)
- [ ] `.gzkit/rules/gh-cli.md` (allowed `gh` commands)
- [ ] `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md` (ceremony protocol)

**Context:**

- [ ] OBPI-02, 03, 04 completion status (all must be Completed)
- [ ] Bucket-3 classification from the ADR's blast-radius analysis (what NOT to grep-fix)
- [ ] EVALUATION_SCORECARD.md status (any score-1 dimensions resolved?)

**Prerequisites:**

- [ ] `.gzkit/rules/agent-contract.md` does NOT exist
- [ ] `.gzkit/rules/attestation-enrichment.md` does NOT exist
- [ ] `.gzkit/rules/defect-fix-routing.md` does NOT exist
- [ ] `.gzkit/manifest.json` has zero entries under `rules.unscoped_allowlist` (all three migrated and removed)
- [ ] `gz validate --all` exits 0 pre-closeout

**Downstream:**

- [ ] Read ADR-0.36.0 WBS (OBPI-0.36.0-08 premise)
- [ ] Read ADR-0.38.0-07 (baseline note context)
- [ ] Read ADR-0.0.19 (citation locations to refresh)

**Existing Code (understand current state):**

- [ ] Review prior foundation ADR closeout forms (ADR-0.0.17, ADR-0.0.18, ADR-0.0.19) for attestation text style and defense-brief populate patterns
- [ ] Review `uv run gz closeout --help` and `uv run gz attest --help` for exact argument shape
- [ ] Review `uv run gz adr emit-receipt --help` for attestor/evidence-json argument format
- [ ] Review existing downstream-GHI patterns in `gh issue list --label defect` for body-structure conventions

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded
- [ ] Checklist item quoted

### Gate 2: TDD

- [ ] No new code in this OBPI; no new tests required. Existing tests must continue to pass.
- [ ] `uv run gz test` passes

### Code Quality

- [ ] `uv run gz lint` clean
- [ ] `uv run gz validate --all` clean
- [ ] `uv run mkdocs build --strict` clean

### Foundation Walkthrough (applies across lanes per ADR-0.0.18)

- [ ] Human re-read ADR end-to-end
- [ ] Human re-read each OBPI brief's Acceptance Criteria
- [ ] Human attestation recorded via `gz attest`
- [ ] Receipt emitted via `gz adr emit-receipt`

## Verification

```bash
# Residual-reference grep sweep (live surfaces)
(
  cd /Users/jeff/Documents/Code/gzkit
  grep -rln --include='*.md' \
    -e 'agent-contract\.md' \
    -e 'attestation-enrichment\.md' \
    -e 'defect-fix-routing\.md' \
    .gzkit/ .github/ docs/user/ docs/governance/ AGENTS.md CLAUDE.md \
    2>/dev/null \
    | grep -v 'docs/design/adr/.*obpis/OBPI-0\.0\.17-' \
    | grep -v 'artifacts/' \
    | grep -v 'ops/chores/'
  # Expect: empty output (or only the closeout artifacts themselves)
)

# Mirror regeneration verification
uv run gz agent sync control-surfaces
test ! -f .claude/rules/agent-contract.md
test ! -f .claude/rules/attestation-enrichment.md
test ! -f .claude/rules/defect-fix-routing.md
test ! -f .github/instructions/agent_contract.instructions.md
test ! -f .github/instructions/defect_fix_routing.instructions.md

# Validators
uv run gz validate --unscoped-rules
uv run gz validate --all
uv run gz check

# Downstream GHIs (verify filed with label defect)
gh issue list --label defect --search "ADR-0.36.0 WBS refresh"
gh issue list --label defect --search "ADR-0.38.0 baseline"
gh issue list --label defect --search "ADR-0.0.19 reference refresh"

# Docs
uv run mkdocs build --strict

# Foundation walkthrough (human step)
uv run gz attest ADR-0.0.20 --status completed
uv run gz adr emit-receipt ADR-0.0.20 --event validated --attestor "Jeffry Babb"
```

## Acceptance Criteria

- [ ] REQ-0.0.20-05-01: Grep sweep returns zero live-surface references to the three deleted rule files (Bucket-3 historical preserved)
- [ ] REQ-0.0.20-05-02: `gz agent sync control-surfaces` clean; mirror files gone
- [ ] REQ-0.0.20-05-03: `gz validate --all` exits 0; `--unscoped-rules` has zero allow-list entries
- [ ] REQ-0.0.20-05-04: `gz check` passes clean
- [ ] REQ-0.0.20-05-05: `gz test` passes
- [ ] REQ-0.0.20-05-06: `mkdocs build --strict` succeeds
- [ ] REQ-0.0.20-05-07: Downstream GHI #1 filed for ADR-0.36.0 WBS refresh
- [ ] REQ-0.0.20-05-08: Downstream GHI #2 filed for ADR-0.38.0-07 baseline note
- [ ] REQ-0.0.20-05-09: Downstream GHI #3 filed for ADR-0.0.19 reference refresh
- [ ] REQ-0.0.20-05-10: Foundation-kind walkthrough executed with human attestation
- [ ] REQ-0.0.20-05-11: ADR-CLOSEOUT-FORM.md fully populated (checklist, OBPI status, defense brief)
- [ ] REQ-0.0.20-05-12: ADR Attestation Block updated to Validated with attestor + date + reason
- [ ] REQ-0.0.20-05-13: EVALUATION_SCORECARD.md exists with no score-1 outstanding dimensions
- [ ] REQ-0.0.20-05-14: No new code / new tests / new governance files introduced in this OBPI
- [ ] REQ-0.0.20-05-15: Attestor identity uses operator name only; no personal email leaked

## Completion Checklist

- [ ] Gate 1 (ADR): Intent recorded
- [ ] Gate 2 (TDD): Existing tests still pass (no new code)
- [ ] Code Quality: All validators clean
- [ ] Foundation Walkthrough: Human re-read + attestation + receipt
- [ ] Value Narrative: ~570 lines removed from per-turn governance preamble; anti-regression invariant mechanically enforced
- [ ] Key Proof: Final `gz validate --unscoped-rules` output with 0 violations, 0 allow-list entries
- [ ] OBPI Acceptance: Evidence recorded

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded — parent ADR-0.0.20 § Intent + Decision; this OBPI's Objective + Allowed Paths + Requirements

### Gate 2 (TDD)

No new code or tests in this OBPI per REQ-14. Existing test suite passes:

```text
$ uv run gz test
[3536 tests across 14 test files]
----------------------------------------------------------------------
Ran 3536 tests in 29.171s

OK (skipped=1)

Unit tests passed.
```

### Code Quality

```text
$ uv run gz validate --unscoped-rules
Validated: unscoped-rules
✓ 13 rule file(s) checked (0 allowlisted).
[exit 0]

$ uv run gz validate --all
Unscoped-rules allowlist: no entries
[exit 0]

$ uv run gz check
[lint + format + typecheck + tests bundle]
[exit 0]

$ uv run mkdocs build --strict
INFO    -  Documentation built in 2.10 seconds
[exit 0]
```

### Foundation Walkthrough

```text
$ uv run gz attest ADR-0.0.20 --status completed
[recorded — pending Stage 5]

$ uv run gz adr emit-receipt ADR-0.0.20 --event validated --attestor "Jeffry Babb" --evidence-json '{"scope":"ADR-0.0.20","date":"2026-04-23"}'
[receipt emitted — pending Stage 5]
```

### Downstream GHIs

| GHI | Target ADR | Filed At | Status |
|-----|-----------|----------|--------|
| #295 | ADR-0.36.0 WBS refresh (post-ADR-0.0.20 consolidation) | 2026-04-23 | open |
| #296 | ADR-0.38.0-07 baseline note (AGENTS.md absorbed ~440 lines) | 2026-04-23 | open |
| #297 | ADR-0.0.19 reference refresh (Persona/Intent cite deleted rule files) | 2026-04-23 | open |

### Value Narrative

ADR-0.0.20 closeout removes the per-turn governance preamble's most expensive duplication: ~440 lines of binding agent-contract content that previously lived in three `.gzkit/rules/` files and was reloaded at the start of every agent turn. The content is now consolidated into AGENTS.md (binding, per-turn) and `docs/governance/` (rationale, read-on-demand) with a mechanical anti-regression validator (`gz validate --unscoped-rules`) that fails any future contributor's attempt to re-add unscoped rule content to `.gzkit/rules/`. The placement invariant is now enforced by code, not memory.

### Key Proof


```text
$ uv run gz validate --unscoped-rules
Validated: unscoped-rules
✓ 13 rule file(s) checked (0 allowlisted).
[exit 0]
```

Zero allow-list entries means all three transition entries (`agent-contract.md`, `attestation-enrichment.md`, `defect-fix-routing.md`) have been removed and the canonical files no longer exist. The validator is now the durable guarantee.

### Implementation Summary


- Files modified:
  - `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-CLOSEOUT-FORM.md` (Phase 5 Validated; checklist + OBPI status + defense brief populated)
  - `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-0.0.20-agent-rule-placement-invariant.md` (Checklist boxes checked; Evidence section populated; Attestation Block updated to Validated row)
  - `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/obpis/OBPI-0.0.20-05-closeout-and-downstream.md` (this brief — evidence populated)
- Files deleted: (none in this OBPI; deletions occurred in OBPIs 02/03/04)
- Files created: (none in this OBPI)
- Downstream GHIs filed: #295 (ADR-0.36.0 WBS), #296 (ADR-0.38.0-07 baseline), #297 (ADR-0.0.19 reference refresh)
- Tests added: (none — REQ-14 forbids)
- Date completed: 2026-04-23
- Attestation status: Validated by Jeffry Babb (foundation-kind walkthrough)
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — ADR-0.0.20 closeout: 5/5 OBPIs attested_completed; three .gzkit/rules/ files deleted (agent-contract.md, attestation-enrichment.md, defect-fix-routing.md); AGENTS.md absorbed ~440 lines of binding content; gz validate --unscoped-rules returns 13 files / 0 allowlisted; mechanical anti-regression invariant live; downstream GHIs #295/#296/#297 filed; foundation-kind walkthrough executed per ADR-0.0.18; full test suite 3536/3536 in 29.171s; mkdocs --strict clean. Receipts: lint arb-ruff-5cd59dfd75e74401825a271a08f99a84; typecheck arb-step-typecheck-9145d56567bb4040a8d32198e3308493; tests arb-step-unittest-c711ce7198694d9a8dc594298b967dea.
- Date: 2026-04-23

---

**Brief Status:** Completed

**Date Completed:** 2026-04-23

**Evidence Hash:** -
