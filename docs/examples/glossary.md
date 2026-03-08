# Glossary of Governance Terms

## CIDM 6330/6395 — Quick Reference

---

## Core Concepts

### ADR (Architecture Decision Record)

A document that captures a single design decision: what was decided, why,
what alternatives were considered, and what the consequences are. ADRs are
the "lab notebook" of software architecture — they preserve reasoning so
future developers (including future-you) understand why the system is built
the way it is.

**Example:** "We chose SQLite over PostgreSQL because the project is a
single-user CLI tool that doesn't need concurrent write support."

### Attestation

A formal human declaration that work is complete and correct. In gzkit,
attestation means a human has observed the evidence (test output, running
software, documentation) and explicitly signed off. This is Gate 5 — the
gate that AI agents cannot pass by themselves.

**Terms:**

- **Completed** — All work finished; all claims verified
- **Completed — Partial** — Some work deferred with documented reason
- **Dropped** — Decision reversed; documented why

### Closeout

The ceremony where completed work is presented for review before
attestation. The presenter runs verification commands, shows output, and
explains what was built. The reviewer then decides whether to attest.

In a classroom: the closeout is your demo. The attestation is the
instructor saying "approved."

### Constitution

A document defining immutable project principles — constraints that every
piece of code must satisfy regardless of which feature is being built.
Examples: "All tests must pass before merge," "No network calls in unit
tests," "Python 3.13+ only."

Constitutions don't change sprint-to-sprint. They are the project's laws.

### Gate

A quality checkpoint that must pass before work can be considered complete.
GZKit defines five gates:

| Gate | Name | What It Checks |
|------|------|----------------|
| 1 | ADR | Design decision is recorded before implementation |
| 2 | TDD | Unit tests pass with adequate coverage |
| 3 | Docs | Documentation is updated and builds cleanly |
| 4 | BDD | Behavior tests prove external contracts work |
| 5 | Human | A human has reviewed and attested the work |

Not all gates apply to all work — see **Lane**.

### Lane

The governance weight applied to a piece of work. Lanes determine which
gates are required.

| Lane | Required Gates | When to Use |
|------|---------------|-------------|
| **Lite** | 1 (ADR) + 2 (TDD) | Internal changes — new functions, refactoring, bug fixes |
| **Heavy** | 1 + 2 + 3 + 4 + 5 | External changes — new CLI commands, API endpoints, schema changes |

**Rule of thumb:** If a user would notice the change, it's Heavy. If only
developers would notice, it's Lite.

### Ledger

An append-only JSONL file (`.gzkit/ledger.jsonl`) that records every
governance event: project init, PRD creation, ADR creation, gate checks,
attestations. The ledger is the source of truth — status is derived from
ledger events, not from editing file headers.

**Append-only** means events can never be deleted or modified. This creates
a tamper-evident audit trail.

### OBPI (One Brief Per Item)

The atomic unit of work in gzkit. Each ADR has a feature checklist, and
each checklist item gets exactly one OBPI brief. The brief scopes the work:
what files to touch, what constraints to follow, what acceptance criteria
to meet.

In the student workflow, OBPIs are equivalent to **tasks**. The name is
different but the principle is identical: one deliverable, one brief, clear
definition of done.

### PRD (Product Requirements Document)

A document that defines what the product must do and why, from the user's
perspective. The PRD answers "what problem are we solving?" and "how will
we know it's solved?" without prescribing how to build it.

The PRD is the starting point of the governance chain:
`PRD → ADR → OBPI/Task → Code → Gates → Attestation`

---

## Workflow Terms

### Alignment Chain

The governance principle that intent, code, and documentation must agree:

```text
Intent (PRD/ADR) ↔ Code (behavior) ↔ Docs (claims)
```

If any link breaks — code doesn't match the ADR, or docs don't match the
code — the work isn't done. Gates verify this chain holds.

### Decomposition

The practice of breaking a large feature into small, independent,
testable tasks. Good decomposition produces tasks that are each completable
in one focused session (2-8 hours) and independently verifiable.

### Decomposition Scorecard

A scoring tool for estimating how many tasks an ADR needs. Five dimensions
are scored 0-2:

| Dimension | 0 | 1 | 2 |
|-----------|---|---|---|
| Data state | No new storage | Simple schema | Complex schema/migration |
| Logic | Trivial | Moderate algorithm | Complex multi-step |
| Interface | No user surface | One command/endpoint | Multiple surfaces |
| Observability | None needed | Logging | Metrics + alerting |
| Lineage | No dependencies | One upstream/downstream | Multiple |

Total score suggests task count: score of 3 → 3-4 tasks.

### Dogfooding

Using your own tool to build itself. GZKit governs its own development
with gzkit — every feature is tracked by an ADR, decomposed into OBPIs,
and attested by a human. This proves the governance model works in practice,
not just in theory.

### Zero Doctrine

GZKit's core philosophy: the human is "index zero" — first in priority,
final in authority. AI agents are powerful tools, but the human must remain
the architect. The doctrine has two sides:

1. Gates constrain agents — they can't skip checkpoints
2. Humans must engage — read everything, question everything

Without both sides, governance fails silently.

---

## File and Format Terms

### Frontmatter

YAML metadata at the top of a markdown file, delimited by `---`:

```yaml
---
id: ADR-0.1.0
status: Draft
lane: lite
date: 2026-03-08
---
```

Frontmatter is machine-readable — tools parse it to determine status,
relationships, and lifecycle state.

### JSONL (JSON Lines)

A file format where each line is a valid JSON object. Used for the ledger
because it supports append-only writes without parsing the entire file:

```json
{"event":"project_init","id":"my-project","ts":"2026-03-08T14:00:00Z"}
{"event":"adr_created","id":"ADR-0.1.0","ts":"2026-03-08T14:05:00Z"}
```

### Manifest

A JSON file (`.gzkit/manifest.json`) that defines the project's governance
schema: what artifact types exist, where they live, what gates apply, and
what verification commands to run. The manifest is the machine-readable
version of your governance contract.

### Skill

A reusable governance procedure defined as a markdown file. Skills describe
*how* to perform a specific governance action (create an ADR, run an audit,
perform closeout). GZKit ships with 40+ skills that AI agents can follow
as structured workflows.

---

## Status Values

### ADR Lifecycle

```text
Pool → Draft → Proposed → Accepted → Completed → Validated
```

| Status | Meaning |
|--------|---------|
| **Pool** | Idea captured; not yet designed |
| **Draft** | Being written; not ready for review |
| **Proposed** | Ready for review and discussion |
| **Accepted** | Approved; implementation can begin |
| **Completed** | All tasks done and gates passed |
| **Validated** | Post-attestation audit confirmed |
| **Superseded** | Replaced by a newer ADR |
| **Abandoned** | Decision reversed; reason documented |

### Task (OBPI) Status

| Status | Meaning |
|--------|---------|
| **Draft** | Brief created; work not started |
| **In Progress** | Actively being implemented |
| **Completed** | All acceptance criteria met; gates pass |
| **Dropped** | Removed from scope with documented reason |

---

## Related

- [First Project Tutorial](tutorial-first-project.md) — See these terms in
  action
- [PRD Guide](guide-prd.md) | [ADR Guide](guide-adr.md) |
  [Task Guide](guide-tasks.md)
