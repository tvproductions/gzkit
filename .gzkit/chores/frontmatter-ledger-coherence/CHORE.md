# CHORE: Frontmatter-Ledger Reconciliation

**Version:** 2.0.0
**Lane:** Heavy
**Slug:** `frontmatter-ledger-coherence`
**ADR:** ADR-0.0.16 (OBPI-03)

---

## Operator Note (binding)

Frontmatter `id`/`parent`/`lane`/`status` are **derived state**. Hand-edits to
these fields will be **overwritten** on the next chore run. Edit the ledger via
`gz` commands instead; the reconciler rewrites frontmatter to match the ledger.

This replaces the prior read-only audit chore (v1.0.0) which instructed humans
to hand-edit. That approach was antithetical to ADR-0.0.16's ledger-wins
doctrine and is now superseded.

---

## Overview

Detect drift between ADR/OBPI YAML frontmatter and the ledger's artifact graph,
then **automatically rewrite** the drifted `id`/`parent`/`lane`/`status` fields
to match the ledger. The chore consumes OBPI-01's validator as its drift
source and OBPI-05's `STATUS_VOCAB_MAPPING` as a pre-flight safety check on
the existing `status:` term.

## Policy and Guardrails

- **Lane:** Heavy — mutating, receipt-emitting, schema-validated
- **Tool:** `gz frontmatter reconcile [--dry-run] [--json]`
- **Authority:** The ledger is the source of truth. When drift is found, the
  ledger value is correct and the frontmatter value is stale.
- **Ungoverned keys:** untouched byte-identically (tags, related, etc.)
- **Pool ADRs:** skipped (no ledger entry by design); listed in receipt.
- **Unmapped status term:** STOPs with a BLOCKER; zero files mutated.
- **Receipt location:** `artifacts/receipts/frontmatter-coherence/<YYYYMMDDTHHMMSSZ>.json`
- **Related GHIs:** #167 (umbrella), #168, #169, #170

## Workflow

### 1. Dry-run

```bash
uv run gz frontmatter reconcile --dry-run
```

Prints planned rewrites and emits a receipt with `dry_run=true`. No files
touched. Recommended before every real run.

### 2. Apply

```bash
uv run gz frontmatter reconcile
```

Rewrites frontmatter and emits a receipt with `dry_run=false`. Idempotent:
a second invocation with no intervening ledger change yields an empty
`files_rewritten` array.

### 3. Machine-readable output

```bash
uv run gz frontmatter reconcile --json
```

Emits the receipt JSON to stdout (in addition to writing it to disk).

### 4. Inspect receipts

```bash
ls -lt artifacts/receipts/frontmatter-coherence/ | head -5
```

## Acceptance Criteria

The chore passes when `gz frontmatter reconcile --dry-run` exits 0 — i.e.
there is no drift to rewrite. If drift exists, run the non-dry-run variant to
resolve, then re-run the dry-run to confirm.

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run gz frontmatter reconcile --dry-run` | 0 |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (no drift, or drift resolved) |
| 1 | User/config error (not a gzkit project) |
| 2 | System/IO error (ledger unreadable, write failure) |
| 3 | Policy breach (unmapped `status:` term — BLOCKER) |

## Evidence Commands

```bash
uv run gz frontmatter reconcile --dry-run --json > ops/chores/frontmatter-ledger-coherence/proofs/dry-run.json
```

---

**End of CHORE: Frontmatter-Ledger Reconciliation**
