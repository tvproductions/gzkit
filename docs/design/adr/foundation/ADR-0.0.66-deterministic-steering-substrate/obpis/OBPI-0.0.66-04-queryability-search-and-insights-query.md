---
id: OBPI-0.0.66-04-queryability-search-and-insights-query
parent: ADR-0.0.66-deterministic-steering-substrate
item: 4
lane: Heavy
status: Draft
allowlist:
- src/gzkit/
- src/gzkit/cli/
- src/gzkit/trust_audits.py
- tests/
- docs/user/manpages/
- docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/**
reqs:
- REQ-0.0.66-04-01
- REQ-0.0.66-04-02
- REQ-0.0.66-04-03
- REQ-0.0.66-04-04
- REQ-0.0.66-04-05
- REQ-0.0.66-04-06
verification:
- gz validate --brief-command-shape and rejected at the verify stage.
- Write multi-step verification as separate uv run ... lines. -->
- uv run gz validate --documents
- uv run gz lint
- uv run gz typecheck
- uv run gz test
---

# OBPI-0.0.66-04-queryability-search-and-insights-query: Queryability Search And Insights Query

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/ADR-0.0.66-deterministic-steering-substrate.md`
- **Checklist Item:** #4 - "queryability-search-and-insights-query: Implement gz search (stdlib SQLite FTS5 index over ledger events, handoffs, and insights; gz search rebuild for full rebuild) and gz insights query (browsable-by-topic read over agent-insights.jsonl). Both MUST be independent of the gz next engine so reads survive engine failure (the 2am-operator invariant). Layer-3 derived; freshness validators. (heavy lane: new CLI verbs)."

**Status:** Draft

## Objective

Implement the queryability layer: gz search (a stdlib SQLite FTS5 index over ledger events, session handoffs, and agent insights, with gz search rebuild for full rebuild and incremental indexing on append) and gz insights query (a browsable-by-topic read over `agent-insights.jsonl`). Both MUST be independent of the gz next engine so raw recall survives engine failure (the 2am-operator invariant — ADR § Boundary Invariant 4). Indexes are Layer-3 derived, fully rebuildable from Layer-1/Layer-2 sources, and guarded by freshness validators. Stdlib-first: SQLite FTS5 is in the stdlib `sqlite3` module — no new dependency. Default human-readable output; `--json` machine form.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/` — the FTS5 index builder/query module and the gz insights query read module
- `src/gzkit/cli/` — the gz search verb (+ `rebuild`) and gz insights query verb
- `src/gzkit/trust_audits.py` (or the validator-scope home) — freshness validator scopes for the search index and the insights view
- `tests/` — REQ-derived tests for FTS5 indexing/query, incremental append, rebuild, the insights query, and the no-gz next-dependency guard
- `docs/user/manpages/` — manpages for gz search and gz insights query (Heavy-lane CLI doctrine)
- `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/**` — parent ADR package scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- The gz next decision engine (OBPI-02) — gz search / gz insights query MUST NOT import, call into, or hard-depend on it (ADR § Boundary Invariant 4)
- Any third-party search/index dependency — SQLite FTS5 ships in the stdlib `sqlite3` module; stdlib-first forbids adding one
- `.gzkit/insights/agent-insights.jsonl` write path — gz insights query is read-only over it; the JSONL stays the T2 system-of-record
- gz metrics (OBPI-03); the superseded ADR frontmatter; `.gzkit/ledger.jsonl` direct edits
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. NEVER make gz search or gz insights query depend on the gz next engine. They MUST function when the next-best-action engine is unavailable (the 2am-operator invariant — ADR § Boundary Invariant 4). No import of, call into, or hard-dependency on the OBPI-02 engine.
2. ALWAYS use stdlib SQLite FTS5 (the `sqlite3` module) for the search index — NEVER add a third-party search/index dependency (stdlib-first doctrine; the `cross-session-search` pool ADR already names FTS5).
3. ALWAYS keep both indexes Layer-3 derived and never source-of-truth: fully rebuildable via gz search rebuild from Layer-1/Layer-2 sources; freshness validators fail-close on staleness (ADR § Boundary Invariant 3). The `agent-insights.jsonl` JSONL remains the T2 system-of-record; gz insights query is read-only over it.
4. ALWAYS keep both verbs Evidentiary/Projection — they surface recall; they never bind a gate or attestation (ADR § Boundary Invariant 1, ADR-0.0.38).
5. ALWAYS support incremental indexing (new ledger events / insights indexed on append) AND a full gz search rebuild; normal operation must not require a full rebuild.
6. ALWAYS provide default human-readable output and `--json` per `.gzkit/rules/cli.md`; both verbs satisfy `gz cli audit`. Pydantic models per `.gzkit/rules/models.md`; paths via `.as_posix()`; no `Optional`/`List` syntax.

> STOP-on-BLOCKERS: if OBPI-01's stream is not yet landed, STOP — the search index reads ledger/stream events as one of its sources (leaf-first sequencing).

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 4 — quote verbatim into Implementation Summary:** *"queryability verbs gz search (FTS5) and gz insights query."* The Decision item is the contract; everything else hangs off it. Read also § Boundary Invariant 4 (queryability must survive gz next engine failure) and the COALESCES clause naming `cross-session-search` and `insights-browsable-by-topic`.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/ADR-0.0.66-deterministic-steering-substrate.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/ADR-0.0.66-deterministic-steering-substrate.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/**`
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
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz search rebuild
uv run gz search attestation
uv run gz insights query --topic skill-feedback
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.66-04-01 [BEHAVIOR]: Given a fixture corpus of ledger events, handoffs, and insights, when gz search <query> runs with an FTS5 query (boolean/phrase/prefix), then it returns grouped, ranked results with source attribution; a `@covers`-decorated test asserts query results against the fixture.
- [ ] REQ-0.0.66-04-02 [BEHAVIOR]: Given a new ledger event/insight appended after the index was built, when incremental indexing runs, then the new record is searchable without a full rebuild; and gz search rebuild reconstructs the identical index from sources. A `@covers`-decorated test asserts incremental-append visibility and rebuild determinism.
- [ ] REQ-0.0.66-04-03 [BEHAVIOR]: Given a topic, when gz insights query --topic <t> runs, then it returns the matching insights from `agent-insights.jsonl` read-only (the JSONL is unmodified); a `@covers`-decorated test asserts topic filtering and that no write occurs to the JSONL.
- [ ] REQ-0.0.66-04-04 [BEHAVIOR]: Given the gz next engine is unavailable (simulated import/call failure), when gz search and gz insights query run, then both still return results; a `@covers`-decorated test asserts the queryability layer does not import or call the OBPI-02 engine (the 2am-operator invariant).
- [ ] REQ-0.0.66-04-05 [SUPPORT]: gz search (+ `rebuild`) and gz insights query expose `--json`, are covered in their manpages, and `uv run gz cli audit` exits 0 with both verbs covered and `uv run gz validate --cli-alignment` passes for the new verbs' doc references; an `artifact_edited` event records the CLI additions. The index uses stdlib `sqlite3` FTS5 with no new dependency in `pyproject.toml`.
- [ ] REQ-0.0.66-04-06 [STRUCTURAL-FENCE]: The queryability layer is independent of the gz next engine and both indexes are Layer-3-never-source-of-truth. Parent ADR-0.0.66 § Boundary Invariants 4 (queryability-survives-engine-failure) and 3 (Layer-3-never-source-of-truth) name these invariants.

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
