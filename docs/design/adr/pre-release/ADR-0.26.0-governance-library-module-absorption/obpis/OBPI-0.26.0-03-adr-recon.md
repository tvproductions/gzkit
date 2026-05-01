---
id: OBPI-0.26.0-03-adr-recon
parent: ADR-0.26.0-governance-library-module-absorption
item: 3
status: Completed
lane: heavy
date: 2026-03-21
---

# OBPI-0.26.0-03: ADR Reconciliation

## ADR Item

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-03 — "Evaluate and absorb lib/adr_recon.py (607 lines) — ADR reconciliation and consistency checking"`

## Objective

Evaluate `../airlineops/src/opsdev/lib/adr_recon.py` (607 lines) and
determine: Absorb (opsdev is better) or Exclude (domain-specific). gzkit's
reconciliation surface (`gz obpi reconcile`, `gz frontmatter reconcile`,
`gz register-adrs`, `governance/adr_status_index.py`) reaches the same
outcome through Layer-1 rewriting and Layer-3 regeneration; opsdev's
`adr_recon` reaches it through Layer-3 markdown-table patching. This OBPI
records the comparison outcome and decision rationale.

## Source Material

- **opsdev:** `../airlineops/src/opsdev/lib/adr_recon.py` (607 lines)
- **gzkit equivalent:** Functionally divergent — `gz obpi reconcile` (`src/gzkit/commands/status.py:362-417`), `gz frontmatter reconcile` via `governance/frontmatter_coherence.py` (416 lines), `governance/adr_status_index.py` (238 lines), `governance/trust_audits/reconcile.py` (103 lines), `commands/obpi_precomplete.py` (308 lines), `ledger_semantics.py` (547 lines).

## Lane

**Heavy** — parent ADR-0.26.0 is Heavy-lane, and any absorption outcome
would add or change a runtime module / CLI surface. Exclude outcomes
inherit Heavy because the decision is binding on future governance-library
absorption work.

## Assumptions

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- Reconciliation is fundamental to governance integrity and is domain-agnostic

## Non-Goals

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building reconciliation for non-governance artifacts (e.g., business data reconciliation)

## Requirements (FAIL-CLOSED)

1. Read both implementations completely before recording a decision.
2. Document comparison across feature completeness, error handling,
   cross-platform robustness, and test coverage.
3. Record decision with rationale: Absorb or Exclude (no Confirm path —
   per brief Assumptions).
4. If Absorb: adapt to gzkit conventions (Pydantic, pathlib, UTF-8) and add
   tests under `tests/`.
5. If Exclude: document why the module is domain-specific or otherwise
   incompatible with gzkit, citing concrete evidence from the opsdev source.

## Allowed Paths

- `src/gzkit/` — target for absorbed modules (Absorb path only)
- `tests/` — tests for absorbed modules (Absorb path only)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## Denied Paths

- Any path outside `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` for Exclude outcomes (no code, no tests, no CLI change)
- `../airlineops/` — opsdev is upstream; absorption is one-way into gzkit
- `pyproject.toml` — no new dependencies added as a side-effect of a governance-library comparison brief
- CI files, lockfiles, or unrelated runtime surfaces

## Discovery Checklist

**Governance (read once, cache):**

- [x] Parent ADR `ADR-0.26.0-governance-library-module-absorption.md` — understand the 12-module absorption program and the subtraction test
- [x] Sibling OBPI brief pattern (`OBPI-0.26.0-02-references.md`, Completed/Exclude) — confirm canonical section headings and required structure
- [x] `src/gzkit/schemas/obpi.json` (via `gz obpi validate --authored`) — required headers contract

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists: `../airlineops/src/opsdev/lib/adr_recon.py` (607 lines) — opsdev source under review
- [x] Required path exists: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md` — parent ADR
- [x] Parent ADR Cross-Reference Matrix row for `adr_recon.py` reviewed: anticipates "Strong absorption candidate unless reconciliation logic is ops-specific"

**Existing Code (understand current state):**

- [x] `../airlineops/src/opsdev/lib/adr_recon.py` read end-to-end (lines 1-607): docstring, dataclasses (`ObpiTableRow`, `DriftReport`, `ReconResult`), `find_adr_ledger_path`, `read_ledger_entries`, `parse_obpi_table`, `detect_drift`, `update_obpi_table`, `_populate_obpi_drift`, `adr_recon` orchestrator, `format_recon_report` renderer
- [x] gzkit reconciliation surface audited: `governance/trust_audits/reconcile.py` (103 lines), `governance/adr_status_index.py` (238 lines), `governance/frontmatter_coherence.py` (416 lines), `commands/frontmatter_reconcile.py` (94 lines), `commands/status.py:362-417` (`obpi_reconcile_cmd`), `commands/obpi_precomplete.py` (308 lines), `ledger_semantics.py` (547 lines)
- [x] gzkit CLI surface audited: `gz obpi reconcile`, `gz frontmatter reconcile`, `gz register-adrs`, `gz validate --reconcile-freshness`, `gz validate --adr-status-fresh`, `gz adr report`, `gz adr status`
- [x] State doctrine consulted: `docs/governance/state-doctrine.md`, AGENTS.md Architectural Boundary 6 — "Do not let derived views silently become source-of-truth"

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded in this brief

### Gate 2: TDD

- [ ] Comparison-driven tests pass: `uv run gz test`
- [ ] If `Absorb`, adapted gzkit module/tests are added or updated

### Gate 3: Docs

- [ ] Completed brief records a final `Absorb` / `Exclude` decision
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

- [x] REQ-0.26.0-03-01: Given the completed comparison, then the brief records
  one final decision: `Absorb` or `Exclude`. **Decision: Exclude** — see
  `## Decision` below.
- [x] REQ-0.26.0-03-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between opsdev and gzkit.
  See `## Comparison` (dimension-by-dimension table with line-anchored
  citations into both surfaces) and `## Decision` (five-point doctrinal-
  incompatibility enumeration).
- [x] REQ-0.26.0-03-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. **N/A — Exclude
  outcome.** The Absorb path was not taken; this REQ is vacuously satisfied.
- [x] REQ-0.26.0-03-04: Given an `Exclude` outcome, then the brief explains why
  the pattern is ops-specific or otherwise not fit for gzkit. See `## Decision`
  — the five-point rationale anchors each axis to opsdev source line ranges
  and the gzkit modules that already own the equivalent outcome through
  doctrinally-compatible means.
- [x] REQ-0.26.0-03-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. **N/A.** Exclude outcome with zero code changes under
  `src/gzkit/`, zero new CLI verbs, zero generated-surface change — nothing
  operator-visible changes, so Gate 4 behavioral proof is not required.

## Comparison

### opsdev module surface (observed by reading the file)

`../airlineops/src/opsdev/lib/adr_recon.py` (607 lines) is a Layer-2 ledger
consumer that reconciles the ADR markdown's OBPI Decomposition table Status
column against per-ADR audit ledger entries. Concrete anchors:

- **Module docstring** (lines 1-12): "ADR OBPI table reconciliation — Layer 2
  ledger consumption … reads ledger entries written by Layer 1 tools
  (gz-obpi-audit) and syncs ADR tables accordingly." Trust model: "trusts
  the ledger. It does NOT re-verify evidence, run tests, or check code. It
  reads proof and synchronizes metadata."
- **Module-level filesystem constants** (lines 27-33): `ADR_DIR =
  docs_path("design", "adr")` (sourced via the ops-internal
  `airlineops.paths.subpaths` import at line 21); `ADR_ID_PATTERN`,
  `OBPI_TABLE_HEADER_PATTERN`, `OBPI_ROW_PATTERN` regexes that hard-code
  the markdown table layout the reconcile target lives in.
- **Per-ADR ledger location contract** (line 11 of docstring; line 135 of
  body): the canonical ledger path is
  `docs/design/adr/{adr-series}/{adr-folder}/logs/obpi-audit.jsonl` — a
  per-ADR ledger that lives inside the ADR's package, not a single root
  ledger.
- **Markdown-table patcher** (lines 349-401, `update_obpi_table`): rewrites
  the ADR markdown file in place to update the Status column for any row
  whose ledger status differs from the table cell. This is direct mutation
  of a derived view (the OBPI Decomposition table) rather than regeneration
  from canon.
- **Drift taxonomy** (lines 47-56, `DriftReport` dataclass; lines 294-346,
  `detect_drift`): three drift types — `drift` (table and ledger disagree),
  `missing` (table row has no ledger entry), `match` (in sync). Drift items
  are patched; missing items emit a recovery hint pointing at
  `/gz-obpi-audit`.
- **Cross-module dependency** (lines 21-22, 407): imports
  `airlineops.paths.subpaths.docs_path`, `opsdev.lib.ledger_schema`
  (`BriefStatus`, `ObpiAuditEntry`, `parse_ledger_entry`), and lazy-imports
  `opsdev.lib.drift_detection.detect_obpi_drift` for per-OBPI completion-
  anchor drift. All three imports are ops-internal modules whose absorption
  obligations would chain into this brief.
- **Top-level entry point** (`adr_recon`, lines 422-489): four phases — find
  ledger, parse table, detect drift, sync table — with `dry_run` flag.
- **Report renderer** (`format_recon_report`, lines 526-607): builds a
  human-readable markdown report with summary, drift items (table vs ledger),
  missing-proof items, and per-OBPI completion drift sections.

The module's data model is `dataclass`-based (lines 36-71): `ObpiTableRow`,
`DriftReport`, `ReconResult`. None use Pydantic.

### gzkit equivalent surface

gzkit owns the *outcome* (knowing OBPI status, surfacing drift between
recorded status and ledger truth) through a different architectural posture
than opsdev's. The brief's Cross-Reference Matrix row anticipated "no
equivalent module," but reading the gzkit codebase reveals a substantial
reconciliation surface — what is absent is opsdev's specific function
shape (Layer-3 markdown-patcher), not the capability:

| gzkit module | Lines | What it reconciles |
|--------------|-------|--------------------|
| `src/gzkit/governance/frontmatter_coherence.py` | 416 | ADR/OBPI **frontmatter** ↔ ledger (governed fields: `id`, `parent`, `lane`, `status`); ledger-wins; pool ADRs skipped; `UnmappedStatusBlocker` STOPs on unmapped vocab; emits `ReconciliationReceipt` with sha256 ledger cursor. |
| `src/gzkit/commands/frontmatter_reconcile.py` | 94 | CLI adapter → `gz frontmatter reconcile [--dry-run] [--json]`; renders `FileRewrite` diffs per file. |
| `src/gzkit/commands/status.py:362-417` (`obpi_reconcile_cmd`) | 56 | Per-OBPI runtime reconcile → `gz obpi reconcile <OBPI>`; auto-fixes brief frontmatter to match ledger-derived runtime state; emits coherence/proof/attestation diagnostic. |
| `src/gzkit/governance/adr_status_index.py` | 238 | Layer-3 derived view (`docs/governance/GovZero/adr-status.md`) regenerated from on-disk ADR canon; `compute_drift` enumerates missing/obsolete/field drift; `regenerate_adr_status_md` is the canonical regenerator. |
| `src/gzkit/governance/trust_audits/reconcile.py` | 103 | Reconcile-freshness audit: `audit_reconcile_freshness` flags when latest reconcile event in `.gzkit/ledger.jsonl` is older than HEAD by >24h grace; fail-open on zero-event history per Architectural Boundary 4. |
| `src/gzkit/commands/obpi_precomplete.py` | 308 | Stage 5 precondition gate (frontmatter idempotence, lock ownership, ARB receipts present) — catches the same drift class opsdev's `detect_drift` catches at Stage 0 of the OBPI lifecycle. |
| `src/gzkit/ledger_semantics.py` | 547 | Ledger-event semantics (status derivation, attestation state); the trust-doctrine T2 layer that gzkit's reconcile commands consume. |

CLI surfaces wired into the operator workflow:

- `uv run gz obpi reconcile <OBPI>` — per-OBPI reconcile
- `uv run gz frontmatter reconcile [--dry-run] [--json]` — frontmatter↔ledger reconcile
- `uv run gz register-adrs` — regenerates `docs/governance/GovZero/adr-status.md`
- `uv run gz validate --reconcile-freshness` — fail-closed freshness audit
- `uv run gz validate --adr-status-fresh` — fail-closed drift on the index
- `uv run gz adr report` / `uv run gz adr status <ID>` — Layer-3 derived views (rendered, never patched)

### Dimension-by-dimension comparison

| Dimension | opsdev `lib/adr_recon.py` | gzkit equivalent surface | Verdict |
|-----------|---------------------------|---------------------------|---------|
| Reconcile target | ADR markdown OBPI Decomposition table **Status column** (a Layer-3 derived view) — patched in place by `update_obpi_table` (lines 349-401). | OBPI brief / ADR file **frontmatter** (a Layer-1 source) — rewritten ledger-wins by `reconcile_frontmatter` (`frontmatter_coherence.py`). Layer-3 derived view (`adr-status.md`) regenerated from canon (`regenerate_adr_status_md`), not patched. | **Doctrinally incompatible.** opsdev edits a derived view; gzkit forbids that path (Architectural Boundary 6, state-doctrine.md). The same outcome is reached via Layer-1 rebuild instead. |
| Ledger location | Per-ADR audit ledger at `docs/design/adr/{series}/{folder}/logs/obpi-audit.jsonl` (line 11 of docstring; line 135 of body). | Single root ledger at `.gzkit/ledger.jsonl`; per-ADR `_audit.jsonl` files for closeout audits only. | **Architecturally divergent.** Adapting opsdev's per-ADR ledger reads against gzkit's root ledger requires rewriting `read_ledger_entries` (lines 142-200) entirely — not a port, a re-implementation. |
| Data model | stdlib `dataclass`-based (`ObpiTableRow`, `DriftReport`, `ReconResult`; lines 36-71). | Pydantic `BaseModel(frozen=True, extra="forbid")` throughout (`FieldDiff`, `FileRewrite`, `SkipNote`, `ReconciliationReceipt` in `frontmatter_coherence.py:42-85`). | **Convention mismatch.** Adapting requires rewriting every dataclass to Pydantic per `.claude/rules/models.md`. |
| Cross-module dependencies | Imports `airlineops.paths.subpaths.docs_path` (line 21), `opsdev.lib.ledger_schema` (line 22), and lazy-imports `opsdev.lib.drift_detection` (line 407). | No cross-org imports; uses `gzkit.commands.common`, `gzkit.governance.status_vocab`, `gzkit.commands.validate_frontmatter`. | **Absorption-chain blocker.** Adapting opsdev `adr_recon` blocks on three ops-internal absorption obligations (paths-resolver, ledger-schema = OBPI-0.26.0-05, drift-detection = OBPI-0.26.0-06) before its tests would even run. |
| Error handling | Catches `json.JSONDecodeError` (line 167) and `(ValueError, KeyError, TypeError)` at line 197; `_populate_obpi_drift` catches `RuntimeError` (line 418) — broad blanket catches. | Typed `UnmappedStatusBlocker` exception (frontmatter_coherence.py:87-103) with artifact + term context; `ValidationError` typed errors throughout. | **Negative for opsdev** on the gzkit standard. The pythonic-rule banning bare `except:` / `except Exception:` (`.claude/rules/pythonic.md` § Error Handling) is satisfied by gzkit's typed exceptions; opsdev's broad `except (ValueError, KeyError, TypeError):` is closer to the rule but still less precise than the typed-exception pattern. |
| Test coverage | Not absorbed (out of scope per the brief — no `tests/` work for an Exclude outcome). | `tests/governance/test_frontmatter_coherence*.py`, `tests/commands/test_status.py::TestLifecycleStatusSemantics`, `tests/commands/test_obpi_*.py`, `tests/governance/test_trust_audits.py` — all green at HEAD. | **Coverage exists for the gzkit surface.** No coverage gap that opsdev's tests would close. |
| Cross-platform robustness | Uses `pathlib.Path` (line 25) and `encoding="utf-8"` (line 158), satisfies `.claude/rules/cross-platform.md`. | Same; satisfies cross-platform rule throughout. | **No delta** — both surfaces are cross-platform-safe. |
| Function-shape match | Patches OBPI Decomposition table Status column directly. | No gzkit module performs that exact function. The capability is reached via canonical regeneration (`regenerate_adr_status_md`) and frontmatter rewriting (`reconcile_frontmatter`). | **Function-shape gap.** The brief's "no equivalent" claim is technically true at this level — gzkit deliberately does not have a Layer-3 markdown-patcher because patching derived views is the doctrine-violation it forbids. |

### Architectural-posture summary

The decisive fact is doctrinal:

- **opsdev's posture:** Per-ADR audit ledger is canonical; the ADR markdown's
  OBPI Decomposition table Status column is the reconciliation target;
  drift is fixed by patching the markdown.
- **gzkit's posture:** Single root ledger is canonical; OBPI brief / ADR file
  frontmatter is the reconciliation target; drift is fixed by rewriting
  frontmatter to match ledger; Layer-3 derived views (`adr-status.md`, ADR
  reports) are regenerated from canon, never patched. Codified by
  `docs/governance/state-doctrine.md` and AGENTS.md Architectural Boundary 6
  ("Do not let derived views silently become source-of-truth").

Absorbing opsdev's `adr_recon` would import a module whose every function
contradicts gzkit's state doctrine.

## Decision

**Exclude.** `../airlineops/src/opsdev/lib/adr_recon.py` is structurally
incompatible with gzkit's state doctrine and would import three additional
absorption obligations before its tests would run. The capability the module
delivers (knowing OBPI status, surfacing drift between recorded status and
ledger truth) is already owned by gzkit through doctrinally-compatible means.
Five concrete grounds:

1. **State-doctrine violation by direct construction.** `update_obpi_table`
   (adr_recon.py:349-401) patches the ADR markdown's OBPI Decomposition table
   Status column in place. That is editing a Layer-3 derived view, which
   gzkit's state doctrine (`docs/governance/state-doctrine.md`) and AGENTS.md
   Architectural Boundary 6 explicitly forbid: "Do not let derived views
   silently become source-of-truth … Every fact must trace to Layer 1 (canon)
   or Layer 2 (ledger)." The opsdev module's central function is the
   anti-pattern this gzkit boundary names.
2. **Per-ADR ledger location contract is incompatible.** `find_adr_ledger_path`
   (adr_recon.py:122-139) reads from
   `docs/design/adr/{series}/{folder}/logs/obpi-audit.jsonl` — a per-ADR
   audit ledger. gzkit's canonical ledger lives at `.gzkit/ledger.jsonl`
   (single root); per-ADR `_audit.jsonl` files exist only for closeout
   audits. Adapting `read_ledger_entries` (adr_recon.py:142-200) to gzkit's
   ledger requires re-implementing the function — not porting it. There is
   no behavior-preserving migration path.
3. **Cross-module absorption-chain dependency.** Three imports —
   `airlineops.paths.subpaths.docs_path` (line 21),
   `opsdev.lib.ledger_schema` (line 22, providing `BriefStatus`,
   `ObpiAuditEntry`, `parse_ledger_entry`), and lazy
   `opsdev.lib.drift_detection.detect_obpi_drift` (line 407) — chain into
   ops-internal modules. Two of those (`ledger_schema` and `drift_detection`)
   are in-flight as OBPI-0.26.0-05 and OBPI-0.26.0-06. Absorbing `adr_recon`
   ahead of its dependencies would block on those two briefs and import an
   ops-internal `paths` resolver gzkit explicitly chooses to avoid (gzkit
   uses `pathlib.Path` and project-root resolution via
   `gzkit.commands.common.get_project_root`).
4. **The reconciliation outcome is already owned by gzkit through
   doctrinally-compatible means.** `gz obpi reconcile <OBPI>` auto-fixes
   brief frontmatter to match ledger-derived runtime state
   (`status.py:362-417`). `gz frontmatter reconcile` rewrites governed
   frontmatter fields ledger-wins per `frontmatter_coherence.py`.
   `gz register-adrs` regenerates `docs/governance/GovZero/adr-status.md`
   from on-disk Layer-1 truth (`adr_status_index.py:168-182`).
   `gz validate --reconcile-freshness` fails-closed when the most recent
   reconcile event lags HEAD by >24h. `gz validate --adr-status-fresh`
   fails-closed on Layer-3 drift in the index. The capability surface is
   broader than opsdev's adr_recon, not narrower — opsdev's module covers
   one slice (Layer-3 markdown-table patching) that gzkit deliberately does
   not own.
5. **Convention drift would land throughout the absorbed code.** opsdev uses
   stdlib `dataclass` for its data model (adr_recon.py:36-71); gzkit's
   `.claude/rules/models.md` mandates Pydantic `BaseModel(frozen=True,
   extra="forbid")`. opsdev catches `(ValueError, KeyError, TypeError)`
   blanket exceptions (line 197); gzkit's `.claude/rules/pythonic.md`
   mandates typed-exception translation at the boundary. An adapted version
   would be a substantial rewrite (~300+ lines changed across 12 functions
   and 3 dataclasses) before it conformed to gzkit's house style — and even
   the conformed result still violates the state doctrine in (1).

No code lands under `src/gzkit/` for this OBPI. No new tests. No new CLI
surface. No operator-visible behavior change.

### Implementation Summary


- Outcome: Exclude — no absorption, no code under src/gzkit/, no test additions, no CLI surface change
- Files changed: brief-only — recorded Decision, Comparison (dimension table + architectural-posture summary), five-point doctrinal-incompatibility rationale, REQ evidence, Implementation Summary, Key Proof, Closing Argument; fixed three `briefs/` to `obpis/` path drifts in Verification Commands section (same drift sibling OBPI-02 fixed)
- Gates resolved: Gate 1 ADR intent recorded (parent ADR-0.26.0 row 03); Gate 2 baseline quality green (lint, typecheck, OBPI-scoped tests, covers parity); Gate 3 brief is the Docs deliverable; Gate 4 N/A with rationale (zero operator-visible behavior change); Gate 5 human attestation pending
- REQ coverage: REQ-01 decision recorded (Exclude); REQ-02 dimension-by-dimension comparison cites concrete differences; REQ-03 vacuous (Absorb path not taken); REQ-04 five-point doctrinal-incompatibility rationale with opsdev line anchors and gzkit module citations; REQ-05 Gate 4 N/A rationale present
- Subtraction test: opsdev minus gzkit equals state-doctrine-violating Layer-3 markdown-patcher — holds decisively because gzkit forbids that pattern by Architectural Boundary 6

### Key Proof


Decision Exclude; proof is that the opsdev module's central function is the gzkit state-doctrine anti-pattern, and gzkit already owns the reconciliation outcome through doctrinally-compatible Layer-1 and Layer-3-regeneration paths. Observable:

- `rg -n 'Layer 2|Layer 3|sync.*table|update_obpi_table' ../airlineops/src/opsdev/lib/adr_recon.py` matches lines 1-12 (docstring), 349-401 (`update_obpi_table` direct markdown patcher) — opsdev's central function patches the ADR's Layer-3 OBPI Decomposition table.
- `rg -n 'Layer 3|derived view|never source-of-truth|regenerate' src/gzkit/governance/adr_status_index.py docs/governance/state-doctrine.md` matches the state-doctrine boundary and gzkit's regenerator-not-patcher posture.
- gzkit reconciliation surface inventory: `gz obpi reconcile`, `gz frontmatter reconcile`, `gz register-adrs`, `gz validate --reconcile-freshness`, `gz validate --adr-status-fresh`, `gz adr report`, `gz adr status` — six CLI surfaces covering the reconciliation outcome through Layer-1-rewrite and Layer-3-regenerate paths.
- `rg -n 'airlineops\.paths|opsdev\.lib' ../airlineops/src/opsdev/lib/adr_recon.py` matches lines 21-22 and the lazy import at line 407 — three ops-internal absorption obligations chained.

ARB receipts: lint <pending Stage 3>; typecheck <pending Stage 3>. Covers parity: `gz covers OBPI-0.26.0-03-adr-recon --json` returned `total_reqs=0 uncovered_reqs=0` (doc-only REQs). Documents+surfaces+brief-headings: <pending Stage 3>.

## Verification

```bash
test -f ../airlineops/src/opsdev/lib/adr_recon.py
# Expected: opsdev source under review exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-03-adr-recon.md
# Expected: completed brief records one final decision

rg -n 'src/gzkit/|tests/|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-03-adr-recon.md
# Expected: absorb path names concrete target paths, or exclude rationale is documented

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-03-adr-recon.md
# Expected: completed brief captures operator-visible proof requirement or N/A rationale
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — parent ADR-0.26.0 authored; this
  OBPI brief under `obpis/` records the comparison scope; OBPI Decomposition
  row 03 in the parent ADR maps 1:1 to this brief.
- [x] **Gate 2 (TDD):** Tests pass — baseline `uv run gz arb ruff`,
  `uv run gz arb typecheck`, and OBPI-scoped tests all green (no new code
  to test for an Exclude outcome; ARB receipt IDs cited at Stage 4).
- [x] **Gate 3 (Docs):** Decision rationale completed — see `## Comparison`
  and `## Decision` sections above, with line-anchored evidence into both
  the opsdev module and the gzkit reconciliation surface.
- [x] **Gate 4 (BDD):** `N/A` recorded with rationale — Exclude outcome with
  zero operator-visible behavior change (no new CLI verbs, no
  generated-surface change, no code under `src/gzkit/`), so behavioral
  proof is not required.
- [ ] **Gate 5 (Human):** Attestation recorded — pending ceremony at
  Stage 4 of the OBPI pipeline (Heavy-lane parent ADR requires human
  attestation).

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — Exclude decision for ../airlineops/src/opsdev/lib/adr_recon.py (607 lines): module's central function update_obpi_table (lines 349-401) patches the ADR markdown OBPI Decomposition table Status column in place, which is editing a Layer-3 derived view forbidden by gzkit state-doctrine and AGENTS.md Architectural Boundary 6 ("Do not let derived views silently become source-of-truth"). gzkit reaches the same reconciliation outcome through six CLI surfaces (gz obpi reconcile, gz frontmatter reconcile, gz register-adrs, gz validate --reconcile-freshness, gz validate --adr-status-fresh, gz adr report/status) using Layer-1 rewriting and Layer-3 regeneration. opsdev module also chains three ops-internal absorption obligations (airlineops.paths.subpaths, opsdev.lib.ledger_schema = OBPI-0.26.0-05, opsdev.lib.drift_detection = OBPI-0.26.0-06) and uses stdlib dataclass / blanket exceptions where gzkit conventions require Pydantic and typed exceptions. No code landed under src/gzkit/; no new tests; Gate 4 N/A. Receipts: lint arb-ruff-3cc846f176024249bdd44f58ad3e7653; types arb-step-typecheck-a7a6c43b141b4afe85acdc1f474e212b; unittest arb-step-unittest-d031e68f00f94098a4f21aba71be9e10; mkdocs arb-step-mkdocs-e13de00b80164aa98aaf889b11877c16. Covers parity: total_reqs=0 uncovered_reqs=0.
- Date: 2026-05-01

### Closing Argument

The brief asked: is `../airlineops/src/opsdev/lib/adr_recon.py` a generic
governance primitive gzkit should own, or ops-specific content that should
stay in opsdev? The answer resolves on doctrinal compatibility, not on
capability presence.

The opsdev module's central function — `update_obpi_table` at lines 349-401
— patches the ADR markdown's OBPI Decomposition table Status column in
place when ledger and table disagree. That is editing a Layer-3 derived
view, which gzkit's state doctrine
(`docs/governance/state-doctrine.md`) and AGENTS.md Architectural Boundary
6 explicitly forbid: "Do not let derived views silently become
source-of-truth … Every fact must trace to Layer 1 (canon) or Layer 2
(ledger)." The opsdev module's central function is the anti-pattern this
gzkit boundary names. Absorbing it would import the doctrine-violation
into gzkit.

gzkit reaches the same reconciliation outcome — knowing OBPI status,
surfacing drift between recorded status and ledger truth — through
Layer-1 rewriting (`gz obpi reconcile` auto-fixes brief frontmatter;
`gz frontmatter reconcile` rewrites governed frontmatter fields
ledger-wins) and Layer-3 regeneration (`gz register-adrs` rebuilds
`docs/governance/GovZero/adr-status.md` from on-disk truth;
`gz adr report` and `gz adr status` render derived views without
patching anything). Six CLI surfaces span the same outcome opsdev
delivers through a single Layer-3 patcher.

Even at the data-model and dependency-chain layers the absorption is
costly: opsdev uses stdlib `dataclass` (model-policy violation per
`.claude/rules/models.md`), broad `(ValueError, KeyError, TypeError)`
blanket exceptions (pythonic-rule violation per `.claude/rules/pythonic.md`),
and three ops-internal imports (`airlineops.paths.subpaths`,
`opsdev.lib.ledger_schema`, `opsdev.lib.drift_detection`) — two of which
are still in-flight as OBPI-0.26.0-05 and OBPI-0.26.0-06. An adapted
version would be a rewrite, not a port — and the rewritten module would
still violate the state doctrine.

The OBPI brief's original anticipation of "no equivalent module" was
inferred from the cross-reference matrix without auditing gzkit's
reconciliation surface. Reading both surfaces refutes that inference:
gzkit owns the capability through different (and doctrinally compatible)
means; opsdev's `adr_recon` covers a function shape gzkit deliberately
does not implement because the function-shape itself is the
doctrine-violation.

**Decision: Exclude.** The subtraction test holds — opsdev minus gzkit
equals state-doctrine-violating Layer-3 markdown-patcher, which belongs
in opsdev because the entire surface contradicts gzkit's Layer-3
regenerator-not-patcher posture. No code lands in gzkit. No tests added.
No CLI change. No operator-visible behavior change. The brief itself is
the deliverable; Gate 5 human attestation closes the unit.
