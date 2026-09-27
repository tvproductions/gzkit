# Traceability

You are here to find out what relates to what: which OBPIs an ADR has, what an
artifact produced, what depends on a node.

## Steps

- **The artifact graph** → **`gz-state`**: relationships, attestation and
  readiness, read from the ledger.
- **One ADR** → **`gz-adr-status`**: lifecycle and OBPI detail.
- **One OBPI's completion** → `uv run gz obpi status <OBPI-ID>`.
- **An ADR to the files it produced** → **`gz-adr-map`**.
- **The governance shape, a node's lineage or blast radius** →
  **`gz-ontology`**, the read-only sonar.
- **Everything about one ADR, as one document** → `uv run gz context <ADR-ID>`.

## Branches

- **These are views.** Completion is a ledger fact; cite the ledger, not a
  derived table.

## Only you can

Nothing; these are read-only.

## Then

Back to the flow that raised the question.
