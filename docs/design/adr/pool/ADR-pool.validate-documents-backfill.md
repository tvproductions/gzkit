---
id: ADR-pool.validate-documents-backfill
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.validate-documents-backfill: Schema convention backfill for pre-convention-era ADR and OBPI artifacts

## Status

Pool

## Intent

`uv run gz validate --documents` currently exits 1 with **3536 errors across ~259 ADR artifact files**. The root cause is **schema convention additions applied retroactively to pre-convention-era artifacts with no backfill pass**. Two cohorts dominate:

- **298 occurrences** of `Missing required section: 'Decomposition Scorecard'` — ADR documents (foundation, pool, and pre-release) that were authored before the Decomposition Scorecard convention landed.
- **240+ occurrences** of `Missing required section: 'Lane' / 'Allowed Paths' / 'Denied Paths' / 'Requirements (FAIL-CLOSED)' / 'Quality Gates'` — OBPI briefs authored before the current brief schema added those sections (concentrated in `ADR-0.7.0-obpi-first-operations`, `ADR-0.38.0`, `ADR-0.39.0`, `ADR-0.40.0`, and adjacent pre-release ADRs).

This is a class of failure, not isolated instances: **every** new required section that lands in the schema accretes a new cohort of failing pre-convention-era artifacts unless the schema change is paired with a mechanical backfill pass.

The downstream cost is **silent governance signal degradation**: `gz check` and ADR closeout evidence have been misread as passing (operators sampling validator output with `tail -5` see one finding instead of 3536), which violates AGENTS.md § Architectural Boundaries #6 ("Do not let derived views silently become source-of-truth"). The validator's exit status is canonical truth; the truncated tail is a derived view that has been silently authoritative.

Discovered during ADR-0.0.35 closeout ceremony (2026-05-17); filed as GHI #480.

## Decision

This ADR is **pool** — backlog awaiting promotion. The substantive decision (whether to backfill artifacts, adjust validator scope, or both) is reserved for the promotion ceremony when this ADR is lifted to `feature` lane. Promotion criteria below.

What this pool ADR commits to *now*:

1. **The class of failure is named and homed.** GHI #480 closes `superseded` citing this ADR. The 3536-error backlog has a registered tracker in the artifact graph, not a session-memory ghost.
2. **The two cohorts are bounded.** Cohort A = ADR documents missing Decomposition Scorecard (298 instances). Cohort B = OBPI briefs missing Lane / Allowed Paths / Denied Paths / Requirements / Quality Gates (240+ instances). Promotion will produce one OBPI brief per cohort plus a third OBPI for validator scope semantics (grandfather vs. backfill policy).
3. **The validator's current behavior is preserved until promotion.** No silent suppression, no `--allow-pre-convention` flag, no schema rollback. The 3536-error count is the honest signal until decided otherwise.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | **Suppress pre-convention errors in `--documents` via authoring-date heuristic** | Layer-3 derived-view shortcut. Implicit grandfather semantics violate AGENTS.md § Architectural Boundaries #6. Cannot answer "is this artifact compliant?" without re-implementing the heuristic. |
| 2 | **Bulk-backfill every artifact mechanically with placeholder section content** | Violates AGENTS.md PRIME DIRECTIVE 4 / DO IT RIGHT #2 ("no vibe coding"). Decomposition Scorecard requires the actual decomposition decision per ADR; OBPI brief Lane/Paths require what was true at authoring time. Mechanical placeholder = canon corruption. |
| 3 | **Add explicit `schema-version:` frontmatter to grandfather pre-convention artifacts** | Adds a new schema field whose only purpose is exception-tracking. Trades 259 noisy errors for 259 frontmatter exemption markers — same problem, different surface. Acceptable only if paired with a deprecation timeline that retires the exemption. |
| 4 | **Withdraw or archive the failing pre-release ADRs (most of the 200+ cohort)** | Many failing pre-release ADRs carry substantive design work the project still intends to land. Wholesale withdrawal is data loss; selective withdrawal is the right operator-driven decision but doesn't fit a single bulk operation. |

The decision deferred to promotion is which combination of #2 (substantive per-artifact backfill), #3 (explicit grandfather frontmatter), and #4 (selective withdrawal) resolves the backlog, and what validator-scope semantics result.

## Promotion plan

Pre-promotion (during pool lifetime):
- Operator can selectively withdraw any pre-release ADR that no longer reflects intent (reduces Cohort B by that ADR's OBPI count).
- Foundation ADRs (24+ failing) get treated separately from pre-release backlog — they are committed canon and any backfill must reflect the actual decomposition that produced them.

Promotion ceremony will decompose into at least three OBPIs:
1. **OBPI-N-01 — Cohort A backfill (foundation ADRs):** author `## Decomposition Scorecard` for each failing foundation ADR with the actual scoring those ADRs would have received under the current scorecard. Lite lane, doc-only.
2. **OBPI-N-02 — Cohort B disposition (pre-release OBPI briefs):** either backfill the missing sections from authoring-time evidence or withdraw the parent ADR. Operator-driven per ADR; lite lane.
3. **OBPI-N-03 — Validator scope semantics:** decide whether `--documents` grandfathers pre-convention artifacts, requires explicit `schema-version` frontmatter exemptions, or strictly enforces current schema. Heavy lane (runtime contract change).

## ADR relationship

- **Upstream evidence:** GHI #480 (filed 2026-05-17)
- **Discovered during:** ADR-0.0.35-foundation-feature-invariance-test closeout ceremony (2026-05-17)
- **Adjacent canon:** AGENTS.md § Architectural Boundaries #6 (derived views never authoritative); `.gzkit/rules/brief-heading-conventions.md` (OBPI brief heading schema)

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
