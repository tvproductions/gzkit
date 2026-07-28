---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-28T00:23:06Z'
agent: claude-code
session_id: f2ee5b4e-8f77-4953-859a-f86517090abf
continues_from: .gzkit/handoffs/20260728T001047Z-ghi-triage-644-closed-two-directions-booked.md
---

## Current State Summary

Context-cleanup handoff. Its purpose is to preserve the full triage board and
the GHI #607 investigation so the conversation can be discarded without losing either.

The triage ran earlier this session: 12 of 13 open GHIs ranked, deck taken from 13 to 12.
That session's narrative, corrections and rulings are in the predecessor; what was NOT
captured there is the board itself and the per-issue reasoning. This handoff carries both.

Then GHI #607 (the adopter Pydantic leak) was investigated against the code rather than
discussed from its body. The finding is stronger than the claim it was meant to check: the
cure for #607's entire class was built twice this month, ships today, and names GHI #607 in
its own docstrings as the complaint it exists to avoid -- while #607 itself was never
converted. The fix is close to copy-paste from a pattern already in the tree.

No code was changed this segment. Investigation and capture only.

## Important Context

THE RANKED BOARD, 12 of 13 open, in pull order. Rendered by
`.claude/skills/ghi-triage/scripts/triage.py --format rank` from
`.gzkit/cache/triage/rank.json`; 60-day `fix(` precedent 313.

  1. #607 [blocking]   models.md + audit_code_contract_mismatches force Pydantic on adopters
  2. #669 [degrading]  obpi-monitor: no mechanical audit that status writers consult the
                       terminal rule (convention-only)
  3. #644 [latent]     tests: at-scale management strategy  -- CLOSED superseded this session
  4. #594 [latent]     arb: no archive/purge half, 1875 receipts unbounded
  5. #691 [degrading]  rules: no aging mechanism, skills have last_reviewed, rules nothing
  6. #719 [degrading]  interview: pool ADR interview JSON is unschema'd
  7. #670 [latent]     design skills: opus self-escalation lacks cross-family second opinion
  8. #567 [latent]     skills: adopt fenced prototype-spike + mine 2 filters (Pocock parity)
  9. #615 [degrading]  schema: structured governance docs regex-scraped, not schema-enforced
 10. #581 [latent]     brief-reconcile: existence-only checks miss dead surfaces & couplings
 11. #611 [latent]     governance: no general append-only corrective-action primitive
 12. #579 [latent]     instructions-budget: anchor on imperative-density, not char count

EXCLUDED FROM THE RANKING: #533 (agents-md-budget 5k recovery target). Its stale-blocker
flag fires -- it cites settled #517 and #712 -- but its real gate is ADR-0.0.37 completion
plus the registry-projection migration, which is `ADR-0.35.0` sitting at 0/9. Ranking it
would have recommended work that cannot start. The stale-blocker instrument reports
citations, not verdicts; #594's cited precondition genuinely cleared while #533's did not,
on the same flag.

THE BOARD SPLITS THREE WAYS BY WHAT IT COSTS TO CLOSE, which is the axis that matters for
deck-clearing and which the rank order alone does not show:

  - Decision-only trackers (#644, #594, #691): parked strategy captures that close or route
    on a ruling, not on implementation. All three were ruled on this session. Only #644
    actually closed; the other two are new capability rather than defect repair, so operator
    canon's GHI-direct-fix override does not reach them and canon forbids a headless OBPI --
    they need an ADR home. Their directions are booked as issue comments and seated in the
    predecessor's Settled Rulings.
  - Bounded builds, no open questions (#607, #669): fully specified, small, no design
    conversation outstanding.
  - Design-shaped or gated (#615, #581, #611, #579, #567, #670, #719): real work or
    architectural. #581 is TRACK-ONLY by prior settled ruling and rides a registry collapse.

ROUTE IS NOT SIZE. The script routes every issue `direct-fix` because the 60-day precedent
is 313 against a threshold of 3. That is the mechanical answer only. Read `route` as "the
thresholds do not block you", never as "this is a small change" -- several of these are
pool-ADR-shaped.

--- GHI #607, investigated against the code (this segment's substantive work) ---

FINDING 1, and it is the decisive one: THE CURE ALREADY EXISTS IN THE TREE, BUILT TWICE
THIS MONTH, AND CITES #607 BY NUMBER. `src/gzkit/config.py` carries `AuthorshipConfig`
(GHI #725) and `SmokeConfig` (GHI #724). Both are opt-in by default. `AuthorshipConfig`'s
docstring reads verbatim: "gzkit ships to adopters, and an identity rule shaped by gzkit's
own operator and enforced on every adopter is the dogfooding-leak complaint open at GHI
#607 -- so the default admits every address." `SmokeConfig` says it is "opt-in for the same
reason." The previous session built the remedy for #607's class, named #607 as the thing it
was avoiding, and left #607 itself unconverted.

FINDING 2: GZKIT'S OWN `src/` CONTAINS ZERO DATACLASSES. Measured, not assumed:
`grep -rln "^\s*\(from dataclasses import\|@dataclass\)" src/` returns nothing. This
matters because the settled ruling that unparked #607 turns on preserving gzkit's own
self-enforcement -- and with zero dataclasses, EVERY candidate fix preserves it for free.
There is no tension to trade off. The self-enforcement objection is empirically empty.

FINDING 3: THE RULE TEXT CANNOT EXPRESS THE POLICY IT WANTS. In
`src/gzkit/instruction_audit.py` `audit_code_contract_mismatches`, the arming condition is
`if "Pydantic" not in body and "BaseModel" not in body: return errors`. Any body that so
much as MENTIONS either word arms a blanket ban on every `@dataclass` and
`from dataclasses import` under `src/`. So an author trying to write the common, legitimate
posture -- Pydantic at the validation boundary, dataclasses fine for internal value objects
-- writes the word "Pydantic", and thereby bans the dataclasses the sentence permits. The
rule is unauthorable, not merely strict. That is a sharper defect than the scope leak and
is not stated this way in the issue body.

FINDING 4: THE TRIGGER IS THE GENERATED MIRROR, NOT CANON. The validator reads
`.github/instructions/models.instructions.md`, not the canonical `.gzkit/rules/models.md`.
The vendor mirror is a sync output, so the gate fires off a derived artifact. Worth knowing
before editing: changing canon without re-syncing leaves the gate reading the old text.

FINDING 5: ROUTING IS SETTLED AND PRECEDENTED. #607 is labeled `defect`, is unparked by
settled ruling (attested REQ-0.14.0-04-04 asserts a detection capability and is silent on
scope, so an adopter-scope predicate does not falsify it), and is defect repair rather than
new capability -- so operator canon's GHI-direct-fix override applies and no ADR is needed.
The two precedent gates landed as exactly this shape: `74a537f35 fix(smoke)` and
`78d851add fix(validate)`, both adding a `.gzkit.json` opt-in block as a direct fix. A
config-key addition for an opt-in gate is a recent, twice-walked path, not a new one.

## Decisions Made

- [operator-ruled] Write the entire triage into a handoff for context cleanup
  (verbatim 2026-07-28: "write the triage to handoff"). This mirrors the standing ruling of
  2026-07-25, "write entire triage to new handoff, i want to clean up".
- [operator-ruled] Discuss the adopter Pydantic leak as this segment's subject (verbatim:
  "discuss this issue:" quoting the claim that it is unparked, bounded, defect repair, and
  the cheapest real close left).
- [agent-chose] Investigated GHI #607 against the code BEFORE discussing it, rather than
  reasoning from its body. Earlier this same session a GHI body's measured state was two
  rows stale and an operator ruling was taken on it; discussing a second issue from its body
  would have repeated the failure within the hour.
- [agent-chose] Measured gzkit's own dataclass usage rather than assuming the
  self-enforcement tension was real. It is zero, which collapses the objection the unparking
  ruling was written to answer and makes every candidate fix cost-free on that axis.
- [agent-chose] Named the unauthorable-rule defect (Finding 3) as distinct from, and
  sharper than, the scope leak the issue title describes. The issue body documents the
  all-or-nothing heuristic as its third defect but does not draw the conclusion that the
  nuanced rule is impossible to WRITE, which is what makes option (2) alone insufficient.
- [agent-chose] Captured the board's cost-to-close split in this handoff even though the
  renderer does not emit it. Rank order alone does not tell a reader which issues close on a
  ruling and which need an ADR, and that distinction is what the deck-clearing session
  actually turned on.

## Immediate Next Steps

1. NOTHING IS AUTHORIZED. This segment was investigation and capture only;
   every step below needs an explicit operator ruling first.
2. Fix GHI #607. Recommended shape: mirror the shipped opt-in pattern -- add a `models`
   block to `.gzkit.json` config (default off), gate `audit_code_contract_mismatches` on it,
   and declare it true in gzkit's own `.gzkit.json`. Direct fix, committed as
   `fix(validate): make the models policy opt-in for adopters (GHI #607)`, no ADR. Consider
   pairing it with a heuristic repair so the rule becomes
   authorable (Finding 3), since opt-in alone leaves the rule unwritable for any project
   that DOES opt in -- including gzkit.
3. Consider whether the scaffolder should stop shipping `models.md` to adopters at all
   (the issue's own option 3: a dogfooding-only frontmatter flag). That is the class fix
   behind the instance; it is larger and touches `src/gzkit/rules/_scaffolder.py`.
4. The two booked-but-unhomed directions still need an ADR home: ARB retention and the
   rules staleness clock. One ADR could plausibly carry both.
5. The next-cheapest bounded build after #607 is #669 (a `gz validate` scope asserting every
   OBPI-status writer routes through the terminal-rule predicate), roughly 100 lines with no
   open design questions.

## Pending Work / Open Loops

12 GHIs open. None filed or closed this segment.

GHI #607 IS INVESTIGATED BUT UNFIXED. Findings above; no code changed.

TWO ISSUES CARRY BOOKED DIRECTIONS AND NO HOME: ARB retention and the rules staleness
clock. Neither direction should be re-adjudicated; only the ADR home is missing.

THE NEW CHORE HAS NEVER BEEN RUN. `test-consolidation-subtest-sweep` is registered and
resolves as `project` with two acceptance criteria, but its proofs directory is empty.

A DESTINATION-LIST WIDENING IS IN EFFECT AND UNRECONCILED: a registered chore counts as a
`ghi-close` landing site by operator ruling, but `ghi-close` SKILL.md still enumerates the
narrower list. Reconciling the skill text to the ruling is unwritten work.

GHI #719 OPEN and unworked -- the carried direction-(b) capability from #718.

NO OBPI LOCK HELD, no in-flight pipeline. No source or test file modified this segment.

## Verification Checklist

git status --short --branch (clean, level with origin/main);
gh issue list --state open --json number (expect 12);
gh issue view 607 --json state (expect OPEN -- investigated, not fixed).

To confirm the decisive finding rather than trusting this document, read the class
docstrings in `src/gzkit/config.py` and observe that both name GHI #607 as the complaint
they exist to avoid. The cure for the class ships; the instance is open.

To confirm the self-enforcement finding, run the dataclass sweep over gzkit's own source
and observe it returns nothing -- gzkit already complies, so no candidate fix trades
anything away:
  grep -rln "^\s*\(from dataclasses import\|@dataclass\)" src/

To confirm the unauthorable-rule finding, read `audit_code_contract_mismatches` in
`src/gzkit/instruction_audit.py` and observe the arming condition is a bare substring test
for "Pydantic" or "BaseModel" over the whole body, with no per-file or boundary escape.

Do NOT pipe these verifiers through tail or grep when the exit code is the signal: the
shell reports the filter's exit, not the verifier's (`.gzkit/rules/tests.md` § Verification
exit-code integrity). The greps above are content reads, not verifier exits, and are safe.

## Evidence / Artifacts

The validator implicated by the issue, and the arming condition in Finding 3:
`src/gzkit/instruction_audit.py`.

The shipped opt-in precedent whose docstrings name GHI #607: `src/gzkit/config.py`.

The sibling gate built on that pattern this month:
`src/gzkit/governance/trust_audits/authorship.py`.

Canonical rule text: `.gzkit/rules/models.md`.

The generated mirror the validator actually reads:
`.github/instructions/models.instructions.md`.

Triage rank input this board was rendered from: `.gzkit/cache/triage/rank.json`.

The two precedent commits landing opt-in config gates as direct fixes: `74a537f35`
(smoke) and `78d851add` (authorship).

Predecessor handoff:
`.gzkit/handoffs/20260728T001047Z-ghi-triage-644-closed-two-directions-booked.md`.

No source or test files were modified this segment.

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
