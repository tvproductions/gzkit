---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-13T23:41:20Z'
agent: claude-code
session_id: 7a42c385-e8e8-4624-8595-d0328b0cac43
continues_from: .gzkit/handoffs/20260813T113311Z-resume-gate-compound-admission-reversed.md
---

## Current State Summary

Resumed the 2026-08-13 resume-gate anchor, reviewed it, verified every claim against Layer-2, and booked a proceed ruling working advised step 1 only with the other five set aside. Step 1 was the RTD default-version flip: the operator applied it at 11:55:27Z and GHI #801 is CLOSED on verified before/after measurement. Chasing a toggle the operator could not find then disproved two premises the issue and .readthedocs.yaml both carried. gzkit.org is NOT a Read the Docs custom domain and never was, so the RTD flip could never have unfrozen it; it is a self-hosted DigitalOcean VPS deployed by hand and stale since 2026-05-28. That gap is filed as GHI #802, open by credential boundary with a blocker comment. Landed at 36966b1e7; origin/main is 0/0 and the tree is clean. The campaign spine, ADR-0.35.0, was NOT pulled and is now set aside for a fourth consecutive session, every time by explicit ruling.

## Important Context

GZKIT.ORG AND READTHEDOCS ARE TWO UNRELATED SYSTEMS AND THE REPO NOW SAYS SO. gzkit.org resolves to 68.183.108.119 (DigitalOcean) and serves no versioned path structure at all: both /en/stable/ and /en/latest/ return 404. An RTD custom domain always serves that structure, so one request settles it. It is a self-hosted Caddy VPS whose deploy is a manual git pull plus mkdocs build, documented at docs/developer/deployment.md:3 and :60-68. No edit to .readthedocs.yaml and no RTD dashboard toggle reaches it.

THE FALSE PREMISE CAME FROM ONE RESPONSE HEADER. server: Caddy was read as an RTD identification. RTD does run Caddy, and so does any self-hosted Caddy box. From that inference the claim propagated into .readthedocs.yaml:16, GHI #801's body, and both predecessor handoffs, each citing the one before it rather than the wire. The correction is now recorded in .readthedocs.yaml with the discriminator named, so the next reader gets the verified surface.

THERE IS NO BUILD VERSIONS AUTOMATICALLY SETTING IN READ THE DOCS. .readthedocs.yaml step 2 instructed unchecking one and the API v3 project object exposes no such field; RTD governs version building through Automation Rules, where any enabled rule carrying a build action gates builds. The cancelled-build stream, 1383 recorded and counting, therefore stops via an automation rule (match=tag, version-type=tag) and not a checkbox. This is now item 3 of the corrected runbook.

GITHUB PAGES ALREADY SOLVES GHI #802 AND IS SITTING UNUSED. tvproductions.github.io/gzkit/ is live, built at v0.34.3 on 2026-08-12, auto-deploys on every release via .github/workflows/docs.yml, and serves the exact page gzkit.org 404s. Its cname is null, so no domain is attached. The recommended remedy is to attach gzkit.org to Pages and retire the droplet, which deletes the failure mode instead of automating around it. Do not build a staleness monitor for a surface that can simply stop being manual.

THE HANDOFF-RESUME GATE WORKS AS THE ANCHOR DESCRIBED, WITNESSED TWICE IN FLIGHT. A three-segment && chain of admitted reads ran as-is, which the pre-2026-08-13 predicate would have refused on shape. A later command carrying 2>&1 was refused with the offending part named as 1, exactly the boundary the anchor documents as deliberately still refused. Neither was a defect and neither needs filing.

READ THE FOLD ALGEBRA FROM THE ADR, NOT FROM MEMORY. For OBPI-0.35.0-01 the ADR's Decision section specifies a single reverse pass and never a fixpoint iteration, and unset tombstone fields MUST be omitted from serialization or corpus_fingerprint re-fingerprints the whole corpus on the landing commit.

## Decisions Made

- [operator-ruled] Work advised step 1 only, with the operator applying the RTD toggle and the agent closing the issue (verbatim selection: "Step 1 — you flip RTD, I close #801"), chosen from a four-option picker whose alternatives were the campaign spine (step 2), the two cheap defect steps (steps 3+4), and booking a hold. Booked via gz handoff decide with steps 2, 3, 4, 5 and 6 recorded --set-aside.
- [operator-ruled] Report the missing toggle rather than let the agent's instruction stand (verbatim: "i don't see this: 2. Recommended while you're there: Settings → uncheck \"Build versions automatically\""). This course-correction is the sole reason the topology error was found; the flip alone would have closed #801 with the false premise intact.
- [operator-ruled] Close #801, correct the doc, and file the VPS gap as its own GHI (verbatim selection: "Close #801, fix the doc, file the VPS gap (Recommended)"), chosen from a four-option picker. The alternatives declined were redeploying the VPS by hand this session instead of tracking it, holding #801 open until both front doors were current, and closing #801 while leaving both the false premise and the staleness untracked.
- [operator-ruled] Author this successor handoff (verbatim: "write successor handoff").
- [agent-chose] Probe the versioned path structure against gzkit.org rather than relay the anchor's RTD-custom-domain premise. The premise had survived three sessions because nobody issued the one request that distinguishes an RTD custom domain from any other Caddy host.
- [agent-chose] Record the Behavior Rule 11 improvement insight under scope rtd-front-door-topology BEFORE completing the corrected work, naming both faults: recommending a dashboard toggle without verifying the runtime surface, and relaying an unverified premise the repo's own deployment doc contradicted.
- [agent-chose] File GHI #802 as a new issue rather than reopen #801. The two are different systems with different causes and different credential boundaries; #801's named defect was genuinely fixed and folding a live unrelated defect into it would have kept a closed issue open as a tracker.
- [agent-chose] Recommend attaching gzkit.org to GitHub Pages over automating the VPS deploy, on the ground that Pages already builds and publishes the identical site on every release, so remedy 1 removes a build pipeline while remedy 2 keeps a second one alive for no stated gain.
- [agent-chose] Correct .readthedocs.yaml's admin runbook in place, marking item 1 APPLIED and naming the nonexistent toggle explicitly as nonexistent, rather than silently deleting the bad instruction. A wrong instruction that vanishes is indistinguishable from one never written, and this runbook had already misdirected an operator once.
- [agent-chose] Record both corrections in the #801 close comment rather than only in the file, so the issue's own archive does not preserve two claims now known false.

## Immediate Next Steps

1. PULL OBPI-0.35.0-01-corpus-tombstone-schema-and-fold. The campaign spine and the topmost unchecked Movement A item whose gate is met. Now set aside FOUR sessions running, every time by explicit ruling rather than neglect. Verified live this session as unstarted: gz adr status reports 0/10 with every brief pending and draft, and the ADR at Draft, which the 2026-08-12 lifecycle ruling settled as correct through implementation. Run `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for the landed count rather than trusting a figure transcribed here. Read the fold algebra from the ADR's Decision section rather than re-deriving it.

2. ATTACH GZKIT.ORG TO GITHUB PAGES, THEN CLOSE GHI #802. The operator-only action of this cycle, replacing the RTD flip that discharged it. Two credentialed steps: GitHub Pages settings, custom domain = gzkit.org (a repo settings mutation, prohibited to agents without explicit approval), then registrar DNS repointing gzkit.org and www off 68.183.108.119 to the GitHub Pages apex targets. Closing evidence needs no credentials: curl the last-modified header at the site root and expect a current date rather than 2026-05-28, and curl gzkit.org/config/gz-cookiecutter-python-stack/ and expect 200 where it returns 404 today. Nothing repo-side is outstanding.

3. RULE ON THE ANCHOR'S BROKEN VERIFICATION LINE. Carried forward unruled for a second session. The 2026-08-13 predecessor's checklist prescribes grep -c undeclared_accepted against data/exemption_control_grandfather.json expecting 71; the command returns 1 because the string is a measurement key, not a per-entry field. Re-measured live this session: the working form counts the quoted claim key and returns 71. One-line correction to a superseded handoff, or leave it.

4. DRAIN THE EXEMPTION CLAIMS NOW THAT THE MAPPING EXISTS. The 71 disclosed undeclared claims in data/exemption_control_grandfather.json are unblocked but undrained; re-measured live this session and still 71. Each entry resolves to a named gate through the gz validate --exemption-controls finding itself. Drain by declaring exempts on each claim, either the no-exemption token or the claim id of the control that exercises it, and decrement baseline_count in data/waiver_ratchet_registry.json as entries are surrendered. Do not add entries to silence anything.

5. AFTER ADR-0.35.0 OBPI-05 AND OBPI-07 LAND, WORK GHI #799. The three corpus entries become a generated artifact rather than a hand ceremony at that point; author them, recompose AGENTS.md, then add all six ADR-0.0.33 rows with honest scores. Do not attempt it earlier, and do not score clauses 1, 2 or 3 as Judgment to make them fit.

6. CONSIDER WHETHER GHI #766 SHOULD BE PULLED. Carried forward unchanged. No new floor bookmarks were produced this session, so the instance count did not grow.

## Pending Work / Open Loops

GHI #802 IS OPEN BY CREDENTIAL BOUNDARY, NOT BY OMISSION, and carries a blocker comment naming the two concrete operator actions plus the credential-free closing evidence. The repo-side half is complete: .readthedocs.yaml no longer asserts the false premise and no other artifact carries it. Until the Pages custom domain is attached, gzkit.org continues serving 2026-05-28 content while tvproductions.github.io/gzkit/ serves current.

THE CANCELLED-BUILD STREAM AT READ THE DOCS IS STILL RUNNING, 1383 builds recorded. Item 3 of the corrected .readthedocs.yaml runbook stops it via an automation rule. This is hygiene, not a correctness defect: latest can never build and stable is unaffected. No GHI filed, because it is disclosed in the runbook with the working mechanism named.

THE 71 DISCLOSED EXEMPTION CLAIMS REMAIN DISCLOSED. Re-measured live this session at 71 accepted_claims entries. The shrink-only ratchet keeps the list from growing but nothing shrinks it automatically.

THE EXEMPTION-CONTROLS GATE STILL OWES ITS OWN CONTROL. Its exemption surface is the accepted_claims list; promoting the covering unit tests to a registered exemption control needs the negative-control table to carry an exempts field.

ADR-0.35.0 IS UNSTARTED, with no OBPI landed, now set aside by explicit ruling in each of the last four sessions. Its status is Draft and that is RULED correct through implementation; the Lifecycle column reading Pending is Layer-3 derived from the absence of completion events and is not drift.

GHI #799 IS OPEN AND BLOCKED ON THE CAMPAIGN SPINE, specifically ADR-0.35.0's OBPI-05 corpus-to-candidate generator and OBPI-07 orchestrator.

GHI #766 IS OPEN AND UNCHANGED. This session produced no new floor bookmarks.

REDIRECTION AND 2>&1 REMAIN REFUSED BY THE RESUME GATE and are NOT covered by the 2026-08-13 chaining ruling. Witnessed live this session when a 2>&1 command was refused with the offending part named as 1. This is a declared boundary recorded in the gate module and the skill Trust Model, not a defect awaiting repair.

AGENTS.MD IS STILL OVER THE CODEX DELIVERY CAP at 33153 B against 32768 B. Tracked on GHI #533; reported as an advisory by every gz check. The standing operator ruling parks all instructions-file budget work until the product stabilizes, so this is disclosed rather than actionable.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD          # 0 0
git log --oneline -2                                          # 36966b1e7, e4139a3ed
curl -s https://app.readthedocs.org/api/v3/projects/gzkit/    # default_version now "stable"
curl -s -o /dev/null -w "%{redirect_url}" https://gzkit.readthedocs.io/   # /en/stable/ (was /en/latest/)
curl -s -o /dev/null -w "%{http_code}" https://gzkit.org/en/stable/       # 404 -- gzkit.org is NOT an RTD custom domain
curl -s -o /dev/null -w "%{http_code}" https://gzkit.org/config/gz-cookiecutter-python-stack/   # 404, expect 200 once GHI #802 closes
curl -s -o /dev/null -w "%{http_code}" https://tvproductions.github.io/gzkit/config/gz-cookiecutter-python-stack/  # 200, Pages is current
dig +short gzkit.org                                          # 68.183.108.119 (DigitalOcean, not RTD)
gh issue view 802 --json number,state                         # OPEN, operator-only Pages + DNS
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing    # read the landed count from Layer-2; 0/10, all briefs pending and draft
grep -c "claim" data/exemption_control_grandfather.json       # 71 accepted_claims entries

## Evidence / Artifacts

Source changed this session:

- `.readthedocs.yaml` -- admin runbook corrected: item 1 marked APPLIED, the nonexistent "Build versions automatically" toggle named as nonexistent with Automation Rules given as the real mechanism, and a new paragraph stating that gzkit.org is not an RTD custom domain, with the versioned-path-structure discriminator recorded
- `.gzkit/insights/agent-insights.jsonl` -- improvement insight under scope rtd-front-door-topology
- `.gzkit/ledger.jsonl` -- the proceed ruling with five set-aside records

Surfaces read but not changed:

- `docs/developer/deployment.md` -- the manual VPS deploy runbook; line 3 is the authority that contradicted the RTD premise
- `.github/workflows/docs.yml` -- the release-triggered GitHub Pages build that already publishes current docs
- `mkdocs.yml` -- site_url points at gzkit.org, the stale surface
- `.gzkit/handoffs/20260813T113311Z-resume-gate-compound-admission-reversed.md` -- the anchor

GitHub state changed: GHI #801 CLOSED with before/after evidence and both corrections recorded; GHI #802 filed and left open with a blocker comment.

Commit: 36966b1e7.

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
- Fix the two defects the review surfaced and stop, rather than working the anchor's campaign steps (verbatim selection: "Fix the two defects only, then stop"), chosen from a four-option picker whose alternatives were fix-then-steps-1-and-2, handoff-steps-1-and-2-only, and hold-sync-only. All four advised steps of the resumed anchor were recorded set-aside via `gz handoff decide`.
- Fix GHI #793 (verbatim: "fix 793"), authorizing in flight the third defect the agent had filed rather than fixed under the preceding ruling.
- Run the patch release and nothing else (verbatim: 'Patch release only'), with all five advised steps of the resumed handoff recorded set-aside.
- Approve the v0.34.3 release notes (verbatim: 'Approved'), which started the Iron Law run through Steps 4a-4e without pauses.
- Fix the multi-GHI subject regex immediately and file a GHI for the chore-closure question rather than fixing both (verbatim: 'Fix regex now, GHI the chore rule').
- Resolve GHI #794 by adding the unclassified_reference disclosure bucket rather than widening the closure types (verbatim: 'rule 794 - add the unclassified_reference bucket').
- Close the resume-gate handoff_path coupling gap, lifting the set-aside that item carried from the 'Patch release only' ruling (verbatim: 'first, fix this:').
- Fix the verifier-pipe gate's escape predicate (verbatim: 'fix this:').
- Route the exemption-untested class as disclose-now-enroll-as-it-drains, the gz validate --gate-callers shape, rather than fixing only the two proven gates or writing rule prose.
- Repoint the Read the Docs badge (verbatim: 'fix the badge').
- Work advised steps 1, 4 and 5 of the resumed handoff and set steps 2 and 3 aside (verbatim selection: Steps 1, 4, 5 - clear the owed rulings, no build), chosen from a four-option picker whose alternatives were the campaign spine (steps 1+2), all five steps, and hold-sync-only. Booked via gz handoff decide with both declined steps recorded --set-aside.
- ADR-0.35.0 holds status Draft through implementation and the lifecycle question is CLOSED (verbatim selection: Hold Draft, record the ruling (Recommended)). Advancing to Proposed and advancing to Accepted were both declined. Recorded in the campaign at two sites so the question cannot recur an eighth time.
- The 71-claim exemption drain WAITS behind the claim-to-gate mapping gap, which is filed as its own GHI (verbatim selection: Wait - file the claim-gate mapping gap (Recommended)). Draining the name-identifiable subset now, and recording the backlog while filing nothing, were both declined.
- The advisory scorecard widens to ADR-0.0.33's six anti-pattern clauses (verbatim selection: Widen to ADR-0.0.33's 6 anti-patterns (Recommended)). Stating the exclusion instead was declined, as was widening to the 18 Boundary Invariants sections, which already carry a proof channel via gz validate --req-kind-discipline.
- File a GHI for the blocked half of the widening rather than accepting the recorded prose blocker alone (verbatim selection: Also file a GHI for the blocked widening). Scoring clauses 4, 5 and 6 as a partial table was declined, as was authoring the mirrors immediately via the corpus ceremony.
- Work advised step 2 only and set the other four aside (verbatim selection: "Step 2 only — defect repair, no feature build"), chosen from a four-option picker whose alternatives were the campaign spine (step 1), spine-plus-defect (steps 1+2), and hold-without-working. Booked via gz handoff decide with steps 1, 3, 4 and 5 recorded set-aside.
- Commit the four session-exit bookmarks as-is with the session's work (verbatim selection: "Commit them as-is with the session's work"), chosen over folding them into an authored successor, deleting them, and leaving them staged. They carry no authored content, and leaving them untracked orphans a Layer-2 handoff_path in a fresh clone.
- Fix the verifier-pipe-gate recovery prose by handing back the caller's own command corrected (verbatim selection: "Hand back the corrected command"), chosen from a four-option picker. The alternatives declined were a prose-only reorder, relaxing the gate to permit filter pipes, and recording the ergonomics as accepted.
- Do the RTD fixes (verbatim: "do the RTD fixes"). This reversed the set-aside that advised step 3 had carried, and it was the third session in which that step had been presented.
- File a GHI to track the RTD dashboard half rather than leaving it to an immediate manual fix (verbatim selection: "File a GHI to track it"), chosen over no-GHI and over re-measuring immediately on the assumption it had already been flipped.
- The verifier-pipe gate friction was worth raising at all (verbatim: "tired of this bullshit:" followed by the block message quoted in full). Recorded as an improvement insight under scope guardrail-recovery-prose per Behavior Rule 11 before the corrected work completed.
- Fix the compound-command refusal immediately, at highest priority (verbatim: 'I want this fixed now, highest priority, I can't tolerate this:' followed by the block message quoted in full, then 'do not let this problem persist'). This REVERSES the operator's own 2026-08-12 disposition-1 ruling on the same question.
- Book the resumed anchor as proceed with every advised step set aside, because the session's work was the gate fix rather than any advised step. Booked via gz handoff decide with all five recorded --set-aside.
- Route the fix to a successor handoff (verbatim: 'did you route this fix to a new handoff?'), which the agent had not done — the ruling was booked in the ledger and the commits landed, but no successor document existed, so the anchor still stood as newest with its five steps reading as live.
