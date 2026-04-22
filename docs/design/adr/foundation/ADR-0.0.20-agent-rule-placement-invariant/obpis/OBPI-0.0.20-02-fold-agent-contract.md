---
id: OBPI-0.0.20-02-fold-agent-contract
parent: ADR-0.0.20-agent-rule-placement-invariant
item: 2
lane: Lite
status: Completed
---

# OBPI-0.0.20-02-fold-agent-contract: Fold agent-contract.md into AGENTS.md / CLAUDE.md / docs/governance/

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-0.0.20-agent-rule-placement-invariant.md`
- **Checklist Item:** #2 — Fold `agent-contract.md` — migrate judgment invariants to AGENTS.md (§ Prime Directive / § DO IT RIGHT / § Behavior Rules); move invariant 10a to CLAUDE.md addendum; extract pedagogy to `docs/governance/agent-contract-rationale.md`; delete canonical + remove allow-list entry + update inbound references + sync.

**Status:** Draft

## Objective

Migrate `.gzkit/rules/agent-contract.md` (213 lines, `paths: "**"`) to its proper homes — judgment invariants into AGENTS.md's existing sections (deduplicated), Claude-specific invariant 10a into CLAUDE.md's "Claude Code addendum" section, pedagogy and Lindsey-2025 rationale into a new `docs/governance/agent-contract-rationale.md`. Delete the canonical file, remove its allow-list entry from `.gzkit/manifest.json`, rewrite inbound references across ~15 Bucket-1 live files, regenerate vendor mirrors via `gz agent sync control-surfaces`. After this OBPI, `gz validate --unscoped-rules` passes with two allow-list entries remaining (OBPIs 03 and 04 pending).

## Lane

**Lite** — Content migration across governance files + rule-file deletion + reference rewrites. No CLI contract, schema, or runtime-contract change. The sync regeneration consumes an existing mechanism (not a modification).

## Allowed Paths

- `AGENTS.md` — fold judgment invariants into existing § Prime Directive / § DO IT RIGHT / § Behavior Rules (dedupe against current text)
- `CLAUDE.md` — add invariant 10a to "Claude Code addendum" section
- `docs/governance/agent-contract-rationale.md` — **NEW** file; pedagogy extract (anti-pattern canon, TASK-driven workflow, Lindsey et al. 2025 rationale for craftsmanship 6g/6h)
- `.gzkit/rules/agent-contract.md` — **DELETED**
- `.claude/rules/agent-contract.md` — regenerated-away by sync (not hand-edited)
- `.github/instructions/agent_contract.instructions.md` — regenerated-away by sync
- `.gzkit/manifest.json` — remove the agent-contract.md allow-list entry
- Inbound-reference updates across Bucket-1 live files (enumerated during discovery; typically ~15 governance/skill/doc files)
- Parent ADR (read-only)

## Denied Paths

- `.gzkit/rules/attestation-enrichment.md` and `.gzkit/rules/defect-fix-routing.md` — unchanged in this OBPI (OBPI-03 and 04)
- Any Python source code (`src/gzkit/**`) — no code changes; this is governance/docs migration
- Bucket-3 historical artifacts (`docs/design/adr/*/obpis/OBPI-0.0.17-*-agents-md-correction.md`, `artifacts/audits/ghi-bodies-temp/**`, release notes, session plans) — references preserved as historical snapshots
- `src/gzkit/templates/agents.md` — unchanged unless discovery shows it needs a reference update
- New rules under `.gzkit/rules/` or `.claude/rules/` — this OBPI removes; does not add
- Any file mutation outside the Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Before migration, enumerate current AGENTS.md § Prime Directive / § DO IT RIGHT / § Behavior Rules. Any invariant from `agent-contract.md` ALREADY present in AGENTS.md is NOT duplicated — AGENTS.md is the canonical wording. Deduplication is by semantic match, not exact-string match.
2. REQUIREMENT: Invariants unique to `agent-contract.md` (craftsmanship 6c/6g/6h, invariant 10a, the "Do not — judgment prohibitions" Pipeline/Attestation/Source-of-truth subsections) are added to AGENTS.md at the appropriate existing section, in the existing numbering sequence. Numbering is updated consistently.
3. REQUIREMENT: Invariant 10a ("When a skill step names a tool to invoke, invoke it in the same turn") is placed in CLAUDE.md under the existing "Claude Code addendum" section. AGENTS.md does NOT carry 10a (it references Claude-specific tool names like `EnterPlanMode`).
4. REQUIREMENT: `docs/governance/agent-contract-rationale.md` is created with three sections — (a) "Anti-pattern canon" (the list of vibe-coding failure modes), (b) "TASK-driven workflow" (GHI #160 discipline), (c) "Rationale for 6g/6h" (Lindsey et al. 2025 reporting-pathway citation). Each section cites its origin GHI.
5. REQUIREMENT: `.gzkit/rules/agent-contract.md` is deleted (canonical only — mirrors regenerate via sync).
6. REQUIREMENT: The allow-list entry for `agent-contract.md` in `.gzkit/manifest.json` under `rules.unscoped_allowlist` is removed. Manifest remains valid per the JSON Schema (two entries remain).
7. REQUIREMENT: Inbound references are rewritten. Discovery identifies all live governance/skill/doc files referencing the three legacy paths (`.gzkit/rules/agent-contract.md`, `.claude/rules/agent-contract.md`, `.github/instructions/agent_contract.instructions.md`). Each reference points to either (a) the new AGENTS.md section, (b) CLAUDE.md addendum (for 10a cites), or (c) `docs/governance/agent-contract-rationale.md` (for pedagogy cites). Historical artifacts (Bucket 3) are LEFT UNTOUCHED.
8. REQUIREMENT: `uv run gz agent sync control-surfaces` is run after the canonical deletion and allow-list edit. The sync output shows no stale mirror-only paths and no drift warnings. The mirrors under `.claude/rules/` and `.github/instructions/` are no longer generated.
9. REQUIREMENT: `uv run gz validate --unscoped-rules` exits 0 AFTER this OBPI's changes.
10. REQUIREMENT: `uv run gz validate --all` exits 0.
11. REQUIREMENT: `uv run mkdocs build --strict` succeeds — no broken internal links from the reference rewrites.
12. REQUIREMENT: TDD test at `tests/governance/test_agent_contract_fold.py` asserts — (a) `AGENTS.md` contains the migrated invariants (semantic check, not string match); (b) `CLAUDE.md` "Claude Code addendum" contains the 10a text; (c) `.gzkit/rules/agent-contract.md` does not exist; (d) `.gzkit/manifest.json` allow-list has exactly two entries post-this-OBPI.
13. REQUIREMENT: No stdlib `dataclass` introduced; no `shell=True` subprocess; no new third-party dependencies.

> STOP-on-BLOCKERS: if OBPI-01 is not complete (validator + allow-list not in place), STOP.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] Parent ADR: ADR-0.0.20
- [ ] `.gzkit/rules/agent-contract.md` (current content to migrate)
- [ ] Current `AGENTS.md` § Prime Directive, § DO IT RIGHT, § Behavior Rules (existing content for dedupe)
- [ ] Current `CLAUDE.md` "Claude Code addendum" section (insertion point for 10a)

**Context:**

- [ ] OBPI-0.0.20-01 completion status (validator must be in place)
- [ ] ADR-0.17.0 three-layer model (unchanged; sync still runs)

**Prerequisites (check existence, STOP if missing):**

- [ ] `gz validate --unscoped-rules` exits 0 pre-migration (validator working)
- [ ] `.gzkit/manifest.json` has three allow-list entries (OBPI-01 complete)
- [ ] `.gzkit/rules/agent-contract.md` exists

**Blast radius (enumerate inbound references):**

- [ ] Grep for `agent-contract.md` / `agent_contract.instructions.md` in `.gzkit/**`, `.github/**` (excluding historical), `docs/**` (excluding Bucket-3), per-directory `AGENTS.md` files hierarchically

**Existing Code (understand current state):**

- [ ] Review current `AGENTS.md` § Prime Directive for existing invariant wording and numbering conventions
- [ ] Review current `AGENTS.md` § DO IT RIGHT for existing craftsmanship item layout (items 6a-6h placement)
- [ ] Review current `AGENTS.md` § Behavior Rules for existing numbering and Always/Never table structure
- [ ] Review current `CLAUDE.md` "Claude Code addendum" section for placement + style of Claude-specific content
- [ ] Confirm existing skill-surface-sync behavior against a test deletion (dry-run if supported) to verify mirror auto-regenerate semantics

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded in this brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests derived from Requirement 12 before migration
- [ ] Red-Green-Refactor per increment
- [ ] `uv run gz test` passes
- [ ] `uv run gz validate --unscoped-rules` passes post-migration

### Code Quality

- [ ] `uv run gz lint` clean
- [ ] `uv run mkdocs build --strict` clean

## Verification

```bash
# Pre-migration snapshot
wc -l .gzkit/rules/agent-contract.md  # Expect 213
uv run gz validate --unscoped-rules --json  # Expect 3 allow-list entries

# Migration verification (post-edits)
test ! -f .gzkit/rules/agent-contract.md
grep -q "Own the work completely" AGENTS.md
grep -q "invoke it in the same turn" CLAUDE.md
test -f docs/governance/agent-contract-rationale.md

# Sync regeneration
uv run gz agent sync control-surfaces
test ! -f .claude/rules/agent-contract.md
test ! -f .github/instructions/agent_contract.instructions.md

# Quality
uv run gz validate --unscoped-rules
uv run gz validate --all
uv run gz lint
uv run mkdocs build --strict

# Tests
uv run -m unittest tests.governance.test_agent_contract_fold -v
```

## Acceptance Criteria

- [ ] REQ-0.0.20-02-01: Judgment invariants deduplicated and merged into AGENTS.md existing sections
- [ ] REQ-0.0.20-02-02: Unique invariants (6c, 6g, 6h, Do-not subsections) added to AGENTS.md with consistent numbering
- [ ] REQ-0.0.20-02-03: Invariant 10a placed in CLAUDE.md addendum (not AGENTS.md)
- [ ] REQ-0.0.20-02-04: `docs/governance/agent-contract-rationale.md` created with three named sections
- [ ] REQ-0.0.20-02-05: `.gzkit/rules/agent-contract.md` deleted
- [ ] REQ-0.0.20-02-06: Allow-list entry removed from manifest (3 → 2 entries)
- [ ] REQ-0.0.20-02-07: Inbound references rewritten across live governance/skill/doc surfaces (Bucket 1)
- [ ] REQ-0.0.20-02-08: `gz agent sync control-surfaces` regenerates mirrors cleanly (mirror files no longer exist)
- [ ] REQ-0.0.20-02-09: `gz validate --unscoped-rules` exits 0
- [ ] REQ-0.0.20-02-10: `gz validate --all` exits 0
- [ ] REQ-0.0.20-02-11: `mkdocs build --strict` succeeds (no broken links)
- [ ] REQ-0.0.20-02-12: TDD test asserts the semantic migration properties listed in REQ 12
- [ ] REQ-0.0.20-02-13: No new dependencies; no shell=True; no dataclass

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR, tests derived from REQs
- [ ] **Code Quality:** Lint, mkdocs clean
- [ ] **Value Narrative:** 213 lines of per-turn governance preamble removed; AGENTS.md remains authoritative
- [ ] **Key Proof:** Side-by-side `wc -l` before/after + sync output
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint + mkdocs output here
```

### Value Narrative

### Key Proof


uv run gz validate --unscoped-rules
  Validated: unscoped-rules
  ✓ 15 rule file(s) checked (2 allowlisted).
  (exit 0)

uv run gz covers OBPI-0.0.20-02 --json (summary field)
  total_reqs=13, covered_reqs=13, uncovered_reqs=0, coverage_percent=100.0

uv run -m unittest discover -q    → 3507 tests pass (skipped=1)
uv run mkdocs build --strict      → Documentation built in 2.05 seconds
uv run gz validate --advisory-scorecard → ✓ All validations passed
uv run gz obpi precomplete OBPI-0.0.20-02-fold-agent-contract → READY: all 5 preconditions met

ARB receipts consulted: arb-step-unittest-4414c4fd30b9432188bd911bd9d006ad (most recent full-suite GREEN step; 239 receipts total in corpus).

### Implementation Summary


- Migration map: 213-line `.gzkit/rules/agent-contract.md` folded into three destinations — unique invariants (craftsmanship 6c/6g/6h, judgment 12–14, Pipeline-lifecycle and State-doctrine "Never" items) into `AGENTS.md`; Claude-specific invariant 10a into `CLAUDE.md` § Claude Code addendum; pedagogy (anti-pattern canon, TASK-driven workflow, Lindsey 2025 rationale for 6g/6h) into new `docs/governance/agent-contract-rationale.md`.
- Canonical rule file deleted; vendor mirrors (.claude/rules/, .github/instructions/) auto-cleaned by `gz agent sync control-surfaces`.
- Manifest allow-list shrunk from 3 → 2 entries (attestation-enrichment.md + defect-fix-routing.md remain, pending OBPI-03 and -04).
- Inbound references rewritten across 13 live Bucket-1 files (two canonical templates + five canonical rules/skills + four docs + two runbooks). Bucket-3 historical artifacts left untouched per brief.
- Test harness: `tests/governance/test_agent_contract_fold.py`, 9 tests, all `@covers`-decorated covering all 13 REQs (100% parity).
- Files created: `docs/governance/agent-contract-rationale.md`, `tests/governance/test_agent_contract_fold.py`, `.claude/plans/OBPI-0.0.20-02-fold-agent-contract.md`.
- Files deleted: `.gzkit/rules/agent-contract.md` (plus two auto-cleaned mirrors).
- Tests added: 9.
- Date completed: 2026-04-22.
- Attestation status: self-close-lite (Lite lane).
- Defects noted: none new.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: self-close-lite — OBPI-0.0.20-02 folds .gzkit/rules/agent-contract.md into AGENTS.md (unique invariants 6c/6g/6h + judgment 12–14 + pipeline/state-doctrine Never items), CLAUDE.md (invariant 10a), and docs/governance/agent-contract-rationale.md (pedagogy + 6g/6h Lindsey 2025 rationale). Canonical deleted; mirrors auto-cleaned; manifest allow-list shrinks 3→2. 13/13 REQ parity via @covers; 9/9 OBPI tests pass; full suite 3507/3507 pass; gz validate --unscoped-rules exits 0; mkdocs --strict clean.
- Date: 2026-04-22

---

**Brief Status:** Completed

**Date Completed:** 2026-04-22

**Evidence Hash:** -
