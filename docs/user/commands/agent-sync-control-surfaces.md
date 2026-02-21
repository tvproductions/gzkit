# gz agent sync control-surfaces

Regenerate agent control surfaces and skill mirrors from canonical governance state.

## Usage

```bash
gz agent sync control-surfaces [--dry-run]
```

## Determinism Contract

For unchanged inputs, sync emits a deterministic updated-path list and stable operator output.

## Fail-Closed Canonical Preflight

Before any mirror propagation, sync validates canonical `.gzkit/skills` integrity.

Blocking preflight failures include:

- missing canonical skill directories (without a legacy bootstrap candidate),
- missing `SKILL.md`,
- missing or invalid `SKILL.md` frontmatter identity fields.

On failure, sync exits non-zero and prints recovery steps.

## Recovery Behavior (Non-Destructive)

Sync copies canonical files into mirrors but does not auto-delete mirror-only stale content.

When stale mirror-only paths exist, sync:

1. completes successfully,
2. emits a recovery warning with stale paths,
3. prints the manual cleanup protocol.

Manual recovery protocol:

```bash
uv run gz skill audit --json
# remove listed stale mirror-only paths
uv run gz agent sync control-surfaces
uv run gz skill audit
```

## Examples

```bash
# Preview targets only
uv run gz agent sync control-surfaces --dry-run

# Apply sync and view recovery warnings (if any)
uv run gz agent sync control-surfaces
```
