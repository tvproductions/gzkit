# gz arb archive

Move aged, uncited ARB receipts into `artifacts/receipts/archive/` (GHI #594).

---

## Overview

`gz arb archive` is a governed **move-not-delete** retention verb over the ARB
receipt store. ARB shipped a read/harvest half (`gz arb advise`, `gz arb
patterns`) and no write-lifecycle half, so the store grew without bound — 3,282
files by the time this verb landed, against the 1,875 recorded when the defect
was filed. This verb relocates aged receipts into an `archive/` subdirectory so
the harvest verbs scan a bounded working set, without ever losing evidence.

**Nothing here deletes.** There is deliberately no `purge` verb: GHI #594 records
that the destructive half *"needs an operator design conversation on retention
window, archive format, and purge authorization"*, so retention stops at
relocation until that ruling exists.

Three mechanical guards protect the store; an eligible receipt passes all three:

| Guard | Rule |
|-------|------|
| **citation-coupling** | A receipt whose id is cited **anywhere** in `.gzkit/ledger.jsonl` is **SKIPPED**. A receipt id is its filename stem (`arb-ruff-<hex>.json` ↔ `arb-ruff-<hex>`), and `AGENTS.md` § Attestation makes those ids the canonical Heavy-lane evidence — a cited receipt must stay where citations resolve. This is the ARB analogue of handoff-archive's `obpi_lock_released` coupling. |
| **ARB-owned only** | A file whose stem does not begin `arb-` is **SKIPPED**. The receipts root is shared with other emitters (`adr-taxonomy-backfill-*`, `foundation-sunset-migration-*`); this verb owns ARB's lifecycle and nothing else's. |
| **no-clobber** | Relocation is an atomic move (`os.link` + unlink): a same-name file already in `archive/` is **never** overwritten, reported under `skipped_conflict` in both `--dry-run` and the real run. |

Two further conservative skips: a receipt newer than the threshold, and a receipt
with no parseable `timestamp_utc`. Age is read from the receipt's own
`timestamp_utc` field, **never** from `mtime` — mtime is rewritten by clone,
checkout, and archive extraction, so ageing on it would silently re-date the
whole store.

The ledger is scanned as text rather than by known event shape. Receipt ids reach
it through several routes (`gz adr emit-receipt --evidence-json` payloads, OBPI
completion attestation text, ARB's own events), and enumerating those routes would
protect only the ones someone remembered.

> **Concurrency.** Like `gz handoff archive`, this is an operator-invoked
> maintenance command assuming exclusive access to the receipts root. Relocation
> is atomic no-clobber, but the plan→execute window is not serialized against a
> second `gz` process emitting receipts at the same time. Run it when no other ARB
> invocation is in flight (the normal single-operator case).

---

## Usage

```
gz arb archive [--older-than DURATION] [--dry-run] [--json]
```

### Options

| Option | Description |
|--------|-------------|
| `--older-than DURATION` | Age threshold, e.g. `30d`. Receipts older than this are eligible. Default: `30d`. Shares its grammar with `gz handoff archive`. |
| `--dry-run` | Classify and report without relocating anything. |
| `--json` | Emit the machine-readable plan/result payload. |

---

## Examples

Preview what would move — no filesystem mutation:

```bash
uv run gz arb archive --older-than 30d --dry-run
```

Observed output:

```
Receipt archive plan (dry-run)
  Root: /Users/jeff/Documents/Code/gzkit/artifacts/receipts
  Older than: 30d
  Eligible: 1538
  Skipped (cited in ledger): 951
  Skipped (newer than threshold): 776
  Skipped (undatable): 0
  Skipped (name conflict in archive/): 0
  Skipped (not ARB-emitted): 16
  Use without --dry-run to relocate.
```

The `Skipped (cited in ledger): 951` line is the guard doing its work — those
receipts are live attestation evidence and stay put regardless of age.

Machine-readable form:

```bash
uv run gz arb archive --older-than 30d --dry-run --json
```

```json
{
  "eligible": [
    "arb-ruff-aaaa1111.json"
  ],
  "skipped_cited": [],
  "skipped_recent": [
    "arb-ruff-bbbb2222.json"
  ],
  "skipped_undatable": [],
  "skipped_conflict": [],
  "skipped_foreign": []
}
```

A non-dry run returns the result payload instead, which wraps the same plan under
a `plan` key and adds `moved` — the receipt filenames relocated into `archive/`.

Relocate the eligible set:

```bash
uv run gz arb archive --older-than 30d
```

An invalid threshold fails closed rather than falling back to the default:

```bash
uv run gz arb archive --older-than bogus --dry-run
```

```
invalid --older-than value: 'bogus' (expected e.g. 30d)
```

---

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Plan computed (dry-run) or eligible receipts relocated. |
| 1 | Invalid `--older-than` value. |
| 2 | System/IO error reading or writing the receipts root. |

---

## See also

- [`arb.md`](arb.md) — the ARB middleware group
- [`arb-advise.md`](arb-advise.md), [`arb-patterns.md`](arb-patterns.md) — the harvest half this verb bounds
- [`handoff-archive.md`](handoff-archive.md) — the move-not-delete precedent (GHI #585)
- `AGENTS.md` § Attestation — why a cited receipt is non-relocatable evidence

---

## History

- **GHI #594** — ARB exposed a harvest half and no write-lifecycle half; receipts
  accumulated unbounded. This verb supplies relocation; purge is reserved for an
  operator ruling on retention window and authorization.
- **GHI #585** — the sibling defect on the handoff store, whose `gz handoff
  archive` established the move-not-delete shape this verb reuses.
