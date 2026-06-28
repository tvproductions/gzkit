---
id: OBPI-0.30.0-03-okf-conformance-validator
parent: ADR-0.30.0-okf-documentation-knowledge-structure
item: 3
lane: heavy
status: Draft
---

# OBPI-0.30.0-03-okf-conformance-validator: Add `gz validate --okf-conformance` (generated-bundle-only conformance) and carry the STRUCTURAL-FENCE REQ that no `gz validate` / gates / closeout surface consumes OKF frontmatter or links as enforcement evidence.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md`
- **Checklist Item:** #3 — "gz validate --okf-conformance scope (generated-bundle-only conformance: parseable frontmatter, non-empty `type`; reserved index.md/log.md structure; does NOT gate authored source docs) AND carry the STRUCTURAL-FENCE REQ that no gz validate / gates / closeout surface consumes OKF frontmatter or links as enforcement evidence — proven via this ADR's `## Boundary Invariants` entry, audited at ADR-closeout layer."

**Status:** Draft

## Objective

Add a `gz validate --okf-conformance` scope that checks the GENERATED OKF bundle ONLY — recognizing a bundle by its reserved files (`index.md`/`log.md`) and `type`-bearing concept docs, NEVER by an `okf/`-format folder name — where every non-reserved markdown file has parseable frontmatter and a non-empty `type`, and reserved `index.md`/`log.md` follow OKF structure; exiting 3 (naming the offending file and field) on a conformance failure and 0 on a clean bundle, and that NEVER gates authored source docs. Carry the STRUCTURAL-FENCE REQ enforcing parent ADR Boundary Invariant 1: no `gz validate` / gates / closeout surface consumes OKF frontmatter or links as enforcement evidence.

## Lane

**Heavy** — This OBPI adds a new `gz validate` scope (a CLI surface contract) and changes operator-facing docs.

> Heavy is reserved for command/API/schema/runtime-contract changes. A new `gz validate --<scope>` is a CLI contract change.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md` — parent ADR for intent and scope
- `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/obpis/OBPI-0.30.0-03-okf-conformance-validator.md` — this brief
- `src/gzkit/governance/trust_audits/` — new `--okf-conformance` validator module
- `src/gzkit/commands/validate_cmd.py` — wire the `--okf-conformance` flag into the `validate` CLI surface
- `src/gzkit/cli/` — argparse registration for the `--okf-conformance` flag (validate subparser)
- `docs/user/manpages/validate.md` — document the new scope (Synopsis / Options / Examples / Exit Codes)
- `tests/` — REQ-derived unittest cases (clean bundle exit 0; malformed bundle exit 3; authored-source-doc not gated)

## Denied Paths

- Paths not listed in Allowed Paths
- The OKF concept-frontmatter model (`src/gzkit/knowledge/` model) — OBPI-0.30.0-01's scope; this validator imports it read-only
- The generator and `.gzkit/governance/knowledge/` bundle output — OBPI-0.30.0-02's scope
- `src/gzkit/commands/` (other than `validate_cmd.py`) — the OKF CLI (`okf` subcommand) is OBPI-0.30.0-04's scope
- ANY change that would make a `gz validate` / gates / closeout surface READ an OKF `type`/tag/link as enforcement evidence (forbidden by Boundary Invariant 1)
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `uv run gz validate --okf-conformance` MUST be a registered scope; `gz validate --help` documents it, and a clean generated bundle exits 0.
2. REQUIREMENT: Given a generated-bundle file with unparseable frontmatter, an empty/missing `type`, or a malformed reserved `index.md`/`log.md`, `gz validate --okf-conformance` MUST exit 3 and name the offending file and field.
3. REQUIREMENT: The scope MUST be generated-bundle-only and MUST identify a bundle by its reserved files (`index.md`/`log.md`) + `type`-bearing concept docs, NEVER by an `okf/`-format folder name — it MUST NOT flag or gate authored source documents (a source doc with no OKF frontmatter is NOT a conformance failure), and it MUST work for a DOMAIN-named bundle root (e.g. `.gzkit/governance/knowledge/`). This is parent ADR Boundary Invariant 2.
4. REQUIREMENT: The conformance check validates the bundle's OWN well-formedness; it MUST NOT consume any OKF `type`/tag/link as evidence for any OTHER governance claim, and no other `gz validate` scope, gate, or closeout step may do so either (parent ADR Boundary Invariant 1).
5. ALWAYS: Tests are derived from the REQs above, not from a run of the implementation (`.gzkit/rules/tests.md` § "Tests assert semantics, not strings").

> SCOPE BOUNDARY: The model is OBPI-0.30.0-01's scope; the generator + `.gzkit/governance/knowledge/` bundle is OBPI-0.30.0-02's scope. This OBPI reads the model and validates the bundle's structure.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the Implementation Summary: "Add a validator (gz validate --okf-conformance) that checks OKF conformance ONLY for the generated bundle: every non-reserved markdown file has parseable frontmatter and a non-empty `type`; reserved index.md and log.md follow OKF structure."
- [ ] Parent ADR § Boundary Invariants — invariants 1 and 2 are the contracts this OBPI mechanizes/fences.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] An existing `gz validate --<scope>` audit under `src/gzkit/governance/trust_audits/` reviewed as the implementation pattern
- [ ] `docs/governance/state-doctrine.md` — the Layer-3-never-source-of-truth doctrine the STRUCTURAL-FENCE protects
- [ ] `.claude/rules/governance-core.md` § Operator-doc verb resolution — `gz validate --okf-conformance` must resolve in docs
- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract

**Context:**

- [ ] OBPI-0.30.0-01 (model, imported read-only) and OBPI-0.30.0-02 (the bundle this validator reads)

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists: `src/gzkit/commands/validate_cmd.py`
- [ ] Required path exists: the OBPI-0.30.0-01 model and the OBPI-0.30.0-02 `.gzkit/governance/knowledge/` bundle (or a fixture bundle for tests)

**Existing Code (understand current state):**

- [ ] Existing validate-scope tests adjacent to the Allowed Paths reviewed before implementation
- [ ] `gz cli audit` coverage requirement reviewed (new flag must be covered across manpage + index)

## Quality Gates

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/user/manpages/validate.md` updated; `uv run gz cli audit` exits 0

### Gate 4: BDD (Heavy only)

- [ ] External surface (new validate scope) covered by direct CLI/validator unit tests; no new `.feature` required

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_okf_conformance -v
uv run gz validate --okf-conformance
uv run gz cli audit
uv run mkdocs build --strict
```

## Demo

```bash
# Clean generated bundle: the conformance scope passes
uv run gz validate --okf-conformance; echo "exit=$?"

# An authored source doc with no OKF frontmatter is NOT gated (generated-bundle-only)
uv run gz validate --okf-conformance docs/governance/state-doctrine.md; echo "exit=$?"
```

## Acceptance Criteria

- [ ] REQ-0.30.0-03-01 [BEHAVIOR]: Given a clean generated OKF bundle, when `gz validate --okf-conformance` is invoked, then it exits 0; and `gz validate --help` documents the `--okf-conformance` scope.
- [ ] REQ-0.30.0-03-02 [BEHAVIOR]: Given a generated-bundle fixture with unparseable frontmatter or an empty/missing `type`, when `gz validate --okf-conformance` runs, then it exits 3 and names the offending file and field.
- [ ] REQ-0.30.0-03-03 [BEHAVIOR]: Given an authored source document with no OKF frontmatter, when `gz validate --okf-conformance` runs, then it does NOT flag that source doc (generated-bundle-only; parent ADR Boundary Invariant 2).
- [ ] REQ-0.30.0-03-04 [SUPPORT]: `docs/user/manpages/validate.md` documents the `--okf-conformance` scope and its generated-bundle-only boundary — proven by `uv run gz validate --documents` and `uv run gz cli audit` passing AND an `artifact_edited` ledger event citing the manpage emitted at OBPI completion.
- [ ] REQ-0.30.0-03-05 [STRUCTURAL-FENCE]: No `gz validate` / gates / closeout surface consumes OKF frontmatter or OKF links as enforcement evidence, per parent ADR `## Boundary Invariants` invariant 1 — audited at ADR-closeout layer (not a per-OBPI behavior test).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

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
# Paste docs-build + cli audit output here
```

### Gate 4 (BDD)

```text
# Direct CLI/validator unit tests cover the external surface; no behave run required
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before this OBPI nothing checks that the generated bundle is well-formed, and nothing fences the feature against authority creep. After this OBPI, `gz validate --okf-conformance` fails closed (exit 3, naming file+field) on a malformed generated bundle, while leaving authored source docs untouched — and the STRUCTURAL-FENCE REQ pins the load-bearing boundary (no OKF data consumed as enforcement evidence) for the ADR-closeout audit.

### Key Proof

`uv run gz validate --okf-conformance; echo exit=$?` exits 0 on a clean bundle; a malformed-frontmatter fixture makes it exit 3 naming the file and field; running the scope against an authored source doc does NOT flag it (generated-bundle-only).

### Implementation Summary

- Files created/modified: validator module under `src/gzkit/governance/trust_audits/`; `src/gzkit/commands/validate_cmd.py` + `src/gzkit/cli/` (flag wiring); `docs/user/manpages/validate.md`; `tests/governance/` (REQ-derived cases).
- Tests added: REQ-0.30.0-03-01,02,03 BEHAVIOR cases (`@covers`); REQ-0.30.0-03-04 SUPPORT (manpage + cli-audit + ledger proof); REQ-0.30.0-03-05 STRUCTURAL-FENCE audited at ADR closeout.
- Date completed: pending.
- Attestation status: pending (Heavy lane Gate 5).
- Defects noted: pending.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: pending
- Attestation: pending
- Date: pending

---

**Date Completed:** pending

**Evidence Hash:** -
