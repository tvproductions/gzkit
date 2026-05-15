---
id: OBPI-0.0.33-04-scenario-reachability-validator
parent: ADR-0.0.33-agent-control-surface-fidelity
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.33-04-scenario-reachability-validator: Scenario Reachability Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`
- **Checklist Item:** #4 - "OBPI-0.0.33-04: Scenario-reachability validator (`gz validate --scenario-reachability`) — advisory Era-1; reads loading-scenarios registry once ADR-0.0.34 lands it; warns on orphan bullets"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Scenario-reachability validator (`gz validate --scenario-reachability`) — advisory Era-1; reads loading-scenarios registry once ADR-0.0.34 lands it; warns on orphan bullets.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/**` — parent ADR package scope
- `src/gzkit/governance/trust_audits/scenario_reachability.py` — validator implementation (new module)
- `src/gzkit/governance/trust_audits/__init__.py` — package re-export of `validate_scenario_reachability`
- `src/gzkit/cli/parser_maintenance.py` — `gz validate --scenario-reachability` flag registration and dispatch
- `tests/governance/test_scenario_reachability.py` — Gate-2 TDD asset
- `docs/user/manpages/gz-validate.md` — manpage entry for the new flag

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- `data/agent-control-surface-scenarios.json` — registry creation is owned by ADR-0.0.34; this OBPI consumes the registry when present but does NOT bootstrap it
- New runtime dependencies (stdlib JSON + substring only)
- Composite wiring into `--surface-fidelity` (owned by OBPI-05)
- Other invariants' validator modules
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

This OBPI implements parent-ADR Invariant 4 only. The other three invariants
are out of scope for this brief.

**Era-1 vs Era-2 behavior is explicit.** Invariant 4 is advisory by parent-ADR
Decision because the loading-scenarios registry is authored under ADR-0.0.34,
not under this ADR. The validator MUST be implemented to the full Era-2
contract from day one; only its exit behavior is Era-1-softened.

1. REQUIREMENT: **Registry-absent behavior (Era 1).** When `data/agent-control-surface-scenarios.json` does NOT exist, the validator MUST exit 0 with a single advisory line to stderr: `scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check`. NEVER silently exit 0 without the advisory line; NEVER exit 3 — registry-absent is bootstrap, not drift. (Mirrors the `--reconcile-freshness` zero-event fail-open pattern at `src/gzkit/governance/trust_audits.py:1024-1028`.)
2. REQUIREMENT: **Registry-present behavior (Era 2).** When `data/agent-control-surface-scenarios.json` exists, the validator parses it as a list of declared loading scenarios. For each scenario, it asserts every Mechanical/Promotable bullet (sourced from `docs/governance/advisory-rules-audit.md`, same source as OBPI-01) is reachable from at least one declared scenario. Reachability semantics: the scenario's declared corpus set covers the bullet's surface file.
3. REQUIREMENT: **Era-2 advisory remains advisory.** Even with the registry present, orphan bullets (covered by no scenario) emit a warning to stderr and exit 0. The validator NEVER exits 3 on orphan bullets without an explicit `--strict` flag (deferred to a follow-up GHI that escalates Era 2 to fail-closed). The advisory mode is per parent-ADR Decision; do NOT promote to fail-closed in this brief.
4. REQUIREMENT: **Registry schema validation (Era 2).** When the registry exists but does not validate against the declared JSON Schema (in `scenario_reachability.py`), the validator exits 3 with a `ValidationError` of `type="scenario_reachability"`. A malformed registry IS fail-closed; an absent registry is NOT.
5. REQUIREMENT: **Output is parseable.** Stderr advisory lines and orphan-bullet warnings MUST share a stable prefix (`scenario-reachability:`) so downstream tooling can grep without false positives. NEVER mix this prefix with other validator output.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Parent ADR file exists: `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`
- [ ] Advisory scorecard exists (bullet source-of-truth): `docs/governance/advisory-rules-audit.md`
- [ ] Trust-audits package exists: `src/gzkit/governance/trust_audits/__init__.py`
- [ ] CLI parser exists: `src/gzkit/cli/parser_maintenance.py`
- [ ] Registry absent is EXPECTED in Era 1; do NOT create `data/agent-control-surface-scenarios.json` in this OBPI (ADR-0.0.34 owns the substrate)

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run gz validate --scenario-reachability             # Era-1: must exit 0 with advisory to stderr
uv run -m unittest tests.governance.test_scenario_reachability -v
test -f src/gzkit/governance/trust_audits/scenario_reachability.py
test ! -f data/agent-control-surface-scenarios.json   # registry MUST remain absent (owned by ADR-0.0.34)
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.33-04-01: Given `data/agent-control-surface-scenarios.json` does not exist (Era-1 state), when `gz validate --scenario-reachability` runs, then it exits 0 AND prints the literal advisory `scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check` to stderr.
- [ ] REQ-0.0.33-04-02: Given a stubbed registry file (test fixture) declaring at least one scenario whose corpus set covers every Mechanical/Promotable bullet, when `gz validate --scenario-reachability` runs, then it exits 0 with no orphan warnings.
- [ ] REQ-0.0.33-04-03: Given a stubbed registry file declaring scenarios that leave at least one Mechanical/Promotable bullet uncovered, when `gz validate --scenario-reachability` runs, then it exits 0 (Era-2 advisory) AND emits `scenario-reachability: orphan bullet` warning lines naming each uncovered bullet.
- [ ] REQ-0.0.33-04-04: Given a registry file that does not validate against the declared JSON Schema, when `gz validate --scenario-reachability` runs, then it exits 3 with a `ValidationError` of `type="scenario_reachability"`.
- [ ] REQ-0.0.33-04-05: Given the validator module, when imported, then `gzkit.governance.trust_audits.validate_scenario_reachability` resolves and matches the package re-export pattern.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
