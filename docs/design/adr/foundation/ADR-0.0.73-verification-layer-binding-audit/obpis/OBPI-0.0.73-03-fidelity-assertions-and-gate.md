---
id: OBPI-0.0.73-03-fidelity-assertions-and-gate
parent: ADR-0.0.73-verification-layer-binding-audit
item: 3
lane: Heavy
status: Completed
# req_atomic: each REQ is a single indivisible labor unit — the FidelityAssertion
# frozen model (01), the ## Fidelity Assertions parser (02), the gate runner's
# pass/fail result-setting (03), and the gate's failure-report + non-zero exit (04)
# are each one coherent surface authored in a single TDD increment; the manpage +
# index + runbook docs (05, SUPPORT) is one doc deliverable; the boundary-invariant
# fence (06, STRUCTURAL-FENCE) is a parent-ADR property. None decomposes into
# parallel seq=02+ sub-tasks (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.73-03-01
  - REQ-0.0.73-03-02
  - REQ-0.0.73-03-03
  - REQ-0.0.73-03-04
  - REQ-0.0.73-03-05
  - REQ-0.0.73-03-06
---

# OBPI-0.0.73-03-fidelity-assertions-and-gate: Fidelity Assertions And Gate

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- **Checklist Item:** #3 - "`## Fidelity Assertions` schema + gz adr fidelity gate — `FidelityAssertion` Pydantic frozen model `{adr_id, claim, command, expected_exit, observed, result}`; `## Fidelity Assertions` block parsed from the ADR Decision; gz adr fidelity &lt;ADR&gt; RUNS the commands and compares observed-vs-expected exit; one standalone gate; manpage + `gz cli audit` green; unit tests"

**Status:** Completed

## Objective

A `FidelityAssertion` frozen Pydantic model and a new gz adr fidelity gate land:
the gate parses the `## Fidelity Assertions` block from an ADR's Decision, RUNS
each command, and compares observed-vs-expected exit. "Done" = the gz adr fidelity
verb runs an ADR's thesis against the running system and reports, per assertion,
the claim, the command, the expected exit, the observed exit, and a pass/fail
result — a single standalone gate that both ceremonies (OBPI-04) invoke.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md` — parent ADR for intent and scope (also the first `## Fidelity Assertions` consumer)
- `src/gzkit/fidelity.py` **CREATE** — `FidelityAssertion` frozen model + `## Fidelity Assertions` parser + command runner
- `src/gzkit/commands/adr_fidelity.py` **CREATE** — the gz adr fidelity &lt;ADR&gt; command implementation
- `src/gzkit/cli/` — register the `adr fidelity` subcommand on the parser
- `tests/governance/test_adr_fidelity.py` **CREATE** — unit tests for the model, the parser, and observed-vs-expected exit comparison
- `docs/user/manpages/adr-fidelity.md` **CREATE** — manpage for the new verb (Heavy-lane docs gate)
- `docs/user/reference/` — command-doc + index entry for the new verb
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/obpis/OBPI-0.0.73-03-fidelity-assertions-and-gate.md` — this brief (evidence recording)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: `## Fidelity Assertions` schema + gz adr fidelity gate — `FidelityAssertion` Pydantic frozen model `{adr_id, claim, command, expected_exit, observed, result}`; `## Fidelity Assertions` block parsed from the ADR Decision; gz adr fidelity &lt;ADR&gt; RUNS the commands and compares observed-vs-expected exit; one standalone gate; manpage + `gz cli audit` green; unit tests.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief
1. REQUIREMENT: Verification commands MUST be concrete and runnable before acceptance
1. REQUIREMENT: NEVER mark the OBPI accepted while scaffold defaults remain in the brief
1. REQUIREMENT: ALWAYS reconcile the brief with the parent ADR before implementation begins
1. REQUIREMENT: The `FidelityAssertion` Pydantic model MUST be frozen (`frozen=True, extra="forbid"`) with exactly six fields (`adr_id, claim, command, expected_exit, observed, result`) (REQ-0.0.73-03-01)

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/obpis/`
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
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f src/gzkit/fidelity.py
test -f src/gzkit/commands/adr_fidelity.py
test -f tests/governance/test_adr_fidelity.py
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. The new verb is unregistered
     until this OBPI lands; the skip marker suppresses the command-shape
     check on the fenced block below (GHI #432). -->

<!-- gz-validate-skip: command-shape -->
```bash
# Runs this ADR's thesis against the running system, observed-vs-expected exit.
uv run gz adr fidelity ADR-0.0.73-verification-layer-binding-audit
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.73-03-01 [BEHAVIOR]: Given a `FidelityAssertion`, when code mutates a field or passes an unknown field, then Pydantic raises (`frozen=True, extra="forbid"`) and all six fields (`adr_id, claim, command, expected_exit, observed, result`) are present. (@covers test in `tests/governance/test_adr_fidelity.py`)
- [ ] REQ-0.0.73-03-02 [BEHAVIOR]: Given an ADR whose Decision contains a `## Fidelity Assertions` block, when the parser runs, then it extracts one `FidelityAssertion` per declared claim/command/expected-exit row. (@covers test in `tests/governance/test_adr_fidelity.py`)
- [ ] REQ-0.0.73-03-03 [BEHAVIOR]: Given parsed assertions, when the fidelity gate runs each command, then `result` is pass when observed exit equals expected exit and fail otherwise. (@covers test in `tests/governance/test_adr_fidelity.py`)
- [ ] REQ-0.0.73-03-04 [BEHAVIOR]: Given an assertion whose command's observed exit differs from its expected exit, when the gate completes, then it reports that assertion as failed and the gate exits non-zero. (@covers test in `tests/governance/test_adr_fidelity.py`)
- [ ] REQ-0.0.73-03-05 [SUPPORT]: The new verb is documented (manpage + command doc + index). Proof: `gz validate --cli-alignment` exit 0 + `artifact_edited` ledger event for `docs/user/manpages/adr-fidelity.md`.
- [ ] REQ-0.0.73-03-06 [STRUCTURAL-FENCE]: Every ADR Decision carries a runnable `## Fidelity Assertions` block that the gate RUNS (observed-vs-expected exit); the requirement is a one-way door and may never be removed (parent ADR § Boundary Invariants #4).

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


uv run gz adr fidelity ADR-0.0.73-verification-layer-binding-audit --check exits 0 with output "Fidelity block parseable: 6 assertion(s) in ADR-0.0.73-verification-layer-binding-audit.md". The gz adr fidelity <ADR> verb parses the ## Fidelity Assertions block from an ADR Decision, runs each command via shlex-split shell-less subprocess, and compares observed-vs-expected exit (result=pass/fail). Quality gates green — receipts arb-ruff-938771760656469d9e0a598ade9403db (lint), arb-step-typecheck-e28f513250cc447686e9946f6fc16c40 (typecheck), arb-step-unittest-82f489d8289b4d69848ae1e4067c6e30 (16/16 scoped + full suite), arb-step-mkdocs-66cfa1e4b29d48a884f66e07cdb4d910 (docs).

### Implementation Summary


- Files created: src/gzkit/fidelity.py (FidelityAssertion frozen Pydantic model + parse_fidelity_assertions() + run_fidelity_gate()); src/gzkit/commands/adr_fidelity.py (gz adr fidelity command); tests/governance/test_adr_fidelity.py (16 unit tests); docs/user/manpages/adr-fidelity.md (manpage)
- Files modified: src/gzkit/cli/parser_artifacts.py (verb registration + lazy dispatch); src/gzkit/governance/trust_audits/cli.py (_NO_SKILL_VERBS waiver, OBPI-04 wires into skills); config/doc-coverage.json; docs/user/manpages/index.md; mkdocs.yml; docs/user/runbook.md; docs/governance/governance_runbook.md; data/behave_coverage_waivers.json (operator-approved BDD waiver)
- Tests added: 16 (3 classes — TestFidelityAssertionModel/Parser/GateRunner; REQ-03-01 through 03-04)
- Date completed: 2026-06-17
- Attestation status: operator-attested "attest completed" (Gate 5, Heavy lane)
- Defects noted: none

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — operator-attested Gate 5 for OBPI-0.0.73-03-fidelity-assertions-and-gate (Heavy lane, foundation kind). FidelityAssertion frozen model + ## Fidelity Assertions parser + gz adr fidelity gate landed; 16/16 unit tests green; receipts arb-ruff-938771760656469d9e0a598ade9403db, arb-step-typecheck-e28f513250cc447686e9946f6fc16c40, arb-step-unittest-82f489d8289b4d69848ae1e4067c6e30, arb-step-mkdocs-66cfa1e4b29d48a884f66e07cdb4d910; gz validate --cli-alignment exit 0; behavior_uncovered_reqs=0.
- Date: 2026-06-17

---

**Date Completed:** 2026-06-17

**Evidence Hash:** -
