---
id: OBPI-0.0.56-03-routing-receipt-model-completion-gate
parent: ADR-0.0.56-closeout-defect-accounting-invariant
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.56-03-routing-receipt-model-completion-gate: Routing Receipt Model Completion Gate

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md`
- **Checklist Item:** #3 - "OBPI-0.0.56-03: `RoutingReceipt` model + completion-gate wiring — author the `RoutingReceipt` frozen Pydantic model (`ghi:<N>` | `commit:<sha>` | `waiver:<operator>+<reason>`, waiver requires a named operator) and wire the reconcile scope into the `gz closeout` completion path as a fail-closed condition; a completion with no recorded snapshot also fails closed."

**Status:** Draft

## Objective

`RoutingReceipt` model + completion-gate wiring — author the `RoutingReceipt` frozen Pydantic model (`ghi:<N>` | `commit:<sha>` | `waiver:<operator>+<reason>`, waiver requires a named operator) and wire the reconcile scope into the `gz closeout` completion path as a fail-closed condition; a completion with no recorded snapshot also fails closed.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md` — parent ADR; READ reference for the § Decision item 3 contract
- `src/gzkit/events.py` — frozen Pydantic models; add the `RoutingReceipt` model (`ghi:<N>` | `commit:<sha>` | `waiver:<operator>+<reason>`)
- `src/gzkit/commands/closeout.py` — `gz closeout` completion path; wire the reconcile scope into `_complete_closeout_pipeline` (line ~474) as a fail-closed condition before the completion event is recorded
- `src/gzkit/governance/trust_audits/closeout_defect_accounting.py` **CREATE** — the reconcile module. It is net-new across the ADR; OBPI-02 lands its initial form ahead of this OBPI in the `01 → 02 → 03` sequence, and this OBPI extends it to consume the canonical `RoutingReceipt` model and add the no-recorded-snapshot fail-closed branch. The `CREATE` marker records that the path does not exist at brief-authoring time — it is not a claim of sole authorship by this OBPI.
- `tests/test_closeout_pipeline.py` — closeout completion-gate tests; add fail-closed-on-unrouted and fail-closed-on-missing-snapshot tests here
- `tests/governance/test_ledger_event_schema_coverage.py` — if `RoutingReceipt` participates in any ledger event payload, the schema coverage tests must reflect it

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/ledger_events.py`, `src/gzkit/schemas/ledger.json` for the `closeout_defect_snapshot` event itself — OBPI-01 owns the snapshot event (this OBPI may only add a `RoutingReceipt` payload shape if the receipt is ledger-recorded)
- `src/gzkit/commands/quality.py`, `src/gzkit/cli/parser_maintenance.py`, `src/gzkit/commands/validate_cmd.py` for scope registration — OBPI-02 owns scope authoring and `gz check` pipeline join
- `src/gzkit/commands/obpi_complete.py`, `src/gzkit/commands/obpi_stages.py` — OBPI-completion extension is OBPI-04 scope
- `.claude/hooks/`, `.gzkit/skills/ghi-close/` — ghi-close backstop is OBPI-05 scope
- `docs/governance/advisory-rules-audit.md`, `docs/user/runbook.md`, `docs/user/manpages/validate.md` — docs + scorecard reclassification is OBPI-06 scope
- Paths not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: A `RoutingReceipt` frozen Pydantic model (`model_config` frozen) MUST be authored in `src/gzkit/events.py`. The model MUST validate exactly three receipt forms: `ghi:<N>` (N a positive integer), `commit:<sha>` (sha a hex commit identifier), and `waiver:<operator>+<reason>` (operator and reason both non-empty). Any other string MUST be rejected by model validation.
2. REQUIREMENT: A `waiver:` receipt MUST require a NAMED operator. An agent-authored waiver — a waiver whose operator field is an agent identity or is empty — MUST be rejected. The agent is NEVER the waiver authority (parent ADR § Consequences/Negative #2).
3. REQUIREMENT: The `gz closeout` completion path (`_complete_closeout_pipeline`) MUST run the `--closeout-defect-accounting` reconcile scope as a fail-closed condition. `gz closeout` MUST NOT record its completion event (attested / lifecycle-transition) while the reconcile exits non-zero.
4. REQUIREMENT: A `gz closeout` completion attempted with NO recorded `closeout_defect_snapshot` event MUST fail closed. This structurally forces the open-anchor — an agent cannot complete a closeout it never opened through `gz closeout` (parent ADR § Consequences/Negative #3c, shakiest-condition mitigation). This is a DISTINCT requirement from REQ #3; both fail-closed branches must exist independently.
5. REQUIREMENT: The fail-closed gate MUST run BEFORE the completion event is recorded, so the closing prose narrated by the agent is inert — the reconcile gate, not the narration, decides whether the closeout completes (parent ADR § Intent).
6. REQUIREMENT: The `waiver:` reason MUST be preserved as a ledger-recordable string so the advisory scorecard can later audit for degenerate patterns ("wip", "later"). NEVER drop or normalize the operator-supplied reason text.
7. REQUIREMENT: This OBPI wires the gate on `gz closeout` ONLY. It MUST NOT extend the gate to `gz obpi complete` (OBPI-04) or ghi-close (OBPI-05). NEVER bundle the other two surfaces into this brief.
8. REQUIREMENT: Work MUST stay inside the Allowed Paths; NEVER touch `.gzkit/ledger.jsonl` directly.

> STOP-on-BLOCKERS: if OBPI-01 (`closeout_defect_snapshot` event) or OBPI-02 (`gz validate --closeout-defect-accounting` scope) is not yet landed, print a BLOCKERS list and halt — this OBPI depends on both.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] `src/gzkit/event_evidence.py` existing frozen-model patterns (e.g. `ObpiReceiptEvidence`, `EventAnchor`) — `RoutingReceipt` shape match
- [ ] `src/gzkit/commands/closeout.py` `_complete_closeout_pipeline` (line ~474) — where the completion event (`attested_event`, `lifecycle_transition_event`) is recorded; the gate inserts before these
- [ ] OBPI-02's `closeout_defect_accounting` reconcile module — the predicate this OBPI wires into the completion path
- [ ] **Related OBPIs:** depends on OBPI-01 (snapshot) and OBPI-02 (reconcile scope). OBPI-04 and OBPI-05 extend this gate to `gz obpi complete` and ghi-close. Sequencing 01 → 02 → 03 → {04, 05} (this is step 03).

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/**`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

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
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below. -->

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_closeout_pipeline -v
uv run -m unittest tests.governance.test_ledger_event_schema_coverage -v
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Attempt a closeout completion while a gate-surfaced defect is unrouted —
# gz closeout fails closed; the agent's closing prose cannot complete it:
uv run gz closeout ADR-0.0.56; echo "exit=$?"

# Attempt a closeout completion with no recorded closeout_defect_snapshot —
# also fails closed, structurally forcing the open-anchor:
uv run gz closeout ADR-0.0.56; echo "exit=$?"

# Validate a routing receipt round-trips the model (all three forms):
uv run python -c "from gzkit.events import RoutingReceipt; print(RoutingReceipt(value='ghi:514')); print(RoutingReceipt(value='commit:8be8d64'))"
# An agent-authored waiver is rejected:
uv run python -c "from gzkit.events import RoutingReceipt; RoutingReceipt(value='waiver:agent+wip')" || echo "agent-authored waiver rejected as expected"
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.56-03-01: Given the three valid receipt forms (`ghi:<N>`, `commit:<sha>`, `waiver:<operator>+<reason>`), when each is constructed via the `RoutingReceipt` model, then the model accepts it; given any other string, then the model rejects it.
- [ ] REQ-0.0.56-03-02: Given a `waiver:` receipt whose operator field is an agent identity or empty, when the `RoutingReceipt` model validates it, then the model rejects it — only a named operator can author a waiver.
- [ ] REQ-0.0.56-03-03: Given a `gz closeout` completion attempt and a `--closeout-defect-accounting` reconcile that exits non-zero, when the completion path runs, then `gz closeout` fails closed and records no completion event.
- [ ] REQ-0.0.56-03-04: Given a `gz closeout` completion attempt with no recorded `closeout_defect_snapshot` event, when the completion path runs, then `gz closeout` fails closed — the open-anchor is structurally forced.
- [ ] REQ-0.0.56-03-05: Given a closeout whose every gate-surfaced defect carries a routing receipt, when `gz closeout` completes, then the fail-closed gate passes and the completion event is recorded.
- [ ] REQ-0.0.56-03-06: Given an operator-supplied waiver reason string, when the waiver is recorded, then the reason text is preserved verbatim and is ledger-recordable for later degenerate-pattern audit.

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

**Date Completed:** -

**Evidence Hash:** -
