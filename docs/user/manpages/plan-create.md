# gz plan create

Create a new ADR scaffold with a deterministic decomposition scorecard.

---

## Usage

```bash
gz plan create <name> --kind {feature,pool} [OPTIONS]
```

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Descriptive kebab-case slug; the id becomes `ADR-<semver>-<name>` (pool: `ADR-pool.<name>`). A full `ADR-<semver>-<slug>` id is used as given. For a non-pool kind a bare semver (`0.2.0`) or a bare `ADR-<semver>` without a slug is refused, exit 1 (GHI #494). |

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
| `--baseline-selected` | integer | lower bound of the computed range | Selected baseline count; a value outside the computed range fails (exit 1) |
| `--dry-run` | flag | — | Show actions without writing |

---

## What It Does

1. Refuses, exit 1 and before any file or ledger write: a missing `--kind`; `--kind foundation` where the kind is closed (see [Closed kind: `foundation`](#closed-kind-foundation)); `--kind feature` with a `0.0.x` `--semver`; a bare-semver or slugless `ADR-<semver>` `name` for a non-pool kind.
2. `feature`: renders the ADR template (`src/gzkit/templates/adr.md`) with status `Draft`, a deterministic `## Decomposition Scorecard` and a `## Checklist` seeded to the scorecard's final OBPI count, and writes `<paths.adrs>/pre-release/<id>/<id>.md` (per-ADR folder).
3. `feature`: appends an `adr_created` ledger event, skipped with a warning when the id already has one. The ADR file is written first, so when this step fails the file stays on disk: exit 3 if the directory name is not a canonical `ADR-<semver>-<slug>` id, exit 2 if the ledger append fails or the id is absent from the graph afterwards. Each message names `gz register-adrs --all` as the recovery.
4. `pool`: renders `src/gzkit/templates/adr_pool.md` (no scorecard, checklist, `kind:` or `semver:`) to `<paths.adrs>/pool/ADR-pool.<name>.md` and appends **no** ledger event. [`gz register-adrs`](register-adrs.md) books pool ADRs. `gz adr promote` requires a `## Target Scope` section, which the pool template does not carry, so author one before promoting.
5. `--dry-run` applies step 1, prints the path it would write and, for a non-pool kind, the `adr_created` event it would append, then exits 0 without writing.

It creates no OBPI briefs; `gz specify` does, one per checklist item.

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

The path printed is absolute:

```
Created ADR: <project>/docs/design/adr/pre-release/ADR-0.2.0-login-impl/ADR-0.2.0-login-impl.md
Created pool ADR: <project>/docs/design/adr/pool/ADR-pool.exotic-idea.md
```

---

## Decomposition Scorecard — Worked Example

The scorecard determines how many OBPIs (task briefs) the ADR should have.
Each dimension is scored 0 (none), 1 (simple), or 2 (complex):

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Data state | 1 | One persisted index |
| Logic | 2 | Predicate DSL parsing + evaluation |
| Interface | 1 | ReadRepo protocol definition |
| Observability | 0 | Not needed yet |
| Lineage | 0 | No upstream/downstream dependencies |
| **Total** | **4** | |

**Reading the total:** `baseline_range_for_total` in `src/gzkit/core/scoring.py`
maps the dimension total to a baseline range, the table in
[OBPI Decomposition Matrix](../../governance/GovZero/obpi-decomposition-matrix.md)
§ Step 2. This total falls in the band that yields a baseline of 3.
`--baseline-selected` chooses inside a range that spans more than one count
and defaults to its lower bound. Each mandatory split flag
(`--split-surface-boundary` and the rest) adds one OBPI, and the sum is the
number of checklist items seeded.

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

- **Frontmatter**: `id`, `status: Draft`, `kind`, `semver`, `lane`, `parent`, `date`
- **Decomposition Scorecard**: dimension scores, baseline range/selection, mandatory splits, final OBPI target
- **Checklist**: one placeholder `OBPI-<semver>-NN` item per targeted OBPI
- **Attestation Block**: lifecycle sign-off tracking
- Persona, Decision, Consequences, Fidelity Assertions, Q&A Transcript, Evidence, Alternatives Considered and Forcing Functions sections carrying `_[Author: …]_` prompts

---

## Workflow

1. Preview with `gz plan create <name> --kind feature --semver X.Y.Z --dry-run`
2. Adjust score/split inputs until target decomposition is right-sized, then create the ADR
3. Create OBPIs with `gz specify <slug> --parent ADR-<X.Y.Z>-<slug> --item <N>`
4. Check lifecycle with `gz status` / `gz adr status`

---

## See also

- [ADR-0.0.17 — ADR Taxonomy (Mechanical)](../../design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md) — the mechanical contract this command implements (`kind:` frontmatter, `--kind` flag, kind/semver binding).
- [ADR-0.0.18 — ADR Taxonomy (Doctrine)](../../design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md) — operator-facing guidance on *when to choose which* kind (PRD → ADR derivation, pool curation, epic grouping, worked examples).
- `AGENTS.md` § Gate Covenant — the kind axis (`feature`, `pool`; `foundation` closed) and `gz validate --taxonomy`.
