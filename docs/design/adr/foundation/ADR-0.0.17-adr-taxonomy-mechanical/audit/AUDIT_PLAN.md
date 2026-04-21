# AUDIT_PLAN — ADR-0.0.17 (ADR Taxonomy — Mechanical)

## Scope

Verify the five mechanical enforcement surfaces declared in the ADR:

1. `kind:` frontmatter field on every non-pool ADR (schema-enforced enum)
2. `gz plan create --kind {pool,foundation,feature}` scaffolds correct shape
3. `gz adr promote --kind {foundation,feature}` expresses promotion intent
4. `gz validate --taxonomy` enforces kind/semver binding
5. Backfill + round-trip: existing ADRs accept the enforcement without mutation defects
6. AGENTS.md corrected to document kind/lane as orthogonal (OBPI-06 docs leg)

## Checks

| # | Claim | Verification |
|---|---|---|
| C1 | All 6 OBPIs complete | `gz adr audit-check ADR-0.0.17` — `complete_obpis == checked_obpis`; `findings == []` |
| C2 | `kind:` frontmatter landed on self | `head` of ADR-0.0.17 shows `kind: foundation` |
| C3 | `gz plan create --kind` works | `--help` lists `{pool,foundation,feature}` as required |
| C4 | `gz adr promote --kind` works | `--help` lists `{pool,foundation,feature}` with pool rejected |
| C5 | `gz validate --taxonomy` clean on canon | exits 0; all validations passed |
| C6 | AGENTS.md § Kinds exists | grep `### Kinds (pool, foundation, feature)` in AGENTS.md |
| C7 | Unit tests pass | ARB `arb-step-unittest-*` exit 0 |
| C8 | Lint clean | ARB `arb-ruff-*` exit 0 |
| C9 | Typecheck clean | ARB `arb-step-typecheck-*` exit 0 |
| C10 | Docs strict | ARB `arb-step-mkdocs-*` exit 0 |
| C11 | Gates 1–4 pass; Gate 5 attested | `gz gates --adr`; ledger `attested` event by Jeffry Babb |

## Risk Focus

- **REQ coverage gap (advisory):** OBPI-06 is Lite-lane docs-only; `gz adr audit-check` fails on 7 advisory-severity `@covers` misses, all traceable to the brief's explicit "N/A for TDD" declaration. Tracked under GHI #268.
- **Value demonstration:** ADR-0.0.17 is foundation-kind; Step 3 shows the taxonomy enforcement running end-to-end on the canonical tree, not just test-passing.
