---
id: OBPI-0.44.0-02-codex-hooks-policy
parent: ADR-0.44.0-vendor-alignment-codex
item: 2
lane: Heavy
status: Draft
sensitivity: security
---

# OBPI-0.44.0-02-codex-hooks-policy: Codex Hooks Policy

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md`
- **Checklist Item:** #2 - "OBPI-0.44.0-02: **codex-hooks-policy** — Generate current Codex hook registration and vendor-native adapters for ten direct lifecycle behaviors, with two `ExitPlanMode` behaviors enforced by runtime substitutes"

**Status:** Draft

## Objective

Control-surface sync emits current Codex hook registration and thin payload
adapters whose observed allow, deny, and feedback decisions match the ten
direct Claude lifecycle behaviors, while the two `ExitPlanMode` behaviors stay
authoritative in the harness-neutral runtime delivered by OBPI-04.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md` — parent ADR and parity contract
- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/obpis/OBPI-0.44.0-02-codex-hooks-policy.md` — this contract and evidence
- `src/gzkit/config.py` — configured Codex hook paths
- `src/gzkit/hooks` — shared policy core and vendor adapters
- `src/gzkit/sync_surfaces.py` — deterministic hook sync wiring
- `src/gzkit/mx/awareness.py` — cross-vendor liveness validation
- `.codex/hooks.json` — generated Codex registration
- `.codex` — generated Codex registration and command adapters
- `.claude/hooks` — regenerated Claude adapters when shared policy changes
- `tests/test_hooks.py` — registration and adapter parity tests
- `tests/test_codex_config_surface.py` — obsolete-shape negative control
- `tests/test_sync.py` — generated surface idempotence
- `tests/governance/test_orientation_freshness.py` — current-schema orientation proof
- `features/agent_sync.feature` — operator-visible generated-hook behavior
- `docs/user` — hook trust and parity documentation

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.agents/**` — skills and personas belong to OBPI-03
- `.codex/agents/**` — role generation belongs to OBPI-03
- `src/gzkit/pipeline_markers.py` — harness-neutral state must land in OBPI-04 first
- `.gzkit/ledger.jsonl` direct edits
- Paths not listed in Allowed Paths
- New dependencies, CI files, and lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Render the current event -> matcher group -> command-handler schema;
   every handler uses `type: command` and a string command anchored to git root.
2. REQUIREMENT: Compose ordered pre-edit, post-edit, and pre-Bash policy chains because
   Codex launches sibling matching handlers concurrently.
3. REQUIREMENT: Normalize `apply_patch` commands into all target paths and before/after
   mutations before evaluating staleness, pipeline, completion, instruction,
   Ruff, and ledger policy.
4. REQUIREMENT: Adapt stable Codex session/assistant fields for commit, triage,
   stop, and MX behavior without parsing an unstable transcript when a stable
   event field exists.
5. REQUIREMENT: Preserve user-owned matcher groups, refresh each gzkit-owned
   group exactly once, and document project-hook hash review without a routine
   trust-bypass path.
6. NEVER: Duplicate the two `ExitPlanMode` policies in a hook or rely on a hook
   as the only fail-closed enforcement boundary.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md`
- [ ] Required path exists or is intentionally created in this OBPI: `.codex/hooks.json`
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
uv run -m unittest tests.test_hooks tests.test_codex_config_surface tests.test_sync tests.governance.test_orientation_freshness
uv run gz validate --orientation-freshness
uv run gz agent sync control-surfaces --dry-run
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
uv run gz validate --orientation-freshness
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.44.0-02-01 [BEHAVIOR]: Given generated Codex hooks, Codex 0.144.1 discovers one ordered gzkit command handler for each configured lifecycle group and no obsolete flat handler remains.
- [ ] REQ-0.44.0-02-02 [BEHAVIOR]: Given equivalent Claude edit input and Codex `apply_patch` input, the normalized policy returns the same allow, deny, or corrective-feedback decision for every target file.
- [ ] REQ-0.44.0-02-03 [BEHAVIOR]: Given Python edits and artifact edits, the ordered post-edit composite reports Ruff feedback before recording each artifact mutation exactly once.
- [ ] REQ-0.44.0-02-04 [BEHAVIOR]: Given commit/push, triage, stop, and MX lifecycle fixtures, Codex exposes the same reminder, silence, feedback, and awareness semantics as Claude.
- [ ] REQ-0.44.0-02-05 [BEHAVIOR]: Given user-owned matcher groups, repeated sync preserves them and renders every gzkit-owned group exactly once.
- [ ] REQ-0.44.0-02-06 [BEHAVIOR]: Given the two `ExitPlanMode` policies, the Codex registration contains no false event mapping and tests prove OBPI-04 runtime substitutes enforce both decisions.

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

- Parent Decision quote: **codex-hooks-policy** — Generate current Codex hook registration and vendor-native adapters for ten direct lifecycle behaviors, with two `ExitPlanMode` behaviors enforced by runtime substitutes
- Planned files: shared hook policy, Codex and regenerated Claude adapters, sync wiring, tests, BDD, and hook documentation listed in Allowed Paths
- Tests added: pending TDD execution
- Date completed: pending
- Attestation status: pending Gate 5
- Defects noted: current `.codex/hooks.json` is inert under Codex 0.144.1 and is corrected by this OBPI

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
