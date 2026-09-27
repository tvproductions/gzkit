# OBPI delivery

The main path. You are here when an OBPI brief exists and the operator has chosen
to work it.

## Steps

1. **Plan.** Plan the OBPI, then **`gz-plan-audit`** checks the plan against the
   ADR's intent and the brief's scope and writes the receipt the pipeline needs.
2. **`gz-obpi-pipeline`** runs five stages:
   1. *Load context* — reads the brief and the plan-audit receipt, claims the
      OBPI lock, writes the pipeline marker.
   2. *Implement* — per task, an implementer subagent, then a spec-reviewer and
      a quality-reviewer.
   3. *Verify* — the quality checks, each wrapped by **`gz-arb`** so it leaves a
      receipt.
   4. *Present evidence* — the operator's gate.
   5. *Sync* — `uv run gz obpi complete` records the attestation; the lock is
      released.
3. **Along the way:**
   - **`gz-obpi-brief-drift`** — before implementation and before completion,
     check the brief still matches the project tree.
   - **`gz-obpi-simplify`** — after implementation, review the OBPI's code for
     reuse, quality and efficiency.
   - **`gz-implement`** — Gate 2 for the parent ADR.
4. **`gz-obpi-sync`** — reconcile briefs and the ADR's table from the ledger.

## Branches

- **Already implemented** → `gz-obpi-pipeline` with `--from=verify`; **already
  verified** → `--from=ceremony`.
- **A stage aborts** → the pipeline releases the lock and writes a handoff; the
  next session resumes from it.
- **Another agent may be working nearby** → **`gz-obpi-lock`** to see or manage
  claims. The pipeline claims its own lock.
- **A defect in this OBPI's own work** → fix it inside the pipeline and record
  it in the brief; it is not a new issue.

## Only you can

Initiate the OBPI; nothing starts one on its own. Attest at Stage 4: your words,
relayed verbatim, are Gate 5 for every lane.

## Then

The next OBPI, or, when all of the ADR's OBPIs are complete,
[ADR closeout](adr-closeout.md).
