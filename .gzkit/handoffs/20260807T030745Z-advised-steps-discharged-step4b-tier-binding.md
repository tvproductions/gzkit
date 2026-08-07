---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-07T03:07:45Z'
agent: claude-code
session_id: 8e5c43b1-7bf5-423b-b4f4-599b1eee0840
continues_from: .gzkit/handoffs/20260807T021138Z-askuserquestion-convergence-hook-mechanics.md
---

## Current State Summary

Resumed the AskUserQuestion-convergence handoff, discharged all five of its advised
steps, then repaired two tracked defects to completion on operator direction. Two commits
landed on main and are unpushed at authoring time: `457ef2e2c` (memory-hygiene witness,
GHI #743) and `ffa1c6115` (Step-4b tier binding, GHI #678). GHI #678 was reopened,
repaired, and closed against its SHA in the same session.

The session's blocker is resolved by measurement rather than argument. Cross-family critic
round-trip in THIS context is 11.62-15.50s bare (mean 13.9s) and 19.62s carrying a 50KB
transcript slice read agentically at xhigh. The withdrawn 7-to-8-minute OBPI figure was
roughly 20x high. A synchronous `command` hook is therefore viable and no escalation ladder
or lag-by-one gating is needed. The hook itself is NOT built -- resolving the mechanism was
the advised step; building was not.

## Important Context

The Step-4b repair turned out to be a surface correction, not a field addition, and that
distinction is the reusable lesson. `SKILL.md:691` demanded `adversary_tier` and
`codex_availability_checked` on `SubagentDispatchRecord`, but that model is Stage-2 dispatch
tracking, is `extra="forbid"`, and is constructed only by `create_subagent_dispatch_record`
for implementer/reviewer roles. No adversary ever flows through it. Adding the two fields as
written would have been cargo-cult; an agent obeying the sentence literally got a
ValidationError rather than a record. The contract actually lives on `gz obpi complete`'s
adversary flags and the `adversarial_validation` ledger event.

`_build_adversarial_event` returns the generic `LedgerEvent` from `src/gzkit/ledger.py`, NOT
the typed `AdversarialValidationEvent` from `src/gzkit/events.py`. Event-specific keys land
in `LedgerEvent.extra` and flatten at `model_dump()`. Both surfaces still need the field: the
typed union is the read path used by `parse_typed_event`, `req_kind_support`, and
`ontology/corpus`. A first test run asserted against the wrong one and produced a genuine RED
that caught it.

The base-rate measurement is a sample, and its ceiling should not be overstated. 68.3% is the
share of defect GHIs whose root cause is a design decision -- it is the UPPER bound on what a
convergence-moment critic could address, because most of those decisions were made silently
and never surfaced as an AskUserQuestion at all. The 23% figure (explicit overconfident-premise
signature in the GHI's own body) is the tighter read.

Two gates fired correctly against this session's own work and are worth not fighting:
`verifier-pipe-gate.py` refused `unittest | tail` (the shell reports tail's exit), and the
handoff resume gate refused every compound command until the operator ruling was booked.

## Decisions Made

- [operator-ruled] Work all five advised steps (verbatim: "do the advised steps"). Booked via `gz handoff decide`; no step set aside.
- [operator-ruled] Injection shape is preamble-always plus an appended option when the base question carries 3 or fewer (selected from a 3-option picker with rendered previews). The critic's PREMISE-ATTACK/VERDICT map to the preamble, its UNASKED line to the option label.
- [operator-ruled] memory-hygiene is restructured, not retired: replace the witness and fix the wheel-shipped path defect, deferring the 41-file migration that would grow the parked instruction surface.
- [operator-ruled] Fix defects when found rather than parking them behind a fence ruling (verbatim: "do it right - fix defects when found"). This authorized the GHI #678 repair after the agent had parked it; standing canon already grants direct-repair authority to GHI-tracked defects, so the park was the error.
- [operator-ruled] Scope challenge on Step 4b (verbatim: "4b is opbi stuff, why surface it here? is it one of the 5 items?"). It IS advised step 3; it entered the design session because Step 4b is the existing precedent for cross-family adversarial review. The agent had flagged the campaign-sequencing tension but missed the OBPI-fence tension, which was the sharper of the two.
- [agent-chose] Reopened GHI #678 instead of filing a fresh GHI. The `/ghi-author` Step-0 prior-art lookup found it closed 26 days prior -- inside the skill's 30-day window -- prescribing exactly the three fields, so the skill's own table binds to reopen.
- [agent-chose] Did NOT reinstate `codex_availability_checked`. The fallback reason must name observed unavailability, so it already evidences the check; a separate boolean is redundant state that can disagree with what it duplicates.
- [agent-chose] Made the declared tier GOVERN with name-inference retained only as the backward-compatible fallback, rather than requiring the new flag on heavy lane. Requiring it would fail-close existing callers, and a second assertion from the same caller is not corroboration anyway.
- [agent-chose] Left the corroboration residual unfiled pending an operator ruling rather than reflexively opening a GHI, per the filing moratorium. It is recorded durably in the `ffa1c6115` commit body and GHI #678's close comment.
- [agent-chose] Recorded the base rate via `gz insights remember --type discovery` so the measurement outlives session context, with a next-action to re-run the same seed after any mechanism ships.

## Immediate Next Steps

1. Rule on the Step-4b corroboration residual. A declared tier is a second assertion from the same caller, not proof; genuine corroboration needs a runtime artifact, but `--adversary-job-id` is documented as "when the runtime supplies one" and mandating it breaks manual Codex runs. 13 of 19 recorded `adversarial_validation` events carry no `job_id`. Decide whether to require one, what substitutes for a manual run, and whether the residual earns its own GHI.
2. Decide whether to build the AskUserQuestion critic hook at all, given Movement C. The mechanism is unblocked -- shape ruled, latency measured at 11.62-19.62s, `updatedInput` proven to render -- but it would be a 19th hook against a reduction gate that is a stated 1.0 prerequisite. Whatever is built should discharge GHI #670 rather than orbit it.
3. Weigh this work against the campaign, which governs sequencing. None of this session's work was on the Build-to-1.0 checklist; the topmost unchecked item remains Movement A item 2, `ADR-0.35.0-canon-entry-corpus-landing` at 0/10 OBPIs landed.
4. Read the AGENTS.md delivery breach. `gz check` reports 33153 B against the Codex 32768 B cap -- 385 B OVER -- so content past that boundary is not delivered under Codex at all. It is byte-identical to the prior commit and is the parked instructions-budget work, but it is now measurably breaching rather than merely close.
5. Re-measure the base rate after any second-opinion mechanism ships, using seed 20260807 and the same five-class taxonomy, to test whether the design-class share actually moves.

## Pending Work / Open Loops

- The corroboration residual on Step 4b is open and unfiled by deliberate choice. 13 of 19 `adversarial_validation` events carry no `job_id`; one names its adversary "independent Codex subagent", which `_is_cross_vendor_adversary` classifies as NOT cross-vendor because the prefix scan is a `startswith`.
- The AskUserQuestion critic hook is unbuilt. Shape and mechanism are settled; nothing is wired.
- `permissionDecision: "deny"` on `AskUserQuestion` was never tested -- only `updatedInput` was exercised. Whether deny blocks cleanly or wedges the picker is unknown.
- Hook `type: "agent"` and `type: "prompt"` remain untested; neither reaches a non-Anthropic vendor, so a cross-family critic still needs a `command` hook shelling out.
- GHI #670 is OPEN and operator-authored; it is the issue any second-opinion build should discharge.
- The 41 `feedback_*` auto-memories are unmigrated. The restructured chore now detects drift from the last pass but does not migrate; migration was declined because it grows the parked instruction surface.
- AGENTS.md is 385 B over the Codex delivery cap; instructions-budget work stays parked by standing ruling.
- ARB harvest still reads a fraction of accumulated receipts; carried untouched across four sessions now.
- Movement C (reduce accretion) remains a 1.0 gate that every new mechanism runs against.

## Verification Checklist

- Confirm both commits are present and pushed: `git log --oneline -3` should show `ffa1c6115` and `457ef2e2c`; `git rev-list --left-right --count origin/main...HEAD` should read `0 0` after the sync.
- Re-run the Step-4b gate suite and read the verifier's OWN exit code, never a pipe: `uv run -m unittest tests.test_adversarial_validation_gate > out.log 2>&1; echo $?` expects 0 across 28 tests.
- Confirm the memory-hygiene witness still discriminates: `uv run python .gzkit/chores/memory-hygiene/check_memory_drift.py` expects exit 0 while no memory postdates `proofs/CHORE-LOG.md`. It is designed to fail when one does, which is the point.
- Confirm no maintainer absolute path returned to either chore surface: `grep -rn "Users-jeff" src/gzkit/chores/ .gzkit/chores/` expects no match.
- Confirm the new flag is registered and documented: `uv run gz obpi complete --help` shows `--adversary-tier {1,2,3}`, and `uv run gz cli audit` exits 0 at full cross-coverage.
- Full gate: `uv run gz check` exited 0 across 49 scopes at authoring time, with two standing advisories (instructions-files budget, spec-test-code drift) that do not affect exit code.
- Confirm GHI #678 is closed and GHI #670 still open: `gh issue view 678 --json state` and `gh issue view 670 --json state`.

## Evidence / Artifacts

- `.gzkit/chores/memory-hygiene/check_memory_drift.py` -- the new witness; resolves the memory directory from the checkout path rather than a hardcoded absolute.
- `.gzkit/chores/memory-hygiene/acceptance.json` -- criteria now lead with the drift check; the unit suite is retained and labelled a precondition, not the discriminator.
- `.gzkit/chores/memory-hygiene/CHORE.md` -- acceptance table reconciled with the JSON, which it previously contradicted.
- `src/gzkit/commands/obpi_complete.py` -- `_is_cross_vendor_adversary` and the tier gate; the declared tier now governs and a declared-tier/name contradiction fails closed.
- `src/gzkit/cli/parser_artifacts.py` -- the `--adversary-tier` flag.
- `src/gzkit/events.py` -- `adversary_tier` on `AdversarialValidationEvent`, the typed read path.
- `src/gzkit/ledger.py` -- `LedgerEvent`, the generic model `_build_adversarial_event` actually returns; extras flatten at `model_dump()`.
- `src/gzkit/schemas/ledger.json` -- the structural-validator side of the same field.
- `src/gzkit/pipeline_runtime.py` -- `SubagentDispatchRecord`, the model the SKILL wrongly named; Stage-2 only, `extra="forbid"`.
- `tests/test_adversarial_validation_gate.py` -- 28 tests; the seven new ones derive from the requirement, not from a run.
- `docs/user/manpages/obpi-complete.md` -- the flag row.
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` -- Step 4b repointed onto the real surface; skill-version bumped to 6.33.0.
- `.gzkit/insights/agent-insights.jsonl` -- carries the base-rate `discovery` record and the scope-deference `improvement` record from this session.
- `.gzkit/handoffs/20260807T021138Z-askuserquestion-convergence-hook-mechanics.md` -- the predecessor this supersedes; its five advised steps are all discharged.

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
- The critic accompanies the question rather than being absorbed by the agent (verbatim: "yes, it is a 2nd opinion, not a usurped opinion. this seems fitting: 'I re-pose the question carrying the critic's verdict unedited, the same way § Attestation makes me pass your words through unchanged.'"). `updatedInput` proved stronger than the ruling required: the harness enforces the passthrough, so the critique never enters the agent's context before the operator sees it.
- Maximum information flows to the hook (verbatim: "we should pass max information to the hook"). Already satisfied by the harness -- `transcript_path` gives the critic the entire session.
- The option cap and similar limits are accepted as design inputs (verbatim: "we can work with 4 options, and other limitations - contraints usually strengthen designs"; spelling preserved).
- Allowing the critic to actually run is the named next blocker (verbatim: "we need to allow the critic to operate, so that needs resolution").
- No OBPI-pipeline mechanism may be imported into this design yet (verbatim: "do not conflate any mechanism for the obpi pipeline with this work just yet"). The withdrawn latency figure is the concrete casualty.
- The agent equivocates after presenting converged options (verbatim: "the option you always provide is 'discuss this' (approximating): the critic needs to engage your premise. You almost always equivocate and hedge in the narrative that follows. easly a discernible majority of the time."; spelling preserved). Booked to insights as an `improvement` under scope `agent-narrative-discipline`.
- Authorized the probe and required the agent to clear its own gate (verbatim: "On probe, we can't proceed unless you do so"). Booked via `gz handoff decide` against the predecessor.
