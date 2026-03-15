---
id: OBPI-0.13.0-05-runtime-engine-integration
parent: ADR-0.13.0-obpi-pipeline-runtime-surface
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.13.0-05-runtime-engine-integration: Runtime Engine Integration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md`
- **Checklist Item:** #5 - "OBPI-0.13.0-05: Make skills, hooks, and future agent control surfaces call into the same runtime engine instead of re-implementing stage logic in prose"

**Status:** Draft

## Objective

Make skills, hooks, and future agent control surfaces call into the same
runtime engine instead of re-implementing stage logic in prose.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/pipeline_runtime.py` - shared runtime engine extracted from the CLI
- `src/gzkit/cli.py` - canonical CLI surface must consume the shared runtime
- `src/gzkit/hooks/claude.py` - generated Claude pipeline hooks must become thin wrappers
- `.claude/hooks/pipeline-router.py` - active generated router surface
- `.claude/hooks/pipeline-gate.py` - active generated write gate
- `.claude/hooks/pipeline-completion-reminder.py` - active generated reminder surface
- `.claude/hooks/obpi-completion-validator.py` - dormant compatibility hook must stop emitting stale guidance
- `.claude/hooks/README.md` - active Claude hook surface docs must match the runtime
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` - canonical wrapper skill must document the shared runtime as implemented
- `.agents/skills/gz-obpi-pipeline/SKILL.md` - Codex mirror must stay synchronized
- `.claude/skills/gz-obpi-pipeline/SKILL.md` - Claude mirror must stay synchronized
- `.github/skills/gz-obpi-pipeline/SKILL.md` - Copilot mirror must stay synchronized
- `docs/user/commands/obpi-pipeline.md` - operator manpage for the canonical runtime command
- `docs/user/concepts/workflow.md` - user workflow must point at the runtime-first loop
- `docs/user/runbook.md` - operator runbook must match the runtime-managed closeout path
- `docs/user/concepts/lanes.md` - lane guidance must reference the canonical command surface
- `docs/user/commands/index.md` - command index must describe the runtime-first execution loop
- `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/obpis/OBPI-0.12.0-05-completion-reminder-surface.md` - prior proof example must match the updated reminder output
- `tests/commands/test_obpi_pipeline.py` - CLI runtime regression coverage
- `tests/test_hooks.py` - generated hook behavior coverage
- `tests/test_pipeline_runtime.py` - direct shared-runtime coverage

## Denied Paths

- `src/gzkit/commands/status.py` - status scope is already handled by prior OBPIs
- `.gzkit/ledger.jsonl` - do not hand-edit ledger state
- New dependencies - runtime extraction must stay inside the existing stdlib/package set
- CI files and lockfiles - not required for this runtime integration tranche

## Requirements (FAIL-CLOSED)

1. ALWAYS: `src/gzkit/pipeline_runtime.py` MUST become the canonical owner of pipeline marker state, receipt loading, next-command calculation, and hook-facing reminder/blocker guidance.
1. ALWAYS: `src/gzkit/cli.py` and the generated Claude pipeline hooks MUST call the shared runtime engine instead of carrying their own copies of stage-state logic.
1. NEVER: change the marker payload schema or Heavy/Foundation human-attestation semantics established by `OBPI-0.13.0-01` through `OBPI-0.13.0-04`.
1. ALWAYS: operator-facing hook guidance MUST use the canonical `uv run gz obpi pipeline ...` / guarded-sync flow and MUST NOT tell operators to recover with stale `/gz-obpi-audit`, `/gz-obpi-sync`, or manual marker-release prose.
1. ALWAYS: the dormant `.claude/hooks/obpi-completion-validator.py` compatibility surface MUST stop advertising stale audit-first completion guidance even though it remains outside the active registration order.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md`
- [x] Related OBPIs in same ADR
- [x] `.gzkit/skills/gz-obpi-pipeline/SKILL.md`

**Prerequisites (check existence, STOP if missing):**

- [x] Existing runtime command contract in `src/gzkit/cli.py`
- [x] Existing Claude hook generator in `src/gzkit/hooks/claude.py`
- [x] Existing active hook files under `.claude/hooks/`

**Existing Code (understand current state):**

- [x] Runtime command pattern: `src/gzkit/cli.py`
- [x] Hook-generation pattern: `src/gzkit/hooks/claude.py`
- [x] Test patterns: `tests/commands/test_obpi_pipeline.py`, `tests/test_hooks.py`

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
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

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
uv run python -m unittest tests.test_pipeline_runtime tests.test_hooks tests.commands.test_obpi_pipeline -v
```

## Acceptance Criteria

- [ ] REQ-0.13.0-05-01: Given the canonical pipeline runtime in `src/gzkit/pipeline_runtime.py`, when `uv run gz obpi pipeline` runs or generated Claude pipeline hooks execute, then both surfaces derive marker state and next-step guidance from that shared runtime instead of duplicated local helpers.
- [ ] REQ-0.13.0-05-02: Given an active OBPI pipeline marker, when the router, write gate, or completion reminder emits operator guidance, then it uses the canonical `uv run gz obpi pipeline ...` / guarded-sync flow and no longer points to stale `/gz-obpi-audit`, `/gz-obpi-sync`, or manual marker-release recovery steps.
- [ ] REQ-0.13.0-05-03: Given the wrapper skill, active hook docs, and dormant validator compatibility surface, when an operator reads or triggers them, then they describe the shared runtime as implemented and no longer misstate the stage engine as future or audit-first behavior.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded in this brief and parent ADR checklist item #5 remains the active unchecked item during implementation

### Gate 2 (TDD)

```text
# Pending implementation
```

### Code Quality

```text
# Pending implementation
```

### Gate 3 (Docs)

```text
# Pending implementation
```

### Gate 4 (BDD)

```text
# Pending implementation
```

### Gate 5 (Human)

```text
# Pending implementation
```

## Value Narrative

Before this tranche, the CLI, generated hooks, and dormant compatibility hook
each carried their own interpretation of receipt loading, marker state, and
operator recovery guidance. That left the active runtime split across code,
generated scripts, and stale prose. After this tranche, one shared runtime
engine owns the stage-state contract and every operator-facing pipeline surface
points at the same canonical next commands.

## Key Proof

```text
$ printf '{"cwd":"<workspace>","tool_input":{"command":"git push origin main"}}' | uv run python .claude/hooks/pipeline-completion-reminder.py
PIPELINE COMPLETION REMINDER

Active OBPI pipeline: OBPI-0.13.0-05-runtime-engine-integration
Brief status: Accepted
Current stage: verify
Receipt state: pass

You are about to commit or push while the governance pipeline still
appears incomplete. Finish the runtime-managed closeout path first:

Next canonical command:
  uv run gz obpi pipeline OBPI-0.13.0-05-runtime-engine-integration --from=ceremony

Do not clear the pipeline marker by hand; the runtime owns it.
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Human Attestation

- Attestor: `human:<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
