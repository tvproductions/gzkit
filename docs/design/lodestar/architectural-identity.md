# Architectural Identity

## Schema-Driven Everything

This is gzkit's primary architectural principle. It is not one invariant
among many — it is the invariant that enables all others.

**Every artifact, every event, every configuration, every rendered surface
is schema-defined and schema-validated.** JSON Schema defines the shape.
Pydantic enforces it at runtime. No config is unvalidated. No event is
untyped. No content type drifts from its schema.

This is not optional. This is not aspirational. This is the reason gzkit
exists.

LLMs are loose and lazy. They hallucinate structure. They invent fields.
They silently drop required properties. They produce output that *looks*
right but violates invariants in ways that compound over time. Left
unconstrained, they create drift — and drift in governance is silent
corruption of the system's ability to assure correctness.

gzkit exists to constrain them. Every `gz` command validates against schema
before writing. Every ledger event is schema-checked before append. Every
rendered surface is generated from canonical, schema-validated content —
never hand-edited, never vibes-authored.

**No drift. No vibes. Schema or nothing.**

---

## gzkit Is a Headless CMS for Governance

gzkit is a **content management system**. Its content types are governance
artifacts — ADRs, OBPIs, rules, skills, attestations, constitutions, PRDs.
Its storage is a JSONL ledger and structured files. Its rendering targets
are the agent harnesses that consume governance: Claude Code, GitHub Copilot,
OpenAI Codex, Gemini CLI, OpenCode, and any future vendor.

This is not a metaphor. gzkit satisfies every property of a headless CMS:

| CMS Concept | gzkit Realization |
|-------------|-------------------|
| Content types | ADRs, OBPIs, rules, skills, attestations, PRDs, constitutions |
| Content schema | JSON Schema (file shape) + Pydantic (runtime validation) |
| Content lifecycle | Pool → Draft → Active → Attested → Closed |
| Event store | `.gzkit/ledger.jsonl` (append-only JSONL, or DB) |
| Content API | `gz state`, `gz status`, `gz validate` (read); `gz plan`, `gz attest` (write) |
| Template engine | `gz agent sync control-surfaces` |
| Rendered outputs | `.claude/`, `.github/`, `.agents/`, `GEMINI.md`, `opencode.json` |
| Admin interface | `gz status --table`, `gz state --json` |
| Configuration | `.gzkit/manifest.json` (Pydantic-validated) |

---

## Three Domains, One System

gzkit is not a CMS for design artifacts that hands off to something else
for implementation. It manages the **full lifecycle** across three domains
that most systems treat as separate concerns:

### Domain 1: Design & Intent

What you intend to build, why, and under what constraints.

| Content type | Purpose | Key commands |
|-------------|---------|-------------|
| PRD | Strategic intent, bound to a Major version | `gz prd` |
| Constitution | North star, values, non-negotiable principles | `gz constitute` |
| ADR | Architectural decision with tradeoffs and alternatives | `gz plan` |
| OBPI | Scoped work unit with acceptance criteria | `gz specify` |
| Rules | Constraints, coding standards, path-scoped policies | `gz agent sync` |
| Skills | Reusable agent workflows and ceremonies | `gz agent sync` |

### Domain 2: Implementation & Outcomes

What was actually built, how it behaves, and what evidence exists.

| Content type | Purpose | Key commands |
|-------------|---------|-------------|
| REQ | Named requirement with test linkage | `gz implement` |
| TASK | Execution step, commit-traceable | ledger events |
| Gate evidence | Test results, coverage, doc builds, BDD runs | `gz gates`, `gz implement` |
| Commit traces | Git commits referencing governing artifact IDs | hooks |
| Ledger events | Every state transition, every command, every gate check | implicit writes |

### Domain 3: Reconciliation & Audit

Whether what was built matches what was intended, attested by a human.

| Content type | Purpose | Key commands |
|-------------|---------|-------------|
| Closeout form | Ceremony workspace — evidence paths, human observation | `gz closeout` |
| Attestation | Human judgment: Completed, Partial, or Dropped | `gz attest` |
| Audit artifact | Post-attestation reconciliation of intent vs. outcome | `gz audit` |
| Reconciliation | Ledger-vs-artifact drift detection | `gz validate`, `gz adr audit-check` |
| Receipts | Scoped evidence payloads for completed events | `gz adr emit-receipt` |

### The Ledger Unifies All Three

The ledger is not a log for one domain. It is the **single event store**
across all three. An `adr_created` event (Domain 1), a `gate_checked` event
(Domain 2), and an `attested` event (Domain 3) are all entries in the same
append-only stream. `gz state` replays the full stream to derive current
state across all three domains simultaneously.

This is what makes gzkit a **systems-mature** CMS rather than a design tool
with validation bolted on. The three domains are not phases that hand off to
each other — they are concurrent views of the same content lifecycle, unified
by the ledger and enforced by schema.

```
┌─────────────────────────────────────────────────────────┐
│                    .gzkit/ledger.jsonl                   │
│              (single event store, all domains)          │
└────────┬──────────────────┬──────────────────┬──────────┘
         │                  │                  │
    ┌────▼────┐       ┌─────▼─────┐      ┌────▼────┐
    │ Design  │       │ Implement │      │  Audit  │
    │ & Intent│       │ & Outcome │      │ & Recon │
    │         │       │           │      │         │
    │ PRD     │       │ REQ       │      │ Closeout│
    │ ADR     │──────►│ TASK      │─────►│ Attest  │
    │ OBPI    │       │ Gate Evid │      │ Audit   │
    │ Rules   │       │ Commits   │      │ Receipt │
    │ Skills  │       │ Ledger    │      │ Recon   │
    └─────────┘       └───────────┘      └─────────┘
```

---

## The Canon Invariant

**Canon always resides in `.gzkit/`.** No exceptions.

Vendor directories (`.claude/`, `.github/`, `.agents/`, `.opencode/`) contain
only **generated mirrors** — rendered templates produced by `gz agent sync
control-surfaces`. They are never edited directly, never treated as
authoritative, and never the source of truth for any governance artifact.

This holds even for the primary harness. Claude Code is gzkit's primary
consumer, but `.claude/rules/` is a generated mirror of `.gzkit/rules/`,
just as `.claude/skills/` is a generated mirror of `.gzkit/skills/`.

The rule is absolute: **you never hand-edit a rendered template.**

---

## Selective Vendor Enablement

Not every repository needs every vendor. `.gzkit/manifest.json` declares
which vendors are enabled. `gz agent sync control-surfaces` generates
mirrors **only** for enabled vendors.

A repository that uses only Claude gets `.claude/` surfaces and nothing else.
A repository that uses Claude and Copilot gets both. Disabled vendors produce
no artifacts, no mirrors, no overhead.

The vendor enablement model:

```
.gzkit/manifest.json
  └── vendors:
        claude:   enabled → .claude/rules/, .claude/skills/, CLAUDE.md
        copilot:  enabled → .github/instructions/, .github/skills/
        codex:    disabled → (nothing generated)
        gemini:   disabled → (nothing generated)
        opencode: disabled → (nothing generated)
```

---

## The Django Parallel

The architectural parallel to Django is structural, not cosmetic:

| Django | gzkit |
|--------|-------|
| Models (ORM) | Pydantic models + JSON Schema |
| Database | JSONL ledger / SQLite |
| Migrations | `gz agent sync`, `gz migrate-semver` |
| Templates → HTML | `.gzkit/rules/` → `.claude/rules/`, `.github/instructions/` |
| `manage.py migrate` | `gz agent sync control-surfaces` |
| `manage.py check` | `gz validate` |
| `settings.py` | `.gzkit/manifest.json` |
| Admin site | `gz status`, `gz state` |
| Middleware | Claude hooks, Copilot hooks, OpenCode plugins |

Django's contract: **models define truth; templates render views; you never
edit rendered HTML.** gzkit's contract is identical: **`.gzkit/` defines
truth; `gz agent sync` renders views; you never edit vendor surfaces.**

---

## Content Types and Their Shapes

Every governance artifact is a content type with:

1. **Schema** — JSON Schema defines the file shape; Pydantic validates at
   runtime. No unvalidated config.
2. **Lifecycle** — Each content type progresses through defined states.
   The ledger records every state transition.
3. **Rendered output** — `gz agent sync` transforms canonical content into
   vendor-specific shapes. Different vendors need different frontmatter,
   different directory conventions, different file names.

### Rules as Content

Rules (constraints, instructions, coding standards) are content:

```
.gzkit/rules/
  tests.md           ← canonical content (vendor-neutral)
  pythonic.md         ← canonical content
  governance-core.md  ← canonical content

gz agent sync control-surfaces generates:

.claude/rules/
  tests.md            ← rendered with `paths: ["tests/**"]` frontmatter
  pythonic.md          ← rendered with `paths: ["**/*.py"]` frontmatter

.github/instructions/
  tests.instructions.md    ← rendered with `applyTo: "tests/**"` frontmatter
  pythonic.instructions.md ← rendered with `applyTo: "**/*.py"` frontmatter
```

Same content, different shape. The canonical definition in `.gzkit/rules/`
carries the vendor-neutral metadata (path scope, content). The sync engine
transforms metadata into each vendor's native format.

### Skills as Content

Skills already follow this pattern:

```
.gzkit/skills/gz-check/SKILL.md     ← canonical
.claude/skills/gz-check/SKILL.md    ← mirror (Claude format)
.github/skills/gz-check/SKILL.md    ← mirror (Copilot format)
.agents/skills/gz-check/SKILL.md    ← mirror (Codex format)
```

---

## Lineage: BEADS and the Event-Sourced Ledger

gzkit's content management architecture descends directly from Steve Yegge's
**BEADS** (Build, Explain, Analyze, Debug, Search). BEADS introduced the
pattern of an append-only JSONL ledger as the single source of truth for
project state, with current state derived from event replay rather than
mutable records.

gzkit extends BEADS in three directions:

1. **Schema-enforced content types.** BEADS events are loosely typed. gzkit
   events are schema-validated (JSON Schema for shape, Pydantic for runtime).
   Every event type has a defined schema version, required fields, and
   validation rules. The ledger is not just append-only — it is
   append-only-and-validated.

2. **Multi-head rendering.** BEADS produces state for a single consumer
   (the developer). gzkit produces rendered governance surfaces for multiple
   consumers (Claude, Copilot, Codex, Gemini, OpenCode), each with different
   format requirements. The same canonical content yields different rendered
   shapes depending on the target harness.

3. **Governance lifecycle.** BEADS tracks build/debug events. gzkit tracks
   a governance lifecycle — intent, decomposition, implementation, verification,
   attestation, audit — where each transition is an event, each state has
   invariants, and the final transition (attestation) requires human action
   that cannot be automated.

The BEADS heritage is visible in gzkit's core operations:

| BEADS Pattern | gzkit Realization |
|---------------|-------------------|
| Append-only JSONL | `.gzkit/ledger.jsonl` |
| State from replay | `gz state` derives current state from ledger events |
| Dependency graph | `parent`, `blocks`, `blocked_by` fields in events |
| Queryable state | `gz state --json`, `gz state --blocked`, `gz state --ready` |
| Implicit writes | All `gz` commands append events; no explicit ledger calls |

BEADS proved that an append-only event log is sufficient for project state.
gzkit proves that the same pattern scales to governance — where the content
types are richer, the lifecycle is longer, the consumers are multiple, and
the final authority is always human.

---

## The Governance Decomposition Hierarchy

gzkit's content types are not flat. They form a five-level decomposition
hierarchy, from strategic intent down to executable work:

```
PRD           Strategic intent. Bound to a Major version.
 └── ADR      Architectural decision. Tradeoffs, constraints, alternatives.
      └── OBPI    Scoped work unit. One Brief Per Item. Acceptance criteria + evidence.
           └── REQ     Named requirement. Test-linked. Behavioral proof.
                └── TASK    Execution step. Bite-sized. Anti-rationalization defended.
```

Each level is a content type with its own schema, lifecycle, and ledger
events. Every level is both **ledger-traceable** (events record creation,
state transitions, evidence) and **git-commit-traceable** (commits reference
the governing artifact ID).

This hierarchy is gzkit's content model. It is the equivalent of a CMS
taxonomy — but instead of categories and tags, it decomposes intent into
progressively smaller, evidence-bearing units until the work is small enough
to execute and verify.

The hierarchy also defines the boundary between gzkit and its complementary
systems. gzkit governs all five levels. Execution methodology (how an agent
actually writes code, runs tests, debugs) is delegated to behavioral systems
like **superpowers**, which operates at the TASK level — providing TDD
discipline, systematic debugging, anti-rationalization, and verification
workflows. gzkit does not replicate those capabilities. It provides the
governance infrastructure (ledger events, evidence requirements, gate
enforcement) that makes the behavioral methodology accountable.

| Level | gzkit provides | Behavioral system provides |
|-------|---------------|---------------------------|
| PRD | Schema, lifecycle, ledger events | — |
| ADR | Schema, lifecycle, gate enforcement | — |
| OBPI | Schema, acceptance criteria, evidence linking | Execution planning (plan structure) |
| REQ | Test linkage, spec-triangle traceability | — |
| TASK | Ledger tracing, commit tracing | TDD, debugging, verification, anti-rationalization |

---

## The Orchestrator Role

gzkit is an **orchestrator/publisher**. It does not compete with the agent
harnesses it serves. It does not replicate their capabilities. It provides
the governance content those harnesses need, in the shapes they expect,
validated against schemas they cannot violate.

The agent harnesses are consumers. They read the rendered surfaces, follow
the rules, invoke the skills, and report through the hooks. gzkit manages
the content lifecycle — creation, validation, attestation, audit — and
publishes the results.

This separation is gzkit's architectural identity. It is what makes
multi-harness governance possible without maintaining five independent
governance systems.

---

## Invariants

These properties are non-negotiable:

| ID | Invariant |
|----|-----------|
| AI-000 | **Everything is schema-driven.** JSON Schema defines shape; Pydantic enforces at runtime. No unvalidated config. No untyped events. No vibes. |
| AI-001 | Canon resides in `.gzkit/`, never in vendor directories |
| AI-002 | Vendor surfaces are generated mirrors, never edited directly |
| AI-003 | All config is enforced by JSON Schema + Pydantic — no exceptions, no "we'll validate later" |
| AI-004 | Vendor enablement is selective, declared in manifest |
| AI-005 | `gz agent sync` is the sole publisher of vendor surfaces |
| AI-006 | Content types have schema, lifecycle, and rendered output |
| AI-007 | The ledger (JSONL or DB) is the event store for all state transitions |
| AI-008 | gzkit is the orchestrator; agent harnesses are consumers |
| AI-009 | gzkit manages the full lifecycle: design, implementation, and audit are one system, not three |
| AI-010 | The ledger is the single event store across all three domains |
| AI-011 | LLMs are loose; gzkit is strict. Schema enforcement is the boundary between the two. |

---

## Lineage and Relationships

### Ancestral Systems

| System | Contribution to gzkit |
|--------|----------------------|
| **BEADS** (Yegge) | Append-only JSONL ledger, state-from-replay, dependency tracking, implicit writes |
| **Django** | Models-define-truth, templates-render-views, migrations, schema enforcement |
| **Headless CMS** (pattern) | Content types, lifecycle states, multi-head rendering, API-first |
| **Superpowers** (obra) | Behavioral methodology at execution level; complementary, not competitive |
| **GSD** (glittercowboy) | Persistent context across sessions, STATE.md pattern |
| **Spec-kit** (GitHub) | Phase model: constitute → specify → plan → implement → analyze |

### Relationship to Other Lodestar Documents

| Document | Defines | This document adds |
|----------|---------|-------------------|
| GovZero Doctrine | WHY — SPRINT/DRIFT, human sovereignty | WHAT — the system's architectural identity |
| Foundational ADR Pattern | HOW — governance is structured | WHAT — the content management model |
| Project Structure | WHERE — files live | WHY — vendor surfaces are generated, not authored |
