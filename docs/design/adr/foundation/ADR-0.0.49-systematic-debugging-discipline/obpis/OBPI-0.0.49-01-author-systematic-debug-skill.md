---
id: OBPI-0.0.49-01-author-systematic-debug-skill
parent: ADR-0.0.49-systematic-debugging-discipline
item: 1
lane: Heavy
status: Draft
allowlist:
- .gzkit/skills/
- .gzkit/skills/gz-systematic-debug/SKILL.md
- references/*.md
- docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/**
- src/gzkit/skills/gz-systematic-debug/
- .claude/skills/gz-systematic-debug/
- .github/skills/gz-systematic-debug/
- .gzkit/rules/skill-surface-sync.md
reqs:
- REQ-0.0.49-01-01
- REQ-0.0.49-01-02
- REQ-0.0.49-01-03
- REQ-0.0.49-01-04
- REQ-0.0.49-01-05
- REQ-0.0.49-01-06
verification:
- uv run gz agent sync control-surfaces
- uv run gz validate --documents
- uv run gz arb ruff
- uv run gz arb typecheck
- uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
---

# OBPI-0.0.49-01-author-systematic-debug-skill: Author `gz-systematic-debug` Skill

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/ADR-0.0.49-systematic-debugging-discipline.md`
- **Checklist Item:** #1 — "Author `gz-systematic-debug` skill at `.gzkit/skills/gz-systematic-debug/SKILL.md` (model: opus; lifecycle_state: active; no gz_command — methodology like gz-design). Includes Iron Law (precondition form, fenced block, same typography as gz-obpi-pipeline/gz-patch-release), four phases (Root Cause / Pattern / Hypothesis / Implementation), 3+-failed-fixes-architecture-pause rule, Red-Flags + Operator-Signals dictionaries, adapted supporting references (root-cause-tracing.md, defense-in-depth.md, condition-based-waiting.md translated to Python/gzkit vocabulary), ARB-receipt integration for Phase-1 evidence (uv run gz arb step --name root-cause-trace)."

**Status:** Draft

## Objective

Author the `gz-systematic-debug` skill as a methodology-class procedure of record for agents responding to bugs, test failures, or unexpected behavior. The skill MUST carry the precondition-form Iron Law, the four-phase procedure (Root Cause / Pattern / Hypothesis / Implementation), the 3+-failed-fixes-architecture-pause rule, two named dictionaries (Red Flags, Operator Signals), adapted supporting references translated to Python/gzkit vocabulary, and explicit ARB-step-receipt integration at Phase 1.

## Lane

**Heavy** — Adds a new canonical surface entry under `.gzkit/skills/` that binds agent behavior across every coding surface. Per `.gzkit/rules/skill-surface-sync.md`, new canonical skill content is a heavy-lane surface change. Foundation-kind parent ADR-0.0.49 triggers universal brief-level Gate 5 attestation per ADR-0.0.36 regardless of lane.

## Allowed Paths

- `.gzkit/skills/` — parent canonical-skills directory; OBPI creates `.gzkit/skills/gz-systematic-debug/SKILL.md` and three `references/*.md` files inside this directory (the new skill directory does not yet exist)
- `docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/**` — parent ADR package scope

**Implementation note:** wheel-shipping (`src/gzkit/skills/gz-systematic-debug/`) and vendor-mirror (`.claude/skills/gz-systematic-debug/`, `.github/skills/gz-systematic-debug/`) surfaces MUST be propagated only by `uv run gz agent sync control-surfaces` per `.gzkit/rules/skill-surface-sync.md`. The implementer never hand-edits any derived surface.

## Denied Paths

- `.gzkit/personas/**` — OBPI-02 scope
- `AGENTS.md`, `src/gzkit/templates/AGENTS.md` — OBPI-03 scope
- `.gzkit/skills/ghi-author/**`, `.gzkit/skills/ghi-close/**` — OBPI-04 scope
- `.gzkit/rules/**`, `docs/governance/advisory-rules-audit.md` — OBPI-05 scope
- `src/gzkit/skills/**`, `.claude/skills/**`, `.github/skills/**` — derived surfaces; written ONLY by `gz agent sync control-surfaces`
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `.gzkit/skills/gz-systematic-debug/SKILL.md` exists with valid YAML frontmatter containing `name: gz-systematic-debug`, `description:` (skill discovery summary), `lifecycle_state: active`, `model: opus` (per `.claude/rules/model-selection.md` routing matrix — judgment-class hypothesis formation), `owner: gzkit-governance`, `skill-version: "0.1.0"` (initial canonical version), and `last_reviewed: 2026-05-17`. The skill declares NO `gz_command:` field — this is methodology like `gz-design`, not CLI-backed.
2. REQUIREMENT: The skill body contains an `## Iron Law` section with a fenced-code-block opening line carrying the precondition-form Iron Law verbatim: `NO FIX MAY BE PROPOSED UNTIL ROOT-CAUSE EVIDENCE IS CAPTURED AS AN ARB STEP RECEIPT.` Typography matches the existing two Iron Laws (`.gzkit/skills/gz-obpi-pipeline/SKILL.md` § The Iron Law, `.gzkit/skills/gz-patch-release/SKILL.md` § The Iron Law): all-caps, single line inside ```` ``` ```` fence, no surrounding prose inside the fence.
3. REQUIREMENT: The skill body contains a `### Rationalization Prevention` table immediately following the Iron Law (same shape as the two existing Iron Law sections) with at least four "Thought / Reality" rows naming the pattern-matched-from-training-memory rationalizations (e.g. *"this looks like a one-line fix, no need for phase 1"* / *"phase 1 evidence capture is a real receipt, not a narrative claim"*).
4. REQUIREMENT: The skill body contains a `## Four Phases` section enumerating four H3 subsections in order: `### Phase 1 — Root Cause`, `### Phase 2 — Pattern`, `### Phase 3 — Hypothesis`, `### Phase 4 — Implementation`. Phase 1 instructions name three concrete trace artifacts the agent MUST capture (the failing assertion's actual vs expected output verbatim; the call-graph between the failure site and the nearest validated invariant; the data-flow trace from the input to the assertion) and the ARB step invocation: `uv run gz arb step --name root-cause-trace -- <trace command>`. Phase 4 names the fix-proposal commit-message trailer that MUST cite the `arb-step-root-cause-trace-*` receipt ID.
5. REQUIREMENT: The skill body contains a `## Phase 4.5 — Architecture Pause (3+ Failed Fixes)` section codifying the rule: after three failed fix attempts on the same defect, the failure class is wrong architecture, not the next patch — the agent STOPs the fix loop and routes to the operator as an architectural GHI (foundation-ADR candidate) via `/ghi-author`, citing the three prior `arb-step-*` receipts in the GHI body.
6. REQUIREMENT: The skill body contains a `## Red Flags` dictionary listing at least five named thought patterns that trigger Phase-1 reset (e.g. *"this looks easy, just patch it"*, *"the error message is probably wrong"*, *"this worked before, I'll just retry"*, *"the test is flaky, run it again"*, *"this is a known issue"*).
7. REQUIREMENT: The skill body contains a `## Operator Signals` dictionary listing at least four named operator phrases that trigger Phase-1 reset (e.g. operator says *"we've fixed this before"*, operator interjects *"why did you skip X"*, operator names a class-of-failure word like *"architecture"*, operator names a prior receipt ID).
8. REQUIREMENT: Three adapted supporting references exist at `.gzkit/skills/gz-systematic-debug/references/root-cause-tracing.md`, `.gzkit/skills/gz-systematic-debug/references/defense-in-depth.md`, and `.gzkit/skills/gz-systematic-debug/references/condition-based-waiting.md`. Each translates the superpowers-source technique to Python/gzkit-CLI vocabulary (no JavaScript/Node idioms; use `uv run`, `unittest`, `pathlib`, `subprocess.run([...], check=True)` examples).
9. REQUIREMENT: The skill's `description:` frontmatter is operator-facing and trigger-discovery oriented per the `.claude/rules/skill-surface-sync.md` skill-description convention: names the operator moment that triggers the skill (e.g. *"Diagnose a bug, test failure, or unexpected behavior using systematic root-cause discipline before proposing any fix"*).
10. REQUIREMENT: After authoring, `uv run gz agent sync control-surfaces` runs successfully and the skill appears in `src/gzkit/skills/gz-systematic-debug/SKILL.md` (wheel-shipping byte-parity copy) and `.claude/skills/gz-systematic-debug/SKILL.md` (vendor mirror). The implementer MUST NOT hand-edit either derived surface (per `.gzkit/rules/skill-surface-sync.md` non-negotiable rule #4 and #5).
11. REQUIREMENT: NEVER include the operator's personal email in the skill body, supporting references, or any example.
12. REQUIREMENT: Does NOT touch `.gzkit/personas/`, `AGENTS.md`, `.gzkit/skills/ghi-author/`, `.gzkit/skills/ghi-close/`, or `.gzkit/rules/systematic-debugging.md` — those edits land in OBPIs 02/03/04/05 respectively.

> STOP-on-BLOCKERS: if `.gzkit/skills/` does not exist or the parent ADR file is absent, print BLOCKERS and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 1 — quote verbatim** into the brief's Implementation Summary. Decision item 1 is the contract.
- [ ] Parent ADR § Intent — the why-frame for the skill's existence.
- [ ] Parent ADR § Why foundation tier? — the structural-witness rationale the skill operationalizes.

**Governance (read once, cache):**

- [ ] `.claude/rules/skill-surface-sync.md` — canonical surface editing invariants (edit `.gzkit/` first, bump skill-version, run sync; never edit mirrors)
- [ ] `.claude/rules/model-selection.md` — `model:` frontmatter declaration contract; routing matrix justifying `opus` for judgment-class hypothesis formation
- [ ] `.claude/rules/tool-skill-runbook-alignment.md` — three invariants (every tool has ≥1 wielding skill; skill `gz_command` aligns with runbook; output form matches Output Contract) — note Invariant 1 does not apply because this skill carries no `gz_command:`

**Context — existing Iron Law sources for typography match:**

- [ ] `.gzkit/skills/gz-obpi-pipeline/SKILL.md` § The Iron Law (lines 45–63) — completion-form Iron Law, fenced-block typography, Rationalization Prevention table
- [ ] `.gzkit/skills/gz-patch-release/SKILL.md` § The Iron Law (lines 81–99) — flow-form Iron Law, identical typography

**Context — existing methodology-class skill for shape match:**

- [ ] `.gzkit/skills/gz-design/SKILL.md` — methodology skill with no `gz_command:`, opus model, similar lifecycle posture

**Context — agent-failure-modes for upstream binding:**

- [ ] `.gzkit/rules/agent-failure-modes.md` § `Skipped cheap verification` row — the named failure class this skill closes structurally

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/skills/` directory present
- [ ] Parent ADR file present at `docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/ADR-0.0.49-systematic-debugging-discipline.md`
- [ ] `gz agent sync control-surfaces` is operational (`uv run gz agent sync control-surfaces --help` exits 0)

**Existing Code (understand current state):**

- [ ] No existing `.gzkit/skills/gz-systematic-debug/` directory (the OBPI is creating it)
- [ ] Existing skill catalog in AGENTS.md § Skills — the new skill will be added there by OBPI-03, not here

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item #1 quoted in Implementation Summary

### Gate 2: TDD

- [ ] Skill body is content; `gz validate --documents` clean run is the structural floor
- [ ] `uv run gz agent sync control-surfaces` exits 0 with the new skill propagated to all derived surfaces
- [ ] No regression in `uv run -m unittest -q`

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] No BDD scenario applies — methodology skill is content, not behavior; per gate covenant § Lane Rules, BDD scope is for external-contract change, not content-only skill authoring. Waiver noted; future GHI promotion to `gz validate --systematic-debug-coupling` (OBPI-05 forward reference) will land BDD scenarios.

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion

## Verification

```bash
test -f .gzkit/skills/gz-systematic-debug/SKILL.md
test -f .gzkit/skills/gz-systematic-debug/references/root-cause-tracing.md
test -f .gzkit/skills/gz-systematic-debug/references/defense-in-depth.md
test -f .gzkit/skills/gz-systematic-debug/references/condition-based-waiting.md
grep -q "^NO FIX MAY BE PROPOSED UNTIL ROOT-CAUSE EVIDENCE IS CAPTURED AS AN ARB STEP RECEIPT" .gzkit/skills/gz-systematic-debug/SKILL.md
grep -q "^model: opus$" .gzkit/skills/gz-systematic-debug/SKILL.md
uv run gz agent sync control-surfaces
test -f src/gzkit/skills/gz-systematic-debug/SKILL.md
test -f .claude/skills/gz-systematic-debug/SKILL.md
uv run gz validate --documents
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# After implementation, list the new skill from the discovery surface:
uv run gz skill list | grep gz-systematic-debug
# Read the SKILL.md to confirm Iron Law typography matches gz-obpi-pipeline:
diff <(grep -A 1 '^```$' .gzkit/skills/gz-systematic-debug/SKILL.md | head -3) \
     <(grep -A 1 '^```$' .gzkit/skills/gz-obpi-pipeline/SKILL.md | head -3) \
     || echo "Iron Law fenced-block shape differs — verify typography"
```

## Acceptance Criteria

- [ ] REQ-0.0.49-01-01: Given the parent ADR § Decision item 1, when this OBPI completes, then `.gzkit/skills/gz-systematic-debug/SKILL.md` exists with `model: opus`, `lifecycle_state: active`, no `gz_command:`, and contains the precondition-form Iron Law fenced-block verbatim.
- [ ] REQ-0.0.49-01-02: Given the four-phase requirement (REQ #4), when the skill body is read, then four H3 subsections appear in order (Root Cause / Pattern / Hypothesis / Implementation), Phase 1 names three concrete trace artifacts and the `uv run gz arb step --name root-cause-trace` invocation, and Phase 4 names the commit-message trailer citing the `arb-step-root-cause-trace-*` receipt ID.
- [ ] REQ-0.0.49-01-03: Given the 3+-failed-fixes-architecture-pause requirement (REQ #5), when the skill body is read, then a `## Phase 4.5 — Architecture Pause (3+ Failed Fixes)` section exists routing to `/ghi-author` for an architectural GHI labeled as a foundation-ADR candidate, citing the three prior `arb-step-*` receipts.
- [ ] REQ-0.0.49-01-04: Given the two named dictionaries (REQs #6/#7), when the skill body is read, then a `## Red Flags` section lists ≥5 thought patterns and a `## Operator Signals` section lists ≥4 operator phrases.
- [ ] REQ-0.0.49-01-05: Given the supporting-references requirement (REQ #8), when the references directory is enumerated, then exactly three files exist (`root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md`), each translated to Python/gzkit-CLI vocabulary.
- [ ] REQ-0.0.49-01-06: Given the sync requirement (REQ #10), when `uv run gz agent sync control-surfaces` runs, then the new skill is byte-parity-propagated to `src/gzkit/skills/gz-systematic-debug/SKILL.md` and `.claude/skills/gz-systematic-debug/SKILL.md` without manual edits to derived surfaces.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief; parent ADR Decision item 1 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** `gz validate --documents` clean, sync exits 0, unittest regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (Skipped cheap verification failure shape unmechanized) vs capability-now (precondition-form Iron Law with ARB step receipt structural witness)
- [ ] **Key Proof:** Iron Law typography matches existing two skills (diff command)
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste validate --documents output here
```

### Code Quality

```text
# Paste lint + typecheck + mkdocs output here with ARB receipt IDs
```

### Gate 5 (Human)

```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

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
