---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-11T01:08:51Z'
agent: claude-code
session_id: e4f85dc5-1719-4e88-beec-b05ee349cb88
continues_from: .gzkit/handoffs/20260810T014401Z-windows-cross-platform-class-and-toolchain.md
---

## Current State Summary

Opened as a routine /git-sync and became seven commits of defect repair plus the first of three structural repairs. Tree clean, main level with origin/main at `ff8ad605d`, `uv run gz check` exit 0 across all 54 steps.

Landed, oldest first: `a3cf2a829` (hook project-root resolve + fail-closed on unplaceable briefs), `0a54d27da` (ty unused-type-ignore-comment enabled on tests, 36 dead suppressions cleared), `f9e9a4618` (surface-delivery witness tests survival rather than heading offset), `9e0bde8c7` (Mechanical-row property witness ratchet, 64 frozen), `e4322635c` (two wrong live ADR counts removed from the predecessor handoff), `ff8ad605d` (transcribed-count structural form plus newest-handoff scan).

CI at authoring time: `check (ubuntu-latest)` success on `ff8ad605d`; the `check (windows-latest)` leg was STILL RUNNING and is deliberately not claimed green. The three commits before it were confirmed green on BOTH legs.

The four advised steps of the resumed anchor were all worked. Steps 5, 2 and 4 are discharged; step 3 is half discharged (the witness blindness is fixed, the truncation it now reports is not).

## Important Context

THE HANDOFF CHAIN IS FORKED and this document does not unfork it. The anchor the session resumed (`20260809T210209Z-critic-promoted-briefs-deferred.md`) and the one it was superseded by (`20260810T014401Z-windows-cross-platform-class-and-toolchain.md`) descend from DIFFERENT ancestors: the latter continues from a 2026-07-26 handoff and never saw the former. The Windows session ran on a clone that had not pulled, so anchor resolution reads local disk and a stale clone resumes a stale anchor, then writes a successor that orphans the newer chain. It was benign only by luck, because that session explicitly did not touch the campaign.

THE WINDOWS CI LEG IS NOW LOAD-BEARING, not decorative. Its first ever run failed and exposed that the OBPI completion validator hook was INERT on Windows: `find_project_root` returned an unresolved `Path.cwd()` while its caller resolved the target, so an 8.3 short-name temp dir made `relative_to` raise and the handler exited 0. A brief could be marked Completed with no Implementation Summary and no Key Proof. Fixed as a class across all three copies, and the call sites now resolve their targets too, because resolving only the root relocates the asymmetry rather than removing it.

SCOPE-LEVEL WITNESS COVERAGE IS NOT PROPERTY-LEVEL PROOF, and this is the sharpest reusable finding. gzkit already owns the mutation machinery: 73 registered enforcement claims, `EnforcementClaimRecord`, and a meta-validator run by `gz check` as the Enforcement floor step. But the registry is SCOPE-granular while scorecard Mechanical rows are PROPERTY-granular. Measured: 64 Mechanical rows over 46 distinct validator flags, six flags carrying two or three rows each. `--instructions-files-budget` is cited by two rows and has a live negative control that plants a per-file char-budget violation; it stayed green through the broken must-survive delivery predicate in the same scope. Counting negative-control coverage would have scored that row witnessed.

THE TRANSCRIBED-COUNT GAPS WERE ONLY USEFUL COUPLED. Widening the pattern alone finds nothing, because the evading `N of M` spelling appears on no registered surface. Registering handoffs alone misses the observed line, because it carries no progress cue within the 24-char window. Both shipped together in `ff8ad605d`.

ADR-0.35.0 CARRIES TEN OBPIs, NOT NINE. The denominator moved and every transcribed copy of the old figure went stale silently, including in the campaign. Read it with `uv run gz adr status ADR-0.35.0` rather than trusting any prose copy, this document included.

THREE FIGURES CARRIED IN PREDECESSOR PROSE REPRODUCED UNDER NO RUN and are superseded by measurement: the ty override cost, the all-rules-enabled diagnostic totals, and the Mechanical row count. Each is now recorded at its source with the command and tool version that produced it.

## Decisions Made

- [operator-ruled] Book the resumed anchor as proceed with every advised step set aside, sync only (verbatim: "sync only, handoff steps deferred").
- [operator-ruled] Proceed on the newest handoff with no step set aside (verbatim: "proceed wth newest"; spelling preserved).
- [operator-ruled] Fix the Windows hook defect at both arms, resolve symmetry AND fail closed, rather than the resolve fix alone or filing it (selected from a three-option picker).
- [agent-chose] Scoped the fail-closed arm to brief-shaped paths instead of every unplaceable path, deviating from the previewed diff. The hook is a PreToolUse on every Edit and Write, so a blanket refusal would have blocked scratchpad and system-file edits and bricked the session. The deviation was surfaced before it was made.
- [operator-ruled] Enable `unused-type-ignore-comment`, clear all 36 dead suppressions, and record the measurement in the config (selected from a three-option picker, after the measured cost came in at five times the figure the predecessor recorded).
- [operator-ruled] Ratchet forward on Mechanical-row witnessing and work the multi-property tranche first, rather than a full 64-row sweep or re-scoring the column (selected from a three-option picker).
- [operator-ruled] Take the three structural repairs cheapest-first, ordered transcribed views, then growth brake, then witness density (selected from a four-option picker whose alternatives were highest-leverage-first, build the measurement instrument first, and set them aside for campaign time).
- [agent-chose] Resolved the ledger rebase conflict by timestamp-ordered union rather than `--ours` or `--theirs`. For an append-only log a side-selection destroys governance events; the union preserved all nine and was verified by line count, JSON parse, and monotonic timestamps.
- [agent-chose] Keyed the Mechanical-row freeze on `<section-id>#<row>` after finding that 31 bare row numbers recur across the three tables, so a bare number cannot key a freeze.
- [agent-chose] Made the freeze file presence the adoption marker for the new binding. Deleting it fails the waiver ratchet closed, verified, so it is not a bypass here, while an adopter who received the scorecard from `gz init` without the freeze is not broken by a binding they were never given.
- [agent-chose] Scanned only the NEWEST handoff for transcribed counts. There are roughly 205 on disk and every older one is superseded by construction, so registering the corpus would refuse a mountain of dated records.
- [agent-chose] Marked the correction note `<!-- historical-count -->` rather than rewriting it, when the newly armed check flagged the very line that QUOTES the bad figure.

## Immediate Next Steps

1. RULE ON THE AGENTS.md TRUNCATION. 385 bytes fall past the codex delivery cap, taking Architectural Boundaries 3 through 6 whole, including the derived-views boundary that `governance-core.md` cites. The witness now names it on every run. The durable remedy is the GHI #580 [settled] reorder, which `data/agents_md_survival_declaration.json` states is a Layer-1 canon change requiring Gate-5 and is parked post-1.0, so it must NOT be taken unilaterally. Confirm with `uv run gz validate --instructions-files-budget`.

2. STRUCTURAL REPAIR 2, THE GROWTH BRAKE. AGENTS.md bytes may not increase while the surface is over the vendor cap. Roughly 15 lines on the shrink-only ratchet pattern already used 20 times in `data/waiver_ratchet_registry.json`. This is the operator doctrine that strictness is earned by the mechanism that discharges it, made mechanical. Sized after reading the surface, unlike the first estimate for item 3.

3. STRUCTURAL REPAIR 1, THE WITNESS-DENSITY CHECK. Compare Mechanical-rows-per-scope against negative-controls-per-scope; a scope claiming more properties than it has controls is provably under-witnessed. Roughly 40 lines reading two files that already exist. It would have caught the delivery-witness defect mechanically.

4. COLLAPSE THE FORKED CHAIN before another session inherits both anchors. Whichever handoff a clone happens to hold is the one its resume gate will pick.

5. THE CAMPAIGN HAS NOT MOVED. The nine ADR-0.36.0 briefs remain scaffold-shaped and are the topmost Magna Carta item; read their state with `uv run gz adr status ADR-0.36.0-convergence-moment-cross-family-critic`. Every session recently has been defect repair, which is authorized and correct, but the feature has not advanced.

## Pending Work / Open Loops

CONFIRM THE WINDOWS CI LEG ON `ff8ad605d`. It was still running when this document was written and is the only unverified claim here. Check with `gh run list --workflow CI --branch main --limit 1`.

THE OPEN-COUNT INSTRUMENT IS STILL THE WRONG ONE and remains unbuilt, carried unfiled from the predecessor. Nothing tracks defect rate, found-versus-introduced, or time-to-detection, so the only signal reaching the operator is the raw count of problems, which a maturing system drives UP. The operator raised exactly this doubt in session and it is the likeliest source of it.

THREE DEFECTS TRACKED AND NOT FIXED, all via `gz insights remember`: no `*.jsonl merge=union` strategy in `.gitattributes`, so concurrent syncs reliably conflict on the ledger; the unresolved `Path.cwd()` fallback in the control-surface-sync hook, low severity because that hook triggers a sync rather than gating; and `gz typecheck` corrupting diagnostic coordinates by expanding emoji shortcodes, which silently cost 1 of 36 parsed locations.

THE 40 ACCEPTED UNCALLED GATES remain disclosed rather than adjudicated, carried from the predecessor.

29 OF 39 CHORES still run the full unit suite as a criterion, roughly 43 minutes of duplicated work in a full sweep. Unfiled.

## Verification Checklist

Tree and gates:

```
git rev-list --left-right --count origin/main...main
uv run gz check
```

Expect `0 0` and exit 0 across 54 steps.

The four surfaces this session changed, each of which should be green and each of which bites when mutated:

```
uv run gz validate --advisory-scorecard
uv run gz validate --transcribed-adr-counts
uv run gz validate --instructions-files-budget
uv run gz validate --waiver-ratchet
```

Expect exit 0 from the first, second and fourth. The third exits 0 but WARNS by design, naming `architectural-boundaries` as a must-survive section straddling the cap; that warning is the live finding of advised step 1, not noise.

Both new gates were mutation-witnessed rather than assumed. Dropping one entry from `data/mechanical_witness_grandfather.json` makes the scorecard scope fail closed naming that exact row; restoring it returns exit 0. The transcribed-count arm caught a real line the moment it was armed.

Cross-platform, because a green local run on macOS is not evidence about Windows:

```
uv run ty check --python-platform win32 tests
gh run list --workflow CI --branch main --limit 3
```

## Evidence / Artifacts

Hook resolve and fail-closed repair:

- `src/gzkit/hooks/scripts/validation.py`
- `src/gzkit/hooks/core.py`
- `tests/test_hooks.py`

Type-check suppression sweep:

- `ty.toml`

Delivery-witness predicate:

- `src/gzkit/governance/trust_audits/surface_delivery_witness.py`
- `tests/governance/test_surface_delivery_witness.py`

Mechanical-row witness ratchet:

- `src/gzkit/governance/trust_audits/release.py`
- `data/mechanical_witness_grandfather.json`
- `data/waiver_ratchet_registry.json`
- `docs/governance/advisory-rules-audit.md`
- `tests/governance/test_advisory_scorecard_coverage.py`

Transcribed-count structural form and newest-handoff scan:

- `src/gzkit/governance/trust_audits/transcribed_counts.py`
- `data/transcribed_count_surfaces.json`
- `tests/governance/test_transcribed_counts.py`

Predecessor handoff corrected in place:

- `.gzkit/handoffs/20260810T014401Z-windows-cross-platform-class-and-toolchain.md`

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
- Fix the Windows defects in this clone rather than pushing from WSL (chosen over the recommended push-from-WSL route).
- Track the cross-platform findings as one GHI covering the class, not three sibling issues.
- Handoffs must never block a git-sync (operator verbatim 2026-08-09: "handoffs should never, never, never, ever, block git-sync. NEVER."), reaffirming the 2026-07-26 standing ruling and converting it into a mechanical exemption plus a covering test.
- Add `windows-latest` to `ci.yml`; macOS excluded on cost-versus-distinct-failure-class grounds.
- Do not blame a cross-platform defect on the tool's implementation language (operator verbatim: "Don't blame things on ty, it was designed to work with Python"). Configuring ty portably is gzkit's job.
- Track ty FORWARD, never pinned backward (operator verbatim: "we progress as Ty progresses, if it has become more strict, then we tighten up, do not avoid hard work by clinging to older version of Ty"). This overruled the `gz-deps-upgrade` Risk-notes recovery posture and the agent's `ty==0.0.55` pin.
- Fix the audit predicate and the rule table immediately rather than filing a GHI, and keep the 324 `features/` removals.
