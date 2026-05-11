# CHORE: Control Surface — Rule-Pair Conflict Matrix (Pass A)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `control-surface-rule-conflicts`

---

## Overview

Audit-only pass. Produce a pairwise conflict matrix across every file in `.gzkit/rules/` and `AGENTS.md`, identifying rule pairs that can disagree on a specific case. Output is a matrix artifact that later drives mechanical-promotion GHIs — this chore does NOT fix the conflicts, only names them.

Background: ADR-0.0.16 through 0.0.18 surfaced acute control-surface instability that traced back to rules written compatible-sounding in isolation but decomposing into contradictory mechanical behaviors in combination (e.g. `tests.md` § "Tests assert semantics" vs `tool-skill-runbook-alignment.md` § Invariant 3 requiring pin-to-string assertions on table markers). Solo maintainer with no peer review means contradictions only surface when an agent hits one in the path of work — this chore makes them surface in a batch instead.

## Policy and Guardrails

- **Lane:** Lite — audit-only; zero file edits outside `.gzkit/chores/control-surface-rule-conflicts/proofs/`
- **Read-only on rules.** This chore does NOT modify any `.gzkit/rules/` file, any skill, or any source.
- **Scope:** every `.md` under `.gzkit/rules/` plus `AGENTS.md` and `CLAUDE.md`. Vendor mirrors (`.claude/rules/`, `.github/instructions/`) are derivatives and are NOT audited here — they should match canonical per sync discipline.
- **No speculation.** A conflict row requires a concrete worked example (a specific case where rule X says one thing and rule Y says the opposite). No "these could maybe conflict" entries.

## Workflow

### 1. Enumerate the rule surface

List every file in scope and its canonical section headings. Record in `proofs/rule-inventory.md`.

### 2. Pairwise walk

For each unordered pair (rule_a, rule_b), ask: can these two files disagree on a concrete case? For each yes, produce one row in `proofs/conflict-matrix.md` with:

- Rule A + section
- Rule B + section
- Worked example (specific scenario that triggers the disagreement)
- Which rule "wins" today (mechanical enforcement, if any), or "unresolved"
- Suggested resolution: reconcile in one rule / split scopes / promote mechanical check

### 3. Severity classification

Each row: `blocking` (an agent hits this monthly+), `episodic` (hit during a specific ADR class), `theoretical` (no observed hit in GHI trail). Cross-reference each blocking/episodic row to the GHI(s) it explains.

### 4. Summary + recommendation list

Write `proofs/summary.md` with counts by severity, top 5 blocking rows, and a prioritized follow-up list (each entry sized for a direct-fix GHI or a mechanical-promotion GHI).

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `test -f .gzkit/chores/control-surface-rule-conflicts/proofs/rule-inventory.md` | 0 |
| exitCodeEquals | `test -f .gzkit/chores/control-surface-rule-conflicts/proofs/conflict-matrix.md` | 0 |
| exitCodeEquals | `test -f .gzkit/chores/control-surface-rule-conflicts/proofs/summary.md` | 0 |
| exitCodeEquals | `uv run python src/gzkit/chores/control-surface-rule-conflicts/check_evidence.py --self-test` | 0 |
| exitCodeEquals | `uv run python src/gzkit/chores/control-surface-rule-conflicts/check_evidence.py --offline` | 0 |

The last two predicates enforce `ADR-pool.control-surface-rule-pair-conflict-audit` § Audit-row schema (GHI #448). `--self-test` validates the parser against embedded fixtures (deterministic, no I/O). `--offline` validates `proofs/conflict-matrix.md` directly: header carries the seven required columns (Rule A, Rule B, Worked example, Evidence, Mechanical winner, Suggested resolution, Severity); each row's Evidence cell carries at least one reference resolving via `git log -1 <SHA>`, `grep <id> .gzkit/insights/agent-insights.jsonl`, or a well-formed `GHI #N` (best-effort `gh issue view` when authenticated, shape-only fallback otherwise to honor chores-lite no-network doctrine).

## Evidence Commands

```bash
ls .gzkit/rules/ > .gzkit/chores/control-surface-rule-conflicts/proofs/rule-surface-listing.txt
wc -l .gzkit/rules/*.md AGENTS.md CLAUDE.md > .gzkit/chores/control-surface-rule-conflicts/proofs/rule-line-counts.txt
```

---
