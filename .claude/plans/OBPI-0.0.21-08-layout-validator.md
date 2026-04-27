# Plan: OBPI-0.0.21-08 — Layout Validator

**OBPI:** OBPI-0.0.21-08-layout-validator
**Parent ADR:** ADR-0.0.21-chores-as-gzkit-surface (Decision #9)
**Lane:** Heavy
**Brief:** `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/obpis/OBPI-0.0.21-08-layout-validator.md`

## Context

ADR-0.0.21 Decision #9 mandates a mechanical backstop preventing future
re-emergence of an `ops/chores/` (or any non-canonical) layout: `gz validate
--chores-layout` MUST fail-close (exit 3) on any `CHORE.md` or
`acceptance.json` discovered outside the two canonical roots —
`src/gzkit/chores/` (canonical, shipped in the wheel) and the project-scoped
`paths.chores` (default `.gzkit/chores/`). Sibling exemplar:
`audit_utf8_prefix` at `src/gzkit/governance/trust_audits.py:424`.

The current tree has CHORE.md / acceptance.json only under `src/gzkit/chores/`
and `.gzkit/chores/`, so the audit returns clean on a green tree. No waivers
required at landing time — the waiver file is provisioned empty for future use.

## Destination-in-mind disclosure (Step 6a)

The implementation approach is locked by the brief's allowed-paths list and the
`audit_utf8_prefix` exemplar pattern: a `Path.rglob("*")` walker that yields
`ValidationError(type="chores_layout")` for every stray file, plus a wire-up
across `validate_cmd.py` (signature → explicit_scopes dict → runners dict →
opt_in_scopes list → `validate()` signature → CLI args dispatcher) and a
`parser_maintenance.py` flag registration. This is a five-surface registry
extension with strong precedent — the structural shape is not a design choice
but a doctrinal constraint.

## Rejected alternatives

1. **Glob-only (no AST or content read).** Considered scanning file *content*
   to confirm shape (e.g. CHORE.md must contain `# Chore:` heading). Rejected:
   the audit's job is *layout* drift, not content drift; that's a separate
   audit (and a separate REQ).
2. **Hardcoded canonical root only.** Considered ignoring `paths.chores` and
   fixing the project root at `.gzkit/chores`. Rejected: brief REQ-08-02
   explicitly requires `{config.paths.chores}/` resolution; OBPI-02 already
   landed the config key.
3. **Default-on (run with no flags).** Considered including the new scope in
   `default_scopes`. Rejected: brief REQ-08-08 mandates opt-in; matches the
   precedent set by `utf8_prefix`, `brief_headings`, etc.
4. **Waiver-as-CLI-flag.** Considered `--waive PATH`. Rejected: explicit JSON
   file matches the `_UTF8_PIPE_WAIVERS` precedent (T2 trust-doctrine
   compliance — waivers are reviewable artifacts, not transient flags).

## Files

**Created:**
- `data/chores_layout_waivers.json` — empty JSON list `[]`, future-waiver scaffold

**Modified:**
- `src/gzkit/governance/trust_audits.py` — new `audit_chores_layout`
  function (~60-80 lines) + new `_CHORES_LAYOUT_WAIVERS` constant + `__all__`
  export
- `src/gzkit/commands/validate_cmd.py` — wire `chores_layout` into 5 surfaces:
  `_collect_validation_errors` signature, `explicit_scopes` dict,
  `_explicit_scope_runners` dict, `opt_in_scopes` list, `validate()` signature
  + dispatcher
- `src/gzkit/cli/parser_maintenance.py` — add `--chores-layout` flag
- `tests/governance/test_trust_audits.py` — 6 REQ-derived TDD tests

## Steps

### 1. RED — Test: stray CHORE.md flagged

Add `TestAuditChoresLayout` class to `tests/governance/test_trust_audits.py`.
First test: `test_audit_chores_layout_flags_stray_chore_md`
(`@covers REQ-0.0.21-08-03`). Plant `tmp/ops/chores/bogus/CHORE.md`,
call `audit_chores_layout(tmp)`, assert exactly one `ValidationError` with
`type="chores_layout"` and message naming the offending path.

Run `uv run -m unittest tests.governance.test_trust_audits.TestAuditChoresLayout
-v` — expect `AttributeError: module ... has no attribute audit_chores_layout`.

### 2. GREEN — Implement walker

Add `audit_chores_layout(project_root: Path) -> list[ValidationError]` to
`src/gzkit/governance/trust_audits.py` immediately after `audit_utf8_prefix`
(or near `audit_brief_headings` at line 1476 — match the local convention).
Skeleton:

- Resolve canonical roots: `src/gzkit/chores/` (always) and `paths.chores` from
  `gzkit.config.load_config(project_root).paths.chores` (default
  `.gzkit/chores/`). Resolve both relative-to project_root.
- Load waivers from `project_root / "data" / "chores_layout_waivers.json"` —
  list of POSIX path strings; tolerant if file missing.
- Walk `project_root.rglob("*")`, filtering on `path.is_file()` and
  `path.name in {"CHORE.md", "acceptance.json"}`.
- Skip any path whose any-segment starts with `.` (dotfile-hidden) OR matches
  `{__pycache__, .venv, dist, build, node_modules}`. Per
  `audit_utf8_prefix`'s prior art.
- Compute `rel = path.relative_to(project_root).as_posix()`.
- If `rel` is in waivers → skip.
- If `rel` starts with one of the canonical-root strings → skip.
- Otherwise emit `ValidationError(type="chores_layout", artifact=rel,
  message=f"stray {path.name} outside canonical roots ...")`.

Add to `__all__` (line 1802).

Re-run test — expect PASS.

### 3. RED+GREEN — Test: canonical roots accept

`test_audit_chores_layout_accepts_src_root` (`@covers REQ-0.0.21-08-02`).
Plant `tmp/src/gzkit/chores/x/CHORE.md`, assert empty list.

`test_audit_chores_layout_accepts_project_root` (`@covers REQ-0.0.21-08-02`).
Plant `tmp/.gzkit/chores/x/CHORE.md`, assert empty list.

These pass on first run if Step 2 logic is right; if RED for the right reason
(e.g., `paths.chores` default not respected), fix Step 2 logic.

### 4. RED+GREEN — Test: waivers honored

`test_audit_chores_layout_honors_waivers` (`@covers REQ-0.0.21-08-05`).
Plant `tmp/legacy/CHORE.md`, write
`tmp/data/chores_layout_waivers.json` with `["legacy/CHORE.md"]`,
assert empty list.

If waiver loading wasn't wired in Step 2, watch RED, then implement loading
and re-run.

### 5. RED+GREEN — Test: dotfile/exclusion paths skipped

`test_audit_chores_layout_skips_excluded_paths` (`@covers
REQ-0.0.21-08-06`). Plant `tmp/.git/objects/CHORE.md`,
`tmp/__pycache__/CHORE.md`, `tmp/.venv/lib/CHORE.md`. Assert empty list.

### 6. RED — CLI exit 3 on drift

`test_cli_validate_chores_layout_exits_3_on_drift` (`@covers
REQ-0.0.21-08-04`). Use the existing CLI test harness pattern (e.g.
`subprocess.run` against a fixture tempdir, or `runner.invoke` if Click). Plant
`tmp/ops/chores/x/CHORE.md`, invoke `gz validate --chores-layout` with
`cwd=tmp`, assert exit code 3.

Run — expect RED (`unrecognized arguments: --chores-layout`).

### 7. GREEN — Wire CLI scope across 5 surfaces

In `src/gzkit/commands/validate_cmd.py`:

- Add `check_chores_layout: bool = False` to `_collect_validation_errors`
  signature (around line 294).
- Add `"chores_layout": check_chores_layout` to the `explicit_scopes` dict
  (around line 333).
- Add `"chores_layout": lambda: trust_audits.audit_chores_layout(project_root)`
  to `_explicit_scope_runners` (around line 403).
- Add `"chores_layout"` to `opt_in_scopes` list (around line 574).
- Add `check_chores_layout: bool = False` to `validate()` signature (around
  line 660+).
- Pipe `check_chores_layout` from CLI args to the dispatcher (find existing
  surface that calls `validate(...)` and pass `check_chores_layout=
  args.check_chores_layout`).

In `src/gzkit/cli/parser_maintenance.py`:

- Add `--chores-layout` flag immediately after `--brief-headings` (line 462+):

```python
p_validate.add_argument(
    "--chores-layout",
    dest="check_chores_layout",
    action="store_true",
    help="Forbid CHORE.md/acceptance.json outside canonical chores roots",
)
```

Re-run CLI test — expect GREEN.

### 8. RED+GREEN — Test: clean tree passes

`test_audit_chores_layout_clean_tree_passes` (`@covers REQ-0.0.21-08-01`).
Plant nothing under `tmp` (or only legitimate `tmp/src/gzkit/chores/`),
assert empty list and (via subprocess) exit 0.

### 9. Create `data/chores_layout_waivers.json`

Empty list:

```json
[]
```

### 10. Verification

Run the brief's verification commands (next section). Re-run
`uv run gz plan audit OBPI-0.0.21-08` to confirm the plan-audit receipt
flips to PASS.

## Verification

```bash
# Lint + typecheck
uv run gz arb ruff
uv run gz arb typecheck

# OBPI-scoped tests (RED→GREEN evidence)
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_trust_audits.TestAuditChoresLayout -v

# Full unittest sweep (Stage 3 baseline)
uv run gz arb step --name unittest -- uv run -m unittest -q

# Audit runs clean on current tree
uv run gz validate --chores-layout

# Smoke fail-closed
mkdir -p /tmp/layout-drift/ops/chores/bogus
echo "# bogus" > /tmp/layout-drift/ops/chores/bogus/CHORE.md
cd /tmp/layout-drift && uv run gz validate --chores-layout; echo "exit:$?"
# expect: exit:3

# REQ→@covers parity (Stage 3 Phase 1b)
uv run gz covers OBPI-0.0.21-08-layout-validator --json
# expect: summary.uncovered_reqs == 0
```

## Notes

- **Coordination with OBPI-06 (rule and doc updates):** OBPI-06 is already
  Completed and its rule text in `.claude/rules/chores.md` already cites
  `gz validate --chores-layout` (line 102). The CLI surface this OBPI lands
  is what makes that rule's reference resolvable. No edit to `chores.md`
  required by this OBPI — that's already done.
- **Coordination with OBPI-09 (chores-doctor):** This OBPI adds a validator
  that will eventually flag drift if OBPI-09 misroutes its scaffolding.
  Defensive precondition for OBPI-09's correctness.
- **Default-scope exclusion confirmed:** REQ-08-08 says `gz validate`
  no-arg default MUST NOT invoke this scope. The plan adds it only to
  `explicit_scopes` and `opt_in_scopes`, not to `default_scopes` or
  `run_all_scopes`. Verified against the existing pattern.
- **Empty waivers file:** Brief REQ-08-05 implies the file exists; the
  current tree has no `ops/chores/` legacy paths to waive, so the file
  ships empty and serves as scaffold for future waiver entries.
- **Performance:** REQ-08-07 (<2s) is satisfied by `rglob("*")` over the
  current tree — no subprocess boundaries, no AST parsing.
