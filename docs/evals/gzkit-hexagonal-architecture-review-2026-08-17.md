# gzkit Hexagonal Architecture Review — 2026-08-17

Status: **RETAINED — evaluation artifact for hexagonal architecture conformance.**
Prompt: [`gzkit_hexagonal_architecture_eval_prompt.md`](gzkit_hexagonal_architecture_eval_prompt.md)
Basis: `main @ 3b394c8b5`, v0.34.3.

---

## 1. Executive verdict

**Moderate alignment (partial strong-form).**

gzkit has a genuinely clean and enforced inner core in `src/gzkit/core/`, with policy checks that implement the stated `stdlib + pydantic` boundary. However, outside that core, several library/domain-adjacent modules still combine domain logic with concrete adapter construction and technology-specific dependencies, which weakens strong-form hexagonal separation.

## 2. Architecture map

| Layer role | Primary surfaces | Notes |
|---|---|---|
| Core domain | `src/gzkit/core/` | Pure models/rules/exceptions; no non-stdlib deps except `pydantic`. |
| Domain model (ontology) | `src/gzkit/ontology/model.py`, `src/gzkit/ontology/purity.py`, parts of `src/gzkit/ontology/work.py`, `src/gzkit/ontology/corpus.py`, `src/gzkit/ontology/unified.py` | Mixed package: some pure, some adapter-bound. |
| Adapters / boundary | `src/gzkit/commands/`, `src/gzkit/cli/`, `src/gzkit/ontology/graph.py`, adapter classes in `src/gzkit/ontology/source.py` | CLI wiring + concrete technologies (`rich`, `yaml`, `networkx`, `tree-sitter`, etc.). |
| Ports (`typing.Protocol`) | `SourceParser`, `ReferenceChecker`, `_LedgerSink`, `Presenter`, `_SurfaceClassifier` | Protocol style is present and used in several key seams. |

## 3. Dependency boundary findings

### 3.1 Core boundary

- `src/gzkit/core/` imports are consistent with stdlib + pydantic + internal imports.
- Boundary is mechanically enforced by `tests/policy/test_import_boundaries.py`.

### 3.2 Non-stdlib/non-pydantic dependency inventory (`src/gzkit/`)

Observed top-level external deps: `rich`, `yaml`, `jsonschema`, `radon`, `structlog`, `jinja2`, `networkx`, `tree_sitter`, `tree_sitter_python`.

Notable confinement:

- `networkx` appears in `src/gzkit/ontology/graph.py`.
- `tree_sitter*` appears in `src/gzkit/ontology/source.py` (function-local import in adapter path).
- CLI/commands carry most `rich`/`yaml` usage.

### 3.3 Domain-adjacent leak/contradiction

`src/gzkit/handoff_api.py` docstring claims “stdlib + Pydantic only,” but imports `yaml`.

## 4. DI/composition analysis

### Strong patterns

- CLI adapter wiring into port-typed API in `src/gzkit/commands/handoff.py`:
  - `_live_reference_checker(...)` composes the `gh` adapter.
  - Injected into `resume_handoff(..., reference_checker=...)` and `create_handoff(..., reference_checker=...)`.

### Weakening patterns

- Several library functions construct concrete defaults internally:
  - `build_source_anchor_index(...)` defaults to `TreeSitterSourceParser()`.
  - `project_corpus(...)`, `replay_work_queue(...)`, `project_all(...)` default to concrete ledger/config/path construction.
- Command handlers commonly call zero-arg composition methods (`project_all()`), reducing explicit composition-root separation.

## 5. Ports: Protocol vs ABC vs concrete coupling

- Ports are primarily `typing.Protocol`-based (good alignment).
- No meaningful production runtime-ABC architecture was found.
- Concrete coupling remains in places where interfaces are not protocolized (notably direct `Ledger` defaults and direct path/config discovery patterns).

## 6. Strong separation exemplars

1. `src/gzkit/core/` purity + policy tests (`tests/policy/test_import_boundaries.py`).
2. `SourceParser` seam with two real adapters (`AstSourceParser`, `TreeSitterSourceParser`) plus parity tests in `tests/test_ontology_source.py`.
3. Command-layer adapter wiring for handoff reference validation.

## 7. Weaknesses and violations

1. Mixed ontology package where pure domain and technology adapters coexist tightly.
2. Default concrete adapter construction inside library code rather than only at CLI composition roots.
3. Purity-claim mismatch in `handoff_api` (`yaml` import).
4. Uneven “never name the technology in core-ish logic” posture outside strict `core/`.

## 8. Prioritized remediation plan

### P0

- Fix `handoff_api` purity contradiction (either remove `yaml` from that module path or narrow/update the claim to reflect actual boundary).

### P1

- Push default adapter construction outward:
  - Require injected parser/ledger in core-library entry points where feasible.
  - Keep no-arg convenience wrappers at command edge only.

### P2

- Clarify package-level architecture map for ontology:
  - Make adapter-bearing modules explicit and separated by intent (even if not by heavy folder reorg).
  - Add targeted policy tests for non-core “domain-adjacent” modules where strict purity is intended.

## 9. Confidence and limits

Confidence: **high** for import-boundary and protocol findings; **moderate-high** for DI/cohesion conclusions.

Limit: this review focused on source architecture and dependency wiring, not runtime behavior benchmarking.
