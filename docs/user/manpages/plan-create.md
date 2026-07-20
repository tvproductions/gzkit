# gz plan create

Create a new ADR scaffold with a deterministic decomposition scorecard.

---

## Usage

```bash
gz plan <name> [OPTIONS]
```

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `name` | Yes | ADR name or identifier |

---

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--kind` | `pool` \| `feature` | — (**required**) | ADR taxonomy: `feature` requires non-`0.0.x` semver; `pool` writes a flat backlog ADR with no `kind:`/`semver:` frontmatter. **`foundation` is closed to new authoring by [ADR-0.34.0](../../design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md) and is rejected here — see [Closed kind: `foundation`](#closed-kind-foundation).** It remains a valid `choices` value and a valid schema enum value so the grandfathered on-disk foundation ADRs keep validating. |
| `--obpi` | string | — | Optional parent OBPI ID |
| `--semver` | string | `0.1.0` | Semantic version (ignored for `--kind pool`) |
| `--lane` | `lite` \| `heavy` | `lite` | Governance lane |
| `--title` | string | — | ADR title |
| `--score-data-state` | `0\|1\|2` | lane default | Decomposition score: Data/State |
| `--score-logic-engine` | `0\|1\|2` | lane default | Decomposition score: Logic/Engine |
| `--score-interface` | `0\|1\|2` | lane default | Decomposition score: Interface |
| `--score-observability` | `0\|1\|2` | lane default | Decomposition score: Observability |
| `--score-lineage` | `0\|1\|2` | lane default | Decomposition score: Lineage |
| `--split-single-narrative` | flag | off | Add mandatory split for mixed narrative |
| `--split-surface-boundary` | flag | off | Add mandatory split for internal/external mixing |
| `--split-state-anchor` | flag | off | Add mandatory split for mixed state writes |
| `--split-testability-ceiling` | flag | off | Add mandatory split when scenario clusters exceed ceiling |
| `--baseline-selected` | integer | computed | Override selected baseline count within computed range |
| `--dry-run` | flag | — | Show actions without writing |

---

## What It Does

1. Rejects `--kind foundation` **before** any file or ledger write (see [Closed kind: `foundation`](#closed-kind-foundation)).
2. Validates `--kind` / `--semver` compatibility **before** any file or ledger write.
3. Creates an ADR document from the taxonomy-appropriate template.
4. Routes output by kind:
   - `feature` → `design/adr/pre-release/<id>/<id>.md` (per-ADR folder)
   - `pool` → `design/adr/pool/ADR-pool.<slug>.md` (flat)
5. For `feature`, computes and writes a deterministic `## Decomposition Scorecard`, seeds `## Checklist`, and records ADR creation in the ledger. Pool ADRs are backlog stubs and are only registered after promotion via `gz adr promote`.

---

## Example

```bash
# Feature ADR (release-carrying capability)
gz plan create login-impl --kind feature --semver 0.2.0 --lane heavy \
  --title "Login Implementation" \
  --score-interface 2 --split-surface-boundary --split-state-anchor

# Pool ADR (backlog item)
gz plan create exotic-idea --kind pool

# Dry run (validation surfaces any kind/semver mismatch)
gz plan create login-impl --kind feature --semver 0.2.0 --dry-run
```

---

## Closed kind: `foundation`

[ADR-0.34.0 (Foundation Sunset)](../../design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md)
closed the `foundation` kind to new authoring. `gz plan create --kind foundation`
is rejected at the command handler, before any file or ledger write:

```bash
$ gz plan create identity-surfaces --kind foundation --semver 0.0.20 --lane heavy
```

```
ERROR: --kind foundation was requested, but the foundation kind is closed to new
authoring by ADR-0.34.0 (Foundation Sunset). It remains a valid schema value only
for the existing grandfathered kind: foundation ADRs already on disk.
Re-run with --kind feature (release-carrying work) or --kind pool (backlog).
```

The kind is **sealed, not deleted**: `foundation` stays in the `--kind` argparse
choices and in the `kind` schema enum precisely so the grandfathered on-disk
foundation ADRs keep validating. The rejection is seated at the command handler
rather than in argparse so it can carry this recovery prose — argparse's bare
`invalid choice` cannot.

Route new work with `--kind feature` (release-carrying capability) or
`--kind pool` (backlog). Existing foundations remain readable and validatable;
use [`/gz-foundation-triage`](../skills/gz-foundation-triage.md) to rank the
in-flight ones.

---

## Output

```
Created ADR: design/adr/pre-release/ADR-0.2.0-login-impl/ADR-0.2.0-login-impl.md
Created pool ADR: design/adr/pool/ADR-pool.exotic-idea.md
```

---

## Decomposition Scorecard — Worked Example

The scorecard determines how many OBPIs (task briefs) the ADR should have.
Each dimension is scored 0 (none), 1 (simple), or 2 (complex):

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Data state | 0 | No persistent storage in this ADR |
| Logic | 2 | Predicate DSL parsing + evaluation |
| Interface | 1 | ReadRepo protocol definition |
| Observability | 0 | Not needed yet |
| Lineage | 0 | No upstream/downstream dependencies |
| **Total** | **3** | |

**Reading the total:** A total of 3 means 3-4 OBPIs are recommended.
The formula is `baseline = total` with a range of `[total, total+1]`.
Mandatory splits (flags like `--split-surface-boundary`) add +1 each.

In this example, three checklist items map naturally:

1. ReadRepo[T] protocol with get, list, filter methods
2. Predicate DSL: Eq, Gt, Lt, Gte, Lte, In\_, And, Or
3. InMemoryAdapter implementing ReadRepo[T]

If the scorecard says 3 but you can only find 2 natural items, don't force
a split. If it says 3 but you need 5, revisit the dimension scores — you
probably underscored something.

---

## ADR Template

The created ADR contains:

- **Metadata**: ID, title, version, lane, parent
- **Decomposition Scorecard**: dimension scores, baseline range/selection, mandatory splits, final OBPI target
- **Checklist**: auto-seeded count that must match scorecard target
- **Attestation Table**: lifecycle sign-off tracking

---

## Workflow

1. Create an ADR with `gz plan` (this command)
2. Adjust score/split inputs until target decomposition is right-sized
3. Create OBPIs with `gz specify --parent ADR-... --item N`
4. Check lifecycle with `gz status` / `gz adr status`
5. Attest with `gz attest`

---

## See also

- [ADR-0.0.17 — ADR Taxonomy (Mechanical)](../../design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md) — the mechanical contract this command implements (`kind:` frontmatter, `--kind` flag, kind/semver binding).
- [ADR-0.0.18 — ADR Taxonomy (Doctrine)](../../design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md) — operator-facing guidance on *when to choose which* kind (PRD → ADR derivation, pool curation, epic grouping, worked examples).
- `AGENTS.md` § Kinds (pool, foundation, feature) — the axis summary and mechanical enforcement surfaces.
