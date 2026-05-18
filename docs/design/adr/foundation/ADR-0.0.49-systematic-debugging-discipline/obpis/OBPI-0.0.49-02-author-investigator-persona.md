---
id: OBPI-0.0.49-02-author-investigator-persona
parent: ADR-0.0.49-systematic-debugging-discipline
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.49-02-author-investigator-persona: Author `investigator` Persona

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/ADR-0.0.49-systematic-debugging-discipline.md`
- **Checklist Item:** #2 — "Author `investigator` persona at `.gzkit/personas/investigator.md` with traits (evidence-first, hypothesis-discipline, fix-impulse-suspending, architecture-questioning), anti-traits (patch-first-instinct, single-hypothesis-fixation, symptom-fixation, narrative-recall-substitution-for-evidence), and grounding paragraph naming the refusal-to-propose-fix-without-evidence behavior. Dispatchable as subagent peer to existing implementer/spec-reviewer/quality-reviewer triad under ADR-0.18.0."

**Status:** Draft

## Objective

Author the `investigator` persona as a dispatchable subagent peer to the existing implementer/spec-reviewer/quality-reviewer triad. The persona's behavioral identity refuses to propose any fix until root-cause evidence is captured as an ARB step receipt; refuses to bundle a fourth fix attempt past the 3+-failed-fixes-architecture-pause signal.

## Lane

**Heavy** — Adds a new canonical surface entry under `.gzkit/personas/` that binds subagent-dispatch behavior. New persona is a dispatch-surface contract change per ADR-0.0.11 / ADR-0.0.12; foundation-kind parent triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `.gzkit/personas/` — parent canonical-personas directory; OBPI creates `.gzkit/personas/investigator.md` here (the new persona file does not yet exist)
- `docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/**` — parent ADR package scope

**Implementation note:** wheel-shipping (`src/gzkit/personas/investigator.md`) and vendor-mirror (`.claude/personas/investigator.md`, `.agents/personas/investigator.md`, `.github/personas/investigator.md`) surfaces MUST be propagated only by `uv run gz agent sync control-surfaces` per `.gzkit/rules/skill-surface-sync.md`. The implementer never hand-edits any derived surface.

## Denied Paths

- `.gzkit/skills/**` — OBPI-01 and OBPI-04 scopes
- `AGENTS.md`, `src/gzkit/templates/AGENTS.md` — OBPI-03 scope (persona table row added there)
- `.gzkit/rules/**`, `docs/governance/advisory-rules-audit.md` — OBPI-05 scope
- `src/gzkit/personas/**`, `.claude/personas/**`, `.agents/personas/**`, `.github/personas/**` — derived surfaces; written ONLY by `gz agent sync control-surfaces`
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `.gzkit/personas/investigator.md` exists with valid YAML frontmatter containing `name: investigator`, `traits:` array of exactly four traits (in this order): `evidence-first`, `hypothesis-discipline`, `fix-impulse-suspending`, `architecture-questioning`, and `anti-traits:` array of exactly four anti-traits (in this order): `patch-first-instinct`, `single-hypothesis-fixation`, `symptom-fixation`, `narrative-recall-substitution-for-evidence`.
2. REQUIREMENT: Frontmatter includes a `grounding:` field with a multi-sentence paragraph naming the persona's behavioral identity: the agent refuses to propose a fix until root-cause evidence is captured as an ARB step receipt; treats the 3+-failed-fixes-architecture-pause as a structural signal, not a judgment call; treats every commit-message receipt-ID citation as the structural witness for the work, not narrative recall. The grounding paragraph MUST match the tone and shape of existing personas (compare `.gzkit/personas/quality-reviewer.md`, `.gzkit/personas/spec-reviewer.md`, `.gzkit/personas/main-session.md`).
3. REQUIREMENT: The persona body contains a `## Behavioral Anchors` section with one H3 subsection per trait (four total), each explaining the trait in 2–4 sentences using gzkit doctrine vocabulary (ARB receipts, structural witness, foundation invariant, Iron Law, GHI lifecycle). Tone matches the four-anchor pattern in `.gzkit/personas/quality-reviewer.md` § Behavioral Anchors.
4. REQUIREMENT: The persona body contains an `## Anti-patterns` section with one bullet per anti-trait (four total), each naming the failure mode the anti-trait prevents (e.g. `patch-first-instinct`: producing a fix proposal from training-corpus pattern-matching without running `uv run gz arb step --name root-cause-trace` first).
5. REQUIREMENT: The persona body contains a `## Register` section (parallel to `.gzkit/personas/quality-reviewer.md` § Register) describing how the investigator frames findings: leads with the root-cause finding (not the fix); cites the `arb-step-root-cause-trace-*` receipt ID before any recommendation; distinguishes Phase-1 evidence from Phase-3 hypothesis; never substitutes narrative recall for receipt-cited evidence.
6. REQUIREMENT: After authoring, `uv run gz agent sync control-surfaces` runs successfully and the persona appears in `src/gzkit/personas/investigator.md` (wheel-shipping copy) and `.claude/personas/investigator.md`, `.agents/personas/investigator.md`, `.github/personas/investigator.md` (vendor mirrors). The implementer MUST NOT hand-edit any derived surface.
7. REQUIREMENT: `uv run gz personas list` shows the new persona as the seventh entry (in addition to the existing six: `implementer`, `main-session`, `narrator`, `pipeline-orchestrator`, `quality-reviewer`, `spec-reviewer`).
8. REQUIREMENT: NEVER include the operator's personal email in the persona body or grounding paragraph.
9. REQUIREMENT: Does NOT modify the persona row table in AGENTS.md — that edit lands in OBPI-03.
10. REQUIREMENT: Does NOT touch any skill file, rule file, or scorecard entry — those land in sibling OBPIs.

> STOP-on-BLOCKERS: if `.gzkit/personas/` does not exist or the parent ADR file is absent, print BLOCKERS and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 2 — quote verbatim** into the brief's Implementation Summary.
- [ ] Parent ADR § Persona — the parent persona's framing of the investigator as a dispatchable peer.

**Governance (read once, cache):**

- [ ] `.claude/rules/skill-surface-sync.md` — canonical surface editing invariants apply to personas as well (no `skill-version:` on personas; classifier rules per the canonical-vs-package_only-vs-runtime_state table)
- [ ] ADR-0.0.11-persona-driven-agent-identity-frames — persona-doctrine source
- [ ] ADR-0.0.12-agent-role-persona-profiles — agent-role × persona contract
- [ ] ADR-0.18.0-subagent-driven-pipeline-execution — the dispatch model the new persona slots into as a seventh peer

**Context — existing personas for shape and tone match:**

- [ ] `.gzkit/personas/main-session.md` — primary operator-session persona, four-trait shape, grounding paragraph form
- [ ] `.gzkit/personas/quality-reviewer.md` — review subagent persona with `## Register` section, anti-traits enumeration
- [ ] `.gzkit/personas/spec-reviewer.md` — review subagent persona, independent-judgment posture (closest sibling tone to investigator)
- [ ] `.gzkit/personas/implementer.md` — implementation subagent, methodical/test-first/complete-units traits

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/personas/` directory present (six existing personas)
- [ ] Parent ADR file present at `docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/ADR-0.0.49-systematic-debugging-discipline.md`
- [ ] `uv run gz personas list` exits 0 and lists six personas

**Existing Code (understand current state):**

- [ ] No existing `.gzkit/personas/investigator.md` file (the OBPI is creating it)
- [ ] Persona schema in `src/gzkit/personas.py` (or equivalent) — check what frontmatter keys are required/validated

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item #2 quoted in Implementation Summary

### Gate 2: TDD

- [ ] Persona body is content; `gz validate --documents` clean run is the structural floor
- [ ] `uv run gz agent sync control-surfaces` exits 0 with the new persona propagated to all derived surfaces
- [ ] No regression in `uv run -m unittest -q`

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] No BDD scenario applies — persona is dispatch-surface content, not external behavior contract; waiver noted.

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion

## Verification

```bash
test -f .gzkit/personas/investigator.md
grep -q "^name: investigator$" .gzkit/personas/investigator.md
grep -qE "^  - evidence-first$" .gzkit/personas/investigator.md
grep -qE "^  - patch-first-instinct$" .gzkit/personas/investigator.md
uv run gz agent sync control-surfaces
test -f src/gzkit/personas/investigator.md
test -f .claude/personas/investigator.md
uv run gz personas list | grep -q '^investigator'
uv run gz validate --documents
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# After implementation, list personas — investigator appears as the seventh:
uv run gz personas list
# Read the persona file to confirm shape:
cat .gzkit/personas/investigator.md | head -40
```

## Acceptance Criteria

- [ ] REQ-0.0.49-02-01: Given the parent ADR § Decision item 2, when this OBPI completes, then `.gzkit/personas/investigator.md` exists with four traits and four anti-traits in the prescribed order.
- [ ] REQ-0.0.49-02-02: Given the grounding requirement (REQ #2), when the frontmatter is parsed, then the `grounding:` field is a multi-sentence paragraph naming the refusal-to-propose-fix-without-evidence identity and the 3+-failed-fixes-architecture-pause as structural signal.
- [ ] REQ-0.0.49-02-03: Given the body-section requirements (REQs #3/#4/#5), when the persona body is read, then `## Behavioral Anchors` (4 H3 subsections), `## Anti-patterns` (4 bullets), and `## Register` sections are present and match the tone of `.gzkit/personas/quality-reviewer.md`.
- [ ] REQ-0.0.49-02-04: Given the sync requirement (REQ #6), when `uv run gz agent sync control-surfaces` runs, then the new persona is byte-parity-propagated to `src/gzkit/personas/investigator.md` and the three vendor mirrors.
- [ ] REQ-0.0.49-02-05: Given the discovery requirement (REQ #7), when `uv run gz personas list` runs, then `investigator` appears as the seventh persona entry.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 2 quoted
- [ ] **Gate 2 (TDD):** `gz validate --documents` clean, sync exits 0, unittest regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (no dispatch-time behavioral anchor for systematic-debug investigation) vs capability-now (seventh persona with explicit refusal-to-propose-fix-without-evidence identity)
- [ ] **Key Proof:** `uv run gz personas list` shows the new persona
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
