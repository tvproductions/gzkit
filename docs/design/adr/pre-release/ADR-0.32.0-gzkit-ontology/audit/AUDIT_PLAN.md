# AUDIT PLAN (Gate-5) — ADR-0.32.0

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.32.0-gzkit-ontology |
| ADR Title | gzkit ontology (object/link plane) |
| SemVer | 0.32.0 |
| ADR Dir | docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology |
| Audit Date | 2026-07-07 |
| Auditor(s) | g0 (operator, attesting) · pipeline-orchestrator (driver) · spec-reviewer + quality-reviewer (independent) |

## Purpose

Confirm ADR-0.32.0 implementation is complete by validating its claims with
reproducible CLI evidence and moving it COMPLETED → VALIDATED. The ADR builds
the object/link plane of the gzkit ontology: ONE typed networkx MultiDiGraph,
three domain subgraphs (corpus / work / source), queried by `gz ontology`
verbs, held Tier-B (derived-never-authority).

**Audit Trigger:** Post-closeout Gate-5 validation (all 7 OBPIs
`attested_completed`, ADR `Completed`, gates 1–5 pass).

## Scope & Inputs

**Primary contract surfaces (introduced/modified by this ADR):**

- `uv run gz ontology sense` — structural-shape sweep + labeled seams
- `uv run gz ontology trace <id>` — vertical lineage + lateral proof + edge provenance
- `uv run gz ontology sense --json` — machine-readable shape + rebuild-fidelity self-report
- `uv run gz validate --ontology-purity` — Harness-Purity fence (product objects barred from `ownership:harness`)
- Pydantic model surface: `OntologyNode` / `OntologyEdge` / typed `LinkType`, JSON schema under `src/gzkit/schemas/`

**Governance/health surfaces:**

- `uv run gz adr audit-check ADR-0.32.0` (Layer-2 ledger proof)
- `uv run gz adr fidelity ADR-0.32.0` (bound Fidelity Gate — the ADR's thesis run live)
- `uv run gz cli audit` (command-doc coverage)

## Planned Checks

| Check | Command / Method | Expected Signal | Status (Planned) |
|-------|------------------|-----------------|------------------|
| Ledger completeness (L2) | `uv run gz adr audit-check ADR-0.32.0` | PASS, all 7 OBPIs completed w/ evidence | Pending |
| Fidelity Gate (bound) | `uv run gz adr fidelity ADR-0.32.0` | 4 pass, 0 fail | Pending |
| Sonar images shape | `uv run gz ontology sense` | Exit 0, structural table | Pending |
| Vertical + lateral trace | `uv run gz ontology trace ADR-0.32.0-gzkit-ontology` | Exit 0, ancestors + descendants + provenance | Pending |
| Harness-Purity fence | `uv run gz validate --ontology-purity` | Exit 0 clean; fails closed (exit 3) on breach | Pending |
| Rebuild-fidelity self-report | `uv run gz ontology sense --json` | `fidelity.complete=true`, `unaccounted_event_types=[]` | Pending |
| CLI doc coverage | `uv run gz cli audit` | All commands covered | Pending |

## Risk Focus

Per the ADR's own pre-mortem, risk concentrates on **Boundary Invariant #1
(rebuild fidelity)** — the load-bearing fence. A wrong graph is more dangerous
than none because it is trusted. The audit's sharpest question: is replay
completeness computed by diffing against the LIVE `TypedLedgerEvent`
discriminator registry (so a future event type surfaces as unaccounted), or a
hardcoded handled-type set (which would silently lie)? Independent
quality-reviewer verification is dispatched on exactly this point.

Secondary focus: **Boundary Invariant #2 (derived-never-authority)** — confirm
no `gz validate` scope / gate / closeout step consumes the graph as enforcement.

## Findings Placeholder

Captured in `AUDIT.md`.

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under `audit/proofs/` and referenced in `AUDIT.md`.
- Bound Fidelity Gate passes (thesis run against the running system).
- Independent spec-reviewer + quality-reviewer verdicts recorded.
- No edits to accepted ADR prose.

## Attestation Placeholder

Operator completes in `AUDIT.md` via verbal `accept audit` / `verify audit`,
relayed into the `validated` receipt.
