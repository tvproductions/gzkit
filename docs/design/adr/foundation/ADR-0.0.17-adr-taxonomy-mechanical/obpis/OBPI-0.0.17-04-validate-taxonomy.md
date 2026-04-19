---
id: OBPI-0.0.17-04-validate-taxonomy
parent: ADR-0.0.17-adr-taxonomy-mechanical
item: 4
lane: Heavy
status: Completed
---

# OBPI-0.0.17-04-validate-taxonomy: gz validate --taxonomy scope

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- **Checklist Item:** #4 — "`gz validate --taxonomy` scope + default-scope registration"

**Status:** Draft

## Objective

Add a `audit_adr_taxonomy` function to `src/gzkit/governance/trust_audits.py` and wire it into `gz validate` as both a default-scope check (runs under bare `gz validate`) and a discrete `--taxonomy` flag. The audit reads every ADR under `docs/design/adr/**` and enforces kind/semver/id consistency.

## Lane

**Heavy** — CLI surface addition; new audit that fires at pre-commit (via the governance test that locks it to a clean tree).

## Allowed Paths

- `src/gzkit/governance/trust_audits.py` (new `audit_adr_taxonomy` function)
- `src/gzkit/commands/validate_cmd.py` (register default + explicit scope)
- `src/gzkit/cli/parser_maintenance.py` (register `--taxonomy` flag — corrected from the brief's original `parser_artifacts.py`; the `gz validate` parser is in `parser_maintenance.py`)
- `tests/governance/test_promoted_advisory_audits.py` (lock-in test + negative cases)
- `tests/commands/test_validate_cmds.py` (dispatch test)
- `docs/user/commands/validate.md`
- `docs/governance/advisory-rules-audit.md` (scorecard entry)

## Denied Paths

- Schema/model (OBPI-01)
- `gz plan create` / `gz adr promote` (OBPI-02, 03)
- Backfill operations (OBPI-05)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `audit_adr_taxonomy(project_root: Path) -> list[ValidationError]` walks every `ADR-*.md` and `ADR-pool.*.md` under `docs/design/adr/**` and returns a `ValidationError` for each violation. It NEVER mutates files.
2. REQUIREMENT: Pool detection is id-based. A file whose id starts with `ADR-pool.` is treated as pool; a `kind:` frontmatter field on a pool ADR IS a violation (pool kind is id-derived, not frontmatter-derived per ADR-0.0.17 § Decision key axis #3).
3. REQUIREMENT: A non-pool ADR missing `kind:` is a violation. Message names the file and cites both `foundation` and `feature` options with their criteria.
4. REQUIREMENT: `kind: foundation` with a semver NOT matching `^0\.0\.\d+$` is a violation. Message names the current semver and the foundation-semver-range constraint.
5. REQUIREMENT: `kind: feature` with a semver matching `^0\.0\.\d+$` is a violation. Message names the current semver and the feature-semver constraint.
6. REQUIREMENT: `kind: <anything-other-than-foundation-or-feature>` is a violation. (Schema should already reject this at OBPI-01 level; validator is a defense-in-depth backup.)
7. REQUIREMENT: Pool ADRs with `semver:` fields do NOT trigger violations (pool ADRs may carry hint fields for future promotion). Pool ADRs with `lane:` fields do NOT trigger violations. Only the `kind:` presence on a pool ADR is a violation.
8. REQUIREMENT: Registered in `_default_scope_runners` so bare `gz validate` runs the check. Also accessible via `gz validate --taxonomy`. The `--taxonomy` flag appears in `gz validate --help`.
9. REQUIREMENT: A lock-in test under `tests/governance/test_promoted_advisory_audits.py::PromotedAdvisoryAudits::test_adr_taxonomy_rule_X` calls `audit_adr_taxonomy(_PROJECT_ROOT)` and `self._assert_clean(...)` — the test must pass on the current tree AFTER OBPI-05's backfill completes.
10. REQUIREMENT: Entry in `docs/governance/advisory-rules-audit.md` scorecard marking the rule as Mechanical.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` / `CLAUDE.md` — agent operating contract
- [x] Parent ADR — understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- [x] Sibling OBPIs in same ADR (OBPI-01 schema, OBPI-02/03 CLI, OBPI-05 backfill)

**Prerequisites (check existence, STOP if missing):**

- [x] OBPI-01 (schema + Pydantic model) landed — schema already includes `kind`
- [x] `gz validate` parser location identified — `src/gzkit/cli/parser_maintenance.py` (brief's original `parser_artifacts.py` corrected)

**Existing Code (understand current state):**

- [x] `src/gzkit/governance/trust_audits.py` audit family reviewed
- [x] `src/gzkit/commands/validate_cmd.py` default/explicit scope conventions reviewed
- [x] Sibling advisory audits (`audit_pool_adr_isolation`, `audit_version_release`) reviewed as precedent

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [x] Tests derived from brief acceptance criteria, not from implementation
- [x] Red-Green-Refactor cycle followed per behavior increment
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated (`docs/user/commands/validate.md`, scorecard)

### Gate 4: BDD (Heavy only)

- [ ] N/A — audit is an internal validator check, not an operator workflow; matches precedent (`audit_pool_adr_isolation`, `audit_version_release`). BDD scenarios can land with the backfill ceremony if needed.

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded (see Evidence)

## Verification

```bash
uv run gz validate --taxonomy
uv run gz validate  # default scope must include taxonomy
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_promoted_advisory_audits tests.commands.test_validate_cmds -v
```

## Evidence

### Gate 1 (ADR)

- Intent and scope recorded in this brief; parent ADR-0.0.17 line 50-56 explicitly authorizes OBPI-04 as the validator leg of the schema/CLI/validator triple.

### Gate 2 (TDD — Red-Green-Refactor)

Red cycle verified: tests authored before implementation failed with ImportError for `audit_adr_taxonomy` and argparse rejection of `--taxonomy`. Green cycle: implemented `audit_adr_taxonomy` + `_parse_adr_frontmatter`, registered `taxonomy` scope in default + explicit runners, added `--taxonomy` flag — 9 negative-case tests + 3 dispatch tests + 1 scorecard-entry test all pass; full `uv run -m unittest -q` reports 3231 pass, 1 skip.

```text
$ uv run gz test --obpi OBPI-0.0.17-04
Ran 14 tests in 0.123s
OK (skipped=1)
OBPI-scoped unit tests passed (14 tests).

$ uv run gz arb step --name unittest -- uv run -m unittest -q
Ran 3231 tests in 103.209s
OK (skipped=1)
ARB receipt: arb-step-unittest-143457240067483e8c69417c6400fd32

$ uv run gz covers OBPI-0.0.17-04 --json
  "summary": {
    "total_reqs": 10,
    "covered_reqs": 10,
    "uncovered_reqs": 0,
    "coverage_percent": 100.0
  }
```

### Code Quality

```text
$ uv run gz arb ruff
arb ruff exit_status=0 receipt=arb-ruff-16720a1725db455ba97b627b939e2703

$ uv run gz arb typecheck
All checks passed!
arb step name=typecheck exit_status=0 receipt=arb-step-typecheck-3d7b91660fa947ccb7faa4c9a54c888c
```

### Gate 3 (Docs)

```text
$ uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
Documentation built in 3.67 seconds
arb step name=mkdocs exit_status=0 receipt=arb-step-mkdocs-003d159458304600b06c29f92e4b2873
```

### Gate 4 (BDD)

N/A for this OBPI — audit is an internal validator check with no operator workflow; matches precedent (`audit_pool_adr_isolation`, `audit_version_release`).

### Gate 5 (Human)

See Human Attestation section below.

### Value Narrative

Before this OBPI, the ADR taxonomy (`pool` / `foundation` / `feature`) from ADR-0.0.17 was mechanically enforced only by JSON schema at authoring time; nothing audited the live tree for kind/semver/id drift. Adopters could hand-edit frontmatter into inconsistent shapes and pre-existing ADRs had no mechanical way to surface their missing-`kind:` drift. After this OBPI, `gz validate --taxonomy` walks every ADR under `docs/design/adr/**` and flags every violation of the six-rule contract (pool id-derived, foundation ⇒ `0.0.x`, feature ⇒ other, unknown kind rejected, pool frontmatter kind rejected, pool semver/lane tolerated). The audit runs under bare `gz validate` as a default scope and is also accessible as a discrete flag for focused invocation — 47 real pre-existing violations surfaced on the live tree, closed by the next OBPI's one-time backfill.

### Key Proof


```text
$ uv run gz validate --taxonomy
Validated: taxonomy

❌ Validation failed with 47 error(s):

   →  docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/...
    Non-pool ADR is missing `kind:` frontmatter. Add `kind: foundation` for an
    app/system invariant ADR (semver `0.0.x`) or `kind: feature` for a capability
    ADR (semver `0.y.z` and up). See ADR-0.0.17 / ADR-0.0.18.
   ...
$ echo $?
1
```

47 real violations deliberately surfaced as the drift-detection role of the audit. Every violation's recovery path is named in the message; the next OBPI's backfill closes them and un-skips the live-tree lock-in test (REQ-0.0.17-04-09).

### Implementation Summary


- Files created/modified:
  - `src/gzkit/governance/trust_audits.py` — new `audit_adr_taxonomy` + `_parse_adr_frontmatter` helper + `__all__` entry. Stdlib-only frontmatter parse (matches every sibling `audit_*` — no PyYAML widening of the trust-audit module's surface).
  - `src/gzkit/commands/validate_cmd.py` — `check_taxonomy` parameter threaded through `validate()` / `_collect_errors` / `_run_scope_checks` / `_resolve_scopes`; `taxonomy` registered in `default_scopes` dict, `_default_scope_runners`, `_explicit_scope_runners`, and `run_all_scopes` list; `_taxonomy_runner` lazy-imports `trust_audits` to preserve import-time discipline.
  - `src/gzkit/cli/parser_maintenance.py` — `--taxonomy` flag + `check_taxonomy=a.check_taxonomy` in dispatch lambda.
  - `tests/governance/test_promoted_advisory_audits.py` — 1 skipped lock-in (`test_adr_taxonomy_rule_X`, `@covers REQ-0.0.17-04-09`); 9 tempdir-fixture negative-case tests in `TaxonomyAuditNegativeCases`; 1 scorecard-entry test (`test_taxonomy_scorecard_entry_exists`, `@covers REQ-0.0.17-04-10`).
  - `tests/commands/test_validate_cmds.py` — `TestValidateTaxonomyFlag` class with 3 dispatch tests (clean-tree-passes, missing-kind-detected, pool-kind-detected), all `@covers REQ-0.0.17-04-08`.
  - `docs/user/commands/validate.md` — `### --taxonomy` section + updated usage line.
  - `docs/governance/advisory-rules-audit.md` — row 6a (Mechanical) citing GHI #218 / ADR-0.0.17.
  - This brief — Allowed Paths corrected (`parser_artifacts.py` → `parser_maintenance.py`); Acceptance Criteria, Discovery Checklist, Quality Gates, Evidence / Implementation Summary / Key Proof / Human Attestation sections added.
- Tests added: 13 unit tests (1 skipped), all `@covers`-decorated; 100% REQ parity via `gz covers`.
- Date completed: 2026-04-19.
- Attestation status: attested completed (Heavy lane).
- Defects noted: 2 tracked (see Tracked Defects below).

## Tracked Defects

- **Pool ADR without `id:` frontmatter.** `docs/design/adr/pool/ADR-pool.gz-preflight-health-orchestration.md` lacks the `id:` frontmatter field entirely and is therefore classified as non-pool by the id-based detection per REQ-02. Backfill scope; the one-time backfill OBPI needs to add the missing id (or equivalent) to every pool file that lacks one.
- **`gz obpi precomplete` lock-path defect (GHI #245).** `src/gzkit/commands/obpi_precomplete.py:186` globs `.gzkit/locks/*.json` but `gz obpi lock claim` writes to `.gzkit/locks/obpi/<id>.lock.json`. Surfaced during this ceremony; filed and out of scope for this brief.

## Human Attestation

- Attestor: `Jeffry Babb (redacted-email)`
- Attestation: attest completed — Confirm decision: gz validate --taxonomy registered as default + explicit scope (--taxonomy flag in parser_maintenance.py); audit_adr_taxonomy walks docs/design/adr/** with stdlib-only frontmatter parse, non-mutating, returns ValidationError list per ADR-0.0.17 § Decision key axis #3 (pool id-derived, foundation ⇒ 0.0.x, feature ⇒ other). 10/10 REQs covered (gz covers OBPI-0.0.17-04 100%); 9 negative-case fixtures deterministic in tempdir; 3231 unittests pass (1 skip = live-tree lock-in deferred to next OBPI backfill, explicit reference in @unittest.skip); 47 live-tree violations surfaced — intended drift-detection, not a gate defect (brief REQ-09 acknowledges post-backfill pass). Brief Allowed Paths corrected in-patch (parser_artifacts.py → parser_maintenance.py where validate parser actually lives). Filed GHI #245 for pre-existing gz obpi precomplete lock-path defect. Receipts: lint arb-ruff-16720a1725db455ba97b627b939e2703; types arb-step-typecheck-3d7b91660fa947ccb7faa4c9a54c888c; tests arb-step-unittest-143457240067483e8c69417c6400fd32; negative-cases arb-step-taxonomy-negative-cases-2661487aa8754f80a3084b912a65f0e6; mkdocs arb-step-mkdocs-003d159458304600b06c29f92e4b2873.
- Date: 2026-04-19

## Acceptance Criteria

- [ ] REQ-0.0.17-04-01: `audit_adr_taxonomy(project_root)` walks every ADR under `docs/design/adr/**` and never mutates files
- [ ] REQ-0.0.17-04-02: pool ADR carrying a `kind:` frontmatter field is a violation
- [ ] REQ-0.0.17-04-03: non-pool ADR missing `kind:` frontmatter is a violation (message cites both foundation and feature options)
- [ ] REQ-0.0.17-04-04: `kind: foundation` with non-`0.0.x` semver is a violation (message names the current semver)
- [ ] REQ-0.0.17-04-05: `kind: feature` with `0.0.x` semver is a violation (message names the current semver)
- [ ] REQ-0.0.17-04-06: `kind:` value other than `foundation` or `feature` on non-pool ADR is a violation
- [ ] REQ-0.0.17-04-07: pool ADRs carrying `semver:` or `lane:` fields do NOT trigger violations
- [ ] REQ-0.0.17-04-08: registered in `_default_scope_runners` and accessible via `gz validate --taxonomy`; flag appears in `--help`
- [ ] REQ-0.0.17-04-09: lock-in test calls `audit_adr_taxonomy(_PROJECT_ROOT)` and `self._assert_clean(...)`; must pass on the live tree after the taxonomy backfill lands
- [ ] REQ-0.0.17-04-10: scorecard entry in `docs/governance/advisory-rules-audit.md` marks the rule Mechanical

## REQ Coverage

- REQ-0.0.17-04-01 through REQ-0.0.17-04-10
