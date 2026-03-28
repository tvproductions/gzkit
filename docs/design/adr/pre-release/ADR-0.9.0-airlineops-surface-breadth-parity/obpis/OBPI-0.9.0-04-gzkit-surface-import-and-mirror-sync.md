---
id: OBPI-0.9.0-04-gzkit-surface-import-and-mirror-sync
parent: ADR-0.9.0-airlineops-surface-breadth-parity
item: 4
lane: Heavy
status: Completed
---

# OBPI-0.9.0-04-gzkit-surface-import-and-mirror-sync: Gzkit surface import and mirror sync

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- **Checklist Item:** #4 — "OBPI-0.9.0-04: Execute approved `.gzkit/**` import tranche and synchronize generated mirror/control surfaces."

**Status:** Completed

## Objective

Import the approved canonical `.gzkit/**` tranche into gzkit with process-plane
compatibility, refresh generated control surfaces, and leave evidence that the
new governance surfaces are truthful, synchronized, and free of AirlineOps
product-plane references.

## Lane

**Heavy** — This unit changes agent-facing governance artifacts and generated
control surfaces, so it requires full documentation, verification, and human
attestation before completion.

## Allowed Paths

- `.gzkit/**` — Approved governance tranche import target.
- `docs/governance/GovZero/gzkit-structure.md` — Must be updated to keep `.gzkit/`
  structure documentation truthful after the import.
- `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/**` —
  OBPI brief updates and parity evidence for this tranche.
- `.agents/skills/**`, `.claude/skills/**`, `.github/skills/**` — Generated mirror
  outputs touched by `gz agent sync control-surfaces`.

## Denied Paths

- `src/**` and `tests/**` — No runtime feature work is part of this tranche.
- `../airlineops/**` — Canonical source is read-only.
- `.claude/hooks/**` — Hook parity belongs to OBPI-0.9.0-01 and OBPI-0.9.0-02.
- `.gzkit/locks/obpi/**` — Explicitly deferred by the OBPI-03 intake matrix.
- Product-plane ontology doctrines, policies, and rules not approved in
  `gzkit-surface-intake-matrix.md`.
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `.gzkit/governance/ontology.schema.json` MUST match the canonical
   AirlineOps schema verbatim.
1. REQUIREMENT: `.gzkit/governance/ontology.json` MUST contain only approved
   process-plane governance content and MUST remain internally reference-safe.
1. REQUIREMENT: Imported governance artifacts MUST contain no `src/airlineops/`
   or other AirlineOps product-plane references.
1. REQUIREMENT: `uv run gz agent sync control-surfaces` MUST be run after the
   `.gzkit/**` import and any sync drift it reports MUST be resolved or captured
   as a tracked defect before closeout.
1. NEVER: Do not import deferred lock runtime surfaces or AirlineOps
   product-plane ontology content.
1. ALWAYS: Keep the local `.gzkit` documentation and OBPI evidence aligned with
   the actual imported structure and command outputs.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` — repo structure
- [x] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [x] Parent ADR — understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- [x] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [x] Canonical `.gzkit` source exists: `../airlineops/.gzkit/`
- [x] Local `.gzkit` target exists: `.gzkit/`
- [x] Tranche definition exists: `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/gzkit-surface-intake-matrix.md`

**Existing Code (understand current state):**

- [x] Current control-surface manifest: `.gzkit/manifest.json`
- [x] Current `.gzkit` structure doc: `docs/governance/GovZero/gzkit-structure.md`
- [x] Sync contract: `docs/user/commands/agent-sync-control-surfaces.md`

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation when behavior changes warrant them
- [x] Tests pass: `uv run gz test`
- [x] Coverage maintained: `uv run coverage run -m unittest && uv run coverage report`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Format clean: `uv run gz format`
- [x] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

<!-- What commands verify this work? Human runs these at closeout. -->

```bash
# Gate 2: Tests
uv run gz test

# Specific verification for this OBPI
cmp -s .gzkit/governance/ontology.schema.json ../airlineops/.gzkit/governance/ontology.schema.json
uv run python - <<'PY'
import json
from pathlib import Path
data = json.loads(Path('.gzkit/governance/ontology.json').read_text())
print(sorted(data['doctrines']))
print(sorted(data['policies']))
print(sorted(data['rules']))
print(sorted(data['actions']))
assert all(item.get('plane') == 'process' for item in data['doctrines'].values())
assert 'src/airlineops/' not in json.dumps(data)
PY
uv run gz agent sync control-surfaces
uv run gz skill audit --json
uv run gz status
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.9.0-04-01: [doc] Given the approved OBPI-03 tranche, when OBPI-04 implementation completes,
      then `.gzkit/governance/ontology.schema.json`, `.gzkit/governance/ontology.json`,
      `.gzkit/lessons/.gitkeep`, and `.gzkit/README.md` exist and reflect the approved
      import/defer/exclude decisions.
- [x] REQ-0.9.0-04-02: [doc] Given the imported ontology, when it is inspected, then it
      contains only process-plane doctrines and contains no `src/airlineops/` or
      other AirlineOps product-plane references.
- [x] REQ-0.9.0-04-03: [doc] Given generated control surfaces depend on canonical
      governance state, when sync is run after the import, then `gz agent sync
      control-surfaces` completes successfully and status remains coherent.
- [x] REQ-0.9.0-04-04: [doc] Given the `.gzkit` structure changed, when documentation is
      reviewed, then `.gzkit/README.md` and `docs/governance/GovZero/gzkit-structure.md`
      both describe the actual local structure without placeholder drift.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Key Proof

```text
$ cmp -s .gzkit/governance/ontology.schema.json ../airlineops/.gzkit/governance/ontology.schema.json && echo schema-match
schema-match

$ uv run python - <<'PY'
import json
from pathlib import Path
data = json.loads(Path('.gzkit/governance/ontology.json').read_text())
print(sorted(data['doctrines']))
PY
['D-FLAG-DEFECTS', 'D-GATE-ATTESTATION', 'D-OBPI-DISCIPLINE']
```

This proves the imported governance tranche landed with the intended
process-plane-only ontology and canonical schema parity.

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed for 0.9.0-04
- Date: 2026-03-09

### Gate 1 (ADR)

- [x] Intent and scope recorded
- [x] Parent ADR checklist item #4 quoted
- [x] Tranche evidence linked from `gzkit-surface-intake-matrix.md`

### Gate 2 (TDD)

```text
uv run gz test
Ran 305 tests in 3.915s
OK

uv run coverage run -m unittest discover tests
Ran 305 tests in 5.202s
OK

uv run coverage report
TOTAL 8568 1107 87%

cmp -s .gzkit/governance/ontology.schema.json ../airlineops/.gzkit/governance/ontology.schema.json
schema-match

uv run python - <<'PY' ... PY
doctrines ['D-FLAG-DEFECTS', 'D-GATE-ATTESTATION', 'D-OBPI-DISCIPLINE']
policies ['P-ATTEST-OBPI-CEREMONY']
rules ['R-ATTEST-OBPI-001']
actions ['A-EDIT-IN-SCOPE', 'A-FILE-DELETE', 'A-GIT-COMMIT', 'A-GIT-NO-VERIFY', 'A-GIT-PUSH', 'A-MARK-OBPI-COMPLETED', 'A-RAW-SQL-ATTESTATION', 'A-READ-FILES', 'A-RUN-FULL-SUITE', 'A-RUN-LINT', 'A-RUN-UNIT-TESTS', 'A-SEARCH-CODEBASE', 'A-UV-ADD']
ontology-sanity-ok

uv run gz implement --adr ADR-0.9.0-airlineops-surface-breadth-parity
Gate 2 (TDD): PASS
```

### Code Quality

```text
uv run gz lint
All checks passed!
ADR path contract check passed.
Lint passed.

uv run gz format
4 files reformatted, 64 files left unchanged
All checks passed!
Format complete.

uv run gz typecheck
All checks passed!
Type check passed.

uv run mkdocs build --strict
Documentation built in 0.66 seconds

uv run -m behave features/
1 feature passed, 3 scenarios passed, 16 steps passed

uv run gz agent sync control-surfaces
Initial attempt failed: canonical skill metadata used invalid `metadata.govzero_layer`
values with an em dash in 17 `.gzkit/skills/**` files.
Remediation: normalized those enum values to the accepted hyphenated forms, then re-ran sync.
Result: sync completed successfully and refreshed mirrored control surfaces, `.gzkit/manifest.json`,
`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and `.github/discovery-index.json`.

uv run gz skill audit --json
{"valid": true, "checked_skills": 46, "issues": [], "success": true}
```

### Implementation Summary

- Value narrative: Before this OBPI, gzkit's `.gzkit/**` surface still lacked the approved
  governance tranche from AirlineOps parity intake, and control-surface sync was not exercised
  against that imported state. After this OBPI, gzkit has a local governance ontology/schema,
  a truthful `.gzkit/` README and structure doc, a lessons scaffold, and synchronized mirror/control
  surfaces backed by passing quality gates.
- Key proof: `.gzkit/governance/ontology.json` now contains only
  `D-FLAG-DEFECTS`, `D-GATE-ATTESTATION`, and `D-OBPI-DISCIPLINE`, and the schema file matches
  canonical byte-for-byte.
- Files created:
  - `.gzkit/governance/ontology.json`
  - `.gzkit/governance/ontology.schema.json`
  - `.gzkit/README.md`
  - `.gzkit/lessons/.gitkeep`
- Files modified:
  - `docs/governance/GovZero/gzkit-structure.md`
  - `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/obpis/OBPI-0.9.0-04-gzkit-surface-import-and-mirror-sync.md`
  - `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/obpis/OBPI-0.9.0-02-compatibility-adaptation-blocking-hooks.md`
  - 17 canonical `.gzkit/skills/**/SKILL.md` files with `metadata.govzero_layer` normalization
  - Generated mirror/control-surface outputs under `.agents/skills/**`, `.claude/skills/**`,
    `.github/skills/**`, `.gzkit/manifest.json`, `AGENTS.md`, `CLAUDE.md`,
    `.github/copilot-instructions.md`, `.github/discovery-index.json`, and `.claude/**` sync surfaces
- Tests added: None (governance/documentation/schema import tranche; existing coverage exercised via full repo gates)
- Governance events recorded:
  - `gate_checked` appended to `.gzkit/ledger.jsonl` by `uv run gz implement --adr ADR-0.9.0-airlineops-surface-breadth-parity`
- Human attestation:
  - Attestor: `human:jeff`
  - Response: `attest completed for 0.9.0-04`
  - Date: 2026-03-09
- Date completed: 2026-03-09

---

**Brief Status:** Completed

**Date Completed:** 2026-03-09

**Evidence Hash:** —
