---
id: OBPI-0.0.66-06-subsume-pool-management-into-gz-next
parent: ADR-0.0.66-deterministic-steering-substrate
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.0.66-06-subsume-pool-management-into-gz-next: Subsume Pool Management Into Gz Next

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/ADR-0.0.66-deterministic-steering-substrate.md`
- **Checklist Item:** #6 - "subsume-pool-management-into-gz-next: Subsume ADR-0.0.46 pool-management, ADR-0.0.47 pool-dag-promotion-routing, and ADR-0.0.48 gz-adr-pool-triage into the unified engine: gz next --pool is the pool-scoped subset of gz next, gz pool graph is the pool DAG read, and /pool-triage becomes a pool-scoped MODE of the renamed gz-next steering skill. This ADR DECLARES the supersession; the verified demotions of 0.0.46/47/48 are a follow-up the main session discharges. (heavy lane: CLI surface unification; declared supersession)."

**Status:** Draft

## Objective

Unify the pool-triage surface under the OBPI-02 engine: implement gz next --pool as the pool-scoped subset of whole-project gz next, and gz pool graph as the pool dependency-DAG read (subsuming the surfaces ADR-0.0.46 pool-management, ADR-0.0.47 pool-dag-promotion-routing, and ADR-0.0.48 gz-adr-pool-triage proposed). `/pool-triage` becomes a pool-scoped mode of the renamed `gz-next` steering skill rather than a standalone skill. This OBPI builds the software unification (the `--pool` scoping + gz pool graph read). It DECLARES — and depends on the parent ADR's body declaring — the supersession of ADR-0.0.46/0.0.47/0.0.48; it does NOT edit those ADRs' frontmatter or status (the verified demotions are a separate follow-up the main session discharges, per ADR § Boundary Invariant 5). Lands last in the leaf-first sequence because it composes OBPI-02's engine.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/` — the `--pool` scoping over the OBPI-02 engine and the gz pool graph DAG-read module
- `src/gzkit/cli/` — the gz next --pool flag and the gz pool graph verb
- `tests/` — REQ-derived tests for pool-scoped routing, the DAG read, and the no-frontmatter-edit guard
- `docs/user/manpages/` — manpages for gz pool graph and the gz next --pool flag (Heavy-lane CLI doctrine)
- `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/**` — parent ADR package scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `docs/design/adr/foundation/ADR-0.0.46-pool-management/**`, `docs/design/adr/foundation/ADR-0.0.47-pool-dag-promotion-routing/**`, `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/**` — this OBPI does NOT edit their frontmatter or status; demotion is the main session's separate follow-up (ADR § Boundary Invariant 5)
- The OBPI-02 whole-project decision engine internals — this OBPI scopes it to `--pool`, it does not rewrite the engine
- The `gz-next` skill authoring — the skill (and its pool-scoped mode) is a downstream GHI, not authored here
- `.gzkit/ledger.jsonl` direct edits; new runtime dependencies; CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. NEVER edit the frontmatter or status of ADR-0.0.46 / ADR-0.0.47 / ADR-0.0.48 in this OBPI. This ADR DECLARES their supersession in its body; the verified demotions are a separate follow-up the main session discharges (ADR § Boundary Invariant 5). Editing them here is out of scope.
2. ALWAYS implement gz next --pool as a pool-scoped SUBSET of the same OBPI-02 engine — NOT a parallel pool-triage engine. The UNIFY framing (one engine, whole-project vs pool-scoped view) is the mitigation for the pre-mortem's "gz next vs gz next --pool semantics collided" failure.
3. ALWAYS keep gz next --pool and gz pool graph Evidentiary/Projection — they read pool state and recommend/render; they never bind a gate (ADR § Boundary Invariant 1, ADR-0.0.38). gz pool graph is a Layer-3 read over pool-ADR relationships.
4. NEVER place LLM inference in the pool-scoped routing path — it inherits OBPI-02's deterministic-decision-table constraint (ADR § Boundary Invariant 2).
5. ALWAYS provide default human-readable output and `--json` per `.gzkit/rules/cli.md`; gz pool graph and the `--pool` flag satisfy `gz cli audit`.
6. NEVER use `Optional`/`List` syntax; Pydantic models per `.gzkit/rules/models.md`; paths via `.as_posix()`.

> STOP-on-BLOCKERS: if OBPI-02's gz next engine is not yet landed, STOP — `--pool` scopes that engine and cannot exist without it (leaf-first sequencing; this OBPI lands last).

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 6 — quote verbatim into Implementation Summary:** *"subsume ADR-0.0.46/47/48 into gz next / gz next --pool and re-home /pool-triage as a pool-scoped mode of gz-next."* The Decision item is the contract; everything else hangs off it. Read also the SUBSUMES clause and § Boundary Invariant 5 (declare-not-demote).
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
uv run gz next --pool --dry-run
uv run gz pool graph
uv run gz pool graph --json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.66-06-01 [BEHAVIOR]: Given a fixture pool of ADRs, when gz next --pool --dry-run runs, then it recommends the pool-scoped next action as a SUBSET of the whole-project gz next over the same state; a `@covers`-decorated test asserts the pool-scoped recommendation and that it shares the OBPI-02 engine (not a parallel engine).
- [ ] REQ-0.0.66-06-02 [BEHAVIOR]: Given pool-ADR relationship metadata, when gz pool graph runs, then it renders the pool dependency DAG; a `@covers`-decorated test asserts the DAG structure against the fixture (table default; `--json` machine form).
- [ ] REQ-0.0.66-06-03 [BEHAVIOR]: Given the pool-scoped routing path, when gz next --pool selects an action, then NO LLM inference is invoked (inherits OBPI-02's deterministic-table constraint); a `@covers`-decorated test asserts pure-function routing over pool state.
- [ ] REQ-0.0.66-06-04 [SUPPORT]: gz next --pool and gz pool graph expose `--json`, are covered in their manpages, and `uv run gz cli audit` exits 0 with both covered and `uv run gz validate --cli-alignment` passes for the new verbs' doc references; an `artifact_edited` event records the CLI additions.
- [ ] REQ-0.0.66-06-05 [STRUCTURAL-FENCE]: This OBPI does NOT edit the frontmatter or status of ADR-0.0.46 / ADR-0.0.47 / ADR-0.0.48 — supersession is declared in the parent ADR body; demotion is a separate follow-up. Parent ADR-0.0.66 § Boundary Invariant 5 (declare-not-demote) names this invariant; a `@covers`-decorated test asserts no diff to those three ADR packages on this OBPI's branch.

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
