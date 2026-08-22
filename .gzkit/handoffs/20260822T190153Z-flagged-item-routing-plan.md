---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-22T19:01:53Z'
agent: claude-code
session_id: 9e91d721-7d7e-4b94-84f6-7e166a51eb13
continues_from: .gzkit/handoffs/20260822T185415Z-uncovered-req-inventory.md
---

## Current State Summary

This handoff carries a PROPOSED routing plan for the items flagged in its
predecessor, and one finding that reframes them. The plan is agent-authored and
NOT ratified: the operator asked what the agent would do and then asked for the
answer to be recorded. No item below is authorized work.

**The finding.** The session-cost complaint that opened this session — any given
task taking 30 to 60 minutes — has been ruled on before. The rulings corpus holds
an operator ruling, verbatim: "great, another 45 minute run, why does any
meaningful action in gzkit take this long to run?" Its settled remedy was
behavioural: use the narrow verifier while iterating, pay for the full gate once.
That remedy is a discipline for the agent with NO mechanical witness, and the
identical complaint recurred. This is the doctrine-declared-without-mechanism
family named in AGENTS.md, applied to gzkit's own running cost.

**The proposed ranking.**

| Rank | Item | Rationale |
|---|---|---|
| 1 | Profile the 56 `gz check` validators, then tier | 3m29s, called twice per OBPI; this is the actual floor |
| 2 | Make `gz drift` report by REQ kind | Overstates the real gap ~100x; a metric that wrong is worse than none |
| 3 | Cover the 6 BEHAVIOR REQs | Real, small; likely 3 repairs since 4 cluster on 2 briefs |
| 4 | Commit the pending report and handoffs | One command |
| drop | mx.awareness, pipeline_runtime, lazy arb init | Measured, low value, more mechanism |
| defer | GHI #847 | Needs an operator decision on ledger volume first |

Rank 1 begins with MEASUREMENT, not surgery: one timing run over the 56
validators decides whether the cost is a few slow tree-walkers or a thousand
cuts, and the remedy differs completely between those.

## Important Context

**Why rank 1 is measurement rather than a fix.** The two plausible shapes need
opposite remedies and the evidence does not yet distinguish them. If a handful of
validators dominate, the fix is to make those change-scoped — most re-walk 1,135
ADR files and roughly 8,300 tracked paths that did not change. If the cost is
spread evenly, the fix is to route the inner loop to `uv run gz smoke` and reserve
the full gate for pre-push, which mechanises the behavioural ruling that already
exists and did not hold. Guessing between them risks optimising the wrong half.

**No gate is proposed for removal.** Only WHEN and HOW OFTEN gates run would
change. This matters because the advisory scorecard's freeze holds that the
imbalance to correct is too much mechanism rather than too little; the coherent
reading is not to delete gates but to stop paying for every gate on every
keystroke. Both `uv run gz check` and `uv run gz smoke` already exist, so rank 1
is wiring rather than new machinery.

**Why rank 2 sits above the actual defects it hides.** `gz drift` reports 715
unlinked specs where 6 are genuine. A metric overstating by two orders of
magnitude is worse than no metric: it trained this repository to read the number
as background noise, which is how 6 real coverage gaps on attested heavy-lane
work sat unnoticed inside it. Repairing the reporter surfaces the defects the
reporter was concealing, so it precedes repairing them.

**What connects ranks 1 and 2.** Both are cases where gzkit measures something
true and reports it in a shape no one can act on. That is a different disease
from missing governance and it does not improve by adding more of it.

**The drop list is the same call as the skip already booked.** The operator ruled
"skip it" on a hook import-budget check because the observed instance was already
witnessed per-instance. `gzkit.mx.awareness` (48ms per user prompt),
`gzkit.pipeline_runtime` (74ms, ExitPlanMode only) and a lazy
`src/gzkit/arb/__init__.py` are the same shape: measured, small, and each would
add surface. Recording them as dropped rather than deferred, per the operator
posture that a deferred item naming no queue is an open loop.

## Decisions Made

- [operator-ruled] Record the flagged-item routing plan as a fresh handoff (verbatim: "send it to fresh handoff").
- [agent-chose] Recorded the plan as PROPOSED and explicitly unratified. The operator asked what the agent would do and asked for it to be written down; neither is approval. Writing an unratified ranking as authorized work would manufacture a ruling that was never given.
- [agent-chose] Ranked the gz check profile first, above the 6 real coverage defects. The defects are genuine but small; the check runtime is the complaint that opened the session and the one thing measured this session that nobody has acted on.
- [agent-chose] Made rank 1 a measurement rather than a fix, because the two candidate shapes of the cost need opposite remedies and current evidence does not separate them.
- [agent-chose] Ranked the gz drift reporter above the defects it conceals, on the reasoning that a metric wrong by 100x is worse than no metric and is why those defects went unseen.
- [agent-chose] Put the three remaining import-hygiene items on a drop list rather than a deferral list, matching the booked "skip it" posture and the operator rule that deferred postures be recorded as accepted.

## Immediate Next Steps

1. Rule on the proposed ranking in the Current State Summary. Nothing below is authorized until that ruling exists; the plan is agent-authored.
2. If rank 1 is approved, run one timing pass over the 56 validators sequenced in `src/gzkit/commands/quality.py` and read which dominate the 3m29s. Expect a single roughly four-minute run. The result decides between change-scoping a few tree-walkers and tiering the inner loop onto `uv run gz smoke`.
3. Decide whether the behavioural ruling already in the corpus should be mechanised rather than restated. It reads "use the narrow verifier while iterating, pay for the full gate once" and it has no witness; the same complaint recurred with it booked.
4. If rank 3 is approved, cover the 6 BEHAVIOR REQs listed in section 1 of the inventory report. Check first whether the 4 on ADR-0.0.63 collapse into 2 brief-scoped repairs, since they cluster on OBPI-03 and OBPI-06.
5. Commit the pending report and the two handoff documents, which are staged but uncommitted.

## Pending Work / Open Loops

- **The whole plan is unratified.** Ranks 1 through 4 and the drop list are agent judgment awaiting an operator ruling. No work has started on any of them.
- **`gz check` remains 3m29s over 56 serial validators**, called twice per OBPI by the pipeline. Unmeasured at per-validator granularity, which is what rank 1 would supply.
- **The behavioural ruling on verifier cost has no mechanical witness.** It is booked in `.gzkit/handoffs/rulings.jsonl` and the complaint it settled recurred anyway.
- **The 6 genuine BEHAVIOR coverage defects are unrouted.** No GHI, no repair. Listed in section 1 of the inventory report.
- **`gz drift` still reports a flat 715** rather than splitting by REQ kind, so the advisory continues to overstate the actionable gap by roughly 100x.
- **Dropped, recorded as accepted rather than deferred**: gzkit.mx.awareness at 48ms per user prompt, gzkit.pipeline_runtime at 74ms on ExitPlanMode, and making `src/gzkit/arb/__init__.py` lazy.
- **GHI #847 [settled] remains open** and is not proposed for this plan. Four sibling hooks still key on tool_input file_path and are bypassed by Bash writes; the ledger-writer arm needs an operator decision on ledger volume before it is buildable.
- **Uncommitted at handoff time**: `.gzkit/ledger.jsonl` and `.claude/plans/.plan-audit-receipt-OBPI-0.26.0-12-docs-lib.json`, plus two hook-generated session-exit bookmarks.

## Verification Checklist

Re-derive the prior ruling this plan turns on, rather than trusting the quotation
above:

```bash
uv run gz handoff rulings --search "gz check"
```

Re-measure the full gate before accepting the 3m29s figure, which is a dated
measurement from 2026-08-22 on one machine:

```bash
uv run gz check
```

Confirm the narrow tier exists and what it currently costs, since rank 1 may
route the inner loop onto it:

```bash
uv run gz smoke
```

Re-derive the coverage split before acting on the 6 figure:

```bash
uv run gz drift --json
```

Confirm the three ADRs holding the genuine defects are still Validated and fully
attested. Read the live landed count from the command rather than a figure
transcribed here — a second copy in prose has no reconciliation path and goes
stale the next time an OBPI is added, withdrawn, parked, or folded. Run it for
each of ADR-0.0.41, ADR-0.0.59, and ADR-0.0.63:

```bash
uv run gz adr status ADR-0.0.63
```

## Evidence / Artifacts

- `.gzkit/handoffs/20260822T185415Z-uncovered-req-inventory.md` — the predecessor handoff; its Pending section is the flagged-item list this plan routes.
- `docs/governance/uncovered-req-inventory-2026-08-22.md` — the 715-row inventory; section 1 lists the 6 genuine BEHAVIOR coverage defects.
- `.gzkit/handoffs/rulings.jsonl` — holds the prior operator ruling on verifier cost that this plan argues was never mechanised.
- `src/gzkit/commands/quality.py` — sequences the 56 validators that rank 1 would profile.
- `src/gzkit/commands/smoke_cmd.py` — the narrow tier rank 1 would route the inner loop onto.
- `.gzkit/rules/tests.md` — declares the smoke tier and the full unit tier's explicitly unbounded runtime.
- `docs/governance/advisory-rules-audit.md` — carries the promotion-order freeze the drop list is reasoned against.

## Settled Rulings

476 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
