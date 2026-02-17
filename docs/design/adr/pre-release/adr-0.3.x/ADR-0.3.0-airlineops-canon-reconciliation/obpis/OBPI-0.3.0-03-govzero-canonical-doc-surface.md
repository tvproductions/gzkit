---
id: OBPI-0.3.0-03-govzero-canonical-doc-surface
parent: ADR-0.3.0
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.3.0-03-govzero-canonical-doc-surface: GovZero Canonical Doc Surface

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/adr-0.3.x/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md`
- **Checklist Item:** #3 — "Import missing canonical `docs/governance/GovZero/*.md` files."

**Status:** Completed

## Objective

Establish a canonical GovZero docs surface in gzkit by importing missing AirlineOps governance documents and binding them to operator habit classes (orientation, verification, presentation) without reinterpretation.

## Lane

**Heavy** — External governance parity surface and operator contract impact.

## Allowed Paths

- `docs/governance/GovZero/**`
- `docs/lodestar/README.md`
- `docs/proposals/REPORT-airlineops-habit-parity-*.md`
- `docs/proposals/REPORT-airlineops-parity-*.md`
- `docs/user/reference/charter.md`
- `docs/user/concepts/*.md`

## Denied Paths

- `/Users/jeff/Documents/Code/airlineops/**`
- `src/gzkit/**`
- `.gzkit/ledger.jsonl (manual edits)`

## Requirements (FAIL-CLOSED)

1. MUST create `docs/governance/GovZero/` in gzkit and import all canonical markdown files from AirlineOps.
1. MUST preserve canonical filenames and structure for path-level parity.
1. MUST keep imported canonical files semantically untouched, except explicit provenance header blocks if needed.
1. MUST map imported canonical docs to operator habit classes in dated parity reporting.
1. NEVER silently reinterpret canonical governance text.
1. ALWAYS keep canonical and overlay docs clearly separated.

> STOP-on-BLOCKERS: if canonical source, required paths, or baseline artifacts are unavailable, stop and report blockers.

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests pass: `uv run -m unittest discover tests`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Format clean: `uv run ruff format --check .` (equivalent non-mutating check)
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs lint/build checks pass for changed docs
- [x] Habit-class mapping references canonical doc paths directly

### Gate 4: BDD (Heavy only)

- [x] Contract-level behavior checks executed or explicitly marked N/A with rationale

### Gate 5: Human (Heavy only)

- [x] Human attestation of OBPI completion and understanding recorded without ADR completion claim

## Verification

```bash
(cd /Users/jeff/Documents/Code/airlineops/docs/governance/GovZero && find . -type f -name "*.md" | sed 's#^\\./##' | sort)
(cd docs/governance/GovZero && find . -type f -name "*.md" | sed 's#^\\./##' | sort)
comm -3 <(cd /Users/jeff/Documents/Code/airlineops/docs/governance/GovZero && find . -type f -name "*.md" | sed 's#^\\./##' | sort) <(cd docs/governance/GovZero && find . -type f -name "*.md" | sed 's#^\\./##' | sort)
uv run mkdocs build --strict
uv run gz validate --documents
uv run -m unittest discover tests
uv run gz lint
uv run gz typecheck
uv run ruff format --check .
```

## Acceptance Criteria

- [x] All canonical GovZero files are present under `docs/governance/GovZero/` with filename parity.
- [x] Habit parity report references canonical doc paths as source evidence.
- [x] Parity scan reports now include OBPI-03 closure artifact documenting canonical doc-surface resolution.
- [x] Document validation and strict docs build pass after import.

## Evidence

### Implementation Summary

- Files created/modified:
  - `docs/governance/GovZero/*.md` (top-level canonical markdown mirror)
  - `docs/governance/GovZero/releases/*.md` (canonical recursive mirror)
  - `docs/governance/GovZero/audits/*.md` (canonical recursive mirror)
  - `mkdocs.yml` (docs root + canonical nav + scope filtering + link validation policy)
  - `docs/user/reference/charter.md` (overlay cross-reference to canonical charter)
  - `docs/user/concepts/lifecycle.md` (overlay cross-reference to canonical lifecycle)
  - `docs/user/concepts/obpis.md` (overlay cross-reference to canonical linkage)
  - `docs/user/concepts/closeout.md` (overlay cross-reference to canonical audit protocol)
  - `docs/proposals/REPORT-airlineops-parity-2026-02-14-obpi-03.md`
  - `docs/proposals/REPORT-airlineops-habit-parity-2026-02-14-obpi-03.md`
- Validation commands run:
  - Recursive path parity check (PASS; canonical 22, gzkit 22, diff 0)
  - Byte parity check (PASS; mismatches 0)
  - `uv run mkdocs build --strict` (PASS)
  - `uv run gz validate --documents` (PASS)
  - `uv run -m unittest discover tests` (PASS)
  - `uv run gz lint` (PASS)
  - `uv run gz typecheck` (PASS)
  - `uv run ruff format --check .` (PASS)
- Gate 4 rationale (if N/A):
  - N/A. No `features/` BDD suite exists in this repository.
- Human attestation:
  - Observation context: "there are habits there that we need"
  - Interpretation for this OBPI: canonical doctrine surface must be installed before semantic reconciliation.
  - Ledger evidence (observation context): `uv run gz adr emit-receipt ADR-0.3.0 --event validated --attestor "Jeffry Babb" --evidence-json '{"scope":"OBPI-0.3.0-03","adr_completion":"not_completed","obpi_completion":"completed_by_observation","observation":"there are habits there that we need","date":"2026-02-14"}'` (PASS)
  - Attestor statement: "I attest I understand the completion of OBPI-0.3.0-03."
  - Ledger evidence (attestation): `uv run gz adr emit-receipt ADR-0.3.0 --event validated --attestor "Jeffry Babb" --evidence-json '{"scope":"OBPI-0.3.0-03","adr_completion":"not_completed","obpi_completion":"attested_completed","attestation":"I attest I understand the completion of OBPI-0.3.0-03.","date":"2026-02-14"}'` (PASS)
- Date completed:
  - 2026-02-14

---

**Brief Status:** Completed
