---
id: OBPI-0.0.57-01-nominal-id-doctrine
parent: ADR-0.0.57-foundation-adr-nominal-id-triage
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.57-01-nominal-id-doctrine: Nominal Id Doctrine

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/ADR-0.0.57-foundation-adr-nominal-id-triage.md`
- **Checklist Item:** #1 - "OBPI-0.0.57-01: **nominal-id-doctrine** — Amend ADR-0.0.17/ADR-0.0.18 to document 0.0.x as a nominal identifier; update CLAUDE.md ordering-rule scope to feature ADRs only; audit validators for sequence-position assumptions."

**Status:** Draft

## Objective

**nominal-id-doctrine** — Amend ADR-0.0.17/ADR-0.0.18 to document 0.0.x as a nominal identifier; update CLAUDE.md ordering-rule scope to feature ADRs only; audit validators for sequence-position assumptions.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md` — amend doctrine to document 0.0.x as nominal-identifier semantics, not a sequence position
- `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md` — amend operator guidance section to clarify nominal vs semver per the new doctrine
- `AGENTS.md` — narrow the existing "Order versioned identifiers semantically" Local Agent Rule to feature ADRs only (ADR-0.0.57 § Decision item 3)
- `src/gzkit/trust_audits.py` — audit `--taxonomy` validator and any related scopes for sequence-position assumptions (e.g. `max_n + 1` style ordering inferences) and remove or document them
- `src/gzkit/validators/` — sibling validator audit if any rely on sequence-position
- `tests/test_taxonomy_validator_nominal.py` — new REQ-derived test asserting validator accepts gaps (e.g. 0.0.5, 0.0.7) without flagging the missing index as drift
- `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/obpis/OBPI-0.0.57-01-nominal-id-doctrine.md` — this brief (evidence updates only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/commands/plan.py` — `_next_available_foundation_semver` replacement is OBPI-0.0.57-02's surface (this OBPI provides the doctrine that justifies it; OBPI-02 implements the allocator change)
- `.gzkit/skills/gz-adr-create/SKILL.md` — skill description update is OBPI-0.0.57-02's surface
- `.gzkit/skills/gz-foundation-triage/**` — new skill is OBPI-0.0.57-03's surface
- `src/gzkit/foundation/**` — triage scoring is OBPI-0.0.57-04's surface
- `docs/user/manpages/**`, `docs/governance/governance_runbook.md` — manpage/runbook updates are OBPI-0.0.57-05's surface
- Renumbering any existing foundation ADR — the doctrine change preserves recorded digits per ADR § Anti-pattern; semantics shift, identifiers do not
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: ADR-0.0.17 MUST receive an amendment block (dated 2026-05-22 or later) that states the third component of foundation ADR IDs (0.0.x) is a nominal integer — a unique identifier, not a sequence position — and links the amendment back to ADR-0.0.57.
2. REQUIREMENT: ADR-0.0.18 MUST receive a companion amendment block documenting nominal-vs-semver operator guidance, preserving the existing foundation/feature/pool guidance content.
3. REQUIREMENT: The "Order versioned identifiers semantically, never lexicographically" rule in AGENTS.md § Local Agent Rules MUST be narrowed to feature ADRs (non-0.0.x semver) — foundation IDs receive a counter-rule explicitly forbidding ordering interpretation.
4. REQUIREMENT: `src/gzkit/trust_audits.py` MUST be audited line-by-line for sequence-position assumptions; any found MUST be documented inline (`# audit-exempt: regression-invariant-overlay <reason>` or equivalent) or removed.
5. REQUIREMENT: `tests/test_taxonomy_validator_nominal.py` MUST assert that `gz validate --taxonomy` accepts a foundation tree with sparse IDs (e.g. 0.0.5 present, 0.0.6 absent, 0.0.7 present) without raising drift errors.
6. NEVER: Renumber, rename, or move any existing foundation ADR directory or file — recorded digits are preserved; semantics shift (ADR § Anti-pattern).
7. NEVER: Edit `src/gzkit/commands/plan.py` in this OBPI — allocator implementation is OBPI-02's boundary; this OBPI authors only the doctrine and validator audit.
8. ALWAYS: Quote the ADR-0.0.57 § Decision verbatim in each amendment block so future readers can trace the doctrine change to its source.
9. REQUIREMENT (Validated-ADR amendment protocol): ADR-0.0.17 and ADR-0.0.18 are both `status: Validated` (see `docs/governance/GovZero/adr-status.md`). Amendments MUST: (a) preserve the original ADR body intact — no rewrites of pre-amendment content; (b) append a dated `## Amendment YYYY-MM-DD — ADR-0.0.57` section at the end of the body, before any Attestation Block; (c) emit one `adr_amendment` evidence event per amended ADR via `uv run gz adr emit-receipt ADR-0.0.<NN> --event amendment --evidence-json '{"source":"ADR-0.0.57","amendment_path":"<rel-path>"}'` so the ledger records the change (Layer-2 truth); (d) leave the parent ADR's `status:` frontmatter at `Validated` — amendments do not re-open closeout.
10. NEVER: Replace, rewrite, or remove existing content in ADR-0.0.17 or ADR-0.0.18 — additive amendment blocks only. The pre-amendment doctrine remains readable as the historical record.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.


## Creates these files

<!-- Net-new files this OBPI creates. Path existence is exempt for these entries per GHI #419. -->

- `src/gzkit/trust_audits.py` **CREATE**
- `tests/test_taxonomy_validator_nominal.py` **CREATE**

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/ADR-0.0.57-foundation-adr-nominal-id-triage.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/ADR-0.0.57-foundation-adr-nominal-id-triage.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/**`
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
uv run gz validate --documents
uv run gz validate --taxonomy
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_taxonomy_validator_nominal

# OBPI-specific surface checks
grep -q "nominal" docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md
grep -q "nominal" docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md
grep -E "feature ADRs only|nominal foundation" AGENTS.md
rg -n "max_n + 1|sequence.position|consecutive.*foundation" src/gzkit/trust_audits.py
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Render the amended doctrine sections
sed -n '/^## Nominal identifier doctrine/,/^## /p' docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md

# Show the narrowed AGENTS.md ordering rule
rg -n "Order versioned identifiers" AGENTS.md

# Demonstrate the validator now accepts sparse foundation IDs (gaps allowed)
uv run gz validate --taxonomy
# Expected: exit 0 even with a gap such as ADR-0.0.55 missing between 0.0.54 and 0.0.56
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.57-01-01: Given ADR-0.0.17 and ADR-0.0.18, when each is read, then both contain a dated amendment block that quotes ADR-0.0.57 § Decision item 1 verbatim and states 0.0.x is nominal, not a sequence position.
- [ ] REQ-0.0.57-01-02: Given the AGENTS.md § Local Agent Rules section, when the ordering rule is read, then its scope is explicitly restricted to feature ADRs and an explicit counter-rule names foundation IDs as nominal.
- [ ] REQ-0.0.57-01-03: Given `src/gzkit/trust_audits.py`, when audited, then every sequence-position assumption (max+1, consecutive integer expectation, etc.) is either removed or annotated with an `audit-exempt` reason.
- [ ] REQ-0.0.57-01-04: Given a foundation tree with a gap (e.g. ADR-0.0.55 absent, 0.0.54 and 0.0.56 present), when `gz validate --taxonomy` runs, then exit code is 0 (no drift error on the missing nominal index).
- [ ] REQ-0.0.57-01-05: Given the brief boundary, when implementation completes, then `src/gzkit/commands/plan.py` is unchanged in this OBPI (allocator change is OBPI-02's surface; doctrine here, code there).
- [ ] REQ-0.0.57-01-06: Given any existing foundation ADR directory under `docs/design/adr/foundation/`, when this OBPI's diff is reviewed, then no directory or file was renamed or moved (digits-preserved invariant).

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
