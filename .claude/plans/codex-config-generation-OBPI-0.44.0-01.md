# OBPI-0.44.0-01 Codex Config Generation Plan

## Context

- Parent: `ADR-0.44.0-vendor-alignment-codex`
- Brief: `OBPI-0.44.0-01-codex-config-generation`
- Outcome: `gz init` and control-surface sync create a configured,
  project-scoped Codex baseline without overwriting a non-empty operator file.
- Boundary: config generation only. Hook registration waits for OBPI-02 after
  OBPI-04 supplies harness-neutral transition state.

## Destination-In-Mind

Before authoring this plan, exploration had already established the intended
shape: add one `PathConfig.codex_config` path, render a small marked TOML
baseline with stdlib string generation, write it only when the configured file
is missing or empty, register the path in manifest metadata, and track the
generated path in sync-parity validation. The marker distinguishes a generated
baseline from a pre-existing operator file for semantic validation without
making the sync writer overwrite either class.

## Rejected Alternatives

1. **Merge arbitrary TOML text.** Rejected because stdlib has a TOML reader but
   no TOML writer; round-tripping unknown operator formatting and comments would
   require a new dependency or an unsafe ad hoc rewriter.
2. **Always rewrite the config.** Rejected because project config is an
   operator-owned extension point; gzkit may create the absent baseline but
   cannot erase model, approval, MCP, or other local settings.
3. **Add hook generation now.** Rejected because hook policy is OBPI-02 and
   depends on OBPI-04. The current inert hook file is a separate defect class.
4. **Raise `project_doc_max_bytes`.** Rejected because current `AGENTS.md` is
   already below Codex's default cap and a larger override would conceal future
   contract growth.

## Files

- `src/gzkit/config.py`
- `src/gzkit/sync_surfaces.py`
- `src/gzkit/sync.py` (public facade exercised by tests; no edit expected)
- `src/gzkit/commands/init_cmd.py` only if direct init wiring is required beyond
  its existing `sync_all()` and hook-setup paths
- `src/gzkit/schemas/manifest.json`
- `src/gzkit/validate_pkg/surface.py`
- `src/gzkit/validate_pkg/sync_parity.py`
- `.codex/config.toml`
- `.gzkit/manifest.json`
- `tests/test_codex_config_surface.py`
- `tests/test_config_paths.py`
- `tests/commands/test_init.py`
- `tests/test_sync.py`
- `tests/test_validate_sync_parity.py`
- `features/agent_sync.feature`
- `features/steps/codex_config_steps.py`
- `docs/user/manpages/init.md`
- Parent ADR and this OBPI brief for evidence only

## TDD Steps

1. **REQ-01 RED/GREEN:** Add one test proving a surface sync in an initialized
   fixture creates parseable configured Codex TOML with workspace-write,
   project network access, and `[features].hooks = true`. Watch the assertion
   fail because no sync writer exists. Add the minimal baseline renderer and
   `sync_all()` wiring; keep init on its established sync path.
2. **REQ-02 RED/GREEN:** Add a test that seeds a non-empty config with an
   operator-only key, runs sync, and asserts byte-for-byte preservation. Watch
   it fail against any unconditional writer, then make the writer create only
   missing or empty targets.
3. **REQ-03 RED/GREEN:** Add a non-default `PathConfig` test and manifest
   assertion. Watch it fail because `codex_config` is not modeled or published,
   then add the path field, manifest schema property, and generated manifest
   entry.
4. **REQ-04 RED/GREEN:** Add semantic tests for a missing configured baseline,
   a corrupted marked generated baseline, and a valid unmarked operator config.
   Watch the relevant assertion fail, then resolve config paths through
   `GzkitConfig` and add the Codex path to sync-parity collection.
5. Add BDD scenarios and focused fixture steps proving creation,
   operator-content preservation, custom-path generation, and managed-drift
   failure through real `gz agent sync` / `gz validate --surfaces` commands.
6. Update the init manpage with observed generated fields, preservation
   behavior, and the delete-then-sync recovery for a drifted managed baseline.
7. Run focused tests after each behavior, then the brief verification commands.

## Requirement Mapping

| Requirement | Plan proof |
|---|---|
| REQ-0.44.0-01-01 | TDD step 1 plus BDD creation scenario |
| REQ-0.44.0-01-02 | TDD step 2 plus BDD preservation scenario |
| REQ-0.44.0-01-03 | TDD step 3 path and manifest assertions |
| REQ-0.44.0-01-04 | TDD step 4 semantic and sync-parity negative controls |

## Verification

```bash
uv run -m unittest tests.test_codex_config_surface tests.test_config_paths tests.test_sync tests.test_validate_sync_parity tests.commands.test_init
uv run gz validate --surfaces
uv run gz agent sync control-surfaces --dry-run
uv run -m behave features/agent_sync.feature
uv run mkdocs build --strict
```

## Scope Check

Every planned edit is listed in the brief's Allowed Paths. The plan does not
touch `.codex/hooks.json`, `.agents/**`, pipeline runtime state, dependencies,
CI, or lockfiles.
