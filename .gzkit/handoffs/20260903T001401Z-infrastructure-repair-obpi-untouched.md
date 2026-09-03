---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-09-03T00:14:01Z'
agent: claude-code
obpi_id: OBPI-0.35.0-04-section-ownership-and-ratchet
session_id: 9b60410d-b9da-4ed2-86d0-e8b165e13b0b
continues_from: .gzkit/handoffs/20260902T222242Z-obpi-0-35-0-04-stage4b-refuted-genesis-gap.md
---

## Current State Summary

THE OBPI WAS NOT TOUCHED THIS SESSION. Not one stage ran, no finding was repaired, and the Step 4b verdict is still REFUTED. `gz obpi precomplete` reads 10 of 11, blocked solely on `adversarial_validation: Step 4b records refuted` — the same state the predecessor handoff recorded. The lock is still HELD (agent=claude-code-9de7e7a3, elapsed 688m of a 1440m ttl) and both pipeline markers are still in place with `current_stage: implement`, `resume_point: verify`.

What this session actually did was repair the infrastructure that was blocking every push. Eight commits landed and `main` is level with `origin/main`. Four checks were failing on `main` at session start and all four now pass locally: the settled-ruling test, the tautological-test audit, task-envelope coherence, and Preflight.

The operator's closing question was whether this OBPI will ever complete. The measured answer is that it is one design ruling and one mechanical fix away, and that under the IRON LAW the agent cannot start it.

## Important Context

THE AGENT CANNOT INITIATE THIS WORK. AGENTS.md IRON LAW, verbatim: 'OBPI WORK WILL NOW ONLY BE OPERATOR INITIATED WORK THAT I EXECUTE VIA THE SKILL' and 'NEVER START ANY OF IT ON YOUR OWN. NEVER'. Every instruction this session named something else — git-sync, read the handoff, file the GHIs, fix 947 then 948, delete the abridged ruling and push, why is gz check called so often, drop Behave, add Preflight, extend the TTL. Each was done. None was the OBPI, and the agent may not reach for it unprompted. A resuming agent must NOT read this handoff as license to start the pipeline.

THE GATE THAT SAID GREEN WAS LYING, AND THAT IS NOW FIXED (GHI #949, closed at 4012acb5). `tests/unit/test_progress_indication.py` patched `get_project_root` to `Path('.')` — the real repository — and stubbed every check step to pass, so `check()` wrote `.gzkit/cache/check-verified.json` for whatever tree was staged. That is the receipt the pre-push gate reuses. Consequence: merely RUNNING the suite stamped the tree as fully verified, and a FAILING `gz check` still left a passing receipt behind, because its own Test step wrote one before the failure was reported. The pre-push gate was satisfiable by having run the tests. Any green pre-push reading from before 4012acb5 should be treated as unevidenced.

PREFLIGHT WAS RED BECAUSE THE OBPI IS PARKED, NOT BECAUSE ANYTHING WAS WRONG. Marker staleness was pure wall-clock age against a 4h TTL, so the checkpoint markers went stale at 16:45Z and then failed every `gz check` — locally AND in CI — regardless of what was being pushed. CI failed on all four pushes today for this. The TTL is now 24h and Preflight is out of the pre-push scope.

CI IS STILL RED ON WINDOWS. `gz check` on windows-latest reports a Test failure that is unrelated to this session's work and was never investigated. Do not read a green local run as a green CI.

THE GHI QUEUE IS GROWING, AND THAT IS THE OPERATOR'S STANDING COMPLAINT. Measured 2026-09-02: 17 issues filed that day against 6 closed, 46 open. Thirteen of the seventeen are defects in governance machinery rather than in any delivered capability. The agent contributed to this by treating every gate it tripped over as in-scope to diagnose.

## Decisions Made

- [operator-ruled] Fix GHI #947 by dropping `artifact_edited` from `_TASK_WORKLOG_TYPES` rather than giving it a real `task_id` channel or grandfathering the rows (selection: 'Drop from worklog roster'). The roster's own criterion is 'worklog event types that carry an optional task_id field' and this type's constructor has no such parameter, so its membership was always inconsistent. An authored pin asserted the opposite and was INVERTED, not deleted; its premise that the tool locus 'is knowable and attributable' was measured false.
- [operator-ruled] Delete the abridged GHI #940 ruling twin and push (verbatim: 'delete the abridged ruling and push'). Verified lossless before deleting: the 85-char abridged text minus its trailing period is a strict prefix of the 281-char fuller form, which survives at line 670.
- [operator-ruled] Keep the per-push gate rather than moving the heavy sweep to CI only (verbatim: 'no, doing it per push is needed').
- [operator-ruled] Drop Behave from the pre-push scope (verbatim: 'yes, drop behave from pre-push'). Measured 30.61s, the largest step in the sweep.
- [operator-ruled] Make the scope roster configurable rather than a module constant (verbatim: 'i like it being configurable', 'that sould be in config though'). Spelling preserved.
- [operator-ruled] Add Preflight to the prepush skips (verbatim: 'add Preflight to the prepush skips').
- [operator-ruled] Raise the pipeline-marker TTL from 4h to 24h (verbatim: '4 hours is too short given how pitiful gzkit is, extend to 24 hours').
- [operator-ruled] Route every verification claim through the ARB canonical invocations, not bare shell commands (verbatim: 'how many times do i need to remind you to RUN FROM SKILLS!!!!!'). Recorded as an improvement insight before the corrected work completed.
- [agent-chose] Did NOT clear the pipeline markers, though doing so would have fixed both the local gate and CI. Clearing a marker is OBPI work under the IRON LAW, and it would destroy the `resume_point` the checkpoint exists to preserve.
- [agent-chose] Did NOT add the seven tautological-audit findings as waivers. The shrink-only waiver ratchet refused it, and every ratchet file says verbatim 'NEVER add an entry to silence a newly-authored gate'. Fixed the scanner instead, which is what the ratchet's own recovery prose prescribes.
- [agent-chose] Filed GHI #949 as an `investigation` rather than asserting a mechanism, because the timeline did not fit the hypothesis. That was correct: the hypothesis was wrong and the real cause was found later by bisection.
- [agent-chose] Corrected a fabricated line in a GHI evidence block by posting a public correction rather than editing it away, and recorded the reporting defect as an insight.
- [agent-chose] Made a prepush run non-recording. It is a partial sweep, and letting a partial verification mint the fingerprint the gate reuses is the presence-check failure AGENTS.md names.

## Immediate Next Steps

1. DO NOT START THE OBPI. Present this state to the operator and wait. Under the IRON LAW only the operator initiates OBPI work, and only via the gz-obpi-pipeline skill.
2. OBTAIN THE FINDING 1 DESIGN RULING. Genesis has no provenance anchor by construction: `load_declaration` accepts any section/floor-coherent declaration carrying a null `floor_event_id`, and self-coherence is exactly what an attacker recomputes. Three candidate anchors: a `section_ownership_genesis` ledger event, a commit-SHA anchor, or forbidding a null `floor_event_id` after day one. The standing agent recommendation is the ledger event, because it is the only one that makes genesis a witnessed STATE rather than a shape. Whichever is chosen must ALSO repair the non-null branch, which today accepts any event id whose floor matches regardless of event type or surface.
3. FIX FINDING 2 — journal replay validation. Mechanical, no ruling needed. `_replay_pending_transition` writes `declaration_json` verbatim and appends its claimed event without validating attestor, reason, event id, transition span, or that the journal starts from the declaration on disk. `_JOURNAL_FIELDS` also omits `ts` while `_append_event_once` reads it.
4. BATCH THE REPAIRS BEFORE RE-VERIFYING. Findings 1, 2, 3 and 4 in one pass, THEN one Stage 3, then regenerate the Stage-4a packet with `gz obpi present-evidence`, then one Step 4b dispatch. Three prior sessions each paid a full verify-and-review cycle per finding, which is the whole reason this has taken as long as it has.
5. RE-DISPATCH STEP 4b through the plugin, never `codex exec`, ARB-wrapped so the receipt can be cited. Only after a clean or caveat-resolved verdict may attestation be solicited. `gz obpi complete` will require `--adversary-resolution` because the standing verdict is refuted.

## Pending Work / Open Loops

- OBPI-0.35.0-04 IS BLOCKED at 10 of 11 preconditions, solely on `adversarial_validation: Step 4b records refuted`. Every other precondition passes.
- ADVERSARY FINDING 1 OPEN [high] — genesis provenance anchor. Blocked on an operator design ruling. Reproduced: floor 8637 hand-raised to 10182 with no ledger file in existence.
- ADVERSARY FINDING 2 OPEN [high] — journal replay is an unvalidated arbitrary declaration write. Introduced by a prior session's own repair. Mechanical; fix first.
- ADVERSARY FINDING 3 OPEN [medium] — `record_unowned_total`'s two-store transaction is not recoverable.
- ADVERSARY FINDING 4 OPEN [medium] — no directory fsync after `os.replace`.
- CI IS RED ON WINDOWS-LATEST — a Test-step failure unrelated to this session and never investigated. Local green does not imply CI green.
- GHI #944 OPEN — Rich markup swallows every validator error type. A sibling sweep found seven further sites plus one already-escaped line in the same file; evidence posted on the issue. Unworked.
- GHI #945 OPEN — the advisory-lock primitive is a private cross-module import. Unworked.
- GHI #946 OPEN — `gz task envelope diagnose` reads the frontmatter channel empty because the caller truncates the OBPI id to its bare form. Root cause proven; unworked.
- NO MECHANICAL GUARD stops a future test from rooting `check()` at the real repository. GHI #949 [settled]'s fix is two call sites, not a fence. Disclosed on the closed issue.
- THE PIPELINE MARKERS AND THE LOCK REMAIN IN PLACE deliberately. They are the live checkpoint, not residue.

## Verification Checklist

Run these before acting on anything above. Every claim here is Layer-1 narrative and is unverified until checked.

    uv run gz obpi precomplete OBPI-0.35.0-04-section-ownership-and-ratchet
    uv run gz obpi status OBPI-0.35.0-04-section-ownership-and-ratchet
    uv run gz obpi lock list
    uv run gz check
    uv run gz validate --tautological-test-audit
    uv run gz validate --task-envelope-coherence
    uv run gz validate --waiver-ratchet
    uv run gz preflight
    git rev-list --left-right --count origin/main...HEAD
    gh run list --limit 4

Expected: precomplete BLOCKED at 10 of 11 with only `adversarial_validation` failing; lock ACTIVE for agent claude-code-9de7e7a3; the four validators above all exit 0; git rev-list reports 0 0; CI still failing on windows-latest.

TO CONFIRM THE GHI #949 FIX RATHER THAN TRUSTING THIS DOCUMENT: delete `.gzkit/cache/check-verified.json`, run `uv run unittest-parallel -t . -s tests --buffer`, and confirm no receipt reappears. Before 4012acb5 it did.

TO CONFIRM THE SCOPE CHANGE: `uv run gz check --reuse-verified` must run 57 steps, print a scoped pass naming Behave and Preflight as not run, and leave no verified fingerprint behind.

## Evidence / Artifacts

Session commits, oldest first:
- `72bbb9a7` chore: ledger session-exit bookmark
- `714c2837` chore: insights record
- `270367d2` fix(task-envelope): drop artifact_edited from the worklog roster (GHI #947)
- `ec68ebd6` fix(tautological-audit): see through helpers, value-loads and raise-assertions (GHI #948)
- `b7245878` fix(handoff): drop the abridged GHI #940 ruling twin
- `c37209e4` perf(check): declare per-scope step membership in config
- `58e4e46d` perf(check): scope the pre-push gate, and raise the marker TTL to 24h
- `4012acb5` fix(check): stop the unit suite minting the repo's verification receipt (GHI #949)

Surfaces changed:
- `src/gzkit/commands/validate_task_envelope.py`
- `src/gzkit/tautological_tests.py`
- `src/gzkit/commands/quality.py`
- `src/gzkit/pipeline_markers.py`
- `src/gzkit/cli/parser_obpi.py`
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py`
- `data/check_step_scopes.json`
- `data/config_registry.json`
- `.gzkit/handoffs/rulings.jsonl`
- `docs/user/manpages/obpi-pipeline.md`
- `docs/governance/GovZero/obpi-pipeline-runbook.md`

Tests changed or added:
- `tests/governance/test_check_step_scopes.py`
- `tests/governance/test_task_envelope_coherence.py`
- `tests/governance/test_tautological_tests.py`
- `tests/unit/test_progress_indication.py`
- `tests/unit/test_runtime_presentation.py`
- `tests/commands/test_preflight.py`
- `tests/test_pipeline_runtime.py`

Live OBPI state, untouched this session:
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md`
- `.claude/plans/.pipeline-active-OBPI-0.35.0-04-section-ownership-and-ratchet.json`
- `.claude/plans/.pipeline-active.json`

Prior handoff in this chain:
- `.gzkit/handoffs/20260902T222242Z-obpi-0-35-0-04-stage4b-refuted-genesis-gap.md`

## Settled Rulings

683 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
