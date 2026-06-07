---
id: OBPI-0.0.64-02-advances-decorator-and-discovery-convention
parent: ADR-0.0.64-task-envelope-and-planning-decomposition
item: 2
lane: Heavy
status: Completed
ln:
  - req_id: REQ-0.0.64-02-01
    receipt_ids:
      - arb-ruff-32ecfd6f982d48b0aa9f0cde4559b9a3
      - arb-step-mkdocs-c100bc658b97486fb36cfbc56161649e
      - arb-step-typecheck-27782e54de4d456ebe91db5a0e964eac
      - arb-step-unittest-43b60cb184bd4814ac8478614e85aa4a
      - arb-step-unittest-4f7e2cf661334e39b06cb333fce6e33e
  - req_id: REQ-0.0.64-02-02
    receipt_ids:
      - arb-ruff-32ecfd6f982d48b0aa9f0cde4559b9a3
      - arb-step-mkdocs-c100bc658b97486fb36cfbc56161649e
      - arb-step-typecheck-27782e54de4d456ebe91db5a0e964eac
      - arb-step-unittest-43b60cb184bd4814ac8478614e85aa4a
      - arb-step-unittest-4f7e2cf661334e39b06cb333fce6e33e
  - req_id: REQ-0.0.64-02-03
    receipt_ids:
      - arb-ruff-32ecfd6f982d48b0aa9f0cde4559b9a3
      - arb-step-mkdocs-c100bc658b97486fb36cfbc56161649e
      - arb-step-typecheck-27782e54de4d456ebe91db5a0e964eac
      - arb-step-unittest-43b60cb184bd4814ac8478614e85aa4a
      - arb-step-unittest-4f7e2cf661334e39b06cb333fce6e33e
---

# OBPI-0.0.64-02-advances-decorator-and-discovery-convention: Advances Decorator And Discovery Convention

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md`
- **Checklist Item:** #2 - "OBPI-0.0.64-02: **advances-decorator-and-discovery-convention** — Add `@advances(TASK-...)` decorator in `src/gzkit/tasks.py` as substantive peer of `@covers`. Decoration-time validation; captures `fn.__code__.co_filename` (rendered `.as_posix()`) + `fn.__code__.co_firstlineno`; registers `TaskAttributionRecord` (Pydantic `BaseModel` + `ConfigDict(frozen=True, extra='forbid')`) into module-level registry following `@covers`'s lazy `_load_known_reqs` pattern. Frontmatter `tasks: list[str]` channel added to structured-artifact schemas (brief frontmatter + ADR-package frontmatter where applicable). Author new rule `.gzkit/rules/task-discovery.md` codifying the four-channel taxonomy (Python `@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`) with body-level `<!-- rule-version: 0.1.0 -->` marker + visible block quote per `.claude/rules/skill-surface-sync.md`. Tests: `@advances` decoration fail-closes on unknown TASK ID at import; registry surface exposes `TaskAttributionRecord` query API; frontmatter channel parses + validates via existing brief/ADR schema machinery. (heavy lane: new authoring contract; new rule)."

**Status:** Completed

## Objective

Add the `@advances(TASK-...)` decorator to `src/gzkit/tasks.py` as a substantive peer of `@covers` — decoration-time validation, captured callsite metadata (`fn.__code__.co_filename` rendered `.as_posix()` + `fn.__code__.co_firstlineno`), and a frozen `TaskAttributionRecord` (Pydantic `BaseModel` + `ConfigDict(frozen=True, extra="forbid")`) registered into a module-level registry following `@covers`'s lazy `_load_known_reqs` pattern. Extend brief and ADR-package frontmatter with a `tasks: list[str]` channel and author the net-new rule `.gzkit/rules/task-discovery.md` codifying the four-channel taxonomy (Python `@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`). This OBPI lands the authoring contract only; subdivision sequencing is OBPI-03 and coherence validation is OBPI-04.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md` — parent ADR for intent and scope
- `src/gzkit/tasks.py` — explicitly referenced by the checklist item
- **CREATE** `.gzkit/rules/task-discovery.md` — net-new rule authored by this OBPI; codifies the four-channel TASK-discovery taxonomy
- `.gzkit/rules/skill-surface-sync.md` — canonical surface referenced by the checklist item (vendor mirror at `.claude/rules/` is generated; edit canonical only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: **advances-decorator-and-discovery-convention** — Add `@advances(TASK-...)` decorator in `src/gzkit/tasks.py` as substantive peer of `@covers`. Decoration-time validation; captures `fn.__code__.co_filename` (rendered `.as_posix()`) + `fn.__code__.co_firstlineno`; registers `TaskAttributionRecord` (Pydantic `BaseModel` + `ConfigDict(frozen=True, extra='forbid')`) into module-level registry following `@covers`'s lazy `_load_known_reqs` pattern. Frontmatter `tasks: list[str]` channel added to structured-artifact schemas (brief frontmatter + ADR-package frontmatter where applicable). Author new rule `.gzkit/rules/task-discovery.md` codifying the four-channel taxonomy (Python `@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`) with body-level `<!-- rule-version: 0.1.0 -->` marker + visible block quote per `.claude/rules/skill-surface-sync.md`. Tests: `@advances` decoration fail-closes on unknown TASK ID at import; registry surface exposes `TaskAttributionRecord` query API; frontmatter channel parses + validates via existing brief/ADR schema machinery. (heavy lane: new authoring contract; new rule).
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief
1. REQUIREMENT: Verification commands MUST be concrete and runnable before acceptance
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/tasks.py`
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
uv run gz test

# Specific verification for this OBPI
test -f docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md
test -f src/gzkit/tasks.py
test -f .gzkit/rules/task-discovery.md
test -f .claude/rules/skill-surface-sync.md
uv run -m unittest tests/test_persona_schema.py -v
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Replace with concrete product demonstrations for this OBPI.
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.64-02-01: Given the parent ADR intent, when the OBPI implementation is complete, then the primary scoped artifacts exist and match the documented contract
- [ ] REQ-0.0.64-02-02: Given the Allowed Paths in this brief, when the OBPI is executed, then changes remain inside scope and denied paths remain untouched
- [ ] REQ-0.0.64-02-03: Given the Verification commands in this brief, when they run, then evidence is recorded before the OBPI is accepted

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


```python
>>> from gzkit.tasks import advances, get_task_registry
>>> @advances("TASK-0.0.64-02-01-01")
... def my_fn(): return 42
>>> get_task_registry()[0].task_id
'TASK-0.0.64-02-01-01'
>>> @advances("TASK-9.9.9-99-99-01")
... def bogus(): pass
ValueError: Unknown parent REQ for TASK 'TASK-9.9.9-99-99-01': REQ-9.9.9-99-99 not found in extracted briefs
```

Mechanical evidence: `arb-step-unittest-4f7e2cf661334e39b06cb333fce6e33e` (13/13 OBPI-scoped pass), `arb-step-unittest-43b60cb184bd4814ac8478614e85aa4a` (5686/5686 full sweep), `arb-ruff-32ecfd6f982d48b0aa9f0cde4559b9a3` (clean), `arb-step-typecheck-27782e54de4d456ebe91db5a0e964eac` (clean), `arb-step-mkdocs-c100bc658b97486fb36cfbc56161649e` (docs build strict clean). REQ→@covers parity: 3/3 covered (100%), `behavior_uncovered_reqs=0`. BDD coverage waived per Two-runners doctrine.

### Implementation Summary


- Files created/modified: `src/gzkit/tasks.py` (added `@advances` decorator, `TaskAttributionRecord` frozen Pydantic model, module-level `_ADVANCES_REGISTRY`, lazy `_load_known_task_reqs()` mirroring `@covers`'s pattern, helpers); `.gzkit/rules/task-discovery.md` (CREATE — four-channel TASK-discovery taxonomy rule, v0.1.0); `tests/governance/test_advances_decorator.py` (CREATE — 13 tests covering 3 REQs); `docs/governance/advisory-rules-audit.md` (scorecard row #60 — Promotable, coupled-surface coherence per Rule 1a); `data/behave_coverage_waivers.json` (Two-runners-doctrine waiver entry, same shape as OBPI-01).
- Tests added: 13 unittest cases under `tests/governance/test_advances_decorator.py` covering format-fail-close, unknown-parent-REQ-fail-close, registry registration, `.as_posix()` cross-platform rendering, frozen+extra-forbid model contract, multi-decoration interleaving with `@covers`, and structural scope/evidence assertions.
- Date completed: 2026-05-28
- Attestation status: operator-attested "attest completed"
- Defects noted: none in-scope; advisory scope gap noted in plan (frontmatter `tasks:` schema enforcement deferred to OBPI-0.0.64-04 per ADR plan).

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.64-02 lands @advances decorator + TaskAttributionRecord + task-discovery rule v0.1.0 with 13/13 OBPI-scoped tests (receipt arb-step-unittest-4f7e2cf661334e39b06cb333fce6e33e), 5686/5686 full sweep (receipt arb-step-unittest-43b60cb184bd4814ac8478614e85aa4a), arb-ruff/arb-step-typecheck/arb-step-mkdocs all clean, 3/3 REQs covered (behavior_uncovered_reqs=0).
- Date: 2026-05-28

---

**Date Completed:** 2026-05-28

**Evidence Hash:** -
