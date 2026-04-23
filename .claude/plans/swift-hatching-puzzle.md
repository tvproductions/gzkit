# OBPI-0.0.20-03 — Fold attestation-enrichment.md

## Context

`.gzkit/rules/attestation-enrichment.md` (156 lines, `paths: "**"`) loads into every
agent turn's context despite being mostly ARB middleware pedagogy. Per parent
ADR-0.0.20 (agent-rule-placement-invariant), a `paths: "**"` rule file must
either hold binding invariants (→ AGENTS.md) or pedagogy/reference (→
`docs/governance/`). This OBPI splits the file accordingly:

- **Binding content** (em-dash pattern, canonical invocations table, lane
  behavior, applies-to, worked example) → new § Attestation in `AGENTS.md`.
- **ARB middleware deep-dive** (core concept, command surface, receipt
  schemas, exit codes, rationale) → new `docs/governance/arb-middleware.md`.
- **Canonical rule file** → deleted, allow-list entry removed, mirrors
  regenerated.

This is OBPI #3 of 5 under ADR-0.0.20. OBPI-01 (validator + allow-list) is
Completed. OBPI-02 (fold agent-contract.md) precedent already modified
AGENTS.md structure and is parallel-safe with OBPI-03.

Lane is Lite, but parent ADR is foundation-kind → brief-level human
attestation still required (Normal-mode Stage 4) per AGENTS.md §
Lane & Kind Attestation Matrix.

## Scope summary

| Change | Count |
|---|---|
| AGENTS.md — add § Attestation | 1 section |
| docs/governance/arb-middleware.md — create | 1 new file |
| .gzkit/rules/attestation-enrichment.md — delete | 1 file |
| .gzkit/manifest.json — remove allow-list entry | 1 entry |
| Python docstring + error-message updates | 6 files (per brief) + 2 scoped AGENTS.md (`src/gzkit/cli`, `src/gzkit/commands`) + 1 template (`src/gzkit/templates/agents.md`) |
| ARB command docs | 8 files in `docs/user/commands/` |
| Manpage + runbook citation fixes | `docs/user/manpages/arb.md` (2 lines), `docs/user/runbook.md` (3 lines) |
| New TDD test | `tests/governance/test_attestation_fold.py` |
| Sync mirrors | `uv run gz agent sync control-surfaces` |
| Downstream staleness GHI | ADR-0.36.0 OBPI-08 |

## Implementation steps

### Step 1 — TDD RED (REQ-14)

Create `tests/governance/test_attestation_fold.py` with assertions for the
semantic migration invariants:

- `TestAttestationFold.test_agents_md_has_canonical_invocations_table` — asserts
  AGENTS.md § Attestation contains all 5 canonical-invocation rows (lint,
  typecheck, tests, coverage, docs).
- `TestAttestationFold.test_agents_md_has_em_dash_pattern` — asserts the
  binding em-dash pattern string is present.
- `TestAttestationFold.test_agents_md_has_lane_behavior` — asserts Lite warn
  / Heavy fail-closed text is present.
- `TestAttestationFold.test_arb_middleware_doc_exists` — asserts
  `docs/governance/arb-middleware.md` exists and contains command examples.
- `TestAttestationFold.test_canonical_rule_file_deleted` — asserts
  `.gzkit/rules/attestation-enrichment.md` does NOT exist.
- `TestAttestationFold.test_no_python_references_deleted_rule` — scans
  `src/gzkit/arb/**` + `src/gzkit/commands/arb.py` + `src/gzkit/commands/obpi_precomplete.py`
  for `.gzkit/rules/attestation-enrichment.md`; asserts zero matches.

Decorate each with `@covers("REQ-0.0.20-03-14")` (mapping to the semantic
REQ). Run once to confirm RED (file still exists, section absent).

### Step 2 — Add § Attestation to AGENTS.md

Insert a new `## Attestation` section between `## Execution Rules` and
`## Control Surfaces` (line ~283) containing:

- Pattern (binding): em-dash format with provenance note
- Canonical invocations table (lint / typecheck / tests / coverage / docs)
- Applies to (obpi complete, adr emit-receipt, git commit, …)
- Lane behavior (Lite warn / Heavy fail-closed)
- One worked example (reuse existing example from rule file, abridged)

Cross-link to `docs/governance/arb-middleware.md` for deep-dive.

### Step 3 — Create docs/governance/arb-middleware.md

New file with sections:
1. ARB Middleware — Core Concept (what ARB is, what it records)
2. Available Commands (ruff / step / typecheck / coverage / validate / advise / patterns)
3. Receipt Schema and Storage (schema `$id`s, `artifacts/receipts/`,
   `.gzkit.json` key `arb.receipts_root`)
4. Exit Codes (0/1/2 semantics)
5. Rationale (Why receipts not narrative; Why canonical commands;
   TDD RED not ARB-shaped — GHI #157)

Lift verbatim (with minor surrounding-prose adjustments) from the rule
file. Add a frontmatter header per `docs/governance/` convention
(title + description).

### Step 4 — Update Python citations (6 files per brief + 3 scope-expansions)

Brief list:
- `src/gzkit/cli/parser_arb.py:6` → "See `AGENTS.md § Attestation` for the
  rule contract"
- `src/gzkit/arb/__init__.py:5-6` → point at `AGENTS.md § Attestation`
  (binding) and `docs/governance/arb-middleware.md` (detail)
- `src/gzkit/arb/validator.py:184` → error message: replace
  `.gzkit/rules/attestation-enrichment.md` with
  `AGENTS.md § Attestation` (canonical invocations are binding rule, not
  deep-dive)
- `src/gzkit/commands/arb.py:4` → same pattern
- `src/gzkit/commands/obpi_precomplete.py:206` → update docstring cite
- `features/steps/gz_steps.py` — brief mentions, but `grep` found no
  direct `.gzkit/rules/attestation-enrichment.md` reference; the scan will
  confirm at RED. If absent, this REQ-05 sub-item is vacuously satisfied;
  if present, update.

Scope expansions (per Prime Directive — update references in step with
deletion):
- `src/gzkit/cli/AGENTS.md:103`
- `src/gzkit/commands/AGENTS.md:186`
- `src/gzkit/templates/agents.md:22,90` — template used by `gz init`;
  leaving the broken citation would propagate the defect to every new
  project scaffold.

### Step 5 — Update 8 ARB command docs

Replace `.gzkit/rules/attestation-enrichment.md` with either
`AGENTS.md § Attestation` (binding contract) or
`docs/governance/arb-middleware.md` (detail reference) per context. The
distinction matches what each doc is citing for: rule authority → AGENTS.md;
technical detail → arb-middleware.md.

Files (grep-confirmed):
- `docs/user/commands/arb.md` (lines 40, 114)
- `docs/user/commands/arb-ruff.md` (lines 53, 61)
- `docs/user/commands/arb-step.md` (lines 54, 62)
- `docs/user/commands/arb-coverage.md` (lines 50, 58)
- `docs/user/commands/arb-typecheck.md` (line 43)
- `docs/user/commands/arb-validate.md` (line 51)
- `docs/user/commands/arb-advise.md` (line 53)
- `docs/user/commands/arb-patterns.md` (line 53)

Also scope-expand:
- `docs/user/manpages/arb.md` (lines 128, 132)
- `docs/user/runbook.md` (lines 163, 164, 178)

### Step 6 — Delete canonical rule file + manifest entry

1. `rm .gzkit/rules/attestation-enrichment.md`
2. In `.gzkit/manifest.json`, remove the allow-list entry at line 83
   (adjust surrounding JSON so the list remains valid).

### Step 7 — Sync control surfaces

`uv run gz agent sync control-surfaces`

Expected: `.claude/rules/attestation-enrichment.md` and
`.github/instructions/attestation_enrichment.instructions.md` (if present)
are pruned; manifest-driven regeneration skips the deleted entry.

### Step 8 — Run TDD GREEN + full verification

```bash
uv run ruff check . --fix && uv run ruff format .
uvx ty check . --exclude 'features/**'
uv run -m unittest tests.governance.test_attestation_fold -v
uv run gz validate --unscoped-rules
uv run gz validate --all
uv run gz test --obpi OBPI-0.0.20-03-fold-attestation-enrichment
uv run mkdocs build --strict
```

### Step 9 — File downstream GHI (REQ-13)

```bash
gh issue create --label defect \
  --title "ADR-0.36.0 OBPI-08 premise broken: .claude/rules/arb.md was absorbed into attestation-enrichment.md (2026-04-21), now consolidated into AGENTS.md per ADR-0.0.20" \
  --body "..."
```

Body cites ADR-0.36.0-OBPI-0.36.0-08 (instruction-file reconciliation for
arb) and proposes either WBS refresh or withdrawal of OBPI-08.

## Critical files to modify

| Path | Action |
|---|---|
| `AGENTS.md` | Add § Attestation (new section, between Execution Rules and Control Surfaces) |
| `docs/governance/arb-middleware.md` | Create (new) |
| `.gzkit/rules/attestation-enrichment.md` | Delete |
| `.gzkit/manifest.json` | Remove allow-list entry (line 83) |
| `src/gzkit/cli/parser_arb.py` | Docstring cite |
| `src/gzkit/arb/__init__.py` | Module docstring |
| `src/gzkit/arb/validator.py` | Error message at line 184 |
| `src/gzkit/commands/arb.py` | Docstring cite |
| `src/gzkit/commands/obpi_precomplete.py` | Docstring at `_check_arb_receipts_present()` |
| `features/steps/gz_steps.py` | If reference present (verify during Step 4) |
| `src/gzkit/cli/AGENTS.md` | Citation update |
| `src/gzkit/commands/AGENTS.md` | Citation update |
| `src/gzkit/templates/agents.md` | Citation update (template for `gz init`) |
| `docs/user/commands/arb*.md` (8 files) | Citation update |
| `docs/user/manpages/arb.md` | Citation update |
| `docs/user/runbook.md` | Citation update |
| `tests/governance/test_attestation_fold.py` | Create (TDD) |

## Reused patterns

- OBPI-0.0.20-02 already modified AGENTS.md (adding Prime Directive material);
  same structural editing approach — insert new H2, follow existing heading
  cadence.
- Existing `docs/governance/` files (e.g. `trust-doctrine.md`,
  `state-doctrine.md`) provide the frontmatter + H1 + ToC shape for
  `arb-middleware.md`.
- `@covers` decorator pattern from `tests/governance/test_*.py` modules
  (e.g. `test_type_ignore_syntax.py`).

## Verification

```bash
# Stage 3 baseline
uv run gz lint
uv run gz typecheck
uv run gz test --obpi OBPI-0.0.20-03-fold-attestation-enrichment
uv run gz validate --unscoped-rules
uv run gz validate --all
uv run mkdocs build --strict

# Phase 1b parity
uv run gz covers OBPI-0.0.20-03-fold-attestation-enrichment --json

# Brief-specific verification (from the brief)
wc -l .gzkit/rules/attestation-enrichment.md          # Expect: file not found
test ! -f .gzkit/rules/attestation-enrichment.md
grep -q "Canonical invocations" AGENTS.md
test -f docs/governance/arb-middleware.md

# Sync
uv run gz agent sync control-surfaces
test ! -f .claude/rules/attestation-enrichment.md

# Downstream GHI
gh issue list --label defect --search "ADR-0.36.0 OBPI-08"
```

## Stage 4 evidence expectations

All 16 REQs addressed with concrete artifacts. Key proof: before/after
line counts on AGENTS.md and the new governance doc, `gz validate
--unscoped-rules` exit 0, ADR-0.36.0 staleness GHI URL.

Normal-mode Stage 4: operator attestation required before Stage 5 sync
(foundation-kind brief-level attestation).
