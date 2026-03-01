# gz skill audit

Audit skill lifecycle metadata and canonical mirror parity.

## Usage

```bash
gz skill audit [--json] [--strict]
```

## What It Checks

- Skill directory naming is kebab-case.
- `SKILL.md` frontmatter taxonomy is enforced:
  - Identity fields: `name`, `description`
  - Required lifecycle fields: `lifecycle_state`, `owner`, `last_reviewed`
  - Optional capability fields: `compatibility`, `invocation`, `gz_command`
- Frontmatter `name` matches the skill directory name.
- Mirror `SKILL.md` frontmatter `name` must match mirrored directory name.
- Canonical `.gzkit/skills` entries match mirror surfaces:
  - `.agents/skills`
  - `.claude/skills`
  - `.github/skills`

If optional capability fields are present in canonical skills, they must be non-empty.

Known nested `metadata` keys are validated when present:

- `metadata.skill-version` (`X.Y.Z`)
- `metadata.govzero-framework-version` (`vN` or `vN.N.N`)
- `metadata.govzero-author` (non-empty)
- `metadata.govzero_layer` (`Layer 1 — Evidence Gathering`, `Layer 2 — Ledger Consumption`, or `Layer 3 — File Sync`)

## Mirror Identity Contract (Fail-Closed)

For every mirrored skill, these frontmatter fields must match canonical exactly:

- `name`
- `description`
- `lifecycle_state`
- `owner`
- `last_reviewed`

When canonical defines optional capability/metadata keys, mirrors must preserve those values exactly.

Any mirror drift, missing mirror directories, or missing mirror `SKILL.md` files is a blocking error.

## Policy Semantics

`gz skill audit` classifies findings into blocking and non-blocking categories:

| Class | Severity | Blocking | Behavior |
|-------|----------|----------|----------|
| Canonical/mirror contract violations | `error` | `true` | Fails audit immediately |
| Stale mirror-only skill directories | `warning` | `false` | Non-blocking by default; fails with `--strict` |

Stale mirror-only directories are findings where a mirror has a skill directory not
present under canonical `.gzkit/skills`.

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit machine-readable report payload |
| `--strict` | Treat warnings as blocking failures |

## JSON Output Additions

`--json` includes additive policy fields:

- Per issue:
  - `code` (stable machine-readable identifier)
  - `blocking` (`true` or `false`)
- Top-level:
  - `blocking_error_count`
  - `non_blocking_warning_count`

## Example

```bash
uv run gz skill audit
uv run gz skill audit --json
uv run gz agent sync control-surfaces
uv run gz skill audit
```

Sample output (`uv run gz skill audit`, captured 2026-03-01):

```text
Skill audit passed.
Checked 45 canonical skills across 4 roots.
Blocking: 0  Non-blocking: 0
```

Sample output (`uv run gz skill audit --json`, captured 2026-03-01):

```json
{
  "valid": true,
  "checked_skills": 45,
  "checked_roots": [
    ".gzkit/skills",
    ".agents/skills",
    ".claude/skills",
    ".github/skills"
  ],
  "issues": [],
  "strict": false,
  "success": true,
  "error_count": 0,
  "warning_count": 0,
  "blocking_error_count": 0,
  "non_blocking_warning_count": 0
}
```
