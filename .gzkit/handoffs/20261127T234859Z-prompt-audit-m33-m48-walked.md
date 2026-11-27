---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-27T23:48:59Z'
agent: claude-code
session_id: cf1b98f7-fd89-4696-8078-829622fb6d09
continues_from: .gzkit/handoffs/20261127T114947Z-prompt-audit-m30-m32-drydock-screen.md
---

## Current State Summary

Resumed on 'resume from h/o'. Prompt-audit walk, rows M33 to M48, screened against CO-1 to CO-4 and the RP orders and walked one row at a time (operator course correction: "no, we do these one-by-one, when I agree to do otherwise?").

GHIs closed, each with a reviewer subagent's CONFIRMED verdict on the issue:
- #1403 (M33, gz-issue-file exit 2)
- #1404 (manpages filed parse errors under exit 1)
- #1405 (M34 and M45, the gz-mx floor and safe-mode trackability)
- #1406 (M36, gz-plan asks one question at a time)
- #1407 (M37, content pipeline cited terminal ADR-0.0.37 OBPIs; four review passes)
- #1408 (M38, content skills' runnable gz lines read uv run gz)
- #1410 (M44, canon pointed at package copies; six review passes, the whole population ruled line by line)
- #1411 (M46, the help-path lazy-import carve-out written; 25 CLI sites labelled or hoisted)
- #1413 (M48, the corpus attestation renamed where 17 surfaces said Gate 5; the scorecard-58b conflict was ruled by the operator)

Rows needing no GHI:
- M35 is carried by drydock U10/T10/W35.
- M47 is carried by the R&D's diamond 2. Under the operator's 'Restore dates + note', bca6a2104 restored last_reviewed on 26 skills that edits had moved since the 2026-11-25 review-only ruling.

Filed and left open:
- #1409 (M43): retire airlineops-parity-scan, gz parity check and its gz check step. Blocked until the safe-mode exit, because the floor forbids removing a control.
- #1412: the per-site PLC0415 reading for the rest of src/gzkit.

M49 was screened and put to the operator, who had not ruled when the session ended. Last action: this handoff, then git-sync.

## Important Context

Safe mode is still open (docs/governance/harbor-pilotage-candidate-2026-10-15.md). Every act is one commit with a Task: trailer, and the ledger is written only through gz verbs. The floor never drops, and it includes no removal of a control.

Method learned this session (insights recorded):
- Read an owner-of-record OBPI's state from gz obpi status or the ledger, never from its brief's status line. OBPI-0.35.0-09 is REPUDIATED, not Active.
- Before a wording repair, ask whether the surface should exist at all (M43).
- Sweep the whole population first, then rule line by line. Keyword sweeps missed members repeatedly on #1407 and #1410.
- An exclusion that rests on a runtime claim must cite the code that makes it true. load_template reads .gzkit/templates first.
- A rule-version bump needs its Coverage Ledger row in docs/governance/advisory-rules-audit.md re-scored and set. Run tests.governance.test_advisory_scorecard_coverage, which the commit hooks do not run.
- last_reviewed moves only on a gz-skill-review pass. Edits bump skill-version alone until diamond 2 rewrites skill-surface-sync.md rule 6.

Screening note: the earlier bulk screen marked M44 and M47 carried. Re-screened row by row, M44 was a live defect and M47 was carried by the R&D rather than the drydock. Re-screen every row marked carried before noting it.

The gh-cli allowed list has no label edit. #1410 lacks the runtime label, which is disclosed in its close.

## Decisions Made

- [operator-ruled] Screen M33 to M51 against the change orders before filing (verbatim: 'yes: "Should I go ahead with that check of M33–M51?"').
- [operator-ruled] Walk the rows one at a time, never as a batch unless agreed (verbatim: "no, we do these one-by-one, when I agree to do otherwise?").
- [operator-ruled] M33: GHI and direct repair, OBPI-0.0.23-04 owner of record (verbatim: "a").
- [operator-ruled] The manpage flag-conflict defect is filed as its own GHI and fixed now (verbatim: "a").
- [operator-ruled] M34 and M45: one GHI repairing the gz-mx skill, the gz mx help and its manpage (verbatim: "a").
- [operator-ruled] M35 is carried by drydock U10 under T10/W35; no GHI (verbatim: "a").
- [operator-ruled] M36: one GHI repairing gz-plan Step 4; S-F2 is carried by H8 (verbatim: "A").
- [operator-ruled] M37: one GHI, direct repair of the content-pipeline citations (verbatim: "A").
- [operator-ruled] M38: one GHI, direct fix; the operator confirmed the route is a direct fix (verbatim: "A (this is very janky, wasn't 0.35.0-09 closed as completed?) are we direct fixing?").
- [operator-ruled] Keeping an AirlineOps skill in gzkit is a mistake (verbatim: "we haven't touched airlineops meaningfully in 8 months, I question this other than giving airlineops the ability to look at the two. Keeping an \"AirlineOps\" skill in gzkit is a mistake.").
- [operator-ruled] The AirlineOps retirement is one GHI held open until the safe-mode exit; M43 and B17 are superseded (verbatim: "A").
- [operator-ruled] M44: one GHI, direct fix pointing canon at .gzkit/templates (verbatim: "A").
- [operator-ruled] M46: one GHI for the rule and the CLI sites, plus a GHI tracking the remaining per-site reading (verbatim: "A").
- [operator-ruled] M47: carried by diamond 2; restore last_reviewed on all 26 skills edits moved after the review-only ruling (verbatim: "A").
- [operator-ruled] M48: one GHI renaming the corpus attestation at every site (verbatim: "A").
- [operator-ruled] The advisor-QC receipt is cited in the corpus attestation, not at Gate 5; scorecard row 58b is amended (verbatim: "A").
- [operator-ruled] Write a fresh handoff and git-sync (verbatim: "write fresh handoff and git sync").
- [agent-chose] Widened closure contracts on recorded review evidence rather than filing sibling GHIs (#1404, #1407, #1410, #1413), per ghi-close's bounded-contract rule.
- [agent-chose] Left the "Era 1 — today" rows and specify_cmd.py:342 for the operator, because which era is current is a doctrine statement.

## Immediate Next Steps

1. Give the operator the strategic, operational and tactical brief, short, vital facts first.
2. Put M49 back to the operator. Options: A, rewrite the 10 'Carried verbatim from root AGENTS.md' lines; B, record M49 as no defect (true dated provenance). The recommendation is B.
3. Walk M50 and M51 one row at a time. Re-screen M50 before calling it carried: earlier carried verdicts were wrong for M44 and M47.
4. Put the era question to the operator: two doctrine docs label Era 1 'today' although corpus playback has landed (insight of 2026-11-27, with specify_cmd.py:342).
5. Then the R&D's T37 and its sub-ids, W44 to W50, the open frontier, the disposition map, review.md and sign-off, as the predecessor advised.

## Pending Work / Open Loops

- M49 has been put to the operator, with no ruling yet. M50 and M51 have not been walked.
- #1409 is open and blocked until the safe-mode exit: retire airlineops-parity-scan, gz parity check and its gz check step. It absorbs #1234 when it lands.
- #1412 is open: the per-site reading of 544 bare noqa and 2556 held PLC0415 sites.
- Insights recorded, not yet routed:
  - the dead anchor in arb-middleware.md;
  - gz task start ignoring --seq beside a task_id;
  - the era tables and specify_cmd.py:342;
  - two more method insights.
- Scorecard row 33c and skill-surface-sync.md rule 6 wait for diamond 2 (operator: 'Restore dates + note').
- The batch-run import error 'tests.arb.test_step_reporter tests' appears when several modules run in one unittest command. It reproduces on the stashed tree, and the module passes alone; the cause is undiagnosed.
- The orientation's injected text is 4851 B against its 4000 B budget.
- #1357 (M1) is still open.

## Verification Checklist

- gh issue view 1403 1404 1405 1406 1407 1408 1410 1411 1413 --json state: all CLOSED, each with a CONFIRMED review comment.
- gh issue view 1409 1412: OPEN.
- uv run gz handoff rulings --search "Third carve-out": settled.
- uv run python -m unittest tests.governance.test_advisory_scorecard_coverage tests.governance.test_promoted_advisory_audits tests.cli.test_help_path_imports: OK.
- uv run gz skill audit: 0 blocking.
- uv run gz validate --surfaces --cli-alignment --distribution --chores-layout --bullet-retention: passes.
- git log 679589695..HEAD: the session's commits, all with Task: trailers.

## Evidence / Artifacts

- `docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md` (the walk's map, rows M33 to M51)
- `docs/governance/harbor-classic-adr-change-order.md` (CO-1 and its held rulings H7 and H8)
- `docs/governance/drydock-taxonomy.md` (U10, T10 and W35)
- `.gzkit/rules/pythonic.md` (0.8.1, the help-path carve-out)
- `.gzkit/rules/cli.md` (0.9.5)
- `docs/governance/advisory-rules-audit.md` (rows 23, 58b, 82 and the Coverage Ledger)
- `.gzkit/skills/gz-adr-create/SKILL.md`
- `.gzkit/chores/README.md`
- `src/gzkit/commands/content/advise_rendition.py`
- `src/gzkit/cli/main.py`
- `.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

2653 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
