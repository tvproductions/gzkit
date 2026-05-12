---
id: {id}
status: Pool
parent: {parent}
lane: {lane}
enabler: null
---

# {id}: {title}

## Status

Pool

## Intent

{intent}

## Decision

{decision}

## Alternatives Considered

{alternatives}

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
