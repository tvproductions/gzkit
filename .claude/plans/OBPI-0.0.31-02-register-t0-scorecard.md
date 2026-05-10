# Plan: OBPI-0.0.31-02-register-t0-scorecard

OBPI: OBPI-0.0.31-02-register-t0-scorecard
Parent ADR: ADR-0.0.31-distribution-invariant-doctrine
Lane: Lite
Allowed Paths:
  - docs/governance/advisory-rules-audit.md

## Context

OBPI-0.0.31-02 adds a T0 scorecard row to `docs/governance/advisory-rules-audit.md`,
classifying the distribution invariant as **Promotable** with ADR-0.0.32 as the tracking
ADR. The brief's REQ-03 references OBPI-0.0.32-05 as the `gz validate --distribution`
landing point; the actual OBPI carrying that validator is OBPI-0.0.32-07
(validate-distribution). The brief was authored before ADR-0.0.32's OBPI numbering
settled. The row cites OBPI-0.0.32-07 as the correct landing point.

## Files

- `docs/governance/advisory-rules-audit.md`

## Steps

1. Confirm column shape by re-reading at least three existing Promotable rows (23,
   29/30, 49, 53 — all five available) to extract: `#`, `Rule` (one-sentence rule
   statement), `Score` (bolded classification), `Notes` (current state + tracking
   ADR/OBPI + future validator scope name + landing condition that flips Promotable
   → Mechanical).

2. Insert a new section "Distribution Invariant Doctrine (T0)" just before the
   `---\n## Summary` block (after the Editor/IDE Protocol Surface section at row 55):

   ```markdown
   ### Distribution Invariant Doctrine (T0) (`docs/governance/trust-doctrine.md` T0 layer + `ADR-0.0.31`)

   | # | Rule | Score | Notes |
   |---|------|-------|-------|
   | 56 | Every canonical surface (skills, rules, hooks, templates, chores, personas) MUST be reproducibly delivered by `pip install py-gzkit && gz init` to a fresh project, byte-equivalent to the wheel's authored canonical content. A wheel that ships without a canonical surface is a T0 breach regardless of whether downstream `gz init` reports success. | **Promotable** | T0 doctrine authored in `docs/governance/trust-doctrine.md` § T0 (OBPI-0.0.31-01) and ADR-0.0.31; mechanical enforcement pending OBPI-0.0.32-07 (`gz validate --distribution`, static check: pyproject.toml include + baseline manifest + on-disk canonical trees, exit 3 on any package-data omission). When OBPI-0.0.32-07 lands this row flips to **Mechanical**. Receipt-id prefix: `arb-distribution-`. |
   ```

3. Update the Summary table counts: Promotable 6 → 7, total 64 → 65 (date: 2026-05-10).

4. Run `uv run gz validate --advisory-scorecard` (scorecard self-test per AGENTS.md
   § Governance doctrine surfaces).

5. Run `uv run gz validate --documents` and `uv run mkdocs build --strict`.

## Verification

```bash
uv run gz validate --advisory-scorecard
uv run gz validate --documents
uv run mkdocs build --strict
grep -q "T0" docs/governance/advisory-rules-audit.md
grep -q "Promotable" docs/governance/advisory-rules-audit.md
grep -q "ADR-0.0.32" docs/governance/advisory-rules-audit.md
grep -q "OBPI-0.0.32-07" docs/governance/advisory-rules-audit.md
```

## Notes

- Documentation-only OBPI; no source, test, schema, or build changes.
- Row 56 is the next sequential number after the current maximum of 55.
- Summary Promotable count updates from 6 to 7; grand total from 64 to 65.
- Brief REQ-03 cites OBPI-0.0.32-05 as landing point; plan corrects to OBPI-0.0.32-07.

## Destination-in-mind disclosure (Step 6a)

**Destination already formed before this plan:** Insert a new section at the tail of the
Scorecard (before Summary), add row 56 classified Promotable, cite OBPI-0.0.32-07 as
the --distribution landing point, update the summary counts.

**Rejected alternatives:**
1. Place T0 row inside the existing "Governance Core" section — rejected; every recent
   rule addition (Exemplar Corpus, Complexity Thresholds, Token Block Discipline, Editor/IDE
   Protocol) gets its own section. T0 is a new rule family and warrants the same.
2. Cite OBPI-0.0.32-05 as the landing point per the brief — rejected based on primary-source
   evidence: OBPI-0.0.32-05 is `init-update-flag`; OBPI-0.0.32-07 is `validate-distribution`.
3. Use receipt prefix `arb-step-distribution-` — rejected; `arb-distribution-` follows
   the shorter pattern of `arb-ruff-` (not `arb-step-ruff-`) for validate-scope receipts.
