---
id: ADR-pool.tool-permission-classifier
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: "Harness architecture checklist: permissions and safety layer"
complements:
  - ADR-pool.harness-aware-execution-modes
  - ADR-pool.workflow-specification
  - ADR-pool.sandboxed-delegation
  - ADR-pool.agent-execution-intelligence
  - ADR-pool.agent-evidence-boundary-flow-controls
  - ADR-pool.harness-trace-bundles
---

# ADR-pool.tool-permission-classifier: Tool Permission Classifier

## Status

Pool

## Date

2026-05-16

## Intent

Define a deterministic permission-classification surface for agent tools,
commands, and governance mutations so gzkit can express the safety layer of its
meta-harness explicitly instead of relying on vendor prompts or prose rules
alone.

The practical harness checklist separates a useful harness from a dangerous one
through permissions: every tool declares a minimum permission, shell-like tools
are classified dynamically by command intent, and destructive actions require
explicit approval. gzkit already has governance safety through lanes, gates,
allowed paths, hooks, and attestation. The missing piece is a shared classifier
that names the permission level for a proposed tool/action before either Mode 1
skill-chain checks or Mode 2 hooks allow it to run.

## Decision

When promoted, add a `gzkit.tool_permission_policy.v1` schema and deterministic
classifier API. Candidate operator-facing surfaces:

```bash
gz permission classify --tool Bash --input command.json
gz permission validate --policy .gzkit/tool-permissions.json
gz harness mode --show-permissions
```

Initial permission levels:

- `read`: no filesystem, ledger, network, process, or workspace mutation.
- `workspace`: mutates files or generated artifacts inside declared allowed
  paths.
- `governance`: mutates canonical governance state, ledger-linked artifacts, or
  lifecycle markers.
- `external`: crosses repository, network, credential, connector, or user-account
  boundaries.
- `full`: destructive, privilege-changing, secret-touching, or irreversible
  actions.

Initial classifier inputs:

- `tool_name`
- `vendor_harness`
- `declared_mode`
- `workflow_stage`
- `task_refs`
- `allowed_paths`
- `command_text` or structured tool input
- `state_target`
- `external_boundary_refs`
- `human_approval_ref`

Initial classifier output:

```text
permission_level
decision
reason
matched_rules
required_approval
trace_event
```

The classifier must be deterministic Python, not an LLM judgment. If a command
cannot be classified safely, the result is `full` or `deny`, not best-effort
execution.

## Target Scope

- Define the permission policy Pydantic model and JSON Schema.
- Add a command classifier for shell-like tools with explicit safe, workspace,
  governance, external, and full-access categories.
- Integrate with `ADR-pool.harness-aware-execution-modes`:
  - Mode 1 uses the classifier at skill-chain transition and token-verification
    points.
  - Mode 2 hooks use the classifier before tool execution where the vendor
    exposes PreToolUse-style interception.
- Integrate with `ADR-pool.workflow-specification` through `permission_policy`
  fields on stages.
- Integrate with `ADR-pool.sandboxed-delegation` so subagent policy tiers map to
  classifier levels.
- Emit `permission_classified`, `permission_escalated`, or `permission_denied`
  trace events when `ADR-pool.harness-trace-bundles` is available.

## Non-Goals

- No replacement for OS sandboxing or vendor sandbox controls.
- No LLM-based safety judgment.
- No promise that every vendor harness exposes enough lifecycle hooks for
  pre-tool enforcement.
- No automatic escalation from a lower permission tier to a higher one without a
  recorded human approval reference.
- No broad rewrite of existing gate, lane, or attestation doctrine.

## Alternatives Considered

1. **Rely on vendor permission prompts.** Rejected. Vendor prompts are useful but
   uneven across harnesses and do not encode gzkit-specific governance state.
2. **Keep permissions as prose in AGENTS.md and skills.** Rejected. Prose can
   guide agents, but it cannot be reused by workflow specs, hooks, delegation
   policy, trace bundles, or validators.
3. **Treat Bash as one permission level.** Rejected. The same shell tool can be
   read-only, workspace-mutating, governance-mutating, external-boundary crossing,
   or destructive depending on command content.
4. **Build a vendor-neutral hook abstraction first.** Rejected. The classifier is
   vendor-neutral policy; hook enforcement remains per-vendor as described in
   `ADR-pool.harness-aware-execution-modes`.

## Dependencies

- **Consumes:** `ADR-pool.harness-aware-execution-modes` for Mode 1/Mode 2
  enforcement boundaries.
- **Feeds:** `ADR-pool.workflow-specification` through stage-level
  `permission_policy`.
- **Feeds:** `ADR-pool.sandboxed-delegation` through subagent policy tiers and
  blocked-tool lists.
- **Feeds:** `ADR-pool.harness-trace-bundles` through permission trace events.
- **Complements:** `ADR-pool.agent-evidence-boundary-flow-controls`; the
  classifier decides whether a proposed action crosses an evidence, credential,
  connector, or account boundary.

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. The operator accepts the permission-level vocabulary.
2. The first enforcement point is selected; recommended first point is Mode 2
   PreToolUse where available, with Mode 1 transition validation as fallback.
3. The first command classifier rule set is approved.
4. The workflow-spec `permission_policy` field shape is accepted.
5. Trace events for classified, escalated, and denied permissions are accepted
   or explicitly deferred.

## Notes

Pool ADRs are backlog items -- they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
