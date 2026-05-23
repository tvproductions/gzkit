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
| `--kind` | `pool` \| `foundation` \| `feature` | — (**required**) | ADR taxonomy: `foundation` requires `--semver 0.0.x`; foundation IDs are allocated nominally (next-free-integer, not sequential — gap-filling when IDs have been retired); `feature` requires non-`0.0.x` semver; `pool` writes a flat backlog ADR with no `kind:`/`semver:` frontmatter. |
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

1. Validates `--kind` / `--semver` compatibility **before** any file or ledger write.
2. Creates an ADR document from the taxonomy-appropriate template.
3. Routes output by kind:
   - `foundation` → `design/adr/foundation/<id>/<id>.md` (per-ADR folder)
   - `feature` → `design/adr/pre-release/<id>/<id>.md` (per-ADR folder)
   - `pool` → `design/adr/pool/ADR-pool.<slug>.md` (flat)
4. For `foundation`/`feature`, computes and writes a deterministic `## Decomposition Scorecard`, seeds `## Checklist`, and records ADR creation in the ledger. Pool ADRs are backlog stubs and are only registered after promotion via `gz adr promote`.
5. For `foundation` kind specifically, scaffolds a `## Why foundation tier?` section between `## Persona` and `## Intent`, pre-populated with two author prompts: the invariance-test answer and the port-vs-adapter framing (ADR-0.0.35 § Decision item #6). Feature- and pool-kind ADRs do not scaffold this section. See the [convention docs](../concepts/foundation-feature-invariance-test.md#why-foundation-tier-the-convention).

---

## Example

```bash
# Foundation ADR (0.0.x infrastructure)
gz plan create identity-surfaces --kind foundation --semver 0.0.20 --lane heavy

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

## Output

```
Created ADR: design/adr/foundation/ADR-0.0.20/ADR-0.0.20.md
Created ADR: design/adr/pre-release/ADR-0.2.0/ADR-0.2.0.md
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
