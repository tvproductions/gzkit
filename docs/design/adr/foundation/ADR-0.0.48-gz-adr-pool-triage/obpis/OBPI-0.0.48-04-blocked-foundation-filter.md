---
id: OBPI-0.0.48-04-blocked-foundation-filter
parent: ADR-0.0.48-gz-adr-pool-triage
item: 4
lane: Heavy
status: Draft
allowlist:
- src/gzkit/pool/blocked_foundation.py
- tests/test_pool_blocked_foundation.py
- tests/fixtures/pool_blocked_foundation/
- docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/obpis/OBPI-0.0.48-04-blocked-foundation-filter.md
reqs:
- REQ-0.0.48-04-01
- REQ-0.0.48-04-02
- REQ-0.0.48-04-03
- REQ-0.0.48-04-04
- REQ-0.0.48-04-05
- REQ-0.0.48-04-06
verification:
- uv run gz validate --documents
- uv run gz lint
- uv run gz typecheck
- uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_pool_blocked_foundation
- uv run python -c "
---

# OBPI-0.0.48-04-blocked-foundation-filter: **blocked-foundation-filter** — Add the dependency cross-check that filters or annotates candidates blocked by in-flight foundation work.

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/ADR-0.0.48-gz-adr-pool-triage.md`
- **Checklist Item:** #4 - "OBPI-0.0.48-04: **blocked-foundation-filter** — Add the dependency cross-check that filters or annotates candidates blocked by in-flight foundation work."

**Status:** Draft

## Objective

**blocked-foundation-filter** — Add the dependency cross-check that filters or annotates candidates blocked by in-flight foundation work.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/pool/blocked_foundation.py` — pure-function filter that consumes prepass record set + the active foundation backlog, returns `(rank_input_filtered, blocked_annotations)`
- `tests/test_pool_blocked_foundation.py` — REQ-derived tests covering blocked-detection, near-closeout urgent-elevation, and annotation surface
- `tests/fixtures/pool_blocked_foundation/` — fixture pool ADRs with `depends_on` pointing at in-flight + near-closeout + completed foundation ADRs
- `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/obpis/OBPI-0.0.48-04-blocked-foundation-filter.md` — this brief (evidence updates only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/pool/triage_prepass.py` — prepass is OBPI-0.0.48-01's surface (this OBPI consumes its output)
- `src/gzkit/pool/cognitive_pass.py` — rank-input is OBPI-0.0.48-02's surface (this OBPI consumes its output)
- `src/gzkit/pool/triage_renderer.py` — renderer is OBPI-0.0.48-03's surface (renderer accepts this OBPI's annotation list)
- `.gzkit/skills/pool-triage/**` — skill body is OBPI-0.0.48-05's surface
- Edits to any pool ADR file or foundation ADR file — the filter is read-only over the ADR corpus
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `filter_blocked_foundation(prepass: list[PoolTriagePrepassRecord], foundation_state: FoundationStateSnapshot) -> tuple[list, list]` MUST be a pure function returning `(retained, blocked_annotations)` where retained excludes every candidate whose `depends_on` includes an in-flight (non-completed) foundation ADR.
2. REQUIREMENT: A candidate whose `depends_on` references an in-flight foundation ADR MUST be emitted as `{id, blocked_on: [<foundation_id>, ...]}` in the blocked-annotations list — never as a rank-input entry.
3. REQUIREMENT: Per ADR § Optional cross-check, when an in-flight blocking foundation ADR is *near closeout* (defined as having all Gate 1-4 evidence recorded and only awaiting Gate 5 attestation), the candidate MUST be elevated to severity `urgent` rather than annotated as blocked.
4. REQUIREMENT: Near-closeout detection MUST query foundation state from the ledger (`adr_eval_completed` / `validated` event sequence) — never from frontmatter `status:` strings, which are Layer-1 authorship not Layer-2 truth (CLAUDE.md state-doctrine).
5. NEVER: Mutate any foundation ADR file or pool ADR file during filter execution — the filter is read-only.
6. NEVER: Silently drop a candidate from both lists — every prepass record MUST appear in exactly one of `retained` or `blocked_annotations` (partition invariant).
7. ALWAYS: Render the blocking foundation IDs in `blocked_on` via canonical `ADR-0.0.NN-<slug>` form, never bare semver.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.


## Creates these files

<!-- Net-new files this OBPI creates. Path existence is exempt for these entries per GHI #419. -->

- `src/gzkit/pool/blocked_foundation.py` **CREATE**
- `tests/test_pool_blocked_foundation.py` **CREATE**
- `tests/fixtures/pool_blocked_foundation/` **CREATE**

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
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_pool_blocked_foundation

# OBPI-specific surface checks
test -f src/gzkit/pool/blocked_foundation.py
# expect in_flight, near_closeout, completed fixtures present
ls tests/fixtures/pool_blocked_foundation/

# Partition invariant: |retained| + |blocked| == |prepass|
uv run python -c "
from gzkit.pool.blocked_foundation import filter_blocked_foundation
import json
prepass = json.load(open('tests/fixtures/pool_blocked_foundation/prepass.json'))
state   = json.load(open('tests/fixtures/pool_blocked_foundation/foundation_state.json'))
retained, blocked = filter_blocked_foundation(prepass, state)
assert len(retained) + len(blocked) == len(prepass), 'partition invariant violated'
"
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Run filter against a fixture where one candidate depends on an in-flight foundation
uv run python -m gzkit.pool.blocked_foundation --prepass tests/fixtures/pool_blocked_foundation/prepass.json --foundation-state tests/fixtures/pool_blocked_foundation/foundation_state.json --format json | jq '.blocked_annotations'

# Run filter against a fixture where the blocking foundation is near-closeout — expect urgent elevation, not annotation
uv run python -m gzkit.pool.blocked_foundation --prepass tests/fixtures/pool_blocked_foundation/near_closeout_prepass.json --foundation-state tests/fixtures/pool_blocked_foundation/near_closeout_state.json --format json | jq '.retained[] | select(.severity == "urgent")'
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.48-04-01: Given a prepass record whose `depends_on` includes an in-flight foundation ADR, when the filter runs, then the record is emitted in `blocked_annotations` with `{id, blocked_on: [<foundation_id>]}` and is absent from `retained`.
- [ ] REQ-0.0.48-04-02: Given a prepass record whose `depends_on` includes only completed foundation ADRs, when the filter runs, then the record is emitted in `retained` and is absent from `blocked_annotations`.
- [ ] REQ-0.0.48-04-03: Given a prepass record whose blocking foundation has all Gate 1-4 ledger evidence recorded and only Gate 5 attestation pending, when the filter runs, then the record is retained with severity elevated to `urgent` per ADR § Optional cross-check.
- [ ] REQ-0.0.48-04-04: Given near-closeout detection runs, when foundation state is queried, then state is sourced from ledger events (`adr_eval_completed` / `validated`) — never from frontmatter `status:` strings (state-doctrine).
- [ ] REQ-0.0.48-04-05: Given any prepass input, when the filter runs, then `len(retained) + len(blocked_annotations) == len(prepass)` (partition invariant — no silent drops).
- [ ] REQ-0.0.48-04-06: Given the filter executes, when execution completes, then no file under `docs/design/adr/foundation/**` or `docs/design/adr/pool/**` has been modified (read-only invariant).

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
