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
| `--obpi` | string | — | Optional parent OBPI ID |
| `--semver` | string | `0.1.0` | Semantic version |
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

1. Creates an ADR document from template
2. Computes and writes a deterministic `## Decomposition Scorecard`
3. Seeds `## Checklist` count from `Final Target OBPI Count`
4. Records ADR creation in the ledger

---

## Example

```bash
# Basic usage
gz plan login-impl

# With options
gz plan login-impl --semver 0.2.0 --lane heavy --title "Login Implementation" \
  --score-interface 2 --split-surface-boundary --split-state-anchor

# Dry run
gz plan login-impl --dry-run
```

---

## Output

```
Created ADR: design/adr/ADR-0.1.0.md
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
