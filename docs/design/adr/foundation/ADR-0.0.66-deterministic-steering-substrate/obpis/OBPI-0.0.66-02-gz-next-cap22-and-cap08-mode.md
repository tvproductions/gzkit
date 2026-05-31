---
id: OBPI-0.0.66-02-gz-next-cap22-and-cap08-mode
parent: ADR-0.0.66-deterministic-steering-substrate
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.66-02-gz-next-cap22-and-cap08-mode: Gz Next Cap22 And Cap08 Mode

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/ADR-0.0.66-deterministic-steering-substrate.md`
- **Checklist Item:** #2 - "gz-next-cap22-and-cap08-mode: Implement gz next (CAP-22) - whole-project deterministic decision-table next-best-action over ledger/OBPI/ADR state - plus the CAP-08 MODE per-invocation intent surface (READ-ONLY / PLAN-FIRST / IMPLEMENT). Decision table is deterministic per ADR-0.0.39/0.0.40 (NO LLM inference). Output modes gz next / --dry-run / --explain; never auto-executes Gate 5 or destructive ops - surfaces human gates and waits. CAP-08 tiers, CAP-09, CAP-10, CAP-21 stay PARKED. (heavy lane: new CLI verb)."

**Status:** Draft

## Objective

Implement gz next (CAP-22) — the whole-project, deterministic decision-table next-best-action engine over current governance state (ledger events, OBPI completion status, ADR lifecycle, pending reconciliation markers, working-tree status) — plus the CAP-08 MODE per-invocation intent surface (READ-ONLY / PLAN-FIRST / IMPLEMENT) emitting `mode_declared`/`mode_resolved` to the OBPI-01 hub. Routing is a deterministic decision table with NO LLM inference (ADR-0.0.39/0.0.40); output modes are gz next (print recommendation + reason, then act), gz next --dry-run (recommend only), and gz next --explain (full state assessment + decision rationale). The engine NEVER auto-executes Gate 5 (human attestation) or destructive operations — it surfaces the action and waits. CAP-08 tiers, CAP-09, CAP-10, and CAP-21 stay PARKED post-1.0. This OBPI delivers the whole-project engine; gz next --pool scoping lands in OBPI-06.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/` — the gz next decision-engine module (state assessment + decision table) and the MODE surface
- `src/gzkit/cli/` — the gz next verb (and `--dry-run` / `--explain` flags); the gz mode declare/resolve surface
- `src/gzkit/events.py` / `src/gzkit/schemas/` — `mode_declared` / `mode_resolved` event kinds registered into the OBPI-01 hub registry (consumes the hub; does not redefine it)
- `tests/` — REQ-derived tests for the decision table and MODE
- `docs/user/manpages/` — manpages for gz next and gz mode (Heavy-lane CLI doctrine)
- `docs/design/adr/foundation/ADR-0.0.66-deterministic-steering-substrate/**` — parent ADR package scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- The OBPI-01 event-kind registry/schema internals — this OBPI REGISTERS kinds via the registry; it does not redefine the registry shape
- gz next --pool scoping and gz pool graph — OBPI-06 (this OBPI is whole-project only)
- Any LLM/model-inference call in the routing or ranking path (ADR § Boundary Invariant 2 — fail-closed prohibition)
- `.gzkit/ledger.jsonl` direct edits; the six coalesced pool ADRs / ADR-0.0.46/0.0.47/0.0.48 frontmatter
- New runtime dependencies; CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. NEVER place LLM/model inference in the gz next routing or ranking path. Selection is a deterministic decision table over observable state per ADR-0.0.39/0.0.40 and ADR § Boundary Invariant 2. If the table proves insufficient, the ONLY sanctioned degrade is advisory output — never LLM-inferred routing.
2. NEVER auto-execute Gate 5 (human attestation) or any destructive/irreversible operation. When the next step needs human judgment, gz next surfaces the action and WAITS (CAP-22 safety clause).
3. ALWAYS keep gz next an Evidentiary/Projection surface: it reads state and recommends; it MUST NOT itself become a gate, a closeout fail-close, or an attestation requirement (ADR § Boundary Invariant 1, ADR-0.0.38).
4. ALWAYS provide all three output modes: gz next (recommend-and-act), gz next --dry-run (recommend only, no side effects), gz next --explain (full state assessment + rationale). Default human-readable output; `--json` machine form per `.gzkit/rules/cli.md`.
5. ALWAYS keep CAP-08 MODE orthogonal to and unable to escalate Tier: MODE declares current-turn intent (READ-ONLY / PLAN-FIRST / IMPLEMENT) and emits `mode_declared`/`mode_resolved` to the OBPI-01 hub; it never raises authority. CAP-08 tiers, CAP-09, CAP-10, CAP-21 stay PARKED — do not implement them here.
6. ALWAYS depend on the OBPI-01 hub for MODE event emission rather than inventing a parallel store; the hub registry is the single source for event kinds (consumer contract from OBPI-01 REQ-...-01).
7. NEVER use `Optional`/`List` syntax; write `str | None` and `list[str]` per `.gzkit/rules/pythonic.md`. Pydantic models per `.gzkit/rules/models.md`.

> STOP-on-BLOCKERS: if OBPI-01's hub registry is not yet landed, STOP — this OBPI's MODE events depend on it (leaf-first sequencing).

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 2 — quote verbatim into Implementation Summary:** *"gz next (CAP-22) plus CAP-08 MODE (deterministic decision table over ledger/OBPI/ADR state; surfaces, never auto-executes, human gates)."* The Decision item is the contract; everything else hangs off it. Read also the HEADLINE CAPABILITY clause (gz next is wielded by a separate GHI-routed skill — this OBPI is substrate only).
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
uv run gz next --dry-run
uv run gz next --explain
uv run gz next --json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.66-02-01 [BEHAVIOR]: Given a governance state where an ADR has zero OBPIs (and analogous states for each decision-table row: authored-not-implemented, gates-unchecked, all-gates-pass-no-attestation, dirty-tree-after-completion, no-active-work), when gz next --dry-run runs, then it recommends the correct next action for that state; a `@covers`-decorated test drives a fixture ledger through each row and asserts the recommendation.
- [ ] REQ-0.0.66-02-02 [BEHAVIOR]: Given any governance state, when gz next selects an action, then NO LLM/model inference is invoked in the routing path; a `@covers`-decorated test asserts routing is pure-function over the state input (same state → same recommendation, deterministically) and that the routing module imports no model-inference dependency.
- [ ] REQ-0.0.66-02-03 [BEHAVIOR]: Given a state whose next step is Gate 5 (human attestation) or a destructive operation, when gz next runs, then it surfaces the action and WAITS — it does not auto-execute; a `@covers`-decorated test asserts no side effect occurs and the human-judgment prompt is emitted.
- [ ] REQ-0.0.66-02-04 [BEHAVIOR]: Given a gz mode declaration (READ-ONLY / PLAN-FIRST / IMPLEMENT), when it is recorded, then a `mode_declared` event is appended via the OBPI-01 hub and resolution emits `mode_resolved`; a `@covers`-decorated test asserts both events land in the stream with the declared MODE.
- [ ] REQ-0.0.66-02-05 [SUPPORT]: gz next exposes `--dry-run`, `--explain`, and `--json` and is covered in its manpage; `uv run gz cli audit` exits 0 with the verb covered across manpage, command doc, and index, `uv run gz validate --cli-alignment` passes for the new verb's doc references, and an `artifact_edited` event records the CLI addition.
- [ ] REQ-0.0.66-02-06 [STRUCTURAL-FENCE]: gz next is Evidentiary/Projection — it never binds a gate, closeout fail-close, or attestation requirement, and its routing path contains no LLM inference. Parent ADR-0.0.66 § Boundary Invariants 1 (evidence-not-authority) and 2 (no-LLM-in-routing) name these invariants.

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
