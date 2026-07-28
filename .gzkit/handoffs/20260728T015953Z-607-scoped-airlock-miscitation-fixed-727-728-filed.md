---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-28T01:59:53Z'
agent: claude-code
session_id: f2ee5b4e-8f77-4953-859a-f86517090abf
continues_from: .gzkit/handoffs/20260728T002306Z-triage-board-captured-607-investigated.md
---

## Current State Summary

Three fixes landed, two GHIs filed, one defect self-inflicted and corrected.
Deck ended at 13, exactly where it started: #607 and #644 closed, #727 and #728 filed.

`486cfd8af` fixed GHI #607 by SCOPING `audit_code_contract_mismatches` to `src/gzkit`,
not by deleting it. Deletion was proposed, authorised by the operator, and then WITHDRAWN
on reading the REQ: the function is bound by name to attested REQ-0.14.0-04-04 in the
OBPI-0.14.0-04 audit ledger, so removing it would have falsified attested canon.

`8d6c25fbc` fixed a doctrine mis-citation across seven surfaces. All of them cited
ADR-0.33.0 § Consequences Negative #5 as authority for the airlock never blocking. That
clause says nothing of the kind -- it governs refusal LEGIBILITY. The real authority is
§ Calibration frontier, which is explicitly staged.

`f8ce93dee` corrected a false claim I had committed an hour earlier: the chore authored
this session asserts it is project-local and never ships, and sync propagated it into the
wheel immediately. Filed as GHI #728.

No ADR or OBPI work. Campaign sequencing UNCHANGED by operator ruling.

## Important Context

FIRST, the recurring method failure, stated plainly because it happened THREE
times in one session and is the most reusable thing here: I asserted properties without
verifying that any mechanism delivers them. A GHI body's measured state (stale by 32 days),
a doctrine's scope (STDLIB-FIRST read as stdlib-only), and a chore's project-local-ness
(no affordance exists) -- each was relayed as fact, each was wrong, each was caught by
reading rather than reasoning. Two `improvement` insights are recorded. The operative
correction: front-load blast radius ONCE before proposing anything, and never emit
AskUserQuestion options derived from an unread surface -- bounded-choice framing presented
as operator economy is guessing with better UI.

SECOND, why GHI #607 was scoped rather than deleted, which is the load-bearing governance
fact of this segment. REQ-0.14.0-04-04 is attested (human, "attest completed", 2026-03-16)
and the OBPI-0.14.0-04 audit ledger binds it to the function BY NAME:
`"audit_code_contract_mismatches() flags 9 dataclass violations"`. The settled unpark
ruling had already anticipated the correct move -- the REQ "asserts a detection capability
and is silent on scope, so an adopter-scope predicate that preserves gzkit's own
self-enforcement does not falsify it". A prior session (handoff `20260724T114926Z`) had
mapped this identical landmine and corrected the identical "direct-fix-sized" estimate.
Deletion was withdrawn only because prior art was grepped. Do NOT re-propose deletion.

THIRD, the operator's doctrine ruling, which must not be re-litigated: `.gzkit/rules/
models.md` TEXT IS FINE and was not touched. STDLIB-FIRST is gzkit's principle and gzkit's
CONSTRAINT -- "STDLIB first != STDLIB only". A named departure licenses the third-party
path where its rationale holds; it does not forbid the stdlib default elsewhere, and a
strong preference stated as gzkit-scoped guidance is what a principle does. The defects
were the mechanization and the export, never the doctrine wording.

FOURTH, the airlock investigation, which the operator asked for and which stands
independent of any work: ADR-0.33.0 is COMPLETE AS SCOPED and INCOMPLETE AS INTENDED. All
6 OBPIs `Completed`, `status: Validated`, attested 2026-07-12 -- there is no unfinished
OBPI to resume. The gap has no artifact at all. Three verified reasons it "feels
incomplete": (a) production reach for an OBPI id yields an EMPTY seam-map, so a real entry
always PROCEEDs (ADR § Calibration frontier, operator-attested 2026-07-10, naming
calibration "a named successor increment"); (b) `gz mx` passes `lambda _node: []` as its
reach in production, so that door structurally cannot produce a seam; (c) automatic
invocation exists ONLY inside `gz obpi pipeline` and `gz mx` -- zero references in
AGENTS.md, any rule, any hook, pre-commit, or CI. The declared end state BLOCKS
(§ BI-4: "an un-accounted seam makes GO structurally unreachable").

FIFTH, the mis-citation mattered precisely because it made that gap look intentional. The
CLI help, manpage, and skill all read as "the gate is DESIGNED never to bite", which
inverts the ADR's intent. It misled THIS session into reporting to the operator that
diagnostic-only was by design. Verbatim, § Negative #5: "Operational (2am): a NO-GO the
operator cannot diagnose. Mitigation: the refusal names the exact un-accounted seam +
provenance + a one-command re-sense -- never a 2am hard wall." That is about an
UNDIAGNOSABLE wall. The correct citation for the current posture is § Calibration frontier.

SIXTH, GHI #728 is GHI #607's class arriving in a third surface within the same session.
A chore authored only under `.gzkit/chores/` is propagated to `src/gzkit/chores/` by sync
and scaffolded into adopters by `gz init`. `.gzkit/rules/chores.md` § Two-Surface Layout
marks the project overlay "Shipped in wheel? No" -- so the rule loaded on chores work
states the property the code does not honour. The classifier already proves the mechanism
is available: `proofs/` stays out of the wheel via the `runtime_state` class. What is
missing is a class meaning "canonical for this project only."

SEVENTH, an unresolved anomaly worth a fresh pair of eyes: the campaign cites "23
`airlock_in` vs 10 `airlock_out`" as of 2026-07-18; counting the ledger today yields 20
and 5. Counts going DOWN on an append-only ledger should be impossible. Not investigated.

## Decisions Made

- [operator-ruled] `models.md` text is fine and must not be rewritten; fix
  the mechanization and the export only (verbatim 2026-07-28: "the text is fine, fix the
  mechanization and the export"). A prior plan to re-scope the doctrine wording was
  withdrawn.
- [operator-ruled] STDLIB-FIRST is gzkit's constraint and a principle, not a bright line
  (verbatim: "STDLIB first != STDLIB only, I am getting tired of tripping up on this" and
  "STDLIB FIRST is gzkit's constraint and it is a principle").
- [operator-ruled] Take the #607 fix now and file the architecture work as its own GHI
  (verbatim: "take the #607 deletion now and file the architecture work as its own GHI").
  The deletion half was substituted for scoping after the attested-REQ binding was found;
  the operator confirmed the substitution (verbatim: "yes, confirm").
- [operator-ruled] Keep campaign sequencing as is (verbatim: "keep sequencing as is").
  Movement A remains topmost; Movement B (airlock on the real doors) is NOT pulled forward
  despite the airlock findings. This is a live ruling against acting on the investigation.
- [operator-ruled] Direct-fix the airlock mis-citation (verbatim: "yes, direct fix
  mis-citation"). No GHI filed -- filing one to construct a trailer anchor is the
  moratorium violation named in `.gzkit/rules/task-discovery.md`.
- [operator-ruled] Correct the chore's false text and file the gap behind it (verbatim:
  selection of "Correct the text, file the gap"). Building the affordance now, deleting the
  chore, and letting it ship uncorrected were all declined.
- [agent-chose] Withdrew the deletion AFTER the operator had authorised it, rather than
  executing an instruction that would falsify attested canon. Surfaced the REQ text and the
  prior-session landmine, then proposed the substitution.
- [agent-chose] Fixed the mis-citation as a CLASS across seven surfaces rather than the
  three originally reported, and deliberately RETAINED the one correct citation
  (`airlock/enter.py:192`, "never a bare denial") -- that is what § Negative #5 actually
  says.
- [agent-chose] Verified class coverage for #607 by sweeping every audit for an unscoped
  root before claiming it in the close comment. `audit_code_contract_mismatches` was the
  only one; the remaining `project_root/"src"` hits are `sys.path` setup and brief-citation
  resolution, which enforce nothing.
- [agent-chose] Delegated the ADR-0.33.0 read to a subagent with an explicit demand for
  verbatim quotes, then re-verified the load-bearing claims (§ Negative #5 text, the
  calibration-frontier note, the ledger counts) directly before relaying any of them.
- [agent-chose] Corrected the chore's false claim in place with an explicit note that it
  was false, rather than silently rewriting it.

## Immediate Next Steps

1. NOTHING IS AUTHORIZED. All work this segment is committed, gated, and
   pushed; every step below needs an explicit operator ruling first.
2. GHI #728 (chores export) is the freshest and is the same class as the #607 fix that
   landed today. The classifier already has the shape -- `proofs/` stays out of the wheel
   via `runtime_state` -- so the work is a fourth class plus its two consumers.
3. GHI #727 (architecture: choices and mechanism objectives unrecorded) is open with a
   blocker naming its fork: is the per-mechanism objective+scope obligation documentary or
   mechanical? The lodestar half is likely rulable independently and is the smaller one.
4. The two directions booked earlier today and still unhomed: ARB retention (mirror
   `gz handoff archive`) and the rules staleness clock. Neither is defect repair, so both
   need an ADR home before an OBPI can carry them. One ADR could plausibly carry both.
5. Campaign Movement A remains topmost by the ruling recorded above:
   `ADR-0.35.0-canon-entry-corpus-landing` at 0/9 and the `ADR-0.34.0-foundation-sunset`
   capstone at 2/5. The airlock findings are captured but explicitly NOT sequenced forward.
6. Optional, unfiled: the ledger transit-count anomaly in § Important Context SEVENTH.

## Pending Work / Open Loops

13 GHIs open -- back to the session's starting count. #607 and #644 closed;
#727 and #728 filed. Two of today's closes were paid for by two new trackers, one of which
exists because this session broke something.

GHI #728 OPEN, filed this segment, with the rule-vs-code contradiction recorded as a
comment.

GHI #727 OPEN with a blocker comment naming the documentary-vs-mechanical fork.

THE SWEEP CHORE STILL SHIPS TO ADOPTERS. Its text now says so honestly and carries adopter
guidance, but the export itself is unfixed pending #728. It has also never been run --
its proofs directory is empty.

AIRLOCK: investigated, nothing built, sequencing explicitly unchanged. ADR-0.33.0 is closed
and attested, so there is no OBPI to resume; Movement B prescribes "a new feature ADR
extending ADR-0.33.0; heavy" with five unchecked boxes.

A DESTINATION-LIST WIDENING REMAINS UNRECONCILED: a registered chore counts as a
`ghi-close` landing site by operator ruling, but `ghi-close` SKILL.md still enumerates the
narrower list.

NO OBPI LOCK HELD, no in-flight pipeline.

## Verification Checklist

git status --short --branch (clean, level with origin/main);
git log --oneline -3 (expect f8ce93dee, 8d6c25fbc, 486cfd8af);
gh issue view 607 --json state (expect CLOSED); 644 (CLOSED); 727 and 728 (OPEN);
gh issue list --state open --json number (expect 13);
uv run gz cli audit (expect 132/132 fully covered);
uv run gz validate --documents --surfaces (expect exit 0, 2 scopes);
uv run gz validate --instructions (expect exit 0);
uv run gz validate --pydantic-models (expect exit 0 -- gzkit self-enforcement intact);
uv run gz test (expect Ran 7532 tests, OK).

To confirm the #607 fix is real rather than vacuous, read
`tests/test_instruction_audit.py::TestCodeContract::test_adopter_tree_without_gzkit_package_is_noop`
and note that the two pre-existing detection tests were MOVED into `src/gzkit/` in the same
edit. Left at `src/` they would have passed vacuously under the new scope, asserting
nothing -- that is the failure mode a scope change invites, and it is silent.

To confirm the mis-citation class is cleared, grep for `Negative #5` across `src/`,
`docs/user/manpages/`, and `.gzkit/skills/`: every surviving hit should either be the
corrective sentence in `commands/airlock.py` or the CORRECT usage in `airlock/enter.py`
("never a bare denial"), which is what the clause actually says.

Do NOT pipe verifiers through tail or grep when the exit code is the signal: the shell
reports the filter's exit, not the verifier's (`.gzkit/rules/tests.md` § Verification
exit-code integrity).

## Evidence / Artifacts

Session commits: `486cfd8af` (GHI #607 scope fix), `8d6c25fbc` (airlock
mis-citation class fix), `f8ce93dee` (GHI #728 false-claim correction).

The scoped validator and its regression guard: `src/gzkit/instruction_audit.py`,
`tests/test_instruction_audit.py`.

The correctly-shaped sibling the fix was modelled on:
`src/gzkit/governance/trust_audits/models.py`.

Mis-citation surfaces repaired: `src/gzkit/cli/parser_governance.py`,
`src/gzkit/commands/airlock.py`, `src/gzkit/commands/mx_cmd.py`,
`src/gzkit/commands/obpi_stages.py`, `src/gzkit/commands/permitted_entry.py`,
`docs/user/manpages/airlock.md`, `.gzkit/skills/gz-airlock/SKILL.md`.

The correct § Negative #5 citation deliberately retained: `src/gzkit/airlock/enter.py`.

The ADR whose calibration frontier is the true authority:
`docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md`.

The rule whose Two-Surface table the chores code contradicts: `.gzkit/rules/chores.md`.

The chore whose text was corrected:
`.gzkit/chores/test-consolidation-subtest-sweep/CHORE.md`.

Course-correction insights recorded this segment: `.gzkit/insights/agent-insights.jsonl`.

Predecessor handoff:
`.gzkit/handoffs/20260728T002306Z-triage-board-captured-607-investigated.md`.

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
- Seat the four recovered rulings via `--settled` on the next handoff, chosen from four presented routes (verbatim: selection of "Seat via --settled next handoff"). Filing a GHI first, direct repair of the committed artifact, and review-only were all declined.
- Run the git-sync (verbatim: "/git-sync"; booked via `gz handoff authorize`, session f2ee5b4e). A git-sync is always authorized per standing canon; no other advised step of the resumed handoff was authorized, and none was worked.
- Test-suite at-scale scope routes as parallelize `gz test` plus the subTest sweep (operator ruling 2026-07-27, chosen from three bounded options). The parallelism half was ALREADY SHIPPED in `baeb1f72e` and needed no work. GHI #512's Option B stays declined on measurement and was not re-litigated. GHI #644 closed `superseded` against `baeb1f72e` plus the project-local chore `test-consolidation-subtest-sweep` registered in `cac0917d8`.
- ARB receipt retention takes the mirror-`gz handoff archive` shape: `gz arb archive --older-than <N>d`, move-not-delete, with a dry-run and a harvest-before-archive guard so `advise`/`patterns` intelligence is never dropped unharvested (operator ruling 2026-07-27). A unified ARB-plus-handoff retention doctrine, purge-only-with-a-window, and won't-fix were all declined. GHI #594 stays OPEN with the direction booked: a new CLI verb is a contract change and this is not defect repair, so the GHI-direct-fix override does not apply and it needs an ADR home.
- Rules get a staleness clock, built with the honest backfill: `last_reviewed` added to `RuleFrontmatter`, each rule stamped with its last substantive commit date rather than today's, advisory first and fail-closed once the stale set clears (operator ruling 2026-07-27). Today's-date-plus-immediate-gating, attest-re-read-on-edit, and won't-fix were declined. GHI #691 stays OPEN with the direction booked: `RuleFrontmatter` is a schema/runtime contract and this is not defect repair, so it needs an ADR home.
- A registered chore counts as a valid `ghi-close` landing site (operator ruling 2026-07-27), widening that skill's enumerated list of commit SHA / registered ADR id / registered OBPI brief id / higher-numbered GHI. A chore satisfies the doctrine's principle -- a real artifact, discoverable via `gz chores list`, with its own acceptance criteria and run/audit lifecycle -- but was not named in the list. The widening is recorded in the GHI #644 close comment rather than applied silently.
- Clear the deck via the rulings lane rather than by implementing (verbatim: selection of "Rule the 3 decision-only trackers"). The two bounded-build options and the combined lane were declined.
- Author the consolidation chore in-session and then close, rather than naming it in the close comment or leaving the tracker open (verbatim: selection of "Author the chore, then close"). This corrected an earlier selection of mine that would have dead-lettered the scope.
- Write the entire triage into a handoff for context cleanup (verbatim 2026-07-28: "write the triage to handoff"). This mirrors the standing ruling of 2026-07-25, "write entire triage to new handoff, i want to clean up".
- Discuss the adopter Pydantic leak as this segment's subject (verbatim: "discuss this issue:" quoting the claim that it is unparked, bounded, defect repair, and the cheapest real close left).
