# ADR closeout

You are here when every OBPI of an ADR is complete and the ADR itself is ready to
be witnessed.

## Steps

1. **`gz-adr-sync`** — discover `@covers` evidence, reconcile OBPI ledger state
   and register the ADR files.
2. **`gz-adr-status`** — confirm every OBPI shows complete and nothing blocks
   closeout.
3. **`gz-adr-closeout-ceremony`** — `uv run gz closeout <ADR-ID> --ceremony`
   walks the operator through the evidence and the ADR's fidelity assertions,
   then records the attestation and runs the closeout pipeline.
4. **`gz-adr-audit`** — the Gate 5 audit: verify the evidence and move the ADR
   from Completed to Validated.
5. **`gz-adr-emit-receipt`** — record a completed, validated or closed receipt
   event with its evidence, where the flow calls for one.

## Branches

- **An OBPI is still open** → back to [OBPI delivery](obpi-delivery.md).
- **The ADR changed a CLI, API, schema or runtime contract** (heavy lane) —
  docs (Gate 3) and BDD (Gate 4) must pass before the attestation.
- **A defect in accepted work surfaces here** → [Defects and GHIs](defects-and-ghis.md).

## Only you can

Attest the ADR. The ceremony presents; you witness and rule.

## Then

[Release](release.md).
