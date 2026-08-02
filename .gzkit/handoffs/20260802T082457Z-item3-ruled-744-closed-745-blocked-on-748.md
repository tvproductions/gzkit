---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-02T08:24:57Z'
agent: claude-code
session_id: 89769dcd-843b-4f3a-8933-98ecc25b4455
continues_from: .gzkit/handoffs/20260802T014210Z-handoff-refresh-synced-queue-unworked.md
---

## Current State Summary

Five commits landed and pushed; tree clean, level with origin, no active locks. `gz check` exits 0 at 48 steps, verified unpiped (REAL EXIT: 0 read from a redirect, per tests.md § Verification exit-code integrity).

Movement A item 3 is RULED and checked off the campaign: `foundation-adr-registers-invariant` retired as superseded by the ADR-0.34.0 Foundation Sunset. GHI #744 is CLOSED with its residual discharged. GHI #745 is advanced and precisely blocked. Four new GHIs filed with reproductions: #746, #747, #748, #749.

The campaign's Movement A now has one open item left (item 2, ADR-0.35.0 at 0/9). Item 3's checkbox is checked with the ruling and two corrections to its own prior text recorded inline.

## Important Context

THE SESSION'S CENTRAL FINDING, and the thing most likely to be mis-read by a successor: gzkit's enforcement is strong wherever a validator reads STRUCTURED DATA and absent wherever PROSE ASSERTS A MECHANISM. Three vapor-mechanism claims were found and all three had propagated unchallenged: the invariant registry named `gz validate --foundation-registers-invariant` (never existed), the campaign named `--invariant-witness` as merely unenrolled (never existed), and `governance-core.md` names a speculative escape marker for `audit_cli_alignment` (never adopted there). Every gate in this repo checks facts; none checks the claims governance makes about its own machinery.

BUT THE SYMMETRIC CORRECTION MATTERS MORE. I initially concluded the speculative marker "was never built" and filed #746 partly on that reading. That was WRONG, and the Step-0 prior-art search on the next GHI caught it. The marker EXISTS: `_SPECULATIVE_MARKER = "<!-- gz-validate-skip: command-shape -->"` at `src/gzkit/hooks/obpi.py:57`, built under GHI #432, and its comment records that it deliberately mirrors the convention in `complexity_doctrine_links.py` so both validators share one marker shape. `obpi.py`'s extractor is ALSO already fenced-aware and multi-word-aware. So all three gaps reported against `trust_audits/cli.py` are already solved in a sibling extractor in the same codebase.

Those two failure shapes look identical from outside — a rule pointing at capability the validator lacks — but they invert the remedy. One says BUILD IT; the other says STOP REBUILDING IT. Do not collapse them. #746 is the first kind (build the wiring). #748 is the second kind (converge on the extractor that already works). A successor who treats #748 as "add fenced-block support to cli.py" will write a third copy of a thing that exists twice.

`gz check` is now 48 steps, not 47. Adding a step is NOT one edit: the QC-binding registry refuses to build with an unclassified step, and a `bound` classification requires an `@enforces` negative control with no debt escape (ADR-0.0.74 Boundary Invariants #6/#8). Four surfaces must land together — `_STEP_CLASSIFICATION`, an entrypoint, a fixture, and a table entry pinning the expected failure message.

Two harness traps hit this session, both worth knowing. First, background task notifications report the exit code of the PIPELINE, not the command: a `uv run gz check | tail -25` reported "exit code 0" while the output said "Some checks failed". That is exactly GHI #589's named trap. Capture to a file and read it. Second, the handoff-resume gate refuses compound commands and pipes even when every element is a read (`ls && git log`, `grep | sort | uniq`) — that is GHI #732's live class, hit twice before the ruling was booked.

## Decisions Made

- [operator-ruled] "Rule item 3, then work the queue" — booked verbatim via `gz handoff authorize` at session start; this is the ruling that lifted the resume gate and set the whole session's scope.
- [operator-ruled] Movement A item 3 disposition: retire the claim as superseded by the Foundation Sunset. Chosen over three alternatives presented (make the claim true by backfilling 51 ADRs; rule it a permanent exception; withdraw the entry). Turned on the fact that ADR-0.34.0 closed the foundation kind at both `adr_created` ingresses, so the claim's subject set is permanently frozen and can never be exercised again.
- [operator-ruled] GHI #744 residual: enroll the ten unreachable default-tier scopes and measure the cost. Chosen over enrolling a subset, leaving them declared-out, or filing a follow-up.
- [operator-ruled] GHI #745 scope: exempt pool ADRs structurally rather than building a per-reference marker, narrowing the rule's declared scope, or deferring.
- [operator-ruled] "do both" — fix the live-surface dead pointers now as a bounded direct fix AND route the speculative-marker build to its own work item.
- [operator-ruled] Sync to origin via `gz git-sync`, twice (after the first three commits, and after the doc repairs).
- [agent-chose] Retained `foundation-adr-registers-invariant.json` rather than deleting it. REQ-0.0.37-01-03 (attested) asserts only that the three seed files exist, load, and validate against the schema — never that the claim text is true — so rewriting `claim` and `structural_witness` preserves attested canon exactly while deletion would falsify it.
- [agent-chose] Enrolled the ten default-tier scopes as ONE bare `uv run gz validate` step rather than ten flag-scoped steps. Measured 1.98s for the whole tier in one subprocess; ten steps would have cost ten process spawns for the same coverage.
- [agent-chose] Made `gz check` membership DECLARED (`data/check_scope_membership.json`) rather than deriving `_build_check_steps` from the scope registry, which was the GHI's other candidate. Derivation would auto-enroll 52 scopes including expensive ones, and would still miss the three scopes that dispatch outside `VALIDATOR_REGISTRY`.
- [agent-chose] Applied the terminal-brief and self-declared-SUPERSEDED exemptions on top of the operator-ruled pool-ADR exemption when measuring #745. Both are precedent-backed — `is_terminal_brief_status` is already used by the manpage arm of the same validator — so this is precedent extension, not a new taxonomy.
- [agent-chose] Stopped short of widening `--cli-alignment` to the full declared `docs/**` scope. The residual 37 sites are design and proposal documents describing genuinely planned surfaces, which needs #748's marker adoption first; widening now would fail 37 sites closed.
- [agent-chose] Filed #749 rather than editing the `gz superbook` runbook section. Six references across four subsections describe a capability that never existed at any commit; recovery requires ruling whether the superpowers-interop story is real, which is not a rename.

## Immediate Next Steps

1. Work GHI #748 — converge the two verb extractors. This is the highest-leverage item in the queue: one refactor retires three separately-reported gaps (#745 fenced blocks, #588 multi-word, the unadopted speculative marker) and unblocks #745's full-scope widening. Read the § Important Context note before starting so it is built as a convergence, not a fourth reimplementation.
2. Rule on GHI #749 — is the `gz superbook` superpowers-interop bridge intended-and-unbuilt, or abandoned? Six references in a live runbook hang on the answer. This is an operator direction call, not an agent call.
3. Work GHI #746 — wire `validate_invariant_witnesses` as a registered `gz validate` scope. Its precondition is now discharged: the committed registry carries zero vapor witnesses after this session's item-3 ruling, so enrolling it lands green rather than holding a gate over a known-red tree.
4. Open ADR-0.35.0-canon-entry-corpus-landing and begin landing its 9 briefs, currently 0/9. This is Movement A item 2 and the only remaining open item in Movement A now that item 3 is ruled.
5. Decide whether the 2026-08-01T12:06:06Z ruling to evaluate the Opus 5 system card against gzkit should be re-run. Re-verified this session: no artifact from it exists anywhere in `docs/` or `.gzkit/insights/`. The ruling still stands undischarged.

## Pending Work / Open Loops

- [tracked] GHI #748, `audit_cli_alignment` reimplements a weaker verb extractor than `hooks/obpi.py` already ships. Open, unworked. Blocks #745's full-scope widening.
- [tracked] GHI #749, the GovZero pipeline runbook documents a `gz superbook` bridge for a verb never registered at any commit. Open, needs an operator direction ruling.
- [tracked] GHI #747, no ledger event-inspection verb. Three surfaces independently prescribed `gz ledger tail`; all three repaired to the grep idiom. A new verb is a CLI contract change, so Heavy lane, not a direct fix.
- [tracked] GHI #746, `validate_invariant_witnesses` has no CLI wiring. Open; precondition now discharged.
- [tracked] GHI #745, open with a blocker comment. Recognizer and skills-scope fix landed; live-surface repairs landed; full widening blocked on #748.
- [tracked] GHI #588 class is still live on `--cli-alignment`: `_known_cli_verbs()` returns top-level verbs only, so `gz adr status` is checked as `adr`. Folded into #748 rather than filed separately.
- [tracked] GHI #740, ADR-0.34.0 shortfall S3. Open, untouched this session.
- [tracked] GHI #742, `validate --documents` silently exempts no-frontmatter ADRs. Open, untouched.
- [tracked] GHI #732, the handoff-resume gate's read allowlist is command-SHAPE based, so compound reads and pipes are refused. Hit twice this session. Open, untouched.
- [tracked] GHI #730, `@covers` satisfies the tautological-test production-code exemption, masking 217 of 290 ops. Open, untouched.
- [open] ADR-0.35.0-canon-entry-corpus-landing at 0 of 9 briefs landed. Movement A item 2; the last open item in Movement A.
- [open] 42 of 84 validate scopes are declared out of `gz check`, recorded in `data/check_scope_membership.json`. Every default-tier scope now gates; the explicit-tier residue is a standing decision surface, not a defect.
- [open] Five modules over the canonical `radon_raw_nloc` block band under the shrink-only ratchet. They may only shrink; splitting is unscheduled.
- [unknown] The 2026-08-01T12:06:06Z Opus 5 system-card evaluation ruling. Re-verified this session as producing no artifact in the tree.

## Verification Checklist

- `git rev-parse --short HEAD` resolves to `1b7852556` on `main`; tree clean, nothing unpushed. NOTE: a handoff can never truthfully pin its own post-sync HEAD, because the commit that lands it changes HEAD. If this SHA is one behind, that is the expected shape, not drift.
- `uv run gz check` exits 0 across 48 steps. Run it WITHOUT a pipe and read the exit from a redirect: piping through `tail` reports the filter's status, not the gate's (tests.md § Verification exit-code integrity, GHI #589).
- `uv run gz validate --cli-alignment` exits 0. The enforced source set is now 267 files, including all 68 SKILL.md files and the governance runbook.
- `uv run gz validate --taxonomy` exits 0. This is the witness the retired invariant entry now names.
- `uv run -m unittest tests.governance.test_check_scope_parity` reports 14 tests OK.
- `uv run -m unittest tests.governance.test_cli_alignment_scope` reports 8 tests OK.
- `uv run -m unittest tests.governance.test_invariant_witness` reports 9 tests OK, with the committed-registry fence at `frozenset()`.
- `uv run gz validate --qc-binding` exits 0 with the new `Validate default scopes` step classified and its negative control registered.
- `uv run gz obpi lock list` reports no active locks.
- `gh issue view 744` reports CLOSED. `gh issue view 745`, `746`, `747`, `748`, `749` all report OPEN.
- `grep -c '"in_check"' data/check_scope_membership.json` finds the roster; `in_check` carries 42 entries and `out_of_check` 42, with zero default-tier scopes unreached.

## Evidence / Artifacts

- `.gzkit/invariants/foundation-adr-registers-invariant.json` -- the retired entry; claim now states the sealed Foundation Sunset reality, witnessed by `gz validate --taxonomy`
- `tests/governance/test_invariant_witness.py` -- shrink-only fence, now at `frozenset()`; observed firing on the rewrite before being closed
- `docs/governance/build-to-1.0-campaign-2026-07-18.md` -- Movement A item 3 checked, with two corrections to its own prior text (the 74-vs-51 figure and the vapor `--invariant-witness` claim)
- `data/check_scope_membership.json` -- declared `gz check` scope membership, 42 in / 42 out, zero default-tier unreached
- `tests/governance/test_check_scope_parity.py` -- the parity fence; five extractor tests against synthetic sources so it cannot pass by computing nothing
- `tests/governance/test_cli_alignment_scope.py` -- eight tests pinning fenced-block and skills-scope detection; five observed RED before the fix
- `src/gzkit/governance/trust_audits/cli.py` -- widened sources and the fenced-block recognizer
- `src/gzkit/qc_binding.py` -- `_STEP_CLASSIFICATION` entry for the new step
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` -- the negative-control fixture planting a rule-version marker drift
- `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py` -- the default-tier collection entrypoint
- `src/gzkit/hooks/obpi.py` -- THE EXTRACTOR TO CONVERGE ON (line 53 pattern, line 57 marker); read before starting #748
- `.gzkit/handoffs/20260802T014210Z-handoff-refresh-synced-queue-unworked.md` -- predecessor

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
