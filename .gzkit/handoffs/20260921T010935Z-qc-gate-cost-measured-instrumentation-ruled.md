---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-21T01:09:35Z'
agent: claude-code
session_id: 89db8fc3-11a3-4b76-8abe-aeb3edb12ce7
continues_from: .gzkit/handoffs/20260921T005611Z-foreign-citation-repair-and-campaign-deferred.md
---

## Current State Summary

A diagnosis session on the cost of the quality gate, ruled to the handoff rather than implemented. The operator called the QC grind ridiculous; `gz check` was measured and structurally read, and the operator ruled option A — instrument the gate before optimising it — then ruled that the work goes to this handoff rather than into this session. NOTHING WAS IMPLEMENTED FOR THAT RULING. No source file was changed after commit 1841c53d9. What this session did change is already pushed: the cross-repository citation repair at 1841c53d9, the handoff and insight material at ed034d6a4, and the prior handoff at 64e712057. `git rev-list --left-right --count origin/main...HEAD` returned zero and zero before this document was written. The measurement itself is the deliverable here, and its headline is that the gate carries no timing instrumentation at all: no per-step duration is printed, `gz check` writes no ledger event, and the verified receipt records only a fingerprint and a scope.

## Important Context

WHAT OPTION A IS, IN THE OPERATOR'S CHOICE. Four routes were put up: A instrument the gate first, B attack the behave tier, C raise the step-concurrency cap, D record and move on. A was ruled. Its content as presented: per-step elapsed time in the step output, and a duration plus timestamp in the verified receipt. The argument for A over B and C is that both B and C are currently unfalsifiable — nothing measures which of the 63 steps costs what, so any optimisation claim would be unprovable in either direction.

THE STRUCTURE, READ FROM DECLARED STATE. `gz check` runs 63 steps. `data/check_step_concurrency.json` declares 61 of them read_only and 2 as writers; the two writers, `Behave` and `Docs build`, therefore run SERIALLY. `_MAX_CONCURRENT_STEPS` in `src/gzkit/commands/quality.py` caps the concurrent pool at 8. `gz check --fast` runs 60 steps, skipping the suite, behave and docs.

THE SCALE BEHIND THE SERIAL PAIR. 467 behave scenarios across 74 feature files, with 95 subprocess-spawn sites in the step definitions. Behave has no native parallelism. The unit tier is 10,775 tests run under unittest-parallel. Every spawned CLI invocation pays interpreter and uv startup; the cheapest real invocation measured this session was one second, which is the floor a per-scenario spawn cannot go below.

THE INSTRUMENTATION GAP IS THE FINDING, NOT THE SLOWNESS. Nothing records what the gate costs. Today's ledger holds a single row and it is the handoff ruling, so `gz check` emits no event. `.gzkit/cache/check-verified.json` stores a fingerprint and a scope with no timestamp and no duration. The consequence is that every conversation about the grind has to re-measure from scratch, which is what this session did.

TWO MITIGATIONS ALREADY EXIST AND ONE WAS UNDER-USED. `gz check --fast` is the inner loop and never satisfies the gate. `gz check --reuse-verified` skips entirely when the exact STAGED tree already passed a full check. This session ran the full gate three times over a tree that changed only slightly, rather than reusing the verified fingerprint. That is an agent error, not a tool cost, and part of what the operator experienced as the grind.

A HYPOTHESIS, MARKED AS ONE. Behave is the likely dominant cost: it is serial, it is 467 scenarios, and it spawns real subprocesses. That is a reading of structure and scale, NOT a measurement, and option A exists precisely so the next session can settle it instead of arguing it.

## Decisions Made

- [operator-ruled] Instrument the quality gate before optimising it — option A of four (verbatim: "A, but send to handoff, git sync it").
- [operator-ruled] The instrumentation work goes to this handoff rather than into this session, and this session ends by syncing (verbatim: "A, but send to handoff, git sync it").
- [operator-ruled] The QC grind is a real problem worth acting on, not an acceptable cost (verbatim: "yes, the QC grind is ridiculous").
- [agent-chose] Measured the gate rather than proposing a fix from its shape, because no per-step cost was recorded anywhere and every route on offer depended on knowing it.
- [agent-chose] Marked behave as a hypothesis rather than a conclusion, since the structural reading that points at it is exactly the kind of claim option A exists to test.
- [agent-chose] Filed no GHI for the instrumentation work, because the operator named this handoff as its destination.

## Immediate Next Steps

1. Build the ruled instrumentation. Per-step elapsed time in the step output of `gz check`, and a duration plus a timestamp in `.gzkit/cache/check-verified.json`. Read `src/gzkit/check_fingerprint.py` first: `record_verified` writes the receipt and currently persists only a fingerprint and a scope, and the module's own docstring explains why the fingerprint names the INDEX tree rather than the working tree. Adding a step to `gz check` carries nine coupled obligations documented in `_build_check_steps`; adding TIMING to existing steps should carry none of them, and that should be confirmed rather than assumed.
2. With timing in hand, settle whether the behave tier dominates. If it does, size the win before changing it: 467 scenarios that each spawn a real CLI cannot go below the interpreter startup floor, so the question is scenario count and spawn count, not test speed.
3. Re-read the concurrency cap once costs are visible. `_MAX_CONCURRENT_STEPS` is 8 against 61 read-only steps, which matters only if those steps are a meaningful share of the total.
4. Use `uv run gz check --reuse-verified` in any session that runs the gate more than once over a barely-changed tree. This session did not, and paid three full runs for it.
5. Two items carried from the previous handoff and still unruled: the pre-commit hook chain does not run the unit tier while the git-sync skill says it does, and the handoff Settled Rulings pointer renders a count computed before the document's own rulings are booked.

## Pending Work / Open Loops

RULED AND PARKED HERE. The option A instrumentation work. It has an operator ruling, a named destination which is this document, and no implementation. It is not an issue, a chore or an OBPI, and it will stay invisible to every queue until someone reads this handoff.

CARRIED FROM THE PREVIOUS HANDOFF, UNROUTED. The pre-commit hook chain runs no unit tier while the git-sync skill's Red Flags table rests on the claim that it does. The Settled Rulings pointer count, rendered before the document's own rulings are booked into the store.

DEFERRED BY RULING, NOT CLOSED. GHI #1069, verified OPEN, with two implementation choices unruled: where the detector arm lives, and whether its scope stays at the tests tree.

CARRIED, UNRESOLVED. OBPI-0.35.0-08 in a runtime state of IN PROGRESS with no lock and no completion proof. GHI #1063, counting 51 validator scopes never invoked. The standing 713 unlinked specs the drift scope reports. GHI #1028, open under the explicit campaign hold for 2026-09-19. Commit 84ea8e435, published without a Task trailer, unrepairable without a force-push that policy forbids.

CAMPAIGN. ADR-0.35.0 remains TOPMOST and the operator returns to it later. Nothing was initiated.

OUTSIDE THIS REPOSITORY. The gz-skills OpenCode v2 bundle, uncommitted on top of the v0.4.0 release commit, with another session active in that tree as of 00:40Z. Not installable until a v0.5.0 tag is published.

## Verification Checklist

Re-measure rather than trusting the figures recorded here; they are a dated observation of this tree on 2026-09-21, not a threshold. The script that produced them ran each command in sequence and read its own exit code.

Run `uv run gz check --fast` and expect exit 0. Observed: 169 seconds over 60 steps, skipping the suite, behave and docs.

Time `uv run gz test` for the unit tier and `uv run mkdocs build --strict` for the docs build. NEITHER WAS TIMED TO COMPLETION HERE: the measuring run was still inside the unit tier when the operator ruled that this work goes to the handoff, so the only observed figure in this document is the fast-scope one. Those two plus behave are the whole difference between 169 seconds and the ten-to-fifteen minutes the operator objected to, so they are the first numbers step 1 should produce.

Run `uv run gz check` and expect exit 0. If you pipe it, use `set -o pipefail` first; the verifier-pipe-gate hook refuses a bare pipe. Do not run it detached across a session boundary — a run in the previous session was detached by a fork and its exit code was lost even though it had printed a pass.

Read `data/check_step_concurrency.json` and expect 63 steps with exactly two declared writers, `Behave` and `Docs build`.

Read `.gzkit/cache/check-verified.json` and expect a fingerprint and a scope and nothing else. That absence is the subject of step 1.

Run `git rev-list --left-right --count origin/main...HEAD` and expect zero and zero.

Run `git log --oneline -4` and expect the citation repair at 1841c53d9 with a Task trailer, the handoff landing at ed034d6a4, and the sync commit at 64e712057.

## Evidence / Artifacts

`src/gzkit/commands/quality.py`
`src/gzkit/check_fingerprint.py`
`data/check_step_concurrency.json`
`.gzkit/cache/check-verified.json`
`src/gzkit/handoff_api.py`
`src/gzkit/commands/reference_checker.py`
`tests/commands/test_reference_checker.py`
`.gzkit/handoffs/20260921T005611Z-foreign-citation-repair-and-campaign-deferred.md`
`.gzkit/handoffs/20260921T002935Z-land-survey-and-unruled-prior-advice.md`
`.gzkit/ledger.jsonl`

## Settled Rulings

1012 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
