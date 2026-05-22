---
id: OBPI-0.0.56-04-obpi-complete-defect-accounting
parent: ADR-0.0.56-closeout-defect-accounting-invariant
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.56-04-obpi-complete-defect-accounting: Obpi Complete Defect Accounting

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md`
- **Checklist Item:** #4 - "OBPI-0.0.56-04: Extend the mechanism to `gz obpi complete` — snapshot at the OBPI-pipeline verify stage, reconcile at OBPI completion."

**Status:** Draft

## Objective

Extend the mechanism to `gz obpi complete` — snapshot at the OBPI-pipeline verify stage, reconcile at OBPI completion.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md` — parent ADR; READ reference for the § Decision item 4 contract
- `src/gzkit/commands/obpi_stages.py` — OBPI-pipeline stage runners; `_run_pipeline_verify_stage` (line ~224) is the snapshot-capture site (the verify-stage analogue of closeout-open)
- `src/gzkit/commands/obpi_complete.py` — `gz obpi complete`; the reconcile-and-gate site (the OBPI-completion analogue of `_complete_closeout_pipeline`)
- `src/gzkit/commands/obpi_precomplete.py` — OBPI pre-completion checks; inspect whether the reconcile predicate belongs in the `_run_all_checks` pre-completion gate chain
- `src/gzkit/governance/trust_audits/closeout_defect_accounting.py` **CREATE** — the reconcile module. It is net-new across the ADR; OBPI-02 lands its initial form and OBPI-03 extends it ahead of this OBPI in the `02 → 03 → 04` sequence, and this OBPI generalizes it to accept an OBPI snapshot anchor as well as a closeout anchor. The `CREATE` marker records that the path does not exist at brief-authoring time — it is not a claim of sole authorship by this OBPI.
- `tests/commands/test_obpi_complete.py` — `gz obpi complete` tests; add OBPI-completion reconcile tests here
- `tests/commands/test_obpi_pipeline.py` — OBPI-pipeline tests; add verify-stage snapshot-capture tests here

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/commands/closeout.py` — the `gz closeout` surface is OBPI-01/03 scope; this OBPI only extends to `gz obpi complete`
- `src/gzkit/event_evidence.py` `CloseoutDefectSnapshot` / `RoutingReceipt` model definitions — OBPI-01 and OBPI-03 author these; this OBPI reuses them as-is. This OBPI MUST NOT add a parallel OBPI-snapshot event class: the OBPI-completion anchor is carried as a discriminated field on the existing snapshot event, not as a second event type. If the existing snapshot event cannot carry an OBPI-completion anchor, that is a blocker the implementer escalates per the STOP-on-BLOCKERS rule — never resolved by silently adding a new event class.
- `.claude/hooks/`, `.gzkit/skills/ghi-close/` — ghi-close backstop is OBPI-05 scope
- `docs/governance/advisory-rules-audit.md`, `docs/user/runbook.md`, `docs/user/manpages/validate.md` — docs + scorecard reclassification is OBPI-06 scope
- Paths not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: The OBPI-pipeline verify stage (`_run_pipeline_verify_stage`) MUST capture a defect baseline snapshot — the verify-stage analogue of the closeout-open snapshot — using the OBPI-01 fingerprint and snapshot mechanism. The snapshot MUST be anchored to the OBPI being verified.
2. REQUIREMENT: `gz obpi complete` MUST run the `--closeout-defect-accounting` reconcile against the verify-stage snapshot as a fail-closed condition. `gz obpi complete` MUST NOT reach a completed state while a gate-surfaced defect from the OBPI's verification lacks a routing receipt (`ghi:<N>` | `commit:<sha>` | `waiver:<operator>+<reason>`).
3. REQUIREMENT: An OBPI completion attempted with NO recorded verify-stage snapshot MUST fail closed — the same open-anchor-forcing rule the closeout path uses (OBPI-03 REQ #4). Freeform OBPI completion that bypasses the pipeline verify stage MUST NOT pass the gate.
4. REQUIREMENT: The mechanism MUST REUSE the OBPI-01 snapshot model, OBPI-02 reconcile predicate, and OBPI-03 `RoutingReceipt` model — this OBPI is an adapter behind the same port, NEVER a parallel implementation. A second fingerprint algorithm or a second reconcile predicate is a defect.
5. REQUIREMENT: The reconcile gate MUST run BEFORE the OBPI completion event is recorded and BEFORE Gate 5 human attestation — defect routing is machine-verified and precedes attestation, never bundled into the attestation payload (parent ADR § Alternatives Considered #2).
6. REQUIREMENT: This OBPI extends the mechanism to `gz obpi complete` ONLY. It MUST NOT touch the `gz closeout` surface (OBPI-01/03) or the ghi-close surface (OBPI-05). NEVER bundle.
7. REQUIREMENT: Work MUST stay inside the Allowed Paths; NEVER touch `.gzkit/ledger.jsonl` directly.

> STOP-on-BLOCKERS: if OBPI-01 (snapshot), OBPI-02 (reconcile scope), or OBPI-03 (`RoutingReceipt` + gate) is not yet landed, print a BLOCKERS list and halt — this OBPI depends on all three.

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

- [ ] `src/gzkit/commands/obpi_stages.py` `_run_pipeline_verify_stage` (line ~224) — the verify-stage runner where the snapshot is captured
- [ ] `src/gzkit/commands/obpi_complete.py` and `obpi_precomplete.py` `_run_all_checks` (line ~116) — the OBPI completion / pre-completion gate chain
- [ ] OBPI-01 snapshot model, OBPI-02 reconcile scope, OBPI-03 `RoutingReceipt` model + gate — the port this OBPI adapts
- [ ] Parent ADR § Decision item 4 — cites insights record ts=2026-05-21T12:31 (behave step coverage, GHI #417/#513) as the live `gz obpi complete` exposure
- [ ] **Related OBPIs:** depends on OBPI-01/02/03. Sibling of OBPI-05 (both extend the same port to a third surface). Sequencing 01 → 02 → 03 → {04, 05} (this is step 04).

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
uv run -m unittest tests.commands.test_obpi_complete -v
uv run -m unittest tests.commands.test_obpi_pipeline -v
uv run gz validate --closeout-defect-accounting
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Run the OBPI pipeline verify stage — it now captures a defect baseline snapshot:
uv run gz obpi pipeline OBPI-0.0.56-04 --from=verify

# Attempt OBPI completion while a verify-stage defect is unrouted — fails closed:
uv run gz obpi complete OBPI-0.0.56-04; echo "exit=$?"

# Attempt OBPI completion with no recorded verify-stage snapshot — also fails closed:
uv run gz obpi complete OBPI-0.0.56-04; echo "exit=$?"
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.56-04-01: Given the OBPI-pipeline verify stage runs, when `_run_pipeline_verify_stage` executes, then a defect baseline snapshot anchored to the OBPI is captured using the OBPI-01 fingerprint and snapshot mechanism.
- [ ] REQ-0.0.56-04-02: Given an OBPI completion attempt and a verify-stage defect with no routing receipt, when `gz obpi complete` runs the reconcile, then completion fails closed.
- [ ] REQ-0.0.56-04-03: Given an OBPI completion attempt with no recorded verify-stage snapshot, when `gz obpi complete` runs, then completion fails closed — the verify-stage open-anchor is structurally forced.
- [ ] REQ-0.0.56-04-04: Given the reconcile gate and Gate 5 human attestation, when `gz obpi complete` runs, then the reconcile gate runs and passes before the attestation step is reached.
- [ ] REQ-0.0.56-04-05: Given an OBPI whose every verify-stage defect carries a routing receipt, when `gz obpi complete` runs, then the reconcile passes and completion proceeds to attestation.

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
