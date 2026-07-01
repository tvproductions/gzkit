---
id: ADR-pool.ghi-triage-closeout
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: null
---

# ADR-pool.ghi-triage-closeout: GitHub Issue Triage and Closeout Integration

## Status

Pool

## Date

2026-03-29

## Parent PRD

PRD-GZKIT-1.0.0

## Context

GitHub Issues (GHIs) are used to track defects, enhancements, and attestation records.
Currently there is no `gz` command to view, triage, or associate GHIs with ADRs. Issue
review during ADR closeout relies on manual `gh issue list --search` invocations, making
it easy to leave orphaned issues open after work is complete.

## Decision

Add a `gz ghi` subcommand group that wraps `gh` CLI calls and correlates issues against ADR identifiers for triage and closeout workflows. Per the three-layer tool/skill/runbook alignment rule (`tool-skill-runbook-alignment.md`), the CLI verbs ship alongside operator-facing skills (`gz-ghi-fix`, `gz-ghi-triage`) and runbook entries so every invariant (tool-wielded-by-skill, skill-matches-runbook-moment, output-form-honored) is satisfied on landing. Scope is merged from the original tool-layer proposal (2026-03-29) and the skill-layer/runbook complements surfaced during the 2026-04-19 `/insights` session.

## Target Scope

Scope decomposes into five OBPIs. Each bullet below becomes one OBPI slug at promotion; narrative detail for each lives in § Detailed Specification.

- gz ghi cli verbs
- gz ghi fix skill
- gz ghi triage skill
- runbook and manpage docs
- gz patch release integration

## Detailed Specification

### gz ghi cli verbs

New subcommand group wrapping `gh` with gzkit integration:

- `gz ghi list` — open issues, triage-friendly Rich table (label / age / linked ADR)
- `gz ghi check ADR-X.Y.Z` — issues referencing the named ADR (used by closeout gate)
- `gz ghi check --all` — issues by ADR association, orphans highlighted
- `gz ghi view <number>` — single-issue detail with linked ADR context
- `gz ghi close <number> --comment` — close with attestation-style comment, emit ledger event
- `gz ghi link <number> ADR-X.Y.Z` — register an issue-to-ADR link in the artifact graph

Exit codes per the standard 4-code map (0 success, 1 user error, 2 system error, 3 policy breach e.g. orphan detected under `--fail-on-orphan`). `--json` mode renders machine-readable output; default is Rich-tabular per CLI doctrine.

### gz ghi fix skill

Per-issue end-to-end skill wielding the new CLI verbs plus the TASK/TDD surface:

1. Read the GHI with `gz ghi view <number>` (or fall back to `gh issue view <number>`)
2. Apply `defect-fix-routing.md` thresholds — route direct-fix vs. OBPI ceremony mechanically, not by intuition
3. For direct-fix: locate governing REQ(s), start a TASK, TDD red-green-refactor, commit with `Task:` trailer referencing `GHI #<number>`, complete TASK
4. For OBPI-ceremony route: open OBPI brief and redirect to `gz obpi pipeline`
5. Root-cause-before-symptom discipline built into the skill prose (anti-rationalization table)
6. Close the issue with `gz ghi close --comment` citing the commit SHA or brief ID

Inherits skill-intent scope invariant from the 2026-04-19 amendment to `ADR-pool.skill-behavioral-hardening`. `MODE: IMPLEMENT` declared at entry; no action beyond the declared fix scope without operator authorization.

### gz ghi triage skill

Batch-mode skill wielding `gz ghi list` + classification + optional dispatch:

1. List open issues, classify each as TRIVIAL / MEDIUM / COMPLEX by diff-size/scope heuristics
2. Produce a prioritized punch list with routing recommendations
3. For TRIVIAL items, optionally dispatch `gz-ghi-fix` per issue (subagent fan-out or sequential)
4. For MEDIUM items, surface to operator for batch approval before dispatch
5. For COMPLEX items, draft ADR-skeleton or OBPI-candidate surface for operator review
6. Emit a run summary referencing all downstream commits and closures

Consumes insights-report framing (section "Bundle GHI fixes into release-driven batches"); aligns with the observed pattern of batched GHI resolution (one recent session closed 14 issues in one pass).

### runbook and manpage docs

- New section in `docs/user/runbook.md` covering the GHI-lifecycle operator moments (triage entry, per-issue fix, closeout gate, orphan detection)
- Manpages under `docs/user/manpages/` for each `gz ghi` verb
- Update `docs/user/commands/` reference
- Behave scenarios tagged with REQ IDs covering the triage → fix → close flow
- Three-layer invariant check passes: every new CLI verb wielded by a skill, every skill's `gz_command` matches the runbook-prescribed moment, every skill Output Contract honored by default verb output

### gz patch release integration

- `gz-patch-release` skill consumes `gz ghi list --since <tag>` to discover landed GHIs for the release narrative
- `gz ghi check --release <tag>` surfaces any unclosed issues associated with commits in the release window
- Release ceremony closes associated GHIs via `gz ghi close` as part of the guarded sync step, emitting ledger events linked to the release event

## Use Cases (preserved from original)

1. **Triage** — operator reviews open issues with labels, age, and linked ADR context.
2. **Closeout gate** — before attestation, `gz ghi check ADR-X.Y.Z` surfaces associated issues so none are silently abandoned.
3. **Orphan detection** — `gz ghi check --all` highlights issues not linked to any ADR.
4. **Per-issue fix (2026-04-19 merge)** — operator invokes `/gz-ghi-fix <number>` and the skill routes direct-fix vs. OBPI-ceremony mechanically, applies TDD discipline, commits with `Task:` trailer, and closes the issue.
5. **Batch sweep (2026-04-19 merge)** — operator invokes `/gz-ghi-triage` and receives a prioritized, routed punch list with optional fan-out dispatch.

## Lane

Heavy — new CLI subcommand group, two new skills, runbook additions, BDD scenarios, manpages, and integration with `gz-patch-release`. Meets Heavy-lane triggers per `cli.md` (new subcommand group) and `skill-surface-sync.md` (new skills require version discipline + mirror sync).

## Consequences

- Closeout ceremony gains a reproducible issue-association check.
- Triage becomes a first-class governance surface rather than ad-hoc `gh` invocations.
- Per-issue fixes gain end-to-end governance: routing decision, TDD cycle, TASK trailer, closure all flow through one skill with receipts.
- Batch GHI sweeps become a repeatable skill invocation, compressing the 14-GHI-in-one-session pattern observed in 2026-04-19 insights.
- Requires `gh` CLI authenticated and available on PATH.
- Added scope gains: skill-layer and runbook layer invariants are satisfied on landing (per three-layer alignment rule), avoiding the post-hoc drift that GHI #141/#149/#150 caught for earlier skills.

## Amendments

### 2026-04-19 — Merged scope (skill + runbook layers) + Target Scope section added

**Motivation.** The 2026-04-19 `/insights` session surfaced `/ghi-fix` as a recurring skill-layer need (15+ sessions running near-identical GHI-triage-to-close patterns); the existing pool scope covered only the tool-layer CLI verbs. Per the three-layer tool/skill/runbook alignment rule, a new CLI verb group without its wielding skills and runbook entries would violate Invariants 1 and 2 on landing. This amendment merges the skill-layer and runbook-layer scope into the pool so promotion produces an invariant-clean ADR.

**What the amendment preserves.** Original Context, Decision (extended, not replaced), Proposed Surface (now detailed under § CLI verbs), Use Cases (preserved + 2 new entries labeled `2026-04-19 merge`), Lane (unchanged — still Heavy), Consequences (preserved + additions).

**What the amendment adds.** New `## Target Scope` section with 5 terse bullets (required for promotion). New `## Detailed Specification` H2 with per-OBPI detail. 2 new Use Cases for the skill-layer flows. 4 new Consequences for the merged scope. Two new skills named (`gz-ghi-fix`, `gz-ghi-triage`). Runbook and manpage coverage added as OBPI-04. `gz-patch-release` integration added as OBPI-05.

**What it does NOT do.** No pre-decision on whether `gz-ghi-fix` should fan-out via subagents or run sequentially (promotion-time decision). No pre-decision on whether `gz-ghi-triage` batch output should auto-dispatch or require operator approval per item (operator-preference choice). No pre-resolution of the routing-threshold tuning (inherits `defect-fix-routing.md` as-is).
