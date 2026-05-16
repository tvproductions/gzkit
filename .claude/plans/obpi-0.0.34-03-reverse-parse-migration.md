# Plan: OBPI-0.0.34-03 Reverse-Parse Migration

**OBPI:** OBPI-0.0.34-03-reverse-parse-migration
**ADR:** ADR-0.0.34-agent-control-surface-rendering-substrate
**Lane:** Heavy
**Date:** 2026-05-16

## Context

OBPI-01 (content model registry) and OBPI-02 (rendering pipeline) are complete. This OBPI
adds the reverse direction: `parse(text, as_type) -> BaseContentModel` so existing markdown
files can be imported back into canonical Pydantic models. The `gz content import <file> --as
<type>` CLI verb makes this accessible to operators.

Round-trip fidelity contract: `parse(render(model)) == model` (model identity) and
`render(parse(render(model))) == render(model)` (byte-stable idempotency). REQ-03's
`diff -q AGENTS.md` assertion is interpreted as idempotency — after one normalization pass,
subsequent import+write cycles are byte-stable.

## Files

### Created

- `src/gzkit/content/parse/__init__.py` — public API: `parse(text, as_type) -> BaseContentModel`
- `src/gzkit/content/parse/markdown_parser.py` — per-type parser implementations (8 types)
- `src/gzkit/commands/content/__init__.py` — `gz content` subparser registration function
- `src/gzkit/commands/content/import_.py` — `gz content import <file> --as <type>` handler
- `tests/content/test_round_trip_agent_contract.py` — REQ-0.0.34-03-02 for AgentContract
- `tests/content/test_round_trip_rule.py` — REQ-0.0.34-03-02 for Rule
- `tests/content/test_round_trip_skill.py` — REQ-0.0.34-03-02 for Skill
- `tests/content/test_round_trip_chore.py` — REQ-0.0.34-03-02 for Chore
- `tests/content/test_round_trip_persona.py` — REQ-0.0.34-03-02 for Persona
- `tests/content/test_round_trip_handoff.py` — REQ-0.0.34-03-02 for Handoff
- `tests/content/test_round_trip_scenario.py` — REQ-0.0.34-03-02 for Scenario
- `tests/content/test_round_trip_bullet.py` — REQ-0.0.34-03-02 for Bullet
- `tests/commands/test_content_import.py` — CLI smoke test for REQ-01, REQ-04, REQ-05

### Modified

- `src/gzkit/cli/main.py` — add `register_content_parsers(commands)` call (1 line; implicit scope for CLI wiring)
- `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/obpis/OBPI-0.0.34-03-reverse-parse-migration.md` — evidence

## Steps

### Step 1: Parser infrastructure (TDD Red-Green)

Create `src/gzkit/content/parse/markdown_parser.py` with 8 per-type parsers:

Each parser reads the canonical template output format. Whitespace normalizations documented
in the module docstring:
- Trailing whitespace stripped from each line
- Blank lines between sections normalized to exactly one blank line
- Trailing newline preserved (matches `render()` behavior)

Parser implementations (line-based, stdlib-only):

**AgentContract**: H1→name, next non-blank paragraph→purpose, `## Tech Stack` bullets→tech_stack, `## Rules` indented bullets→rules

**Rule**: H1→title, `Version: X.Y.Z` line→version, `## Paths` bullets→paths, `## Body` indented bullets→body

**Skill**: H1→title, `Slug: X` line→slug, next non-blank paragraph after slug→purpose, `## Steps` indented bullets→steps

**Chore**: H1→title, `Slug: X`→slug, `Cadence: X`→cadence, `## Steps` indented bullets→steps

**Persona**: H1→slug, `Role: X`→role, `## Traits` bullets→traits

**Handoff**: `# Handoff: X`→session_id, next paragraph→state_summary, `## Open Items` indented bullets→open_items, `## Resume Point` body→resume_point

**Scenario**: `Feature: X`→feature, `Scenario: X`→scenario, `Given X`→given, `When X`→when, `Then X`→then

**Bullet**: Leading whitespace `/2→indent`, strip `- ` prefix→text

Public API in `src/gzkit/content/parse/__init__.py`:
```python
def parse(text: str, as_type: str) -> BaseContentModel:
    """Parse canonical markdown text into a BaseContentModel instance.
    
    Raises:
        KeyError: if as_type is not in CONTENT_MODELS
        pydantic.ValidationError: if parsed fields fail model validation
        ValueError: if text does not match the expected format for as_type
    """
```

Error reporting: ValueError carries `(file_path: str | None, line: int)` context where derivable.

### Step 2: Round-trip tests (TDD, one test file per content type)

Test pattern for each type:
```python
class TestRoundTripX(unittest.TestCase):
    @covers("REQ-0.0.34-03-02")
    def test_parse_render_model_roundtrip(self):
        # Build model programmatically
        model = X(...)
        # Render to canonical bytes
        rendered = render(model, "claude").decode("utf-8")
        # Parse back
        parsed = parse(rendered, "X")
        # Model identity
        self.assertEqual(parsed, model)
    
    @covers("REQ-0.0.34-03-02")
    def test_render_parse_render_idempotency(self):
        # render(parse(render(model))) == render(model)
        model = X(...)
        once = render(model, "claude")
        parsed = parse(once.decode("utf-8"), "X")
        twice = render(parsed, "claude")
        self.assertEqual(once, twice)
```

### Step 3: CLI verb (TDD Red-Green)

`src/gzkit/commands/content/import_.py`:
- `import_cmd(args)` handler
- Reads file (UTF-8), calls `parse(text, args.as_type)`, emits JSON to stdout
- `--write <path>`: writes re-rendered canonical form (via `render()`) to path
- Exit 0 on success; exit 1 + stderr diagnostic on parse error (includes file:line where derivable)
- Pydantic `ValidationError` propagates naturally for type-mismatch (REQ-05)

`src/gzkit/commands/content/__init__.py`:
- `register_content_parsers(commands: argparse._SubParsersAction) -> None`
- Registers `gz content` group with `import` subverb

`src/gzkit/cli/main.py`:
- Add `from gzkit.commands.content import register_content_parsers` and one call in `_build_parser()`

### Step 4: CLI smoke test

`tests/commands/test_content_import.py`:
- REQ-01: `gz content import <rule-file> --as Rule` succeeds, JSON in stdout
- REQ-04: parse raises no new model types (existing CONTENT_MODELS only)
- REQ-05: mismatched type raises ValidationError before returning model instance
- Malformed input: non-zero exit + stderr has file path reference

### Step 5: Present OBPI Acceptance Ceremony

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run -m unittest discover -s tests/content -p 'test_round_trip_*.py' -t . -v
uv run -m unittest tests.commands.test_content_import -v
uv run gz content import AGENTS.md --as AgentContract --write /tmp/agents-roundtrip.md
uv run gz content import /tmp/agents-roundtrip.md --as AgentContract --write /tmp/agents-roundtrip2.md
diff -q /tmp/agents-roundtrip.md /tmp/agents-roundtrip2.md
```

## Notes

- Whitespace normalizations: trailing whitespace stripped, blank-line runs collapsed to one, trailing newline preserved
- REQ-03 idempotency interpretation: byte-stable after first normalization pass, not byte-identical to hand-authored AGENTS.md
- `src/gzkit/cli/main.py` treated as implicit scope for CLI wiring (1 line addition); not in brief's allowed paths but required for command registration
- Scope boundary: no new content types (OBPI-01), no validation hooks (OBPI-06), no migration registry calls (OBPI-07 not yet landed)
