---
id: OBPI-0.0.17-03-adr-promote-kind
parent: ADR-0.0.17-adr-taxonomy-mechanical
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.17-03-adr-promote-kind: --kind flag on gz adr promote

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- **Checklist Item:** #3 — "`gz adr promote --kind` CLI flag + promotion validation"

**Status:** Draft

## Objective

Promotion is the moment a pool ADR is committed to work. `gz adr promote ADR-pool.<slug> --kind {foundation, feature} --semver X.Y.Z --lane {lite, heavy}` now expresses the taxonomic intent at promotion time: the promoted ADR's frontmatter carries the correct `kind:` field, the target directory matches (`foundation/` vs `pre-release/`), and the kind/semver binding is enforced before any file is moved.

## Lane

**Heavy** — CLI contract addition on an existing public command.

## Allowed Paths

- `src/gzkit/cli/parser_artifacts.py`
- `src/gzkit/commands/adr_promote.py` (or whatever module hosts `adr promote`)
- `tests/commands/test_adr_promote.py`
- `docs/user/commands/adr-promote.md` (or equivalent)

## Denied Paths

- Schema/model (OBPI-01)
- `gz plan create` (OBPI-02)
- `gz validate` (OBPI-04)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz adr promote --help` shows `--kind {foundation, feature}` as a required flag. Pool→pool promotion is not a valid operation; `--kind pool` is rejected with exit 1.
2. REQUIREMENT: `--kind foundation` requires `--semver` to match `^0\.0\.\d+$`. Mismatch → exit 1, no file moved, clear recovery message.
3. REQUIREMENT: `--kind feature` requires `--semver` to NOT match `^0\.0\.\d+$`. Mismatch → exit 1, no file moved.
4. REQUIREMENT: The pool source file is preserved (not deleted/moved) until all validation passes; promotion is atomic from the operator's perspective.
5. REQUIREMENT: The promoted ADR's frontmatter carries `kind: <value>` in addition to the existing fields (id, status, semver, lane, parent, date). The id changes from `ADR-pool.<slug>` to `ADR-X.Y.Z`.
6. REQUIREMENT: The promoted ADR lands at:
   - `docs/design/adr/foundation/ADR-X.Y.Z-<slug>/ADR-X.Y.Z-<slug>.md` for `--kind foundation`
   - `docs/design/adr/pre-release/ADR-X.Y.Z-<slug>/ADR-X.Y.Z-<slug>.md` for `--kind feature`
7. REQUIREMENT: The ledger event emitted by promotion records both `kind` and `semver` so downstream audits can reason about the decision. The event schema extension is additive and backward-compatible.
8. REQUIREMENT: Existing `gz adr promote` behavior for already-approved promotions remains unchanged except for the new required flag.

## Verification

```bash
uv run gz adr promote --help | grep -- --kind
# End-to-end smoke (against a throwaway pool ADR created in the test fixture):
#   gz adr promote ADR-pool.test --kind feature --semver 0.99.0 --lane lite
#   → writes docs/design/adr/pre-release/ADR-0.99.0-test/ADR-0.99.0-test.md with kind: feature
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_adr_promote -v
```

## Evidence

- Help output showing `--kind` registered
- Test transcript for each kind + the `--kind pool` rejection
- Ledger event dump showing `kind` and `semver` fields
- ARB receipts

## REQ Coverage

- REQ-0.0.17-03-01 through REQ-0.0.17-03-08
