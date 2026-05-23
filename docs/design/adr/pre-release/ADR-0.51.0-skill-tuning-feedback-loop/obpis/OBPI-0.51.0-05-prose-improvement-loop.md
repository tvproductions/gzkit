---
id: OBPI-0.51.0-05-prose-improvement-loop
parent: ADR-0.51.0-skill-tuning-feedback-loop
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.51.0-05-prose-improvement-loop: **prose-improvement-loop** — Add the evaluator prose-improvement suggestion step: after rubric scoring the evaluator suggests specific skill prose improvements; human gate and attestation closes the loop.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/ADR-0.51.0-skill-tuning-feedback-loop.md`
- **Checklist Item:** #5 - "OBPI-0.51.0-05: **prose-improvement-loop** — Add the evaluator prose-improvement suggestion step: after rubric scoring the evaluator suggests specific skill prose improvements; human gate and attestation closes the loop."

**Status:** Draft

## Objective

**prose-improvement-loop** — Add the evaluator prose-improvement suggestion step: after rubric scoring the evaluator suggests specific skill prose improvements; human gate and attestation closes the loop.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/skills_tuning/prose_improvement.py` — module: evaluator's prose-improvement suggestion emitter; produces structured `ProseImprovementSuggestion` records (Pydantic, frozen, `extra="forbid"`) with `target_line: int`, `current_text: str`, `proposed_text: str`, `rationale_anchor: EvidenceRef` (cites the basket goal that prompted the change)
- `src/gzkit/skills_tuning/human_gate.py` — module: human-gate enforcement that an accepted prose improvement requires explicit operator attestation text before any SKILL.md mutation is permitted; fail-closed when attestation is empty/missing
- `src/gzkit/chores/skill-tuning-optimize/CHORE.md` — append the "Step N — Prose improvement loop" section (canonical edit; sync regenerates package mirror); links to OBPI-04 trim-and-verify run output as the prose-improvement loop's input
- `tests/test_prose_improvement_loop.py` — REQ-derived tests covering suggestion shape, human-gate fail-closed behavior, attestation acceptance text, and integration with OBPI-04's report artifact
- `tests/fixtures/prose_improvement_loop/` — fixture suggestion records: well-formed, malformed (missing attestation), and missing-rationale cases
- `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/obpis/OBPI-0.51.0-05-prose-improvement-loop.md` — this brief (evidence updates only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/skills_tuning/episode.py`, `src/gzkit/skills_tuning/rubric.py`, `src/gzkit/skills_tuning/evaluator_protocol.py` — episode/rubric/evaluator are OBPI-0.51.0-01's surface (this OBPI imports them, does not edit)
- `src/gzkit/core/models.py` — `SkillFrontmatter.optimize` block is OBPI-0.51.0-03's surface
- `.gzkit/chores/skill-authoring-quality/**`, `.gzkit/chores/skill-trigger-testing/**` — hard-basket extensions are OBPI-0.51.0-02's surface
- `src/gzkit/chores/skill-tuning-optimize/trim_and_verify.py`, `recalibrate_verify.py`, `report.py` — run-mode implementations are OBPI-0.51.0-04's surface (this OBPI extends CHORE.md, not the run-mode modules)
- `.gzkit/skills/**/SKILL.md` write paths from this OBPI's runtime — the human-gate module GATES the write; actual mutation happens only when attestation is present and bound to the suggestion
- `docs/user/manpages/**`, `docs/user/runbook.md` — docs/runbook updates are OBPI-0.51.0-06's surface
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `ProseImprovementSuggestion` MUST be a frozen Pydantic `BaseModel` with `extra="forbid"` exposing at minimum: `target_line: int`, `current_text: str`, `proposed_text: str`, `rationale_anchor: EvidenceRef` (`Field(min_length=...)` enforced where applicable so anchor cannot be empty).
2. REQUIREMENT: A suggestion MUST carry a `rationale_anchor` citing the hard-basket goal (OBPI-02) that prompted the suggestion — every prose change traces back to an observed failure.
3. REQUIREMENT: The human-gate module MUST fail-closed when the operator's attestation text is empty, whitespace-only, or missing; only an explicit substantive attestation may unlock the SKILL.md mutation step.
4. REQUIREMENT: The human-gate module MUST encode the Universal OBPI Attestation pattern (ADR-0.0.36) — operator name + verbatim attestation passed through unchanged; agent appends concrete enrichment grounded in the suggestion evidence.
5. REQUIREMENT: The CHORE.md "Step N — Prose improvement loop" section MUST cite OBPI-04 trim-and-verify report artifact as its mandatory input; no orphaned prose-improvement runs.
6. NEVER: Mutate any `.gzkit/skills/**/SKILL.md` from runtime code in this OBPI — the human-gate module governs the boundary; mutation paths exist but are gated.
7. NEVER: Accept a prose-improvement suggestion whose `rationale_anchor` is empty — fail-closed (no unanchored prose changes).
8. ALWAYS: Render any relative path in `rationale_anchor` via `.as_posix()` per `.claude/rules/cross-platform.md`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.


## Creates these files

<!-- Net-new files this OBPI creates. Path existence is exempt for these entries per GHI #419. -->

- `src/gzkit/skills_tuning/prose_improvement.py` **CREATE**
- `src/gzkit/skills_tuning/human_gate.py` **CREATE**
- `src/gzkit/chores/skill-tuning-optimize/CHORE.md` **CREATE**
- `tests/test_prose_improvement_loop.py` **CREATE**
- `tests/fixtures/prose_improvement_loop/` **CREATE**

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/ADR-0.51.0-skill-tuning-feedback-loop.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/ADR-0.51.0-skill-tuning-feedback-loop.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/**`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below. -->

```bash
uv run gz validate --documents
uv run gz validate --surfaces
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_prose_improvement_loop

# OBPI-specific surface checks
test -f src/gzkit/skills_tuning/prose_improvement.py
test -f src/gzkit/skills_tuning/human_gate.py
grep -q "Prose improvement loop" .gzkit/chores/skill-tuning-optimize/CHORE.md
uv run python -c "from gzkit.skills_tuning.prose_improvement import ProseImprovementSuggestion; print(ProseImprovementSuggestion.model_fields)"
uv run python -c "from gzkit.skills_tuning.human_gate import enforce_attestation_present; enforce_attestation_present('') # raises"
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Construct a well-formed prose improvement suggestion from a fixture
uv run python -c "
from gzkit.skills_tuning.prose_improvement import ProseImprovementSuggestion
import json
data = json.load(open('tests/fixtures/prose_improvement_loop/well_formed.json'))
s = ProseImprovementSuggestion.model_validate(data)
print(s.model_dump_json(indent=2))
"

# Demonstrate human-gate fail-closed on empty attestation
uv run python -c "
from gzkit.skills_tuning.human_gate import enforce_attestation_present
try:
    enforce_attestation_present('')
except Exception as e:
    print(f'Gate blocked empty attestation: {e}')
"

# Demonstrate fail-closed on missing rationale_anchor
uv run python -c "
from gzkit.skills_tuning.prose_improvement import ProseImprovementSuggestion
try:
    ProseImprovementSuggestion(target_line=10, current_text='x', proposed_text='y', rationale_anchor=None)
except Exception as e:
    print(f'Rejected unanchored suggestion: {e}')
"
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.51.0-05-01: Given `ProseImprovementSuggestion`, when constructed with all fields including a non-empty `rationale_anchor`, then construction succeeds; given an empty/None `rationale_anchor`, then `ValidationError` is raised.
- [ ] REQ-0.51.0-05-02: Given `enforce_attestation_present` is called with `""`, whitespace-only, or `None`, then a fail-closed error is raised; given a substantive attestation string, then it returns the normalized attestation.
- [ ] REQ-0.51.0-05-03: Given the human-gate module is the only path that mutates `.gzkit/skills/**/SKILL.md`, when grep'd through the OBPI's modules, then no other code path writes to SKILL.md files (boundary invariant).
- [ ] REQ-0.51.0-05-04: Given a prose improvement suggestion, when extra fields are passed, then `extra="forbid"` raises `ValidationError`.
- [ ] REQ-0.51.0-05-05: Given the CHORE.md update, when grep'd, then it includes a "Step N — Prose improvement loop" section that cites the OBPI-0.51.0-04 trim-and-verify report artifact as its mandatory input.
- [ ] REQ-0.51.0-05-06: Given the human-gate enforces attestation, when the attestation text is recorded, then it follows the Universal OBPI Attestation pattern (operator's verbatim words passed through; agent appends concrete enrichment) per ADR-0.0.36.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
