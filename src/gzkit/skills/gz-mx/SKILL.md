---
name: gz-mx
persona: main-session
description: >
  Enter and exit the MX Maintenance Hangar — operator's interface to gz mx.
  Use when entering the hangar to perform governance repair, checking hangar
  status mid-session, or cleanly exiting when repair is complete.
  Operator operates the skill; the skill invokes gz mx; nobody shells out.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-07-24
model: haiku
gz_command: mx
metadata:
  skill-version: "1.1.0"
---

# gz mx

## Overview

The MX Maintenance Hangar lets the operator repair governance surfaces that
the guards themselves protect. While the hangar is open, most governance
guards drop to advisory so repair work can proceed without the checked-in
surfaces blocking the repair itself. Two guards NEVER drop: `gate5_invariants`
and the PRIME DIRECTIVE (ownership — "fix what you know AND what you find").

The operator operates this skill; the skill invokes `gz mx`; nobody shells
out to `gz mx enter` or `gz mx exit` directly.

## When to Use

- **Entering the hangar** — governance repair session needs to begin; guards
  need to go advisory so you can fix the surfaces they protect
- **Checking hangar status** — confirming whether the hangar is currently
  open mid-session
- **Clean exit** — repair is complete; re-enforce all guards at full strength

## Workflow

1. **Open the hangar**
   ```bash
   uv run gz mx enter
   ```
   Creates `.gzkit/mx.json` marker. Most governance guards drop to advisory.

2. **Perform the repair**
   Work on the governance surfaces that needed fixing. Gate 5 invariants and
   the PRIME DIRECTIVE still bind — guards drop to advisory so you can repair
   governance itself, not so defects can be deferred.

3. **Close the hangar**
   ```bash
   uv run gz mx exit
   ```
   Removes `.gzkit/mx.json` marker. Every guard re-runs at full strength;
   exit is a hard gate (all guards must pass before exit succeeds).

## Example

```bash
# Enter the hangar to repair a drifted OBPI brief
uv run gz mx enter

# Perform repair work (briefs, rules, docs)
# ...

# Exit — guards re-enforce; exit fails if any guard is still red
uv run gz mx exit
```

## Repairing a ledger row

The ledger is the one governance surface hangar mode can never make writable:
`AGENTS.md` § Never #2 forbids modifying it, and that prohibition is what makes
it trustworthy. A row recorded in error is therefore repaired *forward*, and
the repair is available inside or outside the hangar.

`gz ledger correct` appends one corrective action naming the prior row by its
`(event, id, ts)` triple — the ledger has no per-row id, because `id` carries
the artifact rather than the event. `gz ledger corrections` is the census of
what is currently in force.

```bash
# Review the exact target first; nothing is written
uv run gz ledger correct \
  --subject-event pipeline_launched \
  --subject-id OBPI-0.35.0-08-remember-post-append-advisory \
  --subject-ts 2026-08-23T13:12:21.832251+00:00 \
  --disposition void --cause agent-error \
  --reason "pipeline launched without operator initiation" \
  --attestor g0 --dry-run

# What is corrected right now
uv run gz ledger corrections
```

Three dispositions: `void` (the row records something that was not true — no
reader may count it), `discharged` (the row was true and its condition has
since been resolved — it leaves the liveness reading but stays evidence), and
`reinstated` (undo a prior correction). Operator-gated: `--attestor` and
`--reason` fail closed when empty, on the same terms as `gz obpi repudiate`.

## Constraints

- Operator operates the skill; the skill invokes `gz mx`; nobody shells out
- `gate5_invariants` and the PRIME DIRECTIVE bind throughout the session
- Exit is a hard gate — do not attempt exit until all detectable defects are fixed
- See `.gzkit/rules/mx-mode.md` for the binding agent rule for hangar sessions
