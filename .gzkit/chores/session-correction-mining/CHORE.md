# CHORE: session-correction-mining — Ground-Truth Correction Mining

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `session-correction-mining`

---

## Overview

Periodically mine the Claude Code session transcripts under
`~/.claude/projects/<project>/` for operator-correction patterns — user
messages bearing corrective markers that follow an assistant turn — and emit
structured proposal records when a pattern recurs across >= 3 distinct
sessions (ADR-0.0.70 Decision §2). The proposals are candidates for the
advisory-scorecard Promotable→Mechanical ladder: each recurring correction is
a static-check-in-waiting (Buetow, Beyond Coding Podcast 2026-06-10:
"data-mine your session logs ... turn that into a static check").

This is the third sensor feeding the promotion ladder — eval-feedback-cluster
mines ledger events, arb-pattern-extraction mines ARB receipts, this chore
mines the un-instrumented ground truth that compliance-dependent
self-reporting (Behavior Rule 11) cannot reach.

## Policy and Guardrails

- **Lane:** Lite — read-only over transcripts; unit-tier only, no network
- **Read-only** everywhere except this chore's `proofs/` directory
  (ADR-0.0.70 Boundary Invariant 2)
- **PII:** proposals quote at most one line, email addresses scrubbed; the
  operator-PII rule binds every record
- **Candidates only:** nothing auto-promotes; review routes through the
  advisory scorecard (ADR-0.0.70 Boundary Invariant 4)
- **Idempotent** by content hash over (cluster_key, sorted session ids) —
  re-runs over unchanged transcripts add nothing
- **Threshold:** recurrence >= 3 distinct sessions (default; `--threshold`)
- **Cadence:** triage drumbeat (campaign § Cadence) — run alongside
  `ghi-triage`; an untriaged proposals pile is the named pre-mortem decay
  mode (ADR-0.0.70 § Negative 3)

## Workflow

### 1. Preview (read-only)

```bash
uv run python -m gzkit.insights.correction_mining --dry-run
```

### 2. Write proposal records

```bash
uv run python -m gzkit.insights.correction_mining
```

### 3. Review proposals

```bash
ls .gzkit/chores/session-correction-mining/proofs/
```

Proposals are JSON files `proposal-<id>.json` with schema: `proposal_id`,
`cluster_key`, `marker`, `recurrence_count`, `session_ids`, `quote`
(scrubbed, <=1 line), `mined_at`, `proposed_action`.

### 3a. Read the run telemetry when a run finds nothing (GHI #614)

A zero-proposal run is not self-explanatory: a stale `CORRECTIVE_MARKERS`
lexicon that no longer matches how the operator phrases corrections reports
`0 cluster(s)` exactly like a healthy run in which nothing recurred. Every run
therefore reports what it scanned, and a **write** run appends one counts-only
line to `proofs/run-log.jsonl` (gitignored; counts and config only, never
operator text, per ADR-0.0.70 Boundary Invariant 2):

```bash
tail -n 1 .gzkit/chores/session-correction-mining/proofs/run-log.jsonl
```

```json
{"ts": "...", "threshold": 3, "transcripts_scanned": 206,
 "sessions_with_corrections": 8, "corrections_matched": 9,
 "clusters_total": 9, "proposals_emitted": 0}
```

Read it as follows:

| Signal | Reading |
|--------|---------|
| `corrections_matched` > 0, `proposals_emitted` == 0 | Healthy null — the lexicon works; nothing recurred across `threshold` distinct sessions |
| `corrections_matched` == 0 across consecutive runs | **Suspect lexicon decay** — markers no longer match operator phrasing; refine `CORRECTIVE_MARKERS` (itself a candidate this chore mines) |
| `transcripts_scanned` == 0 | Wrong transcripts directory, not a mining result |

`--dry-run` reports the same counts on stdout but writes **nothing**, including
no run log — REQ-0.0.70-02-08 fences it read-only.

### 4. Route accepted candidates

Accepted candidates enter the advisory scorecard
(`docs/governance/advisory-rules-audit.md`) as Promotable rows, then promote
to mechanical checks per the promotion discipline.

### 5. Validate layout

```bash
uv run gz validate --chores-layout
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest tests/chores/test_session_correction_mining.py -q` | 0 |
| exitCodeEquals | `uv run gz validate --chores-layout` | 0 |

## Evidence Commands

```bash
ls .gzkit/chores/session-correction-mining/proofs/
```
