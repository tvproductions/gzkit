# Tests Rule — Rationale

*Lifted from `.claude/rules/tests.md` § Rationale under GHI #327. The
binding test policy remains canonical in `.gzkit/rules/tests.md`
(propagated to `.claude/rules/tests.md` via `gz agent sync
control-surfaces`); this page holds the canonical-history and
philosophical-justification narrative.*

## Canonical history of the two-runner boundary

- **GHI #181** (landed in `e22ac553`): introduced `tests/integration/` as a
  second `unittest` tier to isolate 83 subprocess-wrapping tests from the
  unit tier. Fast fix for the symptom (`gz test` from 90s to 30s), but
  labeled the wrong class of failure.
- **GHI #182**: per the DO IT RIGHT maxim (`AGENTS.md` § DO IT RIGHT, items
  1 (6a) and 7 (6c)), the thorough fix is per-test triage — every test
  under the old `tests/integration/` was either (a) already mockable at
  the Python level and relocated back to `tests/commands/` with
  `_git_subprocess_patcher` / `_uv_sync_patcher` / `_quick_init`, or (b)
  genuinely E2E and moved to `features/`. Triage decisions recorded in
  `artifacts/audits/ghi-182-triage.md`. `tests/integration/`, the
  `load_tests` gating protocol, and `gz test --integration` are removed.

## Why TDD rhythm matters

TDD discipline is the most commonly rationalized-away practice in this
codebase. Every TDD anti-pattern listed in `.gzkit/rules/tests.md` § TDD
anti-patterns has been observed in production agent sessions. The
per-increment rhythm keeps the observation loop firing; batched "test-dump
theater" mimics TDD shape while skipping the part that makes it work
(GHI #157).

## Origin

GHI #327 — instructions-files-diet pass.
