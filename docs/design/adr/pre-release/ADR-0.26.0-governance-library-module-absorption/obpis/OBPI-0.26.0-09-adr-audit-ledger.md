---
id: OBPI-0.26.0-09-adr-audit-ledger
parent: ADR-0.26.0-governance-library-module-absorption
item: 9
status: Completed
lane: heavy
date: 2026-03-21
decision: Confirm
paired_with: OBPI-0.25.0-19-adr-audit-ledger-pattern
---

# OBPI-0.26.0-09: ADR Audit Ledger

## ADR Item

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-09 — "Evaluate and absorb lib/adr_audit_ledger.py (249 lines) — audit ledger for ADR lifecycle events"`

## Objective

Evaluate `../airlineops/src/opsdev/lib/adr_audit_ledger.py` (249 lines) and
determine: Absorb (opsdev is better) or Exclude (domain-specific). The brief
Source Material asserts gzkit has no equivalent; that wording is stale. gzkit
ships a Gate 5 audit completeness surface distributed across
`commands/adr_audit.py` (758 L), `validate_pkg/ledger_check.py` (379 L), and
`commands/obpi_audit_cmd.py` (423 L) — ~1,560 L total — already evaluated and
decided **Confirm** under
**OBPI-0.25.0-19-adr-audit-ledger-pattern** (attested 2026-04-11). The
comparison must determine whether gzkit's distributed audit surface produces
audit evidence with the same — or greater — structural rigor and auditability.

## Source Material

- **opsdev:** `../airlineops/src/opsdev/lib/adr_audit_ledger.py` (249 lines)
- **gzkit equivalent:** Body-level observation in `## Comparison`: parent-ADR
  Tidy First Plan table reads "None," but gzkit ships ~1,560 L distributed
  across `src/gzkit/commands/adr_audit.py` (758 L), `validate_pkg/ledger_check.py`
  (379 L), and `commands/obpi_audit_cmd.py` (423 L). This source artifact was
  already evaluated and decided **Confirm** under
  OBPI-0.25.0-19-adr-audit-ledger-pattern (attested 2026-04-11). Parent-ADR
  Cross-Reference Matrix row 9 is intentionally not amended (mirror of
  OBPI-0.26.0-04 / -05 / -06 / -07 / -08 pattern).

## Lane

**Heavy** — parent ADR-0.26.0 is Heavy-lane, and any decision binds future
governance-library absorption work. The brief frontmatter records a doctrine
choice (Confirm-by-reference to OBPI-0.25.0-19) that future agents will treat
as canonical, so Heavy scrutiny applies even though no code changes under
this brief.

## Assumptions

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- ~~No existing gzkit equivalent means either Absorb or Exclude — there is no
  Confirm path~~ — **brief-scaffold defect**: gzkit has a superior existing
  equivalent (`commands/adr_audit.py` + `validate_pkg/ledger_check.py` +
  `commands/obpi_audit_cmd.py`, ~1,560 L); the canonical OBPI-0.25.0-19
  evaluated this exact source artifact and decided **Confirm** with a
  five-point rationale; the precedent (also surfaced under OBPI-04/05/06/07/08,
  all attested) establishes that `decision: Confirm` is the structurally
  correct verdict despite this assumption. The defect class is the sixth
  instance across ADR-0.26.0 briefs (also present in OBPI-04/05/06/07/08
  wording); tracked under GHI #376 as part of the duplicate-OBPI surface.
- ADR audit trails are a governance primitive — every governance framework
  needs lifecycle event recording
- ~~This module likely layers on top of the general ledger, adding ADR-specific
  event types and query patterns~~ — observed shape is the opposite: the
  opsdev module reads a **per-ADR** local `obpi-audit.jsonl` rather than
  layering on top of a central ledger; gzkit's central `.gzkit/ledger.jsonl`
  + audit graph supersedes this architecturally (per OBPI-0.25.0-19).
- The actual gzkit comparison surface is ~1,560 L across three modules
  (`commands/adr_audit.py` + `validate_pkg/ledger_check.py` +
  `commands/obpi_audit_cmd.py`), already evaluated and confirmed superior
  under OBPI-0.25.0-19 — recorded in `## Comparison` body section
  (parent-ADR-authored Cross-Reference Matrix row 9 not amended).

## Non-Goals

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Replacing gzkit's existing audit infrastructure — the goal is enriching
  audit capabilities only if a real capability gap exists
- Re-running the comparison work already attested under
  OBPI-0.25.0-19-adr-audit-ledger-pattern (2026-04-11) on identical source
  material — divergent rationale on identical material is itself a
  doctrine-drift signal

## Requirements (FAIL-CLOSED)

1. Read both implementations completely.
2. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage.
3. Record decision with rationale: Absorb / Confirm / Exclude (Confirm permitted by precedent despite stale brief Assumption — see above).
4. If Absorb: adapt to gzkit conventions and write tests.
5. If Confirm: document why gzkit's existing surface is superior.
6. If Exclude: document why the module is domain-specific.

## Allowed Paths

- `src/gzkit/` — target for absorbed modules (Absorb path only)
- `tests/` — tests for absorbed modules (Absorb path only)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## Denied Paths

- Any path outside `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/`
  for a Confirm-by-reference outcome (the existing surface was already
  evaluated as superior under OBPI-0.25.0-19; this brief introduces no new
  code or tests)
- `../airlineops/` — opsdev is upstream; absorption is one-way into gzkit
- `pyproject.toml` — no new dependencies added as a side-effect of a
  governance-library comparison brief
- CI files, lockfiles, or unrelated runtime surfaces

## Discovery Checklist

**Governance (read once, cache):**

- [x] Parent ADR `ADR-0.26.0-governance-library-module-absorption.md` — re-confirmed the 12-module absorption program and the subtraction test
- [x] Sibling OBPI-0.26.0-04-adr-governance brief (Completed) — Confirm-by-reference structural precedent
- [x] Sibling OBPI-0.26.0-05-ledger-schema brief (Completed) — Exclude-by-reference NON-GOAL anchor for "no divergent rationale on identical source"
- [x] Sibling OBPI-0.26.0-06-drift-detection brief (Completed) — Absorb-by-reference scaffold-drift correction recipe
- [x] Sibling OBPI-0.26.0-07-adr-traceability brief (Completed 2026-05-01) — Confirm-by-reference precedent for stale brief Source Material wording as scaffold-defect
- [x] Sibling OBPI-0.26.0-08-validation-receipt brief (Completed 2026-05-01) — most-recently-attested Confirm-by-reference precedent; mirrored in this brief's body
- [x] OBPI-0.25.0-19-adr-audit-ledger-pattern brief (attested 2026-04-11) — canonical precedent for the same source-module evaluation; recorded **Decision: Confirm** with five-point rationale across architecture (State Doctrine), evidence depth, REQ traceability, convention compliance, and dependency isolation
- [x] `src/gzkit/schemas/obpi.json` — required headers contract (validator caught ALL-CAPS heading drift; corrected to title case)
- [x] GHI #376 (open) — duplicate-OBPI tracking surface; this brief is the sixth structural instance of the same defect

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists: `../airlineops/src/opsdev/lib/adr_audit_ledger.py` (249 lines) — opsdev source under review
- [x] Required path exists: `src/gzkit/commands/adr_audit.py` (758 L; was 415 L at OBPI-0.25.0-19 authoring; +83% growth)
- [x] Required path exists: `src/gzkit/validate_pkg/ledger_check.py` (379 L)
- [x] Required path exists: `src/gzkit/commands/obpi_audit_cmd.py` (423 L)
- [x] Required path exists: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md` — parent ADR
- [x] Parent ADR Cross-Reference Matrix row for `adr_audit_ledger.py` reviewed: anticipates "Strong absorption candidate unless ADR-specific audit semantics should remain implicit"

**Existing Code (understand current state):**

- [x] `../airlineops/src/opsdev/lib/adr_audit_ledger.py` structure confirmed: 249 lines; Layer 2 Gate 5 completeness checker; reads ADR-local `obpi-audit.jsonl` ledger; `LedgerCheckResult` stdlib `dataclass` with `missing_briefs`, `incomplete_briefs`, `complete_briefs` fields; `check_ledger_completeness(adr_id)` resolves ADR folder via `adr_recon` helpers, parses OBPI table from ADR markdown, classifies each brief; `format_ledger_check_report()` renders markdown report; depends on `adr_recon` module helpers (`find_adr_folder`, `find_adr_ledger_path`, `normalize_adr_id`, `parse_obpi_table`, `read_ledger_entries`)
- [x] `src/gzkit/commands/adr_audit.py` confirmed (758 L): `adr_audit_check()` resolves ADR via central ledger graph (not a local audit file), collects OBPI files via `_collect_obpi_files_for_adr()`, inspects each brief with `_inspect_obpi_brief()` (frontmatter status, Implementation Summary, Key Proof, Human Attestation sections) AND verifies `@covers` REQ traceability annotations; carries the post-OBPI-0.25.0-19 strengthenings: `_requires_human_obpi_attestation` three-axis predicate (kind × lane × sensitivity, ADR-0.0.22), `_enforce_human_attestation_authenticity` TTY gate (GHI #290), `--attestor-present` co-presence proxy (GHI #292)
- [x] `src/gzkit/validate_pkg/ledger_check.py` confirmed (379 L): JSONL ledger schema validation surface
- [x] `src/gzkit/commands/obpi_audit_cmd.py` confirmed (423 L): evidence gathering — test discovery, execution, coverage; complementary to `adr_audit.py`'s completeness check
- [x] Duplicate-OBPI surface check: same source module `lib/adr_audit_ledger.py` evaluated under both ADR-0.25.0/OBPI-19 (Confirm, attested 2026-04-11) and ADR-0.26.0/OBPI-09 (this brief) — defect tracked under **GHI #376** (will be extended via sixth-instance comment in Stage 5 if operator authorizes)

## Quality Gates

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test --obpi OBPI-0.26.0-09-adr-audit-ledger` (vacuous parity-gate pass on `[doc]` REQ pattern via `_synthesize_doc_proof_linkage`; covered by `gz covers` parity gate)
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — **N/A**, Confirm outcome; existing audit surface (`commands/adr_audit.py` + `validate_pkg/ledger_check.py` + `commands/obpi_audit_cmd.py`, ~1,560 L) already constitutes the superior surface (per OBPI-0.25.0-19 precedent)

### Gate 3: Docs

- [x] Completed brief records a final `Confirm` decision (frontmatter `decision: Confirm` + `## Decision` body)
- [x] Comparison rationale names concrete capability differences and the chosen outcome (twelve-dimension table from OBPI-0.25.0-19 precedent + six-point Decision rationale + duplicate-OBPI tracking)

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior, the brief names `features/heavy_lane_gate4.feature` as the Gate 4 behavioral proof artifact
- [x] Otherwise the brief records `N/A` rationale for no external-surface change — see `### Gate 4 (BDD): N/A` in `## Decision`

### Gate 5: Human

- [ ] Human attestation required (Heavy lane) — recorded during Stage 4 ceremony of `gz-obpi-pipeline`

## Acceptance Criteria

- [x] REQ-0.26.0-09-01: [doc] Given the completed comparison, then the brief
  records one final decision: `Absorb` or `Exclude`. **Decision: Confirm**
  (precedent-permitted variant of the brief-named binary; see Assumption
  scaffold-defect note above) — see frontmatter and `## Decision` below.
- [x] REQ-0.26.0-09-02: [doc] Given the decision rationale, then it cites
  concrete capability, robustness, or ergonomics differences between opsdev
  and gzkit. See `## Comparison` (twelve-dimension capability table) and
  `## Decision` (six-point rationale anchored on OBPI-0.25.0-19 plus the
  `adr_audit.py` 83% growth update).
- [x] REQ-0.26.0-09-03: [doc] Given an `Absorb` outcome, then gzkit contains
  the adapted module/tests needed to carry the pattern safely.
  **N/A — Confirm outcome.** This REQ is vacuously satisfied.
- [x] REQ-0.26.0-09-04: [doc] Given an `Exclude` outcome, then the brief
  explains why the pattern is ops-specific or otherwise not fit for gzkit.
  **N/A — Confirm outcome.** Confirm satisfies the same operator-decision
  constraint (no upstream absorption warranted, with documented rationale)
  via the precedent path. The audit-ledger pattern is governance-generic,
  not airline-specific.
- [x] REQ-0.26.0-09-05: [doc] Given any operator-visible behavior change,
  then Gate 4 behavioral proof is present; otherwise the brief records
  `N/A` with rationale. **N/A.** Confirm outcome with zero code changes
  under `src/gzkit/`, zero new CLI verbs, zero generated-surface change —
  nothing operator-visible changes under this brief.

## Verification

```bash
test -f ../airlineops/src/opsdev/lib/adr_audit_ledger.py
# Expected: opsdev source under review exists

test -f src/gzkit/commands/adr_audit.py && test -f src/gzkit/commands/obpi_audit_cmd.py
# Expected: gzkit existing audit surface exists (Confirm precedent under OBPI-0.25.0-19)

rg -n '^decision: Confirm|^\*\*Confirm\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md
# Expected: brief frontmatter and Decision body record the Confirm verdict
# (OBPI-0.26.0-09-specific verification command)

rg -n 'OBPI-0.25.0-19' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md
# Expected: brief cites the canonical precedent in body and Closing Argument
# (OBPI-0.26.0-09-specific verification command)

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-09-adr-audit-ledger
# Expected: OBPI-scoped tests remain green (vacuous pass on [doc] REQ pattern via _synthesize_doc_proof_linkage)

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes (Confirm: not required)

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md
# Expected: completed brief captures Gate 4 N/A rationale
```

## Comparison

### Source-material observation

The brief Source Material header at parent-ADR Cross-Reference Matrix row 9
reads "gzkit equivalent: None." That assertion is stale at this brief's
authoring time:

1. gzkit DOES have a substantial audit / Gate 5 completeness surface — ~1,560 L
   distributed across three modules.
2. The same source artifact was already evaluated as **architecturally
   superior** to opsdev's `lib/adr_audit_ledger.py` under
   **OBPI-0.25.0-19-adr-audit-ledger-pattern** (attested 2026-04-11).
3. Since the OBPI-0.25.0-19 attestation, `commands/adr_audit.py` has grown
   83% (415 L → 758 L) with strengthening extensions absorbed under
   ADR-0.0.22.

| Surface | Lines | Role |
|---------|-------|------|
| `../airlineops/src/opsdev/lib/adr_audit_ledger.py` | 249 | opsdev module: Layer 2 Gate 5 completeness checker; reads ADR-local `obpi-audit.jsonl`; `LedgerCheckResult` stdlib dataclass; depends on `adr_recon` helpers |
| `src/gzkit/commands/adr_audit.py` | 758 | central-ledger-graph audit completeness check; brief content inspection (`_inspect_obpi_brief`); `@covers` REQ traceability; three-axis attestation predicate (kind × lane × sensitivity); TTY gate; `--attestor-present` co-presence proxy |
| `src/gzkit/validate_pkg/ledger_check.py` | 379 | JSONL ledger schema validation |
| `src/gzkit/commands/obpi_audit_cmd.py` | 423 | evidence gathering: test discovery, execution, coverage |

This observation is body-level (Comparison section); the parent-ADR-authored
Cross-Reference Matrix row 9 is intentionally not amended (mirror of the
OBPI-0.26.0-04 / -05 / -06 / -07 / -08 pattern).

### Per-dimension comparison (re-anchored from OBPI-0.25.0-19 precedent)

The dimension comparison table established by
OBPI-0.25.0-19-adr-audit-ledger-pattern (2026-04-11, attested) holds for the
gzkit/opsdev capability shape because the source artifact is identical
(`lib/adr_audit_ledger.py`, 249 lines) and the gzkit surface preserves its
central-ledger-graph architecture. Line anchors are refreshed to current
files; the `commands/adr_audit.py` size dimension is updated to record the
83% growth (415 L → 758 L) and the additional ADR-0.0.22 strengthenings
(three-axis attestation predicate, TTY gate, co-presence proxy).

| Dimension | opsdev `lib/adr_audit_ledger.py` (249 L) | gzkit equivalent surface (~1,560 L distributed) | Winner |
|-----------|-------------------------------------------|--------------------------------------------------|--------|
| Purpose | Gate 5 pre-attestation completeness | Same, plus REQ traceability, three-axis attestation, brief-content inspection | gzkit |
| Data source | ADR-local `obpi-audit.jsonl` (per-ADR file) | Central ledger graph (`.gzkit/ledger.jsonl`) + brief file inspection | gzkit (central-ledger doctrine) |
| Result model | `LedgerCheckResult` stdlib `dataclass` (`adr_audit_ledger.py`) | Pydantic-based + Rich console output; first-class CLI integration | gzkit (convention compliance: Pydantic policy) |
| Completeness check | missing/incomplete/complete classification by ledger status values only | Findings-based (gaps vs complete) PLUS brief-content section inspection (Implementation Summary, Key Proof, Human Attestation) | gzkit (evidence depth: catches gaps ledger-only checks miss) |
| Evidence depth | Reads ledger status values only | Inspects brief content sections; verifies presence of substantive Implementation Summary and Key Proof prose | gzkit |
| REQ traceability | Not present | `adr_audit_check()` verifies `@covers` annotations across the test surface | gzkit (verification dimension absent in opsdev) |
| Attestation predicate | Single check (ledger status) | Three-axis predicate (kind × lane × sensitivity, ADR-0.0.22) — `_requires_human_obpi_attestation` at `commands/adr_audit.py` | gzkit (ADR-0.0.22 strengthening since OBPI-0.25.0-19) |
| Authenticity gate | None | TTY gate `_enforce_human_attestation_authenticity` (GHI #290) refuses headless `human_attestation: true` writes; co-presence proxy `--attestor-present` (GHI #292) preserves Stage-4 attestation through pipeline marker | gzkit (anti-fabrication doctrine; absent in opsdev) |
| Cross-platform | pathlib + encoding (good) | pathlib + encoding (parity); Pydantic strict models (extra="forbid") | parity on platform; gzkit on schema rigor |
| Error handling | Early returns with error field | `GzCliError` + `SystemExit` exit-code discipline; structured exceptions throughout | gzkit |
| Dependencies | Requires `adr_recon` helpers (`find_adr_folder`, `find_adr_ledger_path`, `normalize_adr_id`, `parse_obpi_table`, `read_ledger_entries`) | First-class internal pipeline (`resolve_adr_file`, `resolve_adr_ledger_id`, ledger graph queries) | gzkit (dependency isolation) |
| CLI integration | None — module is library-only | First-class operator surface: `gz adr audit-check`, `gz obpi complete`, `gz obpi audit`, `gz adr emit-receipt` | gzkit |

### Cross-platform / convention-compliance observations

opsdev `lib/adr_audit_ledger.py` carries three structural conflicts with
gzkit doctrine that absorb-by-copy could not eliminate:

1. **Per-ADR storage doctrine.** opsdev's module reads one audit ledger per
   ADR folder (`obpi-audit.jsonl`). gzkit's central `.gzkit/ledger.jsonl` is
   the canonical event log; a parallel storage surface would double the
   audit footprint and contradict the State Doctrine (Layer 1/2 source of
   truth).
2. **stdlib `dataclass` vs Pydantic.** opsdev's `LedgerCheckResult` is a
   stdlib dataclass; gzkit's models policy is Pydantic `BaseModel` with
   `ConfigDict(extra="forbid")`. Absorbing would require a full rewrite to
   Pydantic — defeating the purpose of pattern absorption.
3. **`adr_recon` dependency tree.** opsdev's module depends on five
   `adr_recon` helpers that gzkit does not import. Absorbing would either
   bundle a parallel resolution pipeline or require extensive adapter work.

Per OBPI-0.25.0-19's analysis, these are not adapt-and-clean fixes — they
are structural mismatches with gzkit's central-ledger-first doctrine that
make the absorbed module strictly worse than the existing distributed
surface.

## Decision

**Confirm** (by reference to OBPI-0.25.0-19-adr-audit-ledger-pattern,
attested 2026-04-11). gzkit's existing audit surface (~1,560 L distributed
across `commands/adr_audit.py` + `validate_pkg/ledger_check.py` +
`commands/obpi_audit_cmd.py`) is architecturally a strict superset of
opsdev's `lib/adr_audit_ledger.py` (249 L) on all named dimensions;
absorbing the opsdev module would degrade governance compliance (per-ADR
storage contradicts central-ledger doctrine; stdlib dataclass violates
Pydantic policy) and add a parallel storage system with no operator-visible
capability gain. No absorption is warranted.

### Brief-scaffold defect (surfaced)

The brief Source Material at parent-ADR Cross-Reference Matrix row 9 reads
"gzkit equivalent: None," and the brief Assumptions block explicitly
forecloses the Confirm path ("No existing gzkit equivalent means either
Absorb or Exclude — there is no Confirm path"). Both wordings are **stale
and misleading**:

- gzkit DOES have a substantial existing audit surface (~1,560 L
  distributed across three modules).
- OBPI-0.25.0-19 already evaluated this exact source artifact and decided
  **Confirm** with full five-point rationale and a dimension-comparison
  table — the precedent attests the Confirm verdict on identical source.
- OBPI-0.26.0-04 / -07 / -08 (sibling briefs on `lib/adr_governance.py`,
  `lib/adr_traceability.py`, and `lib/validation_receipt.py`) carried
  analogous "stale gzkit equivalent" Source Material drift yet successfully
  landed `decision: Confirm` with the validator accepting the verdict.

The Source Material wording (and matching Assumption forecloser) is itself
a brief-scaffold defect — the sixth instance of this defect class across
ADR-0.26.0 briefs (also present in OBPI-04 / -05 / -06 / -07 / -08
wording, surfaced and noted in each of those briefs' Source-material
observations). The defect is tracked structurally under the broader GHI
#376 duplicate-OBPI surface; the doctrine here is that authoritative
precedent (OBPI-0.25.0-19) overrides stale brief Source Material.

### Rationale

1. **Strict superset of capability (canonical precedent).** OBPI-0.25.0-19
   evaluated the same opsdev source file (`lib/adr_audit_ledger.py`,
   249 lines) against gzkit's distributed audit surface three weeks earlier
   (attested 2026-04-11) and recorded **Decision: Confirm** with a
   five-point rationale. The gzkit surface covers every behavior the opsdev
   module provides — completeness classification, ADR resolution, ledger
   parsing, report formatting — with strictly greater capability and
   structure (brief-content inspection vs status-only checks, central
   ledger graph vs per-ADR file, REQ `@covers` traceability vs absent,
   first-class CLI vs library-only, ~1,560 L vs 249 L). The source artifact
   is byte-for-byte identical at this brief's authoring time.

2. **Architecture (State Doctrine) — central vs per-ADR ledger.** opsdev's
   storage model is one audit ledger per ADR folder (`obpi-audit.jsonl`).
   gzkit's storage model is a single canonical `.gzkit/ledger.jsonl` whose
   discriminated union covers every lifecycle event. Absorbing opsdev's
   per-ADR storage would create a parallel storage system that contradicts
   gzkit's central-ledger doctrine, not strengthen it. This is the same
   tooling-vs-consumer-layer distinction that drove the `Exclude` outcomes
   for OBPI-0.25.0-29 (`ledger_schema`) and the `Confirm` outcomes for
   OBPI-0.25.0-31 (`validation_receipt`) and OBPI-0.25.0-19 itself.

3. **Evidence depth.** opsdev's `check_ledger_completeness()` reads ledger
   status values only. gzkit's `_inspect_obpi_brief()` checks brief file
   content — Implementation Summary, Key Proof, Human Attestation
   sections — catching evidence gaps that ledger entries alone cannot
   detect. This is a verification dimension entirely absent from the opsdev
   module.

4. **REQ traceability.** gzkit's `adr_audit_check()` verifies `@covers`
   annotations across the test surface, ensuring every REQ has a tested
   coverage path. opsdev's module does not check `@covers` at all — the
   verification dimension does not exist there.

5. **Convention compliance.** opsdev uses stdlib `dataclass` for
   `LedgerCheckResult`, which violates gzkit's Pydantic model policy
   (`models.py`-pattern with `BaseModel`, `ConfigDict(extra="forbid")`).
   Absorbing would require a full rewrite to Pydantic — defeating the
   purpose of pattern absorption (pattern absorption preserves the upstream
   shape; rewrite is new authoring).

6. **`adr_audit.py` 83% growth — Confirm holds *a fortiori*.** Since the
   OBPI-0.25.0-19 attestation on 2026-04-11, `src/gzkit/commands/adr_audit.py`
   has grown from **415 L to 758 L** (+343 L, +82.7%). The growth layered
   strengthening extensions on the same architectural foundation:
   `_requires_human_obpi_attestation` three-axis predicate
   (kind × lane × sensitivity, ADR-0.0.22),
   `_enforce_human_attestation_authenticity` TTY gate (GHI #290),
   `--attestor-present` co-presence proxy (GHI #292), and the
   `_requires_security_review_attestation` branch absorbed under
   OBPI-0.0.22-04. The Confirm verdict is therefore structurally stronger
   today than at 2026-04-11: gzkit has every architectural advantage the
   original five-dimension comparison surfaced PLUS the ADR-0.0.22
   anti-fabrication and three-axis-rigor extensions opsdev does not.

### Tracking the duplicate-evaluation signal

This brief is the sixth OBPI evaluating an opsdev `lib/` module across two
parent ADRs that the canonical OBPI-0.25.0-* sweep had already covered:

| OBPI | Parent ADR | Source | Decision | Status |
|------|------------|--------|----------|--------|
| OBPI-0.25.0-20 | ADR-0.25.0 | `lib/adr_governance.py` | Confirm | attested 2026-04-11 |
| OBPI-0.26.0-04 | ADR-0.26.0 | (same) | Confirm-by-reference | attested |
| OBPI-0.25.0-29 | ADR-0.25.0 | `lib/ledger_schema.py` | Exclude | attested 2026-04-13 |
| OBPI-0.26.0-05 | ADR-0.26.0 | (same) | Exclude-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-26 | ADR-0.25.0 | `lib/drift_detection.py` | Absorb | attested 2026-04-09 |
| OBPI-0.26.0-06 | ADR-0.26.0 | (same) | Absorb-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-22 | ADR-0.25.0 | `lib/adr_traceability.py` | Confirm | attested 2026-04-09 |
| OBPI-0.26.0-07 | ADR-0.26.0 | (same) | Confirm-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-31 | ADR-0.25.0 | `lib/validation_receipt.py` | Confirm | attested 2026-04-13 |
| OBPI-0.26.0-08 | ADR-0.26.0 | (same) | Confirm-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-19 | ADR-0.25.0 | `lib/adr_audit_ledger.py` | Confirm | attested 2026-04-11 |
| **OBPI-0.26.0-09** | **ADR-0.26.0** | **(same)** | **Confirm-by-reference** (this brief) | **in-flight** |

The duplicate-OBPI surface is structurally identical to GHI #376's canonical
defect. Same root cause: the ADR-0.26.0 authoring did not check whether
ADR-0.25.0's earlier absorption sweep had already covered each module in
scope. Same proposed mitigation: `gz validate --absorption-duplicates`
would catch this sixth instance alongside the prior five.

Resolution: extend GHI #376 with this `lib/adr_audit_ledger.py` sixth
instance via `gh issue comment` rather than file a parallel GHI — pending
operator authorization (per OBPI-07/08 ceremony observation that
`attest completed` does not authorize external GitHub comment posts; the
GHI extension requires explicit authorization). Root cause and mitigation
are identical; tracking unification keeps the ADR-0.26.0 closeout-audit
footprint single. The Confirm-by-reference verdict here closes the
in-flight duplicate; GHI #376 carries the long-term tracking surface.

### Gate 4 (BDD): N/A

No operator-visible behavior change. The Confirm decision validates that
gzkit's existing audit surface continues to function identically; no new
commands, flags, output formats, or behavioral changes are introduced.
`features/heavy_lane_gate4.feature` is not touched.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — ADR-0.26.0 checklist item #9 captured verbatim above (`OBPI Entry (Level 1 WBS)` line).
- [x] **Gate 2 (TDD):** `uv run gz test --obpi OBPI-0.26.0-09-adr-audit-ledger` remains green; vacuous pass on `[doc]` REQ pattern via `_synthesize_doc_proof_linkage`. Existing test coverage on the gzkit audit surface (`tests/commands/test_adr_audit.py`, `tests/test_adr_audit_ledger_confirm.py`, related) exists from prior OBPIs (Confirm decided gzkit's surface is superior). Evidence captured in Stage 3 of the pipeline run.
- [x] **Gate 3 (Docs):** Decision rationale completed above (`## Decision`, six-point rationale + brief-scaffold-defect surfacing + duplicate-evaluation tracking + Gate 4 N/A) with concrete capability deltas across all named dimensions and the architectural-superiority observation.
- [x] **Gate 4 (BDD):** N/A — the Confirm-by-reference outcome introduces no operator-visible behavior change. `features/heavy_lane_gate4.feature` is not touched. Rationale: no CLI surface, no user-facing command, no ledger entry type, and no doc output is added, removed, or modified by this decision.
- [ ] **Gate 5 (Human):** Attestation recorded during Stage 4 ceremony of `gz-obpi-pipeline`.

### Implementation Summary



- Decision: Confirm — by reference to OBPI-0.25.0-19-adr-audit-ledger-pattern (attested 2026-04-11). gzkit's distributed audit surface (`commands/adr_audit.py` 758 L + `validate_pkg/ledger_check.py` 379 L + `commands/obpi_audit_cmd.py` 423 L; ~1,560 L total) already constitutes an architecturally superior audit surface to opsdev's `lib/adr_audit_ledger.py` (249 L) on all named dimensions.
- Modules compared: opsdev `adr_audit_ledger.py` (249 L; Layer 2 Gate 5 completeness checker, ADR-local `obpi-audit.jsonl` storage, `LedgerCheckResult` stdlib dataclass, depends on `adr_recon` helpers, library-only) vs gzkit distributed surface (`adr_audit_check()` central-ledger-graph traversal, brief content inspection via `_inspect_obpi_brief()`, `@covers` REQ traceability verification, three-axis attestation predicate `_requires_human_obpi_attestation`, TTY gate `_enforce_human_attestation_authenticity`, `--attestor-present` co-presence proxy, first-class CLI via `gz adr audit-check` / `gz obpi complete` / `gz obpi audit`).
- Architectural superiority across all named dimensions: purpose (gzkit adds REQ traceability + three-axis attestation + brief-content inspection), data source (central ledger graph vs per-ADR file), result model (Pydantic vs stdlib dataclass), completeness check (findings-based + content inspection vs status-only), evidence depth (brief content sections vs ledger values only), REQ traceability (gzkit-native vs absent), attestation predicate (three-axis vs single check), authenticity gate (TTY + co-presence proxy vs none), cross-platform parity, error handling (`GzCliError` + `SystemExit` vs early returns), dependencies (first-class internal pipeline vs `adr_recon` helpers), CLI integration (first-class vs library-only).
- New observation since 2026-04-11: `commands/adr_audit.py` has grown 83% (415 L → 758 L, +343 L) with strengthening extensions absorbed under ADR-0.0.22 (three-axis attestation predicate, TTY gate, `--attestor-present` co-presence proxy, `_requires_security_review_attestation` branch). Confirm verdict structurally stronger today than at 2026-04-11.
- Brief-scaffold-defect surfaced: brief Source Material at parent-ADR Cross-Reference Matrix row 9 reads "gzkit equivalent: None," and brief Assumptions block forecloses the Confirm path explicitly; both wordings are stale — gzkit HAS a ~1,560 L distributed audit surface; the precedent OBPI-0.25.0-19 attests Confirm; OBPI-0.26.0-04/07/08 already established `decision: Confirm` is validator-accepted despite the assumption. Sixth instance of the same scaffold-defect class across ADR-0.26.0 briefs.
- Duplicate-OBPI surface tracked under **GHI #376** — sixth structural instance after OBPI-0.26.0-04 (`lib/adr_governance.py`), OBPI-0.26.0-05 (`lib/ledger_schema.py`), OBPI-0.26.0-06 (`lib/drift_detection.py`), OBPI-0.26.0-07 (`lib/adr_traceability.py`), OBPI-0.26.0-08 (`lib/validation_receipt.py`). Resolution: extend GHI #376 with a sixth-instance comment in Stage 5 if operator authorizes; do not file parallel GHI.
- Brief-scaffold drift corrected in flight: ALL-CAPS section headings (`OBJECTIVE`, `SOURCE MATERIAL`, `ASSUMPTIONS`, `NON-GOALS`, `REQUIREMENTS (FAIL-CLOSED)`, `ALLOWED PATHS`, `QUALITY GATES (Heavy)`, `ADR ITEM`) renamed to title case; added missing `Lane`, `Denied Paths`, `Discovery Checklist` sections; `Verification Commands (Concrete)` → `Verification` with two OBPI-specific verification commands.
- No code absorbed under this brief; no `src/gzkit/` or `tests/` edits — Confirm decided existing surface is superior; modifying it would invalidate the OBPI-0.25.0-19 attestation.

### Key Proof



```bash
rg -n '^decision: Confirm|^\*\*Confirm\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md
# Confirms brief frontmatter and ## Decision body record the Confirm verdict.

rg -c 'OBPI-0.25.0-19' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md
# Expected: ≥10 — brief cites the canonical precedent across body, Decision rationale, Implementation Summary, Closing Argument.

test -f src/gzkit/commands/adr_audit.py && test -f src/gzkit/commands/obpi_audit_cmd.py
# Expected: gzkit modules exist (Confirm precedent under OBPI-0.25.0-19 attests they are superior).

wc -l src/gzkit/commands/adr_audit.py
# Expected: 758 (was 415 at OBPI-0.25.0-19 authoring; +83% growth confirms Confirm holds a fortiori).

uv run gz covers OBPI-0.26.0-09-adr-audit-ledger --json
# Expected: {"summary": {"total_reqs": ..., "uncovered_reqs": 0, ...}} — parity-gate pass for [doc] REQs via _synthesize_doc_proof_linkage.

uv run gz obpi validate --authored docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md
# Expected: OBPI Validation Passed.
```

ARB receipts (Stage 3): lint `arb-ruff-462d2e272f1e4fda9da8faab666ee9aa`, typecheck `arb-step-typecheck-05eada7eada74214b46312ca75cae0c0`, OBPI-scoped unittest `arb-step-unittest-67f6a900bcf84c4fb83c389811e4cddc`, mkdocs `arb-step-mkdocs-d205fd3f926042ff99da53150b63598e`. REQ→@covers parity: `gz covers OBPI-0.26.0-09-adr-audit-ledger --json` → `uncovered_reqs: 0` (vacuous parity-gate pass on `[doc]` REQs via `_synthesize_doc_proof_linkage`; `total_reqs: 0` reflects the doc-proof synthesis path). Mirroring the OBPI-04/05/06/07/08 sibling precedent: pre-existing failures (GHI #377 insight schema regression, GHI #378 expired `release.drift_command` flag) remain disclosed in the broader ADR-0.26.0 evidence trail; not introduced by this brief.

## Human Attestation

- Attestor: `Jeffry Babb`
- Date: 2026-05-02
- Attestation: attest completed — OBPI-0.26.0-09 Confirm-by-reference verdict on opsdev lib/adr_audit_ledger.py (249 L). Anchored on OBPI-0.25.0-19-adr-audit-ledger-pattern (attested 2026-04-11, identical 249-line source) and OBPI-0.26.0-04/07/08 sibling precedents for `decision: Confirm` despite stale brief Source Material asserting "gzkit equivalent: None" (and Assumption block foreclosing the Confirm path). Twelve-dimension capability comparison authored in brief ## Comparison; six-point rationale in ## Decision (rationale 6 records adr_audit.py 83% growth from 415 L to 758 L since 2026-04-11, layering ADR-0.0.22 three-axis attestation predicate, TTY gate, and --attestor-present co-presence proxy on the same architectural foundation — Confirm a fortiori). Brief-scaffold-defect surfaced (sixth instance across ADR-0.26.0); Gate 4 N/A (zero operator-visible change). Heavy-lane Stage 3 ARB receipts cited inline in Key Proof: lint arb-ruff-462d2e272f1e4fda9da8faab666ee9aa, typecheck arb-step-typecheck-05eada7eada74214b46312ca75cae0c0, OBPI-scoped unittest arb-step-unittest-67f6a900bcf84c4fb83c389811e4cddc, mkdocs arb-step-mkdocs-d205fd3f926042ff99da53150b63598e. REQ→@covers parity: 5×[doc] REQs, uncovered_reqs:0 via _synthesize_doc_proof_linkage. No `src/` or `tests/` edits (Confirm preserves OBPI-0.25.0-19 attestation). GHI #376 sixth-instance comment deferred to explicit operator authorization (out of scope for `attest completed`).

### Closing Argument

**Confirm-by-reference.** opsdev's `lib/adr_audit_ledger.py` (249 lines)
provides Layer 2 Gate 5 completeness checking via a `LedgerCheckResult`
stdlib dataclass, ADR-local `obpi-audit.jsonl` reading, missing/incomplete/
complete classification, and a markdown report formatter. gzkit's existing
audit surface — ~1,560 L distributed across `src/gzkit/commands/adr_audit.py`
(758 L; central-ledger-graph traversal via `adr_audit_check()`, brief
content inspection via `_inspect_obpi_brief()`, `@covers` REQ traceability,
three-axis attestation predicate `_requires_human_obpi_attestation`, TTY
gate `_enforce_human_attestation_authenticity`, `--attestor-present`
co-presence proxy), `src/gzkit/validate_pkg/ledger_check.py` (379 L; JSONL
ledger schema validation), and `src/gzkit/commands/obpi_audit_cmd.py`
(423 L; evidence gathering — test discovery, execution, coverage) — is
architecturally a strict superset on all named dimensions: purpose (gzkit
adds REQ traceability + three-axis attestation + brief-content inspection),
data source (central ledger graph vs per-ADR file), result model (Pydantic
vs stdlib dataclass), evidence depth (brief content sections vs ledger
status values only), REQ traceability (native vs absent), attestation
predicate (three-axis vs single check), authenticity gate (TTY +
co-presence proxy vs none), error handling (`GzCliError` + `SystemExit` vs
early returns), dependencies (first-class internal pipeline vs `adr_recon`
helpers), and CLI integration (first-class operator surface vs
library-only).

The opsdev module's per-ADR storage model contradicts gzkit's
central-ledger doctrine: `.gzkit/ledger.jsonl` is the single canonical
event log, and adding a parallel per-ADR audit storage system would double
the audit footprint, not strengthen it. Absorbing the opsdev pattern would
also force a stdlib-dataclass-to-Pydantic rewrite that defeats the purpose
of pattern absorption, and would require bundling the `adr_recon` helper
tree gzkit deliberately does not depend on. The post-2026-04-11 evolution
of `commands/adr_audit.py` (+83% growth, +343 L) layered ADR-0.0.22's
three-axis attestation predicate, TTY-fed authenticity gate, and
`--attestor-present` co-presence proxy on the same architectural
foundation — making the Confirm verdict structurally stronger today than at
the 2026-04-11 precedent attestation. Not absorbed.

This brief is the sixth evaluation of an opsdev `lib/` module across two
parent ADRs that the canonical OBPI-0.25.0-* sweep had already covered.
The brief Source Material's "gzkit equivalent: None" wording (and the
matching Assumption forecloser of the Confirm path) is itself a
brief-scaffold defect — gzkit HAS a ~1,560 L distributed audit surface —
and the precedent (OBPI-0.25.0-19 with Decision: Confirm, attested
2026-04-11) attests the Confirm verdict on identical source. OBPI-0.26.0-04
/ -07 / -08 already established the precedent that `decision: Confirm` is
validator-accepted despite the brief assumption; this brief follows that
precedent. GHI #376 to be extended (under operator authorization) with a
sixth-occurrence comment so the absorption sweep does not silently recur.
No code under `src/gzkit/` or `tests/` is modified by this brief; modifying
the existing surface would invalidate the 2026-04-11 OBPI-0.25.0-19
attestation. Gate 4 N/A: zero operator-visible behavior change.
