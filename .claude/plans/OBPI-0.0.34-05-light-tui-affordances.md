# Plan: OBPI-0.0.34-05 Light TUI Affordances

**OBPI:** OBPI-0.0.34-05-light-tui-affordances
**ADR:** ADR-0.0.34-agent-control-surface-rendering-substrate
**ADR Decision item #5 (verbatim):** "Light TUI affordances. Claude-Code-style status lines, chore-runner result tables, plan-mode panels — native CLI affordances. No Textual form editor, no dedicated authoring app."

## Context

- `rich v15.0.0` is already a transitive dependency. No new top-level dependency needed.
- OBPI-0.0.34-04 is complete: `gz content list/show/render/edit` all exit 0.
- All four command handlers currently emit plain text only (no TTY awareness).
- `src/gzkit/content/tui/` does not yet exist — must be created.

## Files

**Create:**
- `src/gzkit/content/tui/__init__.py` — public re-exports
- `src/gzkit/content/tui/status.py` — Claude-Code-style status line for `render`/`edit`
- `src/gzkit/content/tui/tables.py` — Rich table renderer for `list`
- `src/gzkit/content/tui/panels.py` — plan-mode-style panel for `show`
- `tests/content/test_tui_affordances.py` — TTY-on/off, --plain flag, no-textual

**Modify:**
- `src/gzkit/commands/content/render.py` — wire status line (TTY-conditional)
- `src/gzkit/commands/content/edit.py` — wire status line (TTY-conditional)
- `src/gzkit/commands/content/list.py` — wire Rich table (TTY-conditional)
- `src/gzkit/commands/content/show.py` — wire Rich panel (TTY-conditional)
- `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/obpis/OBPI-0.0.34-05-light-tui-affordances.md` — evidence

## Steps

### Step 1: TDD Red — Write failing tests (REQ-0.0.34-05-01 through -05)

Write `tests/content/test_tui_affordances.py` with test cases derived from the 5 REQs:
- `TestStatusLine.test_render_tty_emits_status_to_stderr` (REQ-01)
- `TestTableRenderer.test_list_tty_uses_rich_table` (REQ-02)
- `TestTableRenderer.test_list_non_tty_plain_no_ansi` (REQ-02)
- `TestPanelRenderer.test_show_tty_uses_rich_panel` (REQ-03)
- `TestPanelRenderer.test_plain_flag_suppresses_rich` (REQ-03)
- `TestTextualAbsence.test_no_textual_import_in_src` (REQ-04)
- `TestTextualAbsence.test_no_textual_in_pyproject` (REQ-04 — check pyproject.toml)
- `TestCommandSurface.test_no_new_subcommands` (REQ-05)

Run `uv run -m unittest tests.content.test_tui_affordances -v` → expect failures (RED).

### Step 2: Create `src/gzkit/content/tui/` package

**`src/gzkit/content/tui/status.py`** — `render_status_line(operation: str, source: str, result: str, byte_count: int | None = None) -> None`
- Writes a Rich `[green]✓[/green] <operation> <source> → <result> (<size>)` to stderr via `Console(stderr=True)`.
- Only called when `sys.stdout.isatty()` is True (caller checks).

**`src/gzkit/content/tui/tables.py`** — `render_content_table(rows: list[dict[str, str]]) -> None`
- Renders a Rich `Table` with columns "Type" and "Description" to stdout.
- Caller checks `sys.stdout.isatty()` and `--plain` before calling.

**`src/gzkit/content/tui/panels.py`** — `render_content_panel(title: str, body: str) -> None`
- Renders a Rich `Panel` (plan-mode-style, no padding) to stdout.
- Caller checks `sys.stdout.isatty()` and `--plain` before calling.

**`src/gzkit/content/tui/__init__.py`** — re-export the three functions.

### Step 3: Wire TTY-conditional rendering into command handlers

**`src/gzkit/commands/content/list.py`:**
- Add `--plain` flag to argument parser (in `__init__.py` content subcommand wiring).
- In `content_list_cmd`: if `sys.stdout.isatty() and not plain`: call `render_content_table(rows)` from `tui`; else: existing plain-text path.

**`src/gzkit/commands/content/show.py`:**
- Add `--plain` flag.
- In `content_show_cmd`: if `sys.stdout.isatty() and not plain`: call `render_content_panel(title, body_text)` from `tui`; else: existing prose path.

**`src/gzkit/commands/content/render.py`:**
- In `content_render_cmd`: after successful render, if `sys.stdout.isatty()`: call `render_status_line("rendered", file, vendor, byte_count)` from `tui` to stderr. stdout still gets the rendered bytes (unchanged).

**`src/gzkit/commands/content/edit.py`:**
- In `content_edit_cmd`: after successful atomic replace, if `sys.stdout.isatty()`: call `render_status_line("edited", file, as_type, byte_count)` from `tui` to stderr.

### Step 4: Run TDD Green + Refactor

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest tests.content.test_tui_affordances -v
uv run -m unittest -q
```

All tests pass. Green.

### Step 5: Verify full quality suite

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
uv run mkdocs build --strict
```

### Step 6: Present OBPI Acceptance Ceremony

## Verification

```bash
uv run python -m unittest tests.content.test_tui_affordances -v
grep -r "^import textual" src/ tests/   # MUST produce no matches
grep -r "from textual" src/ tests/      # MUST produce no matches
uv run gz content list --plain          # plain text, no ANSI
uv run gz check
```

## Notes

- `--plain` flag is a new additive flag on `list` and `show`. This is Lite-lane under the CLI Contract Doctrine (additive flag, no new subcommand). However, the OBPI itself is Heavy because it changes the TTY-conditional runtime rendering contract of existing commands.
- The `render` and `edit` status line goes to **stderr** so stdout remains machine-readable (piped output is unaffected).
- `sys.stdout.isatty()` is mocked in tests via `unittest.mock.patch("sys.stdout.isatty", return_value=True/False)`.
- No Textual import anywhere in `src/` or `tests/` — enforced by test and by brief REQ-04.
