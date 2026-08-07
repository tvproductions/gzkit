---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-07T00:53:20Z'
agent: claude-code
session_id: 882dfc48-123b-4b9e-aaff-e2909cd4fe06
continues_from: .gzkit/handoffs/20260806T224538Z-efficacy-channel-triage-top5.md
---

## Current State Summary

Design session; no code landed and none should land until the frame is settled. Sequence: resumed the efficacy-channel handoff, operator ruled proceed (booked), set aside advised steps 1 and 3. Began the advised step 2 (build gz validate --chore-criteria-witness). The /ghi-author Step-0 prior-art lookup caught that GHI #743 already worked that exact class and closed it 2026-08-01. Measurement then showed the predecessor handoff's premise does not hold on the executed surface: only 1 of 39 chores is ambient-only in acceptance.json (quality-check, legitimately), not 11 of 32. But memory-hygiene's rewired witness reads no memory surface at all, so #743's closing claim that all 37 chores now carry a subject witness is false for that member. The operator then reframed the session onto a larger question: an always-on cross-family second-opinion mechanism for agent assessments. A design was drafted and dispatched to two critics on the same core brief, Claude (same-family) and Codex (cross-family, blind to the Claude verdict). BOTH returned PERFORATED. The design as drafted is dead; the need is operator-attested and stands.

## Important Context

The through-line is the Codex frame challenge, which the operator endorsed verbatim as prescient: the trust failure enters at SCOPE SELECTION, not at the conclusion. A critic handed primary-selected surfaces is independent in inference but NOT in scope, and can rigorously validate the wrong slice of reality. Codex's diagnosis of gzkit: not too few gates nor too many, but too many gates whose witnesses do not reliably discriminate their governed subject; adding another receipt-presence gate is the epicycle itself.

The operator supplied a Memento framing for WHY this recurs: frozen weights plus stateless inference, attention dilution with U-shaped positional bias, and goal drift across agentic loops. Codex mapped each to a different mechanism and noted an end-of-turn critic addresses only the third.

The operator's trigger is behavioral and specific: the moment the agent reaches within-session convergence and presents structured, analyzed design options. That is reliably observable. It is explicitly NOT a second airlock.

Mechanical findings that constrain any design. Trigger on AskUserQuestion via PreToolUse is undocumented for blocking and would likely wedge the UI, and covers only about 0.57 percent of turns (239 calls against 41624 assistant turns). The Stop hook reads last_assistant_message and can block, but is FAIL-OPEN by contract and short-circuits on stop_hook_active, so it cannot guarantee a critic ran. No hook fires before prose generation, so check-before-present is unreachable; only check-before-the-operator-acts is achievable.

Two defects in SHIPPED code surfaced and are NOT routed. They are independent of whatever gets designed and must not be folded into the design work.

## Decisions Made

- [operator-ruled] The OBPI process must NOT be altered at all (verbatim: 'we will NOT alter the OBPI process, at all! This is a broader and per-session tool need'). This forecloses the critic alternative of extending adversarial_validation with a phase discriminator. Booked to insights 2026-08-07.
- [operator-ruled] Generalizing FROM the existing 4b skills and tooling is acceptable, but the OBPI pipeline itself stays untouched (verbatim: 'it is possible we generalize from the existing skills/tooling for obpi 4b, but I am hesitant to alter anything about the obpi pipeline as it is the most enduringly stable part of gzkit').
- [operator-ruled] The trigger is the convergence moment (verbatim: 'we are trying to jump in when you offer analyzed and considered design options in the same structed way - you've achieved convergence, within that session, when you do so, I need a 2nd opinion in that exact moment'). Explicitly not an Airlock Jr.
- [operator-ruled] Stated goal for the whole session, verbatim: 'retain cross-family review for consequential decisions'.
- [operator-ruled] Vendor posture is deliberately concrete, not generic (verbatim: 'I am trying to be specific: The US Air Force, the Chinese Air Force, etc. we can refactor to generics once we have platform stability'). Claude is the daily driver; Codex is the named adversary; the lock-in risk is accepted knowingly (verbatim: 'I need forward momentum, not design niceties - they can come with the refactor').
- [operator-ruled] Experimental refinement is expected (verbatim: 'we can experimentally refine this moving forward'), so a calibrated pilot is compatible with the ruling; a universal fail-closed gate on day one is not required.
- [operator-ruled] Park all instructions-file budget work until the product stabilizes (carried from the predecessor session).
- [agent-chose] Dispatched Codex BLIND to the Claude critic's verdict, so the correlated-draw question got an unanchored answer. The briefs were not identical (Codex also received the Memento framing and the vendor question), so only the shared portion supports comparison. Flagged before results, not after.
- [agent-chose] Did NOT reopen GHI #743 despite the /ghi-author Step-0 table prescribing reopen for a recently-closed GHI covering the same finding. Reopening reverses an operator attestation and is the operator's call.
- [agent-chose] Did NOT read ADR-0.44.0 ahead of the critic that was mid-verification on it, to avoid re-anchoring the frame under test.

## Immediate Next Steps

1. Rule on WHERE the second opinion fires. Codex argues scope-challenge must come before conclusion-challenge, and that a conclusion-only critic is another retrospective audit. The operator's stated trigger is the convergence moment, which is conclusion-time. These are not necessarily in conflict (both are possible) but the ordering decision drives the whole design and nothing should be built first.
2. Route the two live shipped defects as GHI direct fixes, separately from this design. (a) The Step 4b dispatch contract is mechanically unsatisfiable: gz-obpi-pipeline SKILL.md lines 689-693 require SubagentDispatchRecord fields adversary_tier, codex_availability_checked and fallback_reason, which the model at src/gzkit/pipeline_runtime.py lines 157-173 does not have and forbids as extras. (b) Cross-vendor enforcement is a string check: obpi_complete.py lines 1976-1985 decides cross-vendor by caller-supplied adversary-name prefix, and 11 of 17 adversarial_validation ledger events carry no job_id. Both need independent verification before filing, since they came from a critic and were not hand-checked this session.
3. Answer the operator's measurable question: how many GHIs trace to this failure mode (overconfident agent design options later found wrong). The operator asked it directly and it is the missing base rate that both critics named as absent. This is a triage-and-count pass over the GHI corpus, and it is the cheapest way to size whether the mechanism earns its surface.
4. Decide the GHI #743 disposition for memory-hygiene: reopen #743 citing the regression, or file a fresh GHI for the narrower finding. Note memory-hygiene may be UNWITNESSABLE by a repo-side gate: it is vendor-scoped to claude and audits files under the user home directory, outside the repository, so 'retire or restructure' is a live option the primary agent failed to offer.
5. Decide whether to author a harness-surface-currency chore. Direct precedent exists in dependency-currency and frontier-model-card-currency. gzkit uses 6 hook events; the harness exposes many more (PreCompact, PostCompact, SubagentStart, SubagentStop, UserPromptSubmit, PermissionRequest, PostToolBatch, StopFailure, InstructionsLoaded). PreCompact is directly relevant to the Memento context-loss problem and is currently addressed only by prose in CLAUDE.md.

## Pending Work / Open Loops

- GHI #670 is OPEN and operator-authored: 'design skills: opus self-escalation lacks cross-family second opinion'. It already books the cross-family requirement and names a scope hint. Whatever is built should discharge it rather than orbit it. Its one recorded blocker (codex:rescue not exposed to the Agent toolset) appears closed: codex:codex-rescue dispatched successfully this session.
- The two shipped Step 4b defects above are unrouted and unverified by hand.
- memory-hygiene's acceptance witness still does not observe its named subject.
- gz validate --chore-criteria-witness remains unbuilt. Whether it should be built at all is now in question, since the executed surface measured far cleaner than the predecessor handoff claimed.
- No base rate exists anywhere in the repo for how often agent recommendations are wrong, or how often a critic changes an operator decision. Both critics named this as the missing measurement.
- Open epistemic question the operator raised and nobody answered: agent confidence self-measurement is not established, so the AGENTS.md 90-percent rule may be placebo. This bears directly on any risk-tiered trigger design.
- ARB harvest still reads 130 of 3286 receipts; 2265 step and 125 red receipts have no harvester. Carried from the predecessor session, untouched.
- Codex could not reach api.github.com, so its reads of GHI #670 and #743 came from local artifacts only. Its GitHub-state claims are UNVERIFIED by its own admission.
- Movement C (reduce accretion) is a named 1.0 gate. Current surface measured this session: 18 hooks, 68 to 69 skills, 99 validate long options. Any new mechanism runs against that mandate and must justify its surface.

## Verification Checklist

- Both critic verdicts were PERFORATED. Codex session id 019fd994-df2e-76e0-8da4-8d5072057e81 is recorded in the transcript; resume with codex resume followed by that id. The critic job id was task-msi73rqr-bjzbcr and its full log is retrievable via the codex-companion result verb.
- Confirm the chore census before acting on any chore claim: the script at scratchpad/census.py reads both acceptance.json and the CHORE.md Acceptance Criteria table for all 39 chore dirs. Result this session: 1 ambient-only in acceptance.json, 8 in CHORE.md prose, 18 disagreeing between the two surfaces (an upper bound, untriaged).
- Confirm memory-hygiene has no memory witness: grep -rln for the claude projects path and MEMORY.md across src/gzkit returns only insights/correction_mining.py, which serves a DIFFERENT chore.
- Verify the Step 4b contract contradiction by hand before filing: read src/gzkit/pipeline_runtime.py lines 157-173 against gz-obpi-pipeline SKILL.md lines 689-693.
- Branch state at authoring: origin/main 0 0, working tree carries only .gzkit/ledger.jsonl and .gzkit/insights/agent-insights.jsonl modifications from this session's governed writes.
- No source code was modified this session. git status should show no src/ or tests/ changes.

## Evidence / Artifacts

- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md` -- Proposed, feature, heavy, 0.44.0. Already addresses the vendor-lock question the operator raised as possibly existential. Codex cites its boundary invariants as already forbidding a fail-closed invariant living solely in a vendor hook.
- `src/gzkit/pipeline_runtime.py` -- SubagentDispatchRecord, the model missing the three fields the skill demands.
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` -- Step 4b contract, the cross-vendor tier ladder, and the Claude-validating-Claude prohibition.
- `src/gzkit/commands/obpi_complete.py` -- cross-vendor decided by adversary-name prefix.
- `.claude/hooks/stop-turn-feedback.py` -- fail-open contract; form-not-truth docstring; last_assistant_message consumption.
- `.claude/hooks/plan-audit-gate.py` -- the precedent that accepts a FAIL verdict, and the self-heal path added when the gate proved un-compliable.
- `src/gzkit/handoff_resume_gate.py` -- four documented allowlist failures and the un-compliable-gate conclusion; the strongest in-repo cost evidence against underspecified fail-closed gates.
- `.gzkit/chores/memory-hygiene/acceptance.json` -- the witness that does not witness.
- `data/waiver_ratchet_registry.json` -- the honesty-mechanism registry any new grandfather surface must join.
- `.gzkit/insights/agent-insights.jsonl` -- two improvement records booked this session under scopes agent-assessment-guidance and second-opinion-system-scope.
- `.gzkit/handoffs/20260806T224538Z-efficacy-channel-triage-top5.md` -- the predecessor this supersedes.

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
