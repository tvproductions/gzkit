---
id: OBPI-0.0.38-01-rule-and-schema
parent: ADR-0.0.38-evidence-authority-projection-doctrine
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.38-01-rule-and-schema: Surface-Axis Rule and Declaration Schema

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.38-evidence-authority-projection-doctrine/ADR-0.0.38-evidence-authority-projection-doctrine.md`
- **Checklist Item:** #1 — `rule-and-schema` — Author `.gzkit/rules/evidence-vs-authority.md` (three-axis taxonomy: Authoritative / Evidentiary / Projection); register in advisory-rules-audit scorecard; define axis-declaration schema for every surface kind.

**Status:** Draft

## Objective

Author the canonical foundation rule codifying the three-axis function-axis taxonomy (Authoritative / Evidentiary / Projection), define the axis-declaration schema for every surface kind (skill frontmatter, rule body marker, code-level module constant, validator-scope registration, CLI verb registration), register the rule in the advisory-rules-audit scorecard as **Mechanical** (enforced by the validator landing under OBPI-0.0.38-02), and update Pydantic schemas + JSON Schemas that govern surface declarations.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.38-evidence-authority-projection-doctrine/**` — parent ADR package
- `.gzkit/rules/evidence-vs-authority.md` (new) — canonical rule file
- `docs/governance/advisory-rules-audit.md` — scorecard registration
- `src/gzkit/rules.py` — `RuleFrontmatter` model (if a frontmatter field is added; rule body-marker convention may suffice without schema change)
- `src/gzkit/schemas/skill.json` (or active equivalent) — add `surface_axis` enum
- `src/gzkit/governance/surface_axis.py` (new) — enum definition + module-level `SURFACE_AXIS` constant convention + introspection helpers
- `src/gzkit/schemas/surface_axis.json` (new) — JSON Schema mirror of axis enum
- `tests/governance/test_surface_axis_rule.py` (new) — REQ-derived assertions on rule shape
- `tests/governance/test_surface_axis_schema.py` (new) — REQ-derived assertions on schema fields

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/governance/trust_audits.py` — validator implementation is OBPI-0.0.38-02's scope
- `src/gzkit/cli/parser_*.py` — CLI registration of `--surface-axis` is OBPI-0.0.38-02's scope
- `artifacts/audits/surface-axis-*.md` — retroactive classification is OBPI-0.0.38-03's scope
- Existing skill / rule / code-level surface axis-declaration edits — those are OBPI-0.0.38-03's scope
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `.gzkit/rules/evidence-vs-authority.md` exists with body-level rule version marker `<!-- rule-version: 0.1.0 -->` and visible block-quote `> **Rule version:** \`0.1.0\``, per the body-level marker convention from `.gzkit/rules/skill-surface-sync.md` v0.2.0.
1. REQUIREMENT: The rule file declares the three categories — **Authoritative**, **Evidentiary**, **Projection** — with the same definitions and caller-contract semantics as the parent ADR § Decision § "The three categories" table.
1. REQUIREMENT: The rule file enumerates the four binding rules: declare-axis-at-authoring, promotion-requires-foundation-ADR, projection-MUST-NOT-bind, receipt-shape-shared-binding-distinct. Each rule states its mechanical witness (validator scope name, schema field, ledger event family) explicitly.
1. REQUIREMENT: The rule file lists the per-surface-kind declaration site for axis: skill YAML frontmatter `surface_axis:`, rule body marker `<!-- surface-axis: <axis> -->`, code-level module constant `SURFACE_AXIS: Final[str]`, validator-scope registry `axis` field, CLI parser `axis` field. Each site MUST be named in the rule with its file-path or registration-point.
1. REQUIREMENT: The rule file declares its own surface_axis as `authoritative` via the body marker — meta-self-classification: a rule that defines axis classification is itself an authoritative surface for the audit pass.
1. REQUIREMENT: `docs/governance/advisory-rules-audit.md` is updated with a new entry classifying `evidence-vs-authority.md` as **Mechanical** (validator-enforced by `gz validate --surface-axis` once OBPI-0.0.38-02 lands), with a forward-reference to OBPI-0.0.38-02 for the validator landing.
1. REQUIREMENT: `src/gzkit/governance/surface_axis.py` defines `SurfaceAxis` (string Enum: `AUTHORITATIVE`, `EVIDENTIARY`, `PROJECTION`) with frozen Pydantic constraints; a `SURFACE_AXIS_CONSTANT_NAME: Final[str] = "SURFACE_AXIS"` declaring the canonical module-level constant name introspection helpers will look for; and a helper `read_module_axis(module: ModuleType) -> SurfaceAxis | None` returning the declared axis or `None`.
1. REQUIREMENT: `src/gzkit/schemas/surface_axis.json` is the JSON Schema mirror; `additionalProperties: false`; enum values match the Python enum exactly. The schema is referenced from the skill schema and the rule schema (where applicable).
1. REQUIREMENT: The skill JSON Schema at `src/gzkit/schemas/skill.json` (or the active equivalent path; verify at implementation time) is extended with an OPTIONAL `surface_axis` field referencing `surface_axis.json#/definitions/axis`. The field is OPTIONAL at this OBPI because retroactive classification is OBPI-0.0.38-03's scope; it becomes REQUIRED once OBPI-0.0.38-02's validator lands and OBPI-0.0.38-03 backfills declarations on existing skills.
1. REQUIREMENT: `tests/governance/test_surface_axis_rule.py` asserts: (a) the rule file exists at the canonical path; (b) it carries the version marker shape; (c) it declares all three categories with their definitions; (d) it declares all four binding rules; (e) it self-classifies as `authoritative`. Assertions are semantic per `.gzkit/rules/tests.md` — read sections by H2/H3 heading and check content presence, NOT byte-level string match.
1. REQUIREMENT: `tests/governance/test_surface_axis_schema.py` asserts: (a) the `SurfaceAxis` enum has exactly three members; (b) the JSON Schema mirror's enum matches the Python enum; (c) the skill schema's optional `surface_axis` field validates against the canonical enum; (d) `read_module_axis` returns the declared axis when the module has the canonical constant and `None` otherwise.
1. REQUIREMENT: `docs/governance/advisory-rules-audit.md` registration includes the new entry's path, its classification (Mechanical), the validator scope name (`--surface-axis`), and the OBPI under which the validator lands (OBPI-0.0.38-02). Format mirrors existing scorecard entries.
1. REQUIREMENT: `gz agent sync control-surfaces` runs cleanly after the rule file lands, mirroring `.gzkit/rules/evidence-vs-authority.md` to `.claude/rules/` and `.github/instructions/` per `.gzkit/rules/skill-surface-sync.md`.
1. REQUIREMENT: NEVER author validator implementation code in this OBPI; that scope is OBPI-0.0.38-02. The brief MUST fail-close if the implementation tree gains a new validator scope.
1. REQUIREMENT: NEVER backfill axis declarations on existing skills, rules, or code-level surfaces in this OBPI; that scope is OBPI-0.0.38-03.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.38-evidence-authority-projection-doctrine/ADR-0.0.38-evidence-authority-projection-doctrine.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.38-evidence-authority-projection-doctrine/ADR-0.0.38-evidence-authority-projection-doctrine.md`
- [ ] Required path exists or is intentionally created in this OBPI: `.gzkit/rules/evidence-vs-authority.md`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
# Documents and rule schema
uv run gz validate --documents
uv run gz validate --advisory-scorecard
uv run gz lint
uv run gz typecheck

# OBPI-specific tests
uv run -m unittest tests/governance/test_surface_axis_rule.py -v
uv run -m unittest tests/governance/test_surface_axis_schema.py -v

# Sync control surfaces (verify rule mirrors land cleanly)
uv run gz agent sync control-surfaces

# Heavy-lane gates
uv run mkdocs build --strict
uv run -m behave features/governance/surface_axis.feature

# Confirm the canonical artifacts exist
test -f .gzkit/rules/evidence-vs-authority.md
test -f .claude/rules/evidence-vs-authority.md
test -f src/gzkit/governance/surface_axis.py
test -f src/gzkit/schemas/surface_axis.json
grep -q "evidence-vs-authority" docs/governance/advisory-rules-audit.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.38-01-01: Given the parent ADR § Decision § "The three categories" table, when `.gzkit/rules/evidence-vs-authority.md` is read, then the rule file declares Authoritative/Evidentiary/Projection with the same definitions and caller-contract semantics.
- [ ] REQ-0.0.38-01-02: Given the parent ADR § Decision § "The four binding rules", when the rule file is read, then all four rules (declare-axis-at-authoring, promotion-requires-foundation-ADR, projection-MUST-NOT-bind, receipt-shape-shared-binding-distinct) are enumerated with their mechanical witnesses named.
- [ ] REQ-0.0.38-01-03: Given the rule body, when the body marker is parsed, then the file declares `<!-- surface-axis: authoritative -->` (meta-self-classification per § Requirements #5).
- [ ] REQ-0.0.38-01-04: Given `src/gzkit/governance/surface_axis.py`, when imported, then `SurfaceAxis` is a string Enum with exactly three members `AUTHORITATIVE`, `EVIDENTIARY`, `PROJECTION` and `read_module_axis()` returns the declared axis or `None`.
- [ ] REQ-0.0.38-01-05: Given `src/gzkit/schemas/surface_axis.json`, when validated as a JSON Schema, then it has `additionalProperties: false` and its enum matches `SurfaceAxis` exactly.
- [ ] REQ-0.0.38-01-06: Given the skill schema at `src/gzkit/schemas/skill.json`, when a skill frontmatter declares `surface_axis: evidentiary`, then schema validation passes; when it declares an off-enum value, validation fails.
- [ ] REQ-0.0.38-01-07: Given `docs/governance/advisory-rules-audit.md`, when read, then the new entry classifies `evidence-vs-authority.md` as **Mechanical** with forward-reference to OBPI-0.0.38-02 as the validator-landing OBPI.
- [ ] REQ-0.0.38-01-08: Given `gz agent sync control-surfaces`, when run after the rule file lands, then `.claude/rules/evidence-vs-authority.md` and `.github/instructions/evidence-vs-authority.md` mirrors are produced with byte-identical body content (allowing for vendor-specific frontmatter rendering).
- [ ] REQ-0.0.38-01-09: Given the Denied Paths boundary, when this OBPI's diff is reviewed, then no validator implementation code lands under `src/gzkit/governance/trust_audits.py` and no axis declarations are backfilled on existing skills/rules/modules — those scopes belong to OBPI-0.0.38-02 and -03 respectively.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
