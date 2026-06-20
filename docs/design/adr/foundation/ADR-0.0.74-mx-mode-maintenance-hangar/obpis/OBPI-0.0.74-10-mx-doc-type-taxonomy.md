---
id: OBPI-0.0.74-10-mx-doc-type-taxonomy
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 10
lane: Heavy
status: Draft
req_atomic:
  - REQ-0.0.74-10-01  # one classification-guard behavior (gz validate --doc-type fail closed exit 3 over the named initial doc set) + tests — single indivisible unit
  - REQ-0.0.74-10-02  # SUPPORT: the four-way classification doctrine doc + the named initial docs tagged — one coupled documentation unit
  - REQ-0.0.74-10-03  # one lexical-alignment behavior (the ONE MX term drifts across tool/skill/rule/marker → fail closed) + test — single indivisible unit
---

# OBPI-0.0.74-10-mx-doc-type-taxonomy: The Governance Doc-Type Taxonomy

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #10 - "The governance doc-type taxonomy — Doctrinal/Lawful/Ordinance/Ops-spec classification + tag the governance docs + a guard that keeps the one term aligned across tool/skill/rule/marker (fail closed on lexical drift); unit tests"

**Status:** Draft

## Objective

Give governance docs a declared, legible binding-class — Doctrinal / Lawful / Ordinance / Ops-spec (maintenance-guide.md § 1.2) — as its own classification doctrine; tag a small named initial doc set; ship `gz validate --doc-type` (fail closed, exit 3) that enforces the tags; and add a lexical-alignment guard (`gz validate --mx-term-alignment`) that fails closed when the ONE MX term drifts across tool / skill / rule / marker — the operator's "one word everywhere", proven every run because "doctrine and rule are inseparable for agents".

## Lane

**Heavy** - This OBPI adds the `gz validate --doc-type` and `gz validate --mx-term-alignment` CLI scopes (new runtime-contract surfaces).

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope (§ Decision item 10)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/**` — parent ADR package scope (this brief's evidence)
- `src/gzkit/governance/doc_type.py` **CREATE** — the `DocType` classification (Doctrinal / Lawful / Ordinance / Ops-spec), the `--doc-type` audit (read each named doc's declared type tag; fail closed on a missing or unknown tag), and the `--mx-term-alignment` guard (the ONE MX term across tool / skill / rule / marker)
- `src/gzkit/commands/validate_cmd.py` — add `check_doc_type` / `check_mx_term_alignment` parameters, scope runners, and dispatch
- `src/gzkit/cli/parser_maintenance.py` — add `--doc-type` and `--mx-term-alignment` CLI arguments and dispatch kwargs (coupled surface — conventional `gz validate` scope pattern)
- `docs/governance/doc-type-taxonomy.md` **CREATE** — the classification doctrine: the four types, their aviation analogue, and binding semantics (owned here, anchored on maintenance-guide.md § 1.2), plus the named initial tagged-doc set
- `docs/governance/maintenance-guide.md` — tag it `Doctrinal + Ops spec` (its own § 1.2 names this) — member of the named initial set
- `.gzkit/rules/**` — the MX rule (OBPI-0.0.74-08) tagged `Lawful (Law)`; also the surface the lexical guard reads the ONE term from
- `docs/user/manpages/validate.md` — document the `--doc-type` and `--mx-term-alignment` scopes (Heavy-lane docs gate, Gate 3)
- `tests/governance/test_doc_type.py` **CREATE** — unit tests: classification fail-closed fixture, no-false-positive fixture, lexical-drift fail-closed fixture

(Security overlap check: no Allowed Path matches a glob in `data/security_surfaces.json` — `validate_cmd.py`, `doc_type.py`, `docs/governance/**`, and `.gzkit/rules/**` are outside every registered security surface — so `sensitivity: security` is not declared.)

## Creates These Files

- `src/gzkit/governance/doc_type.py`
- `docs/governance/doc-type-taxonomy.md`
- `tests/governance/test_doc_type.py`

## Denied Paths

- Paths not listed in Allowed Paths
- Tagging the entire governance corpus — only the small named initial doc set is tagged in this OBPI; full-corpus tagging is named follow-up (ADR scope boundary)
- New dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz validate --doc-type` MUST fail closed (exit 3) when any doc in the named initial set lacks a declared type tag or declares one outside {Doctrinal, Lawful, Ordinance, Ops-spec}, and MUST pass with no false positive when every named doc carries a valid tag (REQ-10-01).
1. REQUIREMENT: The four-way taxonomy MUST be documented as its own classification doctrine (`docs/governance/doc-type-taxonomy.md`), and each doc in the named initial set MUST carry a declared type (REQ-10-02).
1. REQUIREMENT: `gz validate --mx-term-alignment` MUST fail closed (exit 3) when the ONE MX term drifts across tool / skill / rule / marker, and MUST pass when all four agree — the "one word everywhere" is proven every run (REQ-10-03).
1. NEVER: Widen the tagged set beyond the named initial docs in this OBPI.
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 10 — quoted verbatim:** "The governance doc-type taxonomy. Classify governance docs Doctrinal / Lawful / Ordinance / Ops-spec, tag them, and add a guard that keeps the ONE term aligned across tool / skill / rule / marker (fail closed on lexical drift)."
- [ ] Parent ADR § Intent — 'doctrine and rule are inseparable for agents': naked doctrine is rationalized away, so every doctrinal claim ships with its coupled enforcement (here: the taxonomy ships with `--doc-type`, and the one-word rule ships with `--mx-term-alignment`).
- [ ] `docs/governance/maintenance-guide.md` § 1.2 — the source table (Doctrinal / Lawful / Ordinance / Ops spec, aviation analogue, binding semantics) and the "this taxonomy likely deserves its own governance-doc-classification doctrine" open note this OBPI discharges.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] `src/gzkit/commands/validate_cmd.py` + `src/gzkit/cli/parser_maintenance.py` — the conventional shape for adding a `gz validate` scope (parameter, runner, dispatch, CLI arg)
- [ ] `.claude/rules/governance-core.md` § "Operator-doc verb resolution" — both new flags hang off the already-registered `gz validate` verb, so `--cli-alignment` resolves

**Context:**

<!-- gz-validate-skip: command-shape -->
- [ ] OBPI-0.0.74-01 (marker), OBPI-0.0.74-04/05 (`gz mx` tool), OBPI-0.0.74-08 (gz-mx skill + MX rule) — the four surfaces the ONE MX term must agree across

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/validate_cmd.py` and `src/gzkit/cli/parser_maintenance.py` exist (they do — conventional validate-scope host surfaces)
<!-- gz-validate-skip: command-shape -->
- [ ] The marker, the `gz mx` tool, and the gz-mx skill + MX rule have landed (OBPI-01, OBPI-04/05, OBPI-08) so the lexical guard has all four surfaces to compare
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

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
- [ ] Relevant docs updated (`docs/governance/doc-type-taxonomy.md` authored; `docs/user/manpages/validate.md` documents both new scopes)

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --doc-type
uv run gz validate --mx-term-alignment
uv run gz validate --cli-alignment
test -f src/gzkit/governance/doc_type.py
test -f docs/governance/doc-type-taxonomy.md
test -f tests/governance/test_doc_type.py
```

## Demo

```bash
# Every named governance doc declares a binding-class; the guard fails closed on a gap:
uv run gz validate --doc-type
# The ONE MX term is proven aligned across tool / skill / rule / marker every run:
uv run gz validate --mx-term-alignment
```

## Acceptance Criteria

- [ ] REQ-0.0.74-10-01 [behavior]: Given the named initial governance-doc set, when `gz validate --doc-type` runs and any doc lacks a declared type tag or declares one outside {Doctrinal, Lawful, Ordinance, Ops-spec}, then the doc is flagged and the scope exits 3; when every named doc carries a valid tag it passes with no false positive. (@covers test in `tests/governance/test_doc_type.py`)
- [ ] REQ-0.0.74-10-02 [support]: The four-way taxonomy is documented as its own classification doctrine (`docs/governance/doc-type-taxonomy.md`) and each doc in the named initial set carries a declared type. Proof: `gz validate --documents` admits the doctrine doc + `artifact_edited` ledger events for the doctrine doc and each tagged doc.
<!-- gz-validate-skip: command-shape -->
- [ ] REQ-0.0.74-10-03 [behavior]: Given the ONE MX term as it appears across the `gz mx` tool, the gz-mx skill, the MX rule, and the marker, when `gz validate --mx-term-alignment` runs and the term drifts on any one surface, then the guard fails closed (exit 3); when all four agree it passes. (@covers test in `tests/governance/test_doc_type.py`)

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

Before: agents could not reliably tell a binding law from an explanatory rationale from a procedure (maintenance-guide.md § 1.2), so they vibed across the seam; and nothing proved the ONE MX term stayed the same across the tool, the skill, the rule, and the marker. Now: every named governance doc declares a binding-class the `--doc-type` guard enforces, and `--mx-term-alignment` proves the one word everywhere on every run — naked doctrine is no longer rationalized away, because the doctrine ships with its coupled enforcement.

### Key Proof

### Implementation Summary

- **Decision item 10 (verbatim):** "The governance doc-type taxonomy. Classify governance docs Doctrinal / Lawful / Ordinance / Ops-spec, tag them, and add a guard that keeps the ONE term aligned across tool / skill / rule / marker (fail closed on lexical drift)."
- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- gz-validate-skip: command-shape -->
- Sequencing dependency (tracked here per AGENTS.md § PRIME DIRECTIVE #6, brief evidence section — no GHI): the lexical-alignment guard (REQ-10-03) reads the ONE MX term from the marker (OBPI-0.0.74-01), the gz-mx skill + MX rule (OBPI-0.0.74-08), and the `gz mx` tool (OBPI-0.0.74-04/05); those surfaces MUST exist before this guard can bind. This OBPI is sequenced last in the ADR.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
