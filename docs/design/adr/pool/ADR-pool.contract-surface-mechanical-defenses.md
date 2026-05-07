---
id: ADR-pool.contract-surface-mechanical-defenses
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.contract-surface-mechanical-defenses: Contract-Surface Mechanical Defenses

## Status

Pool

## Intent

Convert the per-turn binding contract surface (`AGENTS.md`, `CLAUDE.md`, and any
future top-level governance prose) from honor-system prose into mechanically
audited evidence. Today the existing `gz validate --advisory-scorecard` enforces
*coverage* of `.gzkit/rules/**` files in `docs/governance/advisory-rules-audit.md`,
which is a sharp single-predicate check — but `AGENTS.md` and `CLAUDE.md` are
out of its scope by construction. Every binding invariant added to those files
since the contract was first scored (Invariant 10a, Behavior Rule 11, DO IT
RIGHT 6c/6g/6h, the entire ANTI-VIBING MANTRA section) landed without a
mechanical scorecard row, without a budget gate, and without a promotion-aging
clock.

The result is the failure mode this ADR is named for: doctrine grew faster
than mechanical enforcement, until the per-turn contract surface itself
became too large for agents to hold and they vibed through it. GHI #380
(authoring-time vibing) and GHI #381 (execution-time vibing) are both
instances of the same root cause — Promotable rules sitting unpromoted because
nothing fails closed when prose accretes without a corresponding validator.

## Decision

Author three parallel `gz validate` scopes, each with a single fail-closed
predicate, that together close the contract-surface accretion class. None of
the three is an expansion of the existing `--advisory-scorecard` — the
existing predicate (rule-file coverage) stays sharp. The three new validators
are siblings.

### Queued children

The active children below are listed in promotion order. The first will be
promoted to a foundation ADR via `gz adr promote` once this pool ADR is
acknowledged. The other two stay in the pool until the first lands and proves
the snapshot mechanism, audit-doc shape, and `gz validate` integration.

#### 1. `gz validate --contract-surface-budget` *(promote first)*

| Field | Value |
|---|---|
| Single predicate | `AGENTS.md` and `CLAUDE.md` word-count and binding-invariant count stay under a snapshot budget recorded in `data/contract_surface_budget.json`. |
| Failure case | Silent prose growth between releases. Adding a new invariant to `AGENTS.md` without a snapshot bump fails closed. |
| Snapshot mechanism | Ledger event `contract_surface_snapshot` with `{file, word_count, invariant_count, sha, rationale}`. Budget bumps require the ledger event; the validator reads the latest snapshot and compares. |
| Why first | Most direct slop-defense. Catches the exact accretion pattern that produced GHI #380 / #381 underneath. Snapshot mechanism is reusable by the other two. |
| Heavy lane | Adds new `gz validate` scope (CLI surface change) and a new ledger event schema (runtime contract). Heavy gates 3 docs, 4 BDD, 5 attestation apply. |

#### 2. `gz validate --contract-surface-scorecard`

| Field | Value |
|---|---|
| Single predicate | Every binding invariant in `AGENTS.md` and `CLAUDE.md` has a row in `docs/governance/contract-surface-audit.md`, scored Mechanical / Promotable / Judgment / Ambiguous. |
| Failure case | A new invariant is added to `AGENTS.md` without a scorecard row, OR an existing invariant is removed without a scorecard row marked `retired`. |
| Audit doc | New `docs/governance/contract-surface-audit.md`, parallel to `advisory-rules-audit.md` but keyed on AGENTS.md/CLAUDE.md section anchors rather than rule-file paths. |
| Why second | Depends on the snapshot mechanism from child 1 to identify "binding invariant" boundaries. Without snapshots, the section-anchor extractor would re-scan the file every run; with snapshots it's a delta check. |
| Heavy lane | New `gz validate` scope plus new audit doc surface. Heavy. |

#### 3. `gz validate --scorecard-promotion-aging`

| Field | Value |
|---|---|
| Single predicate | Any row marked `Promotable` in *either* `advisory-rules-audit.md` or `contract-surface-audit.md` older than N days (suggest 90, configurable in `data/audit_thresholds.json`) without a tracking GHI fails closed. |
| Failure case | A Promotable rule sits unpromoted indefinitely without an open GHI. The exact pattern that let Invariants 10a, 6c, 6g, 6h accumulate. |
| Why third | Depends on both scorecards existing. Wrapper that walks both audit docs and applies the aging predicate. Smallest implementation; biggest behavioral change once it lands. |
| Heavy lane | New `gz validate` scope. Heavy. |

### Integration

All three scopes wire into the default `uv run gz check` pipeline once they
land. The existing `--advisory-scorecard` keeps its current narrow coverage
predicate; the three new scopes layer alongside it.

## Amendment 2026-05-07: Executable-contract posture

Specmatic's durable lesson is that external behavior must be verified as an
executable contract, not described as prose. This ADR should therefore treat
AGENTS.md/CLAUDE.md invariants as contract surfaces with three properties:

1. **Declared contract:** the invariant text and its scorecard row.
2. **Executable witness:** the validator, test, receipt, or ledger event that
   proves the invariant is enforced.
3. **Compatibility result:** whether a proposed edit preserves, tightens, or
   breaks the contract.

Promotion should reject any new contract-surface rule that has no executable
witness unless it is explicitly classified as Judgment with a tracking GHI for
mechanization. This absorbs executable-contract rigor without narrowing gzkit to
API contracts alone.

## Alternatives Considered

**A. Expand `--advisory-scorecard` to cover AGENTS.md and CLAUDE.md.** Rejected.
The existing scorecard's predicate is "every file in `.gzkit/rules/**` has a
row in `advisory-rules-audit.md`." Adding AGENTS.md to that scope either
requires fake "file" entries in the table or schema changes that break the
existing predicate. Single-predicate validators stay sharp; conflated ones
soften.

**B. One foundation ADR proposing all three.** Rejected. Coherent but bigger
plan-audit surface, longer ceremony, and the snapshot mechanism in child 1 is
genuinely a load-bearing primitive for children 2 and 3 — proving it on its
own is worth the incremental ceremony.

**C. Skip the ADR ceremony, file three GHIs.** Rejected. That is exactly the
shortcut that produced the slop trajectory underneath this ADR — adding
mechanical work without architectural intent recorded. Filing GHIs without a
parent ADR means no Gate 5 attestation on the design itself, no plan-audit on
the coupled-surface coherence between the three validators, and no canonical
home for the snapshot mechanism's contract.

## Notes

Surfaced from the 2026-05-02 session that filed [tvproductions/gzkit#380](https://github.com/tvproductions/gzkit/issues/380)
(authoring-time vibing) and [tvproductions/gzkit#381](https://github.com/tvproductions/gzkit/issues/381)
(execution-time vibing). Both GHIs are instances of the contract-surface
accretion class this ADR exists to close.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
Recommended promotion order: child 1 first as `foundation` `0.0.x` (snapshot
mechanism is an app-system invariant), then children 2 and 3 as separate
foundation ADRs once child 1 closes Gate 5.
