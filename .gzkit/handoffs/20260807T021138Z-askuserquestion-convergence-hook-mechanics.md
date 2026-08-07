---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-07T02:11:38Z'
agent: claude-code
session_id: d01f355f-362e-45ed-9ed8-4d30ad06d452
continues_from: .gzkit/handoffs/20260807T005320Z-second-opinion-crm-design.md
---

## Current State Summary

Mechanics-discovery session. No product code landed; one temporary diagnostic hook was installed, fired twice, and removed. The predecessor handoff's design was dead (both critics PERFORATED it) and its blocker was named as "rule on WHERE the second opinion fires." That question is now answered by observation rather than design: the convergence moment is an `AskUserQuestion` tool call, and a `PreToolUse` hook on it can rewrite the question before it renders.

Four facts were established empirically, not inferred. (1) `PreToolUse` DOES fire on `AskUserQuestion`, before the picker renders, and fires even when the operator subsequently rejects the question. (2) The payload carries the complete `questions` array (labels, descriptions, previews) plus `transcript_path`, `tool_use_id`, `prompt_id`, `permission_mode`, `effort`, `session_id`, `cwd`, `hook_event_name`. (3) `hookSpecificOutput.updatedInput` IS honored on this tool: both a rewritten question text and an appended option rendered, operator-confirmed "Both appeared". (4) The harness treats the rewrite as canonical -- the tool result echoed back the injected question text as the question that was answered.

Separately, the predecessor's two unverified shipped defects were hand-verified and turn out to be ONE defect, differently shaped than the critic reported. Routing changes from two GHIs to one.

## Important Context

The operator identified the failure mode from the rendered picker itself: every option in an `AskUserQuestion` is downstream of the agent's premise, and only the harness's own "Chat about this" escape lets the operator reject the question. That escape is the one path costing the operator the most, because taking it means typing the critique by hand. The critic's job is therefore to occupy that slot with substance, unprompted. A critic that grades the agent's options has already been captured by the agent's frame.

Fact (4) above is the governance consequence and was not anticipated. Because the harness records the rewritten question as the real question, the decision record automatically carries the critic's verbatim text. No separate witness that the second opinion fired is needed -- the answer record IS the witness and cannot be written without the critique in it. That is a fail-closed property obtained for free.

`transcript_path` dissolves the ordering deadlock the predecessor called its blocker. Codex argued scope-challenge must precede conclusion-challenge because a conclusion-only critic is another retrospective audit; the operator's trigger is the convergence moment, which is conclusion-time. Both hold simultaneously: the hook fires at conclusion-time while handing the critic the whole session transcript, so scope selection is attackable from a conclusion-time trigger.

Two constraints were found by hitting them, not by reasoning. `AskUserQuestion` caps options at 4, so injecting an option requires the base question to carry 3 or fewer -- preamble injection is unconditional, option injection is not. And latency is UNMEASURED: the hook must return before the picker renders, and `async`/`asyncRewake` cannot help because a non-blocking hook cannot inject. The predecessor's 7-to-8-minute Codex figure was withdrawn on operator ruling as OBPI-pipeline contamination and has NOT been replaced with a measurement for this context.

Also available and untested: hook `type` may be `"agent"` (runs an agent with tools, own `model` and `timeout`, PreToolUse-eligible) or `"prompt"`. Neither reaches a cross-family vendor -- `model` takes Anthropic models only -- so a cross-family critic needs a `command` hook shelling out.

## Decisions Made

- [operator-ruled] The critic accompanies the question rather than being absorbed by the agent (verbatim: "yes, it is a 2nd opinion, not a usurped opinion. this seems fitting: 'I re-pose the question carrying the critic's verdict unedited, the same way § Attestation makes me pass your words through unchanged.'"). `updatedInput` proved stronger than the ruling required: the harness enforces the passthrough, so the critique never enters the agent's context before the operator sees it.
- [operator-ruled] Maximum information flows to the hook (verbatim: "we should pass max information to the hook"). Already satisfied by the harness -- `transcript_path` gives the critic the entire session.
- [operator-ruled] The option cap and similar limits are accepted as design inputs (verbatim: "we can work with 4 options, and other limitations - contraints usually strengthen designs"; spelling preserved).
- [operator-ruled] Allowing the critic to actually run is the named next blocker (verbatim: "we need to allow the critic to operate, so that needs resolution").
- [operator-ruled] No OBPI-pipeline mechanism may be imported into this design yet (verbatim: "do not conflate any mechanism for the obpi pipeline with this work just yet"). The withdrawn latency figure is the concrete casualty.
- [operator-ruled] The agent equivocates after presenting converged options (verbatim: "the option you always provide is 'discuss this' (approximating): the critic needs to engage your premise. You almost always equivocate and hedge in the narrative that follows. easly a discernible majority of the time."; spelling preserved). Booked to insights as an `improvement` under scope `agent-narrative-discipline`.
- [operator-ruled] Authorized the probe and required the agent to clear its own gate (verbatim: "On probe, we can't proceed unless you do so"). Booked via `gz handoff decide` against the predecessor.
- [agent-chose] Ran a mutating probe to answer the presentation question instead of reasoning about it, on the ground that the settings schema documents `updatedInput` for PreToolUse generally but says nothing about which tools honor it.
- [agent-chose] Removed the probe hook and its matcher immediately after the result, because it would otherwise have injected a fabricated option into every subsequent question.
- [agent-chose] Recommended AGAINST composite/median/mean aggregation of critic verdicts, on the ground that AGENTS.md § Behavior Rules -- Always #9 makes disagreement the signal, and averaging is unilateral resolution performed by arithmetic. Also premature: the vendor ruling names one adversary, so there is nothing to aggregate.
- [agent-chose] Collapsed the predecessor's two shipped Step 4b defects into one GHI, because the absent `adversary_tier` and the string-prefix vendor check are the same design decision.

## Immediate Next Steps

1. Resolve how the critic actually runs -- the operator's named blocker ("we need to allow the critic to operate"). The hook must return before the picker renders and a non-blocking hook cannot inject, so measure real cross-family round-trip latency in THIS context (not the withdrawn OBPI figure) before choosing between a synchronous `command` hook, a fast local critic with cross-family escalation, or gating the NEXT convergence moment on the previous one's verdict.
2. Rule on the injection shape now that both are proven to render. Preamble is unconditional; added-option requires 3 or fewer base options. Recommendation on the table: preamble always, option when there is room.
3. File ONE GHI for the Step 4b defect, now hand-verified: `adversary_tier` and `codex_availability_checked` exist nowhere in `src` or `tests` while line 691 of the pipeline SKILL demands them on `SubagentDispatchRecord`; `fallback_reason` IS implemented but on the `gz obpi complete` CLI, not that model; and the gate infers tier from a caller-supplied name string via `_is_cross_vendor_adversary`, with no corroborating artifact required.
4. Decide the GHI #743 disposition for memory-hygiene. Its `.gzkit/chores/memory-hygiene/acceptance.json` observes no memory surface at all -- one criterion is the whole unittest suite, the other is the instructions-files budget, which is work the operator has parked. "Retire or restructure" is live.
5. Answer the operator's base-rate question: how many GHIs trace to overconfident agent design options later found wrong. Both critics named this as the missing measurement and it sizes whether the mechanism earns its surface.

## Pending Work / Open Loops

- Cross-family critic latency in the PreToolUse window is unmeasured. This is the single mechanical unknown blocking the design.
- Whether `permissionDecision: "deny"` blocks `AskUserQuestion` cleanly or wedges the picker was never tested -- the probe deliberately stayed non-blocking. Only `updatedInput` was exercised.
- Hook `type: "agent"` and `type: "prompt"` are PreToolUse-eligible and untested here. Neither reaches a non-Anthropic vendor.
- GHI #670 is OPEN and operator-authored ("design skills: opus self-escalation lacks cross-family second opinion"), verified this session. Whatever is built should discharge it rather than orbit it.
- The Step 4b GHI is unfiled. Verification is done; the filing is not.
- memory-hygiene's acceptance witness still does not observe its named subject.
- `gz validate --chore-criteria-witness` remains unbuilt, and whether it should exist is still in question -- the executed surface measured far cleaner than the predecessor claimed (1 ambient-only chore in the acceptance manifests, not 11 of 32).
- No base rate exists anywhere in the repo for how often agent recommendations are wrong, or how often a critic changes an operator decision.
- Agent confidence self-measurement is unestablished, so the AGENTS.md 90-percent rule may be placebo. Bears directly on any risk-tiered trigger.
- ARB harvest still reads 130 of 3286 receipts; 2265 step and 125 red receipts have no harvester. Carried untouched across three sessions.
- Movement C (reduce accretion) is a 1.0 gate. Any new mechanism runs against it: 18 hooks, 68 to 69 skills, 99 validate long options.
- The predecessor's exit bookmark `.gzkit/handoffs/20260807T010232Z-session-exit-bookmark.md` is staged and superseded by this document; commit both together.

## Verification Checklist

- The probe is fully removed. Confirm `grep -c AskUserQuestion .claude/settings.json` returns 0 and that no askuserquestion-payload-probe file exists under `.claude/hooks`. Confirm the settings file is still valid with `jq -e '.hooks.PreToolUse | length' .claude/settings.json` (expect 4).
- The payload capture lived in the session scratchpad under `/private/tmp` and will NOT survive. The observed fields are transcribed into this handoff's Important Context; re-derive by reinstalling an equivalent probe if a raw copy is needed.
- Re-verify the Step 4b finding before filing: `grep -rn "adversary_tier" src tests .gzkit/skills` returns only line 691 of the pipeline SKILL (two mirrored copies). Same for `codex_availability_checked`. By contrast `grep -rn "fallback_reason" src tests` returns the live CLI path at `src/gzkit/cli/parser_artifacts.py` line 1494, `src/gzkit/commands/obpi_complete.py` line 1298, the gate at the same file line 2087, and 7 tests.
- Ledger evidence for the same finding: 17 `adversarial_validation` events exist and only 6 carry a `job_id`, so eleven have no corroborating job artifact. One event names its adversary "independent Codex subagent", which `_is_cross_vendor_adversary` classifies as NOT cross-vendor because the prefix scan is a `startswith` against 12 vendor names.
- Confirm memory-hygiene has no memory witness by reading `.gzkit/chores/memory-hygiene/acceptance.json` directly -- two criteria, neither naming a memory surface.
- Confirm GHI #670 is still open with `gh issue view 670 --json number,state,title`.
- Branch state at authoring: `main`, origin 0/0. No `src/` or `tests/` changes this session.

## Evidence / Artifacts

- `.claude/settings.json` -- the `PreToolUse` block. `ExitPlanMode` is wired to the plan-audit gate; `AskUserQuestion` is the sibling convergence door and is currently UNGATED. The probe matcher was added here and removed here.
- `.claude/hooks/plan-audit-gate.py` -- the working precedent for gating a convergence-shaped tool call. Two properties matter for the design: it self-dispatches the check rather than ordering the agent to go get one (lines 288 to 307), and it accepts a FAIL verdict (lines 297 to 300), so it demands the check RAN, not that it PASSED. That is a second opinion rather than a veto.
- `src/gzkit/handoff_resume_gate.py` -- the counter-precedent: four documented allowlist failures and the un-compliable-gate conclusion. The strongest in-repo cost evidence against underspecified fail-closed gates.
- `src/gzkit/commands/obpi_complete.py` -- `_is_cross_vendor_adversary` at 1976 and its enforcement at 2084 to 2101; `_CROSS_VENDOR_ADVERSARY_PREFIXES` at 1960.
- `src/gzkit/pipeline_runtime.py` -- `SubagentDispatchRecord` at 157, `extra="forbid"`, missing the two fields the skill demands.
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` -- line 691 carries the misdirected dispatch-contract sentence.
- `.gzkit/chores/memory-hygiene/acceptance.json` -- the witness that observes no memory surface.
- `.gzkit/insights/agent-insights.jsonl` -- carries this session's `improvement` record under scope `agent-narrative-discipline`.
- `.gzkit/handoffs/20260807T005320Z-second-opinion-crm-design.md` -- the predecessor this supersedes. Its claim that check-before-present is unreachable is now WRONG for the structured channel.
- `.gzkit/handoffs/20260807T010232Z-session-exit-bookmark.md` -- the mechanical bookmark absorbed by this document.
- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md` -- already addresses the vendor-lock question; its boundary invariants forbid a fail-closed invariant living solely in a vendor hook, which constrains any design placing the gate in `.claude/settings.json`.

## Settled Rulings

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
