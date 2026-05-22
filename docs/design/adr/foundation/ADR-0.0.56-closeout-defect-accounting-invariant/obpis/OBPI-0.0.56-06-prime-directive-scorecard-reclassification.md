---
id: OBPI-0.0.56-06-prime-directive-scorecard-reclassification
parent: ADR-0.0.56-closeout-defect-accounting-invariant
item: 6
lane: Lite
status: Draft
---

# OBPI-0.0.56-06-prime-directive-scorecard-reclassification: Prime Directive Scorecard Reclassification

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md`
- **Checklist Item:** #6 - "OBPI-0.0.56-06: Reclassify PRIME DIRECTIVE #5/#6 Judgment → Mechanical on `docs/governance/advisory-rules-audit.md`; update operator runbook and `gz validate` manpage; commit carries the `Eval-feedback-source:` trailer citing the three insights records."

**Status:** Draft

## Objective

Reclassify PRIME DIRECTIVE #5/#6 Judgment → Mechanical on `docs/governance/advisory-rules-audit.md`; update operator runbook and `gz validate` manpage; commit carries the `Eval-feedback-source:` trailer citing the three insights records.

## Lane

**Lite** - This OBPI changes documentation (`docs/user/runbook.md`, the `docs/user/manpages/validate.md` manpage), the `docs/governance/advisory-rules-audit.md` governance scorecard, and one test file — no command, API, schema, or runtime-contract surface. The `gz validate --closeout-defect-accounting` scope it documents is created by OBPI-02; this OBPI only reflects that scope in docs and reclassifies the scorecard rows. Per AGENTS.md § Lane Rules, documentation-and-scorecard work stays Lite.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md` — parent ADR; READ reference for the § Decision item 6 contract
- `docs/governance/advisory-rules-audit.md` — the advisory scorecard; reclassify the PRIME DIRECTIVE #5/#6 rows to **Mechanical** and update the counts table
- `docs/user/runbook.md` — operator runbook; add the `gz validate --closeout-defect-accounting` scope to the operator workflow
- `docs/user/manpages/validate.md` — `gz validate` manpage; add the new scope to the flag list and the EXAMPLES section with real CLI output
- `tests/governance/test_promoted_advisory_audits.py` — promoted-advisory-audit tests; the reclassified rows must trace to the mechanical witness

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/commands/closeout.py`, `src/gzkit/events.py`, `src/gzkit/governance/trust_audits/`, `src/gzkit/commands/validate_cmd.py` — the mechanism is delivered by OBPI-01/02/03; this OBPI documents and reclassifies, it does not author runtime code
- `.claude/hooks/`, `.gzkit/skills/ghi-close/` — OBPI-05 scope
- `CLAUDE.md`, `AGENTS.md` — the PRIME DIRECTIVE text itself is NOT edited; the ADR § Scope boundary states the prose obligation stays. This OBPI reclassifies the *scorecard entry*, not the directive
- Paths not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: On `docs/governance/advisory-rules-audit.md`, the scorecard rows for PRIME DIRECTIVE #5 (FLAG DEFECTS, NEVER EXCUSE THEM) and #6 (EVERY DEFECT MUST BE TRACKABLE) — currently scored **Judgment** (row 17 "Every defect must be trackable" and the "never say out of scope / flag defects" cluster) — MUST be reclassified to **Mechanical**, with the Notes column naming `gz validate --closeout-defect-accounting` (ADR-0.0.56) as the mechanical witness that refutes row 17's Judgment rationale ("no reliable mechanical signal for 'defect noticed but not tracked'").
2. REQUIREMENT: The scorecard counts table (Mechanical / Promotable / Judgment / Ambiguous) MUST be recomputed to reflect the reclassification, and the "Counts updated" date line MUST be moved to this OBPI's completion date with a note citing ADR-0.0.56.
3. REQUIREMENT: The reclassified rows MUST resolve GHI #514 deferred design question 3 — the Notes column or an accompanying line MUST explicitly state the deferred question is resolved by this ADR's reconcile scope, not deferred again.
4. REQUIREMENT: `docs/user/runbook.md` MUST be updated to include the `gz validate --closeout-defect-accounting` scope in the operator workflow, consistent with the three-layer documentation model in `.claude/rules/gate5-runbook-code-covenant.md`.
5. REQUIREMENT: `docs/user/manpages/validate.md` MUST list the `--closeout-defect-accounting` flag and its EXAMPLES section MUST show real CLI output from the command — NEVER a placeholder or `<…>` example (`.claude/rules/gate5-runbook-code-covenant.md` anti-pattern).
6. REQUIREMENT: The commit closing this OBPI MUST carry an `Eval-feedback-source:` trailer. GHI #514 is `eval-feedback`-labeled; per AGENTS.md Behavior Rule 12 and ADR-0.0.26, a rule edit landing under an eval-feedback GHI requires the trailer. The trailer MUST cite the three insights records the parent ADR § Decision item 6 names (the #486 / #489 / #490 closing-summary-excuse records). The trailer is validated by `gz validate --commit-trailers`.
7. REQUIREMENT: This OBPI MUST NOT edit the PRIME DIRECTIVE text in `CLAUDE.md` / `AGENTS.md` — the prose obligation stays per the parent ADR § Scope boundary. Only the scorecard *classification* and the operator-facing docs change.
8. REQUIREMENT: Every `gz <verb>` string added to an operator-facing doc MUST resolve to a registered parser verb per `.claude/rules/governance-core.md` § Operator-doc verb resolution; `gz validate --cli-alignment` MUST pass.

> STOP-on-BLOCKERS: if OBPI-02 (`gz validate --closeout-defect-accounting` scope) is not yet landed, the manpage example cannot show real output — print a BLOCKERS list and halt. This OBPI is sequenced last (01 → 02 → 03 → {04, 05} → 06).

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

- [ ] `docs/governance/advisory-rules-audit.md` — current PRIME DIRECTIVE #5/#6 scorecard rows and the counts table; note their current score before reclassifying
- [ ] `.claude/rules/gate5-runbook-code-covenant.md` — three-layer documentation model; runbook + manpage are first-class deliverables
- [ ] AGENTS.md Behavior Rule 12 and ADR-0.0.26 — the `Eval-feedback-source:` commit-trailer contract for eval-feedback-labeled rule edits
- [ ] Parent ADR § Decision item 6 and § Intent — the three insights records (#486 / #489 / #490) the trailer must cite
- [ ] **Related OBPIs:** depends on OBPI-02 (the manpage example needs a landed `gz validate --closeout-defect-accounting` scope). Sequenced last: 01 → 02 → 03 → {04, 05} → 06 (this is step 06).

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/governance/advisory-rules-audit.md`
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
uv run gz validate --advisory-scorecard
uv run gz validate --cli-alignment
uv run gz validate --commit-trailers
uv run mkdocs build --strict
uv run -m unittest tests.governance.test_promoted_advisory_audits -v
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Confirm the PRIME DIRECTIVE #5/#6 rows now read Mechanical with the ADR-0.0.56 witness:
grep -nE 'closeout-defect-accounting|EVERY DEFECT|EXCUSE' docs/governance/advisory-rules-audit.md

# The advisory-scorecard self-test passes with the recomputed counts:
uv run gz validate --advisory-scorecard; echo "exit=$?"

# The new scope appears in the operator-facing manpage with real output:
grep -n 'closeout-defect-accounting' docs/user/manpages/validate.md docs/user/runbook.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.56-06-01: Given the advisory scorecard, when the PRIME DIRECTIVE #5/#6 rows are read after this OBPI, then both are scored **Mechanical** and the Notes column names `gz validate --closeout-defect-accounting` (ADR-0.0.56) as the mechanical witness.
- [ ] REQ-0.0.56-06-02: Given the reclassification, when the scorecard counts table is read, then the Mechanical / Promotable / Judgment counts are recomputed consistently and the "Counts updated" date and ADR-0.0.56 citation are present.
- [ ] REQ-0.0.56-06-03: Given the operator-facing docs, when `docs/user/runbook.md` and `docs/user/manpages/validate.md` are read, then both name the `gz validate --closeout-defect-accounting` scope and the manpage EXAMPLES section shows real CLI output (no placeholder).
- [ ] REQ-0.0.56-06-04: Given GHI #514 is `eval-feedback`-labeled, when the closing commit is inspected, then it carries an `Eval-feedback-source:` trailer citing the three insights records (#486 / #489 / #490) and `gz validate --commit-trailers` passes.
- [ ] REQ-0.0.56-06-05: Given the scope boundary, when `CLAUDE.md` and `AGENTS.md` are diffed, then the PRIME DIRECTIVE prose text is unchanged — only the scorecard classification and operator docs moved.
- [ ] REQ-0.0.56-06-06: Given the new scope verbs added to operator docs, when `gz validate --cli-alignment` and `gz validate --advisory-scorecard` run, then both exit 0.

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
