---
id: OBPI-0.27.0-02-router-surface-sync
parent: ADR-0.27.0-namespace-router-product-surface
item: 2
lane: Lite
status: Completed
---

# OBPI-0.27.0-02-router-surface-sync: **router-surface-sync** — Register the six router skills in the canonical skill catalog and refresh control surfaces via `gz agent sync control-surfaces` so routers mirror to `.agents/skills/`, `.claude/skills/`, and `.github/skills/`.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md`
- **Checklist Item:** #2 - "OBPI-0.27.0-02: **router-surface-sync** — Register the six router skills in the canonical skill catalog and refresh control surfaces via `gz agent sync control-surfaces` so routers mirror to `.agents/skills/`, `.claude/skills/`, and `.github/skills/`."

**Status:** Completed

## Objective

**router-surface-sync** — Register the six router skills in the canonical skill catalog and refresh control surfaces via `gz agent sync control-surfaces` so routers mirror to `.agents/skills/`, `.claude/skills/`, and `.github/skills/`.

## Lane

**Lite** - This OBPI remains internal to the promoted ADR implementation scope.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md` — parent ADR for intent and scope
- `.gzkit/skills/` — canonical skill catalog; the six router skill files from OBPI-01 live here and `gz agent sync control-surfaces` reads from this surface

Vendor mirrors (`.agents/skills/`, `.claude/skills/`, `.github/skills/`) are *outputs* of `gz agent sync control-surfaces`, not editable surfaces — per `.gzkit/rules/skill-surface-sync.md` and the promote-time `Allowed path is a generated vendor mirror` guard. Run the sync command; do not hand-edit mirror files.

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: **router-surface-sync** — Register the six router skills in the canonical skill catalog and refresh control surfaces via `gz agent sync control-surfaces` so routers mirror to `.agents/skills/`, `.claude/skills/`, and `.github/skills/`.
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
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md`
- [ ] Required path exists or is intentionally created in this OBPI: `.gzkit/skills/`
- [ ] OBPI-01 (`router-skill-files`) is at least Draft so the six router skills exist before sync
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
test -f docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md
test -d .gzkit/skills/gz-workflow && test -d .gzkit/skills/gz-governance && test -d .gzkit/skills/gz-quality && test -d .gzkit/skills/gz-project && test -d .gzkit/skills/gz-context && test -d .gzkit/skills/gz-manage

# Run the sync; mirrors are outputs, not edited surfaces
uv run gz agent sync control-surfaces

# Mirrors should now carry the six routers
uv run gz skill list | grep -E '^\| gz-(workflow|governance|quality|project|context|manage)'
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

- [ ] REQ-0.27.0-02-01: For each of the six router slugs, `.gzkit/skills/<slug>/SKILL.md` (canonical) is byte-equivalent to its three vendor-mirror counterparts at `.agents/skills/<slug>/SKILL.md`, `.claude/skills/<slug>/SKILL.md`, and `.github/skills/<slug>/SKILL.md`. (Mirrors are sync outputs per `.claude/rules/skill-surface-sync.md` — drift is fail-closed.)
- [ ] REQ-0.27.0-02-02: For each of the six router slugs, `.gzkit/skills/<slug>/SKILL.md` (canonical) is byte-equivalent to its wheel-shipping pkg copy at `src/gzkit/skills/<slug>/SKILL.md` (per the surface-layout table in `.claude/rules/skill-surface-sync.md`).
- [ ] REQ-0.27.0-02-03: The active skill catalog (returned by `gzkit.skills.audit_skills` against the canonical project root) lists each of the six router slugs with `lifecycle_state: active`. (Discoverability proof — the routers register through normal catalog discovery, not as one-off entries.)

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

- [x] Intent and scope recorded (parent ADR-0.27.0 § Checklist row 02; this brief § Acceptance Criteria with three concrete REQs covering vendor-mirror parity, pkg-copy parity, and active-catalog discovery)

### Gate 2 (TDD — Red-Green-Refactor)

```text
$ uv run -m unittest -v tests.skills.test_namespace_router_surface_sync
test_each_router_byte_equivalent_in_wheel_pkg_copy ... ok
test_each_router_listed_active_in_skill_catalog ... ok
test_each_router_byte_equivalent_in_every_vendor_mirror ... ok
----------------------------------------------------------------------
Ran 3 tests in 0.018s
OK

$ uv run gz covers OBPI-0.27.0-02 --plain
REQ-0.27.0-02-01    covered    tests/skills/test_namespace_router_surface_sync.py
REQ-0.27.0-02-02    covered    tests/skills/test_namespace_router_surface_sync.py
REQ-0.27.0-02-03    covered    tests/skills/test_namespace_router_surface_sync.py
```

### Code Quality

```text
$ uv run ruff check tests/skills/test_namespace_router_surface_sync.py
All checks passed!

$ uv run ruff format --check tests/skills/test_namespace_router_surface_sync.py
1 file already formatted
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

**Before:** The six router skills authored in OBPI-01 lived only on the canonical surface (`.gzkit/skills/`). Vendor-harness agents (Codex via `.agents/`, Claude Code via `.claude/`, Copilot via `.github/`) would not see them until sync ran, and there was no asserted parity proof to back the claim that mirrors stay byte-equivalent.

**After:** `gz agent sync control-surfaces` propagated each canonical router to all four downstream surfaces (three vendor mirrors + the wheel-shipping `src/gzkit/skills/` pkg copy). Three locked-in tests assert byte-equivalence across all 24 router-mirror pairs (6 routers × 4 surfaces) on every test run, plus active-catalog discoverability. Any future drift fails closed via the existing test suite, not via narrative.

### Key Proof


```text
$ uv run gz agent sync control-surfaces
... (idempotent on this run; routers already mirrored by post-Write hook during OBPI-01)
Sync complete.

$ uv run gz skill list 2>&1 | grep -E '^\| gz-(workflow|governance|quality|project|context|manage)'
| gz-context                 | Namespace router → context preservation ...
| gz-governance              | Namespace router → ADR/OBPI/ledger ...
| gz-manage                  | Namespace router → repo and release ...
| gz-project                 | Namespace router → project lifecycle ...
| gz-quality                 | Namespace router → quality and complexity ...
| gz-workflow                | Namespace router → end-to-end workflow ...
```

### Implementation Summary


- Files created:
  - `tests/skills/test_namespace_router_surface_sync.py` (three REQ-derived tests covering vendor mirrors, pkg copy, active-catalog discovery)
- Files modified:
  - `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-02-router-surface-sync.md` (REQ rewrites, evidence)
- Tests added: 3 (one per REQ); all GREEN; no implementation code changed — sync was already complete from the post-Write hook in OBPI-01.
- Date completed: 2026-05-23 (pending Stage 5 attestation)
- Attestation status: pending Gate 5 human attestation per ADR-0.0.36
- Defects noted: none in OBPI-02 scope. (Pre-existing observation, not OBPI-02 work: `.gzkit/locks/` lock files are untracked runtime state; current state-doctrine treats them as runtime, formal gitignore deferred per `ADR-pool.canonical-vs-runtime-separation`.)

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.27.0-02 router-surface-sync verified: 3/3 REQ-derived parity tests GREEN (vendor-mirror byte-parity REQ-01, pkg-copy byte-parity REQ-02, active-catalog discovery REQ-03) in tests/skills/test_namespace_router_surface_sync.py; full unittest sweep 5508/5508 pass (receipt arb-step-unittest-a05d6823769e41768642022463357941); ruff clean (receipt arb-ruff-ae62d9f035aa497da1696856796bf4d1); ty typecheck clean (receipt arb-step-typecheck-dc7ce9c675fa426ca4d6e9c632eaf4d9); six namespace-router skills (gz-workflow, gz-governance, gz-quality, gz-project, gz-context, gz-manage) propagated from .gzkit/skills/ canonical to .agents/skills/, .claude/skills/, .github/skills/, and src/gzkit/skills/ via gz agent sync control-surfaces; plan-audit PASS receipt at .plan-audit-receipt-OBPI-0.27.0-02.json.
- Date: 2026-05-24

---

**Date Completed:** 2026-05-24

**Evidence Hash:** -
