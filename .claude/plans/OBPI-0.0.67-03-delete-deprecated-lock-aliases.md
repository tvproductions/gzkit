# Plan: OBPI-0.0.67-03-delete-deprecated-lock-aliases

## Context

- **OBPI:** OBPI-0.0.67-03-delete-deprecated-lock-aliases
- **Parent ADR:** ADR-0.0.67-tool-skill-invariant1-enforcement
- **Lane:** Heavy
- **Brief:** `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/obpis/OBPI-0.0.67-03-delete-deprecated-lock-aliases.md`

## ADR Decision Item (verbatim)

> OBPI-0.0.67-03: Delete the 3 deprecated `obpi lock-*` hyphen aliases and
> their doc cascade (parser, manpages, doc-coverage, mkdocs nav, behave
> scenario)

## Brief Gap (manpage clarification)

The brief's Allowed Paths says to delete `obpi-lock-claim.md`,
`obpi-lock-release.md`, `obpi-lock-status.md` with the note "(the canonical
forms are documented by the space-form manpages)." **These files ARE the
space-form manpages.** Their H1 headings are `gz obpi lock claim/release/list`
(canonical) not `gz obpi lock-claim/release/status` (deprecated). Deleting
them would break `index.md` references and `mkdocs build --strict`. Plan
corrects: KEEP the three manpage files.

Also: `mkdocs.yml` has no nav entries for the deprecated aliases; nothing to
remove there.

The `doc-coverage.json` entries for the 3 deprecated verb keys (`obpi lock-claim`,
`obpi lock-release`, `obpi lock-status`) should be removed as they reference the
deprecated verbs (all have `manpage: false`, `governance_relevant: false`).

## Files

### In scope

- `src/gzkit/cli/parser_artifacts.py` — remove lines 1454-1505 (deprecated-alias block)
- `config/doc-coverage.json` — remove the 3 deprecated verb entries
- `features/obpi_lock.feature` — remove lines 65-69 (deprecated scenario)
- `tests/commands/test_obpi_lock_aliases_removed.py` — new regression test (RED→GREEN)

### Out of scope (explicitly preserved)

- `docs/user/manpages/obpi-lock-claim.md` — canonical `gz obpi lock claim` manpage, KEEP
- `docs/user/manpages/obpi-lock-release.md` — canonical `gz obpi lock release` manpage, KEEP
- `docs/user/manpages/obpi-lock-status.md` — canonical `gz obpi lock list` manpage, KEEP
- `mkdocs.yml` — no deprecated alias nav entries exist, no change needed
- `docs/user/manpages/index.md` — already references canonical forms only, no change needed
- `src/gzkit/cli/parser_artifacts.py:1334-1452` — canonical space-form subgroup, MUST remain

## Steps

### Step 1: Write RED test (TDD)

Create `tests/commands/test_obpi_lock_aliases_removed.py`:

- Import `_known_cli_verb_paths` from `src/gzkit/governance/trust_audits/cli.py`
  or test via subprocess CLI invocation.
- Class `TestObpiLockAliasesRemoved(unittest.TestCase)`:
  - `test_deprecated_aliases_not_registered` — assert `obpi lock-claim`,
    `obpi lock-release`, `obpi lock-status` are absent from known verb paths.
  - `test_canonical_space_forms_still_registered` — assert `obpi lock claim`,
    `obpi lock release`, `obpi lock list` are present in known verb paths.
- Decorate both tests with `@covers("REQ-0.0.67-03-01")`.
- Run `uv run -m unittest tests.commands.test_obpi_lock_aliases_removed -v` → RED.

### Step 2: Delete deprecated alias block from parser_artifacts.py

Remove lines 1454-1505 (the entire deprecated-alias comment + 3 parser blocks):

```
# --- Deprecated flat aliases (OBPI-03 will remove these after skill migration) ---
p_lock_claim_dep = obpi_commands.add_parser("lock-claim", ...)
...
p_lock_status_dep.set_defaults(...)
```

Run test → GREEN. Run `uv run ruff check . --fix && uv run ruff format .`.

### Step 3: Remove deprecated entries from doc-coverage.json

Remove the 3 entries at lines ~455-484:
```json
"obpi lock-claim": { ... },
"obpi lock-release": { ... },
"obpi lock-status": { ... },
```

### Step 4: Remove deprecated behave scenario from features/obpi_lock.feature

Remove lines 65-69:
```gherkin
  Scenario: Deprecated lock-claim alias works
    Given the workspace is initialized
    When I run "gz obpi lock-claim OBPI-0.1.0-01 --json"
    Then it exits with code 0
    And the JSON output field "status" is "claimed"
```

### Step 5: Verify all quality gates

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz cli audit
uv run mkdocs build --strict
uv run -m behave features/obpi_lock.feature
uv run gz validate --documents
uv run gz covers OBPI-0.0.67-03-delete-deprecated-lock-aliases --json
```

## Verification

```bash
# Canonical forms still work:
uv run gz obpi lock list
# Deprecated alias is gone (argparse error, exit != 0):
uv run gz obpi lock-claim OBPI-0.1.0-01  # should fail
```

## Notes

- No new imports required in parser_artifacts.py after deletion.
- `_known_cli_verb_paths()` is the same function introduced by OBPI-01; it is
  already in the working tree per ADR § Decision (1) "already implemented".
- Test uses the `@covers` decorator to satisfy REQ-0.0.67-03-01 parity gate.
- REQ-0.0.67-03-02 (manpages/doc-coverage/mkdocs removed) is support-kind:
  proof via `artifact_edited` ledger events + `gz cli audit` exit 0.
- REQ-0.0.67-03-03 (behave scenario removed) is support-kind:
  proof via `artifact_edited` event + `gz validate --documents` + behave green.
