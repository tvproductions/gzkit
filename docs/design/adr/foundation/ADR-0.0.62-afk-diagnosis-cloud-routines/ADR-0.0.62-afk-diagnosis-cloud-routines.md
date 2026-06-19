---
id: ADR-0.0.62-afk-diagnosis-cloud-routines
status: Draft
kind: foundation
semver: 0.0.62
lane: lite
parent: PRD-GZKIT-1.0.0
date: 2026-05-25
promoted_from: ADR-pool.cloud-agent-routines
inspired_by: "Andy Dev Dan — five-pillar agentic engineering framework (agent harness, software factory, extensible software, always-on agents, agentic access)"
complements:
  - ADR-0.0.60-harness-fitness-report
  - ADR-0.0.61-harness-factoring-minimal-init
  - ADR-pool.doc-gardening-scheduled-chore
  - ADR-pool.managed-agents-outcome-integration
---

# ADR-0.0.62-afk-diagnosis-cloud-routines: AFK-Diagnosis via Cloud Routines

## Persona

**Active persona:** `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Treats unsupervised execution as a doctrine problem first, an automation problem second: the wrong shape ships escape-hatches for vibing into the L2 ledger; the right shape ships defense-in-depth that fails closed at three independent enforcement points.

## Why foundation tier?

**Invariance test:** Without this ADR, would the project still be the project? **Yes** — gzkit remains a governance kit. But the *AFK-detection-vs-AFK-action* doctrine boundary is itself a foundation-level constraint: a kit that allows unsupervised agents to mutate state outside the L2 ledger is structurally a different kit, regardless of how well the action is governed. The invariance is *unsupervised execution is diagnosis-only*. This ADR establishes that boundary; future ADRs (doc-gardening, R-4 sync-check on PR-merge) extend it only by deliberate operator-attested decision.

**Port-vs-adapter framing:** This ADR is a **port** — it defines the abstract `Routine` contract (cadence trigger, exec whitelist, diagnosis-only invariant, ledger event shape) that any AFK-execution substrate (Claude Code routines, future cron/GitHub-Actions/equivalent) must honor. The Claude Code routines substrate is the inaugural **adapter**; substrate-swap is preserved as the recovery surface if the preview-tier feature is deprecated.

## Intent

**Before (today):** Governance drift is silent between operator sessions. ADR status indexes go stale; ledger state diverges from on-disk canon; trust audit violations accumulate; control surface mirrors fall out of sync; session handoffs age past usefulness; technical debt accrues unreviewed. Today these are caught reactively — when an operator lands on the drift during a session — rather than proactively. The cost is **context burn** (diagnosing drift instead of doing work) and **confidence erosion** (the operator cannot trust derived views without first auditing them).

**After (this ADR):** A cloud-scheduled routine fires on operator-defined cadence, runs gzkit's existing mechanical validators headlessly, files a GHI on drift detection, and emits a structured `RoutineExecEvent` that the operator pulls into the local ledger via attested reconcile. The operator returns from AFK to **findings already surfaced**, not drift to diagnose. Context arrives pre-investigated.

**Scope (inaugural shape):** One inaugural routine — **R-3 Trust Audit Suite** running `gz validate --documents --surfaces --advisory-scorecard --cli-alignment` (four validator scopes already production-ready in gzkit and exit-code clean in a headless environment). One new noun namespace (`gz routine`) with seven CLI subcommands. One pluggable `ROUTINE_REGISTRY` (content-addressable by `.gzkit/routines/<name>.yaml`) so future routines (R-1, R-2, R-4, R-5, R-6) plug in via separate ADRs without restructuring this one. One new ledger event class (`RoutineExecEvent` with `recorder_source: str` field). Three independent defense-in-depth enforcement points for the diagnosis-only invariant.

**Anti-vibing constraint (binding, three-layer):** Routines DETECT and REPORT; they NEVER REMEDIATE. The constraint is enforced at three independent fail-closed points:

1. **Schema layer.** `Routine.diagnosis_only: Literal[True]` — Pydantic type-level. A `.yaml` setting `diagnosis_only: false` fails to parse; `gz routine validate` exits 3.
2. **Exec wrapper layer.** `gz routine exec` runs each command through a guarded subprocess wrapper with prefix-match whitelist (`gz validate`, `gz check`, `gz status`, `gz state`, `gz routine results`, `gz issue file` only). Unknown command prefix exits 3 before subprocess invocation.
3. **Hook layer.** New pre-commit hook `forbid-routine-mutation` checks for `GZKIT_ROUTINE_CONTEXT=1` in commit environment; if present, exit 3.

Defense-in-depth is required because routines run **on Anthropic infrastructure, not the operator's machine**. The operator cannot directly audit what the routine does at runtime — the schema layer prevents authoring mistakes, the exec wrapper prevents misuse via routine definition, the hook prevents misuse via subagent escape. Cloud→local L2 push is forbidden; cloud emits a `RoutineExecEvent` to stdout (captured in GHI body), local L2 writes happen only via operator-attested `gz routine reconcile --apply`.

**Beta-tier acceptance (binding):** Claude Code routines is in research preview (`experimental-cc-routine-2026-04-01` beta header). This ADR explicitly accepts preview-tier stability as the substrate. If Anthropic changes the routine config schema or deprecates the feature, `gz routine deploy` regenerator is the operator's recovery surface; the `gz routine exec` headless contract is substrate-independent and survives feature deprecation as a cron / GitHub Actions fallback (future ADR). The substrate dependency is **stamped, not hidden**.

**Factory metric:** time-from-drift-onset-to-operator-awareness. Today: unbounded (drift surfaces only when an operator's `gz check` hits it). Target with cadence=daily: ≤24 hours, with GHI as the operator-readable artifact.

## Decision

### Architectural precedents and exemplars

This ADR composes three established patterns rather than inventing new ones; the implementation OBPIs reuse existing gzkit machinery wherever possible.

- **Precedent — pluggable surface registry ([ADR-0.0.60](../ADR-0.0.60-harness-fitness-report/ADR-0.0.60-harness-fitness-report.md)).** ADR-0.0.60 established a pluggable `Surface` registry for fitness metrics with one inaugural entry (`lane-latency`). This ADR is the **exemplar reuse**: identical registry-with-inaugural-entry pattern, identical "future entries land as separate ADRs" extensibility model.
- **Precedent — canonical-surface class-classifier ([ADR-0.0.32](../ADR-0.0.32-canonical-surfaces-bytewise-byparity/ADR-0.0.32-canonical-surfaces-bytewise-byparity.md)).** The five existing canonical surfaces (skills, rules, personas, templates, chores) all carry classifier helpers (`_classify_*_file`) that route content between canonical/package_only/runtime_state classes. This ADR adds `.gzkit/routines/` as the sixth canonical surface with the same classifier shape — no new doctrine, just one more surface in the existing taxonomy.
- **Precedent — `gz issue file` provenance trailer ([gh-cli.md](../../../.claude/rules/gh-cli.md) v0.2.0).** `gz issue file` already cross-repo files to `tvproductions/gzkit` with auto-stamped provenance. This ADR adds an `--idempotency-key` flag to the existing command (reuses the cross-repo plumbing); routine-emitted GHIs use the `RoutineExecEvent.id` ULID as the key, preventing duplicate fires on retry.
- **Precedent — operator-attested ledger mutation (AGENTS.md § Never #2).** Existing rule: "Do not modify the ledger directly (use gzkit commands)." This ADR's cloud→local trust transition via `gz routine reconcile --apply` is the exemplar application: a gzkit command stamps the local append with `local_reconciled_at` + `local_reconciled_by`, preserving operator-attests-L2 even for cloud-originated events.
- **Anti-precedent — local-execution scheduled chores ([ADR-pool.doc-gardening-scheduled-chore](../../pool/ADR-pool.doc-gardening-scheduled-chore.md)).** The doc-gardening pool ADR proposes local `/schedule`-driven chores that open auto-mergeable regenerative PRs. This ADR explicitly rejects auto-mergeable-action as the inaugural substrate — diagnosis-only is the stronger anti-vibing posture. Doc-gardening coexists as a future companion (its `Routine.action` can extend the schema with an `open_regenerative_pr` variant when promoted), not a competitor.

The eight decisions below are ordered by dependency: data shape (1) before CLI surface (2, 3, 4) before integration behavior (5, 6, 7) before substrate acceptance (8). Each item is independently testable per the OBPI decomposition in the Checklist.

1. Add `Routine` Pydantic models, `.gzkit/routines/` canonical-surface class, and `ROUTINE_REGISTRY` content-addressable loader (Decision 1, below) **because** the routine definition shape is the contract every other decision composes against — without it, the CLI surface has nothing to register against and the ledger event has no provenance discriminator.
2. Add `gz routine exec <name>` CLI with three-layer defense-in-depth enforcement (Decision 2) **because** unsupervised execution requires defense-in-depth that fails closed at three independent points — a single enforcement layer is one bug away from a doctrine breach.
3. Add `gz routine list`, `gz routine show`, `gz routine validate` read-only surface (Decision 3) **because** routine introspection must be possible BEFORE deployment to cloud — the operator must be able to verify the routine definition headlessly before pasting into the Claude Code routines UI.
4. Add `gz routine deploy <name>` config generator (Decision 4) **because** the cloud-side integration must be operator-attested — gzkit generates the config, operator pastes it. Automated push to Anthropic API would require credential management gzkit explicitly avoids.
5. Add `gz routine reconcile [--apply]` + `gz issue file --idempotency-key` (Decision 5) **because** cloud-emitted events become L2 truth only via operator-attested local reconcile; the idempotency key prevents duplicate GHIs on routine retry.
6. Add `gz routine results <name>` derived view + `gz status` integration (Decision 6) **because** routine activity must be discoverable on the same operator surface as project status — otherwise routines become an invisible background that the operator stops trusting.
7. Ship `.gzkit/routines/trust-audit-suite.yaml` as the inaugural routine (Decision 7) **because** R-3 wraps four validator scopes already production-ready in gzkit (no new validators introduced); inaugural shipment proves the substrate end-to-end without scope inflation.
8. Accept Claude Code routines preview-tier as the substrate with explicit stamp (Decision 8) **because** preview-tier risk is real (config schema can change, feature can be deprecated); stamping the acceptance + naming the substrate-swap recovery path makes the dependency legible at every closeout.

### Decision 1 — Routine models, registry, canonical surface

`Routine` Pydantic model in `src/gzkit/routines/models.py`:

```python
class RoutineExecStep(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    command: str = Field(..., min_length=1)
    capture_receipt: bool = Field(default=True)

class RoutineTrigger(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    cadence: Literal["hourly", "daily", "weekly", "on_pr_merge"] = Field(...)
    prefer_idle_days: bool = Field(default=False)

class RoutineOnDrift(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    action: Literal["file_ghi", "emit_ledger_event_only"] = Field(...)
    ghi_title_template: str | None = Field(default=None)
    ghi_label: str | None = Field(default=None)
    ghi_repo: str | None = Field(default=None)

class Routine(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    schema_version: Literal["gzkit.routine.v1"] = Field(default="gzkit.routine.v1")
    name: str = Field(..., pattern=r"^[a-z][a-z0-9-]*$")
    description: str = Field(..., min_length=1)
    trigger: RoutineTrigger
    exec: tuple[RoutineExecStep, ...] = Field(..., min_length=1)
    on_drift: RoutineOnDrift
    on_success: RoutineOnDrift
    diagnosis_only: Literal[True] = Field(default=True)
    wall_clock_budget_seconds: int = Field(default=600, ge=30, le=3600)
```

`RoutineExecEvent` in `src/gzkit/ledger_events.py` (additive, no breaking changes):

```python
class RoutineExecEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    event_type: Literal["routine_exec"] = "routine_exec"
    id: str  # ULID
    timestamp: datetime
    recorder_source: str = Field(..., pattern=r"^routine:[a-z][a-z0-9-]*$")
    extra: dict[str, Any]
```

`.gzkit/routines/` canonical surface class with `_classify_routine_file()` mirroring `_classify_skill_file`. `ROUTINE_REGISTRY` is content-addressable: every `.yaml` in `.gzkit/routines/` is loaded; no hardcoded list.

### Decision 2 — `gz routine exec` with three-layer enforcement

```bash
gz routine exec <name>            # human-readable mode (testing)
gz routine exec <name> --json     # one RoutineExecEvent JSON line to stdout (cloud mode)
gz routine exec <name> --dry-run
gz routine exec <name> --no-network
```

Subprocess wrapper:
- Sets `GZKIT_ROUTINE_CONTEXT=1` environment variable
- Enforces whitelist via prefix-match on `RoutineExecStep.command`
- Allowed prefixes: `uv run gz validate`, `uv run gz check`, `uv run gz status`, `uv run gz state`, `uv run gz routine results`, `uv run gz issue file`
- Passes `shell=False` to `subprocess.run` (no shell-metacharacter escape)
- SIGKILLs subprocess on `wall_clock_budget_seconds` overrun
- Captures stdout/stderr/exit-code per command

New pre-commit hook `forbid-routine-mutation`:
- Checks `GZKIT_ROUTINE_CONTEXT` in env at `git commit` time
- Exits 3 if present (belt-and-suspenders against any path that bypasses the wrapper whitelist)

### Decision 3 — Read-only routine introspection

```bash
gz routine list                    # all registered routines + last-run summary
gz routine show <name>             # routine def + recent runs
gz routine validate <name>         # schema parses + headless executability + budget assertion
```

All read-only. Backed by `ROUTINE_REGISTRY` + `.gzkit/ledger.jsonl` events filtered by `recorder_source: routine:<name>`.

### Decision 4 — Routine deployment as operator handoff

```bash
gz routine deploy <name>           # generates Claude Code routine config
gz routine deploy <name> --dry-run
```

Writes to `.gzkit/routines/.deployed/<name>.json` per the `experimental-cc-routine-2026-04-01` beta config schema. Prints multi-line operator-action handoff:

> 1. Open https://claude.ai/code/routines
> 2. Create a new routine (or edit existing)
> 3. Paste the contents of `.gzkit/routines/.deployed/<name>.json`
> 4. Set the routine's secrets: `GITHUB_TOKEN` (scope: `read:repo` on this repo; `issues:write` on `tvproductions/gzkit`)
> 5. Activate the routine

gzkit does NOT push to Anthropic infrastructure on the operator's behalf. Operator-authorizes-external-action preserved.

### Decision 5 — Operator-attested reconcile + idempotency

```bash
gz routine reconcile                # dry-run by default
gz routine reconcile --apply        # actually appends to local ledger
gz routine reconcile --since <commit>
```

Queries `gh issue list --label routine-finding --json id,body,createdAt`. Parses embedded `RoutineExecEvent` JSON from GHI body's fenced code block. Dedups by event `id` (ULID) against local ledger. On `--apply`, appends with `local_reconciled_at` + `local_reconciled_by` extras.

`gz issue file --idempotency-key <key>` extension to existing command: checks `gh issue list --search <key>` before filing; skips dup-fire and returns the existing GHI URL.

### Decision 6 — Results derived view + status integration

`gz routine results <name>` reads `.gzkit/ledger.jsonl` filtered by `recorder_source: routine:<name>`, renders table (last 30 days) + rollup block (total runs, drift detections, GHIs filed, mean wall-clock, reconcile freshness). `--json` returns `RoutineResultsReport`.

`gz status --table` adds a "Most recent AFK-routine activity" line near the bottom of the status header. STALE detection: if no event for >2x cadence, shows STALE warning with last-fire timestamp.

### Decision 7 — Trust Audit Suite inaugural routine

`.gzkit/routines/trust-audit-suite.yaml`:

```yaml
schema: gzkit.routine.v1
name: trust-audit-suite
description: |
  Runs gzkit's trust audit validator suite headlessly. Reports drift as
  ledger events with recorder_source="routine:trust-audit-suite"; files a
  GHI when drift exceeds the trip threshold.
trigger:
  cadence: daily
  prefer_idle_days: true
exec:
  - command: uv run gz validate --documents
  - command: uv run gz validate --surfaces
  - command: uv run gz validate --advisory-scorecard
  - command: uv run gz validate --cli-alignment
on_drift:
  action: file_ghi
  ghi_title_template: "AFK-routine: {routine_name} surfaced {finding_count} drift signal(s)"
  ghi_label: routine-finding
  ghi_repo: tvproductions/gzkit
on_success:
  action: emit_ledger_event_only
diagnosis_only: true
wall_clock_budget_seconds: 600
```

Headless-executability tests live in `tests/routines/test_trust_audit_suite.py` exercising `gz routine exec --dry-run --no-network` and `gz routine validate`.

### Decision 8 — Beta-tier acceptance attestation

Operator-attested acceptance of preview-tier substrate stamped in Gate 5 evidence bundle:

> *"Claude Code routines is preview-tier (`experimental-cc-routine-2026-04-01`). I accept the substrate stability risk and acknowledge that schema changes or feature deprecation are recovered via `gz routine deploy` regeneration + cron/GitHub-Actions substrate-swap fallback."*

The acceptance is the operator's; the recovery surfaces are gzkit's. This decision is the doctrine boundary at which "we use cloud" stops being implicit.

### Layer-3 assertion

The routine-results derived view (`gz routine results <name>`, `gz status` integration) is Layer-3 derived per `docs/governance/state-doctrine.md`. The routine's ephemeral cloud workspace is **Layer-0 (transient, never reconcilable)** — the only L0 surface gzkit interacts with. The GHI body is the **Layer-1.5 trust-bridge** (operator-readable canonical form of the L0 claim). Local-ledger-after-reconcile is L2.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| WEAK: the gz routine substrate is unbuilt (Draft); the inaugural R-3 trust-audit-suite's exec scope (--cli-alignment, one of its four steps) runs green headlessly. | uv run gz validate --cli-alignment | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.0.62-afk-diagnosis-cloud-routines --check | 0 |

## Consequences

### Positive

- **Drift surfaces between sessions.** Time-from-drift-onset-to-operator-awareness drops from unbounded to ≤24 hours (with daily cadence). Operator returns from AFK to GHIs already filed.
- **Three-layer defense-in-depth.** Schema + wrapper + hook = unsupervised execution that fails closed at three independent points. Doctrine breach requires defeating all three.
- **Pluggable registry, content-addressable.** Future routines (R-1, R-2, R-4, R-5, R-6) add `.yaml` files; no code changes needed. Same pattern as ADR-0.0.60's surface registry.
- **Operator-attests-L2 preserved even for cloud events.** `gz routine reconcile --apply` is the trust transition; cloud emits claims, operator ratifies. No silent L2 mutation from cloud.
- **Substrate-independent contract.** `gz routine exec` headless behavior is substrate-neutral. If Claude Code routines is deprecated, cron / GitHub Actions / equivalent can invoke the same command unchanged.
- **Feeds future ADRs.** Routine-produced sessions are inputs to `ADR-pool.managed-agents-outcome-integration`'s Dreams curation; routine-produced events feed `ADR-0.0.60`'s harness-fitness surfaces; the registry is extensible for `ADR-pool.doc-gardening-scheduled-chore`'s eventual `open_regenerative_pr` action variant.

### Negative

- **Preview-tier substrate dependency.** Claude Code routines is `experimental-cc-routine-2026-04-01`. Schema changes or feature deprecation require regeneration via `gz routine deploy` + operator re-paste. Substrate-swap recovery path is the mitigation; the cost is real.
- **GHI tracker pollution risk on cadence misconfiguration.** Routines that detect drift on every run (because the drift is not actionable) accumulate GHIs. Mitigation: `gz issue file --idempotency-key` dedupe + operator-side GHI closeout via `/ghi-close`. Failure mode is observable in GHI tracker volume.
- **Cloud → local latency.** Routine fires at 03:00 UTC; events arrive in local L2 only after `gz routine reconcile --apply`. Operator runs reconcile manually or on cadence (future automation). The latency is bounded by operator behavior, not by the substrate.
- **Authentication blast radius.** Cloud routine carries a GitHub token with `read:repo` + `issues:write` scopes. Token compromise → drive-by GHI flood at `tvproductions/gzkit`. Mitigation: token scope is minimal; operator owns rotation; `gz issue file --idempotency-key` rate-limits real damage.
- **Defense-in-depth surface complexity.** Three enforcement points (schema, wrapper, hook) create three test surfaces and three places maintenance must coordinate. Mitigation: OBPI-02 bundles all three because they fail-closed together; testing them separately wouldn't validate the contract.
- **8-OBPI implementation commitment on top of ADR-0.0.60 (6 OBPIs) and ADR-0.0.61 (7 OBPIs).** Combined surgical-win backlog now 21 OBPIs across three ADRs. Sequencing matters: this ADR's OBPI-02 (exec + enforcement) is the highest-blast-radius single OBPI in any of the three ADRs.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 8
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 8

Baseline-selected uplift from 5 to 8 is justified by surface diversity (models + canonical surface + 5 new CLI subcommands + new ledger event + new pre-commit hook + idempotency extension to existing command + status integration + inaugural routine yaml + docs cluster). Each surface is a distinct testability concern with its own coverage shape; bundling would violate the OBPI right-sizing matrix.

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.62-01: **routine-models-registry-and-canonical-surface** — Pydantic `Routine` models (`diagnosis_only: Literal[True]`) + `RoutineExecEvent` with `recorder_source` field + `.gzkit/routines/` canonical-surface class + `_classify_routine_file` + schema export + `ROUTINE_REGISTRY` loader.
- [ ] OBPI-0.0.62-02: **gz-routine-exec-with-enforcement** — `gz routine exec <name>` CLI with subprocess wrapper whitelist (`gz validate`/`check`/`status`/`state`/`routine results`/`issue file` prefixes only); `GZKIT_ROUTINE_CONTEXT=1` env injection; `--json` emits one `RoutineExecEvent` line; new `forbid-routine-mutation` pre-commit hook (defense-in-depth).
- [ ] OBPI-0.0.62-03: **gz-routine-read-only-commands** — `gz routine list`, `gz routine show <name>`, `gz routine validate <name>`; `RoutineListReport` + `RoutineSummary` models; read-only surface.
- [ ] OBPI-0.0.62-04: **gz-routine-deploy** — `gz routine deploy <name>` generates Claude Code routine config to `.gzkit/routines/.deployed/`; prints operator-action handoff text; explicitly does NOT push to Anthropic infrastructure.
- [ ] OBPI-0.0.62-05: **gz-routine-reconcile-and-issue-idempotency** — `gz routine reconcile [--apply] [--since] [--dry-run]` queries routine-finding GHIs, parses embedded `RoutineExecEvent`, dedups, appends with `local_reconciled_at`/`local_reconciled_by`; `gz issue file --idempotency-key` extension.
- [ ] OBPI-0.0.62-06: **gz-routine-results-and-status-integration** — `gz routine results <name>` Layer-3 derived view + 30-day rollup; `gz status --table` "Most recent AFK-routine activity" line with STALE detection.
- [ ] OBPI-0.0.62-07: **trust-audit-suite-inaugural-routine** — `.gzkit/routines/trust-audit-suite.yaml` (4 validator scopes) + headless-executability tests + GHI template tests + budget assertion.
- [ ] OBPI-0.0.62-08: **afk-routines-docs-and-attestation** — Runbook section, manpages for 7 routine subcommands, threshold/cadence doc, Gate 4 BDD, Gate 5 attestation evidence bundle (incl. beta-tier-acceptance attestation).

## Target Scope (future routines, named-but-deferred)

The inaugural ADR ships only **R-3 (Trust Audit Suite)** as a concrete routine. The remaining five routines named in the pool ADR are explicitly **named-but-deferred** — each lands as its own future ADR that adds a `.gzkit/routines/<name>.yaml` and consumes the existing `ROUTINE_REGISTRY` machinery without code changes.

### R-1. Dependency Freshness Sweep (weekly)

Parse `pyproject.toml` + `uv.lock`, check PyPI ages, flag stale or deprecated dependencies. Emit findings as a GHI or append to `.gzkit/insights/agent-insights.jsonl`. Already planned as S-6 in the harness engineering improvement handoff; this ADR provides the scheduling substrate.

### R-2. Ledger Reconciliation (daily)

Run `uv run gz validate --reconcile-freshness` and `uv run gz register-adrs --all`. Detect Layer 2/3 drift before it compounds across sessions. File a GHI if reconciliation surfaces unresolvable divergence.

### R-3. Trust Audit Suite (daily) — **INAUGURAL, shipped by this ADR**

Run `uv run gz validate --documents --surfaces --advisory-scorecard --cli-alignment`. Catch rule/doc/surface drift that nobody notices until a session hits it. Report violations as a GHI with the full validator output.

### R-4. Control Surface Sync Check (on PR merge to main)

Verify `.gzkit/manifest.json` to mirror consistency. Flag if `gz agent sync control-surfaces` is needed. Triggered by GitHub PR merge event — skill/rule edits that skip the sync step are a recurring failure mode.

### R-5. Stale Handoff Cleanup (weekly)

Flag handoffs in `.gzkit/handoffs/` older than 7 days. Close resolved session-handoff GHIs. The session orientation hook already reads freshness; the routine acts on it.

### R-6. Tech Debt Review (weekly)

Run `gz-tech-debt-review` scoped to commits since last review. Surface debt before it becomes architectural. Emit findings to insights or file as a GHI.

## Open Questions Resolved

The pool ADR carried three open questions; this ADR resolves all three.

1. **Routine-to-ledger provenance.** **Resolved:** `RoutineExecEvent.recorder_source: str = Field(pattern=r"^routine:[a-z][a-z0-9-]*$")`. Routine-emitted events ALWAYS carry `recorder_source`; interactive-session events carry no such field (field-absence is the discriminator). No schema migration; no backfill; forward-additive only.

2. **Failure notification.** **Resolved:** GHI is the primary surface (`on_drift.action == "file_ghi"`); idempotency-keyed to prevent duplicate fires. Notification channels are out of inaugural scope (operator can wire GHI labels into existing notification systems if desired).

3. **ADR status index regen.** **Resolved** (in the pool ADR already; preserved here): wired into `_complete_closeout_pipeline` as a direct code change. Not a routine.

## Q&A Transcript

Design dialogue 2026-05-25 (main-session persona, operator-attested):

**Operator:** Asked to proceed with surgical win #3 — "AFK-diagnosis scheduled-task lane."

**Agent recommendation:** Promote `ADR-pool.cloud-agent-routines` → ADR-0.0.62. Inaugural routine: R-3 Trust Audit Suite (parallels ADR-0.0.60's `lane-latency` inaugural). Pluggable `ROUTINE_REGISTRY`. Beta-tier acceptance for Claude Code routines preview substrate. Framing refinement: "automate recurring governance hygiene" → "AFK-diagnosis" (read-only, never remediate). Routine-to-ledger provenance resolved via `recorder_source: "routine:<name>"` additive field.

**Operator:** Ratified.

**Section 1 (CLI surface):** Operator ratified. 7 new subcommands under `gz routine` noun namespace: `list`, `show`, `exec`, `deploy`, `reconcile`, `results`, `validate`.

**Section 2 (registry + diagnosis-only invariant):** Operator ratified. Three-layer defense-in-depth (schema/wrapper/hook) chosen because routines run unsupervised on Anthropic infrastructure; single-point enforcement is one bug away from doctrine breach.

**Section 3 (headless execution model):** Operator ratified. Pull-mode reconcile (operator-attested local ledger mutation) chosen over push-from-cloud (no cloud writes to L2). GHI body as L1.5 trust-bridge chosen over separate `.gzkit/routine-claims/` directory (preserves GHI as operator-readable canon).

**Section 4 (output rendering):** Operator ratified. 7 CLI outputs sketched (list, show, exec human/json, results, deploy, reconcile, validate). `gz routine deploy` writes config + prints operator-action handoff; does NOT push to Anthropic API.

**Section 5 (OBPI decomposition):** Operator ratified — 8 OBPIs. Defense-in-depth bundled into OBPI-02 (schema/wrapper/hook fail-closed together). Sequencing: 01 → (02, 03, 04, 05 parallel) → 06, 07 → 08.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/routines/test_models.py`, `tests/routines/test_exec.py`, `tests/routines/test_read_only.py`, `tests/routines/test_deploy.py`, `tests/routines/test_reconcile.py`, `tests/routines/test_results.py`, `tests/routines/test_trust_audit_suite.py`, `tests/commands/test_status_routine_integration.py`, `tests/governance/test_forbid_routine_mutation_hook.py`, `tests/governance/test_gz_issue_idempotency.py`
- [ ] Docs: `docs/user/runbook.md` (AFK-diagnosis section), `docs/governance/routines/afk-diagnosis.md`, `docs/user/manpages/gz_routine_list.md`, `docs/user/manpages/gz_routine_show.md`, `docs/user/manpages/gz_routine_exec.md`, `docs/user/manpages/gz_routine_deploy.md`, `docs/user/manpages/gz_routine_reconcile.md`, `docs/user/manpages/gz_routine_results.md`, `docs/user/manpages/gz_routine_validate.md`
- [ ] BDD: `features/routines_afk.feature`
- [ ] Receipts: `arb-validate-*` receipts captured by inaugural `gz routine exec trust-audit-suite` runs
- [ ] Schema: `src/gzkit/schemas/routine.json` exported from `Routine` Pydantic model

## Alternatives Considered

**Routing alternatives (4 rejected):**

1. **Promote `ADR-pool.doc-gardening-scheduled-chore` first.** *Rejected* — local-execution + auto-mergeable regenerative PRs crosses anti-vibing boundary (agents take action). Cloud-agent-routines is detect-and-report only. Doc-gardening coexists as future companion, not inaugural surgical win.
2. **Promote `ADR-pool.managed-agents-outcome-integration` instead.** *Rejected* — explicit pool ADR statement: "Promotion sequencing: routines first (produces sessions), then this ADR (consumes them for evaluation and curation)." Also ~3x scope.
3. **Fresh ADR without pool reuse.** *Rejected* — `cloud-agent-routines` pool ADR encodes the right intent + 6 well-scoped routines + 3 open questions with operator-judgment markers. Pool reuse is the lower-vibing path; same routing decision as ADR-0.0.60 and ADR-0.0.61.
4. **R-2 (ledger reconciliation) as inaugural routine instead of R-3.** *Rejected* — close call. R-2 is mechanically simpler (single `gz validate` scope) but touches `.gzkit/ledger.jsonl` reconciliation, which has higher blast radius if the routine produces a false-positive drift signal. R-3 is read-only validators with no L2 mutation risk. Inaugural-routine choice prioritizes lowest-blast-radius substrate proof.

**Substrate alternatives (3 rejected):**

5. **Self-hosted scheduler (custom Python cron).** *Rejected* — adds runtime dependency and maintenance burden gzkit explicitly avoids. Substrate-swap to cron / GitHub Actions is named as a recovery path if Claude Code routines is deprecated, but is not the inaugural choice.
6. **GitHub Actions as inaugural substrate.** *Rejected for v1* — operator's primary AFK use case is during the Claude Code session-cycle, where Claude Code routines integrate natively. GitHub Actions is the substrate-swap recovery surface, not the inaugural choice. Future ADR can promote GitHub Actions to first-class if operator usage shifts.
7. **Wait until Claude Code routines exits preview.** *Rejected* — preview-tier acceptance with explicit stamp + substrate-swap recovery path is the right tradeoff for surgical-win velocity. Waiting for GA delays the AFK-diagnosis pillar indefinitely.

**Enforcement-policy alternatives (3 rejected):**

8. **Single-point enforcement (exec wrapper whitelist only).** *Rejected* — unsupervised execution is one-bug-away from doctrine breach with single-point enforcement. Three independent layers (schema, wrapper, hook) fail-closed together; each is testable in isolation.
9. **Action permitted with operator-attested override flag.** *Rejected* — `diagnosis_only: Literal[True]` is type-enforced and cannot be set false. Override flag would be an escape hatch; doctrine boundaries don't have escape hatches.
10. **Allow `git commit` from routine context with operator-attested override.** *Rejected* — `forbid-routine-mutation` hook is unconditional. If a future ADR proves operator value in commit-from-routine (e.g., auto-merge regenerative PRs from doc-gardening), it can promote this hook to a conditional check; this ADR's posture is fail-closed.

**Provenance alternatives (3 rejected):**

11. **Backfill `recorder_source: "session"` on existing 7000+ ledger events.** *Rejected* — backfill has no operator-facing benefit; field-absence is a perfectly fine discriminator. Anti-vibing: don't introduce backfill work that doesn't pay rent.
12. **Cloud routine pushes directly to local `.gzkit/ledger.jsonl` via authenticated git push.** *Rejected* — operator-attests-L2 invariant (AGENTS.md § Never #2) holds for cloud-originated events too. Pull-mode reconcile preserves the invariant; push-from-cloud breaks it.
13. **Cloud routine pushes via PR (fork-and-PR pattern).** *Rejected* — pollutes review queue with cosmetic ledger appends; ADRs already accumulate ledger-merge work in the established ts-sorted-union pattern (commits 30acf5a0, f4c9b2b8, 06957917). Adding a PR per routine fire would inflate review queue by ~30 PRs/month per active routine. Not worth the trust gain over GHI-body-as-trust-bridge.

**Output-surface alternatives (2 rejected):**

14. **Separate `.gzkit/routine-claims/` directory the operator inspects.** *Rejected* — new surface for marginal benefit. GHI is already operator-readable canon; embedding `RoutineExecEvent` in GHI body reuses an existing operator-attention surface.
15. **Email/Slack notification on drift instead of GHI.** *Rejected* — GHI is durable and auditable; notification is faster but ephemeral. Operator can wire GHI labels into notification systems if desired (out of inaugural scope).

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.62 | Pending | | | |
