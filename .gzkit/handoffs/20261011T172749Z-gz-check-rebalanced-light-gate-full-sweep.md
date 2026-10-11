---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-11T17:27:49Z'
agent: claude-code
session_id: c7db117d-bd4b-4172-808b-5a9519f934f4
continues_from: .gzkit/handoffs/20261011T101943Z-patch-release-repairs-made-return-to-feature-work.md
---

## Current State Summary

The operator raised a new concern on resume: `gz check` was too heavy for how often it runs. It is rebalanced, in three commits, and both issues are closed as fixed.

- Plain `uv run gz check` is the per-change gate: lint, format, typecheck, every validator, the smoke tier and the tests the change touches. The pre-push hook runs it.
- `uv run gz check --full` adds the whole unit tier, `Behave`, the docs build, `Preflight` and the guard-canary sweep. It runs in CI on every code push, at every release and as the `quality-check` chore.
- The `--fast` flag is retired and is a usage error.
- The scope policy ships inside the gzkit package, so a project that installs gzkit runs the same per-change gate.

Commits: 701d01506 (GHI #1191), c7b643dfe (GHI #1192), 95dcf448d (tests for both). CI passed on ubuntu-latest and windows-latest for all three. main was even with origin at e0db9cd13 when this was written; this handoff and one insight record are uncommitted. Nothing is in flight: no active pipeline, no active OBPI, no open TASK, no locks, no Gate 5 awaiting attestation.

Measured on one developer host, 2026-10-11 (a record, not a budget): `gz check` took 135s before; after, 42s on the wide fix change and about 17 to 20s on ordinary changes. `gz check --full` took 156s. The unit tier alone took 97s.

## Important Context

- Scope policy: `src/gzkit/check_step_scopes.json`, read through `importlib.resources` by `_check_step_scopes_file` in `src/gzkit/commands/quality.py`. A scope names the steps it drops. When `Test` is dropped, `Test (changed)` runs in its place.
- `Test (changed)` selects tests by filename match and also diffs against the upstream branch. During GHI #1192 it missed two failing tests that assumed a scratch project has no scope policy; `gz check --full` caught them before the push. Run `--full` before pushing a change whose effects reach tests not named after the module.
- Why the suite had tripled: one test ran the whole guard-canary kill sweep, about 118s alone. The sweep is now the `Guard canary sweep` step of the full scope; the cheap binding check stays in the unit tier. The rest of the growth is subprocess-heavy governance tests and is not repaired.
- `gz patch release` pushes only behind `gz check --full`.
- `data/check_step_concurrency.json` stays gzkit-only on purpose, so an installed project runs its steps serially.
- ADR-0.39.0's design record still lists the scope file among the `data/` settings to migrate. The file has left `data/` and `data/config_registry.json`; the Draft briefs were not edited, because briefs are the operator's.
- Shell hook: a verifier such as `gz check` must not be piped or followed by another statement. Redirect to a log and read the log.
- Workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-09-20.md`, section Workflow fronts). Session delta, observed 2026-10-11:
  - handoff system: the previous handoff was resumed and no ruling was booked on it; the operator redirected to this concern without saying proceed or hold. Not otherwise inspected.
  - ghi triage: GHI #1191 and GHI #1192 were filed and closed here. `gh issue list --state open` returned 74. The queue was not triaged.
  - adr/obpi campaign: unchanged. `uv run gz adr status ADR-0.35.0` shows 10/20, closeout BLOCKED.
  - new R&D: not touched and not inspected this session.

## Decisions Made

- [operator-ruled] The push gate drops to the light shape, CI stays per-push, and full QC runs at OBPI completion, release and as a chore (verbatim: "A, and first find out why the suite tripled", on the option worded "the table above — push gate drops to the fast shape, CI stays per-push, full QC at OBPI completion, release and chore.").
- [operator-ruled] The guard-canary kill sweep runs in the full tier, not the unit suite (verbatim: "move the canary sweep to the full tier").
- [operator-ruled] The rebalance is one GHI repaired directly, GHI #1191 (verbatim: "yes, file the GHI and direct fix").
- [operator-ruled] The `AGENTS.md` Execution Rules line drops two conditions of its old wording, C2 and C4 of landing-20261011T144517Z-1a7a9970 (verbatim: "I attest dropping C2 and C4").
- [operator-ruled] Installed projects get the per-change gate too, repaired directly as GHI #1192 (verbatim: "adopters get the light gate too; direct fix 1192").
- [operator-ruled] The `guard-canary-sweep` canary is a fair test and its review is recorded (verbatim: "fair test, record it").
- [agent-chose] Retired `--fast` instead of keeping two names for one scope.
- [agent-chose] Shipped the scope policy in the package, on the precedent of `src/gzkit/quality_command_timeout.json` (GHI #1143), instead of delivering it through `gz init`.
- [agent-chose] Raised the `quality-check` chore timeout to 900s after one loaded run took 514s.
- [agent-chose] Booked no `gz handoff decide` ruling on the resumed handoff, because the operator said neither proceed nor hold.

## Immediate Next Steps

1. Present this handoff to the operator and take their ruling on what to draw next. Execute nothing before it.
2. If the operator returns to feature work: `ADR-0.35.0` item 15, `OBPI-0.35.0-15-pipeline-run-position`, which the operator initiates through gz-obpi-pipeline. Confirm the landed count with `uv run gz adr status ADR-0.35.0` first.
3. If this handoff and the insight record are still uncommitted, ask the operator before syncing them.
4. Put an open item from Pending Work to the operator only when asked, and one at a time.

## Pending Work / Open Loops

- Everything in the Pending Work of the handoff of 2026-10-11T10:19Z stands.
- A project gzkit scaffolds has no CI, so nothing runs its whole unit tier on push. Whether `gz init` should scaffold a CI workflow is the operator's call and has no issue. Recorded in the close comment of GHI #1192 [settled].
- Changed-test selection is a filename heuristic. What it selects in a project whose tests are not named after its modules is unmeasured. Recorded in the close comment of GHI #1192 [settled].
- The unit tier's remaining cost sits in subprocess-heavy governance tests. Recorded as an insight under scope "unit tier wall time"; no issue.
- ADR-0.39.0's Draft briefs still list the scope file among the `data/` settings to migrate.
- A broken docs link is now reported by CI, not before the push, as ruled under GHI #1191 [settled].
- Two unexplained multi-minute stalls on the developer host on 2026-10-11. Recorded as an insight under scope "developer host stalls".
- Open and untouched: GHI #1154, GHI #1171, GHI #1144, GHI #1138, GHI #1034.

## Verification Checklist

- `git status -sb` and `git log --oneline -5`: main at or ahead of e0db9cd13; 701d01506, c7b643dfe and 95dcf448d are the fix commits.
- `gh issue view 1191 --json state` and `gh issue view 1192 --json state`: both CLOSED.
- `uv run gz check` with its output redirected to a log: passes, and its closing message names the dropped steps and `gz check --full`.
- `uv run -m unittest tests.governance.test_check_step_scopes`: passes.
- `uv run gz obpi lock list`: no active locks.
- `uv run gz adr status ADR-0.35.0`: 10/20.

## Evidence / Artifacts

- `src/gzkit/check_step_scopes.json`
- `src/gzkit/commands/quality.py`
- `src/gzkit/guard_canary.py`
- `tests/governance/test_check_step_scopes.py`
- `tests/commands/test_check_changed_tests.py`
- `tests/adr/test_patch_release_full_sweep.py`
- `.gzkit/chores/quality-check/CHORE.md`
- `.gzkit/rules/tests.md`
- `.gzkit/skills/gz-check/SKILL.md`
- `docs/user/manpages/check.md`
- `docs/governance/agent-contract-rationale.md`
- `data/guard_canaries.json`
- `.gzkit/renditions/AGENTS.md/root.retention.json`
- Commits 701d01506, c7b643dfe, 95dcf448d; sync commits d95bd5766 and e0db9cd13.
- CI runs 38149866539, 38151193893 and 38153117807, each green on both platforms.
- Falsifiability receipts arb-red-commit-701d015067c5-dd25d3a73f1d41df874a197373032172 and arb-red-commit-c7b643dfe764-7d839a374a7347e5ae3ca366cdb51a9c. Both reported undriven; the surviving rows were then covered by the tests in 95dcf448d or accounted for in the close comments.
- Corpus landing landing-20261011T144517Z-1a7a9970.

## Settled Rulings

1465 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
