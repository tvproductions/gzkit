# Plan: OBPI-0.27.0-02-router-surface-sync

**OBPI:** OBPI-0.27.0-02-router-surface-sync
**Parent ADR:** ADR-0.27.0-namespace-router-product-surface
**Lane:** Lite

## Context

The six namespace-router skill files were authored in OBPI-01. This OBPI
ensures they are registered in the canonical skill catalog and propagated to
all vendor mirrors via `gz agent sync control-surfaces`. Mirror files are
sync outputs — they are never hand-edited.

## Files

- Created: `tests/skills/test_namespace_router_surface_sync.py` — three REQ-derived tests
- Modified: `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-02-router-surface-sync.md` — evidence recorded

No implementation code modified — sync was completed via `gz agent sync control-surfaces`
during OBPI-01 (post-Write hook propagated mirrors when canonical files were created).

## Steps

1. Verify the six router canonical skills exist under `.gzkit/skills/`:
   `gz-workflow`, `gz-governance`, `gz-quality`, `gz-project`, `gz-context`, `gz-manage`

2. Run `uv run gz agent sync control-surfaces` to propagate to vendor mirrors
   (`.agents/skills/`, `.claude/skills/`, `.github/skills/`) and `src/gzkit/skills/`.

3. Write parity tests in `tests/skills/test_namespace_router_surface_sync.py`:
   - `TestVendorMirrorByteParity.test_each_router_byte_equivalent_in_every_vendor_mirror` → REQ-0.27.0-02-01
   - `TestPkgCopyByteParity.test_each_router_byte_equivalent_in_wheel_pkg_copy` → REQ-0.27.0-02-02
   - `TestRoutersDiscoverableInActiveCatalog.test_each_router_listed_active_in_skill_catalog` → REQ-0.27.0-02-03

4. Confirm REQ coverage: `uv run gz covers OBPI-0.27.0-02 --plain`

## Verification

```bash
uv run -m unittest tests.skills.test_namespace_router_surface_sync -v
uv run gz covers OBPI-0.27.0-02 --plain
uv run gz skill list | grep -E 'gz-(workflow|governance|quality|project|context|manage)'
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

## Notes

Implementation was completed in the 2026-05-23 session. This plan documents
the completed work for governance receipt purposes. All three tests are GREEN.
REQ coverage is 3/3. Vendor mirrors are byte-equivalent to canonical files.
