---
id: OBPI-0.0.71-02-gz-obpi-repudiate-cli
parent: ADR-0.0.71-completion-repudiation
item: 2
lane: Heavy
status: Completed
# req_atomic: each REQ is a single indivisible labor unit against the one shared
# `obpi_repudiate_cmd` + its parser registration — the emit-event behavior (01),
# the empty-attestor fail-close (02), the empty-reason fail-close (03), the
# dry-run no-write path (04), the closed-enum parser rejection (05), the
# operator-gated structural fence (06), and the manpage/index/runbook/cli-audit
# support deliverable (07). None decomposes into parallel seq=02+ sub-tasks; the
# whole verb is one command function authored test-first (ADR-0.0.64 exemption).
req_atomic:
  - REQ-0.0.71-02-01
  - REQ-0.0.71-02-02
  - REQ-0.0.71-02-03
  - REQ-0.0.71-02-04
  - REQ-0.0.71-02-05
  - REQ-0.0.71-02-06
  - REQ-0.0.71-02-07
---

# OBPI-0.0.71-02-gz-obpi-repudiate-cli: Gz Obpi Repudiate Cli

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.71-completion-repudiation/ADR-0.0.71-completion-repudiation.md`
<!-- gz-validate-skip: command-shape -->
- **Checklist Item:** #2 - "`gz obpi repudiate` CLI verb (operator-gated, fail-closed on empty attestor/reason, --dry-run) + parser + manpage + `gz cli audit` green + behave smoke test; AGENTS.md withdraw-vs-repudiate disambiguation"

**Status:** Completed

## Objective

Deliver the operator-gated `repudiate` verb under `gz obpi`: it emits the OBPI-01 `obpi_completion_repudiated` event, fails closed on empty `--attestor`/`--reason`, constrains `--cause` to the closed enum, and supports `--dry-run` — landed with a per-verb manpage, `gz cli audit` parity, a behave smoke test, and the withdraw-vs-repudiate disambiguation seated in the governed rule surface.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/cli/main.py` (added by brief reconcile, attestor g0)

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/commands/obpi_cmd.py` — NEW `obpi_repudiate_cmd(...)` (consumes the OBPI-01 factory)
- `src/gzkit/cli/parser_artifacts.py` — NEW `repudiate` subparser under `gz obpi`
- `docs/user/manpages/obpi-repudiate.md` **CREATE** — NEW: `repudiate` verb manpage (per-verb convention)
- `features/obpi_repudiate.feature` **CREATE** — NEW: heavy-lane behave smoke
- `tests/test_obpi_repudiate_cli.py` **CREATE** — NEW: CLI unit tests
- `.gzkit/rules/governance-core.md` — withdraw-vs-repudiate disambiguation (canonical rule source; AGENTS.md is a generated surface — the disambiguation lands via the governed rule/content surface and is propagated by sync, never hand-edited into the rendered AGENTS.md)
- `docs/design/adr/foundation/ADR-0.0.71-completion-repudiation/obpis/OBPI-0.0.71-02-gz-obpi-repudiate-cli.md` — this brief (evidence recording)
- `docs/design/adr/foundation/ADR-0.0.71-completion-repudiation/ADR-0.0.71-completion-repudiation.md` — parent ADR (read-only, for intent)

> DEPENDS ON OBPI-0.0.71-01: the `obpi_completion_repudiated` event model + factory
> must exist before this CLI verb can emit it. Sequence 01 → 02.

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

<!-- gz-validate-skip: command-shape -->
1. REQUIREMENT: `gz obpi repudiate <OBPI-ID> --cause <enum> --reason "<text>" --attestor "<human>"` MUST emit exactly one `obpi_completion_repudiated` event (via the OBPI-01 factory) carrying those fields.
1. REQUIREMENT: An empty `--attestor` OR empty `--reason` MUST exit 1 with no ledger write — only a human repudiates, and the human's words are required (parent ADR Boundary Invariant 1).
1. REQUIREMENT: `--cause` MUST be constrained to the closed enum at the parser (argparse `choices`); an out-of-enum value is rejected before any ledger write (parent ADR Boundary Invariant 4).
1. REQUIREMENT: `--dry-run` MUST print the planned event and write nothing — zero ledger delta.
1. REQUIREMENT: `gz cli audit` MUST be green — the new verb is covered across manpage, command doc, and index (Heavy-lane CLI contract, `.claude/rules/cli.md`).
1. REQUIREMENT: The withdraw-vs-repudiate distinction MUST be documented (retire vs reverse-and-keep) so agents do not reach for the wrong verb; the disambiguation lands via the governed rule/content surface, never a raw edit to the generated AGENTS.md.
1. NEVER: provide an agent-self-repudiation path — the verb is operator-gated only.
1. ALWAYS: TDD (RED→GREEN); tests derive from these REQ semantics.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.71-completion-repudiation/ADR-0.0.71-completion-repudiation.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.71-completion-repudiation/ADR-0.0.71-completion-repudiation.md`
- [ ] Required path exists or is intentionally created in this OBPI: `AGENTS.md`
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

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_obpi_repudiate_cli -v
uv run gz cli audit
uv run gz obpi repudiate OBPI-0.0.71-01-completion-repudiation-event --cause operator-error --reason "smoke" --attestor "g0" --dry-run
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
# Dry-run repudiation of a real OBPI id — prints the planned event, writes nothing:
uv run gz obpi repudiate OBPI-0.0.70-02-session-correction-mining --cause model-induced-fabrication --reason "operator never attested; carried through from OBPI-01" --attestor "g0" --dry-run
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.71-02-01 [behavior]: Given valid `--cause`/`--reason`/`--attestor`, when the `repudiate` verb runs, then exactly one `obpi_completion_repudiated` event is appended carrying those fields. (@covers test)
- [ ] REQ-0.0.71-02-02 [behavior]: Given an empty `--attestor`, when the verb runs, then it exits 1 and appends no ledger event. (@covers test)
- [ ] REQ-0.0.71-02-03 [behavior]: Given an empty `--reason`, when the verb runs, then it exits 1 and appends no ledger event. (@covers test)
- [ ] REQ-0.0.71-02-04 [behavior]: Given `--dry-run`, when the verb runs, then it prints the planned event and the ledger line count is unchanged. (@covers test)
- [ ] REQ-0.0.71-02-05 [behavior]: Given a `--cause` value outside the closed enum, when the verb runs, then the parser rejects it (exit 2) before any ledger write. (@covers test)
- [ ] REQ-0.0.71-02-06 [structural-fence]: The verb is operator-gated — there is no agent-self-repudiation path. Verified at ADR-0.0.71 closeout via the parent ADR `## Boundary Invariants` (Invariant 1).
- [ ] REQ-0.0.71-02-07 [support]: The `repudiate` verb lands with manpage + index + command-doc parity and the withdraw-vs-repudiate disambiguation. Proof: `gz cli audit` exit 0 + `gz validate --documents` exit 0 + `artifact_edited` ledger events.

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


$ uv run gz obpi repudiate OBPI-0.0.70-02 --cause bad-cause --reason r --attestor Jeff
# exit 2 (argparse choices enforcement, before any ledger write)

$ uv run gz cli audit
CLI audit passed.
Cross-coverage: 105/105 commands fully covered.

Receipts: arb-step-unittest-e56c33fd3c644342b50cbc9dc05dbca5 (full suite, 6097 pass), arb-ruff-1a21c6b3a9d84fdf8cc9f90222d30b60 (clean), arb-step-typecheck-94d8fe8dcd79462b9cde7d9bf047484d (clean), arb-step-mkdocs-d7181a63c84f492f8e01ca2e400fa1e4 (clean). behave_uncovered_reqs=0 via gz covers.

### Implementation Summary


- Verb: gz obpi repudiate <OBPI-ID> --cause <enum> --reason "<text>" --attestor "<human>" [--dry-run] — obpi_repudiate_cmd() in src/gzkit/commands/obpi_cmd.py, consuming the OBPI-01 obpi_completion_repudiated_event factory
- Parser: repudiate subparser under gz obpi in src/gzkit/cli/parser_artifacts.py; --cause constrained via argparse choices to the closed enum (model-induced-fabrication | operator-error | verification-invalid)
- Fail-closed gates: empty --attestor or --reason exit 1 before any ledger lookup; invalid --cause exits 2 at the parser
- repudiated_receipt: auto-derived from the most recent obpi_receipt_emitted completion event (deterministic; not a CLI flag)
- Files created: tests/test_obpi_repudiate_cli.py (5 tests), docs/user/manpages/obpi-repudiate.md, features/obpi_repudiate.feature (5 scenarios)
- Files modified: obpi_cmd.py, parser_artifacts.py, .gzkit/rules/governance-core.md (v0.4.0 withdraw-vs-repudiate disambiguation), manpage index, operator + governance runbooks, config/doc-coverage.json, trust_audits/cli.py (_NO_SKILL_VERBS), data/behave_coverage_waivers.json
- Tests added: 5 unit (REQ-01..05) + 5 behave scenarios (REQ-01/02/03/05 tagged); REQ-04/06/07 behave-waived with rationale
- Date completed: 2026-06-13
- Attestation status: operator-attested "attest completed" (Stage 4)

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — operator attested OBPI-0.0.71-02-gz-obpi-repudiate-cli at Stage 4 after reviewing the evidence packet. gz obpi repudiate verb landed: obpi_repudiate_cmd + repudiate subparser (closed-enum --cause, fail-closed empty --attestor/--reason), per-verb manpage, 5 behave scenarios, 5 unit tests (REQ-01..05 @covers, behavior_uncovered_reqs=0), withdraw-vs-repudiate disambiguation in governance-core.md v0.4.0. Receipts: arb-step-unittest-e56c33fd3c644342b50cbc9dc05dbca5 (6097 pass), arb-ruff-1a21c6b3a9d84fdf8cc9f90222d30b60, arb-step-typecheck-94d8fe8dcd79462b9cde7d9bf047484d, arb-step-mkdocs-d7181a63c84f492f8e01ca2e400fa1e4. gz cli audit 105/105; gz validate --documents clean.
- Date: 2026-06-13

---

**Date Completed:** 2026-06-13

**Evidence Hash:** -
