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
- Canonical `.gzkit/skills` entries match mirror surfaces:
  - `.agents/skills`
  - `.claude/skills`
  - `.github/skills`

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit machine-readable report payload |
| `--strict` | Treat warnings as blocking failures |

## Example

```bash
uv run gz skill audit
uv run gz skill audit --json
```
