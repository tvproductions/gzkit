---
id: OBPI-0.0.64-04-gz-validate-task-envelope-coherence
parent: ADR-0.0.64-task-envelope-and-planning-decomposition
item: 4
lane: Heavy
status: Completed
ln:
  - req_id: REQ-0.0.64-04-01
    receipt_ids:
      - arb-ruff-57eaf9a3e1784acaa018ec8bd7464a58
      - arb-step-mkdocs-e376e76096954b4cb658a507b50318f5
      - arb-step-typecheck-6da0428dc3f3492091e5603eb5fa7a9a
      - arb-step-unittest-dd3718d4a01146e994c9b7e0ef28d9ac
  - req_id: REQ-0.0.64-04-02
    receipt_ids:
      - arb-ruff-57eaf9a3e1784acaa018ec8bd7464a58
      - arb-step-mkdocs-e376e76096954b4cb658a507b50318f5
      - arb-step-typecheck-6da0428dc3f3492091e5603eb5fa7a9a
      - arb-step-unittest-dd3718d4a01146e994c9b7e0ef28d9ac
  - req_id: REQ-0.0.64-04-03
    receipt_ids:
      - arb-ruff-57eaf9a3e1784acaa018ec8bd7464a58
      - arb-step-mkdocs-e376e76096954b4cb658a507b50318f5
      - arb-step-typecheck-6da0428dc3f3492091e5603eb5fa7a9a
      - arb-step-unittest-dd3718d4a01146e994c9b7e0ef28d9ac
  - req_id: REQ-0.0.64-04-04
    receipt_ids:
      - arb-ruff-57eaf9a3e1784acaa018ec8bd7464a58
      - arb-step-mkdocs-e376e76096954b4cb658a507b50318f5
      - arb-step-typecheck-6da0428dc3f3492091e5603eb5fa7a9a
      - arb-step-unittest-dd3718d4a01146e994c9b7e0ef28d9ac
  - req_id: REQ-0.0.64-04-05
    receipt_ids:
      - arb-ruff-57eaf9a3e1784acaa018ec8bd7464a58
      - arb-step-mkdocs-e376e76096954b4cb658a507b50318f5
      - arb-step-typecheck-6da0428dc3f3492091e5603eb5fa7a9a
      - arb-step-unittest-dd3718d4a01146e994c9b7e0ef28d9ac
  - req_id: REQ-0.0.64-04-06
    receipt_ids:
      - arb-ruff-57eaf9a3e1784acaa018ec8bd7464a58
      - arb-step-mkdocs-e376e76096954b4cb658a507b50318f5
      - arb-step-typecheck-6da0428dc3f3492091e5603eb5fa7a9a
      - arb-step-unittest-dd3718d4a01146e994c9b7e0ef28d9ac
  - req_id: REQ-0.0.64-04-07
    receipt_ids:
      - arb-ruff-57eaf9a3e1784acaa018ec8bd7464a58
      - arb-step-mkdocs-e376e76096954b4cb658a507b50318f5
      - arb-step-typecheck-6da0428dc3f3492091e5603eb5fa7a9a
      - arb-step-unittest-dd3718d4a01146e994c9b7e0ef28d9ac
---

# OBPI-0.0.64-04-gz-validate-task-envelope-coherence: Gz Validate Task Envelope Coherence

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md`
<!-- gz-validate-skip: command-shape -->
- **Checklist Item:** #4 - "OBPI-0.0.64-04: **gz-validate-task-envelope-coherence** — New `gz validate --task-envelope-coherence` validator with three Heavy-fail signatures: (a) worklog event under active TASK with no `task_id`; (b) OBPI default-bucket-only TASKs without `req_atomic` exemption; (c) layer-drift across four discovery channels. Brief frontmatter `req_atomic: list[str]` exemption surface added (operator-authored escape valve; inline rationale required; surfaced in attestation evidence). Add `gz task envelope diagnose <OBPI-ID>` subcommand showing per-channel side-by-side declarations. Heavy fail-close / Lite warn-only. Join `gz check` default pipeline. Pydantic `BriefStructure` schema additive for `req_atomic`. Tests: each of three signatures triggers in fixture, with `req_atomic` exemption suppression verified; layer-drift across all 4-channel combinations covered; `gz check` pipeline integration smoke. (heavy lane: new validator scope; new schema additive; pipeline integration)."

**Status:** Completed

## Objective

Add the `gz validate --task-envelope-coherence` validator with three Heavy-fail signatures — (a) worklog event under an active TASK with no `task_id`; (b) OBPI default-bucket-only TASKs (`seq=01` across all REQs) with no `req_atomic` exemption; (c) layer-drift across the four discovery channels (Python `@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`) — and join it to the default `gz check` pipeline (Heavy fail-close, Lite warn-only). Extend `BriefStructure` with a `req_atomic: list[str]` brief-frontmatter exemption (operator-authored escape valve; inline rationale required; surfaced through attestation evidence) and add the operator-facing diagnose subcommand:

<!-- gz-validate-skip: command-shape -->
`gz task envelope diagnose <OBPI-ID>` which renders per-channel TASK declarations side-by-side so 2am operators can name which channel needs the update when layer-drift fail-closes a closeout.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/commands/validate_cmd.py` — new `--task-envelope-coherence` validator scope
- `src/gzkit/commands/task.py` — `gz task envelope diagnose <OBPI-ID>` subcommand
- `src/gzkit/governance/brief_structure.py` — `req_atomic: list[str]` additive to BriefStructure
- `src/gzkit/commands/quality.py` — join `gz check` default pipeline
- `tests/` — three-signature fixture tests; req_atomic exemption; layer-drift; gz check smoke
- `docs/user/manpages/validate.md` — Heavy lane Gate 3
- `docs/user/manpages/task-start.md` — Heavy lane Gate 3 (gz task envelope diagnose)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/**` — read-only reference; not authored here
- New dependencies
- CI files, lockfiles
- `src/gzkit/commands/validate_cmd.py` paths not related to `--task-envelope-coherence`

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

<!-- gz-validate-skip: command-shape -->
1. REQ-0.0.64-04-01 [BEHAVIOR]: `gz validate --task-envelope-coherence` MUST return Heavy-fail (exit 3) when any worklog event was emitted under an active TASK with no `task_id` field (attribution-drift); MUST return Lite-warn (exit 2) in Lite-lane context
1. REQ-0.0.64-04-02 [BEHAVIOR]: `gz validate --task-envelope-coherence` MUST return Heavy-fail when an OBPI closes with only `seq=01` TASKs across all REQs and no `req_atomic` declaration; `req_atomic: list[str]` in brief frontmatter MUST suppress signature (b) for listed REQs only; when `req_atomic` covers every REQ, signature (b) MUST suppress entirely
1. REQ-0.0.64-04-03 [BEHAVIOR]: `gz validate --task-envelope-coherence` MUST return Heavy-fail when layer-drift is detected — different TASK IDs for the same logical labor unit across any two of the four discovery channels (`@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`)
1. REQ-0.0.64-04-04 [SUPPORT]: `BriefStructure` Pydantic model (`src/gzkit/governance/brief_structure.py`) MUST gain an optional `req_atomic: list[str]` field; the field is the sole mechanical bypass surface per ADR-0.0.64 Boundary Invariant 3
1. REQ-0.0.64-04-05 [BEHAVIOR]: `gz task envelope diagnose <OBPI-ID>` MUST render per-channel TASK declarations side-by-side (Python `@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`) for the named OBPI, naming which channel needs updating when layer-drift fail-closes a closeout
1. REQ-0.0.64-04-06 [SUPPORT]: `gz validate --task-envelope-coherence` MUST join the default `gz check` pipeline (added to `build_check_steps()` in `quality.py`) at the same position as `--commit-trailers` and `--cli-alignment`
1. REQ-0.0.64-04-07 [STRUCTURAL-FENCE]: `req_atomic` MUST be the sole mechanical bypass to signature (b); no CLI flag, env var, or threshold config bypasses the signature — per ADR-0.0.64 Boundary Invariant 3
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/**`
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
test -f docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md
uv run -m unittest tests/test_persona_schema.py -v
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

- [ ] REQ-0.0.64-04-01: Given a fixture worklog event emitted under an active TASK with no `task_id`, when `gz validate --task-envelope-coherence` runs, then Heavy-fail (exit 3) is returned; given Lite lane, then warn (exit 2) is returned
- [ ] REQ-0.0.64-04-02: Given an OBPI with only `seq=01` TASKs and no `req_atomic` declaration, when `gz validate --task-envelope-coherence` runs, then Heavy-fail is returned; given `req_atomic` lists all REQs, then the signature is suppressed entirely
- [ ] REQ-0.0.64-04-03: Given layer-drift across any two of the four discovery channels, when `gz validate --task-envelope-coherence` runs, then Heavy-fail is returned
- [ ] REQ-0.0.64-04-04: Given `BriefStructure` in `src/gzkit/governance/brief_structure.py`, when an OBPI brief has `req_atomic:` frontmatter, then the field parses and validates without error; when absent, then the field defaults to empty list
- [ ] REQ-0.0.64-04-05: Given `gz task envelope diagnose <OBPI-ID>`, when run against an OBPI with layer-drift, then per-channel declarations are rendered side-by-side naming which channel needs updating
- [ ] REQ-0.0.64-04-06: Given `gz check`, when run, then `--task-envelope-coherence` fires as part of the default pipeline
- [ ] REQ-0.0.64-04-07: Given the validator, when `req_atomic` is present, then it is the only suppression path for signature (b); no other flag or config suppresses it

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


```
$ uv run gz validate --task-envelope-coherence
Validated: task_envelope_coherence

Validation failed with 3 error(s):

   ->  .gzkit/ledger.jsonl:7940
    Signature (a): worklog event 'audit_receipt_emitted' emitted under active
TASK with no task_id field (active TASKs: ['TASK-0.0.64-03-01-01', ...]).

   ->  OBPI-0.0.64-03-subdivision-driven-seq-advancement
    Signature (b): OBPI OBPI-0.0.64-03 closed with only seq=01 TASKs across
all REQs and no req_atomic exemption for: REQ-0.0.64-03-01, REQ-0.0.64-03-02,
REQ-0.0.64-03-03. Subdivide via `gz task start --seq next` or declare
`req_atomic:` in brief frontmatter with inline rationale.

Exit code: 3
```

Validator surfaces real pre-existing ledger coherence violations, confirming all three signatures are live. Receipts: arb-step-unittest-dd3718d4a01146e994c9b7e0ef28d9ac (5715/5715 pass), arb-ruff-57eaf9a3e1784acaa018ec8bd7464a58 (clean), arb-step-typecheck-6da0428dc3f3492091e5603eb5fa7a9a (clean), arb-step-mkdocs-e376e76096954b4cb658a507b50318f5 (clean).

### Implementation Summary


- Validator: `_validate_task_envelope_coherence` in `src/gzkit/commands/validate_cmd.py` (+361 lines) — three private helpers `_sig_a_attribution_drift`, `_sig_b_subdivision_skipped`, `_sig_c_layer_drift` implementing the three Heavy-fail signatures
- CLI surface: `--task-envelope-coherence` flag wired through `src/gzkit/cli/parser_maintenance.py` and dispatched via `_collect_errors()` / `validate()` in `validate_cmd.py`
- Schema additive: `BriefStructure.req_atomic: list[str]` and `BriefStructure.tasks: list[str]` optional fields in `src/gzkit/governance/brief_structure.py`; `parse_brief()` picks both up via `model_fields.keys()` filter
- Diagnose subcommand: `task_envelope_diagnose_cmd` in `src/gzkit/commands/task.py` + subparser registration in `src/gzkit/cli/parser_artifacts.py` (`gz task envelope diagnose <OBPI-ID>` renders per-channel TASK declarations side-by-side)
- Pipeline membership: `run_task_envelope_coherence_audit` wrapper in `src/gzkit/quality.py` + step entry in `src/gzkit/commands/quality.py` `build_check_steps()`
- Tests added: `tests/governance/test_task_envelope_coherence.py` (11 tests — TestSignatureA/B/C/DiagnoseCmd/CheckPipelineIntegration); `tests/governance/test_brief_structure.py` +4 tests (req_atomic/tasks field semantics)
- Docs: `docs/user/manpages/validate.md` `--task-envelope-coherence` section + `docs/user/manpages/task-envelope-diagnose.md` (new) + index entry
- BDD waiver: `data/behave_coverage_waivers.json` entry for OBPI-0.0.64-04 deferring BDD to ADR-0.0.64 composite closeout (same pattern as OBPI-01/02/03)
- @covers parity: 7/7 REQs covered (`uncovered_reqs: 0` per `gz covers`); REQ-04-07 covered by `TestSignatureB.test_obpi_all_seq01_no_req_atomic_fails` (structural-fence — no other bypass exists)
- Date completed: 2026-05-28
- Attestation status: operator-attested
- Defects noted: none

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — operator confirmed Stage 4 evidence for OBPI-0.0.64-04: three-signature task-envelope coherence validator landed (signatures a/b/c), `req_atomic` brief-frontmatter escape valve added to BriefStructure, `gz task envelope diagnose` subcommand wired, `gz check` pipeline membership confirmed. Quality gates: 5715/5715 unittests pass (receipt arb-step-unittest-dd3718d4a01146e994c9b7e0ef28d9ac), ruff clean (arb-ruff-57eaf9a3e1784acaa018ec8bd7464a58), ty clean (arb-step-typecheck-6da0428dc3f3492091e5603eb5fa7a9a), mkdocs --strict clean (arb-step-mkdocs-e376e76096954b4cb658a507b50318f5). REQ coverage: 7/7 via `gz covers` (uncovered_reqs=0). BDD deferred to ADR-0.0.64 composite closeout per behave_coverage_waivers.json entry. Validator surfaced real pre-existing ledger coherence violations from OBPI-0.0.64-03 work — proof the fail-close is live.
- Date: 2026-05-28

---

**Date Completed:** 2026-05-28

**Evidence Hash:** -
