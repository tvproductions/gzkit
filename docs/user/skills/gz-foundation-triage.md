# /gz-foundation-triage

Rank the in-flight foundation backlog by priority.

---

## Purpose

Runs the bundled `scripts/triage.py` to gather every Draft/Proposed
foundation ADR with its governance-signal counts (insights references,
GHI mentions, invariant mentions). The agent then reads each candidate's
`§ Intent` and `§ Decision`, classifies severity (`urgent`,
`next-quarter`, `latent`), and flags any port/adapter reclassification
candidates. The script renders the deterministic ranked deliverable.

The skill is **diagnosis only** and **ephemeral**: it MUST NOT mutate any
foundation ADR, ledger entry, or registry. The output is a recommended
work order — promotion remains an operator decision.

## When to Use

Reach for `/gz-foundation-triage` when deciding which foundation ADR to
pull next from the in-flight backlog. Foundation IDs are nominal
identifiers (ADR-0.0.57) — they carry no work-order semantics, so the
triage skill is the canonical signal for which foundation to work on
first. Useful at planning checkpoints, when surveying open foundations
before a patch window, or when the next foundation to pull is
ambiguous.

## What to Expect

The skill follows the three-step pattern shared with `/ghi-triage`:

1. **Mechanical pre-pass** — the bundled script emits one JSON record
   per in-flight foundation with signal counts inline.
2. **Cognitive pass** — the agent reads each candidate's Intent +
   Decision sections, composes a rank-input JSON with `{id, severity}`
   entries (plus any `{id, reclassify: "foundation"}` annotations for
   pool ADRs whose scope authors a port-shape invariant).
3. **Deterministic rendering** — the script renders the markdown
   deliverable from the rank-input JSON.

```text
/gz-foundation-triage
```

## Output

A markdown deliverable: one numbered row per ranked foundation, each row
in the form `N. [severity] ADR-X.Y.Z: title`. Reclassification
candidates (if any) render in a separate section beneath.

## Related

- ADR-0.0.57 — foundation-ADR nominal-ID semantics and priority triage
- [`/ghi-triage`](ghi-triage.md) — sibling pattern in the
  `governance-triage` bounded context
