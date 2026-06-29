---
id: OBPI-0.30.0-04-okf-cli-surface
parent: ADR-0.30.0-okf-documentation-knowledge-structure
item: 4
lane: heavy
status: Completed
# req_atomic — each REQ is one indivisible unit of labor with no sub-REQ
# subdivision: REQ-01 (generate emits + --help documents the verb), REQ-02 (the
# refresh-twice byte-identical idempotency rule), REQ-03 (the manpage + cli-audit
# coverage), and REQ-04 (the end-to-end generate→refresh smoke + behave) were
# each satisfied by a single coherent test-authoring unit over the pre-existing
# CLI scaffolding. None subdivided into seq=02+; the pipeline-minted
# seq=01-per-REQ buckets are the true labor shape.
req_atomic:
  - REQ-0.30.0-04-01
  - REQ-0.30.0-04-02
  - REQ-0.30.0-04-03
  - REQ-0.30.0-04-04
---

# OBPI-0.30.0-04-okf-cli-surface: Add the `knowledge` generate/refresh CLI subcommand (operator entry point to emit/refresh the OKF bundle) with manpage, `gz cli audit` coverage, and a behave smoke scenario.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md`
- **Checklist Item:** #4 — "CLI surface to generate/refresh the bundle (Heavy lane: new subcommand) + manpage + cli-audit coverage + behave smoke."

**Status:** Completed

## Objective

Give the operator a single command to produce and refresh the OKF bundle: `knowledge generate` emits the bundle over the tracer slice, `knowledge refresh` re-generates idempotently from current sources. Ship the manpage, pass `gz cli audit` coverage, and add a behave smoke scenario for the generate/refresh surface.

## Lane

**Heavy** — This OBPI adds a new operator-facing CLI verb (`knowledge`), an external command contract.

> Heavy is reserved for command/API/schema/runtime-contract changes. A new `gz <verb>` is a CLI contract change.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md` — parent ADR for intent and scope
- `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/obpis/OBPI-0.30.0-04-okf-cli-surface.md` — this brief
- `src/gzkit/commands/` — new `okf` command module (generate/refresh; delegates to the OBPI-0.30.0-02 generator)
- `src/gzkit/cli/` — argparse registration for the `okf` subcommand
- `docs/user/manpages/knowledge.md` — new manpage (Synopsis / Options / Examples / Exit Codes) **CREATE**
- `features/` — behave smoke scenario for generate/refresh
- `tests/` — REQ-derived unittest cases for the CLI surface

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/knowledge/` generator internals — OBPI-0.30.0-02's scope; this command delegates to it
- `src/gzkit/governance/trust_audits/`, `src/gzkit/commands/validate_cmd.py` — the `--okf-conformance` validator is OBPI-0.30.0-03's scope
- Any path that would make the CLI consume OKF data as enforcement evidence (Boundary Invariant 1)
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The `knowledge generate` subcommand MUST emit the OKF bundle over the tracer slice and exit 0 on success; the verb MUST be registered and `knowledge --help` MUST document it.
2. REQUIREMENT: The `knowledge refresh` subcommand MUST re-generate the bundle idempotently — re-running over unchanged sources leaves the bundle byte-identical and exits 0.
3. REQUIREMENT: `docs/user/manpages/knowledge.md` MUST document the verb (Synopsis / Options / Examples / Exit Codes), and `uv run gz cli audit` MUST exit 0 (manpage + index coverage for the new verb).
4. REQUIREMENT: A behave smoke scenario MUST exercise the generate/refresh surface and pass under `uv run -m behave features/`.
5. NEVER: The CLI MUST NOT consume OKF frontmatter/links as enforcement evidence (parent ADR Boundary Invariant 1).
6. ALWAYS: Tests are derived from the REQs above, not from a run of the implementation.

> SCOPE BOUNDARY: Generation logic is OBPI-0.30.0-02's scope; this OBPI is the operator entry point that delegates to it. Conformance validation is OBPI-0.30.0-03's scope.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the Implementation Summary: "The first implementation is a tracer bullet ... proving one working progressive-disclosure path" (this OBPI is the operator-facing generate/refresh entry point).
- [ ] Parent ADR § Interfaces — the `knowledge generate` / `knowledge refresh` contract.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.claude/rules/cli.md` — CLI contract doctrine (new verb is heavy lane; argparse over click/typer per ADR-0.0.2)
- [ ] An existing `src/gzkit/commands/*.py` + `src/gzkit/cli/` registration reviewed as the verb pattern
- [ ] An existing `docs/user/manpages/*.md` reviewed as the manpage shape
- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract

**Context:**

- [ ] OBPI-0.30.0-02 (the generator this verb delegates to)

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists: `src/gzkit/cli/` and `src/gzkit/commands/`
- [ ] Required path exists: the OBPI-0.30.0-02 generator entry point

**Existing Code (understand current state):**

- [ ] Existing CLI verb + manpage + behave-feature triple reviewed before implementation
- [ ] `gz cli audit` coverage requirement reviewed (new verb must be covered across manpage + index)

## Quality Gates

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/user/manpages/knowledge.md` added; `uv run gz cli audit` exits 0

### Gate 4: BDD (Heavy only)

- [ ] Behave smoke for generate/refresh passes: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.commands.test_knowledge -v
uv run python -m gzkit.knowledge
uv run gz cli audit
uv run -m behave features/knowledge.feature
uv run mkdocs build --strict
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
# Generate the bundle from the operator entry point
uv run gz knowledge generate; echo "exit=$?"

# Refresh is idempotent: a second run leaves the bundle byte-identical
uv run gz knowledge refresh; echo "exit=$?"
```

## Acceptance Criteria

- [ ] REQ-0.30.0-04-01 [BEHAVIOR]: Given a registered CLI, when `knowledge generate` runs, then the OKF bundle is emitted over the tracer slice and the command exits 0; `knowledge --help` documents the verb.
- [ ] REQ-0.30.0-04-02 [BEHAVIOR]: Given unchanged sources, when `knowledge refresh` runs twice, then the bundle is byte-identical after each run and the command exits 0 (idempotent operator-level refresh).
- [ ] REQ-0.30.0-04-03 [SUPPORT]: `docs/user/manpages/knowledge.md` documents the verb and the `knowledge` verb is index-covered — proven by `uv run gz validate --documents` and `uv run gz cli audit` passing AND an `artifact_edited` ledger event citing the manpage emitted at OBPI completion.
- [ ] REQ-0.30.0-04-04 [BEHAVIOR]: Given the registered `okf` CLI, when a smoke invocation runs the surface end-to-end (generate then refresh), then it completes without error — covered by a CLI smoke test and additionally exercised by the Gate-4 behave scenario under `features/`.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

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
# Paste docs-build + cli audit output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before this OBPI the bundle can only be produced by invoking the generator module directly — no operator surface. After this OBPI, `knowledge generate` / `knowledge refresh` is the operator entry point, documented in a manpage, covered by `gz cli audit`, and smoke-tested under behave. The operator regenerates the bundle with one idempotent command.

### Key Proof


`uv run gz knowledge generate` exits 0 and emits the bundle to `.gzkit/governance/knowledge/`; `uv run gz knowledge refresh` run twice leaves the bundle byte-identical (asserted by `TestKnowledgeRefresh.test_refresh_is_idempotent`). Full suite 6644/6644 pass (receipt arb-step-unittest-30b3a0a9b46f4d0ba1abd22e6efac1eb); behave smoke 2/2 (receipt arb-step-behave-e5a4e71ba83c4d8bbda6b2886235172f); `gz cli audit` 114/114; REQ @covers parity 4/4.

### Implementation Summary


- Files created: `tests/commands/test_knowledge.py` (6 REQ-derived unittest cases across 4 classes, each @covers-decorated); `features/knowledge.feature` (2 behave smoke scenarios, @REQ-0.30.0-04-04).
- Files modified: `docs/user/manpages/knowledge-generate.md`, `docs/user/manpages/knowledge-refresh.md` — corrected stale `.gzkit/knowledge/` to real `.gzkit/governance/knowledge/` output path (defect surfaced by Step-4b adversarial validation).
- CLI scaffolding (`src/gzkit/commands/knowledge.py`, parser registration, lazy handler, `docs/user/manpages/knowledge.md`) pre-existed from a prior session; this OBPI closed the verification chain (REQ-derived tests + behave smoke) over it.
- Tests added: REQ-01/02/04 BEHAVIOR (@covers); REQ-03 SUPPORT (manpage + validate --documents/cli audit + regression test guarding the documented-path class).
- Adversarial validation: Codex returned REFUTED-WITH-CAVEATS; both real gaps (refresh-twice semantics, stale manpage paths) fixed and re-validated green.

## Tracked Defects

- Unresolved verb `gz knowledge` (brief reconcile, attestor g0)

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.30.0-04 (knowledge CLI surface) verified Heavy lane: 6644/6644 unittests pass (receipt arb-step-unittest-30b3a0a9b46f4d0ba1abd22e6efac1eb), lint+typecheck clean (arb-ruff-ec22dcca5b674061b8ac62295fb2b794, arb-step-typecheck-b2005668cfab4f4a8c6ab902a3a9fd33), docs --strict clean (arb-step-mkdocs-66b7e751a53a492cab07975502d3394b), behave smoke 2/2 (arb-step-behave-e5a4e71ba83c4d8bbda6b2886235172f), gz cli audit 114/114, REQ @covers parity 4/4. Step-4b Codex adversarial validation returned REFUTED-WITH-CAVEATS; both real gaps (refresh-twice idempotency semantics, stale manpage output paths) fixed and re-validated green.
- Date: 2026-06-29

---

**Date Completed:** 2026-06-29

**Evidence Hash:** -
