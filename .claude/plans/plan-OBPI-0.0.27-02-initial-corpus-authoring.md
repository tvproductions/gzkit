# Plan — OBPI-0.0.27-02-initial-corpus-authoring

**Brief:** `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/obpis/OBPI-0.0.27-02-initial-corpus-authoring.md`
**Parent ADR:** ADR-0.0.27 (foundation, heavy)
**Lane:** Heavy (data-contract artifact + Pydantic model + JSON Schema + six pool stubs).
**Kind:** foundation — brief-level Gate 5 attestation required (TTY + `ATTEST`).
**Prerequisite:** OBPI-0.0.27-01 (`Completed`) — `.gzkit/rules/complexity-doctrine.md` (rule v0.1.0) is canon.

## Context

OBPI-0.0.27-02 lands the empirical anchor of the complexity-doctrine cluster: a pinned 12-15-project corpus across ten archetypal cells, the immutable Pydantic model that types it, the JSON Schema mirror that fail-closes drift, and the six pool stubs the citation graph forward-references. The **defining constraint is operator-witnessed nomination** — agent-supplied lists from training memory are an explicit anti-pattern (`.gzkit/rules/complexity-doctrine.md` § Corpus Anti-Patterns #6). Per-cell projects are locked in `.gzkit/handoffs/2026-04-25-complexity-doctrine-cluster.md` (Django, Starlette, httpx, click, attrs, CPython subsets, hypothesis, rich, mypy, flit), but SHAs, per-project path filters, CPython module enumeration, craftsmanship narratives, and practitioner-reputation citations are NOT locked; those are operator-audit material.

Two corollary constraints govern execution:

1. **No SHA, citation, or path filter may be pattern-matched from training memory.** SHAs are pinned via `gh api repos/<owner>/<repo>/commits/<ref>`; citations name specific PEPs / books / talks by number / title or are omitted. Anything else is `Fabrication` shape per `.claude/rules/agent-failure-modes.md`.
2. **The operator-slate audit (Step 3 below) is the load-bearing checkpoint.** No subagent may proceed past Step 3 without operator confirmation in the session transcript. The slate-confirmation turn drafts the evidence the Stage 4 ceremony attests; Stage 4 walkthrough re-attests on the final corpus, but does not re-litigate per-row craftsmanship.

## Files

### Created (in allowed paths)

| Path | Purpose |
|---|---|
| `src/gzkit/models/exemplar.py` | `ExemplarProject` Pydantic model (`frozen=True, extra="forbid"`), `VacantCell` model, top-level `ExemplarCorpus` wrapper, `load_corpus(Path)` loader |
| `src/gzkit/schemas/exemplar_corpus.json` | JSON Schema mirror (Draft 2020-12) |
| `data/exemplar_corpus.json` | Pinned corpus content |
| `tests/models/test_exemplar.py` | REQ-derived model tests (REQ-03, -07, -08) |
| `tests/governance/test_exemplar_corpus.py` | REQ-derived corpus-content + pool-stub tests (REQ-01, -02, -04, -05, -06, -09) |
| `docs/design/adr/pool/ADR-pool.attestation-quality-measurement.md` | Pool stub |
| `docs/design/adr/pool/ADR-pool.doctrine-amendment-protocol.md` | Pool stub |
| `docs/design/adr/pool/ADR-pool.complexity-doctrine-validate-suite.md` | Pool stub |
| `docs/design/adr/pool/ADR-pool.canon-pillar-codification.md` | Pool stub |
| `docs/design/adr/pool/ADR-pool.complexity-doctrine-meets-chore-system.md` | Pool stub |
| `docs/design/adr/pool/ADR-pool.complexity-guide-obpi-authoring-integration.md` | Pool stub |

### Modified (in allowed paths)

| Path | Change |
|---|---|
| `src/gzkit/commands/validate_cmd.py` | Extend `_validate_manifest_documents` to load `data/exemplar_corpus.json` through `ExemplarCorpus` and surface `ValidationError` records on drift (REQ-07). No new opt-in scope; folds into `--documents`. |
| `data/behave_coverage_waivers.json` | Register OBPI-0.0.27-02 waiver (data-contract-only OBPI; CLI exposure is OBPI-03). |
| `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/obpis/OBPI-0.0.27-02-initial-corpus-authoring.md` | Brief evidence sections (REQ rejection records per REQ-04/05; Implementation Summary; Key Proof; Closing Argument). Allowed by brief allowlist line 38. |

### Read-only references (not edited)

- `.gzkit/rules/complexity-doctrine.md` — selection criteria (rule v0.1.0)
- `.gzkit/rules/models.md` — Pydantic immutable model contract
- `.gzkit/handoffs/2026-04-25-complexity-doctrine-cluster.md` — per-cell project lock-in
- `src/gzkit/models/security_surfaces.py` — pattern reference for `frozen=True, extra="forbid"` model + `TypeAdapter` loader
- `tests/models/test_security_surface_entry.py` — pattern reference for REQ-decorated tests
- `docs/design/adr/pool/ADR-pool.adr-amendment-tracking.md` — pool ADR canonical shape

## Steps

Implementer subagents execute Steps 1, 2, 6, 7, 8, 9 and 10. **Steps 3, 4, and 5 are operator-gated and run in the main session, not under subagents.** This is non-negotiable per `.gzkit/rules/complexity-doctrine.md` Anti-Pattern #6.

### Step 1 — TDD: Author Pydantic-model tests then `ExemplarProject` model + JSON Schema

**Allowed paths:** `src/gzkit/models/exemplar.py`, `src/gzkit/schemas/exemplar_corpus.json`, `tests/models/test_exemplar.py`.

**REQs covered:** REQ-03 (model uses `ConfigDict(frozen=True, extra="forbid")`, no `Optional`/`List`, no implicit defaults), REQ-07 (JSON Schema mirror), REQ-08 (model tests with `@covers`), REQ-09 (path-filter shape at module-subset level), REQ-10 (TDD; `tempfile`-backed; no network).

**RED:** Write `tests/models/test_exemplar.py` first. Decorate every test with `@covers(REQ-0.0.27-02-NN)`. Cover at minimum:

- `model_config.frozen is True` and `model_config["extra"] == "forbid"` on every model — REQ-0.0.27-02-07.
- Mutation of any field on a constructed `ExemplarProject` raises `ValidationError` — REQ-0.0.27-02-07.
- Construction with non-SHA `commit_sha` (branch name `"main"`, tag `"v1.0"`, short hash, 39-char hex, 41-char hex, non-hex 40-char) is rejected — REQ-0.0.27-02-02.
- Construction with empty `included_paths`, missing `excluded_paths_with_rationale`, or empty `path_filter_rationale` is rejected — REQ-0.0.27-02-03.
- Construction with extra keys is rejected — REQ-0.0.27-02-07.
- Construction with `archetypal_cell` outside `1..10` is rejected — implicit acceptance criterion of REQ-04.
- Construction with `pure_python_loc_ratio` outside `0.0..1.0` is rejected — schema-hardening; supports REQ-04 criterion 4.
- A `VacantCell` requires both `archetypal_cell: int` and `vacancy_rationale: str` (non-empty) — REQ-0.0.27-02-04.
- The top-level `ExemplarCorpus` wrapper has `schema_version: str`, `corpus_revision: int`, `projects: tuple[ExemplarProject, ...]`, `vacant_cells: tuple[VacantCell, ...]` — REQ-0.0.27-02-08 (schema-mirror parity).
- `load_corpus(tempfile_path)` returns frozen models — REQ-0.0.27-02-01, REQ-0.0.27-02-07.
- The JSON Schema at `src/gzkit/schemas/exemplar_corpus.json` declares the same `required` fields and the same `commit_sha` `pattern` (`^[0-9a-f]{40}$`) as the Pydantic model — REQ-0.0.27-02-08.

**GREEN:** Author `src/gzkit/models/exemplar.py` modeling:

```python
class ExemplarProject(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    canonical_url: HttpUrl
    commit_sha: str  # validated to ^[0-9a-f]{40}$
    archetypal_cell: int  # validated to 1..10
    cell_label: str
    included_paths: tuple[str, ...]
    excluded_paths_with_rationale: tuple[ExcludedPath, ...]
    path_filter_rationale: str
    longevity_evidence: str
    maintenance_health_evidence: str
    practitioner_reputation_citation: str
    pure_python_loc_ratio: float  # 0.0..1.0
    craftsmanship_signal_narrative: str
    project_doctrine_fitness_narrative: str
```

`ExcludedPath` carries `glob: str, exclusion_rationale: str`. `VacantCell` and `ExemplarCorpus` follow the same `frozen=True, extra="forbid"` pattern. `load_corpus(path: Path) -> ExemplarCorpus` mirrors the `load_registry` shape in `security_surfaces.py:73-76`.

Author `src/gzkit/schemas/exemplar_corpus.json` mirroring exactly the Pydantic field set, types, `required` list, and `commit_sha` pattern. Use the security-surfaces schema (`src/gzkit/schemas/security_surfaces.json`) as the structural template.

**REFACTOR:** Once GREEN, factor any duplicated validation helpers (e.g. SHA pattern compile) to module-private constants. Do not introduce optional fields; doctrine forbids implicit defaults (REQ-03).

### Step 2 — Wire schema + Pydantic validation into `gz validate --documents`

**Allowed paths:** `src/gzkit/commands/validate_cmd.py`, `tests/models/test_exemplar.py` (or new fixture file under same dir).

**REQ covered:** REQ-07.

Extend `_validate_manifest_documents(project_root)` (`src/gzkit/commands/validate_cmd.py:840`) to also load `data/exemplar_corpus.json` if present and call `ExemplarCorpus.model_validate(json.loads(...))`. Surface any `pydantic.ValidationError` as `ValidationError` records in the same shape the existing function returns. This deliberately folds into the `documents` scope per the brief's REQ-07 wording — no new opt-in flag.

Add a unit test that constructs a tempdir with a malformed `data/exemplar_corpus.json` (e.g. missing required field, non-SHA commit field) and asserts `_validate_manifest_documents` returns at least one `ValidationError` row — `@covers(REQ-0.0.27-02-08)`. The test uses `tempfile.TemporaryDirectory()` per `.gzkit/rules/tests.md`.

### Step 3 — **OPERATOR GATE: Slate presentation + audit**

**This step is run in the main session by the operator and the agent in dialogue.** No subagent dispatch. No file edits.

The agent presents a markdown table in chat — **never raw JSON** — with one row per nomination across all ten cells. Per Operator Economy of Effort, the operator reviews human-readable prose, not machine-readable artifacts. Table columns:

| Cell | Project | URL | SHA (to-pin) | Included paths (proposed) | Excluded paths + rationale (proposed) | Pure-Py LOC % | Practitioner citation (specific) | Craftsmanship signal | Project-doctrine fitness |

Concurrent with the table, the agent presents these forced choices for operator decision:

1. **Vacant-cell representation in JSON.** Two reasonable shapes — pick one:
   (A) Top-level `{schema_version, corpus_revision, projects: [...], vacant_cells: [{archetypal_cell, vacancy_rationale}]}` (separate lists; cleanest schema)
   (B) Single `entries: [...]` discriminated by `kind: "project" | "vacant"` (one list; harder to type in Pydantic but symmetric)
   Recommendation: A (cleaner Pydantic + cleaner schema). Operator confirms.
2. **CPython module-subset shape.** Cell 6 is "selected CPython modules" (handoff names pathlib, dataclasses, functools, contextlib). Two reasonable shapes — pick one:
   (A) One `ExemplarProject` row whose `included_paths` enumerates `Lib/pathlib.py`, `Lib/dataclasses.py`, `Lib/functools.py`, `Lib/contextlib.py`. Counts as one entry.
   (B) One `ExemplarProject` row per stdlib module (4 entries from cell 6).
   Recommendation: A — keeps cell 6 to one craftsmanship-signal narrative, leaves room for 12-15 corpus entries across more cells.
3. **Corpus size.** Brief target is 12-15. Ten cells locked, cell 6 collapsed = 10 base entries. Surface candidates for the +2 to +5 second-candidate slots: rich + textual (cell 8 second), pip + flit (cell 10 second), httpx + requests (cell 3 — but requests is older and may fail maintenance criterion; flag for operator), Django + Flask (cell 1 second — Flask-2.x active). Operator picks.
4. **Per-cell rejection records.** REQ-05 forbids pytest (project-doctrine-fitness; demerit-lesson canon) and Pydantic (Rust-core; pure-Python predominance fails). Brief evidence must record both rejections explicitly. Operator confirms wording.

The operator's confirmation is captured verbatim in the agent's session record. **No SHA pinning, no JSON authoring, no test content drafting until the operator has confirmed the slate, the schema-shape questions (#1, #2), the corpus-size choice (#3), and the rejection records (#4).** A `BLOCKED` from this step releases the OBPI lock and creates a session handoff per `gz-obpi-pipeline` § Error Recovery.

### Step 4 — SHA-pinning research (operator-confirmed slate only)

**This step runs in the main session.** Allowed tool: `Bash` (for `gh api`). No file edits.

For each operator-confirmed project, pin the SHA via:

```bash
gh api repos/<owner>/<repo>/commits/<ref> --jq '.sha'
gh api repos/<owner>/<repo>/releases/latest --jq '.published_at'
```

`<ref>` defaults to `HEAD` of `main`/`master` as of the run date — operator may override per project (e.g. last release tag). Maintenance-health evidence is the latest release date returned. Each pinned SHA + date is presented in a follow-up table for the operator to confirm before Step 5 runs.

If `gh api` returns a 404 / network error, **stop the step**. Do not pattern-match a SHA. Surface to operator and treat as `BLOCKED`.

### Step 5 — Author `data/exemplar_corpus.json`

**This step runs as a single Edit/Write in the main session, not under a subagent.** The corpus content is operator-witnessed; sub-agent dispatch would re-introduce the agent-only-authored anti-pattern.

Write `data/exemplar_corpus.json` containing:

```json
{
  "schema_version": "1.0.0",
  "corpus_revision": 1,
  "projects": [ ... operator-confirmed slate ... ],
  "vacant_cells": [ ... operator-confirmed vacancies ... ]
}
```

Each `projects` entry carries every field from Step 1's `ExemplarProject` shape. Path filters are at module-subset level per REQ-09; each excluded path carries an `exclusion_rationale` (e.g. Django's `db/models/sql/compiler.py` excluded with rationale "ORM query compiler — irreducible algorithmic complexity per ADR-0.0.27 anti-pattern; would pull metric distributions toward leniency"). NEVER include the operator's personal email anywhere in this file (REQ-11).

Run `uv run gz arb step --name unittest -- uv run -m unittest tests.models.test_exemplar tests.governance.test_exemplar_corpus -v` after authoring; the parity-checking test from Step 2 must pass.

### Step 6 — Author governance test for corpus content

**Allowed paths:** `tests/governance/test_exemplar_corpus.py`.

**REQs covered:** REQ-01 (12-15 projects, ≥8 of 10 cells), REQ-02 (every entry has every field), REQ-04 (every entry passes seven selection criteria), REQ-05 (pytest + Pydantic absent), REQ-06 (six pool-stub files exist), REQ-08 (tests decorated with `@covers`), REQ-09 (path filters explicit, no whole-project), REQ-10 (`tempfile`-backed; no network).

Tests (each `@covers`-decorated):

- `assert_corpus_size_in_target_band` — `12 <= len(projects) <= 15` (REQ-0.0.27-02-01).
- `assert_archetypal_cell_coverage` — `len({p.archetypal_cell for p in projects} | {v.archetypal_cell for v in vacant_cells}) == 10` AND `len({p.archetypal_cell for p in projects}) >= 8` (REQ-0.0.27-02-04).
- `assert_no_doctrine_violating_projects` — `"pytest" not in {p.name.lower() for p in projects}` AND `"pydantic" not in {p.name.lower() for p in projects}` (REQ-0.0.27-02-05).
- `assert_every_project_has_path_filters` — every entry has at least one `included_paths` element AND a non-empty `path_filter_rationale` (REQ-0.0.27-02-03, REQ-0.0.27-02-09).
- `assert_no_whole_project_inclusion` — every `included_paths` glob is module-subset, never `**` or `*` alone (REQ-0.0.27-02-09).
- `assert_pinned_shas` — every `commit_sha` matches `^[0-9a-f]{40}$` (REQ-0.0.27-02-02).
- `assert_pool_stubs_exist` — all six pool-stub paths from the brief allowlist exist as files with frontmatter `id: ADR-pool.<slug>` and a body section citing `OBPI-0.0.27-02` as booking event (REQ-0.0.27-02-06).
- `assert_no_operator_email_in_corpus` — load corpus as text, assert no `@gmail.com` / no plaintext personal-email shape (REQ-11 hardening, defense-in-depth).

The test loads `Path("data/exemplar_corpus.json")` directly (not via `tempfile`) — the canonical artifact under test must be the on-disk one. `tempfile` use is for *fixture data* in negative cases (e.g. malformed corpus rejection in Step 1).

### Step 7 — Author six pool-stub ADRs

**Allowed paths:** the six `docs/design/adr/pool/ADR-pool.<slug>.md` files in the brief allowlist.

**REQ covered:** REQ-06.

Each pool stub follows the canonical pool-ADR shape (mirror of `docs/design/adr/pool/ADR-pool.adr-amendment-tracking.md`, lines 1-22):

```markdown
---
id: ADR-pool.<slug>
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: ADR-0.0.27
---

# ADR-pool.<title>: <Title>

## Status

Pool

## Date

<today>

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

<one-paragraph rationale lifted from ADR-0.0.27 § Decision "Six pool stubs"
section, ending with: "Booked at OBPI-0.0.27-02 as a forward-reference in
the citation graph.">
```

The booking-event citation is the load-bearing line — the Step 6 governance test asserts every stub mentions `OBPI-0.0.27-02`.

### Step 8 — Register Gate 4 BDD waiver

**Allowed path:** `data/behave_coverage_waivers.json` (this file is in the brief allowlist via the parent-ADR repo-wide read; if waiver registration is rejected as out-of-allowlist, surface to operator before bypassing).

Wait — the brief allowlist (lines 28-38) does not include `data/behave_coverage_waivers.json`. The brief Gate 4 line says *"BDD waiver registered: data-contract-only OBPI; CLI exposure is OBPI-03"* — this is a process expectation but the file is not in the allowlist.

**Decision:** before editing `data/behave_coverage_waivers.json`, surface to operator. Two reasonable routes:
(A) Treat as in-scope per Gate 4 expectation; edit and commit.
(B) Treat as out-of-allowlist; file a small follow-up GHI noting the allowlist gap and add the waiver under that GHI's `fix(...)` route.

Recommendation: (A) — the waiver is mechanically required by Gate 4 and the brief explicitly names it. Surface as a routing fact, then proceed with (A) on operator confirmation.

### Step 9 — Brief evidence sections

**Allowed path:** `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/obpis/OBPI-0.0.27-02-initial-corpus-authoring.md`.

Author the per-section evidence (H3 per `.claude/rules/brief-heading-conventions.md`):

- `### Implementation Summary` — files created/modified, REQ→test map, ARB receipt IDs.
- `### Key Proof` — concrete CLI invocation + observed output (e.g. `uv run gz validate --documents` exit 0; `uv run -m unittest tests.governance.test_exemplar_corpus -v` summary line).
- `### Closing Argument` — one paragraph: why operator-witnessed nominations beat agent-supplied lists; how per-project path-filters close the corpus-contamination class; why pool-stub forward-references are the right citation-graph shape.
- **Rejection records** — within `### Implementation Summary` or a sibling H3 evidence block, name pytest and Pydantic as candidates considered and rejected, citing the criteria (REQ-04, REQ-05). This satisfies the brief's "rejection recorded in brief evidence, not silently filtered" wording.

### Step 10 — Verification + ARB-receipted attestation evidence

Run, in order, capturing receipt IDs for the Stage 4 evidence table:

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.models.test_exemplar tests.governance.test_exemplar_corpus -v
uv run gz arb step --name unittest -- uv run -m unittest -q   # full-suite regression check
uv run gz validate --documents
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz covers OBPI-0.0.27-02 --json   # parity gate (Stage 3 Phase 1b)
ls docs/design/adr/pool/ADR-pool.{attestation-quality-measurement,doctrine-amendment-protocol,complexity-doctrine-validate-suite,canon-pillar-codification,complexity-doctrine-meets-chore-system,complexity-guide-obpi-authoring-integration}.md
```

Each receipt ID is cited inline in the Stage 4 evidence table per `AGENTS.md` § Attestation. The `gz covers` parity gate must show `uncovered_reqs == 0` before Stage 4 begins.

## Verification

The exact Stage 3 verification commands are listed in Step 10 above. Acceptance criteria parity:

| Acceptance criterion | Mechanism |
|---|---|
| REQ-0.0.27-02-01 | `tests/governance/test_exemplar_corpus.py::assert_corpus_size_in_target_band` + `assert_archetypal_cell_coverage` |
| REQ-0.0.27-02-02 | `tests/models/test_exemplar.py::TestExemplarProjectShaValidation` (six rejection cases) |
| REQ-0.0.27-02-03 | `tests/models/test_exemplar.py::TestExemplarProjectPathFilterRequired` |
| REQ-0.0.27-02-04 | `assert_archetypal_cell_coverage` (≥8/10) + brief evidence vacant-cell rationales |
| REQ-0.0.27-02-05 | `assert_no_doctrine_violating_projects` (pytest + Pydantic absent) |
| REQ-0.0.27-02-06 | `assert_pool_stubs_exist` |
| REQ-0.0.27-02-07 | `tests/models/test_exemplar.py::TestExemplarProjectFrozenContract` (mutation raises) |
| REQ-0.0.27-02-08 | `_validate_manifest_documents` integration test + JSON-Schema/Pydantic parity test |

## Notes

- **Persona for implementer subagents:** `implementer` — methodical, test-first, atomic-edits, complete-units. The two-stage review fans out spec-reviewer + quality-reviewer per `gz-obpi-pipeline` Stage 2.
- **Step 3 is not negotiable.** A subagent that drafts `data/exemplar_corpus.json` without operator-confirmed slate has reproduced the exact failure class the OBPI exists to mechanize. Reviewers must reject any commit whose slate did not pass through Step 3.
- **No backwards-compat shims.** `ExemplarProject` is a new model on a new schema; no migration logic, no deprecated-field handling. The only `Optional`/`None` cases are foreign-key shapes the doctrine genuinely allows (none in this OBPI).
- **GHI #195 routing facts** — ceremony route is correct: brief crosses ADR boundary by booking pool stubs (heavy precedent), introduces new schema + new Pydantic model + foundation-kind Gate 5 (Heavy lane mandates), and is part of feature work (planned increment, not defect closure). Direct-fix is not a candidate.

## Confidence self-report (Stage 1→2 gate)

**90%+** — direction is constrained by the operator-confirmed lock-in in the handoff, the rule-canonized selection criteria from OBPI-01, and the existing pattern in `security_surfaces.py`. The 10% residual uncertainty is in the schema-shape questions surfaced for Step 3; those are forced choices on the operator, not agent-resolvable. `gz-justify` walkthrough is not required at this confidence level.
