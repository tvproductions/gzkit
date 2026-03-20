---
id: OBPI-0.17.0-03-slim-claudemd-template
parent: ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir
item: 3
lane: heavy
status: Completed
---

# OBPI-0.17.0-03-slim-claudemd-template: Slim CLAUDE.md Template

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir/ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir.md`
- **Checklist Item:** #3 - "Slim CLAUDE.md Template"

**Status:** Completed

## Objective

Reduce CLAUDE.md to a slim generated template (~50 lines) that delegates governance rules to `.claude/rules/`, skills to `.claude/skills/`, and defers to `AGENTS.md` as the authoritative contract — with regression tests preventing re-bloating and `agents.local.md` injection for project-specific additions.

## Lane

**heavy** - Inherited from parent ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir (heavy).

> Heavy is reserved for command/API/schema/runtime-contract changes. CLAUDE.md is an external agent contract surface consumed by Claude Code.

## Allowed Paths

- `src/gzkit/templates/claude.md` - CLAUDE.md template (50 lines, 6 placeholders)
- `src/gzkit/sync.py` - `sync_claude_md()` generation function
- `src/gzkit/templates/__init__.py` - `render_template()` function
- `tests/test_templates.py` - Template rendering and slimming regression tests
- `CLAUDE.md` - Generated output (read-only verification)

## Denied Paths

- `docs/design/**` - ADR changes out of scope (except this brief)
- New dependencies
- CI files, lockfiles
- `AGENTS.md` - Separate OBPI scope (OBPI-01)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: CLAUDE.md template MUST be <=60 lines with placeholder-driven generation.
2. REQUIREMENT: Template MUST delegate skills to `.claude/skills/` directory reference, NOT embed catalog.
3. REQUIREMENT: Template MUST delegate rules to `.claude/rules/` directory reference, NOT inline rules.
4. REQUIREMENT: Template MUST declare `AGENTS.md` as authoritative governance contract.
5. REQUIREMENT: `agents.local.md` content MUST be injected at template tail with HTML comment markers.
6. NEVER: Skill catalogs, ceremony steps, or workflow prose may not appear in CLAUDE.md.
7. ALWAYS: `sync_claude_md()` must produce identical output to current CLAUDE.md when given same inputs.

> STOP-on-BLOCKERS: if `src/gzkit/templates/claude.md` is missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` - agent operating contract (Layer 3 control surface)
- [x] Parent ADR - three-layer control surface model

**Context:**

- [x] Parent ADR: ADR-0.17.0 Layer 3 control surface documents
- [x] Related OBPIs: OBPI-01 (Skill Catalog), OBPI-02 (Rules Mirroring)

**Prerequisites (check existence, STOP if missing):**

- [x] `src/gzkit/templates/claude.md` exists (50 lines, 6 placeholders)
- [x] `src/gzkit/sync.py` contains `sync_claude_md()` function

**Existing Code (understand current state):**

- [x] Template: `src/gzkit/templates/claude.md` — 50 lines with {project_name}, {project_purpose}, {tech_stack}, {build_commands}, {coding_conventions}, {local_content}
- [x] Generation: `src/gzkit/sync.py` `sync_claude_md()` lines 1183-1195
- [x] Context: `get_project_context()` lines 1033-1081
- [x] Tests: `tests/test_templates.py` TestAdapterTemplatesReferenceCanon, TestRootSurfaceSlimming

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] CLAUDE.md is the documentation artifact itself

### Gate 4: BDD (Heavy only)

- [x] N/A — no behave features for CLAUDE.md template

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification: CLAUDE.md line count and content checks
uv run python -c "
from pathlib import Path
claude = Path('CLAUDE.md').read_text(encoding='utf-8')
lines = claude.splitlines()
print(f'CLAUDE.md: {len(lines)} lines')
assert len(lines) <= 60, f'CLAUDE.md too large: {len(lines)} lines'
assert 'AGENTS.md' in claude, 'Missing AGENTS.md reference'
assert '.claude/rules/' in claude, 'Missing rules delegation'
assert '.claude/skills/' in claude, 'Missing skills delegation'
assert 'agents.local.md' in claude, 'Missing local content injection'
print('PASS: Slim CLAUDE.md validated')
"

# Verify template does NOT embed catalogs
uv run python -c "
from gzkit.templates import render_template
content = render_template('claude', skills_catalog='- test-skill: Desc')
assert 'test-skill' not in content, 'Skills leaked into CLAUDE.md'
print('PASS: Skills not embedded in CLAUDE.md')
"
```

## Acceptance Criteria

- [x] REQ-0.17.0-03-01: CLAUDE.md template is <=60 lines with 6 placeholder variables
- [x] REQ-0.17.0-03-02: Generated CLAUDE.md delegates skills to `.claude/skills/` (not embedded)
- [x] REQ-0.17.0-03-03: Generated CLAUDE.md delegates rules to `.claude/rules/` (not inlined)
- [x] REQ-0.17.0-03-04: CLAUDE.md declares `AGENTS.md` as authoritative governance contract
- [x] REQ-0.17.0-03-05: `agents.local.md` injection via HTML comment markers at template tail
- [x] REQ-0.17.0-03-06: Regression tests prevent re-introduction of bloated content (TestRootSurfaceSlimming)
- [x] REQ-0.17.0-03-07: `sync_claude_md()` generates CLAUDE.md deterministically from template + context

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run gz test
Ran 685 tests in 18.281s — OK

$ uv run -m unittest tests.test_templates.TestAdapterTemplatesReferenceCanon tests.test_templates.TestRootSurfaceSlimming -v
Ran 7 tests in 0.008s — OK
```

### Code Quality

```text
$ uv run gz lint
All checks passed! Lint passed.

$ uv run gz typecheck
All checks passed! Type check passed.
```

### Gate 3 (Docs)

```text
CLAUDE.md is the documentation artifact itself — generated at 58 lines.
Template: 50 lines, 6 placeholders. Skills/rules delegated, not embedded.
```

### Gate 4 (BDD)

```text
N/A — no behave features for CLAUDE.md template
```

### Gate 5 (Human)

```text
Human attestation: "attest completed" — 2026-03-19
```

## Value Narrative

Before this OBPI, CLAUDE.md could grow unbounded as governance content was added directly, causing context window bloat for Claude Code sessions. Now, CLAUDE.md is generated from a slim 50-line template that delegates skills to `.claude/skills/`, rules to `.claude/rules/`, and defers to `AGENTS.md` as the authoritative contract. Regression tests in `TestRootSurfaceSlimming` and `TestAdapterTemplatesReferenceCanon` prevent re-introduction of bloated content.

### Key Proof

```text
$ uv run python -c "from pathlib import Path; claude = Path('CLAUDE.md').read_text(encoding='utf-8'); ..."
CLAUDE.md: 58 lines
PASS: Slim CLAUDE.md validated

$ uv run python -c "from gzkit.templates import render_template; ..."
PASS: Skills not embedded in CLAUDE.md
```

### Implementation Summary

- Files created/modified: `src/gzkit/templates/claude.md` (50-line template), `src/gzkit/sync.py` (`sync_claude_md()`, `get_project_context()`), `src/gzkit/templates/__init__.py` (`render_template()`)
- Tests added: `tests/test_templates.py` (TestAdapterTemplatesReferenceCanon, TestRootSurfaceSlimming — 6 regression tests)
- Date completed: 2026-03-19
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `human:Jeff`
- Attestation: attest completed
- Date: 2026-03-19

---

**Brief Status:** Completed

**Date Completed:** 2026-03-19

**Evidence Hash:** -
