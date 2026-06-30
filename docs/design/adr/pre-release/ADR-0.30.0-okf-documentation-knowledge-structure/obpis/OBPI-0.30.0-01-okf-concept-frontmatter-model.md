---
id: OBPI-0.30.0-01-okf-concept-frontmatter-model
parent: ADR-0.30.0-okf-documentation-knowledge-structure
item: 1
lane: heavy
status: Completed
# req_atomic — each REQ is one indivisible unit of labor with no sub-REQ
# subdivision: REQ-01 (the ConceptFrontmatter field set), REQ-02 (the
# required/non-empty rejection rule), REQ-03 (the extra="allow" posture config),
# and REQ-04 (the JSON schema mirror file) were authored as one coherent change
# proven by a single test module. None was subdivided into seq=02+; the
# pipeline-minted seq=01-per-REQ buckets are the true labor shape.
req_atomic:
  - REQ-0.30.0-01-01
  - REQ-0.30.0-01-02
  - REQ-0.30.0-01-03
  - REQ-0.30.0-01-04
---

# OBPI-0.30.0-01-okf-concept-frontmatter-model: OKF concept-frontmatter Pydantic model + JSON schema (required `type`; optional title/description/resource/tags/timestamp), unknown-field- and unknown-type-tolerant per the OKF posture.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md`
- **Checklist Item:** #1 — "OKF schema + frontmatter model: Pydantic model for OKF concept frontmatter (required `type`, optional title/description/resource/tags/timestamp), unknown-field- and unknown-type-tolerant per OKF posture; JSON schema under src/gzkit/schemas/."

**Status:** Completed

## Objective

Deliver the typed contract every other OBPI in this ADR depends on: a Pydantic model for OKF concept-document frontmatter with a single required field (`type`) and optional `title`/`description`/`resource`/`tags`/`timestamp`, that PRESERVES the OKF posture — unknown frontmatter fields are accepted and unknown `type` values are accepted, neither is an error — plus a JSON schema mirror under `src/gzkit/schemas/`.

## Lane

**Heavy** — This OBPI adds a new schema/runtime-contract surface (a Pydantic model + a JSON schema under `src/gzkit/schemas/`) that downstream OBPIs and the validator consume.

> Heavy is reserved for command/API/schema/runtime-contract changes. A new schema is a runtime contract.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md` — parent ADR for intent and scope
- `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/obpis/OBPI-0.30.0-01-okf-concept-frontmatter-model.md` — this brief (evidence + ceremony updates)
- `src/gzkit/knowledge/` — new OKF package home for the concept-frontmatter model (Pydantic; the named-models departure, ADR-0.0.15) **CREATE**
- `src/gzkit/schemas/` — new OKF concept-frontmatter JSON schema file
- `tests/` — REQ-derived unittest cases for the model and posture tolerance
- `src/gzkit/knowledge/concept_frontmatter.py` — delivered Pydantic concept-frontmatter model (concrete file under the package above)
- `src/gzkit/schemas/okf_concept_frontmatter.json` — delivered JSON schema mirror (concrete product-proof artifact)
- `tests/knowledge/test_concept_frontmatter_model.py` — delivered REQ-derived model/posture tests (concrete file)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/governance/trust_audits/` — the `--okf-conformance` validator is OBPI-0.30.0-03's scope
- `src/gzkit/commands/`, `src/gzkit/cli/` — the OKF CLI (`okf` subcommand) is OBPI-0.30.0-04's scope
- Any consumer that would treat OKF frontmatter as enforcement evidence (STRUCTURAL-FENCE, Boundary Invariant 1)
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The model MUST require exactly one field, `type` (non-empty string); a frontmatter mapping missing `type` or with an empty `type` MUST fail validation.
2. REQUIREMENT: The model MUST accept the optional fields `title`, `description`, `resource`, `tags`, `timestamp` when present, and MUST validate a document carrying ONLY `type`.
3. REQUIREMENT: The model MUST preserve the OKF posture — it MUST accept unknown frontmatter fields (producer-defined keys) AND any unknown `type` value without error. `type` is a free string, NOT a closed enum.
4. REQUIREMENT: A JSON schema mirror of the model MUST exist under `src/gzkit/schemas/` and validate clean against the project's schema-loading path.
5. NEVER: The model MUST NOT be consumed as enforcement evidence by any `gz validate` / gates / closeout surface (parent ADR Boundary Invariant 1).
6. ALWAYS: Tests are derived from the REQs above, not from a run of the implementation (`.gzkit/rules/tests.md` § "Tests assert semantics, not strings").

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the Implementation Summary: "concept documents with YAML frontmatter carrying a required `type` and optional `title`/`description`/`resource`/`tags`/`timestamp` ... consumers MUST preserve the OKF posture: unknown fields and unknown `type` values are NOT errors."
- [ ] Parent ADR § Boundary Invariants — invariant 3 (posture tolerance) is the contract this model encodes.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/models.md` — Pydantic is the named-models departure; how models are shaped here
- [ ] An existing `src/gzkit/schemas/*.json` reviewed as the schema pattern
- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR (OBPI-0.30.0-02 consumes this model; OBPI-0.30.0-03 validates against it)

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists: `src/gzkit/schemas/` (schema home)
- [ ] Parent ADR present and registered

**Existing Code (understand current state):**

- [ ] Existing Pydantic model + JSON schema pair reviewed for local conventions (`extra=` posture, schema-loading path)
- [ ] Confirm the OKF posture is `extra="allow"` (or equivalent), NOT `extra="forbid"`

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

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Schema documented where schemas are catalogued

### Gate 4: BDD (Heavy only)

- [ ] Schema/model surface covered by direct unit tests; no new `.feature` required (no operator-facing CLI in this OBPI)

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.knowledge.test_concept_frontmatter_model -v
```

## Demo

```bash
# A document carrying only `type` validates; unknown fields and unknown type are tolerated
uv run python -c "from gzkit.knowledge import ConceptFrontmatter; print(ConceptFrontmatter(type='doctrine', novel_key='x').type)"

# A document missing `type` is rejected
uv run python -c "from gzkit.knowledge import ConceptFrontmatter; ConceptFrontmatter(title='no type')" ; echo "exit=$?"
```

## Acceptance Criteria

- [ ] REQ-0.30.0-01-01 [BEHAVIOR]: Given a frontmatter mapping with a non-empty `type` and no other fields, when parsed by the OKF concept-frontmatter model, then it validates successfully and exposes `type`.
- [ ] REQ-0.30.0-01-02 [BEHAVIOR]: Given a frontmatter mapping missing `type` (or with an empty-string `type`), when parsed, then validation fails.
- [ ] REQ-0.30.0-01-03 [BEHAVIOR]: Given a frontmatter mapping carrying an unknown producer-defined field AND an unrecognized `type` value, when parsed, then it validates successfully (OKF posture: unknown fields and unknown `type` values are NOT errors) — per parent ADR Boundary Invariant 3.
- [ ] REQ-0.30.0-01-04 [SUPPORT]: A JSON schema mirror exists under `src/gzkit/schemas/` and loads/validates clean — proven by `uv run gz validate --documents` passing AND an `artifact_edited` ledger event citing the new schema file emitted at OBPI completion.

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
# Schema/model covered by direct unit tests; no behave run required
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before this OBPI there is no typed contract for an OKF concept document — every downstream consumer would have to re-implement frontmatter parsing and re-decide the posture (tolerant vs strict). After this OBPI, a single Pydantic model + JSON schema fixes the contract: `type` required, the rest optional, unknown fields and unknown `type` values tolerated. The generator (OBPI-02) and the validator (OBPI-03) build on this one source of truth.

### Key Proof


Posture tolerance (Boundary Invariant 3):
  $ uv run python -c "from gzkit.knowledge import ConceptFrontmatter as C; m=C(type='made-up-doctype', producer_key='x'); print(m.type, m.model_dump()['producer_key'])"
  made-up-doctype x
Required `type` bites: `ConceptFrontmatter()` raises ValidationError.
Full suite: 6623/6623 pass — receipt arb-step-unittest-fa47848991e2499a9886ef41324b771a (exit_status=0).
REQ→@covers parity: behavior_uncovered_reqs=0; gz validate --req-kind-discipline PASS.

### Implementation Summary


- Implements parent ADR Decision item: concept documents with YAML frontmatter carrying a required `type` and optional `title`/`description`/`resource`/`tags`/`timestamp`; consumers preserve the OKF posture (unknown fields and unknown `type` values are NOT errors).
- Files created: `src/gzkit/knowledge/__init__.py` + `concept_frontmatter.py` (the `ConceptFrontmatter` Pydantic model, frozen, `extra="allow"`); `src/gzkit/schemas/okf_concept_frontmatter.json` (schema mirror, `additionalProperties: true`, `required: ["type"]`, `type.minLength: 1`); `tests/knowledge/test_concept_frontmatter_model.py` (6 REQ-derived tests).
- Posture (parent ADR Boundary Invariant 3) encoded as `extra="allow"` + free-string `type` — a documented, ADR-mandated departure from the `.gzkit/rules/models.md` `extra="forbid"` default.
- STRUCTURAL-FENCE (Boundary Invariant 1): the model is data-only; rg-verified zero enforcement-path (validate/gates/closeout/trust_audits) consumers.
- Tests: REQ-0.30.0-01-01/02/03 BEHAVIOR via `@covers`; REQ-0.30.0-01-04 SUPPORT via ledger + `gz validate --documents` structural validator (no `@covers`, per ADR-0.0.59); `req_atomic:` declared (each REQ is one indivisible labor unit).
- Date completed: 2026-06-29. Attestation: operator g0, "attest completed".

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.30.0-01 OKF concept-frontmatter model (src/gzkit/knowledge/) + JSON schema mirror (src/gzkit/schemas/okf_concept_frontmatter.json); full suite 6623/6623 pass (receipt arb-step-unittest-fa47848991e2499a9886ef41324b771a), ruff clean (arb-ruff-23ecd85ba439495f8969250eab390ad1), typecheck clean (arb-step-typecheck-cad9089bd03240148ffba256d26b6d79), mkdocs --strict clean (arb-step-mkdocs-ff4d26b550364c28bdabf53687a614c2), gz validate --documents + --req-kind-discipline pass; 3 BEHAVIOR REQs @covers-covered + REQ-04 SUPPORT via ledger+structural validator (behavior_uncovered_reqs=0); STRUCTURAL-FENCE verified zero enforcement-path consumers; dual adversarial validation (Claude fallback + Codex preferred different-vendor), all real findings fixed.
- Date: 2026-06-29

---

**Date Completed:** 2026-06-29

**Evidence Hash:** -
