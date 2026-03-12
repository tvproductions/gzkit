# Closeout Ceremony

Closeout is a mode where the agent presents evidence paths and commands, and the human observes and decides.

Canonical GovZero source: [`docs/governance/GovZero/audit-protocol.md`](../../governance/GovZero/audit-protocol.md).

---

## Sequence

1. **Orientation**
   - Confirm target ADR and OBPI scope.
   - Confirm lane obligations.
2. **Presentation** (`gz closeout`)
   - Agent provides Gate 1 path, OBPI completion summary, and verification commands.
   - Linked OBPI proof is reconciled first. If any OBPI is not closeout-ready, closeout prints
     `BLOCKERS:` plus follow-up commands and stops before recording `closeout_initiated`.
3. **Human Observation**
   - Human runs commands and inspects artifacts directly after closeout is unblocked.
4. **Attestation** (`gz attest`)
   - Human records `completed`, `partial`, or `dropped`.
   - `gz attest` enforces prerequisite gates by default.
5. **Post-attestation Audit** (`gz audit`)
   - Reconciliation only; blocked before attestation.
6. **Receipts/Accounting** (`gz adr emit-receipt`)
   - Record ADR-level completed/validated receipts after attestation.
   - OBPI completion accounting belongs in the OBPI pipeline before ADR closeout, after guarded `git sync`.

---

## Heavy Lane Gate 4 Handling

For heavy lane ADRs:

- Closeout includes the Gate 4 BDD command.
- Closeout remains blocked until linked heavy-lane OBPIs satisfy their attestation-proof rules.
- Gate 4 must pass before attestation.

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
