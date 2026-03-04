# OBPI Decomposition Matrix

Status: Active
Last reviewed: 2026-03-04
Authority: Canon (Defines the granularity standards for work breakdown structures)

This document provides the formal matrix for decomposing Architectural Decision Records (ADRs) into One Brief Per Item (OBPI) units. It moves the project from heuristic-based planning to a mature, dimension-aware granularity model.

---

## The Granularity Matrix

Decomposition must be right-sized by assessing the ADR across five dimensions.

| Dimension | **Atomic (Lite)** | **Modular (Heavy)** | **Structural (Foundation)** |
| :--- | :--- | :--- | :--- |
| **Data & State** | No schema changes; logic-only. | New schema, config key, or JSON field. | New ledger event, storage engine, or DB migration. |
| **Logic/Engine** | Pure function update or bug fix. | New service, logic flow, or internal component. | New execution runtime, subsystem, or core engine. |
| **Interface** | Internal/Hidden change. | New CLI flag, API endpoint, or UI element. | New CLI command group, Protocol, or Surface. |
| **Observability** | Standard logging inherited. | Targeted status reporting and diagnostics. | Dedicated audit receipts, log paths, and metrics. |
| **Lineage** | N/A. | Scripted state transition or cleanup. | Full historical lineage migration or archival. |

---

## Baseline Structure: The Rule of Three

For any **Heavy** or **Foundation (0.0.x)** ADR, the initial decomposition follows a standard three-layer structural template:

1.  **OBPI-01: Registry/Interface** (Schema, configuration, data structures).
2.  **OBPI-02: Core Execution** (Internal engine, primary logic, algorithms).
3.  **OBPI-03: Lifecycle/Operations** (CLI surface, logging, runbook, status).

---

## Refining Overlay: The Matrix of Four

Once the baseline structure is established, apply the **Matrix of Four** as an overlay filter. Each baseline unit must be tested against these principles; if a unit fails a principle, it MUST be decomposed further.

### 1. The Single-Narrative Rule (Overlay)
**One OBPI = One clear "Value Narrative."**
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

## Lane-Aware Scaling

The matrix scales based on the ADR's lane:

-   **Lite Lane**: Typically triggers 1-2 dimensions. A single, high-granularity OBPI is preferred.
-   **Heavy Lane**: Typically triggers 3+ dimensions. Decomposition into 3-5 OBPIs is the standard.
-   **Foundation (0.0.x)**: Triggers all dimensions. Requires maximum granularity (5+ OBPIs) to ensure base stability.

---

## Enforcement

The `gz-plan` and `gz-adr-promote` skills utilize this matrix during the **Spec Developer Phase**. Agents must perform a "Granularity Assessment" and present the rationale for the resulting OBPI checklist based on these dimensions.
