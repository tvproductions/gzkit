# gz content

Authoring CLI for the canonical content model substrate (ADR-0.0.34). The
`gz content` command group lets operators import, list, inspect, render, and
edit per-turn agent control surface files (rules, skills, personas, chores,
handoffs, scenarios, bullets, agent contracts) as canonical Pydantic models.

## Synopsis

```bash
gz content <subcommand> [OPTIONS]
```

## Description

`gz content` is the operator surface for the ADR-0.0.34 rendering substrate.
Per the headless-CMS doctrine, every per-turn agent control surface file is
rendered byte-stably from a canonical Pydantic model via a Jinja2 template.
Operators interact with these models through `gz content`; output is
human-readable prose by default, machine-readable JSON behind `--json`.

The content type registry exposes eight model types:

| Type | Surface |
|------|---------|
| `AgentContract` | `AGENTS.md`, `CLAUDE.md` |
| `Rule` | `.gzkit/rules/*.md` |
| `Skill` | `.gzkit/skills/*/SKILL.md` |
| `Chore` | `.gzkit/chores/*/CHORE.md` |
| `Persona` | `.gzkit/personas/*.md` |
| `Handoff` | `.gzkit/handoffs/*.md` |
| `Scenario` | BDD scenario records |
| `Bullet` | Single-bullet evidence rows |

Round-trip fidelity is binding: `model == parse(render(model))` for every type.

## Subcommands

### import

Read a hand-authored or canonical markdown file, parse it into a Pydantic
content model, and emit JSON to stdout. Optionally re-render the canonical
form to a target path.

```bash
gz content import <file> --as <type> [--write <path>]
```

`--write` persists the re-rendered canonical form to the named path; useful
for the OBPI-0.0.34-03 reverse-parse migration workflow.

### list

Enumerate the registered content model types from the `CONTENT_MODELS`
registry. Default output is a human-readable two-column table; `--json`
emits a machine-readable array.

```bash
gz content list [--type <content-type>] [--json]
```

`--type` filters output to a single type (e.g. `gz content list --type Rule`).

### show

Parse a canonical content file and display a prose summary (type, title,
field-by-field breakdown). The operator-facing surface is always
human-readable; pass `--json` for the canonical `model_dump_json()` form.

```bash
gz content show <file> --as <type> [--json]
```

### render

Parse a canonical content file and emit the re-rendered markdown to stdout.
Output is byte-identical to `gzkit.content.render.render(model, vendor)` for
the same input (round-trip stability per OBPI-0.0.34-02).

```bash
gz content render <file> --as <type> [--vendor <vendor>]
```

`--vendor` defaults to `claude`; other vendors render their respective
templates.

### edit

Open the canonical-form file in `$EDITOR` (or `$VISUAL`). On editor save,
the temp file is re-parsed and re-validated. **Invalid input aborts with
the validator diagnostic and never writes a partial file.** On successful
validation, the original file is atomically replaced with the re-rendered
canonical form via `Path.replace()`.

```bash
gz content edit <file> --as <type> [--vendor <vendor>]
```

The atomic-replace contract means a failed validation (or a non-zero editor
exit) leaves the original file byte-identical to its pre-edit state. There
is no partial-write state.

## Options

| Flag | Applies To | Description |
|------|-----------|-------------|
| `--as <type>` | import, show, render, edit | Content type name (required for these subcommands) |
| `--type <type>` | list | Filter list output to a single registered type |
| `--json` | list, show | Emit JSON to stdout instead of human-readable prose |
| `--write <path>` | import | Write re-rendered canonical form to this path |
| `--vendor <vendor>` | render, edit | Target vendor template for re-rendering (default: `claude`) |
| `--quiet`, `-q` | global | Suppress non-error output |
| `--verbose`, `-v` | global | Enable verbose output |
| `--debug` | global | Enable debug mode with full tracebacks |
| `--help`, `-h` | global | Show help and exit |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/config error (unknown type, missing `$EDITOR`, parse error, validation error, missing file) |
| 2 | System/IO error (filesystem unreadable, atomic-replace failed) |
| 3 | Policy breach (reserved; not currently emitted by `gz content`) |

## Examples

```bash
# Enumerate registered content types (human-readable table)
uv run gz content list

# Filter to a single type
uv run gz content list --type Rule

# Machine-readable form
uv run gz content list --json

# Inspect a rule file (prose summary)
uv run gz content show .gzkit/rules/tests.md --as Rule

# Machine-readable inspection
uv run gz content show .gzkit/rules/tests.md --as Rule --json

# Render the canonical form of a file to stdout
uv run gz content render AGENTS.md --as AgentContract

# Render against a specific vendor template
uv run gz content render .gzkit/rules/tests.md --as Rule --vendor claude

# Edit a rule with validation guard (invalid edits never land)
EDITOR=vim uv run gz content edit .gzkit/rules/tests.md --as Rule

# Reverse-parse a hand-authored file and write canonical output (OBPI-0.0.34-03)
uv run gz content import AGENTS.md --as AgentContract --write /tmp/agents-canonical.md
```

## Files

| Path | Role |
|------|------|
| `src/gzkit/content/models/` | Canonical Pydantic model definitions (`AgentContract`, `Rule`, `Skill`, …) |
| `src/gzkit/content/templates/` | Jinja2 templates per (content type × vendor) |
| `src/gzkit/content/render.py` | Render pipeline (OBPI-0.0.34-02) |
| `src/gzkit/content/parse.py` | Reverse-parse pipeline (OBPI-0.0.34-03) |
| `src/gzkit/commands/content/` | Operator CLI surface (this OBPI-0.0.34-04) |

## Related

- ADR-0.0.34 — Agent Control Surface Rendering Substrate (`docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/`)
- Doctrine — `docs/governance/agent-control-surface-rendering-substrate.md`
- OBPI-0.0.34-01 — Content model registry generalization
- OBPI-0.0.34-02 — Rendering pipeline
- OBPI-0.0.34-03 — Reverse-parse migration tooling
- OBPI-0.0.34-04 — Authoring CLI (this manpage)
- OBPI-0.0.34-05 — Light TUI affordances (forthcoming)
- OBPI-0.0.34-06 — Validation hooks (forthcoming)
