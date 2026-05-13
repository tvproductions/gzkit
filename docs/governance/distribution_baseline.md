# Distribution Baseline Manifest

The distribution baseline manifest at `data/distribution_baseline_manifest.json`
is the frozen contract that enumerates every canonical artifact the gzkit wheel
MUST deliver to a freshly-initialized adopter project. It is the mechanical arm
of the T0 distribution invariant authored by ADR-0.0.31 and operationalized by
ADR-0.0.32 OBPI-06.

## Role

T0 doctrine states that every canonical surface authored at `.gzkit/<surface>/`
in this repo must ship in the wheel under `src/gzkit/<surface>/` and land in
the adopter's `.gzkit/<surface>/` post-`gz init` byte-equivalent (modulo
project-name substitution) to the canonical source.

Before OBPI-06, T0 was advisory: a canonical surface could quietly stop
shipping and the only signal would be a downstream consumer noticing.
OBPI-06 closes that gap with a build-then-install smoke scenario at
`features/distribution_invariant.feature` that fails CI on any T0 drift —
both directions: a baseline entry missing from the post-init `.gzkit/` tree,
or an installed `.gzkit/` artifact not in the baseline manifest.

## Schema

```json
{
  "schema_version": "1.0",
  "gzkit_version": "<X.Y.Z>",
  "surfaces": {
    "skills": ["<slug>/SKILL.md", ...],
    "rules": ["<filename>.md", ...],
    "personas": ["<filename>.md", ...],
    "templates": ["<filename>.md", ...]
  }
}
```

- `schema_version`: format version of this manifest. Currently `1.0`. Bumped
  if surface taxonomy changes (e.g. new surface added that requires a new
  enumeration shape).
- `gzkit_version`: gzkit release the manifest was authored against. Used by
  diagnostics to flag manifest/wheel mismatch.
- `surfaces`: dict of surface name to list of surface-relative paths.
  - Skill entries are `"<slug>/SKILL.md"` (relative to `src/gzkit/skills/`).
  - Rule, persona, and template entries are bare filenames (relative to
    `src/gzkit/<surface>/`).

## Retired-skill filtering

The manifest captures the **scaffolded contract**, not raw wheel content.
Skills whose canonical SKILL.md declares `lifecycle_state: retired` in
frontmatter are filtered out of `surfaces.skills` because `scaffold_core_skills`
filters them on `gz init` (hard cutover invariant per
`.gzkit/rules/skill-surface-sync.md`). Retired skills may still ship in the
wheel for backward-compatibility, but the smoke scenario cross-checks
post-`gz init` `.gzkit/` against the manifest — including retired entries
would manufacture false drift on every CI run.

The same filter applies to any future surface that adopts a `retired`
lifecycle marker in frontmatter.

## Refresh discipline

The manifest is refreshed every time a new canonical artifact lands at a
tracked surface. Refresh is part of the OBPI that adds the artifact, not a
separate ceremony.

Triggers requiring a refresh:

1. **New skill landed** at `.gzkit/skills/<new-slug>/SKILL.md` and propagated
   to `src/gzkit/skills/<new-slug>/SKILL.md`. Add `"<new-slug>/SKILL.md"` to
   `surfaces.skills`.
2. **New rule landed** at `src/gzkit/rules/<new-name>.md`. Add
   `"<new-name>.md"` to `surfaces.rules`.
3. **New persona landed** at `src/gzkit/personas/<new-name>.md`. Add
   `"<new-name>.md"` to `surfaces.personas`.
4. **New template landed** at `src/gzkit/templates/<new-name>.md`. Add
   `"<new-name>.md"` to `surfaces.templates`.
5. **New surface introduced** (e.g. agents, hooks-as-canonical). Add a new
   top-level key under `surfaces` and bump `schema_version` if the entry
   shape differs from existing surfaces.
6. **gzkit version bumped** in `pyproject.toml`. Update `gzkit_version`
   string to match.

The unit tests at `tests/distribution/test_baseline_manifest.py` enforce
that every manifest entry resolves to a real file under `src/gzkit/<surface>/`.
A refresh that adds a phantom entry (no backing file) fails CI.

## Update procedure

When a new canonical artifact lands:

1. Promote/author the canonical content at the appropriate surface
   (`.gzkit/<surface>/` and `src/gzkit/<surface>/` per ADR-0.0.32
   dual-surface model).
2. Open `data/distribution_baseline_manifest.json`.
3. Add the new entry to the appropriate `surfaces` list, preserving
   alphabetic sort order.
4. Run the unit tests to confirm the new entry resolves:
   ```bash
   uv run -m unittest tests.distribution.test_baseline_manifest -v
   ```
5. (Optional, slower) Run the behave smoke scenario to confirm the wheel
   actually ships the new content end-to-end:
   ```bash
   uv run -m behave features/distribution_invariant.feature
   ```

## Running the smoke test

The smoke scenario builds the wheel via `uv build`, installs it into a fresh
temp venv, runs `gz init`, and asserts byte-equivalence against the manifest.
Wall-clock runtime is approximately 30-90 seconds depending on `uv build`
cache state, dominated by wheel build and venv creation.

The scenario is tagged `@slow` and is **excluded from the standard `gz test`
smoke run** by default. Invoke it explicitly when verifying distribution
contract changes:

```bash
uv run -m behave features/distribution_invariant.feature
```

CI configurations that gate on T0 distribution drift should add this command
as an explicit step rather than relying on the default `gz check` cascade.

## Drift detection — both directions

The smoke scenario fails on drift in either direction:

- **Missing baseline entry in install:** a manifest entry that does not
  resolve to a real file in the post-init `.gzkit/<surface>/` tree. Cause:
  wheel `include:` block stopped shipping the file, or `gz init` scaffolder
  stopped copying it.
- **Extra installed artifact:** a file under `.gzkit/<surface>/` that
  matches the surface's expected file shape (e.g. a SKILL.md under skills)
  but is not in the baseline manifest. Cause: new canonical artifact landed
  but the manifest was not refreshed.

Both directions are fail-closed. Drift cannot accumulate silently between
attestation cycles.

## Related

- [ADR-0.0.31 — Distribution Invariant Doctrine](../design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md)
- [ADR-0.0.32 — Canonical Surface Packaging](../design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md)
- [`.gzkit/rules/skill-surface-sync.md`](../../.gzkit/rules/skill-surface-sync.md) — Canonical-routing direction
- `features/distribution_invariant.feature` — the smoke scenario itself
- `tests/distribution/test_baseline_manifest.py` — unit-tier manifest validation
