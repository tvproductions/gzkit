---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-05T08:22:07Z'
agent: claude-code
session_id: 1f2ee26e-2ca3-44aa-8c6c-3c05ee98587a
continues_from: .gzkit/handoffs/20260805T020727Z-ghi-754-scorecard-clause-coverage-landed.md
---

## Current State Summary

Promoted `.gzkit/rules/tests.md` § Verification exit-code integrity from binding-but-unenforced prose to a live mechanical gate. One commit, `97c32d7d9`, pushed to origin/main.

The clause had been binding since rule `0.8.0` (GHI #589) and enforced by nothing. `docs/governance/advisory-rules-audit.md` row 66 scored it **Promotable, unenforced** and named the promotion path; the predecessor handoff carried it as advised step 5. It is the highest-frequency observed violation class in agent sessions, and its failure mode is the worst kind — it does not error, it produces a confident false green that then gets relayed to an operator as attestation evidence.

Landed: `verifier-pipe-gate.py`, a PreToolUse hook on `Bash`, refusing a verifier in any non-final pipeline stage. Decision core at `src/gzkit/verifier_pipe_gate.py`; quote-aware `shlex` configuration single-sourced into the new `src/gzkit/shell_reading.py` and shared with `handoff_resume_gate._is_compound`; live negative control `verifier-exit-status-masked` wired into `_ensure_production_claims_registered`. Rule bumped `0.13.0` to `0.14.0`; scorecard row 66 rewritten Promotable to **Mechanical** in the same commit, because the advisory-scorecard audit compares them by rule-version and would otherwise fail closed.

Dogfooded live, which is the strongest evidence in the session: once sync wired the hook into this session's own `Bash` chain, `uv run -m unittest -q tests.hooks.test_verifier_pipe_gate | tail -3` was refused with the full three-part recovery prose. The gate blocked its own author.

`uv run gz check` exits 0 across 49 steps; `uv run -m unittest -q` exits 0 at 7914 tests (up 22). Enforcement floor 66 verified, 0 facade, 0 test-bug. Tree clean, level with origin/main.

## Important Context

**The gate was built one step wider than its named promotion path, deliberately.** Scorecard row 66 prescribed a hook "refusing `<verifier> | <filter>`". That scoping is wrong and would have reproduced this codebase's most-repeated mistake. The shell reports the LAST stage's exit *whatever that stage is*, so a `tail`/`head`/`grep` allowlist waves `gz check | cat` straight through — the identical defect wearing a different name. The implemented predicate is *a verifier in any non-final pipeline stage*. This is the same enumerate-the-examples miss the resume gate's own allowlist has now made three times (`_PERMITTED_BASH` documents all three: no `gh`, no `git rev-list`, then instance-fixed instead of class-fixed under GHI #732). Do not narrow it back to the named filters.

**Two escapes are honored because they genuinely work.** `set -o pipefail` makes the shell report the first failing stage; `${PIPESTATUS[0]}` is the remedy the clause itself names. Both are explicit opt-ins. A gate that refused the one correct way to pipe a verifier would be un-compliable, and an un-compliable gate gets worked around — the failure the resume gate's module docstring already names.

**A verifier is what a segment RUNS, not a name that appears in it.** Resolution goes through the command head and the `-m <module>` form, never token presence. A substring check would refuse `grep -rn "unittest" src/`, which mentions a verifier and runs none. That false-positive class is what makes gates get bypassed, so it is asserted directly (`test_a_verifier_name_as_a_quoted_argument_is_not_an_invocation`).

**The verifier set is READ from `CANONICAL_STEP_COMMANDS`, not restated.** That dict in `src/gzkit/arb/validator.py` is the locked authority for what "an ARB-wrapped verifier" means (AGENTS.md § Attestation). `_canonical_program_names()` resolves each runnable entry, so a canonical ARB step added there is covered with no second edit, and `TestCanonicalRegistryCoherence` fails if one ever is not. Reserved slots with empty commands (`security`, `meta-receipt-bind`) contribute nothing, which is correct — there is no invocation to mask yet. A hand-copied list would silently stop matching the clause it enforces: the exact drift class GHI #754 found one file over, last session.

**The negative control asserts a DIFFERENTIAL, not a refusal.** `_ep_verifier_pipe_gate` is truthy only when the gate refuses the piped form AND permits the redirected form, against a command string seeded from a `mkdtemp`-random name. A refusal-only control cannot distinguish a working gate from an always-block one; a fixed sentinel proves only that the gate refuses that one string (the Step-4b facade attack). This mirrors `_ep_resume_gate_differential` exactly.

**Two coupled surfaces fired and both were correct.** Three tests in `tests/test_hooks.py` failed the moment the hook tranche changed — they assert the exact generated `settings.json` shape and the count of anchored hook commands. They were conformed to, never weakened. While editing `src/gzkit/hooks/claude.py` its generated README was found already omitting `ghi-triage-chat-silence.py` from the Bash registration order; that pre-existing drift was repaired in the same commit.

**The clause now binds the next agent, including on its own verification.** Every future session's `Bash` calls pass through this gate. Handoff Verification Checklists that prescribe unpiped runs are no longer advice — piping a verifier is refused at the tool layer.

## Decisions Made

- [operator-ruled] Promote the exit-code-integrity clause to a mechanical hook (verbatim: *"Promote exit-code-integrity hook"*, selected via AskUserQuestion and booked through `gz handoff authorize` — this is the ruling that lifted the resume gate and scoped the entire session). Chosen over returning to the Magna Carta campaign item (`ADR-0.35.0`, `Pending` 0/10), draining the 23 grandfathered scorecard rules, and a review-only ruling authorizing nothing.
- [operator-ruled] Sync after the build (verbatim: *"yes, git sync"*). Executed as `gz git-sync` dry-run then `--apply`, pushing `97c32d7d9`.
- [operator-ruled] Author a successor handoff and sync it (verbatim: *"update hsndoff and git sync it"*, operator spelling preserved) — this document and the `gz git-sync` that follows.
- [agent-chose] Scope the gate by predicate (*a verifier in any non-final pipeline stage*) rather than by the clause's named `tail`/`head`/`grep` filters, widening the promotion path row 66 prescribed. Turned on the fact that the shell reports the last stage's exit regardless of identity, so a filter allowlist would pass `gz check | cat` — the same defect renamed. Rejected alternative recorded in the module docstring so it is not narrowed back.
- [agent-chose] Honor `set -o pipefail` and `${PIPESTATUS[0]}` as escapes rather than refusing every pipe unconditionally. Both genuinely preserve the upstream status; refusing them would make the gate un-compliable for the one correct piped form, which is how gates get worked around.
- [agent-chose] Derive `VERIFIER_PROGRAMS` from `CANONICAL_STEP_COMMANDS` rather than hand-listing verifier names, following the `rule_version_of()` and `TaskId.parse` single-reader precedent. A hand-copied list would drift from the registry that defines the term.
- [agent-chose] Extract the `shlex` lexer configuration into a new `src/gzkit/shell_reading.py` shared by both Bash-reading gates, rather than importing the resume gate's private `_is_compound` or copying its setup. The two gates ask different predicates of the same input; sharing the *tokenizer* and not the predicate is the correct seam.
- [agent-chose] Register ONE enforcement claim, not one per verifier family. The clause declares one rule; splitting would have produced claims no single mechanism discharges (the inverse of the resume gate's deliberate write/bash split, which mirrors two declared clauses).
- [agent-chose] Route as a direct fix under AGENTS.md § Defect-fix routing rather than opening an OBPI, and file no new GHI. The clause is ratified canon whose declared intent prose alone never fulfilled, which is a *correction* under the operator's correction-vs-enhancement doctrine; GHI #589 is cited as provenance only and was not reopened (it closed 2026-06-09). No GHI was filed to satisfy the commit trailer, per the operator moratorium.
- [agent-chose] Conform `tests/test_hooks.py` to the new hook tranche rather than relaxing its assertions, and repair the pre-existing README registration-order omission in the same commit.

## Immediate Next Steps

A handoff ADVISES; it does not authorize. Present these and obtain an operator ruling before executing any of them.

1. **Return to the Magna Carta campaign — it governs pull order.** Movement A item 2 remains the topmost unchecked item whose gate is met: `ADR-0.35.0-canon-entry-corpus-landing` is `Pending` at **0/10 OBPIs**, `heavy` lane, all ten briefs `draft` (verified via `uv run gz adr status ADR-0.35.0`, 2026-08-05). Carried unexecuted across this session and the last; both were GHI-driven or clause-driven defect repair and neither claims priority over it.

2. **Decide whether `out_of_check` entries should carry a reason.** `data/check_scope_membership.json` forces every `gz validate` scope into `in_check` (44) or `out_of_check` (41), fail-closed, but `out_of_check` is a bare list of strings — a deliberate exclusion reads identically to a placement made to satisfy the parity test. Same class as GHI #754: the surface records membership, not the decision. Recorded as a `discovery` insight last session; still not filed. Carried unchanged.

3. **Optionally drain the 23 grandfathered advisory-scorecard rules.** Each is pinned at a version in `data/advisory_scorecard_grandfather.json` (`baseline_count` 23, unchanged this session — `tests.md` was never grandfathered, so bumping it to `0.14.0` did not touch the debt). Draining one means reading its binding clauses, correcting its scorecard rows, moving it into the Coverage Ledger at its current version, and removing its grandfather entry. The ratchet makes this monotonic.

4. **Assess the Dependabot alerts.** 3 vulnerabilities on the default branch (1 high, 2 moderate) were reported by a push two sessions ago and have never been assessed. Carried unverified — `gh api` is the only surface that reads them and it is excluded from the resume gate's allowlist, so this claim has not been re-checked at read-time.

5. **Consider whether other Promotable scorecard rows now have a cheaper path.** This session's work produced a reusable command-shape reader (`src/gzkit/shell_reading.py`) and a second worked example of the hook-plus-differential-NC pattern. Row 61 (three-part guardrail prose) and row 69 (output-form fixture carve-out) are the nearest Promotable neighbors; neither was examined this session.

## Pending Work / Open Loops

- **23 rules carry frozen advisory-scorecard coverage debt.** Enumerated in `data/advisory_scorecard_grandfather.json`, baseline 23, registered shrink-only in `data/waiver_ratchet_registry.json`. Unchanged this session. Not a blocker — the gate is green — but the debt is real and visible by design.

- **`out_of_check` records no reason per entry** (`data/check_scope_membership.json`, 41 entries). Recorded as a `discovery` insight; deliberately not filed under the operator moratorium on reflexive filing.

- **Dependabot reports 3 vulnerabilities on the default branch** (1 high, 2 moderate). Untouched for a third session; no assessment made. This claim is carried forward from a prior handoff and was NOT re-verified.

- **Advisory drift is non-blocking and slightly improved**: 692 unlinked specs (REQs with no test), 4 unjustified code changes — down from 7 last session. Reported by `gz check` as advisory; does not affect exit code.

- **The gate's declared coverage limits are real.** `UNWITNESSABLE` in `src/gzkit/verifier_pipe_gate.py` names three: a verifier invoked *inside* a shell script or Makefile target is unseen (the gate reads the command string the harness is asked to run, not what that command runs in turn); non-Bash execution surfaces never reach the matcher; and `pipefail` / `PIPESTATUS` are honored on presence, not on correct use. A green from this gate is not proof that no verifier exit was ever masked.

- **`CHANGELOG.md` v0.34.0 is RESOLVED** and should not be carried further. The predecessor handoff advised backfilling it; the block landed in `11b054bc9`, one commit after that handoff was written, so its own advised step 2 was already void at read-time. `CHANGELOG.md:59` now carries the full block with 21 GHI citations.

## Verification Checklist

Run every verifier **unpiped**, reading the exit from a redirect. This is no longer only advice: `verifier-pipe-gate.py` now refuses a piped verifier at the tool layer, so a piped run will not execute at all.

```bash
uv run gz check > check.log 2>&1; echo "REAL EXIT: $?"          # expect 0, 49 steps
uv run -m unittest -q > unit.log 2>&1; echo "REAL EXIT: $?"      # expect 0, 7914 tests
uv run gz validate --advisory-scorecard > s.log 2>&1; echo "$?"  # expect 0
uv run gz validate --qc-binding > q.log 2>&1; echo "$?"          # expect 0
uv run gz validate --rule-version-markers > r.log 2>&1; echo "$?" # expect 0
uv run gz validate --distribution > d.log 2>&1; echo "$?"        # expect 0
git rev-list --left-right --count origin/main...HEAD             # expect 0	0
```

**To prove the new gate is load-bearing rather than green-by-construction**, ask the harness to run a piped verifier and observe the refusal:

```bash
uv run -m unittest -q | tail -3
```

It must be blocked before execution with prose naming `unittest`, citing § Verification exit-code integrity, and handing back the redirect form. If it runs, the hook is not wired — check the `Bash` matcher in `.claude/settings.json` for `verifier-pipe-gate.py`.

**To prove the negative control fires**, run the fixture and entrypoint directly:

```bash
uv run python -c "
from gzkit.verifier_pipe_gate import _build_masked_verifier_violation as f, _ep_verifier_pipe_gate as ep
print(ep(f()))"
```

Expect `1`. It is truthy only when the gate BOTH refuses the piped form and permits the redirected one, so an always-block regression returns `0` just as an always-allow one does. That two-pole shape is the calibration; a refusal-only control would pass against a gate that blocks everything.

**To prove the enforcement floor discovered the claim** rather than leaving it an orphan:

```bash
uv run python -c "
from gzkit.enforcement import _ensure_production_claims_registered as reg, run_meta_validator
reg()
r = run_meta_validator()
print(r.verified_count, r.facade_count, r.test_bug_count)"
```

Expect `66 0 0`.

**Do not read `gz check` green as proof the 23 grandfathered rules are scored.** They are frozen, not reviewed. Read `data/advisory_scorecard_grandfather.json` for the live debt list and its `baseline_count`.

## Evidence / Artifacts

Commit `97c32d7d9` — *fix(governance): mechanize verification exit-code integrity (GHI #589)*. 18 files, 839 insertions, 25 deletions. Pushed to origin/main via `gz git-sync --apply`.

**The gate (new):**

- `src/gzkit/verifier_pipe_gate.py` — `decide()` and `masked_verifier()`, the pipeline-stage predicate, `VERIFIER_PROGRAMS` derived from the ARB registry, the live negative control, and the `UNWITNESSABLE` coverage declaration.
- `src/gzkit/shell_reading.py` — `tokenize_shell()`, `strip_uv_run()`, `split_on()`, `program_name()`. The single home for the quote-aware lexer facts both Bash gates depend on.

**Wiring:**

- `src/gzkit/hooks/scripts/quality.py` — `_verifier_pipe_gate_script()`, the generated thin stdin/exit shim.
- `src/gzkit/hooks/claude.py` — registered second in the `PreToolUse` `Bash` chain, written by `setup_claude_hooks`, described in the generated README (whose Bash registration order also had a pre-existing omission repaired).
- `src/gzkit/enforcement.py` — `_ensure_verifier_pipe_claims_registered` wired into `_ensure_production_claims_registered`, the single production-discovery seam.
- `.claude/hooks/verifier-pipe-gate.py` — the generated vendor adapter, live in this repo.

**Refactor:**

- `src/gzkit/handoff_resume_gate.py` — `_is_compound` and `_tokens` now delegate to the shared shell-reading module. Semantics-preserving; its 32 tests and both live negative controls pass unchanged.

**Doctrine:**

- `.gzkit/rules/tests.md` — rule version 0.13.0 to 0.14.0; § Verification exit-code integrity gains its **Mechanized** paragraph.
- `docs/governance/advisory-rules-audit.md` — Coverage Ledger entry for the tests rule moved to 0.14.0; row 66 rewritten **Promotable** to **Mechanical**, recording that the named promotion path was deliberately widened.

**Tests:**

- `tests/hooks/test_verifier_pipe_gate.py` — new, 22 tests across five classes. RED evidence: run against an inert always-`None` stub, all 14 permissive cases passed and all 19 detection assertions failed, proving the suite discriminates in both directions rather than merely failing on import.
- `tests/test_hooks.py` — conformed to the new hook tranche (13 anchored commands to 14, Bash chain shape, tranche file list).

**Session artifacts:**

- `.gzkit/ledger.jsonl` — handoff authorization, agent-sync, and ARB receipt events.
- `.gzkit/handoffs/20260805T020727Z-ghi-754-scorecard-clause-coverage-landed.md` — the resumed predecessor.
- `data/advisory_scorecard_grandfather.json` — unchanged at baseline 23; read to confirm the rule bump did not touch the debt.

**ARB receipts:** `arb-step-unittest-eaed1755a4334ce4a2f6d96cf1d7c8be`, `arb-step-typecheck-c7ab330dda9e42b48d54058916999463`, `arb-ruff-07507fa90377475aa422405588433c23`.

**GitHub:** no issue filed and none closed. GHI #589 cited as provenance only; it closed 2026-06-09 and was not reopened.

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
