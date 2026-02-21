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

## Acceptance Protocol

OBPI closure follows a ceremony, not just a checklist:

1. Present a value narrative (problem before, capability now)
2. Present one key proof example (CLI/code/behavior)
3. Present verification evidence (tests, commands, outputs)
4. Wait for explicit human acceptance
5. Only then set `Brief Status: Completed`

Lane inheritance applies:

- Parent ADR lane `Heavy` or Foundation (`0.0.x`) requires human attestation before OBPI completion.
- Parent ADR lane `Lite` may be self-closeable after evidence is presented.

Reference: `AGENTS.md` section `OBPI Acceptance Protocol`.

---

## OBPI Receipt Practice

When recording OBPI completion before ADR completion, emit an OBPI-native receipt:

- `uv run gz obpi emit-receipt OBPI-... --event completed|validated ...`

This records accountability at OBPI scope without claiming the parent ADR is done.
`gz adr emit-receipt` remains available for ADR-level accounting and legacy scoped payloads.

---

## Related

- [Lifecycle](lifecycle.md)
- [Workflow](workflow.md)
- [gz adr audit-check](../commands/adr-audit-check.md)
- [gz obpi emit-receipt](../commands/obpi-emit-receipt.md)
- [gz adr emit-receipt](../commands/adr-emit-receipt.md)
