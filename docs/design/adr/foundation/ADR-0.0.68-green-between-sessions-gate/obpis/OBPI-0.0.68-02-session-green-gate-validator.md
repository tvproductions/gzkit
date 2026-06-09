---
id: OBPI-0.0.68-02-session-green-gate-validator
parent: ADR-0.0.68-green-between-sessions-gate
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.68-02-session-green-gate-validator: Session Green Gate Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.68-green-between-sessions-gate/ADR-0.0.68-green-between-sessions-gate.md`
- **Checklist Item:** #2 - "OBPI-0.0.68-02: Implement `gz validate --session-green-gate` as a fail-closed floor — parse `.pre-commit-config.yaml`, exit 3 if no `stages: [pre-push]` hook running `gz check` is declared, wire the scope into the `gz check` default scope, add the manpage/docs and a fail-close regression test (Heavy)"

**Status:** Draft

## Objective

Implement `gz validate --session-green-gate` as a fail-closed floor — parse `.pre-commit-config.yaml`, exit 3 if no `stages: [pre-push]` hook running `gz check` is declared, wire the scope into the `gz check` default scope, add the manpage/docs and a fail-close regression test (Heavy).

## Lane

**Heavy** - Adds a new `gz validate --session-green-gate` scope — a CLI/runtime
contract surface — and wires it into the `gz check` default scope. A new validator
flag with a documented exit-3 contract and a manpage entry is exactly the
command/runtime-contract change Heavy lane is reserved for.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/quality.py` — the `run_session_green_gate_audit` function (parse `.pre-commit-config.yaml`; fail-close exit 3 if no `pre-push` `gz check` hook is declared)
- `src/gzkit/commands/quality.py` — wire the new audit into the `gz check` default scope (the audit list near `check()`)
- `src/gzkit/commands/validate_cmd.py` — dispatch the `--session-green-gate` scope
- `src/gzkit/cli/parser_maintenance.py` — register the `--session-green-gate` flag on the `gz validate` parser
- `docs/user/manpages/validate.md` — document the new scope and its exit-3 contract
- `tests/**` — fail-close regression test for the new scope
- `docs/design/adr/foundation/ADR-0.0.68-green-between-sessions-gate/obpis/OBPI-0.0.68-02-session-green-gate-validator.md` — this brief

> The exact module homes above are the current locations of the validate-scope
> machinery; if a refactor has moved them, locate the real home before editing and
> note the divergence — do not author against a stale path.

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.pre-commit-config.yaml` — the pre-push hook declaration is OBPI-01's scope; this OBPI only *reads* it
- `docs/user/runbook.md` — the install-step doc is OBPI-01's scope
- Hardcoding a frozen validator list into the gate (parent ADR Alternative 4 — the gate is `gz check` delegation)
- New runtime dependencies; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `gz validate --session-green-gate` MUST exit 3 when `.pre-commit-config.yaml` declares no `stages: [pre-push]` hook running `gz check`, and exit 0 when such a hook is declared. Fail-closed: an unparseable or missing config is treated as a violation, never a pass.
1. REQUIREMENT: The `--session-green-gate` scope MUST be part of the `gz check` default scope, so deleting the pre-push declaration turns the next `gz check` red (the floor enforces its own wiring).
1. REQUIREMENT: The gate MUST be expressed as `gz check` delegation, NOT a hardcoded validator list — it asserts the *declaration* of a `pre-push` `gz check` hook, so the forthcoming ln-sunset ADR needs zero rewiring of this gate.
1. REQUIREMENT: `docs/user/manpages/validate.md` MUST document the new scope and its exit-3 contract; `gz cli audit` and `mkdocs build --strict` MUST stay green.
1. NEVER: edit `.pre-commit-config.yaml` or `docs/user/runbook.md` — those declaration/doc surfaces are OBPI-01's scope; this OBPI only reads the config.
1. ALWAYS: reconcile this brief against the parent ADR § Decision items (2) and (3) before implementation begins.

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

- [ ] OBPI-0.0.68-01 has landed (the `pre-push` `gz check` declaration exists in `.pre-commit-config.yaml` for the green-path test fixture)
- [ ] `src/gzkit/quality.py` audit-function pattern reviewed (e.g. `run_adr_status_fresh_audit` as the precedent shape)
- [ ] `src/gzkit/commands/quality.py` `check()` default-scope audit list located
- [ ] `docs/user/manpages/validate.md` exists (manpage home for the new scope)

**Existing Code (understand current state):**

- [ ] `run_adr_status_fresh_audit` / `run_command` pattern in `src/gzkit/quality.py` — model the new audit on it (precedent: `--adr-status-fresh` is the existing self-referential `gz check` scope)
- [ ] The `--session-green-gate` flag registration alongside existing scopes in `src/gzkit/cli/parser_maintenance.py`
- [ ] Existing validator-scope tests under `tests/**` for the fail-close test shape and fixtures

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
uv run gz validate --session-green-gate
uv run gz cli audit
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Green path: the declared pre-push gz check hook satisfies the floor:
uv run gz validate --session-green-gate
# Self-referential proof: the scope runs as part of the default gz check:
uv run gz check
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.68-02-01 [behavior]: Given a `.pre-commit-config.yaml` with no `stages: [pre-push]` hook running `gz check`, when `gz validate --session-green-gate` runs, then it exits 3; given one that declares such a hook, then it exits 0. (@covers test driving both fixtures)
- [ ] REQ-0.0.68-02-02 [behavior]: Given the `gz check` default scope, when it is enumerated, then `--session-green-gate` is included — so deleting the pre-push declaration turns the next `gz check` red. (@covers test asserting the scope is in the default `check()` audit set)
- [ ] REQ-0.0.68-02-03 [support]: `docs/user/manpages/validate.md` documents the `--session-green-gate` scope and its exit-3 contract. Proof: `artifact_edited` ledger event + `gz validate --documents` (doc-tree structural validator) + `gz cli audit` and `mkdocs build --strict` green.

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
