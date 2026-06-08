---
id: OBPI-0.0.67-02-wire-orphan-verbs-into-skills
parent: ADR-0.0.67-tool-skill-invariant1-enforcement
item: 2
lane: Heavy
status: Completed
ln:
  - req_id: REQ-0.0.67-02-01
    receipt_ids:
      - arb-step-unittest-6d1f2c6f463d40d79b274943f8249c86
      - arb-ruff-32fa35d49d984f6fb0e54e1faaa4be00
      - arb-step-typecheck-8397155f2c0146f9b9386549c52e81e9
      - arb-step-mkdocs-79257f294a494caeb93f3165a80ab0ed
  - req_id: REQ-0.0.67-02-02
    receipt_ids:
      - arb-step-unittest-6d1f2c6f463d40d79b274943f8249c86
      - arb-ruff-32fa35d49d984f6fb0e54e1faaa4be00
      - arb-step-typecheck-8397155f2c0146f9b9386549c52e81e9
      - arb-step-mkdocs-79257f294a494caeb93f3165a80ab0ed
  - req_id: REQ-0.0.67-02-03
    receipt_ids:
      - arb-step-unittest-6d1f2c6f463d40d79b274943f8249c86
      - arb-ruff-32fa35d49d984f6fb0e54e1faaa4be00
      - arb-step-typecheck-8397155f2c0146f9b9386549c52e81e9
      - arb-step-mkdocs-79257f294a494caeb93f3165a80ab0ed
  - req_id: REQ-0.0.67-02-04
    receipt_ids:
      - arb-step-unittest-6d1f2c6f463d40d79b274943f8249c86
      - arb-ruff-32fa35d49d984f6fb0e54e1faaa4be00
      - arb-step-typecheck-8397155f2c0146f9b9386549c52e81e9
      - arb-step-mkdocs-79257f294a494caeb93f3165a80ab0ed
  - req_id: REQ-0.0.67-02-05
    receipt_ids:
      - arb-step-unittest-6d1f2c6f463d40d79b274943f8249c86
      - arb-ruff-32fa35d49d984f6fb0e54e1faaa4be00
      - arb-step-typecheck-8397155f2c0146f9b9386549c52e81e9
      - arb-step-mkdocs-79257f294a494caeb93f3165a80ab0ed
  - req_id: REQ-0.0.67-02-06
    receipt_ids:
      - arb-step-unittest-6d1f2c6f463d40d79b274943f8249c86
      - arb-ruff-32fa35d49d984f6fb0e54e1faaa4be00
      - arb-step-typecheck-8397155f2c0146f9b9386549c52e81e9
      - arb-step-mkdocs-79257f294a494caeb93f3165a80ab0ed
# req_atomic exemption (return-to-health, 2026-06-08): each REQ is one
# indivisible wire/emit/remove/sync contract. The Implementation Summary
# confirms labor was not subdivided below a REQ, so one seq=01 TASK per REQ is
# the honest grain (no shared coarse-default bucket masking finer labor).
req_atomic:
  - REQ-0.0.67-02-01  # 10-verb audit-clean + none-in-waivers: one audit-clean contract
  - REQ-0.0.67-02-02  # reconcile Phase 1 wields gz obpi audit: one skill-wiring contract
  - REQ-0.0.67-02-03  # obpi_audit_cmd well-formed ledger entry: one audit-emit contract
  - REQ-0.0.67-02-04  # obpi_withdraw_cmd emit + reject re-withdrawal: one withdraw contract
  - REQ-0.0.67-02-05  # 13 stop-gap waivers removed from cli.py: one waiver-removal contract
  - REQ-0.0.67-02-06  # skill-version/last_reviewed bumps + mirror regen: one sync contract
---

# OBPI-0.0.67-02-wire-orphan-verbs-into-skills: Wire Orphan Verbs Into Skills (MAXX, no waivers)

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/ADR-0.0.67-tool-skill-invariant1-enforcement.md`
- **Checklist Item:** #2 — Wire the 10 live orphan verbs into 6 skills (no waivers) + test coverage for `obpi audit` / `obpi withdraw`.
- **Parent ADR § Decision (2) quoted:** "The 10 live orphan verbs are genuinely wielded by skills, with zero new `_NO_SKILL_VERBS` entries … Wiring MUST be genuine procedural use … not a name-drop."

**Status:** Completed

## Objective

Reclaim the 10 live orphan verbs by **genuinely wielding** each in a skill (no
waivers), remove the 13 stop-gap investigation-waivers from `cli.py`, and add
unit coverage for the two previously-uncalled tools (`obpi audit`, `obpi
withdraw`). Headline: `gz obpi audit` becomes the deterministic engine of
gz-obpi-reconcile Phase 1, replacing ad-hoc agent Read/Grep/Bash.

> **SEQUENCING:** Land this **first** (before OBPI-03 deletion and OBPI-01
> recursion keystone). While the audit is still top-level-only, these wirings are
> "dormant" (the audit can't see multi-word verbs yet) — so they land green and
> are activated when OBPI-01's recursion lands last.

## Lane

**Heavy** — edits 6 skill control surfaces (canonical + mirrors) and the
`gz validate --skill-alignment` coverage contract.

## Allowed Paths

- `.gzkit/skills/gz-obpi-reconcile/SKILL.md` — wield `gz obpi audit` (Phase 1, incl. `--adr`), `gz obpi emit-receipt` (receipt step), `gz obpi withdraw` (phantom remediation)
- `.gzkit/skills/gz-status/SKILL.md` — wield `gz obpi status <id>` (focused single-OBPI view)
- `.gzkit/skills/gz-adr-promote/SKILL.md` — wield `gz adr demote` (bidirectional lifecycle)
- `.gzkit/skills/gz-adr-sync/SKILL.md` — wield `gz adr covers-check`
- `.gzkit/skills/gz-arb/SKILL.md` — wield `gz arb ty` (raw `uvx ty` passthrough; NOT an alias of `arb typecheck`)
- `.gzkit/skills/gz-chore-runner/SKILL.md` — wield `gz chores propose-ghi`
- `.gzkit/skills/gz-skill-router/SKILL.md` — wield `gz skill list` and `gz skill new`
- `src/gzkit/governance/trust_audits/cli.py` — **remove** the 13 stop-gap waivers added during investigation (keep the recursion machinery)
- `tests/commands/` — new coverage for `obpi_audit_cmd` and `obpi_withdraw_cmd`

## Denied Paths

- New `_NO_SKILL_VERBS` entries for any of the 10 (no-waivers mandate)
- The 3 deprecated `obpi lock-*` aliases (OBPI-03 owns those)
- Hand-editing generated skill mirrors (use the sync command)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Each of the 10 verbs MUST be wielded by **genuine procedural use** in its home skill body or `gz_command:` — not a name-drop. Pre-mortem guard: a skill that merely mentions a verb in prose without using it in its procedure is an orphan-in-disguise.
1. REQUIREMENT: `gz-obpi-reconcile` Phase 1 MUST invoke `gz obpi audit` (and `gz obpi audit --adr`) as the deterministic evidence step, replacing the ad-hoc agent Read/Grep/Bash audit (SKILL.md lines 120-153). The verb's ledger schema already matches the skill's documented Ledger Schema v1 (SKILL.md lines 375-399 ↔ `obpi_audit_cmd._build_entry`).
1. REQUIREMENT: `obpi_audit_cmd` MUST produce a well-formed `obpi-audit` ledger entry with `criteria_evaluated` when called with an OBPI id or `--adr` scope.
1. REQUIREMENT: `obpi_withdraw_cmd` MUST emit an `obpi_withdrawn` event on first call; re-withdrawal of the same OBPI MUST be rejected.
1. REQUIREMENT: The 13 stop-gap investigation-waivers MUST be removed from `_NO_SKILL_VERBS` in `cli.py`; `gz validate --skill-alignment` MUST be green with zero of the 10 verbs remaining as waivers.
1. REQUIREMENT: Every edited canonical skill MUST bump `skill-version:` AND `last_reviewed:` (today) in the same edit; then run `uv run gz agent sync control-surfaces`.
1. NEVER: add a `_NO_SKILL_VERBS` waiver for any of the 10.
1. NEVER: hand-edit `.claude/`, `.agents/`, `.github/`, or `src/gzkit/skills/` mirrors.

## Discovery Checklist

**Parent ADR (read first):**
- [ ] Parent ADR § Decision (2) homing table — quoted above
- [ ] Parent ADR § Intent / Alternatives — why wire-not-waive

**Per-verb evidence (receipts — read the handler + the target skill before wiring):**
- [ ] `obpi audit` → `src/gzkit/commands/obpi_audit_cmd.py` (handler at line 13, single + `--adr`); reconcile SKILL.md lines 120-153, 375-399
- [ ] `obpi withdraw` → `src/gzkit/commands/obpi_cmd.py` (handler at line 59); ledger consumers `ledger.py` line 670, `state.py` line 86
- [ ] `obpi emit-receipt` → `parser_artifacts.py:1024` (`--event validated`)
- [ ] `obpi status` → `parser_artifacts.py:1048`
- [ ] `adr demote` → `parser_artifacts.py:812`; `adr covers-check` → `parser_artifacts.py:915`
- [ ] `arb ty` → `parser_arb.py:142` (distinct handler `arb_ty_cmd`, NOT `arb_typecheck_cmd`)
- [ ] `chores propose-ghi` → `parser_maintenance.py:1086`
- [ ] `skill list` / `skill new` → `parser_maintenance.py` LAZY_MAP `skill_list`/`skill_new` → `skills_cmd`
- [ ] `.gzkit/rules/skill-surface-sync.md` — edit canonical first, bump version + last_reviewed, sync

**Prerequisites (check existence, STOP if missing):**

- [ ] All 7 target canonical skills exist under `.gzkit/skills/` (gz-obpi-reconcile, gz-status, gz-adr-promote, gz-adr-sync, gz-arb, gz-chore-runner, gz-skill-router)
- [ ] `src/gzkit/governance/trust_audits/cli.py` contains the 13 stop-gap waivers to remove
- [ ] `uv run gz agent sync control-surfaces` runs clean before edits (baseline parity)

**Existing Code (understand current state):**

- [ ] Each target skill's current `gz_command:` + body, so wiring is additive and idiomatic to that skill
- [ ] `obpi_audit_cmd.py` / `obpi_cmd.py:59` handlers, so the new tests assert real behavior not strings
- [ ] `tests/commands/common.py` mocking harness (subprocess boundaries) for the new command tests

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent Decision item quoted

### Gate 2: TDD
- [ ] New tests for `obpi_audit_cmd` + `obpi_withdraw_cmd` (RED→GREEN)
- [ ] `uv run gz test`

### Code Quality
- [ ] `uv run gz lint`
- [ ] `uv run gz typecheck`

### Gate 3: Docs (Heavy)
- [ ] `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy)
- [ ] n/a — skill-content + unit coverage; no new behave surface

### Gate 5: Human (Heavy)
- [ ] Human attestation recorded

## Verification

```bash
uv run gz agent sync control-surfaces
uv run gz validate --skill-alignment
uv run gz validate --surfaces
uv run -m unittest discover -s tests -t .
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
```

## Demo

```bash
# obpi audit is now the deterministic Phase-1 engine reconcile wields:
uv run gz obpi audit --adr ADR-0.0.67
# skill catalog + scaffolding wielded by gz-skill-router:
uv run gz skill list
```

## Acceptance Criteria

- [ ] REQ-0.0.67-02-01 [behavior]: Given the 10 reclaimed verbs, when `audit_skill_alignment` runs (post-OBPI-01), then each is found wielded (`verb_refs` non-empty) and none appears in `_NO_SKILL_VERBS`. (@covers test asserting audit-clean + none-of-10-in-waivers)
- [ ] REQ-0.0.67-02-02 [support]: `gz-obpi-reconcile` Phase 1 procedure invokes `gz obpi audit` / `gz obpi audit --adr` (deterministic evidence step). Proof: `artifact_edited` ledger event for the SKILL.md + `gz validate --skill-alignment` admits the wielding.
- [ ] REQ-0.0.67-02-03 [behavior]: Given an OBPI with discoverable tests, when `obpi_audit_cmd(obpi_id)` and `obpi_audit_cmd(adr_id=...)` run, then a well-formed `obpi-audit` ledger entry with `criteria_evaluated` is produced. (@covers test in `tests/commands/`)
- [ ] REQ-0.0.67-02-04 [behavior]: Given an OBPI in the ledger, when `obpi_withdraw_cmd` runs, then an `obpi_withdrawn` event is emitted and re-withdrawal is rejected. (@covers test in `tests/commands/`)
- [ ] REQ-0.0.67-02-05 [support]: The 13 stop-gap investigation-waivers are removed from `_NO_SKILL_VERBS` (`cli.py`). Proof: `artifact_edited` ledger event + `gz validate --skill-alignment` green.
- [ ] REQ-0.0.67-02-06 [support]: Every edited skill bumps `skill-version` + `last_reviewed`; mirrors regenerated. Proof: `artifact_edited` events + `gz validate --surfaces` green.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** new-tool coverage RED→GREEN
- [ ] **Code Quality:** lint/typecheck clean
- [ ] **Value Narrative:** documented below
- [ ] **Key Proof:** included below
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste obpi_audit_cmd + obpi_withdraw_cmd test output here
```

### Code Quality
```text
# Paste lint/typecheck output here
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict output here
```

### Gate 4 (BDD)
```text
# n/a
```

### Gate 5 (Human)
```text
# Record operator attestation text here
```

### Value Narrative

Before: 10 live, capable verbs had no skill wielding them — including `obpi audit`
(a 240-LOC deterministic auditor reconcile reimplemented ad-hoc) and `obpi
withdraw` (a fully ledger-integrated phantom-cleanup tool nobody could discover).
Now: every verb is wielded; reconcile Phase 1 is deterministic; reconcile can
remediate the 233 phantom `obpi_created` events of GHI #584.

### Key Proof


uv run gz validate --skill-alignment -> All validations passed (1 scopes), with zero of the 10 verbs in _NO_SKILL_VERBS and each wielded in its home skill. ARB receipts: arb-step-unittest-a78ed6bc1d644a109858825b5c0fcfc3 (5958 pass), arb-ruff-47525216a6ea46ee9d38852309ffce00, arb-step-typecheck-ac259f85e30d4064bcfb4319a3010b4b, arb-step-mkdocs-505449bdf3b244099fc950a4d775b113. gz covers OBPI-0.0.67-02 -> behavior_uncovered_reqs=0 (3 BEHAVIOR covered, 3 SUPPORT grandfathered).

### Implementation Summary


- Wired 10 orphan CLI verbs into 6 skills (genuine procedural use, no name-drops): gz-obpi-reconcile (obpi audit/emit-receipt/withdraw), gz-status (obpi status), gz-adr-promote (adr demote), gz-adr-sync (adr covers-check), gz-arb (arb ty), gz-chore-runner (chores propose-ghi), gz-skill-router (skill list/new)
- gz-obpi-reconcile Phase 1 now invokes gz obpi audit / gz obpi audit --adr as the deterministic evidence step, replacing ad-hoc agent Read/Grep/Bash
- Removed 10 multi-word stop-gap waivers from _NO_SKILL_VERBS (cli.py); kept the 3 deprecated obpi lock-* aliases (OBPI-03 owns their parser+doc-cascade removal)
- Added unit coverage: test_obpi_audit_cmd.py, test_obpi_withdraw_cmd.py, test_skill_alignment_10verbs.py (6 tests, RED to GREEN)
- All 7 skills bumped skill-version + last_reviewed (2026-06-07); mirrors regenerated via gz agent sync control-surfaces
- Tests: 5958 pass; lint/typecheck/mkdocs clean; gz validate --skill-alignment green
- Defects noted: anchors GHI #588; obpi withdraw wiring serves GHI #584

## Tracked Defects

- REQ-count drift: 3 declared vs 6 acceptance criteria (brief reconcile, attestor g0)

- GHI #588 — anchor
- GHI #584 — `obpi withdraw` wiring gives reconcile the remediation tool (related)

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — operator Gate-5 attestation (2026-06-07) for OBPI-0.0.67-02-wire-orphan-verbs-into-skills: 10 orphan CLI verbs genuinely wired into 6 skills with zero new _NO_SKILL_VERBS waivers; gz-obpi-reconcile Phase 1 now wields gz obpi audit deterministically; 5958 unittests pass (receipt arb-step-unittest-a78ed6bc1d644a109858825b5c0fcfc3), lint/typecheck/mkdocs clean (arb-ruff-47525216a6ea46ee9d38852309ffce00, arb-step-typecheck-ac259f85e30d4064bcfb4319a3010b4b, arb-step-mkdocs-505449bdf3b244099fc950a4d775b113); gz validate --skill-alignment and --surfaces green.
- Date: 2026-06-07

---

**Date Completed:** 2026-06-07

**Evidence Hash:** -
