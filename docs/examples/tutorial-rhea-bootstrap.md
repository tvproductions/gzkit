# Tutorial: Bootstrapping RHEA with GZKit

## The Greenfield Litmus Test

---

## Context

**RHEA** (Repository Harness for Entity Abstraction) is a small Python
library implementing the Repository pattern with adapter-driven persistence
and a predicate DSL. It currently exists as a single README with a clear
design vision and zero code.

**This tutorial documents how to bootstrap RHEA from empty scaffold to
first attested ADR using gzkit.** It serves two purposes:

1. **Proof of concept** — Validate that gzkit can govern a greenfield
   library project (not just its own CLI)
2. **Reference for students** — Show the governance workflow on a real
   project that isn't gzkit itself

---

## Before You Start

**RHEA's current state:**

```text
rhea/
├── .git/
└── README.md       ← Design vision document (150+ lines)
```

No source code. No tests. No config. No governance. This is as greenfield
as it gets.

**What you need:**

```bash
# gzkit installed
uv tool install gzkit

# Python 3.13+
python --version

# In the RHEA directory
cd /path/to/rhea
```

---

## Phase 1: Initialize Governance

### Step 1.1: Bootstrap gzkit

| Skill (preferred) | CLI equivalent |
|---|---|
| `/gz-init` | `gz init --mode lite` |

```bash
gz init --mode lite
```

**Expected result:**

```text
rhea/
├── .gzkit/
│   ├── ledger.jsonl
│   ├── manifest.json
│   └── skills/
├── .gzkit.json
├── docs/design/
│   ├── prd/
│   ├── constitutions/
│   └── adr/
├── AGENTS.md
├── CLAUDE.md
└── README.md           ← Unchanged
```

**Why Lite mode?** RHEA is a library with no CLI, no external API, and no
user-facing documentation yet. Lite lane (Gates 1-2: ADR + TDD) is
appropriate until RHEA has a public surface worth governing with Heavy gates.

### Step 1.2: Create the PRD

The README already articulates RHEA's vision. Translate it into a PRD:

| Skill (preferred) | CLI equivalent |
|---|---|
| `/gz-prd` | `gz prd RHEA-1.0.0 --title "Repository Harness for Entity Abstraction"` |

The `/gz-prd` skill runs a guided interview before generating the PRD.

```bash
gz prd RHEA-1.0.0 --title "Repository Harness for Entity Abstraction"
```

Open `docs/design/prd/PRD-RHEA-1.0.0.md` and fill it in from the README:

```markdown
---
id: PRD-RHEA-1.0.0
status: Draft
semver: 1.0.0
date: 2026-03-08
---

# PRD-RHEA-1.0.0: Repository Harness for Entity Abstraction

## Problem Statement

Python projects that need to read records from different persistence
backends (in-memory, SQLite, DuckDB) end up either coupling directly to
a specific backend or adopting a full ORM with write-side complexity they
don't need. There is no lightweight, read-first repository abstraction
with semantic parity guarantees across adapters.

## North Star

A developer can swap from an in-memory adapter to SQLite to DuckDB and
get identical query results, with the swap requiring zero changes to
business logic.

## Invariants

- Read-only by design (no Unit of Work, no change tracking)
- Adapter parity is a testable contract, not a hope
- No speculative generalization — add capabilities when needed
- RHEA never imports domain-specific code (AirlineOps, etc.)
- Pydantic 2.x for all models

## Gate Mapping

| Gate | Lane | Requirement |
|------|------|-------------|
| Gate 1 (ADR) | All | All changes have ADRs |
| Gate 2 (TDD) | All | Tests pass, coverage ≥40% |
| Gate 3 (Docs) | Heavy | Documentation updated |
| Gate 4 (BDD) | Heavy | Behavior tests pass |
| Gate 5 (Human) | Heavy | Human attestation recorded |

## Q&A Transcript

Q: Why read-only? Most repositories support writes.
A: RHEA focuses on the read side because reads don't require change
   tracking, commit orchestration, or lifecycle management. Write support
   may be added later under its own ADR with explicit governance.

Q: Why Pydantic instead of plain dataclasses?
A: Pydantic provides validation at the boundary, serialization, and a
   mature ecosystem. Dataclasses would require writing custom validation.

Q: What is "adapter parity" concretely?
A: Given the same data and the same predicate, every adapter must return
   identical results. This is enforced by parameterized tests that run
   the same test suite against every adapter.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 1.0.0 | Pending | | | |
```

---

## Phase 2: First ADR — Core Contract

### Step 2.1: Plan the ADR

RHEA's first feature is the core `ReadRepo[T]` interface and predicate DSL.

| Skill (preferred) | CLI equivalent |
|---|---|
| `/gz-plan` | `gz plan create 0.1.0 --title "Core ReadRepo interface and predicate DSL" --lane lite` |

The `/gz-plan` skill runs 20+ design forcing-function questions before
generating the ADR.

```bash
gz plan create 0.1.0 --title "Core ReadRepo interface and predicate DSL" --lane lite
```

Fill in the ADR:

```markdown
---
id: ADR-0.1.0
status: Draft
semver: 0.1.0
lane: lite
parent: PRD-RHEA-1.0.0
date: 2026-03-08
---

# ADR-0.1.0: Core ReadRepo Interface and Predicate DSL

## Intent

RHEA needs a core interface that all adapters will implement. This ADR
establishes the ReadRepo[T] protocol and the predicate DSL (Eq, Gt, Lt,
In_, And, Or) that consumers use to express queries without knowing
which backend is active.

## Decision

1. Define ReadRepo[T] as a Python Protocol with methods: get, list, filter
2. Implement a predicate DSL with value objects: Eq, Gt, Lt, Gte, Lte, In_
3. Support compound predicates with And and Or combinators
4. Make predicates backend-agnostic — adapters translate them
5. Use Pydantic BaseModel for all entity types (the T in ReadRepo[T])
6. Implement an InMemoryAdapter as the reference implementation

## Consequences

### Positive

- Protocol-based interface allows any adapter without inheritance
- Predicate DSL decouples query expression from query execution
- InMemoryAdapter provides instant test feedback (no I/O)
- Pydantic constraint means all entities are validated at creation

### Negative

- Protocol approach requires Python 3.8+ (runtime_checkable)
- Predicate DSL is less expressive than raw SQL
- InMemoryAdapter won't surface I/O-related bugs

## Decomposition Scorecard

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Data state | 0 | No persistent storage in this ADR |
| Logic | 2 | Predicate DSL parsing + evaluation |
| Interface | 1 | ReadRepo protocol definition |
| Observability | 0 | Not needed |
| Lineage | 0 | No upstream/downstream |
| **Total** | **3** | **3 tasks** |

## Checklist

1. [ ] ReadRepo[T] protocol with get, list, filter methods
2. [ ] Predicate DSL: Eq, Gt, Lt, Gte, Lte, In_, And, Or
3. [ ] InMemoryAdapter implementing ReadRepo[T]

## Alternatives Considered

- **ABC instead of Protocol** — Requires inheritance, which couples
  adapters to a base class. Protocol is more Pythonic and flexible.
- **Raw lambdas for filtering** — Simpler but not serializable, not
  introspectable, and not translatable to SQL.
- **SQLAlchemy Core expressions** — Powerful but ties the DSL to SQL
  concepts. RHEA's predicates must work against in-memory data too.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.1.0 | Pending | | | |
```

### Step 2.2: Create task briefs

| Skill (preferred) | CLI equivalent |
|---|---|
| `/gz-obpi-specify` | `gz specify <slug> --parent ADR-0.1.0 --item N --lane lite` |

```bash
gz specify "ReadRepo protocol" --parent ADR-0.1.0 --item 1 --lane lite
gz specify "Predicate DSL" --parent ADR-0.1.0 --item 2 --lane lite
gz specify "InMemory adapter" --parent ADR-0.1.0 --item 3 --lane lite
```

### Step 2.3: Implement

This is where the real work happens. For each task:

1. Read the brief's requirements and acceptance criteria
2. Write the code
3. Write the tests
4. Verify: `uv run -m unittest discover tests`
5. Update the brief status

**Suggested implementation order** (following dependency chain):

```text
Task 2 (Predicate DSL)    ← no dependencies, pure value objects
Task 1 (ReadRepo protocol) ← uses predicates in filter signature
Task 3 (InMemory adapter)  ← implements ReadRepo, evaluates predicates
```

**Skeleton for Task 2 — Predicate DSL:**

```python
# src/rhea/predicates.py
"""Predicate DSL for backend-agnostic queries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(frozen=True)
class Eq:
    """Field equals value."""
    field: str
    value: Any


@dataclass(frozen=True)
class Gt:
    """Field greater than value."""
    field: str
    value: Any


@dataclass(frozen=True)
class In_:
    """Field value is in a set."""
    field: str
    values: Sequence[Any]


@dataclass(frozen=True)
class And:
    """All predicates must match."""
    predicates: Sequence[Eq | Gt | In_ | And | Or]


@dataclass(frozen=True)
class Or:
    """At least one predicate must match."""
    predicates: Sequence[Eq | Gt | In_ | And | Or]


# Type alias for any predicate
Predicate = Eq | Gt | In_ | And | Or
```

> Note: Predicates use `@dataclass(frozen=True)` instead of Pydantic
> because they are internal value objects, not boundary models. The
> ADR's Pydantic constraint applies to *entities* (the T in ReadRepo[T]),
> not to the query infrastructure.

---

## Phase 3: Verify and Attest

### Step 3.1: Run gates

| Skill (preferred) | CLI equivalent |
|---|---|
| `/gz-gates ADR-0.1.0` | `gz gates --adr ADR-0.1.0` |

```bash
gz gates --adr ADR-0.1.0
```

Both Gate 1 (ADR exists) and Gate 2 (tests pass) must be green.

### Step 3.2: Closeout

| Skill (preferred) | CLI equivalent |
|---|---|
| `/gz-adr-closeout-ceremony ADR-0.1.0` | `gz closeout ADR-0.1.0` |

The `/gz-adr-closeout-ceremony` skill runs the full walkthrough protocol
and rejects vague acknowledgment.

```bash
gz closeout ADR-0.1.0
```

Review the verification output. Run the listed commands.

### Step 3.3: Attest

```bash
gz attest ADR-0.1.0 --status completed
```

---

## Phase 4: What Next?

After the core contract is attested, RHEA's roadmap from the README
suggests:

| ADR | Feature | Lane |
|-----|---------|------|
| 0.2.0 | SQLite adapter | Lite |
| 0.3.0 | Adapter parity test harness | Lite |
| 0.4.0 | Public API and documentation | Heavy |
| 0.5.0 | DuckDB/Parquet adapter | Lite |

Each follows the same cycle. In a Claude Code session, prefer the skills:

```text
/gz-plan → /gz-obpi-specify → /gz-obpi-pipeline → /gz-gates → /gz-adr-closeout-ceremony → gz attest
```

CLI equivalent: `gz plan → gz specify → implement → gz gates → gz closeout → gz attest`.

---

## What This Tutorial Proves

If RHEA can be bootstrapped and governed through its first ADR cycle with
gzkit, it demonstrates that:

1. **gzkit works for greenfield projects** — not just self-governance
2. **gzkit works for libraries** — not just CLI tools
3. **Lite lane is sufficient for internal work** — Heavy gates can be
   adopted when RHEA has a public surface
4. **The governance overhead is proportional** — 3 task briefs for 3
   deliverables; no ceremony for ceremony's sake

These are the exact properties needed for student adoption. A student's
course project is a greenfield library or app, governed in Lite lane,
with Heavy gates introduced only when they present their work.

---

## Friction Points to Watch

When running this tutorial for real, note any friction:

| Potential Issue | What to Record |
|----------------|----------------|
| `gz init` fails or creates wrong structure | Exact error, OS, Python version |
| `gz specify` doesn't parse checklist items | ADR format mismatch with parser expectations |
| `gz gates` doesn't find tests | Path configuration in `.gzkit.json` |
| Ledger events have wrong IDs | ID generation logic edge cases |
| Template sections feel irrelevant for a library | Which sections to strip for library mode |

File these as issues on the gzkit repo. They are the **go-live blockers**
for student adoption.

---

## Related

- [First Project Tutorial](tutorial-first-project.md) — Simpler walkthrough
  with a reading list app
- [GZKit Readiness Assessment](gzkit-readiness-assessment.md) — Full
  evaluation of student readiness
- [Glossary](glossary.md) — Governance terms defined
