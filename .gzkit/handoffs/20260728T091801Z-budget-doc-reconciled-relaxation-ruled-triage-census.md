---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-28T09:18:01Z'
agent: claude-code
session_id: 174f1662-1efa-4e0b-aba3-6cdaa7321122
continues_from: .gzkit/handoffs/20260728T015953Z-607-scoped-airlock-miscitation-fixed-727-728-filed.md
---

## Current State Summary

Session opened as a question about Opus 5 and the Cherny "delete your CLAUDE.md" talk and became a budget-surface repair. Two commits landed on main and are pushed; branch is level with origin/main (0 ahead, 0 behind) and the tree is clean.

`2d55abccd` reconciled the `data/instructions_files_budget.json` `_doc` against its enforced values and retuned the budgets to just-above-measured. `5d6c18e84` reverted that retune on operator ruling and recorded the pre-1.0 relaxation posture with a named exit condition. Enforced values are back to AGENTS.md 50000, CLAUDE.md 15000, .claude/rules/*.md 30000; the ceiling stays 65536.

`uv run gz check` ran green across all 45 gates once per commit. A Behavior Rule 11 course-correction insight was recorded via `gz insights remember`. Evidence added to GHI #727 rather than filing a fifth sibling. A full GHI triage census was rendered: 13 ranked of 13 open, fix() precedent 317 in the 60-day window.

No ADR or OBPI was in flight this session and no OBPI locks were claimed or held.

## Important Context

The budget `_doc` is a chronological ledger living inside a JSON config. Each dated entry states the values true ON ITS DATE; the LAST entry is what is enforced. That reading convention was implicit, which is exactly what failed — a 2026-06-22 entry saying "CLAUDE.md 4000 and .claude/rules/*.md 15000 remain" was read as current when the map said 15000 and 30000. The convention is now written into the entry itself.

The loose budgets are a DELIBERATE PRE-1.0 POSTURE, not drift. The corpus/CMS chain (`gz content remember`, `gz content compose`, land) is the intended control surface for per-turn size and it is not feature-stable: ADR-0.35.0-canon-entry-corpus-landing is Draft at 0 of 9 OBPIs landed, with the corpus-to-candidate generator (OBPI-05) and the `gz content land` orchestrator (OBPI-07) both unbuilt.

Operating principle recorded from that ruling: strictness is earned by the mechanism that discharges it. A gate whose satisfaction path does not exist does not force the work, it blocks it, and then gets widened under pressure. The 2026-06-30 setting of 231 chars (0.7 percent) headroom is the empirical demonstration — it was blown out to 50000 within a week rather than forcing a shrink.

CEILING and BUDGET are different numbers and conflating them cost this session. `_PROJECT_DOC_BUDGET_CEILING_BYTES = 65536` at `tests/governance/test_agents_md_map_doctrine.py` line 66 is the ceiling and IS properly ruled (operator words quoted verbatim in the code comment at lines 58 to 65). The `files` map values are the budgets and were the unrecorded half.

Delivery-channel note: `gz git-sync` bundles derived surface regeneration and its commit template has no slot for why a hand-tuned threshold changed. A deliberate posture therefore arrived on disk indistinguishable from drift. That indistinguishability, not the number, is the defect.

Harness note: the handoff-resume gate refuses compound Bash commands, so a pipe such as `| head` converts a permitted read into a refusal. Use native flags (`git log -n 40`) instead of piping.

Reading warning for this document: the `## Settled Rulings` section below carries TRUNCATED and DUPLICATED entries inherited from the chain (lines 105, 106, 110, 111, 112, 113). Do not read a fragment there as a complete ruling. Detail and verification are in Pending Work.

Session-opening analysis, recorded because it is the most durable output and would otherwise be lost. The session began with the Boris Cherny talk advising operators to delete CLAUDE.md, skills, and hooks every six months and rebuild only what the model demonstrably needs. The conclusion reached, which survives the budget detour:

- That advice targets exactly one content class, CAPABILITY COMPENSATION — lines that exist because a weaker model failed to do what a good engineer does by default ("no vibe coding", "read the code before you change it", "verify observed behavior"). Those are the honest ablation candidates on Opus 5.
- It does NOT cover three other classes present in this contract. PROJECT API FACTS (ledger is Layer-2, canonical ARB invocations, lane rules) are unguessable. OPERATOR CANON THAT CUTS AGAINST TRAINING PRIORS (stdlib-first, unittest over pytest, argparse over click, no feature branches, the PII prohibition) gets WORSE with a smarter model, not better, because the training corpus pulls harder toward pytest and click the more fluent the model is. MECHANISM POINTERS are candidates for deferral behind a discoverable pointer, not deletion.
- The decisive distinction for gzkit: Cherny's remedy is EDITORIAL (delete the lines); gzkit's is ARCHITECTURAL (relocate them — corpus as source, rendition as output). Both produce the same per-turn byte count. Only the second keeps the canon. That means ADR-0.35.0 is already the right answer to the talk, and nothing about Opus 5 changes the plan — if anything it raises the value of the canon that deletion would discard.
- Corollary on measurement: ablation testing has good statistical power against capability failures (immediate, visible) and almost none against governance-conformance failures (tail-risk — the model behaves for twenty sessions then creates a feature branch on the twenty-first). "Delete it and see" is a sound experiment for the first class and an unsound one for the third.
- A framing recorded in error and withdrawn: this session initially characterized the open GHI queue as a latent defect pool and asserted that gzkit "records state faithfully and intent barely at all." Both are false. The queue is 8 enhancement to 5 defect, and gzkit has more intent-capture machinery than most codebases (ADRs, OBPI briefs, the insights store, this `_doc` itself). The real finding was far narrower: ONE delivery path can carry a hand-tuned value without routing it through any of the intent-capture surfaces that already exist.

## Decisions Made

- [operator-ruled] Reconcile the budget `_doc` against the enforced value and restore the gate rather than doing a documentation-only fix (verbatim: "reconcile the budget _doc against the enforced 50000").
- [operator-ruled] Relax limits until gzkit is stable; the retune is reverted and budgets stay at 50000, 15000, 30000 (verbatim: "until we get gzkit stable, I want to relax limits. the cms system is meant to control this, but we don't have gzkit feature stable enough to be strict").
- [operator-ruled] Add the capture-channel evidence as a comment on GHI #727 extending its scope, rather than filing a fifth sibling in the 607, 669, 691, 727 family.
- [operator-ruled] File through the ghi-author skill and push both commits via `gz git-sync`.
- [agent-chose] Kept `2d55abccd` in history rather than amending it away. The misdiagnosis and its correction are both why the `_doc` now reads as it does, and squashing that would reproduce the exact failure the thread is about.
- [agent-chose] Recorded an explicit EXIT CONDITION for the relaxation (re-tighten toward the sub-15k destination when the CMS corpus-splitting path lands) rather than leaving it open-ended.
- [agent-chose] Preserved the reverted retune measurements in the `_doc` so whoever re-tightens does not have to re-measure: AGENTS.md 32,023 chars and 32,208 bytes, CLAUDE.md 1,432 chars, largest rule file tests.md 17,851 chars.
- [agent-chose] Ranked the triage census with the brief-schema-enforcement defect first on the grounds that it actively halts legitimate work via phantom reconcile drift, ahead of items that only accumulate drift.
- [agent-chose] Ran a negative control against a copy of the real per-turn surface before trusting the retune, because a green gate and a binding gate are different claims and only the second was in question.

## Immediate Next Steps

1. Decide whether to chase the `gz drift` advisory of 2020 unlinked specs and 10 orphan tests. This is the one signal flagged twice this session and never investigated. Under the ADR-0.0.59 three-kind taxonomy, SUPPORT and STRUCTURAL-FENCE REQs correctly show as unlinked, so the figure may be entirely benign — but that is unverified, and a quality claim was made without settling it.
2. Review the rendered triage census (13 ranked of 13 open) and authorize which item to pull.
3. Consider routing the 607, 669, 691, 727 family plus this session capture-channel finding to a single pool ADR and closing them superseded, per ghi-author section Doctrine. Five cuts, one root; that is the move that stops the whack-a-mole rather than playing it faster.
4. Read GHI #579 before any future budget re-tightening. It argues chars is a proxy for the real cost unit (instruction-following degradation by count) and bears directly on how the CMS should be designed.

## Pending Work / Open Loops

Open loops carried forward:

- The `gz drift` advisory (2020 unlinked specs, 10 orphan tests) is uninvestigated. Advisory only, does not affect exit code.
- `.claude/rules/tests.md` measures 17,851 chars, above the pre-2026-07-06 rules budget of 15000. A diet pass on its rule-version-history preamble is what would make that value restorable. Recorded in the budget `_doc`, not separately tracked.
- The capture-channel remedy (a rationale slot when a sync bundle touches hand-tuned values under `data/`) exists only as a comment on GHI #727. If #727 routes to a destination without absorbing it, that remedy is lost.
- Complexity-thresholds bootstrap-mode advisory persists (tracked at GHIs #404 and #405). Pre-existing, untouched this session.
- The surface-delivery witness reports AGENTS.md at 32,208 bytes against the 32,768 byte codex delivery cap, 560 bytes of headroom. Advisory by design (the ceiling is decoupled from the vendor cap) but the margin is thin.
- No blockers. No ADR or OBPI in flight, no locks held.

### GHI triage census (2026-07-28) — 13 ranked of 13 open, fix() precedent 317 (60d)

Recorded here because the rank input lives only in a gitignored Layer-3 cache. This table IS the durable record of the census; the cache is not.

| # | GHI | Severity | Title |
|---|-----|----------|-------|
| 1 | 615 | blocking | schema: structured governance docs regex-scraped, not schema-enforced (briefs 597/600 bypass BriefStructure) |
| 2 | 728 | degrading | chores: sync and init export project-local slugs to adopters |
| 3 | 727 | degrading | architecture: tech choices and mechanism objectives are unrecorded |
| 4 | 691 | degrading | rules: no aging mechanism — skills have last_reviewed, rules have nothing |
| 5 | 611 | degrading | governance: no general append-only corrective-action primitive to undo agent/human error |
| 6 | 719 | degrading | interview: pool ADR interview JSON is unschema'd (non-pool is validated) |
| 7 | 581 | degrading | brief-reconcile: existence-only checks miss dead surfaces and code couplings |
| 8 | 579 | degrading | instructions-budget: anchor on imperative-density, not char count |
| 9 | 533 | latent | agents-md-budget: 5k recovery target requires ADR-0.0.37 completion + registry-projection migration |
| 10 | 669 | latent | obpi-monitor: no mechanical audit that every OBPI-status writer consults the terminal rule |
| 11 | 594 | latent | arb: no archive/purge half — 1875 receipts accumulate unbounded |
| 12 | 670 | latent | design skills: opus self-escalation lacks cross-family second opinion |
| 13 | 567 | latent | skills: adopt fenced prototype-spike + mine 2 filters (Pocock parity) |

Ordering rationale (the renderer does not carry it): #615 leads because it actively HALTS work — its regex fallback produced a false `req_count_delta` that blocked a reconcile Stage-1 gate on phantom drift, and it is operator-directed emergency scope. #728 follows because it is shipping wrong content to adopters on every sync, the same export class as #607 which broke an adopter build for two months. #727 is third as the convergent architectural root that #669, #691, and #607 are all cuts of — routing it drains several. The latent tier is genuinely deferrable: #533 is explicitly gated on the CMS this session confirmed is unbuilt, #594 is machine-local and gitignored, #670 has an unresolved reproducibility gap (`codex:rescue` is not exposed to the Agent tool).

### Settled Rulings corruption in the carried corpus (found post-commit, not yet tracked)

The `## Settled Rulings` section of THIS handoff carries damaged entries inherited from the chain. Verified by reading the file:

- Line 110 is TRUNCATED mid-quote: `Work the triage list in its ranked order (operator verbatim 2026-07-25:` with no closing quote and no authorization scope. The intact version of the same ruling exists at line 164.
- Lines 111, 112, 113 are ORPHANED FRAGMENTS with no attribution and no verbatim text: `Proceed with GHI #615 cuts 2 and 3 (migration plus strict enforcement)`, `Escalation should key on lifecycle rather than on frontmatter shape`, `Dimension-aware Draft scoping: a Draft brief does NOT gate on its own`.
- Lines 105 and 106 are NEAR-DUPLICATES of one ruling with differently-worded trailing clauses, so the dedup pass did not collapse them.

This matters because Settled Rulings exists precisely so operator decisions are not re-argued. A truncated entry carries no verbatim text and no authorization scope — a reader of line 111 learns that something about #615 cuts 2 and 3 was ruled, but not what, by whom, or how far the authorization reached.

The corpus documents its own wound: line 107 is a ruling to fix the settled-ruling dedup defect, and a predecessor handoff is named `shattered-rulings-reseated`. So this was found, ruled on, and repaired GOING FORWARD — but the already-corrupted entries were never re-derived from their source handoffs. The forward fix landed; the backfill did not. Same shape as the budget defect this session opened with: mechanism corrected forward, damaged historical record left as-is.

Not filed as a GHI — surfaced for operator routing at the end of this session, not adjudicated.

## Verification Checklist

Commands run this session and their observed results:

- `uv run gz check` — exit 0, all 45 gates green. Run once per commit. Advisories are pre-existing: vendor-cap distance, complexity bootstrap mode, spec-test drift.
- `uv run gz validate --instructions-files-budget` — passes; advisory NOTE reports 32208 B rendered against the codex delivery cap 32768 B.
- `uv run -m unittest tests.governance.test_agents_md_map_doctrine tests.governance.test_agents_md_map_doctrine_application tests.governance.test_audit_instructions_files_budget` — Ran 33 tests, OK.
- Negative control against a copy of the real per-turn surface under the retuned budgets: clean as committed, then fail-closed on AGENTS.md plus 1000 chars, rules/tests.md plus 1200, CLAUDE.md plus 2600. Each of those passes clean under the restored budgets, which is the point of the revert.
- `uv run gz git-sync --apply` — pushed; ahead 0 behind 0 against origin/main afterwards.
- `gh issue view 727` — comment 5102038113 present.

To re-verify the current state: run `uv run gz check` and confirm exit 0, then `git status --short` and confirm a clean tree.

## Evidence / Artifacts

Files touched or produced this session:

- `data/instructions_files_budget.json` — the reconciled surface; carries both new dated entries and the corrected reading convention
- `.gzkit/insights/agent-insights.jsonl` — Behavior Rule 11 course-correction record, type improvement, scope instructions-files-budget
- `.gzkit/cache/triage/rank.json` — the triage rank input for the rendered census. NOTE: gitignored (`.gitignore` line 56, `.gzkit/cache/`), so this is a Layer-3 derived cache and does NOT survive in the repo. It held stale rankings from a prior run when this session opened it (naming GHIs since closed) and was overwritten. Re-render rather than trusting its contents; do not read it as the durable record of this session's census.
- `tests/governance/test_agents_md_map_doctrine.py` — carries the ceiling constant and the verbatim operator ruling that decoupled it from the vendor cap

Commits (both on origin/main):

- `2d55abccd` — reconcile instructions-files `_doc` with enforced values, restore the gate
- `5d6c18e84` — revert the retune, record the pre-1.0 relaxation as ruled posture

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
- `models.md` text is fine and must not be rewritten; fix the mechanization and the export only (verbatim 2026-07-28: "the text is fine, fix the mechanization and the export"). A prior plan to re-scope the doctrine wording was withdrawn.
- STDLIB-FIRST is gzkit's constraint and a principle, not a bright line (verbatim: "STDLIB first != STDLIB only, I am getting tired of tripping up on this" and "STDLIB FIRST is gzkit's constraint and it is a principle").
- Take the #607 fix now and file the architecture work as its own GHI (verbatim: "take the #607 deletion now and file the architecture work as its own GHI"). The deletion half was substituted for scoping after the attested-REQ binding was found; the operator confirmed the substitution (verbatim: "yes, confirm").
- Keep campaign sequencing as is (verbatim: "keep sequencing as is"). Movement A remains topmost; Movement B (airlock on the real doors) is NOT pulled forward despite the airlock findings. This is a live ruling against acting on the investigation.
- Direct-fix the airlock mis-citation (verbatim: "yes, direct fix mis-citation"). No GHI filed -- filing one to construct a trailer anchor is the moratorium violation named in `.gzkit/rules/task-discovery.md`.
- Correct the chore's false text and file the gap behind it (verbatim: selection of "Correct the text, file the gap"). Building the affordance now, deleting the chore, and letting it ship uncorrected were all declined.
