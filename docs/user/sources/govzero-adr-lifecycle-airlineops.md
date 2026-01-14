# ADR Lifecycle and Status Mapping

Status: Draft
Last reviewed: 2026-01-11
Authority: Canon (defines ADR lifecycle states and closeout-to-status mapping)

This document canonizes ADR lifecycle states and their relationship to Gate 5 closeout attestation.
For gate definitions, see [GovZero Charter v6](govzero-charter-v6-airlineops.md). For closeout ceremony behavior, see the upstream audit protocol referenced in the [sources index](README.md).

---

## ADR Lifecycle States

An ADR progresses through these states:

| State | Meaning | Transition Trigger |
|-------|---------|-------------------|
| **Draft** | ADR being authored; not yet ready for review | Author creates ADR file |
| **Proposed** | ADR submitted for review; awaiting acceptance | Author declares ready for review |
| **Accepted** | ADR approved; implementation work may begin | Human accepts the proposal |
| **Completed** | Implementation finished; Gate 5 attestation received | Human attests "Completed" or "Completed — Partial" |
| **Superseded** | Replaced by a newer ADR | New ADR explicitly supersedes this one |
| **Abandoned** | Work stopped; ADR will not be completed | Human attests "Dropped" or declares abandonment |

### Lifecycle Diagram

```text
Draft → Proposed → Accepted → [implementation] → Closeout Ceremony → Completed
                                                                   → Abandoned (if Dropped)
                                                 ↓
                                            Superseded (if replaced by new ADR)
```

---

## Closeout Attestation to Status Mapping

When a human provides Gate 5 attestation, the ADR status updates as follows:

| Closeout Attestation | ADR Status | Notes |
|---------------------|------------|-------|
| **Completed** | Completed | All claims verified; work finished |
| **Completed — Partial: [reason]** | Completed | Deferrals documented in ADR Consequences section; follow-on ADRs created for deferred scope |
| **Dropped — [reason]** | Abandoned | Rationale recorded; ADR does not count toward roadmap |

---

## State Transition Rules

1. **Draft → Proposed**: Author determines ADR is ready for review
2. **Proposed → Accepted**: Human reviews and accepts the proposal for implementation
3. **Accepted → Completed**: Human provides "Completed" or "Completed — Partial" attestation via closeout ceremony
4. **Accepted → Abandoned**: Human provides "Dropped" attestation or explicitly abandons work
5. **Any → Superseded**: A new ADR explicitly declares it supersedes this one (add `Superseded-By: ADR-X.Y.Z` to metadata)

---

## Deprecated Terms

The following terms have been used historically but are **not canonical**:

| Term | Disposition |
|------|-------------|
| Deprecated | Use "Superseded" with rationale, or "Abandoned" if no replacement |
| Pending | Use "Proposed" or "Accepted" depending on approval state |
| Retired | Use "Superseded" with backlink to replacement |

---

## ADR Status Table

The authoritative ADR status table lives upstream in GovZero (see the [sources index](README.md)).

That table MUST use only the lifecycle states defined in this document.
Status values in that table are derived from this canon; if conflict exists, this document governs.

---

## References

- Gate definitions: [GovZero Charter v6](govzero-charter-v6-airlineops.md)
- Closeout ceremony: Upstream audit protocol (see the [sources index](README.md))
- Disposition rubric: Upstream ADR disposition rubric (see the [sources index](README.md))
- ADR status table: Upstream ADR status table (see the [sources index](README.md))
