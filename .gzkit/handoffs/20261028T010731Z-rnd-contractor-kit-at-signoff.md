---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-28T01:07:31Z'
agent: claude-code
session_id: c2190695-4a85-407d-957f-4984a2e3c958
continues_from:
- .gzkit/handoffs/20261027T093232Z-bookmarks-folded-deps-lsp-rnd-committed.md
- .gzkit/handoffs/20261027T215408Z-session-exit-bookmark.md
- .gzkit/handoffs/20261028T000316Z-session-exit-bookmark.md
---

## Current State Summary

The contractor-kit R&D (docs/rnd/contractor-kit.md) is at sign-off, not yet signed. This traversal ruled every remaining matrix row (C5, C10, C11, C12, B12; C13 answered by canon), the modified pipeline as a crosswalk (four differences to cross as pipeline GHIs), the kit's placement as RO-12 immediately after RO-5, the vibe-coded audit chore as a signature catalogue, row 1 not pursued, row 5 as RO-13 (the two-way mode contract program, ratcheted to zero), and row 6. The challenge was restated and docs/rnd/contractor-kit/review.md written. A design review with the operator then ruled two more items (a self-test is accepted only on a red witness inspected at restoration; RO-12 closes only when each of its eight runtime refusals is witnessed refusing) and took three operator corrections, recorded at the end of the record. The anti-vibing mantra in AGENTS.md was reworded on the operator's choice and landed (5598ec3c6). The session ended because the agent flip-flopped; the operator asked for a fresh re-entry.

## Important Context

Read the last four decision entries of docs/rnd/contractor-kit.md before anything else: the design review, judged from the drydock's side, and the maintenance discipline as the drydock's own. The operator confirmed this distinction verbatim as right: safe mode suspends canon, gzkit's normal-operations rules, which is why the alarms are off and why canon's ceremony is not the measure inside the drydock; the maintenance discipline (JFMM, Part 121, TUM, DFARS 217) is the drydock's own regime for going into MX, doing the work and coming back out, and the kit is that discipline, judged by whether it carries the discipline out faithfully. The failure to avoid: judging the drydock by canon's ceremony, and then overcorrecting by calling the maintenance discipline ceremony. Every ruling in the record stands. Safe mode is open (marker .gzkit/mx.json, contract harbor-pilotage-candidate-2026-10-15.md); one commit per act with a Task: TASK-rnd-contractor-kit trailer; never stage docs/rnd/subagent-folding.md; the run executes no disposition row without a row-level go.

## Decisions Made

- [operator-ruled] Give the agent a handoff and re-enter fresh (verbatim: "give yourself a handoff so we can re-enter fresh - you've flip flopped mutliple times now.").
- [operator-ruled] The two-bullet distinction is right (verbatim: "these are right, btw, but i don't think you tell up from down right now"): safe mode suspends canon; the maintenance discipline is the drydock's own regime and the kit is that discipline.
- [operator-ruled] Reword the AGENTS.md anti-vibing mantra to redraft 1 (verbatim: "the anti-vibing mantra is very awkwardly worded"; "1"), landed with all seven conditions kept.
- [agent-chose] Folded both session-exit bookmarks (20261027T215408Z and 20261028T000316Z, the latter from session b2644508) into this handoff and committed them with it.

## Immediate Next Steps

1. The operator reads docs/rnd/contractor-kit/review.md and rules sign-off for the contractor-kit run: kill or fund. Before putting the question, read the record's last four decision entries; do not re-open settled rulings.
2. On fund, the operator gives row-level gos: row 2 (the two self-test defect candidates, the four pipeline-crosswalk GHIs, the persona-witness GHI, through ghi-author); row 4 (the contract's RO-12 and RO-13 rows with RO-12's refusal list as witness, the contractor brief's order, and the doctrine and skill drafts).
3. Push the unpushed commits through git-sync on the operator's go.
4. If the operator wants it, restore the order of the AGENTS.md anti-vibing section (the governance bullet now sits second because the corpus appends in time order; restoring it means re-capturing the drift bullet, a second canon act).

## Pending Work / Open Loops

The mx-session OBPI lock is past 50% of its TTL. The MX hangar carries advisory debt over 250 hours; before gz mx exit, enter the 9 gz check --full failures on the MX punch list, each with its recovery (carried). After gz mx exit, offer the Cosmic Ray route: the 2026-08-22 decline versus the 2026-10-27 words, and an ADR versus a recorded STDLIB-FIRST exception (carried). Remind the operator to turn off cowork-plugin-management via /plugin (carried). Observed, not acted on: the content retention gate refused, rather than warned, while safe mode was open; whether it should be advisory is RO-10's classification, which is parked.

## Verification Checklist

git log --oneline origin/main..HEAD | head -40; git status --short; uv run gz handoff rulings --search contractor; grep -n '^## decision' docs/rnd/contractor-kit.md | tail -8; grep -n -A2 'ANTI-VIBING' AGENTS.md

## Evidence / Artifacts

`docs/rnd/contractor-kit.md`, `docs/rnd/contractor-kit/review.md`, `docs/rnd/contractor-kit/vocabulary-matrix.md`, `AGENTS.md`, `.gzkit/corpus/AGENTS.md.jsonl`, `.gzkit/insights/agent-insights.jsonl`; commits 4c907bc69 to de259af27

## Settled Rulings

1770 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
