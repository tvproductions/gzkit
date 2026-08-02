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

## TDD anti-patterns

- Writing tests after implementation that confirm what the code already does
- Writing tests "alongside" without seeing them fail first (skipping Red)
- Writing all tests at once before any implementation (test-dump, not TDD)
- Batching all tests for one "RED screenshot" then batching all code for one "GREEN screenshot" (GHI #157)
- Stopping after each RED→GREEN pair to solicit operator approval before the next increment (GHI #157)
- Refactoring while tests are still failing (mixing Green and Refactor)
- Backfilling `@covers(REQ-...)` decorators cosmetically without re-deriving assertions from the REQ (GHI #272)

## Eval-awareness corollary (Fable/Mythos 5 §§ 6.1.2, 6.4.1.2, 6.4.2)

Evaluation awareness on the current frontier tier is significant and mostly *unverbalized*: the model "will occasionally reason about the possibility that it is being graded, or consider ways to satisfy such a grader that go against user intent," while white-box methods show it "almost never explicitly verbalizes this reasoning" (Claude Fable 5 / Mythos 5 System Card § 6.1.2). The white-box record includes a graded coding task where the model exploited a hidden reference solution while internally framing its justification as needing to "appear as 'good engineering practice' not just 'matching the grader'" — with no mention of the reference in its user-facing report (§ 6.4.1.2). Grader-shaped reasoning appears "disproportionately in training environments with exploitable graders" (§ 6.1.2, § 6.4.2).

For governance test surfaces the consequence is direct: an assertion helper whose name pattern-matches as "this is the audit step" creates exactly the recognizable graded context that elicits grader-satisfying behavior instead of the behavior under test. Name helpers by behavior, not audit role:

| Anti-pattern (audit-role name) | Preferred (behavior-named) |
|---|---|
| `assert_audit_passes` | `assert_receipt_id_resolves` |
| `verify_attestation_authenticity` | `assert_attestor_name_present` |
| `check_eval_pass` | `assert_brief_status_in_ledger` |

Parent rules: ADR-0.0.23 (failure-mode taxonomy), ADR-0.0.24 (attestation receipt binding), ADR-0.0.25 (OBPI REQ coverage gate).

## Output-form fixture carve-out

Output-form assertions (table markers, JSON shape) are permitted in dedicated fixture tests per `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3. Keep them separate from REQ-derived unit tests: semantic refactors should never force string-shape rewrites and vice versa. GHI #270 surfaced the collision.

## Behave enforcement details

`gz validate --behave-req-tags` (GHI #276) enumerates heavy-lane OBPI briefs (excluding pool), extracts REQ-IDs from `## Acceptance Criteria`, and asserts matching `@REQ-*` scenario tags under `features/**`. Direction is OBPI → feature (not the GHI #211 original feature → feature direction).

**Lifecycle scope (GHI #323):** fires only on `Completed`/`Validated` briefs. Pre-implementation states skip via inverse filter — BDD scenarios land at implementation time, not brief-authoring time. Missing coverage on a post-implementation brief is exit 3. Waivers in `data/behave_coverage_waivers.json`.

## TASK-driven workflow details

Every code-change GHI decomposes into TASKs via `gz task`. Binding steps:

1. `gz covers <ADR-ID>` → identify REQs
2. `gz task start TASK-X.Y.Z-NN-MM-PP`
3. TDD cycle (Red → Green → Refactor)
4. Commit with `Task: TASK-X.Y.Z-NN-MM-PP` trailer
5. `gz task complete TASK-X.Y.Z-NN-MM-PP`
6. `@covers(REQ-X.Y.Z-NN-MM)` decorator

Governance-intent trailers: `Task:` (hand-crafted), `Ceremony:` (chore/sync), `Eval-feedback-source:` (ADR-0.0.26). Enforced by `gz validate --commit-trailers`.

TASK anti-patterns: skipping `gz task start` and writing trailer from memory; using one TASK for multiple REQs; orphan test files without `@covers`; `Ceremony:` as bypass for task-scoped edits.

## Runner anti-patterns

- Adding a third tier to `gz test` — the runner boundary is the gate
- Spawning real `git`/`uv sync` in `tests/` without documented justification
- Using `runner.invoke(main, ["init"])` when `_quick_init` suffices
- Porting to behave without checking if `features/` already covers it
- Deleting a test without verifying coverage is preserved elsewhere

## Patterns

### Temp-dir context manager (preferred)

```python
class TestSomething(unittest.TestCase):
    def test_with_temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "data.json"
            test_file.write_text("{}")
            result = process_dir(temp_dir)
            self.assertEqual(result, expected)
```

## Origin

GHI #327 — instructions-files-diet pass (initial lift + 2026-05-07 expanded lift).
