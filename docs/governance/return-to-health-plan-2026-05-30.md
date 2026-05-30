# Return to Health Plan, 2026-05-30

Status: Active canonical recovery plan.

This plan replaces the prior emergency framing documents, which were removed on
2026-05-30 so they no longer compete for authority:

- `docs/governance/get-out-of-jail-plan-2026-05-23.md`
- `docs/governance/get-out-of-jail-extensions-2026-05-23.md`
- `docs/governance/june-2026-road-to-salvation.md`
- `.claude/plans/rescue-and-repair-roadmap-2026-05-27.md`
- `docs/governance/model-regression-deep-dive-2026-05-23.md`

Those documents captured real distress signals, but their tone and sequencing
kept the project in emergency mode. The recovery posture now is narrower: make
the repo healthy, keep it healthy, and stop expanding governance surfaces until
the harness is green. The model-regression deep dive contributed durable
diagnosis, but its dated command snapshot is superseded by the baseline below.

## Current Baseline

Observed on 2026-05-30:

- `git status --short` is clean.
- `uv run gz check` fails.
- Passing gates include lint, format, typecheck, behave, skill audit, parity,
  readiness, CLI audit, unscoped rules, ADR status freshness, interview
  transcripts, receipt shape, orientation freshness, instruction budget,
  AGENTS.md map conformance, complexity doctrine links, complexity thresholds,
  REQ kind discipline, and surface fidelity.
- Failing gates are concentrated in six surfaces:
  - unit test failure caused by malformed insight records
  - `--kind-invariance`
  - `--insights-shape`
  - `--tautological-test-audit`
  - `--task-envelope-coherence`
  - `preflight`

This is not a collapse. It is a red harness with named failure surfaces.

## Definition of Healthy

gzkit is healthy when all of these are true:

- `uv run gz check` exits 0 on `main`.
- A fresh agent can identify the next recovery action without reading more
  than one recovery plan.
- No open `emergency`-labeled issue remains.
- Current failing gates have either been fixed or routed to active tracked work
  with a named owner and next command.
- Known passive-ceremony risks are either mechanized or represented by active,
  ranked GHIs with the next verification command named.
- New doctrine, new foundation ADRs, and new validators are frozen unless they
  directly repair a failing gate.
- Recovery work reduces always-loaded context or check failures; it does not add
  broad new process.

## Merged Deep-Dive Findings

The retired 2026-05-23 model-regression deep dive leaves these facts in the
active plan:

- The recovery frame is not "newer models are worse." The class of failure is
  under-mechanized governance ceremonies and excessive always-loaded context;
  model behavior exposes those weaknesses rather than explaining them away.
- `gz-obpi-pipeline` remains the comparison target for trustworthy ceremonies:
  staged runtime, explicit verification, human gate, guarded sync, and
  fail-closed boundaries.
- Passive presenter ceremonies, especially closeout and audit workflows, must
  move toward observed runtime checks or stay explicitly routed through GHIs
  such as #516 and #517.
- Validators that claim runtime health must execute or otherwise prove the
  runtime path that matters. The Codex SessionStart cache-pin fix from GHI #510
  is the precedent: authored wiring was not enough.
- `gz check` triage must show fail-closed blockers before advisory bulk. Large
  advisory drift lists are useful only after the exit-code cause is visible.
- Generated mirrors should not multiply diagnostics. Check canonical sources
  first, and collapse or exclude mirror duplicates when reporting skill-script
  and BDD-step findings.

## Operating Rules

1. One active plan. This file is the plan.
2. Green first. Do not start new feature, doctrine, or evaluator work while
   `uv run gz check` is red.
3. Prefer direct fixes for current gate failures when the defect-fix routing
   thresholds allow it.
4. Use existing GHIs for tracked defects. File new GHIs only when the defect is
   not already tracked and cannot be fixed in the current pass.
5. No model-centered rescue framing. Model choice is an implementation detail;
   mechanical gates are the recovery mechanism.
6. No new foundation ADRs during recovery unless the operator explicitly
   approves one after seeing the routing facts.
7. Treat context as a budgeted runtime dependency. Keep always-loaded prose to
   hard invariants, routing pointers, and task entrypoints.
8. Every recovery session starts with:
   - `git status --short`
   - `uv run gz check`
   - `gh issue list --state open --label emergency --limit 20`

## Phase 1: Make the Harness Green

Goal: `uv run gz check` exits 0 without weakening gates.

Known work:

- Fix `.gzkit/insights/agent-insights.jsonl` lines 133 and 134 so they conform
  to `InsightRecord`: include `type`, and make `evidence` a list.
- Add the missing `## Why foundation tier?` section to
  `ADR-0.0.65-handoff-system-consolidation`.
- Clean orphan plan-audit receipts using the runtime-supported preflight path.
- Resolve the four tautological-test audit findings by rewriting or routing the
  tests, not by suppressing the audit.
- Resolve `--task-envelope-coherence` separately. It touches ledger semantics
  and should be treated as the highest-risk failing gate.
- When `gz check` fails, record the first fail-closed blocker and its drilldown
  command before reading advisory output.

Exit criteria:

- `uv run gz test` passes.
- `uv run gz validate --kind-invariance` passes.
- `uv run gz validate --insights-shape` passes.
- `uv run gz validate --tautological-test-audit` passes.
- `uv run gz preflight` passes.
- `uv run gz validate --task-envelope-coherence` passes or has a single active
  tracked remediation with the next command named.

## Phase 2: Reduce Context Load

Goal: stop the recovery process from exhausting agent context.

Work:

- Keep this file as the only active recovery plan.
- Keep superseded recovery docs as short pointers only.
- Do not re-expand `AGENTS.md` or skill bodies while recovery is active.
- Prefer `gz context <ADR-ID>` over broad manual reading when working on a
  specific ADR.
- Keep `AGENTS.md` as a map, not an encyclopedia: move explanatory doctrine to
  routeable docs or skills only when an existing validator or command preserves
  the invariant.
- Replace always-loaded prose with runtime checks where a check can carry the
  same safety property.
- Treat issue #519 as the context-load tracking issue until closed.

Exit criteria:

- No recovery document besides this file claims canonical status.
- A session can orient from `AGENTS.md`, this file, `gz status`, and `gz check`
  without reading the old emergency plans.

## Phase 3: Repair State Drift And Ceremony Runtime Checks

Goal: stop lifecycle, task state, and core ceremonies from presenting false
confidence.

Work:

- Treat `--task-envelope-coherence` as the representative failure.
- Keep coarse TASK bookends only if they do not pretend to be fine-grained work
  attribution.
- Add or repair `task_id` propagation only through the runtime path that emits
  worklog events.
- Do not edit `.gzkit/ledger.jsonl` directly.
- If historical ledger drift needs accommodation, implement it as a validator
  rule or migration command with tests.
- Use `gz-obpi-pipeline` as the mechanical bar when evaluating closeout,
  authoring, evaluation, and audit ceremonies.
- Keep GHI #516 and GHI #517 as the route for passive-presenter ceremony gaps
  unless a specific defect qualifies for direct-fix routing.
- Prefer execution probes over wiring checks when a validator claims a hook,
  generated config, or command path is healthy.
- Do not add prose-only ceremony instructions as remediation for skipped
  verification.

Exit criteria:

- `gz check` includes a passing task-envelope check.
- New worklog events emitted under active TASKs carry the expected attribution.
- Historical exceptions, if any, are explicit and mechanically bounded.
- Known high-risk passive-ceremony gaps have either runtime checks or an active
  GHI route with a concrete next command.

## Phase 4: Drain Recovery Issues

Goal: reduce tracked recovery debt without creating a larger planning surface.

Work order:

1. Emergency-labeled GHIs.
2. Runtime-labeled defects that affect `gz check`, closeout, pipeline, or
   context loading.
3. Tech-debt findings that currently fail promoted validators.
4. Advisory or enhancement work only after the above are green.

Rules:

- Keep WIP to one recovery issue at a time.
- Close issues only with observed command evidence.
- Do not batch unrelated fixes under a recovery umbrella.

Exit criteria:

- No open `emergency` issues.
- Recovery issue count is decreasing week over week.
- Same-day issue creation does not exceed same-day issue closure during recovery.

## Phase 5: Resume Normal Development

Normal development resumes only after health is restored.

Before resuming:

- Run `uv run gz check`.
- Run `gh issue list --state open --label emergency --limit 20`.
- Confirm this file's closeout section has been filled in.
- Archive or delete obsolete sidecar recovery notes that no longer carry facts
  needed for audit.

## Recovery Closeout

Fill this section when complete:

```text
Recovery closeout date:
uv run gz check:
Emergency GHIs open:
Context-load issue state:
Task-envelope coherence:
Open recovery issues:
Decision: normal development may resume / may not resume
```
