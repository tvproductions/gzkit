---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-28T23:17:40Z'
agent: claude-code
session_id: 0462dc35-65f6-444f-919f-ed0190161e7f
continues_from: .gzkit/handoffs/20260928T092244Z-session-end-obpi-07-landed.md
---

## Current State Summary

Session 0462dc35 resumed 20260928T092244Z-session-end-obpi-07-landed (operator ruled proceed on the carried loops and the five 2026-09-28 insights, booked via gz handoff decide). Delivered: GHIs #1145 (brief-reconcile receipt mtime-keyed), #1146 (gz test --obpi no hang bound), #1147 (unquoted heredoc executes backticked prose) and #1148 (ADR-0.0.32 adopter-edit amendment work order, blocked on ADR-0.40.0) filed. Commit 05d1dda14: gz-obpi-pipeline 6.60.0 Stage 5 corrected (lock is released by gz obpi complete; new step 3a authors the Step 4b brief section) and design-amendment disposition 2(a)(b) direct fixes (agent-contract-rationale.md, rnd-discipline.md, gz-rnd 0.4.0). Commit 1e03fbe3c: OBPI-0.37.0-04 line 64 resolution note. Both pushed. Then a full ruling docket: 26 of 28 R2 issues ruled, each ruling posted verbatim as a comment on its GHI. NONE of the ruled work has started.

## Important Context

The rulings live as comments on each GHI (gh issue view N --comments, newest comment headed 'Operator ruling 2026-09-28 (ruling docket)'); read the comment before drawing the issue. Draw ruled work one issue at a time through ghi-close (single writer, fix(<scope>): <summary> (GHI #N), close with SHA). Direct-fix candidates still pass AGENTS.md Defect-fix routing size and live-brief checks at draw time. #894 edits src/gzkit/commands/content/retire.py, which OBPI-0.35.0-08 (in progress) declares read-only; the operator authorized both the _is_named move and a dated brief amendment permitting only that extraction. #832 retags and pushes 22 releases: outward-facing, authorized by ruling, but canary-check the first retag's GitHub release body and assets are untouched. #802 needs the operator to set the Pages custom domain and DNS before an agent can re-measure. #611 (b)(c): run gz ledger correct with --dry-run first and re-derive each subject triple. OBPI work (#978 verbs, #939 retention scope into OBPI-10, #921/#922 held) is operator-initiated only. #927 is not a docket item: verify #849's fix covers non-REQ guards, then close via ghi-close. Research-agent claims in this session were spot-checked for #919, #894 and #832 only; re-derive the rest at draw time. The verifier-pipe-gate hook refuses any command where gz validate/check is not the last statement; capture to a file and read $? next.

## Decisions Made

- [operator-ruled] Proceed on the carried loops and the five insights (verbatim: 'deal with this').
- [operator-ruled] OBPI-0.37.0-04 line 64 gets a dated resolution note (verbatim: 'Dated resolution note (Recommended)').
- [operator-ruled] Docket start (verbatim: 'start the docket with the batch B questions now'), then 'yes', then 'continue with docket'.
- [operator-ruled] GHI #871: corrections to a Validated parent are exempt from strict ascending ADR order via a Magna Carta amendment (verbatim: 'Exempt corrections (Recommended)').
- [operator-ruled] GHI #837: match sibling 'next available feature slot' wording (verbatim: 'Match sibling wording (Recommended)').
- [operator-ruled] GHI #832: repair all 22 grandfathered release tags now (verbatim: 'Repair all 22 now (Recommended)').
- [operator-ruled] GHI #894: move _is_named to a neutral module (verbatim: 'Authorize the move (Recommended)') and amend OBPI-0.35.0-08's read-only declaration for that extraction only (verbatim: 'Amend the brief (Recommended)').
- [operator-ruled] GHI #921 and #922: hold, next OBPI in order (verbatim: 'Hold; next OBPI in order').
- [operator-ruled] GHI #611: apply corrections (b)(c), keep holding (a) (verbatim: 'Apply (b)(c), hold (a) (Recommended)').
- [operator-ruled] GHI #802: point gzkit.org at GitHub Pages and retire the VPS (verbatim: 'Point at Pages, retire VPS (Recommended)').
- [operator-ruled] GHI #803: measure the dead-link backlog, then couple gate to config (verbatim: 'Measure, then couple (Recommended)').
- [operator-ruled] GHI #808: add a declining debt target to the chore (verbatim: 'Add declining target (Recommended)').
- [operator-ruled] GHI #818: author a pool ADR for the Architectural Boundaries and close #818 superseded (verbatim: 'Pool ADR now (Recommended)').
- [operator-ruled] GHI #930: the corrective primitive gains latch-clearing for pipeline_launched (verbatim: 'Add latch-clearing (Recommended)').
- [operator-ruled] GHI #973: design a restore-row primitive under the #611 family (verbatim: 'Design under #611 family (Recommended)').
- [operator-ruled] GHI #950: wire task_id through the four constructors (verbatim: 'Wire task_id through (Recommended)').
- [operator-ruled] GHI #968: close, track the upstream harness request separately (verbatim: 'Close, track upstream separately (Recommended)').
- [operator-ruled] GHI #978: verbs for declare-section and remove-entry, prose for genesis-mint and re-point (verbatim: 'Split (Recommended)').
- [operator-ruled] GHI #939: retention scope folds into OBPI-0.35.0-10 (verbatim: 'Fold into OBPI-10 (Recommended)') and the pipeline skill text states the true Step 4b lane scope (verbatim: 'Correct the skill text (Recommended)').
- [operator-ruled] GHI #1011: restate the four CHORE.md files and retire validate-manpages into test-manpage-examples (verbatim: 'Restate prose; merge manpages (Recommended)').
- [operator-ruled] GHI #1014: fix closeout forward only; the 62 historical rows stay (verbatim: 'Fix forward only (Recommended)').
- [operator-ruled] GHI #1023: the BDD verb becomes a checklist item on the next feature ADR (verbatim: 'Checklist item, next ADR (Recommended)').
- [operator-ruled] GHI #1044: .gzkit/chores/ is canonical for chores (verbatim: '.gzkit/chores/ canonical (Recommended)').
- [operator-ruled] GHI #1124: gz tidy findings set the exit code (verbatim: 'Make findings gate (Recommended)').
- [operator-ruled] GHI #1063: promote the two measuring chores from propose to enforce (verbatim: 'Promote the two chores (Recommended)').
- [operator-ruled] GHI #1134: canonical states Draft/Ratified/Amended/Superseded (verbatim: 'Keep Amended (Recommended)') and the registry reads config.paths.constitutions (verbatim: 'Configured path (Recommended)').
- [agent-chose] Fixed disposition 2(a)(b) directly rather than filing GHIs for them; filed only 2(c) as #1148.

## Immediate Next Steps

1. Present the ruled-work queue so the operator picks what to draw; recommended order is smallest direct fixes first: GHI #837, #808, #1044, #1011, #939 skill text, #1124, #1134, #1014, #950, #894 with its OBPI-0.35.0-08 brief amendment.
2. On the operator's go, draw each through ghi-close one at a time, reading the ruling comment on the issue first, and git-sync after each landing.
3. On the operator's go, run the #611 (b)(c) ledger corrections with --dry-run first, then the #832 retag with a one-tag canary, then #803's measurement.
4. On the operator's go, author the Magna Carta amendment for #871, ADR-pool.architectural-boundaries for #818, and the chore rung promotions for #1063.
5. Remind the operator of their own step for #802 (GitHub Pages custom domain and DNS), and verify-then-close #927 and close #968 through ghi-close.

## Pending Work / Open Loops

- Design work under the #611 family: #930 latch-clearing and #973 restore-row primitive; route before building.
- Operator-initiated OBPI work: #978 two recovery verbs; #939 retention scope inside OBPI-0.35.0-10; #921 (OBPI-0.35.0-12) and #922 (OBPI-0.35.0-11) held in order; #1023 waits for the next feature ADR.
- Open GHIs filed this session: #1145, #1146, #1147 (ready for ghi-close), #1148 (blocked on ADR-0.40.0).
- Other 2026-09-28 insights not in scope this session: content import cycle, ledger CRLF on Windows, skill-alignment subcommand gap, land rollback prose, adversary-workspace Windows interpreter.
- ADR-0.35.0 at 9/14; OBPI-0.35.0-08 in progress with no lock; only the operator initiates the next OBPI.
- Still carried: GHI #1144 worker deadlock; the DDD-discipline R&D run; ADR-0.40.0 promote-versus-fresh with GHI #1131 first.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD (expect 0 0 after sync); git log --oneline -3 shows 05d1dda14 and 1e03fbe3c; gh issue view 837 --comments shows the 2026-09-28 ruling comment (repeat for any issue before drawing it); gh issue list --state open --search 'created:>=2026-09-28' lists #1145-#1148; uv run gz obpi lock list (expect no active locks); uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing reports 9/14.

## Evidence / Artifacts

- `.gzkit/handoffs/20260928T092244Z-session-end-obpi-07-landed.md` (resumed handoff)
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` (6.60.0, Stage 5)
- `.gzkit/skills/gz-rnd/SKILL.md` (0.4.0)
- `docs/governance/rnd-discipline.md`
- `docs/governance/agent-contract-rationale.md`
- `docs/rnd/design-amendment.md` (disposition row 2 discharge note)
- `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-04-transit-trailer-stamp.md`
- `.gzkit/insights/agent-insights.jsonl` (#968 upstream insight)

## Settled Rulings

1188 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
