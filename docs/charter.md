# The gzkit Charter

Status: Active
Version: 1.0
Authority: Canon (sole authority for covenant definitions)

This document defines the **Development Covenant**—the binding agreement between human and agent for how work gets done.

---

## The Covenant

A development covenant is an explicit, binding agreement that:

1. **Preserves intent** across context boundaries
2. **Provides constraints** agents can reason against
3. **Creates verification loops** both parties trust
4. **Reserves judgment** for humans

This is not governance in the compliance sense. It is cognitive infrastructure for productive partnership.

---

## Authority Boundary

| Role | Authority |
|------|-----------|
| **Human** | Originates intent; defines constraints; attests completion |
| **Agent** | Interprets intent; operates within constraints; generates evidence |
| **Verification** | Mutual—tests, checks, and audits that both parties trust |

Human attestation is the closeout gate. Agents cannot attest on behalf of humans.

---

## Five Gates

All work flows through gates. Gates are verification checkpoints, not bureaucratic hurdles.

### Gate 1: ADR (Intent)

**Purpose:** Record intent and tradeoffs before implementation.

**Artifact:** ADR document with problem statement, decision, and consequences.

**Applies to:** All work (Lite and Heavy lanes).

---

### Gate 2: TDD (Tests)

**Purpose:** Verify implementation correctness through automated tests.

**Artifact:** Passing tests with reasonable coverage.

**Applies to:** All work (Lite and Heavy lanes).

---

### Gate 3: Docs (Documentation)

**Purpose:** Ensure documentation accurately describes behavior.

**Artifact:** Documentation that builds, links resolve, content matches code.

**Applies to:** Heavy lane only.

---

### Gate 4: BDD (Behavior)

**Purpose:** Verify external contract behavior through acceptance tests.

**Artifact:** Passing acceptance scenarios for CLI/API/schema contracts.

**Applies to:** Heavy lane only.

---

### Gate 5: Human (Attestation)

**Purpose:** Human directly observes artifacts and attests to completion.

**Artifact:** Explicit human attestation with timestamp.

**Applies to:** Heavy lane only.

**Authority:** Human attestation is the sole authority for completion. Agents present artifacts; humans observe and attest.

---

## Lane Doctrine

| Lane | Gates | Trigger |
|------|-------|---------|
| **Lite** | 1, 2 | Internal changes (no external contract changes) |
| **Heavy** | 1, 2, 3, 4, 5 | External contract changes (CLI, API, schema) |

Default lane is Lite. Escalate to Heavy when external contracts change.

---

## Attestation Terms

Human attestation uses one of these exact forms:

| Term | Meaning |
|------|---------|
| **Completed** | Work finished; all claims verified |
| **Completed — Partial: [reason]** | Subset accepted; remainder deferred |
| **Dropped — [reason]** | Work rejected; rationale provided |

These terms are canonical. Other terms are not valid for closeout.

---

## The Three Concerns

The covenant spans three concerns:

### Specification (Agent-Native)

What invariants must hold. Explicit constraints, declarative intent, acceptance criteria.

Agents ground against specification. It should be:
- Constraint-forward (NEVER/ALWAYS rules)
- Testable (verifiable claims)
- Immutable once accepted (canon)

### Methodology (Shared)

How work flows through phases. Gates, checkpoints, verification loops.

Methodology provides structure. It should be:
- Sequential where dependencies exist
- Parallel where independent
- Observable (status is always knowable)

### Governance (Human-Native)

Who has authority to decide. Attestation, audit, closeout.

Governance reserves judgment. It should be:
- Explicit (written down)
- Human-final (Gate 5)
- Auditable (evidence trail)

---

## Principles

1. **Governance is verification, not celebration** — Gates produce evidence, not theater
2. **Silence is non-compliance** — Unstated assumptions are invalid
3. **Artifacts survive sessions** — Intent must persist across context boundaries
4. **Constraints are first-class** — Agents need explicit boundaries
5. **Human attestation is final** — No automation bypasses Gate 5

---

## References

- [README](../README.md) — Project overview
- [Lineage](lineage.md) — Heritage from spec-kit and GovZero
- [Concepts](concepts/) — Deep dives on the three concerns
