# Idea to ADR

You are here with an idea, a need, or a problem, and no ADR yet.

## Steps

1. **Shape it.**
   - You can state the idea → **`gz-design`**: a design dialogue, one question
     at a time, that exits into an ADR.
   - The problem is open and the outcome unknown, or outside material prompted
     it → **`gz-rnd`** (operator-invoked): defines the problem and ends in a
     disposition map naming which artifacts are warranted. Do not route a need
     the operator has already ruled through it.
2. **Book it.**
   - **`gz-adr-create`** — interview, then the ADR with one OBPI brief per
     Feature Checklist item, co-created and booked in the ledger.
   - **`gz-plan`** — `uv run gz plan create` scaffolds an ADR, or a pool entry
     with `--kind pool`, when the decision is already made.
3. **Score it.** **`gz-adr-evaluate`** rates the ADR and each OBPI; a dimension
   scoring 1 is revised before anything proceeds.
4. **Finish the briefs.** **`gz-obpi-specify`** authors any brief still thin.

## Branches

- **Direction unsure, or a score below the threshold** → **`gz-justify`**, an
  evidence-anchored walkthrough before implementation.
- **Capture for later** → a pool ADR (`gz-plan` with `--kind pool`); when it is
  scheduled, **`gz-adr-promote`** builds its package.
- **Product-level intent changed** → **`gz-prd`** first.
- **It is a small in-flight defect, not a design** → no ADR: follow
  [Defects and GHIs](defects-and-ghis.md).

## Only you can

Approve the design. Choose the kind (`feature` or `pool`). Work feature ADRs in
ascending semver order; a higher one is authored ahead of the lowest in flight
only by your explicit exception.

## Then

[OBPI delivery](obpi-delivery.md), which you initiate one OBPI at a time.
