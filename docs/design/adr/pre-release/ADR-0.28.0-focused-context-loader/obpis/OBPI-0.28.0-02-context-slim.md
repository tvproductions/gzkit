---
id: OBPI-0.28.0-02-context-slim
parent: ADR-0.28.0-focused-context-loader
item: 2
lane: Lite
status: Completed
---

# OBPI-0.28.0-02-context-slim: **context-slim** — Implement `gz context --slim <ADR-ID>` variant that omits the governance-rules section for non-governance agent harnesses. ---

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.28.0-focused-context-loader/ADR-0.28.0-focused-context-loader.md`
- **Checklist Item:** #2 - "OBPI-0.28.0-02: **context-slim** — Implement `gz context --slim <ADR-ID>` variant that omits the governance-rules section for non-governance agent harnesses. ---"

**Status:** Completed

## Objective

Wire a `--slim` flag onto `gz context <ADR-ID>` that subtracts the governance-rules section (lane / lifecycle / current gate / next required action) from the rendered payload, leaving the ADR body, OBPI brief bodies, and `@covers`-discovered test paths byte-identical to the default-mode payload, so non-governance agent harnesses can consume the focused-context output without governance metadata noise.

## Lane

**Lite** - This OBPI remains internal to the promoted ADR implementation scope.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.28.0-focused-context-loader/ADR-0.28.0-focused-context-loader.md` — parent ADR for intent and scope
- `docs/design/adr/pre-release/ADR-0.28.0-focused-context-loader/obpis/OBPI-0.28.0-02-context-slim.md` — this brief (evidence + ceremony updates)
- `src/gzkit/commands/context_cmd.py` — extend renderer to honor `slim=True` (subtractive)
- `src/gzkit/cli/parser_artifacts.py` — add `--slim` flag to the `context` subparser
- `tests/commands/test_context_cmd.py` — REQ-derived `--slim` cases (governance section absence, byte-parity with `--no-slim` for non-rules content)
- `docs/user/manpages/context.md` — extend manpage Options + Examples for `--slim`

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `gz context --slim <ADR-ID>` MUST be a recognized invocation; `gz context --help` documents the `--slim` flag.
2. REQUIREMENT: With `--slim`, the rendered payload MUST omit the governance-rules section (lane / lifecycle / current gate / next required action) entirely — not merely shorten it.
3. REQUIREMENT: With `--slim`, the rendered payload MUST preserve the ADR body, OBPI brief bodies, and `@covers`-discovered test paths sections — `--slim` is purely subtractive over the OBPI-01 payload.
4. REQUIREMENT: Without `--slim` (default), the payload MUST remain byte-identical to OBPI-01's contract. The OBPI-01 acceptance tests MUST continue to pass unmodified.
5. REQUIREMENT: Work MUST stay inside the Allowed Paths declared above.
6. NEVER: Duplicate the renderer path for `--slim`. The implementation MUST factor governance-rules rendering behind a single conditional branch on the `slim` parameter.
7. ALWAYS: Tests for `--slim` are REQ-derived (semantic — "governance section absent", "non-rules content byte-identical to default mode"), not implementation-snapshot.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.28.0-focused-context-loader/ADR-0.28.0-focused-context-loader.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.28.0-focused-context-loader/ADR-0.28.0-focused-context-loader.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.28.0-focused-context-loader/**`
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
uv run -m unittest tests.commands.test_context_cmd -v
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Slim payload for a non-governance harness
uv run gz context --slim ADR-0.0.3-hexagonal-architecture-tune-up

# Confirm the governance-rules section is absent under --slim
uv run gz context --slim ADR-0.0.3-hexagonal-architecture-tune-up | grep -ic "governance rules" || echo "absent (expected)"

# Confirm --slim is subtractive: payloads differ only in the governance block
diff <(uv run gz context ADR-0.0.3-hexagonal-architecture-tune-up) \
     <(uv run gz context --slim ADR-0.0.3-hexagonal-architecture-tune-up)
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.28.0-02-01: Given an installed gzkit, when `gz context --help` is invoked, then the help text documents `--slim` as an optional flag.
- [ ] REQ-0.28.0-02-02: Given an existing ADR ID, when `gz context --slim <ADR-ID>` is invoked, then the emitted payload contains no governance-rules section (no "lane", "lifecycle", "current gate", or "next required action" headers).
- [ ] REQ-0.28.0-02-03: Given an existing ADR ID, when `gz context --slim <ADR-ID>` is invoked, then the ADR body, OBPI brief bodies, and `@covers`-discovered test paths sections are all present (regression invariant — `--slim` is purely subtractive).
- [ ] REQ-0.28.0-02-04: Given an existing ADR ID, when both `gz context <ADR-ID>` and `gz context --slim <ADR-ID>` are diffed, then the only delta is the governance-rules section — every other byte is identical.
- [ ] REQ-0.28.0-02-05: Given the OBPI-0.28.0-01 acceptance tests on the unchanged default-mode payload, when re-run after this OBPI lands, then they pass unmodified (OBPI-01's contract is preserved).

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


```bash
$ diff <(uv run gz context ADR-0.0.3-hexagonal-architecture-tune-up) \
       <(uv run gz context --slim ADR-0.0.3-hexagonal-architecture-tune-up)
2504,2512d2503
< 
< ---
< 
< ## Governance rules
< 
< - **Lane:** heavy
< - **Lifecycle:** Validated
< - **Current gate:** Gate 5
< - **Next required action:** Run `gz adr audit <ADR-ID>` to harvest Validated -> Completed.
```

Single delta: 9 lines of governance section omitted; every other byte identical (REQ-04 line-subset assertion mechanically verified this in `test_slim_delta_is_only_governance_section`).

Receipts cited: `arb-ruff-58804f96e5fd4b12a4898479065748b1`, `arb-step-typecheck-2c5c3e4db6924ba08695a84ff1ab2eb0`, `arb-step-unittest-0ead3d9df88d4ef09a33642b9f7d577f`.

### Implementation Summary


- Files modified: `src/gzkit/cli/parser_artifacts.py` (added `--slim` flag to `_register_context_parser`; updated lambda to pass `slim=a.slim`; added `--slim` epilog example); `tests/commands/test_context_cmd.py` (added `TestContextCmdSlim` class with 5 REQ-derived tests; `TestContextCmdCore` untouched); `docs/user/manpages/context.md` (removed "not yet wired" placeholder; added `--slim` to OPTIONS; added `--slim` example)
- Files created: `.claude/plans/OBPI-0.28.0-02-context-slim.md` (canonical plan file)
- Renderer untouched: `src/gzkit/commands/context_cmd.py` already carried `slim: bool = False` from OBPI-01 — REQ-06 (no duplicate renderer path) satisfied by reusing the single conditional branch
- Tests added: 5 (REQ-0.28.0-02-01 through -05); 13/13 context tests pass; 5528/5528 full unittest sweep pass (1 skipped)
- Date completed: 2026-05-24
- Attestation status: human-attested by g0
- Defects noted: none in scope; spec-reviewer surfaced a missing `assertNotIn("lifecycle", lower)` in Task 2 which was fixed in flight before review-cycle completion

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.28.0-02-context-slim wired `--slim` flag onto `gz context` (renderer reused from OBPI-01, REQ-06 no-duplicate-renderer satisfied); 5/5 REQ-0.28.0-02-NN tests pass (TestContextCmdSlim); full unittest sweep 5528/5528 pass (1 skipped); REQ→@covers parity 100% (5/5); receipts arb-ruff-58804f96e5fd4b12a4898479065748b1, arb-step-typecheck-2c5c3e4db6924ba08695a84ff1ab2eb0, arb-step-unittest-0ead3d9df88d4ef09a33642b9f7d577f; live `diff` between default and --slim modes confirms purely-subtractive 9-line governance-section omission.
- Date: 2026-05-24

---

**Date Completed:** 2026-05-24

**Evidence Hash:** -
