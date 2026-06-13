# Plan: OBPI-0.0.70-04-fourth-source-triangulation

## Context

- **OBPI:** OBPI-0.0.70-04-fourth-source-triangulation
- **Parent ADR:** ADR-0.0.70-turn-end-feedback-and-correction-mining
- **Lane:** Lite (docs-only; no CLI/schema/runtime-contract change)
- **ADR checklist item #4 (verbatim):** "Fourth-source doctrine triangulation — Buetow section appended to `docs/governance/harness-engineering-appraisal.md` per the established per-thesis pattern (citation: Beyond Coding Podcast, 2026-06-10); campaign B.0 cross-link; `mkdocs build --strict` green"

## Files

- `docs/governance/harness-engineering-appraisal.md` — append Buetow section after the CE section, following per-thesis pattern
- `docs/governance/build-to-1.0-campaign-2026-06-10.md` — insert B.0 amendment with operator-verbatim words (2026-06-12), recorded in place per Magna Carta amendment discipline

## Steps

1. Read `harness-engineering-appraisal.md` to understand the per-thesis pattern (Böckeler, Greyling, CE sections)
2. Append `## Fourth Source — Buetow...` section with:
   - Source block (full citation: Beyond Coding Podcast, 2026-06-10 + cracking-ai-engineering.com)
   - Framing (practitioner interview, single-practitioner anecdata, convergent signal not independent proof)
   - Triangulation table (what converges with prior three sources)
   - Adopted-deltas table mapping to OBPI-01/02/03
   - "What Buetow does NOT add" note
   - Sidecar funded-not-displaced statement
   - `ADR-pool.harness-sidecar` dangling-reference reconciliation
   - Campaign B.0 cross-link
3. Record operator-verbatim amendment (2026-06-12) in campaign doc and insert B.0 referencing ADR-0.0.70 ahead of B.1
4. Run `uv run mkdocs build --strict` — must exit 0

## Verification

```
uv run gz validate --documents
uv run gz lint
uv run mkdocs build --strict
rg -n "Buetow" docs/governance/harness-engineering-appraisal.md
rg -n "B.0 ADR-0.0.70" docs/governance/build-to-1.0-campaign-2026-06-10.md
```

## Notes

- SUPPORT REQs only (no `@covers` tests by design — ADR-0.0.59 proof channels apply)
- Proof: `artifact_edited` ledger events + `gz validate --documents` exit 0 + `mkdocs build --strict` exit 0
