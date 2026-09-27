# Skill maintenance

You are here to add, review or retire a skill.

## Add a skill

1. `uv run gz skill new <slug>` scaffolds `.gzkit/skills/<slug>/SKILL.md`.
2. Write the skill. Supporting files go under its `references/`; they ship with
   it.
3. Give it a row in one namespace router and in this guide's catalog, under its
   flow. `gz validate --how-coverage` fails until it has the catalog row.
4. Add its page under `docs/user/skills/` and a row in that index.
5. [Commit and sync](commit-and-sync.md): `gz-agent-sync` writes the mirrors.

## Review a skill

**`gz-skill-review`** — re-verify every claim against the code the skill
wields, correct it and the surfaces that repeat it, then move
`last_reviewed`. `uv run gz skill audit` reports which reviews are ageing or
stale; a stale one blocks every push.

## Retire a skill

Follow `.gzkit/rules/skill-surface-sync.md` § Retirement policy: delete it from
every surface root, and repoint whatever named it, including its catalog row
here.

## Only you can

Decide that a skill is needed, and that one is retired.

## Then

[Commit and sync](commit-and-sync.md).
