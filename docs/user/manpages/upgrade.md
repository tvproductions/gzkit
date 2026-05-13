# gz upgrade

Surface-only refresh of `.gzkit/<surface>/` from the installed wheel's package
data. Simpler than [`gz init --update`](init.md#update-mode-version-aware-refresh) — no manifest
mutation, no scaffolder hooks, no agent sync. Just surface content refresh.

---

## Usage

```bash
gz upgrade [OPTIONS]
```

---

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--surface` | `SURFACES` | — | Comma-separated subset of canonical surfaces to refresh (`skills,rules,templates,personas,hooks`). Default: all. |
| `--force` | flag | — | Overwrite project-local EDITED artifacts with canonical wheel content. Without `--force`, EDITED artifacts are reported as conflicts and left unchanged. |
| `--dry-run` | flag | — | Report what would change without writing any bytes to `.gzkit/`. Exit code matches the corresponding non-dry-run invocation. |

---

## What It Does

`gz upgrade` reads canonical surface content from the installed wheel via
`importlib.resources.files("gzkit.<surface>")` and compares each artifact
against the project's `.gzkit/<surface>/` tree using three-state detection:

- **IDENTICAL** — bytes match the wheel canonical; artifact skipped silently
- **STALE** — bytes differ and no canonical-version marker is present; artifact
  refreshed in place (unless `--dry-run`)
- **EDITED** — bytes differ AND the file carries a
  `<!-- gzkit-canonical-version: X.Y.Z -->` marker; operator has customized this
  file since last scaffold. Without `--force`, the conflict is reported and the
  file is left unchanged. With `--force`, the file is overwritten and a per-file
  audit line is printed.

The command is **idempotent**: running it twice immediately produces exit 0 with
zero STALE or EDITED artifacts on the second invocation (modulo concurrent
project edits).

---

## Three-State Detection

| State | Condition | Action (no `--force`) | Action (`--force`) |
|-------|-----------|-----------------------|---------------------|
| IDENTICAL | project bytes == canonical bytes | Skip | Skip |
| STALE | bytes differ, no version marker | Refresh (write canonical) | Refresh (write canonical) |
| EDITED | bytes differ, version marker present | Report conflict, skip write | Overwrite; print per-file line |

Exit code 3 when any EDITED conflict remains unresolved (without `--force`).

---

## Bootstrap Retrofit

`gz upgrade` works in a fresh `pip install py-gzkit` environment without
requiring `gz init` to have been run first. When `.gzkit/<surface>/` does not
exist, the command creates it and writes canonical content from the wheel — the
**bootstrap-retrofit** case. This makes `gz upgrade` the preferred first-touch
surface installer for projects that were not created via `gz init`.

---

## Relationship to `gz init --update`

| Aspect | `gz init --update` | `gz upgrade` |
|--------|-------------------|--------------|
| Surfaces refreshed | All canonical surfaces | Filterable via `--surface` |
| Manifest | Updated | **Never touched** |
| Scaffolder hooks | Runs `scaffold_core_*` hooks | **Never invoked** |
| Agent sync | Runs `gz agent sync` | **Never invoked** |
| Bootstrap retrofit | No (requires prior `gz init`) | Yes |
| Use case | Full project refresh ceremony | Narrow surface-content refresh |

Use `gz init --update` when you want the full ceremony with manifest refresh
and scaffolder-hook propagation. Use `gz upgrade` when you only need surface
content to match the installed wheel.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success — zero EDITED conflicts (or `--force` resolved them all) |
| 1 | User/config error — unknown `--surface` token or missing project root |
| 2 | System/IO error — package data unavailable or filesystem fault |
| 3 | Policy breach — one or more EDITED conflicts remain (without `--force`) |

---

## Examples

```bash
# Preview all surfaces — show what would change without writing
gz upgrade --dry-run

# Refresh skills and rules from the installed wheel
gz upgrade --surface skills,rules

# Refresh every canonical surface (default)
gz upgrade

# Force overwrite of operator-edited templates with canonical content
gz upgrade --surface templates --force

# Bootstrap retrofit: project never ran gz init; pull canonical content from wheel
gz upgrade
```

---

## Related Commands

- [`gz init`](init.md) — full project initialization and `--update` ceremony
- [`gz agent sync control-surfaces`](agent-sync-control-surfaces.md) — propagate
  `.gzkit/<surface>/` to vendor mirrors (`.[vendor]/`)
