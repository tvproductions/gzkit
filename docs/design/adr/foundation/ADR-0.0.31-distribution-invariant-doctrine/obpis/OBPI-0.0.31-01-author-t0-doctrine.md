---
id: OBPI-0.0.31-01-author-t0-doctrine
parent: ADR-0.0.31-distribution-invariant-doctrine
item: 1
lane: Lite
status: Completed
---

# OBPI-0.0.31-01-author-t0-doctrine: Author T0 Doctrine

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md`
- **Checklist Item:** #1 — "Author T0 doctrine paragraph in `docs/governance/trust-doctrine.md` (extend layer table from T1/T2/T3 to T0/T1/T2/T3, paragraph with verbatim failure-mode quote, forward-link to ADR-0.0.32, cross-link from this ADR's Evidence section)"

**Status:** Draft

## Objective

Land the T0 distribution invariant as authored doctrine in
`docs/governance/trust-doctrine.md` so that every downstream artifact —
ADR-0.0.32's mechanical work, future canonical-surface promotions, future
`gz validate --distribution` enforcement — has a single citable invariant
to satisfy. Concretely: add a T0 paragraph and extend the layer table
from three rows (T1/T2/T3) to four (T0/T1/T2/T3); the paragraph quotes
the GHI #318 failure mode verbatim; forward-links to ADR-0.0.32 as the
mechanical enforcement surface; cross-links from ADR-0.0.31's Evidence
section into the trust-doctrine layer table to close the bidirectional
link. Doctrine surface only — no scaffolders, no `pyproject.toml` edits,
no mechanical enforcement code, AND no scorecard or catalog work lands
in this OBPI (those are OBPI-0.0.31-02 and -03 respectively).

## Lane

**Lite** — documentation-only authoring of a doctrine layer. No CLI
surface, schema, or runtime contract changes. Mechanical enforcement of
T0 lives entirely in ADR-0.0.32 (the heavy-lane sibling). Per § Lane &
Kind Attestation Matrix, this OBPI still gates on **brief-level Gate 5
human attestation** because the parent ADR is `kind: foundation` — lite
foundation OBPIs are not self-closeable.

## Allowed Paths

- `docs/governance/trust-doctrine.md` — add T0 paragraph + extend the layer table from three rows (T1/T2/T3) to four (T0/T1/T2/T3)
- `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md` — extend Evidence section with cross-link confirmations once the upstream file lands

## Denied Paths

- `docs/governance/advisory-rules-audit.md` — scorecard entry belongs to OBPI-0.0.31-02
- `docs/governance/distribution_invariant_catalog.md` — failure-mode catalog belongs to OBPI-0.0.31-03
- `src/**` — no source code changes in this OBPI; mechanical enforcement is ADR-0.0.32 scope
- `pyproject.toml` — wheel includes belong to OBPI-0.0.32-04
- `tests/**`, `features/**` — no test surface; the validate-side mechanical check belongs to OBPI-0.0.32-05
- `.gzkit/rules/**` — no rule promotions in this OBPI
- `docs/design/adr/foundation/ADR-0.0.32-*` — sibling-ADR edits would couple the two artifacts; cross-references should flow ADR-0.0.32 → ADR-0.0.31, not the other direction

## Requirements (FAIL-CLOSED)

1. The T0 paragraph in `docs/governance/trust-doctrine.md` MUST sit alongside the existing T1/T2/T3 entries and follow the same authority/question framing the table establishes for the other three layers.
2. The trust-doctrine layer table MUST grow from three rows to four; T0 MUST be the first row (upstream of T1) per the doctrine sequencing in ADR-0.0.31 § Decision.
3. The T0 paragraph MUST quote the GHI #318 failure mode verbatim ("a wheel that ships without a canonical surface is a T0 breach, regardless of whether downstream `gz init` reports success") so future readers trace the doctrine to its origin defect.
4. The T0 paragraph MUST link forward to ADR-0.0.32 as the citable mechanical enforcement surface; T0 doctrine without a named mechanical sibling is the same advisory-only state the scorecard classifies as Promotable.
5. The ADR-0.0.31 file MUST cross-link into the trust-doctrine layer table from its Evidence section so the bidirectional link is closed once both files land.
6. NO source code, schema, test, or `pyproject.toml` change is permitted in this OBPI. Any such edit is scope creep and STOP-condition.
7. The Mechanical-enforcement contract subsection in ADR-0.0.31 § Decision MUST be reflected verbatim in the T0 doctrine paragraph (the three-item contract: detect missing data, distinguish authored-but-not-shipped, byte-equivalence on fresh install). Drift between the ADR and the doctrine page is the failure pattern this OBPI exists to prevent.
8. The scorecard entry and failure-mode catalog are explicitly OUT OF SCOPE — those land in OBPI-0.0.31-02 and -03 respectively. This OBPI authors the doctrine surface only.

> STOP-on-BLOCKERS:
> - If `docs/governance/trust-doctrine.md` does not exist or does not currently contain a T1/T2/T3 layer table, STOP — the doctrine page must already establish the layer pattern this OBPI extends.
> - If ADR-0.0.32 has not yet been booked at the time of authoring, STOP — T0 references a forward ADR that must exist before the doctrine paragraph can land cleanly.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — names the self-hosting blindness pattern T0 closes
- [ ] Parent ADR § Decision — Mechanical-enforcement contract subsection (the three-item contract that T0 inherits)
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Behavior Rules — Never #7 (state-doctrine layering — T0 sits upstream of T1)
- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix (foundation-kind lite OBPIs require brief-level Gate 5)
- [ ] `docs/governance/trust-doctrine.md` — current T1/T2/T3 layer table (this OBPI extends it)

**Context:**

- [ ] Parent ADR `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/`
- [ ] Sibling ADR `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/` — the mechanical artifact T0 cites
- [ ] GHI #318 — the origin defect that surfaced T0; the verbatim failure-mode quote sources from there
- [ ] ADR-0.0.21 — the chores precedent that established the layered-canon-vs-overlay pattern T0 generalizes from

**Prerequisites (check existence, STOP if missing):**

- [ ] `docs/governance/trust-doctrine.md` exists and contains the T1/T2/T3 table
- [ ] ADR-0.0.32 booked under `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/` (forward-link target)
- [ ] ADR-0.0.31 file exists with `kind: foundation`, `semver: 0.0.31`, `lane: lite`

**Existing Code (understand current state):**

- [ ] Read `docs/governance/trust-doctrine.md` end to end before extending
- [ ] Read at least three existing scorecard rows in `advisory-rules-audit.md` to understand the row schema before adding T0
- [ ] Read ADR-0.0.31 § Decision Mechanical-enforcement contract before paraphrasing (Requirement #8 forbids drift)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item #1 quoted verbatim above
- [ ] Cross-link from ADR-0.0.31 Evidence section into `trust-doctrine.md` lands in the same patch

### Gate 2: TDD (Red-Green-Refactor)

- [ ] No code change → no unit-test red→green cycle. Documentation-only work.
- [ ] Validation: `uv run gz validate --documents` passes after edits
- [ ] Validation: `uv run gz lint` passes (markdownlint catches table-shape regressions)
- [ ] Validation: `uv run mkdocs build --strict` passes (catches broken cross-links)

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] No type-check surface (no Python edits)

### Gate 5: Human (foundation-kind brief-level attestation per § Lane & Kind Attestation Matrix)

- [ ] Human attestation recorded; foundation-kind lite OBPIs are NOT self-closeable

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run mkdocs build --strict

grep -q "^## T0 — Distribution\|^### T0 — Distribution" docs/governance/trust-doctrine.md
grep -q "ADR-0.0.32" docs/governance/trust-doctrine.md
grep -q "trust-doctrine" docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md
# scorecard entry verification belongs to OBPI-0.0.31-02 verification
```

## Acceptance Criteria

- [ ] REQ-0.0.31-01-01: `docs/governance/trust-doctrine.md` contains a T0 section/row alongside T1/T2/T3, with the failure-mode quote ("a wheel that ships without a canonical surface is a T0 breach, regardless of whether downstream `gz init` reports success") rendered verbatim
- [ ] REQ-0.0.31-01-02: The trust-doctrine layer table grows from three rows to four; T0 is the first (upstream) row
- [ ] REQ-0.0.31-01-03: The T0 paragraph forward-links to ADR-0.0.32 as the mechanical enforcement surface
- [ ] REQ-0.0.31-01-04: The Mechanical-enforcement contract from ADR-0.0.31 § Decision (three-item contract) is reflected verbatim in the T0 doctrine paragraph
- [ ] REQ-0.0.31-01-05: ADR-0.0.31 § Evidence section cross-links to `docs/governance/trust-doctrine.md` so the bidirectional link is closed
- [ ] REQ-0.0.31-01-06: No file outside Allowed Paths is touched in this OBPI's commit set; specifically `docs/governance/advisory-rules-audit.md` (OBPI-0.0.31-02 scope) and `docs/governance/distribution_invariant_catalog.md` (OBPI-0.0.31-03 scope) are NOT touched
- [ ] REQ-0.0.31-01-07: `uv run gz validate --documents` and `uv run mkdocs build --strict` both exit 0 after the edits land

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** Documentation-only work; validation gates exit 0
- [ ] **Code Quality:** `gz lint` clean
- [ ] **Value Narrative:** T0 doctrine layer is now citable by every future canonical-surface promotion
- [ ] **Key Proof:** `grep "T0" docs/governance/trust-doctrine.md` returns the new section
- [ ] **OBPI Acceptance:** Evidence recorded below
- [ ] **Gate 5 (Foundation lite-lane brief-level human attestation):** Human witness recorded

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste `gz validate --documents` and `mkdocs build --strict` output here
```

### Code Quality

```text
# Paste `gz lint` output here
```

### Gate 5 (Human)

```text
# Record attestation text here when ceremony fires
```

### Value Narrative

Before this OBPI: the trust-doctrine page documented T1/T2/T3 layers but had no name for the distribution contract — the wheel could ship without a canonical surface and downstream `gz init` would still report success. After this OBPI: T0 names that contract, the failure mode is quotable, and ADR-0.0.32's mechanical work cites a landed invariant rather than a forward-referenced one.

### Key Proof


Key proof command:

```
grep -n "T0" docs/governance/trust-doctrine.md
```

Output confirms T0 row in 4-row layer table (line 67), ### T0 — Distribution Invariant section header (line 74), verbatim GHI #318 failure-mode quote (line 81: "a wheel that ships without a canonical surface is a T0 breach, regardless of whether downstream `gz init` reports success"), and all three mechanical enforcement contract items (lines 87–89).

ARB-receipt evidence:
- Lint clean — receipt arb-ruff-ac8036fb9f454299860fc618e82f614d
- Typecheck clean — receipt arb-step-typecheck-92a2e4f39ffb4d98a3bfa4da571a5e4e
- Unittests pass — receipt arb-step-unittest-f297fe1c2d384935ba29a1fe1963a593

Validation gates:
- uv run gz validate --documents → exit 0
- uv run mkdocs build --strict → exit 0 (no broken links after directory→file path fix)

Cross-link verification:
- grep "trust-doctrine" docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md → multiple matches (Evidence section [x] items reference trust-doctrine.md)

### Implementation Summary


- Files modified: docs/governance/trust-doctrine.md (added ## Trust Layers overview section with T0/T1/T2/T3 layer table, ### T0 — Distribution Invariant paragraph including verbatim GHI #318 failure-mode quote, three-item mechanical enforcement contract, forward-link to ADR-0.0.32, doctrine-source link to ADR-0.0.31); docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md (closed bidirectional cross-link by marking Doctrine and Cross-link Evidence items complete with references to trust-doctrine.md)
- Tests added: n/a — documentation-only OBPI; brief denies tests/ and features/
- REQ verification: all 7 REQs verified through grep + gz validate --documents + mkdocs build --strict; --accept-uncovered passed at completion (documentation-only, no test surface)
- Date completed: 2026-05-10
- Attestation status: Operator-attested via Stage 4 ceremony ("attest completed"); Gate 5 brief-level attestation required because parent ADR is kind: foundation
- Defects noted: ADR-0.0.30 frontmatter drift surfaced and reconciled during precomplete (unrelated)

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — T0 distribution invariant authored in docs/governance/trust-doctrine.md (## Trust Layers section, ### T0 — Distribution Invariant paragraph, 4-row layer table T0/T1/T2/T3, verbatim GHI #318 failure-mode quote, three-item mechanical enforcement contract, forward-link to ADR-0.0.32, bidirectional cross-link from ADR-0.0.31 Evidence section). All 7 REQs verified by grep + gz validate --documents + mkdocs build --strict. ARB receipts: arb-ruff-ac8036fb9f454299860fc618e82f614d (lint clean), arb-step-typecheck-92a2e4f39ffb4d98a3bfa4da571a5e4e (typecheck clean), arb-step-unittest-f297fe1c2d384935ba29a1fe1963a593 (unittests pass). Operator: Jeffry Babb.
- Date: 2026-05-10

---

**Brief Status:** Completed

**Date Completed:** 2026-05-10

**Evidence Hash:** -
