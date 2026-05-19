---
id: ADR-pool.investigator-tracing-skill
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: "openai/symphony .codex/skills/debug — correlation-key + lifecycle-stage + failure-classification pattern keyed on issue_identifier and session_id against log/symphony.log"
complements:
  - ADR-0.0.49-systematic-debugging-discipline
  - ADR-pool.harness-trace-bundles
  - ADR-pool.canonical-vs-runtime-separation
  - ADR-pool.cross-session-history-query
  - ADR-pool.cross-session-search
---

# ADR-pool.investigator-tracing-skill: Investigator Tracing Skill

## Status

Pool

## Date

2026-05-19

## Intent

Author a tracing/correlation skill (`gz-investigator-trace`, working title) that
turns the `investigator` persona's Phase-1 evidence requirement into a
reproducible lookup procedure against gzkit's live correlation surfaces
(`.gzkit/ledger.jsonl`, `.gzkit/pipelines/<pipeline-id>/`,
`artifacts/receipts/arb-*`, and — once promoted — `harness_trace_bundle.v1`
bundles).

ADR-0.0.49-systematic-debugging-discipline (Proposed, foundation, heavy)
names HOW agents debug: the Iron Law (precondition form — "NO FIX MAY BE
PROPOSED UNTIL ROOT-CAUSE EVIDENCE IS CAPTURED AS AN ARB STEP RECEIPT"), the
four phases, the `investigator` persona, and a `gz-systematic-debug`
methodology skill **explicitly framed as methodology not CLI ceremony, like
`gz-design`**. ADR-pool.harness-trace-bundles names the raw evidence
substrate (`gzkit.harness_trace_bundle.v1` schema). Neither names the lookup
procedure — the actual sequence of correlation-key queries an investigator
agent runs to populate Phase-1 evidence and cite it in a receipt.

The unnamed seam is the same seam openai/symphony's `debug` skill fills in
its own context: a discipline that names *what evidence is required* and a
data substrate that names *where the evidence lives* still leave the
investigator without a reproducible procedure for *how to retrieve it*. The
gap shows up as drift: two investigator agents on the same defect produce
two different Phase-1 traces because they reached for different correlation
keys in different orders. The Iron Law catches the missing-receipt failure
mode; it does not catch the non-reproducible-trace failure mode.

This skill closes that seam. It names the canonical correlation keys
(`ADR-ID`, `OBPI-ID`, `pipeline-id`, `arb-receipt-id`, `event-id`,
`workflow-stage`), the canonical lookup commands (`gz ledger`, future
`gz trace`, `gz pipeline status`, ARB receipt readers, log readers), the
canonical lifecycle stages (started / streamed / completed | failed |
stalled) translated to gzkit semantics (pipeline-launched / stage-entered /
stage-completed | stage-failed | stage-stalled), and the failure-family
classification (timeout/stall, validator-rejection, attestation-rejection,
hook-block, scope-violation, fabrication-detection).

## Decision

When promoted, author `gz-investigator-trace` (working title) as a
methodology skill paired to the `investigator` persona under
ADR-0.0.49-systematic-debugging-discipline. The skill is methodology, not
CLI-backed: it sequences commands the agent already has, it does not
introduce a new top-level `gz` verb. Promotion produces:

1. **Skill body** at `.gzkit/skills/gz-investigator-trace/SKILL.md` carrying:
   - **Correlation key catalog**: `ADR-ID`, `OBPI-ID`, `pipeline-id`,
     `arb-receipt-id`, `event-id`, `workflow-stage`, `gate-id`,
     `validator-scope`, `ghi-number`. Each key names the canonical source
     surface it indexes (e.g. `pipeline-id` indexes
     `.gzkit/pipelines/<pipeline-id>/markers/*` and the corresponding
     `pipeline_*` ledger events).
   - **Canonical lookup commands** mapping each correlation key to the
     `uv run gz ...` invocation that retrieves its lifecycle slice. No
     ad-hoc `rg`/`grep` against `.gzkit/ledger.jsonl` for things a
     first-class `gz` command already exposes.
   - **Lifecycle stage vocabulary** translated from Symphony's `Codex
     session started / streamed / completed | failed | stalled` to gzkit's
     `pipeline_launched / stage_entered / stage_completed | stage_failed |
     stage_stalled / attestation_emitted | attestation_rejected /
     hook_blocked / validator_rejected`.
   - **Failure-family taxonomy**: each Phase-1 trace must classify into one
     of `timeout-or-stall`, `validator-rejection`, `attestation-rejection`,
     `hook-block`, `scope-violation`, `fabrication-detection`,
     `gate-failure`, `unclassified` (the last is itself a signal). The
     taxonomy aligns with `.gzkit/rules/agent-failure-modes.md` named
     patterns where possible.
   - **Phase-1 trace template**: the concrete artifact the Iron Law cites.
     A trace MUST contain (a) the failing assertion's actual-vs-expected
     output captured verbatim, (b) the lifecycle slice keyed to the
     correlation keys above, (c) the call-graph (or pipeline-stage graph)
     between the failure site and the nearest validated invariant, (d) the
     data-flow trace from input to assertion, and (e) the failure-family
     classification with rationale. The trace is captured via
     `uv run gz arb step --name root-cause-trace -- ...` per
     ADR-0.0.49 Decision item 1; this skill names *what to put in the
     `-- ...` slot*.
   - **Investigation playbooks** for the recurring shapes: stuck OBPI
     pipeline, ledger drift, audit-check failure, ARB receipt fabrication,
     validator scope rejection, hook block, attestation refusal,
     three-failed-fixes architecture pause. Each playbook names the
     correlation-key entry point, the lifecycle slice to retrieve, the
     expected-vs-actual checks, and the failure family to classify into.

2. **Skill frontmatter**: `model: opus` per `.claude/rules/model-selection.md`
   (judgment-class hypothesis formation, novel correlation reasoning);
   `lifecycle_state: active`; no `gz_command:` (methodology like
   `gz-design` and `gz-systematic-debug`).

3. **Cross-link to `gz-systematic-debug`**: the systematic-debug skill's
   Phase-1 section names `gz-investigator-trace` as the procedure of record
   for retrieving the evidence the Iron Law requires. The cross-link is
   bidirectional; the trace skill names systematic-debug as the upstream
   discipline.

4. **Cross-link to `investigator` persona file**: the persona's grounding
   paragraph cites `gz-investigator-trace` as the procedural skill the
   persona reaches for during Phase 1, alongside `gz-systematic-debug` as
   the disciplinary skill.

5. **Catalog entry**: `gz-investigator-trace` added to the AGENTS.md
   § Skills catalog under the Code Quality cluster, adjacent to
   `gz-systematic-debug`.

6. **Scorecard entry**: rule-file pairing optional at promotion (the skill
   may carry its enforceable doctrine directly; a paired
   `.gzkit/rules/investigator-tracing.md` is a promotion-time decision
   depending on whether `gz validate --systematic-debug-coupling` from
   ADR-0.0.49 OBPI-05 needs trace-shape validation).

## Authority Rules

1. **The trace skill is methodology, not CLI ceremony.** No new `gz` verb;
   only existing `gz` verbs sequenced into a reproducible procedure.
   Parallel to `gz-design` and `gz-systematic-debug`.
2. **The trace skill produces evidence, not decisions.** Failure-family
   classification is an evidence label, not a routing decision; the routing
   decision is owned by AGENTS.md § Defect-fix routing thresholds.
3. **Phase-1 trace shape is canon when promoted.** A Phase-1 trace that
   omits any of the five required artifacts (verbatim actual-vs-expected,
   lifecycle slice, call/stage graph, data-flow trace, failure-family
   classification) is the same class of failure as a fabricated
   `arb-step-unittest-*` receipt — caught structurally if mechanical
   promotion lands, caught by spec-reviewer otherwise.
4. **Correlation keys are stable identifiers, not narrative strings.** A
   trace citing "the OBPI that failed yesterday" is non-reproducible; a
   trace citing `OBPI-0.0.36-04` and `pipeline-2026-05-18T03:14:22` is
   reproducible. The skill enforces the discipline by requiring every
   playbook step to name its correlation key.
5. **The trace skill does not autonomously self-improve.** Trace findings
   may feed `agent-insights.jsonl` records or `/ghi-author` proposals;
   canon changes still go through ADR/OBPI/Gate-5 discipline.

## Target Scope

- Author `gz-investigator-trace` SKILL.md body with the six sections named
  in Decision item 1 (correlation key catalog, canonical lookup commands,
  lifecycle stage vocabulary, failure-family taxonomy, Phase-1 trace
  template, investigation playbooks).
- Add eight investigation playbooks (one per failure family in the
  taxonomy plus the three-failed-fixes architecture-pause case).
- Cross-link `gz-systematic-debug` SKILL.md (bidirectional reference).
- Cross-link `investigator` persona file (procedural-skill reference in
  grounding paragraph).
- Add catalog entry in AGENTS.md § Skills.
- Add scorecard entry in `docs/governance/advisory-rules-audit.md` if the
  skill carries enforceable doctrine; otherwise note advisory loading.
- Add docs page (`docs/governance/investigator-tracing.md`) explaining the
  three-skill stack: `gz-systematic-debug` (discipline) ↔
  `gz-investigator-trace` (procedure) ↔ `harness-trace-bundles` (data).

## Non-Goals

- No new top-level `gz` verb. The skill sequences existing `gz` verbs.
- No replacement of `gz-systematic-debug`. The discipline skill stays
  authoritative for the Iron Law and four phases; this skill is the Phase-1
  procedural detail.
- No replacement of `harness-trace-bundles`. The trace skill consumes
  bundle data once that ADR promotes; it does not redefine the data shape.
- No mechanical promotion of trace-shape validation in this ADR.
  `gz validate --investigator-trace-shape` is a future GHI target if
  ADR-0.0.49 OBPI-05's `gz validate --systematic-debug-coupling` does not
  cover trace-content checks.
- No vendor-specific log-format dependency. The skill operates on gzkit's
  own correlation surfaces; vendor-transcript inputs (Claude Code session
  logs, Codex session logs) are useful inputs but not the canonical source.
- No autonomous defect routing. Failure-family classification is evidence;
  routing decisions remain operator-attested per AGENTS.md § Defect-fix
  routing.

## Alternatives Considered

1. **Fold the tracing-toolchain requirement into ADR-0.0.49 before it
   leaves Proposed.** Rejected — risks scope bloat on an ADR that is
   already heavy lane with five OBPIs. The discipline ADR and the
   procedural ADR are separable surfaces; one names the Iron Law and the
   persona, the other names the lookup procedure. Independent decomposition
   produces cleaner Gate-5 attestations.
2. **Add a new top-level `gz debug` verb that bundles the tracing
   procedure as CLI ceremony.** Rejected — conflicts with the methodology-
   not-ceremony framing inherited from `gz-design` and `gz-systematic-
   debug`. The procedure is judgment-class agent work (which correlation
   key to start with, which lifecycle slice is the right depth, which
   failure family fits the evidence), not deterministic CLI execution.
3. **Let each investigator agent improvise the lookup procedure per
   defect.** Rejected — produces non-reproducible Phase-1 traces. Two
   agents on the same defect with the same Iron Law would reach for
   different correlation keys in different orders and produce different
   evidence shapes. The Iron Law catches missing-receipt; non-reproducible-
   trace requires a named procedure.
4. **Adopt openai/symphony's `debug` skill verbatim with a gzkit
   correlation-key translation.** Rejected — Symphony's skill is keyed on
   Linear-issue / Codex-session vocabulary and a single log surface
   (`log/symphony.log`). gzkit's correlation surfaces are richer (ledger,
   pipeline markers, ARB receipts, eventual trace bundles) and the
   vocabulary needs to translate, not transliterate. The shape is the
   inspiration; the body is gzkit-specific.
5. **Defer to a future GHI after ADR-0.0.49 lands and
   ADR-pool.harness-trace-bundles promotes.** Rejected — the procedural
   gap exists *today* whether or not trace-bundles promote; the Iron Law
   in ADR-0.0.49 will fire as soon as that ADR lands, and the absence of
   a named procedure will produce the non-reproducible-trace failure mode
   on the first defect after landing. Pool placement now lets the operator
   sequence promotion against ADR-0.0.49's lifecycle.

## Dependencies

- **Strong dependency on:** `ADR-0.0.49-systematic-debugging-discipline`
  (Proposed). The trace skill exists to serve the discipline skill's
  Phase-1 requirement; without ADR-0.0.49 landing, the trace skill has no
  Iron Law to anchor to.
- **Complements:** `ADR-pool.harness-trace-bundles`. The trace skill
  consumes harness-trace-bundle data once that ADR promotes; pre-promotion
  it falls back to `.gzkit/ledger.jsonl`, `.gzkit/pipelines/*`, and
  `artifacts/receipts/arb-*`.
- **Complements:** `ADR-pool.canonical-vs-runtime-separation`. The
  storage-root decision for ARB receipts and pipeline markers affects the
  trace skill's canonical-lookup-command catalog.
- **Complements:** `ADR-pool.cross-session-history-query` and
  `ADR-pool.cross-session-search`. Cross-session lookup is a likely future
  expansion of the correlation-key catalog.
- **Complements:** `ADR-pool.skill-behavioral-hardening`. The investigator-
  trace skill is a candidate for behavioral hardening once promoted, since
  judgment-class playbook selection is the canonical hardening target.

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. `ADR-0.0.49-systematic-debugging-discipline` has landed (status:
   Completed) — the Iron Law and `investigator` persona must exist as
   canon before a procedural skill anchors to them.
2. The operator accepts the methodology-not-CLI framing for this skill
   (parallel to `gz-design` and `gz-systematic-debug`); if a CLI verb is
   preferred, the ADR re-opens with a different decomposition.
3. The correlation-key catalog is bounded — promotion enumerates the keys
   that exist today, not the keys that might exist post-`harness-trace-
   bundles` promotion. Future keys land via amendment.
4. At least four of the eight investigation playbooks are drafted in the
   promotion brief, with concrete worked examples from recent gzkit
   history (GHIs #263, #290, #309 are candidate sources).
5. The decision on a paired `.gzkit/rules/investigator-tracing.md` rule
   file is made at promotion (advisory vs absent) — both are valid.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:`
frontmatter. Promotion into the active tree (foundation or feature) is
performed via `gz adr promote`, which rewrites the frontmatter with the
chosen taxonomy. Recommended kind at promotion: **foundation** — the
trace skill shapes how gzkit agents debug, not what they ship, parallel
to ADR-0.0.49.

Working title `gz-investigator-trace` may be revised at promotion;
candidate alternatives include `gz-trace-investigation`,
`gz-debug-pipeline`, `gz-evidence-trace`. The skill's identity is the
lookup procedure paired to the investigator persona; the name is
secondary.

## Inspiration Source Notes

openai/symphony's `.codex/skills/debug/SKILL.md` codifies four moves
worth porting (translated, not transliterated):

1. **Correlation keys as join keys.** Symphony names `issue_identifier`
   (human ticket key), `issue_id` (UUID), `session_id` (thread-turn pair)
   as the join keys for any debugging trace. gzkit needs the same
   discipline applied to its richer correlation surface (`ADR-ID`,
   `OBPI-ID`, `pipeline-id`, `arb-receipt-id`, `event-id`,
   `workflow-stage`).
2. **Lifecycle stages as trace skeleton.** Symphony's `Codex session
   started ... session_id=...` → stream/lifecycle events → terminal event
   (`completed` / `ended with error` / `Issue stalled`) gives the trace a
   skeleton independent of the specific defect. gzkit's equivalent is
   `pipeline_launched` → `stage_entered` events → terminal event
   (`stage_completed` / `stage_failed` / `attestation_rejected` /
   `hook_blocked` / `validator_rejected`).
3. **Failure classification as evidence label.** Symphony's
   *"Stall loop / app-server startup / turn execution failure / worker
   crash"* taxonomy is the evidence-label moment, distinct from the fix
   decision. gzkit needs the same separation between evidence and
   routing.
4. **Quick triage as named procedure.** Symphony's five-step quick
   triage (confirm symptoms → narrow by ticket key → extract session_id
   → trace end-to-end → classify) is the procedural shape this skill
   ports. gzkit's equivalent: confirm symptoms → narrow by ADR-ID/OBPI-
   ID → extract pipeline-id/arb-receipt-id → trace lifecycle → classify
   failure family.

What is NOT ported: Linear GraphQL integration (gzkit uses GHIs),
`log/symphony.log` as the single source (gzkit has multiple correlation
surfaces by design), and any vendor-transcript-specific parsing.
