---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-09-03T11:22:26Z'
agent: claude-code
obpi_id: OBPI-0.35.0-04-section-ownership-and-ratchet
session_id: 5f5fe9c0-7b82-4cb6-8832-393d29902c4f
continues_from: .gzkit/handoffs/20260903T070119Z-obpi-0-35-0-04-all-adversary-findings-fixed-awaiting-clean-4b.md
---

## Current State Summary

OBPI-0.35.0-04 is BLOCKED at 10 of 11 preconditions, solely on `adversarial_validation`, and the tree is green and committed on main at `a592be20`. Four commits landed this session: `565ab200`, `f3f4940f`, `6a4ab55d`, `a592be20`. 9275+ tests exit 0; ruff, typecheck, documents, brief-reconcile, waiver-ratchet, ledger and xenon all exit 0.

THE SESSION'S REAL PRODUCT IS THE THREAT MODEL, NOT THE CODE. Five Step-4b rounds ran against an ABSOLUTE claim ("no ownership transition can occur without ...") with no declared threat model. An adversary instructed to REFUTE an absolute security property escalates the attacker one notch each round, so the gate could not converge by construction. Measured: 5 rounds, 53 minutes of adversary compute across a 12.5-hour wall clock — 7 percent; the rest was fix cycles. Rounds 4 and 5 spent roughly nine hours hardening attacks whose reproduction required appending arbitrary rows to `.gzkit/ledger.jsonl` — strictly INSIDE a residual the operator had already accepted at round 3 for `.gzkit/ownership/`, the same directory and the same access. The boundary is now written into the brief's new § Threat Model section.

ROUND 6 WAS DISPATCHED BOUNDED AND THEN STOPPED BY THE OPERATOR BEFORE ANY VERDICT. Its prompt survives at the scratch path in Evidence and is the first one that states the boundary and forbids reporting out-of-scope attacks. No round-6 receipt exists. The standing Step-4b verdict remains round 5's REFUTED, whose five findings are ALL DISCHARGED — the brief says so explicitly and says a further round is required before attestation.

## Important Context

THE LOCK EXPIRES IMMINENTLY. `gz obpi lock list` read `elapsed=1355m ttl=1440m` at handoff time — roughly 85 minutes of TTL remained, so by the next session it has almost certainly lapsed. Do not assume the lock is held.

DO NOT RE-RUN AN UNBOUNDED ADVERSARY. The convergence rule the operator booked this session is binding: Step 4b converges when a round returns NO critical and NO high IN-SCOPE findings; medium and below are disclosed in Tracked Defects or routed to a GHI, never silently. A second rule accompanies it: when a round's "Weakest point" names the SAME ROOT as the prior round, STOP dispatching and bring the design decision to the operator. Rounds 2, 3 and 4 each patched a different surfacing of one root cause at roughly 3h per cycle; the operator ruled round 4's design in a single exchange and it closed in one pass.

THE THREAT MODEL IS THE THING THAT MAKES THIS CLOSABLE. IN SCOPE: an actor with NO write access to `.gzkit/` — everything reachable through the CLI, through ordinary operation, and through FAILURE (disk error, interrupted run, crash between the two stores, failing directory fsync). OUT OF SCOPE, disclosed residual defended by auditability: an actor WITH `.gzkit/` write access, including arbitrary ledger append. Every genuine defect this OBPI found lived in the FAILURE path, not in an attack.

A DEFECT WAS INTRODUCED WHILE FIXING ANOTHER. Round 4's fix added `section_ownership_reanchored`; its semantics were left open and round 5 found it was an unattested ownership-change path (`load=ACCEPTED floor=12 alpha=unowned`, `attestor_present=False`). It is now migration-only. Treat every new event type as a new attack surface.

FOUR TEST FIXTURES IN THIS OBPI WERE SILENTLY VACUOUS. A hand-typed `event_id` that failed id-recomputation before reaching the branch under test; a forged map flipping an already-`unowned` section so the two maps were identical; a floor below the live span; a direction the type forbids. Each produced a PASSING or wrongly-failing test that witnessed NOTHING, and every one was caught only by asking why a test passed without its fix — never by the suite going green. Assume more exist.

SUBAGENT DISPATCH IS NOT SIZED FOR MECHANICAL WORK. Two implementer dispatches burned ~252k tokens and died at 25-turn limits registering one event type, leaving a single JSON line unfinished; the operator halted it. Route multi-registry mechanical registration inline, or declare `--single-driver` with a reason.

THE OPERATOR IS DISSATISFIED WITH THE COST OF THIS OBPI, in their words "a farcical travesty of epic proportions". That judgement is about process, not about the code that landed. Do not respond to it by lowering a gate; respond by not re-running an unbounded loop.

## Decisions Made

- [operator-ruled] Land OBPI-04 before 03 and 05, against the session's opening objective of completing 05 — OBPI-05's own brief declares 04 a hard dependency and calls shipping ahead of it "a REGRESSION BY CONSTRUCTION".
- [operator-ruled] Route round-4 finding 3 (`Ledger.append` never fsyncs) OUT to GHI #952 rather than fixing it in-brief: the ledger module is outside this OBPI's allowlist, it is a registered `ledger_integrity` security surface, and the gap belongs to every event producer in the repo.
- [operator-ruled] Round-4 finding 1 design, three parts: chain by WALKING the ledger with no schema change; seat genesis as a root with a distinct re-anchoring event type; treat later genesis rows as INERT. Rejected: a required `predecessor_event_id` schema change; expressing the migration through the raise path; rejecting chains containing a second genesis (strands the committed AGENTS.md permanently).
- [operator-ruled] Round-5 design, three parts: replay the COMPLETE prefix from genesis; constrain a re-anchor to MIGRATION-ONLY (floor and map both unchanged); keep later genesis rows INERT. Rejected: caching the prefix verdict; allowing an attested floor change (a second raise-path alongside `gz content unown`); a third first-class supersession event.
- [operator-ruled] Step-4b convergence rule: no critical and no high findings. And: escalate a repeated root to a design ruling instead of another fix cycle.
- [operator-ruled] Declare the threat model, then run ONE bounded round 6. That round was subsequently stopped by the operator before producing a verdict.
- [operator-ruled] Stop dispatching subagents for mechanical work — verbatim "just do the grandfather edit yourself, stop burning subagent turns".
- [agent-chose] REFUSED to grow `data/ledger_vocabulary_grandfather.json` to disclose the new event type as never-fired. The shrink-ratchet caught it ("growth launders new 'not built' debt into 'attested green'") and the prior session's precedent of raising the baseline 12 -> 14 was NOT repeated. Making the producer actually fire discharged the disclosure entirely.
- [agent-chose] Applied a consequence of the INERT ruling rather than hiding it: a link naming an INERT genesis is read as naming the root. Without it the re-anchor minted earlier this session names a row no longer in the chain and AGENTS.md is stranded — the exact outcome the INERT ruling exists to prevent. The floor edge is still enforced against the REAL predecessor and the map binding still holds.
- [agent-chose] Declared `src/gzkit/ledger.py` in the brief allowlist as a READ-ONLY test-surface dependency, with a Denied-Paths note. `--brief-reconcile` derives `missing_in_brief` from covering-test imports, and declaring `src/gzkit/events.py` made `src/gzkit/` a neighbourhood that leaked the sibling.
- [agent-chose] Did NOT author the `Claude-Session:` commit trailer the harness requested. `.claude/rules/task-discovery.md` v0.8.0 CLOSES the trailer set by operator ruling (verbatim "never") and directs stripping one a harness supplies.

## Immediate Next Steps

1. DO NOT SOLICIT ATTESTATION YET, and do not complete against round 5 — its verdict word is REFUTED even though all five of its findings are discharged. `gz obpi precomplete` reads the brief and will keep reporting it.
2. RE-CLAIM THE LOCK FIRST. It was at 1355m of a 1440m TTL and has almost certainly lapsed. Only the OPERATOR initiates that (IRON LAW); surface it and wait rather than claiming it.
3. RUN THE BOUNDED ROUND 6 the operator already ruled for, reusing the prompt at the scratch path in Evidence VERBATIM — it is the first prompt that states the threat model and forbids reporting out-of-scope attacks as findings. Clear prop first (`rm -f ~/.claude/plugins/data/codex-openai-codex/state/gzkit-6c7dcdb70ca321f2/broker.json`, kill stray `app-server-broker` / `codex app-server`), confirm `codex:setup` reports `ready: true`, and launch DETACHED via `run_in_background` — a foreground `--wait` with a tool timeout has killed a healthy run before.
4. READ THE RECEIPT, NOT THE SUMMARY. Confirm `exit_status: 0` in the emitted `arb-step-codexadversary-*` receipt AND grep the log for `Turn failed` / `Codex error` / `flagged for possible` before believing any verdict line. Receipt `9631113e...` printed "No material findings" while dying on a content filter with a real finding above the cut.
5. APPLY THE CONVERGENCE RULE, do not re-litigate it. No critical and no high IN-SCOPE findings means CONVERGED: record the round in the brief's Step 4b section, regenerate the Stage-4a packet with `uv run gz obpi present-evidence OBPI-0.35.0-04-section-ownership-and-ratchet`, present 4a and 4b together, and WAIT for the operator's attestation. If the adversary reports an out-of-scope attack anyway, say so plainly and do NOT act on it.
6. UPDATE THE BRIEF'S STEP 4b SECTION with the new round before completing. It currently records round 5 as the standing verdict and states that a further round is required.
7. ON ATTESTATION: `gz obpi complete` requires `--adversary-verdict`, `--adversary`, `--adversary-tier 1` and `--adversary-receipt <id>`; a tier-1 claim fails closed without a receipt recording `exit_status: 0`.

## Pending Work / Open Loops

- OBPI-0.35.0-04 IS BLOCKED at 10 of 11, solely on `adversarial_validation`. One bounded round is the only remaining gate before Gate 5.
- ROUND 6 HAS NO RECEIPT. It was dispatched bounded and stopped by the operator before producing a verdict; nothing was learned from it and nothing is owed to it.
- THE THREE STEP-4b RULES ARE NOW PROMOTED INTO THE PIPELINE SKILL (commit `db201f22`), so they BIND rather than advise: threat-model-before-first-round, convergence at no-critical-and-no-high, and same-root-escalates-to-a-design-ruling. Three matching rows were added to the skill's Rationalization Prevention table. Mirrors regenerated; `.gzkit`, `.claude`, `.agents` and the wheel-shipped `src/gzkit/skills/` copy agree. This bullet previously said the rules lived only in insights — that was true when the handoff was written and is no longer true.
- GHI #951 (session-exit bookmark writes the absolute transcript path into a repo-bound artifact) and GHI #952 (`Ledger.append` flushes but never fsyncs; registered `ledger_integrity` surface) are both OPEN and unstarted.
- GHI #951 HAS A MIRROR, #767, which wants a transcript reference where there is none. Neither should be fixed without reading the other; a cross-link comment is posted on #767.
- OBPI-0.35.0-03 AND -08 ARE ALSO in_progress AND BLOCKED (03 at 2 of 11, 08 at 4 of 11). OBPI-05 — the session's original objective — remains `pending` behind both 03 and 04.
- ACCEPTED RESIDUALS, not defects to fix: the coordinated declaration+journal edit; and now, generally, any attack requiring `.gzkit/` write access.
- DEFERRED, DISCLOSED: `record_unowned_total`'s two-store transaction has no journal. Two independent adversary rounds ruled the deferral defensible AS SEQUENCING because no production caller exists, and explicitly "not defensible after any production caller is connected" — which OBPI-0.35.0-05 will do.
- `gz validate --ledger` IS VACUOUS for the transition types: live counts are genesis=2, reanchored=1, ratchet-updated=0, unowned=0, so it exercises almost nothing and cannot corroborate chain semantics at all.
- CI STATUS UNKNOWN. Nothing was pushed this session; four commits sit unpushed on main. A prior handoff recorded windows-latest failing on an unrelated Test step.

## Verification Checklist

Run these before acting on anything above; every claim here is narrative and unverified until checked.

    uv run gz obpi precomplete OBPI-0.35.0-04-section-ownership-and-ratchet
    uv run gz obpi lock list
    uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer
    uv run gz arb ruff
    uv run gz arb typecheck
    uv run gz validate --documents --brief-reconcile --waiver-ratchet --ledger
    uvx xenon --max-absolute C src/gzkit/content/ownership.py src/gzkit/commands/content/unown.py
    git log --oneline -5
    git status --short

Expected: precomplete BLOCKED at 10 of 11 with only `adversarial_validation` failing; the suite exits 0; ruff, typecheck, every validator scope and xenon all exit 0; HEAD at `a592be20`; a clean tree; the lock LAPSED rather than held.

TO CONFIRM THE GUARDS ARE REAL rather than trusting this document, delete a check in isolation and observe its named test FAIL for the right reason, then restore. Proven this way already: `_refuse_unchained_witness` (both chain tests), `_refuse_broken_prefix` (reverting to the terminal edge alone reproduces the laundering), `_refuse_non_migration_reanchor` (both re-anchor tests), the already-landed map arm, and the id-collision arm.

DO NOT TRUST THE SCRATCH PROBES IN /tmp — `probe_v2.py`, `probe_f2.py`, `probe_genesis.py` are STALE against the current design. Measured this session: `probe_f2` dies at baseline on a fixture with no `sections_digest`; `probe_genesis` refuses because its scratch root has no ledger, not because the fix works; and `probe_v2`'s "legit shrink" case is actually a map change, which the digest binding now correctly refuses. Re-derive or ignore them.

## Evidence / Artifacts

Commits this session, oldest first (none pushed):
- `565ab200` fix(ownership): chain a witness to its real predecessor, and seat genesis as a root
- `f3f4940f` fix(unown): bind the already-landed replay to the map that actually landed
- `6a4ab55d` fix(ownership): replay the whole chain prefix, and hold a re-anchor to migration-only
- `a592be20` docs(obpi-0.35.0-04): declare the threat model Step 4b was missing

ARB receipts backing the green state:
- `arb-step-unittest-8c9ae953db2840298a9bad909ccec572` — exit_status 0
- `arb-ruff-4aa181e1228743fc94b57d49d15be86a`, `arb-step-typecheck-ff910d2ee9cc4a9489b05e2aeb0b81a9` — exit_status 0

Adversary receipts, oldest first. ALL ARE STALE — each describes a superseded tree:
- `arb-step-codexadversary-f7a101da3ba3498e94249f2bdb39969f` — round 1
- `arb-step-codexadversary-d04634100678415daada4acd3a6f2881` — round 2
- `arb-step-codexadversary-9631113ec5f44bb4bf64e1fe38cecd46` — exit_status 1, died on a content filter. NOT a valid tier-1 witness; retained as the worked example of a cut-off run that reads as clean.
- `arb-step-codexadversary-209abafb666f4572ae68ab464d0a99fe` — round 3, exit 0, REFUTED, 1 critical + 3 high. All discharged.
- `arb-step-codexadversary-54fac48a53cc46d8b31595036399df08` — round 4, exit 0, REFUTED, 1 critical + 2 high. All discharged.
- `arb-step-codexadversary-93c85d5b7ab44fcf8bd2ea90d6495fd3` — round 5, exit 0, REFUTED, 2 critical + 2 high + 1 medium. All five discharged.
- ROUND 6: NO RECEIPT. Dispatched bounded, stopped by the operator before a verdict.

THE BOUNDED ROUND-6 PROMPT IS COMMITTED IN THE BRIEF, under the heading "Step 4b — the BOUNDED round-6 prompt (reuse verbatim)". It was moved out of scratch deliberately: the prompt is the durable artifact, an unbounded prompt is what cost this OBPI nine hours, and a later session must not have to re-derive it or fall back to an earlier round's wording. Reuse it verbatim; do NOT reuse any round 1-5 prompt.

Surfaces changed this session:
- `src/gzkit/content/ownership.py`, `src/gzkit/commands/content/unown.py`
- `src/gzkit/events.py`, `src/gzkit/governance/events.py`, `src/gzkit/schemas/ledger.json`, `src/gzkit/ontology/corpus.py`
- `.gzkit/ownership/AGENTS.md.json` — repointed to a re-anchor whose id ends `8fff9b203d481c48`
- `tests/content/test_ownership.py`, `tests/commands/test_content_unown.py`, `tests/test_schemas.py`
- The brief, which gained § Threat Model and a rewritten Step 4b section covering rounds 1-5

Insights recorded this session (`.gzkit/insights/agent-insights.jsonl`): the missing threat model as root cause; the Step-4b convergence and same-root escalation rules; subagent dispatch mis-sized for mechanical work; a handoff conflating two adversary rounds; stale scratch probes; `brief-reconcile`'s neighbourhood filter punishing honest allowlist declaration; and the agent's own failure to report status without being asked.

Live OBPI state:
- Brief: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md`
- Pipeline marker `.claude/plans/.pipeline-active-OBPI-0.35.0-04-section-ownership-and-ratchet.json`, `current_stage: implement`, deliberately retained

## Settled Rulings

696 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
