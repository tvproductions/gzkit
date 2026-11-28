# gz handoff resume

Resume the newest handoff for an ADR with staleness (ADR-0.0.65).

---

## Overview

`gz handoff resume` is a read-only projection over `.gzkit/handoffs/`. It selects
the newest handoff for the given ADR, classifies its staleness (`Fresh`,
`Slightly-Stale`, `Stale`, `Very-Stale`), reports whether it requires human
verification, and extracts **every** authored next step from the handoff body. It
never writes anything.

Each step also carries the live state of the governance references it cites
(GHI #696). A cited GHI is resolved through `gh` and reported as `live` (open),
`settled` (closed), or `unknown` (unresolvable — `gh` absent, unauthenticated, or
offline). A step citing a `settled` reference is marked **CITES SETTLED**, because
relaying such a step unexamined is how a closed GHI got re-adjudicated three
sessions running. The flag reports the citation, not a verdict: a step may name a
closed GHI as a *precondition* (the work is done — the step is void) or as
*provenance* ("the fix that landed in #696" — the step still stands), and no
available signal distinguishes them. Confirm which before relaying.

`unknown` never collapses into `live` — a check that could not run is reported as
not run.

ADR and OBPI references are extracted and displayed but resolve to `unknown`:
their only repo-local index (`adr-status.md`) is a **Layer-3 derived view**, which
`docs/governance/state-doctrine.md` forbids reading as truth.

The report also separates **decisions** by who made them and lists rulings carried
forward as **settled** (GHI #696). An `[operator-ruled]` decision renders under
`AUTHORITY`; an `[agent-chose]` decision renders as re-arguable; an unmarked one
renders as `unattributed` and is never promoted or demoted. Settled rulings are
closed questions that are still relevant — do not re-open them.

A handoff advises; it does not authorize. The reported steps are advised
actions for the operator to ratify — resuming is not a Gate-5 attestation.

The lineage includes up to 20 unique documents, selecting the nearest ancestors
breadth-first and listing discovered ancestors before their descendants. Shared
ancestors appear once; the selected handoff is last. Cyclic references terminate
deterministically, though a cycle cannot have an ancestor-before-descendant order.
`chain_truncated` is true only when additional references remain unvisited after
the limit. A complete lineage of exactly 20 documents is not truncated. Unvisited
references have not been checked for file existence. CLI output names this limit;
SessionStart qualifies the ancestor count with “at least” only when truncated.

---

## Usage

```
gz handoff resume [--adr ADR] [--json]
```

### Options

| Option | Description |
|--------|-------------|
| `--adr ADR` | ADR id to resume the newest handoff for. Omit to resume the newest handoff overall — the only way to reach a handoff with no parent ADR (GHI #709). |
| `--json` | Emit the machine-readable `ResumeResult`. |

---

## Position and picture

The human report leads with two blocks, so the operator reads where things stand
before what to do next (operator, 2026-11-28: *"build it now so every resume shows
the position - this should cut down on vibe coding."*):

1. **The position, computed from the record** (`gzkit.mx.position`). Each fact
   names where it was read: whether the vessel is out of service and since when
   (`.gzkit/mx.json`); open and blocking discrepancy lines in the ledger and in the
   open contract's § List of discrepancies; the contract's last passage-log entry;
   and how many commits since the handoff name a repair order. A fact that cannot
   be read says so, with its cause. The states of the repair orders are not
   computed, because they live only in prose.
2. **The picture**, the handoff author's tactical, operational and strategic
   levels, in that order (see `gz handoff create` § The picture). It is Layer-1
   narrative, so its claims are verified like any other. A handoff written before
   the picture existed says it has none.

Observed in this repository on 2026-11-28, during the drydock:

```
position (computed from the record):
  Out of service since: 2026-10-20 (38 days), at the drydock level
    from .gzkit/mx.json opened_at and level
  Ledger discrepancy lines: 0 blocking, 0 open
    from .gzkit/ledger.jsonl, discrepancy_recorded and discrepancy_cleared
  Contract discrepancy lines: 16 blocking, 69 open
    from docs/governance/harbor-pilotage-candidate-2026-10-15.md § List of
discrepancies, lines recorded before RP-12 O9
  Passage log, last entry: 2026-11-19
    from docs/governance/harbor-pilotage-candidate-2026-10-15.md § Passage log
  Commits since this handoff: 0 of 12 name a repair order or the drydock
    from git log --since=2026-11-28T09:20:52Z, subjects matching RP-n, RO-n or
drydock
picture (the handoff's author): none; this handoff predates the picture
```

In a project with no hangar open, after a handoff carrying a picture:

```
position (computed from the record):
  Out of service: no (the hangar marker reads absent)
    from .gzkit/mx.json, through gzkit.mx.marker.condition
picture (the handoff's author), Layer 1, so verify its claims:
  Tactical:
    Landed the section flags; the tests pass.
  Operational:
    The adapter work is done; review is next.
  Strategic:
    Handoffs carry continuity for 1.0.
```

The `--json` form carries the picture as `picture` and the handoff's `timestamp`;
the computed position is a property of the tree, not of the document, so it is in
the human report only.

---

## Example

```bash
uv run gz handoff resume --adr ADR-0.0.65
```

Observed output (before 2026-11-28, so without the position and picture blocks):

```
resume — .gzkit/handoffs/20260724T114926Z-ghi-tier-3closed-3deferred.md
  staleness: Fresh
  requires human verification: False
  next steps (4):
    1. Resume the degrading tier from .gzkit/cache/triage/rank.json in rank order: #696 ..., then #580 ..., then #614 ...
       refs: GHI 696: live · GHI 580: live · GHI 614: live
    2. VERIFY reproduction before fixing each item; bodies self-heal and mis-estimate.
    3. #607 (ranked 4, degrading) is GOVERNANCE-PARKED: ... Surface before touching code.
       refs: GHI 607: live
    4. This is a RESUME: present these steps and obtain explicit operator authorization via gz handoff authorize before executing any of them.
```

A step whose citation is closed renders with the `CITES SETTLED` marker and a
trailing count line, and attributed decisions plus carried settled rulings follow:

```
    1. CITES SETTLED — Rule on GHI #693 (cli audit presence-vs-truth).
       refs: GHI 693: settled
  1 step(s) cite a settled reference — confirm whether it is a precondition (step is void) or context (step still stands).
  decisions (1):
    agent-chose:
      - Nothing settled this session.
  settled — do NOT re-open (1):
    - Do NOT promote sensitivity into GATE5_INVARIANTS.
```

Machine-readable form:

```bash
uv run gz handoff resume --adr ADR-0.0.65 --json
```

`steps` is the stored source; `next_steps` and `first_next_step` remain as
derived projections so existing consumers are unbroken.

```json
{
  "path": ".gzkit/handoffs/20260724T114926Z-ghi-tier-3closed-3deferred.md",
  "staleness": "Fresh",
  "requires_human_verification": false,
  "steps": [
    {
      "text": "VERIFY reproduction before fixing each item; bodies self-heal and mis-estimate.",
      "references": [],
      "cites_settled": false
    },
    {
      "text": "#607 (ranked 4, degrading) is GOVERNANCE-PARKED: ... Surface before touching code.",
      "references": [
        { "kind": "GHI", "identifier": "607", "state": "live" }
      ],
      "cites_settled": false
    }
  ],
  "chain": [
    ".gzkit/handoffs/20260724T114926Z-ghi-tier-3closed-3deferred.md"
  ],
  "next_steps": [
    "VERIFY reproduction before fixing each item; bodies self-heal and mis-estimate.",
    "#607 (ranked 4, degrading) is GOVERNANCE-PARKED: ... Surface before touching code."
  ],
  "first_next_step": "VERIFY reproduction before fixing each item; bodies self-heal and mis-estimate."
}
```

---

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Newest handoff resolved and reported. |
| 1 | User error — no handoff exists for the requested ADR. |
