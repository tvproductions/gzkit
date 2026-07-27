---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-27T12:44:56Z'
agent: claude-code
session_id: 8cb665ed-c1a8-4ce2-bfb4-6cca06794a4c
continues_from: .gzkit/handoffs/20260726T193732Z-ghi-723-fixed-724-filed-as-ruling.md
---

## Current State Summary

Off-cycle session, no parent ADR, no OBPI lock. Opened on `handoff` (RESUME), which
surfaced that the orientation hook had pinned a SUPERSEDED handoff: the clone was 11
commits behind and three newer handoffs existed only on origin. Synced, re-presented
against the real one, then reviewed it as an artifact.

Three GHIs closed, two of them filed this session: #726 (behave warnings in Gate-5
proofs) and #725 (authorship guard per-clone) were authored here, then #724, #725 and
#726 were all fixed, verified, closed with evidence, and pushed. A fourth pass
discharged three items I had wrongly left undone.

HEAD `1db47571d`, tree clean and level with origin. `gz check` passed at that SHA via
the pre-push gate. Full suite 7531 tests, exit 0. Open GHIs: 14 at session start, 13
now (+2 filed, -3 closed).

## Important Context

FIRST, and the most reusable finding: the SessionStart orientation hook selects the
newest handoff ON DISK, so a behind clone makes "newest on disk" and "newest authored"
diverge silently. The pinned handoff was Fresh by timestamp and three sessions stale in
fact. Freshness classification cannot detect supersession; only the `continues_from`
chain can, and only if the head is chosen correctly. Always check `git log HEAD..origin/main`
for handoff commits before trusting a resume.

SECOND, a live bootstrap trap in `gz git-sync` that is now self-clearing. Booking a
ruling writes a ledger event, which makes the tree dirty, which makes the ceremony's own
`git add -A && git commit` turn `ahead=0 behind=11` into `ahead=1 behind=11`, which makes
`pull --ff-only` impossible. That is GHI #720 exactly, and its fix (`2a0652b64`) was
sitting in the commits the failure prevented pulling. Recovery was `git reset --hard
origin/main` plus re-running the governed authorize verb, chosen over hand-resolving a
conflict in `.gzkit/ledger.jsonl` (Never #2 forbids editing it). Cannot recur now the
tree is current.

THIRD, `/ghi-author` Step 0 killed a GHI I had recommended filing, which is the strongest
argument for the mandatory pre-flight. Both findings from the handoff review were already
resolved by commit `e84e6a85b`: the shattered ruling is knowingly-unrecoverable pre-fix
damage, and the near-duplicate rulings are a DELIBERATE documented non-change. Do not
re-litigate `_ruling_key`'s narrow normalization: a similarity threshold that collapses
the three real duplicates also erases the two genuinely distinct "Book the patch release"
rulings, which I confirmed independently before finding the commit that already said so.

FOURTH, `ghi-triage` mines blockers from COMMENTS ONLY (`triage.py:243-265` iterates
`issue.comments`; the body is never read) and matches four literal markers: blocker,
blocked on, sequence after, waiting on. A blocker described in an issue body is invisible
to the report the operator reads before pulling work. Both new GHIs got proper blocker
comments after this was verified with the script's own predicate.

FIFTH, a class defect worth remembering: `GzkitConfig.load` rebuilt the model from a
HAND-COPIED key list, so a correctly-named new config block was silently discarded while
`extra="forbid"` still caught typos loudly. The audit shipped green doing nothing until a
negative control exposed it. Now derived from `cls.model_fields`. The same shape existed
in `tests/commands/test_skills.py` and was also fixed; assume it exists elsewhere.

SIXTH, `gz validate --qc-binding` REFUSES a new bound `gz check` step as
green-by-emptiness until a negative control is registered in `_qc_negative_controls`. It
did this to both new steps. The fixture must be present-but-wrong, never merely absent,
and must be deterministic on any machine (the authorship control uses a `.invalid`
suffix for exactly that reason).

SEVENTH, a new CLI verb owes more surfaces than it looks: a wielding skill
(tool-skill-runbook Invariant 1), a `config/doc-coverage.json` entry, manpage, manpage
index, operator runbook, governance runbook, and the `_GOLDEN_EXPLICIT_SET` registry
snapshot for a new validate scope. The pre-push gate caught nine failures from missing
these.

EIGHTH, the adopter boundary is a live design constraint, not theory. A new `gz check`
step hard-failed every adopter because `gz init` output has no `@smoke` tests. Both new
gates are now opt-in via `.gzkit.json` (`smoke.required`, `authorship.required_email_suffix`),
mirroring GHI #607's open complaint about strictures leaking across that boundary.

## Decisions Made

- [operator-ruled] Sync first, then re-present, before working any advised step (verbatim 2026-07-27: "Sync first, then re-present"; booked via `gz handoff authorize`).
- [operator-ruled] Comment the measured blast radius on #717 and file the two genuinely untracked findings, after Step-0 prior art voided the originally-recommended GHI (verbatim: "Comment on #717 + file the two trackers").
- [operator-ruled] Fix GHI #724, #725 and #726 (verbatim: "fix 724, 725, and 726").
- [operator-ruled] Directions, chosen from bounded options: #724 direction (a) build the smoke tier; #725 direction (4) fail-closed assertion; #726 direction (b) silence at the fixtures.
- [operator-ruled] Discharge the three items left undone rather than narrating them (verbatim: "fix:" quoting the turn-closing deferral paragraph). Recorded as an improvement insight per Behavior Rule 11.
- [agent-chose] Did NOT file the Settled Rulings GHI I had recommended. Step 0 showed both findings already resolved by `e84e6a85b`, one as knowingly-unrecoverable residue and one as a deliberate documented non-change. Filing would have produced a duplicate-scope GHI arguing against reasoning already in the tree.
- [agent-chose] Recovered the wedged sync with `git reset --hard origin/main` plus a re-run of the governed authorize verb, over hand-resolving an append-only conflict in the ledger. The only lost content was one regenerable event, and the alternative violates Never #2.
- [agent-chose] Derived smoke-tier coverage from the LIVE CLI parser rather than a per-package marker floor. A per-package floor needs 23 hand-placed markers and a maintainer to keep placing them, which is a membership roster wearing a decorator; a parser sweep covers a new verb the moment it is registered.
- [agent-chose] Made both new gates opt-in after discovering the smoke step hard-failed a freshly scaffolded project. Imposing a tier gzkit invented on every adopter is GHI #607's complaint arriving through a new door.
- [agent-chose] Appended provenance notes to the six sealed proof artifacts rather than rewriting them. A proof records what a run emitted, so editing the capture destroys the record; a note beneath it destroys nothing and answers the reader.
- [agent-chose] Tagged the BDD fixture REQ `[SUPPORT]` rather than `[BEHAVIOR]`. BEHAVIOR's only proof channel is a `@covers` test, so BEHAVIOR would have tripped the REQ-coverage gate and changed what those completion scenarios test.

## Immediate Next Steps

1. NOTHING IS AUTHORIZED. This session's work is closed, CI-gated and pushed; every step below needs an explicit operator ruling first.
2. The carried chain, unworked and still live: GHI #719 (pool interview JSON unschema'd, direction (b) — a `gz plan create --from <interview.json> --kind pool` path and/or a pool-interview schema with a validate scope).
3. Campaign Movement A remains topmost absent a ruling: `ADR-0.35.0-canon-entry-corpus-landing` at 0/9, and the `ADR-0.34.0-foundation-sunset` capstone at 2/5 including wiring the permanent `--taxonomy` gate into `gz check`, currently red with 74 foundation grandfather errors.
4. Promotion of the two pool ADRs when wanted: assign SemVer ids, and for `ADR-pool.worktree-parallel-agents` ratify the ephemeral-worktree doctrine carve-out FIRST — that is a hard promotion gate.
5. Optional cleanup surfaced but not filed: the `Disposition foundation-adr-registers-invariant` one-line canon call declares a structural witness `gz validate --foundation-registers-invariant` that has never existed. Fenced shrink-only today; it needs an operator ruling, not code.

## Pending Work / Open Loops

GHI #719 OPEN and unworked — the deferred direction-(b) capability from #718.

13 GHIs open. #607 is now cited by two landed designs (both new gates are opt-in
specifically to avoid its complaint), so working it would validate or falsify that
choice.

SPEC-TEST DRIFT ADVISORY stands at 2030 findings (2020 unlinked specs, 10 orphan tests).
Advisory only; unchanged by this session.

THE FULL UNIT TIER IS NOW EXPLICITLY UNBOUNDED in `.gzkit/rules/tests.md` 0.13.0. That is
a deliberate contract change, not an omission: its runtime ratchets with the REQ set by
design. GHI #512's Option B stays declined on measurement (71.4s across 32 processes,
still over a 60s ceiling), and GHI #644 (at-scale test management) is the open home for
anyone who wants to revisit suite growth.

NO OBPI LOCK HELD, no in-flight pipeline, nothing carried-and-unstarted from an
authorized queue.

TWO GATES ARE NEW AND UNEXERCISED BY OTHERS: `gz smoke` and `gz validate --authorship`.
Both are opt-in, both are wired into `gz check`, and both have registered negative
controls. Their first contact with another operator's clone is unobserved.

## Verification Checklist

git log --oneline -5 (expect 1db47571d, 74a537f35, a7b1c6c1d, 78d851add, 148e14338);
git status --short --branch (clean, level with origin/main);
gh issue view 724 --json state, and 725, 726 (expect CLOSED for all three);
gh issue view 719 --json state (expect OPEN — the carried item);
uv run gz smoke (expect exit 0, 2 tests, well under the 60s budget);
uv run gz smoke --budget 0 (expect exit 3 — the budget gate has teeth);
uv run gz validate --authorship (expect exit 0 on a correctly configured clone);
uv run gz validate --qc-binding (expect "No QC theater detected" and NO stray prose);
uv run gz cli audit (expect 132/132 fully covered);
uv run gz obpi lock list (expect no active locks).

To re-confirm #726's fix rather than trusting this document, run behave with the streams
SPLIT — a merged run hides it, which is how I missed it on the first look:
  uv run -m behave > out.txt 2> err.txt ; wc -c < err.txt
Expect 0 bytes on stderr and exit 0. Four warning lines there means the fix regressed.

Do NOT pipe any of these verifiers through tail or grep: the shell reports the filter's
exit, not the verifier's (`.gzkit/rules/tests.md` § Verification exit-code integrity).
Capture to a file and read the file.

## Evidence / Artifacts

Session commits, all pushed to main: `148e14338` (GHI #726), `78d851add` (GHI #725),
`a7b1c6c1d` (GHI #724 feature), `74a537f35` (GHI #724 adopter safety), `1db47571d`
(three deferrals discharged).

New runtime surfaces: `src/gzkit/smoke.py`, `src/gzkit/commands/smoke_cmd.py`,
`src/gzkit/governance/trust_audits/authorship.py`.

New tests: `tests/test_smoke_gate.py`, `tests/cli/test_smoke_tier.py`,
`tests/governance/test_authorship_policy.py`,
`tests/governance/test_bdd_tier_stderr_hygiene.py`.

Modified contracts: `.gzkit/rules/tests.md` (0.13.0), `.gzkit.json`,
`config/doc-coverage.json`, `.pre-commit-config.yaml`, `docs/user/manpages/smoke.md`,
`docs/user/manpages/validate.md`, `src/gzkit/config.py`.

BDD harness: `features/environment.py`, `features/validate_receipt_shape.feature`,
`features/steps/attestation_receipt_binding_steps.py`.

Negative controls: `src/gzkit/governance/trust_audits/_qc_negative_controls.py`,
`src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py`.

Derived-not-listed fix: `tests/commands/test_skills.py`.

Insights recorded this session: `.gzkit/insights/agent-insights.jsonl`.

Predecessor handoff: `.gzkit/handoffs/20260726T193732Z-ghi-723-fixed-724-filed-as-ruling.md`.

Campaign: `docs/governance/build-to-1.0-campaign-2026-07-18.md`.

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
