---
id: ADR-pool.workflow-specification
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: https://archon.diy/guides/authoring-workflows/
complements:
  - ADR-pool.harness-trace-bundles
  - ADR-pool.harness-lab
  - ADR-pool.harness-fitness-report
  - ADR-pool.tool-permission-classifier
amendments:
  - 2026-05-19 — added § Amendment 2026-05-19 (conformance matrix dimension, inspired by Symphony SPEC.md §17 + §18)
---

# ADR-pool.workflow-specification: JSON Workflow Specification

## Status

Pool

## Date

2026-04-29

## Intent

Create a machine-readable JSON workflow specification for gzkit's governed
agent-runner semantics. The specification should describe gzkit-native stages,
gate prerequisites, evidence requirements, receipt expectations, attestation
boundaries, and ledger events so the covenant becomes inspectable and executable
by deterministic tooling.

This is motivated by the category gap surfaced while comparing gzkit to Archon:
Archon packages AI coding workflows as YAML DAGs with provider, tool, approval,
worktree, and adapter controls. gzkit should not copy that automation DSL. The
useful lesson is narrower: runner behavior benefits from a validated,
machine-readable workflow shape. gzkit's version must encode governance truth,
not generic prompt orchestration.

## Decision

When promoted, define a JSON-only workflow specification surface for gzkit. The
initial object model should describe existing gzkit workflows before inventing
new execution behavior.

The first target workflow is the OBPI pipeline:

```bash
gz workflow export obpi-pipeline --json
gz workflow validate path/to/workflow.json
gz workflow inspect path/to/workflow.json
```

Later execution hooks may consume the schema directly:

```bash
gz workflow run path/to/workflow.json
gz obpi pipeline --workflow path/to/workflow.json
```

The schema should model gzkit concepts:

- `kind`: schema family, e.g. `gzkit.workflow`
- `name` and `version`: stable workflow identity
- `entrypoints`: supported starts such as `full`, `from_verify`, `from_ceremony`
- `stages`: ordered or graph-shaped stage definitions with deterministic IDs
- `required_gates`: gate predicates and lane/kind/sensitivity conditions
- `evidence`: required artifacts, commands, and observed-output expectations
- `receipts`: ARB or workflow receipts required for completion claims
- `attestation`: human-gate requirements and allowed completion transitions
- `ledger_events`: event types emitted or required at each transition
- `scope`: allowed paths, denied paths, OBPI/ADR binding, and parent lineage
- `failure_policy`: fail-closed behavior, resume points, and blocker envelopes

The specification is JSON, with a JSON Schema and Pydantic model generated from
one canonical source. YAML is explicitly out of scope for the canonical workflow
surface.

The first implementation should export and validate the current pipeline shape
before it allows user-authored workflow execution. Export-first prevents the
schema from being invented as an aspirational design disconnected from the
runtime gzkit already has.

## Amendment 2026-05-07: Borrowed workflows require witnesses

The competitor-strength intake makes this pool ADR the home for absorbing Spec
Kit/Kiro/GSD-style staged workflows without copying their lighter trust model.
The schema must carry an explicit `borrowed_workflow_witnesses` block for any
stage pattern imported from another framework:

- `source`: the prior-art reference and exact workflow lesson being borrowed
- `gzkit_identity_preserved`: the ledger/receipt/validator/attestation invariant
  that prevents the borrowed pattern from becoming honor-system process
- `required_receipts`: receipts that prove the stage ran and produced observed
  output
- `failure_close_policy`: the blocker state emitted when the stage cannot be
  witnessed

This makes "front-door improvement" an executable contract. A future `gz
workflow inspect` view should show not only the stage order, but which parts are
native gzkit doctrine, which parts were borrowed, and how each borrowed part is
mechanically witnessed.

## Amendment 2026-05-16: NLAH/IHR and harness-lab precondition

The Natural-Language Agent Harnesses / Intelligent Harness Runtime paper adds a
useful framing for this pool ADR: workflow specification is the explicit harness
object, while the `gz` runtime owns shared policy, adapters, state semantics,
and child-agent lifecycle. gzkit should keep that boundary visible.

Add these fields to the promotion-time workflow schema decision set:

- `runtime_charter_ref`: the gzkit doctrine/runtime contract that interprets the
  workflow.
- `roles`: named agent/human roles and non-overlapping responsibilities.
- `adapters`: deterministic scripts, validators, and tool shims the workflow may
  invoke.
- `state_semantics`: which artifacts persist, which are derived, and how later
  stages reopen them.
- `failure_taxonomy`: named blocker/failure states and their recovery routes.
- `loop_policy`: maximum iterations or stage passes, legal re-entry edges, and
  termination conditions for each workflow.
- `context_policy`: what remains verbatim, what becomes a pointer, what may be
  summarized, and what must be omitted.
- `prompt_assembly_order`: stable-prefix, dynamic-context, and volatile-state
  ordering for surfaces that render prompts or agent instructions.
- `permission_policy`: declared permission modes for tools, commands, state
  mutation, and human-approval escalation.
- `subagent_policy`: child-agent roles, allowed tools, depth caps, isolation
  rules, and collection contracts.
- `trace_policy`: which stages emit `ADR-pool.harness-trace-bundles` events.
- `ablation_tags`: stable module IDs consumed by `ADR-pool.harness-lab`.

This makes workflow export the first dependency for the offline harness lab. The
lab should evaluate declared workflow objects, not reconstruct pipeline behavior
from prose skills and runbooks.

## Alternatives Considered

- **Adopt a YAML DAG DSL.** Rejected. YAML DAGs are useful for generic workflow
  automation, but gzkit's runner surface is covenant-first: stages, gates,
  receipts, ledger events, and attestation are the primitives. A prompt/bash/loop
  DSL would pull gzkit toward generic orchestration and away from completion
  truth.
- **Keep workflows prose-only in skills and runbooks.** Rejected. Prose skills
  are valuable for operator context, but they are weak as executable contracts.
  The current pipeline already has deterministic runtime pieces; JSON makes
  those pieces inspectable, testable, and reusable across harness surfaces.
- **Make this part of harness-agnostic plan capture.** Rejected. Plan capture
  normalizes construction-phase task plans. Workflow specification describes the
  runner lifecycle around those plans: which stages exist, what gates fire, what
  evidence is required, and what completion transitions are legal.
- **Defer all workflow schema until post-1.0.** Rejected as too passive. Full
  user-authored workflow execution can wait, but export/validate for existing
  gzkit workflows is a low-risk foundation for runner clarity.

## Target Scope

- Define `gzkit.workflow` JSON Schema and Pydantic models.
- Add read-only export for the current OBPI pipeline shape.
- Add validation that fails closed on unknown fields, missing stage IDs, invalid
  gate references, missing ledger event definitions, and non-JSON input.
- Add inspection output that renders the workflow in human-readable form without
  asking operators to review raw JSON.
- Connect workflow stages to existing pipeline markers, ARB receipts, gate
  checks, and attestation predicates.
- Keep user-authored workflow execution as a later phase behind explicit
  promotion-time design.

## Non-Goals

- No YAML canonical workflow format.
- No generic prompt node, bash node, loop node, or arbitrary DAG automation DSL.
- No web dashboard or visual workflow builder.
- No worktree-isolation commitment.
- No Archon adapter commitment.
- No weakening of Gate 5 or self-close rules to fit a workflow abstraction.

## Dependencies

- **Complements:** ADR-pool.harness-aware-execution-modes — workflow specs give
  both universal and full-enforcement modes a shared runner contract.
- **Complements:** ADR-pool.harness-agnostic-plan-capture — canonical plans are
  input artifacts consumed by workflow stages, not the workflow schema itself.
- **Complements:** ADR-pool.execution-memory-graph — future graph state can
  consume workflow stage and transition metadata.
- **Complements:** ADR-pool.pause-resume-handoff-runtime — workflow specs should
  define resumable stage boundaries and required handoff fields.
- **Related:** ADR-pool.agent-execution-intelligence CAP-22 (`gz next`) —
  deterministic next-step routing can use workflow metadata once available.
- **Enables:** ADR-pool.harness-lab — candidate experiments and module ablations
  consume exported workflow objects.
- **Consumes:** ADR-pool.harness-trace-bundles — workflow stages declare which
  trace events are emitted and which bundle manifests are valid evidence.
- **Consumes:** ADR-pool.tool-permission-classifier — workflow stages declare
  their required permission mode and any command-classifier escalation policy.

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. The initial schema boundary is accepted as JSON-only and gzkit-native.
2. The first workflow target is confirmed as `obpi-pipeline`.
3. Export-first sequencing is accepted: describe existing runtime before
   enabling user-authored workflow execution.
4. Required field set is approved: stages, gates, evidence, receipts,
   attestation, ledger events, scope, and failure policy.
5. The promotion plan names which existing pipeline/runtime modules own the
   source of truth for exported data.
6. Runtime-charter, state-semantics, loop-policy, context-policy,
   prompt-assembly-order, permission-policy, subagent-policy, trace-policy, and
   ablation-tag fields are accepted or explicitly deferred with rationale.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

This ADR captures a gzkit intake decision from the Archon comparison: absorb the
machine-readable workflow-shape lesson, not Archon's YAML format or product
surface. gzkit remains a governed meta-harness and agent runner.

---

## Amendment 2026-05-19: Conformance matrix dimension

The `openai/symphony` SPEC.md (re-read 2026-05-19 in full) names two
mechanisms this ADR's original Target Scope implied but did not enumerate:
**§17 Test and Validation Matrix** (per-scope conformance dimensions with
REQUIRED test categories per scope) and **§18 Implementation Checklist —
Definition of Done** (REQUIRED-for-conformance vs RECOMMENDED-extensions
split, plus operational-validation-before-production list). The gzkit
equivalent is a **workflow conformance matrix** that the JSON workflow
schema MUST expose as a first-class surface — distinct from
`harness-fitness-report` (which measures operational reality), distinct
from `gz validate --<scope>` outputs (which check individual artifacts).

### Added Target Scope item

Append to § Target Scope:

- **Conformance matrix surface.** The workflow spec MUST expose a
  `conformance_matrix` field per workflow, enumerating: (a) the set of
  REQUIRED-for-conformance test categories the workflow must satisfy
  (e.g., `stage_id_uniqueness`, `gate_reference_resolves`,
  `ledger_event_in_vocabulary`, `receipt_binding_per_attestation`,
  `failure_class_per_rejection_path`); (b) the set of
  RECOMMENDED-but-not-required categories (e.g., `trace_bundle_emission`,
  `observability_event_per_stage`); (c) a structured Definition-of-Done
  block naming which CLI command produces each conformance witness and
  which ledger event records the witness. Each category resolves to one
  or more `gz validate --<scope>` invocations; the matrix is the join.

### Added CLI surfaces

```bash
gz workflow conformance path/to/workflow.json
# → renders matrix as table: each REQUIRED category, witness command,
#   pass/fail/not-run, witness receipt ID
gz workflow conformance --json path/to/workflow.json
# → same, machine-readable
gz workflow conformance-checklist path/to/workflow.json
# → renders Definition-of-Done block: which CLI verbs MUST have run and
#   produced what receipt before the workflow is conforming
```

### Conformance category schema (illustrative; closed-set at promotion time)

| Category | Required? | Witness command | Witness receipt | Failure routes to |
|---|---|---|---|---|
| `stage_id_uniqueness` | REQUIRED | `gz workflow validate` | structural-validator output | workflow author |
| `gate_reference_resolves` | REQUIRED | `gz workflow validate` | structural-validator output | workflow author |
| `ledger_event_in_vocabulary` | REQUIRED | `gz validate --workflow-event-vocab` | `arb-step-workflow-validate-*` | `ADR-pool.obpi-state-machine` rule 8 vocabulary |
| `receipt_binding_per_attestation` | REQUIRED | `gz validate --attestation-receipt-binding` | `arb-step-receipt-binding-*` | ADR-0.0.24 |
| `failure_class_per_rejection_path` | REQUIRED | `gz validate --failure-class-coverage` | `arb-step-failure-class-*` | `ADR-pool.obpi-state-machine` rule 7 taxonomy |
| `trace_bundle_emission` | RECOMMENDED | `gz harness trace inspect` | trace-bundle manifest | `ADR-pool.harness-trace-bundles` |
| `observability_event_per_stage` | RECOMMENDED | `gz harness report --surface workflow-events` | fitness-report row | `ADR-pool.harness-fitness-report` |
| `concurrency_cap_declared` | RECOMMENDED (REQUIRED for heavy lane) | `gz workflow validate` | structural-validator output | `ADR-pool.obpi-state-machine` Amendment 2026-05-02 |

### Distinct from sibling surfaces

- **Distinct from `harness-fitness-report`.** Fitness measures operational
  reality (validator-hit rate, surface weight, redundancy, retirement
  candidates) — *how the harness behaves at runtime*. The conformance
  matrix verifies that a workflow declaration satisfies the spec's
  structural requirements — *whether the workflow is well-formed*. Both
  surface together: a workflow may pass conformance but rank low on
  fitness, or pass fitness but fail conformance under a new doctrine
  release. Two orthogonal axes; the conformance matrix is the prerequisite,
  the fitness report is the operational measurement.
- **Distinct from `gz validate --<scope>` outputs.** Individual validators
  check individual artifacts (a brief, an ADR file, the manifest, the
  ledger). The conformance matrix is the *aggregator* — given a workflow
  spec, which set of validators MUST have passed for the workflow to be
  conforming. A workflow's conformance status is "all REQUIRED-category
  witness commands have produced a passing receipt." Individual `gz
  validate` exits are the inputs; the conformance matrix is the join.
- **Distinct from `obpi-state-machine` rules 7 and 8.** The state machine
  enumerates failure classes and event vocabulary as *runtime concepts*
  (what the monitor consults). The conformance matrix is a *spec concept*
  (what a workflow declaration must include and what witnesses must exist
  before the workflow is conforming). The state machine produces the
  runtime evidence; the conformance matrix verifies the evidence is
  structurally sufficient.

### Coupled-surface coherence

- **[ADR-pool.obpi-state-machine](ADR-pool.obpi-state-machine.md)
  § Amendment 2026-05-19** — supplies the rule-7 failure-class taxonomy
  and the rule-8 event vocabulary that this amendment's `failure_class_per_rejection_path`
  and `ledger_event_in_vocabulary` categories consume. The two amendments
  ship in lockstep; the workflow conformance matrix cannot validate
  rule-7 / rule-8 references without the state-machine ADR's enumerations
  being authored.
- **[ADR-pool.harness-fitness-report](ADR-pool.harness-fitness-report.md)** —
  consumes the conformance-matrix-pass-rate signal as one input to fitness
  measurement. Workflows ranking high on conformance but low on fitness
  surface as "well-formed but operationally cold" candidates for redesign;
  workflows ranking low on conformance surface as immediate
  doctrine-debt fixes.
- **[ADR-pool.harness-trace-bundles](ADR-pool.harness-trace-bundles.md)** —
  the `trace_bundle_emission` RECOMMENDED category resolves to trace-bundle
  manifest existence; trace bundles declare their workflow association so
  the conformance check can find them.
- **[ADR-0.0.53](../foundation/ADR-0.0.53-validator-remediation-payload-invariant/)
  (Draft 2026-05-19)** — `gz workflow conformance` failure output emits
  `RemediationPayload`s naming the canonical witness-command-to-run for
  each missing category. The matrix is one specific consumer of the
  payload contract.

### Distinct from Symphony

- **Workflow-scoped, not implementation-scoped.** Symphony §17 / §18
  measure conformance of an *implementation* of the Symphony spec (does
  this Rust/Python/Go service satisfy Symphony's REQUIRED categories?).
  The gzkit conformance matrix measures conformance of a *workflow
  declaration* (does this OBPI-pipeline / patch-release / ADR-closeout
  workflow satisfy the gzkit workflow spec's REQUIRED structure?). gzkit
  has one implementation (the Python `gz` CLI); the conformance question
  applies per-workflow, not per-implementation.
- **Receipt-witnessed, not test-suite-witnessed.** Symphony's conformance
  is verified by running the spec's reference test suite against an
  implementation. gzkit's conformance is verified by ARB receipts produced
  during normal runtime — the same receipts that bind attestation.
  Conformance is not a separate offline check; it is a property the live
  workflow produces evidence of as it runs.
- **Distinct REQUIRED vs RECOMMENDED split.** Symphony's REQUIRED set is
  what every Symphony implementation MUST do; gzkit's REQUIRED set is
  what every conforming workflow declaration MUST include. The split
  exists in both surfaces but the surfaces are different (implementation
  vs declaration). Symphony's §18 Operational Validation Before
  Production list maps to gzkit's RECOMMENDED set, not the REQUIRED set.

### Inspired By (extended)

[openai/symphony SPEC.md](https://github.com/openai/symphony/blob/main/SPEC.md)
**§17 Test and Validation Matrix** (per-scope conformance dimensions with
REQUIRED test categories per scope: Workflow and Config Parsing, Workspace
Manager and Safety, Issue Tracker Client, Orchestrator Dispatch, Coding-
Agent App-Server Client, Observability, CLI and Host Lifecycle, Real
Integration Profile) and **§18 Implementation Checklist — Definition of
Done** (REQUIRED-for-Conformance vs RECOMMENDED-Extensions split + Operational
Validation Before Production list). The full re-read of Symphony SPEC.md on
2026-05-19 surfaced the *matrix-as-first-class-surface* pattern that this
ADR's original Target Scope omitted — workflow conformance was implicit in
"validate" but never enumerated as a structured matrix consumers can
program against. This amendment closes the enumeration gap.
