---
id: OBPI-0.0.43-04-frontmatter-cascade-keys-validators
parent: ADR-0.0.43
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.43-04-frontmatter-cascade-keys-validators: ADR/GHI/OBPI frontmatter cascade keys

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/ADR-0.0.43-ddd-domain-cascade.md`
- **Checklist Item:** #4 — "ADR / GHI / OBPI frontmatter cascade keys + Pydantic + validators — `bounded_context` (required for non-pool ADR / GHI), `domain_model` (optional), `crosses_contexts` (optional), `cascade_change` (GHI only), `bounded_context_override` (OBPI rare case)."

**Status:** Draft

## Objective

Extend frontmatter schemas of three artifact types (ADR, GHI, OBPI) with cascade keys; add Pydantic fields; wire CLI gates that fail closed at authoring time when `bounded_context` is missing for non-pool ADRs/GHIs. This OBPI is the authoring-time gate; OBPI-06 builds the document-validation-time validator.

## Lane

**Heavy** — schema changes to three canonical frontmatter contracts + authoring-time CLI gates.

## Allowed Paths

- `src/gzkit/schemas/adr.json` — EXTEND with `bounded_context`, `domain_model`, `crosses_contexts`
- `src/gzkit/schemas/ghi.json` — EXTEND with `bounded_context`, `crosses_contexts`, `cascade_change`
- `src/gzkit/schemas/obpi.json` — EXTEND with `bounded_context_override`
- `src/gzkit/governance/frontmatter.py` — EXTEND or NEW; cascade-key resolution helpers
- `src/gzkit/cli/plan.py` — EXTEND `gz plan create` with `--bounded-context`
- `src/gzkit/cli/adr.py` — EXTEND `gz adr promote` with `--bounded-context`
- `tests/governance/test_frontmatter_cascade.py` — NEW
- `tests/cli/test_plan_create_bounded_context.py` — NEW
- `tests/cli/test_adr_promote_bounded_context.py` — NEW

## Denied Paths

- `src/gzkit/governance/domain_models.py` — OBPI-01 / OBPI-02
- Other schema files — other OBPI scopes
- `src/gzkit/governance/trust_audits/domain_cascade.py` — OBPI-06 (this OBPI provides schemas; OBPI-06 enforces resolution)
- `src/gzkit/cli/domain.py` — OBPI-03
- `src/gzkit/ledger/**` — OBPI-05
- `.gzkit/skills/**` — OBPI-08 / 09 / 10
- Existing ADR / GHI / OBPI content files — schema-only changes; content amendment lives in OBPI-07 and OBPI-13
- Runtime dependencies

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (ADR `bounded_context` schema key).** Optional string or list-of-strings. Pattern `^[a-z][a-z0-9-]*$` per element. `governance` is a real slug, never special-cased.
2. **REQUIREMENT (ADR `domain_model` schema key).** Optional string. Pattern `^DM-[a-z][a-z0-9-]*$`. Resolution to existing DMs is OBPI-06.
3. **REQUIREMENT (ADR `crosses_contexts` schema key).** Optional list-of-strings. When non-empty, declares cross-BC impact requiring PRD § 2.3 context-map entry. Resolution is OBPI-06.
4. **REQUIREMENT (GHI `bounded_context` schema key).** Same shape as ADR. Applies to gzkit-managed GHI surfaces (export/import) and `gz issue file` cross-repo provenance.
5. **REQUIREMENT (GHI `cascade_change` schema key).** Optional boolean. When `true`, signals resolution introduces new BC/term/context-map entry. OBPI-10's `ghi-triage` skill prioritizes.
6. **REQUIREMENT (OBPI `bounded_context_override` schema key).** Optional string-or-list. Defaults to inheriting parent ADR's `bounded_context`. Used in rare cases when OBPI scopes to single BC of multi-BC parent.
7. **REQUIREMENT (`gz plan create --bounded-context`).** Required for `--kind foundation` and `--kind feature`; exempt for `--kind pool`. Multiple flags allowed. Fail-closed exit 3 with `Resolve:` line on (a) omission for non-pool (b) value not kebab-case.
8. **REQUIREMENT (`gz adr promote --bounded-context`).** Same shape; required for non-pool promotions; refuses if source pool ADR omits AND flag not provided.
9. **REQUIREMENT (schema backward compatibility).** Existing artifacts without cascade keys remain schema-valid (keys optional at schema layer). OBPI-06 enforces operator-time required-ness with legacy-mapping fallback.
10. **REQUIREMENT (override discipline).** OBPI `bounded_context_override` MUST appear in parent ADR's `bounded_context` list. Cross-ADR BC drag is forbidden.

> STOP-on-BLOCKERS: if existing ADR/GHI Pydantic models do not exist, STOP — cascade keys need both schema + Pydantic representation.

## Discovery Checklist

**Parent ADR:**

- [ ] Parent ADR § Decision item #4 quoted
- [ ] Parent ADR § Intent
- [ ] Parent ADR file

**Governance:**

- [ ] `AGENTS.md` § Kinds (pool, foundation, feature), § Lane Rules
- [ ] `.gzkit/rules/governance-core.md`

**Context:**

- [ ] OBPI-01 landed
- [ ] Existing `src/gzkit/schemas/adr.json`, `ghi.json`, `obpi.json`
- [ ] Existing frontmatter parsing in `src/gzkit/governance/`
- [ ] Existing `gz plan create` and `gz adr promote`

**Prerequisites:**

- [ ] OBPI-01 (strategic Pydantic + schemas) landed
- [ ] Existing artifact schemas authoring conventions clear

**Existing Code:**

- [ ] Schema authoring style
- [ ] CLI flag patterns

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #4 quoted
- [ ] Intent recorded

### Gate 2: TDD

- [ ] ADR schema: cascade keys accepted; unknown rejected; list-form; slug pattern
- [ ] GHI schema: `cascade_change` boolean; `bounded_context` shape
- [ ] OBPI schema: `bounded_context_override` shape
- [ ] `gz plan create --kind foundation` without `--bounded-context` → exit 3
- [ ] `gz plan create --kind pool` without flag → exit 0
- [ ] Single-BC scaffold → `bounded_context: <slug>`
- [ ] Multi-BC scaffold → `bounded_context: [a, b]`
- [ ] OBPI inheritance: child without override inherits parent
- [ ] OBPI override outside parent's list → schema valid but OBPI-06 (separate) flags
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint / typecheck clean

### Gate 3: Docs (Heavy only)

- [ ] mkdocs build --strict clean
- [ ] `gz plan create` manpage updated with `--bounded-context`
- [ ] `gz adr promote` manpage updated

### Gate 4: BDD (Heavy only)

- [ ] No new scenarios (OBPI-06 covers cascade-integrity scenarios)

### Gate 5: Human (Heavy + Foundation)

- [ ] Attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

uv run python -c "
import json
adr = json.load(open('src/gzkit/schemas/adr.json'))
ghi = json.load(open('src/gzkit/schemas/ghi.json'))
obpi = json.load(open('src/gzkit/schemas/obpi.json'))
assert 'bounded_context' in adr['properties']
assert 'cascade_change' in ghi['properties']
assert 'bounded_context_override' in obpi['properties']
print('cascade keys present')
"
```

## Demo

```bash
# Scaffold without bounded-context — fails
uv run gz plan create demo-fail --kind foundation --semver 0.99.0 --lane lite || echo "exit 3 (expected)"

# Scaffold with bounded-context — succeeds
uv run gz plan create demo-ok --kind foundation --semver 0.99.0 --lane lite --bounded-context governance
grep -A 1 '^bounded_context:' docs/design/adr/foundation/ADR-0.99.0-demo-ok/ADR-0.99.0-demo-ok.md

# Cleanup
rm -rf docs/design/adr/foundation/ADR-0.99.0-demo-ok/
```

## Acceptance Criteria

- [ ] REQ-0.0.43-04-01: Given ADR schema, when `bounded_context: "experimentation"`, then schema passes
- [ ] REQ-0.0.43-04-02: Given ADR schema, when `bounded_context: ["a", "b"]`, then schema passes
- [ ] REQ-0.0.43-04-03: Given ADR schema, when `bounded_context: "Experimentation"` (uppercase), then schema fails on pattern
- [ ] REQ-0.0.43-04-04: Given GHI schema, when `cascade_change: "yes"` (string), then schema fails
- [ ] REQ-0.0.43-04-05: Given `gz plan create --kind foundation` without `--bounded-context`, then exit 3 with `Resolve:` line
- [ ] REQ-0.0.43-04-06: Given `gz plan create --kind pool` without `--bounded-context`, then exit 0
- [ ] REQ-0.0.43-04-07: Given `--kind foundation --bounded-context experimentation`, when scaffold completes, then frontmatter contains `bounded_context: experimentation`
- [ ] REQ-0.0.43-04-08: Given `--bounded-context a --bounded-context b`, when scaffold completes, then frontmatter contains `bounded_context: [a, b]`
- [ ] REQ-0.0.43-04-09: Given OBPI with `bounded_context_override` not in parent, when OBPI-06 validator runs, then violation flagged (schema valid here)
- [ ] REQ-0.0.43-04-10: Given existing ADR without cascade keys, when validated against updated schema, then validation passes (backward-compatible)

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR followed
- [ ] **Code Quality:** Clean
- [ ] **Gate 3 (Docs):** mkdocs + manpage updates clean
- [ ] **Gate 5 (Human):** Attestation recorded
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/typecheck output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs output here
```

### Gate 4 (BDD)

```text
# N/A
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
