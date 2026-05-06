# Plan: OBPI-0.0.29-02-diagnosis-engine

**OBPI:** OBPI-0.0.29-02-diagnosis-engine
**Parent ADR:** ADR-0.0.29 (foundation, heavy lane)
**Objective:** Author the complexity advisor's diagnosis engine at `src/gzkit/complexity/advisor/engine.py`. Given an `AstContext` plus a `(metric, value)` crossing and a `ThresholdTable` (ADR-0.0.28-02), the engine returns an `AdvisorDiagnosis` (OBPI-0.0.29-01) when the value crosses a band, else `None`. Refactor-archetype detection rules are doctrine, not code: they live as a JSON rule table at `data/advisor_archetype_rules.json` (loaded once per engine instance), validated by a JSON Schema mirror at `src/gzkit/schemas/advisor_archetype_rules.json`, and surfaced through a frozen Pydantic loader at `src/gzkit/complexity/advisor/archetype_rules.py`. The engine binds `ThresholdTable` for band classification (never reimplements `band_for`), reads OBPI-0.0.27-04's distilled-characteristics document to populate the `recommended_move` and the default `doctrinal_frame`, and fails closed (named `EngineError`) on empty proof or missing/unparseable distilled-characteristics. This is the trigger-time data contract OBPI-03 (`gz complexity-advise` CLI) and OBPI-05 (auto-chain hook) bind against.

## Files (creates these files)

This OBPI is net-new engine authoring; every file below is created by this plan:

- **CREATE** `src/gzkit/complexity/advisor/engine.py` — the engine (`AstContext`, `EngineError`, `DiagnosisEngine`, `diagnose()` public function); decomposed per `.claude/rules/pythonic.md` § Size Limits into named helpers (`_extract_proof`, `_match_archetype_rule`, `_resolve_default_doctrinal_frame`, `_load_recommended_move`).
- **CREATE** `src/gzkit/complexity/advisor/archetype_rules.py` — frozen Pydantic `ArchetypeRule`, `MetricPredicate`, `AstPredicate` models; `load_archetype_rules(path)` loader; module-level constant for the canonical rule-table path (`Path("data") / "advisor_archetype_rules.json"`) consumed by `DiagnosisEngine` default construction.
- **CREATE** `data/advisor_archetype_rules.json` — initial rule table seeded against the four-authority canon (Fowler / Martin / Page-Jones / Constantine) and the ten-archetype enumeration locked at OBPI-0.0.29-01 (`RefactorArchetype`); ordered by descending specificity so the first-match-wins semantic in REQ-04 yields the most-specific archetype before falling through to the default.
- **CREATE** `src/gzkit/schemas/advisor_archetype_rules.json` — JSON Schema (Draft 2020-12, `$schema` declared, `additionalProperties: false`) validating: top-level non-empty array; per-rule `archetype` ∈ ten-value enum (matches `RefactorArchetype` values); `metric_predicate` and `ast_predicate` non-empty objects; `doctrinal_frame.authority` ∈ four-value enum (matches `DoctrinalFrame.authority` Literal); `metric_predicate.metrics` non-empty array of strings; `metric_predicate.bands` non-empty array of `block`/`warn`/`advise` enum values.
- **CREATE** `tests/complexity/advisor/test_engine.py` — REQ-derived assertions one per REQ in REQ-0.0.29-02-01..06 (acceptance criteria) plus the additional REQ-08 sub-cases (block-band crossing; recommended_move populated from distilled-characteristics, never fabricated; default-archetype fallback). Uses `@covers("REQ-0.0.29-02-NN")` decorators and `tempfile`-backed fixtures (synthetic AST, synthetic distilled-characteristics, synthetic threshold table, synthetic rule table) — no live corpus, no network, no fixtures outside the temp dir.
- **CREATE** `tests/complexity/advisor/test_archetype_rules.py` — schema validation tests (REQ-05, REQ-07): rule-load round-trip; malformed rule rejected; unknown archetype rejected; unknown authority rejected; empty rule list rejected; missing required field rejected.
- **MODIFY** `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-02-diagnosis-engine.md` — evidence section only at completion (Stage 5 closure-narrative).

## Allowed Files

Same set as Files above. Allowed paths exactly match the brief allowlist (line 28-33):

- `src/gzkit/complexity/advisor/engine.py`
- `src/gzkit/complexity/advisor/archetype_rules.py`
- `data/advisor_archetype_rules.json`
- `src/gzkit/schemas/advisor_archetype_rules.json`
- `tests/complexity/advisor/test_engine.py`
- `tests/complexity/advisor/test_archetype_rules.py`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-02-diagnosis-engine.md` (evidence section only)

## Context

### Source-of-truth artifacts read

- **ADR-0.0.29 § Decision rationale #1** — engine consumes `ThresholdTable` model directly, never re-parses; closes parser-divergence drift class at the ADR-0.0.28-02 layer.
- **ADR-0.0.29 § Decision rationale #2** — diagnostic vocabulary restricted to four canonical authorities (Fowler / Martin / Page-Jones / Constantine).
- **ADR-0.0.29 § Decision rationale #5** — verdict ↔ proof binding mandatory; engine fails closed if proof unavailable. ADR canon names this "the structural defense against plausible-looking advice with no traceable evidence."
- **ADR-0.0.29 § OBPI-0.0.29-02 paragraph (line 72)** — confirms data-driven rule table at `data/advisor_archetype_rules.json`; rules are doctrine; amendments flow through doctrine-amendment-protocol pool stub.
- **OBPI-0.0.29-02 brief — Requirements 1-11** — full FAIL-CLOSED requirement set (signature, AstContext shape, rule-table contract, default-archetype fallback, empty-proof failure, missing-distilled-characteristics failure, schema constraints, test coverage, function-size discipline, TDD discipline, no operator PII).
- **OBPI-0.0.29-02 brief — STOP-on-BLOCKERS clause (line 59)** — three prerequisites verified at Stage 1: OBPI-01 schema present at `src/gzkit/complexity/advisor/diagnosis.py` (5 frozen models); ADR-0.0.28-02 `ThresholdTable` importable from `gzkit.complexity.thresholds`; OBPI-0.0.27-04 distilled-characteristics document present at `docs/governance/complexity/distilled-characteristics-2026-05-04.md`.
- **OBPI-0.0.29-01 brief + diagnosis.py source** — confirms five public symbols re-exported from `gzkit.complexity.advisor`: `AdvisorDiagnosis`, `RefactorArchetype` (10 enum values: `LONG_PARAMETER_LIST`, `ARROWHEAD`, `SWITCH_ON_TYPE`, `FEATURE_ENVY`, `LARGE_CLASS`, `DIVERGENT_CHANGE`, `SHOTGUN_SURGERY`, `PRIMITIVE_OBSESSION`, `DATA_CLUMPS`, `MESSAGE_CHAIN`), `DoctrinalFrame` (authority Literal: 4 values), `ProofRange`, `IntrinsicAttestationRef`. The engine binds against these — never re-declares.
- **`src/gzkit/complexity/thresholds.py` source** — `ThresholdTable.band_for(metric, value)` returns `ThresholdBand | None` (highest-severity band the value crosses). `ThresholdBand.trigger_semantic` is `block`/`warn`/`advise` Literal. The engine consumes `band_for` for REQ-01 (return None below all bands) and gets the `trigger_semantic` for the `crossing_band` field of `AdvisorDiagnosis`.
- **`src/gzkit/complexity/citation.py` source** — `Citation` carries `distilled_characteristics_path`, `section_anchor`, `corpus_revision`. `ThresholdTable.citation` is the source-of-truth tuple the engine resolves the distilled-characteristics document path from (REQ-06: "path resolved from the active citation tuple in the threshold table").
- **`docs/governance/complexity/distilled-characteristics-2026-05-04.md` source** — confirms the per-metric section structure: `## Metric: \`<metric>\`` H2 header; `**Numeric boundary:**` line; `**Qualitative band (at-or-below boundary):**` line; `**Doctrinal frame:**` prose line (e.g. `Martin (Clean Code) — cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.`); `### Practitioner-eye observation` H3 subsection with operator-attested prose. The engine extracts the doctrinal-frame prose for the default `DoctrinalFrame` (REQ-04 fallback path) and the practitioner-eye prose for `recommended_move` (REQ-06).
- **`.claude/rules/models.md`** — `BaseModel` with `ConfigDict(frozen=True, extra="forbid")`; `Field(...)` with description; `str | None` over `Optional[str]`. The engine's `AstContext`, `ArchetypeRule`, `MetricPredicate`, `AstPredicate` all conform.
- **`.claude/rules/pythonic.md`** — function ≤ 50 lines, module ≤ 600 lines; top-level imports only; explicit exceptions (engine declares `class EngineError(Exception)`); type-check suppression syntax (bare `# type: ignore` or `# ty: ignore[<code>]`, never mypy-style `# type: ignore[<code>]`); EAFP for IO (file open inside `_load_recommended_move`).
- **`.claude/rules/cross-platform.md`** — `pathlib.Path`; `encoding="utf-8"` on every read; `.as_posix()` for any relative-path rendering inside ledger/JSON outputs (no rendering is required by this OBPI's surface — engine returns models, doesn't emit text — but kept binding for docstring path examples).
- **`.claude/rules/complexity-doctrine.md` § Citation contract** — citation tuple is the only valid form; raw distributions and corpus references are forbidden. The engine reads through `parse_citation` (`gzkit.complexity.citation`) — never re-parses.
- **`.claude/rules/complexity-thresholds.md` § Trigger-Semantic Vocabulary** — three values: `block`, `warn`, `advise`. The engine's matching logic respects this vocabulary verbatim (no fourth value).
- **`AGENTS.md` § STDLIB-FIRST DOCTRINE** — Python `ast` module is stdlib (canonical for AST inspection); `pathlib` is stdlib; `json` is stdlib; `re` is stdlib. Pydantic is the named departure for the validation layer (REQ-07 schema enforcement on rules; REQ-02 frozen `AstContext`); `jsonschema` is the existing runtime dep for the JSON Schema validation pass on rule load.
- **AGENTS.md § Local Agent Rules** — Operator PII never in code, fixtures, rule data, or docstrings (REQ-11). Plan and rule-data fixtures use `Test Author` / `gzkit` style placeholder strings only.

### Sibling precedents (structural template)

- **`src/gzkit/complexity/citation.py` + `src/gzkit/schemas/complexity_citation.json`** — frozen Pydantic + JSON Schema mirror (`additionalProperties: false`); module-level pattern constants; `parse_*` factory function returning the model. Used as the structural template for `archetype_rules.py` + `advisor_archetype_rules.json`.
- **`src/gzkit/complexity/thresholds.py`** — frozen Pydantic table model with named lookup methods (`band_for`, `bands_for_metric`); module-level regex constants for parser shapes; named `_load_threshold_table` factory. Used as the structural template for `archetype_rules.py`'s loader.
- **`src/gzkit/complexity/advisor/diagnosis.py`** — frozen `BaseModel` ConfigDict pattern; `Field(..., description=...)` discipline; `model_validator(mode="after")` for cross-field invariants. The engine's `AstContext` follows this discipline.

### Gates inherited from parent ADR

- **Lane: Heavy** — full gate stack required. New runtime engine; downstream consumers (OBPI-03 CLI, OBPI-05 auto-chain hook) bind against this surface.
- **Kind: Foundation** — brief-level Gate 5 attestation required (TTY + `ATTEST` co-presence proxy via active pipeline marker per `--attestor-present`).
- **Sensitivity: absent** — engine touches no security surface (no credentials, no signing, no ledger writes, no PII handling). Confirmed by allow-paths review against `data/security_surfaces.json` registry.

## Steps

Each step is a unit of TDD discipline (RGR cycle). Tests reference REQ IDs as `@covers("REQ-0.0.29-02-NN")` decorators per `.gzkit/rules/tests.md`. Steps are sequential by dependency; subagent dispatch (Stage 2 mode) takes them one at a time.

### Step 1 — JSON Schema for the rule table

Author `src/gzkit/schemas/advisor_archetype_rules.json` first (the contract every later step binds against):

- Draft 2020-12 (`"$schema": "https://json-schema.org/draft/2020-12/schema"`).
- Top-level: `type: array`, `minItems: 1`, `items: { $ref: "#/definitions/Rule" }`.
- `definitions.Rule`: `type: object`, `additionalProperties: false`, required `[archetype, metric_predicate, ast_predicate, doctrinal_frame]`.
- `archetype`: `type: string`, `enum: [<the ten RefactorArchetype values>]`.
- `metric_predicate`: object, `additionalProperties: false`, required `[metrics, bands]`. `metrics`: non-empty array of strings (`minItems: 1`, `items.type: string`). `bands`: non-empty array of enum `[block, warn, advise]`.
- `ast_predicate`: object, `additionalProperties: false`, at least one of `[node_kind, min_param_count, min_branch_count, min_argument_count, min_class_attributes, min_method_calls]` required (use `oneOf`/`anyOf` to enforce). All numeric thresholds carry `minimum: 1`. The `node_kind` field is a string enum of common AST node names (`FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `If`, `For`, `While`, `Match`, `Call`, `Attribute`, `BinOp`).
- `doctrinal_frame`: object, `additionalProperties: false`, required `[authority, citation, excerpt]`. `authority`: `enum: [fowler, martin, page_jones, constantine]`. `citation`: `type: string, minLength: 1`. `excerpt`: `type: string, minLength: 1`.

### Step 2 — Pydantic loader for the rule table

Author `src/gzkit/complexity/advisor/archetype_rules.py`:

- Top-level imports: `from __future__ import annotations`; `import json`; `from pathlib import Path`; `from typing import Literal`; `from pydantic import BaseModel, ConfigDict, Field`; `from jsonschema import Draft202012Validator`; `from gzkit.complexity.advisor.diagnosis import DoctrinalFrame, RefactorArchetype`.
- Module constants: `CANONICAL_RULE_TABLE_PATH = Path("data") / "advisor_archetype_rules.json"`; `CANONICAL_SCHEMA_PATH = Path("src") / "gzkit" / "schemas" / "advisor_archetype_rules.json"`.
- `MetricPredicate(BaseModel)` (frozen, extra=forbid): `metrics: tuple[str, ...] = Field(min_length=1)`; `bands: tuple[Literal["block", "warn", "advise"], ...] = Field(min_length=1)`. Method `matches(self, metric: str, band: str) -> bool`.
- `AstPredicate(BaseModel)` (frozen, extra=forbid): all six numeric/string fields optional with default `None`; root validator asserting at-least-one-non-None to mirror the schema's `oneOf`. Method `matches(self, node: ast.AST) -> bool` returning True when every non-None field is satisfied by the node.
- `ArchetypeRule(BaseModel)` (frozen, extra=forbid): `archetype: RefactorArchetype`; `metric_predicate: MetricPredicate`; `ast_predicate: AstPredicate`; `doctrinal_frame: DoctrinalFrame` (re-uses OBPI-01 model — no re-declaration).
- `load_archetype_rules(path: Path | None = None) -> tuple[ArchetypeRule, ...]`:
    1. Resolve `path` (default to `CANONICAL_RULE_TABLE_PATH`).
    2. Read schema via `CANONICAL_SCHEMA_PATH.read_text(encoding="utf-8")`, parse, build `Draft202012Validator`.
    3. Read rule file via `path.read_text(encoding="utf-8")`, parse JSON.
    4. Validate against the schema — collect errors and raise a single `ValueError` listing every failure (no silent truncation).
    5. Construct `tuple(ArchetypeRule.model_validate(rule) for rule in data)` and return.
- Function size discipline: every function ≤ 30 lines; helpers extracted as needed.

Tests (`tests/complexity/advisor/test_archetype_rules.py`) — RGR per REQ-05 + REQ-07:

- `@covers("REQ-0.0.29-02-05")` `test_load_rules_round_trip_succeeds_on_canonical_table` — loads the seeded `data/advisor_archetype_rules.json` and asserts at least one rule exists.
- `@covers("REQ-0.0.29-02-05")` `test_load_rules_rejects_empty_array` — `tempfile`-backed `[]` → raises `ValueError` mentioning `minItems`.
- `@covers("REQ-0.0.29-02-05")` `test_load_rules_rejects_unknown_archetype` — rule with `archetype: "made_up_archetype"` → raises.
- `@covers("REQ-0.0.29-02-07")` `test_load_rules_rejects_unknown_authority` — rule with `doctrinal_frame.authority: "uncle_bob"` → raises.
- `@covers("REQ-0.0.29-02-07")` `test_load_rules_rejects_empty_metric_predicate_metrics` — empty `metrics: []` → raises.
- `@covers("REQ-0.0.29-02-07")` `test_load_rules_rejects_empty_ast_predicate` — `ast_predicate: {}` → raises (`oneOf` failure).
- `@covers("REQ-0.0.29-02-05")` `test_load_rules_rejects_missing_required_field` — rule omits `doctrinal_frame` → raises.

### Step 3 — Seed `data/advisor_archetype_rules.json`

Author the initial rule table — six to ten rules covering the most-common archetype/metric crossings. Each rule's `doctrinal_frame` cites a primary-source authority + excerpt; no fabricated quotations (excerpts paraphrase the canonical work without invoking authorial voice). Ordering is descending specificity so `_match_archetype_rule`'s first-match-wins yields the strongest match.

Seed shape (illustrative; final seed authored against the four-authority canon):

```json
[
  {
    "archetype": "long_parameter_list",
    "metric_predicate": {"metrics": ["lizard_param_count"], "bands": ["warn", "block"]},
    "ast_predicate": {"node_kind": "FunctionDef", "min_param_count": 4},
    "doctrinal_frame": {
      "authority": "fowler",
      "citation": "Refactoring 2e, ch. 11 — Long Parameter List",
      "excerpt": "Long parameter lists obscure the relationship between caller and callee; introduce a Parameter Object or Preserve Whole Object to recover intent."
    }
  },
  {
    "archetype": "arrowhead",
    "metric_predicate": {"metrics": ["lizard_nesting_depth"], "bands": ["warn", "block"]},
    "ast_predicate": {"node_kind": "FunctionDef", "min_branch_count": 3},
    "doctrinal_frame": {
      "authority": "martin",
      "citation": "Clean Code, ch. 7 — Boundary Conditions",
      "excerpt": "Deeply nested control flow signals missing guard clauses; collapse the arrowhead with early returns."
    }
  }
  // additional rules: switch_on_type, large_class, feature_envy, primitive_obsession ...
]
```

Validation: re-run `load_archetype_rules()` against the seeded file in test (`test_load_rules_round_trip_succeeds_on_canonical_table`).

No operator PII in rule data (REQ-11). Excerpts paraphrase rather than quote, to avoid licensing concerns.

### Step 4 — `AstContext`, `EngineError`, helpers

Author the engine's foundation in `src/gzkit/complexity/advisor/engine.py`:

- Top-level imports: `from __future__ import annotations`; `import ast`; `import re`; `from pathlib import Path`; `from pydantic import BaseModel, ConfigDict, Field`; `from gzkit.complexity.advisor.archetype_rules import ArchetypeRule, load_archetype_rules`; `from gzkit.complexity.advisor.diagnosis import AdvisorDiagnosis, DoctrinalFrame, ProofRange, RefactorArchetype`; `from gzkit.complexity.citation import Citation, parse_citation`; `from gzkit.complexity.thresholds import ThresholdBand, ThresholdTable`.

- `EngineError(Exception)` — single named exception class. The error message is the contract surface; tests assert specific substrings (`"empty proof"`, `"OBPI-0.0.27-07"`).

- `AstContext(BaseModel)` (frozen, extra=forbid):
  - `file_path: str = Field(min_length=1)`
  - `source: str = Field(min_length=1)`
  - `tree: ast.Module` — Pydantic's `arbitrary_types_allowed` toggled on this model alone (justified: `ast.Module` is a stdlib type, not a Pydantic-validated payload; the model exists for shape + immutability, not deep validation).
  - `target_node: ast.AST` — same justification.
  - `model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)`.

- Module-level regex constants for distilled-characteristics parsing:
  - `_METRIC_SECTION_PATTERN` — captures the `## Metric: \`<metric>\`` H2 section through to the next H2 boundary.
  - `_DOCTRINAL_FRAME_LINE_PATTERN` — captures the `**Doctrinal frame:** <authority-prose>` line.
  - `_PRACTITIONER_EYE_SECTION_PATTERN` — captures the `### Practitioner-eye observation` H3 subsection through to the next H2/H3 boundary.
  - `_AUTHORITY_KEYWORD_MAP: dict[str, str]` — case-insensitive lookup table mapping authority signals (`"fowler"`, `"martin"`, `"page-jones"` → `"page_jones"`, `"constantine"`) to the four-value enum.

### Step 5 — `_extract_proof(target_node, file_path)`

Helper returning `tuple[ProofRange, ...]`:

- Walks `target_node` once via `ast.walk` collecting nodes with `lineno` attribute.
- Builds one `ProofRange(file_path=file_path, start_line=node.lineno, end_line=getattr(node, "end_lineno", node.lineno), ast_node_kind=type(node).__name__)`.
- Deduplicates by `(start_line, end_line, ast_node_kind)`.
- Returns the resulting tuple sorted by `start_line` ascending.

Function ≤ 25 lines.

### Step 6 — `_match_archetype_rule(rules, metric, band, target_node)`

Helper returning `ArchetypeRule | None`:

- Iterates `rules` in declared order.
- For each rule: calls `rule.metric_predicate.matches(metric, band)` AND `rule.ast_predicate.matches(target_node)`.
- Returns the first satisfying rule; `None` when no rule matches.

Function ≤ 15 lines.

### Step 7 — `_resolve_default_doctrinal_frame(metric, distilled_text)`

Helper returning `DoctrinalFrame`:

- Locates the `## Metric: \`<metric>\`` section via `_METRIC_SECTION_PATTERN`.
- Within that section, locates the `**Doctrinal frame:**` line via `_DOCTRINAL_FRAME_LINE_PATTERN`.
- Splits on em-dash (`—`) into `(authority_prose, excerpt_prose)`.
- Resolves authority via `_AUTHORITY_KEYWORD_MAP` (case-insensitive substring match).
- If section, line, or authority cannot be resolved: raise `EngineError(f"distilled-characteristics document missing doctrinal frame for metric {metric!r}; resolution path: gz validate --complexity-doctrine-links (OBPI-0.0.27-07)")`.
- Otherwise return `DoctrinalFrame(authority=<resolved>, citation=<authority_prose stripped>, excerpt=<excerpt_prose stripped>)`.

Function ≤ 30 lines.

### Step 8 — `_load_recommended_move(metric, distilled_text)`

Helper returning `str`:

- Locates the metric's section, then the `### Practitioner-eye observation` subsection via `_PRACTITIONER_EYE_SECTION_PATTERN`.
- Strips HTML comments (`<!-- ... -->`) from the captured body.
- Strips whitespace.
- If the resulting string is empty: raise `EngineError(f"distilled-characteristics document missing practitioner-eye observation for metric {metric!r}; resolution path: gz validate --complexity-doctrine-links (OBPI-0.0.27-07)")`.
- Otherwise return the cleaned string.

Function ≤ 25 lines.

### Step 9 — `_read_distilled_text(citation: Citation)`

Helper returning `str`:

- Resolves `Path(citation.distilled_characteristics_path)` (project-relative).
- If the path does not exist: raise `EngineError(f"distilled-characteristics document {citation.distilled_characteristics_path!r} not found; resolution path: gz validate --complexity-doctrine-links (OBPI-0.0.27-07)")`.
- Otherwise return `path.read_text(encoding="utf-8")`.

Function ≤ 15 lines.

### Step 10 — `DiagnosisEngine` class

Author the engine class:

```python
class DiagnosisEngine:
    """Trigger-time diagnosis engine binding ThresholdTable and distilled-characteristics."""

    def __init__(
        self,
        rules: tuple[ArchetypeRule, ...] | None = None,
        rule_path: Path | None = None,
    ) -> None:
        if rules is not None and rule_path is not None:
            msg = "DiagnosisEngine accepts rules OR rule_path, not both"
            raise EngineError(msg)
        self._rules = rules if rules is not None else load_archetype_rules(rule_path)

    def diagnose(
        self,
        ast_context: AstContext,
        metric: str,
        value: float,
        table: ThresholdTable,
    ) -> AdvisorDiagnosis | None:
        band = table.band_for(metric, value)
        if band is None:
            return None
        proof = _extract_proof(ast_context.target_node, ast_context.file_path)
        if not proof:
            msg = f"engine produced empty proof for metric {metric!r} crossing {band.trigger_semantic!r}"
            raise EngineError(msg)
        distilled_text = _read_distilled_text(table.citation)
        recommended_move = _load_recommended_move(metric, distilled_text)
        matched_rule = _match_archetype_rule(self._rules, metric, band.trigger_semantic, ast_context.target_node)
        if matched_rule is not None:
            archetype = matched_rule.archetype
            doctrinal_frame = matched_rule.doctrinal_frame
        else:
            archetype = RefactorArchetype.LONG_PARAMETER_LIST
            doctrinal_frame = _resolve_default_doctrinal_frame(metric, distilled_text)
        return AdvisorDiagnosis(
            metric=metric,
            crossing_band=band.trigger_semantic,
            crossing_value=value,
            archetype=archetype,
            doctrinal_frame=doctrinal_frame,
            proof=proof,
            recommended_move=recommended_move,
        )
```

`diagnose` is ≤ 50 lines.

### Step 11 — Module-level `diagnose()` convenience function

Per OBPI-02 brief signature (REQ-01: `engine.diagnose(...)` callable directly), expose a module-level helper:

```python
def diagnose(
    ast_context: AstContext,
    metric: str,
    value: float,
    table: ThresholdTable,
    rules: tuple[ArchetypeRule, ...] | None = None,
) -> AdvisorDiagnosis | None:
    return DiagnosisEngine(rules=rules).diagnose(ast_context, metric, value, table)
```

Function ≤ 10 lines. Tests target this surface for the most common path; the class is the explicit-construction surface for callers (CLI, auto-chain hook) that need rule reuse.

### Step 12 — REQ-derived engine tests

Author `tests/complexity/advisor/test_engine.py`:

For each test, build synthetic fixtures (no live corpus) inside a `tempfile.TemporaryDirectory` block:
- A synthetic distilled-characteristics document with one `## Metric: \`<metric>\`` section per metric under test.
- A synthetic threshold table (parsed via `load_threshold_table`) citing the synthetic document.
- A synthetic AST built via `ast.parse(source)`; `target_node` selected from `tree.body[0]`.
- A small in-test rule list passed via `DiagnosisEngine(rules=...)` to avoid loading `data/advisor_archetype_rules.json` for every test.

Tests:
- `@covers("REQ-0.0.29-02-01")` `test_diagnose_below_all_bands_returns_none` — value below the lowest band → returns `None`.
- `@covers("REQ-0.0.29-02-02")` `test_diagnose_warn_band_with_matching_rule_returns_diagnosis_with_rule_archetype` — function with 5 params crosses warn → archetype matches the rule's archetype.
- `@covers("REQ-0.0.29-02-02")` `test_diagnose_block_band_returns_diagnosis` — value at block threshold → returns diagnosis with `crossing_band="block"`.
- `@covers("REQ-0.0.29-02-03")` `test_diagnose_empty_proof_raises_engine_error` — `target_node` synthesized without `lineno` (a bare `ast.Module()`) → `EngineError("empty proof")`.
- `@covers("REQ-0.0.29-02-04")` `test_diagnose_missing_distilled_characteristics_raises_engine_error_referencing_obpi_27_07` — citation points to non-existent path → `EngineError` mentions `OBPI-0.0.27-07`.
- `@covers("REQ-0.0.29-02-04")` `test_diagnose_missing_practitioner_eye_section_raises_engine_error_referencing_obpi_27_07` — distilled doc missing the H3 subsection → `EngineError` mentions `OBPI-0.0.27-07`.
- `@covers("REQ-0.0.29-02-04")` `test_diagnose_missing_doctrinal_frame_raises_engine_error_referencing_obpi_27_07` — distilled doc missing the `**Doctrinal frame:**` line → `EngineError` mentions `OBPI-0.0.27-07`.
- `@covers("REQ-0.0.29-02-06")` `test_diagnose_no_matching_rule_returns_default_archetype` — engine constructed with empty rule list and metric crossing → `archetype == RefactorArchetype.LONG_PARAMETER_LIST`.
- `@covers("REQ-0.0.29-02-06")` `test_diagnose_recommended_move_populated_from_distilled_characteristics_not_fabricated` — distilled doc carries a unique sentinel string in the practitioner-eye section; engine's `recommended_move` contains that sentinel exactly (no agent paraphrasing).

All tests run inside `tempfile.TemporaryDirectory` for fixture isolation; no test mutates the real `docs/governance/complexity/` tree or `data/advisor_archetype_rules.json` (REQ-10).

### Step 13 — Run the verification bundle

Per the brief's Verification section (line 92-98):

```bash
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/advisor/test_engine.py tests/complexity/advisor/test_archetype_rules.py -v
uv run gz arb step --name unittest -- uv run -m unittest -q   # full sweep, ARB-wrapped per Stage 3 contract
uv run gz arb ruff
uv run gz arb typecheck
uv run gz validate --documents
```

Expected: all green; ARB receipts written under `.gzkit/arb/receipts/`; no new ruff or ty findings; no document-validation drift.

### Step 14 — REQ → @covers parity gate (Stage 3 Phase 1b)

```bash
uv run gz covers OBPI-0.0.29-02-diagnosis-engine --json
```

Expected: `summary.uncovered_reqs == 0` for REQs 01-06 (the acceptance-criteria REQs). REQs 07-11 are infrastructure REQs satisfied by schema/test/code-shape evidence rather than a covering test; if `gz covers` flags them, decorate the most-on-point existing test (the schema test for REQ-07; the synthetic-fixture test class for REQ-10; etc.) before advancing.

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/advisor/test_engine.py tests/complexity/advisor/test_archetype_rules.py -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
uv run gz covers OBPI-0.0.29-02-diagnosis-engine --json
```

Heavy-lane Gate 4 BDD waiver: this OBPI is engine-internal; user-facing scenarios land at OBPI-03 (`gz complexity-advise` CLI). Register the waiver in `data/behave_coverage_waivers.json` only if the brief's Gate 4 evidence section names it explicitly; otherwise file a pre-completion GHI noting the waiver gap (the brief currently lists the waiver as a Gate 4 expectation; confirm at Stage 5 closure).

## Notes

- **Doctrine binding.** Engine never re-implements `band_for` (REQ-01 makes this explicit); never re-parses citations (`parse_citation` is the canonical surface); never re-declares `RefactorArchetype` / `DoctrinalFrame` / `ProofRange` (OBPI-01 owns these). Any drift here is the parser-divergence failure class ADR-0.0.29 § Decision rationale #1 explicitly forbids.
- **Fail-closed surfaces.** Three named failure paths in REQ-04, REQ-05, REQ-06 all raise `EngineError` with a recovery hint. The error message contract is part of the public surface — tests assert substrings, so changing the message shape breaks tests deliberately (the message is the operator-facing repair pointer).
- **Rule-table doctrine seam.** Per ADR-0.0.29 § Positive #7 ("Refactor-archetype detection rules are data-driven doctrine"), rule edits flow through the doctrine-amendment-protocol pool stub — not through code patches. The engine surface is stable; the doctrine surface (the JSON file) is amendable.
- **No ledger writes.** This OBPI is the engine layer; ledger emission for intrinsic-complexity attestation lands at OBPI-07. Confirmed against `data/security_surfaces.json` registry — no security surface overlap.
- **Plan-audit reconciliation.** The Stage 1 `gz plan audit` run flagged five "allowed path does not exist" gaps for the net-new files this OBPI authors. Per the GHI #403 fix recorded in commit `0beee072`, plan-declared net-new paths suppress the existence gap once this plan file is on disk and re-audited; the second `gz plan audit` pass at Stage 2 is expected to report PASS on those five paths. The 200-row "scope-collision" advisory list is a known false-positive shape across speculative pre-release ADRs (0.32 / 0.34 / 0.31 / 0.39 listing every advisor file as "contested") and does not block PASS — the brief allowlist is the authoritative scope contract.

## Destination-in-mind disclosure (Step 6a)

**Conclusion already formed before authoring this plan:** A two-module split (engine + rule loader) with a JSON Schema mirror, exposing both a class (`DiagnosisEngine`) and a module-level `diagnose()` function. The class enables rule-reuse for the CLI; the function enables one-shot calls from tests and the auto-chain hook. The doctrinal-frame default-fallback path parses the distilled-characteristics document via per-metric regex sections (the same shape `complexity-doctrine.md` § Citation contract canonizes for citation parsing).

**Rejected alternatives during exploration:**

1. **Single-module engine (engine.py owns rule loading too).** Rejected: violates `pythonic.md` § Size Limits (combined module would land near 600 lines after tests + helpers + class); also blurs the "rule-table is doctrine" seam by burying the loader inside the consumer.
2. **Rule predicates as Python callables registered in code (not data-driven JSON).** Rejected: explicit ADR-0.0.29 § Alternative #8 rejection — rules are doctrine, not configuration; data-driven keeps amendments under the doctrine-amendment-protocol pool stub instead of requiring code patches per amendment.
3. **Engine returns a list of diagnoses (one per matched rule).** Rejected: the OBPI brief Requirement #4 explicitly names "first matching rule" semantics, and `AdvisorDiagnosis` is singular by design (OBPI-01). Returning a list would change the OBPI-01 contract.
4. **`recommended_move` synthesized by the engine when the practitioner-eye section is empty.** Rejected: REQ-08 explicitly forbids agent-fabricated recommended_move text ("never from agent training memory"). Empty section → `EngineError` is the structural defense — fail closed and surface the operator-action path (write the practitioner-eye prose at the next distillation pass).
5. **Allow `arbitrary_types_allowed=True` globally on every model.** Rejected: scoped to `AstContext` only; the rule-table models (`MetricPredicate`, `AstPredicate`, `ArchetypeRule`) carry only validated primitives + the `RefactorArchetype` enum + the `DoctrinalFrame` model. Narrowing the toggle minimizes the validation-bypass surface.
6. **Cache the loaded distilled-characteristics text per engine instance.** Rejected for OBPI-02 scope: the engine fires once per metric crossing, which is rare enough that caching is premature optimization. The rule-table cache (REQ-03 — "loaded once per engine instantiation") is the only caching this OBPI introduces; document-text caching is a downstream concern (OBPI-09 timeout/fallback layer).
