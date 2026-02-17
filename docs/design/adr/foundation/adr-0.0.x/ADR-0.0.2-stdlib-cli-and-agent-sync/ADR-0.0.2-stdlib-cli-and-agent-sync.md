# ADR-0.0.2: Stdlib CLI Foundation and Agent Sync Grammar

<!--
ADR TEMPLATE: ADR_TEMPLATE_SEMVER.md
Foundational ADR (0.0.z)
This ADR authorizes migration and command normalization work.
-->

---

## Tidy First Plan

Behavior-preserving tidyings required before parser migration work:

1. Inventory current `gz` command surface, aliases, and docs references.
2. Define compatibility guarantees for existing commands and flags.
3. Freeze canonical command grammar for agent control-surface synchronization.

**No governance semantics change in this phase.**

STOP / BLOCKERS:

- If any existing command loses parity without an explicit deprecation path, stop.
- If migration requires non-stdlib CLI frameworks, stop.

---

## Status & Metadata

**Date Added:** 2026-02-07
**Status:** Draft
**SemVer:** 0.0.2
**Series:** adr-0.0.x
**Area:** Governance Foundation - CLI Runtime
**Lane:** Foundational

---

## Feature Checklist - Appraisal of Completeness

Each item below is an execution authorization and MUST map to one OBPI.

1. Define stdlib-only CLI invariant (`argparse` + stdlib support modules).
2. Establish canonical command grammar: `gz agent sync control-surfaces`.
3. Provide compatibility aliases with explicit deprecation messaging.
4. Migrate command parsing/dispatch off Click while preserving command behavior.
5. Remove Click from runtime dependencies and test harness.
6. Update generated control surfaces to use canonical grammar.
7. Add regression tests for canonical command path and alias behavior.

---

## Intent

Ensure `gzkit` CLI governance behavior is implemented with Python standard library
facilities only, and make agent control-surface synchronization unambiguous via a
stable command grammar.

---

## Decision

### Stdlib Parser Requirement

`gzkit` MUST use stdlib CLI capabilities for argument parsing and dispatch.

Allowed examples:

- `argparse`
- `shlex`
- `sys.argv`

Disallowed for runtime command parsing:

- third-party parser frameworks (for example, Click/Typer).

---

### Canonical Command Grammar

The canonical command for control-surface synchronization is:

`gz agent sync control-surfaces`

Compatibility aliases may exist during transition but must:

- emit deprecation guidance
- preserve behavior
- include removal criteria in follow-up OBPIs

Aliases covered by this ADR:

- `gz agent-control-sync`
- `gz sync`

---

### Governance Priority

Command grammar and parser policy are governance surfaces because they determine
cross-tool reproducibility (Codex, Copilot, Claude).

Therefore, command naming and parser runtime choices are controlled by ADR,
not ad-hoc implementation preference.

---

## Rationale

1. Third-party parser frameworks introduce avoidable dependency and behavior drift risk.
2. Stdlib parser usage improves portability and long-term maintainability.
3. A single canonical sync grammar reduces instruction drift across tool-specific surfaces.
4. Explicit alias policy allows migration without breaking active workflows.

---

## Consequences

### Positive

- Parser/runtime policy is explicit and enforceable.
- Command instructions can converge across AGENTS/CLAUDE/Copilot surfaces.
- Reduced dependency surface for critical governance entrypoints.

### Negative

- Short-term migration cost from existing Click-decorated command wiring.
- Temporary complexity while alias paths remain supported.
- Test harness must move away from Click-specific utilities.

These tradeoffs are intentional.

---

## Evidence (Foundational Gates)

- **Gate 1 (ADR):** This document defines parser and command-surface invariants.
- **Gate 3 (Docs):** Canonical grammar and deprecation policy are documented.
- **Gate 5 (Human):** Human attests migration direction before implementation completion.

---

## Evidence Ledger (Authoritative)

### Canonical Inputs

- `AGENTS.md`
- `src/gzkit/cli.py`
- `src/gzkit/sync.py`
- `src/gzkit/templates/*`

### Produced Outputs

- This ADR
- Follow-on OBPIs and implementation changes

---

## OBPIs

| ID | Description | Status |
|----|-------------|--------|
| OBPI-0.0.2-01 | CLI command surface inventory and compatibility matrix | Pending |
| OBPI-0.0.2-02 | argparse dispatcher and command binding migration | Pending |
| OBPI-0.0.2-03 | Canonical sync grammar + alias deprecation behavior | Pending |
| OBPI-0.0.2-04 | Runtime/test dependency removal for Click | Pending |
| OBPI-0.0.2-05 | Docs/control-surface regeneration + drift checks | Pending |

---

## Attestation Block

| Field | Value |
|-------|-------|
| Attestation Term | 0.0.2 |
| Attested By | - |
| Attested At | - |
| Evidence | Pending |

Human attestation required before status changes to Completed.
