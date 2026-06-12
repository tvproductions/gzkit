---
id: OBPI-0.0.41-05-session-handoff-surface-updates
parent: ADR-0.0.41-token-block-lock-discipline
item: 5
lane: Heavy
status: Abandoned
---

# OBPI-0.0.41-05-session-handoff-surface-updates: Session-Handoff Surface Updates

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/ADR-0.0.41-token-block-lock-discipline.md`
- **Checklist Item:** #5 — OBPI-0.0.41-05: Update `gz-session-handoff` SKILL.md (CREATE trigger = `obpi_lock_release_cmd` invocation, not "when an agent pauses work"), `scripts/session_orientation.py` (single canonical store), `docs/user/runbook.md`, `docs/governance/governance_runbook.md`, and the per-turn agent contract surfaces. Bump skill version, run `gz agent sync control-surfaces`.

**Status:** Draft

## Objective

Make the surface layer match the runtime layer landed in OBPI-02/03/04 — rewrite the `gz-session-handoff` skill so its CREATE trigger is mechanical (`obpi_lock_release_cmd` invocation), wire the SessionStart hook (`scripts/session_orientation.py`) to warn at 50% TTL and auto-reap at 100% TTL per Sub-Invariant 4, refresh the runbooks, cross-link the token-block rule from AGENTS.md, bump the skill version, and rerun `gz agent sync control-surfaces` so canonical and mirror skill copies are byte-equivalent.

## Lane

**Heavy** — Changes an agent-facing contract surface (skill SKILL.md), changes a runtime behavior on the SessionStart hook (warn-then-reap timing), and bumps the skill version. All three are governance-surface contracts.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `.gzkit/skills/gz-session-handoff/SKILL.md` — rewrite CREATE trigger from "when an agent pauses work" to `obpi_lock_release_cmd` invocation; bump `metadata.skill-version`; cross-link `.gzkit/rules/token-block-discipline.md` § Sub-Invariant 5.
- `scripts/session_orientation.py` — (a) confirm `.gzkit/handoffs/` as the only discovery path (remove any ADR-package mirror read code); (b) on SessionStart, list active locks and log a WARNING for any whose elapsed time ≥ 50% TTL; (c) invoke `lock_manager.reap_expired_locks()` for any lock whose elapsed time ≥ 100% TTL.
- `docs/user/runbook.md` — refresh the OBPI lock workflow section to reflect fail-closed release, `--abandon` flag, reaping ledger trail.
- `docs/governance/governance_runbook.md` — refresh the governance side (validator usage, audit-path runbook entries).
- `AGENTS.md` — add a binding reference to `.gzkit/rules/token-block-discipline.md` in the appropriate Mechanical-scope list (the existing § "Mechanical scopes that bind here" block).
- `tests/scripts/test_session_orientation.py` — REQ-derived `@covers`-decorated tests for warn-at-50% and reap-at-100% behaviors.
- `tests/governance/test_token_block_discipline.py` — Sub-Invariant 4 integration assertions (warn-then-reap escalation policy is in code, not prose).

> Skill mirror copies (`.claude/skills/`, `.agents/skills/`, `.github/skills/`) regenerate from the canonical `.gzkit/skills/gz-session-handoff/SKILL.md` via `uv run gz agent sync control-surfaces` and are NOT in Allowed Paths — they are generated artifacts per ADR-0.0.33.

## Denied Paths

- `src/gzkit/lock_manager.py` — `reap_expired_locks` itself is owned by OBPI-03; this OBPI invokes the function from the hook but does not modify it.
- `src/gzkit/commands/obpi_lock.py` — release/claim command logic is owned by OBPI-02/03.
- `src/gzkit/governance/trust_audits/lock_handoff_coupling.py` — validator code is owned by OBPI-04.
- `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/ADR-0.0.41-token-block-lock-discipline.md` — parent ADR not modified here; OBPI-04 owns the `## Boundary Invariants` addition.
- `.gzkit/rules/token-block-discipline.md` — authored by OBPI-01; only read/cross-linked here.
- Skills other than `gz-session-handoff` — out of scope; only this one skill's contract changes.
- New dependencies, CI files, lockfiles.
- Paths not listed in Allowed Paths.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `scripts/session_orientation.py` MUST log a WARNING (to both stderr and `.gzkit/ledger.jsonl`) for every active OBPI lock whose elapsed time ≥ 50% of its TTL; thresholds MUST read from `lock_manager.LockData` semantics, never hardcoded in the hook. (REQ-0.0.41-05-01)
1. REQUIREMENT: `scripts/session_orientation.py` MUST invoke `lock_manager.reap_expired_locks()` at SessionStart for every lock whose elapsed time ≥ 100% TTL; the reap MUST emit the `abandoned_by_reaper` handoff and `obpi_lock_released` event per OBPI-03. The hook invokes — never reimplements — reaping. (REQ-0.0.41-05-02)
1. REQUIREMENT: `scripts/session_orientation.py` MUST read handoff documents only from `.gzkit/handoffs/`; no read or scan of `{ADR-package}/handoffs/`. (REQ-0.0.41-05-03)
1. REQUIREMENT: the `gz-session-handoff` SKILL.md CREATE-trigger language MUST match parent ADR § Decision item 4 verbatim (`obpi_lock_release_cmd` invocation); `metadata.skill-version` MUST be bumped to `6.6.0` or higher; canonical and mirror copies MUST be byte-equivalent after `gz agent sync control-surfaces`. (REQ-0.0.41-05-04)
1. REQUIREMENT: `docs/user/runbook.md` MUST name fail-closed release, the `--abandon` flag, and the `gz-session-handoff` skill as the binding lock workflow; `docs/governance/governance_runbook.md` MUST document `gz validate --lock-handoff-coupling` in its audit-path section. (REQ-0.0.41-05-05)
1. REQUIREMENT: `AGENTS.md` § "Mechanical scopes that bind here" MUST include a binding-bullet for `.gzkit/rules/token-block-discipline.md` § Sub-Invariants 1–5 with the matching `gz validate --lock-handoff-coupling` check reference. (REQ-0.0.41-05-06)

> STOP-on-BLOCKERS: if OBPI-02/03/04 have not landed, STOP. The skill rewrite references their behaviors (fail-closed release, abandoned_by_reaper handoff, validator), and stale skill text would mis-train agents on the unlanded contract.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 4 — quote into Implementation Summary verbatim.** "`gz-session-handoff` skill CREATE trigger is mechanical, not judgment. The trigger is `obpi_lock_release_cmd` invocation — the skill is the agent's tool for satisfying the release precondition, not 'when an agent pauses work.'"

> **STOP:** If you cannot quote parent ADR § Decision item 4 into Implementation Summary, STOP and re-read. The CREATE trigger rewrite is the contract.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/token-block-discipline.md` § Sub-Invariant 4 — TTL canon (warn at 50%, reap at 100%); § Sub-Invariant 5 — release precondition skill is meant to satisfy.
- [ ] `.gzkit/rules/skill-surface-sync.md` — rule-version + skill-version discipline; mirror byte-equivalence.
- [ ] `AGENTS.md` § "Mechanical scopes that bind here" — the binding-bullets list to extend.

**Context:**

- [ ] Current `.gzkit/skills/gz-session-handoff/SKILL.md` — the language to rewrite (CREATE-trigger section).
- [ ] Current `scripts/session_orientation.py` — the hook's existing structure; identify the SessionStart entry point.
- [ ] OBPI-02/03/04 briefs — confirm the surfaces this skill text now references are in their final shape.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-04 brief is at `attested_completed` state (the validator the runbook references must exist).
- [ ] `.gzkit/skills/gz-session-handoff/SKILL.md` exists with `metadata.skill-version` field (verified — current version `6.5.0`).
- [ ] `scripts/session_orientation.py` exists with a SessionStart entry point (verified).
- [ ] `uv run gz agent sync control-surfaces` is runnable (verified — gz-agent-sync skill).

**Existing Code (understand current state):**

- [ ] Read `.gzkit/skills/gz-session-handoff/SKILL.md` end-to-end — locate the CREATE trigger paragraph; identify all derived references that need update.
- [ ] Read `scripts/session_orientation.py` end-to-end — find the SessionStart hook entry point and the existing lock-discovery code (if any).
- [ ] Read `tests/scripts/test_session_orientation.py` — existing test conventions for the hook script.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 4 quoted into Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Warn-at-50%-TTL test authored RED (fixture lock with elapsed > 50% TTL; assert WARNING in ledger + stderr)
- [ ] Reap-at-100%-TTL test authored RED (fixture lock past TTL; assert reap_expired_locks invoked)
- [ ] Tests pass: `uv run gz test`
- [ ] Coverage maintained or improved

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] `docs/user/runbook.md` updated; `docs/governance/governance_runbook.md` updated
- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `uv run gz validate --documents --surfaces` clean

### Gate 4: BDD (Heavy)

- [ ] `features/` scenario covering SessionStart warn-at-50% behavior (seeded lock fixture)
- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded via `gz obpi complete --attestation-text "…"`

## Verification

```bash
uv run gz validate --documents
uv run gz validate --surfaces
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz agent sync control-surfaces
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# (a) Skill canonical + mirrors byte-equivalent after sync.
uv run gz agent sync control-surfaces
uv run gz validate --surfaces

# (b) SessionStart hook surfaces warn-at-50%-TTL (using a seeded lock fixture or natural state).
uv run python scripts/session_orientation.py

# (c) Resume any in-flight session via the skill's new CREATE-trigger semantics.
uv run gz adr status ADR-0.0.41-token-block-lock-discipline --json
```

## Acceptance Criteria

- [ ] REQ-0.0.41-05-01 [BEHAVIOR]: `scripts/session_orientation.py` logs a WARNING (to both stderr and `.gzkit/ledger.jsonl`) for every active OBPI lock whose elapsed time ≥ 50% of its TTL; thresholds read from `lock_manager.LockData` semantics, not hardcoded in the hook. Covering test: `tests/scripts/test_session_orientation.py::test_warn_at_half_ttl_emitted`.
- [ ] REQ-0.0.41-05-02 [BEHAVIOR]: `scripts/session_orientation.py` invokes `lock_manager.reap_expired_locks()` at SessionStart for every lock whose elapsed time ≥ 100% TTL; the reap call emits the `abandoned_by_reaper` handoff and `obpi_lock_released` ledger event per OBPI-03. Covering test: `tests/scripts/test_session_orientation.py::test_reap_at_full_ttl_invoked`.
- [ ] REQ-0.0.41-05-03 [BEHAVIOR]: `scripts/session_orientation.py` reads handoff documents only from `.gzkit/handoffs/`; no read or scan of `{ADR-package}/handoffs/**`. Covering test: `tests/scripts/test_session_orientation.py::test_no_adr_package_handoff_reads`.
- [ ] REQ-0.0.41-05-04 [SUPPORT]: `.gzkit/skills/gz-session-handoff/SKILL.md` CREATE-trigger language matches parent ADR § Decision item 4 verbatim ("`obpi_lock_release_cmd` invocation"); `metadata.skill-version` is bumped to `6.6.0` or higher; canonical and mirror copies are byte-equivalent after `gz agent sync control-surfaces`. Verified by `gz validate --surfaces` + `artifact_edited` ledger event.
- [ ] REQ-0.0.41-05-05 [SUPPORT]: `docs/user/runbook.md` OBPI lock workflow section names fail-closed release, `--abandon` flag, and `gz-session-handoff` skill as the binding workflow; `docs/governance/governance_runbook.md` documents `gz validate --lock-handoff-coupling` in the audit-path section. Verified by `gz validate --documents` + `artifact_edited` ledger event.
- [ ] REQ-0.0.41-05-06 [SUPPORT]: `AGENTS.md` § "Mechanical scopes that bind here" includes a binding-bullet entry for `.gzkit/rules/token-block-discipline.md` § Sub-Invariants 1–5 with the matching `gz validate --lock-handoff-coupling` check reference. Verified by `gz validate --documents` + `artifact_edited` ledger event.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent and Decision quote recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle; warn + reap tests authored RED before hook changes
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Runbooks updated; mkdocs --strict clean; surface validation clean
- [ ] **Gate 4 (BDD):** behave scenarios cover SessionStart warn path
- [ ] **Gate 5 (Human):** Heavy lane — human attestation required before `gz obpi complete`
- [ ] **Value Narrative:** Surface-layer ↔ runtime-layer drift named and closed
- [ ] **Key Proof:** Skill mirror byte-equivalence + SessionStart warn transcript included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded; Decision item 4 quoted in Implementation Summary

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint / type-check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build + surface-validate output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

<!-- Before OBPI-05: OBPI-02/03/04 close the runtime contract, but the agent-facing
     surface (skill + hook + runbook + AGENTS.md) still describes the old asymmetry
     (CREATE trigger = "when an agent pauses work"; runbooks silent on validator;
     no warn-then-reap on the hook). Agents trained on stale surfaces re-create the
     5/5/0 asymmetry from natural behavior. After OBPI-05: surface and runtime are
     in lockstep; agents are mechanically trained to satisfy the release precondition
     because the skill IS the satisfaction tool, not a parallel rule. -->

### Key Proof

<!-- Skill mirror byte-equivalence transcript; SessionStart hook warn-at-50% output;
     diff of runbook before/after showing the new lock-release workflow. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
