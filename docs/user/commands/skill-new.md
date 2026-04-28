# gz skill new

Create a new skill scaffold with required files.

## Usage

```bash
gz skill new <name> [--description TEXT]
```

## Description

Generates a new skill directory with template files including metadata, documentation, and configuration. The skill name should be lowercase with hyphens.

## Options

| Option | Description |
|--------|-------------|
| `--description` | Short description of the skill, written into the scaffolded `SKILL.md` frontmatter |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Skill scaffold created successfully |
| 1 | Skill already exists or invalid name |
