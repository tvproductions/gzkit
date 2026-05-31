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

### Snapshot A — plan authoring (2026-05-30, morning): RED

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

### Snapshot B — re-measured (2026-05-30, after GHI #570 landed): GREEN

- `git status --short` is clean.
- `uv run gz check` exits 0 — all 26 gates pass. GHI #570 added Line endings as
  gate 26 and cleared the unit-test failure. The only remaining output is a
  non-blocking advisory (spec-test-code drift, 1687 findings, explicitly "does
  not affect exit code").
- All six Snapshot-A failure surfaces are now green: Test, `--kind-invariance`,
  `--insights-shape`, `--tautological-test-audit`, `--task-envelope-coherence`,
  and `preflight`.
- Phase 1 (Make the Harness Green) is complete. Remaining recovery work is the
  context-load surface tracked by emergency GHI #519 (Phase 2 / Phase 4 item 1)
  and the passive-presenter closeout route tracked by GHI #516 (Phase 3).
  GHI #517 (the broader 5-alarm structural emergency) is closed.

Snapshot A is preserved for audit; Snapshot B is the live baseline.

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

## Designated Workstream — Harness Hardening (anti-vibe mechanization, post-green)

Recorded here from the 2026-05-30 operator+agent dialogue so the analysis becomes
durable, sequenced action instead of being re-derived next session (Operating
Rules 1 and 7). This workstream does **not** start while `uv run gz check` is red
(Operating Rule 2), and promoting its ADRs is an explicit operator decision
against the Architectural Boundary 1 freeze (Operating Rule 6) — not a default.

North star: gzkit should flow like superpowers — enforcement off the operator's
face and into the machine: invisible when the operator is right, blocking only at
the moment of a mistake. Friction-always is the disease; pre-action mechanism is
the cure. Same move as Operating Rule 7, applied to behavior instead of context.

Two failure classes (both observed live on 2026-05-30):

| Class | Example | Mechanizable? | Cure surface |
|---|---|---|---|
| Skill-bypass / unauthorized mutation | agent ran raw `gz`/edit tools outside the governing skill | yes — pre-tool | the spine below |
| Claim fabrication | agent asserted false findings (a GHI map, a `gz check` table) in prose with no tool call | partly — no hook fires on a chat assertion | receipt-cited claims + human at attestation; irreducible residue remains |

Verified spine (five pool ADRs, all confirmed extant 2026-05-30; promotion-ordered
by dependency):

| ADR (pool) | Role | Depends on |
|---|---|---|
| `tool-permission-classifier` | deterministic `classify(tool,args)` → read / workspace / governance / external / full; unclassifiable → fail-closed (full/deny) | none — leaf; first promotion |
| `agent-execution-intelligence` (CAP-08 MODE) | per-invocation MODE: READ-ONLY / PLAN-FIRST / IMPLEMENT (independently promotable) | none |
| `tdd-receipt-stream` | generalized governance receipts (`mode_declared`, `scope_widened`, `mode_violation`, …); append-only; works even record-only | classifier, MODE |
| `skill-behavioral-hardening` | skill-intent scope invariant + circuit breaker: a skill's declared scope bounds its mutating calls; out-of-scope mutation needs authorization before the call | classifier, MODE, receipts |
| `harness-aware-execution-modes` | Mode 1 skill-chain self-gate / Mode 2 PreToolUse hook **block** (Claude Code today) | envelope, classifier |

Promotion sequence (when unfrozen): `tool-permission-classifier` (leaf,
fail-closed, smallest win) → `agent-execution-intelligence` MODE +
`tdd-receipt-stream` → `skill-behavioral-hardening` → `harness-aware-execution-modes`
Mode 2.

Non-negotiable gates:

- Any AGENTS.md / `.claude/rules` change this implies routes through the CMS
  (`gz content`, `gz governance render`) — never a hand-edit to a rendered surface.
- Green-first: no promotion while `gz check` is red.
- Boundary 1 exception is the operator's explicit call, made after seeing routing facts.

The honest limit: the claim-fabrication class cannot be fully mechanized — a model
asserting a false synthesis in chat fires no hook. Reduce the surface (cite a
receipt for every state claim, or mark it unverified), then place the human at
attestation, not at every keystroke. Do not answer this class with a new prose
rule; 2026-05-30 proved prose does not bind.

Exit criteria:

- The skill envelope records a governance event on every named skill invocation
  and (Mode 2) blocks an out-of-envelope mutating call before it runs.
- `uv run gz check` includes a passing check that the classifier/envelope are wired.
- A deliberate skill-bypass attempt in a test session is mechanically stopped,
  observed by the operator.

Provenance: spine ADRs verified extant via `gh`/Glob/Read on 2026-05-30; failure
classes from observed incidents that session (fabricated GHI map, fabricated
`gz check` table, overwritten-then-git-restored recovery plan).

## Designated Workstream — Context-Load CMS (density-dial composition; #519 remediation)

Recorded here (Operating Rules 1 and 7) so this turn's diagnosis and decision become
durable, resumable action rather than re-derived next session. This is the **concrete
remediation route for emergency GHI #519** — it replaces the earlier tracked-but-parked
posture. Session handoff:
`.gzkit/handoffs/20260531T000357Z-adr-0.0.37-density-dial-cms-extension.md`.

**Diagnosis (observed 2026-05-30).** AGENTS.md is meant to be a rendered Layer-3 view, but
the live path is a hardcoded monolith: `sync_agents_md` → `render_template("agents")` over a
100%-prose template, with `.gzkit/agents.local.md` spliced in raw and literals hardcoded in
`get_project_context`. Two half-built render-from-source substrates exist for the same
surface and neither drives it — ADR-0.0.37's flat invariant registry and ADR-0.0.34's
`AgentContract` content model. The authoritative target is the substrate doctrine
[`docs/governance/agent-control-surface-rendering-substrate.md`](agent-control-surface-rendering-substrate.md)
(binding claim: nothing hand-authored at the rendered location). Codex loads root AGENTS.md
at ~98% of its 32 KiB `project_doc_max_bytes` cap — the #519 magnitude.

**Decision (operator, 2026-05-30).** Extend ADR-0.0.37 to bear the always-intended CMS
vision: one master content model at MAX fidelity; a render *temperature* (lite/medium/heavy)
that dials prose density; section add/withhold; per-vendor templates; eventual
harness/model detection. Spine = `AgentContract` (ADR-0.0.34); the invariant registry
becomes its foundation-classified subset. The dial has an absolute floor — *"we don't go to
0 Kelvin"*: `Judgment`-class bullets render at every temperature; the dial thins only
Mechanical/Reference prose.

**In-flight state.** ADR-0.0.37 Decision extended (new subsection "Decision Extension
(2026-05-30): CIC-1 Density-Dial Composition"); checklist items 11–16 added; Decomposition
Scorecard made coherent (final target 16); six brief stubs created (1:1 sync, 16↔16);
`gz validate --documents` green. The six briefs are scaffolds pending semantic authoring;
implementation follows. This is a foundation-ADR scope change made under explicit operator
direction as #519 emergency relief (Architectural Boundary 1 / Operating Rule 6 waived by
the operator's explicit call now that `gz check` is green).

**Open loop named.** This session re-derived the rendering architecture from source despite
the substrate doctrine already documenting it and three prior same-day insights logging the
lesson — capture without re-injection does not bind. OBPI-0.0.37-16 (docs-for-agents
orientation index) is the structural fix; the session handoff is the interim re-injection.
See `.gzkit/insights/agent-insights.jsonl` (2026-05-30 open-loop entry).

**Exit criteria.** OBPIs 11–16 authored and implemented; `sync_agents_md` renders from the
master model; AGENTS.md and vendor mirrors render at per-vendor temperatures; zero
hand-authored prose at the rendered location; Codex root-surface load fits its budget with
headroom; `gz check` green throughout.

## Recovery Closeout

Final closeout is filled only when recovery completes (Definition of Healthy all
true). Recovery is **not yet closed** — emergency GHI #519 (context load) remains
open. The progress snapshot below records observed evidence; the `Decision` line
stays blocked until #519 closes.

### Progress snapshot — 2026-05-30 (post-GHI-#570 re-measurement)

```text
Snapshot date:            2026-05-30 (recovery still open)
uv run gz check:          exit 0 — 26/26 gates pass (advisory-only drift remains)
Emergency GHIs open:      1 — #519 (codex context surface exhausts 258K window)
Context-load issue state: #519 OPEN — remediation route now IN-FLIGHT (ADR-0.0.37 density-dial CMS, OBPIs 11-16); see Designated Workstream — Context-Load CMS
Task-envelope coherence:  PASS — gz check gate green
Open recovery issues:     #519 (emergency; Phase 2 / Phase 4 item 1), #516 (closeout passive-presenter; Phase 3). #517 closed.
Decision:                 normal development may NOT resume — blocked on emergency GHI #519
```

## Appendix: The Smooth-vs-Replicable Axis (2026-05-30 dialogue insights)

Preserved from the 2026-05-30 operator+agent dialogue so this framing is not re-derived next session.

**The axis.** Superpowers is smooth but makes *snowflakes* (artisanal, low-replicability, non-reproducible). gzkit is replicable but *toxic* ("breathing tar fumes"). That is the real tradeoff this recovery is negotiating.

**Toxicity is mostly incidental, not essential — replicability and toxicity live in different layers:**

| Layer | What it is | Toxic? |
|---|---|---|
| Replicability (the value) | ledger as system-of-record, deterministic `gz` commands, receipts/attestation, fail-closed gates | No |
| Delivery (current form) | 32k always-loaded prose, in-your-face ceremony, context-rot, truncation, *performed* compliance | Yes — and removable |

Proof they separate: Superpowers *enforces hard* (its docs: the model rationalizes out of the rules ~90% of the time without the "iron law") yet stays smooth, because enforcement is lean, just-in-time, and shaped as a process you flow through. **Enforcement is not the tar; front-loaded, human-facing enforcement is.**

**Design principle (the synthesis).** Make replicability *invisible-when-right*, the way Superpowers makes enforcement invisible-when-right: the ledger writes itself (hook), IDs mint at runtime, gates stay silent unless a mistake is imminent, the CMS renders the surface. Replicability becomes a *byproduct* of the work, not a *tax* on it. The pieces already exist (ledger-writer hook, CMS) — they are buried under prose.

**The irreducible floor (where the tradeoff is real).** Replicability requires the one thing Superpowers refuses to pay: a human making binding decisions explicit and attesting to them at promotion boundaries (Gate 5). It cannot be automated — but it must be *a handful of moments per phase, not constant.* Concentrate attestation-grade friction at the real decision points; automate everything around them. gzkit cannot be Superpowers-smooth, but the floor that genuinely must hurt is thin; nearly all current toxicity sits above it.

**The phases reframe (the practical answer).** The tools are not competitors; they are phases.

- *Exploration / snowflake phase* → Superpowers. Snowflakes are fine for sketches and greenfields; do not reproduce a prototype.
- *Hardening phase* → gzkit, when a greenfield succeeds and must become reproducible, auditable, team-survivable.
- gzkit feels like tar because it makes you *manufacture while still sketching*. This is gzkit's own pool→foundation gradient applied to the *work*: near-zero ceremony during exploration, crystallize ceremony only at promotion. **The goal is a cheap handoff from the snowflake phase to the hardening phase — not one tool for everything.**

**Grounding (Claude Opus 4.8 system card, read 2026-05-30 — checked, not theorized).**

- gzkit's failures map to *named, measured* metrics: "situational hallucination" (hallucinating file/tool-output contents) and "missing-context hallucination" (fabricating output for an unavailable tool) — §6.2.3.1.3, §6.3.3.
- The trend is *improving*, not hopeless: 4.8 is "a significant improvement over Opus 4.7 on most aspects of honesty" (p97); it had "the lowest incorrect-rate of the six models on every benchmark," achieved "mainly by abstaining … when it was uncertain" (p115); and it "scores the highest" at resisting unavailable-tool fabrication (p119).
- Critical caveat (p83): the card measures the model under *normal* scaffolds, "rather than specific product surfaces such as the Claude app, Claude Code, or Cowork." gzkit's extreme context load is *outside* the regime where those reliability numbers hold. **The context diet is the safety work — it returns the model to its measured-reliable regime — not cosmetic.**

Provenance: 2026-05-30 operator+agent dialogue; Claude Opus 4.8 system card; Superpowers docs + obra/superpowers issue #237; context-engineering field findings (retrieval + static analysis + span-level verification, reported up to ~96% combined hallucination reduction).
