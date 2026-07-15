# gz handoff archive

Move handoffs older than a threshold into `.gzkit/handoffs/archive/` (ADR-0.0.65).

---

## Overview

`gz handoff archive` is a governed **move-not-delete** retention verb over the
canonical handoff store `.gzkit/handoffs/`. The store is append-only by design
and grows monotonically (GHI #585); this verb relocates handoffs older than
`--older-than` into the `.gzkit/handoffs/archive/` subdirectory so operators can
declutter without ever losing the audit trail — archiving **moves** a handoff,
it never deletes one.

Three mechanical guards protect the store; an eligible handoff is one that
passes all three:

| Guard | Rule |
|-------|------|
| **lock-coupling** | A handoff referenced by an `obpi_lock_released` event's `handoff_path` is **SKIPPED** — these are non-deletable audit artifacts (ADR-0.0.41 / token-block discipline). |
| **chain-integrity** | A handoff involved in any `continues_from:` chain — in **either** direction (a referrer that points, or a target that is pointed at) — is **SKIPPED**. The whole chain stays canonical, so resume-chain resolution never breaks and nothing is orphaned. |
| **migration-floor** | Relocation is an atomic **no-clobber** move (`os.link` + unlink): a same-name file already in `archive/` is **never** overwritten. The counted total (canonical + archive) is preserved, so the migration baseline floor is never dropped. |

Two further conservative skips: a handoff with no parseable frontmatter
timestamp (an audit trail that cannot be aged is never moved), and a handoff
whose name already exists in `archive/` (reported under `skipped_conflict`, in
both `--dry-run` and the real run — never overwritten).

> **Concurrency.** `gz handoff archive` assumes exclusive access to the handoff
> store — it is an operator-invoked maintenance command, not a concurrently-run
> service. Relocation is atomic no-clobber, so it never overwrites an existing
> archived handoff; but it does not serialize against a *second* `gz` process
> writing `.gzkit/handoffs/` at the same time. Run it when no other handoff
> mutation is in flight (the normal single-operator case).

---

## Usage

```
gz handoff archive --older-than DURATION [--dry-run] [--json]
```

### Options

| Option | Description |
|--------|-------------|
| `--older-than DURATION` | Age threshold, e.g. `30d`. Handoffs older than this are eligible. Required. |
| `--dry-run` | Report the would-move set and skipped groups without moving anything. |
| `--json` | Emit the machine-readable plan/result payload. |

---

## Example

Preview what would move — no filesystem mutation:

```bash
uv run gz handoff archive --older-than 30d --dry-run
```

Observed output:

```
would move: 24
  .gzkit/handoffs/20260312T101836Z-obpi-06-completed-next-closeout.md
  .gzkit/handoffs/20260321T000000Z-obpi-03-completed-next-obpis.md
  ...
SKIPPED (locked): 1
  .gzkit/handoffs/20260715T100727Z-OBPI-0.0.65-03-gz-handoff-cli-verb-complete.md
SKIPPED (chained): 2
  .gzkit/handoffs/20260610T070018Z-0.0.69-01-implemented-operator-runs-ceremony.md
  ...
```

Move the eligible set (move-not-delete):

```bash
uv run gz handoff archive --older-than 30d
```

Machine-readable form:

```bash
uv run gz handoff archive --older-than 30d --dry-run --json
```

```json
{
  "dry_run": true,
  "skipped_locked": [],
  "skipped_chained": [],
  "skipped_recent": [],
  "skipped_undatable": [],
  "would_move": [
    ".gzkit/handoffs/20260312T101836Z-obpi-06-completed-next-closeout.md"
  ]
}
```

A non-dry run replaces `would_move` with `moved` — the canonical paths that were
relocated into `archive/`.

---

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Plan computed (dry-run) or eligible handoffs moved. |
| 1 | Invalid `--older-than` value. |
