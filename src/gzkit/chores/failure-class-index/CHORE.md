# CHORE: failure-class-index — GHI Recurrence Chains

**Slug:** `failure-class-index`
**Lane:** lite
**Module:** `src/gzkit/insights/failure_classes.py`
**Tests:** `tests/chores/test_failure_class_index.py`

## Overview

Every GHI authored through `/ghi-author` carries a `## Class of failure` section —
the author's own root-cause diagnosis, written at filing time and mandatory in the
skill's body template. That makes the GHI corpus a **recurrence dataset that
already exists**.

Measured 2026-08-07 over the 333 GHIs closed since 2026-05-09:

| Measure | Value |
|---|---|
| Carrying a `## Class of failure` section | **288 of 333 (87%)** |
| Declaring themselves a recurrence of a named prior class | **71 of 288 (25%)** |
| Chains of depth >= 3 | **15** |
| Deepest chain | **12** |

Nothing read it. GHI #554 could say *"5th instance in 4 weeks"* only because a
human happened to remember; #732's *"(4th miss)"* was caught the same way. This
chore makes the detection mechanical, so a chain surfaces **before** the next
instance is authored rather than after.

This is the highest-compliance authored channel in the repo — 87%, against
`@advances` at 0, frontmatter `tasks:` at 7 of 534 pre-stamp, and commit `Task:`
trailers at ~15% pre-stamp. It is compliant because `/ghi-author` makes the
section part of filing rather than a convention to remember.

## Policy and Guardrails

- **Read-only against the corpus.** The chore never edits a GHI, never files one,
  and never closes one. Its output is a report plus run telemetry under `proofs/`.
- **The core takes records as a parameter.** `failure_classes.py` never invokes
  `gh` (`.gzkit/rules/hexagonal-architecture.md` rules 1 and 4); the snapshot step
  below is the adapter. Every function is exercisable with no network.
- **A link requires an authored declaration.** Only a class statement whose own
  prose declares a recurrence ("same class as", "5th instance", "recurrence of")
  contributes a chain edge. A passing mention of another GHI does not merge two
  families — the author's claim is the link.
- **Fails soft.** An absent or malformed snapshot yields an empty corpus and a
  zero-finding report, never a crash inside a maintenance run.
- **The report advises; it does not rule.** A chain is evidence that a family
  recurs. Whether that family earns a campaign box, a rule, or a validator scope
  is an operator decision.

## Workflow

### 1. Snapshot the corpus (the adapter step)

```bash
gh issue list --state closed --limit 800 --search 'closed:>=YYYY-MM-DD' \
  --json number,title,body > "${TMPDIR:-/tmp}/ghi-snapshot.json"
```

Widen with `--state all` to include open GHIs when triaging what to pull next.

**Write the snapshot outside the repo.** It is a regenerable adapter input, not a
proof: the 2026-08-07 snapshot of 333 closed GHIs was **1.4 MB** of verbatim issue
bodies. Committing it bloats the tree, and GHI bodies are third-party text that has
never been scanned against the operator-PII prohibition
(`AGENTS.md` § Local Agent Rules). Only the emitted report and run telemetry belong
under `proofs/`.

### 2. Preview (read-only)

```bash
uv run python -m gzkit.insights.failure_classes \
  --snapshot .gzkit/chores/failure-class-index/proofs/snapshot.json --dry-run
```

Prints the scan counts and every chain at or above `--min-depth` (default 3),
writing nothing.

### 3. Write the report and run telemetry

```bash
uv run python -m gzkit.insights.failure_classes \
  --snapshot .gzkit/chores/failure-class-index/proofs/snapshot.json --stamp YYYY-MM-DD
```

### 4. Read the counts even when a run finds nothing

The scan line always reports records read, statements indexed, and the declaring
count — so *"read 333, indexed 288, 0 chains"* is legible as a real result and
distinguishable from *"read an empty snapshot"* (the negative-signal shape
GHI #614 established for `session-correction-mining`).

### 5. Route what the report surfaces

A chain of depth >= 3 whose members are still producing instances is a **family**,
not a set of incidents. Route it to the owning surface — a campaign box, a rule, or
a validator scope. Record the routing; do not re-derive the chain next quarter.

## Acceptance Criteria

- [ ] `uv run -m unittest tests.chores.test_failure_class_index` exits 0.
- [ ] A run over a snapshot containing a known chain reports that chain at its
      authored depth — the chore's own subject, not merely that it executed.
      Reference case: `#505` cites `#279 -> #305 -> #344`, so a snapshot holding
      the `279/305/344/468/494/505` set must report **depth 6**.
- [ ] A statement declaring no recurrence contributes no edge, and a passing
      citation does not merge two chains.
- [ ] An absent or malformed snapshot yields a zero-finding report at exit 0.
- [ ] The report names every chain member and marks which members declared the
      recurrence themselves.

## Evidence Commands

```bash
uv run -m unittest tests.chores.test_failure_class_index
uv run python -m gzkit.insights.failure_classes --snapshot <path> --dry-run
uv run gz chores doctor
```
