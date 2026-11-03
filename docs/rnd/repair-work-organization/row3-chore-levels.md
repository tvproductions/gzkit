# Row 3 advice: the chores by check level

> Advice for disposition row 3 of [`repair-work-organization.md`](../repair-work-organization.md), written 2026-11-03 on the operator's go (*"row 3 is a go"*). Row 3 is **advise only**: the operator directs admission, and nothing here is written to `.gzkit/chores/registry.json` until then. It holds no authority; the record governs.

## What is advised

1. **Each chore carries a check level, A to D, and a date interval.** The levels below are the census's reading mapped through the ruled table (*propose* → A; *repair* on the line → B; unclear → C; out of service → D). That mapping is the agent's draft (record, decision *the agent's draft of gzkit's check levels*); the census itself *"assigns no check level"*. Every level is **provisional**: row 5's classification program classifies each chore and moves these.
2. **Every chore is due by date** (ruled: *"B for now until we have more maturity"*). An interval the operator already set is kept (*"the operator keeps the frequency"*, `command-doctrine.md`). A chore whose staleness reads only a signal (`cd` content-delta, `aw` accumulated-work) gains a date interval beside it, due at whichever comes first, as the FAA's intervals run (*"hours of time in service, cycles, and calendar-time, or some other identifiable increment"*). The advised default by level: **A 14 days, B 30, C 90, D 180.**
3. **Checks are packaged by level, each including those below.** An A check runs the A chores; a B check runs A and B; a C check runs A to C; a D check runs all 41.
4. **Recommendation points, advised and never gated:** A and B at a GHI drawdown; C and D at a minor release and at `gz mx exit`, and by date.
5. **The waiver lists' drawdown is C work.** 37 lists, about 6,796 entries, may only shrink and carry no drawdown commitment today. A C check draws one down by an amount the operator sets.

## What admission needs first

The registry cannot carry a level today. `ChoreDeclaration` (`src/gzkit/commands/chores_declaration.py:119`) is `extra="forbid"`, so a `checkLevel` key fails the registry's own parse, and `ChoreStaleness` requires a signal, with a period optional. Admitting the levels is therefore a schema change to the chore declaration, coupled to the chore class system in row 4 (`docs/governance/chore-class-system.md`) and to `gz chores status`, which would read the level and package by it. Until then the table below is the advice of record.

## The chores

Census verdicts and rungs: `sources/census-chores.md` § Census, read 2026-11-02. Intervals today: `.gzkit/chores/registry.json`, read 2026-11-03.

| Level | Chore | Rung | Census verdict | Interval today | Advised date interval |
|---|---|---|---|---|---|
| A | `arb-pattern-extraction` | propose | line | et 30d | 30 days (kept) |
| A | `competitor-radar-currency` | propose | line | et 30d | 30 days (kept) |
| A | `control-surface-rule-conflicts` | propose | line | cd | 14 days, alongside its signal |
| A | `control-surface-rule-vs-check-drift` | propose | line | cd | 14 days, alongside its signal |
| A | `control-surface-skill-rule-reachability` | propose | line | cd | 14 days, alongside its signal |
| A | `control-surface-validator-reachability` | propose | line | cd | 14 days, alongside its signal |
| A | `eval-feedback-cluster` | propose | line | et 30d | 30 days (kept) |
| A | `evidence-integrity-audit` | propose | line | cd | 14 days, alongside its signal |
| A | `failure-class-index` | propose | line | et 30d | 30 days (kept) |
| A | `ghi-cross-reference-staleness` | propose | line | et 30d | 30 days (kept) |
| A | `ledger-vocabulary-inertness` | propose | line | cd | 14 days, alongside its signal |
| A | `pool-triage` | propose | line | aw | 14 days, alongside its signal |
| A | `pythonic-design-pattern-detection` | propose | line | cd | 14 days, alongside its signal |
| A | `quality-check` | propose | line | cd | 14 days, alongside its signal |
| A | `session-correction-mining` | propose | line | et 30d | 30 days (kept) |
| A | `skill-authoring-quality` | propose | line | cd | 14 days, alongside its signal |
| A | `skill-trigger-testing` | propose | line | cd | 14 days, alongside its signal |
| B | `coverage-40pct` | repair | line | cd | 30 days, alongside its signal |
| B | `doc-coverage` | repair | line | cd | 30 days, alongside its signal |
| B | `pep257-docstring-compliance` | repair | line | cd | 30 days, alongside its signal |
| B | `test-manpage-examples` | repair | line | cd | 30 days, alongside its signal |
| C | `cli-contract-governance` | op-only | unclear | cd | 90 days, alongside its signal |
| C | `complexity-reduction-xenon` | repair | unclear | cd | 90 days, alongside its signal |
| C | `config-paths-remediation` | repair | unclear | cd | 90 days, alongside its signal |
| C | `cross-platform-test-cleanup` | repair | unclear | cd | 90 days, alongside its signal |
| C | `exceptions-and-logging-rationalization` | repair | unclear | cd | 90 days, alongside its signal |
| C | `frontmatter-ledger-coherence` | repair | unclear | cd | 90 days, alongside its signal |
| C | `hardcoded-root-eradication` | repair | unclear | cd | 90 days, alongside its signal |
| C | `module-sloc-cap-radon` | repair | unclear | cd | 90 days, alongside its signal |
| C | `pythonic-design-pattern-application` | repair | unclear | cd | 90 days, alongside its signal |
| C | `pythonic-refactoring` | repair | unclear | cd | 90 days, alongside its signal |
| C | `repository-structure-normalization` | repair | unclear | cd | 90 days, alongside its signal |
| C | `test-consolidation-subtest-sweep` | repair | unclear | cd | 90 days, alongside its signal |
| C | `test-isolation-compliance` | repair | unclear | cd | 90 days, alongside its signal |
| D | `control-surface-permission-consent-drift` | op-only | out of service | et 30d | 30 days (kept) |
| D | `decommission-tautological-tests` | repair | out of service | aw | 180 days, alongside its signal |
| D | `dependency-currency` | repair | out of service | et 1d | 1 days (kept) |
| D | `frontier-model-card-currency` | op-only | out of service | et 30d | 30 days (kept) |
| D | `instructions-files-diet` | op-only | out of service | aw | 180 days, alongside its signal |
| D | `memory-hygiene` | op-only | out of service | cd | 180 days, alongside its signal |
| D | `skill-command-doc-parity` | op-only | out of service | cd | 180 days, alongside its signal |

Counts: A 17, B 4, C 13, D 7. Intervals kept: 9. Intervals added beside a signal: 32.

## Open for the operator

- The default interval per level (A 14, B 30, C 90, D 180) is the agent's, not ruled.
- `quality-check` sits at A by its rung, yet it is the `gz check --full` sweep, which runs in CI on every push; whether it belongs among the chores at all is row 5's question.
- `dependency-currency` keeps its 1-day period at D, the heaviest level: a daily D is a contradiction the classification program should settle, since its daily part (reading upstream) is A work and only its upgrade step is D.
