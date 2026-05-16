# Plan: OBPI-0.0.34-04-authoring-cli

**OBPI:** OBPI-0.0.34-04-authoring-cli
**Parent ADR:** ADR-0.0.34-agent-control-surface-rendering-substrate
**Lane:** Heavy

## Context

OBPI-0.0.34-01 (content model registry), OBPI-0.0.34-02 (rendering pipeline),
and OBPI-0.0.34-03 (reverse-parse migration + `gz content import`) are all ATTESTED
COMPLETED. The `gz content` subparser group exists in `__init__.py` with only `import`
registered. CONTENT_MODELS has 8 types (AgentContract, Rule, Skill, Chore, Persona,
Handoff, Scenario, Bullet). `render()` and `parse()` are importable from
`gzkit.content.render` and `gzkit.content.parse`.

This plan implements the four remaining subcommands (`list`, `show`, `render`, `edit`)
plus the operator manpage. All work is CLI-surface-only per REQ-0.0.34-04-04.

## Decision Quote (ADR-0.0.34 § Checklist item #4)

> "OBPI-0.0.34-04: Authoring CLI — `gz content edit / render / list / show` with
> human-readable prose output (never raw JSON in operator review surface)"

## Files

- `src/gzkit/commands/content/list.py` — new
- `src/gzkit/commands/content/show.py` — new
- `src/gzkit/commands/content/render.py` — new
- `src/gzkit/commands/content/edit.py` — new
- `src/gzkit/commands/content/__init__.py` — extend (register 4 new subcommands)
- `tests/commands/test_content_cli.py` — new (smoke tests for all 4 subcommands)
- `docs/user/manpages/gz-content.md` — new (manpage for all 5 `gz content` subcommands)

## Steps

### Step 1: Write tests (TDD — Red phase)

Create `tests/commands/test_content_cli.py` with `@covers` decorators for all 5 REQs.
Tests run against `gzkit.cli.main:main` via `CliRunner`. Write tests first; expect
them to fail because the subcommands are not registered yet.

Test cases required:
- REQ-0.0.34-04-01: `gz content list` emits a table (not raw JSON); verify no JSON parse succeeds on stdout
- REQ-0.0.34-04-01: `gz content list --json` emits valid JSON
- REQ-0.0.34-04-02: `gz content show <path>` emits prose summary (contains model type/title; no raw JSON)
- REQ-0.0.34-04-02: `gz content show <path> --json` emits valid JSON
- REQ-0.0.34-04-03: `gz content edit <path>` with invalid post-edit content exits non-zero, no partial write
- REQ-0.0.34-04-04: `gz content render <path>` output equals `render(parsed_model, vendor)` byte-for-byte
- REQ-0.0.34-04-05: `gz content --help` lists all 5 subcommands (edit, render, list, show, import)

For `edit` testing: mock `$EDITOR` to avoid real editor invocation; use subprocess-based
mock or patch `os.environ["EDITOR"]` + subprocess.run to write invalid/valid content.

### Step 2: Implement `gz content list`

Create `src/gzkit/commands/content/list.py`:
- `content_list_cmd(*, type_filter: str | None, as_json: bool) -> None`
- Without `--type`: iterate CONTENT_MODELS, display a two-column table: Type | Description
- With `--type <type>`: filter to matching type(s); exit 1 on unknown type
- Default output: human-readable table (pipe-delimited or formatted columns)
- `--json` flag: emit JSON array of `{type, description}` objects to stdout
- Exit 0 on success, 1 on bad type argument

### Step 3: Implement `gz content show`

Create `src/gzkit/commands/content/show.py`:
- `content_show_cmd(*, file: str, as_json: bool) -> None`
- Read the file, attempt to auto-detect type via `parse()` or by trying each type
- Alternatively, require `--as <type>` like `import` does (simpler, consistent)
- Display prose summary: Type, Title (if present), field count, fields listed
- `--json` flag: emit `model.model_dump_json(indent=2)` to stdout
- Exit 0 on success, 1 on parse/validation error, 2 on IO error

**Design decision:** Require `--as <type>` for `show`, consistent with `import`.
This avoids fragile type-sniffing and stays within CLI-surface-only scope.

### Step 4: Implement `gz content render`

Create `src/gzkit/commands/content/render.py`:
- `content_render_cmd(*, file: str, as_type: str, vendor: str) -> None`
- Parse the file via `parse(text, as_type, file_path=...)` from OBPI-03
- Call `render(model, vendor)` from OBPI-02
- Write bytes to stdout (binary mode: `sys.stdout.buffer.write(rendered)`)
- Default vendor: `"claude"` (consistent with `import` command)
- `--vendor` flag for machine consumers wanting other vendors
- Exit 0 on success, 1 on parse/validation error, 2 on IO error

### Step 5: Implement `gz content edit`

Create `src/gzkit/commands/content/edit.py`:
- `content_edit_cmd(*, file: str, as_type: str) -> None`
- Validate `as_type` is in CONTENT_MODELS; exit 1 if not
- Read file; fail fast if not readable (exit 2)
- Write canonical-form to a temp file via `tempfile.NamedTemporaryFile`
- Launch `$EDITOR` (or `VISUAL`) via `subprocess.run([editor, tmp_path])`
- On editor exit: read temp file, `parse()` + Pydantic `ValidationError` check
- If invalid: print diagnostic to stderr, exit 1 — NEVER write to original path
- If valid: write rendered canonical form back to original path atomically
  (write to `.tmp` sibling, then `Path.replace()` — no partial write)
- If `$EDITOR` not set: print error, exit 1

### Step 6: Extend `__init__.py` to register all 4 new subcommands

Update `src/gzkit/commands/content/__init__.py`:
- Add lazy loader functions for `list_`, `show_`, `render_`, `edit_` modules
- Register `list`, `show`, `render`, `edit` subparsers with argparse
- `list`: optional `--type <content-type>`, `--json` flag
- `show`: positional `<file>`, required `--as <type>`, `--json` flag
- `render`: positional `<file>`, required `--as <type>`, optional `--vendor` (default: "claude")
- `edit`: positional `<file>`, required `--as <type>`
- Update description in parent content parser to mention all 5 subcommands

### Step 7: Create `docs/user/manpages/gz-content.md`

Author the manpage covering all five `gz content` subcommands (import, list, show, render, edit):
- Description, Synopsis, Subcommands section
- Per-subcommand: description, flags, examples
- Exit codes
- Follow existing manpage structure (e.g., `gz-content-import`-adjacent pages)

### Step 8: Verify

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_content_cli -v
uv run gz content --help | grep -E 'edit|render|list|show'
uv run gz content list
uv run mkdocs build --strict
uv run gz validate --documents
uv run gz covers OBPI-0.0.34-04
```

## Verification

```bash
# Subcommand registration
uv run gz content --help

# Human-readable default output (not raw JSON)
uv run gz content list

# Machine output
uv run gz content list --json

# All gates
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run mkdocs build --strict
uv run gz validate --documents
uv run gz covers OBPI-0.0.34-04
```

## Notes

- `edit` command must NEVER write partial files — atomicity via `Path.replace()`.
- `render` writes bytes (binary-mode stdout) for byte-stable output.
- `show` and `list` require `--json` for machine consumption; human output is the default.
- REQ-0.0.34-04-04 scopes this to CLI + I/O only; no model/render/parse logic lives here.
- All 4 new modules follow the `import_.py` pattern: lazy-load via `_content(name)` in `__init__.py`.
