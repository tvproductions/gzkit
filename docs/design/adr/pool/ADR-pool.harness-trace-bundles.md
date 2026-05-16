---
id: ADR-pool.harness-trace-bundles
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: "arXiv:2603.28052v1 Meta-Harness; arXiv:2603.25723 Natural-Language Agent Harnesses"
complements:
  - ADR-pool.harness-lab
  - ADR-pool.workflow-specification
  - ADR-pool.skill-tuning-feedback-loop
  - ADR-pool.canonical-vs-runtime-separation
  - ADR-pool.tool-permission-classifier
---

# ADR-pool.harness-trace-bundles: Harness Trace Bundles

## Status

Pool

## Date

2026-05-16

## Intent

Create a schema-governed, path-addressable trace bundle surface for raw
harness execution evidence: prompts and rendered control surfaces, tool calls,
command runs, file reads/writes, child-agent boundaries, state transitions,
validator decisions, failure classifications, and budget/cost observations.
Trace bundles make raw harness behavior inspectable rather than remembered.

The Meta-Harness result is narrow and directly applicable to gzkit: harness
improvement depends on raw execution traces, not only scalar scores or
summaries. gzkit already has ledger events and ARB receipts, but those surfaces
are intentionally terse. They prove governance decisions and QA-step outcomes;
they do not preserve enough diagnostic context to explain why a harness,
workflow, skill, or validator behaved the way it did.

The NLAH/IHR result adds a second pressure: executable natural-language
harnesses need durable artifacts with explicit state semantics. A trace bundle
is the durable object later stages, review agents, harness-lab runs, and
operators can reopen without relying on narrative recall.

## Decision

When promoted, define a `gzkit.harness_trace_bundle.v1` schema and storage
contract for raw harness traces. The bundle is a diagnostic proof surface, not
ledger truth.

Required bundle shape:

```text
run_id
schema
created_at
root_commit
workspace_id
harness_surface
workflow_ref
task_refs
control_surface_snapshot
event_log
artifact_manifest
receipt_refs
ledger_event_refs
failure_classifications
budget
redactions
hashes
retention_policy
```

The event log should support typed entries for:

- `control_surface_rendered`
- `prompt_presented`
- `tool_call_started`
- `tool_call_finished`
- `command_started`
- `command_finished`
- `file_read`
- `file_written`
- `child_agent_spawned`
- `child_agent_returned`
- `state_transition`
- `validator_result`
- `hook_blocked`
- `permission_classified`
- `permission_escalated`
- `failure_classified`
- `evidence_presented`

Storage root is a promotion-time decision. Candidate roots:

- `artifacts/harness-traces/<run-id>/` if the design follows the current ARB
  `artifacts/receipts/` precedent.
- `.gzkit/receipts/harness-traces/<run-id>/` if
  `ADR-pool.canonical-vs-runtime-separation` lands first and moves runtime
  evidence under a unified `.gzkit/receipts/` tree.

In either case, the ledger stores only accepted governance decisions and stable
pointers/hashes. The full trace payload is not written to `.gzkit/ledger.jsonl`.

## Authority Rules

1. **Trace bundles are diagnostic evidence, not completion proof.** Gate
   completion still depends on L1 canon, L2 ledger events, ARB receipts, and
   human attestation where required.
2. **Ledger events may point to bundles.** Accepted decisions can cite a bundle
   manifest path plus content hash.
3. **No unverifiable bundle citation.** A cited bundle must have a manifest,
   schema version, root commit, and hash over included event files.
4. **Trace capture is not autonomous self-improvement.** Trace bundles may feed
   proposals, skill tuning, and harness-lab reports, but canon changes still go
   through ADR/OBPI/Gate 5 discipline.
5. **Redaction is first-class.** Bundle manifests must record omitted or redacted
   fields. A redacted trace is acceptable; an unexplained missing trace segment
   is a defect.

## Target Scope

- Define `gzkit.harness_trace_bundle.v1` Pydantic model and JSON Schema.
- Add a manifest writer and validator.
- Add `gz trace validate <path>` or an equivalent validator surface.
- Add helper APIs for pipeline runtime, skill tuning, harness lab, and sidecar
  consumers to append typed trace events without inventing per-surface formats.
- Define privacy and retention policy fields before any bundle can be committed
  as durable evidence.
- Add docs explaining how trace bundles differ from ARB receipts and ledger
  events.

## Non-Goals

- No raw transcript dumping into the ledger.
- No requirement that every normal `gz check` invocation records a full trace.
- No autonomous patch promotion based on trace analysis.
- No vendor-specific transcript format as the canonical schema.
- No commitment to retaining high-volume traces forever.

## Alternatives Considered

1. **Store only scalar scores and summaries.** Rejected. Meta-Harness shows that
   compressed feedback loses the information needed for harness diagnosis.
2. **Store trace text directly in ledger events.** Rejected. The ledger is the
   authoritative event log, not a bulk transcript database. Large traces would
   poison reviewability and make L2 state carry diagnostic payloads it should
   only reference.
3. **Let each consumer define its own trace format.** Rejected. Skill tuning,
   harness lab, sidecar, workflow export, and review stages would drift into
   incompatible proof shapes.
4. **Use vendor transcripts as the trace source of truth.** Rejected. Vendor
   transcripts are useful inputs, but gzkit needs a vendor-neutral trace schema
   with explicit state semantics and redaction policy.

## Dependencies

- **Enables:** `ADR-pool.harness-lab` candidate-run store and ablation reports.
- **Enables:** `ADR-pool.skill-tuning-feedback-loop` trace-backed candidate
  comparison.
- **Complements:** `ADR-pool.workflow-specification`; workflow stage IDs should
  appear in trace events.
- **Complements:** `ADR-pool.agent-evidence-boundary-flow-controls`; trace
  events provide the raw boundary facts that evidence-flow audits consume.
- **Complements:** `ADR-pool.tool-permission-classifier`; permission decisions
  and escalations should be traceable as typed events.
- **May depend on:** `ADR-pool.canonical-vs-runtime-separation` for final
  storage-root doctrine.

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. The operator accepts the storage-layer distinction: ledger for decisions,
   trace bundles for diagnostic payloads.
2. The first producing surface is selected; recommended first producer is
   `gz obpi pipeline` Stage 3/4 or `skill_tuning` episodes.
3. The storage root is chosen in light of
   `ADR-pool.canonical-vs-runtime-separation`.
4. Redaction and retention fields are accepted as required manifest data.
5. The first consumer is selected; recommended first consumer is
   `ADR-pool.harness-lab`.

## Notes

Pool ADRs are backlog items -- they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
