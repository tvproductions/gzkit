# OBPI-0.26.0-01 — ADR Management Evaluation Plan

## Context

OBPI-0.26.0-01 (Heavy lane, Normal execution mode) requires comparing
`../airlineops/src/opsdev/lib/adr.py` (1,588 lines, generic ADR management
library) against gzkit's current ADR handling and recording one final decision:
**Absorb**, **Confirm**, or **Exclude**. The parent ADR is already Validated
(scorecard complete); this OBPI's work product is the completed brief with
rationale, not a re-scoring of the ADR.

Phase-1 exploration established:

- **opsdev side.** Consolidated 1,588-line module. Capabilities span discovery,
  parsing, status normalization, reconciliation, index/table generation, and
  Rich rendering. Data models are **plain dicts** (no Pydantic). Error handling
  is **lenient** (`read_text(..., errors="ignore")`, broad `OSError` catches).
  Tests are **pytest**. Heavy coupling to opsdev-specific `adr_recon.py` and
  `validation_receipt.py`. **No airline-domain coupling** — the "airlineops"
  surface is import-path only; the logic is genuinely generic.

- **gzkit side.** Distributed across `src/gzkit/commands/` — `plan.py` (320),
  `status.py` (554), `adr_audit.py` (643), `adr_promote.py` + `_utils.py`
  (939), `adr_coverage.py` (426), `gates.py`, plus `ledger.py` (675) and
  `ledger_events.py` (309). Data models are **Pydantic `BaseModel`**
  (`core/models.py`, `AdrFrontmatter` with 19 fields, JSON schemas under
  `src/gzkit/schemas/`). **5-gate pipeline**, **kind/semver binding**
  (foundation ⇔ 0.0.x, feature ⇔ non-0.0.x, pool ⇔ no semver), **pool→canonical
  promotion**, **ledger semantics** (`ledger_semantics.py` derives OBPI state
  from event stream), **ARB receipt infrastructure**. Tests are stdlib
  **unittest** across 14+ ADR-focused files.

- **Precedent.** OBPI-0.25.0-02 (Confirm — gzkit's progress infra wins on
  mode integration + context managers). OBPI-0.25.0-27 (narrow Absorb — a
  7-line `_safe_print` helper, not the whole module).

The comparison matters not because line count decides the outcome — a 1,588-line
module with plain dicts and lenient errors is not automatically superior to
2,800+ lines of Pydantic-modeled, schema-validated, ledger-integrated,
5-gate-enforced logic. The brief must name the concrete differences honestly.

## Recommended Approach

**Decision path: Confirm**, with explicit scan for any narrow
absorption-worthy helpers (OBPI-0.25.0-27 pattern). Rationale must be grounded
in side-by-side capability matrix — not "gzkit has more lines" or "gzkit is
better by default," both of which ADR-0.26.0 line 65 explicitly prohibits.

### Work Plan

**Step 1 — Deep read of opsdev/lib/adr.py**

- Read the full file (1,588 lines) to verify the Phase-1 structural summary
  and spot any capability the explore agent missed.
- Output: mental model of every public symbol and its rationale.

**Step 2 — Deep read of gzkit ADR surfaces**

- Read the gzkit ADR command files identified in Phase 1:
  `src/gzkit/commands/plan.py`, `status.py`, `adr_audit.py`, `adr_promote.py`,
  `adr_promote_utils.py`, `adr_coverage.py`, `gates.py`, `ledger.py`,
  `ledger_events.py`, `core/models.py`.
- Output: mental model of gzkit's current coverage for each opsdev capability.

**Step 3 — Build capability matrix**

- For each opsdev capability bucket (a–h from Phase 1), name gzkit's equivalent
  (file:line or "absent") and compare on: feature completeness, error handling,
  data modeling, cross-platform robustness, test pattern, integration with the
  5-gate pipeline.
- Output: matrix ready to paste into the brief's rationale section.

**Step 4 — Narrow-absorption scan**

- Scan opsdev/adr.py for any small, self-contained helper that is cleanly
  better than its gzkit counterpart (the OBPI-0.25.0-27 `_safe_print` pattern).
  Candidates to probe:
  - `_relpath()` (lines 281-290) — POSIX path normalization for generated
    markdown. Check gzkit equivalent; likely already covered by `pathlib`
    conventions.
  - `_sort_key()` (lines 219-237) — semver-aware sorting with legacy+pool
    bucketing. Check gzkit's ADR ordering; gzkit already enforces semver
    ordering via `core/models.py` and CLAUDE.md local rule.
  - Regex patterns (lines 35-54) — H1/ID/status/date extraction. Check
    whether gzkit already has equivalent frontmatter-based parsing; it does,
    via Pydantic schema validation.
- Decision rule: absorb only if the helper adds concrete, non-duplicative
  value and passes the subtraction test. Default: no absorption.

**Step 5 — Draft decision**

- Likely **Confirm** (documentation-only). Rationale must cite the concrete
  differences, not vague adjectives. If any helper passes Step 4, decision
  shifts to **narrow Absorb** (e.g. "Absorb-helper: `_safe_print` only").

**Step 6 — Author brief sections**

Write directly into
`docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-01-adr-management.md`:

- **Decision line** (so `rg 'Absorb|Confirm|Exclude'` hits it per the brief's
  verification command on line 114)
- **Comparison rationale** (the capability matrix + concrete-differences prose)
- **### Implementation Summary** — bulleted "- Key: value" form (satisfies
  `_has_substantive_implementation_summary`)
- **### Key Proof** — concrete command + output + ARB receipt IDs (from
  Step 8)
- **### Closing Argument** — "why Confirm wins on these named dimensions"
- **Gate 4 N/A rationale** — documentation-only Confirm has no operator-visible
  behavior change; record N/A with a sentence explaining why
- **Completion checklist boxes** — Gates 1/2/3/4/5 ticked with evidence

**Step 7 — Tests**

- If decision is **Confirm** with no code change: no new tests required. The
  brief's Gate 2 is satisfied by running `uv run gz test --obpi OBPI-0.26.0-01`
  and observing existing coverage remains green.
- If decision is **Absorb (narrow)**: add the helper to its target gzkit
  module, write unittest tests (TempDBMixin if DB-touching; 40% coverage
  floor), decorate with `@covers(REQ-0.26.0-01-03)`.
- If decision is **Exclude**: no tests; document the domain-specific reason.

**Step 8 — ARB receipts (Heavy lane required)**

- `uv run gz arb ruff` → `arb-ruff-*`
- `uv run gz arb typecheck` → `arb-step-typecheck-*`
- `uv run gz arb step --name unittest -- uv run -m unittest -q` →
  `arb-step-unittest-*`

Cite these IDs in the brief's Key Proof and in the attestation text per
`AGENTS.md` § Attestation.

**Step 9 — Stage 3 REQ parity gate**

- Run `uv run gz covers OBPI-0.26.0-01 --json` and confirm
  `summary.uncovered_reqs == 0`. REQ-01 through REQ-05 must each be traceable
  to a `@covers` reference. For a **Confirm** outcome, the coverage may be
  documentation-based: decorate a single brief-verification test that asserts
  the decision line exists in the brief (`rg 'Decision: Confirm|Absorb|Exclude'`)
  with `@covers(REQ-0.26.0-01-01)` and extend similarly for REQ-02, REQ-04,
  REQ-05. Verify this pattern matches how prior Confirm-outcome OBPIs closed
  the parity gate before adopting it; if the pattern differs, follow
  precedent.

**Step 10 — Stage 4 + 5 governance**

- Present the Stage 4 ceremony template populated with the brief's decision
  rationale and ARB receipt IDs.
- After operator attestation, run `gz obpi precomplete` then `gz obpi complete
  --attestor-present` (primary path) with enriched attestation text, lock
  release, pipeline marker cleanup, two git-syncs, and reconcile — per the
  pipeline skill's Stage 5 recipe.

### Critical files to modify

- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-01-adr-management.md`
  — the primary artifact; where the decision, rationale, evidence, and
  closing argument land.

### Files to modify only on narrow-Absorb outcome

- `src/gzkit/<target-module>.py` — the specific file that would host an
  absorbed helper (determined by Step 4's probe).
- `tests/<corresponding-test-file>.py` — unittest coverage for the absorbed
  helper, decorated with `@covers`.

### Files to reuse (no modification)

- Existing ADR command handlers listed in Phase-1 (they are the **evidence**
  that gzkit already has full coverage, not targets for refactor in this OBPI).

## Verification

```bash
# Gate 2 — baseline tests pass (OBPI-scoped per Stage 3 scope discipline)
uv run gz test --obpi OBPI-0.26.0-01

# Lint + typecheck (ARB-wrapped for receipt citation)
uv run gz arb ruff
uv run gz arb typecheck

# Brief-specific verification commands from the brief (lines 108-124)
test -f ../airlineops/src/opsdev/lib/adr.py
test -f src/gzkit/cli.py
rg -n 'Absorb|Confirm|Exclude' \
  docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-01-adr-management.md

# Stage 3 Phase 1b — REQ parity gate
uv run gz covers OBPI-0.26.0-01 --json

# Brief heading hygiene (canonical H3 for evidence sections)
uv run gz validate --brief-headings

# Stage 5 preflight
uv run gz obpi precomplete OBPI-0.26.0-01
```

All must pass before attestation. If any ARB receipt is missing at Heavy
lane, Stage 5 attestation fails closed per `AGENTS.md` § Attestation.

## Out of scope

- Modifying any other OBPI-0.26.0-NN brief (those are separate pipeline runs).
- Refactoring gzkit's distributed ADR handling into a unified `src/gzkit/adr/`
  library — that's an architectural decision for a future ADR, not this OBPI's
  Absorb/Confirm/Exclude scope.
- Changing the existing `gz adr` CLI contract (per brief NON-GOALS).
- Updating the parent ADR's EVALUATION_SCORECARD (already Validated).
