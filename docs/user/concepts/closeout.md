# Closeout Ceremony

Closeout is a mode where the agent presents evidence paths and commands, and the human observes and decides.

Canonical GovZero source: [`docs/governance/GovZero/audit-protocol.md`](../../governance/GovZero/audit-protocol.md).

---

## Sequence

1. **Orientation**
   - Confirm target ADR and OBPI scope.
   - Confirm lane obligations.
2. **Presentation** (`gz closeout`)
   - Agent provides Gate 1 path plus verification commands.
   - Output is commands/paths only, no interpreted outcomes.
3. **Human Observation**
   - Human runs commands and inspects artifacts directly.
4. **Attestation** (`gz attest`)
   - Human records `completed`, `partial`, or `dropped`.
   - `gz attest` enforces prerequisite gates by default.
5. **Post-attestation Audit** (`gz audit`)
   - Reconciliation only; blocked before attestation.
6. **Receipts/Accounting** (`gz adr emit-receipt`)
   - Record completed/validated receipts, including OBPI-scoped evidence when appropriate.

---

## Heavy Lane Gate 4 Handling

For heavy lane ADRs:

- If `features/` exists, closeout includes the Gate 4 BDD command.
- If `features/` is absent, closeout and status surfaces report Gate 4 as N/A with explicit rationale.

---

## Canonical Attestation Choices

- `Completed`
- `Completed — Partial: [reason]`
- `Dropped — [reason]`

---

## Related

- [Lifecycle](lifecycle.md)
- [Gates](gates.md)
- [gz closeout](../commands/closeout.md)
- [gz attest](../commands/attest.md)
- [gz audit](../commands/audit.md)
