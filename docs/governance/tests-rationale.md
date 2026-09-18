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

## Eval-awareness corollary (Fable/Mythos 5.1 §§ 6.3.1, 6.5.4, 6.6.1)

Evaluation awareness on the current frontier tier is significant and often *unverbalized*. Verbalized grader awareness is frequent in agentic coding training environments — "at the start of RL the majority of the long agentic coding episodes are grader aware" (Claude Fable 5.1 & Claude Mythos 5.1 System Card § 6.3.1) — and the white-box record adds the unverbalized forms: "Modeling a hidden test or grader" (acting as if a hidden grader is checking its work when neither prompt nor output mentions one), "Unverbalized evaluation-awareness with principled conduct" and "Knowingly failing an evaluation" (§ 6.6.1). On coding tasks where the answer is leaked in the repository, the model "used a leaked answer without disclosure 70.1% of the time" (§ 6.5.4).

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

## Lifted 2026-09-17 from tests.md 0.25.0 (diet pass, GHI #921)

The rule at `0.26.0` keeps every binding sentence; the measured instances, histories and worked examples below left it verbatim. Each block is a dated record of the rule as it read on 2026-09-17.

### Full unit tier — the timing record

- **Full unit tier: no fixed ceiling.** Its runtime grows with the REQ set by design — every BEHAVIOR REQ owes a covering test and § Coverage Floor requires it — so a constant ceiling over a ratcheting workload can only be breached, never held. That is why the 60s budget belongs to the `@smoke` subset, and the reason is the ratchet, NOT a ruling against parallel execution: the canonical "Tests pass" invocation runs `unittest-parallel` (GHI #856). Dated record, 2026-08-27 at `2c81cb7d`, 10-core host, 8,912 tests, both exit 0: **144.23s serial, 41.34s parallel** — illustrative of the gap, never a threshold; the enforced budget is whatever `uv run gz smoke` fails closed on.

### Eval-awareness corollary — why it stays advisory

**Eval-awareness corollary (advisory — no mechanical witness, and none is planned).** Audit-helper names SHOULD NOT pattern-match as audit-step names — name them by behavior, not audit role (e.g. `assert_receipt_id_resolves` not `assert_audit_passes`). This clause binds at authoring and review time only. A name-shape scan over `tests/**` is tractable and was scored as a promotion candidate for months without being built; under the § Recommended promotion order freeze in `docs/governance/advisory-rules-audit.md` (2026-06-08, opt-in-with-justification), a check nobody has observed catching anything is mechanism this codebase should not add. Reclassify only on a named, observed instance of the confusion this clause names.

### Output-form fixture carve-out — the settled advisory disposition

**Output-form fixture carve-out.** Output-form assertions are permitted in dedicated fixture tests per `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3. Keep them in separate test classes from REQ-derived unit tests. **Declare the carve-out** with an `# output-contract: <reason>` comment inside the test function, or by placing the test in a class whose name ends `OutputForm`, `OutputContract`, or `Rendering`. `gz test-shape` reads those markers; an undeclared assertion on `result.output` / `.getvalue()` / `assertRegex` is reported as advisory, never fail-closed (GHI #571) — **and advisory is the settled disposition, not a waypoint.** The scorecard carried this row as a promotion candidate whose stated path was "flip that arm closed once the declared-marker backlog drains"; draining a backlog is not observed drift, and the § Recommended promotion order freeze (2026-06-08) admits a new fail-closed check only on named, observed evidence. Flipping the arm closed would also fail-close the whole legacy corpus at once, which is the reason it was left open in the first place. *(GHI #270 reconciliation: output-form fixture tests are **BEHAVIOR** REQ proofs under the REQ Scope Discipline taxonomy — they test CLI render-code behavior, not file content. The apparent contradiction between § 6f's prose-content prohibition and Invariant 3's render-form requirement dissolves once REQ kind is named.)*

### Per-increment rhythm — why horizontal slicing fails

**Per-increment rhythm:** One test → one observed RED → minimum code to GREEN → next increment. **Do not slice horizontally** — authoring every test for a brief and then every implementation is not TDD with a long cycle, it is a different activity that produces tests insensitive to change. Written against an implementation you are *about to* write, assertions record the shape you already intend rather than the behavior the REQ demands, and none is ever observed failing for the right reason: the RED that arrives with ten other REDs is noise, not a signal about any one of them. Slice vertically — one REQ carried from failing test to passing code before the next begins. This is § The discriminator applied at authoring time rather than review time: a test batch-written alongside its implementation is the shape most likely to answer "no" to *if behavior changed but text did not, would this test fail?*

### Mutation-sweep integrity — the measured collision and the worked example

**Mutation-sweep integrity (binding, GHI #963).** A mutation sweep grades a guard by deleting it and observing whether a test notices. Its verdicts are quoted as governance evidence, so the sweep must be at least as trustworthy as the tests it grades. **A failing mutant run is NOT a kill.** An absent target, a no-op edit, a mutant that does not import, an unrelated failure, or a red baseline each produce a non-zero exit indistinguishable from a real one; a surviving run can equally conceal a mutation that never activated. Report **four** outcomes, never two — `killed` and `survived` are claims about the GUARD, `invalid` and `inconclusive` are claims about the RUN, and a sweep that lumps them reports coverage it never observed.

Every mutant MUST run in a subprocess with its own `PYTHONPYCACHEPREFIX`. CPython validates a cached `.pyc` on `(mtime-seconds, size)`, so two mutations of equal length landing in the same clock second let the second subprocess import the first mutant's bytecode — measured on an OBPI-0.35.0-04 sweep, where a guard reported PASSED in-sweep and FAILED correctly in isolation.

Use `gzkit.mutation_witness.run_mutation_sweep`, which verifies baseline, activation, isolation and failure cause and returns the four-way verdict; do not hand-roll a shell loop, which is the shape that produced the collision. A kill may be required to name a covering test via `Mutation.expected_tests` — without it, a failure elsewhere in the suite counts as coverage this guard does not have.

```bash
uv run python -c '
from pathlib import Path
from gzkit.mutation_witness import Mutation, run_mutation_sweep
s = run_mutation_sweep(Path("."), Path("src/gzkit/<module>.py"),
    [Mutation(find="<guard>", replace="<broken>", label="<name>",
              expected_tests=["<covering test>"])],
    ["uv", "run", "-m", "unittest", "tests.<module>", "-v"])
print(s.killed, s.survived, s.invalid, s.inconclusive, s.is_conclusive)'
```

Only a sweep whose `is_conclusive` is true may be cited as evidence about coverage; a sweep carrying `invalid` or `inconclusive` rows reports what it could not grade, and those rows are disclosed rather than dropped.

### Verification exit-code integrity — the measured instances (GHIs #589, #940, #1008, #970, #969)

**Verification exit-code integrity (binding, GHI #589).** A verifier's truth is its own exit code, never a downstream filter's. NEVER pipe `unittest`/`behave`/`mkdocs --strict` (or any ARB-wrapped verifier) through `tail`/`head`/`grep`/`Select-Object`: the shell reports the *last* process's exit (the filter's — always 0), masking a failing suite as a green run. Capture to a file (`> out.log 2>&1`) and read the ARB receipt's `exit_status` (GHI #317). A harness "exit code 0" notification on a piped command attests the filter, not the verifier.

**The sequence form masks identically (GHI #940).** The rule is about the LAST thing the shell runs, not about the pipe character. `verifier > log; tail log` discards the verifier's status exactly as `verifier | tail` does — the shell reports the last *statement* just as it reports the last *stage*. Fixing this by naming `tail`/`head`/`grep` would repeat the enumerate-the-examples miss the clause already made once: `verifier > log; echo done` masks just as completely. Two remedies, and they are **not interchangeable** — `set -o pipefail` fixes a pipe and does nothing for a sequence; `set -e` aborts a sequence and does nothing for a pipe. Reading `$?` in the statement *immediately* after the verifier is the third route, and immediacy is load-bearing: `$?` reports whatever ran last, so a read placed after an intervening statement reports that statement instead and only looks like evidence. `&&` carries a failure to the END of its chain, so the separator that decides is the one ending the chain, not the verifier's own (GHI #971): `verifier && ok` reports the failure, but `verifier && ok; ls` and `verifier && ok || echo x` both exit 0, and `set -e` rescues neither (POSIX suppresses errexit for a non-final command in an AND-OR list). Read `$?` immediately after the chain — when it short-circuits, `$?` IS the verifier's status. Under `pipefail` a verifier in any pipeline stage carries its status to the statement's end the same way. After `&`, `$?` reads the background LAUNCH (0), never the verifier: run a verifier in the foreground.

**A group is one command (GHI #1008).** `( … )` and `{ …; }` report their last statement, so a grouped verifier is read exactly as a bare one: `(verifier); ls` and `(verifier; ls)` both exit 0 over a failure, while `(cd x && verifier)` reports it. `set -e` or `pipefail` set inside `( … )` does not outlive it. errexit is suppressed for every command inside a group that is not last in its AND-OR list — `set -e; (verifier; ls) || echo x` exits 0 — so read `$?` inside the group instead. A heredoc body, a reserved-word prefix and `$( … )` stay declared limits (GHI #1013, #1012).

**The `||` branch announces, it does not report (GHI #970).** `verifier || echo failed` exits 0 *exactly when* the verifier failed: the branch runs on failure and then replaces the failing status with its own. Announcing and reporting are different claims — anything reading the status rather than the transcript sees green, and a Step-4a packet is a CURATED excerpt, so the announcement can simply not be pasted (measured 2026-09-06: such a packet verified with zero blockers). The remedy is neither `pipefail` nor `set -e` — the shell suppresses errexit for a command left of `||` — but the branch itself: `verifier || echo "REAL EXIT: $?"`. The verdict idiom stays permitted, and the arm's canonical scope is what saves it: `test -f x && echo DEFECT || echo OK` exits non-zero when the assertion HOLDS and runs no verifier.

**The aggregate status is a floor, not a proof.** Even a correctly-written `verifier > out.log 2>&1; echo "REAL EXIT: $?"` still *exits* with the last statement's code, so a harness summary that reports only the aggregate can still announce success over a red suite. The shell-level rule makes the truth visible in the output; it cannot make a notification line carry it. For attestation, cite the ARB receipt's `exit_status` — the only channel that carries the verifier's own result out of the shell. Tracked at GHI #969 — a declared limit with no open destination is an untrackable defect (AGENTS.md § PRIME DIRECTIVE #6).

**Mechanized** by the `verifier-pipe-gate.py` PreToolUse hook over `Bash` (decision: `gzkit.verifier_pipe_gate.decide`; live negative control `verifier-exit-status-masked`). The gate refuses a verifier in any *non-final* pipeline stage — the masking is the pipe, not the filter's identity, so `gz check | cat` is the same defect as `gz check | tail` and both are refused. Two escapes are permitted because they genuinely preserve the status: `set -o pipefail` and reading `${PIPESTATUS[0]}`. The verifier set is READ from `CANONICAL_STEP_COMMANDS` (AGENTS.md § Attestation), so a canonical step added there is covered without a second edit.

### REQ Scope Discipline — what it replaced

### What this replaces

Before ADR-0.0.59: every REQ used the BEHAVIOR proof channel uniformly, producing
tautological filesystem-grep tests for content REQs (32% project-wide / 42% governance).
SUPPORT-kind REQs are now witnessed by the ledger + structural validator; no `@covers`
test is required or appropriate for them — authoring one is the anti-pattern this rule
names.


## Origin

GHI #327 — instructions-files-diet pass (initial lift + 2026-05-07 expanded lift). GHI #921 — 2026-09-17 lift from rule `0.25.0` (section above).
