---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-15T10:27:20Z'
agent: claude-code
session_id: f6dec6b5-558f-4ce0-bac2-a6eb07ccb646
continues_from: 20260915T094830Z-fix-1008-grouped-verifier.md
---

## Current State Summary

Continues `20260915T094830Z-fix-1008-grouped-verifier.md` within the same session.

The operator objected that GHI growth outruns feature work (measured 2026-09-15: 207 opened / 176 closed in 30 days, 44 open; 142 `fix` vs 3 `feat` commits in 14 days) and that the 2026-09-12 chores and R&D work seemed lost. They ruled "A and C together". Landed as `b7fc95e95`, pushed:

- **A, the R&D discipline.** `docs/governance/rnd-discipline.md` answers the open design questions from `mpas-appropriation-analysis.md`; all six recommendations were accepted. The operator-invoked `gz-rnd` skill is authored at `.gzkit/skills/gz-rnd/SKILL.md`, with a record template, manpage, index, nav and router entries. `ghi-author` Step 0 now searches `docs/governance/rnd/` as prior art.
- **C, the campaign amendment** (§ Amendments 2026-09-15). At NEXT-IN-PRIORITY, work drawn without the operator is taken as: R&D, then the chore estate, then GHI direct repair only when it closes a named arm of the family-closure box, blocks those two, or is an emergency. Handoffs give a multi-session thread its own line. The Workflow fronts R&D entry is rewritten.
- **Item 4 withdrawn.** It proposed routing non-blocking findings to insights instead of GHIs. The operator ruled it out; the ruling is recorded in the amendment (uncommitted at authoring, carried by this handoff's git-sync).

Correction made in session: the alignment map was NOT lost. It landed 2026-09-13 as `docs/governance/rules-tools-audits-refactors-alignment.md` (`980691150`). The agent had relayed the old handoff's "only carrier" claim unverified (insight `agent/relayed-handoff-claim-unverified`).

At authoring: HEAD `b7fc95e95` level with origin/main; the campaign item-4 ruling edit uncommitted; no OBPI locks.

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **new R&D:** now FIRST in drawn-work order. `gz-rnd` is built but has never run. Its acceptance test is the operator's next "consider this for gzkit" paste. It is operator-invoked only (`disable-model-invocation: true`), so no session starts a run on its own.
- **chore estate:** SECOND. Chore-class-system steps 1–6 are all landed, including the conversion directive and per-chore declarations (2026-09-13). What remains is running the chores: board at 36 overdue / 1 due / 3 unmeasured, plus #997, #808, #1009, #1011, and the staleness-gate inconsistency carried from `20260915T085452Z` step 2.
- **ghi triage:** THIRD, narrowed. 44 open at authoring. Draw a GHI only if it closes a named arm of the family-closure box, blocks R&D or chores, or is an emergency. #1013 (heredoc bodies read as statements) blocks ordinary heredoc authoring, which arguably qualifies as blocking.
- **adr/obpi campaign:** unchanged. ADR-0.35.0 TOPMOST; OBPI work only on operator initiation.

### Carry forward
- A multi-session thread in a handoff gets its own named line with a doc pointer (amendment item 2). R&D design: `docs/governance/rnd-discipline.md`. Alignment threads: `docs/governance/rules-tools-audits-refactors-alignment.md` § Advised order. Chores: `docs/governance/chore-class-system.md` § Implementation order.
- Heredoc prose containing `; <verifier>` is refused by the gate until #1013 lands; write commit and issue bodies from a file.

## Decisions Made

- [operator-ruled] On the diagnosis of GHI growth outrunning feature work: "A and C together" (land R&D in committed records and draft the R&D skill design; draft a campaign amendment rebalancing drawn work).
- [operator-ruled] Campaign amendment draft: "Ratify 1–3, rule 4 apart (Recommended)".
- [operator-ruled] R&D design draft: "Accept all six (Recommended)".
- [operator-ruled] Item 4 (insights instead of GHIs for non-blocking findings): "don't change anything about the PD". Prime Directive #6 stands unchanged; the question is closed.
- [agent-chose] Ordered R&D and chores inside the existing NEXT-IN-PRIORITY position rather than moving boxes: the chore class system already discharges under the family-closure box as its agent-side arm (operator ruling 2026-09-12).
- [agent-chose] Recorded the item-4 ruling in the campaign amendment itself, so the stale "put to the operator separately" line cannot invite re-adjudication.

## Immediate Next Steps

1. Put the next move to the operator under the new drawn-work order, never as a flat menu: (a) R&D — the first `/gz-rnd` run, which only the operator starts; ask whether they have material to consider, or whether to take the next open thread in `rules-tools-audits-refactors-alignment.md` § Advised order through an R&D run; (b) chore estate — run overdue chores by class (`uv run gz chores status`); (c) GHI repair only where the amendment's condition holds, with #1013 the likeliest candidate because it blocks heredoc authoring.
2. If (b): start from `gz chores status` and `docs/governance/chore-class-system.md` § Implementation order; present the chore staleness-gate inconsistency (carried from `20260915T085452Z` step 2) as a named inconsistency, not a menu.
3. Keep verification to each work order's named evidence (insight `agent/verification-scope-on-short-fixes`), and verify any handoff claim that something is missing or only in one place before relaying it (insight `agent/relayed-handoff-claim-unverified`).

## Pending Work / Open Loops

- `gz-rnd` has not been exercised; its record directory `docs/governance/rnd/` does not exist until the first run.
- Chore estate: 36 overdue; #997, #808, #1009, #1011 open; staleness-gate inconsistency unruled.
- GHIs from this session: #1012 (reserved-word prefixes and `$( … )`), #1013 (heredoc bodies). Carried: #810, #934, #983 and #894 ruling-gated, #969, #968.
- Untracked except here, as before: the shared lexer reads a quoted lone metacharacter as an operator, and the `shell_reading` docstring claims otherwise.
- Carried from `20260915T085452Z`: insights `chores/staleness-gate-class-fit`, `chores/staleness-signal-fit`, `cli/manpage-flag-claims` awaiting calibration; `--log-file` absent; permission-consent-drift lacks `proofs/settings-patch.md`.

## Verification Checklist

```bash
git status -sb
git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
uv run gz chores status
grep -n "don't change anything about the" docs/governance/build-to-1.0-campaign-2026-08-16.md
test -f .gzkit/skills/gz-rnd/SKILL.md && echo "gz-rnd present"
```
Expected: level with origin; no locks; chores board printed; the item-4 ruling line present; `gz-rnd present`. Re-run rather than trust.

## Evidence / Artifacts

- `.gzkit/handoffs/20260915T094830Z-fix-1008-grouped-verifier.md` (predecessor).
- `docs/governance/rnd-discipline.md`, `.gzkit/skills/gz-rnd/SKILL.md`, `.gzkit/skills/gz-rnd/assets/rnd-record-template.md`, `docs/user/skills/gz-rnd.md`.
- `docs/governance/build-to-1.0-campaign-2026-08-16.md` (§ Amendments 2026-09-15, banner, Movement C box, Workflow fronts).
- `.gzkit/skills/ghi-author/SKILL.md`, `.gzkit/skills/gz-workflow/SKILL.md`, `.gzkit/skills/gz-skill-router/SKILL.md`, `data/distribution_baseline_manifest.json`.
- `docs/governance/rules-tools-audits-refactors-alignment.md`, `docs/governance/chore-class-system.md`, `docs/governance/mpas-appropriation-analysis.md`.
- `.gzkit/insights/agent-insights.jsonl` (insight scopes campaign/work-drawing-balance and agent/relayed-handoff-claim-unverified).
- Commit `b7fc95e95`.

## Settled Rulings

871 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
