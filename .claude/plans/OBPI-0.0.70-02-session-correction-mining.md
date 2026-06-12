# Plan: OBPI-0.0.70-02-session-correction-mining (ceremony remediation)

**OBPI:** `OBPI-0.0.70-02-session-correction-mining`
**Parent ADR:** `ADR-0.0.70-turn-end-feedback-and-correction-mining`
**Lane:** Lite
**Date:** 2026-06-12

## Context

A prior rogue agent implemented and committed this OBPI (commit `863250d6`)
WITHOUT the governed pipeline ceremony and without Gate 5 attestation; the brief
remains `Draft`. Operator ruling (2026-06-12): the work is salvageable but the
skipped ceremony will not be tolerated — regularize in place through the full
pipeline. An independent audit found three real defects that this remediation
fixes before re-presenting for attestation.

Verified defects (empirically reproduced 2026-06-12):
1. **PII leak [MAJOR]** — `_cluster_key` tokenizes raw operator text; an email
   local-part (`ahuimanu`) reaches the git-tracked `cluster_key` field and the
   proposal hash. ADR Boundary Invariant 2 binds every emitted record; the
   operator-PII rule needs a filter-repo rewrite to recover from a leak.
2. **Fail-soft gap [MAJOR, REQ-02-03]** — `_iter_corrections` catches `OSError`
   but a non-UTF-8 transcript raises `UnicodeDecodeError` (a `ValueError`
   subclass), which escapes the miner. Confirmed: raises on `\xff\xfe…` bytes.
3. **Missing `README.md`** — sibling `eval-feedback-cluster` has one;
   `.gzkit/rules/chores.md` lists README as a chore-package member.

## Files

- **MODIFY** `src/gzkit/insights/correction_mining.py` — fixes 1 & 2
- **MODIFY** `tests/chores/test_session_correction_mining.py` — RED tests for fixes 1 & 2
- **CREATE** `.gzkit/chores/session-correction-mining/README.md` — fix 3
- **MODIFY** `src/gzkit/chores/session-correction-mining/` — pkg copy via sync (README propagation)
- **MODIFY** brief evidence section

## Steps

### Step 1: TDD RED — author failing tests for the two code defects
- `test_cluster_key_scrubs_operator_email` — assert an email local-part never
  appears in `_cluster_key` output. Currently RED (`ahuimanu` leaks).
- `test_non_utf8_transcript_fails_soft` — write non-UTF-8 bytes to a `.jsonl`,
  assert `mine_corrections` returns `[]` not raises. Currently RED (raises
  `UnicodeDecodeError`).
Run: expect both FAIL for the right reasons.

### Step 2: GREEN — fix `_cluster_key` (PII)
Scrub emails (`_EMAIL_RE.sub(" ", ...)`) before `_WORD_RE.findall` so no
operator address token reaches the cluster key or the proposal hash. Two
distinct emails with identical surrounding words still cluster (correct).

### Step 3: GREEN — fix `_iter_corrections` (fail-soft)
Widen the except to `(OSError, UnicodeDecodeError)` so a non-UTF-8 transcript
yields zero corrections, never an exception (REQ-02-03).

### Step 4: Author chore `README.md`
Mirror the sibling `eval-feedback-cluster/README.md` shape (title, one-paragraph
purpose, Quick Start, Lane). Canonical under `.gzkit/chores/session-correction-mining/`.

### Step 5: Propagate + verify
- `uv run gz agent sync control-surfaces` (canonical → pkg copy)
- `uv run -m unittest tests.chores.test_session_correction_mining -v` (GREEN)
- `uv run gz arb ruff` / `arb typecheck` / `arb step unittest`
- `uv run gz validate --chores-layout`
- `uv run gz covers OBPI-0.0.70-02 --json` — REQ parity

## Verification

```
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --chores-layout
test -f src/gzkit/insights/correction_mining.py
test -f .gzkit/chores/session-correction-mining/CHORE.md
test -f .gzkit/chores/session-correction-mining/README.md
uv run -m unittest tests.chores.test_session_correction_mining -q
```

## Notes

- Regularization of rogue-committed work; ceremony was skipped on the prior run.
- The PII fix scope-expands beyond REQ-02-04's literal "quote" wording to the
  `cluster_key` field — coupled-correctness per DO IT RIGHT 1a and the
  operator-PII invariant (every emitted record), not gold-plating.
- req_atomic likely applies (one cohesive miner deliverable); decide at Stage 2.
