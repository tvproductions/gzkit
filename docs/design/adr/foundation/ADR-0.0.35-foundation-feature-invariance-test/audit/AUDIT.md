# AUDIT — ADR-0.0.35-foundation-feature-invariance-test

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.0.35-foundation-feature-invariance-test |
| ADR Title | Foundation/Feature Invariance Test |
| Kind / Lane | foundation / lite |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.35-foundation-feature-invariance-test |
| Audit Date | 2026-05-17 |
| Auditor(s) | Jeffry Babb (operator) + Opus 4.7 (driver) |
| Persona Dispatch | `spec-reviewer`, `quality-reviewer`, `narrator` (parallel) |
| Layer 2 trust | Ledger proof verified — `gz adr audit-check` returned `passed: true` with all 4 OBPIs `attested_completed`; staleness ≤ 1 day |

## Feature Demonstration (Step 3 — MANDATORY)

**Before ADR-0.0.35 landed**, an adopter facing a substrate-vs-port edge case
had no mechanical recourse. *"Is the JSONL ledger backend foundation, or just
the current plug?"* devolved into authorial taste, and the resulting kind
classification couldn't be audited — the doctrine lived in tribal memory,
not in any surface the validator could read. A foundation ADR could ship
with no articulated reason it was foundation, and the next adopter inherited
the ambiguity.

### Capability 1 — Mechanical kind classification (the validator)

```bash
$ uv run gz validate --kind-invariance
Validated: kind_invariance

✓ All validations passed (1 scopes).
```

Every one of the 38 `kind: foundation`-frontmattered ADRs now carries a
load-bearing `## Why foundation tier?` section. A missing section is
fail-closed at CI time (the validator runs inside the default
`uv run gz check` pipeline), not caught in review. The validator's authored
scope is documented in Shortfall #1.

### Capability 2 — Scaffolder routes the convention

```bash
$ uv run gz plan create audit-probe-demo-only --kind foundation --semver 0.0.999 --lane lite --dry-run
Dry run: no files will be written.
  Would create ADR:
C:\Users\Jeff\source\repos\va\gzkit\docs\design\adr\foundation\ADR-0.0.999-audit-probe-demo-only\ADR-0.0.999-audit-probe-demo-only.md
  Would append ledger event: adr_created (ADR-0.0.999-audit-probe-demo-only)
```

The `gz plan create --kind foundation` invocation lands ADRs under
`docs/design/adr/foundation/` with the `## Why foundation tier?` section
pre-seated in the scaffolded template. Operators following the path of
least resistance produce validator-compliant ADRs by default.

### Capability 3 — Skill prompts carry the verbatim test across all surfaces

```bash
$ uv run -m unittest tests.governance.test_foundation_invariance_skill_enrichment -v
... (suite covers 6 REQs × 4 skills × byte-parity across mirrors) ...
Ran 30 tests in 0.004s

OK
```

The 4 kind-deciding skills (`gz-plan`, `gz-design`, `gz-adr-create`,
`gz-adr-promote`) carry the verbatim invariance test across all 5 mirrored
surfaces: `.gzkit/skills/`, `src/gzkit/skills/` (wheel-shipped),
`.claude/skills/`, `.agents/skills/`, `.github/skills/`. Independent probe:

```text
Skill mirrors carrying the verbatim invariance test
(4 skills × 5 surfaces = expected 20):
20
```

Whichever agent surface the operator drives, the same one-line test prompts
the same classification decision.

### Capability 4 — Single canonical reference for the doctrine

```text
concept page: docs/user/concepts/foundation-feature-invariance-test.md
bytes=7414 lines=131

Anchor content present (Select-String confirms):
  L14: > **"Foundation = without it, we wouldn't be doing the project."**
  L31: ## The hexagonal-ports lens
  L70: **Feature — JSONL→SQLite ledger backend:**
  L82: ### ADR-0.0.33 and ADR-0.0.34 as paired foundations
  L114: ## The anti-pattern
```

The concept page holds the verbatim test, the hexagonal-ports lens
(*ports = invariance, plugs = features*), both worked examples
(JSONL→SQLite substrate; ADR-0.0.33/0.0.34 paired foundations), and the
named anti-pattern (*"foundation because it feels foundational"*). One URL
to cite in every future kind dispute.

### Value Summary

The structural defense this ADR earns is the shift from honor-system
convention to fail-closed validator. Before: *"please articulate why this
is foundation"* was a review-time ask that drifted. After:
`gz validate --kind-invariance` runs in the default `gz check` pipeline,
so a foundation ADR cannot land without answering the test in the ADR's
own body. The doctrine is no longer something an adopter has to remember
— it is something the toolchain refuses to forget.

---

## Execution Log

| Check | Command | Result | Notes |
|-------|---------|--------|-------|
| Ledger proof complete | `uv run gz adr audit-check ADR-0.0.35 --json` | ✓ | `passed: true`; 4/4 OBPIs `attested_completed`; 24/32 REQs covered; 8 advisory uncovered (concept-page semantics, no test surface). Proof: `audit/proofs/audit-check.json` |
| Lifecycle pre-audit | `uv run gz adr status ADR-0.0.35 --json` | ✓ | `lifecycle_status: Completed`; gates 1, 2, 5 pass; 3, 4 n/a (lite). Proof: `audit/proofs/adr-status.json` |
| Validator runs clean | `uv run gz validate --kind-invariance` | ✓ | `All validations passed (1 scopes).` Proof: `audit/proofs/validate-kind-invariance.txt` |
| Scaffolder routes `--kind foundation` | `uv run gz plan create audit-probe-demo-only --kind foundation --semver 0.0.999 --lane lite --dry-run` | ✓ | Dry-run reports `Would create ADR` + `Would append ledger event`. Proof: `audit/proofs/plan-create-dry-run-real.txt` |
| Concept page anchor probe | `Select-String` on `docs/user/concepts/foundation-feature-invariance-test.md` | ✓ | 7414 bytes / 131 lines; verbatim test at L14, lens at L31, paired-foundations example at L82, anti-pattern at L114. |
| Skill-surface byte parity | content probe on 4 skills × 5 surfaces | ✓ | 20/20 surfaces hold the verbatim invariance test |
| Scoped tests green | `uv run -m unittest tests.governance.test_kind_invariance tests.governance.test_foundation_invariance_skill_enrichment tests.governance.test_kind_invariance_docs` | ✓ | 45 tests OK in 0.049s. Proof: `audit/proofs/scoped-unittest.txt` |
| Foundation-ADR section coverage | filesystem probe on 48 foundation ADR files | ⚠ | 38/48 carry `## Why foundation tier?`; 10 legacy ADRs (ADR-0.0.1 through ADR-0.0.15) lack `kind:` frontmatter and are invisible to the validator. See Shortfall #1. |
| Pre-validation lifecycle report | `uv run gz adr report ADR-0.0.35` | ✓ | `Completed` (will assert `Validated` after receipt emit). Proof: `audit/proofs/adr-report-pre-validation.txt` |

---

## Persona Review Findings

### `spec-reviewer` — independent REQ tracing

Sampled load-bearing REQs across all 4 OBPIs against the test surface;
specifically interrogated cosmetic-`@covers`-backfill anti-pattern (GHI
#272/#309).

- **OBPI-04 REQ-02/03/04 (validator semantics)** — `test_kind_invariance.py:127-247`
  asserts `errors == []` / `len(errors) > 0` against real
  `audit_kind_invariance` calls on tmpdir fixtures. Cannot pass for the
  wrong reason. Three placeholder-body failure modes (`STRICT_PLACEHOLDERS`,
  `_[Author: ...]_`, empty) walked individually.
- **OBPI-04 REQ-07 anti-pin guard** — `test_kind_invariance_docs.py:46-66`
  mechanically forbids four pinnable validator strings. Correct guard.
- **OBPI-02 REQ-01/02/03** — `assertIn(constant_string, file_content)` is
  the **correct** assertion shape here because the REQ wording says
  *"verbatim"* — string presence IS the REQ semantic, not a cosmetic shape
  pin.
- **OBPI-03 REQ-01/02/04** — `tests/commands/test_plan.py:513-583`
  asserts both heading byte-identicality AND both prompt phrases present.

> `VERDICT: NON-BLOCKING FINDINGS` — Validator enumeration predicate
> (`kind: foundation` frontmatter) under-covers vs ADR-0.0.35 Negative
> Consequence #5 prose ("every existing foundation ADR"); 10 legacy ADRs
> invisible to first run. Route to GHI for frontmatter backfill or
> enumeration-widening; does not block ADR-0.0.35 Validated.

### `quality-reviewer` — structural coherence

- **Single capability.** doctrine ↔ concept page ↔ exact heading pin ↔
  validator constant `_SECTION_HEADING` align byte-for-byte across all
  surfaces. One coherent capability.
- **Hexagonal-ports fidelity.** `audit_kind_invariance` is the **port**;
  the glob+heading-scan+placeholder-regex is the **plug**. The ADR's own
  doctrine is honored.
- **Scaffolder ↔ validator loop.** Scaffolded section + `_is_placeholder_body`
  rejection of "paste"/"one-sentence" tokens (which match scaffold prompts)
  → scaffolded-but-unfilled ADRs fail; scaffolded-and-filled pass. Loop
  closed.
- **Self-applying.** ADR-0.0.35 main file lines 17-21 carry the section
  non-placeholder; frontmatter line 4 declares `kind: foundation`. Passes
  its own validator.
- **Code quality.** `kind_invariance.py` 134 lines, single responsibility,
  all functions ≤25 lines, pure stdlib, encoding=utf-8, pathlib throughout.

> `VERDICT: NON-BLOCKING WEAKNESSES` — Validator scope (frontmatter-kind)
> narrower than ADR scope (filesystem `/foundation/`); 10 legacy
> frontmatter-less ADRs invisible to `gz validate --kind-invariance`,
> silently contradicting Negative Consequence #5's promise.

### `narrator` — value framing

Composed the Feature Demonstration section above (Step 3 deliverable).
Driver substituted real captured outputs for two synthesized lines
(narrator drafted `Ran 2 tests in 0.18s` for Capability 3 and a fabricated
`gz validate --documents --surfaces` block for Capability 4; replaced with
the actually-observed 30-test run and the Select-String anchor probe).

---

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | ✓ All 4 OBPIs `attested_completed`; ledger proof verified |
| Data Integrity | ✓ 20/20 byte-parity across mirrored skill surfaces |
| Coverage | ✓ 24/32 REQs covered; 8 advisory uncovered (concept-page authoring, no test surface by design) |
| Documentation Alignment | ⚠ See Shortfall #1 — validator scope ≠ Negative Consequence #5 prose |
| Self-Application | ✓ ADR-0.0.35 passes its own validator |
| Hexagonal-ports lens fidelity | ✓ Port (`audit_kind_invariance`) / plug (regex+glob) split honored |
| Tests | ✓ 45 scoped tests pass |

---

## Evidence Index

- `audit/AUDIT_PLAN.md` — plan
- `audit/proofs/audit-check.json` — ledger proof roll-up
- `audit/proofs/adr-status.json` — pre-audit lifecycle snapshot
- `audit/proofs/adr-report-pre-validation.txt` — `gz adr report` (Completed)
- `audit/proofs/validate-kind-invariance.txt` — validator clean run
- `audit/proofs/plan-create-dry-run-real.txt` — scaffolder demonstration
- `audit/proofs/scoped-unittest.txt` — 45-test scoped suite
- `audit/proofs/kind-invariance.txt` — duplicate validator capture (initial)
- `audit/proofs/plan-create-dry-run.txt` — duplicate scaffolder capture (initial)

---

## Shortfalls

### Shortfall #1 — Validator scope ≠ ADR Negative Consequence #5 prose (NON-BLOCKING)

**Description.** ADR-0.0.35's Decision §6 and Negative Consequence #5
promise that `gz validate --kind-invariance` *"reports drift on every
existing foundation ADR on first run, which produces the work list for the
backfill sweep mechanically rather than requiring up-front enumeration."*
Shipped behavior does not match: the validator filters by
`frontmatter.get("kind") != "foundation"`
(`src/gzkit/governance/trust_audits/kind_invariance.py:72-73`), and 10
legacy ADRs under `docs/design/adr/foundation/` lack `kind:` frontmatter
entirely (they predate ADR-0.0.17, which made `kind:` mechanical). Those 10
ADRs are silently skipped — the promised drift report shows zero where the
prose says it would show 10.

**Affected ADRs (10):** ADR-0.0.1, ADR-0.0.2, ADR-0.0.7, ADR-0.0.9,
ADR-0.0.10, ADR-0.0.11, ADR-0.0.12, ADR-0.0.13, ADR-0.0.14, ADR-0.0.15.

**Severity:** non-blocking. The validator does what its OBPI-04 brief
contract authored (`kind: foundation` frontmatter → section presence).
The defect is between ADR-0.0.35's NC#5 prose and the validator-scope as
authored — not within the OBPI-04 implementation. Both spec-reviewer and
quality-reviewer converged on this routing.

**Two clean remediation paths (operator to choose post-audit, via GHI):**

1. **Backfill `kind: foundation` frontmatter on the 10 legacy ADRs.** Aligns
   with ADR-0.0.17's mechanical taxonomy mandate. Validator then surfaces
   the 10 ADRs as missing-section, producing the work list NC#5 promised.
   Higher-fidelity fix.
2. **Widen the validator** to use filesystem location
   (`docs/design/adr/foundation/**`) as the foundation predicate, with
   frontmatter-coherence as a separate audit. Faster but loses the
   single-source-of-truth posture frontmatter gives.

**Routing:** GHI #483 filed post-audit per AGENTS.md Prime Directive 6
("every defect must be trackable"). Open with blocker comment: operator
must choose Option A (frontmatter backfill, 10 files → OBPI ceremony) or
Option B (validator widening, 1 file → direct fix) before the GHI routes
to a destination artifact.

### Shortfall #2 — None (no other blocking or non-blocking findings)

---

## Attestation

I, Jeffry Babb, attest that ADR-0.0.35-foundation-feature-invariance-test
is implemented as intended, the four delivered capabilities are
demonstrably working, evidence is reproducible from the proofs index above,
and the one non-blocking shortfall is routed to a follow-up GHI rather than
silenced.

The ADR moves from Lifecycle `Completed` → `Validated`.

Signed: _Jeffry Babb, 2026-05-17_
Driver: Opus 4.7 (claude-opus-4-7) under `/gz-adr-audit 0.0.35`
Persona dispatch: `spec-reviewer`, `quality-reviewer`, `narrator` (all returned non-blocking verdicts)
