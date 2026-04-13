# Pool Triage

- **Version:** 0.1.0
- **Lane:** Lite
- **Slug:** `pool-triage`
- **Parent ADR:** `ADR-pool.pool-management`

## Scope Boundary (read first)

This chore is a **near-term implementation stopgap** subordinate to
`docs/design/adr/pool/ADR-pool.pool-management.md` § 8 "Near-Term Implementation: `pool-triage` Chore". The chore surfaces drift signals for operator triage — it is **read-only** and takes **no automated actions**. Its entire lifetime is bounded by `ADR-pool.pool-management`'s promotion cycle. When the parent ADR promotes and ships the full `gz pool rank` / `gz pool triage` / `gz pool override` CLI surface, this chore is either retired or absorbed per the parent ADR's promotion-outcome clause.

The chore is a **gzkit-internal maintenance item** (targets gzkit's own pool, runs in gzkit's own chore suite). It is not a framework deliverable or a template for downstream projects. Downstream projects that adopt gzkit may author their own triage chores using gzkit's chore framework, but this specific chore is not packaged for inheritance.

## Overview

gzkit's pool (`docs/design/adr/pool/`) holds ~58 pool ADRs capturing architectural intent awaiting promotion. Without periodic triage, the pool accumulates drift: stale items no one will promote, superseded items that were never archived, items whose dependencies have since completed (and are now promotion-ready but nobody noticed), and duplicate-scope items that quietly drift apart.

The failure mode: operator focus iterates on active ADRs, the pool accumulates silently, and promotion opportunities or archival candidates stay invisible until someone runs a manual audit. This chore surfaces those four drift signals on demand so the between-ADR maintenance window can act on them.

## Heuristics (the four drift signals)

Each heuristic is derivable from frontmatter, file-system mtime, ledger events, and pool-internal `Dependencies` sections. No new data model, no computed priority ranking, no cluster boundary proposals — those are deferred to the parent ADR.

| # | Signal | Detection |
|---|--------|-----------|
| 1 | **Stale** | Pool ADRs with no git-tracked update in >6 months (`git log -1 --format=%ct -- <path>`) |
| 2 | **Unarchived-superseded** | Pool ADRs with `status: Superseded` in frontmatter that still sit in `docs/design/adr/pool/` instead of `docs/design/adr/pool/archive/` |
| 3 | **Newly-unblocked** | Pool ADRs whose `Dependencies` section references ADRs that are now `Completed` in the ledger (`gz adr report` for completion state, ledger `artifact_edited` events for frontmatter status) |
| 4 | **Duplicate-scope candidates** | Pool ADRs whose titles, keywords, or path references overlap with other pool ADRs (simple keyword-overlap heuristic; not the full cluster-identification surface from the parent ADR) |

## Workflow

### 1. Scan pool directory

```bash
ls docs/design/adr/pool/ADR-pool.*.md | wc -l
```

Establish the population. Capture count in proofs.

### 2. Detect stale items

```bash
for f in docs/design/adr/pool/ADR-pool.*.md; do
    last_modified=$(git log -1 --format=%ct -- "$f" 2>/dev/null || echo 0)
    now=$(date +%s)
    age_days=$(( (now - last_modified) / 86400 ))
    if [ "$age_days" -gt 180 ]; then
        echo "STALE ($age_days days): $f"
    fi
done
```

### 3. Detect unarchived-superseded items

```bash
rg -l '^status: Superseded' docs/design/adr/pool/ADR-pool.*.md
```

Every match is a candidate: the file is in `pool/` but the frontmatter says it should be archived.

### 4. Detect newly-unblocked items

Read each pool ADR's `## Dependencies` section (or equivalent). For every referenced ADR slug, check whether that ADR is now `Completed` via `uv run gz adr report --json` (or the equivalent state surface). A pool ADR whose dependencies are all completed is promotion-ready.

### 5. Detect duplicate-scope candidates

Compute a simple token-overlap score between every pair of pool ADRs (titles + first-line descriptions). Flag pairs with >0.4 Jaccard similarity. **This heuristic is deliberately coarse** — the parent ADR's cluster-identification is where the precise work lives.

### 6. Surface results

Output a structured drift report to stdout and to `proofs/pool-triage-report-YYYY-MM-DD.md` with one section per heuristic. No file mutations to the pool itself — the operator reads the report and decides whether to act.

## Policy

- **Read-only.** The chore never writes to `docs/design/adr/pool/`, `.gzkit/ledger.jsonl`, or any governance artifact.
- **No automated archival.** Unarchived-superseded items are flagged, not moved. The operator moves them via `git mv` during triage.
- **No automated promotion.** Newly-unblocked items are flagged, not promoted. Promotion requires human judgment and the full `gz adr promote` ceremony.
- **No ranking.** The four heuristics are unranked findings, not prioritized. Priority ranking belongs to the parent ADR's `gz pool rank` surface.
- **Heuristic coarseness is intentional.** The duplicate-scope detector uses simple token overlap because the precise cluster-identification work is deferred to the parent ADR. The chore's job is surfacing, not semantic analysis.

## Acceptance Criteria

| # | Criterion | Command |
|---|-----------|---------|
| 1 | All tests pass | `uv run -m unittest -q` |
| 2 | Pool directory exists | `test -d docs/design/adr/pool` |
| 3 | Pool archive directory exists | `test -d docs/design/adr/pool/archive` |

## Evidence Commands

```bash
uv run -m unittest -q
ls docs/design/adr/pool/ADR-pool.*.md | wc -l
rg -l '^status: Superseded' docs/design/adr/pool/ADR-pool.*.md
```

## Retirement Condition

This chore retires (or gets absorbed) when `ADR-pool.pool-management` promotes and ships `gz pool rank` / `gz pool triage` / `gz pool override`. The decision — retire vs absorb — belongs to the parent ADR's promotion review. See `ADR-pool.pool-management.md` § 8 "Promotion outcome — retire-or-absorb decision" for the governing clause.
