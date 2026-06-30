---
id: OBPI-0.30.0-02-okf-bundle-generator
parent: ADR-0.30.0-okf-documentation-knowledge-structure
item: 2
lane: heavy
status: Completed
# req_atomic — each REQ is one indivisible unit of labor with no sub-REQ
# subdivision: all four REQs (REQ-01 emit index+concept docs, REQ-02
# progressive-disclosure links, REQ-03 source immutability, REQ-04 idempotency)
# are satisfied by the single `generate_bundle` function authored as one
# coherent TDD change and proven by one test module. None subdivided into
# seq=02+; the pipeline-minted seq=01-per-REQ buckets are the true labor shape.
req_atomic:
  - REQ-0.30.0-02-01
  - REQ-0.30.0-02-02
  - REQ-0.30.0-02-03
  - REQ-0.30.0-02-04
---

# OBPI-0.30.0-02-okf-bundle-generator: Generate an OKF-conformant knowledge bundle (root `index.md`, concept docs, directory `index.md` progressive disclosure, markdown-link edges) over the tracer slice; source docs preserved canonical.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md`
- **Checklist Item:** #2 — "OKF bundle generator: produce a root index.md plus concept docs over the tracer slice (state doctrine, trust doctrine, agent-contract rationale, active campaign reference), with directory index.md progressive disclosure and markdown-link edges; source docs preserved canonical."

**Status:** Completed

## Objective

Deliver the generator that emits a small, OKF-conformant markdown bundle over the tracer slice — a root `index.md`, one concept document per tracer-slice source doc (each carrying OKF frontmatter built from OBPI-0.30.0-01's model), directory `index.md` files for progressive disclosure, and markdown links as graph edges — WITHOUT modifying any source document.

## Lane

**Heavy** — This OBPI adds a generation engine that produces a runtime artifact (the OKF bundle) consumed by agents and validated by OBPI-0.30.0-03. The generation behavior is a runtime contract.

> Heavy is reserved for command/API/schema/runtime-contract changes.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md` — parent ADR for intent and scope
- `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/obpis/OBPI-0.30.0-02-okf-bundle-generator.md` — this brief
- `src/gzkit/knowledge/` — the bundle generator (consumes the OBPI-01 model) **CREATE**
- `.gzkit/governance/knowledge/` — DOMAIN-named OKF bundle output root for the governance tracer slice (named by knowledge domain, NEVER by the OKF format; OKF-conformance is a property of the files, not the folder name). A dedicated sub-root under `.gzkit/governance/` that keeps the generated bundle cleanly SEPARATE from the pre-existing `.gzkit/governance/ontology.json` / `ontology.schema.json` in the parent dir (operator-ratified, 2026-06-28). Generated, additive; OUTSIDE the mkdocs `docs_dir`. The generator writes its reserved files (`index.md`, `log.md`) and concept docs here; the only authored file expected in this sub-root is OBPI-06's `content-boundary.md` (an authored concept node), which the generator MUST NOT clobber. **CREATE**
- `tests/` — REQ-derived unittest cases for generator output shape and idempotency
- `src/gzkit/knowledge/generate.py` — delivered bundle generator (concrete file under the package above; product-proof artifact)
- `tests/knowledge/test_bundle_generator.py` — delivered REQ-derived generator output/idempotency tests (concrete file)

## Denied Paths

- Paths not listed in Allowed Paths
- `docs/governance/state-doctrine.md`, `docs/governance/trust-doctrine.md`, `docs/governance/agent-contract-rationale.md`, and the active campaign reference — READ-ONLY source docs; the generator reads them, NEVER edits them (source docs stay canonical)
- `src/gzkit/governance/trust_audits/`, `src/gzkit/commands/`, `src/gzkit/cli/` — validator (OBPI-03) and CLI (OBPI-04) scopes
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The generator MUST emit a root `index.md` plus one concept document per tracer-slice source doc (state doctrine, trust doctrine, agent-contract rationale, active campaign reference), each with OKF frontmatter validated by the OBPI-0.30.0-01 model.
2. REQUIREMENT: The bundle MUST provide progressive disclosure via directory `index.md` files and MUST connect concepts to their source docs with markdown links (graph edges), using the `resource` frontmatter and/or body links to point at the canonical source doc.
3. REQUIREMENT: The generator MUST NOT modify any source document — source docs remain byte-unchanged after generation (generated-and-additive).
4. REQUIREMENT: Generation MUST be idempotent — re-running over unchanged sources MUST yield a byte-identical bundle (no nondeterministic ordering or timestamps that churn the output).
5. NEVER: The generated bundle MUST NOT be consumed as enforcement evidence by any `gz validate` / gates / closeout surface (parent ADR Boundary Invariant 1).
6. ALWAYS: Tests are derived from the REQs above, not from a run of the implementation.

> SCOPE BOUNDARY: The frontmatter model is OBPI-0.30.0-01's scope; this OBPI consumes it. Conformance validation is OBPI-0.30.0-03's scope; the CLI entry point is OBPI-0.30.0-04's scope.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the Implementation Summary: "a root index.md, concept documents with YAML frontmatter ..., directory index.md files for progressive disclosure, and markdown links as graph edges ... Source docs are preserved as the canonical authored documents — the bundle is generated over them, never replacing them."
- [ ] Parent ADR § Intent — the why-frame (agents traverse instead of whole-corpus reads).
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `docs/governance/okf-cms-knowledge-structure-note-2026-06-23.md` § Tracer Bullet — the exact tracer-slice contents and bundle shape
- [ ] `docs/governance/state-doctrine.md` — generated bundle is Layer-3, never source-of-truth
- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract

**Context:**

- [ ] OBPI-0.30.0-01 (consumed model) — the frontmatter contract this generator emits

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists: `src/gzkit/knowledge/` with the OBPI-0.30.0-01 concept-frontmatter model
- [ ] Required path exists: each tracer-slice source doc (`docs/governance/state-doctrine.md`, `docs/governance/trust-doctrine.md`, `docs/governance/agent-contract-rationale.md`, active campaign reference)

**Existing Code (understand current state):**

- [ ] Existing generator/rendering pattern in `src/gzkit/` reviewed for deterministic-output conventions
- [ ] Confirm the active campaign reference path before wiring it as a tracer-slice source

## Quality Gates

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict` (generated bundle lives OUTSIDE `docs_dir`; the published-site build is unaffected)

### Gate 4: BDD (Heavy only)

- [ ] Generator output shape and idempotency covered by direct unit tests; the operator-facing generate/refresh smoke is OBPI-0.30.0-04's behave scope

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.knowledge.test_bundle_generator -v
```

## Demo

```bash
# Generate the bundle, then re-generate: the second run is byte-identical (idempotent)
uv run python -m gzkit.knowledge
uv run python -m gzkit.knowledge
# Inspect the emitted OKF root index and a concept doc
cat .gzkit/governance/knowledge/index.md
cat .gzkit/governance/knowledge/state-doctrine.md
```

## Acceptance Criteria

- [ ] REQ-0.30.0-02-01 [BEHAVIOR]: Given the tracer slice, when the generator runs, then a root `index.md` and one OKF concept document per tracer-slice source doc exist, each with frontmatter that the OBPI-0.30.0-01 model validates.
- [ ] REQ-0.30.0-02-02 [BEHAVIOR]: Given the generated bundle, when its structure is inspected, then directory `index.md` progressive-disclosure files exist and each concept document links to its canonical source doc (markdown-link / `resource` edge).
- [ ] REQ-0.30.0-02-03 [BEHAVIOR]: Given the tracer-slice source docs, when the generator runs, then no source document is modified (source docs are byte-unchanged).
- [ ] REQ-0.30.0-02-04 [BEHAVIOR]: Given unchanged sources, when the generator runs twice, then the second bundle is byte-identical to the first (idempotent generation).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

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
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# Generator covered by direct unit tests; behave smoke is OBPI-04
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before this OBPI there is a typed model but nothing that produces a bundle — an agent still has to read whole source docs. After this OBPI a generated OKF bundle exists over the tracer slice: a root index, typed concept docs, directory indexes for progressive disclosure, and links back to the canonical sources. The bundle is generated-and-additive (sources untouched) and idempotent (re-runnable without churn), so it is safe to regenerate as sources evolve.

### Key Proof


`python -m gzkit.knowledge` run twice yields a byte-identical .gzkit/governance/knowledge/ bundle (hash 919e97f98ebd0d330eb467a7c08efa06697c63ba15a2f8f0a1b6fef626077961); `git diff` shows zero change to the four tracer-slice source docs (state-doctrine, trust-doctrine, agent-contract-rationale, active-campaign). Each concept doc carries OKF frontmatter (type=doctrine) with a `resource` edge to its canonical source; the root index.md (type=index) links each concept for progressive disclosure. Independently reproduced by a Codex adversary, which also proved both load-bearing tests are non-tautological (injected regressions forced FAIL). Receipt arb-step-unittest-6d9affbf8b834b67b8923b16bcbe5d5a (exit_status 0); covers parity 4/4.

### Implementation Summary


- Files created: src/gzkit/knowledge/generate.py (generate_bundle + TRACER_SLICE + BUNDLE_OUTPUT); src/gzkit/knowledge/__main__.py (warning-free `python -m gzkit.knowledge` entry); tests/knowledge/test_bundle_generator.py (4 @covers REQ tests).
- Files modified: src/gzkit/knowledge/__init__.py (exports generate_bundle); this brief (Demo/Key-Proof command amended to `python -m gzkit.knowledge`).
- Generated artifact: .gzkit/governance/knowledge/ (root index.md + 4 concept docs over the governance tracer slice).
- Parent ADR Decision item implemented: "a root index.md, concept documents with YAML frontmatter, directory index.md files for progressive disclosure, and markdown links as graph edges ... Source docs are preserved as the canonical authored documents."
- TDD: verified assertion-level RED (NotImplementedError, not import error) before GREEN; two-stage independent review (spec PASS, quality PASS_WITH_CONCERNS) plus a Codex adversarial pass.
- Quality-review correction: relocated module entry from a generate.py __main__ block to __main__.py, eliminating a RuntimeWarning on the documented demo command.
- req_atomic declared: all 4 REQs satisfied by the single generate_bundle function; no sub-REQ labor subdivision.
- Tests added: REQ-0.30.0-02-01,02,03,04 BEHAVIOR cases (@covers).
- Date completed: 2026-06-29. Attestation: g0 (Heavy lane Gate 5).

## Tracked Defects

- Bundle-root domain naming and coexistence — RESOLVED (operator-ratified, 2026-06-28). Per the OKF spec, bundles are DOMAIN-named (never format-named); the governance tracer slice homes at the dedicated sub-root `.gzkit/governance/knowledge/`, kept cleanly separate from the pre-existing `.gzkit/governance/ontology.json` / `ontology.schema.json` in the parent dir. The generator writes its reserved files + concept docs there and MUST NOT clobber OBPI-06's authored `content-boundary.md`.
- CLI verb name — RESOLVED (operator-ratified, 2026-06-28): the verb is the `knowledge` subcommand (`generate`/`refresh`), matching the domain-named `src/gzkit/knowledge/` package. The `--okf-conformance` validator flag is unchanged — it names the OKF standard the bundle is checked against, not a namespace.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OKF bundle generator landed Heavy lane: 4/4 REQ-derived @covers tests green (receipt arb-step-unittest-6d9affbf8b834b67b8923b16bcbe5d5a), ruff/typecheck/mkdocs clean (arb-ruff-dc533074a46a4b159eca8f26e37fe388, arb-step-typecheck-d660ff0718bf4ab7b28398c3d0a9f264, arb-step-mkdocs-12e45120565b4451a408b3e5576204ab), covers parity 4/4 (100%). Idempotent bundle hash 919e97f98ebd0d330eb467a7c08efa06697c63ba15a2f8f0a1b6fef626077961 independently reproduced by a Codex adversary (verdict REFUTED-WITH-CAVEATS; core REQs not refuted, caveat resolved to expected pipeline state).
- Date: 2026-06-29

---

**Date Completed:** 2026-06-29

**Evidence Hash:** -
