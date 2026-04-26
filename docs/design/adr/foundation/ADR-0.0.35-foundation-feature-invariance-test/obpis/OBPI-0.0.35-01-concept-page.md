---
id: OBPI-0.0.35-01-concept-page
parent: ADR-0.0.35-foundation-feature-invariance-test
item: 1
lane: Lite
status: Draft
---

# OBPI-0.0.35-01-concept-page: Foundation/Feature Invariance Test — Concept Page

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.35-foundation-feature-invariance-test/ADR-0.0.35-foundation-feature-invariance-test.md`
- **Checklist Item:** #1 — "Concept page authoring — `docs/user/concepts/foundation-feature-invariance-test.md` as canonical reference (verbatim test, hexagonal-ports lens, both worked examples, anti-pattern), bidirectional cross-link with ADR-0.0.18's concepts page, `docs/user/index.md` integration, runbook navigation entry. Parallel-root."

**Status:** Draft

## Objective

Author `docs/user/concepts/foundation-feature-invariance-test.md` as the canonical operator-facing reference for kind classification: states the invariance test verbatim, presents the hexagonal-ports lens as the structural cue with port-vs-plug definitions, lands both worked examples (ledger discipline vs. backend; ADR-0.0.33/0.0.34 paired foundations), names the "feels foundational" anti-pattern, and integrates bidirectionally into the existing concept-page surface (`adr-taxonomy.md` cross-link, `index.md` navigation, mkdocs nav, runbook entry).

## Lane

**Lite** — Pure documentation work. No CLI/schema/runtime-contract change. Foundation-kind rigor still applies at brief-level Gate 5 attestation per AGENTS.md § OBPI Acceptance Protocol (parent ADR-0.0.35 is foundation-kind).

## Allowed Paths

- `docs/user/concepts/foundation-feature-invariance-test.md` — new concept page (the canonical artifact)
- `docs/user/concepts/adr-taxonomy.md` — back-link addition only (one cross-reference paragraph or "see also" tail entry)
- `docs/user/index.md` — concept-section index entry for the new page
- `docs/user/runbook.md` — navigation/cross-reference entry where kind classification is discussed
- `mkdocs.yml` — nav entry insertion under the existing `Concepts:` block

## Denied Paths

- `src/**` — no source code change
- `tests/**` — no test surface (concept-page authoring; mkdocs --strict is the verification gate)
- `.gzkit/skills/**`, `.claude/skills/**`, `.github/skills/**` — skill prompt enrichment is OBPI-02's scope
- `src/gzkit/templates/**` — foundation-ADR scaffolding template is OBPI-03's scope
- `src/gzkit/governance/trust_audits.py` — `gz validate --kind-invariance` validator is OBPI-04's scope
- `docs/design/adr/foundation/ADR-0.0.35-*/ADR-0.0.35-*.md` — parent ADR; read for intent, do not edit
- `docs/design/adr/foundation/ADR-0.0.18-*/**` — referenced for cross-link only; do not amend ADR-0.0.18 (its body is Validated)
- All other ADR/OBPI files

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT — verbatim test.** The concept page MUST quote the invariance test verbatim: *"Foundation = without it, we wouldn't be doing the project."* The quoted form is the canonical phrasing; rewording or summarizing is a defect.
2. **REQUIREMENT — hexagonal-ports lens.** The concept page MUST present the hexagonal-ports lens with explicit port-vs-plug definitions: ports point to invariance (the abstract contract; foundation work); plugs are concrete implementations behind a port (specific capability; feature work).
3. **REQUIREMENT — ledger worked example.** The concept page MUST land the ledger discipline (foundation) vs. ledger storage backend (feature) worked example with both sides explicitly classified.
4. **REQUIREMENT — paired-foundations worked example.** The concept page MUST land ADR-0.0.33 (Agent Control Surface Fidelity) and ADR-0.0.34 (Agent Control Surface Rendering Substrate) as paired foundations passing the test, with the invariance answer named for each.
5. **REQUIREMENT — anti-pattern named.** The concept page MUST name the anti-pattern *"classifying as foundation because it feels foundational"* and supply the corrective: foundation is a test answer, not a vibe.
6. **REQUIREMENT — bidirectional cross-link with ADR-0.0.18 concept page.** `adr-taxonomy.md` MUST link forward to `foundation-feature-invariance-test.md`, and `foundation-feature-invariance-test.md` MUST link back to `adr-taxonomy.md`. Asymmetric linking is a defect.
7. **REQUIREMENT — discoverability via index and nav.** The concept page MUST be reachable from `docs/user/index.md` (concepts-section listing) and from `mkdocs.yml` nav (under the existing `Concepts:` block).
8. **REQUIREMENT — runbook cross-reference.** `docs/user/runbook.md` MUST cross-reference the new page wherever kind classification or `gz plan create --kind` is discussed.
9. **REQUIREMENT — mkdocs strict build clean.** `uv run mkdocs build --strict` MUST exit 0 against the new page; no broken links, no orphan files, no duplicate slugs.
10. **NEVER — amend ADR-0.0.18 body.** The parent-ADR Decision and the concept-page narrative explicitly forbid backward amendment to ADR-0.0.18. Adding a one-paragraph forward link/back-link in `adr-taxonomy.md` is permitted; editing ADR-0.0.18's frontmatter, Decision, or Consequences is forbidden.
11. **NEVER — re-litigate kind taxonomy vocabulary.** The kind names (`pool`, `foundation`, `feature`) are locked in ADR-0.0.17. The concept page applies the test against the existing taxonomy; it does not re-define the terms.

> STOP-on-BLOCKERS: if `docs/user/concepts/adr-taxonomy.md` is missing or `mkdocs.yml` does not have a `Concepts:` nav section, print BLOCKERS and halt — the integration target is the prerequisite, not optional.

## Discovery Checklist

**Parent ADR (read first; order pinned per GHI #321):**

- [ ] Quote ADR-0.0.35 § Decision item #1–#5 (verbatim test, hexagonal-ports lens, port/plug definitions) into Implementation Summary
- [ ] Read ADR-0.0.35 § Intent (the why-frame for the test)
- [ ] Read ADR-0.0.35 § Decision § "Worked example" subsections (the canonical examples this page lands)
- [ ] Read ADR-0.0.35 § Consequences (positive #1–#5; negative #1–#5)

> **STOP:** If you cannot quote the ADR-0.0.35 § Decision item #1 verbatim, STOP and re-read.

**Sibling concept page (read for convention):**

- [ ] Read `docs/user/concepts/adr-taxonomy.md` end-to-end — this is the ADR-0.0.18 concept page; the new page mirrors its structure (no frontmatter, prose-first, inline cross-links).
- [ ] Identify the natural cross-link insertion point in `adr-taxonomy.md` (likely a "see also" tail or a kind-decision section).

**Integration surfaces:**

- [ ] Read `docs/user/index.md` § Concepts section — identify where the new page slots in alphabetically/topically.
- [ ] Read `mkdocs.yml` lines 38-50 (`Concepts:` block) — confirm nav insertion shape matches sibling entries.
- [ ] Read `docs/user/runbook.md` — locate sections discussing kind classification (`gz plan create --kind`, foundation-vs-feature decision moments).

**Prerequisites (STOP if missing):**

- [ ] `docs/user/concepts/adr-taxonomy.md` exists and is the ADR-0.0.18 concept page.
- [ ] `mkdocs.yml` has a `Concepts:` nav block.
- [ ] `docs/user/index.md` has a concepts listing.

**Existing Code (understand current state):**

- [ ] `docs/user/concepts/adr-taxonomy.md` — read end-to-end; the new page mirrors its prose-first / no-frontmatter / inline-cross-link structure. Note the existing kind-decision section as a forward-link insertion point.
- [ ] `docs/user/concepts/lifecycle.md`, `docs/user/concepts/lanes.md`, `docs/user/concepts/gates.md` — sibling concept pages; confirm the canonical heading depth (H1 page title, H2 sections, H3 subsections) and "see also" tail convention.
- [ ] `mkdocs.yml` lines 38-50 (`Concepts:` block) — confirm nav entry shape: `- <Title>: user/concepts/<slug>.md`. Pick alphabetic-by-title slot for the new entry.
- [ ] `docs/user/index.md` — locate the concepts listing; confirm format and pick insertion slot.
- [ ] `docs/user/runbook.md` — `Grep` for `--kind`, `kind:`, `foundation`, `feature` to locate every existing kind-classification touchpoint where a cross-reference belongs.
- [ ] `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md` § Decision (read for the existing decision-guidance narrative the new test extends; do NOT edit).

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR § Decision item quoted in Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)

Documentation OBPI — no test tier. The semantic equivalent of Red-Green-Refactor is: identify required content (REQ-derived); author it; verify mkdocs --strict builds clean. The "test that fails first" is `mkdocs build --strict` against an unauthored page (broken link or missing nav entry); the "test that passes" is the same command after authoring lands.

- [ ] mkdocs --strict fails before page lands (the failing-state evidence)
- [ ] mkdocs --strict passes after page lands (the green-state evidence)

### Code Quality

- [ ] Lint clean: `uv run gz lint`

### Gate 3: Docs (Lite — applies because the deliverable IS docs)

- [ ] `uv run mkdocs build --strict` exits 0
- [ ] No broken cross-links between `adr-taxonomy.md` ↔ `foundation-feature-invariance-test.md`
- [ ] Page renders correctly in mkdocs serve (manual visual check)

### Gate 5: Human (Foundation-kind brief-level attestation)

- [ ] Foundation-kind parent → brief-level attestation required per AGENTS.md § OBPI Acceptance Protocol § Lane & Kind Attestation Matrix.
- [ ] Operator confirms verbatim test wording, both worked examples, and anti-pattern naming match the 2026-04-25 / 2026-04-26 session intent.

## Verification

```bash
# Page exists and contains the verbatim test
test -f docs/user/concepts/foundation-feature-invariance-test.md
grep -F "Foundation = without it, we wouldn't be doing the project" docs/user/concepts/foundation-feature-invariance-test.md

# Bidirectional cross-link
grep -F "foundation-feature-invariance-test" docs/user/concepts/adr-taxonomy.md
grep -F "adr-taxonomy" docs/user/concepts/foundation-feature-invariance-test.md

# Index and nav integration
grep -F "foundation-feature-invariance-test" docs/user/index.md
grep -F "foundation-feature-invariance-test" mkdocs.yml

# Runbook cross-reference
grep -F "foundation-feature-invariance-test" docs/user/runbook.md

# mkdocs strict clean
uv run mkdocs build --strict

# ARB receipts (foundation-kind brief-level attestation)
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb ruff
```

## Acceptance Criteria

- [ ] **REQ-0.0.35-01-01:** Given a fresh checkout, when an operator opens `docs/user/concepts/foundation-feature-invariance-test.md`, then the page contains the verbatim invariance test *"Foundation = without it, we wouldn't be doing the project"* exactly once and labels it as the binding rule.
- [ ] **REQ-0.0.35-01-02:** Given the concept page, when an operator reads the structural-cue section, then the hexagonal-ports lens is explained with explicit port-vs-plug definitions and a worked classification table mapping ports to foundation and plugs to feature.
- [ ] **REQ-0.0.35-01-03:** Given the concept page, when an operator reads the worked-examples section, then the ledger discipline vs. ledger storage backend example is presented with both sides explicitly classified, and the ADR-0.0.33/ADR-0.0.34 paired-foundations example is presented with the invariance answer named for each.
- [ ] **REQ-0.0.35-01-04:** Given the concept page, when an operator reads the anti-pattern section, then the *"feels foundational"* failure mode is named with its corrective ("foundation is a test answer, not a vibe").
- [ ] **REQ-0.0.35-01-05:** Given `docs/user/concepts/adr-taxonomy.md` and `docs/user/concepts/foundation-feature-invariance-test.md`, when an operator follows the cross-link from either page, then they reach the other; symmetric linking holds.
- [ ] **REQ-0.0.35-01-06:** Given `docs/user/index.md` and `mkdocs.yml`, when an operator browses the concepts listing or the mkdocs nav, then `foundation-feature-invariance-test.md` is reachable from both.
- [ ] **REQ-0.0.35-01-07:** Given `docs/user/runbook.md`, when an operator reads sections discussing kind classification, then a cross-reference to the new concept page is present at every such section.
- [ ] **REQ-0.0.35-01-08:** Given the full docs surface, when `uv run mkdocs build --strict` runs, then the build exits 0 with no broken links, no orphan files, and no duplicate slugs.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent § Decision quoted
- [ ] **Gate 2 (Doc-equivalent):** Failing-state mkdocs evidence captured before authoring; passing-state captured after
- [ ] **Code Quality:** Lint clean
- [ ] **Gate 3 (Docs):** mkdocs --strict ✓
- [ ] **Gate 5 (Human):** Foundation-kind brief-level attestation recorded
- [ ] **Value Narrative:** Recorded below
- [ ] **Key Proof:** One concrete classification example walked through with the test
- [ ] **OBPI Acceptance:** Evidence section populated

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (Doc-equivalent RGR)

```text
# Paste failing mkdocs --strict output (red) and passing output (green) here
```

### Code Quality

```text
# Paste lint output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here
```

### Gate 5 (Human)

```text
# Record foundation-kind brief-level attestation text here
```

### Value Narrative

Before this OBPI: adopters facing a foundation-vs-feature kind decision had ADR-0.0.18's heuristic ("does this shape app-system identity?") plus worked examples. The heuristic routes the typical case but leaves substrate-vs-port and doctrine-vs-tooling edges ambiguous. After this OBPI: the canonical concept page lands the invariance test as the one-line tiebreaker, paired with the hexagonal-ports lens, with both worked-example classes (substrate, paired-foundations) on the page; adopters get a deterministic resolution rule for the edge cases the heuristic alone leaves open.

### Key Proof

Walk-through example added inline on the page: an adopter faces *"should ledger storage backend selection be a foundation ADR or a feature ADR?"* and resolves it in one sentence by applying the invariance test (the project remains the project under either backend; storage is a plug; the ADR is feature).

### Implementation Summary

- Files created: `docs/user/concepts/foundation-feature-invariance-test.md`
- Files modified: `docs/user/concepts/adr-taxonomy.md`, `docs/user/index.md`, `mkdocs.yml`, `docs/user/runbook.md`
- Tests added: none (doc-only)
- Date completed: -
- Attestation status: -
- Defects noted: -

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` — required (foundation-kind parent)
- Attestation: -
- Date: -

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
