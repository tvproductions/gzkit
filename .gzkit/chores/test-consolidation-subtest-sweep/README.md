# test-consolidation-subtest-sweep

Raise `subTest` adoption in the unit suite, wire the unused slow-test profiler,
and audit fixture consolidation — the three consolidation items that survived
GHI #644 when its parallelism half turned out to be already shipped.

**Lane:** lite (unit-tier only; no behave, no network).
**Surface:** intended project-local, but it DOES ship in the wheel and reaches
adopters via `gz init` — no project-local-only affordance exists in sync or init
(GHI #728). It encodes gzkit's own test hygiene rather than portable adopter
governance, so an adopter receiving it should disregard it or re-measure first.

Baseline at authoring (2026-07-27): 78 of 497 test files use `subTest` (15.7%);
`scripts/profile_unittest_modules.py` is wired to nothing.

Read `CHORE.md` before running. Re-measure the baseline first — the GHI this
came from carried two rows of stale state, which is exactly what this chore's
Out-of-scope section exists to prevent repeating.
