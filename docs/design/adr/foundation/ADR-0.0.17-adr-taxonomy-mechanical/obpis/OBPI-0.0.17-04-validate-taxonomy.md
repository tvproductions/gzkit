---
id: OBPI-0.0.17-04-validate-taxonomy
parent: ADR-0.0.17
item: 4
lane: Heavy
status: Draft
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
- `src/gzkit/cli/parser_artifacts.py` (register `--taxonomy` flag)
- `tests/governance/test_promoted_advisory_audits.py` (lock-in test)
- `tests/commands/test_validate.py` (dispatch test)
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

## Verification

```bash
uv run gz validate --taxonomy
uv run gz validate  # default scope must include taxonomy
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_promoted_advisory_audits tests.commands.test_validate -v
```

## Evidence

- `gz validate --taxonomy` clean run output
- Unit test output (negative cases covering each violation class)
- Scorecard entry diff
- ARB receipts

## REQ Coverage

- REQ-0.0.17-04-01 through REQ-0.0.17-04-10
