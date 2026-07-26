---
id: OBPI-0.0.66-03-gz-metrics-read-view
parent: ADR-0.0.66-deterministic-steering-substrate
item: 3
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
- REQ-0.0.66-03-01
- REQ-0.0.66-03-02
- REQ-0.0.66-03-03
- REQ-0.0.66-03-04
- REQ-0.0.66-03-05
verification:
- gz validate --brief-command-shape and rejected at the verify stage.
- Write multi-step verification as separate uv run ... lines. -->
- uv run gz validate --documents
- uv run gz lint
- uv run gz typecheck
- uv run gz test
---

# OBPI-0.0.66-03-gz-metrics-read-view: Gz Metrics Read View

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/ADR-0.0.66-deterministic-steering-substrate.md`
- **Checklist Item:** #3 - "gz-metrics-read-view: Implement gz metrics - a read-view over the receipt stream computing throughput, duration, defect rate, rework cycles, WIP, and trend. Read-view only (collapses the proposed parallel session-metrics.jsonl into a read over the unified stream); Layer-3 derived; freshness drift validator. (heavy lane: new CLI verb)."

**Status:** Draft

## Objective

Implement gz metrics — a read-view over the OBPI-01 receipt stream and ledger computing OBPI throughput, session duration, defect rate, rework cycles, WIP, and trend. It is a read-view ONLY: it collapses the proposed parallel `session-metrics.jsonl` store into a read over the unified governance-event stream (no second store). The view is Layer-3 derived, fully rebuildable from Layer-1/Layer-2 sources, and guarded by a freshness drift validator that fail-closes when the stream has advanced past the view's last computation. Default human-readable table; `--json` machine form. This OBPI delivers the metrics read-view only.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/` — the gz metrics read-view module (aggregation over the stream/ledger)
- `src/gzkit/cli/` — the gz metrics verb and flags (`--json`, time-window options)
- `src/gzkit/trust_audits.py` (or the validator-scope home) — the freshness drift validator scope for the metrics view
- `tests/` — REQ-derived tests for the aggregations and the freshness fail-close
- `docs/user/manpages/` — gz metrics manpage (Heavy-lane CLI doctrine)
- `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/**` — parent ADR package scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- A parallel `session-metrics.jsonl` (or any second metrics store) — explicitly REJECTED (ADR Alternative 6); metrics are a read-view over the unified stream only
- The OBPI-01 hub registry/schema internals — this OBPI READS the stream; it does not add event kinds
- gz next / gz search / gz insights surfaces (OBPIs 02, 04)
- `.gzkit/ledger.jsonl` direct edits; the superseded ADR frontmatter
- New runtime dependencies; CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS implement gz metrics as a READ-VIEW over the OBPI-01 stream and ledger — NEVER a second store. A parallel `session-metrics.jsonl` is explicitly rejected (ADR Alternative 6); the view computes from the unified stream on read.
2. ALWAYS keep the view Layer-3 derived and never source-of-truth: it is fully rebuildable from Layer-1/Layer-2 sources, and a freshness drift validator fail-closes when the stream has advanced past the view's last computation (ADR § Boundary Invariant 3; state-doctrine).
3. ALWAYS keep gz metrics Evidentiary/Projection — it reports; it never binds a gate or attestation (ADR § Boundary Invariant 1, ADR-0.0.38).
4. ALWAYS provide default human-readable table output and a `--json` machine form per `.gzkit/rules/cli.md`; the manpage/command-doc/index must satisfy `gz cli audit`.
5. NEVER compute a metric from narrative or prose; every metric derives from receipt-stream/ledger events (the receipt-grounded-not-narrative property the hub generalization established).
6. NEVER use `Optional`/`List` syntax; Pydantic models per `.gzkit/rules/models.md`; paths via `.as_posix()` per `.gzkit/rules/cross-platform.md`.

> STOP-on-BLOCKERS: if OBPI-01's stream is not yet landed, STOP — this read-view has no source to read (leaf-first sequencing).

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 3 — quote verbatim into Implementation Summary:** *"gz metrics read-view over the stream."* The Decision item is the contract; everything else hangs off it. Read also the COALESCES clause naming `session-productivity-metrics` and ADR Alternative 6 (parallel store rejected).
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
uv run gz metrics
uv run gz metrics --json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.66-03-01 [BEHAVIOR]: Given a fixture receipt stream/ledger with known events, when gz metrics runs, then it reports throughput, duration, defect rate, rework cycles, WIP, and trend computed from those events; a `@covers`-decorated test asserts each metric against the fixture's known-correct values.
- [ ] REQ-0.0.66-03-02 [BEHAVIOR]: Given the metrics view computed at stream position N, when the stream advances to N+k, then the freshness drift validator fail-closes (exit 3) until the view is recomputed; a `@covers`-decorated test asserts the fail-close on stale view and pass after rebuild.
- [ ] REQ-0.0.66-03-03 [BEHAVIOR]: Given the same source stream, when the view is rebuilt from scratch, then it reproduces the identical metrics (Layer-3 fully-rebuildable property); a `@covers`-decorated test asserts rebuild determinism.
- [ ] REQ-0.0.66-03-04 [SUPPORT]: gz metrics exposes `--json`, is covered in its manpage, and `uv run gz cli audit` exits 0 with the verb covered and `uv run gz validate --cli-alignment` passes for the new verb's doc references; an `artifact_edited` event records the CLI addition.
- [ ] REQ-0.0.66-03-05 [STRUCTURAL-FENCE]: gz metrics is a read-view only — no parallel metrics store is created, and the view never becomes source-of-truth or binds a gate. Parent ADR-0.0.66 § Boundary Invariants 1 (evidence-not-authority) and 3 (Layer-3-never-source-of-truth) name these invariants; ADR Alternative 6 rejects the parallel store.

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
