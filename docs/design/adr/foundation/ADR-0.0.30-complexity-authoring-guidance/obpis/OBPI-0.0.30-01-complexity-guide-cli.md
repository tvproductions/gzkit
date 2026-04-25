---
id: OBPI-0.0.30-01-complexity-guide-cli
parent: ADR-0.0.30
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.30-01-complexity-guide-cli: gz complexity-guide CLI Verb

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/ADR-0.0.30-complexity-authoring-guidance.md`
- **Checklist Item:** #1 — "`gz complexity-guide` CLI verb (Heavy-lane new subcommand: ADR + manpage + smoke + release notes; default in-line hint prose; --json mode)"

**Status:** Draft

## Objective

Author the `gz complexity-guide` CLI verb at `src/gzkit/commands/complexity_guide.py`, register it on the parser, document via manpage and runbook, and cover with a behave smoke scenario per `.gzkit/rules/cli.md` § "New Subcommand (Heavy Lane)". The verb consumes the OBPI-03 hint engine and emits in-line authoring-time hints.

## Lane

**Heavy** — New CLI subcommand is a contract change requiring full Heavy-lane treatment. Foundation-kind brief-level Gate 5 attestation per ADR-0.0.18.

## Allowed Paths

- `src/gzkit/commands/complexity_guide.py`
- `src/gzkit/cli/parser_artifacts.py` — register `complexity-guide` verb
- `tests/commands/test_complexity_guide.py`
- `features/complexity_guide.feature` — behave smoke scenario
- `docs/user/manpages/gz-complexity-guide.md`
- `docs/user/runbook.md` — entry under "Complexity doctrine surfaces"
- `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/obpis/OBPI-0.0.30-01-complexity-guide-cli.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/complexity/authoring/hint.py` — projection is OBPI-03
- `src/gzkit/complexity/authoring/engine.py` — engine is OBPI-03
- `src/gzkit/complexity/authoring/protocol.py` — protocol is OBPI-04
- `.gzkit/skills/complexity-guide/**` — skill is OBPI-02
- `.gzkit/skills/gz-justify/**` — justify integration is OBPI-05
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz complexity-guide <path>` analyzes the file/directory at `<path>`, runs the OBPI-03 authoring engine for each `advise`-band crossing in the threshold table (ADR-0.0.28), and emits an `AuthoringHint` per crossing. Default human-readable output is in-line hint prose (one block per hint: archetype, doctrinal-frame excerpt headline, recommended-move headline); `--json` emits canonical `AuthoringHint` Pydantic serialization.
2. REQUIREMENT: The CLI follows the four-code exit map per `.claude/rules/cli.md`: 0 success (no advise crossings or hints emitted), 1 user/config error (bad path, malformed flags), 2 system/IO error (missing threshold table, AST parse error). Exit 3 is NOT used here — the authoring-guide surface never blocks; that is OBPI-0.0.29's trigger-time response.
3. REQUIREMENT: Standard flags per `.claude/rules/cli.md` § Flag Conventions: `--quiet`, `--verbose`, `--json`, `--help`/`-h`. Help text per the Help Text Requirements section.
4. REQUIREMENT: Manpage at `docs/user/manpages/gz-complexity-guide.md` documents purpose, exit codes (noting why 3 is NOT used), all flags, at least two example invocations (one ad-hoc, one with `--json`), and the runbook cross-reference.
5. REQUIREMENT: Runbook entry under "Complexity doctrine surfaces" prescribes `gz complexity-guide` for the operator moment "preview authoring-time complexity hints on a file before committing".
6. REQUIREMENT: A behave smoke scenario at `features/complexity_guide.feature` tagged `@REQ-0.0.30-01-{01..03}` covers: clean file produces exit 0 with "no advise hints"; file with advise-band crossing produces exit 0 + hint prose; `--json` mode emits valid JSON validating against `src/gzkit/schemas/authoring_hint.json`.
7. REQUIREMENT: Tests cover argument parsing, `--json` mode validity, exit-code map invariants (3 is never produced), help text contains all required sections. Each test decorated with `@covers(REQ-0.0.30-01-NN)`.
8. REQUIREMENT: Tool / Skill / Runbook alignment per `.gzkit/rules/tool-skill-runbook-alignment.md` Invariants 1, 2, 3 — the runbook prescribes this verb, OBPI-02's skill routes to it, the verb's default form matches the skill's Output Contract.
9. REQUIREMENT: TDD discipline; tests mock subprocess boundaries.
10. REQUIREMENT: NEVER include the operator's personal email in code, manpage, runbook, fixtures, or commit messages.

> STOP-on-BLOCKERS: if OBPI-03's hint engine is not landed, STOP — the CLI has nothing to wire to.

## Discovery Checklist

- [ ] OBPI-03 hint engine + `AuthoringHint` projection
- [ ] `.claude/rules/cli.md` — Heavy-lane subcommand discipline
- [ ] `.claude/rules/gate5-runbook-code-covenant.md` — manpage + runbook covenant
- [ ] OBPI-0.0.29-03 (`gz complexity-advise`) — exemplar shape for the sister verb

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Manpage + runbook entry

### Gate 4: BDD (Heavy)
- [ ] Behave smoke scenarios pass

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
uv run mkdocs build --strict
uv run gz complexity-guide --help
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_complexity_guide.py -v
uv run -m behave features/complexity_guide.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.30-01-01: Given a clean file with no advise crossings, when `gz complexity-guide <path>` runs, then exit 0 and output names "no advise hints".
- [ ] REQ-0.0.30-01-02: Given a file with advise-band crossings, when the verb runs, then exit 0 and one in-line hint block per crossing is emitted with archetype, doctrinal-frame headline, and recommended-move headline.
- [ ] REQ-0.0.30-01-03: Given `--json`, when invoked, then stdout is valid JSON validating against the authoring_hint JSON Schema.
- [ ] REQ-0.0.30-01-04: Given a block-or-warn-band crossing (which the trigger-time advisor handles), when this verb runs, then those crossings are NOT included in the output (advise-band only); exit code never reaches 3.
- [ ] REQ-0.0.30-01-05: Given `--help`, when invoked, then exit 0 and output contains description, usage, options, and at least one example.
- [ ] REQ-0.0.30-01-06: Given `gz cli audit`, when invoked, then exit 0 and the new verb is covered in manpage + command doc + index.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: mkdocs --strict + manpage + runbook
- [ ] Gate 4: behave scenarios pass
- [ ] Gate 5: TTY + `ATTEST`

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR + unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict + manpage + runbook diffs
```

### Gate 4 (BDD)
```text
# Paste behave output
```

### Gate 5 (Human)
```text
# Record attestation + receipt IDs
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Closing Argument

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>`
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
