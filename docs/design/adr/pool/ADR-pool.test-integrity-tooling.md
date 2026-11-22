---
id: ADR-pool.test-integrity-tooling
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.test-integrity-tooling: Test Integrity Tooling

**Date Added:** 2026-10-01 (proposed by the 2026-09-24 test audit § 9; added to the pool by operator ruling 2026-10-01, verbatim: "Apply, re-based (Recommended)")
**Status:** Pool
**SemVer:** Unassigned; allocate only at operator-authorized promotion.
**Amended:** 2026-11-21, TI-01 withdrawn (operator, verbatim: "withdraw TI-01 from the pool ADR, keep the rest"); see § Target Scope.
**Amended:** 2026-11-22, § Target Scope states the contract required of any mutation provider in place of one provider's documents and issues (operator, verbatim: "do not reference the dependency by its title, we make it generic and abstracted to the contract desired from any provider").

## Intent

Make test sensitivity measurable for enforcement code: surface weak test
structure and measure the cost of that evidence. Preserve the
separation between executing a line and asserting the behavior on that line.

## Target Scope

These are local candidate keys, not OBPI identifiers or existing briefs.
At promotion, author a feature ADR and one brief per accepted checklist item.

TI-01 (`mutate`) is withdrawn (2026-11-21). Mutation testing now comes from a
provider library. The engine's design, dependencies and schedule are the provider's.
gzkit states only the contract it requires of any mutation provider:

- **Isolation:** apply each mutation to a copy of the code, never to the tree under
  test, and run the selected tests against that copy.
- **Complete outcomes:** report every job and classify every outcome. A missing
  job, a failed baseline, code under test imported from somewhere other than the
  mutated copy, or an unclassified outcome is a failure, never a pass.
- **No score floor:** report survivors without a global kill percentage. A survivor
  percentage alone does not fail quality; a reviewed non-equivalent survivor is a
  finding for the operator.

The pilot's full record, and the § 10 gate "General mutation diagnostic
completeness" that this contract restates, stay in
[the 2026-09-24 audit](../../../evals/test-suite-integrity-audit-2026-09-24.md).

- **TI-02 — `test-quality`:** AST measurements with stated detection limits;
  distinguish scan candidates from confirmed defects, account for inherited
  assertion helpers, and do not grade a test's semantics from its shape alone.
- **TI-03 — `test-times`:** per-test unittest duration measurements with test
  identity and run metadata, used to size the diagnostic and review redundant
  work; timing by itself does not justify deleting a behavior proof.

### Gates routed here from the audit's § 10

Operator ruling 2026-10-01 (verbatim: "Split by intent (Recommended)"): the
§ 10 gates that are new capability live in this pool. The gates that make an
existing gate meet its declared intent are corrections under GHI #1154 and
#1155. The contracts below are the audit's § 10 rows, unchanged.

- **TI-02** carries § 10 "Constant/vacuous test regression". Fail newly
  introduced unconditional `assertTrue(True)` methods. For selected scanners,
  require nonempty independent fixture expectations and a rejected zero-result
  fault. Never fail on `assertIsInstance`, an absent assert spelling, or a
  conditional assertion alone.
- **TI-04 — coverage measurement integrity:** require a passing unit run,
  fresh measured data and an explicit child-process policy. Bind the existing
  authored line floor to CI only after that binding is decided; propose no
  branch or mutation score floor.
- **TI-05 — pool references and identity:** fail active-work references to
  absent briefs and reserved pool semver collisions; allow explicitly dated
  historical accounts.

## Promotion criteria and evidence boundaries

The operator cannot promote now. This pool records the proposed split and
measurement, with no active OBPI, reserved semver, or automatic promotion.
The promoted design must also evaluate the three pool-worthiness conditions:
reversal cost, context-dependent decision, and a named losing alternative.

See [pool-curation.md](../../../governance/pool-curation.md).
