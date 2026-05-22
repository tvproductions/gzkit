---
id: OBPI-0.0.56-02-closeout-defect-accounting-reconcile-scope
parent: ADR-0.0.56-closeout-defect-accounting-invariant
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.56-02-closeout-defect-accounting-reconcile-scope: Closeout Defect Accounting Reconcile Scope

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md`
- **Checklist Item:** #2 - "OBPI-0.0.56-02: `gz validate --closeout-defect-accounting` reconcile scope — re-run `gz check --json` at completion, diff against the recorded snapshot, exit 3 on any residual defect lacking a routing receipt; join the scope into the default `gz check` pipeline."

**Status:** Draft

## Objective

`gz validate --closeout-defect-accounting` reconcile scope — re-run `gz check --json` at completion, diff against the recorded snapshot, exit 3 on any residual defect lacking a routing receipt; join the scope into the default `gz check` pipeline.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md` — parent ADR; READ reference for the § Decision item 2 contract
- `src/gzkit/governance/trust_audits/` — validator-scope home; add a `closeout_defect_accounting.py` reconcile-scope module alongside siblings (`reconcile.py`, `attestation_receipts.py`)
- `src/gzkit/commands/validate_cmd.py` — `gz validate` scope dispatch; register `closeout_defect_accounting` in the explicit-scope runners and as a default scope joined to the `gz check` pipeline
- `src/gzkit/cli/parser_maintenance.py` — `gz validate` flag registration; add the `--closeout-defect-accounting` argument
- `src/gzkit/commands/quality.py` — `_build_check_steps` (line ~282); join the new scope into the default `gz check` pipeline so derived drift is caught at every quality run
- `tests/commands/test_validate.py` — `gz validate` command tests; add reconcile-scope tests here
- `tests/test_closeout_pipeline.py` — closeout/reconcile integration tests against a recorded snapshot

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/commands/closeout.py`, `src/gzkit/events.py`, `src/gzkit/ledger_events.py`, `src/gzkit/schemas/ledger.json` — the `closeout_defect_snapshot` model, factory, and schema are delivered by OBPI-01; this OBPI consumes the recorded snapshot, it does not author it
- `RoutingReceipt` model and the `gz closeout` fail-closed completion wiring — OBPI-03 scope (this OBPI authors the reconcile predicate; OBPI-03 wires it into the completion path as a gate)
- `src/gzkit/commands/obpi_complete.py`, `src/gzkit/commands/obpi_stages.py` — OBPI-completion extension is OBPI-04 scope
- `.claude/hooks/`, `.gzkit/skills/ghi-close/` — ghi-close backstop is OBPI-05 scope
- `docs/governance/advisory-rules-audit.md`, `docs/user/runbook.md`, `docs/user/manpages/validate.md` — docs + scorecard reclassification is OBPI-06 scope
- Paths not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: A new `gz validate --closeout-defect-accounting` scope MUST be authored. Given an open closeout that has a recorded `closeout_defect_snapshot` event (OBPI-01), the scope MUST re-run `gz check --json`, compute the completion-state defect set using the OBPI-01 fingerprint, and reconcile it against the snapshot.
2. REQUIREMENT: For every defect in the completion-state set, the scope MUST classify it as either RESOLVED (absent from the completion-state result), or ACCOUNTED (carries a routing receipt), or UNROUTED (present, no receipt). The scope MUST exit 3 (fail-closed) on ANY unrouted residual and exit 0 only when every defect is resolved or accounted.
3. REQUIREMENT: A defect that is genuinely NEW at completion — present in the completion-state set but absent from the snapshot — MUST be treated identically to a baseline defect: it needs a routing receipt. The snapshot is the FLOOR of what must be accounted for, NEVER a whitelist of what is allowed to remain (parent ADR § Consequences/Negative #4).
4. REQUIREMENT: The scope MUST reject a snapshot whose recorded `gz_check_invocation` was not the canonical full `gz check` — a snapshot captured under a narrowed scope fails the reconcile closed (parent ADR § Consequences/Negative #8, performative-snapshot risk).
5. REQUIREMENT: The scope MUST be joined into the default `gz check` pipeline via `_build_check_steps` in `src/gzkit/commands/quality.py`, so closeout-defect-accounting drift is caught at every quality run, not only at the closeout boundary (parent ADR § Consequences/Positive #6).
6. REQUIREMENT: When there is no open closeout with a recorded snapshot, the scope MUST exit 0 (no-op) rather than fail — a bare `gz check` outside any closeout context is not a violation. NEVER fail-closed on absence-of-closeout-context; that is OBPI-03's open-anchor concern.
7. REQUIREMENT: This OBPI authors the reconcile predicate and the validate scope ONLY. It MUST NOT wire the scope into the `gz closeout` completion path as a fail-closed gate, and it MUST NOT author the `RoutingReceipt` model — both are OBPI-03. The reconcile may consume a routing-receipt shape, but the canonical `RoutingReceipt` model lands in OBPI-03.
8. REQUIREMENT: Work MUST stay inside the Allowed Paths; the `--closeout-defect-accounting` flag string MUST resolve to a registered parser verb per `.claude/rules/governance-core.md` § Operator-doc verb resolution.

> STOP-on-BLOCKERS: if the `closeout_defect_snapshot` event (OBPI-01) is not yet landed, or `src/gzkit/commands/validate_cmd.py` / `src/gzkit/cli/parser_maintenance.py` is absent, print a BLOCKERS list and halt — this OBPI depends on OBPI-01.

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

- [ ] `src/gzkit/governance/trust_audits/reconcile.py` and `attestation_receipts.py` — sibling validator-scope module shape
- [ ] `src/gzkit/commands/validate_cmd.py` `_explicit_scope_runners` / `_default_scope_runners` — how a scope is registered and joined
- [ ] `src/gzkit/commands/quality.py` `_build_check_steps` (line ~282) — how a check step is added to the default `gz check` pipeline
- [ ] OBPI-01's `closeout_defect_snapshot` event payload and defect fingerprint — this OBPI reconciles against it
- [ ] **Related OBPIs:** depends on OBPI-01 (snapshot primitive must land first); OBPI-03 wires this scope into the `gz closeout` completion path as a fail-closed gate. Sequencing 01 → 02 → 03 (this is step 02).

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
uv run gz validate --closeout-defect-accounting
uv run -m unittest tests.commands.test_validate -v
uv run -m unittest tests.test_closeout_pipeline -v
uv run gz check   # confirm the new scope runs as part of the default check pipeline
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Run the reconcile scope directly against an open closeout with a recorded snapshot:
uv run gz validate --closeout-defect-accounting

# Exit 0 when every completion-state defect is resolved or carries a routing receipt;
# exit 3 with a per-defect listing when any residual is unrouted. Confirm the exit code:
uv run gz validate --closeout-defect-accounting; echo "exit=$?"

# The scope also runs as part of the default check pipeline:
uv run gz check
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.56-02-01: Given an open closeout with a recorded `closeout_defect_snapshot` event and a completion-state defect that carries a routing receipt, when `gz validate --closeout-defect-accounting` runs, then the scope classifies the defect ACCOUNTED and exits 0.
- [ ] REQ-0.0.56-02-02: Given an open closeout with a recorded snapshot and a completion-state defect that carries NO routing receipt, when `gz validate --closeout-defect-accounting` runs, then the scope classifies the defect UNROUTED and exits 3.
- [ ] REQ-0.0.56-02-03: Given a completion-state defect that is absent from the recorded snapshot (genuinely new), when the scope reconciles, then the new defect is treated identically to a baseline defect — it must carry a routing receipt or the scope exits 3; the snapshot is never a whitelist.
- [ ] REQ-0.0.56-02-04: Given a snapshot whose `gz_check_invocation` was not the canonical full `gz check`, when the scope reconciles, then the scope rejects the narrowed-scope snapshot and fails closed.
- [ ] REQ-0.0.56-02-05: Given the new scope is joined into `_build_check_steps`, when `gz check` runs, then the closeout-defect-accounting reconcile executes as part of the default check pipeline.
- [ ] REQ-0.0.56-02-06: Given no open closeout with a recorded snapshot exists, when `gz validate --closeout-defect-accounting` runs, then the scope exits 0 as a no-op rather than failing on absence-of-closeout-context.

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
