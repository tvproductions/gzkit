---
id: ADR-pool.agent-evidence-boundary-flow-controls
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: arxiv-2026-agent-evidence-boundary-flow-controls
---

# ADR-pool.agent-evidence-boundary-flow-controls: Agent Evidence and Boundary-Flow Doctrine with Enforced Flow Controls

## Status

Pool

## Intent

Capture the Agent Evidence Doctrine and Boundary-Flow Doctrine as one
enforcement-first pool ADR. The operator constraint is explicit: "a doctrine
without enforcement is noise." Therefore this pool item treats doctrine as
accepted only when it names the producer, consumer, validator, failure mode, and
receipt evidence that make the rule mechanically reviewable.

The motivating failure class is agent work that looks governed because it has
instructions, receipts, or review prose, but remains structurally unverifiable:
data crosses tool or connector boundaries without a flow policy; agent memory
stores narrative summaries instead of schema-grounded records; gate checks prove
format rather than semantics; model/provider drift changes behavior without a
compatibility gate; final answers pass while intermediate traces show
contamination or unreviewed recovery paths.

This ADR records the pool thesis that agent evidence and boundary-flow controls
are the same governance problem viewed from two sides:

- Agent evidence asks whether a claim about work is backed by structured,
  replayable, receipt-bearing facts.
- Boundary flow asks whether data movement across tools, artifacts, memory,
  models, connectors, and human review surfaces is classified, permitted, and
  checked.

## Decision

If promoted, gzkit should codify the following invariant:

> A governance rule is accepted only when it declares its producer, consumer,
> validator, failure mode, fail-closed behavior, and receipt evidence. Otherwise
> it remains rationale, not doctrine.

The promoted ADR should establish two mutually reinforcing doctrines.

### Agent Evidence Doctrine

Claims made by or about agents are valid only when backed by structured
evidence. Final responses, human-readable summaries, and remembered narrative
are not evidence by themselves. Evidence-bearing surfaces must preserve the
facts needed to replay or audit the claim: command/tool invocation, changed
artifacts, source inputs, output artifacts, model/runtime identity where
relevant, validation result, receipt ID, and the trace boundary where the claim
became true.

### Boundary-Flow Doctrine

Agent workflows must classify data movement across trust boundaries before that
movement can support gate evidence. A correct agent can still violate policy by
faithfully moving sensitive data from one benign surface to another. Every
flow-control rule must state the source, sink, sensitivity, propagation mode,
redaction requirement, validator, and gate behavior when classification is
missing or violated.

### Enforcement Rule

Any sentence promoted as doctrine from this pool ADR must map to at least one
mechanical surface:

- JSON schema or Pydantic model
- `gz validate` check
- gate or audit predicate
- ARB receipt requirement
- hook or pipeline block
- generated governance graph invariant
- CLI command that emits observed evidence

Sentences that cannot meet that bar stay in rationale.

---

## Problem Statement

gzkit already has strong governance primitives: ADR/OBPI lineage, lane and kind
classification, sensitivity review, ARB receipts, ledger events, and Gate 5
attestation. The remaining class of failures is not "no governance exists"; it
is "the governance surface is too narrative or too local to catch
cross-boundary agent behavior."

Recent agent-system papers sharpen the failure pattern:

- MCP-style tools can compose benign permissions into cross-boundary credential
  or sensitive-data propagation.
- Terminal-agent benchmarks can be reward-hackable when tests verify shallow
  output instead of semantic completion.
- Agent memory must behave like a system of record for stable state, not like
  retrieved prose.
- Workflow evaluation needs execution traces, audit logs, service state, and
  artifacts, not just final answers.
- Model updates are supply-chain changes when model behavior is a dependency.
- Multi-agent workflows can suffer trace-level contamination that final
  correctness alone does not reveal.

The shared answer is not another prose rule. The shared answer is a flow-control
and evidence-control layer that makes these claims fail closed.

---

## Target Scope

When promoted, this pool ADR should decompose into implementation units that
deliver the following controls.

1. **Flow-control manifest and schema**

   Define a versioned manifest for agent/tool/artifact/model flows. Candidate
   path: `data/agent_flow_controls.json` with schema under
   `src/gzkit/schemas/agent_flow_controls.json` and Pydantic models under
   `src/gzkit/models/`. Required fields should include:

   - `id`
   - `source`
   - `sink`
   - `boundary`
   - `sensitivity`
   - `allowed_propagation`
   - `redaction_required`
   - `validator`
   - `receipt_prefix`
   - `failure_mode`

2. **Flow-control validator**

   Add a `gz validate --flow-controls` scope that validates the manifest,
   detects missing source/sink classification, checks propagation rules against
   existing sensitivity surfaces, and exits non-zero when a governed flow lacks
   a policy.

3. **Trace-native receipt extension**

   Extend ARB or adjacent receipt schemas so gate-critical receipts can carry
   structured trace facts: commands, tools, files read/written, artifacts
   produced, source/sink labels, model/runtime identity where applicable, and
   receipt parentage. Heavy-lane evidence should be able to cite these receipt
   IDs instead of relying on narrative reconstruction.

4. **Adversarial gate-test metadata**

   Require gate-critical tests or verification fixtures to declare the semantic
   assertion, hard negative, reward-hack vector, and observed-output command
   they defend. A validator should fail missing metadata for tests that carry
   governance coverage markers.

5. **Schema-grounded memory writes**

   Treat handoffs, insights, locks, claims, and evidence summaries as records
   with explicit `unknown`, `superseded`, `source_event`, and `validated_by`
   semantics where state matters. Narrative notes may accompany records, but may
   not replace the structured write path.

6. **Model/runtime compatibility gates**

   Define model/runtime behavior as a supply-chain dependency when a gate,
   receipt, validator, or generated artifact depends on it. Add a compatibility
   manifest and a validation path for model/provider drift that can block
   gate-critical evidence until focused checks pass.

7. **Governance graph invariants**

   Export or derive a graph connecting ADRs, OBPIs, rules, schemas, validators,
   receipts, skills, hooks, and flow-control records. Add checks for orphaned
   rules, rules with no validator, validators with no documented rule, and
   producer/consumer drift.

---

## Enforcement Control Matrix

| Claim | Producer | Consumer | Validator | Fail-Closed Behavior | Evidence |
|---|---|---|---|---|---|
| Boundary flows are classified before use | Flow-control manifest | Tool, connector, receipt, and audit surfaces | `gz validate --flow-controls` | Missing or escaped classification blocks gate evidence | ARB flow-control receipt |
| Gate tests assert semantics | Test metadata beside governance-covered tests | `gz test`, `gz adr audit-check`, reviewers | Test metadata validator | Coverage marker without semantic/hard-negative metadata fails | Test receipt plus metadata finding |
| Memory is schema-grounded | Handoff, insight, lock, claim writers | Session orientation, status views, attestation drafting | JSONL/schema validation | Narrative-only state cannot satisfy evidence requirements | Schema validation receipt |
| Receipts preserve trace facts | ARB and gate commands | Attestation, audit, closeout | Receipt schema validator | Heavy-lane receipt without required trace fields is invalid | `arb-*` or `arb-step-*` receipt |
| Model drift is a supply-chain event | Model/runtime manifest | Gate-critical model-dependent checks | Compatibility validator | Unpinned or drifted model blocks dependent evidence | Compatibility-suite receipt |
| Doctrine has an enforcing surface | Rule, ADR, or skill author | Agent control surfaces and validators | Governance graph invariant | Orphan doctrine is advisory only, not binding | Graph validation receipt |

---

## Alternatives Considered

1. **Separate Agent Evidence and Boundary-Flow ADRs**

   Rejected for the pool record. The concepts are separable in prose but coupled
   in enforcement. A boundary-flow violation becomes visible through evidence,
   and evidence is only meaningful if its inputs and propagation path are
   classified.

2. **Doctrine-only ADR**

   Rejected. The operator explicitly named the failure: doctrine without
   enforcement is noise. A doctrine-only ADR would expand the instruction
   surface without reducing the vibing surface.

3. **Security-only flow controls**

   Rejected as too narrow. ADR-0.0.22 already establishes security sensitivity.
   This pool ADR generalizes the enforcement pattern to all gate-critical agent
   evidence and data movement, while still reusing security sensitivity as one
   axis.

4. **Receipt-only enhancement**

   Rejected as incomplete. Better receipts make claims auditable, but they do
   not by themselves classify whether the underlying data movement was allowed.

5. **Runtime monitoring first**

   Deferred. Runtime monitoring may eventually be useful, but gzkit's first
   enforceable surface should be repository-native: schemas, manifests,
   validators, gate predicates, and receipts.

---

## Dependencies

- **Builds on**: ADR-0.0.22 security sensitivity doctrine; ADR-0.0.24
  attestation receipt binding; ADR-0.23.0 agent burden of proof.
- **Related pool entries**:
  ADR-pool.agent-reliability-framework,
  ADR-pool.agentic-security-review,
  ADR-pool.content-injection-scanning,
  ADR-pool.execution-memory-graph,
  ADR-pool.semantic-recall-over-ledger,
  ADR-pool.multimodal-evidence-binding,
  ADR-pool.contract-surface-mechanical-defenses.
- **Likely lane on promotion**: heavy. This changes schema contracts,
  validation behavior, receipt shape, and gate evidence semantics.
- **Likely kind on promotion**: foundation if promoted as doctrine/invariant;
  feature if narrowed to one CLI capability such as `gz validate
  --flow-controls`.

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human chooses whether the first promotion is foundation-wide doctrine or a
   narrower feature slice.
2. The minimum viable flow-control manifest fields are accepted.
3. The first validator scope is chosen (`gz validate --flow-controls` or a
   narrower name).
4. The receipt extension boundary is chosen: ARB schema extension, separate
   flow receipt schema, or both.
5. The relationship to ADR-pool.agent-reliability-framework is resolved:
   subordinate OBPI, superseding foundation, or peer dependency.

---

## Inspired By

- [MCPHunt: An Evaluation Framework for Cross-Boundary Data Propagation in Multi-Server MCP Agents](https://arxiv.org/abs/2604.27819) - cross-boundary propagation can arise from faithful tool composition, not only malicious behavior.
- [What Makes a Good Terminal-Agent Benchmark Task](https://arxiv.org/abs/2604.28093) - adversarial, difficult, legible verification blocks reward-hackable evaluation.
- [From Unstructured Recall to Schema-Grounded Memory](https://arxiv.org/abs/2604.27906) - reliable memory needs schemas and validated write paths, not retrieval-only recall.
- [Claw-Eval-Live](https://arxiv.org/abs/2604.28139) - workflow-agent evaluation should ground both external demand and verifiable agent action.
- [Test Before You Deploy: Governing Updates in the LLM Supply Chain](https://arxiv.org/abs/2604.27789) - model behavior drift is a deployer-side supply-chain governance problem.
- [Trace-Level Analysis of Information Contamination in Multi-Agent Systems](https://arxiv.org/abs/2604.27586) - final correctness and trace integrity are related but distinct evidence dimensions.
- [Knowledge Graph Representations for LLM-Based Policy Compliance Reasoning](https://arxiv.org/abs/2604.27713) - policy surfaces become more checkable when represented as queryable graph structure.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No new runtime connector implementation in the pool stage.
- No claim that every agent action must be logged at full fidelity.
- No replacement for existing security sensitivity rules; flow controls compose
  with them.
- No model-provider-specific policy.
- No formal verification of model reasoning. This governs artifacts, flows,
  traces, and evidence.

---

## Open Questions

1. Should the first validator operate only on declared manifests, or also infer
   flows from receipts and tool traces?
2. Should flow controls live under `data/`, `.gzkit/`, or both?
3. Should `allowed_propagation` be a closed enum such as `blocked`, `redacted`,
   `internal_only`, `task_mandated`, and `human_attested`?
4. How should flow-control receipts relate to existing ARB receipt prefixes?
5. Which existing narrative state surfaces should be converted first:
   handoffs, insights, locks, closeout evidence summaries, or all of them?
6. Should governance graph invariants be implemented as a `gz state` extension,
   a `gz validate` scope, or a dedicated audit command?

---

## Notes

Pool ADRs are backlog items - they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
