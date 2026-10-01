---
id: ADR-pool.new-cli-command-absorption
status: Pool
parent: PRD-GZKIT-1.0.0
---

# ADR-pool.new-cli-command-absorption: Remaining CLI Command Absorption

**Date Added:** 2026-03-21
**Status:** Pool
**SemVer:** Unassigned; allocate only at promotion.

## Intent

Evaluate the remaining opsdev quality-tooling ports independently of the three
test-integrity candidates. This is backlog intent, not an active work order.

## Proposed split — 2026-09-24

Move `mutate`, `test-quality`, and `test-times` to
[ADR-pool.test-integrity-tooling](ADR-pool.test-integrity-tooling.md), allowing
that scope to be considered for promotion on its own. Retain the other seven
original command rows here, including the already-withdrawn complexity row.
This proposal promotes neither entry and reserves no release number.

`ADR-0.31.0-obpi-state-machine` holds SemVer 0.31.0. The former absorption
package was demoted at `993a16c11` on 2026-05-23, removing its briefs. Its
old numbered OBPI references are historical identities, not current briefs.

## Target Scope

The keys below are document-local candidate keys, not OBPI identifiers.
At promotion, reassess each candidate against the then-current CLI, allocate
one feature ADR, and author one OBPI brief per accepted checklist item.

| Key | Original row | Candidate | Disposition |
|---|---:|---|---|
| CLI-01 | 1 | `sloc-scan`: SLOC analysis | Pending evaluation |
| CLI-02 | 2 | `complexity-check`: cyclomatic complexity | Withdrawn 2026-04-25; subsumed by [ADR-0.0.29](../foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md) |
| CLI-05 | 5 | `metrics scan`: code quality violation scanning | Pending evaluation |
| CLI-06 | 6 | `metrics report/watch`: monitoring and reporting | Pending evaluation |
| CLI-08 | 8 | `validate-manpages`: manpage structure validation | Pending evaluation |
| CLI-09 | 9 | `sync-manpage-docstrings`: docstring synchronization | Pending evaluation |
| CLI-10 | 10 | `interrogate`: docstring coverage integration | Pending evaluation |

**Briefs:** This flat pool entry has no current OBPI package. These rows do not
claim a corresponding brief exists. Briefs are authored at promotion, using
the promoted ADR's newly allocated identifier.

## Promotion decisions

- Establish that a proposed command adds a capability the current gzkit CLI
  does not already supply; the original port inventory is a dated proposal.
- Choose the supported input, output, failure, and configuration contracts.
- Resolve actual capability dependencies; the old references to ADR-0.25.0
  and ADR-0.30.0 must not be treated as current dependencies by number alone.
- Use stdlib first. Any dependency needs an explicit promoted ADR/OBPI
  rationale naming the capability stdlib cannot supply and its maintenance cost.
- Follow [pool curation](../../../governance/pool-curation.md): sponsor,
  acceptance criteria, settled dependencies, capacity, and operator promotion.

## Consequences

The test-integrity decision can be considered without committing to the six
remaining pending ports. The withdrawn row stays in the historical inventory.
No CLI, dependency, validator, release, ledger event, or execution commitment
is introduced by this pool proposal.

## Evidence

- Original inventory dated 2026-03-21; retained by git history.
- Demotion commit `993a16c11` removed the former feature package and briefs.
- Audit baseline `5d9885a08c438b0aa546716b20a181c55342612e`, measured
  2026-09-24: this pool frontmatter says Pool while its former body said
  Proposed, reserved 0.31.0, and claimed every numbered row had a brief.
- The test-integrity pilot and proposed promotion trigger belong in the
  [split entry](ADR-pool.test-integrity-tooling.md).
