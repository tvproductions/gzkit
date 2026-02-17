# OBPIs

OBPI means One Brief Per Item.

Canonical GovZero source: [`docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md`](../../governance/GovZero/adr-obpi-ghi-audit-linkage.md).

---

## Purpose

OBPI is the operational unit of completion in gzkit.

Each OBPI represents one ADR checklist value increment and should include:

1. Work execution on scoped paths
2. Proof of value (tests/verification)
3. Human-usable documentation updates
4. Narrative justification and evidence

This keeps parity with GovZero skill discipline: pre-orientation, tool use, post-accounting, validation, verification, and presentation.

ADR lifecycle state should be treated as a roll-up of OBPI increments, not a substitute for OBPI-level execution evidence.

---

## Completion Signals

An OBPI is operationally complete when:

- Brief status is `Completed`
- Implementation summary evidence is substantive (not placeholder)
- Linked runtime/doc changes are verifiable

`gz adr audit-check` validates these conditions per linked ADR.

---

## OBPI Receipt Practice

When recording OBPI completion before ADR completion, use ADR receipt events with explicit evidence scope:

- `scope: "OBPI-..."`
- `adr_completion: "not_completed"`
- `obpi_completion: "attested_completed"`

This records accountability without claiming the parent ADR is done.

---

## Related

- [Lifecycle](lifecycle.md)
- [Workflow](workflow.md)
- [gz adr audit-check](../commands/adr-audit-check.md)
- [gz adr emit-receipt](../commands/adr-emit-receipt.md)
