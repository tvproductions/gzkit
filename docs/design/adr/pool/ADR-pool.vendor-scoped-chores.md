---
id: ADR-pool.vendor-scoped-chores
status: Pool
lane: heavy
parent: ADR-0.8.0-gz-chores-system
---

# ADR-pool.vendor-scoped-chores: Vendor-Scoped Chores

## Status

Pool

## Date

2026-04-04

## Parent ADR

[ADR-0.8.0-gz-chores-system](../pre-release/ADR-0.8.0-gz-chores-system/ADR-0.8.0-gz-chores-system.md)

---

## Intent

The chore registry treats all chores as universal — every chore surfaces for
every agent harness. But some maintenance tasks are vendor-specific (Claude Code
has auto-memory, Codex and Copilot don't). Today there's no way to express this,
so vendor-specific chores either surface uselessly for the wrong harness or don't
get registered at all. The immediate trigger is a memory-hygiene chore that should
audit Claude Code's auto-memory for process corrections that drifted into
machine-local storage instead of governed artifacts — but registering it means it
shows up for Codex runs where it's meaningless.

---

## Decision

1. Add optional `vendor` field to `ChoreDefinition` — null means universal, a
   string value means harness-specific
2. CLI filters at discovery time — `gz chores list`, `advise`, and `run` skip
   non-matching vendor chores
3. Harness detection uses existing config/environment signals, not a new flag
4. First consumer: `memory-hygiene` chore with `vendor: "claude"` that scans
   auto-memory and flags process drift
5. Existing chores unaffected — missing `vendor` defaults to universal

**Broader pattern:** This establishes vendor scoping beyond chores. Hooks, skills,
and other surfaces can adopt the same field. The baseline (universal) vs extension
(vendor-scoped) split is the real design value — it creates the mechanism for
defining what every harness gets versus what's harness-specific.

---

## Target Scope

### 1. Chore Schema Extension

- Add optional `vendor` field to `ChoreDefinition` Pydantic model
- `vendor: str | None = Field(None, description="Harness this chore applies to")`
- `extra="forbid"` means this is a schema-breaking change requiring model update
- Registry JSON gains optional `"vendor": "claude"` per chore entry

### 2. Harness Detection

- At chore discovery time, detect the active harness (Claude Code, Codex, etc.)
- Filter chores whose `vendor` field doesn't match the active harness
- Chores with `vendor: null` always surface (universal)
- Detection mechanism: environment signals or config (not a new CLI flag)

### 3. CLI Surface Changes

- `gz chores list` shows vendor column when any vendor-scoped chore exists
- `gz chores list --vendor claude` filters to vendor-specific chores
- `gz chores advise` and `gz chores run` skip inapplicable vendor chores with a note

### 4. Memory Hygiene Chore (First Consumer)

- Register `memory-hygiene` chore with `vendor: "claude"`
- CHORE.md workflow: scan memory files, classify by type, flag process drift
- Acceptance criteria: feedback/project memories identified, migration candidates listed
- Does not auto-delete memories — surfaces recommendations for operator review

### 5. Existing Chore Migration

- All existing chores gain `vendor: null` (universal) — no behavioral change
- Registry format remains backward-compatible (missing `vendor` = universal)

---

## Alternatives Considered

1. **Naming convention** (prefix chores with vendor, e.g. `claude-memory-hygiene`) —
   rejected because naming conventions aren't machine-enforceable; the CLI can't
   filter on a prefix pattern reliably, and it's a social contract not a schema
   contract
2. **Separate registries per vendor** — rejected because it fragments the
   single-registry model, duplicates execution infrastructure, and means
   `gz chores list` can't show the full picture
3. **Let agents skip via skill instructions** — rejected because it pushes vendor
   filtering into the LLM context instead of the deterministic CLI layer; agents
   can and do ignore soft instructions

---

## Consequences

### Positive

1. Vendor-specific maintenance becomes a first-class registry concept
2. Establishes the vendor scoping pattern that hooks, skills, and other surfaces
   can adopt later
3. Memory drift detection becomes a governed periodic operation instead of ad-hoc
   corrections
4. Non-applicable chores stop cluttering output for wrong harnesses
5. Creates the baseline/extension mechanism — universal chores every harness gets,
   vendor-specific extensions on top

### Negative

1. Schema change to `ChoreDefinition` (`extra="forbid"`) — technically breaking
   registry contract
2. Harness detection is a new runtime concern — gzkit must now know which harness
   is driving it
3. `vendor` field adds a maintenance dimension — authors must decide universal vs
   scoped per chore
4. Risk of over-scoping: chores that should be universal might get vendor-tagged
5. Overall complexity increase that threatens to introduce new unseen conflicts
   and contradictions across the vendor dimension

---

## Non-Goals

- Changing the chore execution model (advise/run/audit lifecycle unchanged)
- Auto-migrating memory content to skills/rules (human judgment required)
- Disabling auto-memory (operator choice, not governance mandate)
- Supporting per-chore vendor *lists* (single vendor or universal; multi-vendor
  is YAGNI)
- Vendor scoping for non-chore surfaces (hooks, skills) — this ADR establishes
  the pattern; adoption in other surfaces is future work

---

## Evidence of Need

During ADR-0.0.12 audit (2026-04-04), the agent wrote two memories for process
corrections instead of fixing the audit skill. The operator identified that:

1. Memory is machine-local and cannot be made project-portable
2. Memory creates a shadow persistence layer competing with governed artifacts
3. The correction loop (detect drift → migrate to governed artifact) should be a
   chore, not ad-hoc
4. The chore only applies to Claude Code — no mechanism to express this today

Related: tvproductions/gzkit#90

---

## Lane Justification

**Heavy** — Changes the chore schema contract (`ChoreDefinition` model with
`extra="forbid"`), adds a CLI column to `gz chores list`, and introduces
harness-detection behavior. These are external contract changes requiring
docs and BDD verification.

---

## Interview

Conducted conversationally (2026-04-04) with answers recorded via
`gz interview adr --from`. Answers file:
`docs/design/adr/pool/vendor-scoped-chores-interview.json`

---

## Dependencies

- ADR-0.8.0-gz-chores-system (chore registry and execution model)
- Claude Code auto-memory system (external, not governed by gzkit)
