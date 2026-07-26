---
id: OBPI-0.0.48-02-candidate-cognitive-pass
parent: ADR-0.0.48-gz-adr-pool-triage
item: 2
lane: Heavy
status: Draft
allowlist:
- src/gzkit/pool/cognitive_pass.py
- src/gzkit/schemas/pool_triage_rank_input.json
- docs/governance/pool-triage-cognitive-pass.md
- tests/test_pool_cognitive_pass.py
- tests/fixtures/pool_cognitive_pass/
- docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/obpis/OBPI-0.0.48-02-candidate-cognitive-pass.md
reqs:
- REQ-0.0.48-02-01
- REQ-0.0.48-02-02
- REQ-0.0.48-02-03
- REQ-0.0.48-02-04
- REQ-0.0.48-02-05
- REQ-0.0.48-02-06
verification:
- uv run gz validate --documents
- uv run gz lint
- uv run gz typecheck
- uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_pool_cognitive_pass
- uv run python -c "from gzkit.pool.cognitive_pass import PoolTriageRankInputEntry; PoolTriageRankInputEntry(id='ADR-pool.x', severity='urgent')"
- uv run python -m json.tool tests/fixtures/pool_cognitive_pass/golden_rank_input.json
- uv run python -c "from gzkit.pool.cognitive_pass import PoolTriageRankInputEntry; import json; print(json.dumps(PoolTriageRankInputEntry.model_json_schema(), indent=2))"
---

# OBPI-0.0.48-02-candidate-cognitive-pass: **candidate-cognitive-pass** — Author the skill's read-each-candidate procedure, requiring Intent and Decision review before structural-only rank input is produced; includes port/adapter reclassification check that flags foundation-appropriate pool items.

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/ADR-0.0.48-gz-adr-pool-triage.md`
- **Checklist Item:** #2 - "OBPI-0.0.48-02: **candidate-cognitive-pass** — Author the skill's read-each-candidate procedure, requiring Intent and Decision review before structural-only rank input is produced; includes port/adapter reclassification check that flags foundation-appropriate pool items."

**Status:** Draft

## Objective

**candidate-cognitive-pass** — Author the skill's read-each-candidate procedure, requiring Intent and Decision review before structural-only rank input is produced; includes port/adapter reclassification check that flags foundation-appropriate pool items.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/pool/cognitive_pass.py` — port/adapter classifier + structural-only rank-input emitter; Pydantic model `PoolTriageRankInputEntry`
- `src/gzkit/schemas/pool_triage_rank_input.json` — JSON schema for the structural-only `{id, severity}` rank-input contract
- `docs/governance/pool-triage-cognitive-pass.md` — procedural document the OBPI-05 skill body includes verbatim (read-each-candidate + Intent/Decision pin + port/adapter reclassification rule)
- `tests/test_pool_cognitive_pass.py` — REQ-derived tests covering rank-input shape, severity enumeration, reclassification surface, and structural-only constraint
- `tests/fixtures/pool_cognitive_pass/` — fixture pool ADR set + golden rank-input + golden reclassification annotation
- `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/obpis/OBPI-0.0.48-02-candidate-cognitive-pass.md` — this brief (evidence updates only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.gzkit/skills/pool-triage/SKILL.md` — skill body is OBPI-0.0.48-05's surface (this OBPI's docs/governance file is included by reference, not edited here)
- `src/gzkit/pool/triage_prepass.py` — prepass record set is OBPI-0.0.48-01's surface
- `src/gzkit/pool/triage_renderer.py` — markdown rendering is OBPI-0.0.48-03's surface
- `src/gzkit/pool/blocked_foundation.py` — blocked-foundation cross-check is OBPI-0.0.48-04's surface
- Edits to any pool ADR file under `docs/design/adr/pool/**` — the cognitive pass is read-only over the corpus
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `PoolTriageRankInputEntry` MUST be a frozen Pydantic `BaseModel` with `extra="forbid"` and MUST expose exactly two fields: `id: str` and `severity: Literal["urgent", "next-quarter", "latent"]` (ADR § Step 2 structural-only schema, mirroring `ghi-triage` round-3 hardening per GHI #424).
2. REQUIREMENT: The cognitive-pass procedure MUST require reading the candidate ADR's § Intent AND § Decision sections before emitting any rank-input entry — encoded as a STOP-guarded checklist in `docs/governance/pool-triage-cognitive-pass.md`.
3. REQUIREMENT: The port/adapter reclassification check MUST flag any candidate whose scope authors an invariant or prerequisite without which downstream features cannot exist (ADR § Step 2 "port/adapter reclassification check"); flagged candidates are emitted as `{id, reclassify: "foundation"}` in a separate annotation list, NOT as a rank-input entry.
4. REQUIREMENT: Reclassified candidates MUST NOT appear in the promotion-rank list under any code path — the rank-input list and the reclassification annotation list are mutually exclusive.
5. NEVER: Emit prose narrative, rationale, or per-entry justification fields in rank-input — the structural-only schema is the deliverable (GHI #424 round-3 hardening).
6. NEVER: Mutate any pool ADR file during cognitive-pass execution — the pass is read-only over the ADR corpus.
7. ALWAYS: Validate every emitted rank-input record against `src/gzkit/schemas/pool_triage_rank_input.json` before returning from the cognitive pass.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.


## Creates these files

<!-- Net-new files this OBPI creates. Path existence is exempt for these entries per GHI #419. -->

- `src/gzkit/pool/cognitive_pass.py` **CREATE**
- `src/gzkit/schemas/pool_triage_rank_input.json` **CREATE**
- `docs/governance/pool-triage-cognitive-pass.md` **CREATE**
- `tests/test_pool_cognitive_pass.py` **CREATE**
- `tests/fixtures/pool_cognitive_pass/` **CREATE**

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/ADR-0.0.48-gz-adr-pool-triage.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/ADR-0.0.48-gz-adr-pool-triage.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/**`
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
     yielded. The yielded product belongs in the `## Demo` section below. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_pool_cognitive_pass

# OBPI-specific surface checks
test -f src/gzkit/pool/cognitive_pass.py
test -f src/gzkit/schemas/pool_triage_rank_input.json
test -f docs/governance/pool-triage-cognitive-pass.md
uv run python -c "from gzkit.pool.cognitive_pass import PoolTriageRankInputEntry; PoolTriageRankInputEntry(id='ADR-pool.x', severity='urgent')"
uv run python -m json.tool tests/fixtures/pool_cognitive_pass/golden_rank_input.json

# Verify schema dual matches Pydantic model emission
uv run python -c "from gzkit.pool.cognitive_pass import PoolTriageRankInputEntry; import json; print(json.dumps(PoolTriageRankInputEntry.model_json_schema(), indent=2))"
# Compare emitted schema to src/gzkit/schemas/pool_triage_rank_input.json (must match)
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Run the cognitive pass against a fixture pool corpus; emit structural-only rank-input
uv run python -m gzkit.pool.cognitive_pass --pool-root tests/fixtures/pool_cognitive_pass --format json | jq '.rank_input'

# Inspect port/adapter reclassification annotations on a corpus with one foundation-shaped pool ADR
uv run python -m gzkit.pool.cognitive_pass --pool-root tests/fixtures/pool_cognitive_pass --format json | jq '.reclassify_foundation'

# Verify no prose narrative leaks into rank-input (structural-only enforcement)
uv run python -m gzkit.pool.cognitive_pass --pool-root tests/fixtures/pool_cognitive_pass --format json | jq '.rank_input[0] | keys'
# Expected output: ["id", "severity"]
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.48-02-01: Given `PoolTriageRankInputEntry`, when an entry is constructed with `severity="urgent"`/`"next-quarter"`/`"latent"`, then construction succeeds; any other severity value raises `ValidationError` (Literal enforcement).
- [ ] REQ-0.0.48-02-02: Given a rank-input entry, when extra fields like `rationale` or `why` are passed, then `extra="forbid"` raises `ValidationError` — the structural-only contract is fail-closed.
- [ ] REQ-0.0.48-02-03: Given a fixture candidate ADR whose scope authors an invariant (port-shape), when the cognitive pass runs, then the candidate appears in `reclassify_foundation` annotation list with `{id, reclassify: "foundation"}` AND does NOT appear in the rank-input list (mutual exclusion).
- [ ] REQ-0.0.48-02-04: Given the procedural document `docs/governance/pool-triage-cognitive-pass.md`, when it is read, then it includes a STOP-guarded Intent + Decision pre-read checklist and is referenced verbatim from the OBPI-05 skill body.
- [ ] REQ-0.0.48-02-05: Given the JSON schema `src/gzkit/schemas/pool_triage_rank_input.json`, when a Pydantic-emitted rank-input record is validated against it, then validation succeeds — schema/model drift fail-closes the test suite.
- [ ] REQ-0.0.48-02-06: Given the cognitive pass is invoked, when execution completes, then no file under `docs/design/adr/pool/**` has been modified — read-only invariant.

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
