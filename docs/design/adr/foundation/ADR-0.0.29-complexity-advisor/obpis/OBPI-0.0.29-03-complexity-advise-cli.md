---
id: OBPI-0.0.29-03-complexity-advise-cli
parent: ADR-0.0.29
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.29-03-complexity-advise-cli: gz complexity-advise CLI Verb

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md`
- **Checklist Item:** #3 — "`gz complexity-advise` CLI verb (Heavy-lane new subcommand: ADR + manpage + smoke + release notes)"

**Status:** Draft

## Objective

Author the `gz complexity-advise` CLI verb at `src/gzkit/commands/complexity_advise.py`, register it on the parser, document it via manpage and runbook entries, and cover it with a behave smoke scenario per `.gzkit/rules/cli.md` § "New Subcommand (Heavy Lane)".

## Lane

**Heavy** — New CLI subcommand is a contract change requiring full Heavy-lane treatment per `.gzkit/rules/cli.md`. Foundation-kind brief-level Gate 5 stacks per ADR-0.0.18.

## Allowed Paths

- `src/gzkit/commands/complexity_advise.py`
- `src/gzkit/cli/parser_artifacts.py` — register `complexity-advise` verb
- `tests/commands/test_complexity_advise.py`
- `features/complexity_advise.feature` — behave smoke scenario
- `docs/user/manpages/gz-complexity-advise.md`
- `docs/user/runbook.md` — entry under "Complexity doctrine surfaces"
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-03-complexity-advise-cli.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/complexity/advisor/diagnosis.py` — schema is OBPI-01
- `src/gzkit/complexity/advisor/engine.py` — engine is OBPI-02
- `src/gzkit/complexity/advisor/intrinsic.py` — attestation is OBPI-07 (CLI flag wiring for `--attest-intrinsic` lands in OBPI-07, not here)
- `src/gzkit/complexity/advisor/timeout.py` — timeout is OBPI-09
- `.gzkit/skills/complexity-advisor/**` — skill is OBPI-04
- `.gzkit/hooks/**` — auto-chain hook is OBPI-05
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz complexity-advise <path>` analyzes the file or directory at `<path>`, runs the engine (OBPI-02) for each metric crossing in the threshold table (ADR-0.0.28), and emits an `AdvisorDiagnosis` per crossing. Default human-readable output is structured prose; `--json` mode emits the canonical Pydantic serialization.
2. REQUIREMENT: The CLI follows the four-code exit map per `.claude/rules/cli.md`: 0 success (no crossings or all advise-band), 1 user/config error (bad path, malformed flags), 2 system/IO error (missing threshold table, AST parse error), 3 policy breach (a `block`-band crossing). The exit-code map is documented in the manpage.
3. REQUIREMENT: Standard flags per `.claude/rules/cli.md` § Flag Conventions: `--quiet`, `--verbose`, `--dry-run` (no-op for analysis but reserved), `--json`, `--help`/`-h`. The auto-chain marker flag (`--auto-chain`) is reserved here; semantics defined in OBPI-05.
4. REQUIREMENT: Help text per `.claude/rules/cli.md` § Help Text Requirements: description (1–2 sentences), usage line, all options listed, at least one example, lines ≤ 80 chars. `-h`/`--help` exits 0.
5. REQUIREMENT: Manpage at `docs/user/manpages/gz-complexity-advise.md` documents purpose, exit codes, all flags, at least two example invocations (one ad-hoc, one with `--json`), and the runbook cross-reference.
6. REQUIREMENT: Runbook entry under "Complexity doctrine surfaces" prescribes `gz complexity-advise` for the operator moment "preview advisor diagnosis on a file before commit".
7. REQUIREMENT: A behave smoke scenario at `features/complexity_advise.feature` tagged `@REQ-0.0.29-03-{01,02,03}` covers: a clean file produces exit 0; a file with a warn-band crossing produces exit 0 + diagnosis prose; a file with a block-band crossing produces exit 3.
8. REQUIREMENT: Tests cover: argument parsing (path required, flag interactions); `--json` mode produces valid JSON validating against `src/gzkit/schemas/advisor_diagnosis.json`; exit-code map invariants per the four-code rule; help text contains all standard sections. Each test decorated with `@covers(REQ-0.0.29-03-NN)`.
9. REQUIREMENT: Tool / Skill / Runbook alignment per `.gzkit/rules/tool-skill-runbook-alignment.md` Invariants 1, 2, 3 — the runbook prescribes this verb, OBPI-04's skill routes to it, and the verb's default output form matches the skill's Output Contract.
10. REQUIREMENT: TDD discipline; tests mock subprocess boundaries (no spawned subprocesses in the unit tier per `.claude/rules/tests.md`).
11. REQUIREMENT: NEVER include the operator's personal email in code, manpage, runbook, fixtures, or commit messages.

> STOP-on-BLOCKERS: if OBPI-02 engine and OBPI-01 schema are not landed, STOP — the CLI has nothing to wire to.

## Discovery Checklist

- [ ] OBPI-01 schema, OBPI-02 engine
- [ ] `.claude/rules/cli.md` — Heavy-lane subcommand discipline, exit-code map, flag conventions, help text requirements
- [ ] `.claude/rules/gate5-runbook-code-covenant.md` — manpage + runbook in same patch
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` Invariants 1–3
- [ ] Existing CLI verb implementations (e.g. `src/gzkit/commands/validate.py`) for shape reference

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Manpage section + runbook entry

### Gate 4: BDD (Heavy)
- [ ] `features/complexity_advise.feature` smoke scenarios pass with REQ tags

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
uv run mkdocs build --strict
uv run gz complexity-advise --help
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_complexity_advise.py -v
uv run -m behave features/complexity_advise.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.29-03-01: Given a clean file with no metric crossings, when `gz complexity-advise <path>` runs, then exit 0 and the output names "no crossings".
- [ ] REQ-0.0.29-03-02: Given a file with a warn-band crossing, when the verb runs, then exit 0, diagnosis prose is emitted, and the output names the archetype + doctrinal frame.
- [ ] REQ-0.0.29-03-03: Given a file with a block-band crossing, when the verb runs, then exit 3.
- [ ] REQ-0.0.29-03-04: Given `--json`, when the verb runs against any file, then stdout is valid JSON validating against the advisor_diagnosis JSON Schema.
- [ ] REQ-0.0.29-03-05: Given `--help`, when invoked, then exit 0 and the output contains description, usage, options, and at least one example.
- [ ] REQ-0.0.29-03-06: Given the manpage, when read, then it documents purpose, exit codes, all flags, and at least two example invocations.
- [ ] REQ-0.0.29-03-07: Given `gz cli audit`, when invoked, then exit 0 and the new verb is covered (manpage, command doc, index parity).

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
# Paste mkdocs --strict + manpage + runbook diff hunks
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
