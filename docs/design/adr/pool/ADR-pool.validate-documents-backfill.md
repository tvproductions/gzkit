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

**Update — 2026-05-20 (GHI #500, operator decision).** Cohort B's
`gz validate --documents`-scope symptom is resolved. GHI #500 was filed as a
standalone defect for the OBPI-brief cohort; during its `ghi-close` the
conflict with this ADR's Decision #3 ("preserve validator behavior until
promotion") was surfaced, and the operator chose to decide the OBPI cohort
early rather than hold it for the promotion ceremony. Commit `4bfbddab` lands
the fix: `_validate_manifest_documents` no longer raw-schema-validates OBPI
briefs — OBPI corpus hygiene is delegated to the version-aware `briefs` scope
(`_validate_obpi_briefs`), and strict authored checks remain in
`gz obpi validate --authored`. The live `gz validate --documents` count is now
**1725 errors — Cohort A (ADR documents) only**; Cohort B no longer appears in
the `--documents` scope.

**Update — 2026-05-24 (cohort redistribution discovered; ADR-0.28.0 closeout).**
The 1725-count framing implicitly bundled pool ADRs with foundation/feature
ADRs into "Cohort A." Re-measuring during ADR-0.28.0 closeout produced
**1825 errors** (delta +100 since 2026-05-20) with the following
distribution by ADR kind:

- **Cohort C — pool ADRs:** **1599 errors (87.6%)** across `ADR-pool.*`
  identifiers — `Field 'status' must be one of` (the schema enum rejects
  `Pool` though pool ADRs use it), `Missing required section: 'Decomposition
  Scorecard'`, `Missing required section: 'Checklist'`, `Missing required
  section: 'Attestation Block'`, `Missing required section: 'Consequences'`,
  `Missing required section: 'Decision'`. **These sections describe work in
  flight; pool ADRs by definition have no work in flight** (per
  `## Notes` below: "Pool ADRs are backlog items — they carry no `semver:`
  or `kind:` frontmatter"). The validator is applying foundation/feature
  shape requirements to pool placeholders.
- **Cohort A (now narrower) — foundation / feature ADR documents:**
  **~226 errors (12.4%)** — the actually-pre-convention case the original
  framing named. This count is roughly stable across recent recovery
  sessions and is the genuine backfill question.

The cohort shift surfaces a fifth alternative not previously considered —
see Alt #5 in the table below. Cohort C is not "pre-convention pool ADRs
needing backfill"; it is "pool ADRs validated against the wrong kind
schema." Promotion ceremony now decides over Cohort A and Cohort C
independently.

GHI #480 reopened 2026-05-24 with the regression evidence and the Cohort C
discovery. The reopen does not invalidate this ADR's prior framing — it
provides a sharper lens for the eventual promotion decision.

**Update — 2026-07-22 (GHI #480 closed `superseded` into this ADR).**
`uv run gz validate --documents` now exits 0 (3536 → 1825 → 1643 → 0). The
`--documents`-scope *symptom* is fully resolved by the two narrow scope
guards in `src/gzkit/validate_pkg/document.py` (kind-aware pool skip +
lifecycle-aware Completed/Validated grandfather), not by backfill. Those
guards shipped untested in OBPI-0.0.54-03; commit `53078405` pins both
predicates with paired negative controls and a narrowness assertion
(mutation-verified). The substantive Alt #2/#3/#4/#5 decision for Cohort A
remains this ADR's promotion work, and Alt #5's pool-kind schema artifact
remains the authoritative home for the fact that pool ADRs currently
receive *zero* validation rather than pool-shape validation.

## Decision

This ADR is **pool** — backlog awaiting promotion. The substantive decision (whether to backfill artifacts, adjust validator scope, or both) is reserved for the promotion ceremony when this ADR is lifted to `feature` lane. Promotion criteria below.

What this pool ADR commits to *now*:

1. **The class of failure is named and homed.** GHI #480 closes `superseded` citing this ADR. The 3536-error backlog has a registered tracker in the artifact graph, not a session-memory ghost.
2. **The two cohorts are bounded.** Cohort A = ADR documents missing Decomposition Scorecard (298 instances). Cohort B = OBPI briefs missing Lane / Allowed Paths / Denied Paths / Requirements / Quality Gates (240+ instances). Promotion will produce one OBPI brief per cohort plus a third OBPI for validator scope semantics (grandfather vs. backfill policy).
3. **The validator's behavior for Cohort A is preserved until promotion.** No silent suppression, no `--allow-pre-convention` flag, no schema rollback for the ADR-document cohort. The OBPI cohort (Cohort B) was decided early — see Intent § Update (GHI #500): `--documents` delegates OBPI validation to the dedicated `briefs` scope. The remaining **1725-error count (Cohort A)** is the honest signal until decided otherwise.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | **Suppress pre-convention errors in `--documents` via authoring-date heuristic** | Layer-3 derived-view shortcut. Implicit grandfather semantics violate AGENTS.md § Architectural Boundaries #6. Cannot answer "is this artifact compliant?" without re-implementing the heuristic. |
| 2 | **Bulk-backfill every artifact mechanically with placeholder section content** | Violates AGENTS.md PRIME DIRECTIVE 4 / DO IT RIGHT #2 ("no vibe coding"). Decomposition Scorecard requires the actual decomposition decision per ADR; OBPI brief Lane/Paths require what was true at authoring time. Mechanical placeholder = canon corruption. |
| 3 | **Add explicit `schema-version:` frontmatter to grandfather pre-convention artifacts** | Adds a new schema field whose only purpose is exception-tracking. Trades 259 noisy errors for 259 frontmatter exemption markers — same problem, different surface. Acceptable only if paired with a deprecation timeline that retires the exemption. |
| 4 | **Withdraw or archive the failing pre-release ADRs (most of the 200+ cohort)** | Many failing pre-release ADRs carry substantive design work the project still intends to land. Wholesale withdrawal is data loss; selective withdrawal is the right operator-driven decision but doesn't fit a single bulk operation. |
| 5 | **Validator scope by `kind`: pool ADRs validate against a pool-shape contract (Intent / Target Scope / Non-Goals + reduced frontmatter); foundation / feature ADRs validate against the current full schema** | Net-new lens introduced 2026-05-24. **Distinct from Alt #1** — Alt #1 was "suppress real errors via authoring-date heuristic" (Layer-3 derived view, can't answer compliance question). Alt #5 is "apply the correct schema for the kind in the first place" (Layer-1 canon — pool ADRs have a documented, structurally-distinct shape contract per `## Notes` below and per `src/gzkit/schemas/adr.json:37`). Resolves Cohort C (1599 errors, 87.6%) without backfilling or grandfathering anything. Cohort A (226 errors) remains for Alt #2 / #3 / #4 decision. Reframes the question from "how do we forgive pool ADRs their missing sections?" to "why are we asking pool ADRs about sections they were never supposed to carry?". Trade-off: needs a published "pool ADR schema" JSON or equivalent contract — without that, the validator has no authoritative shape to check against, so this alternative ships paired with a pool-kind schema artifact, not as standalone scope logic. |

The decision deferred to promotion is which combination of #2 (substantive per-artifact backfill), #3 (explicit grandfather frontmatter), #4 (selective withdrawal), and #5 (validator scope by kind) resolves the backlog, and what validator-scope semantics result. Alt #5 resolves Cohort C; #2 / #3 / #4 resolve Cohort A.

**Cohort B resolution (GHI #500, 2026-05-20).** GHI #500 resolved Cohort B by a fifth approach not in the table above: `--documents` delegates OBPI corpus validation to the dedicated version-aware `briefs` scope. This is **not** rejected Alternative #1 — it is not an authoring-date heuristic and produces no implicit grandfather semantics: OBPI compliance remains answerable via `gz validate --briefs` and `gz obpi validate --authored`. The deferred decision above now covers Cohort A only.

## Promotion plan

Pre-promotion (during pool lifetime):
- Operator can selectively withdraw any pre-release ADR that no longer reflects intent (reduces Cohort B by that ADR's OBPI count).
- Foundation ADRs (24+ failing) get treated separately from pre-release backlog — they are committed canon and any backfill must reflect the actual decomposition that produced them.

Promotion ceremony will decompose into at least three OBPIs:
1. **OBPI-N-01 — Cohort A backfill (foundation ADRs):** author `## Decomposition Scorecard` for each failing foundation ADR with the actual scoring those ADRs would have received under the current scorecard. Lite lane, doc-only.
2. **OBPI-N-02 — Cohort B disposition (pre-release OBPI briefs):** the `--documents`-scope symptom is resolved (GHI #500, commit `4bfbddab`); residual scope is whether the historical OBPI briefs are substantively backfilled or their parent ADRs withdrawn — now surfaced by the `briefs` scope and `gz obpi validate --authored`, not `--documents`. Operator-driven per ADR; lite lane.
3. **OBPI-N-03 — Validator scope semantics (Cohort A):** decide whether `--documents` grandfathers pre-convention ADR documents, requires explicit `schema-version` frontmatter exemptions, or strictly enforces current schema. The OBPI-brief side of this question was decided by GHI #500 (delegation to the `briefs` scope); OBPI-N-03 now covers the ADR-document cohort only. Heavy lane (runtime contract change).

## ADR relationship

- **Upstream evidence:** GHI #480 (filed 2026-05-17)
- **Cohort B early resolution:** GHI #500 (closed 2026-05-20) — commit `4bfbddab`; OBPI cohort decided ahead of promotion per operator decision (see Intent § Update)
- **Discovered during:** ADR-0.0.35-foundation-feature-invariance-test closeout ceremony (2026-05-17)
- **Adjacent canon:** AGENTS.md § Architectural Boundaries #6 (derived views never authoritative); `.gzkit/rules/brief-heading-conventions.md` (OBPI brief heading schema)

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
