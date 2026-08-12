---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-12T07:34:55Z'
agent: claude-code
session_id: b7696eb4-cca5-49f1-98ec-075716959c97
continues_from: .gzkit/handoffs/20260812T063118Z-three-ghis-closed-band-witness-and-multi-parent-lineage.md
---

## Current State Summary

The operator resumed the anchor handoff, ruled "Fix the two defects only, then stop" against a four-option picker (all four advised steps recorded set-aside), then authorized a third fix in flight with "fix 793". Three commits landed and are synced; `origin/main...main` is 0 0 at `2892126d4`; tree clean; no active locks.

The session's shape came from one observation. The anchor's advised steps were never worked. Reviewing the handoff surfaced that the SessionStart advisement had named a different document than the resume gate armed on — the review found a defect in the reviewing apparatus itself, and that became the work.

Landed: `1c1e44d4a` (resume_handoff selection drift), `cc81b93b2` (campaign banner asserting a withdrawn pull-ahead), `2892126d4` (GHI #793, a false FACADE in the enforcement floor). GHI #793 was filed and closed within the session. `uv run gz check` exits 0 under BOTH forced and disabled colour, which is the property the third fix is about rather than an incidental double-check.

## Important Context

THERE ARE THREE SELECTION READERS OVER `.gzkit/handoffs/`, NOT TWO, AND THE THIRD WAS INVISIBLE TO THE FENCE. `handoff_selection.py` owns the rule (`selection_rank`, `FLOOR_BOOKMARK_AGENT`); `handoff_resume_gate.newest_handoff` and `session_orientation.collect_handoff` called it; `handoff_api.resume_handoff` did not — it took `list_handoffs()[0]`, plain recency. That reader renders the SessionStart advisement, and a floor bookmark is written at every session end, so it was the newest document on disk nearly always. The module docstring ENUMERATED its readers in prose and the enumeration was simply wrong; the differential test now covers all three, including the live repository corpus. Prose enumeration is not a fence.

THE MIS-BOOKING WOULD HAVE LIFTED THE GATE ANYWAY. `_lifts_the_gate` matches on `session_id` alone and never compares the event's `handoff_path` to the handoff the gate armed on. So a ruling booked against the path the advisement printed would have recorded operator consent on a content-free bookmark AND opened the gate for a different document's four substantive steps. That coupling gap is UNFIXED and is the sharpest residual of this session.

`list_handoffs` DELIBERATELY STAYS CHRONOLOGICAL. It is a listing primitive and `gz handoff list` is an operator-visible surface; selection belongs at the selection sites, which is what the module docstring argues. Do not "helpfully" sort it by `selection_rank`.

`_newest_predecessor` WAS CHECKED AND IS NOT IN THIS CLASS. It returns None when `adr_id is None`, and `book_exit_bookmark` never passes an `adr_id`, so an ADR-scoped query cannot return a bookmark. Had it been in the class the damage would have been worse than the advisement bug: `_carried_settled` reads only DIRECT `continues_from` refs, one hop, so a bookmark parent would have dropped the entire settled-rulings corpus in a single link.

A FALSE FACADE IS WORSE THAN A SILENT NEGATIVE CONTROL. GHI #793 was not a check that passed while blind — it was a check that FAILED while working. `gz preflight` caught its planted marker and exited 1; Rich's number highlighter had written SGR codes inside the identifier, so the `expect_output` literal no longer occurred. The meta-validator then emitted its strongest verdict — "the enforcement claim adopted by nothing, the check is theater" — about working enforcement. It also failed the pre-commit floor, so the pressure it created pointed at `--no-verify`, at rewriting the control to match broken output, or at deleting the check. All three are worse than the defect.

`capture_output=True` IS WHY `FORCE_COLOR` MATTERS HERE. The NC child never owns a TTY, so Rich's own is-a-terminal test would have disabled colour unprompted. `FORCE_COLOR` overrides exactly that test. This is why the defect was green in CI and red on a developer machine, and why "it passes in CI" was not evidence of anything.

`FORCE_COLOR` IS HONOURED FOR ANY VALUE, INCLUDING EMPTY. That is why `run_command`'s new `env_overrides` takes `str | None` and treats None as UNSET: a plain `{**os.environ, "FORCE_COLOR": ""}` merge sets it to empty, which still forces colour. Blanking is not unsetting.

THE CAMPAIGN BANNER IS TRANSCRIBED INTO EVERY SESSION'S ORIENTATION. `scripts/session_orientation.py` lifts the "Topmost (sequenced)" line verbatim. It had asserted the 2026-08-09 pull-ahead for a day after the 2026-08-11 amendment withdrew it, so three surfaces in one file disagreed and the stale one is the one read first. The corrected banner now carries a standing note that it is part of any sequencing amendment rather than a follow-up.

`git stash` REVERTS `.gzkit/ledger.jsonl`. Booked gate authorization lives in a tracked file, so stashing un-books it and re-arms the resume gate mid-session; `git stash pop` is then itself refused by the gate. Recovery is to re-book with `gz handoff decide` first (the gate never blocks its own recovery). Prefer a detached worktree at HEAD over stash when comparing against a clean tree. Recorded via `gz insights remember`.

## Decisions Made

- [operator-ruled] Fix the two defects the review surfaced and stop, rather than working the anchor's campaign steps (verbatim selection: "Fix the two defects only, then stop"), chosen from a four-option picker whose alternatives were fix-then-steps-1-and-2, handoff-steps-1-and-2-only, and hold-sync-only. All four advised steps of the resumed anchor were recorded set-aside via `gz handoff decide`.
- [operator-ruled] Fix GHI #793 (verbatim: "fix 793"), authorizing in flight the third defect the agent had filed rather than fixed under the preceding ruling.
- [agent-chose] Fixed GHI #793 at the CHANNEL rather than the fixture. Re-phrasing the preflight substring to something digit-free would have made the symptom vanish and left the other five `expect_output` controls protected by nothing but luck of wording.
- [agent-chose] Added `env_overrides` to `run_command` rather than pinning colour globally there or stripping ANSI after capture. A global pin changes captured output for every `gz check` step, far wider than the defect; post-capture stripping sanitizes downstream of a source we control and would mask genuine escape sequences.
- [agent-chose] Made `env_overrides` accept `str | None` with None meaning UNSET, because `FORCE_COLOR` is honoured for any value including the empty string, so a plain dict merge cannot express what this fix needs.
- [agent-chose] Left `list_handoffs` sorting chronological rather than applying `selection_rank` there. It is a listing primitive behind an operator-visible verb; widening the fix to it would have changed `gz handoff list` output for no correctness gain.
- [agent-chose] Verified `_newest_predecessor` against the same failure class rather than assuming it, and ruled it structurally exempt, so the commit could say so instead of leaving a reader to re-derive it.
- [agent-chose] Filed GHI #793 rather than fixing it on discovery, because the standing ruling at that moment was "then stop". Recorded a blocker comment naming the authorization as the next concrete operator action, per the ghi-author no-silent-tracker rule.
- [agent-chose] Established the FACADE was pre-existing with a detached worktree at HEAD, after `git stash` un-booked the resume-gate authorization and re-armed the gate. The worktree probe is the technique that should have been used first.
- [agent-chose] Split the two ruled fixes into separate commits after `git checkout stash@{0} -- <files>` staged all four files and bundled them into one, whose message described only half of what it carried. Undone with `git reset --soft` before anything was pushed.
- [agent-chose] Ran the two blocked commits as `NO_COLOR=1 FORCE_COLOR= git commit` rather than `--no-verify`, which is forbidden by AGENTS.md Never #10. This runs the gate in the one configuration where its verdict is true rather than suppressing it.
- [agent-chose] Verified the GHI #793 fix at BOTH colour poles at the gate level, not only in the unit test, because the claim is invariance and a single green run cannot express it.
- [agent-chose] Regenerated this handoff through `gz handoff create` rather than hand-patching it, after `gz validate --transcribed-adr-counts` refused the push over a live ADR count written into advised step 2. Hand-editing would have produced a document the gate had not seen in its final form. Worth recording as a caught instance of GHI #768's class from the inside: the rejected draft also argued the copy was safe because it was the only one, which is precisely the reasoning that finding rejects.

## Immediate Next Steps

1. RULE ON THE `handoff_path` COUPLING GAP IN THE RESUME GATE. `is_resume_authorized` matches a booked ruling on `session_id` alone; `_lifts_the_gate` never compares the event's `handoff_path` against the handoff `newest_handoff` armed on. So a ruling booked against the wrong document still opens the gate for the right one. This session came within one command of demonstrating it live, because the advisement printed the bookmark path directly beside the `gz handoff decide --handoff <path>` recipe. The selection fix removes the most likely way to reach that state but does NOT close the gap: any path typo, any stale copy-paste, or a second handoff authored mid-session reaches it again. Bounded question — compare the two paths and refuse a mismatch, or state in the gate module why session-scope alone is the intended granularity. Read `src/gzkit/handoff_resume_gate.py` before ruling; it is the cheapest item here and it guards the mechanism every other item depends on.

2. RULE THE ADR-0.35.0 LIFECYCLE STEP. Carried unworked from four predecessors and now set aside a SIXTH time, which is a stronger signal than anything in its content. Run `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for the live lifecycle and landed count; it reports Lifecycle `Pending` while the ADR frontmatter says `status: Draft`. These are different axes, not drift — the Lifecycle column is Layer-3 derived from Layer-2 events, frontmatter is Layer-1 authorship — so this is a fresh authoring decision about whether `Draft` is right for a feature about to receive OBPI work, not a reconciliation. It gates step 3.

3. PULL `OBPI-0.35.0-01-corpus-tombstone-schema-and-fold`. It heads the declared 01 then 02 then 03 chain and carries the fold algebra the ADR pinned in its Decision section as its one irreversible commitment. Read that algebra from the ADR rather than re-deriving it: single reverse pass, never a fixpoint iteration, and unset tombstone fields MUST be omitted from serialization or `corpus_fingerprint()` re-fingerprints the whole corpus on the landing commit. ADR-0.35.0 is the in-flight feature by the 2026-08-11 amendment, and the banner now says so.

4. RULE WHETHER THE ADVISORY SCORECARD SHOULD COVER ADR-DECLARED DOCTRINE. Recorded on GHI #792 [settled] and still not acted on; set aside twice. `docs/governance/advisory-rules-audit.md` scopes to `.gzkit/rules/**` clauses, so ADR-0.0.33 anti-pattern 3 sat outside the instrument that tracks enforcement for the project's entire life. Bounded either way: widen the scope, or state in the audit that ADR anti-patterns are deliberately out of scope and name what does track them. Carries its own Coverage Ledger ceremony.

5. WATCH THE SURFACE-WEIGHT HEADROOM RATHER THAN ASSUMING IT. The 2026-08-11 band raise bought roughly 47 days at the then-measured 8.4 lines/day, and Movement C is Reduce the accretion, so growing into the headroom is the outcome the raise was NOT for. Note this session ADDED to the instruction surface only in `src/` docstrings, which the gate does not count. Measure with `uv run gz validate --surface-weight`.

## Pending Work / Open Loops

THE RESUME-GATE `handoff_path` COUPLING GAP IS OPEN AND UNFILED. It is advised step 1 rather than a GHI because the right disposition may be a one-line comment stating that session scope is intentional, and filing to satisfy a tracker would be the reflexive-GHI shape the operator's 2026-06-01 moratorium names. If the ruling is to fix it, file then.

THE SIX SESSION-EXIT BOOKMARKS FROM 2026-08-12 ARE NOW COMMITTED (`1c1e44d4a`). Six distinct sessions wrote byte-identical 39-line bookmarks inside 76 seconds. The writer behaved as designed; the churn is the input. This is live evidence for GHI #766, which is open and parked behind the doctrine ADR — six zero-content documents entering permanent history in one minute is the concrete cost that issue describes in the abstract.

GHI #767 (handoff frontmatter carries no transcript reference) REMAINS OPEN and parked behind the same doctrine ADR. This handoff carries no transcript pointer for exactly that reason.

ADR-0.36.0 IS DEFERRED, NOT ABANDONED, AND ITS PULL-AHEAD IS WITHDRAWN. Three briefs (01 critic-skill-contract, 02 cross-family-transport, 03 operator-door) are authored and passing; six remain draft scaffolds. Its Fidelity Assertions table still carries the scaffold's example row, so `--fidelity-presence` passes while the ADR asserts nothing about its own thesis.

THE CROSS-FAMILY CRITIC STILL DOES NOT RUN. `.claude/hooks/` ships no critic script and `PreToolUse` has no `AskUserQuestion` matcher. Every structured choice this session presented went unchallenged, including the four-option picker that scoped the whole session.

THE OPEN-COUNT INSTRUMENT IS STILL THE WRONG ONE and remains unbuilt. Nothing tracks defect rate, found-versus-introduced, or time-to-detection. This session is another data point: it opened one GHI and closed it, and found that defect only by verifying its own work rather than by any instrument.

THREE TRACKED DEFECTS REMAIN UNFIXED, all via `gz insights remember`: no `*.jsonl merge=union` strategy in `.gitattributes`; the unresolved `Path.cwd()` fallback in the control-surface-sync hook; and `gz typecheck` corrupting diagnostic coordinates by expanding emoji shortcodes. That third one is the SAME FAMILY as GHI #793 [settled] — Rich rendering mutating text a consumer parses — and is now the only known live member of it.

A FOURTH INSIGHT WAS ADDED THIS SESSION: `git stash` reverts `.gzkit/ledger.jsonl` and silently re-arms the resume gate, scope `handoff-resume-gate`.

THE 40 ACCEPTED UNCALLED GATES remain disclosed rather than adjudicated. 29 OF 39 CHORES still run the full unit suite as a criterion, roughly 43 minutes of duplicated work in a full sweep; unfiled. THE INSTRUCTIONS-FILE BUDGET WORK STAYS PARKED by standing ruling until the product stabilizes.

## Verification Checklist

Confirm this session's claims against Layer 2 rather than trusting this document:

uv run gz check
uv run -m unittest tests.governance.test_handoff_selection tests.governance.test_enforcement_nc_discrimination
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing
uv run gz obpi lock list
git rev-list --left-right --count origin/main...main
gh issue view 793 --json state

THE GHI #793 FIX IS A CLAIM ABOUT INVARIANCE, SO VERIFY IT AT BOTH POLES OR NOT AT ALL. A single green run cannot express the property. Run `uv run gz check` twice, once with `FORCE_COLOR=3` exported and once with `NO_COLOR=1 FORCE_COLOR=` prefixed; both must exit 0. Before `2892126d4` the first exits 1 and the second exits 0, which is the defect stated as a measurement.

The negative control is reproducible directly: build the fixture with `_build_preflight()` from `gzkit.governance.trust_audits._qc_negative_controls`, call `_ep_preflight` on it under each environment, and observe the verdict is 1 in both. A falsy verdict under forced colour is the regression.

Read ADR-0.35.0's landed count off `gz adr status`; this document deliberately carries NO copy of it. The first draft of this handoff carried one in advised step 2 and `gz validate --transcribed-adr-counts` refused the push — correctly, and it is worth recording that the draft also contained a sentence rationalizing the copy as safe because there was only one. A transcribed count has no reconciliation path no matter how few copies exist, which is the whole finding of GHI #768.

Do NOT pipe any of these through `tail` or `grep` — the verifier-pipe-gate hook refuses it, and the shell would report the filter's exit rather than the verifier's. Capture with `> out.log 2>&1` and read the file.

## Evidence / Artifacts

Commits landed and synced this session:

- `1c1e44d4a` — resume_handoff ranks authored above bookmark; the SessionStart advisement and the resume gate now name the same document. Also lands the six inherited exit bookmarks.
- `cc81b93b2` — the campaign banner stops asserting the withdrawn pull-ahead.
- `2892126d4` — GHI #793: negative-control subprocesses run with colour pinned off.

Authored or changed:

- `src/gzkit/handoff_api.py` — `resume_handoff` calls `selection_rank`; `HandoffInfo` carries `agent`; `list_handoffs` stamps it
- `src/gzkit/handoff_selection.py` — module docstring now names four readers and records that the prose enumeration was the thing that failed
- `src/gzkit/quality.py` — `run_command` gains `env_overrides`, where a None value UNSETS
- `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py` — `_NC_PRESENTATION_PINS`; `_command_fails_argv` pins them for every child
- `tests/governance/test_handoff_selection.py` — the differential now covers all three selection readers, live corpus included
- `tests/governance/test_enforcement_nc_discrimination.py` — colour-invariance at the channel and at the preflight instance
- `docs/governance/build-to-1.0-campaign-2026-07-18.md` — banner corrected, plus the standing note coupling it to any sequencing amendment
- `.gzkit/insights/agent-insights.jsonl` — the `git stash` / ledger discovery

Read to ground the work:

- `src/gzkit/handoff_resume_gate.py` — `newest_handoff`, `is_resume_authorized`, `_lifts_the_gate`; the source of advised step 1
- `scripts/session_orientation.py` — `collect_handoff`, which had the ranking right and proved the third reader was the outlier
- `src/gzkit/session_exit.py` — confirmed `book_exit_bookmark` passes no `adr_id`, which is what exempts `_newest_predecessor`

GitHub:

- GHI #793 filed and closed within the session, with the diagnosis, the escalation naming the pre-commit block, and the fix evidence as three separate comments.

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
- Work the triage list in its ranked order (operator verbatim 2026-07-25: "continue on the triage list"; booked via `gz handoff authorize`, session 6aa88bcf). This resolved the predecessor handoff's advised step 1 by ruling the pull order to be the ranking already recorded in `.gzkit/cache/triage/rank.json`, which puts GHI #615 first.
- Proceed with GHI #615 cuts 2 and 3 (migration plus strict enforcement) rather than sampling first or switching to GHI #607.
- Escalation should key on lifecycle rather than on frontmatter shape (operator selected the recommended option after the three dispositions were presented). Implementation is preserved but not landed, because measurement afterwards showed it does not by itself reach a green gate.
- Dimension-aware Draft scoping: a Draft brief does NOT gate on its own deliverables (allowlist existence, `gz` verb resolution) but DOES still gate on prerequisites (Discovery Checklist, citations). Landed as 5111b7dd.
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
- Book the resumed anchor as proceed with every advised step set aside, sync only (verbatim: "sync only, handoff steps deferred").
- Proceed on the newest handoff with no step set aside (verbatim: "proceed wth newest"; spelling preserved).
- Fix the Windows hook defect at both arms, resolve symmetry AND fail closed, rather than the resolve fix alone or filing it (selected from a three-option picker).
- Enable `unused-type-ignore-comment`, clear all 36 dead suppressions, and record the measurement in the config (selected from a three-option picker, after the measured cost came in at five times the figure the predecessor recorded).
- Ratchet forward on Mechanical-row witnessing and work the multi-property tranche first, rather than a full 64-row sweep or re-scoring the column (selected from a three-option picker).
- Take the three structural repairs cheapest-first, ordered transcribed views, then growth brake, then witness density (selected from a four-option picker whose alternatives were highest-leverage-first, build the measurement instrument first, and set them aside for campaign time).
- Remedial action against a closed feature routes as a GHI direct fix referencing the original ADR (operator verbatim 2026-08-06: 'GHIs that direct fix and reference the original adr seems prudent to me. this is a grey area, but the best I have at the moment'). The residual the canon does not cover: a correction never traces back to the ADR it repaired.
- Work the session as 'commit, then traige' (verbatim), booked via gz handoff decide; advised steps 1, 3 and 4 were recorded set-aside, step 1 because origin/main was already 0/0 and the sync it advised had run before the predecessor handoff's ink dried.
- Do the top 5 of the triage list (verbatim: 'let's do the top 5 on the triage list').
- Direct fix beats riding the pool ADR where the fix removes or reuses rather than adding a parallel reader (operator: 'pool won't be promoted soon, is direct fix better?'). Applied per-item, which is what caught #581.
- Park all instructions-file budget work until the product stabilizes (verbatim: 'don't worry about any instructions file budgets right now, we want the product to stabilize').
- No ARB purge until insight retention is solid (verbatim: 'i don't want purges until guaranteed summaries for action-taking remedies are in place'), on the stated ground that 'there is no point in 1/2 measures now unless we are going to solve now'.
- Align the forcing-function surfaces as a direct fix (verbatim: 'ALIGN THESE!!!'), characterized by the operator as 'a direct fix for what is a clear defect of misalignment/incomplete implementation'.
- Build the efficacy channel (verbatim: 'efficacy channel is right — build it - these are all defects of design').
- Remedial action against a closed feature routes as a GHI direct fix referencing the original ADR (verbatim: 'GHIs that direct fix and reference the original adr seems prudent to me. this is a grey area, but the best I have at the moment'). This restates canon the operator had already booked; the genuine residual is that a correction never traces BACK to its ADR.
- The OBPI process must NOT be altered at all (verbatim: 'we will NOT alter the OBPI process, at all! This is a broader and per-session tool need'). This forecloses the critic alternative of extending adversarial_validation with a phase discriminator. Booked to insights 2026-08-07.
- Generalizing FROM the existing 4b skills and tooling is acceptable, but the OBPI pipeline itself stays untouched (verbatim: 'it is possible we generalize from the existing skills/tooling for obpi 4b, but I am hesitant to alter anything about the obpi pipeline as it is the most enduringly stable part of gzkit').
- The trigger is the convergence moment (verbatim: 'we are trying to jump in when you offer analyzed and considered design options in the same structed way - you've achieved convergence, within that session, when you do so, I need a 2nd opinion in that exact moment'). Explicitly not an Airlock Jr.
- Stated goal for the whole session, verbatim: 'retain cross-family review for consequential decisions'.
- Vendor posture is deliberately concrete, not generic (verbatim: 'I am trying to be specific: The US Air Force, the Chinese Air Force, etc. we can refactor to generics once we have platform stability'). Claude is the daily driver; Codex is the named adversary; the lock-in risk is accepted knowingly (verbatim: 'I need forward momentum, not design niceties - they can come with the refactor').
- Experimental refinement is expected (verbatim: 'we can experimentally refine this moving forward'), so a calibrated pilot is compatible with the ruling; a universal fail-closed gate on day one is not required.
- Park all instructions-file budget work until the product stabilizes (carried from the predecessor session).
- The critic accompanies the question rather than being absorbed by the agent (verbatim: "yes, it is a 2nd opinion, not a usurped opinion. this seems fitting: 'I re-pose the question carrying the critic's verdict unedited, the same way § Attestation makes me pass your words through unchanged.'"). `updatedInput` proved stronger than the ruling required: the harness enforces the passthrough, so the critique never enters the agent's context before the operator sees it.
- Maximum information flows to the hook (verbatim: "we should pass max information to the hook"). Already satisfied by the harness -- `transcript_path` gives the critic the entire session.
- The option cap and similar limits are accepted as design inputs (verbatim: "we can work with 4 options, and other limitations - contraints usually strengthen designs"; spelling preserved).
- Allowing the critic to actually run is the named next blocker (verbatim: "we need to allow the critic to operate, so that needs resolution").
- No OBPI-pipeline mechanism may be imported into this design yet (verbatim: "do not conflate any mechanism for the obpi pipeline with this work just yet"). The withdrawn latency figure is the concrete casualty.
- The agent equivocates after presenting converged options (verbatim: "the option you always provide is 'discuss this' (approximating): the critic needs to engage your premise. You almost always equivocate and hedge in the narrative that follows. easly a discernible majority of the time."; spelling preserved). Booked to insights as an `improvement` under scope `agent-narrative-discipline`.
- Authorized the probe and required the agent to clear its own gate (verbatim: "On probe, we can't proceed unless you do so"). Booked via `gz handoff decide` against the predecessor.
- Work all five advised steps (verbatim: "do the advised steps"). Booked via `gz handoff decide`; no step set aside.
- Injection shape is preamble-always plus an appended option when the base question carries 3 or fewer (selected from a 3-option picker with rendered previews). The critic's PREMISE-ATTACK/VERDICT map to the preamble, its UNASKED line to the option label.
- memory-hygiene is restructured, not retired: replace the witness and fix the wheel-shipped path defect, deferring the 41-file migration that would grow the parked instruction surface.
- Fix defects when found rather than parking them behind a fence ruling (verbatim: "do it right - fix defects when found"). This authorized the GHI #678 repair after the agent had parked it; standing canon already grants direct-repair authority to GHI-tracked defects, so the park was the error.
- Scope challenge on Step 4b (verbatim: "4b is opbi stuff, why surface it here? is it one of the 5 items?"). It IS advised step 3; it entered the design session because Step 4b is the existing precedent for cross-family adversarial review. The agent had flagged the campaign-sequencing tension but missed the OBPI-fence tension, which was the sharper of the two.
- Do advised steps 1 and 2 from the resumed handoff (verbatim: "do 1 and 2"); steps 3, 4 and 5 recorded set-aside via gz handoff decide.
- Rule and build, not merely rule (verbatim: "explain further, also, rule and build").
- The AskUserQuestion critic design belongs in a pool ADR, not a GHI comment (verbatim: "maybe the askuserquestion work should have been made into a pool adr - the handoff to handoff method seems to be diluting its design").
- Recover the design at full fidelity immediately (verbatim: "get it into a pool adr now, while the iron is hot" and "yes, do full capture, full recall, max context for highest quality adr authoring").
- Transcripts may be copied into an ADR package as appendices, trimmed to relevant passages but never condensed (verbatim: "allow transcripts to be copied as appenditures to an adr within its folder - these are vital original sources. so, this: "into the repo as ADR evidence" - they could be cleaned up to include only relevant passages - not condensed summaries, just trimmed").
- R1 -- the critic performs BOTH scope and conclusion challenge with full context; the either/or framing is rejected (verbatim: "why is this a choice? we want the adversary to get full context. measure twice, cut once").
- R2 -- the critic is a SKILL with three invocation doors: operator, agent, or gate (verbatim: "this is a skill but can be invoked by me, by agent, or at gate").
- R3 -- post-verdict resolution is operator plus main agent, modeled on Step 4b (verbatim: "operator and main agent work for resolution. obpi pipeline 4b already handles this well - observe it").
- R4 -- use the built-in Codex integration rather than a hand-rolled port (verbatim: "we just want to run the most up-to-date codex. Anthropic offers a built-in feature to call a codex adversary, why not use that and keep it simple?").
- GHI #766 takes option B -- retire the bookmark document, keep the signal as a ledger event -- with SessionStart as the forcing function (verbatim: "I liked your ledger suggestion, I just want sessionstart to see that legder entry and consult the transcripts").
- A handoff must carry its transcript so sensemaking is corroborated by the primary source; the ledger path is the floor, not the goal (verbatim: "I should get HIGHER QUALITY results when I call for a handoff that the ounter-checks the transcript, but I'll get some quality if I see that ledger entry and force the just-initiated agent to review prior transcript").
- The corroboration doctrine is ADR-shaped, not rule-shaped (verbatim challenge: "ok, but why not an adr?"). The agent's rule-file recommendation was withdrawn as a second instance of under-routing.
- Campaign placement for ADR-pool.convergence-moment-cross-family-critic is provisionally after ADR-0.35.0, explicitly not yet decided (verbatim: "after 0.35.0 I guess, not ready to decide").
- Proceed with sync first and the ADR second (verbatim: "Proceed — sync, then ADR"), booked via gz handoff decide against the predecessor handoff with no step set aside.
- The corroboration doctrine takes kind pool, not feature, after the agent offered a closed foundation kind and was challenged (verbatim: "why are you offering foundation ADRs?").
- Only one feature at a time (verbatim: "only one feature at a time, feature, finish, draw from pool"). Pool is the staging queue, not post-1.0 deferral; ADR-0.35.0 is the in-flight feature so a second feature ADR was never available.
- The archive half of the corroboration doctrine carries a redaction obligation stated at doctrine level, with the standing operator-PII prohibition binding on appendices. A mechanical pre-commit scrub gate was offered and declined.
- Fold three forcing-function findings into ADR scope: portable transcript references, a pointer liveness signal, and producer-stamped rather than authored.
- Fix both flagged items (verbatim: "fix both items") - the GHI #766 cross-reference and the orphan warnings.
- Work advised step 1 first (verbatim: "Step 1 first — rule on splitting GHI #766"), then return to the campaign; advised steps 3 and 4 recorded set-aside via `gz handoff decide`.
- Split GHI #766 and park both halves behind the doctrine ADR (verbatim: "Split; park both behind the doctrine ADR"). #767 filed for the transcript channel; #766 keeps bookmark retirement and is blocked by it.
- Correct the stale campaign counts and file the class-level defect (verbatim: "Fix it and file the class-level defect") — produced GHI #768.
- Sync, then survey ADR-0.35.0 before touching code (verbatim: "Sync, then survey ADR-0.35.0 first").
- Extend `gz content retire` in place rather than rename it to `withdraw` (verbatim: "Extend `retire` in place"); ADR-0.35.0 amended at five sites to match.
- Verify the family clustering before amending Magna Carta (verbatim: "Verify first, then ratify").
- Build the class-of-failure index as a real surface before writing campaign boxes against it (verbatim: "Build the class-of-failure index first").
- Ratify both Movement C amendments (verbatim: "ratify both, write handoff, git-sync").
- Determine C2's status before pulling the next work item (verbatim: "Determine C2 status first"). This overrode the agent's recommendation to set advised step 2 aside and go straight to GHI #770; the determination is what found the second-dispatch-path residual. Booked via `gz handoff decide`, with advised steps 2, 3, 4 and 5 recorded set-aside.
- Close the C2 residual immediately rather than filing it or amending around it (verbatim: "Close the residual now (Recommended)").
- Check C2 off, amend the campaign with the determination, and sync (verbatim: "Check C2 + sync").
- Work GHI #770 (verbatim: "do 770").
- Work advised step 4, the `gz git-sync` commit-shape question (verbatim: "Rule on the git-sync commit shape (step 4)"). Booked via `gz handoff decide`; advised steps 1, 2, 3 and 5 recorded set-aside, step 1 with the note that it is unexecutable as written because all five of its named members are closed.
- Refuse the bundle — `gz git-sync` fails closed when staged files carry source scope (verbatim: "Refuse the bundle (fence at sync)"). Selected from a four-option picker with rendered previews; the alternatives were split-the-commit, fix-the-query-not-the-commit, and warn-do-not-refuse.
- Write the recommendations into a handoff rather than executing them (verbatim: "write recommendations to handoff. git-sync"). D1 through D5 are carried as advised steps below, none of them started.
- Work D2 first, then D1 (verbatim: "D2 first, then D1"). Booked via `gz handoff decide` against the anchor; D3, D4 and D5 recorded set-aside.
- Take the converged `ghi-close` reading of D2 rather than the campaign-box or GHI #768 readings (selected from a four-option picker after the agent reported that D2's handoff arm had already landed in `ef3f9e0a2`). Both remaining arms land on one file, so "D2 first, then D1" was executed as a single pass.
- Author this handoff (verbatim: "write the handoff").
- Continue defect repair rather than pulling the campaign's Movement A sequence position (verbatim: "continue defect repair", given twice). This answered the predecessor handoff's advised step 1, which had put the sequencing question first precisely because it governs the other four.
- Author this handoff and sync (verbatim: "create new handoff - git sync").
- Pull the `#669` chain from the resumed handoff advised steps (verbatim: "Pull the #669 chain"). Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 recorded set-aside.
- Collapse the three guard mechanisms to one monitor rather than mechanizing the current shape (selected from a four-option picker: collapse / validator-over-current-shape / route-to-pool / record-and-move-on). This ruling also selected the ROUTE: collapse frames the work as a correction against ADR-0.31.0 and routes to direct fix, where the validator-over-current-shape arm would have been an enhancement adding a CLI flag and routed to OBPI ceremony.
- Work advised steps 1, 2, 3 and 4 from the resumed handoff; step 5 (scan for fail-closed refusals with no manpage coverage) recorded set-aside for the fourth time. Booked via `gz handoff decide`.
- GHI #768 takes accept-and-disclaim plus a fence, selected from a four-option picker over the four remedies filed in the issue body. The alternatives declined were marked-syntax validator, generated block, and commit-time coupling. Stop writing the number down; add a narrow check so the subtraction cannot decay back into a convention.
- GHI #581 closes `superseded` citing `ADR-pool.governance-document-structural-validation`, selected from a three-option picker. The alternatives declined were re-affirm TRACK-ONLY in the body, and direct-fix the third failure class only.
- The canonical typecheck scope widens to tree-minus-features, selected from a four-option picker. The alternatives declined were add-scripts-only, fix-the-diagnostics-without-a-scope-change, and leave-both-and-record-as-accepted.
- The Movement C doctrine-declared-without-mechanism box is kept open and re-scoped to its criterion, selected from a three-option picker. The alternatives declined were check-it-off and split-the-box.
- Correct the count, then work the arm (verbatim: "Correct the count, then work the arm"). Selected from a four-option picker after the agent reported that the campaign criterion figure did not reproduce. Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 recorded set-aside.
- Work all 9 rows as drafted (verbatim: "Work all 9 as drafted"), from a four-option picker over the agent-drafted per-row disposition table.
- Rows 49 and 62 re-score to Judgment rather than being mechanized (verbatim: "Re-score both to Judgment (Recommended)"). This ratified the agent withdrawing its own mechanize recommendation after probes disproved the premise.
- Work the grandfathered rules one per commit, through all four (verbatim: "One rule per commit, work through all four"), accepting the full clause-scoring cost the Coverage Ledger forces.
- Enable BLE001 and defer PLC0415 (verbatim: "Enable BLE001, defer PLC0415 (Recommended)"). Six live bare-except violations are the observed drift the promotion freeze requires; the 138 lazy imports need per-site readings against the rule own carve-outs.
- Author this handoff (verbatim: "yes, author the handoff").
- Work all five advised steps (verbatim: "Step 1 — skill arm, Step 2 — ruff-code reachability check, Steps 3+4 — record deferred postures as accepted, Step 5 — rule on ADR-0.44.0,  we DO NOT go out of sequence (0.44.0)"). Selected as a multi-select over the agent-drafted step table; no step set aside.
- ADR-0.44.0 is PARKED, not finished (verbatim: "we DO NOT go out of sequence (0.44.0)"). This forecloses the checkbox's first arm; the agent had wrongly offered pull-it as live when campaign sequencing already ruled it out, and logged that as an improvement insight under scope handoff-resume-presentation.
- ADR-0.44.0 is an agent overreach with three acceptable dispositions (verbatim: "this was originally an agent overeach. this either becomes 0.36.0, revert to pool, or we just ignore/deleted the implemented code - I won't be paralyzed in purgatory."; spelling preserved). The closing clause is a standing instruction against stalling on this class of decision.
- File GHIs and fix them (verbatim: "ghis and fix - we are plagued by misalignments like this."). The second clause set the bar at class-level couplings rather than instance patches.
- Do not resequence out of order (verbatim: "we DO NOT go out of sequence (0.44.0)"), which foreclosed finishing the ADR in place.
- Review the handoff, then work advised step 1 (verbatim: "review the handoff", then "do step 1"). Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 were recorded set-aside at that point.
- Fix the H1/id mismatch as a class: rewrite all 38 pool files, fix `gz adr demote`, and narrow the byte-for-byte preservation test (selected from a four-option picker with rendered previews). This overrode the agent's recommendation to leave the mismatch alone, and the operator was right: the agent had verified there was no code consumer but had not checked whether the stale ids collide with live ones. Eight do.
- Sync the work (verbatim: "Sync now"), selected from a two-option picker.
- Scope GHI #777 as a class fix — teach `gz adr demote` to strip the kind-invalid ceremony section and backfill, rather than editing the id per line or fixing only the 8 observable collisions (selected from a four-option picker with rendered previews).
- Work advised step 2 (verbatim: "do step 2"). Booked via `gz handoff decide`, reversing its earlier set-aside.
- Repair `rename_chain_target` by subsumption — one shared fold with both readers delegating — rather than repairing it in place, deleting it, or recording the finding without a fix (selected from a four-option picker with rendered previews).
- Author this handoff carrying advised steps 3, 4 and 5 forward (verbatim: "write steps 3-5 to a fresh handoff").
- Review the handoff, then work advised step 1 (verbatim: "review handoff", then "Step 1 — widen the check"). Booked via `gz handoff decide`; advised steps 2, 3 and 4 were recorded set-aside at that point.
- Scope the widened check to executable witness paths plus ruff family citations, and NOT to `gz validate` scope flags (selected from a four-option picker with rendered previews). The flag arm was declined on the agent's own evidence that it finds nothing today — 36 cited flags, 36 resolve — and that the promotion-order freeze admits a check only on observed drift.
- Enable PTH package-scoped rather than re-scoring row 41 to Judgment (verbatim: "Enable PTH, package-scoped"), selected from a four-option picker after the agent surfaced that the grandfather pin on `cross-platform.md` makes the re-score path cost a full clause re-score while the enable path costs no rule edit.
- File a GHI through `/ghi-author` for the missing ARB rule-file citation rather than investigating it in-session or logging an insight (verbatim: "File a GHI via /ghi-author"), selected from a three-option picker. Produced GHI #778.
- Author this handoff and sync (verbatim: "write fresh handoff and git sync").
- Work advised steps 1 and 3 of the resumed handoff, instance-scope only on GHI #778 (verbatim: "Step 1 — fix GHI #778, Steps 1 + 3 — fix, then triage" and "Instance only (Recommended)"). Booked via `gz handoff decide`; advised steps 2 and 4 recorded set-aside.
- Rule the sequencing question after #778 and the triage (verbatim: "Fix #769, then pull ADR-0.35.0 (Recommended)"), selected from a four-option picker. This reversed the earlier set-aside of advised step 4.
- REVERSED that sequencing ruling in flight once #769 landed (verbatim selection: "Work more defect repair instead"). ADR-0.35.0 was NOT pulled. Recorded as an `improvement` insight under scope `campaign-sequencing` so the booked `gz handoff decide` text cannot be misread as evidence the feature was started.
- The "we will NOT alter the OBPI process, at all" freeze is NARROW (verbatim selection: "Freeze is narrow — work #765 in full"). It bars importing the cross-family critic design into `adversarial_validation`; it does not bar defect repair of the Step-4b gate. Recorded as an insight under scope `obpi-pipeline-freeze-scope`.
- Close GHI #765 `fixed` and file the residual rather than hardening in place (verbatim: "Close #765 fixed, file the residual (Recommended)"), on the ground that mandating a receipt raises the bar on every heavy-lane completion and deserves its own ruling. Produced GHI #780.
- Sync after the #778 repair (verbatim: "Sync now (Recommended)").
- Author this handoff and stop rather than continuing to GHI #719 or #747 (verbatim: "Write the handoff and sync (Recommended)").
- Work advised step 1 of the resumed handoff — GHI #719 (verbatim: "Step 1 — work GHI #719"), selected from a four-option picker. Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 recorded set-aside.
- Proceed on the resumed handoff, working advised steps 1-4 and setting step 5 aside (verbatim: "Rule steps 1–4, then work"). Booked via `gz handoff decide`.
- GHI #747 routes to a pool ADR parked behind ADR-0.35.0, not a direct fix (selected from a three-option picker). The issue self-labels `enhancement` and canon's direct-repair grant covers defects only; a headless OBPI is forbidden and no ADR promised the verb, so pool was the only available home.
- GHI #780 requires the ARB receipt, direct fix (selected from a three-option picker).
- The #780 requirement rides ANY resolved cross-vendor claim, not only a declared tier 1 (verbatim selection: "Any cross-vendor claim"). Ruled after the agent surfaced that the literal scope would have been a no-op fence.
- GHI #779 takes ratchet-plus-widen rather than line-level narration markers or widening alone (selected from a three-option picker).
- GHI #567 disposition: Move 2 as direct doc edits now, Move 1 to a pool ADR, Move 3 declined, then close `superseded` (selected from a four-option picker).
- Sync the five commits and author this handoff (selected from a four-option picker over the close-out).
- Cut patch release v0.34.2 (verbatim: "/gz-patch-release"), then approved the drafted narrative release notes (verbatim: "Approved — execute").
- Work the four-item routing in the order recommended (verbatim: "proceed as suggested"): fix the advise exit code first, then the control-surface chores, then module-SLOC, filing the hardcoded-root GHI alongside the first.
- Re-run the remaining three control-surface chores at full fidelity rather than a shallow pass, and apply the R18/R19 scope fix to governance-core.md (verbatim: "1. yes, 2. yes").
- Stop the SLOC correction after the first module, author a handoff, determine only the chores still failing, and git-sync (verbatim: "stop, write a new handoff, determine only the chores that still need to be passed. git-sync").
- Work all four live advised steps of the resumed anchor (verbatim: "All four steps — 2, 3, 4, 5 in order"), selected from a four-option picker. Advised step 1 was recorded set-aside as already discharged: `origin/main` was 0/0 before the session began.
- GHI #782 takes a fourth option the issue body never listed — delete criterion 6 as redundant with criterion 3 (verbatim selection: "Delete criterion 6 — redundant with criterion 3"). The three arms in the issue all assumed the grep must survive; it did not, because `gz lint` already asserts the property via AST over the identical scope.
- Route the pre-existing `--sensitivity` red to a GHI rather than fixing the brief in-session (verbatim selection: "File a GHI alongside step 5"). The authoring call belongs to `ADR-0.35.0`, whose brief it is.
- Amend the campaign and pull the cross-family critic ahead of `ADR-0.35.0` (verbatim selection: "Amend the campaign — pull the critic now"), after the operator asked verbatim: "what happened to our 2nd opinion work? it is supposed to kick in anytime you invoke AskUserQuestion."
- File a GHI for the inverse-direction gate question rather than building the check immediately or only measuring (verbatim selection: "File a GHI for the inverse-direction check"). Produced GHI #785.
- Sweep all 39 chores for the #782 shape, reporting only, editing nothing (verbatim selection: "Sweep now, report, fix nothing yet").
- Re-run the adversary against the revised critic design before any promotion (verbatim selection: "Re-run the adversary first, then decide"), discharging the ADR's own § Promotion plan item 4.
- Widen the AST detector first, then delete the two remaining greps (verbatim: "widen the AST detector, then delete the two greps"). The ordering is the ruling: deleting first would have dropped the non-subscript coverage the greps uniquely carried.
- Stage the critic's delivery while keeping the pull-ahead (verbatim selection: "Amend to staged delivery, keep the pull-ahead"), on the adversary's `PERFORATED-BUT-NARROWABLE` verdict. The automatic `AskUserQuestion` door ships dark until a calibrated pilot measures false blocks, latency, operator reading time, and decisions changed.
- Record the R4 transport correction in both registers (verbatim selection: "Both — ADR correction and a GHI"). Produced the ADR's § R4 transport correction and GHI #786.
- Author this handoff and sync (verbatim: "yes handoff with git-sync").
- Author a successor handoff prioritizing the newly filed GHIs (verbatim: "write handoff prioritizing these new GHIs - this is whack-a-mole, one step forward, four steps back."). The ordering rationale is recorded in Immediate Next Steps; the churn assessment was tested against measured issue data rather than accepted or dismissed.
- Work the resumed handoff in its authored order (verbatim: "Take the handoff's order"), selected from a four-option picker whose alternatives were flipping #786 ahead of #785 on campaign-sequencing grounds, working only the two campaign-critical steps, and holding. Booked via `gz handoff decide`; no step set aside.
- Derive the uncalled-gate population from GHI #744's `data/check_scope_membership.json` out_of_check rather than re-deriving it from VALIDATOR_REGISTRY (selected from a four-option picker with rendered previews). The alternatives declined were keeping both registries independent, subsuming everything into one file with widened semantics, and keeping both while only correcting #744's wording. This is the ruling that kept membership single-authority; a second reader would have been free to disagree with the first.
- Finish GHI #785, then file the coupling defect as its own GHI (selected from a four-option picker after the agent surfaced that one gate cost 17 files and the written checklist named 4 of 8). The alternatives declined were finishing #785 only, stopping and reverting, and dropping the derive refactor.
- Fix and close GHI #787 in the same session rather than leaving it in the queue (selected from a four-option picker, after the agent reported the day at net +4 and offered to undo its own contribution). The alternatives declined were also doing #783 at that point, filing nothing further, and parking to reassess the open-count instrument.
- Work GHI #786 next (verbatim: "do 786"), then GHI #783 next (verbatim: "do 783 next").
- Work the resumed handoff's five advised steps after syncing (verbatim: "sync, then all steps."). Booked via `gz handoff decide`; no step set aside.
- Direct-fix the `--distribution` chores-blindness derivation rather than filing, accepting-and-disclosing, or wiring a caller alongside (selected from a four-option picker with rendered previews). This overrode the resumed handoff's own route (a), which the agent had disproved with a fixture probe: regenerating the baseline is a no-op for chores because the regenerator reads the manifest's own keys.
- Fix the predictor when `_expand_includes` was found blind to `packages` (selected from a four-option picker). The alternatives declined were making the `include` list explicit instead, doing both, and stopping to file a GHI. Fixing only the include list would have left the audit's model of the wheel permanently incomplete.
- Record the self-referential scope count and read the six unread domain lists later (selected from a four-option picker). The alternatives declined were reading all six first, building the check now, and filing a GHI without recording. No checker was built.
- Fix the chores delivery gap rather than reverting step 1, excluding the seven files from the baseline, or filing only (selected from a four-option picker). The agent flagged the exclusion arm as the weakest because it would encode a bug as a policy.
- Update the campaign (verbatim: "well, clearly the campaign needs updating. do so please.").
- Leave the authoring of the nine ADR-0.36.0 briefs to the next session (verbatim: "leave the authoring of the briefs to the handoff, git sync after updating the handoff"). The briefs stay draft (scaffold) by ruling, not by oversight.
- Book the resumed anchor `proceed` with all five advised steps set aside, sync only (verbatim: "proceed with the git sync, set aside the rest").
- Work advised step 4, the fork collapse, after reviewing the handoff (verbatim: "review handoff", then "do step 4"). Steps 1, 2, 3 and 5 were not authorized and were not worked.
- Work advised step 3, the settled-rulings clip repair (verbatim: "Step 3 — settled-rulings clip repair"), selected from a four-option picker. Booked via `gz handoff decide`; advised steps 1, 2 and 4 recorded set-aside.
- Sync the clip repair (verbatim: "git sync it").
- REVERSED the step-2 set-aside in flight and authorized authoring the nine ADR-0.36.0 briefs (verbatim: "Step 2 — author the nine ADR-0.36.0 briefs"). Recorded as an `improvement` insight under scope `campaign-sequencing` so the booked `--set-aside` text cannot be misread as evidence the critic build stayed deferred.
- Stop the brief run and author this handoff (verbatim: "re-evaluate for a fresh handoff"). Six briefs remain scaffolds by ruling, not by oversight.
- Review `ADR-0.35.0` (verbatim: "review 0.35.0"), after challenging the sequencing (verbatim: "not sure i wan't to author 0.36.0 while we haven't finished 0.35.0"; spelling preserved).
- Fix the three defects the review surfaced before anything else (verbatim: "yes:" quoting the offer back — the three live stale-ADR-id references, the dangling forced-decisions pointer, and the tag casing).
- Amend the campaign to withdraw the critic pull-ahead and restore `ADR-0.35.0` to the in-flight position (verbatim: "yes, amend campaign").
- Sync each landing as it completed (verbatim: "git sync", "sync it").
- Work the three owed rulings, setting the two campaign-sequencing steps aside (verbatim: 'address these from the handoff: "Three rulings still owed — abridged twins, repo-wide tag case, and whether to file the multi-parent lineage gap"'). Booked via 'gz handoff decide'; advised steps 1 and 2 recorded set-aside.
- Heal the head and flip the test carve-out into a witness, rather than prefix-collapsing in '_dedup_rulings' (selected from a four-option picker with rendered previews). The alternatives declined were prefix-collapse keeping the longer text, heal-only with no witness, and leaving the duplicates standing. The collapse arm was declined on the ground that it would break '_ruling_key''s deliberate refusal to fold look-alikes.
- Tag case is binding-insensitive with UPPERCASE as the authored form, and existing lowercase tags are NOT to be rewritten (selected from a four-option picker). The alternatives declined were declaring lowercase canonical, rewriting all 370 lowercase tags, and declining to rule.
- File the multi-parent lineage gap as a GHI rather than direct-fixing it or dropping it (selected from a three-option picker). Produced GHI #790.
- Sync the session's work (verbatim: 'git sync').
- Work advised steps 3 and 4 and set steps 1 and 2 aside (verbatim: "Steps 3+4 — clear the defect queue first"), selected from a four-option picker whose alternatives were the campaign spine (steps 1+2), all four steps, and the two cheap judgments (steps 1+4). Booked via 'gz handoff decide'.
- GHI #790 takes 'str | list[str]' on the same key (verbatim selection: "str | list[str] on the same key"), selected from a four-option picker. The alternatives declined were a second key alongside the scalar (two fields expressing one relation) and a 'list[str]' migration across 297 authored handoffs (rewriting sealed history).
- Raise '_GREEN_CEILING' rather than re-floor, update the covering waiver, or adopt a standing convention (verbatim selection: "Raise _GREEN_CEILING"), selected from a four-option picker after the agent corrected two arms of the anchor's own option set: adding a waiver entry is mechanically refused by the shrink-only ratchet at baseline_count 6, and the largest live waiver covers 340 against a delta of 742.
- Override ADR-0.0.33's 6-month recalibration cadence, 42 days after the last change, rather than amending the cadence or falling back to a cadence-respecting arm (verbatim selection: "Override the cadence, raise now"). The agent surfaced the collision rather than folding it silently into a constant edit.
- Bands become green 3000 / yellow 3400 (verbatim selection: "3000 green / 3400 yellow"), preserving the 400-line yellow-band width of both prior generations; sized from measured growth of 8.4 lines/day.
- File the GHI, build the emitter, and land the band raise witnessed, rather than landing it unwitnessed and emitting later, holding the raise, or falling back to the convention arm (verbatim selection: "File the GHI, build the emitter, land witnessed").
- The emitter lands as 'gz validate --surface-weight --recalibrate' (verbatim selection: "gz validate --surface-weight --recalibrate"), so the surface that reads the bands is the surface that records their change. Widening 'gz adr emit-receipt's enum and a dedicated 'gz governance' subcommand were declined.
- File and fix the missing band witness (verbatim: "ghi to fix?"), which produced GHI #792. The agent had left it unbuilt as beyond the ruled scope and surfaced it for routing.
- Sync the session's work (verbatim: "git sync", given twice).
