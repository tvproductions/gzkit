---
id: OBPI-0.0.48-01-triage-prepass-contract
parent: ADR-0.0.48-gz-adr-pool-triage
item: 1
lane: Heavy
status: Draft
allowlist:
- src/gzkit/pool/__init__.py
- src/gzkit/pool/triage_prepass.py
- src/gzkit/schemas/pool_triage_prepass.json
- tests/test_pool_triage_prepass.py
- tests/fixtures/pool_triage_prepass/
- docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/obpis/OBPI-0.0.48-01-triage-prepass-contract.md
reqs:
- REQ-0.0.48-01-01
- REQ-0.0.48-01-02
- REQ-0.0.48-01-03
- REQ-0.0.48-01-04
- REQ-0.0.48-01-05
- REQ-0.0.48-01-06
verification:
- uv run gz validate --documents
- uv run gz lint
- uv run gz typecheck
- uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_pool_triage_prepass
- 'uv run python -c "from gzkit.pool.triage_prepass import PoolTriagePrepassRecord; PoolTriagePrepassRecord.model_validate({...})"  # validate fixture'
- uv run python -m json.tool tests/fixtures/pool_triage_prepass/expected.json
---

# OBPI-0.0.48-01-triage-prepass-contract: **triage-prepass-contract** — Define the single mechanical pre-pass record set that composes ready-pool graph output, pool-overlap triage output, GHI occurrence counts, and agent-insights signal counts.

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/ADR-0.0.48-gz-adr-pool-triage.md`
- **Checklist Item:** #1 - "OBPI-0.0.48-01: **triage-prepass-contract** — Define the single mechanical pre-pass record set that composes ready-pool graph output, pool-overlap triage output, GHI occurrence counts, and agent-insights signal counts."

**Status:** Draft

## Objective

**triage-prepass-contract** — Define the single mechanical pre-pass record set that composes ready-pool graph output, pool-overlap triage output, GHI occurrence counts, and agent-insights signal counts.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/pool/__init__.py` — new `gzkit.pool` subpackage (created here; subsequent OBPIs add modules)
<!-- gz-validate-skip: command-shape -->
- `src/gzkit/pool/triage_prepass.py` — composer that calls upstream `gz pool graph --ready --json` + `gz pool triage --overlap --json` and emits the unified record set; Pydantic model `PoolTriagePrepassRecord`
- `src/gzkit/schemas/pool_triage_prepass.json` — JSON schema dual of the Pydantic model (mirrors the `authoring_guide_protocol.json` precedent)
- `tests/test_pool_triage_prepass.py` — REQ-derived tests covering record shape, age_class bucketing, and signal-count counters
- `tests/fixtures/pool_triage_prepass/` — fixture pool ADRs + golden prepass JSON for deterministic record-set assertions
- `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/obpis/OBPI-0.0.48-01-triage-prepass-contract.md` — this brief (evidence updates only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.gzkit/skills/pool-triage/**` — skill body is OBPI-0.0.48-05's surface
- `src/gzkit/pool/cognitive_pass.py` — rank-input + reclassification check is OBPI-0.0.48-02's surface
- `src/gzkit/pool/triage_renderer.py` — markdown renderer is OBPI-0.0.48-03's surface
- `src/gzkit/pool/blocked_foundation.py` — blocked-foundation filter is OBPI-0.0.48-04's surface
- `docs/user/manpages/**` — manpage edits are OBPI-0.0.48-06's surface
<!-- gz-validate-skip: command-shape -->
- Edits to `gz pool graph` / `gz pool triage` upstream CLI surfaces (ADR-0.0.46/47 own those)
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `PoolTriagePrepassRecord` MUST be a frozen Pydantic `BaseModel` with `extra="forbid"` and MUST declare the eleven fields named in ADR § Step 1: `id`, `status`, `lane`, `tags`, `depends_on`, `complements`, `blocks`, `age_class`, `overlap_cluster_id`, `intent_summary`, `decision_summary`, `ghi_occurrence_count`, `insights_signal_count`.
2. REQUIREMENT: `age_class` MUST be a Literal of exactly `{"fresh", "aging", "stale"}` derived from the pool ADR's `date:` frontmatter against today using the thresholds `<3mo` / `3-6mo` / `>6mo`.
3. REQUIREMENT: `ghi_occurrence_count` MUST be computed by counting open GHIs whose title OR body references the pool ADR's ID — counted, not narrated. (Amended 2026-05-22.)
4. REQUIREMENT: `insights_signal_count` MUST be computed by counting records in `.gzkit/insights/agent-insights.jsonl` whose `scope` field references the pool ADR's design space — counted, not narrated. (Amended 2026-05-22.)
5. REQUIREMENT: `src/gzkit/schemas/pool_triage_prepass.json` MUST validate identical examples to the Pydantic model — drift between schema and model is fail-closed at test time.
6. NEVER: Issue subprocess calls or write to disk during record construction — the composer is a pure transform from upstream JSON inputs.
7. NEVER: Mutate any file under `docs/design/adr/pool/**` or `docs/design/adr/foundation/**` — the prepass is read-only over the ADR corpus.
8. ALWAYS: Render any relative path field via `.as_posix()` per `.claude/rules/cross-platform.md` before serializing to JSON.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.


## Creates these files

<!-- Net-new files this OBPI creates. Path existence is exempt for these entries per GHI #419. -->

- `src/gzkit/pool/__init__.py` **CREATE**
- `src/gzkit/pool/triage_prepass.py` **CREATE**
- `src/gzkit/schemas/pool_triage_prepass.json` **CREATE**
- `tests/test_pool_triage_prepass.py` **CREATE**
- `tests/fixtures/pool_triage_prepass/` **CREATE**

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
<!-- gz-validate-skip: command-shape -->
- [ ] **Upstream CLI dependency:** `gz pool graph --ready --json` (ADR-0.0.47) and `gz pool triage --overlap --json` (ADR-0.0.46) MUST be registered parser verbs before the composer can be exercised end-to-end. Authoring/test scaffolding may proceed against fixture inputs; full integration STOPS until both upstream ADRs reach Validated status. See ADR-0.0.48 § Implementation Sequencing Criteria.

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
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_pool_triage_prepass

# OBPI-specific surface checks
test -f src/gzkit/pool/triage_prepass.py
test -f src/gzkit/schemas/pool_triage_prepass.json
uv run python -c "from gzkit.pool.triage_prepass import PoolTriagePrepassRecord; PoolTriagePrepassRecord.model_validate({...})"  # validate fixture
uv run python -m json.tool tests/fixtures/pool_triage_prepass/expected.json
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Construct the prepass record set for the full pool (read-only)
uv run python -m gzkit.pool.triage_prepass --pool-root docs/design/adr/pool --format json | head -50

# Inspect age_class bucketing on a known fresh + aging + stale fixture
uv run python -m gzkit.pool.triage_prepass --fixture tests/fixtures/pool_triage_prepass/mixed_ages.json --format json | jq '.[].age_class'

# Inspect signal counters on a pool ADR with known GHI + insights references
uv run python -m gzkit.pool.triage_prepass --slug ADR-pool.example --format json | jq '{ghi:.ghi_occurrence_count, insights:.insights_signal_count}'
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.48-01-01: Given a valid pool ADR with frontmatter, when `PoolTriagePrepassRecord.model_validate(...)` is called with the eleven ADR § Step-1 fields, then construction succeeds and `extra="forbid"` rejects any unknown key.
- [ ] REQ-0.0.48-01-02: Given a pool ADR dated 30/120/200 days before today, when `age_class` is computed, then the values are `fresh`/`aging`/`stale` respectively (thresholds <3mo / 3-6mo / >6mo).
- [ ] REQ-0.0.48-01-03: Given an open GHI whose body contains the literal pool ADR ID, when `ghi_occurrence_count` is computed, then the count increments by exactly one per matching GHI (amended 2026-05-22).
- [ ] REQ-0.0.48-01-04: Given a record in `.gzkit/insights/agent-insights.jsonl` whose `scope` references the pool ADR's design space, when `insights_signal_count` is computed, then the count increments by exactly one per matching record (amended 2026-05-22).
- [ ] REQ-0.0.48-01-05: Given the JSON schema at `src/gzkit/schemas/pool_triage_prepass.json`, when a Pydantic-emitted record is validated against it, then validation succeeds — and schema/model drift fail-closes the test suite.
- [ ] REQ-0.0.48-01-06: Given the prepass composer is invoked, when no upstream CLI write side-effect is observed, then the composer is confirmed pure-transform (no subprocess writes, no ADR mutation).

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
