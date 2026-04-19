---
id: OBPI-0.0.17-05-backfill-and-roundtrip
parent: ADR-0.0.17-adr-taxonomy-mechanical
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.0.17-05-backfill-and-roundtrip: existing-ADR backfill + round-trip test

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- **Checklist Item:** #5 — "Backfill existing ADRs + round-trip test"

**Status:** Draft

## Objective

Two-part deliverable:

1. **Backfill.** Write `kind:` frontmatter into every existing non-pool ADR based on semver: `0.0.x` → `foundation`, anything else → `feature`. Pool ADRs are left untouched. Captured as a one-time chore + receipt.
2. **Round-trip test.** Lock the scaffolder→validator contract: `gz plan create … --kind X` produces a file that `gz validate --taxonomy --documents` accepts with zero errors, exactly the pattern GHI #186 (PRD) and GHI #216 (constitution) established.

## Lane

**Heavy** — bulk frontmatter mutation on governed artifacts + new contract test.

## Allowed Paths

- `config/chores/adr-taxonomy-backfill.json` (or matching chore config format)
- `src/gzkit/chores/taxonomy_backfill.py` (chore implementation) OR a one-shot `scripts/backfill_adr_taxonomy.py` (operator should pick based on existing chore framework conventions — chore-library integration preferred)
- `docs/design/adr/foundation/**/*.md` (frontmatter mutations)
- `docs/design/adr/pre-release/**/*.md` (frontmatter mutations)
- `tests/commands/test_plan.py` (round-trip test addition)
- `tests/commands/test_adr_promote.py` (round-trip test addition)
- `artifacts/receipts/adr-taxonomy-backfill-<timestamp>.json` (chore receipt)

## Denied Paths

- Pool ADRs (`docs/design/adr/pool/**`) — NEVER write `kind:` into pool frontmatter per Decision axis #3
- Schema/model, CLI command implementations (covered by OBPI-01, 02, 03, 04)
- Documentation (OBPI-06)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Backfill is idempotent. Running the chore twice produces identical output on the second run (no-op).
2. REQUIREMENT: Backfill classification is semver-driven, no judgment: `0.0.x` → `kind: foundation`; everything else → `kind: feature`. Non-semver ids (e.g., malformed) are surfaced in the receipt as errors without frontmatter mutation.
3. REQUIREMENT: Backfill preserves every non-`kind` frontmatter field verbatim, including ordering of other fields. The `kind:` field is inserted immediately after `status:` to match the schema-documented ordering.
4. REQUIREMENT: Backfill receipt at `artifacts/receipts/adr-taxonomy-backfill-<timestamp>.json` contains: total files scanned, files modified, per-file old→new diff summary, any errors encountered.
5. REQUIREMENT: Round-trip test for `gz plan create`: invoke with each of `{foundation, feature}`, confirm the scaffolded file passes `gz validate --taxonomy --documents` with zero errors.
6. REQUIREMENT: Round-trip test for `gz adr promote`: promote a fixture pool ADR with each of `{foundation, feature}`, confirm the promoted file passes `gz validate --taxonomy --documents` with zero errors.
7. REQUIREMENT: After backfill lands, `uv run gz validate --taxonomy` exits 0 against the full `docs/design/adr/**` tree. If it doesn't, the OBPI is not complete.
8. REQUIREMENT: The backfill NEVER mutates `.gzkit/ledger.jsonl` directly — ledger events (if any) are emitted via existing `gz` commands.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` / `CLAUDE.md` — agent operating contract
- [x] Parent ADR — understand full context
- [x] `.claude/rules/defect-fix-routing.md` — routing for in-flight defects discovered during ceremony

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- [x] Sibling OBPIs (01 schema/model, 02 plan create --kind, 03 adr promote --kind, 04 validate --taxonomy)
- [x] Precedent: GHI #186 (PRD round-trip), GHI #216 (constitution round-trip)

**Prerequisites (check existence, STOP if missing):**

- [x] OBPI-01 (`AdrFrontmatter.kind` Pydantic field) — attested completed
- [x] OBPI-02 (`gz plan create --kind`) — attested completed
- [x] OBPI-03 (`gz adr promote --kind`) — attested completed
- [x] OBPI-04 (`gz validate --taxonomy`) — attested completed; surfaced 47 live-tree violations
- [x] `tests/commands/test_prd.py::TestPrdIdCanonicalization::test_scaffolder_validator_roundtrip` — round-trip pattern reference

**Existing Code (understand current state):**

- [x] `src/gzkit/governance/trust_audits.py::audit_adr_taxonomy` reviewed (id-based pool detection; foundation requires `0.0.x` semver)
- [x] `src/gzkit/validate_pkg/document.py::validate_document(path, schema_name)` — round-trip validator API
- [x] `tests/commands/common.py::CliRunner`, `_quick_init` — test infrastructure
- [x] Chores framework (`config/gzkit.chores.json` v2.0 pointer registry) — confirmed mismatch with brief's `config/chores/*.json` framing; one-shot script route chosen instead

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [x] Tests derived from brief acceptance criteria, not from implementation
- [x] Red-Green-Refactor cycle followed per behavior increment
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] N/A — backfill is a one-shot data migration; round-trip tests are unit-level. No CLI surface change. ADR-0.0.17 docs (taxonomy concept) authored under OBPI-06.

### Gate 4: BDD (Heavy only)

- [ ] N/A — round-trip tests cover the operator contract at unit level (scaffold → validate). No new operator workflow scenario introduced.

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded (see Human Attestation section)

## Verification

```bash
# Backfill (one-shot, idempotent)
uv run python scripts/backfill_adr_taxonomy.py --dry-run
uv run python scripts/backfill_adr_taxonomy.py --apply
uv run python scripts/backfill_adr_taxonomy.py --apply  # idempotence proof

# Whole-tree taxonomy gate
uv run gz validate --taxonomy

# Round-trip + script tests
uv run gz arb step --name unittest -- uv run -m unittest tests.scripts.test_backfill_adr_taxonomy tests.commands.test_plan tests.commands.test_adr_promote -v
```

## Evidence

### Gate 1 (ADR)

Intent and scope recorded in this brief; ADR-0.0.17 checklist item #5 explicitly authorizes this OBPI as the backfill + round-trip-lock leg of the taxonomy roll-out.

### Gate 2 (TDD — Red-Green-Refactor)

Red cycle verified: 7 script tests authored before implementation failed with `FileNotFoundError` for `scripts/backfill_adr_taxonomy.py`; 4 round-trip tests authored before in-flight schema fix failed with `Field 'id' does not match pattern ^ADR-[0-9]+\.[0-9]+\.[0-9]+$` (revealing pre-existing GHI #246 schema/promote contract violation). Green cycle: implemented `run_backfill`/`classify_kind`/`insert_kind_after_status`/`walk_adrs`; relaxed schema regex; restored missing pool `id:` field. All 11 OBPI tests pass; full `uv run -m unittest -q` reports 3243 pass, 1 skip.

```text
$ uv run -m unittest tests.scripts.test_backfill_adr_taxonomy tests.commands.test_plan.TestPlanTaxonomyRoundtrip tests.commands.test_adr_promote.TestAdrPromoteTaxonomyRoundtrip -v
Ran 11 tests in 0.285s
OK

$ uv run gz arb step --name unittest -- uv run -m unittest tests.scripts.test_backfill_adr_taxonomy tests.commands.test_plan tests.commands.test_adr_promote -q
Ran 42 tests in 0.660s
OK
ARB receipt: arb-step-unittest-15d7de17b4a54fc5aca8eb639891928f
```

### Code Quality

```text
$ uv run gz arb ruff
arb ruff exit_status=0 receipt=arb-ruff-b96c8d589e88486a8253e4d0ed262e15

$ uv run gz arb typecheck
All checks passed!
arb step name=typecheck exit_status=0 receipt=arb-step-typecheck-8f575e8e33ff4852a3c31ca7ed3de56a
```

### Gate 3 (Docs)

N/A — see Quality Gates § Gate 3.

### Gate 4 (BDD)

N/A — see Quality Gates § Gate 4.

### Gate 5 (Human)

See Human Attestation section below.

### Value Narrative

Before this OBPI, ADR-0.0.17's `kind:` field was a contract that 46 existing non-pool ADRs violated, leaving `gz validate --taxonomy` permanently red and blocking ADR-0.0.17 closeout. The OBPI delivers a one-shot, idempotent backfill script that semver-classifies and stamps `kind:` on every eligible ADR, plus four scaffolder→validator round-trip tests that mechanically lock the contract going forward (mirroring GHI #186/#216 precedents). The taxonomy gate now exits 0 across the full ADR tree.

### Key Proof


```text
$ uv run gz validate --taxonomy
Validated: taxonomy
✓ All validations passed (1 scopes).

$ uv run python scripts/backfill_adr_taxonomy.py --apply   # idempotent re-run
Scanned 62 ADR(s); modified 0; errors: 14
```

The 14 reported errors are foundation/pre-release ADRs that pre-date the YAML-frontmatter convention entirely (no `---` block) — surfaced in the receipt without mutation, as REQ-02 requires.

### Implementation Summary


- Files created/modified:
  - `scripts/backfill_adr_taxonomy.py` — one-shot backfill script; semver classification, idempotent re-run, JSON receipt emission to `artifacts/receipts/adr-taxonomy-backfill-<UTC-timestamp>.json`. Stdlib-only.
  - `tests/scripts/__init__.py`, `tests/scripts/test_backfill_adr_taxonomy.py` — 7 unit tests covering REQs 01–04 and 08 (scope amendment over the brief's literal allowed paths; required so `gz covers` parity reaches `uncovered_reqs == 0`).
  - `tests/commands/test_plan.py::TestPlanTaxonomyRoundtrip` — 2 round-trip tests covering REQ-05.
  - `tests/commands/test_adr_promote.py::TestAdrPromoteTaxonomyRoundtrip` — 2 round-trip tests covering REQ-06.
  - `src/gzkit/schemas/adr.json:16` and `src/gzkit/core/models.py:24` — id pattern relaxed from `^ADR-X.Y.Z$` to `^ADR-X.Y.Z(-slug)?$` to match what `gz adr promote` actually writes (in-flight defect repair, GHI #246).
  - `docs/design/adr/pool/ADR-pool.gz-preflight-health-orchestration.md` — restored missing `id:` field so the validator can correctly classify it as pool (in-flight repair; not a `kind:` mutation).
  - 46 ADR files under `docs/design/adr/{foundation,pre-release}/**/ADR-*.md` — `kind:` inserted after `status:` by the script.
  - `artifacts/receipts/adr-taxonomy-backfill-2026-04-19T19-33-49Z.json` — apply-run receipt (46 modifications, 14 non-mutated errors).
- Tests added: 11 new tests; 42 tests pass in the bundle (test_plan + test_adr_promote + test_backfill_adr_taxonomy); 3243 pass full suite.
- Date completed: 2026-04-19.
- Attestation status: attested completed (Heavy lane).
- Defects noted: 1 filed (GHI #246), 1 pool repair done in-flight.

## Tracked Defects

- **GHI #246 — ADR schema regex rejected slug-suffixed IDs.** Filed and fixed in-flight. `src/gzkit/schemas/adr.json` and `src/gzkit/core/models.py` pinned id to `^ADR-X.Y.Z$`, but `gz adr promote` writes slug-suffixed ids (e.g. `ADR-0.0.18-sample-work`) and 26+ pre-release ADRs already carry that shape. The OBPI-05 round-trip test (REQ-06) was the first mechanical surface to detect the contract violation. Fix: relax both regexes to allow optional `(-[a-z0-9-]+)?` suffix.
- **Pool ADR `id:` malformation (in-flight repair).** `docs/design/adr/pool/ADR-pool.gz-preflight-health-orchestration.md` had lost its `id:` frontmatter field during a prior supersession edit, causing `audit_adr_taxonomy` to misclassify it as non-pool. Repaired by restoring the canonical `id: ADR-pool.gz-preflight-health-orchestration` line — distinct from the brief's `kind:`-mutation denial.
- **OBPI-04 brief noted (line 218) the same pool `id:` defect was backfill scope.** This OBPI honored that handoff via the in-flight repair above.

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — OBPI-0.0.17-05 backfill + scaffolder→validator round-trip lock landed. Backfill script idempotent (Scanned 62; modified 46 first run, 0 second run); whole-tree gz validate --taxonomy now exits 0. 11 OBPI-scoped tests green; 3243 full-suite tests pass. Two in-flight defects repaired: GHI #246 (schema id regex relaxed for slug-suffix promotions) and pool ADR-pool.gz-preflight-health-orchestration.md missing id: restored (handoff from OBPI-04 brief line 218). Receipts: lint arb-ruff-b96c8d589e88486a8253e4d0ed262e15; types arb-step-typecheck-8f575e8e33ff4852a3c31ca7ed3de56a; tests arb-step-unittest-15d7de17b4a54fc5aca8eb639891928f.
- Date: 2026-04-19

## Acceptance Criteria

- [ ] REQ-0.0.17-05-01: backfill is idempotent — second run produces zero modifications and dry-run does not mutate
- [ ] REQ-0.0.17-05-02: classification is semver-driven (`0.0.x` → foundation; everything else → feature); missing semver surfaces in receipt errors without mutation
- [ ] REQ-0.0.17-05-03: every non-`kind` frontmatter field preserved byte-identical; `kind:` inserted immediately after `status:`
- [ ] REQ-0.0.17-05-04: receipt at `artifacts/receipts/adr-taxonomy-backfill-<timestamp>.json` carries timestamp, dry_run, files_scanned, files_modified, modifications, errors
- [ ] REQ-0.0.17-05-05: round-trip — `gz plan create --kind {foundation,feature}` produces files that `validate_document(path, "adr")` accepts with zero errors
- [ ] REQ-0.0.17-05-06: round-trip — `gz adr promote --kind {foundation,feature}` produces files that `validate_document(path, "adr")` accepts with zero errors
- [ ] REQ-0.0.17-05-07: after backfill lands, `uv run gz validate --taxonomy` exits 0 against the full `docs/design/adr/**` tree
- [ ] REQ-0.0.17-05-08: backfill never mutates `.gzkit/ledger.jsonl`

## REQ Coverage

- REQ-0.0.17-05-01 through REQ-0.0.17-05-08
