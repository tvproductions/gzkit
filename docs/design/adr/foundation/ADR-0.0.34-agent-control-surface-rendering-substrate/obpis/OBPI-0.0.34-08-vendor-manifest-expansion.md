---
id: OBPI-0.0.34-08-vendor-manifest-expansion
parent: ADR-0.0.34-agent-control-surface-rendering-substrate
item: 8
lane: Heavy
status: Draft
---

# OBPI-0.0.34-08-vendor-manifest-expansion: Vendor Manifest Expansion

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`
- **Checklist Item:** #8 - "OBPI-0.0.34-08: Vendor manifest expansion — extend ADR-0.16.0 OBPI-03 vendor manifest schema as the canonical declaration of which content types render to which vendor mirrors"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Vendor manifest expansion — extend ADR-0.16.0 OBPI-03 vendor manifest schema as the canonical declaration of which content types render to which vendor mirrors.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `data/vendor-manifest.json` — vendor manifest content (extend with `content_type_routes` block)
- `src/gzkit/schemas/vendor_manifest.json` — vendor manifest JSON Schema (extend with `content_type_routes` definition)
- `src/gzkit/content/vendors.py` — vendor routing helpers (load manifest, expose `routes_for(content_type) -> list[Vendor]`)
- `src/gzkit/content/render/pipeline.py` — read `content_type_routes` from manifest instead of hard-coded routing
- `src/gzkit/governance/trust_audits.py` — `gz validate --vendor-manifest` scope registration (modification, not creation)
- `tests/content/test_vendor_manifest.py` — schema validation, route enumeration, drift fail-closed
- `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/obpis/OBPI-0.0.34-08-vendor-manifest-expansion.md` — this brief

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: **Extend ADR-0.16.0 OBPI-03 vendor manifest schema.** Add a `content_type_routes` object mapping each registered content type → list of vendor mirror identifiers that receive its rendered output. Schema lives at `src/gzkit/schemas/vendor_manifest.json`; data lives at `data/vendor-manifest.json`.
2. REQUIREMENT: **Schema-validated manifest.** `data/vendor-manifest.json` MUST validate against `src/gzkit/schemas/vendor_manifest.json`; `gz validate --vendor-manifest` exits 3 on drift. Wire this scope into `src/gzkit/governance/trust_audits.py` alongside existing validators.
3. REQUIREMENT: **Consumed by OBPI-02 pipeline.** The render pipeline MUST read `content_type_routes` from the manifest and route accordingly; NEVER hard-code per-vendor branches in renderer or sync code.
4. REQUIREMENT: **Schema-only scope.** NEVER define new content types here (OBPI-01 owns the registry). NEVER define new vendors here (ADR-0.16.0 governs the vendor set). This OBPI extends the manifest's shape; content-type and vendor inventories are unchanged.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] **External prerequisite:** ADR-0.16.0 OBPI-03 vendor manifest schema must exist (seeded vendor manifest). This OBPI extends it; if missing, file a blocker GHI.
- [ ] **Soft co-dependency:** OBPI-0.0.34-01 (content model registry) — `content_type_routes` keys are the content-type names; may run in parallel but routes can only be validated end-to-end once OBPI-01 is complete.
- [ ] **Soft co-dependency:** OBPI-0.0.34-02 (rendering pipeline) — consumer of the manifest's `content_type_routes`. May land in either order; pipeline can ship with a minimal in-code routing fallback that this OBPI replaces.
- [ ] No downstream OBPIs in this ADR depend on OBPI-08 strictly — it can run early (alongside OBPI-01) or late.

**Prerequisites (check existence, STOP if missing):**

- [ ] `data/vendor-manifest.json` exists (ADR-0.16.0 OBPI-03 artifact).
- [ ] `src/gzkit/schemas/vendor_manifest.json` exists (ADR-0.16.0 OBPI-03 artifact).
- [ ] Parent ADR evidence artifacts referenced by this brief are present.

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
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run gz validate --vendor-manifest                                                # exits 0 on clean manifest
uv run python -c "import json; m = json.load(open('data/vendor-manifest.json')); assert 'content_type_routes' in m, sorted(m)"
uv run python -m unittest tests.content.test_vendor_manifest -v
# Render pipeline reads the manifest (not hard-coded vendors):
rg -q "content_type_routes" src/gzkit/content/render/pipeline.py
rg -n "vendor\s*==\s*['\"]claude['\"]" src/gzkit/content/render/ && exit 1 || true   # no hard-coded branches
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.34-08-01: Given `data/vendor-manifest.json`, when validated against `src/gzkit/schemas/vendor_manifest.json`, then validation passes; `gz validate --vendor-manifest` exits 0.
- [ ] REQ-0.0.34-08-02: Given the expanded manifest, when read by the render pipeline (OBPI-02), then each registered content type → vendor mirror routing is honored without per-vendor hard-coded branches in renderer or sync code (verified by `rg "vendor == 'claude'"` returning no matches in `src/gzkit/content/render/`).
- [ ] REQ-0.0.34-08-03: Given a new content type added in OBPI-01, when its `content_type_routes` entry is missing from the manifest, then `gz validate --vendor-manifest` exits non-zero naming the missing entry — coupled-surface coherence per AGENTS.md Invariant 1a.
- [ ] REQ-0.0.34-08-04: Given an existing vendor mirror set, when the manifest is reloaded, then the render pipeline's enumerated set of `(content_type, vendor)` pairs equals the manifest's declared routes (no implicit vendor expansion, no implicit drop).
- [ ] REQ-0.0.34-08-05: Given the test suite after this OBPI lands, when `tests/content/test_vendor_manifest.py` runs, then it covers: schema-clean case, manifest-drift fail-closed case, route enumeration round-trip.

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

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
