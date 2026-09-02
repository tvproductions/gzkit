---
id: OBPI-0.35.0-13-render-order-truncation-survival
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 13
lane: Heavy
status: Draft
allowlist:
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md
  - AGENTS.md
  - data/agents_md_survival_declaration.json
  - AGENTS.md
  - src/gzkit/templates/agents.md
  - src/gzkit/templates/adr.md
  - src/gzkit/sync_surfaces.py
reqs:
  - REQ-0.35.0-13-01
  - REQ-0.35.0-13-02
  - REQ-0.35.0-13-03
verification:
  - test -f docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md
  - rg -n "^## Persona$" AGENTS.md
  - test -f data/agents_md_survival_declaration.json
  - test -f src/gzkit/templates/agents.md
  - test -f src/gzkit/templates/adr.md
  - test -f src/gzkit/sync_surfaces.py
---

# OBPI-0.35.0-13-render-order-truncation-survival: Render Order Truncation Survival

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #13 - "Render-order permutation for truncation survival -- order `AGENTS.md` sections so every rank at or above `must_survive_through_rank` renders before the consuming vendor's project-doc byte cap; ranking source is the ratified `data/agents_md_survival_declaration.json`, never inferred criticality. Absorbed from `ADR-pool.render-order-truncation-survival` by operator ruling 2026-09-02 (GHI #815)"

**Status:** Draft

## Objective

Render-order permutation for truncation survival -- order `AGENTS.md` sections so every rank at or above `must_survive_through_rank` renders before the consuming vendor's project-doc byte cap; ranking source is the ratified `data/agents_md_survival_declaration.json`, never inferred criticality. Absorbed from `ADR-pool.render-order-truncation-survival` by operator ruling 2026-09-02 (GHI #815).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- Verified against on-disk reality 2026-09-02 per gz-obpi-specify
     § Pre-Save Ground-Truth Check. Every path below was globbed; the
     pool ADR's stale `markdown_parser.py` reference resolves to
     `src/gzkit/content/parse/markdown_parser.py`, not `content/`. -->

- `src/gzkit/content/render/pipeline.py` — the render surface the permutation applies at
- `src/gzkit/content/models/agent_contract.py` — `Pillar.order` (line 18, `"Render order (ascending)."`)
- `src/gzkit/content/parse/markdown_parser.py` — builds one `Pillar` per `##` section "in document order" (line 295)
- `data/agents_md_survival_declaration.json` — the ratified ranking source (read-only here; ranks are operator policy)
- `AGENTS.md` — the Layer-1 surface being permuted
- `tests/content/test_render_pipeline.py` — render-order coverage
- `tests/content/test_round_trip_agent_contract.py` — round-trip fidelity coverage
- `tests/content/test_byte_stability.py` — verbatim-preservation coverage
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-13-render-order-truncation-survival.md` — this brief

## Denied Paths

- `src/gzkit/governance/trust_audits/surface_delivery_witness.py` — the witness LANDED under GHI #712 and is the independent check on this work. Editing the instrument that grades the change is the failure this brief must not commit.
- `data/vendor-manifest.json` — the cap is gzkit's belief about a vendor's physical truncation; raising it cannot relieve the cap and would fake the result.
- `.gzkit/corpus/AGENTS.md.jsonl` — permutation reorders; it never adds, removes, or edits a corpus entry.
- `src/gzkit/templates/agents.md` — the adopter-bootstrap template is a different surface from the rendered root contract.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The ranking source is `data/agents_md_survival_declaration.json`. NEVER infer criticality from `Bullet.classification` / `Bullet.witness` — that was built, measured and REFUTED 2026-07-24: run live it pushed § Attestation 15->18 and § Defect-fix routing 16->19 (the two sections GHI #580 was filed to lift) and demoted PRIME DIRECTIVE 3->9. Root cause: those are `Bullet` fields and gzkit's most binding material is TABLES, which rank 0.
2. REQUIREMENT: Do NOT repurpose `Pillar.order` as a criticality field. It carries DOCUMENT order for round-trip fidelity. The permutation MUST renumber `order` to match the new document order so round-trip parity still holds, per the field's own contract (`"Render order (ascending)."`).
3. REQUIREMENT: The permutation is ORDER-ONLY. Every section's text MUST survive byte-identical — no trim, no rewrite, no merge. A reorder that changes a byte is a different operation with a different attestation disposition.
4. REQUIREMENT: The recomposed `AGENTS.md` and its rendition MUST be committed TOGETHER. `gz validate --invariant-coherence` byte-compares deterministic rendition playback against the committed surface and is in the default `gz check` scope, so a surface committed without its rendition fails closed.
5. REQUIREMENT: After permutation, `uv run gz validate --instructions-files-budget` MUST report ZERO must-survive sections straddling or past the codex cap. Measured 2026-09-01 before the change: 11,768 B undelivered (`operator-doctrine-verbatim-canon` straddling, losing 11,173 B; `architectural-boundaries` lost entire).
6. NEVER: edit the surface-delivery witness or the vendor cap to obtain a green reading. Both are in Denied Paths.
7. ALWAYS: treat this as a Layer-1 canon change. An agent silently reordering the canon it is governed by is the failure gzkit exists to prevent (pool ADR constraint 2).

> **OPEN OPERATOR QUESTION — do not resolve in-flight (Behavior Rules — Always #9).**
> `ADR-pool.render-order-truncation-survival` constraint 2 requires operator Gate-5
> attestation through the recompose ceremony. The attestation-granularity ruling of
> 2026-08-17 says verbatim *"a rerender of unhanged canon does not require my
> attestation"* (spelling preserved), and an order-only permutation preserves every
> entry verbatim — which reads as disposition (1), or at most (4) *"trims and
> compressions ... might invite a review"*. The two point different ways. Surface it
> and let the operator rule; do NOT pick one.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- [ ] Required path exists or is intentionally created in this OBPI: `AGENTS.md`
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
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md
rg -n "^## Persona$" AGENTS.md
test -f data/agents_md_survival_declaration.json
test -f src/gzkit/templates/agents.md
test -f src/gzkit/templates/adr.md
test -f src/gzkit/sync_surfaces.py
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Replace with concrete product demonstrations for this OBPI.
```

## Acceptance Criteria

<!-- REQ kinds per ADR-0.0.59; enforced by gz validate --req-kind-discipline. -->

- [ ] REQ-0.35.0-13-01 [BEHAVIOR]: Given the ratified survival declaration, when the render pipeline emits `AGENTS.md`, then sections are ordered by declared rank ascending, ranks at or above `must_survive_through_rank` first, and ties keep document order via a stable sort
- [ ] REQ-0.35.0-13-02 [BEHAVIOR]: Given a permuted surface, when `Pillar.order` is read back, then it has been renumbered to match the new document order, so a parse/render round trip reproduces the committed surface byte-for-byte
- [ ] REQ-0.35.0-13-03 [BEHAVIOR]: Given any section, when the surface is permuted, then that section's text is byte-identical before and after — the permutation reorders and never rewrites
- [ ] REQ-0.35.0-13-04 [BEHAVIOR]: Given the permuted `AGENTS.md`, when the surface-delivery witness runs, then it reports zero must-survive sections straddling or past the codex delivery cap
- [ ] REQ-0.35.0-13-05 [SUPPORT]: `data/agents_md_survival_declaration.json` is the sole ranking source and is read, never written, by this OBPI — `gz validate --instructions-files-budget` + `artifact_edited` event
- [ ] REQ-0.35.0-13-06 [STRUCTURAL-FENCE]: `Pillar.order` remains document order and is never repurposed as a criticality axis — audited at ADR closeout against § Boundary Invariants

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
