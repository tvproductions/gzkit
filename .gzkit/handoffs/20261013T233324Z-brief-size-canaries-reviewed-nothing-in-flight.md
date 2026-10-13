---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-10-13T23:33:24Z'
agent: claude-code
session_id: 10275a90-7ba7-4466-bcda-ea077c3d5579
continues_from: .gzkit/handoffs/20261013T094641Z-brief-size-bound-landed-three-issues-open.md
---

## Current State Summary

This session resumed the predecessor, verified its claims, and booked one operator review. It did no OBPI work and changed no source.

- The two guard canaries for the claims brief-size and brief-size-grandfathered are reviewed. `gz canary review` wrote two guard_canary_reviewed ledger events at 2026-10-13T23:29:01Z with attestor g0 and the operator's words, and reviewed_by reads g0 on both entries in `data/guard_canaries.json`. No canary in the registry is left unreviewed (25 entries, none with a null reviewed_by).
- Verified at resume against Layer 2: OBPI-0.35.0-15-pipeline-run-position reads ATTESTED COMPLETED; no lock is held; origin/main and HEAD were level at 9ae7aab35; `gz validate --brief-size` and `gz validate --receipt-shape` each exited 0; GHI #1196 reads CLOSED; GHI #1193, #1194, #1195, #1197, #1198, #1199, #1200, #1202 to #1210 read OPEN.
- Not re-run this session: the 26 brief-size unit tests, the full gate, and the canary sweep. The predecessor's statement that they passed on the landed tree stands unchecked.
- Nothing is in flight: no lock, no pipeline marker, no pipeline run.
- The session ends with the operator's git-sync, which commits this handoff, the canary registry, and the ledger rows.

## Important Context

- The predecessor holds for everything it says about the brief-size bound, the ceilings, the operator's judgment on decomposition, and the rule that a concluded brief is not changed. Read it before cutting or initiating any ADR-0.35.0 brief.
- This session's start-of-session orientation was generated at 09:10Z and named the 09:01Z handoff as newest. The 09:46Z handoff was written afterward by another session in this checkout. `gz handoff resume` selected the 09:46Z document, and that is the one resumed. Run `gz handoff resume` and do not rely on the orientation text when a session has been open a while.
- The predecessor's claim of a clean tree was stale at resume by one row: a session_exit_bookmark_skipped event for session 1c9a4ac3, written at 09:48:50Z after that handoff. It voided no advised step and is committed by this session's git-sync.
- A canary review lapses when the guard function, the claim id or the designated test id changes: the binding hash no longer matches and the canary waits for a fresh review. Both reviewed bindings are on audit_brief_size in `src/gzkit/governance/trust_audits/brief_size.py`; a repair under GHI #1197 that edits that function will lapse both.
- The brief-size canary's designated test exercises the three counted dimensions (REQs, numbered requirements, allowed paths) and not the two byte dimensions. The mutant disables the comparison for all five, so the test still fails under it. The operator was told this before accepting.
- No `gz handoff decide` ruling was booked on the predecessor. The operator's words in this session addressed the canaries and the session close, not the handoff as a whole.
- Workflow fronts (source: the active campaign plan, section Workflow fronts). adr/obpi campaign: not worked; ADR-0.35.0 item 16 is next by the campaign order, its brief is over a size bound and under a ceiling, and only the operator initiates it. ghi triage: the queue was not read as a whole; the issues named below were checked for state only. handoff system: used, not changed. new R&D: not touched.

## Decisions Made

- [operator-ruled] Both brief-size guard canaries are accepted as reviewed (verbatim: "accept both"). Booked through gz canary review for the claims brief-size and brief-size-grandfathered.
- [operator-ruled] Close the session with a new handoff and then a git-sync (verbatim: "new handoff, then git sync").
- [agent-chose] Resumed the 09:46Z handoff and not the 09:01Z one the session-start orientation named, because the 09:46Z document is newer and continues from it.
- [agent-chose] Did not book a gz handoff decide ruling, because no operator words in this session ruled on the predecessor as a whole.
- [agent-chose] Did not re-run the unit tests, the full gate or the canary sweep at resume; reported them to the operator as unverifiable and left them so.

## Immediate Next Steps

1. Present this handoff to the operator and take their ruling before executing anything. Confirm with git status --short, git rev-list --left-right --count origin/main...HEAD, uv run gz obpi lock list and uv run gz validate --brief-size.
2. Before OBPI-0.35.0-16 is initiated, put to the operator how briefs OBPI-0.35.0-16 to -20 are re-cut. Each is over a size bound and held by a ceiling, and the operator has said they are not well decomposed. Re-cutting edits the ADR-0.35.0 checklist and is the operator's to initiate. Tell the operator too that the -16 brief names refresh_pipeline_markers, a function OBPI-0.35.0-15 removed, and that GHI #1203 may be ruled into it.
3. Take the operator's rulings that open issues wait on: for GHI #1200, what a run may do when it reaches the fix-cycle bound; for GHI #1210, whether any section of a concluded brief stays writable and whether the repair is worked alone; for GHI #1204, how five sentences of a completed brief are read; for GHI #1206, whether a work-starting re-entry passes the launcher's gates; for GHI #1207, whether the launcher gains the two checks or the manpage loses the two bullets.
4. If the operator selects a direct repair: GHI #1197 should read the bounds in src/gzkit/brief_size_bounds.json and not declare a second set, and will lapse both canary reviews if it edits audit_brief_size; GHI #1205 and GHI #1208 are small and carry reproductions in their bodies.

## Pending Work / Open Loops

- Open and unselected from the brief-size session: GHI #1197, GHI #1200, GHI #1210.
- Open and unselected from the OBPI-0.35.0-15 run: GHI #1193, GHI #1194, GHI #1195, GHI #1198, GHI #1199, GHI #1202, GHI #1203, GHI #1204, GHI #1205, GHI #1206, GHI #1207, GHI #1208, GHI #1209.
- Remaining under ADR-0.35.0: OBPI-0.35.0-11, -12, -13, -16, -17, -18, -19 and -20 pending, and OBPI-0.35.0-09 repudiated.
- Carried from the predecessor and not acted on here: the whole-tree acceptance digest and the inert negative-control decoys are recorded as insights and have no issue; compound requirements have no mechanical witness; the ceiling values are held against HEAD by a unit test only; registered worktrees named gzkit-red and several under the Codex worktrees directory were seen and left alone.
- Carried from the 09:01Z handoff and not acted on here: seven observations that live only in the completed brief's Tracked Defects; the unruled question of an issue for the three settled-GHI regression tests that skip silently when the uv offline cache holds no pre-commit; stale Codex broker processes left running.

## Verification Checklist

- git status --short prints nothing and git rev-list --left-right --count origin/main...HEAD prints 0 0, or only later commits.
- grep -c '"reviewed_by": null' data/guard_canaries.json prints 0.
- grep -c guard_canary_reviewed .gzkit/ledger.jsonl counts the two events for brief-size and brief-size-grandfathered dated 2026-10-13T23:29:01Z among its rows.
- uv run gz validate --brief-size exits 0 and prints Validated: brief_size.
- uv run gz validate --receipt-shape exits 0.
- uv run gz obpi lock list prints No active locks.
- uv run gz obpi status OBPI-0.35.0-15-pipeline-run-position reads Runtime State ATTESTED COMPLETED.
- gh issue view 1196 --json state reads CLOSED; 1197, 1200 and 1210 read OPEN.

## Evidence / Artifacts

- `data/guard_canaries.json` (reviewed_by now g0 on the two brief-size entries)
- `.gzkit/ledger.jsonl` (two guard_canary_reviewed events; one session_exit_bookmark_skipped row from the prior session)
- `src/gzkit/governance/trust_audits/brief_size.py` (the guard both canaries bind)
- `tests/governance/test_brief_size.py` (the two designated tests)
- `docs/user/manpages/canary-review.md` (what a review records and when it lapses)
- `.gzkit/handoffs/20261013T094641Z-brief-size-bound-landed-three-issues-open.md` (the predecessor)
- `.gzkit/handoffs/20261013T090121Z-obpi-0.35.0-15-all-findings-filed-and-linked.md` (its predecessor, for the OBPI-0.35.0-15 issues)

## Settled Rulings

1524 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
