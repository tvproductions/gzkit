---
id: OBPI-0.35.0-13-render-order-truncation-survival
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 13
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/content/render/order.py
  - src/gzkit/content/composer.py
  - tests/content/test_render_order.py
  - tests/content/test_composer.py
  - tests/content/test_round_trip_agent_contract.py
  - tests/content/test_byte_stability.py
  - features/render_order.feature
  - features/steps/render_order_steps.py
  - .gzkit/renditions/AGENTS.md/
  - AGENTS.md
  - docs/user/manpages/content.md
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-13-render-order-truncation-survival.md
reqs:
  - REQ-0.35.0-13-01
  - REQ-0.35.0-13-02
  - REQ-0.35.0-13-03
  - REQ-0.35.0-13-04
  - REQ-0.35.0-13-05
  - REQ-0.35.0-13-06
verification:
  - uv run -m unittest tests.content.test_render_order tests.content.test_composer tests.content.test_round_trip_agent_contract tests.content.test_byte_stability
  - uv run -m behave features/render_order.feature
  - uv run gz validate --instructions-files-budget --invariant-coherence --rendition-freshness
  - uv run gz validate --documents --req-kind-discipline
  - uv run mkdocs build --strict
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

- `src/gzkit/content/render/order.py` — **CREATE**, following adjacent render/test/BDD modules
- `src/gzkit/content/composer.py`
- `tests/content/test_render_order.py` — **CREATE**, following adjacent render/test/BDD modules
- `tests/content/test_composer.py`
- `tests/content/test_round_trip_agent_contract.py`
- `tests/content/test_byte_stability.py`
- `features/render_order.feature` — **CREATE**, following adjacent render/test/BDD modules
- `features/steps/render_order_steps.py` — **CREATE**, following adjacent render/test/BDD modules
- `.gzkit/renditions/AGENTS.md/` — governed publication/playback only; never manual authoring
- `AGENTS.md` — governed publication/playback only; never manual authoring
- `docs/user/manpages/content.md`
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-13-render-order-truncation-survival.md`

## Denied Paths

- `src/gzkit/governance/trust_audits/surface_delivery_witness.py` — the witness LANDED under GHI #712 and is the independent check on this work. Editing the instrument that grades the change is the failure this brief must not commit.
- `data/vendor-manifest.json`, `.codex/config.toml` — read-only configuration inputs for this order-only unit. Codex project_doc_max_bytes is configurable, including trusted project configuration; changing the budget is legitimate but is not this unit's mechanism.
- `data/agents_md_survival_declaration.json` — read-only ratified ranks; no policy edits
- `src/gzkit/content/models/agent_contract.py`, `src/gzkit/content/parse/markdown_parser.py` — consume document-order metadata without redefining it
- `.gzkit/corpus/AGENTS.md.jsonl` — permutation reorders; it never adds, removes, or edits a corpus entry.
- `src/gzkit/templates/agents.md` — the adopter-bootstrap template is a different surface from the rendered root contract.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The ranking source is `data/agents_md_survival_declaration.json`. NEVER infer criticality from `Bullet.classification` / `Bullet.witness` — that was built, measured and REFUTED 2026-07-24: run live it pushed § Attestation 15->18 and § Defect-fix routing 16->19 (the two sections GHI #580 was filed to lift) and demoted PRIME DIRECTIVE 3->9. Root cause: those are `Bullet` fields and gzkit's most binding material is TABLES, which rank 0.
2. REQUIREMENT: Do NOT repurpose `Pillar.order` as a criticality field. It carries DOCUMENT order for round-trip fidelity. After the byte permutation, parsing derives order from the new document position. Never sort by an invented criticality value in Pillar.order, and never claim the existing model parser preserves arbitrary raw bytes.
3. REQUIREMENT: The permutation is ORDER-ONLY. Every section's text MUST survive byte-identical — no trim, no rewrite, no merge. A reorder that changes a byte is a different operation with a different attestation disposition.
4. REQUIREMENT: The recomposed `AGENTS.md` and its rendition MUST be committed TOGETHER. `gz validate --invariant-coherence` byte-compares deterministic rendition playback against the committed surface and is in the default `gz check` scope, so a surface committed without its rendition fails closed.
5. REQUIREMENT: After permutation, `uv run gz validate --instructions-files-budget` MUST report ZERO must-survive sections straddling or past the codex cap. Measured 2026-09-01 before the change: 11,768 B undelivered (`operator-doctrine-verbatim-canon` straddling, losing 11,173 B; `architectural-boundaries` lost entire).
6. NEVER modify the independent witness or the declared/configured budget during the order-only comparison. Record the current configured budget and its observed delivery evidence; use no hardcoded 32768-byte requirement.
7. ALWAYS: treat this as a Layer-1 canon change. An agent silently reordering the canon it is governed by is the failure gzkit exists to prevent (pool ADR constraint 2).

> **RULED 2026-09-02 — OPERATOR GATE-5 ATTESTATION IS REQUIRED for this permutation.**
> The question below was surfaced and is now closed; it is retained as the record of
> what was weighed. `ADR-pool.render-order-truncation-survival` constraint 2 requires
> operator Gate-5 attestation through the recompose ceremony. The attestation-
> granularity ruling of 2026-08-17 says verbatim *"a rerender of unhanged canon does
> not require my attestation"* (spelling preserved), and an order-only permutation
> preserves every entry verbatim — which reads as disposition (1), or at most (4)
> *"trims and compressions ... might invite a review"*. The two point different ways,
> and the operator ruled constraint 2 governs.
>
> The ground for the ruling, recorded so it is not re-argued: the granularity ruling
> partitions on whether **what canon IS** changes, and disposition (4) attaches review
> to a trim precisely because it *"changes what canon LOOKS like without changing what
> canon IS"*. An order-only permutation changes neither — but its whole PURPOSE is to
> change which canon is **delivered** under the codex cap, and undelivered canon is not
> in force. Changing the in-force governing set for a vendor is a stronger claim than
> either disposition (1) or (4) contemplates, so it takes the attestation constraint 2
> already specified. Recorded, not drawn: no lock, no pipeline marker, no TASK, no
> dispatch (IRON LAW — only the operator initiates OBPI work).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Lossless Ordering Contract

Dependencies: 05/06/07 provide candidate generation, lineage verification and governed
landing; 09 supplies root playback. This item hooks the pure generator immediately before
lineage offsets are computed, so later generation and landing preserve the approved order.
It introduces no alternate CLI writer and leaves ordinary adopter/model rendering alone.

The helper in content/render/order.py accepts raw UTF-8 surface bytes and the validated
survival declaration. It preserves the H1/preamble and moves complete H2 spans, including
their trailing whitespace and delimiters. Consume the fence-aware shared boundary iterator delivered by 05 so ownership, generation
and permutation agree. Example headings inside fences never become sections. Reuse the
existing section-id vocabulary and reject duplicate ids.
Do not parse and re-render through AgentContract to perform the permutation: the current
parser strips trailing blanks and special-cases Tech Stack/Rules. Renumbered Pillar.order
is a derived observation after parsing, not the mechanism that preserves text.

The current declaration uses unique contiguous ranks. Validate its exact membership against
the surface before ordering; do not infer a rank for a new section or mutate the declaration.
Apply ascending rank order and retain all bytes, even expendable-under-pressure sections.
With no declaration, preserve the existing order. An existing but invalid declaration fails.
Reject malformed UTF-8 and preserve multibyte sequences without byte/character confusion.

Before publication, compute must-survive end offsets including the preamble. If any exceed
the recorded current budget, show the exact residual and refuse to claim survival; policy or
budget changes require their own authorized correction. Exact-boundary fixtures pass.
Keep the independent delivery-witness implementation unchanged and compare its actual
findings, including a deliberately infeasible cap fixture. Repeat generation and playback
must remain coherent with the committed rendition and its lineage/provenance.

The approved permutation is prepared and verified in isolated acceptance fixtures first.
The September 2 operator ruling below still governs real publication: present the exact
per-section before/after hashes and byte offsets for human approval, then use governed
landing/playback and commit the rendition and AGENTS.md together. Do not mutate corpus entries.

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

- [ ] Read the ratified survival declaration and agents-md-map-doctrine.md; verify current configured budget and record observed delivery evidence

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- [ ] Required path exists or is intentionally created in this OBPI: `AGENTS.md`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Read content/render/pipeline.py and its template iteration; changing Pillar.order alone does not sort the list
- [ ] Read content/parse/markdown_parser.py and content/ownership.py for section ids, fence behavior and normalization limits
- [ ] Read content/composer.py and the landed 05/06/07 generation/lineage/publication interfaces
- [ ] Read tests/content/test_render_pipeline.py, test_round_trip_agent_contract.py and test_byte_stability.py
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

The new tests and feature are implementation deliverables. Budget findings are advisory;
exit 0 alone is not survival proof. Assert the witness's actual per-section offsets and
must-survive loss count, with a too-small-cap negative control.

```bash
uv run -m unittest tests.content.test_render_order tests.content.test_composer tests.content.test_round_trip_agent_contract tests.content.test_byte_stability
uv run -m behave features/render_order.feature
uv run gz validate --instructions-files-budget --invariant-coherence --rendition-freshness
uv run gz validate --documents --req-kind-discipline
uv run mkdocs build --strict
```

## Demo

Run these after governed permutation/publication; retain the witness's before/after section
readout rather than reporting its exit status alone.

```bash
uv run gz validate --instructions-files-budget --json
uv run gz validate --invariant-coherence --rendition-freshness
uv run -m behave features/render_order.feature
```

## Acceptance Criteria

<!-- REQ kinds per ADR-0.0.59; enforced by gz validate --req-kind-discipline. -->

- [ ] REQ-0.35.0-13-01 [BEHAVIOR]: Given the ratified survival declaration, when the render pipeline emits `AGENTS.md`, then sections are ordered by declared rank ascending, numeric ranks <= `must_survive_through_rank` first; declaration identity and contiguous unique-rank validation fail before publication for duplicate, unknown, omitted or dangling section ids
- [ ] REQ-0.35.0-13-02 [BEHAVIOR]: Given a permuted surface, when `Pillar.order` is read back, then it matches the new document position; governed rendition playback is byte-identical to the approved surface, including repeated generation, without asserting that the lossy model parser itself preserves arbitrary bytes
- [ ] REQ-0.35.0-13-03 [BEHAVIOR]: Given any section, when the surface is permuted, then that section's text is byte-identical before and after — the permutation reorders and never rewrites
- [ ] REQ-0.35.0-13-04 [BEHAVIOR]: Given the permuted `AGENTS.md`, when the surface-delivery witness runs, then its measured byte offsets show every must-survive section ending at or before the recorded configured cap; a too-small-cap fixture reports residual loss and refuses publication rather than trimming text or changing policy
- [ ] REQ-0.35.0-13-05 [SUPPORT]: `docs/user/manpages/content.md` documents the read-only ranking source, configurable budget, infeasible-order refusal and governed publication flow. Witnessed by `artifact_edited` citing `docs/user/manpages/content.md` + `gz validate --documents`.
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
