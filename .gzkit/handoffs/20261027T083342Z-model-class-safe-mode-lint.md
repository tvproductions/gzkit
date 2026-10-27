---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-27T08:33:42Z'
agent: claude-code
session_id: 98cf1de4-25e5-4f09-b70d-f05989cfaeee
continues_from: .gzkit/handoffs/20261027T010924Z-uv-floor-mx-traps-stop-hook.md
---

## Current State Summary

Session of 2026-10-26/27, safe mode open throughout (contract docs/governance/harbor-pilotage-candidate-2026-10-15.md). Four threads landed and are pushed (origin/main in sync at 494d3f584):

1. /doctor cleanup (user-scope only, nothing checked in): removed the duplicate Homebrew cask claude-code@latest, updated the native install to 2.1.311, disabled the unused code-review, skill-creator and playwright plugins in ~/.claude/settings.json, and disabled the claude.ai Claude Docs connector for this project in ~/.claude.json. Backups at ~/.claude/settings.json.doctor-bak and ~/.claude.json.doctor-bak. cowork-plugin-management is still to be turned off by the operator via /plugin.
2. GHI #1284 filed, fixed and closed as fixed: .gzkit/rules/model-selection.md (now 0.8.0) names models by class, never a versioned ID. New default-tier validator gz validate --model-class-only over .gzkit/rules, .gzkit/skills and .gzkit/agents, with negative control NC:model-class-only, guard canary model-class-only (operator reviewed: "all is well"), scorecard row 52c and manpage section. Commits 75d6d2c8f and deef91410.
3. Operator correction on safe-mode lint (insight 2026-10-27T08:18:18Z): sweep commit 0d8831595 cleared the 757ddea7e lint debt and the RO-0 lint punch line; arming commit e560b92e5 kept lint and the fast static checks on in safe mode (complexity ceiling and cheap surface-fidelity hooks off the alarm switch, a new whole-tree lint-pre-push hook, CRITICAL pins by LEVEL, mx-mode 1.14.0 and the doctrine amendments).
4. Two problems found and fixed along the way (operator's words, verbatim):
- Banner drift: the awareness hook's fallback banner had already drifted from awareness.py, so its test was failing before I started. Both now match.
- Constant from Act 1: the config-registry gate flagged the _MIN_ARGS constant I added in the sweep. I replaced it with a check that needs no constant and added a test for the usage error.

uv run gz check exits 0 on main after e560b92e5, Lint included.

## Important Context

- Safe mode no longer means "all alarms off". Lint (per commit, and whole tree at pre-push), the complexity ceiling and the cheap surface-fidelity subset (bullet retention, surface weight, pointer anchors) stay on and are pinned CRITICAL by LEVEL, so the hangar cannot demote them. Still switched off through gzkit.mx.alarms: validator reachability, ledger vocabulary, the gz check pre-push gate, the unittest hook and the verifier pipe gate. Lint and fast-static debt is swept by the act that lints it, never parked on the punch list.
- This settles part of GHI #1273's trap 6 ("full Ruff lint and the cognitive baseline applying in safe mode"): full lint now applies in safe mode by ruling. The cognitive-baseline half and the rest of #1273 stay open.
- The pre-commit runner is not on PATH; it lives in the uv archive Python named in .git/hooks/pre-push (INSTALL_PYTHON). Run hooks by hand with that interpreter: <INSTALL_PYTHON> -m pre_commit run <hook-id> --hook-stage pre-push --all-files.
- GZKIT_MX_FULL_STRENGTH=1 uv run gz validate printed nothing and exited 0 in this session; the full-strength override does not behave as the 2026-10-26 handoff described (that belongs to #1273).
- gz arb red --commit grades only the commit's own test modules, so registration wiring reads "survived" even when repo fences (tests.cli.test_validate_dispatch_consistency) catch it; the punch list already holds it as not a per-act record until #1268 is fixed.
- A new validate scope needs the full registration set: VALIDATOR_REGISTRY entry, validate() parameter (keyword-only after *, to keep the FBT001 ratchet), parser flag and forward, check step and its quality.py runner, _STEP_GUARD_META, qc_binding, check_scope_membership.json (insert without re-sorting), check_step_concurrency.json, negative control plus entrypoint (import by name, not _ep.x, to avoid SLF001), claim exemption and population, guard canary, registry-parity declaration, manpage, scorecard row with NC:<claim> plus source= plus data/advisory_scorecard_identities.json.
- Workflow front this session touched: GHI triage (#1284 filed and closed). The campaign queue in docs/governance/build-to-1.0-campaign-2026-09-20.md was not advanced.

## Decisions Made

- [operator-ruled] Model selection names models by class, not version (verbatim: "ghi the model issue, cleary we should use class of model, not specific version.").
- [operator-ruled] Fix GHI #1284 in this session with a mechanical witness (verbatim: "fix it now, with the validator").
- [operator-ruled] Lint stays on during safe mode (verbatim: "i think, even during repairs or contruction, somebody sweeps up the shop floor every night. The point is, it is too strivt to disable linting during safemode drydock/mx hangar. We are writing/changing code and that deserves").
- [operator-ruled] Scope of that correction: sweep the existing debt and keep every fast static check armed (verbatim choice: "Sweep + all fast static").
- [operator-ruled] Guard canary model-class-only reviewed through gz canary review (verbatim: "all is well").
- [operator-ruled] /doctor cleanup applied in full (verbatim choice: "Clean up everything (recommended)").
- [agent-chose] Pinned the fast static checks by LEVEL, not by NAME in GATE5_INVARIANTS, following mx-mode "Default to LEVEL"; reversible, and the checks are not Gate-5 invariants.
- [agent-chose] Added .gzkit/agents to the --model-class-only scope beside rules and skills, recorded as a contract amendment on #1284.
- [agent-chose] Left records (ledger, handoffs, data provenance fields, data/frontier_model_cards.json) outside the validator: they name the model that did a piece of work and must stay exact.

## Immediate Next Steps

1. Ask the operator whether to resume the contractor-kit R&D through gz-rnd (docs/rnd/contractor-kit.md), carried from the predecessor's step 1: append a decision entry with the operator's words, check the record against git, recompute the frontier.
2. Then the mode contract's syntax: candidate Python affordances for code controls (decorators, typing.Protocol ports, context managers, class registration, entry points), after reading the census and the seven chore --self-test arms.
3. When the operator takes up GHI #1273, carry the 2026-10-26 trap table and the report-only ruling, plus today's ruling that full lint applies in safe mode (trap 6, lint half settled), and the observation that GZKIT_MX_FULL_STRENGTH=1 printed nothing.
4. Remind the operator to turn off cowork-plugin-management via /plugin (the one /doctor action left to them).

## Pending Work / Open Loops

- GHI #1273: MX-system review; lint half of trap 6 now settled by the 2026-10-27 ruling, the cognitive-baseline half and traps 3 and the marker's place in git remain.
- GHI #1268: arb red --commit grading; the commit witness stays off the per-act record until it is fixed (RO-0 punch line 2).
- GHI #1263: parked; the reference patch no longer applies cleanly to main.
- RO-0 punch list line 1: four alarm hooks (validator reachability, ledger vocabulary, gz check pre-push, unittest) and the verifier pipe gate remain off until exit.
- advisory-rules-audit Coverage Ledger: mx-mode.md is scored at 1.10.0 while the rule is now 1.14.0; clauses since 1.10.0 are unscored (the advisory-scorecard guard reports it).
- 11 older CI unit-test failures, not yet checked against the punch list or any GHI (carried).
- The safe-mode lease runs to about 2026-10-28T01:07Z; advisory debt keeps aging (about 240h at last read).

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0.
- uv run gz check exits 0 (Lint included).
- uv run gz validate --model-class-only exits 0.
- uv run -m unittest tests.mx.test_alarms tests.governance.test_audit_model_class_only tests.hooks.test_mx_awareness passes.
- gh issue view 1284 --json state reads CLOSED.
- grep -n "gzkit.mx.alarms" .pre-commit-config.yaml lists only validator-reachability-ratchet, ledger-vocabulary-inertness, gz-check-pre-push and unittest entries (plus the header comment).

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/model_class.py`, `tests/governance/test_audit_model_class_only.py`: the --model-class-only validator and its tests (75d6d2c8f, deef91410).
- `.gzkit/rules/model-selection.md` (0.8.0), `docs/user/manpages/validate.md`, `docs/governance/advisory-rules-audit.md` (row 52c), `data/guard_canaries.json`.
- `src/gzkit/mx/alarms.py`, `src/gzkit/hooks/scripts/quality.py`, `.claude/hooks/verifier-pipe-gate.py`, `data/ruff_baseline.json`: the lint sweep (0d8831595).
- `.pre-commit-config.yaml`, `src/gzkit/commands/validate_cmd.py`, `src/gzkit/commands/quality.py`, `tests/mx/test_alarms.py`: arming (e560b92e5).
- `src/gzkit/mx/awareness.py`, `src/gzkit/hooks/scripts/mx.py`: banner and its fallback now match.
- `.gzkit/rules/mx-mode.md` (1.14.0), `docs/governance/safe-mode-doctrine.md`, `docs/governance/harbor-ro10-safe-mode-classification.md`, `docs/governance/harbor-pilotage-candidate-2026-10-15.md`, `docs/governance/rule-version-history.md`.
- `.gzkit/insights/agent-insights.jsonl`: insight 2026-10-27T08:18:18Z (scope safe-mode-alarms).
- ARB receipts: `artifacts/receipts/arb-red-commit-75d6d2c8fe3f-ff9a16fde5584d88b82d9c1b6e77e2bd.json`, `artifacts/receipts/arb-red-commit-deef91410997-c77a1196054148388e7dd96ef80a14d6.json`.

## Settled Rulings

1764 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
