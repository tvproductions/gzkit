# gz frontmatter reconcile

Rewrite drifted ADR/OBPI frontmatter (`id`/`parent`/`lane`/`status`) to match the ledger (ledger-wins). Emits a schema-validated reconciliation receipt per run.

## Usage

```bash
gz frontmatter reconcile [--dry-run] [--json]
```

## Description

Consumes the OBPI-01 frontmatter validator as its drift source and the OBPI-05 `STATUS_VOCAB_MAPPING` as a pre-flight guard. When drift is detected, the command rewrites the four governed fields in-place; ungoverned keys (`tags:`, `related:`, etc.) are preserved byte-identically. Pool ADRs (identified by `ADR-pool.*` id or path under `docs/design/adr/pool/`) are skipped and listed in the receipt. An existing frontmatter `status:` term not in the canonical vocabulary STOPs the run with a BLOCKER — no files are mutated.

Ledger state is pinned at run-start (sha256 of `.gzkit/ledger.jsonl`) and the validator sees that snapshot only — a mid-run ledger mutation cannot leak into the receipt.

A receipt is emitted under `artifacts/receipts/frontmatter-coherence/<YYYYMMDDTHHMMSSZ>.json` every run, including `--dry-run`. The receipt validates against `data/schemas/frontmatter_coherence_receipt.schema.json` before being written.

## Options

| Flag | Effect |
|------|--------|
| `--dry-run` | Compute and emit the receipt; do NOT mutate any ADR/OBPI file. |
| `--json` | Additionally emit the receipt JSON to stdout for machine consumption. |

## Examples

```bash
# Preview what would change
uv run gz frontmatter reconcile --dry-run

# Apply reconciliation
uv run gz frontmatter reconcile

# Machine-readable receipt to stdout
uv run gz frontmatter reconcile --json
```

## Exit Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Success — no drift, or drift resolved | N/A |
| 1 | User/config error — not inside a gzkit project | Run from a project root with `.gzkit.json` present |
| 2 | System/IO error — ledger unreadable, write failure | Check disk and `.gzkit/ledger.jsonl` integrity |
| 3 | Policy breach — unmapped `status:` term encountered | Correct the frontmatter or extend `STATUS_VOCAB_MAPPING` |

## Related

- `gz validate --frontmatter` — detect drift without rewriting
- `gz chores run frontmatter-ledger-coherence` — run the dry-run acceptance criterion
- `ops/chores/frontmatter-ledger-coherence/CHORE.md` — operator workflow for the chore
- ADR-0.0.16 — frontmatter-ledger coherence guard
