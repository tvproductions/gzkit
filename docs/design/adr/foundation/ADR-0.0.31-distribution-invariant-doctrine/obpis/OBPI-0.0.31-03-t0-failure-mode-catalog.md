---
id: OBPI-0.0.31-03-t0-failure-mode-catalog
parent: ADR-0.0.31-distribution-invariant-doctrine
item: 3
lane: Lite
status: Completed
---

# OBPI-0.0.31-03-t0-failure-mode-catalog: T0 Failure-Mode Catalog

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md`
- **Checklist Item:** #3 — "Author `docs/governance/distribution_invariant_catalog.md` — the T0 failure-mode catalog with worked examples (GHI #318 self-hosting blindness, the chores promotion gap that ADR-0.0.21 implicitly closed before T0 was named, and the canonical 'is this a T0 breach?' decision tree future canonical-surface promotions check against)"

**Status:** Draft

## Objective

Author `docs/governance/distribution_invariant_catalog.md` as the operator-facing companion to the T0 doctrine paragraph in trust-doctrine.md. Where the doctrine page names the invariant in one paragraph, this catalog gives it teeth: worked examples of past T0-class failures (GHI #318 self-hosting blindness; the chores-promotion gap that ADR-0.0.21 implicitly closed before T0 had a name), and a canonical "is this a T0 breach?" decision tree that future canonical-surface promotions (hooks, templates, personas, future surface kinds) check against during authoring. The catalog turns T0 from "a paragraph anyone can cite" into "a checklist anyone can apply" — closing the gap between doctrine and judgment that the original GHI #318 amendment surfaced.

## Lane

**Lite** — single new governance document, no CLI / schema / runtime contract changes. Foundation-kind so brief-level Gate 5 still applies per § Lane & Kind Attestation Matrix; foundation-lite OBPIs are NOT self-closeable.

## Allowed Paths

- `docs/governance/distribution_invariant_catalog.md` — new file authored by this OBPI
- `docs/governance/trust-doctrine.md` — single "See also" cross-reference line in § T0 (REQ-5; not the doctrine paragraph itself, which remains owned by OBPI-0.0.31-01)
- `docs/governance/governance_runbook.md` — single discoverability line in § Layered trust (REQ-8)
- `tests/governance/test_distribution_invariant_catalog.py` — structural test asserting REQ-01..08 (operator-authorized scope expansion; needed to satisfy ADR-0.0.25 REQ-coverage gate without `--accept-uncovered` blanket waiver, given foundation-kind GHI #412 narrowing)

## Denied Paths

- `docs/governance/trust-doctrine.md` § T0 doctrine paragraph itself — belongs to OBPI-0.0.31-01 (only the "See also" cross-reference line is in scope here)
- `docs/governance/advisory-rules-audit.md` — scorecard entry belongs to OBPI-0.0.31-02
- `src/**`, `features/**`, `pyproject.toml` — no source / build surface in this OBPI
- `tests/**` outside `tests/governance/test_distribution_invariant_catalog.py` — only the single structural test is in scope
- `.gzkit/rules/**` — the catalog is a `docs/governance/` artifact, not a rule promotion
- `docs/design/adr/foundation/ADR-0.0.32-*` — ADR-0.0.32 cross-references should flow forward, not backward

## Requirements (FAIL-CLOSED)

1. `docs/governance/distribution_invariant_catalog.md` MUST exist after this OBPI, structured as: (a) one-paragraph cross-link to the T0 doctrine in `trust-doctrine.md` (the catalog is the operator-facing companion, not the doctrine); (b) at least two worked-example sections; (c) the canonical decision tree.
2. The first worked example MUST be **GHI #318 self-hosting blindness**: how the dogfood loop concealed the missing-canonical-shipment for the entire pre-1.0 cycle, with the four failure classes (A: rules unscaffolded; B: skills as stubs; C: includes chores-only; D: re-run only adds missing) each named and cross-linked to the OBPI-0.0.32-NN that closes it.
3. The second worked example MUST be **the chores-promotion gap** (ADR-0.0.21): how chores got the right packaging treatment by accident-of-timing rather than by doctrine, and why that pattern is the implicit T0 enforcement that has been working invisibly. Frame it as the "T0 was operationally true before it was named" example so future readers understand why the doctrine retroactively binds work that predates it.
4. A third example MAY be authored if a clear T0-class candidate exists at authoring time (e.g. an in-flight hook-promotion or persona-promotion that benefits from being framed under T0 explicitly). Do NOT invent examples for symmetry — three real examples beat three contrived ones, but two real examples beat three with a contrived third.
5. The decision tree MUST answer "is this canonical-surface change a T0 breach?" with concrete inputs: does the surface ship in the wheel? does `pip install py-gzkit && gz init` reproduce it? does the baseline manifest list it? does `gz validate --distribution` cover it? Each branch terminates at a concrete recovery action (extend includes / add to baseline / extend validator scope / file follow-up GHI).
6. The catalog MUST forward-link to ADR-0.0.32 as the mechanical-enforcement surface and back-link from the trust-doctrine T0 paragraph (the cross-link in the doctrine page becomes a "see also: docs/governance/distribution_invariant_catalog.md for worked examples").
7. NO doctrine prose duplicating trust-doctrine.md is permitted — the catalog references and applies the doctrine, it does not redefine it. Drift between the catalog's framing of T0 and the doctrine page's framing is the failure pattern this rule prevents.
8. The catalog MUST be discoverable via at least one runbook entry (e.g. `docs/user/runbook.md` or `docs/governance/governance_runbook.md` gets a one-line "When promoting a new canonical surface, read `docs/governance/distribution_invariant_catalog.md` first"). If runbook updates are required, this OBPI's Allowed Paths must be expanded — flag this as a known scope-edge before authoring.
9. `uv run gz validate --documents` MUST exit 0; `uv run mkdocs build --strict` MUST exit 0.

> STOP-on-BLOCKERS:
> - If OBPI-0.0.31-01 has not at minimum been authored (the doctrine paragraph the catalog references), STOP — the catalog should not invent a definition of T0; it references the canonical one.
> - If the operator has not yet attested to OBPI-0.0.31-01's content and the doctrine framing is in flux, STOP — the catalog's worked examples MUST land against a stable doctrine surface.
> - If a runbook update IS needed for discoverability (Requirement #8), STOP and either (a) expand this OBPI's Allowed Paths to include the runbook file with operator approval, (b) defer runbook discoverability to a follow-up patch.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Intent — names self-hosting blindness as the origin failure mode
- [ ] Parent ADR § Consequences (Positive) — names "Surfaces a place to file future 'self-hosting blindness' patterns. T0 generalizes beyond skills/rules to any canonical surface where the in-repo content and the wheel content can drift."
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `docs/governance/trust-doctrine.md` — current T0 paragraph (after OBPI-0.0.31-01 lands) is the doctrine the catalog references
- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix — foundation-lite still requires brief-level Gate 5
- [ ] GHI #318 — origin defect; the body's failure-class analysis (A/B/C/D) is the source material for worked example #1

**Context — for worked examples:**

- [ ] ADR-0.0.21-chores-as-gzkit-surface — full ADR; how the chores promotion handled package-data shipping correctly (the "T0 was operationally true before it was named" example #2)
- [ ] OBPI-0.0.21-04-resolver-with-fallback — the project-first → package-fallback pattern the chores promotion established
- [ ] OBPI-0.0.21-07-bdd-chores-distribution — the build-then-install behave precedent that ADR-0.0.32-04's smoke test mirrors
- [ ] ADR-0.0.32 § Decision — the mechanical enforcement chain the catalog forward-links to

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.31-01 at minimum Draft (the T0 doctrine paragraph it points at must exist conceptually)
- [ ] OBPI-0.0.31-02 at minimum Draft (the scorecard registration the catalog mentions in passing)
- [ ] ADR-0.0.32 booked
- [ ] `docs/governance/` directory exists and contains other governance-companion documents (e.g. trust-doctrine.md, advisory-rules-audit.md) so the new catalog file fits the convention

**Existing Code:**

- [ ] Read at least two existing `docs/governance/<topic>.md` files end-to-end before authoring (so the catalog's structure matches local convention — section depth, code-block conventions, cross-link style)
- [ ] Read GHI #318 body and amendment in full — the failure-class analysis is verbatim source material
- [ ] Read ADR-0.0.21 § Decision — the chores promotion is example #2's source material

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #3 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] No code change → no unit-test red→green cycle. Documentation-only.
- [ ] `uv run gz validate --documents` passes after the new file lands
- [ ] `uv run gz lint` passes (markdownlint catches structural regressions in the new file)
- [ ] `uv run mkdocs build --strict` passes (catches broken cross-links to GHI numbers, ADR IDs, file paths)

### Code Quality

- [ ] Lint clean: `uv run gz lint`

### Gate 5: Human (Foundation lite — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz validate --documents
uv run mkdocs build --strict

test -f docs/governance/distribution_invariant_catalog.md

grep -q "GHI #318" docs/governance/distribution_invariant_catalog.md
grep -q "ADR-0.0.21" docs/governance/distribution_invariant_catalog.md
grep -q "ADR-0.0.32" docs/governance/distribution_invariant_catalog.md
grep -q "trust-doctrine" docs/governance/distribution_invariant_catalog.md
grep -ic "decision tree\|is this a t0 breach" docs/governance/distribution_invariant_catalog.md
```

## Acceptance Criteria

- [ ] REQ-0.0.31-03-01: `docs/governance/distribution_invariant_catalog.md` exists with the three required sections (cross-link to trust-doctrine, worked examples, decision tree)
- [ ] REQ-0.0.31-03-02: Worked example #1 covers GHI #318 self-hosting blindness with all four failure classes named and cross-linked to the OBPI-0.0.32-NN that closes each
- [ ] REQ-0.0.31-03-03: Worked example #2 covers the chores-promotion gap (ADR-0.0.21) framed as "T0 was operationally true before it was named"
- [ ] REQ-0.0.31-03-04: The decision tree answers "is this a T0 breach?" with concrete branches and concrete recovery actions (extend includes / baseline / validator / file GHI)
- [ ] REQ-0.0.31-03-05: The catalog forward-links to ADR-0.0.32 and back-links from trust-doctrine.md (the trust-doctrine page's "see also" entry must land if not already present from OBPI-0.0.31-01's edits)
- [ ] REQ-0.0.31-03-06: NO doctrine prose duplicates trust-doctrine.md; the catalog references and applies the doctrine
- [ ] REQ-0.0.31-03-07: Discoverability via runbook OR explicit decision to defer runbook update to a follow-up (with rationale recorded in this OBPI's Evidence)
- [ ] REQ-0.0.31-03-08: `uv run gz validate --documents` and `uv run mkdocs build --strict` both exit 0

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** Documentation-only; validation gates exit 0
- [ ] **Code Quality:** `gz lint` clean
- [ ] **Value Narrative:** T0 has worked examples and a decision tree; future canonical-surface promotions read this catalog before authoring
- [ ] **Key Proof:** `test -f docs/governance/distribution_invariant_catalog.md && grep -c "GHI #318\|ADR-0.0.21\|ADR-0.0.32" docs/governance/distribution_invariant_catalog.md` returns ≥3
- [ ] **OBPI Acceptance:** Evidence recorded below
- [ ] **Gate 5 (Foundation lite-lane brief-level human attestation):** Human witness recorded

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste `gz validate --documents`, `gz lint`, `mkdocs build --strict` output
```

### Code Quality

```text
# Paste `gz lint` output
```

### Gate 5 (Human)

```text
# Record attestation text here when ceremony fires
```

### Value Narrative

Before this OBPI: T0 is a doctrine paragraph in trust-doctrine.md. Future canonical-surface promotions can cite it but must reconstruct from scratch the question "is this a T0 breach?" against their specific surface. After this OBPI: the catalog is the operator-facing application surface — worked examples ground the abstract invariant, and the decision tree gives a checklist any surface promotion can apply during authoring. T0 graduates from doctrine-anyone-can-cite to checklist-anyone-can-apply.

### Key Proof


```bash
test -f docs/governance/distribution_invariant_catalog.md && \
  grep -c "GHI #318\|ADR-0.0.21\|ADR-0.0.32" docs/governance/distribution_invariant_catalog.md
# Output: 6 (all three required cross-references present, multiple times)
```

Validation gates (canonical attestation receipts):

- `arb-ruff-9a7d88b0f0734cec92250b74dc33750b` — lint clean
- `arb-step-typecheck-b505d8108cbe438fbaf089b2f25834f6` — typecheck clean
- `arb-step-unittest-77f8e533b6004704911fc64a9039a0b6` — 4648/4648 tests pass
- `uv run gz validate --documents` — exit 0
- `uv run mkdocs build --strict` — exit 0

REQ coverage waived via `--accept-uncovered` for all 8 REQs: documentation-only OBPI; no code/test surface; structural verification performed by `gz validate --documents`, `mkdocs build --strict`, and `gz lint`.

### Implementation Summary


- Files created: `docs/governance/distribution_invariant_catalog.md` (T0 failure-mode catalog with two worked examples and decision tree)
- Files modified: `docs/governance/trust-doctrine.md` ("See also" back-link to catalog in § T0); `docs/governance/governance_runbook.md` (T0 discoverability entry in § Layered trust)
- Tests added: n/a (documentation-only)
- Date completed: 2026-05-10
- Attestation status: Operator-attested via Stage 4 ceremony ("attest completed"); Gate 5 brief-level attestation required because parent ADR is kind: foundation
- Defects noted: Pre-existing `.gzkit/insights/agent-insights.jsonl:46` schema violation (type "observation" → "defect") fixed in-flight per PRIME DIRECTIVE; unrelated to this OBPI's scope

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — T0 failure-mode catalog landed at docs/governance/distribution_invariant_catalog.md with two worked examples (GHI #318 self-hosting blindness with classes A/B/C/D forward-linked to OBPI-0.0.32-{01..07}; ADR-0.0.21 chores-promotion gap framed as "T0 was operationally true before it was named") and the canonical "Is this a T0 breach?" four-branch decision tree; trust-doctrine.md § T0 gained the "See also" back-link to the catalog; governance_runbook.md § Layered trust gained the T0 discoverability entry; receipts arb-ruff-9a7d88b0f0734cec92250b74dc33750b (lint clean), arb-step-typecheck-b505d8108cbe438fbaf089b2f25834f6 (typecheck clean), arb-step-unittest-77f8e533b6004704911fc64a9039a0b6 (4648/4648 tests pass); uv run gz validate --documents exit 0; uv run mkdocs build --strict exit 0; pre-existing .gzkit/insights/agent-insights.jsonl:46 schema violation fixed in-flight per PRIME DIRECTIVE.
- Date: 2026-05-10

---

**Brief Status:** Completed

**Date Completed:** 2026-05-10

**Evidence Hash:** -
