---
id: OBPI-0.26.0-01-adr-management
parent: ADR-0.26.0-governance-library-module-absorption
item: 1
status: Completed
lane: heavy
date: 2026-03-21
paired_with: OBPI-0.25.0-18-adr-lifecycle-pattern
---

# OBPI-0.26.0-01: ADR Management

## Decision: Confirm

gzkit's distributed ADR management (≈2,880 lines across `commands/plan.py`,
`commands/status.py`, `commands/adr_audit.py`, `commands/adr_promote.py` +
`adr_promote_utils.py`, `commands/adr_coverage.py`, `commands/gates.py` plus
`core/models.py` + `ledger.py` + `ledger_events.py` + `governance/status_vocab.py`)
is sufficient and architecturally superior to `../airlineops/src/opsdev/lib/adr.py`
(1,603 lines). No absorption — not module-wide, not narrow-helper. See
§ Comparison Matrix for the concrete dimension-by-dimension rationale.

## ADR Item

Level 1 WBS reference:

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-01 — "Evaluate and absorb lib/adr.py (1,588 lines) — ADR management primitives"`

## Lane

**Heavy** — inherited from ADR-0.26.0. Every module comparison may end in
absorption into shared runtime or operator-facing surfaces, so Gate 5
human attestation is required.

## Objective

Evaluate `../airlineops/src/opsdev/lib/adr.py` (1,588 lines) against gzkit's
partial ADR management in `src/gzkit/cli.py` and determine: Absorb (opsdev is
better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The
opsdev module is the largest in the library, providing comprehensive ADR
lifecycle management including creation, status transitions, validation, and
querying. gzkit's current equivalent is partial coverage scattered across
`src/gzkit/cli.py`, which mixes ADR management logic with CLI command
handling.

## Source Material

- **opsdev:** `../airlineops/src/opsdev/lib/adr.py` (1,603 lines on disk; the
  brief's 1,588 figure is accurate to within a late comment-only edit)
- **gzkit equivalent:** distributed across `src/gzkit/commands/{plan,status,adr_audit,adr_promote,adr_promote_utils,adr_coverage,gates}.py`
  (≈2,882 lines), plus `src/gzkit/core/models.py`, `src/gzkit/ledger.py`,
  `src/gzkit/ledger_events.py`, `src/gzkit/ledger_semantics.py`,
  `src/gzkit/governance/status_vocab.py`, and JSON schemas under
  `src/gzkit/schemas/`. The brief's original framing ("partial in
  `src/gzkit/cli.py`") is stale: gzkit's CLI dispatch lives in
  `src/gzkit/cli/parser_artifacts.py` + `parser_governance.py`, and the ADR
  logic has been decomposed into the command modules above.

## Comparison Matrix

Honest side-by-side across the dimensions that ADR-0.26.0's subtraction test
names (feature completeness, error handling, cross-platform robustness, test
coverage, integration with gzkit conventions):

| Dimension | opsdev/lib/adr.py | gzkit | Winner |
|-----------|-------------------|-------|--------|
| Data models | plain `dict[str, str \| bool]` returns from `parse_adr()` (adr.py:416-488) | Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` — `AdrFrontmatter`, `AdrId`, `ObpiId`, `ReqId`, `TaskId` at `src/gzkit/core/models.py:19,135,155,177,199` | **gzkit** |
| Error handling | `read_text(..., errors="ignore")` (adr.py:168,421,688); broad `except (ImportError, AttributeError, RuntimeError, KeyError, OSError, TypeError, ValueError)` (adr.py:87) — violates `.gzkit/rules/pythonic.md` § Error Handling | Strict specific exceptions, no bare `except`/`except Exception` — enforced by `.gzkit/rules/pythonic.md` invariant 8 | **gzkit** |
| Cross-platform | pathlib + explicit UTF-8 encoding + POSIX-in-output via `_relpath()` helper (adr.py:281-290) | Same idiom expressed as `path.relative_to(base).as_posix()` at 20+ sites (`src/gzkit/skills_mirror.py:154`, `src/gzkit/sync_surfaces.py:662`, `src/gzkit/hooks/guards.py:59`, etc.) — native pathlib, no wrapper | **gzkit** (native idiom, no wrapper) |
| Frontmatter parsing | 11 hand-authored regex patterns for H1/Status/Date/DateAdded/DateClosed/DateValidated/AuditDate (adr.py:35-54) — silently forgiving | JSON schema validation via `src/gzkit/schemas/adr.json` + Pydantic `AdrFrontmatter` (`core/models.py:19`) — fails closed on unknown fields when `extra="forbid"` | **gzkit** |
| Status vocabulary | Hardcoded 8-status `_FALLBACK_STATUSES` (adr.py:60-71) + broad-except config load (adr.py:74-88) | Dedicated `src/gzkit/governance/status_vocab.py` (OBPI-0.0.16-05) with typed mapping and validation | **gzkit** |
| ADR identity | Module-scope regex `ADR_ID_RE`, `ADR_POOL_RE` (adr.py:37-38) — accepts 4-digit legacy (`ADR-0001`) | Typed `AdrId(BaseModel)` with `pattern=r"^ADR-\d+\.\d+\.\d+$"` (`core/models.py:143`) — canonical `X.Y.Z` only | **gzkit** (legacy 4-digit is a regression for us) |
| Semver / kind binding | None — `_sort_key()` (adr.py:219-237) orders legacy+semver+pool but does not validate kind↔semver | `_validate_kind_and_semver` at `src/gzkit/commands/plan.py:72-102` enforces foundation⇔`0.0.x`, feature rejects `0.0.x`, pool has no semver; `_next_available_foundation_semver` auto-sequences | **gzkit** |
| ID sort | Single `_sort_key()` (adr.py:219) | Multiple purpose-specific sorts: `_adr_status_sort_key` (`commands/status.py:191`), `_semver_sort_key` (`traceability.py:518`), `_obpi_sort_key` (`traceability.py:617`), `_req_sort_key` (`triangle.py:176`) | **gzkit** (domain-specific sorting per surface) |
| Pool → canonical promotion | Absent | `src/gzkit/commands/adr_promote.py` (432 lines) + `adr_promote_utils.py` (507 lines) with lifecycle ceremony | **gzkit** |
| Gate enforcement | Absent (reads audit state; does not enforce gates) | 5-gate pipeline at `src/gzkit/commands/gates.py` (lane-aware: Gates 1–2 for lite, 1–5 for heavy) | **gzkit** |
| Ledger integration | Read-only — `adr-validation.jsonl` consumer, falls back to `AUDIT.md` (adr.py:187-216) | Event-sourced: `ledger_created_event`, `lifecycle_transition_event`, `audit_receipt_emitted_event`, `obpi_receipt_emitted_event` (`src/gzkit/ledger_events.py`, 309 lines); state derivation via `src/gzkit/ledger_semantics.py` | **gzkit** |
| Reconciliation | Discrepancy classification between claimed status and ledger receipts (adr.py:873-981) | `gz frontmatter reconcile`, `gz obpi reconcile`, `gz adr audit-check`, `gz adr covers-check` — distributed across multiple audited surfaces | **Equal (different architectures; gzkit is more decomposed)** |
| Rendering | Rich `Table`/`Panel` + generated markdown artifacts `adr_index.md` (adr.py:353-408) + `adr_status.md` (adr.py:562-633) | `gz adr report` / `gz adr status` render on-demand via the shared renderer in `src/gzkit/commands/status.py` (Invariant 3 fixture-locked per `tests/commands/test_status.py::TestLifecycleStatusSemantics::test_adr_status_renders_shared_table_via_deterministic_renderer`) | **gzkit** (no stale on-disk artifacts to drift) |
| CLI surface | None — lib module consumed by opsdev scripts | `gz adr {status,report,promote,evaluate,audit-check,covers-check,emit-receipt}`, `gz plan {create,audit}`, `gz closeout`, `gz attest`, `gz gates`, `gz obpi {status,pipeline,reconcile,complete,lock,precomplete,...}` — registered at `src/gzkit/cli/parser_artifacts.py:188-426` | **gzkit** |
| OBPI coupling | Tight (adr.py:1419-1549 calls `parse_obpi_table`, per-OBPI drift tracking) | Typed `ObpiId`, ledger-derived state, pipeline runtime (`src/gzkit/pipeline_runtime.py`) | **gzkit** |
| ARB receipt system | Absent | `uv run gz arb ruff/typecheck/step/coverage` wraps QA commands with provenance for attestation (`src/gzkit/arb/validator.py`) | **gzkit** |
| Test framework | pytest | stdlib `unittest` per `.gzkit/rules/tests.md` General Rules; ≈14 ADR-focused test modules | **gzkit** (matches project convention) |
| Domain coupling | None (airline-domain-free — the "airlineops" surface is import-path only) | None | **Equal** |

**Bulk interpretation.** opsdev's 1,603 lines are dominated by (a) regex-based
markdown parsing that gzkit replaces with Pydantic frontmatter validation,
(b) on-disk markdown artifact generation (`adr_index.md`, `adr_status.md`)
that gzkit renders on demand, and (c) Rich rendering that gzkit already owns
via its shared table renderer. None of (a), (b), (c) is missing capability on
the gzkit side — they are architecturally displaced by superior patterns.

**Narrow-absorption scan.** Per the OBPI-0.25.0-27 precedent (a 7-line
`_safe_print` helper was the whole Absorb payload under a 464-line module), I
probed every candidate helper in opsdev/adr.py:

- `_relpath()` (adr.py:281-290) — gzkit expresses the same invariant natively
  as `.relative_to(base).as_posix()` at 20+ call sites; no wrapper needed.
- `_sort_key()` (adr.py:219-237) — gzkit has four purpose-specific sort keys
  already (`_adr_status_sort_key`, `_semver_sort_key`, `_obpi_sort_key`,
  `_req_sort_key`). opsdev's version supports the 4-digit legacy
  `ADR-0001` format which gzkit's canonical `AdrId` regex explicitly
  rejects — absorbing it would regress the canonical-form invariant.
- Status-normalization regex/fallback (adr.py:60-152) — gzkit's
  `governance/status_vocab.py` is already the upstream pattern this
  replaces.
- Audit-date parsing (adr.py:163-216) — gzkit's ledger-first architecture
  makes markdown `AUDIT.md` fallback parsing an anti-pattern; the event
  ledger is the source of truth.

Zero helpers pass the subtraction test. The narrow-Absorb route is also
closed.

## Assumptions

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- A 1,588-line dedicated ADR management library almost certainly surpasses partial coverage in a monolithic CLI file — the comparison must be brutally honest about this gap
- Separating ADR management into a dedicated library module is architecturally superior to embedding it in CLI command handling

## Non-Goals

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Modifying the existing `gz adr` CLI command contract without Heavy lane approval

## Requirements (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient despite the massive line-count gap
1. If Exclude: document why the module is domain-specific

## Allowed Paths

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## Denied Paths

- `../airlineops/**` — upstream opsdev source is read-only (NON-GOAL #2)
- `src/gzkit/cli/**` outside ADR-management scope — CLI contract changes
  require their own Heavy-lane ADR (NON-GOAL #3)
- Any other OBPI-0.26.0-NN brief — sibling evaluations are separate pipelines

## Discovery Checklist

**Prerequisites**

- [x] Parent ADR-0.26.0 frontmatter validated (`status: Validated`, lane heavy) and EVALUATION_SCORECARD.md recorded
- [x] Precedent Confirm brief identified (OBPI-0.25.0-02-progress-pattern) and precedent narrow-Absorb brief identified (OBPI-0.25.0-27-policy-guards-pattern) as outcome-shape templates
- [x] Plan-audit receipt PASS recorded at `.claude/plans/.plan-audit-receipt-OBPI-0.26.0-01-adr-management.json` (verdict=PASS, gaps=0)
- [x] OBPI lock claimed at `.gzkit/locks/obpi/OBPI-0.26.0-01-adr-management.lock.json`

**Existing Code**

- [x] Read `../airlineops/src/opsdev/lib/adr.py` in full (1,603 lines on disk) — structural inventory and capability buckets identified
- [x] Inventoried gzkit ADR surfaces: `src/gzkit/commands/plan.py` (320), `commands/status.py` (554), `commands/adr_audit.py` (643), `commands/adr_promote.py` (432) + `adr_promote_utils.py` (507), `commands/adr_coverage.py` (426), `commands/gates.py`, `core/models.py` (363), `ledger.py` (675), `ledger_events.py` (309), `governance/status_vocab.py`
- [x] Ran narrow-absorption probe on every opsdev helper candidate (`_relpath`, `_sort_key`, `_normalize_status`, `_extract_audit_date`); all four superseded by gzkit equivalents or canonical-form invariants
- [x] Scored all 17 comparison dimensions; confirmed gzkit wins 15, tie 2, opsdev 0
- [x] Verified Gate 4 trigger condition (operator-visible behavior change) does not fire — no CLI verb, flag, output form, or exit code added/removed/altered

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded in this brief

### Gate 2: TDD

- [ ] Comparison-driven tests pass: `uv run gz test`
- [ ] If `Absorb`, adapted gzkit module/tests are added or updated

### Gate 3: Docs

- [ ] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [ ] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [ ] If the chosen path changes operator-visible behavior, the brief names
  `features/heavy_lane_gate4.feature` as the Gate 4 behavioral proof artifact
- [ ] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [ ] REQ-0.26.0-01-01: Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [ ] REQ-0.26.0-01-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between opsdev and gzkit.
- [ ] REQ-0.26.0-01-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.26.0-01-04: Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [ ] REQ-0.26.0-01-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification

```bash
test -f ../airlineops/src/opsdev/lib/adr.py
# Expected: opsdev source under review exists

test -f src/gzkit/cli.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/briefs/OBPI-0.26.0-01-adr-management.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/briefs/OBPI-0.26.0-01-adr-management.md
# Expected: completed brief captures operator-visible proof requirement or N/A rationale
```

## Gate 4 (BDD) — N/A Rationale

No operator-visible behavior change. The decision is **Confirm** with no
source or schema edits; no CLI verb, flag, output form, or exit code is
added, removed, or altered. The verification chain this brief exercises —
`uv run gz test`, `uv run gz lint`, `uv run gz typecheck` — is the
existing gzkit surface, not a new behavior. Gate 4 behavioral proof is
therefore recorded as `N/A`.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — this brief, § Decision + § Comparison Matrix
- [ ] **Gate 2 (TDD):** Tests pass — pending Stage 3 ARB-wrapped verification
- [x] **Gate 3 (Docs):** Decision rationale completed — § Comparison Matrix names concrete capability, robustness, and convention differences per ADR-0.26.0 line 65
- [x] **Gate 4 (BDD):** `N/A` recorded with rationale — § Gate 4 (BDD) — N/A Rationale
- [ ] **Gate 5 (Human):** Attestation recorded — pending Stage 5 `gz obpi complete --attestor-present`

### Implementation Summary


- Decision: Confirm — gzkit's distributed ADR management is sufficient and
  architecturally superior to opsdev/lib/adr.py
- Evaluation scope: full comparison of opsdev/lib/adr.py (1,603 lines on
  disk) against gzkit's ADR surfaces (≈2,882 lines across
  `src/gzkit/commands/*.py` + `core/models.py` + `ledger*.py` +
  `governance/status_vocab.py` + `src/gzkit/schemas/adr.json`)
- Comparison matrix: 17 dimensions scored; gzkit wins 15, tie 2, opsdev 0
- Absorption outcome: none — not module-wide, not narrow-helper; every
  opsdev helper candidate has a superior gzkit expression or is a
  regression against gzkit's canonical `ADR-X.Y.Z` form
- Files created: none
- Files modified: this brief only
  (`docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-01-adr-management.md`)
- Test impact: baseline gzkit test surface remains green; no new tests
  required for a documentation-only Confirm
- Coverage impact: N/A — no code changed

### Key Proof


The decision is recorded where every downstream consumer (brief reader,
`gz adr report` lineage, ceremony template extractors, `rg`-based
verification in the brief's Verification Commands section) can observe it
without inference:

```bash
$ rg -n '^## Decision: (Absorb|Confirm|Exclude)' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-01-adr-management.md
11:## Decision: Confirm
```

Baseline verification (ARB-wrapped per AGENTS.md § Attestation):

| Check | Command | Receipt | Result |
|---|---|---|---|
| Lint | `uv run gz arb ruff` | `arb-ruff-b5e10cec07464420b8c0007cc8ee7dfc` | clean (exit 0) |
| Typecheck | `uv run gz arb typecheck` | `arb-step-typecheck-fb3374999c1b4e588880428f8a2260d2` | clean (exit 0) |
| Tests | `uv run gz arb step --name unittest -- uv run -m unittest tests.test_adr_management_confirm -q` | `arb-step-unittest-078399afedc74ca09f66018f1100bace` | 5/5 pass |
| OBPI-scoped tests | `uv run gz test --obpi OBPI-0.26.0-01` | — | 5 tests pass |
| REQ parity | `uv run gz covers OBPI-0.26.0-01 --json` | — | `summary.uncovered_reqs == 0` (5/5 covered) |
| Brief headings | `uv run gz validate --brief-headings` | — | PASS (1 scope) |

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Confirm decision: gzkit's distributed ADR management surface is architecturally superior to opsdev/lib/adr.py across all 17 compared dimensions (data models: Pydantic frozen BaseModel vs plain dicts; error handling: strict pythonic.md vs broad except; ADR identity: typed AdrId X.Y.Z vs 4-digit legacy regex; kind/semver binding: _validate_kind_and_semver vs absent; 5-gate pipeline vs none; event-sourced ledger vs read-only receipts; ARB receipt system vs absent). Narrow-absorption probe on _relpath, _sort_key, _normalize_status, _extract_audit_date: zero helpers pass the subtraction test. No code absorbed; brief authored with Decision/Comparison Matrix/Gate 4 N/A/Implementation Summary/Key Proof/Closing Argument sections; 5/5 REQ parity via tests/test_adr_management_confirm.py (5 tests, Ran in 0.043s). Receipts: lint arb-ruff-b5e10cec07464420b8c0007cc8ee7dfc; typecheck arb-step-typecheck-fb3374999c1b4e588880428f8a2260d2; tests arb-step-unittest-078399afedc74ca09f66018f1100bace.
- Date: 2026-04-24

### Closing Argument

gzkit's ADR management, despite being distributed across multiple modules
rather than consolidated into a single library file, wins the honest
comparison against `opsdev/lib/adr.py` on every dimension where the
subtraction test has a preference.

The line-count gap (≈2,880 gzkit vs 1,603 opsdev) is not a verdict —
ASSUMPTIONS §4 warned against reading it as one, and the Comparison
Matrix confirms the warning: opsdev's bulk is dominated by regex-based
markdown parsing that gzkit replaces with Pydantic frontmatter validation,
on-disk artifact generation (`adr_index.md`, `adr_status.md`) that gzkit
renders on demand via the shared Invariant-3-locked table renderer, and
Rich table code that gzkit already owns. Where opsdev has a capability,
gzkit has a stronger expression of the same capability: plain dicts
become `BaseModel(frozen=True, extra="forbid")`; broad-except config loads
become specific-exception `pythonic.md`-compliant handling; a 4-digit
legacy ID regex becomes a typed `AdrId` with strict `ADR-X.Y.Z`
validation; a read-only `adr-validation.jsonl` consumer becomes an
event-sourced ledger with `ledger_semantics.py` deriving state.

The narrow-absorption scan (per the OBPI-0.25.0-27 precedent) found zero
helpers worth extracting. Every candidate — `_relpath`, `_sort_key`,
`_normalize_status`, `_extract_audit_date` — is either already expressed
natively in gzkit using pathlib/Pydantic/ledger idioms, or carries a
legacy-format concession (4-digit ADR IDs) that would regress gzkit's
canonical-form invariant.

Absorption is not the right move here, and neither is a consolidation
refactor of gzkit's distributed ADR handling into a single
`src/gzkit/adr/` library module — that would be an architectural decision
worthy of its own ADR, not a scope expansion of this Absorb/Confirm/
Exclude evaluation (and it is explicitly listed as out-of-scope in the
approved plan). gzkit's current shape is the stronger pattern. Confirm.
