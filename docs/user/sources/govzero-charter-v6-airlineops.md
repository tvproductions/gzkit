# GovZero Charter v6

Status: Active
Last reviewed: 2026-01-08
Authority: Canon (sole authority for gate definitions)

This document is the **sole authority** for GovZero gate definitions and semantics.
All other documents MUST reference gates by number only and defer here for meaning.

---

## Authority Boundary

| Role | Authority |
|------|-----------|
| **Human** | Attests to ADR closeout; provides explicit attestation |
| **Agent** | Assists with implementation, testing, documentation; presents artifacts |
| **Audit** | Runs post-attestation to reconcile artifacts; does not grant authority |

Human attestation is the closeout gate. Agents cannot attest on behalf of humans.
Audit is a reconciliation mechanism, not an authority mechanism.

---

## Gate Definitions

### Gate 1: ADR (Intent)

**Purpose:** Record intent and tradeoffs before implementation.

**Artifact:** ADR document with problem statement, decision, and consequences.

**Applies to:** All work (Lite and Heavy lanes).

---

### Gate 2: TDD (Tests)

**Purpose:** Verify implementation correctness through automated tests.

**Artifact:** Passing unit tests with coverage floor (≥40%).

**Applies to:** All work (Lite and Heavy lanes).

---

### Gate 3: Docs (Documentation)

**Purpose:** Ensure documentation accurately describes code behavior.

**Artifact:** Clean markdown lint, mkdocs build passes, links/anchors valid.

**Applies to:** Heavy lane only.

---

### Gate 4: BDD (Behavior)

**Purpose:** Verify external contract behavior through acceptance tests.

**Artifact:** Passing Behave scenarios for CLI/API/schema contracts.

**Applies to:** Heavy lane only.

---

### Gate 5: Human Attestation

**Purpose:** Human directly observes artifacts and attests to ADR completion.

**Artifact:** Explicit human attestation recorded with timestamp.

**Applies to:** Heavy lane only (required for ADR closeout).

**Authority:** Human attestation is the sole authority for ADR closeout.
Agents present artifacts; humans observe and attest. Audit runs post-attestation.

---

## Lane Doctrine

| Lane | Gates | Trigger |
|------|-------|---------|
| **Lite** | 1, 2 | Internal changes only (no external contract changes) |
| **Heavy** | 1, 2, 3, 4, 5 | External contract changes (CLI, API, schema, error messages) |

Default lane is Lite. Escalate to Heavy only when external contracts change.

---

## Closeout Attestation Terms

Human attestation MUST use one of these exact forms:

| Term | Meaning |
|------|---------|
| **Completed** | ADR work finished; all claims verified |
| **Completed — Partial: [reason]** | Subset accepted; remainder deferred with rationale |
| **Dropped — [reason]** | ADR rejected; clear rationale provided |

These terms are canonical. Other terms (accept, approve, sign off) are not valid for closeout.

---

## References

- ADR lifecycle and status mapping: [govzero-adr-lifecycle-airlineops.md](govzero-adr-lifecycle-airlineops.md)
- ADR status table: Upstream ADR status table (see the [sources index](README.md))
- Closeout ceremony behavior: Upstream audit protocol (see the [sources index](README.md))
- ADR/OBPI/GHI/audit linkage: Upstream linkage doc (see the [sources index](README.md))
- Agent contract: [/AGENTS.md](/AGENTS.md)
- Machine-readable governance: [/config/governance_manifest.json](/config/governance_manifest.json)
