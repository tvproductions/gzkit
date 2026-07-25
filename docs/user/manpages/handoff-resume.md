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

## Example

```bash
uv run gz handoff resume --adr ADR-0.0.65
```

Observed output:

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
