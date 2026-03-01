# gz skill audit

Audit skill lifecycle metadata and canonical mirror parity.

## Usage

```bash
gz skill audit [--json] [--strict] [--max-review-age-days N]
```

## What It Checks

- Skill directory naming is kebab-case.
- `SKILL.md` frontmatter taxonomy is enforced:
  - Identity fields: `name`, `description`
  - Required lifecycle fields: `lifecycle_state`, `owner`, `last_reviewed`
  - Transition evidence fields (all-or-none when declared):
    - `lifecycle_transition_from`
    - `lifecycle_transition_date`
    - `lifecycle_transition_reason`
    - `lifecycle_transition_evidence`
  - Deprecation fields (state-conditional):
    - `deprecation_replaced_by`
    - `deprecation_migration`
    - `deprecation_communication`
    - `deprecation_announced_on`
    - `retired_on`
  - Optional capability fields: `compatibility`, `invocation`, `gz_command`
- `last_reviewed` staleness policy is enforced for canonical skills
  (default threshold: 90 days, configurable via CLI option).
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

## Lifecycle Transition Contract (Fail-Closed)

When transition metadata is declared, all transition fields are required and validated:

- `lifecycle_transition_from`
- `lifecycle_transition_date`
- `lifecycle_transition_reason`
- `lifecycle_transition_evidence`

Allowed transitions:

| From | To |
|---|---|
| `draft` | `active` |
| `active` | `deprecated` |
| `deprecated` | `active` |
| `deprecated` | `retired` |

Unsupported/no-op transitions are blocking failures.
`lifecycle_transition_date` must be `YYYY-MM-DD`.

## Deprecation State Contract (Fail-Closed)

State-specific requirements:

| `lifecycle_state` | Required fields |
|---|---|
| `draft` / `active` | No deprecation-only fields allowed |
| `deprecated` | `deprecation_replaced_by`, `deprecation_migration`, `deprecation_communication`, `deprecation_announced_on` |
| `retired` | All `deprecated` fields + `retired_on` |

Date fields must be `YYYY-MM-DD`.

## Mirror Identity Contract (Fail-Closed)

For every mirrored skill, these frontmatter fields must match canonical exactly:

- `name`
- `description`
- `lifecycle_state`
- `owner`
- `last_reviewed`

When canonical defines optional capability/metadata/transition/deprecation keys,
mirrors must preserve those values exactly.

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
| `--max-review-age-days N` | Maximum allowed age of `last_reviewed` before blocking failure (default: `90`) |

## JSON Output Additions

`--json` includes additive policy fields:

- Per issue:
  - `code` (stable machine-readable identifier)
  - `blocking` (`true` or `false`)
- Top-level:
  - `blocking_error_count`
  - `non_blocking_warning_count`
  - `max_review_age_days`
  - `stale_review_count`

## Example

```bash
uv run gz skill audit
uv run gz skill audit --json
uv run gz skill audit --max-review-age-days 120
uv run gz agent sync control-surfaces
uv run gz skill audit
```

Sample output (`uv run gz skill audit`, captured 2026-03-01):

```text
Skill audit passed.
Checked 45 canonical skills across 4 roots.
Blocking: 0  Non-blocking: 0
Max review age: 90 days
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
  "non_blocking_warning_count": 0,
  "max_review_age_days": 90,
  "stale_review_count": 0
}
```
