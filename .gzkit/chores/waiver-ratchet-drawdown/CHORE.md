# CHORE: Waiver-Ratchet Drawdown

**Lane:** Lite
**Slug:** `waiver-ratchet-drawdown`

---

## Overview

Report how far each **shrink-ratchet** surface in `data/waiver_ratchet_registry.json` has been drawn down.

`gz validate --waiver-ratchet` refuses a debt list that grows (ADR-0.0.73 Boundary Invariant #8). It cannot see a
list that never shrinks: a baseline committed at its high-water mark passes forever at that mark. This chore reads
each surface's live count against its baseline and names its state: **at zero**, **drawn down** (the baseline can
tighten to the live count), **not drawn down**, or **over baseline** (the gate is failing). Measured at landing,
2026-11-12: of 35 shrink-ratchet surfaces, 22 had never been drawn down, 7 had been and could tighten, and 6 were at
zero; 4,607 live entries against 6,707 baselined.

## Background

Commissioned as disposition row 3 of `docs/rnd/hexagonal-specification.md` (funded 2026-11-11), from Montenegro's
*"Make reducing the freeze store part of regular sprint work"* (§ 7.8). The run's advice, recorded there, scoped it to
the whole registry rather than the run's own baselines: every new baseline must register in
`data/waiver_ratchet_registry.json` when it lands (an unregistered `*_waivers` or `*_grandfather` file fails closed),
so one sweep reaches them all. Admitted on the operator's word, verbatim: *"Admit it"* (2026-11-12).

The house-style run's disposition row 4(e) commissions an owner, a close-at-zero plan and a target date for each
shrink-ratchet. Until it lands, this chore reports counts and states only; when it does, the report gains each
surface's owner and its distance from the target date.

## Policy and Guardrails

- **Lane:** Lite. Read-only: the chore reads the registry and each registered file, and writes nothing.
- **It never tightens a baseline.** Lowering `baseline_count` to the live count locks progress in, and is a change to
  a gate's data, so it is proposed per surface and landed by whoever owns the surface, never by this chore.
- **It never removes an entry.** Drawing a list down means fixing what each entry waives; that is the owning work's.
- **Counting follows the gate.** A surface's live count is the length of the collection at its `entries_path`, the
  rule `gz validate --waiver-ratchet` applies; the two never disagree on a count.
- **Closed-set locks and dated cutovers are out of scope.** Neither has a baseline to draw down.

## Workflow

### 1. Report — observe

```bash
uv run python .gzkit/chores/waiver-ratchet-drawdown/check_drawdown.py --report
```

### 2. Propose

For each surface **drawn down**, propose tightening its `baseline_count` to the live count, to its owner. For each
surface **not drawn down**, name it to its owner with its count. A surface **over baseline** is the gate's failure;
route it to `uv run gz validate --waiver-ratchet`.

### 3. Record

Write the table to `proofs/` with the date.

## Mode Contract

Read-only and advisory: **on** at the operational condition, the hangar level and the drydock level alike, since it
gates nothing and changes nothing. MEL entry: no bypass procedure is needed; its limitation is that it reports counts,
not the coverage a waived entry was providing (GHI #998); its self-test is the `--self-test` criterion, run on every
chore run.

## Acceptance

`acceptance.json`: the self-test exits 0, and the report exits 0 with every surface countable.
