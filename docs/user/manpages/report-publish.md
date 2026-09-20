# gz report publish

## Overview

Publish an operator-requested big-picture assessment. The command preserves the
source's exact UTF-8 bytes under `<paths.docs_root>/reports/big-picture/<id>.md`
and appends a `report_published` event to `paths.ledger`. Both paths come from
`.gzkit.json`. Publication records a model assessment, not operator endorsement,
human attestation, or an architecture decision.

## Usage

```text
gz report publish --source SOURCE --id REPORT_ID [--period PERIOD] [--evidence-cutoff EVIDENCE_CUTOFF] [--json]
```

## Options

| Option | Description |
| --- | --- |
| `--source SOURCE` | Required authored UTF-8 Markdown file; never modified. |
| `--id REPORT_ID` | Required stable identity: 1–128 lowercase ASCII letters, digits, underscores or hyphens, starting with a letter or digit. `index`, `current`, and Windows device names are reserved. |
| `--period PERIOD` | Optional reporting period description, retained in the publication event. |
| `--evidence-cutoff EVIDENCE_CUTOFF` | Optional evidence cutoff description, retained in the event. |
| `--json` | Emit the publication result as JSON. |

## Examples

```bash
uv run gz report publish --source /tmp/assessment.md --id 2026-09-19t235400z --period "Last 60 days" --evidence-cutoff "2026-09-19" --json
```

## Retention and accounting

Every published report remains in place. `index.md` lists published reports;
`current.md` is a byte-for-byte copy of the latest by ledger publication order.
These views are rebuildable. Earlier reports are not regenerated from a model.
The event carries series, path, SHA-256, period, evidence cutoff, publication
time, identity, and predecessor. The ledger is the publication log; the index
is a derived view. New assessments and corrections use new identities; explain
correction linkage in the report's evidence appendix.

The `publication.lock` sidecar coordinates concurrent writers and contains no report
history. New project scaffolding ignores it; existing projects can add
`**/reports/big-picture/publication.lock` to their `.gitignore`. Keep the report
Markdown files tracked.

An identical retry emits no duplicate event and rebuilds both views. Retrying
an older report never makes it current again. Changing bytes or metadata under
an already-published identity is refused. Previously published bytes are checked
against their ledger fingerprints before any new publication.

## Recovery

Bytes are saved before the event, and views are refreshed after it. An IO failure
may leave retained bytes without an event, or a complete publication with stale
views. Resolve the IO failure and repeat the exact command and source bytes.
Do not change the identity to work around an interrupted publication. A same-id
retry safely completes accounting or rebuilds views. A changed or missing
historical report requires restoring its exact bytes from preserved history;
publication refuses to conceal the discrepancy.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Publication and views complete, including an identical retry. |
| 1 | Invalid input, conflicting identity, or changed published content. |
| 2 | Usage or IO error; publication may be partial. See recovery above. |
