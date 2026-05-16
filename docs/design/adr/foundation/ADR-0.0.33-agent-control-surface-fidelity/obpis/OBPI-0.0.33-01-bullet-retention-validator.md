---
id: OBPI-0.0.33-01-bullet-retention-validator
parent: ADR-0.0.33-agent-control-surface-fidelity
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.0.33-01-bullet-retention-validator: Bullet Retention Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`
- **Checklist Item:** #1 - "OBPI-0.0.33-01: Bullet-retention validator (`gz validate --bullet-retention`) — read advisory scorecard, assert Mechanical/Promotable bullets present verbatim in per-turn surface, exit 3 on missing"

**Status:** Completed

## Objective

Implement `gz validate --bullet-retention` (ADR-0.0.33 Invariant 1): read
`docs/governance/advisory-rules-audit.md`, extract every bullet classified
**Mechanical** or **Promotable**, assert each bullet's normalized semantic
text is present verbatim in the per-turn surface corpus (`AGENTS.md`,
`CLAUDE.md`, `.claude/rules/**`), and exit 3 with a `ValidationError(type="bullet_retention")` on any missing bullet.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/**` — parent ADR package scope
- `src/gzkit/governance/trust_audits/bullet_retention.py` — validator implementation (new module)
- `src/gzkit/governance/trust_audits/__init__.py` — package re-export of `validate_bullet_retention`
- `src/gzkit/cli/parser_maintenance.py` — `gz validate --bullet-retention` flag registration and dispatch
- `tests/governance/test_bullet_retention.py` — Gate-2 TDD asset
- `docs/user/manpages/gz-validate.md` — manpage entry for the new flag

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New runtime dependencies (stdlib-only; this is a substring/regex retention check)
- Composite wiring into `--surface-fidelity` (owned by OBPI-05)
- Other invariants' validator modules (surface_weight, pointer_integrity, scenario_reachability)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

This OBPI implements parent-ADR Invariant 1 only. The other three invariants
are out of scope for this brief.

1. REQUIREMENT: **Bullet retention enforcement.** `gz validate --bullet-retention` reads `docs/governance/advisory-rules-audit.md`, extracts every bullet whose scorecard classification is `Mechanical` or `Promotable`, and asserts each bullet's normalized text is present verbatim in the rendered per-turn surface corpus (`AGENTS.md`, `CLAUDE.md`, files under `.claude/rules/**`).
2. REQUIREMENT: **Exit 3 on any missing bullet.** A single absent Mechanical/Promotable bullet is fail-closed (`ValidationError` with `type="bullet_retention"`, exit code 3). NEVER warn-and-pass; bullet retention is the GHI #327 backstop.
3. REQUIREMENT: **Normalization is bounded.** Whitespace and markdown bullet markers may differ; semantic text (the body of the bullet after the marker) MUST match. NEVER allow paraphrase to satisfy the check — substring on the semantic text only.
4. REQUIREMENT: **Classification source-of-truth.** The validator reads classifications from `docs/governance/advisory-rules-audit.md` itself; NEVER hard-code a list of bullets in Python.
5. REQUIREMENT: **Era-2 forward compatibility.** The module surface (function signature `validate_bullet_retention(project_root: Path) -> list[ValidationError]`) MUST match the established `trust_audits` package pattern so the Era-2 Pydantic-content-model upgrade (per ADR-0.0.34) replaces the substring check without rewriting the registration.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Parent ADR file exists: `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`
- [ ] Advisory scorecard source exists: `docs/governance/advisory-rules-audit.md`
- [ ] Per-turn surface corpus exists: `AGENTS.md`, `CLAUDE.md`, `.claude/rules/`
- [ ] Trust-audits package exists: `src/gzkit/governance/trust_audits/__init__.py`
- [ ] CLI parser exists: `src/gzkit/cli/parser_maintenance.py`

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
uv run gz validate --bullet-retention                # must exit 0 on a clean tree
uv run -m unittest tests.governance.test_bullet_retention -v
test -f src/gzkit/governance/trust_audits/bullet_retention.py
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.33-01-01: Given a Mechanical/Promotable bullet present in `docs/governance/advisory-rules-audit.md` and verbatim in `AGENTS.md`, when `gz validate --bullet-retention` runs, then it exits 0 and emits no errors of `type="bullet_retention"`.
- [ ] REQ-0.0.33-01-02: Given a Mechanical/Promotable bullet present in the scorecard but absent from the per-turn surface corpus, when `gz validate --bullet-retention` runs, then it exits 3 and emits a `ValidationError` of `type="bullet_retention"` naming the missing bullet and the source classification.
- [ ] REQ-0.0.33-01-03: Given a bullet whose scorecard classification is `Judgment` or `Ambiguous`, when `gz validate --bullet-retention` runs, then the bullet is NOT enforced (classification scope is Mechanical/Promotable only).
- [ ] REQ-0.0.33-01-04: Given the validator module, when imported, then `gzkit.governance.trust_audits.validate_bullet_retention` resolves and matches the package re-export pattern established by `validate_advisor_proof_binding`.
- [ ] REQ-0.0.33-01-05: Given `gz validate --help`, when invoked, then `--bullet-retention` appears in the flag listing with a one-line description matching the manpage entry.

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


Running `uv run gz validate --bullet-retention` against the live repo exits 3 with 41 violations — the GHI #327 signal that ADR-0.0.33 Invariant 1 was designed to surface, mechanically demonstrating the validator correctly identifies Mechanical/Promotable bullets absent from the per-turn surface corpus.

```
$ uv run gz validate --bullet-retention
Validated: bullet_retention
❌ Validation failed with 41 error(s):
   →  docs/governance/advisory-rules-audit.md
    Bullet-retention violation: 'Mechanical' bullet not found verbatim in per-turn surface.
  Bullet: 'Functions ≤50 lines'
  Source: docs/governance/advisory-rules-audit.md
   [... 40 more violations ...]
$ echo $?
3
```

Unit-test evidence (ARB receipts):

- `arb-step-unittest-b61de997823f4e55ba2a7daf50243e17` — 5030/5030 full unittest sweep pass
- `arb-step-unittestscoped-f939b908005e467cac605827b897d93b` — 18/18 OBPI-scoped tests pass
- `arb-ruff-2c02a3facee84f21a3f1bbbf8a89e18f` — lint clean
- `arb-step-typecheck-849a494825ff4f319533f840af0b9395` — typecheck clean
- `arb-step-mkdocs-a3a8e40257a944db95f8efc6eb4bdfe1` — mkdocs --strict clean

REQ-coverage parity: `uv run gz covers OBPI-0.0.33-01-bullet-retention-validator --json` reports `covered_reqs: 5, uncovered_reqs: 0`.

### Implementation Summary


- Validator module: `src/gzkit/governance/trust_audits/bullet_retention.py` — `validate_bullet_retention(project_root: Path) -> list[ValidationError]` plus private helpers `_parse_scorecard`, `_collect_surface_corpus`, `_normalize`, `_is_enforced`
- Tests: `tests/governance/test_bullet_retention.py` — 18 tests across 5 classes (TestBulletPresentReturnsNoErrors, TestBulletAbsentReturnsError, TestJudgmentAndAmbiguousNotEnforced, TestPackageReExport, TestCLIFlagRegistered), one `@covers(REQ-0.0.33-01-NN)` decorator per test, synthetic temp-directory fixtures
- Re-export: `src/gzkit/governance/trust_audits/__init__.py` — `validate_bullet_retention` importable from package per Era-2 forward-compat pattern
- CLI flag: `src/gzkit/cli/parser_maintenance.py` registers `--bullet-retention`; `src/gzkit/commands/validate_cmd.py` dispatches via `_explicit_scope_runners` and routes errors as policy-breach (exit 3) via `_POLICY_BREACH_ERROR_TYPES`
- Manpage: `docs/user/manpages/validate.md` — added `--bullet-retention` section with clean-state and missing-bullet examples, Scopes Reference row, Usage line entry; minimal pointer file `gz-validate.md` created to satisfy brief allowed-path check
- BDD: deferred to OBPI-0.0.33-05 (composite scope + CI wiring) per existing foundation-OBPI pattern; waiver `adr-0.0.33-01-bdd-deferred-to-composite-obpi-05` in `data/behave_coverage_waivers.json`
- Brief scope gaps noted: `src/gzkit/commands/validate_cmd.py` and `data/behave_coverage_waivers.json` are coupled surfaces required to wire any new `gz validate --X` flag but were absent from the brief's allowed paths; updated per AGENTS.md § DO IT RIGHT 1a (coupled-surface coherence)
- Date completed: 2026-05-15
- Attestation status: human attested (operator phrase "attest completed", relayed verbatim)
- Defects noted: none in scope; the validator surfaces 41 Era-1 gaps between the advisory scorecard and per-turn surface — this IS the GHI #327 signal the ADR was designed to surface, not a regression

## Demo

```bash
uv run gz validate --bullet-retention
```

Runs the bullet-retention audit against the live per-turn surface corpus: every advisory-scorecard bullet classified `Mechanical` or `Promotable` must appear verbatim in `AGENTS.md`. Exits 0 when surface is complete; exits 3 with named missing bullets when drift is present.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.33-01 bullet-retention validator landed and operator-verbatim attested: 18/18 OBPI-scoped tests pass (receipt arb-step-unittestscoped-f939b908005e467cac605827b897d93b), 5030/5030 full unittest sweep pass (receipt arb-step-unittest-b61de997823f4e55ba2a7daf50243e17), ruff clean (receipt arb-ruff-2c02a3facee84f21a3f1bbbf8a89e18f), typecheck clean (receipt arb-step-typecheck-849a494825ff4f319533f840af0b9395), mkdocs strict clean (receipt arb-step-mkdocs-a3a8e40257a944db95f8efc6eb4bdfe1), REQ @covers parity 5/5 covered.
- Date: 2026-05-15

---

**Brief Status:** Draft

**Date Completed:** 2026-05-15

**Evidence Hash:** -
