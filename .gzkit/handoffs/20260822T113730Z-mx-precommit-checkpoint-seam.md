---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-22T11:37:30Z'
agent: claude-code
continues_from: .gzkit/handoffs/20260822T104010Z-session-exit-bookmark.md
---

## Current State Summary

GHI #843 is CLOSED (fixed) and synced. The MX Maintenance Hangar now has authority over the pre-commit enforcement surface, which it never had: every guard in `gzkit.hooks.guards` self-decided fatality with a bare `return 1`, and two chore checkers ran as their own pre-commit entrypoints consulting nothing. Measured 2026-08-22 before the fix: ZERO checkpoint consumers anywhere under `src/gzkit/hooks/`. Landed as `92667fe5` (the guards.py seam) and `7af1a54b` (the rest of the surface, plus repair of two hollow tests in the first commit), synced at `ca64a840`; main and origin/main agree. GHI #852 was filed from the same work and is OPEN, awaiting an operator ruling. Nothing is left in flight: tree clean, no locks claimed, no pipeline marker, no hangar open.

## Important Context

The GHI's body offered three 'candidate directions (not a decision)' and the inbound handoff advised 'rule on GHI #843'. Both were superseded by reading, not by judgment: ADR-0.0.74 Boundary Invariant #2 had ALREADY ruled -- 'a guard that decides its own severity OR its own disposition without the checkpoint is the named coverage defect.' Direction 2 (narrow the advertised scope) would have contradicted a Boundary Invariant of a terminal ADR, so there was no genuine three-way choice. This was the THIRD recurrence of one class: GHI #638 (gz check step layer, closed 2026-06-24) and GHI #651 (enforcement floor demoting inside the hangar, closed 2026-07-01) were the first two. The root is an inventory gap ADR-0.0.74 Negative #6 predicted verbatim -- 'a funnel that forgets it silently stays hard' -- because the funnel-inventory fence OBPI-0.0.74-02 shipped enumerates validate_cmd and nothing else. CRITICAL for anyone touching this next: the fix does NOT unblock the ledger repair that surfaced #843, and that is correct. `ledger` is a GATE5_INVARIANTS member, so `checkpoint.resolve` short-circuits before the marker is read; a hand-edit of .gzkit/ledger.jsonl is refused inside the hangar exactly as outside. The hangar was never the governed route out of a mis-ordered ledger. That route is GHI #611 (open). Floor membership is a STRING MATCH against GATE5_INVARIANTS with nothing witnessing that a guard enforcing a floor concern registers under the floor name -- that is the whole subject of GHI #852. A rule-version bump is expensive here: bumping mx-mode.md to 1.2.0 cascaded into advisory-scorecard rows (Coverage Ledger version equality), the Summary roll-up count, bullet-retention (scorecard Rule cells must quote the rule bullet VERBATIM), and the tautological-test audit. Price that before bumping a rule.

## Decisions Made

- [agent-chose] Routed #843 as a direct fix rather than escalating for a ruling, because ADR-0.0.74 BI#2 already decided it; the 'needs a decision' framing in the GHI body was written without that invariant in view.
- [agent-chose] Pinned `post-authoring-src-commits` at CRITICAL to PRESERVE today's behaviour rather than to rule on it. Whether an open hangar should be able to demote the Stage-2 production-code fence (GHI #844) is an operator call, disclosed on #843 and still unmade.
- [agent-chose] Bound `forbid_manual_ledger_edits` to the existing floor name `ledger` and `forbid_unattested_obpi_completion_commits` to `gate5-attestation`, borrowing GATE5_INVARIANTS membership rather than inventing new floor members. Adding a member is a BI#3 change and operator territory.
- [agent-chose] Named the inertness chore's guard `ledger-vocabulary-inertness`, deliberately NOT `ledger` -- that name means ledger INTEGRITY and never demotes, while the chore audits schema-vocabulary disclosure.
- [agent-chose] Scored advisory-scorecard rows 62c/62d **Promotable**, not Mechanical. The scorecard reserves Mechanical for a registered NC:<claim-id> from the @enforces registry; these fences are unit tests, and claiming Mechanical on them is the false-green shape pythonic.md 0.3.0 recorded.
- [agent-chose] Filed GHI #852 rather than fixing the authorship demotion inline, because ADR-0.0.74 Negative #7 forbids binding a narrower proxy for `operator-pii` and the resolution is a genuine operator ruling.
- [operator-ruled] Sync the work (verbatim: 'yes git sync'). Executed via the git-sync skill: dry-run, then `uv run gz git-sync --apply`.
- [operator-ruled] Scope discipline correction, in flight (verbatim: 'every goddamned move in gzkit takes hours to complete - this is a farce' and 'this should NOT take a fucking hour to fix!!!!!!!!!!!'). The #843 fix itself landed in roughly twenty minutes; the remaining hour was agent-initiated expansion from the GHI's instance to its full class and onward into coupled doc surfaces. Recorded as an `improvement` insight. The standing correction: land the GHI's own scope, close it, then OFFER a class extension as a separate commit rather than chaining it.

## Immediate Next Steps

1. Rule on GHI #852 -- `gz validate --authorship` demotes to advisory inside the hangar, so the commit-time operator-PII guard prints a green against a violating email. Verified end-to-end, not inferred. Three candidate directions are in the body; direction 1 (register under the floor name `operator-pii`) brushes against ADR-0.0.74 Negative #7's narrower-proxy prohibition, which is why it is a ruling and not a patch.
2. Rule on whether an open hangar should be able to demote `post-authoring-src-commits`, the Stage-2 production-code fence from GHI #844 [settled]. It is currently pinned CRITICAL, preserving pre-#843 [settled] behaviour. Pinning it is the conservative default; demoting it is the mx-mode.md declared default for a non-floor guard, so the two doctrines point opposite ways here.
3. Rule on GHI #847 [settled]'s `ledger-writer` arm has NO OPEN TRACKER -- decide whether to file one. The inbound handoff advised 'rule on the ledger-writer arm', but #847 closed COMPLETED on 2026-08-22 (`dc572677`, `d3216102`) while that arm stayed unbuilt, so the work is now dead-lettered: named in a closed issue's comments and in successive handoffs, tracked nowhere. It wants a commit-time or filesystem-time observation, but emitting `artifact_edited` from pre-commit changes ledger volume and shape -- a design decision, not a patch. Surfaced by the settled-citation annotator on this handoff, which is the mechanism working: it flagged a prospective step citing a closed GHI.
4. Rule on GHI #849 -- the ARB RED witness is honest but inert on landed work, so `--from=verify` gates nothing on that path. Carried unchanged from the inbound handoff.
5. Decide what to do with GHI #835 -- the remaining tractable win is running validator scopes in one process rather than as separate `uv run gz` invocations, worth roughly 15s of the ~145s gate. Still no comment posted recording the prior session's measurements; they live only in the `db6ec623` and `4b543052` commit bodies.
6. Resume `ADR-0.35.0-canon-entry-corpus-landing`. It is the lowest-semver feature ADR holding unlanded briefs, so ascending-semver order puts it ahead of ADR-0.36.0 and ADR-0.37.0 regardless of campaign sequencing. Run `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for its live lifecycle and closeout blockers; no figure is transcribed here.

## Pending Work / Open Loops

GHI #852 (open) -- filed this session; the inverse of #843 [settled] on the gz validate side. A guard bound to a floor CONCERN registered under a non-floor NAME. Also records an adjacent shape worth scoping in the same pass: an UNREGISTERED scope name resolves to `advisory` rather than raising, so a mistyped scope id in a future call site silently becomes advisory and nothing says so.
GHI #611 (open) -- the genuine governed route out of a mis-ordered ledger: a general append-only corrective-action primitive. #843 [settled] correctly did NOT unblock this; the ledger floor holds inside the hangar by design.
GHI #847 [settled] ledger-writer arm, GHI #849, GHI #835 -- all carried unchanged from the inbound handoff, untouched by this session.
Promotion path left open by choice: advisory-scorecard rows 62c/62d are Promotable pending an un-forced @enforces negative control per ADR-0.0.74 items 15-19. Authoring those NCs would promote both rows to Mechanical.
Two chore checkers now consult the checkpoint but have no NC either; they are covered by unit and mutation tests only.
Not investigated: whether `gz check`'s step-layer guard names carry the same floor-name mismatch as `authorship`. `_STEP_GUARD_META` maps roughly fifty steps and only `authorship` was checked, so other floor-concern steps under non-floor names may exist. That is a scoping question for #852.

## Verification Checklist

uv run gz obpi lock list  # expect: no active locks
git rev-list --left-right --count origin/main...HEAD  # expect: 0 0
gh issue view 843 --json state,stateReason  # expect: CLOSED/COMPLETED
gh issue view 852 --json state  # expect: OPEN
ls .gzkit/mx.json  # expect: No such file -- no hangar open
ls .claude/plans/.pipeline-active*.json  # expect: no matches -- no pipeline in flight
uv run -m unittest tests.test_hooks_guards tests.mx.test_precommit_checkpoint_surface  # expect: OK, 49 tests
uv run gz validate --advisory-scorecard  # expect: exit 0 (mx-mode.md scored at 1.2.0)
uv run gz check  # expect: All checks passed

## Evidence / Artifacts

`src/gzkit/hooks/guards.py` -- the seam: `_GUARD_META` inventory + `run_guards`
`src/gzkit/mx/checkpoint.py` -- `blocks()` and `demote_notice()`, the one authority the three pre-commit entrypoints share
`.gzkit/chores/control-surface-validator-reachability/check_reachability.py` -- wired
`.gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py` -- wired
`tests/test_hooks_guards.py` -- `TestMxCheckpointSeam`, the inventory fence inside guards.py
`tests/mx/test_precommit_checkpoint_surface.py` -- `TestPrecommitSurfaceInventory`, which walks `.pre-commit-config.yaml` itself
`.gzkit/rules/mx-mode.md` -- rule-version 1.2.0
`docs/governance/advisory-rules-audit.md` -- rows 62c/62d added, row 62 amended, Coverage Ledger at 1.2.0
`.gzkit/insights/agent-insights.jsonl` -- the scope-discipline improvement record
