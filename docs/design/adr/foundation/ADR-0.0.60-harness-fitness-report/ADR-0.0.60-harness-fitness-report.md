---
id: ADR-0.0.60-harness-fitness-report
status: Proposed
kind: foundation
semver: 0.0.60
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-25
promoted_from: ADR-pool.harness-fitness-report
---

# ADR-0.0.60-harness-fitness-report: Harness Fitness Report

## Persona

Active persona: `main-session` — craftsperson, governance-aware, whole-file
reasoning, direct. Treats harness-fitness measurement not as a vanity metric
but as the structural means by which the gzkit harness keeps itself honest:
if the factory's loop time isn't observable, the anti-vibing mantra has no
empirical floor.

## Intent

### Before (current state)

Currently, gzkit's "software factory" has no observable loop time. The
pipeline is intentionally heavy — five gates, universal Stage-5 attestation,
ARB receipts per QA step, ledger of truth — but **today** the question "how
long does it actually take from `pipeline_launched` to OBPI Stage-5
attestation, per lane?" can only be answered by anecdote. Operators cannot
tell whether lite-lane OBPIs complete in 20 minutes or 4 hours, whether
heavy-lane attestation latency is trending up, or whether a recent rule
change tripled prompt→Stage-5 wall-clock. The ledger records the events; no
surface aggregates them into the loop-time view. As a result, factory-
fitness claims are unfalsifiable and anti-vibing discipline has no empirical
floor.

### After (target state)

After this ADR lands, operators run `gz harness report --surface
lane-latency` and **see** median + p95 + rolling median for prompt→Stage-5
latency per OBPI lane, computed from `pipeline_launched_event` paired with
`obpi_receipt_emitted_event` (with `obpi_completion ∈ {"completed",
"attested_completed"}`). When a lane's rolling median exceeds a configured
floor for N consecutive completions, a GHI is auto-filed with the threshold
facts and OBPI IDs in the breach window. The factory's loop time becomes
falsifiable.

### Scope (inaugural metric)

The inaugural concrete metric this ADR ships is **prompt→Stage-5 latency per
OBPI lane** — the operator-facing answer to "is the factory fast enough to
call it a factory?" The broader harness-fitness scope inherited from the
pool ADR (validator-coverage, control-surface weight, receipt-citation
coverage, trace availability) is preserved as a multi-surface architecture
but intentionally NOT delivered by this ADR; subsequent foundation ADRs add
surfaces to the registry without restructuring this one.

### Anti-vibing constraint (binding)

This ADR MUST NOT introduce gate authority via latency floors. A latency
floor that fails a gate is functionally identical to "lighter ceremony as a
tradeoff axis" — the exact failure mode the anti-vibing mantra was authored
to make structurally impossible (AGENTS.md § Make LLM Stochastic Vibes
Inert, operative claim 2). The floor MUST be advisory; accountability comes
from auto-filed GHIs, not from refused attestations.

## Why foundation tier?

Without this ADR, the project would not be the project because the
anti-vibing mantra ("5:1 governance-to-output ratio is the product") has no
empirical floor — without observable loop time per lane, every claim that
gzkit's heavy ceremony is justified by structural integrity is operator
narrative, not measured fact. Harness fitness is identity-shaping: it is the
mechanism by which the factory metabolizes its own ledger into a falsifiable
performance claim. Feature ADRs cannot encode this invariant; it sits below
every release.

## Decision

Add `gz harness report --surface lane-latency` as the first concrete surface
under a pluggable surface registry. The implementation is architected so
future surfaces (validators, control-surfaces, receipt-citation,
stage-latency) add registry entries without restructuring this ADR.

### Architecture

**Surface registry.** A `Surface` Protocol (`runtime_checkable`) in
`src/gzkit/harness/surfaces/__init__.py` with `name`, `description`, and
`render(args: argparse.Namespace) -> int`. Surfaces register in a
module-level `SURFACES: dict[str, Surface]`. This ADR ships exactly one
entry: `lane-latency`. Subsequent ADRs add entries.

**Sequencing — ride coarse.** Use today's wired ledger events
(`pipeline_launched_event` in `src/gzkit/ledger_events.py:343`,
`obpi_receipt_emitted_event` at line 184 with
`extra.obpi_completion ∈ {"completed", "attested_completed"}`). When
`pipeline_stage_entered` lands via `ADR-pool.tdd-receipt-stream`, a future
ADR adds a `stage-latency` surface to the same registry for per-stage
breakdown. The upgrade is a registry addition, not a restructuring.

### CLI surface

```text
gz harness report --surface lane-latency
gz harness report --surface lane-latency --lane heavy --json
gz harness report --surface lane-latency --since v0.5.0
gz harness report --list-surfaces
gz harness report --surface lane-latency --no-auto-ghi
```

| Flag | Required | Default | Behavior |
|---|---|---|---|
| `--surface <name>` | yes (unless `--list-surfaces`) | — | Unknown surface → exit 2. |
| `--list-surfaces` | no | off | Print registry; exit 0. Mutually exclusive with `--surface`. |
| `--since <commit>` | no | none | Filter to pipelines launched on/after `git show -s --format=%cI <commit>`. |
| `--json` | no | off | `LaneLatencyReport.model_dump_json()` to stdout; diagnostics to stderr. |
| `--lane <lite\|heavy\|both>` | no | `both` | Filter aggregation by lane. |
| `--no-auto-ghi` | no | off | Suppress auto-GHI filing for this invocation; breach still rendered and recorded to insights. |

**Exit codes** (4-code map per `.gzkit/rules/cli.md`):

- `0` — report rendered, no advisory breach
- `1` — user/config error (bad `--since`, missing threshold config)
- `2` — system/IO error or unknown surface
- `3` — policy breach (advisory floor exceeded). **Soft non-zero** — fires
  after render and after auto-GHI side-effects so JSON consumers see the
  full report. Never fail-closes a gate.

### Data flow

1. **Pair events.** For each `pipeline_launched_event` with OBPI id `X`,
   find the latest `obpi_receipt_emitted_event` where `id == X`,
   `extra.obpi_completion` is set, and `ts > launched.ts`. If multiple
   launches exist for `X` (retried pipeline), pair the latest launch
   preceding the completion.
2. **Orphan handling.** Launched-without-completion = in-flight (excluded
   from latency, counted in a separate per-lane tally). Completion-without-
   launch = pre-pipeline-mandate or corruption; logged stderr, excluded.
3. **Lane resolution.** `pipeline_launched.extra.lane` is authoritative.
   Cross-check against brief frontmatter; drift logged as `lane_drift`
   insight, launched-event wins.
4. **Aggregate per lane.** Median, p95, sample count, oldest/newest sample
   ts, rolling median over the most recent `consecutive_breaches` samples.
5. **Cache.** `.gzkit/telemetry/lane-latency.json` — single
   `LaneLatencyReport` JSON document, overwritten per scan, fully
   regenerable from `.gzkit/ledger.jsonl`. Cache loss is non-fatal.
6. **Breach detection.** Rolling-window is per-OBPI-close, not per-time-
   bucket, so cadence variance never produces false positives. Thresholds
   in `.gzkit/config.toml` under `[harness.lane_latency.floor_seconds]`
   (defaults: lite=1800, heavy=7200, consecutive_breaches=5).
7. **Auto-GHI on breach.** Always append `harness_regression_detected` to
   `.gzkit/insights/agent-insights.jsonl` (Behavior Rule 11). Check open
   GHIs labeled `harness-regression` for the lane; comment on existing or
   file new via `/ghi-author` (Behavior Rule 13 — never direct
   `gh issue create`). Dedup by labels `harness-regression` + `lane:<lane>`
   + `surface:<surface>`.

### Layer assertion (binding)

`gz harness report --surface lane-latency` writes nothing to
`.gzkit/ledger.jsonl`. It reads ledger events (Layer 2), writes a derived
cache under `.gzkit/telemetry/` (Layer 3), may append to
`.gzkit/insights/agent-insights.jsonl`, and may invoke `/ghi-author` (which
writes a GitHub Issue, not the ledger). Per `docs/governance/state-doctrine.md`,
this surface is Layer 3 in toto. The validator scope `gz validate
--harness-telemetry` (OBPI-05) is the structural integrity check that catches
ledger-derivation drift; exit 3 fail-closed.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| WEAK: gz harness report and --harness-telemetry are unbuilt (Proposed); the ledger event substrate lane-latency is computed from validates green. | uv run gz validate --ledger | 0 |

## Consequences

### Positive

- The factory's actual loop time becomes observable per lane, not just
  inferable from "how does that feel?"
- Advisory floor + auto-GHI creates accountability without manufacturing the
  velocity-vs-anti-vibing tradeoff axis the mantra rejects.
- Pluggable surface registry means subsequent harness-fitness work
  (validator coverage, control-surface weight, stage-latency) adds entries
  to the dispatcher without restructuring this ADR.
- The cache JSON schema becomes the integration surface for downstream
  consumers (`ADR-pool.session-productivity-metrics`, future dashboards) —
  contract-stable, not renderer-stable.
- Ride-coarse sequencing means we ship today rather than waiting on
  `pipeline_stage_entered`; upgrade path is documented but not implemented.

### Negative

- Heavy-lane CLI surface change requires Gates 1–5 and a runbook update.
- A new validator scope (`--harness-telemetry`) joins `gz check`'s default
  pipeline; one more thing that can break a clean check run.
- Auto-GHI on regression depends on `/ghi-author`'s prior-art lookup
  working correctly; thresholds will need calibration after the first month
  of real telemetry to avoid GHI noise.
- `.gzkit/telemetry/` becomes a new operator-machine-state surface
  (gitignored cache file); operators on shared machines need to understand
  the cache is per-checkout, not per-repo.
- Six OBPIs is a non-trivial implementation commitment behind a backlog of
  four already-pending foundation ADRs (0.0.55, 0.0.56, 0.0.58, 0.0.59).

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 6
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 6

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.60-01: **lane-latency-models** — Pydantic models (`LaneLatencyRecord`, `LaneLatencyAggregate`, `LaneLatencyReport`, `HarnessRegressionInsight`, `HarnessLaneLatencyConfig`) + JSON schema export to `src/gzkit/schemas/harness_lane_latency.json` + schema-drift CI gate.
- [ ] OBPI-0.0.60-02: **lane-latency-scanner** — Ledger scanner pairing `pipeline_launched` → `obpi_receipt_emitted` (with `obpi_completion ∈ {"completed","attested_completed"}`); orphan handling; lane drift detection; rolling-window aggregation; cache write to `.gzkit/telemetry/lane-latency.json`.
- [ ] OBPI-0.0.60-03: **lane-latency-renderer** — Rich-table renderer matching `gz status` house style; `--json` emits `LaneLatencyReport.model_dump_json()` to stdout, diagnostics to stderr; `--lane`, `--since <commit>`, `--list-surfaces`, `--no-auto-ghi` flags; soft-non-zero exit 3 on breach.
- [ ] OBPI-0.0.60-04: **harness-regression-helper** — Shared `file_or_comment_ghi` helper in `src/gzkit/harness/regression.py` routing through `/ghi-author` (Behavior Rule 13); deterministic label policy (`harness-regression` + `lane:<lane>` + `surface:<surface>`); always emits `HarnessRegressionInsight` to `.gzkit/insights/agent-insights.jsonl` regardless of file-vs-comment outcome.
- [ ] OBPI-0.0.60-05: **harness-telemetry-validator** — New `gz validate --harness-telemetry` scope: schema validity, ledger-event resolution for both event IDs per record, high-water-mark monotonicity, in-flight count sanity. Exit 3 fail-closed on drift; wired into default `gz check`.
- [ ] OBPI-0.0.60-06: **lane-latency-docs-and-attestation** — Operator runbook section; `gz harness report` manpage with examples; Gate 4 BDD scenarios; threshold-config doc at `docs/governance/harness/lane-latency-config.md`; Gate 5 attestation evidence bundle.

## Target Scope

- Define telemetry event schema for validator and harness-module observations.
- Add a report renderer that produces a compact table plus detailed sections.
- Add `--since <commit>` delta mode.
- Add a zero-hit and high-cost scope review section.
- Add links to doctrine anchors and recovery commands for failing scopes.
- Add a "guide coverage" section that points to rule/skill content whose
  described failure class lacks a corresponding sensor.
- Add harness-lab episode summary ingestion once `ADR-pool.harness-lab` exists.

## Non-Goals

- No web dashboard.
- No replacement for `gz check`.
- No automatic deletion of rules or validators.
- No telemetry emission into `.gzkit/ledger.jsonl`.
- No operator-facing raw JSON/YAML report as the primary review surface.
- No per-stage latency breakdown (deferred to future ADR after `pipeline_stage_entered` lands).
- No fail-closed gate authority for floor breaches (advisory-only per anti-vibing mantra).

## Dependencies

- **Consumes:** `ADR-pool.harness-trace-bundles` for trace availability and
  trace-quality reporting.
- **Consumes:** `ADR-pool.harness-lab` for module ablation outcomes.
- **Complements:** `docs/governance/harness-engineering-appraisal.md`, which
  names harness-fitness measurement as an open blindspot.
- **May absorb:** The validator-telemetry idea from the 2026-04-26
  harness-engineering improvement handoff if the operator prefers one ADR
  rather than a separate pool ADR.

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. The operator chooses the command shape: `gz harness report`, `gz health`, or
   both with one delegating to the other.
2. The telemetry storage root is chosen.
3. The first metric set is accepted: validator count/duration/hits,
   control-surface weight, receipt-citation coverage, and trace availability.
4. Delta semantics for `--since <commit>` are defined.
5. The report's authority boundary is accepted: advisory fitness signal, not a
   gate by itself.

## Notes

Pool ADRs are backlog items -- they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.harness-fitness-report` on 2026-05-25; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

Per the design dialogue's rejected-alternatives discipline (Lindsey et al.
2025 rhyme experiment — a chosen alternative is only interpretable in
contrast to the rejections). Each was considered, evaluated against the
operator's intent, and rejected for the concrete reason named.

### Routing alternatives (the load-bearing overlap check)

- **Promote `ADR-pool.session-productivity-metrics` instead.** Throughput is
  its native frame; latency would land as the inaugural aggregation on a
  read-view over the unified governance-event stream. **Rejected** —
  session-productivity is session-level not lane-level; promoting it would
  force resolving the parallel-ledger-vs-read-view tension in the same
  ceremony, expanding scope. Lane-latency is a cleaner inaugural metric
  under `harness-fitness-report`.
- **Net-new foundation ADR; supersede pool slices afterward.** Sharpest
  scope, but **rejected** — leaves three pool ADRs
  (`harness-fitness-report`, `session-productivity-metrics`,
  `tdd-receipt-stream`) with stale edges requiring follow-on cleanup.
  Promoting the pool entry is the smallest-delta path.
- **Wait for `ADR-pool.obpi-state-machine` / `tdd-receipt-stream` to land
  first.** Avoids building on the un-canonized `pipeline_stage_entered`
  vocabulary. **Rejected** — pushes work back significantly; coarse
  latency from today's wired events is concretely available
  (`pipeline_launched_event` + `obpi_receipt_emitted_event`). The
  ride-coarse path documents an upgrade hook for when the richer events
  land.

### Floor-policy alternatives

- **Fail-closed at the lane gate — actually a floor.** OBPI completion
  refused if lane latency exceeds threshold. **Rejected** — explicit
  anti-vibing-mantra violation (AGENTS.md § Make LLM Stochastic Vibes
  Inert, operative claim 2). A latency floor that fails a gate manufactures
  the velocity-vs-anti-vibing tradeoff the mantra was authored to make
  structurally impossible. An agent under deadline pressure would route
  around ceremony to satisfy the floor.
- **Pure observation, no floor or GHI.** Cleanest mantra-compliance, but
  **rejected** — the operator's verbatim ask was for a "measurable
  throughput floor"; observation-only defers the accountability question
  entirely and offers no structural reason "measurable" appears in the
  framing.
- **Advisory-only — report breach, never block, never file.** **Rejected**
  — risk of becoming wallpaper. Auto-GHI on persistent regression is the
  accountability hook that makes the rendered breach actionable without
  giving the renderer gate authority.

### Architecture alternatives

- **Stream-anchored fitness section** (bundle lane-latency, validator-
  fitness, control-surfaces, receipt-citation as one `gz harness report`
  render under a no-flag contract). **Rejected** — bundles four surfaces
  into one render, contradicting the ride-coarse decision and the
  operator's explicit lane-latency-first ask. Smallest-vibing-surface check
  fails: more surface = more places for stochastic LLM vibing to leak.
  Defer the umbrella render to a successor ADR after at least two surfaces
  exist independently.
- **Standalone `gz harness latency` verb** (no `--surface` flag, no umbrella
  group, future fitness surfaces become sibling verbs). **Rejected** —
  drops the "lane" qualifier; invites future collisions with
  `stage-latency`. The pluggable-renderer dispatcher (chosen approach)
  preserves the parent pool ADR's named umbrella shape (`gz harness
  report`) while keeping each surface's contract pure.
- **Append latency events to `.gzkit/ledger.jsonl` directly.** **Rejected**
  — violates the parent pool ADR's explicit non-goal AND the Layer-2/Layer-3
  state-doctrine boundary (`docs/governance/state-doctrine.md`). Latency
  is *derived* from two existing ledger events; emitting it as a third
  event would create a reconciliation invariant (ledger duration must equal
  computed duration) with no operator value and one more thing to drift.

### Data-shape alternatives

- **Cache as `.jsonl` (line-delimited records).** **Rejected** — forces
  consumers to reassemble the aggregates/records relationship across
  disjoint lines, defeating the schema-stable contract that `--json` mode
  promises. The cache is a single nested `LaneLatencyReport` document; the
  natural serialization is one JSON document per file.
- **Widen `HarnessRegressionInsight.scope` to `Literal["harness.lane_latency",
  "harness.stage_latency"]` proactively.** **Rejected** — smallest-vibing-
  surface preference. Add scope values when their consumers exist; minor-
  version additions are backward-compatible.
- **`Surface` as ABC instead of Protocol.** **Rejected** — Protocol with
  `runtime_checkable` allows future surfaces in unrelated modules to plug
  in without inheriting from `harness/`. Looser coupling matches the
  pluggable-renderer intent.

### Operational alternative

- **Keep this work in the pool backlog until reprioritized.** **Rejected**
  by operator decision (2026-05-25 design dialogue, Approach 1) — promotion
  to active foundation work proceeds despite four already-pending
  foundation ADRs (0.0.55, 0.0.56, 0.0.58, 0.0.59), because lane-latency
  observability has compounding value across the unfinished work.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.60 | Pending | | | |
