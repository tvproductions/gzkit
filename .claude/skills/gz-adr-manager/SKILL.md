---
name: gz-adr-manager
description: Compatibility alias for gz-adr-create to preserve cross-repository governance ritual continuity.
compatibility: GovZero v6 compatibility alias for historical AirlineOps command language.
invocation: Use when prompts or docs call `/gz-adr-manager`; this alias delegates to `/gz-adr-create`.
gz_command: gz plan + gz specify workflow through gz-adr-create semantics
metadata:
  skill-version: "6.0.0"
  govzero-framework-version: "v6"
  govzero-author: "gzkit-governance"
  govzero_layer: "Layer 3 — File Sync"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-01
---

# gz-adr-manager (compatibility alias)

## Purpose

Provide backward-compatible invocation for historical references to `gz-adr-manager` while keeping `gz-adr-create` as the canonical skill in gzkit.

## Alias Contract

- Canonical behavior source: `../gz-adr-create/SKILL.md`
- Lifecycle, gate, and OBPI co-creation rules are inherited without modification.
- No separate templates, policy variants, or parallel semantics are allowed.

## Procedure

1. Read `../gz-adr-create/SKILL.md`.
2. Execute the same ADR creation workflow as `gz-adr-create`.
3. When updating docs or prompts, prefer `gz-adr-create` and keep `gz-adr-manager` noted as legacy alias.

## Constraints

- Do not diverge from `gz-adr-create` behavior.
- Do not introduce alias-only governance rules.
- Treat any behavior drift between alias and canonical skill as a defect.
