---
id: OBPI-0.3.0-02-divergent-skill-reconciliation
parent: ADR-0.3.0
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.3.0-02-divergent-skill-reconciliation: Divergent Skill Reconciliation

## ADR Item

- **Source ADR:** `docs/design/adr/adr-0.3.x/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md`
- **Checklist Item:** #2 — "Reconcile shared skill behavior (`gz-adr-audit`, `gz-adr-create`) to canonical behavior."

**Status:** Completed

## Objective

Install full AirlineOps ADR create/audit behavior into gzkit so the operator experience is parity-complete: orientation, command execution, post-accounting, validation/verification, and human presentation.

## Lane

**Heavy** — Governance contract, runtime command surface, and operator proof surfaces are all affected.

## Allowed Paths

- `.github/skills/gz-adr-audit/**`
- `.github/skills/gz-adr-create/**`
- `.claude/skills/gz-adr-audit/**`
- `.claude/skills/gz-adr-create/**`
- `src/gzkit/**`
- `tests/**`
- `docs/user/commands/**`
- `docs/user/runbook.md`
- `docs/user/index.md`
- `docs/user/quickstart.md`
- `docs/proposals/**`
- `docs/design/constitutions/**` (for config-path coherence audit)

## Denied Paths

- `/Users/jeff/Documents/Code/airlineops/**`
- `.gzkit/ledger.jsonl (manual edits)`

## Requirements (FAIL-CLOSED)

1. MUST deliver hard rename cutover from `gz-adr-manager` to `gz-adr-create` in gzkit (no compatibility alias).
1. MUST replace shared skill stubs with full-depth create/audit procedures and assets.
1. MUST implement runnable gzkit command surfaces required by these skills (`closeout`, `audit`, `adr status`, `adr audit-check`, `adr emit-receipt`, `check-config-paths`, `cli audit`).
1. MUST update proof surfaces (manpages + runbook + user workflow pages) to match runtime behavior.
1. MUST produce gzkit-first AirlineOps backport guidance for bidirectional parity.
1. NEVER claim parity-complete while runtime commands or proof surfaces are missing.

> STOP-on-BLOCKERS: if canonical source, required paths, or baseline artifacts are unavailable, stop and report blockers.

## Quality Gates

### Gate 1: ADR

- [x] Intent and expanded scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests pass: `uv run -m unittest discover tests`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Manpages + runbook updated for new command surfaces

### Gate 4: BDD (Heavy only)

- [x] BDD executed OR explicitly N/A with rationale in evidence

### Gate 5: Human (Heavy only)

- [x] Human attestation of OBPI completion and understanding recorded (ADR-level closeout attestation remains separate)

## Verification

```bash
uv run -m unittest discover tests
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
uv run gz validate --documents
uv run gz cli audit
uv run gz check-config-paths
uv run gz adr audit-check ADR-0.3.0
uv run gz status --json
```

## Acceptance Criteria

- [x] `gz-adr-audit` and `gz-adr-create` are full-depth and non-stub in canonical and mirror surfaces.
- [x] `gz-adr-manager` is removed from active gzkit surfaces.
- [x] Runtime commands required by these skills are implemented and tested.
- [x] Manpages and runbook match command behavior.
- [x] New parity report records F-002 closure for gzkit and mandatory AirlineOps backport work.

## Evidence

### Implementation Summary

- Files created/modified:
  - `.github/skills/gz-adr-audit/SKILL.md`
  - `.github/skills/gz-adr-audit/assets/AUDIT.template.md`
  - `.github/skills/gz-adr-audit/assets/AUDIT_PLAN.template.md`
  - `.github/skills/gz-adr-create/SKILL.md`
  - `.github/skills/gz-adr-create/assets/ADR_TEMPLATE_SEMVER.md`
  - `.claude/skills/gz-adr-audit/**`
  - `.claude/skills/gz-adr-create/**`
  - `src/gzkit/cli.py`
  - `src/gzkit/ledger.py`
  - `src/gzkit/skills.py`
  - `src/gzkit/sync.py`
  - `tests/test_cli.py`
  - `tests/test_sync.py`
  - `docs/user/commands/*.md` (new command manpages + index)
  - `docs/user/runbook.md`
  - `docs/user/index.md`
  - `docs/user/quickstart.md`
  - `docs/proposals/PLAN-airlineops-backport-OBPI-0.3.0-02.md`
  - `docs/proposals/REPORT-airlineops-parity-2026-02-14.md`
- Validation commands run:
  - `uv run -m unittest discover tests` (PASS; 147 tests)
  - `uv run gz lint` (PASS)
  - `uv run gz typecheck` (PASS)
  - `uv run mkdocs build --strict` (PASS)
  - `uv run gz validate --documents` (PASS)
  - `uv run gz cli audit` (PASS)
  - `uv run gz check-config-paths` (PASS)
  - `uv run gz adr audit-check ADR-0.3.0` (FAIL by design-state: OBPI-03/04/05 not Completed)
  - `uv run gz status --json` (PASS)
- Gate 4 rationale (if N/A):
  - N/A. No `features/` BDD suite is present in this repository; Gate 4 evidence is represented through runtime parity checks, CLI orchestration behavior, and documentation proof surfaces.
- Human attestation:
  - Attestor: Jeffry Babb
  - Attestation: "I attest I understand the completion of OBPI-0.3.0-02."
  - Ledger evidence (attestation): `uv run gz adr emit-receipt ADR-0.3.0 --event validated --attestor "Jeffry Babb" --evidence-json '{"scope":"OBPI-0.3.0-02","adr_completion":"not_completed","obpi_completion":"attested_completed","attestation":"I attest I understand the completion of OBPI-0.3.0-02.","date":"2026-02-14"}'` (PASS)
  - Prior context receipt: `uv run gz adr emit-receipt ADR-0.3.0 --event validated --attestor "Jeffry Babb" --evidence-json '{"scope":"OBPI-0.3.0-02","correction":"Supersedes prior completed receipt emitted in error at 2026-02-14T11:34:29.927845+00:00.","adr_completion":"not_completed","obpi_completion":"completed_by_observation","observation":"no, we close the obpi with my observation","date":"2026-02-14"}'` (PASS)
  - Note: ADR-0.3.0 closeout remains open until remaining OBPIs are completed.
- Date completed:
  - 2026-02-14

---

**Brief Status:** Completed
