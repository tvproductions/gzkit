# gz ontology

Read-only sonar over the corpus-domain ontology projection (ADR-0.32.0).

---

## Overview

`gz ontology` images the actual shape of governance lineage from the
corpus-domain projection — a Tier-B derived view rebuilt from L1 canon and the
L2 ledger. It is strictly **read-only**: it never writes graph state (Boundary
Invariant #2). Its only filesystem write is the regenerable
`.gzkit/ontology/last_sweep.json` diff-baseline cache.

The five verbs:

| Verb | Purpose |
|------|---------|
| [`gz ontology sense`](ontology-sense.md) | Sweep the current structural shape + surface STRUCTURAL seams |
| [`gz ontology trace`](ontology-trace.md) | Walk one node's vertical lineage + lateral proof with edge provenance |
| [`gz ontology resense`](ontology-resense.md) | Diff the current shape versus the last sweep (the airlock re-sense gate) |
| [`gz ontology seams`](ontology-seams.md) | Fast contacts-only STRUCTURAL seam check |
| [`gz ontology reach`](ontology-reach.md) | Return one node's downstream blast-radius (transitive dependents) |

`sense`, `seams`, and `resense` always exit 0 — the sonar never gates
(Boundary Invariant #2, derived-never-authority). `trace` and `reach` exit 1
on an unknown node id.

`sense` images the **STRUCTURAL** shape only and never claims semantic
completeness (Boundary Invariant #3). Semantic-seam recall is deferred to
RECALL / Phase-4 (L3-advisory).

---

## Example

```bash
uv run gz ontology sense
uv run gz ontology trace ADR-0.31.0-obpi-state-machine
uv run gz ontology resense
```
