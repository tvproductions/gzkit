---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-14T00:53:56Z'
agent: claude-code
session_id: b2b4db78-34d0-40f3-9c26-e0b6766287c7
continues_from: .gzkit/handoffs/20260813T234120Z-rtd-fixed-and-gzkit-org-found-to-be-a-separate-stale-vps.md
---

## Current State Summary

Resumed `.gzkit/handoffs/20260813T234120Z-rtd-fixed-and-gzkit-org-found-to-be-a-separate-stale-vps.md` (Fresh). Every claim it made was verified against Layer-2 before presentation; all verified TRUE except one detail in step 6 (see Important Context). The operator ruled steps 3 and 4, setting aside 1, 2, 5 and 6. Both ruled steps are COMPLETE and pushed; the tree is clean at `b57f8ffcd`.

STEP 3 — the broken verification line is corrected at BOTH sites, not just the anchor the predecessor named. Two handoffs prescribed a `grep -c undeclared_accepted` check against `data/exemption_control_grandfather.json` expecting 71; it returns 1, because that string is a measurement key whose VALUE is 71, not a per-entry field. Replaced with `jq '.accepted_claims | length'`, verified returning 71. The broken form is named in place rather than deleted.

STEP 4 — first drain pass against the GHI #797 inventory. Eight gates were read end-to-end, found to carry no admit path, declared `exempts='none'`, surrendered from the accepted list, and `baseline_count` decremented 71 to 63 in the same commit. The validator flagged exactly those eight as stale acceptances before removal, no more and no fewer. A further 46 claims had their admit path read or located and were deliberately NOT declared; 17 were not reached. All of it is recorded in `docs/governance/exemption-control-triage.md`.

The pre-push module-size gate then refused the drain commit: the edit took `_qc_negative_controls.py` to 1040 SLOC against a 1031.9 band. Split by cohesion into `_qc_claim_exemptions.py` rather than grandfathered — the gate's own refusal names grandfathering as the laundering ADR-0.0.73 Boundary Invariant #8 forbids, which is the invariant the drain serves.

The campaign spine was NOT worked. `ADR-0.35.0` remains 0/10, every brief pending and draft, set aside for a FIFTH consecutive session by explicit ruling.

## Important Context

THE BAR FOR DECLARING AN EXEMPTION-FREE GATE IS RECORDED IN CODE, and the next pass must apply the same one or the counts stop meaning anything. A claim is declarable only when no input makes its gate ADMIT an item it has judged in violation. Waiver and grandfather tables, `excluded` lists, escape markers, opt-in arms and authorization bookings ARE exemptions. Scope predicates (which artifacts a gate examines), threshold parameters (a budget defines what a violation is), artifact-absent returns and error paths are NOT. The bar and its rationale live in the `_qc_claim_exemptions.py` module docstring.

MEMBERSHIP IS A READING, NEVER A SCAN. Two heuristics have already failed this exact question in this repo — a naming-convention scan matched 0 of 70, and claim-id-to-module-stem correlation matched 7 of 71. A grep for waiver tokens was used ONLY to locate candidates for reading, never to decide one. Seventeen claims are left explicitly unclassified rather than inferred; do not close them from a scan.

THE ADVISED STEP CONFLICTED WITH A BOOKED RULING, and the conflict is priced, not resolved. The handoff advised draining all 71. `exemption_controls.py` records the operator's 2026-08-12 ruling that the module is INVENTORY AND DISCLOSURE, NOT ENROLLMENT, and that writing controls for all 70 at once is the backlog-draining the `advisory-rules-audit` promotion freeze declines to fund. Roughly 46 of the remaining 63 claims need a NEW differential control before they can declare truthfully, which is enrollment. A future pass that starts writing controls needs a fresh operator ruling.

MODULE-SIZE HEADROOM IS NEARLY GONE at the drain's own site. `_qc_negative_controls.py` now sits at 1015 SLOC against a 1031.9 block band — 17 SLOC of room. It was at 1012 before this session, so the tightness is pre-existing, not introduced here. The next addition to that file will trip the pre-push gate. Add to `_qc_claim_exemptions.py` (28 SLOC) instead, or split again by cohesion. Do not grandfather it.

STEP 6 OF THE RESUMED HANDOFF CARRIED ONE FALSE DETAIL, and it strengthens rather than voids the step. It asserted that no new floor bookmarks were produced and the instance count did not grow. `20260814T000023Z-session-exit-bookmark.md` was written six minutes AFTER that handoff and is boilerplate-identical to its two predecessors (1753, 1753 and 1765 bytes). GHI #766 therefore has one more instance than it did.

THE MAINTENANCE RATIO WAS MEASURED THIS SESSION and is unruled. Last 30 days on main: 592 commits — 260 `fix`, 232 `chore`, 74 `docs`, and 13 `feat`. 116 GHIs filed, 112 closed. Every gate green throughout. The agent recommended abandoning the triage for the campaign spine on that evidence; the operator reaffirmed the triage. The measurement is recorded because it is the context for why step 1 keeps losing, and no ruling was sought on the ratio itself.

## Decisions Made

- [operator-ruled] Work advised steps 3 and 4 only (verbatim selection: "Steps 3+4 — the two cheap defect fixes"), chosen from a four-option picker whose alternatives were the campaign spine (step 1), pulling GHI #766 (step 6), and booking a hold. Booked via `gz handoff decide` with steps 1, 2, 5 and 6 recorded `--set-aside`.
- [operator-ruled] Finish the 71-gate triage rather than abandon it (verbatim: "Finish the 71-gate triage as ruled"), reaffirmed AFTER the agent measured the 83 percent maintenance / 2.2 percent feature commit ratio and recommended switching to the campaign spine. The reaffirmation is the ruling; the measurement stands as recorded context.
- [operator-ruled] Triage all 71 and declare only the honest exemption-free gates (verbatim selection: "Triage all 71, declare only the honest 'none's"), chosen over a measurement-only pass, a full drain including new controls, and filing a GHI about the routing conflict.
- [operator-ruled] Commit and git-sync before authoring this handoff, accepting that the handoff itself then needs a second sync (verbatim: "commit and git-sync first, then author the successor handoff against a clean tree, but that will require a follow on git-sync").
- [agent-chose] Correct the broken verification line in BOTH handoffs carrying it rather than only the anchor the predecessor named, since the line had already propagated once and the instance is not the class.
- [agent-chose] Name the broken form in place rather than delete it, following the 2026-08-13 `.readthedocs.yaml` precedent: a wrong instruction that vanishes is indistinguishable from one never written.
- [agent-chose] Declare only the eight claims whose gates were read end-to-end, and leave 17 explicitly unread rather than infer them from a token scan. The asymmetry is deliberate: a wrong declaration launders an admit path, while an absent one costs only a later reading.
- [agent-chose] Put the declarations in a named map beside the registration table rather than a fifth positional column, because `expect` is already optional and a positional slot would scatter the judgment across 70 rows behind `None` placeholders.
- [agent-chose] Split the oversize module by cohesion rather than take the available grandfather waiver, on the ground that waiving a size gate to land a commit about not taking waivers would have been the defect.
- [agent-chose] Re-classify the three reported "findings" as observations after the operator challenged the label, and correct the triage document in place — the measurement that settled it (56 QC steps registered, dozens of scopes unenrolled) showed the `--type-ignores` gap was not the singular hole it had been written as.

## Immediate Next Steps

1. PULL OBPI-0.35.0-01-corpus-tombstone-schema-and-fold. The campaign spine, Magna Carta by operator canon, and the topmost Movement A item whose gate is met. Now set aside FIVE sessions running, every time by explicit ruling rather than neglect, and both set-aside lists are on the ledger with the operator's words attached. Verified live this session as unstarted: `gz adr status` reports 0/10 with every brief pending and draft. Read the fold algebra from the ADR's Decision section rather than re-deriving it, and run `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for the landed count rather than trusting any figure transcribed here.
2. ATTACH GZKIT.ORG TO GITHUB PAGES, THEN CLOSE GHI #802. Unchanged and still operator-only. Verified live this session: `https://gzkit.org/config/gz-cookiecutter-python-stack/` returns HTTP 404. Two credentialed steps: GitHub Pages settings with custom domain gzkit.org, then registrar DNS repointing gzkit.org and www off 68.183.108.119. Closing evidence needs no credentials.
3. CONTINUE THE EXEMPTION DRAIN FROM THE TRIAGE, NOT FROM SCRATCH. `docs/governance/exemption-control-triage.md` names the bar, the located admit path for 46 claims, and the 17 not reached. The cheap remaining work is reading those 17 and declaring any that are genuinely exemption-free. Do NOT start writing differential controls without a fresh ruling; that is the enrollment the 2026-08-12 ruling declined.
4. CONSIDER WHETHER GHI #766 SHOULD BE PULLED. The floor bookmark produced another boilerplate-identical instance this cycle, so the issue's evidence is one instance stronger than when it was last considered.
5. AFTER ADR-0.35.0 OBPI-05 AND OBPI-07 LAND, WORK GHI #799. Unchanged and still correctly gated. Do not attempt it earlier, and do not score clauses 1, 2 or 3 as Judgment to make them fit.

## Pending Work / Open Loops

- SEVENTEEN CLAIMS UNREAD in the exemption inventory, listed by name in the triage document under Tier B. They are unclassified, not classified-as-clean; declaring any of them requires reading its gate first.
- ROUGHLY 46 DIFFERENTIAL CONTROLS OWED before the disclosed list can shrink further. Each proves its gate refuses without the exemption and admits with it, the shape the two existing exemplar controls already use. This is enrollment and needs an operator ruling before it starts.
- THE MAINTENANCE RATIO IS UNRULED. 260 fix, 232 chore, 74 docs and 13 feat commits over 30 days, with every gate green. Recorded as a measurement; no ruling was sought on whether it should change how sessions are spent.
- MODULE-SIZE HEADROOM at `_qc_negative_controls.py` is 17 SLOC against the block band. Pre-existing, not introduced this session, and it will refuse the next addition to that file.
- FIVE CLAIMS INHERIT THEIR EXEMPTION FROM AN EXTERNAL TOOL (lint, format, typecheck, test, behave) whose escapes are ruff, ty, unittest and behave surfaces rather than gzkit ones. Worth deciding once as a family rather than five times.
- `gz validate --type-ignores` already polices the typecheck gate's suppression escape but carries no enforcement claim, so it cannot be named as that gate's control. Recorded as an option, NOT a defect: dozens of explicit-only validate scopes are in the same state and the QC registry holds only 56 steps.

## Verification Checklist

uv run gz validate --exemption-controls          # exit 0; 76 inventoried, 13 declared, 63 disclosed
uv run gz validate --waiver-ratchet              # exit 0; baseline_count 63 matches the live list
jq '.accepted_claims | length' data/exemption_control_grandfather.json   # 63
uv run gz validate                               # exit 0, 13 default scopes
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing   # read the landed count from Layer-2, expect 0/10
git rev-list --left-right --count origin/main...HEAD         # expect 0 0 after the follow-on sync
gh issue view 802 --json number,state            # OPEN, operator-only remedy
gh issue view 766 --json number,state            # OPEN, one instance stronger this cycle

## Evidence / Artifacts

`docs/governance/exemption-control-triage.md`
`src/gzkit/governance/trust_audits/_qc_claim_exemptions.py`
`src/gzkit/governance/trust_audits/_qc_negative_controls.py`
`data/exemption_control_grandfather.json`
`data/waiver_ratchet_registry.json`
`.gzkit/handoffs/20260813T104754Z-gate-mapping-fixed-recovery-prose-corrected-and-rtd-freeze-found.md`
`.gzkit/handoffs/20260812T104530Z-three-rulings-cleared-draft-holds-and-two-blockers-filed.md`
`.gzkit/ledger.jsonl`
`artifacts/receipts/arb-step-unittest-0d269f001f7e4dd986fbe14d6b130ba0.json`
`artifacts/receipts/arb-ruff-4647d5cc9b1345409ef487a38f256c1c.json`
`artifacts/receipts/arb-step-typecheck-9433095368254ba89fc69fb2508c93e6.json`
`artifacts/receipts/arb-step-mkdocs-492123fcd2584b76b12bdf4dfe5adc38.json`

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
- Work advised step 1 only, with the operator applying the RTD toggle and the agent closing the issue (verbatim selection: "Step 1 — you flip RTD, I close #801"), chosen from a four-option picker whose alternatives were the campaign spine (step 2), the two cheap defect steps (steps 3+4), and booking a hold. Booked via gz handoff decide with steps 2, 3, 4, 5 and 6 recorded --set-aside.
- Report the missing toggle rather than let the agent's instruction stand (verbatim: "i don't see this: 2. Recommended while you're there: Settings → uncheck \"Build versions automatically\""). This course-correction is the sole reason the topology error was found; the flip alone would have closed #801 with the false premise intact.
- Close #801, correct the doc, and file the VPS gap as its own GHI (verbatim selection: "Close #801, fix the doc, file the VPS gap (Recommended)"), chosen from a four-option picker. The alternatives declined were redeploying the VPS by hand this session instead of tracking it, holding #801 open until both front doors were current, and closing #801 while leaving both the false premise and the staleness untracked.
- Author this successor handoff (verbatim: "write successor handoff").
