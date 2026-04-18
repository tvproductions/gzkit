---
id: OBPI-0.0.15-01-cli-command-scaffold
parent: ADR-0.0.15-ghi-driven-patch-release-ceremony
item: 1
lane: Heavy
status: in_progress
---

# OBPI-0.0.15-01: CLI Command Scaffold

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md`
- **Checklist Item:** #1 - "`gz patch release` CLI command scaffold with `--dry-run` and `--json`"

**Status:** Draft

## Objective

`uv run gz patch release` is a registered CLI subcommand that accepts `--dry-run`
and `--json` flags, dispatches to a command module, and exits cleanly with proper
help text.

## Lane

**Heavy** - New CLI subcommand is an external contract change per CLI doctrine.
Requires manpage, command docs, and BDD smoke test.

## Allowed Paths

- `src/gzkit/commands/patch_release.py` (new)
- `src/gzkit/cli/parser_governance.py`
- `tests/adr/test_patch_release.py` (new)
- `docs/user/commands/patch-release.md` (new)
- `docs/user/manpages/patch-release.md` (new)
- `features/patch_release.feature` (new)

## Denied Paths

- `src/gzkit/commands/closeout.py` — no modifications in this OBPI
- `RELEASE_NOTES.md` — not yet
- `docs/releases/` — not yet

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz patch release --help` MUST exit 0 and display usage with
   description, flags, and at least one example
2. REQUIREMENT: `gz patch release --dry-run` MUST exit 0 with a placeholder
   message (full logic in later OBPIs)
3. REQUIREMENT: `gz patch release --json` MUST produce valid JSON to stdout
4. REQUIREMENT: The command MUST be registered in the governance parser group
   alongside `gz closeout`

> STOP-on-BLOCKERS: if the parser registration pattern has changed since
> ADR-0.0.14, investigate before proceeding.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/cli/parser_governance.py` exists
- [ ] `src/gzkit/commands/closeout.py` exists (pattern reference)

**Existing Code (understand current state):**

- [ ] Parser registration pattern: `src/gzkit/cli/parser_governance.py`
- [ ] Command module pattern: `src/gzkit/commands/closeout.py`
- [ ] Test patterns: `tests/adr/test_closeout.py`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Command docs: `docs/user/commands/patch-release.md`
- [ ] Manpage: `docs/user/manpages/patch-release.md`

### Gate 4: BDD (Heavy)

- [ ] Acceptance scenarios pass: `uv run -m behave features/patch_release.feature`

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/patch_release.feature

# Specific verification
uv run gz patch release --help
uv run gz patch release --dry-run
uv run gz patch release --json
```

## Acceptance Criteria

- [ ] REQ-0.0.15-01-01: `gz patch release --help` exits 0 with usage text
- [ ] REQ-0.0.15-01-02: `gz patch release --dry-run` exits 0
- [ ] REQ-0.0.15-01-03: `gz patch release --json` produces valid JSON
- [ ] REQ-0.0.15-01-04: Command registered in governance parser group

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Value Narrative

Before this OBPI, gzkit had no CLI surface for patch releases. Operators wanting to
ship patch-level version bumps had no formal command, leading to manual edits and
version drift. Now `gz patch release` exists as a registered governance command with
`--dry-run` and `--json` flags, establishing the foundation for OBPIs 02-06.

### Key Proof


```bash
$ uv run gz patch release --json
{"status": "not_implemented", "message": "gz patch release is scaffolded. Full logic arrives in later OBPIs.", "dry_run": false}
```

### Implementation Summary


- Files created/modified: src/gzkit/commands/patch_release.py (new), src/gzkit/cli/parser_governance.py (modified), tests/adr/test_patch_release.py (new), features/patch_release.feature (new), docs/user/commands/patch-release.md (new), docs/user/manpages/patch-release.md (new)
- Tests added: 7 unit tests in test_patch_release.py, 3 BDD scenarios in patch_release.feature
- Date completed: 2026-04-07
- Attestation status: Completed
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: Completed — all 4 REQs verified, 2645 tests pass, BDD green, docs built.
- Date: 2026-04-08

---

**Brief Status:** Completed

**Date Completed:** 2026-04-08

**Evidence Hash:** -
