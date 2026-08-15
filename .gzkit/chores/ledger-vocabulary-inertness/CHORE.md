# CHORE: Ledger Vocabulary Inertness

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `ledger-vocabulary-inertness`

---

## Overview

Audit-plus-disclosure pass over the **ledger's vocabulary**. Two dimensions:

1. **Never-fired types (enforced).** Event types declared in
   `src/gzkit/schemas/ledger.json` that have never appeared in
   `.gzkit/ledger.jsonl`. Held to a shrink-only disclosure baseline.
2. **Paired-event ratios (reported, never judged).** For event types that open
   and close a state, the ratio of one half to the other.

The sibling chore `control-surface-validator-reachability` (Pass D) asks whether
a *validator* runs. This one asks the same question of the *ledger*: a declared
event type that nothing emits is vocabulary with no producer — it reads as a
modelled fact and records nothing.

## Background

Surfaced 2026-08-15 alongside Pass D. Two clusters made the case:

- The **MX Maintenance Hangar** ships a CLI (`gz mx`), a skill, and a hook
  (`mx-awareness.py`), and has recorded **zero sessions** — both halves of its
  session pair are declared and neither has ever fired.
- The **graph edge vocabulary** — `blocks`, `blocked_by`, `validates`,
  `discovered_from` — is the traceability spine, and has never been written to.

Neither is visible to any existing gate. `gz validate --event-schemas` checks
that every *emitted* type has a schema entry; nothing checks the converse.

## Policy and Guardrails

- **Lane:** Lite — audit-only; this chore never edits the schema, the ledger, or
  any producer.
- **The ledger is never modified.** `.gzkit/ledger.jsonl` is append-only and
  agent-writable only through `gz` verbs (`AGENTS.md` § Never #2). This chore
  reads it and nothing else.
- **Growth is disclosed, not forbidden.** Declaring a type before wiring its
  producer is legitimate work. What is forbidden is absorbing it silently: a new
  never-fired type must be added to the baseline deliberately, with a reason.
  Same posture as `data/uncalled_gate_grandfather.json` — an entry records an
  absence, it does not justify one.
- **Ratios are reported and NOT interpreted, and this is binding.** The
  2026-08-15 audit read `obpi_parked`/`obpi_unparked` as an operator
  "abandonment channel" and named a `gz obpi park` verb **that does not exist**.
  The counts were right; the story was invented. Parking is emitted by
  `src/gzkit/foundation/sunset_migrate.py` when an ADR is demoted to pool, and
  that module states in its own words that parking *"is reversible on
  re-promotion and is not a negation of completed work."* A ratio is evidence
  for an operator ruling, never a verdict this chore may reach.
- **A pair is a claim about semantics.** `_PAIRS` membership asserts that the
  first event opens a state the second closes, about the same subject. Two events
  that merely co-occur are not a pair, and adding one would manufacture a ratio
  that means nothing.

## Workflow

### 1. Report both dimensions

```bash
uv run python src/gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py --report
```

Record the output in `proofs/vocabulary-inertness.md`.

### 2. Dispose of each never-fired type

Each one owes exactly one of:

| Disposition | When |
|---|---|
| **Wire the producer** | the type models something real that is happening and simply is not recorded |
| **Retire the declaration** | the modelled thing does not happen, or happens under another type |
| **Disclose** | the producer is genuinely planned; add it to the baseline with a reason and raise `baseline_count` in `data/waiver_ratchet_registry.json` in the same commit |

Disclosure is the honest holding state, never the default. A type that has been
disclosed across several runs is a retirement candidate, not a fixture.

### 3. Read each lopsided pair to its producer

For any pair whose halves diverge, **find what emits each half before saying
what it means.** The ratio names a question; the producer answers it. Route the
answer to the operator — this chore does not rule.

### 4. Enforcement

```bash
uv run python src/gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py
```

Exit 3 when an undisclosed never-fired type appears.

## Acceptance Criteria

- `check_ledger_inertness.py --self-test` exits 0
- `check_ledger_inertness.py` exits 0 (no undisclosed never-fired type)
- Proof artifacts postdate the surfaces they audit

## Cadence

Run when the ledger vocabulary changes shape — a new event type in the schema, a
new producer, or a retired one — and at minimum before each release. The
disclosure baseline covers the between-runs case: a newly declared type with no
producer fails the chore whenever it next runs.

## Related

- `control-surface-validator-reachability` (Pass D) — the same question asked of validators
- `gz validate --event-schemas` — every *emitted* type has a schema entry (the converse check)
- `gz validate --event-handlers` — every ledger event type is claimed by a graph handler
- `data/waiver_ratchet_registry.json` — where this chore's baseline is registered
  (ADR-0.0.73 Boundary Invariant #8)
- `docs/governance/state-doctrine.md` — the ledger is Layer 2; derived views are never source-of-truth
