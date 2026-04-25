---
id: OBPI-0.0.31-01-author-t0-doctrine
parent: ADR-0.0.31-distribution-invariant-doctrine
item: 1
lane: Lite
status: Draft
---

# OBPI-0.0.31-01-author-t0-doctrine: Author T0 Doctrine

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md`
- **Checklist Item:** #1 — "Author T0 doctrine paragraph in `docs/governance/trust-doctrine.md`, cross-link from this ADR, and add the scorecard entry in `docs/governance/advisory-rules-audit.md` classifying T0 as Promotable"

**Status:** Draft

## Objective

Land the T0 distribution invariant as authored doctrine in
`docs/governance/trust-doctrine.md` so that every downstream artifact —
ADR-0.0.32's mechanical work, future canonical-surface promotions, future
`gz validate --distribution` enforcement — has a single citable invariant
to satisfy. Concretely: add a T0 paragraph and table row alongside the
existing T1/T2/T3 layers; cross-link from ADR-0.0.31's text into the
trust-doctrine layer table; register T0 in `docs/governance/advisory-rules-audit.md`
as **Promotable** (the scorecard classification that says: "this rule is
advisory now, mechanical enforcement is owed and named in ADR-0.0.32").
Doctrine surface only — no scaffolders, no `pyproject.toml` edits, no
mechanical enforcement code lands in this OBPI.

## Lane

**Lite** — documentation-only authoring of a doctrine layer. No CLI
surface, schema, or runtime contract changes. Mechanical enforcement of
T0 lives entirely in ADR-0.0.32 (the heavy-lane sibling). Per § Lane &
Kind Attestation Matrix, this OBPI still gates on **brief-level Gate 5
human attestation** because the parent ADR is `kind: foundation` — lite
foundation OBPIs are not self-closeable.

## Allowed Paths

- `docs/governance/trust-doctrine.md` — add T0 paragraph + extend the layer table from three rows (T1/T2/T3) to four (T0/T1/T2/T3)
- `docs/governance/advisory-rules-audit.md` — add T0 scorecard entry classified Promotable
- `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md` — extend Evidence section with cross-link confirmations once the upstream files land

## Denied Paths

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
5. The scorecard entry in `docs/governance/advisory-rules-audit.md` MUST classify T0 as **Promotable** (not Mechanical, not Judgment, not Ambiguous), and MUST cite ADR-0.0.32 as the tracking ADR for promotion.
6. The ADR-0.0.31 file MUST cross-link into the trust-doctrine layer table from its Evidence section so the bidirectional link is closed once both files land.
7. NO source code, schema, test, or `pyproject.toml` change is permitted in this OBPI. Any such edit is scope creep and STOP-condition.
8. The Mechanical-enforcement contract subsection in ADR-0.0.31 § Decision MUST be reflected verbatim in the T0 doctrine paragraph (the three-item contract: detect missing data, distinguish authored-but-not-shipped, byte-equivalence on fresh install). Drift between the ADR and the doctrine page is the failure pattern this OBPI exists to prevent.

> STOP-on-BLOCKERS:
> - If `docs/governance/trust-doctrine.md` does not exist or does not currently contain a T1/T2/T3 layer table, STOP — the doctrine page must already establish the layer pattern this OBPI extends.
> - If `docs/governance/advisory-rules-audit.md` does not contain a Promotable column or row classification, STOP — the scorecard schema must already accept the Promotable classification.
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
- [ ] `docs/governance/advisory-rules-audit.md` — current Promotable/Mechanical/Judgment/Ambiguous schema (this OBPI adds a row)

**Context:**

- [ ] Parent ADR `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/`
- [ ] Sibling ADR `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/` — the mechanical artifact T0 cites
- [ ] GHI #318 — the origin defect that surfaced T0; the verbatim failure-mode quote sources from there
- [ ] ADR-0.0.21 — the chores precedent that established the layered-canon-vs-overlay pattern T0 generalizes from

**Prerequisites (check existence, STOP if missing):**

- [ ] `docs/governance/trust-doctrine.md` exists and contains the T1/T2/T3 table
- [ ] `docs/governance/advisory-rules-audit.md` exists and accepts Promotable classification
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
grep -q "T0" docs/governance/advisory-rules-audit.md
grep -q "ADR-0.0.32" docs/governance/trust-doctrine.md
grep -q "trust-doctrine" docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md
```

## Acceptance Criteria

- [ ] REQ-0.0.31-01-01: `docs/governance/trust-doctrine.md` contains a T0 section/row alongside T1/T2/T3, with the failure-mode quote ("a wheel that ships without a canonical surface is a T0 breach, regardless of whether downstream `gz init` reports success") rendered verbatim
- [ ] REQ-0.0.31-01-02: The trust-doctrine layer table grows from three rows to four; T0 is the first (upstream) row
- [ ] REQ-0.0.31-01-03: The T0 paragraph forward-links to ADR-0.0.32 as the mechanical enforcement surface
- [ ] REQ-0.0.31-01-04: The Mechanical-enforcement contract from ADR-0.0.31 § Decision (three-item contract) is reflected verbatim in the T0 doctrine paragraph
- [ ] REQ-0.0.31-01-05: `docs/governance/advisory-rules-audit.md` contains a T0 row classified **Promotable** with ADR-0.0.32 as the tracking ADR
- [ ] REQ-0.0.31-01-06: ADR-0.0.31 § Evidence section cross-links to `docs/governance/trust-doctrine.md` so the bidirectional link is closed
- [ ] REQ-0.0.31-01-07: No file outside Allowed Paths is touched in this OBPI's commit set
- [ ] REQ-0.0.31-01-08: `uv run gz validate --documents` and `uv run mkdocs build --strict` both exit 0 after the edits land

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

```bash
grep -n "T0" docs/governance/trust-doctrine.md
# Expected: T0 row in layer table + at least one paragraph defining the invariant
```

### Implementation Summary

- Files created/modified:
- Tests added: n/a (documentation-only)
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
