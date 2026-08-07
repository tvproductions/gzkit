# failure-class-index

Index the authored `## Class of failure` statements across the GHI corpus and
surface **recurrence chains** — families of defects whose own authors declared
them instances of a prior class.

Every GHI filed through `/ghi-author` carries that section, so the corpus is a
recurrence dataset that already exists. Measured 2026-08-07 over the 333 GHIs
closed since 2026-05-09: **288 (87%)** carry the section, **71 of those (25%)**
declare themselves a recurrence, forming **15 chains of depth ≥ 3** with a
deepest chain of **12**. Nothing read it — GHI #554 could say *"5th instance in
4 weeks"* only because a human happened to remember.

A read-only stdlib+Pydantic indexer parses each statement, detects authored
recurrence phrasing, resolves citation edges into chains, and emits a report plus
run telemetry to `.gzkit/chores/failure-class-index/proofs/`. Output is evidence
only — nothing auto-routes.

## Quick Start

```bash
gh issue list --state closed --limit 800 --search 'closed:>=2026-05-09' \
  --json number,title,body > "${TMPDIR:-/tmp}/ghi-snapshot.json"

uv run python -m gzkit.insights.failure_classes \
  --snapshot "${TMPDIR:-/tmp}/ghi-snapshot.json" --dry-run
```

Drop `--dry-run` to write the report and run telemetry to `proofs/`. Keep the
snapshot **outside** the repo — it is a regenerable adapter input, 1.4 MB of
third-party issue text, not a proof.

```bash
uv run -m unittest tests/chores/test_failure_class_index.py -q
```

## Why a chain matters

A depth-3 chain is a family, not three incidents. Closing the newest instance
leaves the family open — which is how `#279 → #305 → #344 → #468 → #494 → #505`
reached six members, each closed correctly on its own scope. The index makes the
sixth visible before a seventh is authored.

Read `CHORE.md` for the workflow, guardrails, and acceptance criteria.
