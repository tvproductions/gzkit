# Skill & Surface Sync — Rationale

> Expansion doc for `.gzkit/rules/skill-surface-sync.md` § Rationale (ADR-0.0.54-04 lift).
> Prose preserved verbatim; see rule file for binding bullets.

## Rationale

`.claude/` surfaces are the path of least resistance — that is what the agent reads at runtime. Editing there is the common drift mode; the next sync silently overwrites it. Rules cannot fully override the editing instinct, so the mechanical backstop is version + commit hash comparison: even when an agent edits the wrong surface, the version and git history make the conflict detectable and resolvable.

The split between frontmatter `skill-version` (skills) and body-level `<!-- rule-version: ... -->` (rules) keeps each artifact's version marker close to the surface that consumes it. The skill schema validates frontmatter strictly, so `skill-version` belongs there. The rule schema is deliberately minimal (id/paths/description) so that it can grow without breaking every rule file at once — the body-level marker preserves the version-bump invariant without requiring a schema migration every time the metadata vocabulary changes. See `chores.md` for the canonical body-marker form.
