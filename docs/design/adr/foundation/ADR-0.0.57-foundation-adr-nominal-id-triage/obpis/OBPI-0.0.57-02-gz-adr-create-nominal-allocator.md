---
id: OBPI-0.0.57-02-gz-adr-create-nominal-allocator
parent: ADR-0.0.57-foundation-adr-nominal-id-triage
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.57-02-gz-adr-create-nominal-allocator: Gz Adr Create Nominal Allocator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/ADR-0.0.57-foundation-adr-nominal-id-triage.md`
- **Checklist Item:** #2 - "OBPI-0.0.57-02: **gz-adr-create-nominal-allocator** — Update gz-adr-create to replace the minor-version odometer with a next-free-integer nominal allocator (runtime-contract change; Gate 5 attestation required)."

**Status:** Completed

## Objective

**gz-adr-create-nominal-allocator** — Update gz-adr-create to replace the minor-version odometer with a next-free-integer nominal allocator (runtime-contract change; Gate 5 attestation required).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/commands/plan.py` — replace `_next_available_foundation_semver` (the odometer at lines ~113-125 returning `max_n + 1`) with `_next_free_nominal_foundation_id` that returns the lowest unused integer in `0.0.<N>` regardless of gaps; rename the function and update all call sites in `plan.py`
- `tests/test_plan_command.py` (or the existing plan-create test module) — REQ-derived tests asserting nominal allocation behavior, including the gap-allocation case
- `tests/fixtures/foundation_nominal_allocator/` — fixture foundation trees: contiguous, sparse-with-gap, empty
- `.gzkit/skills/gz-adr-create/SKILL.md` — update skill description and any odometer-language references to nominal-allocator semantics; bump `skill-version` + `last_reviewed`
- `docs/user/manpages/plan-create.md` (or `docs/user/manpages/plan.md` — author wherever the existing plan-create manpage lives) — update odometer language to nominal-allocator semantics; pre-Gate-3 docs build must pass
- `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/obpis/OBPI-0.0.57-02-gz-adr-create-nominal-allocator.md` — this brief (evidence updates only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/**` — doctrine amendment is OBPI-0.0.57-01's surface
- `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/**` — doctrine amendment is OBPI-0.0.57-01's surface
- `src/gzkit/trust_audits.py` — validator audit is OBPI-0.0.57-01's surface (this OBPI assumes the validator already accepts gaps before runtime allocator behavior depends on it)
- `.gzkit/skills/gz-foundation-triage/**` — new skill is OBPI-0.0.57-03's surface
- `src/gzkit/foundation/**` — rubric/triage modules are OBPI-0.0.57-04's surface
- `docs/governance/governance_runbook.md`, `docs/user/runbook.md` — runbook updates are OBPI-0.0.57-05's surface
- Renaming or moving existing foundation ADR directories — digits preserved (ADR § Anti-pattern)
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `_next_free_nominal_foundation_id(foundation_root: Path) -> str` MUST return the lowest non-negative integer N such that no `ADR-0.0.{N}-*` directory exists under `foundation_root`, including N=0 if absent, and MUST tolerate sparse trees with gaps (e.g. {1,2,5,7} → returns "0.0.3", not "0.0.8").
2. REQUIREMENT: The old `_next_available_foundation_semver` name MUST NOT remain — rename to the nominal allocator name to make the doctrine shift visible in `git log`.
3. REQUIREMENT: Every call site in `src/gzkit/commands/plan.py` that referenced the old odometer MUST be updated, including the error-message hint shown when `--kind foundation` is missing a valid semver.
4. REQUIREMENT: The CLI surface change `gz plan create --kind foundation` MUST be a Heavy lane change — Gate 3 (docs build), Gate 4 (BDD scenario), and Gate 5 (human attestation) MUST all be recorded before completion per AGENTS.md § Lane Rules.
5. REQUIREMENT: `.gzkit/skills/gz-adr-create/SKILL.md` MUST be updated; the canonical edit MUST bump `skill-version:` AND `last_reviewed:` in the same commit per `.claude/rules/skill-surface-sync.md` non-negotiable rule #6.
6. REQUIREMENT: After the canonical skill edit, `uv run gz agent sync control-surfaces` MUST be executed so vendor mirrors stay byte-equivalent (mirror parity invariant).
7. NEVER: Mutate existing foundation ADR directories or files — only new allocations claim a fresh nominal integer; existing digits stay where they are.
8. ALWAYS: Pin the `Eval-feedback-source:` commit trailer if this OBPI lands under a GHI labeled `eval-feedback` (ADR-0.0.26 / AGENTS.md Behavior Rule 12).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.


## Creates these files

<!-- Net-new files this OBPI creates. Path existence is exempt for these entries per GHI #419. -->

- `tests/test_plan_command.py` **CREATE**
- `tests/fixtures/foundation_nominal_allocator/` **CREATE**

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/ADR-0.0.57-foundation-adr-nominal-id-triage.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/ADR-0.0.57-foundation-adr-nominal-id-triage.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/**`
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
uv run gz validate --surfaces
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_plan_command
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run -m behave features/plan_create_nominal.feature

# OBPI-specific surface checks
rg -n "_next_free_nominal_foundation_id|_next_available_foundation_semver" src/gzkit/commands/plan.py
# Expected: nominal function present; old odometer name absent

grep -E "nominal|next-free integer" docs/user/manpages/plan-create.md
grep -E "nominal" .gzkit/skills/gz-adr-create/SKILL.md

# Mirror parity after sync
diff .gzkit/skills/gz-adr-create/SKILL.md src/gzkit/skills/gz-adr-create/SKILL.md
diff .gzkit/skills/gz-adr-create/SKILL.md .claude/skills/gz-adr-create/SKILL.md
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Demonstrate gap-allocation against a sparse fixture (foundations 0.0.1, 0.0.2, 0.0.5, 0.0.7 → next is 0.0.3)
uv run python -c "
from pathlib import Path
from gzkit.commands.plan import _next_free_nominal_foundation_id
print(_next_free_nominal_foundation_id(Path('tests/fixtures/foundation_nominal_allocator/sparse_with_gap')))
"
# Expected output: 0.0.3

# Run the actual plan-create command against a fixture root
uv run gz plan create my-nominal-test --kind foundation --no-author-obpis --foundation-root tests/fixtures/foundation_nominal_allocator/sparse_with_gap --dry-run
# Expected: ADR-0.0.3-my-nominal-test allocated, not 0.0.8
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

> **REQ-0.0.57-02-01 through -02-04 are SUPERSEDED by
> [ADR-0.34.0 (Foundation Sunset)](../../../../pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md),
> discharged under OBPI-0.34.0-02 (2026-07-20, operator-ruled).** ADR-0.34.0
> closed the `foundation` kind to new authoring at every door, so
> `_next_free_nominal_foundation_id` — the allocator these REQs specify — was
> deleted along with the authoring path it served. Their subject no longer
> exists, so no honest test can cover them; authoring one would be the
> filesystem-grep anti-pattern named in `.gzkit/rules/tests.md` § REQ Scope
> Discipline. The attested record below is preserved unchanged — this is a
> supersession note, not a retraction. `gz covers` will report these as
> uncovered; that gap is explained here rather than papered over.
>
> **The REQ ids below are left plain and uncovered on purpose.** A first pass
> struck them through, which silences `gz covers` (it skips struck lines as
> malformed) while `gz adr covers-check` still counts them as live obligations —
> two consumers disagreeing, with the cleaner-looking one hiding a real gap.
> gzkit has no modeled supersession state, so the honest representation is an
> uncovered REQ plus this note. `gz adr covers-check ADR-0.0.57` already exited
> non-zero before ADR-0.34.0 — REQ-0.0.57-01-05, -02-07 **and -05-03** were
> already missing at HEAD `1c0f5251`; these four add to that list rather than
> newly breaking it. (The `-05-03` entry was omitted from a first draft of this
> note and restored after Step-4b round-3 replayed the baseline from HEAD
> objects. `gz covers` and `gz adr covers-check` legitimately report different
> coverage for the same 32 REQs: the former counts BDD tags, the latter only
> Python `@covers` annotations.)
>
> Observed while annotating (pre-existing, NOT caused by ADR-0.34.0): the
> REQ-0.0.57-02-06 text below specifies a *manpage* claim, while its covering
> test (`tests/test_plan_command.py::test_claude_mirror_is_byte_equivalent_to_canonical`)
> asserts *skill-mirror byte-equivalence*. The REQ and its proof describe
> different subjects — and ADR-0.34.0 has now retired the manpage clause it
> names. Flagged for ADR-0.0.57's owner; not repaired here.

- [ ] REQ-0.0.57-02-01: Given a foundation tree with IDs {1,2,5,7}, when `_next_free_nominal_foundation_id` is called, then it returns `"0.0.3"` — the lowest non-allocated integer, not `max+1`.
- [ ] REQ-0.0.57-02-02: Given an empty foundation tree, when the allocator is called, then it returns `"0.0.1"` (or `"0.0.0"` if the doctrine treats zero as valid — pin in the test fixture).
- [ ] REQ-0.0.57-02-03: Given a contiguous tree {1,2,3}, when the allocator is called, then it returns `"0.0.4"` — gap-tolerant behavior degenerates to odometer behavior in the gap-free case.
- [ ] REQ-0.0.57-02-04: Given `src/gzkit/commands/plan.py`, when grepped, then `_next_available_foundation_semver` is absent and `_next_free_nominal_foundation_id` is the sole allocator (rename invariant).
- [ ] REQ-0.0.57-02-05: Given `.gzkit/skills/gz-adr-create/SKILL.md` was edited, when committed, then both `skill-version:` and `last_reviewed:` advanced in the same commit (skill-surface-sync rule).
- [ ] REQ-0.0.57-02-06: Given `gz plan create --kind foundation` is invoked, when the manpage at `docs/user/manpages/plan-create.md` is rendered, then it describes the nominal-allocator semantics and no longer uses "next available" / odometer language.
- [ ] REQ-0.0.57-02-07: Given this OBPI is Heavy lane, when closeout runs, then Gate 5 human attestation is recorded with operator name (per OBPI Universal Attestation, ADR-0.0.36).

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


Fixture tree tests/fixtures/foundation_nominal_allocator/sparse_with_gap/ contains ADR-0.0.{1,2,5,7}-*; allocator returns "0.0.3" (gap-fill), not "0.0.8" (max+1). Same surface via CLI: `gz plan create my-adr --kind foundation --semver 99.0.0` prints "Next free nominal foundation ID: 0.0.3". Receipts: arb-step-unittest-889d9e6d (5449/5449), arb-step-behave-110aab86 (2/2 scoped @REQ tags), arb-ruff-76eab7ef (clean), arb-step-typecheck-8801ff81 (clean), arb-step-mkdocs-46586bdb (clean).

### Implementation Summary


- Files created: tests/test_plan_command.py (8 tests covering REQ-01..06); tests/fixtures/foundation_nominal_allocator/{sparse_with_gap,contiguous,empty}/ (8 stub ADR dirs + .gitkeep); features/plan_create_nominal.feature (2 scenarios @REQ-0.0.57-02-01, @REQ-0.0.57-02-03); features/steps/plan_create_nominal_steps.py (1 step def).
- Files modified: src/gzkit/commands/plan.py (rename _next_available_foundation_semver -> _next_free_nominal_foundation_id; update sole call site + error message); tests/test_taxonomy_validator_nominal.py (coupled-surface AGENTS.md§1a — removed obsolete import + test_plan_allocator_is_unchanged); .gzkit/skills/gz-adr-create/SKILL.md (description + govzero-compliance-areas updated; skill-version 6.4.2->6.5.0; last_reviewed 2026-05-21->2026-05-23); docs/user/manpages/plan-create.md (error-hint language -> nominal-allocator semantics); tests/governance/test_foundation_invariance_skill_enrichment.py (coupled-surface §1a — expected gz-adr-create version 6.4.2->6.5.0); data/behave_coverage_waivers.json (REQ-02/04/05/06/07 non-CLI-surface waiver).
- Tests added: 8 unit + 2 BDD scenarios + 1 step def. Coverage 6/7 mechanical; REQ-07 is the attestation gate itself (waived via --accept-uncovered).
- Date completed: 2026-05-23.
- Attestation status: attest completed (operator verbatim).
- Defects noted: none.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.57-02 lands the foundation ADR nominal allocator (max+1 odometer → lowest-unused-integer gap-fill). 5449/5449 tests pass (arb-step-unittest-889d9e6ddbf544e7ab8e167f580c559c), ruff clean (arb-ruff-76eab7ef166a438e90a41060c7d3534b), typecheck clean (arb-step-typecheck-8801ff81889c4a6f874a2e6044d34a65), mkdocs --strict clean (arb-step-mkdocs-46586bdb5a6445199174e12661d5968f), 2/2 scoped BDD scenarios pass (arb-step-behave-110aab8648974de59668b3052020e2eb). REQ-coverage 6/7 mechanical; REQ-07 is the attestation itself.
- Date: 2026-05-23

---

**Date Completed:** 2026-05-23

**Evidence Hash:** -
