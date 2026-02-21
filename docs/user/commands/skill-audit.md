# gz skill audit

Audit skill lifecycle metadata and canonical mirror parity.

## Usage

```bash
gz skill audit [--json] [--strict]
```

## What It Checks

- Skill directory naming is kebab-case.
- `SKILL.md` frontmatter has required lifecycle fields.
- Frontmatter `name` matches the skill directory name.
- Mirror `SKILL.md` frontmatter `name` must match mirrored directory name.
- Canonical `.gzkit/skills` entries match mirror surfaces:
  - `.agents/skills`
  - `.claude/skills`
  - `.github/skills`

## Mirror Identity Contract (Fail-Closed)

For every mirrored skill, these frontmatter fields must match canonical exactly:

- `name`
- `description`
- `lifecycle_state`
- `owner`
- `last_reviewed`

Any mirror drift, missing mirror directories, or missing mirror `SKILL.md` files is a blocking error.

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit machine-readable report payload |
| `--strict` | Treat warnings as blocking failures |

## Example

```bash
uv run gz skill audit
uv run gz skill audit --json
uv run gz agent sync control-surfaces
uv run gz skill audit
```
