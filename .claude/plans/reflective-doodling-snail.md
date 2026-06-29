# OBPI-0.30.0-04 Implementation Plan: OKF CLI Surface

## Context

**What:** Implement the CLI surface for the OKF bundle generator to give operators a command to emit and refresh the bundle.

**Why:** The OKF orientation bundle (generated in OBPI-02) currently can only be produced by invoking the generator module directly. Operators need a user-facing CLI command: `gz knowledge generate` to emit the bundle, `gz knowledge refresh` to re-generate idempotently.

**Scope:** OBPI-0.30.0-04 delivers:
- New command module with `knowledge_cmd()` entry point
- CLI registration in `src/gzkit/cli/parser_artifacts.py`
- New manpage: `docs/user/manpages/knowledge.md`
- Unit tests for the CLI surface and generator integration
- Behave smoke test for end-to-end generate/refresh flow
- Verification that `gz cli audit` passes (manpage + index coverage)

**Constraints:**
- Heavy lane: new CLI verb is an external contract change requiring human attestation (Gate 5)
- Command MUST NOT consume OKF frontmatter as enforcement evidence (Boundary Invariant 1)
- Generation logic delegates to `src/gzkit/knowledge/generate.generate_bundle()`; this OBPI only wraps it
- TDD discipline: tests derived from acceptance criteria, not from implementation
- Follow existing gzkit patterns (lazy handler dispatch, sys.exit(), Path operations with UTF-8)

---

## Phase 1: Exploration Summary

### ✅ Agent 1: Knowledge Generator Module

**Public Interface:**
- Function: `generate_bundle(sources: list[SourceEntry], output_dir: Path | str) -> None`
- Constants: `TRACER_SLICE` (4 hardcoded governance sources), `BUNDLE_OUTPUT = Path(".gzkit/governance/knowledge")`

**For CLI Wrapping:**
- Both `generate` and `refresh` call: `generate_bundle(TRACER_SLICE, BUNDLE_OUTPUT)`
- Idempotent (same output on re-run with unchanged sources)
- No special error handling needed; Path exceptions propagate naturally

### ✅ Agent 2: CLI Command and Registration Patterns

**Architecture:** Parser registration → lazy handler dispatch → command implementation

**Key Pattern:**
- Function `_register_knowledge_parser()` in `src/gzkit/cli/parser_artifacts.py`
- Use `add_subparsers()` for generate/refresh
- Dispatch via `set_defaults(func=lambda a: _lazy("knowledge_cmd")(...args...))`
- Handler: `def knowledge_cmd(*, subverb: str | None = None) -> None:`
- Exit codes: 0=success, 2=system/IO error

### ✅ Agent 3: Manpage and Test Patterns

**Manpage:** Sections: NAME, SYNOPSIS, DESCRIPTION, OPTIONS, EXIT STATUS, EXAMPLES
**Unit Tests:** Helper function, @covers decorator, organized test classes
**Behave:** `When I run the gz command "..."` syntax, REQ tags

---

## Implementation Strategy

### File Structure

```
src/gzkit/commands/knowledge.py          (new)
src/gzkit/cli/parser_artifacts.py        (modify - add _register_knowledge_parser)
src/gzkit/cli/parser_handler_manifest.py (modify - add lazy handler entry)
docs/user/manpages/knowledge.md          (new)
docs/user/manpages/index.md              (modify - add knowledge row)
features/knowledge.feature               (new)
tests/commands/test_knowledge.py         (new)
```

### Deliverables

#### 1. Command Handler: `src/gzkit/commands/knowledge.py`

- Single `knowledge_cmd(*, subverb: str | None = None) -> None` function
- Both generate and refresh invoke `generate_bundle(TRACER_SLICE, BUNDLE_OUTPUT)`
- Catch OSError/FileNotFoundError → print to stderr → sys.exit(EXIT_SYSTEM_ERROR)

#### 2. CLI Parser: `src/gzkit/cli/parser_artifacts.py`

- New `_register_knowledge_parser()` function
- Parent parser: "knowledge" verb
- Subparsers: "generate" and "refresh"
- Call in `register_artifact_parsers()`

#### 3. Lazy Handler: `src/gzkit/cli/parser_handler_manifest.py`

- Add: `"knowledge_cmd": "gzkit.commands.knowledge"` to `_LAZY_HANDLERS`

#### 4. Manpage: `docs/user/manpages/knowledge.md`

- Title: `# gz knowledge`
- Sections: Usage, Description, Exit Codes, Examples
- Document both subcommands in SYNOPSIS and EXAMPLES

#### 5. Manpage Index: `docs/user/manpages/index.md`

- Add row: `| \`gz knowledge\` | Generate/refresh OKF knowledge bundle |`

#### 6. Unit Tests: `tests/commands/test_knowledge.py`

**Test Coverage (from OBPI brief acceptance criteria):**
- REQ-0.30.0-04-01 (BEHAVIOR): generate exits 0 and produces bundle
- REQ-0.30.0-04-02 (BEHAVIOR): refresh is idempotent (byte-identical)
- REQ-0.30.0-04-03 (SUPPORT): manpage exists, `gz cli audit` passes
- REQ-0.30.0-04-04 (BEHAVIOR): end-to-end CLI smoke

**Pattern:**
- Helper: `_invoke_knowledge(*, subverb=None) -> int` converts SystemExit to code
- Test classes: `TestKnowledgeGenerate`, etc.
- Decorators: `@covers("REQ-0.30.0-04-XX")`
- Clean bundle dir in setUp/tearDown

#### 7. Behave Feature: `features/knowledge.feature`

- Scenario 1: Generate exits 0, files created (REQ-0.30.0-04-01, -04)
- Scenario 2: Refresh idempotent (REQ-0.30.0-04-02)
- Scenario 3: CLI audit passes (REQ-0.30.0-04-03)

---

## Verification Checklist

After implementation:
```bash
uv run -m unittest tests.commands.test_knowledge -v
uv run gz lint
uv run gz typecheck
uv run gz knowledge generate
uv run gz knowledge refresh
uv run gz cli audit
uv run -m behave features/knowledge.feature
uv run mkdocs build --strict
```

**Success Criteria:**
- All tests pass with REQ coverage
- Lint/type check clean
- Bundle generated to `.gzkit/governance/knowledge/`
- Refresh produces byte-identical output
- Manpage renders; `gz cli audit` exits 0

---

## Status

✅ **Exploration Complete** — All three agents returned detailed findings
✅ **Design Finalized** — Implementation strategy ready
⏳ **Ready for Approval** — Call ExitPlanMode to proceed
