---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-28T06:38:05Z'
agent: claude-code
session_id: 207842df-0151-44e3-bfe3-1dcfa1073f79
continues_from: .gzkit/handoffs/20261028T051718Z-lsp-route-repaired.md
---

## Current State Summary

Resumed from the lsp-route-repaired handoff; all four advised steps done, then the contractor kit was signed off and funded, rows 2 and 4 executed, and the eight follow-up rulings landed. Anti-vibing order restored (37c310fa1). GHI #1278 fixed and closed (7710d1e1b): ceremony-step-gate.py and control-surface-sync.py retired through _RETIRED_HOOKS, TestHookSetsAgree the three-set check; a pre-existing private-import red fixed (52bc18ad0). Sign-off booked in docs/rnd/contractor-kit.md (ecccc69b0). Row 2: GHIs #1289-#1296 filed, #1273 carries the two mode rulings, seven cross-links posted. Row 4: RO-5 amendment (7cf5d0318), contract with RO-12/RO-13 rows, sea trial exit 10, list of discrepancies (721047b3b), doctrine (9017ee55c), mode-contract rule and templates (72c6878a1, compressed c6ed1b9c0), five skills (8501b6ac4). Rulings 1-8: B12 interim close by reviewer subagent (86aebae92, 6291b3f7f), C5 pipeline wording via the inventory (ac530a6c9), exit 8 clears blocking lines only (ff98bef2e), RO-5 five conflicts ruled (e51c9c342), turn-lock retired under GHI #1297 (6f29df43e, cba32815d) and closed after a NOT CONFIRMED then CONFIRMED review. All pushed; origin/main level.

## Important Context

Safe mode is open; the MX session lease is expired and the mx-session claim lease too (announced, never evicted): renew through gz-mx if work continues. The order is RO-5 with its pre-kit repairs, then RO-12 (the kit), then RO-4 and the rest under the kit; RO-13 follows RO-12. AGENTS.md § Defect-fix routing now requires a reviewer that did not do the fix to confirm on the issue before a GHI closes; ghi-close 2.14.0 dispatches it. The pipeline's stage files render from data/obpi_pipeline_control_inventory.json and are digest-pinned in src/gzkit/pipeline_procedure.py: reword through the inventory, never by hand. A gz content land that drops a condition needs a retention map extracted by an independent reviewer (spec-reviewer) and the dropped id named in the attestation text; scorecard rows in docs/governance/advisory-rules-audit.md cite corpus entry ids and must follow a recapture. Subagent gh issue comment calls are denied by the permission classifier; post them from the main session only on the operator's word.

## Decisions Made

- [operator-ruled] Take care of the four advised steps before the funding decision (verbatim: "take care of all 4 items then i give my funding decision").
- [operator-ruled] Contractor kit signed off and funded, with the go on rows 2 and 4 (verbatim: "fund, yes to 2 and 4").
- [operator-ruled] Address the eight open items one at a time (verbatim: "let's adress 1-8, one-at-a-time").
- [operator-ruled] Interim GHI close under B12: a reviewer subagent confirms, then the agent closes (verbatim choice: "Reviewer subagent (Recommended)").
- [operator-ruled] Post all seven blocked cross-link comments (verbatim choice: "Post all seven (Recommended)").
- [operator-ruled] GHI #1294 owns the turnover review; OBPI-0.35.0-19 keeps the occupant record (verbatim choice: "#1294 owns the review (Recommended)").
- [operator-ruled] C5 pipeline wording lands now through the control inventory (verbatim choice: "Reword now via inventory (Recommended)").
- [operator-ruled] Contract exit 8 clears only blocking lines; the rest transfer at handback (verbatim choice: "Blocking lines clear (Recommended)").
- [operator-ruled] RO-5: a second event work_package_changed; a test change by change order is a reopening; operator approves alterations at freeze; a DFS on a REQ is the scope disposition; lifecycle gains commenced and accepted (verbatim choices, each "(Recommended)").
- [operator-ruled] Retire the closeout turn-lock writer (verbatim choice: "Retire it (Recommended)").
- [agent-chose] Retired both #1278 hooks instead of wiring them: each was deliberately unregistered with its README and order line, only the cleanup was missed.
- [agent-chose] Left the kit internals (personas, runtime, records) to RO-12 and drafted only canon amendments under row 4.
- [agent-chose] Compressed the new mode-contract rule under the AGENTS.md size-limit rule rather than asking; compression invites operator review.
- [agent-chose] Left the crosswalk in the R&D record until its home is named, per its own decision.

## Immediate Next Steps

1. The operator reviews the compressed mode-contract rule (c6ed1b9c0), since a compression changes how canon reads.
2. Pull RO-5 with its pre-kit repairs (#1200, #1206, #1208, #1028, #1273 and the reused-part set), the campaign sequencing the next pull; renew the MX lease through gz-mx first.
3. Specify RO-12, the kit, with the operator once RO-5 lands; its witness is the eight-refusal list.
4. Optionally run a retroactive review on GHI #1278 [settled], which closed before the reviewer-closes rule.

## Pending Work / Open Loops

- The skill template has no Mode Contract section: the scaffold is inline in src/gzkit/skills/__init__.py (GHI #453 [settled] removed templates/skill.md); needs a src change.
- The gz-obpi-specify brief asset (.gzkit/skills/gz-obpi-specify/assets/OBPI_BRIEF-template.md) lacks the Mode Contract section the ADR and OBPI templates gained.
- data/instructions_files_budget.json still holds the personas total; GHI #1295 carries the per-file cap.
- The vocabulary crosswalk stays in docs/rnd/contractor-kit.md until the DDD-discipline run names its home.
- The record notes an open tension: reviewer dispatch per act costs more than the cheaper-sessions clause allows; per-task-card routing does not settle it.
- The R&D record says the assert self-test arm always returns 0; GHI #1290 records that this holds only under python -O.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0.
- uv run python -m unittest tests.test_hooks tests.test_closeout_ceremony_cmd tests.governance.test_pipeline_procedure_render passes.
- uv run mkdocs build --strict and uv run gz validate --documents each exit 0.
- gh issue view 1297 --json state reads CLOSED; GHIs #1289-#1296 are OPEN.
- uv run gz handoff rulings --search "Reviewer subagent" returns the B12 interim ruling.

## Evidence / Artifacts

- `docs/rnd/contractor-kit.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/governance/safe-mode-doctrine.md`
- `docs/governance/harbor-ro5-work-packages.md`
- `docs/governance/harbor-contractor-brief.md`
- `.gzkit/rules/mode-contract.md`
- `.gzkit/skills/ghi-close/references/problem-report-states.md`
- `data/obpi_pipeline_control_inventory.json`
- `tests/test_hooks.py`
- `tests/test_closeout_ceremony_cmd.py`

## Settled Rulings

1782 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
