---
id: OBPI-0.0.68-01-pre-push-gz-check-hook
parent: ADR-0.0.68-green-between-sessions-gate
item: 1
lane: Lite
status: Draft
---

# OBPI-0.0.68-01-pre-push-gz-check-hook: Pre Push Gz Check Hook

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.68-green-between-sessions-gate/ADR-0.0.68-green-between-sessions-gate.md`
- **Checklist Item:** #1 - "OBPI-0.0.68-01: Declare and install the pre-push `gz check` hook — add a `pre-push` stage to `.pre-commit-config.yaml` running `gz check`, document `pre-commit install --hook-type pre-push` in the setup/runbook doc, and install it locally so the gate enforces immediately (Lite)"

**Status:** Draft

## Objective

Declare and install the pre-push `gz check` hook — add a `pre-push` stage to `.pre-commit-config.yaml` running `gz check`, document `pre-commit install --hook-type pre-push` in the setup/runbook doc, and install it locally so the gate enforces immediately (Lite).

## Lane

**Lite** - Adds a version-controlled pre-commit hook stage and a runbook line; it
introduces no CLI/schema/runtime contract surface of its own (the fail-closed
validator surface is OBPI-02, Heavy). The pre-push hook merely *runs* the existing
`gz check` verb — it does not change it.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `.pre-commit-config.yaml` — add a `stages: [pre-push]` hook whose entry runs `gz check`
- `docs/user/runbook.md` — document the one-time `pre-commit install --hook-type pre-push` setup step
- `tests/**` — the `@covers` test that parses `.pre-commit-config.yaml` and asserts the pre-push `gz check` hook is declared
- `docs/design/adr/foundation/ADR-0.0.68-green-between-sessions-gate/obpis/OBPI-0.0.68-01-pre-push-gz-check-hook.md` — this brief

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/**` — the `--session-green-gate` validator implementation is OBPI-02's scope, not this brief's
- Any other `gz validate` scope wiring (OBPI-02 owns the fail-closed floor)
- New runtime dependencies; lockfiles
- The existing `manual`-staged unittest hook (do not flip its stage — see parent ADR Alternative 3)

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `.pre-commit-config.yaml` MUST declare a hook with `stages: [pre-push]` whose entry invokes `gz check` (the version-controlled declaration is the artifact the OBPI-02 validator reads).
1. REQUIREMENT: `docs/user/runbook.md` MUST document the one-time `pre-commit install --hook-type pre-push` step so a fresh clone becomes enforcing.
1. REQUIREMENT: The hook MUST be installed locally (`pre-commit install --hook-type pre-push`) so the gate enforces immediately in this working tree.
1. NEVER: flip the existing `manual`-staged unittest hook to `pre-commit` or `pre-push` frequency (parent ADR Alternative 3 — wrong boundary).
1. NEVER: add or modify any `gz validate` scope or `src/gzkit/**` module — that is OBPI-02's fail-closed-floor scope.
1. ALWAYS: reconcile this brief against the parent ADR § Decision item (1) before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.68-green-between-sessions-gate/ADR-0.0.68-green-between-sessions-gate.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] `.pre-commit-config.yaml` exists at the repo root and is parseable
- [ ] `gz check` runs end-to-end (the verb the hook will invoke)
- [ ] `pre-commit` is available in the environment (`pre-commit --version`)
- [ ] `docs/user/runbook.md` exists (the setup-step home)

**Existing Code (understand current state):**

- [ ] The existing `manual`-staged unittest hook in `.pre-commit-config.yaml` reviewed (do not change its stage)
- [ ] Current `.git/hooks/` state reviewed to confirm no pre-push hook is installed yet
- [ ] `gz check` default scope reviewed so the hook entry matches the canonical invocation

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

# Specific verification for this OBPI
uv run pre-commit run --hook-stage pre-push --all-files
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# The pre-push hook fires gz check at the session boundary (push):
uv run pre-commit run --hook-stage pre-push --all-files
# Inspect the version-controlled declaration that makes the gate portable:
uv run pre-commit install --hook-type pre-push
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.68-01-01 [behavior]: Given `.pre-commit-config.yaml`, when it is parsed, then it declares a hook with `stages: [pre-push]` whose entry invokes `gz check`. (@covers test parsing the config and asserting the pre-push `gz check` hook is present)
- [ ] REQ-0.0.68-01-02 [support]: `docs/user/runbook.md` documents the one-time `pre-commit install --hook-type pre-push` setup step. Proof: `artifact_edited` ledger event for the runbook + `gz validate --documents` (doc-tree structural validator) + `mkdocs build --strict` green.

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
