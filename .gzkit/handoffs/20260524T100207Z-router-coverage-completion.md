---
mode: CREATE
adr_id: ADR-0.27.0
branch: main
timestamp: "2026-05-24T10:02:07Z"
agent: claude-code
obpi_id: OBPI-0.27.0-04
session_id:
continues_from:
---

<!-- Handoff document for ADR-0.27.0 — created by claude-code at 2026-05-24T10:02:07Z -->

## Current State Summary

ADR-0.27.0 (namespace-router-product-surface) work mid-flight. OBPI-0.27.0-01 (router skill files) and OBPI-0.27.0-02 (router surface sync) shipped in prior sessions. OBPI-0.27.0-03 (router-tables-validator) shipped implementation in commit `9b8b408b feat(validate): add --router-tables scope (OBPI-0.27.0-03)` but ceremony was deferred this session after the validator's exit-1 surface revealed a design gap in the parent ADR.

This session:
- Ran OBPI-03 through Stage 1 + Stage 4 evidence prep (ARB receipts generated; brief authored-readiness fixed by removing HTML comment containing "one-sentence" placeholder trigger in the Objective section).
- Operator surfaced that the 16 direction-2 `router_tables_coverage` advisories are not a validator defect but evidence of incomplete ADR design: Promotion Criteria #2 used "no orphaned high-use skills" without defining "high-use."
- Decision: route all skills (drop the undefined "high-use" qualifier); add `gz-chores` as 7th router for the 7 chore-flavored skills; route remaining 9 under existing routers by natural namespace.
- Empirical grounding from GSD (https://github.com/open-gsd/get-shit-done-redux) reference: routers range 696–1131 bytes (avg ~930, ~60 bytes/skill); the original ≤500-byte gzkit aspiration was unbacked.
- Filed GHI #522 capturing design gap + resolution; closed `superseded` once OBPI-04 brief was authored.
- Amended parent ADR-0.27.0: Decision section now lists 7 routers; Promotion Criteria #2 rewritten to "every concrete skill routed by exactly one router"; Decomposition Scorecard updated (Split Surface Boundary: 1, Final Target OBPI Count: 4); Checklist row 04 added.
- Authored OBPI-0.27.0-04-router-coverage-completion brief end-to-end (Allowed Paths narrowed to actual router files, FAIL-CLOSED requirements name the 7 chore + 9 non-chore routings, Acceptance Criteria carry concrete REQ IDs, verification commands runnable). `gz obpi validate --authored` passes.

OBPI-03 lock released. OBPI-03 ARB receipts (`arb-ruff-64d8727299814330960f7e52b9103b05`, `arb-step-typecheck-8e4cf7c1774647648c0c291dc07bc9b1`, `arb-step-unittest-33716fff2ddd486ab73b2409b23b239d`, `arb-step-unittestscoped-5c5784eb255842fa9d17bf0da34e293e`) persist in `artifacts/receipts/` — they remain valid for the eventual OBPI-03 ceremony.

## Important Context

- **OBPI-03 ceremony is paused, not abandoned.** Its brief has full evidence (value narrative, key proof, implementation summary). The block on attestation is purely that `uv run gz validate --router-tables` exits 1 — and that exits 1 because the design gap exists. Once OBPI-04 lands and the validator returns exit 0, OBPI-03 can attest with the existing evidence + an updated Key Proof showing the clean validator state.
- **Skill-surface sync discipline (binding):** `.claude/rules/skill-surface-sync.md` non-negotiable rule #6 — any `skill-version:` bump MUST set `last_reviewed:` to today in the same edit. Every router SKILL.md edited in OBPI-04 needs both bumps. Forgetting the date desynchronizes the 90-day staleness audit.
- **Router byte budget is empirical, not hard-capped.** ADR-0.27.0 § Decision now says so explicitly ("Router byte budget is empirical, not hard-capped — GSD reference routers range 696–1131 bytes…"). Don't artificially cap at the old 500-byte aspiration; landing in GSD's 696–1131 envelope is the contract.
- **gz-chores is NEW (uses `**CREATE**` marker).** OBPI-04's Allowed Paths declares `.gzkit/skills/gz-chores/SKILL.md **CREATE**` so the brief validator's path-existence check exempts the net-new file (`extract_brief_creates_paths` in `src/gzkit/governance/brief_path_validity.py`).
- **OBPI-03 retrospective plan file exists** at `.claude/plans/OBPI-0.27.0-03-router-tables-validator.md`. The plan-audit receipt (`.plan-audit-receipt-OBPI-0.27.0-03.json`) is PASS. Both untracked — will land in this session's git-sync.
- **Pipeline markers exist for OBPI-03** (`.claude/plans/.pipeline-active-OBPI-0.27.0-03-router-tables-validator.json` and legacy `.claude/plans/.pipeline-active.json`). Cannot be removed by hand (classifier policy); next pipeline run will overwrite them. They are stale-but-harmless once the lock is released.

## Decisions Made

- **Decision:** Drop "high-use" qualifier from ADR-0.27.0 Promotion Criteria #2; rewrite as "every concrete skill is routed by exactly one router."
  **Rationale:** "High-use" was undefined — no list, no threshold, no opt-out mechanism — so it could not mechanically resolve. The validator (correctly per its REQs) enforces "every skill," not "every high-use skill." The two didn't match. Tightening to "every skill" makes the rule mechanical.
  **Alternatives rejected:** (a) Add a `router_coverage: exempt` frontmatter field so internal-only skills can opt out — rejected because looking at the actual 16 unrouted skills, every one has a natural router home; the "internal-only" class was theoretical complexity for a class that doesn't exist. (b) Loosen the validator's exit code for direction-2 — rejected because it makes the gap quieter without solving it.

- **Decision:** Add `gz-chores` as a 7th namespace router; route 7 chore-flavored skills under it.
  **Rationale:** Operator's stated origin instinct included a "chores" router; 7 of the 16 unrouted skills are chore-flavored (chore-runner, deps-upgrade, foundation-triage, pythonic-pattern-detect, pythonic-pattern-apply, check-config-paths, cli-audit). Semantic clarity beats grab-bag.
  **Alternatives rejected:** (a) Expand `gz-manage` to absorb chores (GSD's `ns-manage` does this with 11 skills) — rejected because it loses the "chores" discoverable surface; gz-manage stays operational/workflow management. (b) Distribute chores across gz-quality / gz-manage / gz-governance — rejected; loses chores as discoverable namespace.

- **Decision:** Route 9 non-chore unrouted skills under existing routers by natural namespace.
  **Routing map:** `gz-justify` + `gz-plan-audit` → `gz-workflow`; `gz-competitor-radar` → `gz-project`; `gz-adr-evaluate` + `gz-migrate-semver` + `gz-obpi-lock` → `gz-governance`; `gz-obpi-simplify` → `gz-quality`; `gz-issue-file` → `gz-manage`.
  **Rationale:** Each was missed in OBPI-01 by expediency, not by design. The placements are unambiguous.

- **Decision:** Defer OBPI-03 ceremony until OBPI-04 lands a clean `gz validate --router-tables` exit 0.
  **Rationale:** Attesting OBPI-03 while the validator exits 1 against the live surface would attest to an intentionally-broken state. The validator's job is to surface gaps; the gap is real. Closing OBPI-04 makes attestation honest.
  **Alternatives rejected:** Attest OBPI-03 now with a known-failing validator and file a follow-on — rejected; couples attestation with an open known-bad state.

## Immediate Next Steps

1. **Execute OBPI-04:** Run `/gz-obpi-pipeline OBPI-0.27.0-04` to enter the pipeline. The brief is authored-validated; needs plan-audit (likely via `/gz-plan-audit OBPI-0.27.0-04` first). Implementation pass writes the new `.gzkit/skills/gz-chores/SKILL.md`, edits the 5 existing routers (gz-workflow, gz-project, gz-governance, gz-quality, gz-manage) to add their respective new entries, runs `uv run gz agent sync control-surfaces`, confirms `uv run gz validate --router-tables` returns exit 0 with 0 errors, and presents Stage 4 evidence for operator attestation.

2. **Resume OBPI-03 ceremony:** After OBPI-04 attests clean, run `/gz-obpi-pipeline OBPI-0.27.0-03 --from=ceremony` to re-enter Stage 4 for OBPI-03. The brief's Key Proof section needs updating to show the post-OBPI-04 validator state (exit 0, 0 errors) — replace the "16 advisories" demo with the clean run. ARB receipts from this session are still valid; re-running the unittests is optional but cheap. Then attest.

3. **Optional: Author OBPI-03 ceremony preflight.** Before the ceremony, refresh ARB receipts if they exceed the staleness threshold; rerun `uv run gz arb step --name unittest -- uv run -m unittest -q` and `uv run gz arb ruff` if so.

4. **Close out ADR-0.27.0:** After both OBPIs attest, the parent ADR is ready for closeout. Run `/gz-adr-closeout-ceremony ADR-0.27.0` to walk through the ceremony.

## Pending Work / Open Loops

- **OBPI-0.27.0-03 ceremony pending.** Brief is authored, validator implementation committed (`9b8b408b`), ARB receipts captured this session. Blocked on OBPI-04.
- **OBPI-0.27.0-04 ready to execute.** Brief authored + validated; plan-audit and implementation are next-session work.
- **Stale pipeline markers for OBPI-03** exist at `.claude/plans/.pipeline-active-OBPI-0.27.0-03-router-tables-validator.json` and `.claude/plans/.pipeline-active.json`. Cannot be removed by hand. Will be overwritten or aged-out (`gz obpi pipeline --clear-stale` removes after 4h).
- **Manpage docs for `gz validate --router-tables`** shipped in OBPI-03's commit — confirm no further docs work is needed once OBPI-04 lands clean (`uv run gz lint` and `uv run gz validate --documents` already pass).
- **Optional rule edit:** `.claude/rules/skill-surface-sync.md` non-negotiable rule #6 fires on every router SKILL.md edit in OBPI-04. If the rule's `last_reviewed:` field on the 6 existing routers is older than today, those bumps are part of OBPI-04 acceptance criterion REQ-04-05.

## Verification Checklist

- [ ] `git branch --show-current` → `main` (matches handoff frontmatter)
- [ ] `uv run gz obpi validate --authored docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-04-router-coverage-completion.md` → PASS
- [ ] `uv run gz obpi validate --authored docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-03-router-tables-validator.md` → PASS
- [ ] `uv run gz validate --router-tables` → exit 1 with 16 advisories (baseline before OBPI-04)
- [ ] `uv run gz obpi lock list` → no lock on OBPI-0.27.0-03 (released this session)
- [ ] `gh issue view 522 --json state` → CLOSED
- [ ] `uv run gz register-adrs` shows ADR-0.27.0 with 4 OBPIs in the checklist

## Evidence / Artifacts

- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md` — parent ADR (amended: 7-router decision table, mechanical promotion criteria, scorecard update, OBPI-04 checklist row)
- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-04-router-coverage-completion.md` — newly authored OBPI-04 brief (authored-validated)
- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-03-router-tables-validator.md` — OBPI-03 brief (Objective HTML comment removed; otherwise unchanged from prior session)
- `.claude/plans/OBPI-0.27.0-03-router-tables-validator.md` — retrospective plan file for OBPI-03 (untracked; will land in git-sync)
- `.claude/plans/.plan-audit-receipt-OBPI-0.27.0-03.json` — plan-audit PASS receipt for OBPI-03 (untracked)
- `artifacts/receipts/arb-ruff-64d8727299814330960f7e52b9103b05.json` — OBPI-03 ARB ruff receipt (lint clean)
- `artifacts/receipts/arb-step-typecheck-8e4cf7c1774647648c0c291dc07bc9b1.json` — OBPI-03 ARB typecheck receipt (clean; warnings in unrelated files)
- `artifacts/receipts/arb-step-unittest-33716fff2ddd486ab73b2409b23b239d.json` — OBPI-03 ARB unittest receipt (5508/5508 pass)
- `artifacts/receipts/arb-step-unittestscoped-5c5784eb255842fa9d17bf0da34e293e.json` — OBPI-03 ARB scoped unittest receipt (3/3 pass)
- `.gzkit/ledger.jsonl` — ledger events for OBPI-03 lock claim/release and pipeline init
- `docs/governance/GovZero/adr-status.md` — Layer-3 derived view; regenerated this session via `uv run gz register-adrs`

## Environment State

- Python 3.13.x via `uv run`
- Branch `main`, ahead/behind clean before this session's edits
- `gh` authenticated as the operator's user
- Pipeline runtime confirmed active (`uv run gz obpi pipeline OBPI-0.27.0-03-router-tables-validator --from ceremony` ran cleanly mid-session before lock release)
