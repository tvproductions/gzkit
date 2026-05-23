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

## Signal Dimensions

Priority score formula: `insights×3 + ghi_occurrence×2 + feature_unblocking×5`

| Dimension | Weight | Source |
|-----------|--------|--------|
| `insights_signal` | ×3 | Rows in `.gzkit/insights/agent-insights.jsonl` mentioning the ADR ID |
| `ghi_occurrence` | ×2 | Unique GHI numbers referenced in those rows |
| `feature_unblocking` | ×5 | Pool/feature ADRs with `depends_on` listing the foundation ID |

Higher `feature_unblocking` weight reflects the chain-blocker cost: a foundation
not landed means every pool ADR depending on it cannot be promoted.

## Ephemeral Output Property

The ranked report is **ephemeral**: it exists only in the conversation.
Nothing is written to any ADR, ledger entry, or promotion state. The skill
does not call `gz adr promote` or modify the foundation backlog. Promotion
remains a manual operator decision via `gz adr promote --kind foundation <slug>`.

Do not run foundation triage as a commit gate. Use it on-demand, before
sprint planning or when multiple Draft/Proposed foundations compete for the
next increment.

## Step 1 Output Example

Running the mechanical pre-pass against a fixture backlog with three
in-flight foundations (IDs 0.0.1, 0.0.2, 0.0.4 — gap at 0.0.3):

```bash
uv run python .gzkit/skills/gz-foundation-triage/scripts/triage.py --format json
```

```json
[
  {
    "ghi_count": 2,
    "id": "ADR-0.0.1",
    "insight_count": 2,
    "invariant_mentions": 0,
    "path": "docs/design/adr/foundation/ADR-0.0.1-foundation-fixture-one/ADR-0.0.1-foundation-fixture-one.md",
    "signal_total": 4,
    "status": "Draft",
    "title": "Fixture Foundation One"
  },
  {
    "ghi_count": 0,
    "id": "ADR-0.0.2",
    "insight_count": 1,
    "invariant_mentions": 0,
    "path": "docs/design/adr/foundation/ADR-0.0.2-foundation-fixture-two/ADR-0.0.2-foundation-fixture-two.md",
    "signal_total": 1,
    "status": "Draft",
    "title": "Fixture Foundation Two"
  },
  {
    "ghi_count": 0,
    "id": "ADR-0.0.4",
    "insight_count": 0,
    "invariant_mentions": 0,
    "path": "docs/design/adr/foundation/ADR-0.0.4-foundation-fixture-four/ADR-0.0.4-foundation-fixture-four.md",
    "signal_total": 0,
    "status": "Proposed",
    "title": "Fixture Foundation Four"
  }
]
```

ADR-0.0.1 scores highest (`insight_count=2`, `ghi_count=2`). The cognitive
pass reads each candidate's `§ Intent` and `§ Decision`, then classifies
severity and emits the rank-input JSON for Step 3.

## Related

- ADR-0.0.57 — foundation-ADR nominal-ID semantics and priority triage
- [`/ghi-triage`](ghi-triage.md) — sibling pattern in the
  `governance-triage` bounded context
- [`gz plan create`](../manpages/plan-create.md) — nominal allocator for
  foundation IDs; see "Nominal Allocator — Gap-Filling Example"
- `docs/user/runbook.md` § Foundation Triage — operator workflow
- `docs/governance/governance_runbook.md` § Foundation-Triage Planning Workflow
