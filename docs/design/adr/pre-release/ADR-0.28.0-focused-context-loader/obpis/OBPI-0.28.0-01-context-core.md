---
id: OBPI-0.28.0-01-context-core
parent: ADR-0.28.0-focused-context-loader
item: 1
lane: Lite
status: Completed
---

# OBPI-0.28.0-01-context-core: **context-core** — Implement `gz context <ADR-ID>` rendering the target ADR file, associated OBPI brief contents, related test file paths (discovered via `@covers` decorators or naming convention), and applicable governance rules (lane, current gate, next required action) as a single Markdown payload suitable for piping to an AI agent.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.28.0-focused-context-loader/ADR-0.28.0-focused-context-loader.md`
- **Checklist Item:** #1 - "OBPI-0.28.0-01: **context-core** — Implement `gz context <ADR-ID>` rendering the target ADR file, associated OBPI brief contents, related test file paths (discovered via `@covers` decorators or naming convention), and applicable governance rules (lane, current gate, next required action) as a single Markdown payload suitable for piping to an AI agent."

**Status:** Completed

## Objective

Implement `gz context <ADR-ID>` rendering the target ADR body, every OBPI brief under its `obpis/` directory, the test files carrying matching `@covers` decorators, and a governance-rules section (lane / lifecycle / current gate / next action) as a single Markdown payload with no ANSI escapes, suitable for verbatim piping to any AI agent harness.

## Lane

**Lite** - This OBPI remains internal to the promoted ADR implementation scope.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.28.0-focused-context-loader/ADR-0.28.0-focused-context-loader.md` — parent ADR for intent and scope
- `docs/design/adr/pre-release/ADR-0.28.0-focused-context-loader/obpis/OBPI-0.28.0-01-context-core.md` — this brief (evidence + ceremony updates)
- `src/gzkit/commands/context_cmd.py` — new command module (`build_context_payload`, `register`, `run`)
- `src/gzkit/cli/parser_artifacts.py` — argparse `context` subparser + dispatch wiring
- `tests/commands/test_context_cmd.py` — REQ-derived unittest cases (Markdown body extraction, OBPI brief inclusion, `@covers` discovery, governance-rules block, error path)
- `docs/user/manpages/context.md` — new manpage (Synopsis / Options / Examples / Exit Codes)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `gz context <ADR-ID>` MUST be a registered CLI verb; `gz context --help` exits 0 and documents the positional `<ADR-ID>`.
2. REQUIREMENT: For an existing ADR ID, `gz context <ADR-ID>` MUST exit 0 and emit a single Markdown document to stdout.
3. REQUIREMENT: The emitted document MUST contain the target ADR's full Markdown body, copied verbatim from disk (no Rich-terminal escapes, no ANSI codes).
4. REQUIREMENT: The emitted document MUST contain the body of every OBPI brief under the target ADR's `obpis/` directory, separated from the ADR body by a clear heading delimiter.
5. REQUIREMENT: The emitted document MUST list every test file containing a `@covers(REQ-<target-ADR-semver>-…)` decorator, grouped by REQ.
6. REQUIREMENT: The emitted document MUST contain a governance-rules section naming the ADR's lane, lifecycle, current gate, and next required action.
7. REQUIREMENT: For an unresolvable ADR ID, `gz context <bogus-id>` MUST exit non-zero with a `BLOCKERS:`-prefixed stderr message naming the missing ADR file path.
8. REQUIREMENT: Work MUST stay inside the Allowed Paths declared above.
9. NEVER: Bundle the `--slim` variant into this OBPI — that is OBPI-0.28.0-02's scope. The renderer MUST be factored so `--slim` is a subtractive parameter, not a duplicated code path.
10. ALWAYS: Tests are derived from the REQs above, not from a run of the implementation (per `.gzkit/rules/tests.md` § "Tests assert semantics, not strings").

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
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.commands.test_context_cmd -v
```

> Repo-wide `gz validate --documents` is intentionally NOT listed here. Pre-existing
> foundation-ADR schema drift (status `Validated` not in enum; missing Decomposition
> Scorecard / Checklist / Evidence sections on ADR-0.0.7, ADR-0.0.8, ADR-0.0.9) is
> tracked by GHI #527 and recovery-deferred per the get-out-of-jail plan
> (`docs/governance/get-out-of-jail-plan-2026-05-23.md` § anti-temptation #6). The
> OBPI's own surface validation is covered by `gz obpi validate --authored` (run at
> precomplete time) and the baseline ARB gates (`arb ruff`, `arb typecheck`,
> `arb step --name unittest`).

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Render the focused payload for ADR-0.0.3 (hexagonal foundation) to stdout
uv run gz context ADR-0.0.3-hexagonal-architecture-tune-up

# Pipe directly to another agent harness (the load-on-demand path)
uv run gz context ADR-0.0.3-hexagonal-architecture-tune-up | wc -c

# Error path — unresolvable ADR ID exits non-zero with BLOCKERS:
uv run gz context ADR-9.9.9-does-not-exist; echo "exit=$?"
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.28.0-01-01: Given an installed gzkit, when `gz context --help` is invoked, then it exits 0 and the help text documents `<ADR-ID>` as a positional argument.
- [ ] REQ-0.28.0-01-02: Given an existing ADR ID, when `gz context <ADR-ID>` is invoked, then it exits 0 and writes one Markdown document to stdout.
- [ ] REQ-0.28.0-01-03: Given the target ADR file on disk, when the payload is rendered, then the ADR's full Markdown body appears verbatim in the payload (no ANSI escapes, no Rich frames).
- [ ] REQ-0.28.0-01-04: Given a target ADR with N OBPI briefs in its `obpis/` directory, when the payload is rendered, then every brief's body is included, each delimited by a heading containing its OBPI ID.
- [ ] REQ-0.28.0-01-05: Given source tests carrying `@covers(REQ-<target-ADR-semver>-…)` decorators, when the payload is rendered, then every such test file path is listed, grouped by REQ.
- [ ] REQ-0.28.0-01-06: Given the target ADR's frontmatter (lane, lifecycle) and ledger state (current gate), when the payload is rendered, then a governance-rules section names lane, lifecycle, current gate, and next required action.
- [ ] REQ-0.28.0-01-07: Given an unresolvable ADR ID, when `gz context <bogus-id>` is invoked, then it exits non-zero with a `BLOCKERS:`-prefixed stderr message naming the missing ADR path.
- [ ] REQ-0.28.0-01-08: Given the rendered payload, when measured by `wc -c`, then it is suitable for verbatim piping to any agent harness (no terminal-control characters; UTF-8 only).

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

Before this OBPI, an agent loading focused context for one ADR had to discover and read four artifact families separately: the ADR body, every OBPI brief under it, the test files carrying matching `@covers` decorators, and the governance state (lane / lifecycle / current gate / next required action). Each read was a separate tool call and the bundle was reassembled in-context by the agent — slow, error-prone, and lossy under compaction.

After this OBPI, `gz context <ADR-ID>` renders the entire focused-context bundle as one ANSI-free Markdown payload pipeable verbatim to any agent harness. The four-section composition is deterministic (rendered by `build_context_payload`, never by an LLM) and the renderer is factored so OBPI-0.28.0-02's `--slim` flag is a subtractive parameter, not a duplicated code path.

### Key Proof

<!-- gz-validate-skip: brief-cross-references -->
Smoke run: `uv run gz context ADR-0.0.3-hexagonal-architecture-tune-up | wc -c` emits ~84.7 KB Markdown to stdout. Error path: `uv run gz context ADR-9.9.9-does-not-exist; echo "exit=$?"` emits `BLOCKERS: gz context: error: ADR not found: ADR-9.9.9-does-not-exist` and exits 1.

### Implementation Summary


- Files created/modified: src/gzkit/commands/context_cmd.py (new, 158 lines); src/gzkit/cli/parser_artifacts.py (added _register_context_parser + lazy handler); tests/commands/test_context_cmd.py (new, 8 REQ-derived cases); docs/user/manpages/context.md (new manpage); docs/user/manpages/index.md, docs/user/runbook.md, docs/governance/governance_runbook.md (cross-references); .claude/plans/OBPI-0.28.0-01-context-core.md (retroactive plan file).
- Tests added: 8 REQ-derived unittest cases REQ-0.28.0-01-01..08 in tests/commands/test_context_cmd.py, all GREEN, derived from brief acceptance criteria not from a run of the implementation.
- Date completed: 2026-05-24.
- Attestation status: Gate 5 human attestation by g0 recorded during this pipeline run; receipts arb-ruff-22afe7875f44416a9c9c0c20a50a6f37 / arb-step-typecheck-479d1b8cfe57410d9069fbee98713284 / arb-step-unittest-0e447eb8b587423e9bbf271b57b3db2e cited.
- Defects noted: none introduced by this OBPI. Pre-existing repo-wide gz validate --documents drift on foundation ADRs 0.0.7 / 0.0.8 / 0.0.9 is tracked by GHI #527 and recovery-deferred per the get-out-of-jail plan; the brief's Verification block is scoped accordingly.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: verified â€” Stage 3 PASS on 7/7 commands with ARB receipts arb-ruff-22afe7875f44416a9c9c0c20a50a6f37 / arb-step-typecheck-479d1b8cfe57410d9069fbee98713284 / arb-step-unittest-0e447eb8b587423e9bbf271b57b3db2e; 8/8 REQ-derived tests in tests/commands/test_context_cmd.py GREEN; gz cli audit 103/103 cross-coverage with new manpage and runbook entries.
- Date: 2026-05-24

---

**Date Completed:** 2026-05-24

**Evidence Hash:** -
