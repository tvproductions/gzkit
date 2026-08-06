---
mode: CREATE
adr_id: ADR-0.0.65
branch: main
timestamp: '2026-08-06T07:01:21Z'
agent: claude-code
session_id: 7ea92a0a-d0ad-490f-8c44-6285b532fc32
continues_from: .gzkit/handoffs/20260806T053254Z-exit-beat-staging-and-selection-coupling.md
---

## Current State Summary

Three commits landed and pushed; tree clean, origin/main in sync at `cf6571577`. Supersedes the `20260806T053254Z` anchor and the `20260806T055706Z` floor bookmark — that bookmark is now committed (it rode `a856c4e89`), so the sensemaking it was flagged for is discharged and no bookmark awaits processing.

Three GHIs filed and closed, each citing its commit SHA: #760 (the exit-beat skip predicate was defeated by the handoff's own landing commit), #761 (SessionStart listed handoff evidence but never assembled the account), #762 (the delta rule was carried by convention, so each reader relearned it separately).

The session opened as a handoff review and the review is what found #760. The predecessor's advised step 3 was "watch the next session start: the skip predicate will fire for the first time against a real corpus". It fired and declined to skip, and the ledger showed zero `session_exit_bookmark_skipped` events since the predicate landed the previous evening. The operator ruled the fix, then ruled the next advised step, which produced #761. The operator then read this agent's report of that work and rejected its framing: two instances had been fixed and reported as though the class were closed. That correction produced #762, which is the only one of the three that closes a family rather than an instance.

## Important Context

The three GHIs are one lesson at three depths, and reading them in commit order is what makes the third one legible.

`gz git-sync` bundles every `.gzkit/**` change into a single `chore: update .gzkit` commit. That means the commit which lands a handoff routinely carries adjacent files — an insights line, a ledger entry — and is therefore NOT handoff-only. Every "what has happened since this handoff" query has to exclude that commit, and a pathspec cannot: a path filter only drops commits touching handoffs ALONE. A commit range excludes its own endpoint and cannot make the mistake. This is the whole of #760 and it recurred verbatim in #761's surface an hour later.

The recurrence is the finding, not the bug. Both consumers learned the identical lesson in separate commits with separate tests, an hour apart, in one session, the second written by the agent that had just written the first. A lesson that cannot survive sixty minutes inside a single context window is not being carried by the code. That is the operational test for convention-versus-mechanism and it is cheaper than any argument about it.

`src/gzkit/handoff_selection.py` already held the answer and had held it since GHI #758 — one definition, imported by every reader, plus a scan that fails closed on a second copy. #758 applied it to the SELECTION question ("which handoff") and stopped there. The DELTA question ("what happened since it") was left uncoupled and drifted the same way. #762 is that module absorbing the second rule; nothing about the mechanism is new.

What is shared is the question's GRAMMAR — the range form and the exclusion pathspec. What stays local is each caller's subprocess wrapper and timeout, because a boot hook and a CLI have genuinely different budgets. The module's own docstring already warned that forcing one signature would make one reader worse. The seam goes between the rule and the spending, never between the modules.

`scripts/session_orientation.py` is stdlib-only-when-it-must-be, so it reaches the shared rule through a guarded `handoff_delta_rule()`, the shape `floor_bookmark_agent()` established. That guard degrades to rendering NO account rather than to a local copy of the rule. A local copy would be invisible until the two answers disagreed, which is precisely the failure the shared module exists to prevent. It composes with `_scan_handoffs`, which already returns None on the same condition, so an unimportable gzkit drops the section whole instead of rendering half of one.

The account section deliberately does not narrate. It assembles evidence and states one mechanical verdict, and its own closing line says so. An account that editorialized would be a second authority competing with the handoff it measures against.

One trap worth naming for whoever touches the differential tests: a test helper that admits a different corpus than production is not a differential. The live-corpus test first errored on `NoneType > datetime` because the helper skipped `_looks_like_handoff` and the mtime fallback, so it was reading `.gzkit/handoffs/AGENTS.md` — a directory README, which production has excluded all along, with its own test. That was a defect in the test, not in the code under test, and it would have read as a shipped defect in the RED log.

## Decisions Made

- [operator-ruled] Fix the skip-predicate hole (verbatim: "Fix the skip-predicate hole", selected via AskUserQuestion and booked through `gz handoff decide` against the `20260806T053254Z` handoff — this is the ruling that lifted the resume gate and scoped the session's opening). Chosen over building the SessionStart synthesis first, ruling GHI #759 plus re-running triage, and a review-only ruling authorizing nothing. Four advised steps were recorded `--set-aside` in the same booking.
- [operator-ruled] Continue with the next handoff step (verbatim: "continue with the next handoff step") — read as advised step 1, the SessionStart handoff-account synthesis, which the predecessor named as the one operator-directed item still unstarted.
- [operator-ruled] Sync via the governed ritual (verbatim: "git-sync", invoked as the `/git-sync` skill) — executed as `gz git-sync` dry-run then `--apply`, pushing `a856c4e89` and `e972c7469`.
- [operator-ruled] The two "adjacent defects" reported as resolved are not resolved (verbatim: "okay, these need to be addressed", quoting this agent's own report back at it). This is the ruling that produced GHI #762. The agent had fixed two instances and written that the class was closed; the operator read the report and rejected the framing.
- [operator-ruled] Author a fresh handoff and sync it (verbatim: "create a fresh handoff and gut sync", operator spelling preserved) — this document and the `gz git-sync` that follows.
- [agent-chose] Filed #760's two symptoms as ONE GHI rather than two, because both are the same defect in one function's anchor resolution — the anchor was resolved by timestamp-plus-pathspec where it meant commit identity — and both are closed by the same change. The constraint forbids bundling UNRELATED defects, not two manifestations of one class.
- [agent-chose] Routed all three as direct fixes under GHIs rather than opening an OBPI, per the operator's standing doctrine that a GHI is the work order and the receipt, and the standing routing ruling for handoff-lifecycle items ("stop. pool it. or direct ghi and attribute to the handoff adr"). #761 exceeded the ten-line direct-fix threshold and was still routed direct: it is a CORRECTION, since the shipped surface did not fulfil the intent of the ruling it was built under.
- [agent-chose] Resolved an absent landing commit to `HEAD` rather than treating it as an uncertainty. A staged-but-uncommitted handoff has no anchor and needs none — every commit in history predates it — so the range is empty by construction. The fail-toward-writing bias is right for an unreadable corpus and wrong for a case that can actually be decided.
- [agent-chose] Refused the `current` verdict when git is unreachable, rather than rendering an empty delta. An unknown account and a clean one are the same to a reader deciding whether to trust the anchor, and only one of them is true.
- [agent-chose] Did not collapse the three handoff-corpus readers the predecessor session deliberately left separate. They answer genuinely different questions and one is a PreToolUse hot path. Only the two asking the SAME question were merged; sharing across distinct questions is how the wrong filter reaches the wrong arm.
- [agent-chose] Fenced the exclusion pathspec by literal scan rather than by convention, mirroring `test_the_identity_literal_appears_only_in_its_defining_module`. A convention is what failed twice in one session.

## Immediate Next Steps

1. Rule GHI #759, which has now been open across three handoffs. Its mechanism landed at `c94de7e4b` (the coupling validator proves repository membership rather than disk presence) but the issue was deliberately left open for the remaining design surface and nobody has ruled on whether that surface still exists. Either close it citing the SHA or state what stays open, because an issue whose mechanism shipped is a shadow tracker.

2. Decide whether `ExitBookmarkResult.skipped` deserves an operator-visible surface. It is only in the ledger today. The skip predicate now works, so this field will start being `True` routinely and its silence becomes a real gap rather than a theoretical one — a deliberate no-op and a crashed hook read identically from outside.

3. Watch the account section at the next session start. It should report this handoff as the anchor with zero commits since, because the commit that lands it is excluded by identity. That is the same property `test_the_handoffs_own_landing_commit_is_not_unaccounted_work` asserts, observed against the live corpus rather than a fixture.

4. Re-run GHI triage before pulling anything new. The ranked list at `.gzkit/cache/triage/rank.json` predates this session's three closes and still names #581 and #611 as highest-merit.

5. Return to the campaign's topmost item, `ADR-0.35.0-canon-entry-corpus-landing`, which is `Pending` at 0 of 10 OBPIs and has not been touched across five handoffs. Everything this session did was handoff-lifecycle repair, which the campaign permits as a primary propellant but does not sequence.

## Pending Work / Open Loops

- GHI #759 is open although its mechanism landed at `c94de7e4b`, now carried unruled across three handoffs. This is the oldest untouched item in the chain.
- `ExitBookmarkResult.skipped` is visible only in the ledger. The field was inert until this session because the predicate never fired; it is live now.
- Three open GHIs still run on premises that have cleared and nobody has re-derived: #581 (its gate, #519, settled), #533 (ADR-0.0.37 now Validated 15/15), #594 (sibling #585 settled and `gz handoff archive` ships).
- GHI #670's stated reproducibility gap is stale: `codex:rescue` is available in-session.
- ARB receipts continue to accumulate unbounded, well past the 1875 cited on #594, and three more were emitted this session.
- The campaign's topmost item is untouched: `ADR-0.35.0-canon-entry-corpus-landing`, `Pending`, 0 of 10 OBPIs.
- The account section and the bookmark section overlap by one line — the account reports a bookmark count, the bookmark section reports each bookmark's inclusion status. That is deliberate today (different questions) but it is the kind of adjacency that becomes duplication if either grows.
- No handoff-corpus reader is fenced against a FIFTH consumer arriving with a third question about the same corpus. Selection and delta are each fenced now; the pattern of "a new question, a new local implementation" is closed only for the two questions that exist.

## Verification Checklist

- `git status --short` is empty and `git rev-list --left-right --count origin/main...main` returns `0	0`.
- `uv run gz arb step --name unittest -- uv run -m unittest -q` exits 0 with `Ran 8004 tests` / `OK`. The count rose 7989 to 7998 to 8004 across the session's three commits, matching the tests added by each. Every exit code was read from an explicit `echo` after redirecting to a file, never from a pipe — the exit-code-integrity hook refused a piped verifier twice during this session and was correct both times.
- `uv run -m unittest tests.governance.test_handoff_selection tests.governance.test_session_exit tests.scripts.test_session_orientation` exits 0 with 102 tests.
- `grep -rn "exclude).gzkit/handoffs" src/gzkit/ scripts/` returns exactly one line, in `src/gzkit/handoff_selection.py`. More than one means the fence has been bypassed.
- `uv run python scripts/session_orientation.py` exits 0 and renders the account section with an anchor, a delta, and a verdict.
- `uv run gz typecheck` exits 0.
- `uv run ruff check .` exits 0.

## Evidence / Artifacts

- `src/gzkit/handoff_selection.py` — now owns both cross-reader rules for the handoff corpus: the selection rule (`FLOOR_BOOKMARK_AGENT`, `selection_rank`) and the delta rule (`HANDOFF_PATHSPEC_EXCLUDE`, `commits_since_range`).
- `src/gzkit/session_exit.py` — the skip predicate, anchored on commit identity and importing the shared rule.
- `scripts/session_orientation.py` — the account collector and renderer, plus the guarded `handoff_delta_rule()` that crosses the stdlib boundary.
- `tests/governance/test_handoff_selection.py` — the delta fence, the range semantics, and the fourth-reader differential.
- `tests/governance/test_session_exit.py` — the bundled-landing-commit and staged-handoff tests.
- `tests/scripts/test_session_orientation.py` — the nine account-synthesis tests.
- `.gzkit/handoffs/20260806T053254Z-exit-beat-staging-and-selection-coupling.md` — the anchor this document supersedes.
- `.gzkit/handoffs/20260806T055706Z-session-exit-bookmark.md` — the floor bookmark, committed at `a856c4e89`; superseded and requiring no further sensemaking.
- ARB receipt `arb-step-unittest-3a4a5a803a834dae9477a4408aba2b67` (7998 tests, GHI #761).
- ARB receipt `arb-step-unittest-dcd724e0d4c547bd97bbdacfa097d445` (8004 tests, GHI #762).
- Commits: `a856c4e89`, `e972c7469`, `cf6571577`.
- GitHub issues: #760, #761, #762 — all filed through the ghi-author skill and closed through the ghi-close skill, each citing its SHA.

## Settled Rulings

- attest completed — OBPI-0.34.0-05 activates the permanent Foundation Sunset closure gate: ("ADR taxonomy", run_taxonomy_audit) is the LAST step in _build_check_steps() and `gz check --json` reports "ADR taxonomy": true, while the registration membrane refuses an un-grandfathered `kind: foundation` package at both adr_created ingresses (gz register-adrs and first-run gz init) with the 51-entry grandfathered roster still booking normally (GHI #706 discharged). 4/4 REQs proven on their correct ADR-0.0.59 channels with behavior_uncovered_reqs 0; REQ-0.34.0-05-01 was re-kinded BEHAVIOR->SUPPORT…
- "update handoff and campaign, then git sync" — booked verbatim via gz handoff authorize as the ruling on the resumed handoff. The predecessor's advised step (continue the ADR-0.34.0 checklist or open the next OBPI) was NOT authorized and remains unexecuted.
- The same words ratify the campaign amendment under section 8, in the same shape as the 2026-07-29 "fix discrepancy" ratification.
- attest completed — ADR-0.34.0 Foundation Sunset closeout, g0 verbatim, 11-step ceremony attested 2026-07-31T11:46:09Z; lifecycle transitioned to Validated and released as v0.34.0 on bump commit 551366064. Receipts arb-step-unittest-f02e079a9c5c4fce83433f15d1ace4b1 (7685 OK), arb-ruff-9b11bcbc647c4b9a9ddb6282f7fc34b4, arb-step-typecheck-4c8436dc00e842b8847ebcacb7dc866c, arb-step-mkdocs-3f31717e44a04a46821f35433f53b0c2.
- accept audit — ADR-0.34.0 Foundation Sunset validated with three shortfalls recorded open, accepted after each was presented with its verification evidence, g0 verbatim 2026-07-31T12:26:25Z. Bound fidelity gate 2/2, gz validate --taxonomy exits 0 on the terminal tree, gz cli audit 132/132 commands covered, 18/20 REQs covered with 2 SUPPORT REQs proof-exempt by ADR-0.0.59 channel. Shortfalls open: S1 inert @covers coverage, S2 missing exit-3 membership assertions, S3 framework-wide closure is the rejected alternative (GHI #740).
- refresh handoff (verbatim) — booked via gz handoff authorize against the 20260731T090547Z handoff for session a7d9d6b9-db29-49a3-8f87-f333222230a6. This is the ruling that lifted the resume gate; it authorizes the handoff refresh and nothing beyond it.
- "let's complete all chores — run all 37 + fix what's fixable" — booked via gz handoff authorize against the 20260731T202443Z handoff. This authorized chore work and NOTHING else; the predecessor's advised steps remain unexecuted.
- Rewrite all 37 D401 findings to imperative mood and adopt full ruff `D`, rather than exempting D401 to preserve the "True when ..." predicate convention. Landed in 44f7aac2e.
- For module-sloc-cap-radon: adopt the canonical radon_raw_nloc band and register the five over-band modules in a shrink-only ratchet, rather than splitting them now or leaving the chore red. Landed in 33df03496.
- yes, sync it, then GHI #743 (OPEN) -- booked via gz handoff authorize 2026-08-01T12:05:01Z for session 6b50f5be. This is the ruling that authorized the four control-surface audit re-runs; the work landed in 0551bbbd3 and GHI #743 closed 2026-08-01T23:40:06Z.
- evaluate this against gzkit: the Opus 5 system card -- booked via gz handoff authorize 2026-08-01T12:06:06Z for session 3d1de280. No artifact from that evaluation exists in the tree; the ruling stands undischarged.
- Refresh the handoff first -- booked verbatim via gz handoff authorize at 2026-08-02T00:58:21Z for session 0145e706-edae-4c07-bdad-3dc761fd0c3f. This authorized the handoff refresh and nothing beyond it; every item in Immediate Next Steps remains unexecuted and unauthorized.
- sync it -- ruled 2026-08-02 once the refreshed handoff was written and validated. Executed as gz git-sync --apply, landing commit e3e8d5428.
- Refresh the handoff first -- booked verbatim via gz handoff authorize at 2026-08-02T00:58:21Z. It authorized the handoff refresh and nothing beyond it, which is why every queue item below remains unexecuted.
- "Rule item 3, then work the queue" — booked verbatim via `gz handoff authorize` at session start; this is the ruling that lifted the resume gate and set the whole session's scope.
- Movement A item 3 disposition: retire the claim as superseded by the Foundation Sunset. Chosen over three alternatives presented (make the claim true by backfilling 51 ADRs; rule it a permanent exception; withdraw the entry). Turned on the fact that ADR-0.34.0 closed the foundation kind at both `adr_created` ingresses, so the claim's subject set is permanently frozen and can never be exercised again.
- GHI #744 residual: enroll the ten unreachable default-tier scopes and measure the cost. Chosen over enrolling a subset, leaving them declared-out, or filing a follow-up.
- GHI #745 scope: exempt pool ADRs structurally rather than building a per-reference marker, narrowing the rule's declared scope, or deferring.
- "do both" — fix the live-surface dead pointers now as a bounded direct fix AND route the speculative-marker build to its own work item.
- Sync to origin via `gz git-sync`, twice (after the first three commits, and after the doc repairs).
- Evaluate the Claude Opus 5 System Card against gzkit (verbatim: "evaluate this against gzkit").
- Land items 2, 4, and 5, then discuss 1, 3, and 6 (verbatim: "do 2, 4, and 5, then let's further discuss 1, 3, 6").
- Proceed on the recommended sequence: item 3 first, then item 1A, deferring 1C and 6 behind Movement A (verbatim: "proceed as recommended").
- Gate 5 attestation for the AGENTS.md rendition recompose, plus authorization to commit (verbatim: "attest completed — commit it").
- Push to origin/main (verbatim: "push it").
- Evaluate the GPT-5.6 System Card against gzkit (verbatim: 'evaluate this against gzkit (suggest updates where applicable)' — https://deploymentsafety.openai.com/gpt-5-6/gpt-5-6.pdf).
- Rule on the resumed handoff and route the evaluation as one GHI + direct doc fix with pattern-9 held (verbatim: 'do this: "rule on the handoff, then I file one GHI via /ghi-author covering the GPT-5.6 evaluation findings (items 1, 3, 4, and the citation-refresh half of 2) and route it as a direct doc fix, with the pattern-9 addition held until the ceiling question is settled."'). Booked via gz handoff authorize; executed as GHI #750 -> commit 7f0b8bdf4 -> closed citing the SHA.
- Relieve the surface-weight ceiling by diet, then land pattern 9 (verbatim: 'diet pass — relieve the ceiling and land pattern-9'). The same verbatim words were relayed as the Gate 5 attestation token (attestor g0) for the AGENTS.md claude-rendition recompose, enriched per AGENTS.md § Attestation.
- Refresh the handoff and sync (verbatim: 'refresh the handoff and sync') — this document and the following git-sync are that execution.
- The Opus 4.7 reference and premise are stale; live doctrine retains no superseded-model references (verbatim: 'no, that 4.7 reference, and premise, is stale. I don't want to retain direct references. and rationale, to older models, that is the point of the chore.'). Executed as the purge in 70af74a81 + the taxonomy/tests-rationale re-source in d3fb2aa12.
- Tuning for both vendors (verbatim: 'I don't know that we want just opus tuning without gpt tuning. I'd like to be able to run with either although gzkit is mostly designed to work with opus.'). Executed as docs/governance/gpt-tuning.md + CLAUDE.md template pointer.
- Adopt the fable tier (verbatim: 'It seems like we should incorporate fable for the cases and times.'). Executed as model-selection 0.5.0/0.5.1 + skill_model Literal 'fable' + routing-matrix row; Mythos-class operator-supervised judgment work only, never the pipeline default.
- Retain and rotate system cards (verbatim: 'when we obtain a new system card, we need to retain it, and rotate/remove older cards.'). Executed as data/system_cards/ + registry rotation policy + chore 1.1.0 guardrail reversal.
- Execute GHI #751 (verbatim: 'do 751 — consume the fable card'), with the card PDF URL operator-supplied mid-turn. Landed in d3fb2aa12; #751 closed citing the SHA.
- Refresh the handoff and sync (verbatim: 'refresh the handoff and sync') — this document and the following git-sync.
- Rule finding 1 as a bounded direct fix (verbatim: "rule finding 1 as a bounded direct fix first — it is a live residual against a ruling you made this morning"). Executed as 724cbb8de.
- Work finding 2 and GHI #748 (verbatim: "do these: 1. Finding 2 — the resume gate refuses git rev-list, which the handoff's own Verification Checklist prescribes. Same class as the gh gap from GHI #574 follow-ups; a one-entry allowlist addition. 2. GHI #748 (both confirmed OPEN, #745 blocked behind it) — the handoff's own step 2, carried unworked across four handoffs now."). Executed as b3b54317c and 082bd8760, with #748 closed citing the SHA.
- Sync, then record the insight (verbatim: "sync it, then record the insight"). Executed as two gz git-sync --apply runs and the discovery record in 66decb6b1.
- Refresh the handoff and work GHI #745 (verbatim: "refresh the handoff, do this: - GHI #745 — now unblocked (its precondition was #748), untouched. Remaining scope: widen _cli_alignment_sources to the full declared docs/** with the three structural exemptions, and mark the residual ~37 references."). This document is that refresh; the #745 work follows within the same session.
- Handle every one of the 98 residual sites rather than deferring any to a separate work item (verbatim: "it seems best to do something with all 98"). Executed in c49557f38 as 3 renames, 79 marked sites via 65 markers, and 674 sites structurally exempted.
- Superbook and superpowers are sunsetted, not an open question (verbatim: "no, superbook and superpowers was sunsetted and deprecated months ago"), correcting this agent's proposal to leave the references marked pending a GHI #749 ruling. Executed as 7b13cecde; #749 closed by the ruling.
- Remove the residual docs/superpowers/ surface (verbatim: "take care of this", against the flagged residual). Executed as d55401e00.
- Update the handoff and push (verbatim: "update handoff, sync, push"). This document and the git-sync that follows.
- Close GHI #732 and stop there rather than proceeding to ADR-0.35.0 or the deferred queue (verbatim: "Close #732 only, then stop"). Booked via gz handoff authorize against the resumed handoff; this is the ruling that lifted the resume gate and set the session's entire scope.
- Discharge the declared class before closing, rather than closing on the landed instance fix and routing the residual to a new GHI (selected: "Discharge the class, then close"). Chosen over closing as-is with a follow-up GHI, and over replacing the enumeration with a general read-only-git predicate in code, which exceeds direct-fix thresholds.
- Sync only, then stop, rather than proceeding to ADR-0.35.0 or GHI #746 (verbatim: 'Sync only, then stop'). Booked via gz handoff authorize; this is the ruling that lifted the resume gate and scoped the session's first half.
- Run the GHI triage and commit it to a handoff (verbatim: 'run the ghi triage and commit that to a handoff'). This is the ruling that authorized the second half; it did not authorize working any ranked issue.
- Work the triage in the resumed handoff (verbatim: "work the triage in handoff"). Booked via `gz handoff authorize`; this is the ruling that lifted the resume gate and scoped the session.
- GHI #739 direction: symmetry + rename -- `gz closeout` writes an in-flight manifest at bump time via a shared path contract, and `audit_version_release` accepts `RELEASE-v{version}.md` alongside `PATCH-v`. Chosen over the minimal reuse of the `PATCH-` writer (which leaves every minor release mislabelled) and over an audit-side time window (which weakens rule 11 to time-based rather than evidence-based).
- GHI #737 routing: fold into ADR-0.35.0 as a tenth OBPI rather than repairing standalone, wiring the corpus reader immediately, demoting the field to advisory, or deferring behind the ADR. Turned on the ADR standing at 0/9 unstarted over the exact corpus surface.
- GHI #737 representation: the corpus wins where it owns the section, the scorecard elsewhere. Chosen over absorbing the 144 scorecard rows into the corpus (far larger than one OBPI, collides with OBPI-04) and over ruling the scorecard binding with the field declared advisory (leaves the field inert and the skew unobserved).
- Continue working the ranked queue after the two blocking-tier issues (verbatim: "continue triage queue").
- Work GHI #736 next rather than settling the GHI #742 operator call first (verbatim: "736").
- Work GHI #742 as the rank-next issue, and REGULARIZE the no-frontmatter ADR packages rather than formally retiring them (verbatim selections: "GHI #742 — the rank-next issue" / "REGULARIZE — backfill and register"). Booked via `gz handoff authorize`; this is the ruling that lifted the resume gate and scoped the session. Chosen over FORMALLY RETIRE, splitting the call per package, and deferring behind the validator predicate change.
- Sync and close GHI #742 citing the SHA, recording the two body corrections as a closing comment so the false-zero grep is not re-derived later. Chosen over sync-only-leave-open and holding the commit local for review.
- Route both surfaced residuals rather than deferring either (selections: "adr-status title rendering" and "#736 residual (parse_artifact_metadata)"). Chosen over leaving both for a later session.
- Close GHI #746 (verbatim: "close 746").
- Update the handoff (verbatim: "update handoff").
- Pool ADR scope is whole-class -- absorbs #741, #719, #696 and the doc-content proof channel, not just the #615 remainder (operator, 2026-08-03)
- GHI #615 closes superseded, not fixed -- the pool ADR records both what landed and what remains, so it is the fuller record for a later reader (agent judgment, stated in the close comment)
- "fix 615" -- operator ruling on the 20260803T111119Z handoff, read as *do the work*, not *close it*. Seated here via --settled because it was lost from the promotion chain: the 20260804T051547Z handoff's Decisions entries carried list markers but no [operator-ruled] attribution, the mirror shape validate_decision_markers does not catch, so all six parsed UNATTRIBUTED and none promoted.
- "close 731" (verbatim) -- booked via `gz handoff authorize` against the 20260804T051547Z handoff; this is the ruling that lifted the resume gate and scoped the session.
- Defect remedies route to DIRECT FIX under their GHI even when the owning ADR is Validated and closed out (verbatim: "direct fix defects using ghi's"). `ADR-0.0.64` was not reopened, amended, or given a sixth OBPI. This is AGENTS.md section Operator Doctrine applied -- "GHIs are AUTHORIZED for direct repair, always" -- not a new exception; the agent had escalated a question canon already answered.
- GHI #752 remedy: producer-stamp `tasks:` and demote `@advances` to advisory. Chosen over narrowing the envelope to the two channels that already pair, and over backfilling both channels by authoring.
- "update handoff and sync it" (verbatim) -- this document and the `gz git-sync` that follows.
- "close 728" (verbatim) -- booked as the session's continuation of the triage queue after the #731/#752 pass.
- "write handodd and git-sync" (verbatim, operator's spelling preserved) -- this document and the `gz git-sync` that follows.
- "do 4, then 3" (verbatim) -- booked via `gz handoff authorize` against the resumed handoff; this is the ruling that lifted the resume gate and scoped the session to those two advised items, in that order.
- "update handoff and sync" (verbatim) -- this document and the `gz git-sync` that follows.
- Author pool ADR, close superseded (verbatim) -- booked via gz handoff authorize against the resumed handoff. This is the ruling that lifted the resume gate and set the destination route for GHI #691.
- git sync (verbatim) -- executed as gz git-sync --apply after the two #691 commits.
- close 727 (verbatim) -- the second GHI close of the session.
- git-sync (verbatim) -- the second sync, after the #727 commit.
- run triagr and create new handoff, git sync that (verbatim, operator spelling preserved) -- the triage re-run, this document, and the sync that follows.
- run triagr and create new handoff, git sync that (verbatim, operator spelling preserved) -- the triage re-run, the predecessor handoff, and its sync.
- approve (verbatim) -- Step 3 approval of the drafted v0.34.1 release notes. Under the ceremony Iron Law this authorized Steps 4a through 4e to run to completion without further pauses, and they did.
- refresh handoff (verbatim) -- this document.
- The coverage gap routes as a **correction under ADR-0.0.73**, never a fresh pool ADR (verbatim: *"if this is a prior adr, them is a new discovery an extension of that adr?"*). This applied the operator's own correction-vs-enhancement doctrine to a routing recommendation that had contradicted it; an `improvement` insight was recorded via `gz insights remember` before the corrected work proceeded, per Behavior Rule 11.
- Fix immediately rather than defer to campaign sequencing (verbatim: *"do it right, fix things now"*).
- File both findings as **one GHI with two arms** rather than two issues or none (AskUserQuestion selection, 2026-08-05).
- Authorize the handoff resume so filing could proceed (verbatim: *"Rule now so I can file"*, booked via `gz handoff authorize`).
- Commit the untracked prior-session handoff and author a successor (verbatim: *"commit and update handoff"*).
- Promote the exit-code-integrity clause to a mechanical hook (verbatim: *"Promote exit-code-integrity hook"*, selected via AskUserQuestion and booked through `gz handoff authorize` — this is the ruling that lifted the resume gate and scoped the entire session). Chosen over returning to the Magna Carta campaign item (`ADR-0.35.0`, `Pending` 0/10), draining the 23 grandfathered scorecard rules, and a review-only ruling authorizing nothing.
- Sync after the build (verbatim: *"yes, git sync"*). Executed as `gz git-sync` dry-run then `--apply`, pushing `97c32d7d9`.
- Author a successor handoff and sync it (verbatim: *"update hsndoff and git sync it"*, operator spelling preserved) — this document and the `gz git-sync` that follows.
- Fix the clearance defect first, verbatim: "go ahead — open the GHI and start on item 1 - design against the constraints of the claude code docs".
- Commit the fix and update GHI #732, verbatim: "commit and update 732".
- The remaining lifecycle items are refinements to the original handoff ADR, verbatim: "these are refinements to the original handoff adr".
- Do not reopen ADR-0.0.65, verbatim: "no, author a supplememt, i don't think we actually reopened 0.0.65".
- Route the remaining work as pool or as direct GHIs attributed to the handoff ADR, verbatim: "stop. pool it. or direct ghi and attribute to the handoff adr".
- Handoff is startup and shutdown behavior regardless of how the aircraft is used; airlock is use tracking and justification.
- A mid-flight bookmark amends the clearance and never revokes it; revocation would be a Schrodinger's flight.
- The exit beat must not block, verbatim: "DO NOT BLOCK HERE. Observe, contextualize, update status, develop suggestions, pose questions, write them all to the handoff bookmark, and leave."
- Sync blockers are always resolved, but resolving them is not conflated with the bookmark; the bookmark's job is done once written.
- Record clearance amendments the way ATC records all clearances issued and all amendments.
- The CaptainOverride rename is not worth doing if it turns out to be a hassle.
- git-sync (verbatim) — booked via gz handoff authorize; scoped the session's first act to the sync alone.
- file the two lifecycle GHIs (verbatim) — routed through /ghi-author, which found #756 and #757 already open and correctly refused to file duplicates.
- do next work (verbatim) — authorized the first half of GHI #756.
- continue with 1, fix 2 (verbatim) — authorized the SessionEnd exit beat and this successor handoff.
- The bookmark is durable evidence and the hook should land it, not merely write it (verbatim: 'the bookmark is durable evidence — the hook should commit it').
- SessionStart owns sensemaking; committing at the exit beat is too much friction, and the operator will normally author a handoff and git-sync manually on the way out (verbatim: 'i think the design is something for session start to pick up for planning since committing is going to be too much friction. this session end is a precuation').
- SessionStart must look for bookmarks, offer sensemaking, and flag them for inclusion going forward (verbatim: 'make sure we look for bookmarks as a part of sessionstart - offer the do sensemaking and flag for inclusion moving forward').
- Fix the shadowing as a direct fix under a new GHI and file the validator durability gap separately (verbatim: 'yes, ghi it').
- Proceed on the resumed handoff at session start (verbatim: 'review handoff, run ghi triage, review'); booked via gz handoff decide, advised step 2 set aside.
- Staged counts as durable; the exit hook should git add the bookmark (verbatim: 'staged counts as durable — have the hook git add it').
- SessionStart should look for bookmarks, read the ledger, and develop a handoff account from all evidence (verbatim: 'then, sessiostart looks for those, looks at ledger, and develops a handoff account based on all evidence').
- Shelling out to git is acceptable for the validator; the bookmark is a safety valve and any dirty tree will be caught (verbatim: 'the bookmark is a safety valve, so simpler shellling out to git is fine. any dirty tree will be caught').
- Be intentional about bookmarks: skip the bookmark when a proper handoff and a clean tree exist (verbatim: 'if we have a proper frsh handoff and a clean tree, skip the bookmark').
- Fix the three-reader residual rather than recording it as a note (verbatim instruction to fix the residual paragraph).
- Skip predicate is provably-nothing-since rather than fresh-plus-clean, and a deliberate skip books a ledger event rather than being silent.
