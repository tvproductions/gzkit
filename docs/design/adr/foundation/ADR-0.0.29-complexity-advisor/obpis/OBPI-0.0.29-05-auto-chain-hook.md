---
id: OBPI-0.0.29-05-auto-chain-hook
parent: ADR-0.0.29
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.29-05-auto-chain-hook: Auto-chain from xenon-as-gate Failure

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md`
- **Checklist Item:** #5 — "Auto-chain from xenon-as-gate failure (pre-commit hook; preserves SKIP-bypass guard wiring)"

**Status:** Draft

## Objective

Implement the pre-commit auto-chain hook at `.gzkit/hooks/pre-commit-complexity-advisor` that fires `gz complexity-advise --auto-chain` when xenon-as-gate exits non-zero. Preserve the existing `complexity-reduction-xenon` chore's SKIP-bypass guard wiring; the hook is additive on the failure path, not substitutive of xenon.

## Lane

**Heavy** — New pre-commit hook is an operator-facing surface that can affect every commit. Foundation-kind brief-level Gate 5 attestation per ADR-0.0.18.

## Allowed Paths

- `.gzkit/hooks/pre-commit-complexity-advisor`
- `src/gzkit/hooks/install_complexity_advisor.py` — installer helper invoked by `gz init` or operator-explicit install
- `tests/hooks/test_complexity_advisor_auto_chain.py`
- `features/complexity_advisor_auto_chain.feature` — behave scenario tagged with REQ IDs
- `docs/user/runbook.md` — entry under "Complexity doctrine surfaces" describing the hook
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-05-auto-chain-hook.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/commands/complexity_advise.py` — CLI is OBPI-03; this OBPI consumes it
- `src/gzkit/complexity/advisor/timeout.py` — timeout is OBPI-09 (this hook invokes it but does not implement it)
- `src/gzkit/chores/complexity-reduction-xenon/**` — chore strengthening is tracked separately (per handoff)
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The hook at `.gzkit/hooks/pre-commit-complexity-advisor` is opt-in: `gz init` does NOT install it by default; the operator runs `python -m gzkit.hooks.install_complexity_advisor` (or equivalent CLI surface — preferred) to install. The rationale per § Negative #6: pre-commit hook interaction is fragile; opt-in defends against unwelcome installation.
2. REQUIREMENT: The hook runs xenon-as-gate first (preserving the `complexity-reduction-xenon` chore's existing invocation) and inspects the exit code. On exit 0, the hook exits 0 silently. On non-zero exit, the hook fires `gz complexity-advise --auto-chain <staged-files>`.
3. REQUIREMENT: The hook honors the existing SKIP-bypass guard wiring: if the operator's environment names the SKIP variable per the chore's existing convention, both xenon AND the auto-chain advisor are skipped. The SKIP semantics are NOT redefined here; they are honored as-is from the chore.
4. REQUIREMENT: The hook wraps the `gz complexity-advise --auto-chain` invocation in OBPI-09's timeout primitive; on timeout the hook fails open with a logged warning (per OBPI-09's contract).
5. REQUIREMENT: The hook only inspects staged files (not the full working tree); auto-chain analysis is scoped to what the developer is committing.
6. REQUIREMENT: The hook's exit code on auto-chain block-band crossing is 1 (developer must amend); on warn-band crossing the hook exits 0 with diagnosis printed to stderr (commit proceeds, advisor diagnosis informs the operator).
7. REQUIREMENT: Tests cover: hook exits 0 silently when xenon exits 0; hook fires advisor when xenon exits non-zero; hook honors SKIP env var (xenon + advisor both skipped); hook wraps in timeout (mocked); hook scopes to staged files only; hook exit codes match the contract above. Each test decorated with `@covers(REQ-0.0.29-05-NN)`. Tests use `tempfile`-backed git repo fixtures.
8. REQUIREMENT: A behave scenario at `features/complexity_advisor_auto_chain.feature` tagged `@REQ-0.0.29-05-{01..04}` covers the four canonical paths: clean commit, warn-band commit, block-band commit, SKIP-bypassed commit.
9. REQUIREMENT: Runbook entry under "Complexity doctrine surfaces" prescribes the install command and documents the SKIP semantics.
10. REQUIREMENT: Hook script is POSIX-shell-compatible and tested on Linux + macOS; cross-platform invocation per `.claude/rules/cross-platform.md` (Windows hook installation is a forward-iteration concern; the Python installer is cross-platform but the hook itself is shell — a pool stub or future OBPI may add Windows-native hook scripts).
11. REQUIREMENT: TDD discipline; hooks tested via subprocess invocation in behave only, mocked at the Python boundary in unit tier per `.claude/rules/tests.md`.
12. REQUIREMENT: NEVER include the operator's personal email in hook script, installer, runbook, fixtures, or commit messages.

> STOP-on-BLOCKERS: if OBPI-03's CLI verb (`gz complexity-advise --auto-chain` semantics) and OBPI-09's timeout primitive are not present, STOP — both are consumer dependencies of this hook.

## Discovery Checklist

- [ ] OBPI-03 CLI verb (`--auto-chain` flag semantics)
- [ ] OBPI-09 timeout primitive
- [ ] `src/gzkit/chores/complexity-reduction-xenon/CHORE.md` — existing SKIP-bypass guard wiring
- [ ] Parent ADR § Decision — opt-in install, exit-code semantics, staged-file scoping
- [ ] `.claude/rules/cross-platform.md` — POSIX shell discipline + Windows boundary
- [ ] AGENTS.md § Behavior Rules — hook discipline (do not work around hook blocks; investigate root cause)

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Runbook entry with install command + SKIP semantics

### Gate 4: BDD (Heavy)
- [ ] Behave scenarios pass for four canonical paths with REQ tags

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest tests/hooks/test_complexity_advisor_auto_chain.py -v
uv run -m behave features/complexity_advisor_auto_chain.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.29-05-01: Given xenon exits 0, when the hook runs, then the hook exits 0 silently and the advisor is not invoked.
- [ ] REQ-0.0.29-05-02: Given xenon exits non-zero, when the hook runs, then `gz complexity-advise --auto-chain` is invoked against staged files.
- [ ] REQ-0.0.29-05-03: Given the SKIP environment variable is set per the existing chore convention, when the hook runs, then both xenon and the advisor are skipped (exit 0 silent).
- [ ] REQ-0.0.29-05-04: Given a block-band crossing in staged files, when the hook runs the advisor, then the hook exits 1 (commit blocked).
- [ ] REQ-0.0.29-05-05: Given a warn-band crossing only, when the hook runs the advisor, then the hook exits 0 with diagnosis printed to stderr.
- [ ] REQ-0.0.29-05-06: Given the advisor times out per OBPI-09, when the hook runs, then it fails open with logged warning (commit proceeds).
- [ ] REQ-0.0.29-05-07: Given the runbook entry, when read, then the install command and SKIP semantics are documented.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: mkdocs --strict + runbook entry
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
# Paste mkdocs --strict + runbook diff
```

### Gate 4 (BDD)
```text
# Paste behave output for four canonical paths
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
