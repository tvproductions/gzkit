---
id: OBPI-0.0.67-03-delete-deprecated-lock-aliases
parent: ADR-0.0.67-tool-skill-invariant1-enforcement
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.67-03-delete-deprecated-lock-aliases: Delete Deprecated Lock Aliases

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/ADR-0.0.67-tool-skill-invariant1-enforcement.md`
- **Checklist Item:** #3 — Delete the 3 deprecated `obpi lock-*` hyphen aliases and their doc cascade.
- **Parent ADR § Decision (3) quoted:** "Execute the unlanded cleanup: remove the parser registrations + 3 manpages + `doc-coverage.json` entries + `mkdocs.yml` nav + the behave scenario `features/obpi_lock.feature:65`, keeping `gz cli audit` and `mkdocs build --strict` green."

**Status:** Draft

## Objective

Execute the cleanup the source itself scheduled but never landed: delete the 3
deprecated `obpi lock-claim` / `lock-release` / `lock-status` hyphen aliases and
their full documentation cascade, keeping `gz cli audit` and `mkdocs build
--strict` green. The canonical space forms (`obpi lock claim/release/list`) are
unaffected and remain wielded by gz-obpi-lock.

> **SEQUENCING:** Land **after OBPI-02, before OBPI-01**. While the audit is still
> top-level-only the aliases are invisible to it, so deletion is audit-neutral
> until OBPI-01's recursion lands last.

> **REVERSIBILITY (from ADR pre-mortem):** This is the ~one-way door — a CLI
> contract change. Re-adding is cheap, but treat the deletion with the most
> evidence: prove the space forms still work and `cli audit` stays green.

## Lane

**Heavy** — removes registered CLI verbs (contract change) + doc surface.

## Allowed Paths

- `src/gzkit/cli/parser_artifacts.py` — remove the deprecated-alias block (`:1454-1505`: `p_lock_claim_dep`, `p_lock_release_dep`, `p_lock_status_dep`)
- `docs/user/manpages/obpi-lock-claim.md`, `obpi-lock-release.md`, `obpi-lock-status.md` — delete (the canonical forms are documented by the space-form manpages)
- `config/doc-coverage.json` — remove the 3 alias entries
- `mkdocs.yml` — remove the 3 nav entries
- `features/obpi_lock.feature` — remove the `Scenario: Deprecated lock-claim alias works` (`:65`) and any sibling alias scenarios
- `docs/user/manpages/index.md` — drop alias rows if present
- `tests/commands/` — regression test (new file, e.g. `test_obpi_lock_aliases_removed.py`): the 3 hyphen verbs are unregistered AND the space forms still resolve (REQ-03-01 @covers)

## Denied Paths

- The canonical `obpi lock` subgroup (`claim`/`release`/`check`/`list`, `parser_artifacts.py:1334-1452`) — MUST remain
- gz-obpi-lock / gz-obpi-pipeline skills (they already wield the space forms; no change)
- Any verb other than the 3 hyphen aliases

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: After removal, `gz obpi lock-claim` / `lock-release` / `lock-status` MUST NOT be registered verbs (argparse rejects them); `gz obpi lock claim/release/list` MUST still work.
1. REQUIREMENT: `uv run gz cli audit` MUST exit 0 with full coverage (no dangling manpage/doc-coverage references).
1. REQUIREMENT: `uv run mkdocs build --strict` MUST pass (no broken nav/links).
1. REQUIREMENT: The behave alias scenario MUST be removed (it tests a now-deleted verb); `uv run -m behave features/obpi_lock.feature` MUST pass.
1. NEVER: touch the canonical space-form subgroup.

## Discovery Checklist

**Parent ADR (read first):**
- [ ] Parent ADR § Decision (3) — quoted above
- [ ] Parent ADR § Consequences (Negative) — one-way-door reversibility note

**Prerequisites (check existence, STOP if missing):**
- [ ] OBPI-02 has landed (wiring); OBPI-01 (recursion keystone) has NOT yet landed — deletion is audit-neutral until then
- [ ] `src/gzkit/cli/parser_artifacts.py:1454-1505` deprecated-alias block present
- [ ] The 3 alias manpages + `config/doc-coverage.json` + `mkdocs.yml` references present to remove

**Existing Code (understand current state):**
- [ ] `src/gzkit/cli/parser_artifacts.py:1454-1505` (the deprecated-alias block + same-handler dispatch proof: `lock-claim`→`obpi_lock_claim_cmd`, etc.)
- [ ] `src/gzkit/cli/parser_artifacts.py:1334-1452` (canonical space-form subgroup — MUST remain)
- [ ] `features/obpi_lock.feature:65` (the alias scenario to remove)
- [ ] `.gzkit/rules/cli.md` (CLI contract doctrine — verb removal is Heavy lane)

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent Decision item quoted

### Gate 2: TDD
- [ ] Test asserts the 3 hyphen verbs are unregistered AND the space forms resolve (RED→GREEN)
- [ ] `uv run gz test`

### Code Quality
- [ ] `uv run gz lint`
- [ ] `uv run gz typecheck`

### Gate 3: Docs (Heavy)
- [ ] `uv run mkdocs build --strict`
- [ ] `uv run gz cli audit`

### Gate 4: BDD (Heavy)
- [ ] `uv run -m behave features/obpi_lock.feature` (alias scenario removed; space-form scenarios pass)

### Gate 5: Human (Heavy)
- [ ] Human attestation recorded

## Verification

```bash
uv run gz cli audit
uv run mkdocs build --strict
uv run gz validate --documents
uv run -m behave features/obpi_lock.feature
uv run -m unittest discover -s tests -t .
uv run gz lint
```

## Demo

```bash
# Canonical forms still work:
uv run gz obpi lock list
# Deprecated alias is gone (argparse error, exit != 0):
uv run gz obpi lock-claim OBPI-0.1.0-01
```

## Acceptance Criteria

- [ ] REQ-0.0.67-03-01 [behavior]: Given the rebuilt parser, when `_known_cli_verb_paths()` / `_build_parser()` are inspected, then `obpi lock-claim`, `obpi lock-release`, `obpi lock-status` are absent AND `obpi lock claim/release/list` are present. (@covers test)
- [ ] REQ-0.0.67-03-02 [support]: The 3 alias manpages, `doc-coverage.json` entries, and `mkdocs.yml` nav rows are removed. Proof: `artifact_edited` ledger events + `gz validate --documents` green + `gz cli audit` exit 0.
- [ ] REQ-0.0.67-03-03 [support]: The `Deprecated lock-claim alias works` behave scenario is removed and `features/obpi_lock.feature` still passes. Proof: `artifact_edited` event + `gz validate --documents` (spec surface admits the trimmed feature) + behave green recorded in evidence.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** unregister/space-form test RED→GREEN
- [ ] **Code Quality:** lint/typecheck clean
- [ ] **Value Narrative:** documented below
- [ ] **Key Proof:** included below
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste unregister/space-form test output here
```

### Code Quality
```text
# Paste lint/typecheck output here
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict + gz cli audit output here
```

### Gate 4 (BDD)
```text
# Paste behave features/obpi_lock.feature output here
```

### Gate 5 (Human)
```text
# Record operator attestation text here
```

### Value Narrative

Before: 3 deprecated hyphen aliases (`obpi lock-claim/-release/-status`) the source
itself marked "remove after skill migration" lingered unremoved — dead weight the
CLI surface advertised as real. Now: the unlanded OBPI-03 cleanup is executed; the
CLI stops lying about what it supports; the canonical space forms remain.

### Key Proof

`uv run gz obpi lock list` works; `uv run gz obpi lock-claim ...` errors as an
unknown verb; `uv run gz cli audit` and `uv run mkdocs build --strict` green.

### Implementation Summary

- Files created/modified: `parser_artifacts.py`, 3 manpages (deleted), `config/doc-coverage.json`, `mkdocs.yml`, `features/obpi_lock.feature`
- Tests added: unregistered-alias + space-form-resolves guard
- Date completed:
- Attestation status:
- Defects noted: anchors GHI #588

## Tracked Defects

- GHI #588 — anchor

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
