# Test Consolidation — subTest Sweep & Slow-Tier Quarantine

> **Origin:** routed out of GHI #644 (at-scale test-suite management) when that
> tracker closed `superseded`. The tracker's parallelism half was already
> satisfied by shipped code (`baeb1f72e` — `run_tests` invokes
> `unittest-parallel`); these consolidation items are the scope that survived.

**Intended project-local; ships anyway — tracked at GHI #728.** This chore
encodes gzkit's own test-hygiene posture, not portable adopter governance, and
was authored only under `.gzkit/chores/`. It is nonetheless propagated into
`src/gzkit/chores/` by `gz agent sync control-surfaces` and scaffolded into
adopter projects by `gz init`: no project-local-only affordance exists in either
path, even though `gz chores doctor` honours exactly that category
(REQ-0.0.21-09-06) and `.gzkit/rules/chores.md` § Two-Surface Layout marks the
project overlay "Shipped in wheel? **No**".

An earlier revision of this file asserted the opposite as fact. That claim was
false; it is corrected here rather than quietly dropped.

**If you are an adopter who received this chore:** the baseline table below is
gzkit's own measurement, not yours. Re-measure before acting, or disregard the
chore — it is gzkit's internal hygiene, not governance you adopted.

## Why this exists

The unit suite grows monotonically with the REQ set by design
(`.gzkit/rules/tests.md` 0.13.0 declares the full unit tier explicitly
unbounded). Growth is therefore not a defect to be capped — but the stdlib
consolidation levers that keep a growing suite legible are under-used, and one
already-written tool is not wired to anything.

## Measured baseline (2026-07-27, re-measured at authoring)

| Signal | Value | Command |
|---|---|---|
| Test files | 508 | `find tests -name 'test_*.py' -type f \| wc -l` |
| Files using `subTest` | 84 (16.5%) | `grep -rl "subTest" tests --include='test_*.py' \| wc -l` |
| Slow-test profiler | exists, wired to nothing | `scripts/profile_unittest_modules.py` |

Re-measured 2026-07-31 on the chore's first run: 508 files / 84 using `subTest`
(16.5%), up from 497 / 78 (15.7%) at authoring on 2026-07-27, and from GHI
#644's 449 / 59 (13.1%) on 2026-06-25. Three measurements, three different
denominators in five weeks — **re-measure before acting rather than trusting
any figure above.** The ratio is drifting upward on its own, which is worth
knowing before treating the sweep as urgent.

The "wired to nothing" row still holds: `grep -rn profile_unittest_modules`
across `*.py`/`*.md`/`*.json`/`*.toml`/`*.yml` returns only this CHORE.md, its
README, and their `src/gzkit/` mirrors — no runner, no CI step, no `gz` verb
invokes it. That tracker also carried two rows of stale state — it asserted `gz
test` and CI were serial when both had been parallel since `baeb1f72e` — which
is the specific reason this chore states its commands rather than its
conclusions.

## Scope

1. **subTest sweep.** Convert table-driven tests that loop without `subTest` so
   a single failing case reports its own parameters instead of aborting the
   loop. Target the worst offenders first; this is a legibility lever, not a
   coverage lever — test count should not change.
2. **Slow-tier quarantine.** Wire `scripts/profile_unittest_modules.py` so the
   slow tail is ranked and visible, then decide whether the tail belongs in a
   separate segment. Wiring first, policy second.
3. **Fixture consolidation audit.** Confirm duplicated `setUp` bodies route
   through the existing `tests/fakes/{config,filesystem,ledger,process}.py` and
   `tests/commands/common.py` patchers rather than being re-inlined.

## Out of scope

- **Any change to `CANONICAL_STEP_COMMANDS`** (`src/gzkit/arb/validator.py`) or
  the four ARB attestation sites. That path is deliberately serial and
  attestation-locked; `AGENTS.md` § Attestation pins the invocations.
- **Re-pinning `unittest-parallel` in `pyproject.toml`.** The April broad
  version (`02e190e3`) was reverted same-day (`54a71ae6`) and redone narrow and
  un-pinned. Re-pinning re-introduces the rejected shape.
- **Extending parallelism further.** GHI #512's Option B is declined on
  measurement (71.4s across 32 processes, over the ceiling) and that ruling is
  settled canon. Do not re-litigate it here.
- **Deleting tests to reduce count.** Tautological-test pruning has its own
  chore (`decommission-tautological-tests`) under ADR-0.0.59.

## Workflow

```bash
uv run gz chores plan test-consolidation-subtest-sweep --replace
uv run gz chores advise test-consolidation-subtest-sweep
# re-measure the baseline table above before editing anything
uv run gz test                    # green before
# ... surgical consolidation edits ...
uv run gz test                    # green after; test COUNT must not drop
uv run gz chores run test-consolidation-subtest-sweep
```

## Acceptance

Both criteria in `acceptance.json` must pass:

- `uv run gz validate --chores-layout` — exit 0; no stray chore artifacts.
- `uv run gz test` — exit 0; the suite is green after any consolidation edit.

A consolidation pass that reduces the test count has deleted coverage rather
than consolidating it, and is a failed pass regardless of a green suite.

## Related

- GHI #644 — the tracker this chore was routed out of (closed `superseded`)
- GHI #512 — the narrow `unittest-parallel` adoption; Option B declined
- `baeb1f72e` — the commit that parallelized `run_tests`
- ADR-0.0.59 — REQ-kind taxonomy; consolidation-by-deletion lives there
- `.gzkit/rules/tests.md` § General Rules — tier budgets and the unbounded
  full-unit-tier declaration
