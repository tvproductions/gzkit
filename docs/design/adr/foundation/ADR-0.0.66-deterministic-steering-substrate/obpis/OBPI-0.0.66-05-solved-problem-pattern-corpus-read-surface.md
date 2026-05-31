---
id: OBPI-0.0.66-05-solved-problem-pattern-corpus-read-surface
parent: ADR-0.0.66-deterministic-steering-substrate
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.66-05-solved-problem-pattern-corpus-read-surface: Solved Problem Pattern Corpus Read Surface

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/ADR-0.0.66-deterministic-steering-substrate.md`
- **Checklist Item:** #5 - "solved-problem-pattern-corpus-read-surface: Implement the solved-problem pattern corpus as a governed prior-art memory read-surface, bound by the four invariants (append-only, Layer-2, each entry cites primary evidence, skill-written never hand-edited). Provides the aggregated recurring-failure-pattern artifact that per-occurrence search does not. (heavy lane: new read surface over governed corpus)."

**Status:** Draft

## Objective

Implement the solved-problem pattern corpus as a governed prior-art memory read-surface — the aggregated recurring-failure-pattern artifact that per-occurrence gz search (OBPI-04) does not provide. The corpus is bound by the four governance invariants inherited from `ADR-pool.solved-problem-pattern-corpus`: (1) append-only and Layer-2 (entries written by a skill, never hand-edited, same shape as the ledger); (2) each entry cites primary evidence (session ID, GHI number, ADR ID, or commit SHA) — entries without citations are rejected at write; (3) entries are skill-written, never free-form operator prose; (4) the read-surface is governed, not a vibing dump. This OBPI delivers the corpus schema + the governed write path + the read-surface; the per-pattern skill that authors entries is downstream. Default human-readable output; `--json` machine form.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/` — the corpus schema, the governed write path (citation-enforced), and the read-surface module
- `src/gzkit/schemas/` — the JSON schema for a corpus entry (citation field required)
- `src/gzkit/cli/` — the read verb (e.g. gz patterns / gz insights patterns, resolved at implementation against the existing namespace)
- `tests/` — REQ-derived tests for citation enforcement, append-only write, and the read-surface
- `docs/user/manpages/` — manpage for the new read verb (Heavy-lane CLI doctrine)
- `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/**` — parent ADR package scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- A hand-edit path into the corpus — entries are skill-written only; no operator-typed free-form prose surface (invariant 3)
- The per-pattern authoring skill itself — downstream of this ADR (this OBPI delivers schema + write path + read-surface, not the skill)
- gz search / gz insights query (OBPI-04) internals; gz next engine (OBPI-02)
- `.gzkit/ledger.jsonl` direct edits; the superseded ADR frontmatter
- New runtime dependencies; CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS reject a corpus entry that cites no primary evidence (session ID, GHI number, ADR ID, or commit SHA) at write time. This is the load-bearing invariant separating a governed corpus from a vibing dump (invariant 2); an uncited entry is fail-closed.
2. ALWAYS keep the corpus append-only and skill-written: entries are appended through gzkit code, never hand-edited, same shape as `.gzkit/ledger.jsonl` (invariants 1 and 3). NEVER add an operator-typed free-form prose surface.
3. ALWAYS keep the read-surface Evidentiary/Projection and Layer-3-never-source-of-truth: it surfaces aggregated prior-art; it never binds a gate or attestation (ADR § Boundary Invariants 1 and 3, ADR-0.0.38).
4. NEVER let the corpus reproduce training-corpus bias: every pattern entry is grounded in the project's own primary evidence (the original objection to free-form learnings corpora holds for ungoverned dumps, not for this governed evidence surface — `ADR-pool.solved-problem-pattern-corpus` § Intent).
5. ALWAYS provide default human-readable output and `--json` per `.gzkit/rules/cli.md`; the read verb satisfies `gz cli audit`.
6. NEVER use `Optional`/`List` syntax; Pydantic models with `ConfigDict(extra="forbid")` per `.gzkit/rules/models.md`; paths via `.as_posix()`.

> STOP-on-BLOCKERS: if the citation-enforcement contract cannot be satisfied (no schema field to bind primary evidence), STOP — an uncited corpus is the rejected vibing-dump shape.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 5 — quote verbatim into Implementation Summary:** *"solved-problem-pattern-corpus read-surface (governed; append-only; citation-bound)."* The Decision item is the contract; everything else hangs off it. Read also the COALESCES clause naming `solved-problem-pattern-corpus` and the source pool ADR's four governance invariants.
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
uv run gz patterns
uv run gz patterns --json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.66-05-01 [BEHAVIOR]: Given a corpus entry with NO primary-evidence citation, when the governed write path runs, then the write is rejected; given an entry citing a session ID / GHI / ADR ID / commit SHA, the write succeeds. A `@covers`-decorated test asserts both branches (citation enforcement is the load-bearing invariant).
- [ ] REQ-0.0.66-05-02 [BEHAVIOR]: Given the corpus, when the read verb runs, then it returns the aggregated patterns with their citations; a `@covers`-decorated test asserts the read returns appended entries with citation fields intact.
- [ ] REQ-0.0.66-05-03 [BEHAVIOR]: Given the corpus entry model, when instantiated with an unknown field, then `ValidationError` is raised per `ConfigDict(extra="forbid")`; a `@covers`-decorated test asserts the strict-shape rejection.
- [ ] REQ-0.0.66-05-04 [SUPPORT]: The read verb exposes `--json`, is covered in its manpage, and `uv run gz cli audit` exits 0 with the verb covered; an `artifact_edited` event records the CLI addition.
- [ ] REQ-0.0.66-05-05 [STRUCTURAL-FENCE]: The corpus is append-only, skill-written, citation-bound, and the read-surface is Layer-3-never-source-of-truth and gate-non-binding. Parent ADR-0.0.66 § Boundary Invariants 1 (evidence-not-authority) and 3 (Layer-3-never-source-of-truth) name these invariants; the four governance invariants are inherited from `ADR-pool.solved-problem-pattern-corpus`.

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
