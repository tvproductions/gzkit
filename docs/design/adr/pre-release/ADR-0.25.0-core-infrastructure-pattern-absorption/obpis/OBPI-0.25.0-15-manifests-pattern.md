---
id: OBPI-0.25.0-15-manifests-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 15
status: Completed
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-15: Manifests Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-15 — "Evaluate and absorb common/manifests.py (89 lines) — manifest loading and validation"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/common/manifests.py` (89 lines) against gzkit's partial manifest handling in `validate.py` and determine: Absorb (airlineops is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The airlineops module provides manifest loading and validation utilities. gzkit has partial manifest handling scattered across validation logic, so the comparison must determine whether airlineops's dedicated module provides a cleaner pattern.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/common/manifests.py` (89 lines)
- **gzkit equivalent:** Partial in `src/gzkit/validate.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Manifest loading is a generic governance pattern (`.gzkit/manifest.json` is central to gzkit)

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Redesigning gzkit's manifest schema — only improving the loading/validation code

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

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

- [ ] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated
- [ ] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [ ] REQ-0.25.0-15-01: Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [ ] REQ-0.25.0-15-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [ ] REQ-0.25.0-15-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.25.0-15-04: Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [ ] REQ-0.25.0-15-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/common/manifests.py
# Expected: airlineops source under review exists

test -f src/gzkit/validate.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-15-manifests-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Gate 3 (Docs):** Decision rationale completed
- [ ] **Gate 4 (BDD):** Behavioral proof present or `N/A` recorded with rationale
- [ ] **Gate 5 (Human):** Attestation recorded

## COMPARISON ANALYSIS

| Dimension | airlineops `manifests.py` | gzkit manifest handling |
|-----------|--------------------------|------------------------|
| **Purpose** | Writes deterministic JSON manifests for demand-run artifacts (`artifacts/_artifacts/{run_id}/manifest.json`) | Validates governance manifests (`.gzkit/manifest.json`) and doc-coverage manifests (`config/doc-coverage.json`) |
| **Core function** | `write_manifest(run_id, payload, root)` — enriches payload with SHA256, timestamp, package version, writes to disk | `validate_manifest(path)` — checks required fields, schema version, structure against JSON schema; `DocCoverageManifest` — Pydantic model for doc-coverage loading |
| **Data model** | `@dataclass(frozen=True) ManifestResult` (path, sha256, created_ts) | Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` for `DocCoverageManifest`, `CommandEntry`, `SurfaceRequirements` |
| **Error handling** | `contextlib.suppress(PackageNotFoundError)` — silently falls back to `"0.0.0"` | Structured `ValidationError` returns with type, artifact, message, field |
| **Cross-platform** | `Path` + `encoding="utf-8"` (good) | Same — `Path` + `encoding="utf-8"` throughout |
| **Dependencies** | `airlineops.common.config.load_config` for artifacts root; `importlib.metadata` for version | `gzkit.schemas.load_schema` for JSON schema; `gzkit.core.validation_rules` for error types |
| **Schema** | `airlineops.manifest.v1` (run artifact schema) | `gzkit.manifest.v1` / `gzkit.manifest.v2` (governance schema) |
| **Test coverage** | Out of scope for this evaluation | `tests/` includes manifest validation coverage |

### Subtraction Test

Removing airline-specific concerns from `manifests.py`:

- Remove `load_config()` dependency (artifacts root resolution) → **airline-specific**
- Remove `run_id` concept (demand-run artifact lifecycle) → **airline-specific**
- Remove `airlineops.manifest.v1` schema enrichment → **airline-specific**
- Remove `importlib.metadata` version lookup → **airline-specific** (package version injection)

**Remainder after subtraction:** ~13 lines of SHA256 hashing (`hashlib.sha256`) and deterministic JSON serialization (`json.dumps(sort_keys=True, separators=(",",":"))`). These are trivial utility primitives, not a module. OBPI-0.25.0-03 (Signature Pattern) previously evaluated and Excluded the same SHA256 primitive on identical reasoning: "trivial utility functions (~13 lines combined) that don't warrant a standalone module."

## DECISION

**Decision: Exclude** — The manifests module is domain-specific to airlineops's demand-run artifact workflow and has no governance analog in gzkit.

**Rationale:**

1. **Different purposes.** airlineops `manifests.py` writes run-level artifact manifests for demand processing. gzkit's manifests serve governance declaration and validation — completely different domain. There is no functional overlap.

2. **Tight domain coupling.** The module depends on `airlineops.common.config.load_config` for artifact root resolution and injects `airlineops` package version metadata. These are airline-operations concerns with no governance equivalent.

3. **gzkit already has superior manifest handling.** gzkit uses Pydantic models with `ConfigDict(frozen=True, extra="forbid")` for manifest loading (`doc_coverage/manifest.py`) and structured `ValidationError` returns for manifest validation (`validate_pkg/manifest.py`). Both are more robust than the airlineops pattern.

4. **Generic remainder is trivial.** After subtracting airline-specific concerns, only ~13 lines of SHA256 + deterministic JSON remain — the same primitive already evaluated and Excluded in OBPI-0.25.0-03.

## Gate 4 (BDD)

**N/A** — Exclude decision produces no code changes. No operator-visible behavior is affected. No behavioral proof required.

### Implementation Summary


- Outcome: Exclude — airlineops `common/manifests.py` is domain-specific to demand-run artifact workflow
- Comparison: Six-dimension analysis (purpose, core function, data model, error handling, cross-platform, dependencies)
- Subtraction test: Removing airline-specific concerns leaves ~13 lines of SHA256 + JSON primitives, previously Excluded in OBPI-0.25.0-03
- No code changes: gzkit's existing Pydantic-based manifest loading and structured validation are already more sophisticated

### Key Proof


```bash
rg -n 'Decision: Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-15-manifests-pattern.md
```

Returns: `**Decision: Exclude** — The manifests module is domain-specific to airlineops's demand-run artifact workflow and has no governance analog in gzkit.`

## Human Attestation

- Attestor: `Jeffry`
- Attestation: Attested as completed. Evaluated airlineops manifests.py against gzkit manifest handling. Exclude decision is correct — module is domain-specific to demand-run artifacts with no governance analog. All quality gates pass.
- Date: 2026-04-10

## Closing Argument

OBPI-0.25.0-15 evaluated airlineops `common/manifests.py` (89 lines) against gzkit's manifest handling across six dimensions: purpose, core function, data model, error handling, cross-platform robustness, and dependencies. The subtraction test conclusively identifies the module as domain-specific: removing airline concerns leaves only trivial SHA256 + JSON primitives previously Excluded in OBPI-0.25.0-03. gzkit's existing Pydantic-based manifest loading and structured validation are more sophisticated for their governance purpose. Decision: **Exclude**.
