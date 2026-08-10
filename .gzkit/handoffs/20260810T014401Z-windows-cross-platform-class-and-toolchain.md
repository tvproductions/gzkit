---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-10T01:44:01Z'
agent: claude-code
continues_from: .gzkit/handoffs/20260726T193732Z-ghi-723-fixed-724-filed-as-ruling.md
---

## Current State Summary

A routine `/git-sync` was refused by the pre-push gate on a tree CI had just
passed green, and diagnosing that consumed the session. HEAD at `228a0717`, tree clean,
`main` level with `origin/main`, `gz check` exit 0 across all 54 steps, 8326 tests OK,
ARB receipt `arb-step-unittest-2ac3c0f8261c4b23a06ac54e0030fde4` at `exit_status=0`.

Four commits landed: `7afb2b5c` (cross-platform class fix, witness, CI matrix),
`75fa2287` (handoff gate never blocks git-sync), `228a0717` (toolchain upgrade plus the
full ty 0.0.69 migration), on top of `003fe3e1`. GHI #681 was re-opened and re-closed;
#788 and #789 were filed and closed. No active OBPI lock, no in-flight pipeline.

This session did NOT touch the Build-to-1.0 campaign. Movement A remains exactly where
the predecessor handoff left it.

## Important Context

FIRST, the finding that explains months of recurrence:
`.claude/rules/cross-platform.md` declares Windows, macOS and Linux co-equal, while
`.github/workflows/ci.yml` ran `ubuntu-latest` with no matrix and `release.yml` shipped
`windows-latest` binaries. The platform was shipped and never gated. Four defects reached
main through that gap -- GHI #383 (backslashes in compared paths), #275 (Windows console
encoding), #582 (cp1252 subprocess decode), #681 (CRLF in generated surfaces) -- each
found by hand on the operator's clone. `windows-latest` is now in the matrix with
`fail-fast: false`. macOS was deliberately excluded: 10x billing against Windows's 2x,
and it shares POSIX path and newline semantics with Linux.

SECOND, GHI #681 is the canonical fix-the-instance-not-the-class case and is worth
reading before any similar repair. Its own Class-of-failure section enumerated 8 write
sites in ONE module; that module was fixed and four other surface writers were left
translating newlines. It recurred 28 days later. The durable half is not the six
one-line pins but `audit_generated_surface_newlines`, which asserts the PROPERTY over
every write in scope rather than a list of known-good line numbers.

THIRD, three things compounded to make the CRLF class structurally invisible, and all
three matter: the cross-platform rule's only line-ending guidance was a Quick Reference
row scoped to CSV, so the property had no rule to be checked against; `gz validate
--line-endings` inspects committed files rather than writers, so a writer that WILL emit
CRLF is outside what it can detect; and on Linux the defective writers emit correct LF,
so CI was green throughout.

FOURTH, `gz validate --surfaces` was a validator that WRITES. It ran a full sync to disk,
byte-compared, then restored from a hand-maintained 3-entry tuple while `sync_all` writes
22 nested `AGENTS.md`. A read-only validation therefore left 19 files unrestorable and
reported as drift the bytes it had just written itself. The set is now derived from
`nested_agents_md_paths`, the same classification the writer uses.

FIFTH, and the most reusable finding: `audit_type_ignores` had been instructing people to
DELETE WORKING SUPPRESSIONS. ty deliberately interoperates with mypy -- codes without a
`ty:` prefix are skipped so one comment can serve both checkers -- so
`# type: ignore[ty:invalid-assignment]` and the combined `[arg-type, ty:...]` form
genuinely suppress. The audit matched every bracketed form. Its advisory-scorecard row
claimed "Mechanical - enforced" the whole time.

SIXTH, the operator's standing 2026-07-26 ruling that a git-sync is never gated on a
handoff had existed as prose in a handoff's Settled Rulings and was mechanized by
nothing, so every session since re-litigated a closed question. It now has a test and a
named constant.

## Decisions Made

- [operator-ruled] Fix the Windows defects in this clone rather than pushing from WSL (chosen over the recommended push-from-WSL route).
- [operator-ruled] Track the cross-platform findings as one GHI covering the class, not three sibling issues.
- [operator-ruled] Handoffs must never block a git-sync (operator verbatim 2026-08-09: "handoffs should never, never, never, ever, block git-sync. NEVER."), reaffirming the 2026-07-26 standing ruling and converting it into a mechanical exemption plus a covering test.
- [operator-ruled] Add `windows-latest` to `ci.yml`; macOS excluded on cost-versus-distinct-failure-class grounds.
- [operator-ruled] Do not blame a cross-platform defect on the tool's implementation language (operator verbatim: "Don't blame things on ty, it was designed to work with Python"). Configuring ty portably is gzkit's job.
- [operator-ruled] Track ty FORWARD, never pinned backward (operator verbatim: "we progress as Ty progresses, if it has become more strict, then we tighten up, do not avoid hard work by clinging to older version of Ty"). This overruled the `gz-deps-upgrade` Risk-notes recovery posture and the agent's `ty==0.0.55` pin.
- [operator-ruled] Fix the audit predicate and the rule table immediately rather than filing a GHI, and keep the 324 `features/` removals.
- [agent-chose] Suppressed rather than rewrote the 80 negative-path tests, after mechanically confirming 80 of 80 sit inside `assertRaises`. The code there is already maximally strict; ty cannot see the `assertRaises` context. Rejected: rewriting the assertions, which would have destroyed proofs of immutability and required-field validation.
- [agent-chose] Excluded `*.md` from `ruff format`. ruff 0.16 began formatting Python blocks inside Markdown, which grew the governed surface corpus by 742 lines in one pass and pushed it into the yellow band. The formatter owns Python; the surface budget owns Markdown.
- [agent-chose] Kept the ty exclude SCOPE unchanged while re-spelling it, so no receipt's coverage claim shifts, and added the dated `RETIRED_STEP_COMMANDS` row so the roughly 1875 existing receipts stay valid.
- [agent-chose] Did NOT edit `.git/config` to remove the stale WSL credential helper; suppressed it per-invocation instead, because the operator may use this same clone from WSL.

## Immediate Next Steps

1. NOTHING IS AUTHORIZED. This session's work is landed and pushed; every step below needs an explicit operator ruling.
2. Rule on `ty.toml`'s `tests/**` override. Measured: re-enabling all six rules costs 1185 diagnostics, 915 being the `invalid-argument-type` Pydantic false-positive class the config comment already names, so blanket strictness is not worth it at ty 0.0.x. But `unused-type-ignore-comment` costs 7 and is the detector for exactly the dead-suppression class swept this session, switched off in the tree where 188 accumulated. One line. The override records no count and no ty version, so its justification cannot be re-checked; `pythonic.md` section Imports is the model for recording it.
3. Rule on the surface-weight floor. The per-turn surface sits at 2600 lines against a 2601 yellow band -- zero margin, and the next three lines added anywhere trip it. The floor (1859) dates to 2026-05-15 and the corpus has grown 742 since. This is a recalibration-or-diet decision, not a boundary waiver.
4. Rule on witnessing the 67 Mechanical scorecard rows. Five have been found false in two days (four on 2026-08-08, one this session). The scorecard self-test validates version freshness, not claim truth -- nothing plants a violation and confirms the named gate catches it. The mutation check was done by hand for row 24; generalizing it across 67 rows is real work.
5. Verify the Windows CI leg actually passes on its first run. It has never executed, and a green Linux history is no evidence for it.

## Pending Work / Open Loops

GHI #681, #788 and #789 are all CLOSED with commit SHAs and before/after
measurements. No open GHI is owned by this session.

THE WINDOWS CI LEG IS UNPROVEN. It was added this session and has never run. If it fails
on first execution that is expected discovery rather than a regression -- the entire point
is that this platform was never exercised.

THE PER-TURN SURFACE HAS ZERO MARGIN (2600 of 2601). Any rule edit, including a routine
version-marker bump, can trip `gz validate --surface-fidelity`. Do not resolve that by
waiving at the boundary.

THE STALE WSL CREDENTIAL HELPER IS UNCHANGED in `.git/config`:
`credential.helper = store --file /mnt/c/Users/Jeff/.git-credentials`. It breaks
`gz git-sync` from Windows because the ritual cannot pass `-c`. It was suppressed
per-invocation this session, never fixed, because it may serve WSL sessions on this clone.

THE BEHAVE TIER still carries the log noise GHI #723 fixed for unittest, carried forward
unresolved from the predecessor handoff. THE g0 AUTHORSHIP GUARD IS STILL PER-CLONE, also
carried forward.

CARRIED AND UNWORKED: GHI #719; campaign Movement A (ADR-0.35.0 at 0 of 9, ADR-0.34.0 at
2 of 5); promotion of the two pool ADRs with the ephemeral-worktree carve-out ratified
first. SPEC-TEST DRIFT ADVISORY stands at 698 unlinked specs, advisory only.

## Verification Checklist

`git log --oneline -4` (expect `228a0717`, `75fa2287`, `7afb2b5c`,
`003fe3e1`); `git status --short --branch` (expect clean, level with `origin/main`);
`git log -1 --format=%an` (expect `g0`); `gh issue view 681 --json state`, `788`, `789`
(expect CLOSED for all three); `uv run gz check` (expect exit 0, all 54 steps, with the
pre-existing spec-test-drift and complexity advisories); `uv run gz obpi lock list`
(expect no active locks); `gh run list --workflow=CI --limit 3` -- the Windows leg is NEW,
so confirm it ran and read its result rather than assuming.

To re-confirm the central cross-platform claim rather than trusting this document:
`uv run gz validate --surfaces` should exit 0 AND leave `git status` clean. Before this
session it exited 1 with 43 errors and dirtied 16 files.

To re-confirm the typecheck fix: `uv run ty check . --exclude features` should exit 0,
while substituting the retired `features/**` glob should exit 1 with 25 diagnostics, every
one of them inside `features/`.

## Evidence / Artifacts

Session commits: `7afb2b5c`, `75fa2287`, `228a0717`.

Cross-platform surfaces: `src/gzkit/rules/__init__.py`, `src/gzkit/skills/__init__.py`,
`src/gzkit/personas/__init__.py`, `src/gzkit/governance/adr_status_index.py`,
`src/gzkit/governance/trust_audits/cross_platform.py`,
`src/gzkit/validate_pkg/sync_parity.py`.

The witness: `tests/governance/test_generated_surface_line_endings.py`.

Handoff gate: `src/gzkit/handoff_resume_gate.py`,
`tests/governance/test_handoff_resume_gate.py`.

Typecheck contract: `src/gzkit/arb/validator.py`, `.pre-commit-config.yaml`,
`tests/arb/test_typecheck_scope_lockstep.py`.

The ty-ignore predicate and rule: `src/gzkit/governance/trust_audits/code_quality.py`,
`.gzkit/rules/pythonic.md`, `tests/governance/test_type_ignore_syntax.py`,
`docs/governance/advisory-rules-audit.md`.

CI matrix: `.github/workflows/ci.yml`. Dependency surface: `pyproject.toml`, `uv.lock`.
Surface budget: `data/surface_weight_floor.json`.

Insights recorded this session: `.gzkit/insights/agent-insights.jsonl`.
Predecessor handoff:
`.gzkit/handoffs/20260726T193732Z-ghi-723-fixed-724-filed-as-ruling.md`.
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
