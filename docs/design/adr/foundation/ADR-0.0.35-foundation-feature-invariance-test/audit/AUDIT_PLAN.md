# AUDIT PLAN — ADR-0.0.35-foundation-feature-invariance-test

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.35-foundation-feature-invariance-test |
| ADR Title | Foundation/Feature Invariance Test |
| SemVer | 0.0.35 |
| Kind / Lane | foundation / lite |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.35-foundation-feature-invariance-test |
| Audit Date | 2026-05-17 |
| Auditor(s) | g0 (operator) + Opus 4.7 (driver) + spec-reviewer + quality-reviewer + narrator |

## Purpose

Confirm ADR-0.0.35 implementation is complete and validated by exercising the
four delivered capabilities (concept page, skill enrichment, scaffolder
convention, validator) with reproducible CLI evidence. Attestation gate:
foundation-kind ⇒ brief-level Gate 5 already attested per OBPI; this audit
moves the ADR's lifecycle from `Completed` → `Validated`.

**Audit trigger:** Post-implementation audit ceremony invoked via
`/gz-adr-audit 0.0.35`. All four OBPIs are `attested_completed` in the ledger;
the audit asks the harder question: does the ADR's *integrated* claim hold?

## Scope & Inputs

**Primary contract surfaces this ADR introduces or modifies:**

- New validator scope: `uv run gz validate --kind-invariance`
  (wired into default `uv run gz check`)
- New CLI flag class: `uv run gz plan create --kind {pool,foundation,feature}`
  (scaffolder pre-populates `## Why foundation tier?` for `--kind foundation`)
- Skill prompt enrichment: `gz-plan`, `gz-design`, `gz-adr-create`,
  `gz-adr-promote` — verbatim invariance test in all 5 mirrored surfaces
- New canonical doctrine page: `docs/user/concepts/foundation-feature-invariance-test.md`
- New foundation-ADR convention: load-bearing `## Why foundation tier?` section

**Ledger / system-of-record:**

- `.gzkit/ledger.jsonl` — attestation events for OBPI-01/02/03/04
- `uv run gz adr audit-check ADR-0.0.35 --json` — coverage and attestation roll-up
- `uv run gz adr status ADR-0.0.35 --json` — lifecycle + per-OBPI evidence

## Planned Checks

| Check | Command | Expected Signal | Status |
|-------|---------|-----------------|--------|
| Ledger proof complete | `uv run gz adr audit-check ADR-0.0.35 --json` | `passed: true`, all 4 OBPIs `attested_completed` | ✓ |
| Validator runs clean | `uv run gz validate --kind-invariance` | `✓ All validations passed (1 scopes).` | ✓ |
| Scaffolder honors `--kind foundation` | `uv run gz plan create audit-probe-demo-only --kind foundation --semver 0.0.999 --lane lite --dry-run` | Reports `Would create ADR` + `Would append ledger event: adr_created` | ✓ |
| Concept page present and canonical | filesystem probe + content anchor check on `docs/user/concepts/foundation-feature-invariance-test.md` | File exists; carries verbatim test, hexagonal-ports lens, both worked examples, anti-pattern | ✓ |
| Skill prompts byte-parity across surfaces | content probe on 4 skills × 5 surfaces | 20/20 surfaces carry verbatim `"Foundation = without it, we wouldn't be doing the project"` | ✓ |
| Scoped tests green | `uv run -m unittest tests.governance.test_kind_invariance tests.governance.test_foundation_invariance_skill_enrichment tests.governance.test_kind_invariance_docs` | 45 tests OK | ✓ |
| Foundation ADRs carry the section | filesystem probe on `docs/design/adr/foundation/ADR-*/ADR-*.md` | All `kind: foundation`-frontmattered ADRs hold `## Why foundation tier?` | ⚠ (38/38 frontmattered pass; 10 legacy ADRs without `kind:` frontmatter invisible — see Shortfall #1) |

## Risk Focus

1. **Validator-scope vs ADR-scope divergence** — the validator enumerates by
   `frontmatter.get("kind") == "foundation"`; ADR-0.0.35 Negative
   Consequence #5 promises *"reports drift on every existing foundation ADR
   on first run"*. 10 legacy ADRs under `docs/design/adr/foundation/` lack
   `kind:` frontmatter and are silently skipped. This is the load-bearing
   risk the audit must surface explicitly.

2. **Self-application** — ADR-0.0.35 is itself foundation-kind. Must pass
   its own validator and its own `## Why foundation tier?` section must
   answer the invariance test substantively.

3. **Mirror parity** — 4 skills × 5 surfaces = 20 byte-identical copies of
   a verbatim doctrine string. Any drift would silently disagree between
   `.claude/` (what Claude reads) and `.gzkit/` (what operators edit).

## Persona Dispatch (per skill mandate)

- `spec-reviewer` — independent REQ tracing against test surface (anti
  cosmetic-`@covers`-backfill check)
- `quality-reviewer` — ADR-level structural coherence; port/plug fidelity;
  scaffolder ↔ validator loop closure
- `narrator` — operator-value framing for Step 3 Feature Demonstration

## Acceptance Criteria

- All planned checks ✓ or ⚠ with documented non-blocking rationale
- Feature Demonstration section composed and grounded in real captured output
- All persona reviews returned non-blocking verdicts
- Operator's verbal `accept audit` / `verify audit` received
- `uv run gz adr emit-receipt ADR-0.0.35 --event validated …` recorded
- `uv run gz adr report ADR-0.0.35` Lifecycle column shows `Validated`
