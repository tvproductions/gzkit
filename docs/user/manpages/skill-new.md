# gz skill new

Create a new skill scaffold with required files.

## Usage

```bash
gz skill new <name> [--description TEXT]
```

## Description

Generates a new skill directory with template files including metadata, documentation, and configuration. The skill name should be lowercase with hyphens.

A custom scaffold is unfinished: its explicit placeholder steps produce
`SKA-BODY-UNFINISHED` findings until authored according to
`.gzkit/rules/skill-authoring.md`. Creation succeeds so the file can be edited;
it does not certify the procedure. Packaged skills retain their authored bodies.

## Options

| Option | Description |
|--------|-------------|
| `--description` | Short description of the skill, written into the scaffolded `SKILL.md` frontmatter |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Skill scaffold created successfully |
| 1 | Skill already exists or invalid name |
