---
id: OBPI-0.0.2-05-control-surface-regeneration
parent: ADR-0.0.2-stdlib-cli-and-agent-sync
item: 5
lane: Lite
status: Pending
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.0.2-05 — Docs/control-surface regeneration and drift checks

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.2-stdlib-cli-and-agent-sync/ADR-0.0.2-stdlib-cli-and-agent-sync.md`
- **Checklist Item:** #5 — "Update generated control surfaces to use canonical grammar. Add regression tests for canonical command path and alias behavior."

**Status:** Pending — retroactive brief authored 2026-04-15 under GHI #160 Phase 3 Mode F. Operator attestation required (Foundation ADR).

## Objective

Regenerate every vendor control surface to reflect the canonical `gz agent sync control-surfaces` grammar and add drift checks that enforce coherence going forward.

## Acceptance Criteria

- [x] REQ-0.0.2-05-01: Given `gz agent sync control-surfaces` is run, when it completes, then `.claude/`, `.github/`, and `.agents/` mirrors are regenerated from canonical `.gzkit/` state.
- [x] REQ-0.0.2-05-02: Given `gz check-config-paths` is run, when it completes, then control-surface path drift is detected and reported.
- [x] REQ-0.0.2-05-03: Given `gz validate --surfaces` is run, when it completes, then any divergence between canonical state and vendor mirrors fails the check.

### Implementation Summary

- Sync grammar drives all control-surface regeneration
- Drift detection lives in `gz check-config-paths` and `gz validate --surfaces`
- Date authored: 2026-04-15 (retroactive backfill)
- Defects noted: none

### Key Proof

```bash
$ uv run gz check-config-paths
$ uv run gz validate --surfaces
```

## Human Attestation

- Attestor: pending — operator attestation required (Foundation ADR)
- Date: pending
