---
id: OBPI-0.0.17-05-backfill-and-roundtrip
parent: ADR-0.0.17-adr-taxonomy-mechanical
item: 5
lane: Heavy
status: Draft
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

## Verification

```bash
# Pre-backfill: taxonomy validator reports every non-pool ADR as missing kind
uv run gz validate --taxonomy  # expected: violations listed per file
# Run backfill (idempotent)
uv run gz chores run adr-taxonomy-backfill  # or equivalent invocation
# Second run is no-op
uv run gz chores run adr-taxonomy-backfill
# Post-backfill: clean
uv run gz validate --taxonomy
# Round-trip tests
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_plan tests.commands.test_adr_promote -v
```

## Evidence

- Backfill receipt artifact
- Before/after `gz validate --taxonomy` outputs
- Round-trip test output for each kind
- Idempotence proof (second-run receipt shows zero modifications)
- ARB receipts

## REQ Coverage

- REQ-0.0.17-05-01 through REQ-0.0.17-05-08
