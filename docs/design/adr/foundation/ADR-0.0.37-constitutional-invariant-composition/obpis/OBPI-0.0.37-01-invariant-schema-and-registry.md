---
id: OBPI-0.0.37-01-invariant-schema-and-registry
parent: ADR-0.0.37-constitutional-invariant-composition
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.37-01-invariant-schema-and-registry: Invariant Schema And Registry

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #1 — "OBPI-0.0.37-01 — Constitutional invariant schema + registry primitive (frozen Pydantic ConstitutionalInvariant + JSON Schema mirror + first three seed invariants: CIC-1, CIC-2, foundation-ADR-registers-invariant)"

**Status:** Draft

## Objective

Land the foundation primitive of CIC-1: a frozen Pydantic `ConstitutionalInvariant` model, a JSON Schema mirror at `src/gzkit/schemas/constitutional_invariant.json`, and three seed YAML invariants (`CIC-1`, `CIC-2`, `foundation-adr-registers-invariant`) under `.gzkit/invariants/`. The registry is the structural witness layer on which OBPI-02's renderer and OBPI-03's drift validator both depend.

## Lane

**Heavy** — Introduces a new schema (`constitutional_invariant.json`), a new runtime model (`ConstitutionalInvariant`), and a new canonical content directory (`.gzkit/invariants/`). Schema and runtime-contract surfaces trigger Heavy per `.gzkit/rules/cli.md`.

## Allowed Paths

- `src/gzkit/governance/invariants.py` (new) — Pydantic `ConstitutionalInvariant` model + registry loader
- `src/gzkit/governance/__init__.py` (modify) — export `ConstitutionalInvariant` and loader
- `src/gzkit/schemas/constitutional_invariant.json` (new) — JSON Schema mirror
- `.gzkit/invariants/CIC-1.yaml` (new) — composition invariant
- `.gzkit/invariants/CIC-2.yaml` (new) — brief↔reality coherence invariant
- `.gzkit/invariants/foundation-adr-registers-invariant.yaml` (new) — self-referential check
- `tests/governance/test_invariants.py` (new) — REQ-derived assertions
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-01-invariant-schema-and-registry.md` (this brief)

## Denied Paths

- Paths not listed in Allowed Paths
- `AGENTS.md` (touched by OBPI-09 migration, not here)
- CLI verbs (`gz governance render`, `gz brief reconcile`) — OBPI-02, OBPI-06
- Validator scopes (`--invariant-coherence`, `--brief-reconcile`) — OBPI-03, OBPI-05
- Ledger event types — OBPI-03/06 register; this OBPI must not preemptively touch the event schema
- CI files, lockfiles, dependency additions

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `src/gzkit/governance/invariants.py` defines a frozen Pydantic `ConstitutionalInvariant` with fields: `id: str`, `claim: str`, `structural_witness: list[str]` (Field(min_length=1)), `composition_targets: list[str]`. Model uses `model_config = ConfigDict(frozen=True, extra="forbid")`.
2. REQUIREMENT: `src/gzkit/schemas/constitutional_invariant.json` mirrors the Pydantic model: `additionalProperties: false`; required keys `id`, `claim`, `structural_witness`, `composition_targets`; `structural_witness` is `{"type":"array", "minItems": 1, "items": {"type":"string"}}`.
3. REQUIREMENT: A registry loader function `load_invariants(root: Path) -> dict[str, ConstitutionalInvariant]` walks `.gzkit/invariants/*.yaml`, validates each YAML body against the JSON Schema, then constructs ConstitutionalInvariant instances. Validation errors raise; no silent skip.
4. REQUIREMENT: Three seed YAML files exist under `.gzkit/invariants/`:
   - `CIC-1.yaml` — composition invariant (claim text = ADR § Decision CIC-1 paragraph; structural_witness includes `gz validate --invariant-coherence`; composition_targets includes `AGENTS.md`).
   - `CIC-2.yaml` — brief↔reality coherence invariant (claim text = ADR § Decision CIC-2 paragraph; structural_witness includes `gz validate --brief-reconcile`, `gz obpi pipeline (stage 1)`, `gz obpi complete (stage 5)`; composition_targets is `[]`).
   - `foundation-adr-registers-invariant.yaml` — self-referential check (claim: "Every foundation-kind ADR registers ≥1 invariant in `.gzkit/invariants/`"; structural_witness: `gz validate --foundation-registers-invariant` — forward-reference; composition_targets: `[]`).
5. REQUIREMENT: This OBPI does NOT introduce the renderer (OBPI-02), the drift validator (OBPI-03), or any CLI verb. The registry primitive is loadable but unconsumed at landing.

> **Forward-reference acknowledgment:** The seed YAML `structural_witness` entries reference verbs that land in later OBPIs: `gz validate --invariant-coherence` (OBPI-03), `gz validate --brief-reconcile` (OBPI-05), and `gz validate --foundation-registers-invariant` (future). At OBPI-01 landing time these are intentional forward-references per the ADR sequencing mandate; they are unresolvable until their respective OBPIs land. Resolvability is verified at OBPI-03 (REQ-0.0.37-03-02 exercises `--invariant-coherence`) and OBPI-05 (REQ-0.0.37-05-06 exercises `--brief-reconcile`). This is not a "placeholder structural witness" defect — it is an explicitly-sequenced forward-reference. The anti-pattern named in ADR § Consequences Negative #2 is a witness that *never* becomes real; the sequenced forward-reference here becomes real at OBPI-03/05 landing.

> STOP-on-BLOCKERS: if `src/gzkit/governance/` is not a package, or if `src/gzkit/schemas/` does not exist, halt and report the missing prerequisite.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] Parent ADR § Decision item — quote CIC-1 paragraph (constitutional invariant registry establishment) verbatim into the Implementation Summary
- [ ] Parent ADR § Intent — the why-frame for CIC-1
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the CIC-1 paragraph this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` — for the composition target form OBPI-02 will eventually render against
- [ ] `.gzkit/rules/models.md` — Pydantic conventions
- [ ] `docs/governance/state-doctrine.md` — Layer 1 (canon) vs Layer 3 (derived view) doctrine

**Context (existing exemplars):**

- [ ] `src/gzkit/governance/code_quality.py` — example of frozen Pydantic governance model in this codebase
- [ ] `src/gzkit/schemas/adr.json` — example of JSON Schema mirror pattern with `additionalProperties: false`
- [ ] `.gzkit/personas/` — example of per-YAML canonical-content directory under `.gzkit/`

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/governance/__init__.py` exists (will be modified)
- [ ] `src/gzkit/schemas/__init__.py` exists
- [ ] `.gzkit/` directory exists and is writable
- [ ] `pyyaml` available as transitive dependency (used by existing `.gzkit/skills/` loaders)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this brief
- [ ] Parent ADR checklist item #1 quoted verbatim in Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests in `tests/governance/test_invariants.py` derived from Acceptance Criteria REQs below
- [ ] Red-Green-Refactor cycle followed per REQ
- [ ] Tests pass: `uv run -m unittest tests.governance.test_invariants`
- [ ] Validation commands recorded with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] No new docs deliverable for this OBPI — the `gz governance render` and `gz brief reconcile` manpages belong to OBPI-02 / OBPI-06. Mark this gate satisfied with an explicit "deferred to OBPI-02/06 — registry primitive has no operator-facing CLI" note in evidence.

### Gate 4: BDD (Heavy)

- [ ] BDD scenarios in `features/constitutional_invariants.feature` deferred to OBPI-02 (renderer is the externally-observable behavior). Registry primitive itself has no scenario worth a feature file — unit tests are the right fidelity. Mark satisfied with explicit deferral note.

### Gate 5: Human (Heavy + Foundation universal — ADR-0.0.36)

- [ ] Human attestation recorded for foundation-kind brief-level Gate 5

## Verification

```bash
# Lint, types, tests
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_invariants -v

# REQ-01: model is frozen, structural_witness rejects empty
uv run python -c "
from gzkit.governance.invariants import ConstitutionalInvariant
inv = ConstitutionalInvariant(id='X', claim='c', structural_witness=['gz validate --x'], composition_targets=[])
try:
    inv.id = 'Y'
    raise SystemExit('FAIL: model is not frozen')
except (ValueError, TypeError):
    pass
try:
    ConstitutionalInvariant(id='Y', claim='c', structural_witness=[], composition_targets=[])
    raise SystemExit('FAIL: empty structural_witness accepted')
except Exception:
    pass
print('REQ-01 OK')
"

# REQ-02: JSON Schema mirror is conformant and strict
uv run python -c "
import json, jsonschema
s = json.load(open('src/gzkit/schemas/constitutional_invariant.json'))
jsonschema.Draft7Validator.check_schema(s)
assert s.get('additionalProperties') is False, 'additionalProperties must be false'
assert s['properties']['structural_witness']['minItems'] == 1
print('REQ-02 OK')
"

# REQ-03 / REQ-04: three seed YAML files load and validate
uv run python -c "
from pathlib import Path
from gzkit.governance.invariants import load_invariants
inv = load_invariants(Path('.'))
assert 'CIC-1' in inv and 'CIC-2' in inv and 'foundation-adr-registers-invariant' in inv
print('REQ-03/04 OK — three seed invariants loaded')
"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-01-01: `ConstitutionalInvariant` Pydantic model is frozen (raises on post-construction mutation) and rejects empty `structural_witness` at instantiation
- [ ] REQ-0.0.37-01-02: `src/gzkit/schemas/constitutional_invariant.json` has `additionalProperties: false` and `structural_witness.minItems = 1`; validates a known-good invariant and rejects an invariant missing `id`
- [ ] REQ-0.0.37-01-03: `.gzkit/invariants/CIC-1.yaml`, `.gzkit/invariants/CIC-2.yaml`, and `.gzkit/invariants/foundation-adr-registers-invariant.yaml` exist; `load_invariants` returns all three; each validates against the schema
- [ ] REQ-0.0.37-01-04: `load_invariants` raises (does not silently skip) on a YAML file that fails schema validation

## Completion Checklist

- [ ] **Gate 1 (ADR):** CIC-1 paragraph quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle followed per REQ; tests pass
- [ ] **Code Quality:** Lint, typecheck clean
- [ ] **Gate 3 (Docs):** Deferral note recorded (renderer manpage in OBPI-02)
- [ ] **Gate 4 (BDD):** Deferral note recorded (renderer scenarios in OBPI-02)
- [ ] **Gate 5 (Human):** Foundation-kind attestation per ADR-0.0.36
- [ ] **Value Narrative:** Problem-before / capability-now documented
- [ ] **Key Proof:** One concrete usage (e.g., `load_invariants(Path('.'))` returning the three seeds)
- [ ] **OBPI Acceptance:** Evidence recorded; `gz brief reconcile OBPI-0.0.37-01-invariant-schema-and-registry` reports zero drift before completion

## Evidence

### Gate 1 (ADR)

- [ ] CIC-1 paragraph quoted

### Gate 2 (TDD)

```text
# Paste `uv run -m unittest tests.governance.test_invariants -v` output here
```

### Code Quality

```text
# Paste lint/typecheck output here
```

### Gate 3 (Docs)

```text
# Deferred to OBPI-02 — registry primitive has no operator-facing CLI; no manpage drift to record.
```

### Gate 4 (BDD)

```text
# Deferred to OBPI-02 — externally-observable rendering behavior tested via features/constitutional_invariants.feature there.
```

### Gate 5 (Human)

```text
# Record attestor name and verbatim attestation text per AGENTS.md § Attestation
```

### Value Narrative

<!-- Before: constitutional invariants were prose claims in AGENTS.md with no schema, no loader, no fail-closed validation. After: every constitutional invariant is an addressable schema-validated YAML record loadable into a frozen Pydantic model. -->

### Key Proof

<!-- e.g. `python -c "from gzkit.governance.invariants import load_invariants; print(load_invariants(Path('.')).keys())"` returning {'CIC-1', 'CIC-2', 'foundation-adr-registers-invariant'} -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #495 — ADR-0.0.37 OBPI briefs in unindividualized scaffold state (this brief authored under that GHI)
- GHI #485 — `gz specify` --author mode bundles full ADR Decision (root-cause for the scaffold defect this brief corrects)

## Human Attestation

- Attestor: `<name>` when Gate 5 fires
- Attestation: substantive attestation text grounded in the seed-invariant loader output
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
