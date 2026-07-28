# gz airlock

Operator surface over the airlock entry/exit membrane (ADR-0.33.0).

---

## Overview

`gz airlock` is the operator surface over the airlock — the entry/exit membrane
extracted from the OBPI pipeline's proven Stage-1 (pre-flight) / Stage-5 (exit)
geometry. It reasons about the **seams** a sortie touches (a seam is both a
BODY — a contiguous region of similarity, the declared Allowed Paths — and a
BOUNDARY — the push/pull edges) so the model need not hold the whole project
resident across sorties.

It is **diagnostic-only for now**: a NO-GO prints a refusal naming the
un-accounted seam and its provenance, but the verb still exits 0.

**This is a staged posture, not the declared contract.** The call sites log a
NO-GO rather than raising `SystemExit(3)` because production reach for an OBPI
id yields an empty seam-map, so a fail-closed gate would be vacuous or arbitrary
— parent ADR § Calibration frontier, operator-attested 2026-07-10, which names
calibration "a named successor increment". The declared end state **blocks**:
Boundary Invariant #4, *"an un-accounted seam makes GO structurally
unreachable."* Parent ADR § Consequences Negative #5 governs the *shape* of a
refusal — it must name the seam, its provenance, and a one-command re-sense, and
the captain override must be logged and revocable — never whether a refusal
blocks.

The airlock **never writes L1
canon** (Boundary Invariant #1): every encounter is logged to the L2 ledger
(`airlock_in` / `airlock_out` events); it only proposes governed, attested
amendments.

The two verbs:

| Verb | Purpose |
|------|---------|
| [`gz airlock in`](airlock-in.md) | Airlock-IN preflight for a target OBPI: DECLARE → PING (`gz ontology reach`) → RECONCILE → acknowledge-and-decide gate |
| [`gz airlock out`](airlock-out.md) | Airlock-OUT exit drift-diff (push-minus-pull) for a target OBPI: findings → recommendations → decision menu → log to L2 |

The airlock's gate is **acknowledge-and-decide** (proceed | pause | hold |
revert), a different sort of operator input from Gate-5 completion attestation
(Boundary Invariant #3) — keeping the two distinct preserves the force of the
sacrosanct completion word.

---

## Example

```bash
uv run gz airlock in --target OBPI-0.33.0-01 --dry-run
uv run gz airlock out --target OBPI-0.33.0-01 --dry-run
```
