# gz handoff authorize

**Deprecated alias for [`gz handoff decide`](handoff-decide.md).** Behaves
identically, including every flag; read that page for the full contract.

---

## Why the rename

The gate books an **acknowledge-and-decide transit**, not a completion
attestation. ADR-0.0.33 § Alternatives rejects that conflation by name —
*"completion-attestation is sacrosanct and reserved for claims about completed
planned work ... conflating them would spend and cheapen the sacred word"* — yet
the verb was called `authorize` and the ledger event's own docstring claimed
*"the same relay model as Gate 5 attestation"*. The vocabulary was borrowing a
register it had no business spending (GHI #757).

`authorize` was also a **consent boolean**: booking it *was* authorization, so an
operator who reviewed the handoff and ruled *not yet* left no record at all.
`decide` carries a decision token, and only `proceed` lifts the gate.

## Why the alias survives

`gz handoff authorize` is named across skills, runbooks, the resume gate's own
block prose, and every handoff in the corpus. Both verbs register through one
shared flag builder, so the alias cannot drift from the verb it aliases, and
both are permitted by the resume gate's read allowlist — a gate that blocked
its own recovery under one of its two spellings would be worse than the hole it
plugs.

Prefer `gz handoff decide` in new work.

---

## Exit codes

Identical to [`gz handoff decide`](handoff-decide.md#exit-codes).
