# Project setup

You are here when a repository has no gzkit scaffolding yet, or its scaffolding
needs repair, or its founding intent is not written down.

## Steps

1. **`gz-init`** — `uv run gz init` scaffolds `.gzkit/`, the skills, rules,
   chores, personas and templates, and the control surfaces. On an existing
   install, its repair mode delivers what is new without overwriting what the
   project edited.
2. **`gz-constitute`** — write the constitution: the principles every later
   artifact answers to.
3. **`gz-prd`** — write the product requirements. ADRs are subject to both the
   constitution and the PRD (`AGENTS.md` § Pattern Discovery).

## Branches

- **Paths look wrong after init** (a surface in the wrong place, a manifest
  path that does not resolve) → `gz-check-config-paths`, in
  [Surface integrity](surface-integrity.md).
- **Adopter repository.** The `foundation` ADR kind is open to you; in gzkit
  itself it is closed to new authoring.

## Only you can

Ratify the constitution and the PRD; they state your intent, not the agent's.

## Then

[Idea to ADR](idea-to-adr.md) for the first piece of work, or
[Session start](session-start.md) to orient.
