---
id: OBPI-0.0.37-05-brief-reconcile-engine
parent: ADR-0.0.37-constitutional-invariant-composition
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.37-05-brief-reconcile-engine: Brief Reconcile Engine

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #5 — "OBPI-0.0.37-05 — Brief reconciliation engine (project-tree walker; per-dimension delta computation across the five drift classes)"

**Status:** Draft

## Objective

Land the engine that walks a brief (parsed via OBPI-04's `BriefStructure`), walks the current project tree, and computes per-dimension deltas across the five drift classes (allowlist, Discovery Checklist, Verification verbs, REQ counts, citation tuples). Engine returns a structured `ReconcileResult` per ADR § Decision Rationale point 4. Backs the `gz brief reconcile` CLI (OBPI-06) and the Stage 1/5 gates (OBPI-07/08).

## Lane

**Heavy** — Engine surface that pipeline gates depend on. Runtime contract.

## Allowed Paths

- `src/gzkit/governance/brief_reconcile.py` (new) — reconcile engine
- `src/gzkit/governance/trust_audits/brief_reconcile.py` (new) — `validate_brief_reconcile` validator-scope wrapper
- `src/gzkit/governance/trust_audits/__init__.py` (modify) — register the validator
- `tests/governance/test_brief_reconcile.py` (new)
- `tests/fixtures/brief_reconcile/` (new) — fixture briefs + project trees (matching, allowlist-drift, verb-drift, req-drift, citation-drift)
- `features/brief_reconcile.feature` (new) — BDD scenarios for CIC-2 reconcile engine; tagged `@REQ-0.0.37-05-*`; subsequent OBPIs (06, 07, 08) add scenarios to this file
- `docs/governance/advisory-rules-audit.md` (modify) — scorecard entry for `--brief-reconcile`
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-05-brief-reconcile-engine.md` (this brief)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/governance/brief_structure.py` (OBPI-04 — consume)
- CLI verb — OBPI-06
- Ledger event registration (`brief_reconciled`, `brief_reconcile_drift_detected`) — OBPI-06 owns these
- Pipeline gates — OBPI-07/08
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `reconcile_brief(brief_path: Path, project_root: Path) -> ReconcileResult` is the engine entry point. `ReconcileResult` is a frozen dataclass with fields:
   - `brief_id: str`
   - `allowlist_delta: AllowlistDelta` (missing_in_brief: list[str]; missing_on_disk: list[str])
   - `discovery_delta: DiscoveryDelta` (unresolved_paths: list[str])
   - `verification_delta: VerificationDelta` (unresolved_verbs: list[str])
   - `req_count_delta: ReqCountDelta` (declared_reqs: int, acceptance_criteria_count: int, delta: int)
   - `citation_delta: CitationDelta` (stale_citations: list[tuple[str, str]])
   - `has_drift: bool` (True if any dimension delta is non-empty/non-zero)
2. REQUIREMENT (allowlist dimension): For each path in `BriefStructure.allowlist`, the engine cross-references against (a) test files that import the path, (b) actual on-disk existence. Reports `missing_on_disk` (allowlisted path doesn't exist after implementation) and `missing_in_brief` (a src/ file imported by REQ tests but not allowlisted).
3. REQUIREMENT (Discovery Checklist dimension): Parses the brief's `## Discovery Checklist` markdown bullets that reference paths; for each path, checks file existence; `unresolved_paths` are those that don't exist.
4. REQUIREMENT (Verification verbs dimension): Parses every `gz <verb>` reference in the brief's `## Verification` block; resolves each against `src/gzkit/cli/parser_artifacts.py` registered verbs; `unresolved_verbs` are those not in the parser registry.
5. REQUIREMENT (REQ count dimension): Compares len(BriefStructure.reqs) against the count of checkbox items in `## Acceptance Criteria`; non-zero delta reported.
6. REQUIREMENT (citation tuples dimension): For each `(artifact_path, anchor)` in `BriefStructure.citations`, verifies (a) artifact_path exists, (b) anchor (e.g., a heading or REQ-ID) exists within that artifact. Stale citations reported.
7. REQUIREMENT: `validate_brief_reconcile(root: Path)` is the trust-audit-scope wrapper that walks all OBPI briefs in the project, runs `reconcile_brief` against each, returns ERROR severity when any brief has drift. Wired into `gz validate --brief-reconcile`.
8. REQUIREMENT: Engine is pure (no I/O side effects beyond reading files; no ledger writes). Ledger emission belongs to OBPI-06's CLI surface.

> STOP-on-BLOCKERS: OBPI-04 (`BriefStructure`) must be landed; engine consumes it.

## Discovery Checklist

**Parent ADR:**

- [ ] Quote ADR § Decision item #5 (reconcile engine) verbatim
- [ ] ADR § Decision Rationale point 4 (the five drift dimensions) — the engine's contract

**Governance:**

- [ ] `.gzkit/rules/governance-core.md` § Operator-doc verb resolution — the `gz <verb>` reference resolution pattern is the same shape needed for dimension #4
- [ ] `.gzkit/rules/brief-heading-conventions.md` — H2/H3 boundary informs section-parsing

**Context (exemplars):**

- [ ] `src/gzkit/governance/trust_audits/cli.py` — verb-resolution against `parser_artifacts.py` already implemented; reuse, do not re-implement
- [ ] `src/gzkit/governance/briefs.py` — existing brief-reading helpers
- [ ] `src/gzkit/governance/code_quality.py` — example of a dataclass-returning audit module

**Prerequisites:**

- [ ] OBPI-04 landed
- [ ] `src/gzkit/cli/parser_artifacts.py` parseable (verb registry accessible)

## Quality Gates

- [ ] Gate 1: Reconcile-engine paragraph quoted
- [ ] Gate 2: `test_brief_reconcile.py` covers one passing fixture + one drifted fixture per dimension (5 drifts × at least 1 case each); RGR followed
- [ ] Code Quality: lint + typecheck
- [ ] Gate 3: `advisory-rules-audit.md` scorecard entry for `--brief-reconcile`; mkdocs strict
- [ ] Gate 4: `features/brief_reconcile.feature` includes scenarios per dimension tagged `@REQ-0.0.37-05-*`; behave passes
- [ ] Gate 5: Foundation-kind attestation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_brief_reconcile -v
uv run mkdocs build --strict
uv run -m behave features/brief_reconcile.feature --tags=REQ-0.0.37-05

# REQ-01: engine returns ReconcileResult
uv run python -c "
from pathlib import Path
from gzkit.governance.brief_reconcile import reconcile_brief
r = reconcile_brief(
    Path('docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-01-invariant-schema-and-registry.md'),
    Path('.')
)
print(f'brief_id={r.brief_id} has_drift={r.has_drift}')
assert r.brief_id == 'OBPI-0.0.37-01-invariant-schema-and-registry'
print('REQ-01 OK')
"

# REQ-07: validator wrapper resolves via gz validate --brief-reconcile
uv run gz validate --brief-reconcile && echo "REQ-07 OK on clean tree"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-05-01: `reconcile_brief(brief_path, project_root)` returns `ReconcileResult` with `brief_id`, all five dimension-delta fields, and `has_drift: bool`
- [ ] REQ-0.0.37-05-02: Allowlist dimension reports `missing_on_disk` for an allowlisted path that does not exist; reports `missing_in_brief` for a src/ file imported by REQ tests but absent from allowlist
- [ ] REQ-0.0.37-05-03: Verification-verb dimension resolves `gz <verb>` references against `parser_artifacts.py`; reports `unresolved_verbs` for unregistered verbs
- [ ] REQ-0.0.37-05-04: REQ count dimension compares declared REQs vs Acceptance Criteria checkbox count and reports delta
- [ ] REQ-0.0.37-05-05: Citation-tuple dimension verifies (artifact_path, anchor) pairs and reports stale citations
- [ ] REQ-0.0.37-05-06: `gz validate --brief-reconcile` exits 0 when no brief has drift; exits 3 when any brief has drift; reports per-brief delta in output
- [ ] REQ-0.0.37-05-07: Engine is pure — emits no ledger events, writes no files (ledger emission belongs to OBPI-06)

## Completion Checklist

- [ ] All gates satisfied
- [ ] `gz brief reconcile OBPI-0.0.37-05-brief-reconcile-engine` reports zero drift

## Evidence

```text
# Per-gate outputs
```

### Value Narrative

<!-- Before: brief drift was caught only by manual evaluation (as in EVALUATION_SCORECARD.md for ADR-0.0.37 itself). After: engine computes drift per dimension mechanically; humans review delta summaries, not raw briefs. -->

### Key Proof

<!-- Run engine against one ADR-0.0.37 OBPI brief and another adjacent brief; show per-dimension deltas. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #495, GHI #485

## Human Attestation

- Attestor: `<name>`
- Attestation: per ADR-0.0.36 universal Gate 5
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
