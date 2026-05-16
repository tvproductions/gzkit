---
id: OBPI-0.0.34-03-reverse-parse-migration
parent: ADR-0.0.34-agent-control-surface-rendering-substrate
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.34-03-reverse-parse-migration: Reverse Parse Migration

<!-- gz-validate-skip: brief-demo-section --> <!-- Draft brief; Demo section authored at implementation time per GHI #431 grandfather pattern. -->

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`
- **Checklist Item:** #3 - "OBPI-0.0.34-03: Reverse-parse migration tooling — `gz content import <file> --as <type>` reads existing hand-authored markdown back into canonical Pydantic models; round-trip fidelity contract enforced"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Reverse-parse migration tooling — `gz content import <file> --as <type>` reads existing hand-authored markdown back into canonical Pydantic models; round-trip fidelity contract enforced.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/content/parse/__init__.py` — parser public entrypoint (`parse(text, as_type) -> Model`)
- `src/gzkit/content/parse/markdown_parser.py` — reverse-parse implementation per content type
- `src/gzkit/commands/content/__init__.py` — `gz content` subparser registration
- `src/gzkit/commands/content/import_.py` — `gz content import <file> --as <type>` CLI verb
- `tests/content/test_round_trip_agent_contract.py` — round-trip fidelity for `AgentContract`
- `tests/content/test_round_trip_rule.py` — round-trip fidelity for `Rule`
- `tests/content/test_round_trip_skill.py` — round-trip fidelity for `Skill`
- `tests/content/test_round_trip_chore.py` — round-trip fidelity for `Chore`
- `tests/content/test_round_trip_persona.py` — round-trip fidelity for `Persona`
- `tests/content/test_round_trip_handoff.py` — round-trip fidelity for `Handoff`
- `tests/content/test_round_trip_scenario.py` — round-trip fidelity for `Scenario`
- `tests/content/test_round_trip_bullet.py` — round-trip fidelity for `Bullet`
- `tests/commands/test_content_import.py` — CLI smoke test
- `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/obpis/OBPI-0.0.34-03-reverse-parse-migration.md` — this brief

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: **`gz content import <file> --as <content-type>` CLI verb.** Reads a hand-authored markdown file, returns a Pydantic model instance from `CONTENT_MODELS`, emits JSON to stdout by default; `--write <path>` persists a canonical-form re-render at `<path>`.
2. REQUIREMENT: **Round-trip fidelity contract.** For every content type registered in OBPI-01, `parse(render(model)) == model` AND `render(parse(text)) == text` byte-equal (modulo whitespace normalizations explicitly enumerated in the parser's docstring). One test file per content type under `tests/content/test_round_trip_<content_type>.py`.
3. REQUIREMENT: **Lossless migration of existing surfaces.** `gz content import AGENTS.md --as AgentContract --write /tmp/x.md && diff -q AGENTS.md /tmp/x.md` exits 0. Same for `CLAUDE.md` and each file in `.gzkit/rules/*.md`.
4. REQUIREMENT: **Parse-only scope.** NEVER define new content types here (OBPI-01 owns the registry). NEVER fire validation hooks here (OBPI-06 owns hook wiring). NEVER apply schema migrations directly — invoke OBPI-07's migration registry once it exists, otherwise pass-through.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] **Prerequisite OBPI:** OBPI-0.0.34-01 (content model registry) — parser needs target model classes.
- [ ] **Prerequisite OBPI:** OBPI-0.0.34-02 (rendering pipeline) — round-trip contract requires `render()` for fidelity proof.
- [ ] **Soft co-dependency:** OBPI-0.0.34-07 (migration layer) — parser invokes migrations when source `schema_version` differs from current; pass-through if OBPI-07 hasn't landed.
- [ ] Downstream consumer: OBPI-04 (`gz content edit` re-parses on save).

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.34-01 complete: `from gzkit.content.models import CONTENT_MODELS` imports cleanly.
- [ ] OBPI-0.0.34-02 complete: `from gzkit.content.render import render` imports cleanly.
- [ ] Parent ADR evidence artifacts referenced by this brief are present.

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run gz content import AGENTS.md --as AgentContract --write /tmp/agents-roundtrip.md
diff -q AGENTS.md /tmp/agents-roundtrip.md       # MUST exit 0 (zero-byte diff)
uv run gz content import CLAUDE.md  --as AgentContract --write /tmp/claude-roundtrip.md
diff -q CLAUDE.md /tmp/claude-roundtrip.md       # MUST exit 0
uv run python -m unittest discover -s tests/content -p 'test_round_trip_*.py' -t . -v
uv run python -m unittest tests.commands.test_content_import -v
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.34-03-01: Given `gz content import <file> --as <ctype>`, when invoked on a valid canonical markdown file, then a Pydantic model instance is produced and emitted to stdout as JSON (exit 0).
- [ ] REQ-0.0.34-03-02: Given each content type registered in OBPI-01, when its round-trip test loads a fixture, parses it, then re-renders the result, then output bytes equal input bytes (whitespace normalizations explicitly enumerated in the parser's docstring).
- [ ] REQ-0.0.34-03-03: Given the project's current `AGENTS.md`, when `gz content import AGENTS.md --as AgentContract --write /tmp/x.md` runs, then `diff -q AGENTS.md /tmp/x.md` exits 0.
- [ ] REQ-0.0.34-03-04: Given a malformed input file, when `gz content import` runs, then exit code is non-zero and the diagnostic names the failing parser location (file path + line number, where derivable).
- [ ] REQ-0.0.34-03-05: Given a file whose `--as` declared type mismatches the actual content shape, when parse runs, then `pydantic.ValidationError` is raised before any model instance is returned to the caller.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
