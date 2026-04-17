---
id: OBPI-0.0.16-01-validate-frontmatter-guard
parent: ADR-0.0.16
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.16-01-validate-frontmatter-guard: gz validate --frontmatter guard

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- **Checklist Item:** #1 - "Guard function: gz validate --frontmatter parses every ADR/OBPI file, compares four governed fields against ledger graph, emits per-file per-field drift report (human + JSON); --adr single-file scope and --explain remediation mode; exit codes per CLI doctrine 4-code map"

**Status:** Draft

## Objective

Add a `--frontmatter` flag to `gz validate` that parses every ADR/OBPI file in `docs/design/adr/**` and compares four governed frontmatter fields (`id`, `parent`, `lane`, `status`) against the ledger's artifact-graph equivalent, emitting a per-file per-field drift report in human and `--json` modes. Scope is strictly the four governed fields; ungoverned frontmatter (`tags:`, `related:`, free-form keys) is ignored. The validator is pure Python, reads the ledger via the same API `gz adr report` uses for lifecycle (no reimplementation), and is exclusively a gate-time / ad-hoc check — it never mutates files. Supports `--adr <ID>` single-file scope and `--explain <ADR-ID>` that prints step-by-step remediation per drifted field. No gate wiring yet (that's OBPI-02), no chore (OBPI-03), no backfill (OBPI-04). This brief is pure validator-layer.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/commands/validate.py` — add `--frontmatter` subcommand/option to existing validate surface
- `src/gzkit/commands/validate_frontmatter.py` — new module if separation is cleaner than inline
- `src/gzkit/cli/parser_artifacts.py` — register `--frontmatter` flag per CLI doctrine
- `tests/commands/test_validate_frontmatter.py` — unit tests for validator behavior and exit codes
- `docs/user/commands/validate.md` — document `--frontmatter`, `--adr`, `--explain` options
- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md` — parent ADR for intent and scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `gz validate --frontmatter` parses every ADR file under `docs/design/adr/**` and every OBPI file under `**/obpis/**` and compares exactly four fields against the ledger's artifact graph: `id`, `parent`, `lane`, `status`.
2. REQUIREMENT: ALWAYS key the ledger lookup on the file's canonical filesystem path, NEVER on the frontmatter `id:` value. (Keying on `id:` reproduces GHI #166; path-keyed lookup is the fix.)
3. REQUIREMENT: If the ledger graph does not expose a path→artifact mapping today, the OBPI STOPs with a BLOCKER naming the missing API and opens a follow-on ADR scoping the ledger schema extension before proceeding. NEVER reimplement a path→id index inside the validator.
4. REQUIREMENT: The validator reads lifecycle state via the same API `gz adr report` uses. It NEVER reimplements lifecycle derivation.
5. REQUIREMENT: Ungoverned frontmatter keys (`tags:`, `related:`, and any key outside the four governed fields) are IGNORED by the validator. The validator NEVER false-positives on a non-governed key.
6. REQUIREMENT: Default output is human-readable per-file per-field drift (ledger value vs frontmatter value). `--json` emits structurally equivalent JSON to stdout; logs to stderr. Empty-input and fully-coherent repos produce empty output bodies (not "no drift" prose).
7. REQUIREMENT: `--adr <ID>` restricts validation to a single artifact. `--explain <ADR-ID>` prints a step-by-step remediation per drifted field, each step naming an executable recovery command (`gz adr promote`, `gz chore run frontmatter-ledger-coherence`, `gz register-adrs`). Remediation NEVER suggests hand-editing frontmatter.
8. REQUIREMENT: Exit codes follow the CLI doctrine 4-code map: `0` clean, `1` user/config error (missing target, malformed ADR ID), `2` system/IO error, `3` policy breach (drift found). Exit codes are documented in `--help`.
9. REQUIREMENT: The validator NEVER mutates files. Reconciliation is OBPI-03's responsibility (chore).
10. REQUIREMENT: The validator does NOT wire into `gz gates` in this OBPI. Gate integration is OBPI-02.
11. REQUIREMENT: Runtime budget: < 1.0s total on the current repo (~80 ADRs, ~200 OBPIs). Measured via a test that invokes the validator on the real repo and asserts wall-clock under budget.
12. REQUIREMENT: Unit tests cover: (a) clean repo → exit 0, empty output; (b) seeded frontmatter-status drift → exit 3, drift line for that file; (c) seeded frontmatter-lane drift → exit 3; (d) seeded frontmatter-parent drift → exit 3; (e) seeded frontmatter-id drift where path is still canonical → exit 3, lookup succeeded via path; (f) `--adr <ID>` scopes output to one file; (g) `--json` output is structurally equivalent; (h) ungoverned-key drift does not trigger exit 3; (i) `--explain` emits at least one recovery-command line per drifted field.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/**`
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
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.16-01-01: Given a fully coherent repo, when `gz validate --frontmatter` runs, then it exits 0 with no drift output.
- [ ] REQ-0.0.16-01-02: Given an ADR file with `status:` drifted from the ledger, when `gz validate --frontmatter` runs, then it exits 3 and prints a drift line citing the file path, field name, ledger value, and frontmatter value.
- [ ] REQ-0.0.16-01-03: Given an ADR file with frontmatter `id:` rewritten but the file path unchanged, when `gz validate --frontmatter` runs, then the validator still resolves the artifact via path-keyed lookup and reports the `id:` drift (never silently trusts the drifted id).
- [ ] REQ-0.0.16-01-04: Given any frontmatter key outside the four governed fields, when the validator runs, then the key is ignored and does not trigger exit 3.
- [ ] REQ-0.0.16-01-05: Given `--json` is passed, when the validator runs against a drifted repo, then stdout contains a valid JSON document with a `drift` array whose entries have `path`, `field`, `ledger_value`, `frontmatter_value` keys.
- [ ] REQ-0.0.16-01-06: Given `--explain ADR-X.Y.Z`, when that ADR has drift, then the explain output contains at least one line naming an executable `gz` recovery command per drifted field.
- [ ] REQ-0.0.16-01-07: Given `--adr ADR-X.Y.Z`, when the validator runs, then output is scoped to that artifact only; other drifted artifacts are not mentioned.
- [ ] REQ-0.0.16-01-08: Given the full repo at current scale (~80 ADRs, ~200 OBPIs), when the validator runs, then total wall-clock is under 1.0s (measured by test).

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
