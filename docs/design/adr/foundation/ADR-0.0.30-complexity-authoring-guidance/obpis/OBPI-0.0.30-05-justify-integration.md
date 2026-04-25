---
id: OBPI-0.0.30-05-justify-integration
parent: ADR-0.0.30
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.30-05-justify-integration: gz justify Integration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/ADR-0.0.30-complexity-authoring-guidance.md`
- **Checklist Item:** #5 — "`gz justify` integration (amend `.gzkit/skills/gz-justify/SKILL.md` so authoring-guidance hints for an OBPI's .py allowed-paths surface in the justification scaffold's evidence section)"

**Status:** Draft

## Objective

Amend the existing `gz-justify` skill (ADR-0.0.19) so that when an operator runs `gz justify` for an OBPI whose `Allowed Paths` include `.py` files, the authoring-guidance hints for those files surface in the justification scaffold's evidence section. This closes the ADR-0.0.19 ↔ ADR-0.0.30 forward reference at brief level. The amendment is additive — the existing reasoning-walkthrough structure is preserved.

## Lane

**Heavy** — Skill amendment + extension to `gz justify` rendering pipeline = two contract-touching changes. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `.gzkit/skills/gz-justify/SKILL.md` — additive amendment only (existing structure preserved)
- `.claude/skills/gz-justify/`, `.agents/skills/gz-justify/`, `.github/skills/gz-justify/` — vendor mirrors via `gz agent sync control-surfaces`
- `src/gzkit/commands/justify.py` (or wherever the justify rendering lives) — extend rendering pipeline to invoke OBPI-03's authoring engine for `.py` allowed-paths
- `tests/commands/test_justify_authoring_hints.py`, `tests/skills/test_gz_justify_complexity_amendment.py`
- `features/justify_complexity_hints.feature` — behave scenarios tagged with REQ IDs
- `docs/user/runbook.md` — entry under "Complexity doctrine surfaces" describing the integration
- `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/obpis/OBPI-0.0.30-05-justify-integration.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/complexity/authoring/**` — engine/protocol/hint are OBPI-03/04 (consumed, not edited)
- `src/gzkit/commands/complexity_guide.py` — CLI is OBPI-01
- `.gzkit/skills/complexity-guide/**` — skill is OBPI-02
- `src/gzkit/justify/reasoning_structure.py` (or equivalent) — the existing reasoning-walkthrough structure is NOT redesigned
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The amendment to `.gzkit/skills/gz-justify/SKILL.md` is additive: a new section names the complexity-hints integration; the existing skill body, frontmatter (other than `skill-version` bump), and operator workflow are preserved unchanged. The skill-version marker bumps per `.gzkit/rules/skill-surface-sync.md` (e.g. `0.5.0` → `0.6.0`).
2. REQUIREMENT: The `gz justify` rendering pipeline detects when the active OBPI's `Allowed Paths` include `.py` glob patterns and, if so, invokes `engine.analyze(path)` from OBPI-03 against each matching path. Hints are injected into the justification scaffold's evidence section under a new sub-heading `### Authoring-time complexity hints`.
3. REQUIREMENT: When no `.py` paths are in scope OR no advise-band crossings are found, the authoring-time complexity hints sub-heading is NOT injected (silent absence, not empty section).
4. REQUIREMENT: The hints rendering shows: per-hint metric + precedence band + archetype + doctrinal-frame headline + recommended-move headline + file:line range. Format consistent with OBPI-01's CLI default human-readable form for visual coherence.
5. REQUIREMENT: The integration uses the OBPI-03 `engine.analyze` interface directly (Python import, not subprocess shellout); the integration is in-process for performance and to avoid subprocess fragility.
6. REQUIREMENT: A failure in the authoring engine (e.g. OBPI-0.0.27-04 distilled-characteristics document missing) MUST NOT block `gz justify`; the integration fails open, omits the complexity-hints sub-heading, and logs a warning to `.gzkit/insights/justify-failures.jsonl` (re-using the failure-log shape from OBPI-0.0.29-09 if compatible; otherwise the integration defines its own log shape with the same envelope).
7. REQUIREMENT: Tests cover: justify on an OBPI with `.py` allowed-paths and advise-band crossings injects the hints sub-heading; justify on an OBPI with no `.py` paths skips the sub-heading; justify on an OBPI with `.py` paths but no crossings skips the sub-heading; engine failure fails open with logged warning; skill amendment adds the new section without modifying existing content; vendor mirrors are byte-identical after sync. Each test decorated with `@covers(REQ-0.0.30-05-NN)`.
8. REQUIREMENT: A behave scenario at `features/justify_complexity_hints.feature` tagged `@REQ-0.0.30-05-{01,02,03}` covers: justify with hints; justify without hints (no .py paths); justify-engine-failure fail-open path.
9. REQUIREMENT: Runbook entry under "Complexity doctrine surfaces" describes the integration: when it fires, where the hints land in the justification scaffold, and the fail-open behavior.
10. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures simulate ADR + OBPI + brief structure for justify invocation.
11. REQUIREMENT: NEVER include the operator's personal email in skill body, code, fixtures, runbook, or commit messages.

> STOP-on-BLOCKERS: if OBPI-03's `engine.analyze` interface is not landed, OR if the existing `gz justify` skill's frontmatter / structure has changed since this OBPI was authored, STOP and reconcile.

## Discovery Checklist

- [ ] OBPI-03 engine + `AuthoringHint`
- [ ] Existing `.gzkit/skills/gz-justify/SKILL.md` — current frontmatter and body
- [ ] `src/gzkit/commands/justify.py` (or equivalent) — current rendering pipeline
- [ ] ADR-0.0.19 — pre-execution reasoning walkthrough doctrine (parent of `gz justify`)
- [ ] OBPI-0.0.29-09 failure-log envelope (re-used or sister-shape)
- [ ] `.gzkit/rules/skill-surface-sync.md` — skill-version bump discipline

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Runbook entry

### Gate 4: BDD (Heavy)
- [ ] Behave scenarios cover three canonical paths

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz validate --documents --surfaces
uv run gz agent sync control-surfaces  # post-sync diff empty
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_justify_authoring_hints.py tests/skills/test_gz_justify_complexity_amendment.py -v
uv run -m behave features/justify_complexity_hints.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.30-05-01: Given an OBPI with `.py` allowed-paths and advise-band crossings, when `gz justify` runs, then the justification scaffold's evidence section contains the `### Authoring-time complexity hints` sub-heading with one block per hint.
- [ ] REQ-0.0.30-05-02: Given an OBPI with no `.py` allowed-paths, when `gz justify` runs, then the complexity-hints sub-heading is absent (silent skip).
- [ ] REQ-0.0.30-05-03: Given an OBPI with `.py` paths but no advise-band crossings, when `gz justify` runs, then the complexity-hints sub-heading is absent.
- [ ] REQ-0.0.30-05-04: Given the OBPI-03 engine raises (e.g. distilled-characteristics document missing), when `gz justify` runs, then it completes successfully with the complexity-hints sub-heading omitted and a warning logged.
- [ ] REQ-0.0.30-05-05: Given the amended `gz-justify` skill, when frontmatter is parsed, then `skill-version` has been bumped and the existing structure (other than the new section) is preserved verbatim.
- [ ] REQ-0.0.30-05-06: Given a clean working tree, when `uv run gz agent sync control-surfaces` runs, then the three vendor mirrors of `gz-justify` are byte-identical.

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
# Paste behave output
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
