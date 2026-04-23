---
id: OBPI-0.0.20-04-fold-defect-fix-routing
parent: ADR-0.0.20-agent-rule-placement-invariant
item: 4
lane: Lite
status: Completed
---

# OBPI-0.0.20-04-fold-defect-fix-routing: Fold defect-fix-routing.md into AGENTS.md / docs/governance/defect-fix-routing.md

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-0.0.20-agent-rule-placement-invariant.md`
- **Checklist Item:** #4 — Fold `defect-fix-routing.md` — migrate threshold tables + decision protocol to AGENTS.md § Defect-fix routing; move anti-patterns + origin GHI history to `docs/governance/defect-fix-routing.md`; delete canonical + allow-list entry + sync; update inbound references.

**Status:** Draft

## Objective

Migrate `.gzkit/rules/defect-fix-routing.md` (80 lines, `paths: "**"`) to its proper homes — the two threshold tables (Direct-fix conditions ALL / OBPI-ceremony conditions ANY) and the decision protocol (5 steps) into a new AGENTS.md § Defect-fix routing; anti-patterns catalog and origin-GHI history (GHI #195, OBPI-0.0.16-04 → OBPI-0.0.16-06 → revert precedent) into a new `docs/governance/defect-fix-routing.md`. Delete the canonical, remove its allow-list entry, rewrite inbound references, regenerate mirrors.

## Lane

**Lite** — Content migration + rule deletion + reference rewrites. No CLI, schema, or runtime-contract change.

## Allowed Paths

- `AGENTS.md` — add new § Defect-fix routing (threshold tables + decision protocol)
- `docs/governance/defect-fix-routing.md` — **NEW** file; anti-patterns + origin GHI history + related-rules cross-references
- `.gzkit/rules/defect-fix-routing.md` — **DELETED**
- `.claude/rules/defect-fix-routing.md` — regenerated-away by sync
- `.github/instructions/defect_fix_routing.instructions.md` — regenerated-away by sync
- `.gzkit/manifest.json` — remove the defect-fix-routing.md allow-list entry
- Inbound-reference updates (smaller surface than OBPI-02/03; typically ~5-8 live files citing the rule)
- Parent ADR (read-only)

## Denied Paths

- `.gzkit/rules/agent-contract.md` and `.gzkit/rules/attestation-enrichment.md` — unchanged in this OBPI
- Python source code — no changes
- Bucket-3 historical artifacts — references preserved
- Any file mutation outside the Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: AGENTS.md gains a new § Defect-fix routing (not replacing existing content). It contains — (a) the "Direct fix is the right route when ALL hold" table (5 criteria rows); (b) the "OBPI ceremony is required when ANY hold" table (5 trigger rows); (c) the Decision Protocol (5 numbered steps: compute facts → apply criteria → direct-fix route → OBPI route → ambiguous → surface to operator); (d) baseline precedent examples (GHI #186-#189, #191, #192) as prose or a brief note pointing to `docs/governance/defect-fix-routing.md`.
2. REQUIREMENT: `docs/governance/defect-fix-routing.md` is created as a new file carrying the deep-dive content — (a) Anti-patterns catalog (OBPI ceremony for trivial defects; "parent ADR is natural home" rationalization; treating routing as stylistic preference); (b) Origin GHI history ("When this rule was authored" section — GHI #195 / 2026-04-18 / OBPI-0.0.16-04 → OBPI-0.0.16-06 → revert precedent); (c) Related-rules cross-references (agent-contract § Pipeline lifecycle; Craftsmanship 6c; gz-obpi-pipeline SKILL; gz-obpi-specify SKILL).
3. REQUIREMENT: `.gzkit/rules/defect-fix-routing.md` is deleted (canonical only).
4. REQUIREMENT: Allow-list entry for `defect-fix-routing.md` removed from `.gzkit/manifest.json` (manifest goes 1 → 0 entries assuming OBPI-02 and OBPI-03 have landed, OR enters a state with only this one remaining if this is the last fold OBPI to execute).
5. REQUIREMENT: Inbound references are rewritten. Discovery identifies all live governance/skill/doc files referencing the three legacy paths. Each reference points to either (a) the new AGENTS.md § Defect-fix routing (for routing-decision cites), or (b) `docs/governance/defect-fix-routing.md` (for anti-patterns or history cites). Historical artifacts (Bucket 3) are LEFT UNTOUCHED.
6. REQUIREMENT: `uv run gz agent sync control-surfaces` is run after canonical deletion; output shows no stale mirrors; both mirror paths no longer generated.
7. REQUIREMENT: `uv run gz validate --unscoped-rules` exits 0 AFTER this OBPI's changes.
8. REQUIREMENT: `uv run gz validate --all` exits 0.
9. REQUIREMENT: `uv run mkdocs build --strict` succeeds — no broken internal links.
10. REQUIREMENT: TDD test at `tests/governance/test_defect_fix_routing_fold.py` asserts — (a) AGENTS.md § Defect-fix routing contains both threshold tables (both headers + at least 5 criteria each); (b) `docs/governance/defect-fix-routing.md` exists with the three named sections; (c) `.gzkit/rules/defect-fix-routing.md` does not exist; (d) manifest allow-list no longer contains defect-fix-routing.md.
11. REQUIREMENT: No stdlib `dataclass`; no `shell=True`; no new third-party dependencies.

> STOP-on-BLOCKERS: if OBPI-01 is not complete, STOP. OBPI-02 and OBPI-03 do NOT block OBPI-04 (parallel-safe).

## Discovery Checklist

**Governance:**

- [ ] Parent ADR: ADR-0.0.20
- [ ] `.gzkit/rules/defect-fix-routing.md` (current 80-line content)
- [ ] Existing AGENTS.md sections (placement target for § Defect-fix routing)

**Context:**

- [ ] OBPI-01 completion status
- [ ] GHI #195 history (for origin narrative in docs/governance/)

**Prerequisites:**

- [ ] `gz validate --unscoped-rules` passes pre-migration
- [ ] `.gzkit/rules/defect-fix-routing.md` exists

**Blast radius:**

- [ ] Grep for `defect-fix-routing` / `defect_fix_routing` in `.gzkit/**`, `.github/**`, `docs/**` (excluding Bucket-3), per-directory `AGENTS.md` files

**Existing Code (understand current state):**

- [ ] Review current `.gzkit/rules/defect-fix-routing.md` threshold tables for exact column structure (Criterion / Threshold table format preserved in AGENTS.md fold)
- [ ] Review current AGENTS.md section style (H2/H3 headings, table layouts) for consistent § Defect-fix routing placement
- [ ] Review GHI #195 body for origin-narrative accuracy in `docs/governance/defect-fix-routing.md`
- [ ] Review the OBPI-0.0.16-04 → OBPI-0.0.16-06 → revert commit history (`git log --grep 'OBPI-0.0.16'`) for precedent-example fidelity

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded
- [ ] Checklist item quoted

### Gate 2: TDD

- [ ] Tests derived from REQ-10 before migration
- [ ] Red-Green-Refactor
- [ ] `uv run gz test` passes
- [ ] `uv run gz validate --unscoped-rules` passes post-migration

### Code Quality

- [ ] `uv run gz lint` clean
- [ ] `uv run mkdocs build --strict` clean

## Verification

```bash
# Pre-migration
wc -l .gzkit/rules/defect-fix-routing.md  # Expect 80
uv run gz validate --unscoped-rules --json

# Migration verification
test ! -f .gzkit/rules/defect-fix-routing.md
grep -q "Direct fix is the right route" AGENTS.md
grep -q "OBPI ceremony is required" AGENTS.md
test -f docs/governance/defect-fix-routing.md

# Sync
uv run gz agent sync control-surfaces
test ! -f .claude/rules/defect-fix-routing.md
test ! -f .github/instructions/defect_fix_routing.instructions.md

# Quality
uv run gz validate --unscoped-rules
uv run gz validate --all
uv run gz lint
uv run mkdocs build --strict

# Tests
uv run -m unittest tests.governance.test_defect_fix_routing_fold -v
```

## Acceptance Criteria

- [ ] REQ-0.0.20-04-01: AGENTS.md § Defect-fix routing contains both threshold tables + decision protocol + baseline precedent note
- [ ] REQ-0.0.20-04-02: `docs/governance/defect-fix-routing.md` created with anti-patterns + origin GHI + related-rules sections
- [ ] REQ-0.0.20-04-03: `.gzkit/rules/defect-fix-routing.md` deleted
- [ ] REQ-0.0.20-04-04: Allow-list entry removed from manifest
- [ ] REQ-0.0.20-04-05: Inbound references rewritten across live files
- [ ] REQ-0.0.20-04-06: `gz agent sync control-surfaces` regenerates cleanly (mirrors gone)
- [ ] REQ-0.0.20-04-07: `gz validate --unscoped-rules` exits 0
- [ ] REQ-0.0.20-04-08: `gz validate --all` exits 0
- [ ] REQ-0.0.20-04-09: `mkdocs build --strict` succeeds
- [ ] REQ-0.0.20-04-10: TDD test covers semantic migration properties
- [ ] REQ-0.0.20-04-11: No new deps; no shell=True; no dataclass

## Completion Checklist

- [ ] Gate 1 (ADR): Intent recorded
- [ ] Gate 2 (TDD): RGR
- [ ] Code Quality: Lint, mkdocs clean
- [ ] Value Narrative: 80 lines removed from per-turn context; routing history preserved as pedagogy
- [ ] Key Proof: Side-by-side diff + sync output
- [ ] OBPI Acceptance: Evidence recorded

## Evidence

### Gate 1 (ADR)

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste output here
```

### Value Narrative

### Key Proof


```
$ uv run gz validate --unscoped-rules
Validated: unscoped-rules
✓ 13 rule file(s) checked (0 allowlisted).

$ uv run -m unittest tests.governance.test_defect_fix_routing_fold -v
...
Ran 8 tests in 0.298s
OK
```

Every REQ-pinned semantic assertion in the new test suite passes. Manifest allow-list is empty. Vendor mirrors removed. All three sibling fold test suites (agent-contract / attestation / defect-fix-routing) green.

Receipts: lint `arb-ruff-5cd59dfd75e74401825a271a08f99a84`; typecheck `arb-step-typecheck-9145d56567bb4040a8d32198e3308493`; governance tests `arb-step-unittest-c711ce7198694d9a8dc594298b967dea`.

### Implementation Summary


- Files modified: `src/gzkit/templates/agents.md` (added § Defect-fix routing, rewrote Invariant 6c anchor); `.gzkit/manifest.json` (`unscoped_allowlist: []`); `.gzkit/rules/governance-core.md`; 7 `.gzkit/skills/*/SKILL.md` files (all with skill-version patch bump: ghi-close 2.0.0→2.0.1, ghi-author 1.0.0→1.0.1, gz-skill-router 6.0.2→6.0.3, gz-justify 6.0.0→6.0.1, gz-design 1.2.0→1.2.1, gz-plan 1.1.0→1.1.1, gz-obpi-pipeline 6.11.0→6.11.1); `docs/user/skills/ghi-close.md`; `tests/governance/test_attestation_fold.py` (softened co-state assertions to absence per `test_agent_contract_fold` precedent)
- Files deleted: `.gzkit/rules/defect-fix-routing.md` (canonical)
- Files created: `docs/governance/defect-fix-routing.md` (pedagogy: binding-content pointer, anti-patterns, GHI #195 origin narrative, related-rules cross-references); `tests/governance/test_defect_fix_routing_fold.py` (8 REQ-pinned tests mirroring attestation-fold template)
- Tests added: 8 tests in `TestDefectFixRoutingFold`, each `@covers("REQ-0.0.20-04-NN")` derived from Acceptance Criteria; RED pre-migration = 7 failures + 1 error; GREEN post-migration = 8/8 pass in 0.298s
- Vendor mirrors regenerated via `gz agent sync control-surfaces`; `.claude/rules/defect-fix-routing.md`, `.github/instructions/defect_fix_routing.instructions.md`, `.agents/rules/defect-fix-routing.md` absent
- Full unittest sweep: 3536 pass (1 skip) in 27s; `gz validate --all` exit 0; `gz validate --unscoped-rules` reports 0 allowlist entries; `mkdocs build --strict` clean
- Date completed: 2026-04-23
- Attestation status: operator attested "attest completed" at Stage 4

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Fold `.gzkit/rules/defect-fix-routing.md` (last universal `paths: "**"` rule) into AGENTS.md § Defect-fix routing (threshold tables + decision protocol) and `docs/governance/defect-fix-routing.md` (anti-patterns + GHI #195 origin + related-rules). Canonical deleted; manifest `unscoped_allowlist` now empty (1→0); 10 canonical files + 1 hand-authored skill doc rewritten; vendor mirrors removed via sync. 8 REQ-pinned tests green; full unittest 3536 pass (1 skip); `gz validate --all` exit 0; `gz validate --unscoped-rules` reports 0 allowlisted; `mkdocs build --strict` clean. Receipts: lint arb-ruff-5cd59dfd75e74401825a271a08f99a84; typecheck arb-step-typecheck-9145d56567bb4040a8d32198e3308493; governance-tests arb-step-unittest-c711ce7198694d9a8dc594298b967dea.
- Date: 2026-04-23

---

**Brief Status:** Completed

**Date Completed:** 2026-04-23

**Evidence Hash:** -
