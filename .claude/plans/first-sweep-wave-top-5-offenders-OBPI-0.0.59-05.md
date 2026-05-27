# OBPI-0.0.59-05: First Sweep Wave — Top 5 Offenders

## Context

ADR-0.0.59 Decision item 4 (last clause): operator-paced first sweep wave of the
`decommission-tautological-tests` chore over the five named worst-offender
governance test files. The chore infrastructure shipped in OBPI-0.0.59-04;
this OBPI applies the chore — per-file disposition decisions, per-file ledger
event emission, and post-wave baseline regeneration + drift-gate validation.

Parent ADR: ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine
OBPI: OBPI-0.0.59-05-first-sweep-wave-top-5-offenders
Lane: Heavy
Sensitivity: absent

## Files

### Modified files (per-file disposition application)

- `tests/governance/test_audit_check_covers_backfill.py` — remove tautological doc-cite test (1 AST op); REQ-0.0.23-05-10 retains sibling BEHAVIOR coverage via parser-registration test
- `tests/governance/test_promoted_advisory_audits.py` — remove 4 scorecard-cite tests (4 AST ops); keep 1 as fixture (hash-compare non-mutation BEHAVIOR test, line 766)
- `tests/governance/test_distribution_audit.py` — remove 2 tautological tests (2 AST ops); keep 2 as fixtures (tempdir manifest idempotence + tempdir ledger emission BEHAVIOR tests)
- `tests/governance/test_brief_path_validity.py` — no-op; 0 AST ops by scanner (scanner false-positive in original #531 quantification)

### Deleted files

- `tests/governance/test_token_block_discipline.py` — whole-file delete (10 tautological tests, no `@covers` decorators; archetypal anti-pattern)

### State-file regeneration

- `data/tautological_test_baseline.json` — regenerated post-wave (`exclude={'context_hint'}` to avoid retired-path leak — defect noted in brief Tracked Defects)
- `data/tautological_test_waivers.json` — 3 new waiver entries (rationale keys: `obpi-0.0.59-05-hash-compare-non-mutation`, `obpi-0.0.59-05-tempdir-manifest-idempotence`, `obpi-0.0.59-05-tempdir-ledger-emission`)

### BDD waiver

- `data/behave_coverage_waivers.json` — add `obpi-0.0.59-05-bdd-deferred-to-adr-closeout` default-rationale key + waiver entry for all 5 REQs (deferred to ADR-0.0.59 closeout composite scope)

### OBPI brief

- `docs/design/adr/foundation/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine/obpis/OBPI-0.0.59-05-first-sweep-wave-top-5-offenders.md` — substantively authored brief + Evidence section fills

## Steps

### Step 1: Author brief substantively (Stage 1)

Fill Objective, Allowed Paths, Denied Paths, Requirements (REQs with `[kind]` tags),
Discovery Checklist, Quality Gates, Verification, Demo, Acceptance Criteria.
Validate via `gz validate --req-kind-discipline` and `gz obpi validate --authored`.

### Step 2: Claim OBPI lock

`gz obpi lock claim OBPI-0.0.59-05-first-sweep-wave-top-5-offenders --ttl 240`

### Step 3: Launch pipeline (emits pipeline_launched event)

`gz obpi pipeline OBPI-0.0.59-05-first-sweep-wave-top-5-offenders`

### Step 4: Per-file sweep (operator-paced)

For each of the five named files in order:

1. Scan with `scan_test_tree()` + `propose_disposition()`
2. Read the file at scan-line context
3. Surface proposed disposition to operator with rationale
4. Apply operator-confirmed disposition (edit / delete / waive)
5. Run `uv run python -m unittest <file>` — confirm passing
6. Emit `chore_decommission_processed` ledger event via `gzkit.ledger_events.chore_decommission_processed_event()`

### Step 5: Regenerate baseline

```python
ops = scan_test_tree(Path('tests'))
baseline = {
    'operations': [op.model_dump(exclude={'context_hint'}) for op in ops],
    'generated_at': datetime.now(timezone.utc).isoformat(),
}
Path('data/tautological_test_baseline.json').write_text(json.dumps(baseline, indent=2))
```

Emit `artifact_edited` events citing `data/tautological_test_baseline.json` and `data/tautological_test_waivers.json`.

### Step 6: Verify drift gate + full check

```bash
uv run gz validate --tautological-test-audit  # exit 0
uv run gz check                                # all steps pass
```

### Step 7: Fill brief Evidence section

Per-File Disposition Log (5 rows), Baseline Snapshot summary, Value Narrative, Key Proof (file-4 whole-file delete is canonical demo), Implementation Summary, Tracked Defects.

### Step 8: Pipeline verify -> ceremony -> sync -> complete

`gz obpi precomplete`, then `gz obpi pipeline --from verify` (and through subsequent stages).

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --tautological-test-audit
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run mkdocs build --strict
grep '"event":"chore_decommission_processed"' .gzkit/ledger.jsonl | grep "OBPI-0.0.59-05" | wc -l  # expect 5
```

## Notes

- Operator-paced per ADR-0.0.59 § Decision item 4 — each file's disposition requires explicit operator review before application.
- Scope-collision warnings from plan-audit (6 sibling-ADR overlaps on shared `tests/governance/test_*.py` files) are all advisory — those siblings shipped tests in the named files; this OBPI deletes/rewrites only the tautological-pattern subset, preserving sibling REQ coverage via @covers retention or documented reclassification in Tracked Defects.
- AST scanner is the canonical authority on op counts; the regex/wc counts quoted in the parent-ADR checklist text (49/50/26/20/23) are methodology-only different (AST is conservative; no in-flight edits to the 5 files since the 2026-05-25 measurement).
- Three legacy REQs (`REQ-0.0.17-04-10`, `REQ-0.0.32-07-08`, `REQ-0.0.32-07-09`) enter effective-SUPPORT-pending-reclassification — tracked in brief § Tracked Defects with full proof-channel preservation note.
- CHORE.md § 4 baseline-regen recipe defect (`context_hint` leak) tracked in brief § Tracked Defects with recommended structural fix path.
- BDD deferred to ADR-0.0.59 closeout (same composite-scope pattern as OBPI-02, -03, -04).
