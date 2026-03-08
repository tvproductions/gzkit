# ADR-pool.change-isolation-workspace: Filesystem Change Isolation

## Status

Proposed

## Date

2026-03-08

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Adopt OpenSpec's change isolation pattern: `gz plan` creates a `changes/<adr-slug>/`
workspace containing the ADR, tasks, and scratchpad. On `gz closeout`, the ADR merges
into the canonical `docs/design/adr/` tree. This physically separates in-flight work
from completed decisions, reducing context confusion for both humans and AI agents.

---

## Target Scope

- `gz plan` creates `changes/<slug>/` with ADR, tasks, and a scratchpad.md
- `gz closeout` moves the ADR from changes/ to canonical docs/design/adr/
- Ledger records workspace creation and merge events
- Existing ADR workflow remains functional (changes/ is additive, not mandatory)

---

## Inspired By

[OpenSpec](https://github.com/Fission-AI/OpenSpec) — `changes/` directory pattern
for isolating pending modifications from current system state.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None

---

## Notes

- OpenSpec's killer feature — prevents AI context drift by physical separation
- Must preserve backward compatibility: existing pool/ ADRs and direct creation still work
- Consider: should `changes/` be gitignored or committed? (Committed — it's documentation)
