---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-27T23:47:48Z'
agent: claude-code
session_id: f2ee5b4e-8f77-4953-859a-f86517090abf
continues_from: .gzkit/handoffs/20260727T124456Z-ghi-724-725-726-fixed-deferrals-discharged.md
---

## Current State Summary

Off-cycle session, no parent ADR, no OBPI lock. Two units of work: the
operator's git-sync, then a review of the resumed handoff as an artifact.

The git-sync ran clean. HEAD `d2c4213e1`, tree clean and level with origin. Its only
content was the ledger event the `gz handoff authorize` verb itself writes, which is the
bootstrap condition GHI #720 fixed.

The review ran the resumed handoff's own twelve-item Verification Checklist. All twelve
passed, including the split-stream behave check it flagged as its own trap: exit 0, zero
bytes on stderr. Eleven of its twelve claims verified against Layer-2.

One claim is FALSE. The handoff asserted the four shattered Settled Rulings were
"knowingly-unrecoverable pre-fix damage", and rested an `[agent-chose]` decision not to
file a GHI on that premise. A predecessor in its own chain says verbatim that both are
recoverable from `20260725T110348Z`, and the full text of all four is intact there. All
four are reseated in this handoff via `--settled`.

## Important Context

FIRST, and the reason this mattered rather than being cosmetic: the worst
fragment is a semantic inversion, not a truncation. "Dimension-aware Draft scoping: a
Draft brief does NOT gate on its own" drops the clause "but DOES still gate on
prerequisites". The carried form reads as Draft briefs not gating at all, which is the
opposite of half the ruling, and it propagated through twelve handoffs. Second-worst drops
"Implementation is preserved but not landed, because measurement afterwards showed it does
not by itself reach a green gate" -- so the fragment reads as a directive to build exactly
what the full ruling records as measured-insufficient.

SECOND, why dedup could never have caught these. `_ruling_key` folds only quote glyphs,
whitespace and case. A fragment dedups against its full twin only when BOTH are in the
carried set; here the full text lives upstream of where truncation occurred, so the
fragments entered the chain with no twin. They are orphans, not duplicates -- which is
precisely why the six visible duplicate pairs got flagged and these four did not.

THIRD, and the direct consequence of the route chosen: seating the full text does NOT
retire the fragment. Both now appear in the carried set. That is the documented deliberate
asymmetry in `_ruling_key` (`e84e6a85b`: a visible duplicate is harmless, while collapsing
two genuinely distinct rulings drops a booked operator ruling silently). The full text is
authoritative and sits adjacent to its fragment. Retiring the fragments needs its own
ruling and has no channel today.

FOURTH, the parser defect itself is FIXED and this is pure residue. `e84e6a85b` requires an
indented continuation line, so no newly authored wrapped ruling shatters. But residue in an
append-only carry-forward chain is self-perpetuating: every future handoff re-copies it
until something is seated over the top of it.

FIFTH, corpus scale is now the live structural question. The carried set stood at 65
rulings with six duplicate pairs before this session, growing about two per session.
`gz-session-handoff` SKILL.md names the threshold itself: routine `--settled` use signals
that rulings belong in a durable ruling store, campaign Movement D box 3. This session used
the flag four times in one sitting.

## Decisions Made

- [operator-ruled] Seat the four recovered rulings via `--settled` on the
  next handoff, chosen from four presented routes (verbatim: selection of "Seat via
  --settled next handoff"). Filing a GHI first, direct repair of the committed artifact,
  and review-only were all declined.
- [operator-ruled] Run the git-sync (verbatim: "/git-sync"; booked via `gz handoff
  authorize`, session f2ee5b4e). A git-sync is always authorized per standing canon; no
  other advised step of the resumed handoff was authorized, and none was worked.
- [agent-chose] Tested the handoff's "unrecoverable" claim rather than relaying it. The
  Claim Verification Gate requires checking assertions against Layer-2, and an
  `[agent-chose]` decision resting on an untested premise is the exact shape that gate
  exists to catch.
- [agent-chose] Wrote this handoff in the same turn as the ruling rather than recording the
  route for a later session. The chosen route names the next handoff as the seat, so
  recording the intent and stopping would have left the finding with no durable home --
  the ruling store the skill points at is unbuilt.
- [agent-chose] Did NOT widen `_ruling_key` to collapse the fragments against their
  restored full texts. That is the change `e84e6a85b` deliberately declined, and the same
  similarity threshold that would collapse these four also erases the two genuinely
  distinct "Book the patch release" rulings.

## Immediate Next Steps

1. NOTHING BEYOND THIS HANDOFF IS AUTHORIZED. The git-sync and the
   reseating are done and pushed; every step below needs an explicit operator ruling first.
2. Rule on whether the four superseded fragments should be retired from the carried set.
   Seating the full text left them coexisting by design; retiring them means either
   widening `_ruling_key` (which `e84e6a85b` deliberately declined) or building an explicit
   suppression channel, which does not exist today.
3. The carried chain, unworked and still live: GHI #719 (pool interview JSON unschema'd,
   direction (b) -- a `gz plan create` path taking an interview file, and/or a
   pool-interview schema with a validate scope).
4. Campaign Movement A remains topmost absent a ruling:
   `ADR-0.35.0-canon-entry-corpus-landing` at 0/9, and the `ADR-0.34.0-foundation-sunset`
   capstone at 2/5 including wiring the permanent `--taxonomy` gate into `gz check`,
   currently red with 74 foundation grandfather errors.
5. Promotion of the two pool ADRs when wanted: assign SemVer ids, and for
   `ADR-pool.worktree-parallel-agents` ratify the ephemeral-worktree doctrine carve-out
   FIRST -- that is a hard promotion gate.

## Pending Work / Open Loops

GHI #719 OPEN and unworked -- the deferred direction-(b) capability from #718.

13 GHIs open, unchanged by this session. No GHI was filed or closed here.

FOUR SUPERSEDED FRAGMENTS now coexist with their restored full texts in the carried set.
This is by design, not an oversight, and it is not a thing to quietly clean up: advised
step 2 above is the ruling it needs.

THE DURABLE RULING STORE named by `gz-session-handoff` SKILL.md (campaign Movement D box 3)
remains unbuilt, and the carried set keeps growing.

NO OBPI LOCK HELD, no in-flight pipeline, nothing carried-and-unstarted from an authorized
queue.

SPEC-TEST DRIFT ADVISORY unchanged by this session; no source or test file was modified.

## Verification Checklist

git status --short --branch (clean, level with origin/main);
git log --oneline -3 (expect this handoff's commit, then d2c4213e1, 8a0171feb);
uv run gz handoff resume (expect this handoff, staleness Fresh, settled count 74 -- the
65 carried, plus the predecessor's 5 promoted operator rulings, plus the 4 seated here);
uv run gz obpi lock list (expect no active locks);
gh issue view 719 --json state (expect OPEN -- the carried item);
uv run gz smoke (expect exit 0, 2 tests, well under the 60s budget);
uv run gz validate --qc-binding (expect "No QC theater detected");
uv run gz cli audit (expect 132/132 fully covered).

To confirm the reseating rather than trusting this document, read the Settled Rulings
section of this file and find the Draft-scoping ruling there TWICE: once as the surviving
fragment, which stops dead at "on its own", and once as the restored full text, which runs
through the prerequisites clause and ends "Landed as 5111b7dd." If only the truncated form
is present the seating failed, and that fragment alone is the inversion this session
repaired. The same doubled shape holds for the other three reseated rulings.

Assert on that structure, NOT on a whole-file occurrence count. A count is self-referential
here -- this checklist names the ruling too, so every restatement of the count changes the
answer it is checking. Two drafts of this handoff were discarded to that trap before the
check was re-anchored on structure.

Do NOT pipe any of the verifiers above through tail or grep: the shell reports the
filter's exit, not the verifier's (`.gzkit/rules/tests.md` § Verification exit-code
integrity). Capture to a file and read the file. Counting occurrences inside a document is
a document read, not a verifier exit, and is safe.

## Evidence / Artifacts

Reviewed artifact:
`.gzkit/handoffs/20260727T124456Z-ghi-724-725-726-fixed-deferrals-discharged.md`.

Recovery source for all four reseated rulings, full text intact at lines 76-88:
`.gzkit/handoffs/20260725T110348Z-ghi-615-three-cuts-migration-held.md`.

The predecessor that recorded the recoverability the reviewed handoff denied, at line 61:
`.gzkit/handoffs/20260726T091905Z-ghi-615-schema-enforced-641-scoped.md`.

Dedup and composition logic read this session: `src/gzkit/handoff_api.py`.

The parser fix whose residue this session cleaned, and whose declined change is cited
above: commit `e84e6a85b`.

Session commit: `d2c4213e1` (git-sync; ledger event only).

No source or test files were modified this session.

## Settled Rulings

- Work the degrading tier starting with #696 (verbatim authorization booked via gz handoff authorize, session 81765765).
- Finish what is on the plate rather than deferring items for later sequencing rulings.
- Do not assert campaign-movement intent without reading it; the claim that Movement C is shrinking the pre-1.0 board was fabricated and is withdrawn. Movement C is Reduce the accretion.
- #696 defect 2 was the buildable cut; defects 3/4 were NOT to be left to an unbuilt ADR.
- Reframe #580 from periphery criticality to truncation survival (operator verbatim 2026-07-25: 'reframe #580 to truncation survival'). The mechanism is unchanged; the warrant and ranking source are replaced. Arrived AFTER the prior handoff was written and was carried by neither its Decisions nor its Settled section.
- #580's survival declaration is ratified with must-survive = ranks 1-11 (operator-doctrine-verbatim-canon first, architectural-boundaries last), cumulative 21582 B, leaving 11186 B of growth headroom. Ranks 12-20 are declared expendable-under-pressure because they are recoverable, not because they are unimportant. Ratified as data only: applying the order to committed AGENTS.md remains a Layer-1 canon change requiring Gate-5 attestation.
- #580's destination is SPLIT, not a single home. The witness half (declaration plus the assertion that every must-survive section begins before the vendor cap, plus fail-closed declaration completeness) lands with GHI #712. The reorder half (permuting the surface) parks to pool post-1.0, because only it is expensive and it pays off only once the cap binds. This supersedes the withdrawn whole-issue pool recommendation, which rested on a false claim about Movement C.
- GHI #607 is UNPARKED. Attested REQ-0.14.0-04-04 asserts a detection capability and is silent on scope, so an adopter-scope predicate that preserves gzkit's own self-enforcement does not falsify it. No repudiation and no amendment are required to work the issue.
- Work advised steps 1 through 4 (verbatim authorization "do 1 to 4", booked via gz handoff authorize, session 8b138d99).
- Mechanize GHI-blocker freshness by extending the bundled triage script rather than adding a gz verb, so the signal lands in the report the operator already reads before pulling work.
- Work GHI #712 (operator verbatim 2026-07-25: 'authorized, proceed with GHI #712'; booked via gz handoff authorize, session bb837938). This authorized the resumed handoff's advised step 1 only; steps 2 through 5 were not authorized and were not worked.
- Fix the gz check advisory-visibility defect, and file it as a GHI first (operator verbatim 2026-07-25: 'yes, fix this defect'). The defect was surfaced for routing rather than fixed unilaterally because it changes a shared renderer's output contract for every step; the operator's ruling converted it into authorized work.
- Fix the gz check advisory-visibility defect, and file it as a GHI first (operator verbatim 2026-07-25: 'yes, fix this defect'). It had been surfaced for routing rather than fixed unilaterally because it changes a shared renderer's output contract for every step.
- Fix the settled-ruling dedup defect, then author a fresh handoff (operator verbatim 2026-07-25: 'fix, then write me a fresh handoff'). It had been surfaced with routing facts rather than fixed, because 'write handoff' is a narrow skill scope and Always #17 forbids launching unrequested implementation work off the back of one.
- Fix the CI failure (operator verbatim 2026-07-25: "fix this:"; booked via gz handoff authorize, session bd43ecd7). This authorized the CI repair only; the resumed handoff's five advised steps were not authorized and were not worked.
- Write the entire triage into a new handoff for context cleanup (operator verbatim 2026-07-25: "write entire triage to new handoff, i want to clean up").
- Work the triage list in its ranked order (operator verbatim 2026-07-25:
- Proceed with GHI #615 cuts 2 and 3 (migration plus strict enforcement)
- Escalation should key on lifecycle rather than on frontmatter shape
- Dimension-aware Draft scoping: a Draft brief does NOT gate on its own
- Book the patch release as the session's work and leave the resumed handoff's five advised steps unauthorized (operator verbatim 2026-07-25: "/gz-patch-release"; booked via gz handoff authorize, session e6b3da00). GHI #615's held migration was NOT authorized and was not worked.
- Backfill the runtime label on #532 and #682 only, not on #533 or #710 (Step 1a labeling-recovery). Both landed genuine validator changes under gz validate; #533 is an open tracker with markdown-only commits and #710 was a skill-doc change, so the excluded bucket is correct for them per Step 1a's own guidance.
- Describe only what actually landed for the open GHIs in the narrative, omit #533 entirely, and file a GHI against the closure-marker heuristic after the release completed rather than pausing the ceremony.
- Approve the drafted release notes as written (operator verbatim: "yes"), triggering the Iron Law run of Steps 4a-4e without pauses.
- Fix GHI #714 via Direction 2 -- keep the commit marker authoritative for discovery, consult upstream state one layer down, and downgrade a still-OPEN GHI to a warned bucket the operator adjudicates (operator verbatim: "direction 2"). Directions 1 and 3 were declined.
- Deferring a proven defect with a governance-flavored rationale is not acceptable (operator verbatim 2026-07-25: "slop, bullshit, facade, and wank"). The turn-closing "one thing worth your judgment" note on the git-sync gate gap was rejected as rationalized incompleteness; the correction produced the hook-enforcement investigation, its two commits, and GHI #715. Recorded as an improvement insight per Behavior Rule 11.
- Work GHI #715 and correct campaign line 131 (operator verbatim 2026-07-25: "#715 + campaign line 131"; booked via `gz handoff authorize`, session e4c56baa). This authorized the resumed handoff's advised steps 1 and 2 only; steps 3, 4, and 5 were not authorized at that point.
- Route GHI #615's residual findings by mechanical re-triage into three classes, file a GHI for the scenario-reachability advisory, and confirm the brief_reconcile landing order (operator verbatim 2026-07-25: "Mechanical re-triage into 3 classes; File a GHI; #615 -> #581 -> #641"; booked via `gz handoff authorize`). Routes (i), (ii), and (iii) were declined; building the scenario registry now and accepting Era-1 as permanent were declined; landing #641 first was declined.
- Book the patch release as this session's work and leave the resumed handoff's five advised steps unauthorized (operator verbatim 2026-07-25: "/gz-patch-release"; booked via `gz handoff authorize`, session bfc3ccad). GHI #716, #615 cuts 2 and 3, #581, and #641 were NOT authorized and were not worked.
- Fix the CI failure, diagnosed by the operator from the job log as blocking skill-audit staleness rather than a code runtime defect (operator verbatim 2026-07-25: "fix:"). This authorized the skill-audit repair only.
- Approve the v0.33.3 release narrative as drafted and execute it (operator verbatim 2026-07-25: "yes, appprove the patch release narrative - do the work"), triggering the Iron Law run of Steps 4a through 4e without pauses.
- Decline the near-edge staleness sweep and record it in a handoff instead (operator verbatim 2026-07-25: "no, but place it into a handoff and then git-sync the handoff").
- Authorize the git-sync only, before any handoff steps were worked (operator verbatim 2026-07-25: "authorized, git-sync only"; booked via `gz handoff authorize`, session a76662eb). The stale-pinned handoff's five advised steps were NOT authorized at that point and were not worked.
- Work advised steps 1 through 5 of the current handoff (operator verbatim 2026-07-25: "do these:" followed by the five steps; booked via `gz handoff authorize`). Steps 1 through 3 were completed; 4 and 5 were not started.
- Resolve the skill-version pin collision by asserting the increment rather than the literal, chosen over updating the four frozen constants and over reverting the stamps. The equality pins contradicted REQ-0.0.35-02-04's own wording.
- Add a fixed 75-day non-blocking warn band, chosen over deriving the band from the ceiling and over leaving the gate binary.
- Retire ADR-0.0.33 Invariant 4 rather than build the scenario registry; GHI #716 closed withdrawn against the retirement commit.
- Fix the handoff evidence check's category error when the pre-push gate blocked the retirement, chosen over annotating the two sealed handoffs and over reverting the retirement.
- Work all four authorized buckets (operator verbatim 2026-07-26, booked via `gz handoff authorize`, session 7dd80db9): "GHI #615 cuts 2 and 3, Then #581, then #641, Steps 3 and 4 (the two cheap judgments), Fix the two handoff-surface defects".
- Fix the engine first, then repair genuine drift — chosen over rewriting 22 briefs to satisfy the scrapers as written, and over landing the extractor fixes as a separate prior commit.
- Seal the 8 pre-frontmatter ADR-0.0.1 briefs as `archived` rather than `Completed` — an honest claim that they are no longer a live authoring surface, without asserting a ledger completion they do not carry.
- Scope GHI #581 first and do NOT build — chosen over executing the 6-registry collapse, over building the 6th validator dimension, and over closing the issue unexamined.
- Take GHI #641's own strawman naming: `gz brief reconcile` becomes `gz obpi brief-drift`, `gz obpi reconcile` becomes `gz obpi sync`, and the single-verb `brief` namespace goes away.
- Fix the engine first, then repair genuine drift — chosen over rewriting 22 briefs to satisfy the scrapers as written.
- Seal the 8 pre-frontmatter ADR-0.0.1 briefs as `archived` rather than `Completed` — no ledger completion is asserted.
- Scope GHI #581 first and do NOT build — chosen over executing the collapse, over building the 6th validator dimension, and over closing it unexamined.
- Take GHI #641's own strawman naming, then execute it (operator verbatim 2026-07-26: "refresh it" followed the landing; the rename itself was authorized by the strawman ruling and the follow-up "okay, so what about 641?").
- Work GHI buckets 1, 3, 4, and 5; decline bucket 2 (the Movement A campaign work).
- Retire .gzkit/schemas/ledger_events.json by forward supersession and keep the file.
- Write two pool ADRs (substrate + capability) crediting swarm-forge + superpowers (verbatim: "authorized -- write the two pool ADRs"; booked via gz handoff authorize, session 786a9e8f).
- Primary use case = parallel read-only review personas; parallelism itself "isn't too important"; record the alternatives (parallel OBPI impl / GHI fixes / ADR pipelines) as future scope.
- Allow ephemeral worktrees (scratch checkouts, land on main, no branch dance) -- a carve-out from "never create feature branches"; ratifying it is a hard promotion gate for ADR-pool.worktree-parallel-agents.
- Ledger concurrency = single-writer-by-construction (only merge-to-main writes Layer-2), NOT a daemon.
- Two pool ADRs (substrate + capability), not one combined nor three.
- Use the governed skill, not hand-scaffolding ("there is an adr authoring skill don't vibe"; "use skills - skills have rules + tools"). Recorded as an improvement insight.
- Fix GHI #718 via direction (a), the skill-doc fix (chosen via AskUserQuestion).
- File the #718 follow-on via /ghi-author (became GHI #719).
- A git-sync is ALWAYS authorized and never gated on a handoff (operator verbatim 2026-07-26: "yes, just do my git-sync - a git-sync will ALWAYS be authorized - think about it, if we need to sync with remote, your local handoff is almost always likely to have been superseded by something on remote. Challenging me on a handoff for a git-sync is silly."). Booked via `gz handoff authorize` against both the gating handoff and, after the pull replaced it, its successor. Borne out mechanically in-session: the 24 pulled commits had already landed all five advised steps of the handoff being gated on.
- Add the local `user.name = g0` guard (operator verbatim 2026-07-26: "yes, do the user.name = g0 guard.").
- Fix GHI #720 with the recompute approach rather than reordering the ceremony to pull before committing (operator verbatim 2026-07-26: "fix #720 with the recompute").
- Fix GHI #722 by failing closed at authoring rather than widening the parser (operator verbatim 2026-07-26: "fix #722 by failing closed at authoring"). Direction (a), widening `_section_items`, was declined.
- Write this successor handoff rather than leave the stale claim standing (operator verbatim 2026-07-26: "yes, write the successor handoff").
- Fix GHI #723 with the buffer flag (operator verbatim 2026-07-26: "fix #723 with the buffer flag").
- File the smoke-budget breach as a GHI (operator verbatim 2026-07-26: "file the smoke budget GHI"), which became #724.
- Write this successor handoff (operator verbatim 2026-07-26: "write the successor handoff").
- Sync first, then re-present, before working any advised step (verbatim 2026-07-27: "Sync first, then re-present"; booked via `gz handoff authorize`).
- Comment the measured blast radius on #717 and file the two genuinely untracked findings, after Step-0 prior art voided the originally-recommended GHI (verbatim: "Comment on #717 + file the two trackers").
- Fix GHI #724, #725 and #726 (verbatim: "fix 724, 725, and 726").
- Directions, chosen from bounded options: #724 direction (a) build the smoke tier; #725 direction (4) fail-closed assertion; #726 direction (b) silence at the fixtures.
- Discharge the three items left undone rather than narrating them (verbatim: "fix:" quoting the turn-closing deferral paragraph). Recorded as an improvement insight per Behavior Rule 11.
- Work the triage list in its ranked order (operator verbatim 2026-07-25: "continue on the triage list"; booked via `gz handoff authorize`, session 6aa88bcf). This resolved the predecessor handoff's advised step 1 by ruling the pull order to be the ranking already recorded in `.gzkit/cache/triage/rank.json`, which puts GHI #615 first.
- Proceed with GHI #615 cuts 2 and 3 (migration plus strict enforcement) rather than sampling first or switching to GHI #607.
- Escalation should key on lifecycle rather than on frontmatter shape (operator selected the recommended option after the three dispositions were presented). Implementation is preserved but not landed, because measurement afterwards showed it does not by itself reach a green gate.
- Dimension-aware Draft scoping: a Draft brief does NOT gate on its own deliverables (allowlist existence, `gz` verb resolution) but DOES still gate on prerequisites (Discovery Checklist, citations). Landed as 5111b7dd.
