---
id: ADR-pool.vendor-capability-matrix
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: vendor-alignment-codex-2026-04
---

# ADR-pool.vendor-capability-matrix: Vendor Capability Matrix

## Status

Pool

## Date

2026-04-23

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Create a canonical, source-cited vendor capability matrix that separates
upstream vendor capability truth from gzkit support state and local
feature-flag policy. Vendor-alignment ADRs currently risk becoming stale prose:
they record point-in-time Codex, Claude Code, Copilot, Gemini CLI, and OpenCode
facts inside implementation narratives. That makes every vendor ADR responsible
for both design decisions and ongoing product surveillance.

This pool ADR captures the durable substrate: a machine-readable capability
registry, validation rules, and read-only CLI rendering surface. ADRs such as
`ADR-0.44.0-vendor-alignment-codex` should consume the matrix instead of
embedding the full current capability inventory themselves.

---

## Problem

The current vendor-alignment pattern has three failure modes:

- **Stale prose**: current vendor facts live in ADR text and age silently.
- **Conflated meanings**: "Codex has hooks", "gzkit supports Codex hooks",
  and "gzkit policy enables Codex hooks" can collapse into one ambiguous claim.
- **Uneven parity decisions**: each vendor ADR re-discovers maturity, feature
  availability, source links, and policy constraints independently.

The Codex alignment discussion exposed the issue directly. Codex baseline
capabilities now include config, hooks, skills, subagents, plugins, MCP,
memories, automations, sandbox/approval policies, and cross-surface execution
modes. Some are stable, some are experimental, and some are deliberately
disallowed by gzkit policy. ADR prose is the wrong durable home for that matrix.

## Decision

Introduce a vendor capability matrix as canonical data, with feature flags used
only for local enablement and policy.

### Canonical Registry

Store vendor capability rows under a dedicated canonical directory, for example:

```text
.gzkit/vendor-capabilities/
  codex.yaml
  claude-code.yaml
  copilot.yaml
  gemini-cli.yaml
  opencode.yaml
```

Each row records descriptive upstream truth, gzkit integration state, and local
policy links without treating any one as a substitute for the others.

Recommended fields:

| Field | Meaning |
|---|---|
| `vendor` | Canonical vendor id, e.g. `codex` or `claude-code` |
| `capability_id` | Stable dotted id, e.g. `hooks.pre_tool_use` |
| `category` | Grouping such as `hooks`, `skills`, `memory`, `automation`, `mcp` |
| `surface` | Product surface: `cli`, `ide`, `app`, `web`, `github`, `slack`, etc. |
| `upstream_maturity` | Vendor-published maturity state |
| `gzkit_support` | Local integration state |
| `enforcement_locus` | Where gzkit enforces or observes the capability |
| `feature_flag` | Optional flag key controlling local enablement |
| `policy_default` | Recommended default for generated configs |
| `source_url` | Authoritative upstream documentation link |
| `source_checked_at` | Date the source was last verified |
| `notes` | Short caveat, especially when parity is non-textual |

Example row:

```yaml
vendor: codex
capability_id: hooks.pre_tool_use
category: hooks
surface: cli
upstream_maturity: experimental
gzkit_support: documented
enforcement_locus: codex_hook_or_runtime_guard
feature_flag: vendor.codex.hooks.enabled
policy_default: false
source_url: https://developers.openai.com/codex/hooks/
source_checked_at: 2026-04-23
notes: "Hooks exist, but only portable invariants may be mapped."
```

### State Model

Separate upstream capability maturity from gzkit readiness:

| Axis | States |
|---|---|
| `upstream_maturity` | `stable`, `beta`, `experimental`, `preview`, `unavailable`, `unknown` |
| `gzkit_support` | `unsupported`, `observed`, `documented`, `generated`, `validated`, `enforced` |

This split prevents a disabled feature flag from implying that a vendor lacks a
capability. For example, `vendor.codex.automations.worktrees_allowed = false`
means gzkit policy disallows that operating mode; it does not mean Codex lacks
automation support.

### Feature Flag Boundary

Use the existing ADR-0.0.8 feature flag machinery for local enablement and
policy only. Do not store upstream capability facts in `data/flags.json`.

Example policy flags:

- `vendor.codex.hooks.enabled`
- `vendor.codex.memories.allowed`
- `vendor.codex.automations.local_project_allowed`
- `vendor.codex.automations.worktrees_allowed`
- `vendor.claude-code.hooks.enabled`
- `vendor.claude-code.agent_teams.enabled`

The capability registry may reference a flag, but the flag registry does not
replace the capability row.

### Validation

Add a validation scope:

```bash
uv run gz validate --vendor-capabilities
```

Validation should fail on:

- missing or malformed `source_url`
- stale or missing `source_checked_at`
- invalid `upstream_maturity` or `gzkit_support` enum
- referenced `feature_flag` absent from `data/flags.json`
- `policy_default: true` on `experimental` capability without explicit
  justification
- vendor policy violations such as `vendor.codex.automations.worktrees_allowed`
  resolving to `true`

### Rendering

Add read-only operator surfaces:

```bash
uv run gz vendor matrix
uv run gz vendor matrix --vendor codex
uv run gz vendor matrix --vendor codex --compare claude-code
uv run gz vendor capability codex hooks.pre_tool_use
```

All rendering commands should support `--json` and table output. ADRs,
runbooks, and agent prompts should cite matrix rows rather than duplicating
capability inventories inline.

### Relationship to ADR-0.44.0

`ADR-0.44.0-vendor-alignment-codex` should consume this matrix once promoted
work begins. Its Codex-specific OBPIs remain valid, but their inputs should be
matrix rows:

- config generation consumes Codex config/sandbox/approval rows
- hooks policy consumes Codex hook rows and portability classifications
- skills/personas/subagents consumes Codex skill and subagent rows
- docs and validation consume matrix freshness and support-state checks

The matrix is not a replacement for vendor alignment ADRs. It is the fact base
those ADRs consume.

---

## Target Scope

- Canonical `.gzkit/vendor-capabilities/*.yaml` registry.
- Pydantic models and loader for capability rows.
- JSON schema or equivalent validation contract.
- `gz validate --vendor-capabilities` scope.
- Read-only `gz vendor matrix` and `gz vendor capability` CLI surfaces.
- Integration with existing feature flag registry for policy references.
- Documentation explaining the capability/flag/policy split.
- Initial seed rows for Codex and Claude Code sufficient to support
  `ADR-0.44.0` planning.

---

## Non-Goals

- No attempt to auto-scrape vendor documentation in the first increment.
- No replacement of ADRs with a matrix; ADRs still record decisions.
- No use of feature flags as upstream fact storage.
- No generated vendor configs in this ADR; vendor alignment ADRs own those.
- No worktree-based Codex automation enablement; gzkit policy disallows that
  operating mode unless a future ADR explicitly reverses it.

## Alternatives Considered

1. **Keep capability facts in vendor ADR prose.** Rejected because capability
   facts are ongoing surveillance data, while ADRs are decision records. Mixing
   them makes every vendor ADR stale by default.
2. **Put capability booleans directly in feature flags.** Rejected because
   feature flags answer "may gzkit enable this locally?", not "does the vendor
   provide this upstream?" Flags are policy, not product truth.
3. **Use one cross-vendor comparison document.** Rejected because a Markdown
   matrix is readable but not enforceable. The durable form needs schema,
   validation, JSON output, and source freshness checks.
4. **Fold the matrix into `ADR-0.44.0`.** Rejected because Codex alignment is
   only the forcing example. Claude Code, Copilot, Gemini CLI, OpenCode, and
   future vendors need the same capability substrate.

---

## Dependencies

- **Blocks on**: None.
- **Blocked by**: Status/ledger recognition drift around
  `ADR-0.44.0-vendor-alignment-codex` should be resolved before promoted
  implementation depends on matrix-derived status outputs.
- **Related**: ADR-0.0.8-feature-toggle-system,
  ADR-pool.vendor-alignment-codex, ADR-0.44.0-vendor-alignment-codex,
  ADR-pool.vendor-alignment-claude-code, ADR-pool.vendor-alignment-copilot,
  ADR-pool.vendor-alignment-gemini-cli, ADR-pool.vendor-alignment-opencode,
  ADR-pool.universal-agent-onboarding, ADR-pool.harness-aware-execution-modes.

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human chooses whether the promoted ADR is foundation-kind or feature-kind.
   Recommended: foundation-kind, because it defines a durable source-of-truth
   model and validation contract.
2. Initial capability taxonomy and enum states are accepted.
3. Feature flag boundary is accepted: flags are local policy, not upstream
   truth.
4. Staleness threshold for `source_checked_at` is chosen.
5. Minimum seed vendors are chosen. Recommended: Codex and Claude Code first,
   then Copilot, Gemini CLI, and OpenCode.
6. Relationship to `ADR-0.44.0` is ratified: Codex alignment consumes the
   matrix rather than owning the full product capability inventory.

---

## Notes

- This should be heavy lane when promoted if it adds validation scopes, CLI
  surfaces, schemas, or feature flag policy checks.
- The matrix should preserve source dates explicitly. A stale source should be
  visible to operators even when the row remains syntactically valid.
- The first implementation should be read-only. Write/update automation can be
  designed later if manual upkeep proves too expensive.
- The term "capability" should remain vendor/product focused. Gzkit readiness
  belongs in `gzkit_support`; local enablement belongs in feature flags.
