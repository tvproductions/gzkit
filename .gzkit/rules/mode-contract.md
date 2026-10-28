---
id: mode-contract
paths:
  - "src/**/*.py"
  - ".claude/hooks/**"
  - ".gzkit/skills/**"
  - ".gzkit/rules/**"
  - ".gzkit/chores/**"
description: Every new control carries its two-way mode contract from the start (advisory until RO-13)
---

<!-- rule-version: 0.1.2 -->

# Mode Contract (gzkit)

> **Rule version:** `0.1.2` — the fail-safe default restored after the 0.1.1 compression (operator review, 2026-10-28); advisory until RO-13 lands its witness.

Every new control, module, skill, rule or surface carries the two-way mode contract from its first commit: operator, 2026-10-26, *"an overarching design requirement permanently and always with everything we build"*. A design without it is incomplete. Retrofitting what exists is RO-13's program.

## What a new control declares

1. **Its behavior** at the operational condition, the **hangar** level and the **drydock** level: on, advisory or off. The condition is on only when the marker is present, parses, is bound to an open `mx_session_opened` and is not exiting. Anything else is the operational condition.
2. **Its MEL entry:** level per standby level, (M) bypass procedure, (O) limitation, placard, restore condition and deadline (at the latest the exit re-run), self-test interval, accepted state.
3. **Its built-in self-test:** suitable when its latest result passed within the declared interval, otherwise inoperative under its (O) limitation.

`GATE5_INVARIANTS` is never listed. The level is applied at the place of call, never by the declaration. Until RO-13 builds the declaration shapes (decorator, Markdown MEL block, `gzkit.mx.alarms` arguments), state the contract in the design artifact's § Mode Contract.

**Advisory: no mechanical witness yet.** RO-13's shrink-only baseline of controls with no MEL entry, closed at zero, is the planned witness. Record: `docs/rnd/contractor-kit.md` § *the mode contract is a permanent design requirement for everything gzkit builds*.
