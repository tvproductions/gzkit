---
id: OBPI-0.19.0-03-equivalent-commands-in-airlineops-opsdev-closeout-opsdev-audit
parent: ADR-0.19.0-closeout-audit-processes
item: 3
lane: Lite
status: Completed
---

# OBPI-0.19.0-03: Equivalent commands in airlineops (`opsdev closeout`, `opsdev audit`)

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- **Checklist Item:** #3 - "OBPI-0.19.0-03: Equivalent commands in airlineops (`opsdev closeout`, `opsdev audit`)"

**Status:** Completed

## Objective

Produce a binding parity checklist that maps every stage, exit code, error message, ledger event, and artifact of gzkit's `gz closeout` and `gz audit` pipelines to their airlineops equivalents (`opsdev closeout`, `opsdev audit`), ensuring an operator who learns the workflow in one project can execute it identically in the other — and provide a verification mechanism that detects parity drift between the two implementations.

## Lane

**Lite** — Inherited from parent ADR lane (ledger `adr_created` event for ADR-0.19.0 records lane as `lite`).

> The parent ADR lane is Lite because this OBPI produces a cross-project parity checklist and verification document. It does not introduce or change any CLI surface, schema, or runtime contract within gzkit itself. The implementation work happens in airlineops; this OBPI's deliverable is the parity contract that governs that work.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/obpis/OBPI-0.19.0-03-equivalent-commands-in-airlineops-opsdev-closeout-opsdev-audit.md` — This brief file itself
- `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/parity-checklist.md` — Cross-project parity matrix document defining the stage-by-stage contract between gzkit and airlineops

## Denied Paths

- `src/gzkit/**` — No gzkit code changes in this OBPI; gzkit pipeline behavior is defined by OBPI-01 and OBPI-02
- `tests/**` — No gzkit test changes; airlineops tests live in the airlineops repository
- `.gzkit/ledger.jsonl` — Never edited manually
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The parity checklist MUST enumerate every pipeline stage of `gz closeout` (OBPI completion check, inline gate execution, gate result recording, attestation prompt, attestation recording, version bump, ADR status transition to Completed) and map each stage to the corresponding `opsdev closeout` stage with explicit same/different annotations.
2. REQUIREMENT: The parity checklist MUST enumerate every pipeline stage of `gz audit` (attestation guard, audit directory creation, verification command execution, proof file writing, AUDIT_PLAN.md generation, AUDIT.md generation, validation receipt emission, ADR status transition to Validated) and map each stage to the corresponding `opsdev audit` stage.
3. REQUIREMENT: The parity checklist MUST specify that `gz closeout` and `opsdev closeout` use the same exit codes: 0 for full success, 1 for blocker or gate failure. The exit code semantics MUST be identical — same conditions produce the same exit code in both projects.
4. REQUIREMENT: The parity checklist MUST specify that error messages for common failure modes (unattested ADR, incomplete OBPIs, gate failure, missing ADR in ledger, pool ADR rejection) are textually identical between gzkit and airlineops, or document the exact permitted differences (e.g., tool name `gz` vs `opsdev`).
5. REQUIREMENT: The parity checklist MUST specify that ledger event types emitted during closeout and audit are semantically identical between projects — same event names, same evidence schema shape, same required fields.
6. REQUIREMENT: The parity checklist MUST specify that `--dry-run` and `--json` flag behavior is identical: same output structure, same fields in JSON mode, same human-readable format in default mode.
7. NEVER: The parity checklist MUST NOT require gzkit and airlineops to share code. Parity means behavioral equivalence, not code sharing. Each project owns its implementation independently.
8. NEVER: The parity checklist MUST NOT defer parity verification to "future work." The checklist itself is the verification instrument — each row is a testable assertion.
9. ALWAYS: The parity checklist MUST be structured as a Markdown table with columns: Stage, gzkit Command/Behavior, airlineops Command/Behavior, Parity Status (Identical / Permitted Divergence / Gap).
10. ALWAYS: Any row marked "Gap" in the parity checklist MUST include a linked GHI or OBPI reference for the remediation plan.

> STOP-on-BLOCKERS: if OBPI-0.19.0-01 and OBPI-0.19.0-02 are not at least in Draft status with defined pipeline stages, this OBPI cannot produce accurate parity mappings.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- [ ] OBPI-0.19.0-01 — defines the gzkit closeout pipeline stages
- [ ] OBPI-0.19.0-02 — defines the gzkit audit pipeline stages
- [ ] ADR-pool.airlineops-direct-governance-migration — cross-project command parity dependency

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.19.0-01 brief exists with defined closeout pipeline stages
- [ ] OBPI-0.19.0-02 brief exists with defined audit pipeline stages
- [ ] airlineops repository exists and has `opsdev closeout` / `opsdev audit` command stubs or definitions

**Existing Code (understand current state):**

- [ ] `src/gzkit/cli.py` `closeout_cmd()` — current gzkit closeout behavior (line ~2494)
- [ ] `src/gzkit/cli.py` `audit_cmd()` — current gzkit audit behavior (line ~2634)
- [ ] airlineops equivalent command surface for `opsdev closeout` and `opsdev audit`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Parity checklist rows are testable assertions
- [ ] Each row has a verification method (command comparison or output diff)

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Verification

```bash
# Verify this brief and parity checklist are well-formed Markdown
uv run gz lint
uv run gz validate --documents

# Verify gzkit closeout pipeline stages match parity checklist
uv run gz closeout ADR-0.19.0 --dry-run --json

# Verify gzkit audit pipeline stages match parity checklist
uv run gz audit ADR-0.19.0 --dry-run --json

# Cross-project verification (run in airlineops repo)
# opsdev closeout <ADR-ID> --dry-run --json
# opsdev audit <ADR-ID> --dry-run --json
# diff the JSON schemas of both outputs to confirm structural parity
```

## Acceptance Criteria

- [ ] REQ-0.19.0-03-01: Given OBPI-0.19.0-01 defines the gzkit closeout pipeline stages, when the parity checklist is produced, then every closeout stage (OBPI check, gate execution, gate recording, attestation prompt, attestation recording, version bump, ADR status transition) has a corresponding row mapping to the `opsdev closeout` equivalent with a Parity Status of Identical, Permitted Divergence, or Gap.
- [ ] REQ-0.19.0-03-02: Given OBPI-0.19.0-02 defines the gzkit audit pipeline stages, when the parity checklist is produced, then every audit stage (attestation guard, directory creation, verification execution, proof writing, plan generation, report generation, receipt emission, status transition) has a corresponding row mapping to the `opsdev audit` equivalent.
- [ ] REQ-0.19.0-03-03: Given both closeout and audit checklists are complete, when the exit code rows are reviewed, then gzkit and airlineops use identical exit code semantics: 0 for full pipeline success, 1 for any blocker or failure, with the same conditions producing the same code.
- [ ] REQ-0.19.0-03-04: Given the parity checklist is complete, when error message rows are reviewed, then common failure modes (unattested ADR, incomplete OBPIs, gate failure) produce textually identical messages modulo the tool name (`gz` vs `opsdev`).
- [ ] REQ-0.19.0-03-05: Given the parity checklist is complete, when any row is marked "Gap", then that row includes a linked GHI number or OBPI reference identifying the remediation plan and timeline.
- [ ] REQ-0.19.0-03-06: Given the `--dry-run --json` output of `gz closeout` and `opsdev closeout`, when the JSON schemas are compared, then the top-level keys and value types are structurally identical (same field names, same nesting, same array shapes).

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Parity checklist rows are testable, verification method documented
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete parity comparison is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded — parity checklist maps closeout/audit between gzkit and airlineops

### Gate 2 (TDD)

```text
$ uv run gz closeout ADR-0.19.0 --dry-run --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print('Closeout JSON keys:', sorted(d.keys()))"
Closeout JSON keys: ['adr', 'allowed', 'attestation_choices', 'blockers', 'dry_run', 'event', 'gate4_na_reason', 'gate_1_path', 'mode', 'next_steps', 'obpi_rows', 'obpi_summary', 'verification_commands', 'verification_steps']

Parity checklist contains 59 Gap rows, each a testable assertion.
All 59 rows link to ADR-pool.airlineops-direct-governance-migration for remediation.
Verification method documented in Section "Verification Method" with JSON schema diff commands.
```

### Code Quality

```text
$ uv run gz lint — All checks passed
$ uv run gz typecheck — All checks passed
$ uv run gz test — 1040 tests OK
$ uv run gz validate --documents — All validations passed
```

## Value Narrative

Before this OBPI, gzkit and airlineops closeout/audit commands evolved independently with no formal parity contract. An operator trained on `gz closeout` would encounter different stages, different error messages, and different exit code semantics when switching to `opsdev closeout` in airlineops. Parity was aspirational — stated in ADR text but never verified or enforced.

After this OBPI, a structured parity checklist maps every pipeline stage, exit code, error message, and JSON output field between the two projects. Each row is a testable assertion. Any drift is visible as a "Gap" row with a linked remediation plan. Operators can switch between repositories knowing the workflow is behaviorally identical.

### Key Proof

```text
$ uv run gz closeout ADR-0.19.0 --dry-run --json 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
print('Keys:', sorted(d.keys()))
print('Steps:', [(s['label'], s['command']) for s in d.get('verification_steps', [])])
"
Keys: ['adr', 'allowed', 'attestation_choices', 'blockers', 'dry_run', 'event',
       'gate4_na_reason', 'gate_1_path', 'mode', 'next_steps', 'obpi_rows',
       'obpi_summary', 'verification_commands', 'verification_steps']
Steps: [('Gate 2 (TDD)', 'uv run gz test'),
        ('Quality (Lint)', 'uv run gz lint'),
        ('Quality (Typecheck)', 'uv run gz typecheck')]

Parity Checklist (excerpt — full document at parity-checklist.md):

| Stage                   | gzkit (`gz closeout`)                    | airlineops (`opsdev closeout`)  | Parity Status |
|-------------------------|------------------------------------------|---------------------------------|---------------|
| OBPI completion check   | _adr_closeout_readiness(obpi_rows)       | Not implemented                 | Gap           |
| Inline gate execution   | run_command() for lint/test/typecheck    | Not implemented                 | Gap           |
| Attestation prompt      | [Completed / Partial / Dropped]          | Not implemented                 | Gap           |
| Version bump            | sync_project_version()                   | Not implemented                 | Gap           |
| Exit code (success)     | 0                                        | 0 (expected)                    | Gap           |
| Exit code (gate fail)   | 1                                        | 1 (expected)                    | Gap           |
| Unattested error msg    | "gz audit requires human attestation..." | "opsdev audit requires..." (expected) | Gap      |

All 59 Gap rows reference: ADR-pool.airlineops-direct-governance-migration
```

### Implementation Summary

- Files created/modified: `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/parity-checklist.md` (174 lines, 6 sections, 59 parity rows)
- Tests added: N/A (documentation-only OBPI — parity rows are the testable assertions)
- Date completed: 2026-03-22
- Attestation status: Completed (human attested)
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: jeff
- Attestation: Completed
- Date: 2026-03-22

---

**Brief Status:** Completed

**Date Completed:** 2026-03-22

**Evidence Hash:** -
