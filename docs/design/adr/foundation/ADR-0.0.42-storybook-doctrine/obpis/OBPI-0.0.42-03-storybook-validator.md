---
id: OBPI-0.0.42-03-storybook-validator
parent: ADR-0.0.42-storybook-doctrine
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.42-03-storybook-validator: gz validate --storybook-fresh + structural validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.42-storybook-doctrine/ADR-0.0.42-storybook-doctrine.md`
- **Checklist Item:** #3 — "`gz validate --storybook-fresh` + structural validator — Anchor staleness check + per-ADR STORY.md presence (non-pool only) + arc-type frontmatter validation. Separate `gz storybook validate --arc <slug>` for structural issues distinct from freshness. Wires into `gz check`."

**Status:** Draft

## Objective

Land two validator scopes: (1) `gz validate --storybook-fresh` — anchor staleness + per-ADR STORY.md presence (non-pool ADRs only) + arc-type frontmatter conformance, fail-closed and wired into `gz check`. (2) `gz storybook validate --arc <slug>` — structural validation of one arc's frontmatter, marker-pair presence, and schema conformance, separate from freshness so that broken arcs can be diagnosed without a full freshness sweep.

## Lane

**Heavy** — new validator scope, new fail-closed exit path, wires into the existing `gz check` pipeline. External-contract change per AGENTS.md.

## Allowed Paths

- `src/gzkit/governance/` — directory exists; OBPI authors `storybook_audits.py` (or co-locates with existing `trust_audits.py`) for the freshness/structural validator scopes
- `src/gzkit/cli/` — directory exists; OBPI extends existing `validate` parser with `--storybook-fresh` flag and existing `storybook` parser with `validate --arc` subverb
- `tests/governance/` — exists; OBPI adds storybook freshness tests
- `tests/cli/` — exists; OBPI adds structural validator CLI tests
- `docs/governance/advisory-rules-audit.md` — exists; OBPI adds scorecard entry
- `.gzkit/rules/` — directory exists; OBPI authors `storybook-doctrine.md` (or section in existing file)
- `docs/user/manpages/` — exists; OBPI authors `gz-storybook-validate.md` and either updates `gz-validate.md` with `--storybook-fresh` section or authors a sibling manpage

## Denied Paths

- `docs/user/storybook/` — arc files are OBPI-01 scope
- `src/gzkit/schemas/storybook.json` — schema is OBPI-01 scope
- `src/gzkit/storybook/` — runtime module is OBPI-02 scope (validator imports from it but does not modify it)
- `.gzkit/skills/gz-adr-create/**` — STORY.md scaffolding is OBPI-04 scope
- New runtime dependencies, lockfiles, CI configuration

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (anchor staleness check):** `gz validate --storybook-fresh` MUST recompute each arc's expected anchor block in-memory and compare against committed content. Drift between in-memory recomputation and committed bytes MUST fail closed (exit 3).
2. **REQUIREMENT (per-ADR STORY.md presence — non-pool only):** For every non-pool ADR (kind in `{foundation, feature}`), the validator MUST verify a `STORY.md` file exists inside the ADR package directory. Missing STORY.md MUST fail closed. Pool ADRs (under `docs/design/adr/pool/`) are exempt — pool stubs already capture intent at value-claim altitude.
3. **REQUIREMENT (arc-type frontmatter):** Every arc file MUST carry valid `arc-type` frontmatter restricted to the schema enum `{journey, capability-bundle, capability-family}`. Missing or invalid `arc-type` MUST fail closed.
4. **REQUIREMENT (`gz check` integration):** `--storybook-fresh` MUST run as part of the default `gz check` pipeline, with the same fail-closed semantics as `--adr-status-fresh`.
5. **REQUIREMENT (structural validator separate scope):** `gz storybook validate --arc <slug>` MUST validate one arc's frontmatter conformance, marker-pair presence, and schema enum without performing freshness recomputation. This separation lets operators diagnose structural issues at 2am without running a full freshness sweep.
6. **REQUIREMENT (advisory scorecard entry):** A new entry MUST be added to `docs/governance/advisory-rules-audit.md` classifying the storybook freshness/structural rule as Mechanical, with the validator implementation cited as the enforcement artifact.
7. **REQUIREMENT (rule file):** A canonical rule file MUST be authored (`.gzkit/rules/storybook-doctrine.md` or a clearly-named section) declaring the freshness/structural invariants, the deriver-vs-validator authority split, and the recovery commands.
8. **REQUIREMENT (per-ADR STORY.md presence is conditional on OBPI-04):** Until OBPI-04 lands the scaffolding, the per-ADR STORY.md presence check MAY be implemented as warn-only (exit 0 with diagnostic) and switch to fail-closed once OBPI-04 has populated the corpus. The implementation MUST emit an explicit ledger event (`storybook_validator_warn_only_phase`) on each warn-only run so the warn-only phase is auditable, and MUST switch to fail-closed automatically once a sentinel condition is met (e.g. all currently-Validated foundation ADRs have a STORY.md).

> STOP-on-BLOCKERS: if OBPI-01 has not landed (no schema), or if OBPI-02 has not landed (no anchor parser, no derive logic to invoke for staleness recompute), halt — this OBPI imports from both.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim.
- [ ] Parent ADR § Intent.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.42-storybook-doctrine/ADR-0.0.42-storybook-doctrine.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance:**

- [ ] `AGENTS.md` § Lane Rules
- [ ] `.gzkit/rules/governance-core.md` § ADR status index regeneration (precedent for `--adr-status-fresh`)
- [ ] `docs/governance/advisory-rules-audit.md` — scorecard format
- [ ] `docs/governance/state-doctrine.md` — Layer 1/2/3 doctrine

**Context:**

- [ ] OBPI-02's deriver — staleness recomputation reuses its anchor-rebuild logic
- [ ] Existing validator scopes (`--adr-status-fresh`, `--documents`, `--surfaces`) for shape precedent
- [ ] `gz check` pipeline registration (find in `src/gzkit/checks/` or equivalent)

**Prerequisites:**

- [ ] OBPI-01 landed: schema and arc files exist
- [ ] OBPI-02 landed: deriver module exists, can be imported by validator for staleness recompute

**Existing Code:**

- [ ] `src/gzkit/governance/trust_audits/` — existing audit-scope conventions
- [ ] `src/gzkit/commands/validate_cmd.py` — existing flag registration
- [ ] `src/gzkit/quality.py` — `gz check` aggregation pipeline

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #3 quoted in Implementation Summary
- [ ] Intent and scope recorded

### Gate 2: TDD

- [ ] Tests cover: stale-arc fails fresh, current-arc passes fresh, missing arc-type fails, invalid arc-type fails, missing STORY.md (non-pool) fails, missing STORY.md (pool) passes, structural validator on broken arc fails with structural-not-freshness diagnostic, warn-only phase emits expected ledger event
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Manpage for `gz storybook validate` exists
- [ ] `gz validate --help` lists `--storybook-fresh`
- [ ] Scorecard entry present in `docs/governance/advisory-rules-audit.md`
- [ ] Rule file present and consistent with implementation

### Gate 4: BDD (Heavy)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`
- [ ] At minimum: scenario where staleness is introduced, `gz check` fails closed; recovery via `gz storybook derive` makes `gz check` pass

### Gate 5: Human (Heavy + foundation)

- [ ] Human attestation recorded — foundation parent kind requires brief-level attestation

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz validate --advisory-scorecard

uv run gz validate --storybook-fresh                # passes when storybook is fresh
uv run gz storybook validate --arc from-init-to-first-attested-release   # structural pass

uv run gz check                                      # includes --storybook-fresh in default pipeline
```

## Demo

```bash
uv run gz validate --storybook-fresh                # shows fresh status

# Mutate strawman to introduce drift in anchor block (without running deriver):
uv run python -c "
import pathlib
p = pathlib.Path('docs/user/storybook/from-init-to-first-attested-release.md')
content = p.read_text()
# corrupt anchor block somehow
p.write_text(content.replace('ADR-0.0.1', 'ADR-0.0.999'))
"

uv run gz validate --storybook-fresh                # exit 3, names stale arc
uv run gz check                                      # also fails

uv run gz storybook derive --arc from-init-to-first-attested-release   # recovery
uv run gz validate --storybook-fresh                # passes again
```

## Acceptance Criteria

- [ ] REQ-0.0.42-03-01: Given an arc whose anchor block matches in-memory recomputation, when `gz validate --storybook-fresh` runs, then it exits 0.
- [ ] REQ-0.0.42-03-02: Given an arc whose committed anchor block diverges from in-memory recomputation, when `gz validate --storybook-fresh` runs, then it exits 3 with a diagnostic naming the stale arc and the diverged anchors.
- [ ] REQ-0.0.42-03-03: Given a non-pool ADR package without a `STORY.md` file, when `gz validate --storybook-fresh` runs in fail-closed phase, then it exits 3 with a diagnostic naming the missing ADR's package path.
- [ ] REQ-0.0.42-03-04: Given a pool ADR (in `docs/design/adr/pool/`), when `gz validate --storybook-fresh` runs, then it does not require `STORY.md` and does not flag the pool ADR.
- [ ] REQ-0.0.42-03-05: Given an arc with `arc-type: invalid-value` in frontmatter, when `gz validate --storybook-fresh` runs, then it exits 3 with a diagnostic naming the invalid value.
- [ ] REQ-0.0.42-03-06: Given `gz check` is invoked, when it runs, then `--storybook-fresh` is part of the default pipeline and any failure fails the overall check.
- [ ] REQ-0.0.42-03-07: Given an arc with a malformed marker pair (missing END marker, duplicate BEGIN), when `gz storybook validate --arc <slug>` runs, then it exits 3 with a structural diagnostic distinct from a freshness diagnostic.
- [ ] REQ-0.0.42-03-08: Given the warn-only phase (active until OBPI-04 has populated STORY.md corpus), when the validator runs, then it emits a `storybook_validator_warn_only_phase` ledger event making the phase auditable.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Full test suite covering both validator scopes and warn-only phase
- [ ] **Code Quality:** Lint, type check clean
- [ ] **Gate 3 (Docs):** mkdocs --strict + advisory scorecard + rule file consistent
- [ ] **Gate 4 (BDD):** Acceptance scenarios pass
- [ ] **Gate 5 (Human):** Attestation recorded (foundation parent requires)
- [ ] **Value Narrative:** Documented below
- [ ] **Key Proof:** Concrete validator failure + recovery output below
- [ ] **OBPI Acceptance:** Evidence recorded

## Evidence

### Gate 1 (ADR)

- [ ] Intent recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste validator test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs + advisory scorecard validation output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

<!-- Before: storybook arcs could silently drift away from artifact-graph reality; cohesion failures landed unnoticed. After: gz validate --storybook-fresh makes drift a fail-closed signal in gz check, while gz storybook validate --arc gives 2am operators a structural diagnostic distinct from freshness. -->

### Key Proof

```text
# Paste actual validator pass + induced-drift fail + recovery sequence
```

### Implementation Summary

- Files created/modified: `src/gzkit/governance/storybook_audits.py` (new), `src/gzkit/cli/validate.py`/`parser_validate.py` (extended), `src/gzkit/cli/storybook.py`/`parser_storybook.py` (extended with validate subverb), `src/gzkit/checks/` (pipeline integration), `docs/governance/advisory-rules-audit.md` (scorecard entry), `.gzkit/rules/storybook-doctrine.md` (rule file), manpages, tests under `tests/governance/` and `tests/cli/`
- Tests added: freshness, structural, STORY.md presence (non-pool only), warn-only phase, recovery roundtrip
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked at brief authoring time._

## Human Attestation

- Attestor: `<name>` (foundation parent kind requires)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
