# OBPIs

OBPI means One Brief Per Item.

Canonical GovZero source: [`docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md`](../../governance/GovZero/adr-obpi-ghi-audit-linkage.md).

---

## Purpose

OBPI is the operational unit of completion in gzkit.

Each OBPI is also a bounded transaction. Scope is defined up front, verified by
changed-files audit, and blocked when work escapes the declared allowlist.

Each OBPI represents one ADR checklist value increment and should include:

1. Work execution on scoped paths
2. Proof of value (tests/verification)
3. Human-usable documentation updates
4. Narrative justification and evidence

Before implementation begins, authored briefs should pass:

- `uv run gz obpi validate <path-to-brief> --authored`
- `uv run gz obpi validate --adr ADR-<X.Y.Z> --authored`

This keeps parity with GovZero skill discipline: pre-orientation, tool use, post-accounting, validation, verification, and presentation.

ADR lifecycle state should be treated as a roll-up of OBPI increments, not a substitute for OBPI-level execution evidence.

---

## Completion Signals

An OBPI is operationally complete when:

- Brief status is `Completed`
- Implementation summary evidence is substantive (not placeholder)
- Key proof is substantive and machine-readable in receipt/runtime state
- Linked runtime/doc changes are verifiable

Runtime surfaces now derive OBPI state from both ledger evidence and brief content.
`runtime_state` stays fail-closed when completion proof is missing, placeholder, or
out of sync with the brief.
Execution-boundary rules such as allowlists, spine-touch serialization, and
parallel-safe blocking live in the
[OBPI Transaction Contract](../../governance/GovZero/obpi-transaction-contract.md).
The full machine-readable contract is defined in
[`docs/governance/GovZero/obpi-runtime-contract.md`](../../governance/GovZero/obpi-runtime-contract.md).

Use the OBPI-native runtime surfaces to inspect that state directly:

- `uv run gz obpi status OBPI-...`
- `uv run gz obpi validate path/to/OBPI-...md`
- `uv run gz obpi reconcile OBPI-...`

For parser-safe evidence detection, keep `### Implementation Summary` as inline
`- key: value` bullets (for example, `- Date completed: 2026-02-23`) rather than
splitting values onto nested bullet lines.
When a defect is filed during the OBPI, record it in a dedicated
`## Tracked Defects` section using `- GHI-123 (open|closed): summary` bullets so
status and closeout surfaces can preserve defect-level traceability offline.

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

## Transaction Boundaries

Every OBPI brief should be readable as an execution contract:

- brief and ADR context are loaded before implementation begins
- authored validation should pass before pipeline entry
- `Allowed Paths` are the only paths that may be changed.
- `Denied Paths` make non-goals explicit.
- when a plan-audit receipt exists, it must be read as part of transaction
  context
- `git diff --name-only` is the minimum changed-files audit before completion.
- `gz obpi validate` is the fail-closed pre-completion gate for allowlist,
  evidence, and git-sync readiness.
- Spine-touch work is serialized.
- Parallel OBPI work is valid only when allowlists are disjoint and no shared
  blocker exists.
- Until lock parity exists, shared-scope or spine-touch work stays single-OBPI.

If any of those conditions fail, the correct outcome is `BLOCKERS`, not "close
enough."

Compatibility gaps do not weaken the contract. They must be called out
explicitly and handled fail-closed.

---

## OBPI Receipt Practice

When recording OBPI completion before ADR completion, emit an OBPI-native receipt:

- `uv run gz obpi emit-receipt OBPI-... --event completed|validated ...`

This records accountability at OBPI scope without claiming the parent ADR is done.
Completed receipts also persist `req_proof_inputs`, which are later consumed by
`gz obpi status`, `gz obpi reconcile`, and ADR lifecycle surfaces.
The same runtime issues now block `gz closeout` until every linked OBPI is ready
for ADR-level closeout.
`gz adr emit-receipt` remains available for ADR-level accounting and legacy scoped payloads.
Each normalized proof-input item uses the stable contract shape:
`name`, `kind`, `source`, `status`, with optional `scope` and `gap_reason`.

---

## Related

- [Lifecycle](lifecycle.md)
- [Workflow](workflow.md)
- [OBPI Transaction Contract](../../governance/GovZero/obpi-transaction-contract.md)
- [OBPI Runtime Contract](../../governance/GovZero/obpi-runtime-contract.md)
- [gz obpi status](../commands/obpi-status.md)
- [gz obpi reconcile](../commands/obpi-reconcile.md)
- [gz adr audit-check](../commands/adr-audit-check.md)
- [gz obpi emit-receipt](../commands/obpi-emit-receipt.md)
- [gz adr emit-receipt](../commands/adr-emit-receipt.md)
