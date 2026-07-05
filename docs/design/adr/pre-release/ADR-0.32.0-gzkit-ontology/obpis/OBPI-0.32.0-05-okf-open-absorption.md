---
id: OBPI-0.32.0-05-okf-open-absorption
parent: ADR-0.32.0-gzkit-ontology
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.32.0-05-okf-open-absorption: OKF Open-Absorption

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md`
- **Checklist Item:** #5 - "OKF open-absorption: Doc subtype = OKF type verbatim, no subset-validator (honors OKF BI-1/BI-3), links_to edges kept."

**Status:** Draft

## Objective

Define how documentation `Doc` objects enter the gzkit ontology's corpus subgraph by open-absorption from the generated OKF bundle (ADR-0.30.0): each `Doc.subtype` is set to the source OKF `type` frontmatter value VERBATIM, `links_to` edges are built from the concept-doc markdown links, and NO subset-validator constrains the `type` set — preserving OKF Boundary Invariants BI-1 (no OKF frontmatter/link consumed as enforcement evidence) and BI-3 (unknown `type` values are not errors).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Heavy because it adds a new importable runtime surface — the OKF Doc-absorption path in `gzkit.ontology.okf` — whose emitted `Doc` node / `links_to` edge contract is bound against by OBPI-0.32.0-02's corpus projection and OBPI-0.32.0-03's gz ontology interface. No CLI verb or schema change lands here, but the absorption is a runtime interface other OBPIs consume, so the sibling-consistent lane is Heavy.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/ontology/okf.py` — **CREATE**: the Doc-ingestion path that reads the generated OKF bundle (`.gzkit/governance/knowledge/`) and emits `Doc` nodes (subtype = OKF `type` verbatim) + `links_to` edges from the concept-doc markdown links
- `tests/test_ontology_okf.py` — **CREATE**: `@covers`-decorated REQ tests (verbatim-subtype, unknown-type tolerance, links_to edges)
- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/obpis/OBPI-0.32.0-05-okf-open-absorption.md` — this brief (evidence writeback only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/knowledge/**` — the OKF bundle generator + `ConceptFrontmatter` model (ADR-0.30.0); read-only input, never regenerated or edited here
- `src/gzkit/governance/trust_audits/okf_conformance.py` — the `--okf-conformance` validator (ADR-0.30.0); untouched
- `src/gzkit/governance/trust_audits/**` — NO new validator scope; specifically no closed-set/subset check on `Doc.subtype` (the rejected alternative)
- `.gzkit/governance/knowledge/**` — the generated OKF bundle is READ-ONLY input; never written by this OBPI
- `src/gzkit/ontology/model.py` (OntologyNode/OntologyEdge/typed LinkType, OBPI-0.32.0-01) — the model is CONSUMED, never modified here
- `src/gzkit/ontology/corpus.py` (corpus projection, OBPI-0.32.0-02) — consumed via its Doc-admission surface; its internals are not modified here
- `src/gzkit/commands/**`, `src/gzkit/cli/**` — no CLI verb here (that is OBPI-0.32.0-03, the gz ontology interface)
- `src/gzkit/schemas/**` — no schema change (the ontology schema is OBPI-0.32.0-01)
- Paths not listed in Allowed Paths
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS: Set `Doc.subtype` to the source OKF concept doc's `type` frontmatter value VERBATIM — no normalization, no lowercasing, no mapping to a closed set.
2. NEVER: Add a subset-validator or any closed-set membership check constraining `Doc.subtype` to an enumerated OKF `type` set — a closed-set check breaches OKF BI-3 and breaks shipped OKF v0.30.0.
3. NEVER: Consume any OKF `type`, tag, description, or markdown link as enforcement evidence in a `gz validate` scope, gate, or closeout step — the absorption path only populates the derived Tier-B ontology, honoring OKF BI-1 and ADR-0.32.0 Boundary Invariant #5.
4. NEVER: Edit the OKF generator (`src/gzkit/knowledge/**`), the `--okf-conformance` validator, the ontology model (OBPI-0.32.0-01), the corpus projection internals (OBPI-0.32.0-02), or add a CLI verb (OBPI-0.32.0-03).
5. ALWAYS: Build `links_to` edges from the OKF concept-doc markdown links, reading the generated bundle at `.gzkit/governance/knowledge/` READ-ONLY.
6. ALWAYS: Reconcile this brief against the parent ADR § Decision (the OKF open-absorption clause) before implementation; quote it verbatim into `### Implementation Summary`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision OKF open-absorption clause** quoted verbatim into `### Implementation Summary`: "Docs are absorbed via OKF open-absorption: Doc subtype = OKF type verbatim, NO subset-validator (a closed-set check would breach OKF BI-1/BI-3), links_to edges kept." The Decision clause is the contract; everything else hangs off it.
- [ ] Parent ADR § Boundary Invariants entry #5 ("OKF absorption stays open") — the STRUCTURAL-FENCE anchor REQ-04/REQ-05 audit against.
- [ ] Parent ADR § Intent + § Alternatives Considered — the "OKF subset-validator ... REJECTED" rationale is the why-frame for REQ-05.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**OKF fences (read; these are the fences this OBPI must honor — ADR-0.30.0):**

- [ ] ADR-0.30.0 § Boundary Invariants BI-1 (no OKF frontmatter/link consumed as enforcement evidence) and BI-3 (unknown fields / unknown `type` values are NOT errors).

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] OBPI-0.32.0-01 (model: `Doc` node / `links_to` LinkType) and OBPI-0.32.0-02 (corpus projection admitting Doc nodes) — the surfaces this path emits into.

**Prerequisites (STOP if missing):**

- [ ] `src/gzkit/ontology/` package exists — created by OBPI-0.32.0-01 (model) + OBPI-0.32.0-02 (corpus projection); this OBPI lands `okf.py` as a sibling.
- [ ] `OntologyNode`/`OntologyEdge` and a `links_to` `LinkType` are importable from the ontology model (OBPI-0.32.0-01).
- [ ] The corpus-domain projection admits `Doc` nodes (OBPI-0.32.0-02).
- [ ] The generated OKF bundle exists at `.gzkit/governance/knowledge/` — regenerate via the `gz knowledge` generator (ADR-0.30.0) if absent.

**Existing Code (read; do NOT modify — this is the input this OBPI absorbs):**

- [ ] `src/gzkit/knowledge/generate.py` — the OKF bundle generator; concept-doc shape is `type` frontmatter + a `Canonical source: [name](link)` markdown-link edge. This is the exact input this absorption reads.
- [ ] `src/gzkit/knowledge/concept_frontmatter.py` — `ConceptFrontmatter` (required `type`, free-form, unknown-field-tolerant); the verbatim `type` this OBPI maps to `Doc.subtype`.
- [ ] `src/gzkit/schemas/okf_concept_frontmatter.json` — `type` is the ONLY required field, `additionalProperties: true`, `type` is a free string (NOT an enum): the schema proof that a closed subset-validator is illegal.
- [ ] `src/gzkit/governance/trust_audits/okf_conformance.py` — the generated-bundle-only `--okf-conformance` validator; establishes the OKF-side fence, NOT modified here.

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
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_ontology_okf -v
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo.

     API names below are the intended surface; the exact signatures are
     implementation-defined, but the observed behavior is pinned by the REQs. -->

```bash
# Absorb the generated OKF bundle into Doc nodes; subtype echoes the OKF `type` verbatim.
uv run python -c "from gzkit.ontology.okf import absorb_okf_bundle; nodes, edges = absorb_okf_bundle('.gzkit/governance/knowledge'); print([(n.id, n.subtype) for n in nodes])"

# An arbitrary, never-registered OKF `type` is tolerated (OKF BI-3) — no rejection; subtype kept verbatim.
uv run python -c "from gzkit.ontology.okf import doc_from_concept; d = doc_from_concept({'type': 'never-registered-type'}, 'docs/x.md'); print('subtype:', d.subtype)"

# links_to edges are built from the concept-doc markdown links.
uv run python -c "from gzkit.ontology.okf import absorb_okf_bundle; nodes, edges = absorb_okf_bundle('.gzkit/governance/knowledge'); print([(e.src, e.link_type, e.dst) for e in edges if e.link_type == 'links_to'])"
```

## Acceptance Criteria

<!-- Each REQ carries exactly one [kind] tag (ADR-0.0.59): BEHAVIOR proves via a
     @covers test, STRUCTURAL-FENCE via the parent ADR ## Boundary Invariants
     entry, SUPPORT via a ledger event + structural validator. -->

- [ ] REQ-0.32.0-05-01 [BEHAVIOR]: The OKF absorption path sets a `Doc` node's `subtype` to the source OKF concept doc's `type` frontmatter value VERBATIM — byte-for-byte, no normalization or mapping — pinned by a `@covers(REQ-0.32.0-05-01)` test in `tests/test_ontology_okf.py` that ingests a bundle concept doc of a known `type` and asserts `Doc.subtype` equals it exactly.
- [ ] REQ-0.32.0-05-02 [BEHAVIOR]: Ingesting an OKF concept doc whose `type` is an arbitrary, never-registered string produces a `Doc` node and raises no error — the absorption path holds no closed `type` set and rejects nothing, honoring OKF (ADR-0.30.0) Boundary Invariant BI-3 (unknown `type` values are NOT errors) — pinned by a `@covers(REQ-0.32.0-05-02)` test asserting the tolerated `Doc.subtype` is carried verbatim.
- [ ] REQ-0.32.0-05-03 [BEHAVIOR]: For every markdown link in an ingested OKF concept doc body, the absorption path emits a `links_to` `OntologyEdge` from the `Doc` node to the link target — pinned by a `@covers(REQ-0.32.0-05-03)` test that ingests a concept doc carrying a known markdown link (its `Canonical source:` edge) and asserts the corresponding `links_to` edge is present in the emitted edge set.
- [ ] REQ-0.32.0-05-04 [STRUCTURAL-FENCE]: The absorption path reads OKF `type` and OKF markdown links ONLY to populate the derived Tier-B ontology (`Doc.subtype`, `links_to` edges); no OKF `type`, tag, description, or link is consumed as enforcement evidence by any `gz validate` scope, gate, or closeout step — preserving OKF (ADR-0.30.0) Boundary Invariant BI-1 and honoring ADR-0.32.0 Boundary Invariant #5. Anchored in the parent ADR `## Boundary Invariants` (entry #5, "OKF absorption stays open").
- [ ] REQ-0.32.0-05-05 [STRUCTURAL-FENCE]: No subset-validator — no closed-set membership check constraining `Doc.subtype` to an enumerated OKF `type` set — is added anywhere by this OBPI (the rejected alternative: a closed-set check would breach OKF BI-1/BI-3 and break shipped OKF v0.30.0). Anchored in the parent ADR `## Boundary Invariants` (entry #5) and its "OKF subset-validator ... REJECTED" alternative.
- [ ] REQ-0.32.0-05-06 [SUPPORT]: This brief's `### Implementation Summary` quotes the parent ADR § Decision OKF open-absorption clause verbatim (Requirements (FAIL-CLOSED) reconciliation item 6) — proven by `uv run gz validate --documents` passing AND an `artifact_edited` ledger event citing this brief file emitted at OBPI completion.

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
