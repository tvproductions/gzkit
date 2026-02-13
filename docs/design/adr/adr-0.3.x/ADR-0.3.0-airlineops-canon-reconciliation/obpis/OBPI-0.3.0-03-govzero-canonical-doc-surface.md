---
id: OBPI-0.3.0-03-govzero-canonical-doc-surface
parent: ADR-0.3.0
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.3.0-03-govzero-canonical-doc-surface: GovZero Canonical Doc Surface

## ADR Item

- **Source ADR:** `docs/design/adr/adr-0.3.x/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md`
- **Checklist Item:** #3 — "Import missing canonical `docs/governance/GovZero/*.md` files."

**Status:** Draft

## Objective

Establish a canonical GovZero docs surface in gzkit by importing the missing AirlineOps governance documents.

## Lane

**Heavy** — External governance parity surface and operator contract impact.

## Allowed Paths

- `docs/governance/GovZero/*.md`
- `docs/lodestar/README.md`
- `docs/proposals/REPORT-airlineops-parity-*.md`

## Denied Paths

- `/Users/jeff/Documents/Code/airlineops/**`
- `src/gzkit/**`
- `.gzkit/ledger.jsonl (manual edits)`

## Requirements (FAIL-CLOSED)

1. MUST create `docs/governance/GovZero/` in gzkit and import all currently-missing canonical markdown files.
1. MUST preserve canonical filenames and structure for path-level parity.
1. MUST add provenance notes without rewriting canonical meaning.
1. NEVER silently reinterpret canonical governance text.
1. ALWAYS keep canonical and overlay docs clearly separated.

> STOP-on-BLOCKERS: if canonical source, required paths, or baseline artifacts are unavailable, stop and report blockers.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests pass: `uv run -m unittest discover tests`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Format clean: `uv run gz format --check` (or equivalent non-mutating check)
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs lint/build checks pass for changed docs

### Gate 4: BDD (Heavy only)

- [ ] Contract-level behavior checks executed or explicitly marked N/A with rationale

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
find /Users/jeff/Documents/Code/airlineops/docs/governance/GovZero -maxdepth 1 -type f -name "*.md" -exec basename {} \; | sort
find docs/governance/GovZero -maxdepth 1 -type f -name "*.md" -exec basename {} \; | sort
uv run gz validate --documents
```

## Acceptance Criteria

- [ ] All missing canonical GovZero files are present under `docs/governance/GovZero/`.
- [ ] Parity scan no longer reports canonical GovZero doc-surface as missing.
- [ ] Document validation passes after import.

## Evidence

### Implementation Summary

- Files created/modified:
- Validation commands run:
- Date completed:

---

**Brief Status:** Draft
