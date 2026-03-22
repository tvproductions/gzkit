---
id: OBPI-0.13.0-05-runtime-engine-integration
parent: ADR-0.13.0-obpi-pipeline-runtime-surface
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.13.0-05-runtime-engine-integration: Runtime Engine Integration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md`
- **Checklist Item:** #5 - "OBPI-0.13.0-05: Make skills, hooks, and future agent control surfaces call into the same runtime engine instead of re-implementing stage logic in prose"

**Status:** Completed

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

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

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

- [x] REQ-0.13.0-05-01: Given the canonical pipeline runtime in `src/gzkit/pipeline_runtime.py`, when `uv run gz obpi pipeline` runs or generated Claude pipeline hooks execute, then both surfaces derive marker state and next-step guidance from that shared runtime instead of duplicated local helpers.
- [x] REQ-0.13.0-05-02: Given an active OBPI pipeline marker, when the router, write gate, or completion reminder emits operator guidance, then it uses the canonical `uv run gz obpi pipeline ...` / guarded-sync flow and no longer points to stale `/gz-obpi-audit`, `/gz-obpi-sync`, or manual marker-release recovery steps.
- [x] REQ-0.13.0-05-03: Given the wrapper skill, active hook docs, and dormant validator compatibility surface, when an operator reads or triggers them, then they describe the shared runtime as implemented and no longer misstate the stage engine as future or audit-first behavior.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded in this brief and parent ADR checklist item #5 remains the active unchecked item during implementation

### Gate 2 (TDD)

```text
$ uv run python -m unittest tests.test_pipeline_runtime tests.test_hooks tests.commands.test_obpi_pipeline -v
Ran 61 tests in 1.209s
OK

$ uv run gz test
Running tests...
Ran 406 tests in 12.874s
OK
Tests passed.
```

### Code Quality

```text
$ uv run gz validate --documents
All validations passed.

$ uv run gz lint
Running linters...
All checks passed!

ADR path contract check passed.
Lint passed.

$ uv run gz typecheck
Running type checker...
All checks passed!

Type check passed.

$ uv run gz git-sync --apply --lint --test
Git sync execution
  Branch: main
  Remote: origin
  ahead=1 behind=0 diverged=False dirty=True
  Actions:
    - git add -A
    - git fetch --prune origin
    - git push origin main
  Executed:
    - git add -A
    - gz lint (pre-sync)
    - gz test (pre-sync)
    - git commit
    - git push origin main
    - gz lint (post-sync)
Git sync completed.
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/jeff/Documents/Code/gzkit/site
INFO    -  Documentation built in 0.84 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
2 features passed, 0 failed, 0 skipped
6 scenarios passed, 0 failed, 0 skipped
31 steps passed, 0 failed, 0 skipped
```

### Gate 5 (Human)

```text
Human attestation received on 2026-03-15: "attest completed"

$ uv run gz obpi emit-receipt OBPI-0.13.0-05-runtime-engine-integration --event completed --attestor human:jeff --evidence-json '{...}'
OBPI receipt emitted.
  OBPI: OBPI-0.13.0-05-runtime-engine-integration
  Parent ADR: ADR-0.13.0-obpi-pipeline-runtime-surface
  Event: completed
  Attestor: human:jeff
```

### Value Narrative

Before this tranche, the CLI, generated hooks, and dormant compatibility hook
each carried their own interpretation of receipt loading, marker state, and
operator recovery guidance. That left the active runtime split across code,
generated scripts, and stale prose. After this tranche, one shared runtime
engine owns the stage-state contract and every operator-facing pipeline surface
points at the same canonical next commands.

### Key Proof

```text
$ uv run python -m unittest tests.test_pipeline_runtime tests.test_hooks tests.commands.test_obpi_pipeline -v
...
test_pipeline_completion_reminder_uses_runtime_managed_guidance ... ok
test_pipeline_router_and_gate_messages_use_runtime_command ... ok
...
Ran 61 tests in 1.209s
OK
```

### Implementation Summary

- Files created/modified: `src/gzkit/pipeline_runtime.py`, `src/gzkit/cli.py`, `src/gzkit/hooks/claude.py`, active/generated Claude hook files, the dormant `.claude/hooks/obpi-completion-validator.py`, pipeline docs, mirrored `gz-obpi-pipeline` skills, `tests/test_pipeline_runtime.py`, `tests/test_hooks.py`, `tests/commands/test_obpi_pipeline.py`, `features/steps/gz_steps.py`, and `tests/commands/test_status.py`
- Tests added: direct shared-runtime coverage in `tests/test_pipeline_runtime.py`, CLI pipeline regressions in `tests/commands/test_obpi_pipeline.py`, hook-runtime integration coverage in `tests/test_hooks.py`, and BDD fixture coverage aligned to canonical completed-receipt evidence in `features/steps/gz_steps.py`
- Date completed: 2026-03-15
- Attestation status: human attestation recorded
- Defects noted: repaired a rebase regression that dropped `reflection_issues` from `gz adr status` JSON, fixed stale completed-receipt fixtures in `tests/commands/test_status.py` and `features/steps/gz_steps.py`, and refreshed completion anchors for sibling `OBPI-02/03/04` so the parent ADR no longer collapses back into stale shared-scope drift after this tranche

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed
- Date: 2026-03-15

---

**Brief Status:** Completed

**Date Completed:** 2026-03-15

**Evidence Hash:** 7ff314f
