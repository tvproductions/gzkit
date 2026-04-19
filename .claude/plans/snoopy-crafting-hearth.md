# Plan: OBPI-0.0.17-04 — `gz validate --taxonomy` scope

## Context

ADR-0.0.17 elevates the ADR taxonomy (`pool` / `foundation` / `feature`)
from an implicit semver convention into a first-class mechanical contract.
The schema + Pydantic model + `--kind` CLI scaffolders are already landed:
`src/gzkit/schemas/adr.json` requires `kind ∈ {foundation, feature}`, and
`gz plan create` / `gz adr promote` both expose `--kind`. Pool ADRs carry
their kind via the `ADR-pool.<slug>` id prefix, not frontmatter.

OBPI-0.0.17-04 closes the validator leg of the triple: a
`gz validate --taxonomy` scope that walks every ADR under
`docs/design/adr/**` and enforces kind / semver / id consistency. It joins
the `audit_*` family in `src/gzkit/governance/trust_audits.py`, registers
as both a discrete flag and a default-scope runner, and adds a scorecard
entry so `gz validate --advisory-scorecard` stays clean.

A separate future OBPI performs the one-time backfill that writes `kind:`
into every pre-0.0.17 ADR. Until that backfill lands, the current tree has
105+ non-pool ADRs missing `kind:` — so the lock-in test's `_assert_clean`
call must be `@unittest.skip(...)` with an explicit reference to the
pending backfill, per brief REQ-09 ("must pass on the current tree AFTER
the backfill completes"). The audit function itself is correct and fully
exercised via tempdir-fixture negative-case tests; only the live-tree
lock-in is deferred.

## Brief-path reconciliation (defect surfaced in flight)

Brief Allowed Paths list `src/gzkit/cli/parser_artifacts.py` as the home
for the `--taxonomy` flag, but the `gz validate` parser is actually
defined in `src/gzkit/cli/parser_maintenance.py` (lines 350–477, same
file that hosts `--version-release`, `--pool-adr-isolation`,
`--advisory-scorecard`, etc.). This is an Allowed Paths authoring defect.
Per Invariants 2/4 (scope expansion for in-flight defects), the patch
will:

1. Edit `parser_maintenance.py` (the correct file) alongside the
   brief-named paths.
2. Amend the brief's Allowed Paths to replace `parser_artifacts.py` with
   `parser_maintenance.py` in the same patch.
3. Note the correction in the OBPI brief's Evidence section.

This is a brief-authoring drift, not a routing change — the audit stays on
this OBPI's boundary.

## Critical files (touches)

| File | Change | REQ |
|---|---|---|
| `src/gzkit/governance/trust_audits.py` | Add `audit_adr_taxonomy(project_root)` + `_parse_adr_frontmatter` helper + `__all__` entry | REQ-01 … REQ-07 |
| `src/gzkit/commands/validate_cmd.py` | Register `taxonomy` runner in `_default_scope_runners` and `_explicit_scope_runners`; add `check_taxonomy` param; extend `_resolve_scopes` `run_all_scopes` | REQ-08 |
| `src/gzkit/cli/parser_maintenance.py` | Add `--taxonomy` flag; thread `check_taxonomy=a.check_taxonomy` into the dispatch lambda | REQ-08 |
| `tests/governance/test_promoted_advisory_audits.py` | Add skipped lock-in test + focused negative-case tests against tempdir fixtures | REQ-01…07, REQ-09 |
| `tests/commands/test_validate_cmds.py` | Add `--taxonomy` dispatch test (flag is recognized, routes to audit, exits 0 on clean fixture tree) | REQ-08 |
| `docs/user/commands/validate.md` | Add `### --taxonomy` section | REQ-08 |
| `docs/governance/advisory-rules-audit.md` | Add scorecard row (Mechanical) citing GHI #218 / ADR-0.0.17 | REQ-10 |
| `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/obpis/OBPI-0.0.17-04-validate-taxonomy.md` | Amend Allowed Paths: swap `parser_artifacts.py` → `parser_maintenance.py`; flip status `Draft` → `Proposed` during implementation, `Completed` at ceremony | brief-path defect |

## Implementation steps (TDD per REQ)

### Step 1 — Tests first (RED)

Write unit tests **before** any implementation so each REQ sees a failing
test that references the target symbol name:

- `tests/governance/test_promoted_advisory_audits.py`:
  - `test_adr_taxonomy_rule_X` — `@unittest.skip("unskip after ADR-0.0.17
    backfill lands")`; calls `audit_adr_taxonomy(_PROJECT_ROOT)` and
    `self._assert_clean(...)`.
  - A sibling `TaxonomyAuditNegativeCases` class using
    `tempfile.TemporaryDirectory()` + hand-written ADR stubs to exercise
    each violation class deterministically:
    - `test_pool_kind_frontmatter_is_violation` (REQ-02)
    - `test_non_pool_missing_kind_is_violation` (REQ-03)
    - `test_foundation_with_non_0_0_x_semver_is_violation` (REQ-04)
    - `test_feature_with_0_0_x_semver_is_violation` (REQ-05)
    - `test_unknown_kind_value_is_violation` (REQ-06)
    - `test_pool_with_semver_field_is_not_violation` (REQ-07a)
    - `test_pool_with_lane_field_is_not_violation` (REQ-07b)
    - `test_audit_never_mutates_files` (REQ-01) — hash file contents
      before and after, assert equal.
  - Each test uses `@covers("REQ-0.0.17-04-NN")` decorators so the Stage
    3 `@covers` parity gate sees every REQ reachable.

- `tests/commands/test_validate_cmds.py`:
  - `test_validate_taxonomy_flag_dispatches` — `_quick_init`, confirm
    `validate --taxonomy` runs and exits 0 on an empty ADR tree (fresh
    init has no ADRs → zero violations).
  - `test_validate_taxonomy_detects_missing_kind` — write a synthetic
    foundation ADR into the tmp tree missing `kind:`; assert non-zero
    exit + `taxonomy` in output.
  - Both decorated `@covers("REQ-0.0.17-04-08")`.

Run the suite. Every new test should fail (ImportError for
`audit_adr_taxonomy`, AttributeError for `check_taxonomy`, etc.). This is
RED.

### Step 2 — Implement the audit (GREEN for REQs 1–7)

In `src/gzkit/governance/trust_audits.py`:

```python
_FOUNDATION_SEMVER_RE = re.compile(r"^0\.0\.\d+$")
_POOL_ID_PREFIX = "ADR-pool."


def audit_adr_taxonomy(project_root: Path) -> list[ValidationError]:
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    errors: list[ValidationError] = []
    for adr_md in sorted(adr_root.rglob("ADR-*.md")):
        # Skip nested audit / obpi / brief artefacts (same convention
        # as _validate_decomposition in validate_cmd.py).
        if "obpis" in adr_md.parts or "briefs" in adr_md.parts or "audit" in adr_md.parts:
            continue
        frontmatter = _parse_adr_frontmatter(adr_md)
        if frontmatter is None:
            continue  # non-ADR-shaped file; skip rather than fail
        rel = adr_md.relative_to(project_root).as_posix()
        adr_id = frontmatter.get("id", "")
        kind = frontmatter.get("kind")
        semver = frontmatter.get("semver")
        is_pool = isinstance(adr_id, str) and adr_id.startswith(_POOL_ID_PREFIX)

        if is_pool:
            if kind is not None:
                errors.append(ValidationError(
                    type="taxonomy", artifact=rel,
                    message=(
                        "Pool ADRs derive kind from the `ADR-pool.*` id "
                        "prefix; remove the `kind:` frontmatter field."
                    )))
            continue

        if kind is None:
            errors.append(ValidationError(
                type="taxonomy", artifact=rel,
                message=(
                    "Non-pool ADR is missing `kind:` frontmatter. Add "
                    "`kind: foundation` for an app/system invariant ADR "
                    "(semver `0.0.x`) or `kind: feature` for a capability "
                    "ADR (semver `0.y.z` and up). See ADR-0.0.17 / ADR-0.0.18."
                )))
            continue

        if kind not in ("foundation", "feature"):
            errors.append(ValidationError(
                type="taxonomy", artifact=rel,
                message=(
                    f"Unknown `kind: {kind}`. Expected `foundation` or "
                    "`feature` (pool kind is id-derived, not frontmatter)."
                )))
            continue

        if kind == "foundation" and not (
            isinstance(semver, str) and _FOUNDATION_SEMVER_RE.match(semver)
        ):
            errors.append(ValidationError(
                type="taxonomy", artifact=rel,
                message=(
                    f"`kind: foundation` requires semver `0.0.x`; got "
                    f"`{semver}`. Foundation ADRs are app/system invariants "
                    "and never impact release versioning."
                )))
        elif kind == "feature" and isinstance(semver, str) and _FOUNDATION_SEMVER_RE.match(semver):
            errors.append(ValidationError(
                type="taxonomy", artifact=rel,
                message=(
                    f"`kind: feature` forbids semver `0.0.x`; got `{semver}`. "
                    "Feature ADRs carry release-impacting semver (`0.y.z` and up)."
                )))
    return errors


def _parse_adr_frontmatter(path: Path) -> dict[str, str] | None:
    """Minimal YAML-front-matter reader — returns a flat str→str mapping.

    Stays stdlib-only (no PyYAML import) to match every sibling audit in
    this module. Returns None if no frontmatter block.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None
    fields: dict[str, str] = {}
    for raw in lines[1:end]:
        if ":" not in raw:
            continue
        key, _, value = raw.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            value = value[1:-1]
        fields[key] = value
    return fields
```

Add `"audit_adr_taxonomy"` to the module `__all__`.

**Rationale for stdlib-only YAML parse:** every existing `audit_*` in this
module uses `ast`, `re`, `tokenize`, or `json.loads` — none reach for
PyYAML. A trust-audit pulling a third-party parser to read a flat
frontmatter block enlarges the trust surface with no benefit.

Run the negative-case tests — they should go GREEN (except the still-skipped
lock-in test).

### Step 3 — Register the scope (GREEN for REQ-08)

`src/gzkit/commands/validate_cmd.py`:

- Add `check_taxonomy: bool = False` parameter to `_collect_errors` and
  `validate`.
- Add `"taxonomy": check_taxonomy` to the `default_scopes` dict (so bare
  `gz validate` runs it — matches REQ-08's default-scope language).
- Add `"taxonomy": lambda: trust_audits.audit_adr_taxonomy(project_root)`
  to `_default_scope_runners`.
- Also add a `"taxonomy"` entry in `_explicit_scope_runners` so a bare
  `--taxonomy` invocation still works.
- Add `"taxonomy"` to `run_all_scopes` in `_resolve_scopes`.
- Thread `check_taxonomy=check_taxonomy` through `_run_scope_checks` and
  the `as_json` / scorecard / dispatch lambdas.

`src/gzkit/cli/parser_maintenance.py`:

```python
p_validate.add_argument(
    "--taxonomy",
    dest="check_taxonomy",
    action="store_true",
    help="Enforce ADR kind/semver/id-prefix consistency (ADR-0.0.17)",
)
```

Thread `check_taxonomy=a.check_taxonomy` into the dispatch lambda on line
~472 alongside the other `check_*` kwargs.

Dispatch tests should now go GREEN.

### Step 4 — Docs (GREEN for REQ-10)

`docs/user/commands/validate.md` — add a `### --taxonomy` section after
`--commit-trailers`, describing the scope (id-prefix / kind / semver
invariants) and the default-scope inclusion.

`docs/governance/advisory-rules-audit.md` — add a scorecard row in the
Architectural Boundaries or ADR-structure section (match the style of
rules 1, 4, 11, 21): score **Mechanical**, cite
`gz validate --taxonomy` and ADR-0.0.17 / GHI #218.

### Step 5 — Brief amendment + OBPI ceremony

Update brief Allowed Paths (swap parser file) and set status → `Completed`
during ceremony via `gz obpi complete`.

## Verification (Stage 3 commands)

```bash
# Baseline quality (Heavy lane)
uv run gz lint
uv run gz typecheck
uv run gz test --obpi OBPI-0.0.17-04
uv run gz validate --documents
uv run mkdocs build --strict

# Coverage parity
uv run gz covers OBPI-0.0.17-04 --json

# Brief-specific verification
uv run gz validate --taxonomy           # focused scope
uv run gz validate                      # default scope includes taxonomy
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_promoted_advisory_audits tests.commands.test_validate_cmds -v
```

Expectations at ceremony time:

- `gz validate --taxonomy` — **reports violations** on current tree
  (105+ non-pool ADRs missing `kind:`) until the pending backfill lands.
  That is the intended class of failure — the audit's job is to surface
  the gap.
- `gz validate` (bare, default scope) — also reports taxonomy violations;
  same reason.
- `uv run -m unittest` — passes because the lock-in test is
  `@unittest.skip`-ed with an explicit reference to the pending
  backfill, and every negative test uses tempdir fixtures unrelated to
  the live tree.
- `gz arb step --name unittest …` — GREEN; use the receipt ID for
  attestation enrichment.

## Rejected alternatives

- **PyYAML for frontmatter parsing** — every sibling `audit_*` uses
  stdlib only; introducing a third-party trust-critical parser in a
  trust-audit module is an unwarranted surface expansion.
- **Registering only as `--taxonomy`, not default-scope** — REQ-08 names
  default-scope explicitly; deferring would mean bare `gz validate`
  silently ignores the invariant, which is exactly the class of drift
  ADR-0.0.17 closes.
- **Non-skipped lock-in test that asserts a bounded violation count** —
  brittle and inverts the audit's semantics.
- **Editing `parser_artifacts.py` to match the brief path** — would be
  wrong-file editing; the validate parser lives in
  `parser_maintenance.py`. Correct the brief instead.
- **Using `validate_document` / JSON schema to enforce taxonomy** — the
  schema already requires `kind` structurally, but catches only
  per-ADR-type errors; the cross-cutting id-prefix / semver-range rules
  don't fit JSON-schema cleanly. A discrete audit matches precedent
  (`audit_pool_adr_isolation`, `audit_version_release`).

## Scope boundary (out of this OBPI)

- Backfill of existing ADR frontmatter — separate OBPI.
- `AGENTS.md:194–217` kind/lane orthogonality correction — separate OBPI.
- `docs/user/concepts/adr-taxonomy.md` creation — ADR-0.0.18 doctrine.
- Skill updates to `gz-adr-create` / `gz-plan` to prompt for `--kind` —
  ADR-0.0.18.
