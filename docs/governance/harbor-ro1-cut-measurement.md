<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-1 specification — stopping the bleeding, and measuring every cut

**2026-10-25. Status: acts (a) to (g) landed 2026-10-17 and 2026-10-18 (passage log); specified for the remaining work.** Operator: **g0**. Repair order RO-1 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), serving the control plane.

## What has landed

Acts (a) to (g) are in the passage log: session-start text on one channel under 4 KB; the dead `instruction-router` hook removed; skill descriptions to one sentence under 6,000 chars; rule version banners lifted to `rule-version-history.md`; the governance read mandate pointed at the Coverage Ledger; the budget witness extended to every loaded surface (GHI #1249, closed); the recurrence threshold for choosing cuts by cause, with its check (`gz insights recurrence`).

## What remains: the measurement protocol (GHI #1252)

RO-1's witness column names *"WP-16's effectiveness read per cut"*. The cuts themselves are RO-7's: GHI #1246 is RO-7's stage 1 (its cross-link comment and RO-7's register row both say so), and RO-7 runs the later stages. RO-1 owns the protocol every one of those stages is measured by.

## Rulings

- Operator, 2026-10-16, verbatim: *"help me test how much we can cut and remain effective, I need to better balance context bloat"*.
- Operator, 2026-10-25, selection *"B"*: during the drydock each stage is measured cheaply; the full flight runs once at restoration. Recorded as an insight and as a closure-contract amendment on GHI #1252.
- Operator, 2026-10-25, selection *"A"*: the contractor stops and waits on every structural question; which losses a stage may accept is one.

## The protocol, per cut stage

The baseline is the tag `control-plane-baseline-2026-10-16`.

1. **Size.** Each touched surface's bytes before and after, read from `gz validate --instructions-files-budget`.
2. **Meaning retention.** The retention map of every landing in the stage, and a read of each rule and skill cut by the method of `docs/evals/compression-sweep-2026-09-24.md`: every binding condition graded BROADENED, WEAKENED, DROPPED or MOVED, with counts.
3. **Instruction eval.** `gz readiness evaluate` before and after; every positive control still passes.
4. **Ruling.** Each binding loss goes to the operator, who accepts it, restores it, or moves it. The contractor stops here and waits.
5. **Record.** `docs/evals/control-plane-cut-<stage>-<date>.md` with steps 1 to 4, and one passage-log row. A stage with no report is not accepted.

Steps 1 to 3 run in seconds and ring no alarm, so they run with the alarms off.

## Restoration (RO-1's punch-list line)

The flight runs once, when the cleanup contractor turns the alarms back on: a fresh session flies one work package on the cut surfaces, scored on `gz check` green, `gz arb red --commit` driven, the `Task:` trailer and the passage-log row present without being asked, and every guard that fired recorded. The result closes the per-stage report series with a one-table summary of what each stage cost and what it lost. It is one sample, and the report says so.

## Contractor acts

1. Record the baseline: `gz readiness evaluate` and the budget read at `control-plane-baseline-2026-10-16`, written to `docs/evals/control-plane-cut-baseline-2026-10-16.md`.
2. Apply the protocol to each RO-7 stage as RO-7 lands it.

## Closure

RO-1 closes when the baseline report exists, every RO-7 stage has its report, and its punch-list line (the restoration flight) is cleared.
