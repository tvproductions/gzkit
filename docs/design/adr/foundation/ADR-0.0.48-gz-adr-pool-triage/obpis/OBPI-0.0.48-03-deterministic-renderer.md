---
id: OBPI-0.0.48-03-deterministic-renderer
parent: ADR-0.0.48-gz-adr-pool-triage
item: 3
lane: Heavy
status: Draft
allowlist:
- src/gzkit/pool/triage_renderer.py
- tests/test_pool_triage_renderer.py
- tests/fixtures/pool_triage_renderer/inputs/
- tests/fixtures/pool_triage_renderer/golden/
- docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/obpis/OBPI-0.0.48-03-deterministic-renderer.md
reqs:
- REQ-0.0.48-03-01
- REQ-0.0.48-03-02
- REQ-0.0.48-03-03
- REQ-0.0.48-03-04
- REQ-0.0.48-03-05
- REQ-0.0.48-03-06
verification:
- uv run gz validate --documents
- uv run gz lint
- uv run gz typecheck
- uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_pool_triage_renderer
- uv run python -m gzkit.pool.triage_renderer --input "$fx"
---

# OBPI-0.0.48-03-deterministic-renderer: **deterministic-renderer** — Implement the deterministic markdown renderer for the ranked promotion recommendation deliverable.

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/ADR-0.0.48-gz-adr-pool-triage.md`
- **Checklist Item:** #3 - "OBPI-0.0.48-03: **deterministic-renderer** — Implement the deterministic markdown renderer for the ranked promotion recommendation deliverable."

**Status:** Draft

## Objective

**deterministic-renderer** — Implement the deterministic markdown renderer for the ranked promotion recommendation deliverable.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/pool/triage_renderer.py` — pure-function renderer that takes a validated rank-input list and returns a deterministic markdown deliverable
- `tests/test_pool_triage_renderer.py` — REQ-derived tests covering determinism (same input → same output), section ordering, and reclassification surfacing
- `tests/fixtures/pool_triage_renderer/inputs/` — fixture rank-input JSON files (urgent-only, mixed-severity, reclassify-only, empty)
- `tests/fixtures/pool_triage_renderer/golden/` — golden markdown output files paired byte-for-byte with each fixture input
- `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/obpis/OBPI-0.0.48-03-deterministic-renderer.md` — this brief (evidence updates only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/pool/triage_prepass.py` — prepass record set is OBPI-0.0.48-01's surface
- `src/gzkit/pool/cognitive_pass.py` — rank-input emitter is OBPI-0.0.48-02's surface
- `src/gzkit/pool/blocked_foundation.py` — filter logic is OBPI-0.0.48-04's surface
- `.gzkit/skills/pool-triage/**` — skill body is OBPI-0.0.48-05's surface
- `docs/user/manpages/**` — manpage authoring is OBPI-0.0.48-06's surface
- Edits to any pool ADR file under `docs/design/adr/pool/**` — the renderer is a pure transform over JSON
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `render_pool_triage(rank_input: list[PoolTriageRankInputEntry], reclassify: list[dict]) -> str` MUST be a pure function — identical inputs MUST produce byte-identical output across runs, processes, and platforms.
2. REQUIREMENT: The renderer MUST emit three severity sections in fixed order — `## Urgent`, `## Next Quarter`, `## Latent` — and a final `## Reclassify as Foundation` section when the reclassify list is non-empty (omitted entirely when empty).
3. REQUIREMENT: Within each severity section, entries MUST be ordered lexicographically by `id` — never by any agent-supplied ordering — to preserve determinism under set-shuffled inputs.
4. REQUIREMENT: A `## Blocked on Foundation` annotation section MUST be reserved in the renderer's contract for OBPI-04's filter output (renderer accepts the optional list; emits the section when populated).
5. NEVER: Embed timestamps, run-IDs, hostnames, or any non-input-derived content in the rendered output — the renderer is deterministic per ADR § Step 3.
6. NEVER: Invoke subprocess, network, or filesystem reads inside the renderer — it is a pure transform from JSON input to markdown string.
7. ALWAYS: Validate the rank-input list against `src/gzkit/schemas/pool_triage_rank_input.json` (OBPI-02's contract) before rendering; reject malformed inputs with explicit Pydantic `ValidationError`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.


## Creates these files

<!-- Net-new files this OBPI creates. Path existence is exempt for these entries per GHI #419. -->

- `src/gzkit/pool/triage_renderer.py` **CREATE**
- `tests/test_pool_triage_renderer.py` **CREATE**
- `tests/fixtures/pool_triage_renderer/inputs/` **CREATE**
- `tests/fixtures/pool_triage_renderer/golden/` **CREATE**

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
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_pool_triage_renderer

# OBPI-specific surface checks
test -f src/gzkit/pool/triage_renderer.py
# >= 4 fixtures
ls tests/fixtures/pool_triage_renderer/inputs/
# paired golden files
ls tests/fixtures/pool_triage_renderer/golden/

# Determinism check — the renderer is pure; identical input yields byte-identical
# output (asserted by tests.test_pool_triage_renderer above). Spot-check each fixture:
for fx in tests/fixtures/pool_triage_renderer/inputs/*.json; do
  uv run python -m gzkit.pool.triage_renderer --input "$fx"
done
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Render a mixed-severity fixture and inspect the deliverable
uv run python -m gzkit.pool.triage_renderer --input tests/fixtures/pool_triage_renderer/inputs/mixed.json

# Render a reclassify-only fixture — expect ## Reclassify as Foundation section, no severity sections
uv run python -m gzkit.pool.triage_renderer --input tests/fixtures/pool_triage_renderer/inputs/reclassify_only.json

# Verify byte-equivalence with golden output
diff <(uv run python -m gzkit.pool.triage_renderer --input tests/fixtures/pool_triage_renderer/inputs/mixed.json) \
     tests/fixtures/pool_triage_renderer/golden/mixed.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.48-03-01: Given any rank-input fixture, when the renderer is invoked twice in two separate processes, then the two outputs are byte-identical (determinism invariant).
- [ ] REQ-0.0.48-03-02: Given a mixed-severity rank-input list, when the renderer emits markdown, then the section order is exactly `## Urgent` → `## Next Quarter` → `## Latent` and entries within each section are lexicographically sorted by `id`.
- [ ] REQ-0.0.48-03-03: Given a rank-input where the reclassify list is non-empty, when the renderer emits markdown, then a `## Reclassify as Foundation` section appears as the final block; given an empty reclassify list, the section is omitted entirely.
- [ ] REQ-0.0.48-03-04: Given a `blocked_on_foundation` annotation list is passed to the renderer, when it is non-empty, then a `## Blocked on Foundation` section is emitted between the severity sections and the reclassify section.
- [ ] REQ-0.0.48-03-05: Given a rank-input fixture, when rendered, then the output contains no timestamp, hostname, run-ID, or other non-input-derived substring (regex assertion on golden output).
- [ ] REQ-0.0.48-03-06: Given a malformed rank-input record (missing field, invalid severity), when passed to the renderer, then a Pydantic `ValidationError` is raised before any markdown is emitted.

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
