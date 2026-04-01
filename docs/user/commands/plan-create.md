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
