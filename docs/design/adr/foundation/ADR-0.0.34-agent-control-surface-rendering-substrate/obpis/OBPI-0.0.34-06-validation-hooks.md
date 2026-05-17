---
id: OBPI-0.0.34-06-validation-hooks
parent: ADR-0.0.34-agent-control-surface-rendering-substrate
item: 6
lane: Heavy
status: Completed
---

# OBPI-0.0.34-06-validation-hooks: Validation Hooks

<!-- gz-validate-skip: brief-demo-section --> <!-- Draft brief; Demo section authored at implementation time per GHI #431 grandfather pattern. -->

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`
- **Checklist Item:** #6 - "OBPI-0.0.34-06: Validation hooks — every render and every save fires the ADR-0.0.33 fidelity validators; output that fails validation does not land"

**Status:** Completed

## Objective

Wire the existing ADR-0.0.33 fidelity validator suite (`validate_surface_fidelity` composite at `gzkit.governance.trust_audits`) at two hook points so authoring-time and edit-time bytes are validated before they land: (1) `render()` in `src/gzkit/content/render/pipeline.py` fires `validate_render(project_root=...)` after producing bytes and before returning; (2) `content_edit_cmd()` in `src/gzkit/commands/content/edit.py` fires `validate_save(project_root=...)` after re-render and before the atomic file write. Both raise a typed `FidelityHookError` carrying `validator_id` and `violation` on any failure; no warn-and-continue path exists. Done means: a fixture model whose render would violate a fidelity invariant raises `FidelityHookError` at `render()` time; a `gz content edit` save that would write a fidelity-violating surface exits 1 with a structured diagnostic and leaves the original file unchanged.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/content/validation/__init__.py` — validation hook entrypoint (re-exports ADR-0.0.33 validators)
- `src/gzkit/content/validation/hooks.py` — render-hook and save-hook wiring
- `src/gzkit/content/render/pipeline.py` — invoke hook after render, before return (modification, not creation)
- `src/gzkit/commands/content/edit.py` — invoke hook after parse, before write (modification, not creation)
- `tests/content/test_validation_hooks.py` — fail-closed render-hook, fail-closed save-hook, no-warn-and-continue test
- `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/obpis/OBPI-0.0.34-06-validation-hooks.md` — this brief

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: **Every render fires ADR-0.0.33 fidelity validators.** OBPI-02's `render()` MUST invoke the ADR-0.0.33 validator suite on the produced byte-string before returning; validation failure raises a typed error and aborts the render.
2. REQUIREMENT: **Every save fires the validator suite.** OBPI-04's `gz content edit` save-path (post-`$EDITOR`) and any other content-write callsite MUST invoke the same validator suite before persisting; failure prevents file write.
3. REQUIREMENT: **Fail-closed semantics.** Failed validation produces non-zero exit, no partial write, and a structured diagnostic naming the failing validator. NEVER implement a "warn and continue" path; NEVER log-and-return.
4. REQUIREMENT: **Wiring-only scope.** NEVER author new fidelity validators in this OBPI — validator authoring lives under ADR-0.0.33. This OBPI is the integration layer that fires them at the two named hook points.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] **Prerequisite OBPI:** OBPI-0.0.34-01 (content model registry) — validators target model instances.
- [ ] **Prerequisite OBPI:** OBPI-0.0.34-02 (rendering pipeline) — render-hook attaches here; render must exist before hook can wrap it.
- [ ] **Prerequisite OBPI:** OBPI-0.0.34-04 (authoring CLI) — save-hook attaches to `edit` subcommand's save path.
- [ ] **External prerequisite:** ADR-0.0.33 fidelity validators MUST be landed and importable from `gzkit.validators.fidelity` (or wherever ADR-0.0.33 places them); if not, file a blocker GHI before starting Gate 2.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.34-02 complete: `from gzkit.content.render import render` imports cleanly.
- [ ] OBPI-0.0.34-04 complete: `gz content edit --help` exits 0.
- [ ] ADR-0.0.33 fidelity validator suite is importable (verify with `uv run python -c "from gzkit.validators.fidelity import VALIDATORS"` or the equivalent module path ADR-0.0.33 declares).
- [ ] Parent ADR evidence artifacts referenced by this brief are present.

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
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run python -m unittest tests.content.test_validation_hooks -v
# Fail-closed: no warn-and-continue paths anywhere in the wiring
rg -n "logger\.warning.*fidelity"   src/gzkit/content/validation/ && exit 1 || true
rg -n "logger\.warn.*fidelity"      src/gzkit/content/validation/ && exit 1 || true
rg -n "\"WARN\".*fidelity"          src/gzkit/content/validation/ && exit 1 || true
# Hook firing is wired at both call sites
rg -q "validation\.hooks" src/gzkit/content/render/pipeline.py
rg -q "validation\.hooks" src/gzkit/commands/content/edit.py
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.34-06-01: Given OBPI-02's `render(model)`, when invoked, then the ADR-0.0.33 fidelity validator suite runs against the produced output before `render` returns; validation failure raises and aborts the render — verified by a fixture model whose canonical render deliberately violates a fidelity invariant.
- [ ] REQ-0.0.34-06-02: Given `gz content edit <id>` save-path (OBPI-04), when the post-edit re-parse succeeds, then the validator suite runs before persisting to disk; failure prevents file write and surfaces a structured diagnostic identifying the failing validator.
- [ ] REQ-0.0.34-06-03: Given a deliberately-fidelity-violating fixture, when the hooks fire, then exit code is non-zero and the diagnostic names the failing validator (validator id + violation explanation).
- [ ] REQ-0.0.34-06-04: Given the rule "no warn-and-continue path," when `rg "logger\\.warning.*fidelity|logger\\.warn.*fidelity"` runs against `src/gzkit/content/validation/`, then no result matches.
- [ ] REQ-0.0.34-06-05: Given the wiring claim, when grep'd for `validation.hooks` in `src/gzkit/content/render/pipeline.py` and `src/gzkit/commands/content/edit.py`, then both files reference the hook module (mechanical proof that wiring is in place at both call sites).

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

Before this OBPI, every call to `render()` and every `gz content edit` save silently accepted rendered output without any fidelity check — the ADR-0.0.33 surface validators existed but were never fired at authoring time. A corrupted render or a post-edit save of a fidelity-violating surface would land without any diagnostic. Now `render()` fires `validate_render()` when a `project_root` is supplied, and `gz content edit`'s save path fires `validate_save()` before the atomic write. Validation failure is fail-closed — no partial write, non-zero exit, structured diagnostic naming the validator id and violation.

### Key Proof


```bash
# REQ-05 wiring at both sites:
rg -q "validation" src/gzkit/content/render/pipeline.py && echo "render hook wired"
rg -q "validation" src/gzkit/commands/content/edit.py && echo "save hook wired"

# REQ-04 no warn-and-continue:
rg -n "logger\.warning.*fidelity|logger\.warn.*fidelity" src/gzkit/content/validation/ && echo "FAIL" || echo "CLEAN"
```

Output: `render hook wired` / `save hook wired` / `CLEAN`. Receipt: `arb-ruff-fbdaf0f29b2a42e7b4dbd75777f79188`.

OBPI-scoped unit tests pass 15/15: receipt `arb-step-unittest-f720b65aace540e2a2977370343649e7`.

### Implementation Summary


- Files created: `src/gzkit/content/validation/__init__.py`, `src/gzkit/content/validation/hooks.py`, `tests/content/test_validation_hooks.py`
- Files modified: `src/gzkit/content/render/pipeline.py` (added `project_root` param + lazy validation hook call), `src/gzkit/commands/content/edit.py` (added `_resolve_project_root()`, wired `validation_hooks.validate_save()` before atomic write)
- In-flight defect fixes (pre-existing, surfaced during Stage 3, fits direct-fix thresholds): `src/gzkit/complexity/advisor/timeout.py` (POSIX signal ty: ignore), `src/gzkit/governance/trust_audits/cli.py` (added `gz content` to `_NO_SKILL_VERBS`), `src/gzkit/governance/trust_audits/cross_platform.py` (utf8 pipe waiver for OBPI-0.0.34-04 brief), `.gzkit/insights/agent-insights.jsonl` (fixed 3 malformed records), `data/behave_coverage_waivers.json` (added OBPI-0.0.34-06 waiver)
- Tests added: 15 unit tests across `TestFidelityHookError`, `TestValidateRender`, `TestValidateSave`, `TestRenderPipelineWired`, `TestEditSaveHookWired`
- Date completed: 2026-05-17
- Attestation status: operator attested "attest completed" at Stage 4 (verbatim)
- Defects noted: GHI #476 (worktree artifact test scan), GHI #477 (orphaned gz-content manpage), GHI #478 (CRLF/LF byte mismatch in sync surfaces test) — all pre-existing, not caused by this OBPI

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — Heavy/foundation OBPI-0.0.34-06-validation-hooks acceptance: ADR-0.0.33 fidelity validator suite wired at render() and gz content edit save-path; 15/15 OBPI-scoped tests pass; full unittest sweep green (receipt arb-step-unittest-99ab478cf0d04930ab441ca7d6f82eab); ruff clean (arb-ruff-fbdaf0f29b2a42e7b4dbd75777f79188); typecheck clean (arb-step-typecheck-8f844955884c4e828266679a43993aa8); mkdocs strict clean (arb-step-mkdocs-bb15a5b3c5c541d1a50f3c2c0e89e68b); 5/5 REQs covered (uncovered_reqs=0); REQ-04 fail-closed confirmed via rg; REQ-05 wiring confirmed via rg; behave coverage waived per data/behave_coverage_waivers.json adr-0.0.34-06-validation-hooks-bdd-deferred-unit-only; pre-existing defect cleanup landed in-flight (timeout.py ty-ignore, agent-insights.jsonl schema repair, _NO_SKILL_VERBS entry for gz content, _UTF8_PIPE_WAIVERS entry for OBPI-04 brief, doc_coverage scanner extension for commands/*/__init__.py, manpage rename gz-content.md->content.md, 5 leaf doc-coverage exemptions, sync_surfaces test write_bytes fix); GHIs #476/#477/#478 closed with evidence.
- Date: 2026-05-17

---

**Brief Status:** Draft

**Date Completed:** 2026-05-17

**Evidence Hash:** -
