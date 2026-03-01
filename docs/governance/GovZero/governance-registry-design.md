# GovZero Ontology Design

**Status:** Draft
**Last reviewed:** 2026-02-15
**Authority:** Design document (pre-ADR)
**Inspired by:** [Palantir Ontology](https://www.palantir.com/docs/foundry/architecture-center/ontology-system/),
ISO 27001 Controls Framework, NIST Cybersecurity Framework,
[Aircraft Manufacturing Process](https://engineerfix.com/the-step-by-step-aircraft-manufacturing-process/)

---

## Motivation

AirlineOps has a product and a factory.

The **product** is an airline scheduling and operations platform --- CLI
commands, warehouse adapters, data pipelines, configuration schemas. ADRs
specify what to build. OBPIs hold the implementation to exact spec, like
jigs holding aircraft parts in sub-millimeter alignment during assembly.
Gates 1-4 verify the aircraft works.

The **factory** is the governance system that ensures the product is built
correctly --- enforcement hooks, policy tests, chores, skills, instruction
files, agent contracts, attestation ceremonies. Process rules constrain how
agents work. The factory is what makes three different AI agents (Claude,
Codex, Copilot) produce consistent, quality results.

In aircraft manufacturing, you would never build a factory room by room,
bolting on a new assembly station every time a new variant comes along, then
ask technicians to reconstruct the full process by reading signs posted on
10 different walls. The factory has a **master process plan** --- a single
document that specifies every station, every jig, every quality gate, every
tool, and how they connect.

AirlineOps has no master process plan. The factory grew organically. Each
ADR bolted on its own enforcement wiring. Each doctrine was stated in prose
across multiple files. Each chore was created as a standalone task with no
declared connection to the rules it serves. The result: a 1:4 ratio of
product work to governance overhead. Not because governance is unnecessary,
but because the factory itself was never designed as a system.

This document designs the master process plan: the **GovZero Ontology**.

### Two Planes of Governance

Both the product and the factory must be governed. Aerospace recognizes this
with separate certifications: a Type Certificate for the aircraft (product)
and a Production Certificate for the factory (process). You can have a
perfect aircraft design and a terrible factory, or vice versa. Both must
be governed independently.

| Plane | What It Governs | Certification Analog |
|-------|----------------|---------------------|
| **"Build the right thing"** (Product) | Code behavior, data contracts, CLI design, API surfaces | Type Certificate |
| **"Build the thing right"** (Factory) | How ADRs are structured, how OBPIs are attested, how chores report, how agents are constrained | Production Certificate |

The Ontology governs both planes in a single model.

### Aircraft Manufacturing Parallels

| Aircraft Manufacturing | AirlineOps Factory |
|---|---|
| CAD/CAE models (3D design, simulation) | ADRs (design decisions, tradeoff analysis) |
| Jigs and fixtures (hold components in exact alignment) | OBPIs (hold implementation to exact spec, one brief per item) |
| Specialized tooling (purpose-built per assembly step) | Skills, chores, hooks (purpose-built per governance step) |
| Major structural assembly (sub-assemblies combined) | Product code (features assembled per OBPI specifications) |
| Ground / taxi / flight tests (sequential gates) | Gates 1-5 (ADR, TDD, Docs, BDD, Attestation) |
| Regulatory certification (FAA/EASA sign-off) | Human attestation (Gate 5 closeout ceremony) |
| Master process plan (every station, tool, gate) | GovZero Ontology (every rule, enforcement, control surface) |

The master process plan does not add work --- it **eliminates rework**. Without
it, technicians assemble parts wrong, quality catches it late, parts get
scrapped and rebuilt. The 1:4 ratio is rework cost: agents doing governance
wrong, getting caught by hooks they did not know about, redoing work that
violates rules they could not find.

### The Ontology as Factory Audit

Creating the Ontology is simultaneously a factory inspection. Every rule
mapped forces the question: is this rule earning its keep? Is its enforcement
proportional? Is it stated in the right place, or in too many places? The
deliverables of ADR-A are simultaneously the audit of the existing governance
system. Not the product --- the factory.

---

## Problem Statement

The GovZero governance system has three independently-growing dimensions with no
central model connecting them:

| Dimension | Count | Where They Live |
|-----------|-------|-----------------|
| Rules/Policies | ~600-700 | 6 CLAUDE.md, 13 instruction files, 22 GovZero docs, AGENTS.md |
| Enforcement tools | ~140 | 24 pre-commit hooks, 15 policy tests, 26 chores, opsdev commands |
| Control surfaces | ~113 | Skills (claude/codex/github), hooks, instruction files |

There is **no join table**. No artifact maps a rule to its enforcement, its
observability surface, its traceability chain, or its remediation path. The
consequences are:

1. **Agent onboarding cost:** An agent must read ~10 documents (~2,500 lines of
   prose) to reconstruct the rule landscape. Even then, it cannot answer "what
   enforces this rule?" without grepping across pre-commit hooks, policy tests,
   chores, and skills independently.

2. **Governance-of-governance gap:** Each new ADR independently wires up its own
   enforcement. There is no pattern that says "when you create a rule, register
   it here, and the enforcement chain is X."

3. **Gap invisibility:** No mechanism can answer "which rules have no automated
   enforcement?" (gap analysis), "which enforcement tools cover which rules?"
   (coverage), or "what is the compliance status of doctrine X across all its
   policies?" (observability).

4. **Productivity cost:** The ratio of product work to governance overhead
   approaches 1:4 when working with AI agents. The governance system's
   complexity is a significant contributor because rules are scattered across
   narrative prose in dozens of files rather than centrally indexed.

5. **Tool development friction:** gzkit tools must hardcode knowledge of where
   rules live, what enforcement exists, and how to check compliance. A central
   ontology would allow tools to be generic against the governance model.

6. **Agent stochasticity:** Every unconstrained decision point is a source of
   agent improvisation. Improvisation is stochasticity. Maximizing the
   machine-readable decision-space coverage directly reduces agent variance.

### The Core Question

> "What is the full set of constraints an agent must satisfy?"

No single artifact can answer this today.

---

## Design Principles

### Palantir Ontology Alignment

This design adopts terminology and structure from the
[Palantir Ontology](https://www.palantir.com/docs/foundry/architecture-center/ontology-system/)
while preserving GovZero-specific concepts where they add precision.

**Adopted from Palantir:**

- **"Ontology"** as the name for the central semantic model (not "registry")
- **Object Types** as the structural primitive for entities
- **Link Types** as first-class named relationships between objects
- **Action Types** as operational verbs with authorization boundaries
- **Three-layer architecture:** Language (schema), Engine (gzkit), Toolchain
  (control surfaces)
- **Four-fold integration model:** data, logic, action, security

**Preserved from GovZero:**

- **Control surfaces** (more precise than "toolchain" for agent instruction
  delivery: skills, hooks, instruction files, CLAUDE.md)
- **Doctrine / Policy / Rule hierarchy** (richer taxonomy than flat object
  types; Palantir has no equivalent hierarchy)
- **Attestation** (human-gate concept with no Palantir equivalent)
- **Observability** (governance-specific compliance visibility)
- **Traceability** (governance audit chain)

### ISO 27001 / NIST CSF Parallels

The Ontology follows the **controls framework** pattern used by mature
compliance systems:

| ISO 27001 | NIST CSF | GovZero Ontology |
|-----------|----------|------------------|
| Control Objective | Identify | Doctrine |
| Control | Protect | Policy / Rule |
| Statement of Applicability | — | Ontology (the file itself) |
| Audit Evidence | Detect | Observability |
| Corrective Action | Respond | Remediation |
| Management Review | Recover | Governance (self-model) |

The Ontology is the **Statement of Applicability** for software engineering
governance: a matrix listing every constraint, whether it applies, how it is
enforced, and where the evidence lives.

### Core Design Decisions

These decisions were resolved through Q&A (2026-02-15):

| # | Decision | Resolution |
|---|----------|------------|
| 1 | Palantir alignment | Terminology + structure adopted. Object/Link/Action types, Language/Engine/Toolchain layers. GovZero-specific terms preserved. |
| 2 | AGENTS.md relationship | Partially generated. Constraints, Permissions, and Enforcement sections rendered from Ontology. Prose sections (Prime Directive, Workflow, Mission) hand-authored. |
| 3 | Portability | Build in airlineops, design for extraction. Airlineops is reference implementation; gzkit extracts generalizable patterns when mature. |
| 4 | ADR packaging | Two ADRs. ADR-A: Ontology schema + full population. ADR-B: Tool integration + generated artifacts. |
| 5 | Granularity | Maximum decision-space coverage. Register everything that constrains agent decisions. Severity as compliance-behavior signal. |
| 6 | Versioning | Stable IDs with semantic slugs (ruff-style). Parameters change, identity does not. IDs never reused. |
| 7 | Permissions | Action Types with authorization levels (autonomous / human-gated / prohibited). |
| 8 | Enforcement gaps | Explicit classification: automated / human-gated / gap. |
| 9 | File structure | Single file (ontology.json). Optimized for agent consumption. Human views are generated artifacts. |
| 10 | Scope | Central nervous system. All governance tools (ARB, chores, hooks, skills) link through the Ontology. |
| 11 | Two planes | Product rules (constrain code) + Process rules (constrain governance). Both in same Ontology. |
| 12 | Maintenance | Agent-authored, human-attested, machine-validated. Same pattern as product delivery. |
| 13 | Agent profiles | Agent-agnostic core + optional agent-specific guidance field per entry. |

---

## Two Planes in the Ontology

As established in the Motivation section, the Ontology governs both the
product and the factory. Both planes produce rules in the same model:

| Plane | Governs | Examples |
|-------|---------|---------|
| **Product** ("build the right thing") | How code is written | D-CONFIG-FIRST, R-SQL-PARAM-001 |
| **Process** ("build the thing right") | How governance tools behave | R-ADR-LIFECYCLE-001, R-OBPI-ATTESTATION-001 |

ADRs and OBPIs are **product delivery tools** --- jigs and CAD models for the
aircraft. The Ontology does not subsume them. It **governs how they function**:
how an ADR must be structured, what constitutes valid OBPI completion, what
evidence is sufficient for attestation.

Both planes reduce agent stochasticity. Product rules constrain *what* the
agent builds. Process rules constrain *how* the agent works.

---

## The Ontology as Central Nervous System

The Ontology is not a rules index that sits alongside other systems. It is
the hub through which all governance systems connect:

```text
                    +-------------+
          +-------->|  ONTOLOGY   |<--------+
          |         | (single     |         |
          |    +--->|  source of  |<---+    |
          |    |    |  truth)     |    |    |
          |    |    +------+------+    |    |
          |    |           |           |    |
         ARB  ADR/       Chores     Skills  Hooks
         (QA   OBPI      (serve     (enforce (block
         receipts (life-  ontology   ontology on
         trace  cycle     elements)  rules)  ontology
         back)  linked)                      rules)
```

Every existing system gains a **rationale** within the Ontology:

- A chore is not "maintenance task #14" --- it is "the remediation mechanism
  for rules R-SQL-PARAM-001 through R-SQL-PARAM-012."
- An ARB receipt is not a standalone QA artifact --- it is compliance evidence
  against specific Ontology rules.
- A skill is not a standalone workflow --- it serves specific Ontology
  elements (enforcement, remediation, or observation).
- The ADR/OBPI lifecycle tracks changes to the product, governed by process
  rules in the Ontology.

---

## Object Types

The Ontology contains four top-level object types.

### Doctrine (Object Type)

A high-level engineering principle that guides decision-making. Not directly
testable --- it is a direction, not a constraint.

**ID format:** `D-{SLUG}` (e.g., `D-CONFIG-FIRST`)

**Properties:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| title | string | yes | Human-readable name |
| description | string | yes | What this doctrine means and why it exists |
| origin_adr | string | no | ADR that established this doctrine |
| canonical_source | string | yes | File path of the authoritative statement |
| also_stated_in | array | no | Other files that restate this doctrine |
| category | string | yes | Classification (see categories below) |
| plane | enum | yes | `product` or `process` |

**Categories:** architecture, cli, configuration, data-access, data-modeling,
dependencies, documentation, portability, process, security, stability,
testing, tooling, versioning

### Policy (Object Type)

A codified interpretation of a doctrine scoped to a specific domain. Broader
than a single rule but testable at the policy level.

**ID format:** `P-{DOCTRINE-ABBREV}-{SLUG}` (e.g., `P-CFG-NO-ENV`)

**Properties:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| title | string | yes | Human-readable name |
| description | string | yes | What this policy requires |
| doctrine | string | yes | Parent doctrine ID |
| scope | string | yes | File paths or domains this policy applies to |
| canonical_source | string | yes | File path of the authoritative statement |

### Rule (Object Type)

An atomic constraint on agent or code behavior. Maximizes decision-space
coverage to minimize agent stochasticity.

**ID format:** `R-{POLICY-ABBREV}-{NNN}` (e.g., `R-CFG-NO-ENV-001`)

**Properties:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| title | string | yes | Human-readable name (semantic slug) |
| description | string | yes | Precise statement of the constraint |
| policy | string | yes | Parent policy ID |
| severity | enum | yes | `blocking`, `advisory`, `pattern`, `anti-pattern` |
| plane | enum | yes | `product` or `process` |
| enforcement | object | yes | Enforcement mechanisms (see Link Types) |
| observability | object | no | How to see compliance status |
| traceability | object | yes | Links to origin artifacts |
| remediation | object | no | How to fix violations |
| agent_guidance | object | no | Per-agent hints (see Agent Guidance) |

**Severity model (compliance-behavior signal):**

| Severity | Agent Behavior | Meaning |
|----------|---------------|---------|
| `blocking` | Must comply; enforcement will catch violations | Hard constraint |
| `advisory` | Should comply; no automated enforcement yet | Soft constraint (enforcement gap) |
| `pattern` | Preferred approach when multiple options exist | Decision-space narrower |
| `anti-pattern` | Explicitly prohibited; do not consider | Decision-space exclusion |

### Action Type (Object Type)

An operation with an authorization boundary. Models permissions as first-class
Ontology entries, mapping to Palantir's Action concept.

**ID format:** `A-{SLUG}` (e.g., `A-GIT-PUSH`)

**Properties:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| title | string | yes | Human-readable name |
| description | string | yes | What this action does |
| authorization | enum | yes | `autonomous`, `human-gated`, `prohibited` |
| scope | string | no | Where this action applies |
| rules_enforced | array | no | Rule IDs this action helps enforce |
| agent_guidance | object | no | Per-agent hints |

**Authorization model:**

| Level | Meaning | Example |
|-------|---------|---------|
| `autonomous` | Agent may perform without asking | Run unit tests, read files, lint |
| `human-gated` | Agent must get explicit approval first | git push, uv add, file deletion |
| `prohibited` | Agent must never perform | git commit --no-verify, raw SQL for attestation |

---

## Link Types

Named relationships between Ontology objects, adopted from Palantir's Link
Type concept. Links are stored as properties on the objects they connect
(not as separate entities).

| Link Type | From | To | Meaning |
|-----------|------|----|---------|
| `enforces` | Hook / Policy Test | Rule | Catches violations of this rule |
| `remediates` | Chore | Rule | Fixes violations of this rule |
| `evidences` | ARB Receipt / Proof | Rule | Proves compliance with this rule |
| `implements` | ADR / OBPI | Doctrine / Policy | Introduced or modified this element |
| `observes` | Insight / Log | Rule | Observation about this rule's compliance |
| `authorizes` | Action Type | Agent Profile | Authorization level for this agent |
| `serves` | Skill | Rule / Action | Helps enforce or execute this element |
| `derives_from` | Policy | Doctrine | This policy codifies this doctrine |
| `constrains` | Rule | Policy | This rule is an atomic test of this policy |

Links are represented in the Ontology as foreign key references in object
properties (e.g., a rule's `policy` field is a `constrains` link, a rule's
`enforcement.policy_tests` array contains `enforces` links from tests).

---

## Agent Guidance

Rules and actions may include optional per-agent guidance. The core Ontology
is agent-agnostic; guidance helps each agent find *its* specific compliance
path.

```json
{
  "agent_guidance": {
    "claude_code": "Enforce via chore-config-paths-remediation skill",
    "copilot": "Instruction file: cli.instructions.md section Config-First",
    "codex": "Policy test covers this; run uv run -m unittest tests.policy"
  }
}
```

Agent guidance is optional and non-authoritative. The rule itself is the
authority; guidance is a convenience for reducing agent lookup time. When
gzkit extracts the schema for other repos, agent guidance fields are
portable (new repos fill in their own agent hints).

---

## Three-Layer Architecture

Following Palantir's operationalization model:

### Language Layer (Schema)

The Ontology schema defines the semantic model: object types, properties,
link types, ID conventions, severity model. This is the generalizable layer
that gzkit will eventually extract.

**Artifacts:**
- `.gzkit/governance/ontology.schema.json` --- JSON Schema definition
- This design document --- human-readable specification

### Engine Layer (gzkit)

The tools that read, write, query, and validate the Ontology. gzkit is the
engine that operates against the Language layer.

**Capabilities:**
- Query: "What rules apply to `src/airlineops/warehouse/`?"
- Validate: "Do all referenced hooks, tests, chores, and skills exist?"
- Gap analysis: "Which rules have severity=blocking but enforcement coverage=gap?"
- Compliance trace: "This session touched files in scope of rules X, Y, Z"

### Toolchain Layer (Control Surfaces)

The control surfaces where governance touches the agent: skills, hooks,
instruction files, CLAUDE.md, AGENTS.md. These are the delivery mechanisms
that bring Ontology constraints into agent context.

**Control surface types:**

| Surface | Delivery Mechanism | Agent |
|---------|-------------------|-------|
| `.github/instructions/*.md` | Auto-injected by GitHub | Copilot |
| `CLAUDE.md` / `AGENTS.md` | Read at session start | All agents |
| `.claude/skills/` | Invoked during workflow | Claude Code |
| `.agents/skills/` | Invoked during workflow | All agents |
| `.pre-commit-config.yaml` | Triggered on commit | All agents |
| `config/opsdev/chores.json` | Invoked on demand | All agents |

---

## Enforcement Coverage Model

Each rule declares its enforcement coverage using an explicit classification:

| Coverage | Meaning | Example |
|----------|---------|---------|
| `automated` | Machine enforcement exists and is active | Policy test, pre-commit hook |
| `human-gated` | Deliberately requires human judgment (by design) | Gate 5 attestation, PR review |
| `gap` | No enforcement exists; this is a debt | Rule documented but not yet tested |

This three-way classification enables precise gap analysis:

- **Actionable gaps:** Rules where `coverage: "gap"` --- enforcement is
  missing and should be built
- **Intentional human gates:** Rules where `coverage: "human-gated"` ---
  no automated enforcement needed by design
- **Fully covered:** Rules where `coverage: "automated"` --- machine
  enforcement is active

---

## ID Conventions

IDs are **stable semantic slugs** following the ruff/ty model:

| Object Type | Prefix | Format | Example |
|-------------|--------|--------|---------|
| Doctrine | `D-` | `D-{SLUG}` | `D-CONFIG-FIRST` |
| Policy | `P-` | `P-{ABBREV}-{SLUG}` | `P-CFG-NO-ENV` |
| Rule | `R-` | `R-{ABBREV}-{NNN}` | `R-CFG-NO-ENV-001` |
| Action | `A-` | `A-{SLUG}` | `A-GIT-PUSH` |

**Rules:**

- Slugs are UPPERCASE, HYPHEN-SEPARATED, human-readable
- Numbers are zero-padded to three digits within a policy
- IDs are permanent --- once assigned, never reused, never renamed
- Parameters may change (e.g., coverage threshold 40% to 50%) but the ID
  and its semantic meaning are stable
- Deprecated rules are marked `deprecated: true`, never deleted
- Git history tracks all parameter changes

---

## Proposed Location

```text
.gzkit/
  governance/
    ontology.json           # The populated GovZero Ontology (single file)
    ontology.schema.json    # JSON Schema for validation
```

**Rationale:** Per the `.gzkit/` directory structure (ADR-0.0.25), governance
metadata belongs in `.gzkit/`, not `.github/` (GitHub-specific) or `config/`
(runtime application config). The Ontology is governance metadata:
git-tracked, machine-readable, consumed by agents and tools.

Single file optimized for agent consumption. Human-readable views (governance
guides, compliance dashboards, rule summaries) are generated artifacts
produced by Engine layer tools.

---

## Maintenance Model

The Ontology is maintained using the same governance pattern it defines:

| Phase | Who | What |
|-------|-----|------|
| Discovery | Agent scans codebase | Identifies candidate rules, enforcement, gaps |
| Drafting | Agent proposes entries | Writes entries with IDs, links, metadata |
| Attestation | Human reviews | Approves, adjusts, or rejects proposed entries |
| Validation | Machine checks | Hook/chore verifies references exist, no orphans |
| Evolution | Agent updates per ADR/OBPI | New rules are part of the deliverable |

When a new ADR introduces a constraint, the corresponding Ontology entry is
part of the ADR's deliverables --- not an afterthought.

---

## Doctrines Inventory

Preliminary enumeration of doctrines currently embedded in governance prose:

| ID | Title | Origin | Category | Plane |
|----|-------|--------|----------|-------|
| D-CONFIG-FIRST | Config-First | ADR-0.1.0 | configuration | product |
| D-SUBSYSTEM-ISOLATION | Subsystem Isolation | ADR-0.0.3 | architecture | product |
| D-STDLIB-FIRST | Stdlib-First | Convention | dependencies | product |
| D-CROSS-PLATFORM | Cross-Platform | ADR-0.0.1 | portability | product |
| D-FLAG-DEFECTS | Flag Defects Never Excuse | ADR-0.0.27 | process | process |
| D-DOCS-AS-DELIVERABLE | Documentation-as-Deliverable | GovZero charter | documentation | process |
| D-LITE-BY-DEFAULT | Lite-by-Default | GovZero charter | process | process |
| D-DB-ISOLATION | DB Isolation | Convention | testing | product |
| D-PYDANTIC-MODELS | Pydantic Data Models | Convention | data-modeling | product |
| D-CLIG-CLI | clig.dev CLI Design | Convention | cli | product |
| D-SQL-HYGIENE | SQL Hygiene | Convention | data-access | product |
| D-OBPI-DISCIPLINE | One Brief Per Item | GovZero charter | process | process |
| D-OWNER-COMPLETION | Complete Ownership | GovZero charter | process | process |
| D-GATE-ATTESTATION | Human Gate Attestation | GovZero charter | process | process |
| D-APPEND-ONLY-LEDGERS | Append-Only Governance Ledgers | ADR-0.0.25 | tooling | process |
| D-LAYERED-TRUST | Layered Trust Architecture | ADR-0.0.21 | tooling | process |
| D-SESSION-CONTINUITY | Session Handoff Continuity | ADR-0.0.25 | process | process |
| D-NO-SECRETS | No Secrets in Code | Convention | security | product |
| D-FROZEN-INTERFACES | Frozen Interface Protection | Convention | stability | product |
| D-SEMVER-ADR | SemVer ADR Discipline | Convention | versioning | process |

This inventory is preliminary. Full population is ADR-A scope.

---

## ADR Packaging

### ADR-A: GovZero Ontology (Schema + Population)

**Scope:** Define the Ontology schema and fully populate it with all
doctrines, policies, rules, and actions for both product and process planes.

**Deliverables:**

- Ontology schema (JSON Schema for validation)
- Populated ontology.json (single file, all entries)
- ID conventions and naming rules
- Registration protocol (when you create a rule, add it here)
- Doctrine, policy, rule, and action type definitions
- Link type definitions
- Severity model and enforcement coverage model

### ADR-B: Tool Integration + Generated Artifacts

**Scope:** Wire existing governance tools through the Ontology and produce
generated artifacts.

**Deliverables:**

- Skills, hooks, and chores reference Ontology entry IDs
- AGENTS.md partial generation (Constraints, Permissions, Enforcement
  sections rendered from Ontology)
- Pre-commit hook validates Ontology integrity (referenced artifacts exist)
- Generated human-readable governance guide
- Compliance trace tooling (per-session rule coverage)
- discovery-index.json migration to `.gzkit/governance/`

---

## Impact Analysis

### For Agents

| Before | After |
|--------|-------|
| Read ~10 docs (~2,500 lines prose) | Read ontology.json (structured, filterable) |
| Hope you remembered all constraints | Query rules by category, scope, severity, plane |
| Get caught by unknown hooks | Know enforcement status before starting |
| Improvise at unconstrained decision points | Decision space maximally covered |
| No compliance trace | Generate per-session compliance trace |

### For gzkit

| Before | After |
|--------|-------|
| Tools hardcode knowledge of rules | Tools query Ontology by ID |
| Each tool discovers its own context | Tools share a common governance model |
| Chores are standalone tasks | Chores serve specific Ontology elements |
| Gap analysis requires manual audit | Gap analysis is an Ontology query |

### For Human Operators

| Before | After |
|--------|-------|
| Read scattered prose | Read generated governance guide |
| Trust that enforcement exists | See enforcement coverage map |
| Manual audit of compliance | Dashboard from Ontology data |
| Ad hoc rule creation | Registration protocol with required fields |

---

## Relationship to Existing Artifacts

| Existing Artifact | Relationship to Ontology |
|-------------------|------------------------|
| `discovery-index.json` | Structural navigation; Ontology handles governance semantics. Future (ADR-B): migrate to `.gzkit/governance/`. |
| `AGENTS.md` | Universal agent entry point. Constraints/Permissions/Enforcement sections become generated from Ontology (ADR-B). Prose sections remain hand-authored. |
| `CLAUDE.md` | Project orientation; links to Ontology for full constraint set. |
| `.github/instructions/*.md` | Domain-specific prose; canonical source for policies. Ontology indexes them, does not replace them. |
| `config/opsdev/chores.json` | Chore registry. Each chore gains rationale via Ontology rule IDs it remediates (ADR-B). |
| `.pre-commit-config.yaml` | Hook definitions. Each hook linked to Ontology rule IDs it enforces (ADR-B). |
| `tests/policy/*.py` | Policy tests. Test docstrings gain `@covers` references to Ontology rule IDs (ADR-B). |
| `docs/governance/GovZero/*.md` | Governance process docs. Remain authoritative for process descriptions. Ontology indexes rules derived from them. |
| `.gzkit/insights/agent-insights.jsonl` | Raw observations. Ontology provides structured context for categorizing insights by rule. |
| ARB receipts | QA validation artifacts. Trace back to Ontology rules as compliance evidence (ADR-B). |

---

## References

- [Palantir Ontology](https://www.palantir.com/docs/foundry/architecture-center/ontology-system/) ---
  Inspiration for terminology and structure
- [GovZero Charter](charter.md) --- Gate definitions and authority
- [Layered Trust Architecture](layered-trust.md) --- Tool layer model
- [Architectural Enforcement](architectural-enforcement.md) --- Enforcement patterns
- [.gzkit/ Directory Structure](gzkit-structure.md) --- Storage conventions
- [Unified Ledger Schema](ledger-schema.md) --- JSONL field definitions
- [ADR Lifecycle](adr-lifecycle.md) --- Status values and transitions
