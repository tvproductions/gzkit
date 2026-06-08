---
id: OBPI-0.0.67-03-delete-deprecated-lock-aliases
parent: ADR-0.0.67-tool-skill-invariant1-enforcement
item: 3
lane: Heavy
status: Completed
ln:
  - req_id: REQ-0.0.67-03-01
    receipt_ids:
      - arb-step-unittest-6d1f2c6f463d40d79b274943f8249c86
      - arb-ruff-32fa35d49d984f6fb0e54e1faaa4be00
      - arb-step-typecheck-8397155f2c0146f9b9386549c52e81e9
      - arb-step-mkdocs-79257f294a494caeb93f3165a80ab0ed
  - req_id: REQ-0.0.67-03-02
    receipt_ids:
      - arb-step-unittest-6d1f2c6f463d40d79b274943f8249c86
      - arb-ruff-32fa35d49d984f6fb0e54e1faaa4be00
      - arb-step-typecheck-8397155f2c0146f9b9386549c52e81e9
      - arb-step-mkdocs-79257f294a494caeb93f3165a80ab0ed
  - req_id: REQ-0.0.67-03-03
    receipt_ids:
      - arb-step-unittest-6d1f2c6f463d40d79b274943f8249c86
      - arb-ruff-32fa35d49d984f6fb0e54e1faaa4be00
      - arb-step-typecheck-8397155f2c0146f9b9386549c52e81e9
      - arb-step-mkdocs-79257f294a494caeb93f3165a80ab0ed
# req_atomic exemption (return-to-health, 2026-06-08): each REQ is one
# indivisible parser/doc/feature contract. The implementation did not subdivide
# labor below a REQ, so one seq=01 TASK per REQ is the honest grain (no shared
# coarse-default bucket masking finer labor).
req_atomic:
  - REQ-0.0.67-03-01  # hyphen aliases unregistered, space forms retained: one parser contract
  - REQ-0.0.67-03-02  # alias manpages + doc-coverage + mkdocs nav removed: one doc-cascade contract
  - REQ-0.0.67-03-03  # deprecated behave scenario removed, feature still green: one feature-trim contract
---

# OBPI-0.0.67-03-delete-deprecated-lock-aliases: Delete Deprecated Lock Aliases

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/ADR-0.0.67-tool-skill-invariant1-enforcement.md`
- **Checklist Item:** #3 — Delete the 3 deprecated `obpi lock-*` hyphen aliases and their doc cascade.
- **Parent ADR § Decision (3) quoted:** "Execute the unlanded cleanup: remove the parser registrations + 3 manpages + `doc-coverage.json` entries + `mkdocs.yml` nav + the behave scenario `features/obpi_lock.feature:65`, keeping `gz cli audit` and `mkdocs build --strict` green."

**Status:** Completed

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
- `src/gzkit/governance/trust_audits/cli.py` — remove the 3 stale `_NO_SKILL_VERBS` waivers for the deleted verbs (coupled-surface coherence: a waiver naming an unregistered verb fails the skill-alignment stale-waiver check)
- `docs/user/manpages/obpi-lock-claim.md`, `obpi-lock-release.md`, `obpi-lock-status.md` — delete (the canonical forms are documented by the space-form manpages)
- `config/doc-coverage.json` — remove the 3 alias entries
- `mkdocs.yml` — remove the 3 nav entries
- `features/obpi_lock.feature` — remove the `Scenario: Deprecated lock-claim alias works` (`:65`) and any sibling alias scenarios
- `docs/user/manpages/index.md` — drop alias rows if present
- `tests/commands/` — regression test (new file, e.g. `test_obpi_lock_aliases_removed.py`): the 3 hyphen verbs are unregistered AND the space forms still resolve (REQ-03-01 @covers)
- `data/behave_coverage_waivers.json` — operator-authorized waiver for REQ-03-01/02/03 (REQ-01 unit-covered + existing behave; REQ-02/03 SUPPORT-kind, no behave channel)

## Denied Paths

- The canonical `obpi lock` subgroup (`claim`/`release`/`check`/`list`, `parser_artifacts.py:1334-1452`) — MUST remain
- gz-obpi-lock / gz-obpi-pipeline skills (they already wield the space forms; no change)
- Any verb other than the 3 hyphen aliases

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: After removal, the `obpi lock-claim` / `obpi lock-release` / `obpi lock-status` hyphen aliases MUST NOT be registered verbs (argparse rejects them); `gz obpi lock claim/release/list` MUST still work.
1. REQUIREMENT: `uv run gz cli audit` MUST exit 0 with full coverage AND `uv run mkdocs build --strict` MUST pass (no dangling doc-coverage references, no broken nav/links).
1. REQUIREMENT: The behave alias scenario MUST be removed (it tests a now-deleted verb); `uv run -m behave features/obpi_lock.feature` MUST pass.
1. NEVER: touch the canonical space-form subgroup.

## Discovery Checklist

**Parent ADR (read first):**
- [x] Parent ADR § Decision (3) — quoted above
- [x] Parent ADR § Consequences (Negative) — one-way-door reversibility note

**Prerequisites (check existence, STOP if missing):**
- [x] OBPI-02 has landed (wiring); OBPI-01 (recursion keystone) has NOT yet landed — deletion is audit-neutral until then
- [x] `src/gzkit/cli/parser_artifacts.py` deprecated-alias block present (lines 1454-1505)
- [x] The 3 alias manpages + `config/doc-coverage.json` + `mkdocs.yml` references present to remove

**Existing Code (understand current state):**
- [x] `src/gzkit/cli/parser_artifacts.py` deprecated-alias block (lines 1454-1505, same-handler dispatch proof)
- [x] `src/gzkit/cli/parser_artifacts.py` canonical space-form subgroup (lines 1334-1452 — MUST remain)
- [x] `features/obpi_lock.feature` alias scenario to remove (line 65)
- [x] `.gzkit/rules/cli.md` (CLI contract doctrine — verb removal is Heavy lane)

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
# The deprecated `lock-claim` hyphen alias is gone: argparse rejects it
# (exit 2) because it is no longer a registered verb. Use `gz obpi lock claim`.
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


`uv run gz obpi lock list` works; the `obpi lock-claim` hyphen alias is absent from `_known_cli_verb_paths()` and argparse rejects it. `uv run gz cli audit` reports 104/104 commands fully covered; `uv run gz validate --skill-alignment` is clean (the previously-stale `_NO_SKILL_VERBS` waivers are gone); `uv run -m behave features/obpi_lock.feature` passes 13 scenarios with the deprecated-alias scenario removed. Receipts: `arb-step-unittest-4a9c23d865274378b15a756176f7fbe0` (scoped 3/3), `arb-ruff-f5abd593884a4ea598aaef45065bcb41`, `arb-step-typecheck-8358e62da4224d658d50410fda5fc35b`, `arb-step-mkdocs-3717686a837b41339db41a1f8d8393c1`.

### Implementation Summary


- Removed: deprecated-alias parser block in `src/gzkit/cli/parser_artifacts.py` (`lock-claim`/`lock-release`/`lock-status`, ~52 lines)
- Removed: 3 stale `_NO_SKILL_VERBS` waivers in `src/gzkit/governance/trust_audits/cli.py` (coupled surface — stale waivers naming the deleted verbs broke 3 skill-alignment tests; ADR Decision (1) named this check)
- Removed: redundant orphan manpage `docs/user/manpages/obpi-lock-status.md` (canonical `obpi-lock-list.md` retained and covers `gz obpi lock list`)
- Removed: 3 deprecated entries in `config/doc-coverage.json`; deprecated-alias scenario in `features/obpi_lock.feature`
- Added: `tests/commands/test_obpi_lock_aliases_removed.py` (3 tests — alias absence, canonical presence, no stale waiver)
- Operator-authorized behave-coverage waiver for REQ-03-01/02/03 in `data/behave_coverage_waivers.json`
- Tests: full suite 5961 pass / 1 skip / 0 fail; cli audit 104/104; mkdocs --strict clean; behave 13/13; skill-alignment + documents + req-kind-discipline validators clean
- Defects noted: anchors GHI #588

## Tracked Defects

- REQ-count drift: 4 declared vs 3 acceptance criteria (brief reconcile, attestor g0)

- GHI #588 — anchor

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — deprecated obpi lock-claim/lock-release/lock-status hyphen aliases removed across all coupled surfaces (parser block, redundant obpi-lock-status.md manpage, doc-coverage entries, behave alias scenario, and 3 stale _NO_SKILL_VERBS skill-alignment waivers); canonical space forms intact. Full suite 5961 pass / 1 skip / 0 fail; cli audit 104/104; skill-alignment clean; behave 13/13. Receipts: arb-step-unittest-4a9c23d865274378b15a756176f7fbe0, arb-ruff-f5abd593884a4ea598aaef45065bcb41, arb-step-typecheck-8358e62da4224d658d50410fda5fc35b, arb-step-mkdocs-3717686a837b41339db41a1f8d8393c1.
- Date: 2026-06-08

---

**Date Completed:** 2026-06-08

**Evidence Hash:** -
