---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-02T01:01:23Z'
agent: claude-code
session_id: 0145e706-edae-4c07-bdad-3dc761fd0c3f
continues_from: .gzkit/handoffs/20260801T103513Z-chore-acceptance-class-fixed-four-audits-red.md
---

## Current State Summary

The predecessor handoff is superseded by work that landed the same day. Its sole outstanding item -- re-run the four control-surface audits -- was executed 2026-08-01 across commits 2810b8e51, 2ac4df598, 0551bbbd3 and 4048a4486, and GHI #743 closed at 2026-08-01T23:40:06Z. All four proof-freshness checks now exit 0, verified this session. HEAD is 4048a4486 on main, level with origin, tree clean, no active locks, 37 chores all carrying logs. The four audit passes routed two new class GHIs, #744 and #745, both open and unworked. That session ended without authoring a successor handoff, so this one booted on orientation advice its own tree had already discharged. Refreshing the handoff is the only work this session performed; nothing else in the queue was touched.

## Important Context

Three things a resuming agent will otherwise get wrong. FIRST, the predecessor recorded false dates for its own evidence. Its Open Loops bullet says two chores had proofs from 2026-06-25; that date never existed. check_proof_freshness.py rendered commit epochs via git show -s --format=%cs @{<epoch>}, but @{n} is reflog-relative revision syntax, not an epoch formatter -- it clamps to the reflog floor for anything older and emits a warning on stderr while returning the floor date on stdout. True dates were 2026-05-10, so the staleness was ~12 weeks, not ~5. Exit codes were always sound because main compares raw epochs from _last_commit_epoch; only the prose lied, which is the worse failure because remediation gets planned off the explanation. Fixed in 2ac4df598 and pinned by two mutation-proven assertions in 4048a4486. SECOND, the predecessor Open Loops entry reading ADR-0.34.0 audit shortfalls S1 and S2 still have no GHI of their own is literally true and materially misleading. Both were REMEDIATED in-session per the disposition table in the ADR-0.34.0 AUDIT.md; only S3 is tracked, as GHI #740. An insight logged 2026-08-01T11:59:06Z records that the wording nearly caused three cargo-cult GHIs to be filed, and prescribes that Open Loops entries carry a disposition verb rather than the mere absence of a tracker. This handoff adopts that shape. THIRD, both new GHIs deliberately refuse to quote a violation count. #744 declines an unreachable-scope number because the gz check step list is not name-mapped to validate flags, so a naive match is untrustworthy and the enumeration is itself part of the work. #745 declines a violation count because the detector cannot see fenced blocks, so the true count is unmeasurable until the recognizer is widened -- and it warns that the backlog widening surfaces is the finding, not a reason to keep the detector narrow. Separately, three operator rulings were booked against the predecessor after it was written: git sync only at 10:42Z, yes, sync it, then GHI #743 (OPEN) at 12:05Z which authorized the audit re-run, and at 12:06Z an instruction to evaluate the Opus 5 system card against gzkit. No artifact from that third ruling exists anywhere in the tree.

## Decisions Made

- [operator-ruled] Refresh the handoff first -- booked verbatim via gz handoff authorize at 2026-08-02T00:58:21Z for session 0145e706-edae-4c07-bdad-3dc761fd0c3f. This authorized the handoff refresh and nothing beyond it; every item in Immediate Next Steps remains unexecuted and unauthorized.
- [agent-chose] Authored with no adr_id, because the work this handoff records (chore audits and GHI repair) has no parent ADR, and mode rather than adr_id is the is-this-a-handoff discriminator (GHI #709).
- [agent-chose] Corrected the S1/S2 open loop rather than carrying the predecessor wording forward, because the AUDIT.md disposition table records both as Remediated and the carried wording had already nearly produced three unnecessary GHIs.
- [agent-chose] Adopted disposition verbs in Pending Work per the 2026-08-01T11:59:06Z insight, so an entry states remediated, tracked, open or unknown rather than leaving the reader to infer status from the absence of a tracker.
- [agent-chose] Filed no GHI for the missing successor handoff. Handoff authoring is on-demand by contract, so the omission was a session authoring choice, not a tool defect; recording it here is the tracking.

## Immediate Next Steps

1. Rule on Movement A item 3, the foundation-adr-registers-invariant disposition. One line of operator canon, now carried unexecuted across three consecutive handoffs. It unfences tests/governance/test_invariant_witness.py so --invariant-witness can rejoin gz check.
2. Work GHI #744. Enumerate which gz validate scopes gz check actually runs, then choose between a fail-closed parity test and deriving _build_check_steps from the scope registry. GHI-tracked, so it routes direct-fix per operator doctrine.
3. Work GHI #745. Teach the three --cli-alignment detectors to read fenced blocks, then re-audit the full declared scope for what was hiding. Expect a backlog; the backlog is the finding.
4. Open ADR-0.35.0-canon-entry-corpus-landing and begin landing its 9 briefs, currently 0/9. Topmost unchecked campaign item, and the campaign governs pull order.
5. Decide whether the 2026-08-01T12:06:06Z ruling to evaluate the Opus 5 system card against gzkit produced anything worth keeping, or whether it should be re-run.

## Pending Work / Open Loops

- [tracked] GHI #744, gz check membership is a hand-written literal list in src/gzkit/commands/quality.py that never reads the validate scope registry. Open, unworked. The default-tier scope --rule-version-markers has never fired on any commit.
- [tracked] GHI #745, all three --cli-alignment verb detectors require backticks or quotes, so a verb inside a fenced block is invisible. Open, unworked.
- [tracked] GHI #740, ADR-0.34.0 shortfall S3: foundation closure is framework-wide, not project-local as decided. Open.
- [remediated] ADR-0.34.0 shortfalls S1 and S2. Both fixed in-session per the AUDIT.md disposition table; they are NOT untracked work and need no GHI. This supersedes the predecessor Open Loops bullet.
- [open] Movement A item 3, the foundation-adr-registers-invariant disposition. Unruled.
- [open] ADR-0.35.0-canon-entry-corpus-landing at 0 of 9 briefs landed.
- [open] 513 mypy-style type-ignore comments under tests/ and scripts/. They suppress nothing in ty, and tests/governance/test_type_ignore_syntax.py fail-closes on src/** only, so that surface is unguarded. Undecided whether deliberate.
- [open] Ruff D past src/gzkit. Full adoption surfaces 6321 findings under tests, features and scripts, plus 74 in generated skill mirrors and hooks that must never be hand-edited.
- [open] Five modules over the canonical radon_raw_nloc block band under the shrink-only ratchet: cli/parser_artifacts.py 1743, cli/parser_maintenance.py 1582, commands/obpi_complete.py 1429, commands/validate_cmd.py 1309, commands/adr_audit.py 1034. They may only shrink; splitting is unscheduled.
- [unknown] The 2026-08-01T12:06:06Z ruling authorized an Opus 5 system-card evaluation against gzkit. No artifact from that session exists in the tree.

## Verification Checklist

- git rev-parse --short HEAD resolves to 4048a4486 on main; tree clean, nothing unpushed.
- uv run python scripts/check_proof_freshness.py <slug> exits 0 for all four control-surface slugs: rule-conflicts, permission-consent-drift, skill-rule-reachability, rule-vs-check-drift. If any exits 3, a surface moved after 2026-08-01 and that audit is stale again.
- gh issue view 743 reports state CLOSED; gh issue view 744 and gh issue view 745 both report OPEN.
- uv run gz obpi lock list reports no active locks.
- uv run gz chores audit --all lists 37 chores, every one with a log.
- uv run gz validate --rule-version-markers exits 0. Run it DIRECTLY -- per GHI #744 this scope is registered but absent from gz check, so a green gz check proves nothing about it.
- uv run gz check exits 0.

## Evidence / Artifacts

- `.gzkit/handoffs/20260801T103513Z-chore-acceptance-class-fixed-four-audits-red.md` -- predecessor, superseded on its headline item
- `scripts/check_proof_freshness.py` -- the freshness gate whose date rendering was the reflog artifact
- `tests/governance/test_proof_freshness_date_format.py` -- two mutation-proven assertions pinning epoch rendering, the second forbidding any subprocess call
- `.gzkit/chores/control-surface-rule-conflicts/proofs/summary.md` -- 28 files, 378 pairs, 17 scored rows
- `.gzkit/chores/control-surface-rule-vs-check-drift/proofs/summary.md` -- 25 rules, 122 enforcement claims, 41 scored rows
- `.gzkit/chores/control-surface-skill-rule-reachability/proofs/summary.md` -- 68 skills, 25 rules, 12 orphaned, 3 hard dangling citations
- `.gzkit/chores/control-surface-permission-consent-drift/proofs/summary.md` -- 216 grants, 6 live drift findings against a prior run recording 0
- `src/gzkit/commands/quality.py` -- the hand-written _build_check_steps literal list behind GHI #744
- `src/gzkit/governance/trust_audits/cli.py` -- the three delimiter-bound verb detectors behind GHI #745
- `.gzkit/rules/mx-mode.md` -- marker and block quote reconciled in 2810b8e51
- `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/audit/AUDIT.md` -- the S1/S2/S3 disposition table
- `tests/governance/test_invariant_witness.py` -- the shrink-only fence that Movement A item 3 would unfence

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
