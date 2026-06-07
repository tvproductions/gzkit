---
id: OBPI-0.0.67-01-recursive-verb-path-enumeration
parent: ADR-0.0.67-tool-skill-invariant1-enforcement
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.67-01-recursive-verb-path-enumeration: Recursive Verb Path Enumeration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/ADR-0.0.67-tool-skill-invariant1-enforcement.md`
- **Checklist Item:** #1 — Recursive verb-path enumeration + group-cascade waivers so `audit_skill_alignment` enforces Invariant 1 across multi-word subcommands (foundation port).
- **Parent ADR § Decision (1) quoted:** "Add `_known_cli_verb_paths()` that walks the full argparse tree and returns space-joined leaf paths … `audit_skill_alignment` enforces against this full surface. `_NO_SKILL_VERBS` gains group-prefix cascade + multi-word key support … `_known_cli_verbs()` (top-level) is left untouched so `audit_cli_alignment`'s behavior is unchanged."

**Status:** Draft

## Objective

Make `audit_skill_alignment` enforce Invariant 1 across the **full** CLI surface
(multi-word subcommands), via recursive enumeration + group-cascade waivers, with
a non-vacuous regression test. **This is the keystone — it lands LAST** (after
OBPI-02 wiring and OBPI-03 deletion), so the moment the audit can see multi-word
verbs, they are already wielded/removed and the audit goes green in one step.

> **SEQUENCING (critical):** Implementation order is **02 → 03 → 01**. The
> recursion mechanism is already present in the working tree from the in-flight
> investigation; OBPI-02 removes the 13 stop-gap waivers and replaces them with
> real wiring, OBPI-03 deletes the 3 deprecated aliases, and this OBPI lands the
> mechanism + tests as the keystone. Landing recursion before wiring/deletion
> would make `gz check` RED on 13 orphans — do not do that under the no-waivers
> mandate.

## Lane

**Heavy** — changes the `gz validate --skill-alignment` runtime-contract surface.

## Allowed Paths

- `src/gzkit/governance/trust_audits/cli.py` — `_known_cli_verb_paths`, `_verb_path_waived`, `_waiver_targets_live_verb`, `audit_skill_alignment`
- `tests/governance/test_promoted_advisory_audits.py` — enumeration + non-vacuous regression tests
- `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/**` — parent ADR package scope

## Denied Paths

- `_known_cli_verbs()` semantics (top-level) — MUST stay unchanged (coupled-surface coherence with `audit_cli_alignment`)
- `_NO_SKILL_VERBS` waiver entries for the 13 orphans (those belong to OBPI-02 — wire, don't waive)
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `audit_skill_alignment` MUST enumerate the full leaf-path surface (multi-word subcommands included) via `_known_cli_verb_paths()`.
1. REQUIREMENT: The audit MUST NOT be vacuously green — an unwielded, unwaived multi-word verb MUST produce exactly one `skill_alignment` error.
1. NEVER: introduce `_NO_SKILL_VERBS` entries for the 13 orphans here (no-waivers mandate; OBPI-02 wires them).
1. NEVER: alter `_known_cli_verbs()` (top-level) — `audit_cli_alignment` must remain byte-behaviorally identical.
1. ALWAYS: land after OBPI-02 + OBPI-03 (keystone ordering).

> STOP-on-BLOCKERS: if OBPI-02/03 have not landed, the audit will be RED; do not "fix" with waivers.

## Discovery Checklist

**Parent ADR (read first):**

- [ ] Parent ADR § Decision item (1) — quoted above
- [ ] Parent ADR § Intent — rule-as-enforced ⊊ rule-as-written framing

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-02 (wiring) and OBPI-03 (deletion) have landed — keystone ordering; otherwise the audit goes RED on the 13 orphans
- [ ] `src/gzkit/governance/trust_audits/cli.py` present with the recursion machinery from the in-flight investigation
- [ ] `tests/governance/test_promoted_advisory_audits.py` present and importable

**Existing Code (understand current state):**

- [ ] `src/gzkit/governance/trust_audits/cli.py:125-136` (`_known_cli_verbs`, top-level — the bug site)
- [ ] `cli.py:164-208` original `audit_skill_alignment`
- [ ] Working-tree implementation already present: `_known_cli_verb_paths`, `_verb_path_waived`, `_waiver_targets_live_verb`, rewritten `audit_skill_alignment`

## Quality Gates

### Gate 1: ADR
- [ ] Intent and scope recorded; parent ADR Decision item quoted

### Gate 2: TDD
- [ ] Tests derived from REQs; RED observed (enumeration absent / vacuous) → GREEN
- [ ] `uv run gz test`

### Code Quality
- [ ] `uv run gz lint`
- [ ] `uv run gz typecheck`

### Gate 3: Docs (Heavy)
- [ ] `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy)
- [ ] n/a — no new behave surface (validator-level change; unit-covered)

### Gate 5: Human (Heavy)
- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --skill-alignment
uv run gz validate --cli-alignment
uv run -m unittest discover -s tests -t . -p test_promoted_advisory_audits.py
uv run gz lint
uv run gz typecheck
```

## Demo

```bash
# Multi-word verbs are now enumerated and enforced (previously invisible):
uv run gz validate --skill-alignment
# -> green across the full 107-verb surface, zero waivers for the 13 orphans
```

## Acceptance Criteria

- [ ] REQ-0.0.67-01-01 [behavior]: Given the registered CLI tree, when `_known_cli_verb_paths()` runs, then it returns space-joined leaf paths recursing into nested subparsers — including `obpi complete`, `adr status`, and `obpi lock claim` — and `audit_skill_alignment` enforces against that set. (@covers test: `test_skill_alignment_enumerates_multiword_subcommands`)
- [ ] REQ-0.0.67-01-02 [behavior]: Given a registered multi-word verb with no wielding skill and no waiver/cascade, when `audit_skill_alignment` runs, then it returns exactly one `skill_alignment` error whose artifact is `gz <path>` (non-vacuous). (@covers test: new — temporarily drop one wiring/waiver via patch, assert the exact flag)
- [ ] REQ-0.0.67-01-03 [behavior]: Given `_NO_SKILL_VERBS` with top-level group keys, when `_verb_path_waived` evaluates a multi-word path, then a path is covered by an exact key OR by its top-level group key (cascade); and `_waiver_targets_live_verb` flags no currently-registered waiver as stale. (@covers test)
- [ ] REQ-0.0.67-01-04 [behavior]: Given the coupled `audit_cli_alignment` consumer, when this OBPI lands, then `_known_cli_verbs()` still returns top-level tokens only and `uv run gz validate --cli-alignment` stays green. (@covers test asserting top-level-only set)

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from REQs
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** documented below
- [ ] **Key Proof:** included below
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste unittest output (test_promoted_advisory_audits.py) here
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
# n/a — validator-level change, unit-covered
```

### Gate 5 (Human)
```text
# Record operator attestation text here
```

### Value Narrative

Before: `audit_skill_alignment` enumerated top-level verbs only — 32 multi-word
subcommands passed `gz validate --skill-alignment` by invisibility, not coverage.
Now: the audit enforces Invariant 1 across the full CLI surface; a new unwielded
multi-word verb fails the gate.

### Key Proof

`uv run gz validate --skill-alignment` green across all 107 verbs with zero
`_NO_SKILL_VERBS` entries for the 13 reclaimed orphans; the non-vacuous test
proves the audit fires when coverage is removed.

### Implementation Summary

- Files created/modified: `src/gzkit/governance/trust_audits/cli.py`, `tests/governance/test_promoted_advisory_audits.py`
- Tests added: enumeration test (present) + non-vacuous flag test + cascade/stale test + cli-alignment-unchanged guard
- Date completed:
- Attestation status:
- Defects noted: anchors GHI #588

## Tracked Defects

- GHI #588 — anchor (skill-alignment top-level-only scope)

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
