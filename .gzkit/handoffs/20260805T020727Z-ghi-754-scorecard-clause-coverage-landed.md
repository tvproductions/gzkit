---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-05T02:07:27Z'
agent: claude-code
session_id: 823f6a47-7f1a-485b-be36-47bb700ea820
continues_from: .gzkit/handoffs/20260805T000259Z-v0341-published-two-pool-adrs-authored-triage-refreshed.md
---

## Current State Summary

An evidence-verification pass over a Claude Code `/insights` usage report, followed by landing the one real defect it surfaced.

Of the report's six proposed CLAUDE.md additions, **four were already canon** — verification-before-claiming-green (`.gzkit/rules/tests.md:81` § Verification exit-code integrity, GHI #589), evidence-over-pattern-matching (AGENTS.md § DO IT RIGHT #2/#4/6g), work-ordering (Magna Carta operator canon), derived-artifacts (Architectural Boundary 6 + state-doctrine). **Two were refuted as contradicting canon**: the shell-constraint addition describes the handoff-resume gate working exactly as designed (`src/gzkit/handoff_resume_gate.py:349-353` names the command-smuggling threat model), and the "record standing sync authorization in the handoff" suggestion would disarm the gate GHI #574 built — the gate's own prose reads *"A handoff ADVISES; it does not authorize."* Nothing from the report's list was filed.

The finding worth filing was not on the report's list. `audit_advisory_scorecard` was `if stem in scorecard_text` — a filename-substring check that no edit to an existing rule file could falsify, while its docstring promised "a complete index". Two drifts had shipped behind it. Filed as GHI #754 and closed via `35818d1b8`.

Landed: the audit is now rule-version equality (single-sourced through a new `rule_version_of()`), it runs for the first time as `gz check` step 14/49, and enrolling it auto-enrolled it in the ADR-0.0.73 QC-step registry — the antibody immediately demanded a negative control at exit 3, and one was authored. 23 rules are grandfathered shrink-only; `tests.md` and `task-discovery.md` were scored for real.

`uv run gz check` exits 0 across 49 steps; `uv run -m unittest -q` exits 0 at 7892 tests. Tree clean, level with origin/main.

## Important Context

**The rejected design matters more than the accepted one.** The obvious implementation of clause-level coverage is to extract binding clauses by their bold-leading `**...**` convention and require each to appear in the scorecard. That was measured before being written: **8 of 26 rule files carry zero bold-leading clauses**, so that population would pass trivially. That is `empty-input-passes`, and a clause-shape grader is additionally `shape-graded-not-substance` — **two of the seven theater signatures the audit exists to catch** (`src/gzkit/governance/trust_audits/qc_binding.py` `THEATER_SIGNATURES`). Do not retry it. The anchor used instead is the `<!-- rule-version: X.Y.Z -->` marker, which `gz validate --rule-version-markers` already enforces as present on every canonical rule, so the check is exact version equality with no heuristic.

**A prior claim in this session was wrong and is retracted on the GHI.** An earlier comment asserted ADR-0.0.73 shipped with negative-control debt ("51 audit functions, 1 with a control"). That counted `@enforces` decorator occurrences in source, not registered claims. Measured properly: **48 of 48 bound QC steps carry negative controls, zero missing**. ADR-0.0.73's debt is genuinely discharged and its Fidelity Assertion claiming so is honest. The real gap was narrower — Boundary Invariant #1 derives the QC registry from what `gz check` actually runs, so a validator outside `gz check` is outside the antibody *by construction*, not by neglect. That is why wiring the scope into `gz check` was the load-bearing arm rather than a convenience.

**The antibody defended itself, which is the strongest evidence in the session.** Adding the step to `gz check` made `uv run gz validate --qc-binding` fail closed immediately (exit 3, `QC registry build failed — unclassified step`). The negative-control fixture authored in response is calibrated against the removed proxy: its scorecard *does* contain the rule's stem, so the pre-fix implementation would have passed it. A control that only fails for a new reason would not prove the old hole is closed.

**Two coupled surfaces fired during the work and both were correct.** `tests/governance/test_check_scope_parity.py` failed the moment `gz check` membership changed, forcing the `data/check_scope_membership.json` move (GHI #744's instrument). `gz validate --bullet-retention` then failed on six new scorecard rows: ADR-0.0.33 Invariant 1 requires every **Mechanical**/**Promotable** bullet to appear verbatim in the per-turn surface corpus, so the Rule column must quote rule text verbatim rather than paraphrase it. Both were fixed by conforming, not by weakening the gates.

**Grandfather semantics are version-pinned on purpose.** `data/advisory_scorecard_grandfather.json` freezes 23 rules at their *current* versions. An edited grandfathered rule leaves its pin behind and must be scored for real before `gz check` goes green. Debt can only shrink and cannot follow a rule forward silently. It is registered shrink-only in `data/waiver_ratchet_registry.json` per ADR-0.0.73 Boundary Invariant #8 — the waiver ratchet fail-closes on any `data/*_grandfather*.json` absent from that registry, so the registration is not optional bookkeeping.

## Decisions Made

- [operator-ruled] The coverage gap routes as a **correction under ADR-0.0.73**, never a fresh pool ADR (verbatim: *"if this is a prior adr, them is a new discovery an extension of that adr?"*). This applied the operator's own correction-vs-enhancement doctrine to a routing recommendation that had contradicted it; an `improvement` insight was recorded via `gz insights remember` before the corrected work proceeded, per Behavior Rule 11.
- [operator-ruled] Fix immediately rather than defer to campaign sequencing (verbatim: *"do it right, fix things now"*).
- [operator-ruled] File both findings as **one GHI with two arms** rather than two issues or none (AskUserQuestion selection, 2026-08-05).
- [operator-ruled] Authorize the handoff resume so filing could proceed (verbatim: *"Rule now so I can file"*, booked via `gz handoff authorize`).
- [operator-ruled] Commit the untracked prior-session handoff and author a successor (verbatim: *"commit and update handoff"*).
- [agent-chose] Anchor coverage on the `<!-- rule-version: -->` marker rather than extracting clauses by shape, after measuring that 8 of 26 rule files carry zero bold-leading clauses. Rejected alternative recorded on GHI #754 so it is not retried.
- [agent-chose] Single-source the version grammar through a new `rule_version_of()` in `src/gzkit/validators/rule_version_markers.py` rather than restating the regex in the audit, following the `TaskId.parse` single-reader precedent in `.claude/rules/task-discovery.md`.
- [agent-chose] Grandfather 23 rules at pinned versions rather than stamp all 25 as reviewed-at-current-version. Stamping would have laundered exactly the unreviewed coverage the audit exists to surface; the `fidelity_presence_grandfather` precedent was followed instead.
- [agent-chose] **Retract arm 4** of the GHI rather than build it. The proposed population guard is already enforced by `tests/governance/test_check_scope_parity.py::test_every_registered_scope_is_classified` (GHI #744), which fail-closes on any scope in neither `in_check` nor `out_of_check`. Building a second instrument would have been duplicate state.
- [agent-chose] Record the residual finding (no reason recorded per `out_of_check` entry) to `.gzkit/insights/agent-insights.jsonl` as a `discovery` rather than filing a GHI, per the operator moratorium on reflexive GHI-filing.
- [agent-chose] Keep the prior-session handoff out of the fix commit and commit it separately, so a governance artifact authored by another session did not ride into an unrelated defect repair.

## Immediate Next Steps

A handoff ADVISES; it does not authorize. Present these and obtain an operator ruling before executing any of them.

1. **Return to the Magna Carta campaign — it governs pull order.** Movement A item 2 is the topmost unchecked item whose gate is met: `ADR-0.35.0-canon-entry-corpus-landing` is `Pending` at **0/10 OBPIs** (verified via `uv run gz adr status ADR-0.35.0`, 2026-08-05). This session's work was GHI-driven defect repair and does not claim priority over it.

2. **Backfill the missing `CHANGELOG.md` v0.34.0 block, or rule that it stays absent.** Carried from the prior handoff and **re-verified still open**: `grep -nE "^#+ .*0\.3[345]" CHANGELOG.md` shows `v0.34.1 (2026-08-04)` followed directly by `v0.33.3 (2026-07-25)`. No existing check can see the hole — the hermetic scope validates shape, and the coverage cross-check is scoped to the current release range.

3. **Decide whether `out_of_check` entries should carry a reason.** `data/check_scope_membership.json` forces every `gz validate` scope into `in_check` or `out_of_check` (fail-closed), but `out_of_check` is a bare list of 41 strings — a deliberate exclusion reads identically to a placement made to satisfy the parity test. Same class as GHI #754: the surface records membership, not the decision. Recorded as a `discovery` insight; not filed.

4. **Optionally drain the 23 grandfathered rules.** Each is pinned in `data/advisory_scorecard_grandfather.json`. Draining one means reading its binding clauses, adding or correcting its scorecard rows, moving it into the Coverage Ledger at its current version, and removing its grandfather entry. The ratchet makes this monotonic — the count can only fall.

5. **Consider the promotion path named for the exit-code-integrity clause.** Scorecard row 66 records it: a `PreToolUse` hook refusing a verifier piped into `tail`/`head`/`grep`, reusing the shell-aware `shlex` parsing already in `src/gzkit/handoff_resume_gate.py` (`_is_compound`) rather than a fresh regex. It is the highest-frequency observed violation class in agent sessions and is currently **Promotable, unenforced**.

## Pending Work / Open Loops

- **23 rules carry frozen advisory-scorecard coverage debt.** Enumerated in `data/advisory_scorecard_grandfather.json`, baseline count 23, registered shrink-only in `data/waiver_ratchet_registry.json`. Not a blocker — the gate is green — but the debt is real and visible by design. Editing any grandfathered rule forces it to be scored before `gz check` passes.

- **`out_of_check` records no reason per entry** (`data/check_scope_membership.json`, 41 entries). Recorded as a `discovery` insight in `.gzkit/insights/agent-insights.jsonl`; deliberately not filed as a GHI under the operator moratorium on reflexive filing. Available if it earns a work order.

- **`CHANGELOG.md` has no v0.34.0 block.** Carried forward from the prior handoff and re-verified open this session. Layer-3 derived view with a hole no current check can see.

- **The exit-code-integrity clause remains Promotable and unenforced.** It is now *scored* (row 66) with a named promotion path, which is what this session's work delivered — scoring is not enforcement. `PIPESTATUS` appears in no file repo-wide and no hook inspects Bash command strings for a verifier piped into a filter.

- **Dependabot reports 3 vulnerabilities on the default branch** (1 high, 2 moderate), surfaced by the push. Untouched this session; no assessment made.

- **Advisory drift is unchanged and non-blocking**: 692 unlinked specs (REQs with no test), 7 unjustified code changes. Reported by `gz check` as advisory; does not affect exit code.

## Verification Checklist

Run every verifier **unpiped**, reading the exit from a redirect. Piping through `tail`/`head`/`grep` reports the filter's status, always 0 — `.gzkit/rules/tests.md` § Verification exit-code integrity, the clause this session scored.

```bash
uv run gz check > check.log 2>&1; echo "REAL EXIT: $?"          # expect 0, 49 steps
uv run -m unittest -q > unit.log 2>&1; echo "REAL EXIT: $?"      # expect 0, 7892 tests
uv run gz validate --advisory-scorecard > s.log 2>&1; echo "$?"  # expect 0
uv run gz validate --qc-binding > q.log 2>&1; echo "$?"          # expect 0
uv run gz validate --waiver-ratchet > w.log 2>&1; echo "$?"      # expect 0
uv run gz validate --bullet-retention > b.log 2>&1; echo "$?"    # expect 0
git rev-list --left-right --count origin/main...HEAD             # expect 0	0
```

**To prove the new gate is load-bearing rather than green-by-construction**, bump any rule's `<!-- rule-version: -->` marker and its visible block quote together, then re-run `--advisory-scorecard`: it must exit 3 naming that rule. Revert afterward. A grandfathered rule works equally well — its pin is left behind by the bump, which is the freeze semantics under test.

**To prove the negative control fires**, run the fixture and entrypoint directly:

```bash
uv run python -c "
from gzkit.governance.trust_audits import _qc_negative_controls as nc
from gzkit.governance.trust_audits import _qc_nc_entrypoints as ep
print(len(ep._ep_advisory_scorecard(nc._build_advisory_scorecard())))"
```

Expect `1`. The fixture's scorecard deliberately contains the rule's filename stem, so a regression to the old substring check would return `0` — that is the calibration against the removed proxy.

**Do not read `gz check` green as proof the 23 grandfathered rules are scored.** They are frozen, not reviewed. Read `data/advisory_scorecard_grandfather.json` for the live debt list and its `baseline_count`.

## Evidence / Artifacts

Commit `35818d1b8` — *fix(governance): score the advisory scorecard by rule-version, not filename (GHI #754)*. 14 files, 491 insertions, 27 deletions.

**Audit rewritten (the class fix):**

- `src/gzkit/governance/trust_audits/release.py` — `audit_advisory_scorecard` now compares the scorecard Coverage Ledger against each rule's version marker; adds `_scorecard_coverage_ledger` and `_grandfathered_rules`.
- `src/gzkit/validators/rule_version_markers.py` — new `rule_version_of()`, the single reader of the marker grammar.

**Enrolled in `gz check` and under the ADR-0.0.73 antibody (the load-bearing arm):**

- `src/gzkit/quality.py` — new `run_advisory_scorecard_audit`.
- `src/gzkit/commands/quality.py` — step registered as *Advisory scorecard coverage*, plus its `_STEP_GUARD_META` MX seam entry.
- `src/gzkit/qc_binding.py` — `_STEP_CLASSIFICATION` entry, `bound` / `python_function`.
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — `_build_advisory_scorecard` fixture and its table row.
- `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py` — `_ep_advisory_scorecard`.

**Data surfaces:**

- `data/advisory_scorecard_grandfather.json` — new, 23 rules pinned, shrink-only.
- `data/waiver_ratchet_registry.json` — registers the grandfather under ADR-0.0.73 Boundary Invariant #8.
- `data/check_scope_membership.json` — `advisory_scorecard` moved `out_of_check` to `in_check`; counts 44/41.

**Doctrine surface:**

- `docs/governance/advisory-rules-audit.md` — new binding *Coverage Ledger* section; `.gzkit/rules/tests.md` scored at version 0.13.0 and `.gzkit/rules/task-discovery.md` at version 0.7.0; rows 66-72 added (including exit-code integrity, previously unscored); stale row 60 corrected with new rows 60a/60b.

**Tests:**

- `tests/governance/test_advisory_scorecard_coverage.py` — new, 5 tests. RED evidence: 3 of 4 unit cases failed before implementation with `AssertionError: [] is not true`, including the regression guard asserting filename presence no longer satisfies the audit.

**Session artifacts:**

- `.gzkit/insights/agent-insights.jsonl` — one `improvement` (the pool-ADR routing course-correction) and one `discovery` (the `out_of_check` reason gap).
- `.gzkit/ledger.jsonl` — handoff authorization and ARB receipt events.
- `.gzkit/handoffs/20260805T000259Z-v0341-published-two-pool-adrs-authored-triage-refreshed.md` — prior-session handoff, committed this session.

**ARB receipts:** `arb-step-unittest-938bea36d83b4ffeaf539bbc15c3b496`, `arb-step-typecheck-af6d2cdb5d3f49129dfeb9f506a2f7a4`.

**GitHub:** GHI #754 filed and closed; cross-link comment posted on GHI #579 recording the sibling-cut relationship (same proxy-versus-property class, different instrument).

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
