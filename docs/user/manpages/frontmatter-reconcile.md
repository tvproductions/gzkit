# gz frontmatter reconcile

Rewrite drifted ADR/OBPI frontmatter (`id`/`parent`/`lane`/`status`) to match the ledger (ledger-wins). Emits a schema-validated reconciliation receipt per run.

## Usage

```bash
gz frontmatter reconcile [--dry-run] [--json]
```

## Description

Consumes the OBPI-01 frontmatter validator as its drift source and the OBPI-05 `STATUS_VOCAB_MAPPING` as a pre-flight guard. When drift is detected, the command rewrites the four governed fields in-place; `status:` is written as the canonical frontmatter mirror term for the ledger state (for example, a ledger-withdrawn OBPI writes `Abandoned`, not raw `withdrawn`). Ungoverned keys (`tags:`, `related:`, etc.) are preserved byte-identically. Pool ADRs (identified by `ADR-pool.*` id or path under `docs/design/adr/pool/`) are skipped and listed in the receipt. An existing frontmatter `status:` term not in the canonical vocabulary STOPs the run with a BLOCKER — no files are mutated.

**Runtime Invariant Monitor (OBPI-03):** For OBPI artifacts, a runtime invariant monitor validates each status transition against the CANONICAL_TRANSITIONS declared in the OBPI state machine (ADR-0.31.0 OBPI-01). A status rewrite that would represent an invalid state machine transition (e.g., attempting to un-withdraw a terminal-state OBPI) is refused — the file is not mutated, and the refusal is recorded in the receipt as a `refused_rewrites` entry. This prevents silent frontmatter drift like GHI #348 where an operator's hand-marked terminal state would have been silently reverted by the reconciler.

Ledger state is pinned at run-start (sha256 of `.gzkit/ledger.jsonl`) and the validator sees that snapshot only — a mid-run ledger mutation cannot leak into the receipt.

A receipt is emitted under `artifacts/receipts/frontmatter-coherence/<YYYYMMDDTHHMMSSZ>.json` every run, including `--dry-run`. The receipt validates against `data/schemas/frontmatter_coherence_receipt.schema.json` before being written. If the receipt contains `refused_rewrites` entries, exit code is 0 (success — some rewrites were completed, others were refused). Refused rewrites are rendered directly in the command's human-readable output (a `refused rewrites:` count plus a `REFUSED <path> / <reason>` line per entry) in addition to the receipt JSON; a run carrying refusals is never reported as "no drift detected". Operators MUST review refused rewrites to determine whether the frontmatter intent or ledger state needs correction.

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
- `src/gzkit/chores/frontmatter-ledger-coherence/CHORE.md` — operator workflow for the chore (canonical; project overlay at `.gzkit/chores/frontmatter-ledger-coherence/`)
- ADR-0.0.16 — frontmatter-ledger coherence guard
