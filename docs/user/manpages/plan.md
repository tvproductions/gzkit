# gz plan

Create ADRs and run plan-audit checks.

`gz plan` is a parent verb that groups ADR authoring and plan-OBPI alignment
verification. All real work happens in its subcommands; invoke `gz plan`
without a subcommand to see this help.

---

## Usage

```bash
gz plan {create,audit} [OPTIONS]
```

---

## Subcommands

| Subcommand | Purpose | Details |
|------------|---------|---------|
| [`gz plan create`](plan-create.md) | Create a new ADR scaffold | Taxonomy-aware: `--kind {pool,foundation,feature}` routes output and frontmatter. Foundation requires `--semver 0.0.x`; feature requires non-`0.0.x`; pool writes a flat backlog ADR. |
| [`gz plan audit`](plan-audit.md) | Structural prerequisite check for plan-OBPI alignment | Verifies ADR package, OBPI brief, plan file, and allowed-path containment before implementation begins. |

---

## Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help and exit |
| `-q`, `--quiet` | Suppress non-error output |
| `-v`, `--verbose` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

---

## Examples

```bash
gz plan create my-feature --kind feature --semver 0.1.0 --lane lite
gz plan audit OBPI-0.1.0-01
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/config error |
| 2 | System/IO error |
| 3 | Policy breach |

---

## See Also

- [`gz plan create`](plan-create.md) — ADR authoring
- [`gz plan audit`](plan-audit.md) — plan-OBPI alignment check
- [`gz adr promote`](adr-promote.md) — promote a pool ADR into canonical structure
- [ADR-0.0.17](../../design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md) — ADR taxonomy (pool / foundation / feature)
- [ADR-0.0.18](../../design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md) — taxonomy operator doctrine
