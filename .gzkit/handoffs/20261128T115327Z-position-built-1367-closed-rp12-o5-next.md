---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-28T11:53:27Z'
agent: claude-code
session_id: e72a4b01-70e5-474b-8956-e7d1025b8368
continues_from: .gzkit/handoffs/20261128T092052Z-open-ghi-queue-1361-1370-fences-as-scopes.md
---

## The Picture

### Tactical

This session closed GHI #1367 and built the position into every resume. Nothing on the drydock's repair orders moved: of the 366 commits since 2026-11-22, 56 name a repair order, and none of today's do.

- #1367, the size-limit fence: rebuilt as a proximity test after two independent reviews returned NOT CONFIRMED; closed under your "Disclosed shapes (Recommended)" ruling after a fourth review confirmed.
- The position: `gz handoff resume` and session orientation now lead with facts read from the record, then this picture. `gz handoff create` refuses a CREATE handoff without all three levels.
- The board: https://claude.ai/artifact/7qER9po2RYys2iQdsFwkHJ, ordered tactical, operational, strategic, with the campaign and gzkit itself added.
- The hangar lease was renewed (24h) at the end of the session.

Next: review the board with you, then cut RP-12 O5's tasks for your approval.

### Operational

The drydock has been out of service since 2026-10-20. Of its 16 repair orders, 3 are closed (RP-2, RP-3, RP-9), and 2 of its 13 exit conditions are met.

- RP-12, the contractor kit, is the critical path. O1 to O4 closed through Gate 5 by 2026-11-22. O5, stop work and the hold on the extended block (refusal 4, rulings 11 to 13), is next and has no task cut yet; O6 to O9 follow.
- RP-14's later tranches and RP-13's retrofit run under the kit, so they wait on it.
- 16 of the 69 open lines on the contract's list of discrepancies block return to service; the ledger's list holds none yet, since RP-12 O9 carries the prose lines into it.
- The passage log's last entry is 2026-11-19: the prompt-audit residue worked since then closed issues, not orders.

### Strategic

The road to 1.0 is the campaign plan, 7 of 30 items done, and it is parked behind the drydock. Its topmost item sits inside ADR-0.35.0, which RP-8 froze, so the campaign cannot move until civil rule; updating it to the drydock's results is civil rule's first work.

The drydock is the strategic act now: replacing the ADR and OBPI process with the catalog, work package and release structure, cutting what agents load, and re-rigging the toolchain. Its exit is written in the contract's § Exit; nothing new needs inventing. Work that closes no repair order delays it.

## Current State Summary

The session resumed from `20261128T092052Z-open-ghi-queue-1361-1370-fences-as-scopes.md` and worked its step 2, GHI #1367, then turned to the position you asked for at every resume.

- #1367 is CLOSED. Commits 90153eb95, 090d850f6, f588107a7, 666063e40, c8a0f7bee, 6ced7f4ca, 11d14f1d5, e82ec33b7. The fence reads sentences, judges by proximity, reads chores, the AGENTS corpus, AGENTS.md, CLAUDE.md, README.md, docs/user, non-dated docs/governance and src/gzkit, and admits dated history only in anchored forms. Scorecard row 20a scores the clause; pythonic.md is at 0.8.3.
- The position and picture are BUILT (a98d11b64, 1e1f7cd3a): `gzkit.mx.position`, the picture flags at `gz handoff create`, resume and orientation leading with both. gz-session-handoff is at 7.10.1.
- The drydock board is published at https://claude.ai/artifact/7qER9po2RYys2iQdsFwkHJ, a snapshot read 2026-11-28.
- The MX lease was renewed with `gz mx renew` (no guard ran).
- Full unit tier: 14,499 tests OK. `gz check` passes with the pre-existing MX demotions only.

## Important Context

- The board (https://claude.ai/artifact/7qER9po2RYys2iQdsFwkHJ) is reviewed with the operator at every resume: re-read its facts from the record, republish its data files, then walk it. Its datasets are fixed files (orders, exit, facts, campaign, project); the page is `files/index.html` in its store.
- `gz handoff resume` prints the computed position first. Relay those numbers as printed, never from memory. Repair-order states are not computed; they live in the contract's prose.
- A new loose module under `src/gzkit/` is a hexagon finding: the position went into `gzkit/mx/`, the picture grammar into `handoff_validation.py`.
- The orientation is over its budget (advisory); it shrank by 312 B this session while gaining the position block. Compress before any growth.
- RP-12's specification is `docs/governance/harbor-ro12-contractor-kit.md`; O4's task cut (approved 2026-11-20) is the pattern for O5's.
- A `pre-fix #N` phrase in a commit message trips the closing-keyword guard on push; write "before the fix of #N".

## Decisions Made

- [operator-ruled] Work step 2, #1367 (verbatim: "proceed with step 2, #1367").
- [operator-ruled] The size-limit fence does not read the pool ADRs (verbatim: "the pool adr will be phased out and drained into the requirements catalog/backlog, why bother? so much of what we are doing now is related to what we are trying to achieve in the dry dock").
- [operator-ruled] #1367's Invariant holds over the fence's disclosed shapes (verbatim: "Disclosed shapes (Recommended)").
- [operator-ruled] Build the drydock status board (verbatim: "yes, build the drydock status board - I asked for this as a part of every handoff resume and still dont have it: current tactical|operational|strategic position.").
- [operator-ruled] Build the position into resume now, ahead of the handback the 2026-10-31 ruling had sequenced (verbatim: "build it now so every resume shows the position - this should cut down on vibe coding.").
- [operator-ruled] Both an authored picture and computed facts (verbatim: "Both (Recommended)").
- [operator-ruled] The picture's order (verbatim: "left to right: tactical | operational | strategic").
- [operator-ruled] Expand the board with the campaign and gzkit, and review it each time (verbatim: "we should expand that board to also include the campaign and gzkit itself, that is a useful artifact to have you present/review with me each time.").
- [operator-ruled] Renew the lease, write this handoff toward RP-12 O5, and sync (verbatim: "renew the lease and create a fresh handoff (RP-12 O5) and git sync").
- [agent-chose] Repair-order states stay in the picture, not the computed position, because no record carries them.
- [agent-chose] Orientation's account names 3 commit subjects instead of 10, to grow the position block without growing the orientation.
- [agent-chose] The position stays out of `gz handoff resume --json`: it is a property of the tree, not of the document.

## Immediate Next Steps

1. Present the computed position from `uv run gz handoff resume` and this picture, then re-read the board's facts from the record, republish them, and review the board (https://claude.ai/artifact/7qER9po2RYys2iQdsFwkHJ) with the operator.
2. On the operator's go, cut RP-12 O5's tasks for approval, as O4's were cut: stop work and the hold on the extended block (refusal 4), from rulings 11 to 13 of `docs/governance/harbor-ro12-contractor-kit.md`. Work it through its governed path.
3. Read CI on the pushed head (`gh run list --branch main --limit 3`): the run on 1e1f7cd3a was in progress at handoff.
4. Put the pending operator decisions one at a time: the review of the 9 guard canaries (size-limit-citations among them, rebound this session), and whether `test_git_sync_flags_stated_once.py` (#1390 [settled]) becomes a scope.
5. Work the open-issue queue only where an issue blocks return to service; otherwise it waits for civil rule, since issues close no repair order.

## Pending Work / Open Loops

- SPEC-session-handoff-picture pieces 3 (the session log) and 4 (the exit signal) are not built, and piece 1's sync order and boundary rule are not either; the contract's brief line stays open until the operator finds the picture reads well (acceptance row 10).
- Surfaces the size-limit fence does not read (non-pool docs/design, docs/rnd, .claude/plans, .yaml and .json under .gzkit) await an operator ruling: insight 2026-11-28T10:52:49.661442+00:00.
- 9 guard canaries await operator review.
- #1365 is blocked on OBPI-0.35.0-20, which safe mode cannot initiate. #1418 needs a ruling on renormalization.
- The coverage-40pct chore id embeds its value; the Dependency currency failure on d4dea64c5 is unexamined; whether anything calls render_rule_for_copilot is unclaimed.
- The open queue carried from the predecessor (#1371, #1372, #1377, #1378, #1380, #1382, #1385, #1388, #1409, #1412, #1418) stays queued, screened against the drydock first.
- Shift turnover: no tag hung (`gz wp tag show --all`: none issued), no work package in flight (`gz wp runs`: none), no ledger discrepancy line open; the contract's prose list holds 69 open, 16 blocking.

## Verification Checklist

- `uv run gz handoff resume`: the position leads, then this picture.
- `gh run list --branch main --limit 3`: CI on 1e1f7cd3a.
- `uv run gz validate --size-limit-citations` at full strength (`GZKIT_MX_FULL_STRENGTH=1`): 0 findings.
- `uv run -m unittest tests.test_handoff_position tests.test_handoff_cli`: OK.
- `uv run unittest-parallel -t . -s tests --buffer`: 14,499+ OK.
- `uv run gz wp tag show --all` and `uv run gz wp runs` for the turnover.

## Evidence / Artifacts

- `src/gzkit/mx/position.py`
- `src/gzkit/handoff_validation.py`
- `src/gzkit/commands/handoff.py`
- `scripts/session_orientation.py`
- `src/gzkit/governance/trust_audits/size_limit_citations.py`
- `tests/test_handoff_position.py`
- `tests/governance/test_audit_size_limit_citations.py`
- `docs/governance/session-handoff-rationale.md`
- `docs/design/briefs/SPEC-session-handoff-picture.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/user/manpages/handoff-create.md`
- `docs/user/manpages/handoff-resume.md`
- `.gzkit/skills/gz-session-handoff/SKILL.md`

## Settled Rulings

2673 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
