# OBPI Decomposition Matrix

Status: Active
Last reviewed: 2026-10-28
Authority: Canon (Defines the granularity standards for work breakdown structures)

This document provides the formal matrix for sizing work. **Rekeyed 2026-10-28** by drydock RO-5 ruling 9 (`docs/governance/harbor-ro5-work-packages.md`): the five dimensions and the single-narrative rule size an **outcome** and a **task card** instead of an ADR checklist, detached from lane and kind. The Lite, Heavy and Foundation columns and the checklist-count step are retired. A work package's lane is read from its outcome (heavy when the outcome is user-facing, requirements model decision 10) or stored on its repair package (ruling 4), never from this matrix. Legacy ADR checklists and OBPIs stay as frozen history; the sections marked *legacy* below describe how they were sized.

---

## The Granularity Matrix

Size an outcome by assessing it across five dimensions; each scores 0, 1 or 2.

| Dimension | **Score 0** | **Score 1** | **Score 2** |
| :--- | :--- | :--- | :--- |
| **Data & State** | No schema changes; logic-only. | New schema, config key, or JSON field. | New ledger event, storage engine, or DB migration. |
| **Logic/Engine** | Pure function update or bug fix. | New service, logic flow, or internal component. | New execution runtime, subsystem, or core engine. |
| **Interface** | Internal/Hidden change. | New CLI flag, API endpoint, or UI element. | New CLI command group, Protocol, or Surface. |
| **Observability** | Standard logging inherited. | Targeted status reporting and diagnostics. | Dedicated audit receipts, log paths, and metrics. |
| **Lineage** | N/A. | Scripted state transition or cleanup. | Full historical lineage migration or archival. |

---

## Baseline Structure: The Rule of Three (legacy)

Legacy **Heavy** and **Foundation (0.0.x)** ADRs followed a standard three-layer structural template:

1.  **OBPI-01: Registry/Interface** (Schema, configuration, data structures).
2.  **OBPI-02: Core Execution** (Internal engine, primary logic, algorithms).
3.  **OBPI-03: Lifecycle/Operations** (CLI surface, logging, runbook, status).

---

## Refining Overlay: The Matrix of Four

Apply the **Matrix of Four** as an overlay filter to each task card (and, on legacy ADRs, to each OBPI). A unit that fails a principle MUST be decomposed further.

### 1. The Single-Narrative Rule (Overlay)
**One task card = One clear "Value Narrative."**
-   *Rule*: Avoid the word "and" in objectives.
-   *Decomposition*: If OBPI-03 covers "Implement CLI commands AND automated auditing," split into two OBPIs.

### 2. The Testability Ceiling (Overlay)
**Small surface = Reliable verification.**
-   *Rule*: Maximum 5 distinct test scenario clusters per OBPI.
-   *Decomposition*: If OBPI-02 (Core) requires 8 different edge-case setups, split into "Core Happy Path" and "Core Error Recovery."

### 3. The State Anchor (Overlay)
**Isolate side-effects.**
-   *Rule*: Isolate any component that writes to the Ledger or modifies persistent state.
-   *Decomposition*: If OBPI-01 defines a schema AND seeds the initial ledger event, split the seeding into its own unit.

### 4. The Surface Boundary (Overlay)
**Separate the "How" from the "What."**
-   *Rule*: Internal logic must never share a brief with an external-facing surface (CLI/API).
-   *Decomposition*: If OBPI-02 attempts to implement the core engine AND the CLI parser, split them.

---

## Deterministic Decomposition Scorecard (legacy)

Legacy ADR decomposition was computed with a scorecard. The scorecard's arithmetic is still
validated where a legacy ADR carries one; its target no longer binds the checklist (Step 4).

### Step 1: Dimension Scores (0/1/2)

Score each dimension:

- Data/State
- Logic/Engine
- Interface
- Observability
- Lineage

Compute:

- `Dimension Total = sum(5 dimension scores)`

### Step 2: Baseline Count

Map `Dimension Total` to a baseline range:

- `0-3 => 1-2`
- `4-6 => 3`
- `7-8 => 4`
- `9-10 => 5+`

Select one baseline count inside that range as `Baseline Selected`.

### Step 3: Mandatory Split Adders

Add `+1` OBPI for each triggered split rule:

- Single-Narrative violation (mixed objectives)
- Surface Boundary violation (internal logic + external surface in one unit)
- State Anchor violation (state-writing mixed with non-state work)
- Testability Ceiling violation (>5 test scenario clusters)

Compute:

- `Split Total = sum(triggered split rules)`
- `Final Target OBPI Count = Baseline Selected + Split Total`

### Step 4: Checklist Synchronization (retired)

Retired 2026-10-28 by RO-5 ruling 9. The checklist count was bound to `Final Target OBPI Count`
by `gz specify`, `gz validate --decomposition` and the ADR document check; none binds it now
(the harbor contract's § List of discrepancies records the retirement).

### Step 5: Per-Brief Size Bounds

Steps 1 to 3 set how many briefs a legacy ADR had. They do not measure one brief. Each live brief is
also held to size bounds on its REQs, requirements, allowed paths, contract bytes and total bytes
by `gz validate --brief-size`, which runs in `gz check`. The bounds are the table in
`src/gzkit/brief_size_bounds.json`; a brief past one is split, as the Refining Overlay requires.

### Calibration Policy

Cutoffs are notional defaults, not immutable constants. They MUST be reviewed and tuned from project
evidence (rework rate, failed gates, attestation churn, and delivery predictability).

---

## Enforcement

Agents sizing an outcome or its task cards perform a "Granularity Assessment" against the five dimensions and the overlays, and present the rationale. The `gz-plan` and `gz-adr-promote` skills still read the legacy scorecard for ADRs authored before the rekey.
