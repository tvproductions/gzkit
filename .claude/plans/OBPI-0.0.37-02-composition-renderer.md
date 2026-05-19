# Plan: OBPI-0.0.37-02-composition-renderer

**OBPI:** OBPI-0.0.37-02-composition-renderer
**Parent ADR:** ADR-0.0.37-constitutional-invariant-composition
**Lane:** Heavy
**Date:** 2026-05-19

## Context

OBPI-0.0.37-01 (schema + registry primitive) has landed. `src/gzkit/governance/invariants.py`
and `.gzkit/invariants/*.json` are present. `ConstitutionalInvariant` Pydantic model and
`load_invariants(root)` are the consumed API. Jinja2 `>=3.1` is already a declared
project dependency (`pyproject.toml`). No YAML — the registry files are JSON per
the AGENTS.md no-YAML-for-data-files rule established in OBPI-01.

This OBPI lands the deterministic composition renderer and the `gz governance render`
CLI verb. It does NOT register ledger events (OBPI-03 scope). No modification to
`AGENTS.md` itself (OBPI-09 scope). The renderer is a stand-alone producer.

**Destination-in-mind (Step 6a disclosure):** Before authoring this plan, the
implementation approach was already formed: Jinja2 as the primary template engine
(it's already a dep), `string.Template` as the import-fail fallback, test fixtures
in `tests/fixtures/compose/` with a minimal Jinja2 template, CLI implemented via the
existing `_LAZY_HANDLERS` + lazy-dispatch pattern in `parser_artifacts.py`.

**Rejected alternatives:**
- `str.format_map()` instead of Jinja2/string.Template: rejected because REQ-03
  explicitly names the two acceptable approaches (Jinja2 then string.Template).
- A new template file (not `agents.md` in template_root): rejected because the brief
  says "project into AGENTS.md template shape"; `template_root / "agents.md"` is the
  canonical projection target.
- Parallel parallel dispatch for tests: N/A — steps are sequential TDD increments.

## Files

**New:**
- `src/gzkit/governance/compose.py`
- `src/gzkit/commands/governance_render.py`
- `tests/governance/test_compose.py`
- `tests/commands/test_governance_render.py`
- `tests/fixtures/compose/` (directory with `agents.md` Jinja2 template + fixture JSONs)
- `docs/user/manpages/gz-governance.md`
- `features/constitutional_invariants.feature`
- `features/steps/constitutional_invariants_steps.py`

**Modified:**
- `src/gzkit/cli/parser_artifacts.py` (add `governance_render_cmd` to `_LAZY_HANDLERS`; add `_register_governance_parsers`)
- `docs/user/runbook.md` (add `gz governance render --check` entry)
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-02-composition-renderer.md` (evidence sections)

## Steps

### Step 1: TDD RED — test_compose.py

Write `tests/governance/test_compose.py` with failing tests:

1a. Create `tests/fixtures/compose/agents.md` — minimal Jinja2 template:
```
# AGENTS

{% for inv_id, inv in invariants.items() %}
## {{ inv_id }}
{{ inv.claim }}
{% endfor %}
```

1b. Create `tests/fixtures/compose/CIC-test-1.json` and `CIC-test-2.json` —
two fixture invariant JSON files with valid `id`, `claim`, `structural_witness`,
`composition_targets` fields (matching constitutional_invariant.json schema).

1c. Write test class `TestRenderAgentsMd` with `@covers("REQ-0.0.37-02-01")` and
`@covers("REQ-0.0.37-02-02")` decorators:
- `test_byte_determinism_same_call`: call `render_agents_md` twice with same args,
  assert `result1 == result2` (REQ-01)
- `test_byte_determinism_different_process`: render twice with fixture data, assert
  byte-identical (REQ-01)
- `test_sorted_iteration_order`: fixture has inv-B and inv-A; assert rendered bytes
  contain inv-A before inv-B regardless of dict insertion order (REQ-02)
- `test_template_based_not_hardcoded`: change template content, assert rendered bytes
  change accordingly (REQ-03 — template-driven)
- `test_output_is_bytes`: assert return type is `bytes` (REQ-01)
- `test_missing_template_raises`: template_root with no `agents.md` raises (defensive)

Run: `uv run -m unittest tests.governance.test_compose -v` → expect FAIL
(module `gzkit.governance.compose` does not exist yet)

### Step 2: TDD GREEN — compose.py

Implement `src/gzkit/governance/compose.py`:

```python
"""Composition renderer for constitutional invariant registry (ADR-0.0.37, OBPI-0.0.37-02)."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from gzkit.governance.invariants import ConstitutionalInvariant


def render_agents_md(
    invariants: Mapping[str, ConstitutionalInvariant],
    template_root: Path,
) -> bytes:
    """Render AGENTS.md bytes from the invariant registry.

    Byte-deterministic: same inputs produce identical bytes across calls and processes.
    Iteration order is always lexicographic by id (REQ-02).
    Uses Jinja2 if importable; falls back to stdlib string.Template (REQ-03).
    """
    sorted_invariants: dict[str, ConstitutionalInvariant] = dict(sorted(invariants.items()))
    template_path = template_root / "agents.md"
    template_text = template_path.read_text(encoding="utf-8")

    try:
        from jinja2 import BaseLoader, Environment  # type: ignore
        env = Environment(loader=BaseLoader(), keep_trailing_newline=True)
        tmpl = env.from_string(template_text)
        rendered = tmpl.render(invariants=sorted_invariants)
    except ImportError:
        from string import Template
        tmpl = Template(template_text)
        rendered = tmpl.substitute(invariants=sorted_invariants)

    return rendered.encode("utf-8")
```

Run lint and tests: `uv run ruff check . --fix && uv run ruff format . && uv run -m unittest tests.governance.test_compose -v` → expect PASS

### Step 3: TDD RED — test_governance_render.py

Write `tests/commands/test_governance_render.py` with failing tests.
Use `tests/commands/common.py` patterns for CLI invocation isolation.

Test class `TestGovernanceRenderCmd`:
- `@covers("REQ-0.0.37-02-04")` `test_stdout_mode_emits_bytes`: call the command
  handler with `--stdout` flag; assert stdout contains rendered bytes, no file written
- `@covers("REQ-0.0.37-02-02")` `test_check_exits_0_on_match`: write rendered output
  to a temp AGENTS.md, run `--check` against it, assert exit code 0
- `@covers("REQ-0.0.37-02-02")` `test_check_exits_3_on_drift`: write modified content
  to temp AGENTS.md, run `--check`, assert SystemExit(3) raised; assert diff emitted
- `@covers("REQ-0.0.37-02-03")` `test_write_mode_writes_file`: run without `--check`
  or `--stdout`, assert file at AGENTS.md path contains rendered bytes
- `@covers("REQ-0.0.37-02-05")` `test_unsupported_target_raises_argparse_error`:
  invoke with `--target skill-readme`, assert SystemExit(2) with "unsupported target"
  in stderr
- `@covers("REQ-0.0.37-02-06")` `test_no_ledger_event_emitted`: run renderer in
  write mode, confirm no ledger event was written (read ledger tail, assert no
  `composition_rendered` event — that's OBPI-03's scope)

Run: `uv run -m unittest tests.commands.test_governance_render -v` → expect FAIL

### Step 4: TDD GREEN — governance_render.py + parser wiring

4a. Implement `src/gzkit/commands/governance_render.py`:

```python
"""gz governance render command implementation (OBPI-0.0.37-02)."""

from __future__ import annotations

import difflib
import sys
from pathlib import Path

from gzkit.commands.common import get_project_root
from gzkit.governance.compose import render_agents_md
from gzkit.governance.invariants import load_invariants


_SUPPORTED_TARGETS = {"agents-md"}


def governance_render_cmd(
    *,
    target: str,
    check: bool = False,
    stdout: bool = False,
) -> None:
    """Implement ``gz governance render --target agents-md``."""
    if target not in _SUPPORTED_TARGETS:
        raise SystemExit(f"unsupported target: {target!r}. Supported: {sorted(_SUPPORTED_TARGETS)}")

    root = get_project_root()
    invariants = load_invariants(root)
    template_root = Path(__file__).parent.parent / "templates"
    rendered = render_agents_md(invariants, template_root)

    if stdout:
        sys.stdout.buffer.write(rendered)
        return

    agents_path = root / "AGENTS.md"

    if check:
        current = agents_path.read_bytes() if agents_path.exists() else b""
        if current == rendered:
            return  # exit 0 — no drift
        current_lines = current.decode("utf-8", errors="replace").splitlines(keepends=True)
        rendered_lines = rendered.decode("utf-8").splitlines(keepends=True)
        diff = list(difflib.unified_diff(
            current_lines, rendered_lines,
            fromfile="AGENTS.md", tofile="<rendered>",
            n=3,
        ))[:50]
        sys.stderr.writelines(diff)
        raise SystemExit(3)

    agents_path.write_bytes(rendered)
    print(f"Wrote {len(rendered)} bytes to {agents_path.as_posix()}")
```

4b. Wire into `src/gzkit/cli/parser_artifacts.py`:
- Add `"governance_render_cmd": "gzkit.commands.governance_render"` to `_LAZY_HANDLERS`
- Add `_register_governance_parsers(commands)` function:
  ```python
  def _register_governance_parsers(commands: argparse._SubParsersAction) -> None:
      p_gov = commands.add_parser(
          "governance",
          help="Constitutional invariant governance commands",
      )
      gov_commands = p_gov.add_subparsers(dest="governance_command")
      gov_commands.required = True

      p_render = gov_commands.add_parser(
          "render",
          help="Render a governance surface from the invariant registry",
      )
      p_render.add_argument("--target", required=True, help="Render target (agents-md)")
      p_render.add_argument("--check", action="store_true", help="Byte-compare; exit 3 on drift")
      p_render.add_argument("--stdout", action="store_true", help="Emit to stdout; do not write file")
      p_render.set_defaults(
          func=lambda a: _lazy("governance_render_cmd")(
              target=a.target, check=a.check, stdout=a.stdout
          )
      )
  ```
- Call `_register_governance_parsers(commands)` in `register_artifact_parsers()`

Run: `uv run ruff check . --fix && uv run ruff format . && uv run -m unittest tests.commands.test_governance_render -v` → expect PASS

Also run full suite: `uv run -m unittest -q` → expect all pass

### Step 5: Heavy Lane Docs

5a. Create `docs/user/manpages/gz-governance.md`:
```markdown
# gz-governance(1)

## NAME

gz-governance — constitutional invariant governance commands

## SYNOPSIS

```
gz governance render --target <target> [--check] [--stdout]
```

## DESCRIPTION

The `governance` command group exposes constitutional invariant governance
operations. Currently the only supported subcommand is `render`.

### gz governance render

Render a governance surface from the constitutional invariant registry at
`.gzkit/invariants/`. The rendered output is byte-deterministic — the same
registry state and template always produce identical bytes.

## OPTIONS

### render

`--target agents-md`
: The only accepted render target. Future targets (skill READMEs, persona files)
  are forward-references for future feature ADRs.

`--check`
: Compare the rendered bytes against the committed file. Exits 0 on match;
  exits 3 on drift and prints a unified diff of the first 50 differing lines.
  Does not write the file.

`--stdout`
: Emit rendered bytes to stdout. Does not write the file.
  Used by drift validators and integration tests.

## EXAMPLES

Check whether AGENTS.md is in sync with the registry:

```
gz governance render --target agents-md --check
```

Stream rendered bytes to stdout for inspection:

```
gz governance render --target agents-md --stdout
```

Confirm byte-determinism across two invocations:

```
diff <(gz governance render --target agents-md --stdout) \
     <(gz governance render --target agents-md --stdout) \
  && echo "byte-identical"
```

Write rendered output to AGENTS.md (after template migration in OBPI-09):

```
gz governance render --target agents-md
```
```

5b. Update `docs/user/runbook.md` — add entry under a "Governance render" section:
```markdown
### When AGENTS.md drifts: `gz governance render --check`

If `gz check` reports invariant-coherence drift (OBPI-03 wires the validator),
run:

```bash
gz governance render --target agents-md --check
```

Exit 0: AGENTS.md matches the registry — no action needed.
Exit 3: drift detected — a unified diff is printed. Run without `--check` to
regenerate, or edit the registry entry that changed.
```

5c. Verify docs build: `uv run mkdocs build --strict`

### Step 6: BDD scenarios (Heavy lane Gate 4)

6a. Create `features/constitutional_invariants.feature`:

```gherkin
Feature: Constitutional invariant composition renderer
  As an operator maintaining gzkit governance
  I want the composition renderer to produce byte-deterministic output
  And I want --check mode to detect drift precisely

  @REQ-0.0.37-02-01
  Scenario: Renderer produces identical bytes across consecutive invocations
    Given the constitutional invariant registry has at least one entry
    When I run "gz governance render --target agents-md --stdout" twice
    Then the two outputs are byte-identical

  @REQ-0.0.37-02-02
  Scenario: --check exits 0 when committed file matches rendered output
    Given the constitutional invariant registry has at least one entry
    And AGENTS.md contains the current rendered output
    When I run "gz governance render --target agents-md --check"
    Then the command exits with code 0

  @REQ-0.0.37-02-02
  Scenario: --check exits 3 and prints diff when file differs from rendered output
    Given the constitutional invariant registry has at least one entry
    And AGENTS.md contains stale content
    When I run "gz governance render --target agents-md --check"
    Then the command exits with code 3
    And the output contains a unified diff

  @REQ-0.0.37-02-03
  Scenario: Unsupported target exits with argparse error "unsupported target"
    When I run "gz governance render --target skill-readme"
    Then the command exits with a non-zero code
    And the output contains "unsupported target"
```

6b. Create `features/steps/constitutional_invariants_steps.py` with step definitions
that use subprocess to invoke `gz governance render` commands.

6c. Run: `uv run -m behave features/constitutional_invariants.feature` → expect PASS

### Step 7: REQ-coverage parity gate

```bash
uv run gz covers OBPI-0.0.37-02-composition-renderer --json
```

Confirm `summary.uncovered_reqs == 0`.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_compose tests.commands.test_governance_render -v
uv run mkdocs build --strict
uv run -m behave features/constitutional_invariants.feature
uv run gz covers OBPI-0.0.37-02-composition-renderer --json

# REQ-01/02: byte-determinism
diff <(uv run gz governance render --target agents-md --stdout) \
     <(uv run gz governance render --target agents-md --stdout) && echo "REQ-01 OK"

# REQ-04/02: --check exit codes (after rendering once)
uv run gz governance render --target skill-readme 2>&1 | grep -q "unsupported target" && echo "REQ-06 OK"
```

## Notes

- OBPI-03 (drift validator) is downstream — this OBPI does NOT emit
  `composition_rendered` ledger events. Tests explicitly assert no ledger events.
- The `string.Template` fallback in compose.py is import-guard protected; since
  Jinja2 is a hard dependency, the fallback path is defensive for wheel-build
  edge cases only.
- Scope collisions listed by `gz plan audit` are all advisory (no active locks
  on contested paths at time of plan authoring).
- `src/gzkit/templates/agents.md` is NOT modified here; the existing template
  uses `{var}` format syntax. Test fixtures use separate Jinja2 templates.
  OBPI-09 handles the actual migration.
