---
id: ADR-pool.managed-agents-outcome-integration
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.managed-agents-outcome-integration: Managed Agents Outcome Integration

## Status

Pool

## Intent

Integrate platform-managed agent grading (Claude Managed Agents API,
GPT equivalents) into gzkit's OBPI pipeline, trust doctrine, and
attestation chain. The core value proposition: close the self-reporting
gap by adding an independent, provider-hosted evaluation layer between
agent self-report and human attestation — a Layer 2.5 trust surface
that is append-only, provenance-bound, and reconcilable against L2
receipts.

Provider-neutral by design. The outcome/rubric surface sits behind
feature flags so that Claude and GPT grading backends are
interchangeable without touching pipeline semantics.

## Feature Checklist

1. **Rubric generation from OBPI briefs** — REQ-list to `define_outcome`
   rubric translation, rubric schema definition, brief-to-rubric mapping
   contract. The rubric is a derived artifact (L3) regenerated from the
   brief (L1); brief mutation while an outcome session is active is
   fail-closed (invalidate and re-issue, no mid-flight REQ self-mutation).

2. **Managed session dispatch** — Role-to-session mapping for the four
   dispatch roles (Implementer, Spec-Reviewer, Quality-Reviewer,
   Pipeline-Orchestrator). HandoffResult and ReviewResult remain the
   output contracts; session output is parsed into these Pydantic models.
   Model routing flows through managed agent config, not gzkit's
   ModelRoutingConfig. Provider adapter behind feature flag.

3. **ARB receipt evidence upload** — Receipt JSON uploaded to session
   storage via the provider's Files API. Rubric criteria reference
   receipt evidence by ID so the independent grader evaluates mechanical
   artifacts, not agent narrative. Receipt provenance validated by
   `CANONICAL_STEP_COMMANDS` before upload.

4. **Evaluation-to-attestation bridge** — Grader terminal states map to
   pipeline actions: `satisfied` is necessary-but-not-sufficient (ARB
   cross-check mandatory); `needs_revision` triggers fix cycle;
   `max_iterations_reached` and `failed` escalate to human operator for
   Gate 5 review. Evaluation lifecycle events emit ledger events. Grader
   results stored as L2.5: append-only, provenance-bound to originating
   L2 ledger lines, rebuildable from L2, fail-closed on drift per T2/T3.

5. **Chained outcome pipeline orchestration** — The 5-stage OBPI
   pipeline maps to sequential outcome chains (one active outcome at a
   time, next issued after terminal). Marker state integration for
   re-entry on interrupted evaluations. Stage-to-outcome sequencing
   replaces inline subagent dispatch.

6. **Dreams-based memory curation** — Async curation of accumulated
   session knowledge via the Dreams API (`client.beta.dreams.create`).
   Three input surfaces, one output surface:

   **Input surfaces** (session transcripts and memory stores fed to Dreams):

   - *Agent insights* — `.gzkit/insights/agent-insights.jsonl` records
     (course corrections per Behavior Rule 11, defect observations,
     improvement patterns) are context for session transcripts Dreams
     mines. Curation deduplicates recurring corrections, surfaces
     failure-class patterns not yet codified in the six-pattern taxonomy
     (`.gzkit/rules/agent-failure-modes.md`), and drops one-off
     transient observations. Output feeds advisory scorecard rule
     promotion (Judgment → Mechanical).

   - *ARB receipt patterns* — Receipt corpus (`.gzkit/arb/receipts/`)
     across sessions reveals recurring quality-gate patterns: which
     steps fail most often, which receipts are re-run after fix cycles,
     which canonical commands produce false confidence. Dreams mines
     session transcripts containing ARB-wrapped runs for these patterns.
     Receipt IDs are evidence, not curation targets — Dreams never
     modifies the receipt corpus, only produces memory-store entries
     summarizing cross-session receipt trends.

   - *Session handoff chains* — `continues_from` chains accumulate
     stale decisions, superseded context, and resolved blockers across
     sessions. Dreams ingests the transcripts of chained sessions and
     produces a curated memory store that preserves booked decisions
     and active blockers while dropping resolved items. The staleness
     classification (Fresh/Slightly-Stale/Stale/Very-Stale) signals
     when curation is due; Dreams is the mechanical action behind the
     signal.

   **Output surface**: A new memory store (L3 derived — regenerable
   from L2 session transcripts) attached to future managed sessions via
   the Memory Stores API. The curated store is review-before-adopt:
   operator inspects the output store before it replaces the prior one.
   Non-destructive — input store is never modified.

   **Scheduling**: Paired with `ADR-pool.cloud-agent-routines` — cloud
   routines (R-1 through R-6) are the primary session producers; Dreams
   runs periodically (weekly or on accumulated-session threshold) to
   curate the routine-produced session corpus. Curation instructions
   are per-routine-family (e.g., trust-audit sessions get "focus on
   recurring drift patterns; drop transient validator noise").

   **Constraints**: 100 session max per dream, 4096-char instruction
   limit, research preview stability tier. Same provider adapter and
   feature flag as Features 1–5; no new dependency surface.

## Booked Decisions

| # | Question | Decision |
|---|----------|----------|
| 1 | SDK dependency posture | Provider-neutral interface behind feature flags. Optional extras group per provider (`gzkit[claude-agents]`, `gzkit[openai-agents]`), not core runtime dependency. Stdlib-first doctrine preserved. |
| 2 | Grader trust level | L2.5 intermediate. Trusted-but-external; mandatory reconciliation against L2 ARB receipts. Feature flag determines active grading backend. |
| 3 | Brief mutation during active outcome | Fail-closed. No REQ self-mutation mid-session. Pipeline invalidates active outcome and re-issues with updated rubric. |
| 4 | Grader pass sufficiency | Necessary but not sufficient. ARB mechanical cross-check is mandatory even when grader returns `satisfied`. Two-key attestation model. |
| 5 | Cost governance | In-scope. Iteration budgets per lane/kind, per-session token caps, cost observability surface. Opus-tier models can overrun plan ceilings; the cost surface must be budget-aware. |

## Architectural Context

### Trust layer positioning

| Layer | Owner | Shape |
|---|---|---|
| L1 (Canon) | Git-versioned markdown/YAML | Brief REQs, rubric schema |
| L2 (Ledger) | Append-only JSONL | Pipeline events, ARB receipts |
| **L2.5 (Grader)** | **Provider-hosted evaluation** | **Evaluation results, per-criterion verdicts** |
| L3 (Derived) | Ephemeral caches | Rubrics (regenerated from L1), status views |

L2.5 invariants: append-only immutability, binding provenance per T3
(each entry cites originating L2 event), fail-closed on drift per T2,
rebuildable from L2.

### Relationship to existing pool ADRs

- **ai-runtime-foundations**: Owns observability, traces, cost/latency,
  guardrail outcomes. This ADR consumes those signals but does not
  produce them.
- **agent-execution-intelligence**: Owns autonomy tiers and stall
  detection. This ADR's cost-governance surface interacts with
  progressive autonomy budgets but does not define the tier model.
- **controlled-agency-recovery**: Owns error taxonomy and recovery
  policies. This ADR's `failed`/`max_iterations_reached` escalation
  paths feed into recovery policy but do not define it.
- **cloud-agent-routines**: Primary session producer for Dreams
  curation (Feature 6). Routines generate the session corpus that
  Dreams mines; Dreams output stores feed back into routine context.
  Promotion sequencing: routines first (produces sessions), then this
  ADR (consumes them for evaluation and curation).

### Provider abstraction

```
Pipeline Runtime
  ├─ OutcomeDispatcher (provider-neutral interface)
  │    ├─ ClaudeOutcomeAdapter (managed-agents-2026-04-01 beta)
  │    │    └─ define_outcome, poll, retrieve files
  │    ├─ OpenAIOutcomeAdapter (future)
  │    └─ LocalOutcomeAdapter (testing, offline)
  └─ DreamsCurator (memory curation interface)
       ├─ ClaudeDreamsAdapter (dreaming-2026-04-21 beta)
       │    └─ create dream, poll, adopt/discard output store
       └─ LocalDreamsAdapter (testing, offline — snapshot-based)
```

Feature flags gate adapter selection at runtime. The
`LocalOutcomeAdapter` enables offline testing and CI without provider
credentials.

## Alternatives Considered

- **Direct Anthropic SDK integration without provider abstraction** —
  rejected; locks gzkit to a single vendor, violates the multi-provider
  reality of the operator's environment.
- **Grader results as L2 (full ledger trust)** — rejected; the grader
  runs outside gzkit's trust perimeter. L2.5 with mandatory ARB
  cross-check is the appropriate trust level.
- **Brief mutation allowed mid-outcome** — rejected; REQ self-mutation
  during evaluation creates an untestable moving target. Fail-closed
  invalidation preserves rubric integrity.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

At promotion time, the six feature-checklist items decompose into OBPIs
per the OBPI Decomposition Matrix. Features 1–4 are independent units;
Feature 5 (chained orchestration) depends on all four; Feature 6
(Dreams curation) depends on Feature 2 (managed session dispatch —
sessions must exist before Dreams can mine them) and pairs with
`ADR-pool.cloud-agent-routines` as its primary session source.
