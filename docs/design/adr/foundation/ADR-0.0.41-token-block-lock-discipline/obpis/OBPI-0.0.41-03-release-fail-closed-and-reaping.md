---
id: OBPI-0.0.41-03-release-fail-closed-and-reaping
parent: ADR-0.0.41-token-block-lock-discipline
item: 3
lane: Heavy
status: Completed
req_atomic:
  - REQ-0.0.41-03-01  # one edit: flip the release no-handoff branch to exit 3 + its fail-closed test — single indivisible TDD unit
  - REQ-0.0.41-03-02  # one helper: _write_reaping_handoff frontmatter + its field-assertion test — no labor below the REQ
  - REQ-0.0.41-03-03  # one emission: obpi_lock_released with handoff_path in reap + its capturing-double test — single unit
  - REQ-0.0.41-03-04  # one ordering invariant: write→unlink→event try/except + its negative fail-closed test — single unit
  - REQ-0.0.41-03-05  # one static fence: no ADR-package handoff writes assertion over src/ — single unit
  - REQ-0.0.41-03-06  # one coupled-surface doc pass: both obpi-lock manpages (exit-3 + reaping) — single unit
---

# OBPI-0.0.41-03-release-fail-closed-and-reaping: Release Fail-Closed and Reaping

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/ADR-0.0.41-token-block-lock-discipline.md`
- **Checklist Item:** #3 — OBPI-0.0.41-03: Flip release precondition to fail-closed. `obpi_lock_release_cmd` rejects release without a register entry (or `--abandon`). Update `lock_manager.py:reap_expired_locks` to emit the OBPI-01-specified `abandoned_by_reaper` degenerate handoff per reaped lock. Storage consolidation: `.gzkit/handoffs/` becomes the canonical write target; ADR-package mirror is regenerated as Layer-3 derived view. Migrate existing register entries.

**Status:** Completed

## Objective

Flip the OBPI-02 release warning to fail-closed (exit 3) and rewrite `reap_expired_locks` to emit an `abandoned_by_reaper` degenerate handoff plus an `obpi_lock_released` ledger event per reaped lock — making reaping symmetric with ordinary release per Sub-Invariant 3 § Reaping-Attestation Requirement. Confirm `.gzkit/handoffs/` as the only handoff write target; no register-entry migration is needed (45 entries already canonical; the ADR-package mirror has no on-disk presence).

## Lane

**Heavy** — Flips a runtime contract from warning to fail-closed (a backwards-incompatible behavior change at the `gz obpi lock release` surface) and changes `reap_expired_locks` from silent delete to ledger-witnessed surrender.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/commands/obpi_lock.py` — `obpi_lock_release_cmd` flips the OBPI-02 warning to fail-closed (exit 3) when no handoff and no `--abandon`.
- `src/gzkit/lock_manager.py` — `reap_expired_locks` rewritten to write an `abandoned_by_reaper` handoff before deletion, emit `obpi_lock_released` event with `handoff_path`, and fail-closed (preserve the lock) if the handoff write fails.
- `src/gzkit/content/models/handoff.py` — only if `abandoned_by_reaper` shape needs reaping-specific fields beyond OBPI-02's additions (`previous_agent`, `abandoned_at` may already be present from OBPI-02).
- `src/gzkit/ledger_events.py` — only if `obpi_lock_released_event` needs a reaping-source distinction; otherwise the existing OBPI-02 surface suffices.
- `docs/user/manpages/obpi-lock-release.md` — exit codes table reflects exit 3 (policy breach); new "Reaping behavior" subsection documents the abandoned_by_reaper write.
- `docs/user/manpages/obpi-lock-list.md` — note that list reaping now emits ledger events + handoff files.
- `tests/test_lock_manager.py` — REQ-derived `@covers`-decorated tests for `reap_expired_locks` rewriting (handoff written, event emitted, handoff_path populated, fail-closed on write error).
- `tests/test_obpi_lock_cmd.py` — REQ-derived `@covers`-decorated tests for `obpi_lock_release_cmd` fail-closed flip (exit 3 on no handoff; existing happy paths still succeed).
- `tests/governance/test_token_block_discipline.py` — add Sub-Invariant 3 + Sub-Invariant 5 assertions (release fail-closed; reaping writes register entry before delete).
- `src/gzkit/handoff_validation.py` — READ-ONLY test dependency, NOT edited here. `tests/governance/test_token_block_discipline.py` imports `find_handoff_for_release` / `write_degenerate_handoff` / `parse_abandon_spec` for its OBPI-01/02 assertions; because OBPI-03 also adds reap tests to that shared module, the brief-reconcile allowlist must list this import. OBPI-02 owns the surface.

## Denied Paths

- `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/ADR-0.0.41-token-block-lock-discipline.md` — no parent-ADR amendments here; STRUCTURAL-FENCE + Boundary Invariants belong to OBPI-04.
- `src/gzkit/validators/**` or the `--lock-handoff-coupling` validator scope — OBPI-04 owns this.
- `scripts/session_orientation.py`, `.gzkit/skills/gz-session-handoff/**`, `docs/user/runbook.md`, `docs/governance/governance_runbook.md` — surface updates and warn-at-50%-TTL logic belong to OBPI-05.
- `src/gzkit/lock_manager.py:write_lock` race-fix — OBPI-02 owns that surface.
- `src/gzkit/cli/parser_artifacts.py` `--abandon` flag registration — OBPI-02 owns that.
- New dependencies, CI files, lockfiles.
- Paths not listed in Allowed Paths.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `obpi_lock_release_cmd` MUST exit 3 (policy breach) when no handoff matches the active lock AND `--abandon` is not provided; the stderr message MUST name both the `gz-session-handoff` skill and the `--abandon` flag as remediation. OBPI-02's `--abandon` happy path and the found-handoff path MUST still succeed (exit 0) — OBPI-03 only flips the no-handoff-no-abandon case from warning to fail-closed. (REQ-0.0.41-03-01)
1. REQUIREMENT: `reap_expired_locks` MUST write an `abandoned_by_reaper` degenerate handoff to `.gzkit/handoffs/` for each reaped lock — frontmatter `abandoned: true`, `category: reaping`, `abandoned_by`, `abandoned_at`, `previous_agent`, plus the Sub-Invariant 2 minimum-information fields. (REQ-0.0.41-03-02)
1. REQUIREMENT: For each reaped lock, `reap_expired_locks` MUST emit an `obpi_lock_released` ledger event whose `handoff_path` points at the written register entry, replacing the current silent-delete behavior. NO code path may emit `obpi_lock_released` without a `handoff_path` payload (OBPI-02 made the field optional; OBPI-03 makes it mandatory at every emission site). (REQ-0.0.41-03-03)
1. REQUIREMENT: When the `abandoned_by_reaper` handoff write fails, `reap_expired_locks` MUST NOT delete the lock file and MUST NOT emit the ledger event — the handoff is written BEFORE deletion; failure preserves the lock (fail-closed, Sub-Invariant 3 § Reaping-Attestation Requirement). (REQ-0.0.41-03-04)
1. REQUIREMENT: After this OBPI lands, NO code path under `src/gzkit/` MUST write a handoff to `{ADR-package}/handoffs/`; all handoff writes MUST target `.gzkit/handoffs/`. (REQ-0.0.41-03-05)
1. REQUIREMENT: `docs/user/manpages/obpi-lock-release.md` MUST reflect exit 3 in its exit-codes table and document the `abandoned_by_reaper` reaping behavior in a Reaping subsection; `docs/user/manpages/obpi-lock-list.md` MUST note that reaping during `list` now emits ledger events. (REQ-0.0.41-03-06)

> STOP-on-BLOCKERS: if OBPI-02 has not landed and merged, STOP. The `--abandon` flag and degenerate-handoff writer are upstream of this OBPI; flipping fail-closed without them collapses operator workflows.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 1 — quote into Implementation Summary verbatim.** The "MUST refuse to release the lock unless …" rule is the contract OBPI-03 finally enforces.
- [ ] Parent ADR § Consequences § Negative — the "Backwards incompatible at the release-edge once OBPI-03 lands" framing; this OBPI is the named cost.

> **STOP:** If you cannot quote parent ADR § Decision item 1 into Implementation Summary, STOP and re-read. The fail-closed flip is the contract; everything else hangs off it.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/token-block-discipline.md` § Sub-Invariant 3 — reaping register-entry rule; § Sub-Invariant 5 — release fail-closed precondition.
- [ ] `.gzkit/rules/cli.md` — exit-code conventions (exit 3 = policy breach).

**Context:**

- [ ] OBPI-02 brief + landed implementation — the `--abandon` flag, degenerate-handoff writer, and warning text this OBPI promotes to fail-closed.
- [ ] OBPI-04 checklist line (parent ADR line 165) — the validator OBPI-04 will write enforces the post-OBPI-03 ledger invariant; verify naming/payload shape compatible.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-02 brief is at `attested_completed` state (or at minimum the `--abandon` flag has landed) — `gz adr status ADR-0.0.41-token-block-lock-discipline --json`.
- [ ] `.gzkit/handoffs/` exists and contains at least one existing register entry (verified: 45 entries on disk).
- [ ] `src/gzkit/lock_manager.py` (`reap_expired_locks`) exists (verified — line 171).
- [ ] `src/gzkit/commands/obpi_lock.py` (`obpi_lock_release_cmd`) exists (verified — line 92).

**Existing Code (understand current state):**

- [ ] Read `src/gzkit/lock_manager.py` (`reap_expired_locks`) (lines 171-182) — current silent-delete behavior; no ledger event emission, no handoff write.
- [ ] Read `src/gzkit/commands/obpi_lock.py` (`obpi_lock_release_cmd`) (lines 92-138) — OBPI-02's warning text is the template for the fail-closed message.
- [ ] Read `.gzkit/handoffs/` sample entries — current frontmatter shape; ensure `abandoned_by_reaper` writes follow the convention.
- [ ] Read `tests/test_lock_manager.py` for existing reap-test patterns.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 1 quoted into Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Fail-closed release test authored RED first (exit 3; stderr names skill + flag)
- [ ] Reaping-writes-handoff test authored RED before reap_expired_locks rewrite
- [ ] Reap-fails-closed-on-write-error test authored RED (handoff write raises → lock survives + no ledger event)
- [ ] Tests pass: `uv run gz test`
- [ ] Coverage maintained or improved

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/obpi-lock-release.md` exit codes table updated; reaping subsection added
- [ ] `docs/user/manpages/obpi-lock-list.md` notes ledger emission on reaping
- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy)

- [ ] `features/` scenario covering fail-closed release (exit 3 transcript)
- [ ] `features/` scenario covering reaping (expired lock → abandoned_by_reaper handoff + ledger event)
- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded via `gz obpi complete --attestation-text "…"`

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --closeout-proof
```

## Demo

```bash
# (a) Fail-closed release: no handoff, no --abandon → exit 3.
uv run gz obpi lock claim OBPI-DEMO-0.1 --ttl 60 --json
uv run gz obpi lock release OBPI-DEMO-0.1 --json

# (b) Reaping demo: expire a lock; next list reaps it, writes abandoned_by_reaper handoff, emits ledger event.
uv run gz obpi lock claim OBPI-DEMO-0.1 --ttl 1 --json
uv run gz obpi lock list --json

# (c) Inspect the reaped-handoff frontmatter and the most-recent release event.
uv run gz state --json
```

## Acceptance Criteria

- [ ] REQ-0.0.41-03-01 [BEHAVIOR]: `obpi_lock_release_cmd` exits 3 (policy breach) when no handoff document matches the active lock AND `--abandon` is not provided; stderr message names both `gz-session-handoff` skill and `--abandon` flag as remediation paths. Covering test: `tests/test_obpi_lock_cmd.py::test_release_fail_closed_without_handoff_or_abandon`.
- [ ] REQ-0.0.41-03-02 [BEHAVIOR]: `lock_manager.reap_expired_locks` writes an `abandoned_by_reaper` degenerate handoff to `.gzkit/handoffs/` for each reaped lock — frontmatter includes `abandoned: true`, `category: reaping`, `abandoned_by: <reaper-agent>`, `abandoned_at: <ISO-timestamp>`, `previous_agent: <agent-from-claim>`, plus minimum-info fields from Sub-Invariant 2. Covering test: `tests/test_lock_manager.py::test_reap_writes_abandoned_by_reaper_handoff`.
- [ ] REQ-0.0.41-03-03 [BEHAVIOR]: For each reaped lock, `reap_expired_locks` emits an `obpi_lock_released` ledger event whose `handoff_path` payload points at the written `abandoned_by_reaper` register entry; replaces the current silent-delete behavior at `lock_manager.py:178`. Covering test: `tests/test_lock_manager.py::test_reap_emits_ledger_event_with_handoff_path`.
- [ ] REQ-0.0.41-03-04 [BEHAVIOR]: When the `abandoned_by_reaper` handoff write fails (e.g., filesystem error), `reap_expired_locks` MUST NOT delete the lock file and MUST NOT emit the ledger event — preserves Sub-Invariant 3 § Reaping-Attestation Requirement. Covering test: `tests/governance/test_token_block_discipline.py::test_reap_fails_closed_when_handoff_write_fails`.
- [ ] REQ-0.0.41-03-05 [BEHAVIOR]: After OBPI-03 lands, no code path under `src/gzkit/` writes a handoff document to `{ADR-package}/handoffs/`; all writes target `.gzkit/handoffs/`. Covering test: `tests/governance/test_token_block_discipline.py::test_no_adr_package_handoff_writes` (grep-based static assertion plus runtime verification on `gz obpi lock release --abandon`).
- [ ] REQ-0.0.41-03-06 [SUPPORT]: `docs/user/manpages/obpi-lock-release.md` exit codes table reflects exit 3 (policy breach) for no-handoff-no-abandon; a new "Reaping behavior" subsection documents the `abandoned_by_reaper` write and ledger emission. `docs/user/manpages/obpi-lock-list.md` notes that reaping during `list` now emits ledger events. Verified by `gz validate --documents` + `artifact_edited` ledger event.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent and Decision quote recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle; fail-closed test RED before release flip; reap-write-then-emit test RED before lock_manager rewrite
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Manpages updated; mkdocs --strict clean
- [ ] **Gate 4 (BDD):** behave scenarios cover fail-closed + reaping happy paths
- [ ] **Gate 5 (Human):** Heavy lane — human attestation required before `gz obpi complete`
- [ ] **Value Narrative:** Warning-before-bite (OBPI-02) → bite (OBPI-03) framing; reaping symmetry recorded
- [ ] **Key Proof:** Fail-closed transcript + reaping ledger event JSON included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded; Decision item 1 quoted in Implementation Summary

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
# Paste docs-build output here
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

<!-- Before OBPI-03: release silently succeeds without a handoff (warning only —
     OBPI-02 staging); reap_expired_locks silently deletes lock files with no
     ledger trail. After OBPI-03: release fail-closes (exit 3) on no-handoff-
     no-abandon; reaping emits abandoned_by_reaper handoff + ledger event,
     making forcible surrender as auditable as voluntary surrender.
     The asymmetry GHI #410 surfaced (5/5/0) is closed at every code path. -->

### Key Proof


$ uv run gz obpi precomplete OBPI-0.0.41-03-release-fail-closed-and-reaping → READY (8/8 preconditions). Full suite: 6033 tests pass (receipt arb-step-unittest-c7c7cd4adb494d6aa1746df098be40b9). Fail-closed ordering proven negatively: tests/governance/test_token_block_discipline.py::test_reap_fails_closed_when_handoff_write_fails patches _write_reaping_handoff to raise OSError → asserts the lock file survives, no obpi_lock_released event captured, reaped == []. gz covers OBPI-0.0.41-03 --json: behavior_uncovered_reqs=0 (5 BEHAVIOR covered; REQ-03-06 SUPPORT grandfathered). ARB lint/typecheck/unittest/mkdocs all exit_status=0.

### Implementation Summary


- Release fail-closed: obpi_lock_release_cmd exits 3 without --abandon and no matching register entry; stderr names the gz-session-handoff skill + --abandon; the --abandon and found-handoff paths still exit 0 (REQ-03-01).
- Reaping symmetry: reap_expired_locks writes an abandoned_by_reaper register entry (abandoned/category:reaping/abandoned_by/abandoned_at/previous_agent + Sub-Invariant-2 min-info) BEFORE deleting, then deletes, then emits obpi_lock_released with handoff_path; OSError on write OR unlink → lock survives, no event, not reaped (REQ-03-02/03/04).
- Storage fence: all handoff writes target .gzkit/handoffs/ (REQ-03-05). Manpages obpi-lock-release/list updated for exit-3 + reaping (REQ-03-06, SUPPORT).
- Design: reap's ledger sink typed as a structural _LedgerSink Protocol (LedgerEvent under TYPE_CHECKING) — no layering/circular import; tests use a capturing double.
- In-flight fixes (disclosed): reviewer F1 (unguarded unlink), a circular import, a YAML-timestamp test-helper bug, and brief-reconcile false-positives — resolved via the Protocol + doubles + req_atomic + reshaping the three 0.0.41 briefs to the REQUIREMENT: convention.
- Files: src/gzkit/lock_manager.py, src/gzkit/commands/obpi_lock.py, docs/user/manpages/obpi-lock-release.md + obpi-lock-list.md, tests/test_lock_manager.py, tests/test_obpi_lock_cmd.py, tests/governance/test_token_block_discipline.py.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.41-03 release fail-closed + reaping: release exits 3 without --abandon and no matching register entry (stderr names the gz-session-handoff skill AND --abandon); reap_expired_locks writes an abandoned_by_reaper register entry, then deletes the lock, then emits obpi_lock_released with handoff_path — fail-closed on write OR unlink failure (no event for a surrender that did not complete); manpages updated; full suite 6033 green; independent spec-reviewer PASS + quality-reviewer COHERENT with reviewer F1 (unguarded unlink / event-before-delete) fixed. Evidence — lint: receipt arb-ruff-a5dd88ec0657479c88e7583d80292e53; typecheck: receipt arb-step-typecheck-96b6a40f8a86406a81729acd13424e7c; unittest: receipt arb-step-unittest-a4e17c56b7f74843accc342ea8dfb37a; mkdocs: receipt arb-step-mkdocs-70343cb28b5d49b9a6c69b327204cadd
- Date: 2026-06-11

---

**Date Completed:** 2026-06-11

**Evidence Hash:** -
