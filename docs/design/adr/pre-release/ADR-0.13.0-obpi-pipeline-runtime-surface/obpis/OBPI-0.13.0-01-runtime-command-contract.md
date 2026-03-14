---
id: OBPI-0.13.0-01-runtime-command-contract
parent: ADR-0.13.0-obpi-pipeline-runtime-surface
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.13.0-01-runtime-command-contract: Runtime Command Contract

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md`
- **Checklist Item:** #1 - "OBPI-0.13.0-01: Introduce a runtime command contract such as `gz obpi pipeline <obpi>`, `--from=verify`, and `--from=ceremony`"

**Status:** Completed

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Introduce a runtime command contract such as `gz obpi pipeline <obpi>`,
`--from=verify`, and `--from=ceremony`.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/cli.py` - CLI parser, runtime launcher, and pipeline stage selection
- `src/gzkit/commands/common.py` - command-doc registration for the new surface
- `tests/commands/test_obpi_pipeline.py` - command contract and blocker coverage
- `docs/user/commands/obpi-pipeline.md` - operator manpage for the new surface
- `docs/user/commands/index.md` - command index registration
- `docs/user/concepts/workflow.md` - workflow narrative alignment
- `docs/user/runbook.md` - operator runbook alignment
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` - wrapper-skill guidance pointing at the CLI runtime

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.claude/hooks/**` - hook-wrapper rewiring belongs to `OBPI-0.13.0-05`
- stage-state schema files beyond the existing active markers - richer persistence belongs to `OBPI-0.13.0-02`
- machine-readable runtime output contracts - structured outputs belong to `OBPI-0.13.0-03`
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `gz obpi pipeline <OBPI-ID>` MUST exist as a real CLI surface under the existing `obpi` command group.
1. REQUIREMENT: The command MUST accept `--from=verify` and `--from=ceremony` and reject any other `--from` value.
1. REQUIREMENT: The command MUST resolve canonical and short-form OBPI identifiers using the existing ledger-first resolution path.
1. REQUIREMENT: Stage 1 MUST create `.claude/plans/.pipeline-active-{OBPI-ID}.json` and `.claude/plans/.pipeline-active.json` for the active OBPI.
1. REQUIREMENT: The command MUST fail closed with `BLOCKERS:` when the OBPI brief is missing, already completed, the matching plan-audit receipt verdict is `FAIL`, another OBPI is already active, or verification commands fail.
1. NEVER: This OBPI MUST NOT introduce richer stage persistence, JSON runtime output, abort/resume subcommands, or wrapper/hook rewiring.
1. ALWAYS: User docs and the wrapper skill MUST identify `uv run gz obpi pipeline` as the canonical runtime launch surface.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` - repo structure
- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md`
- [x] `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
- [x] `docs/user/commands/obpi-status.md`
- [x] `docs/user/commands/obpi-reconcile.md`

**Prerequisites (check existence, STOP if missing):**

- [x] Existing `obpi` parser exists in `src/gzkit/cli.py`
- [x] Claude plan receipt and active-marker contracts already exist under `.claude/plans/`

**Existing Code (understand current state):**

- [x] Pattern to follow: `src/gzkit/commands/status.py` fail-closed runtime output
- [x] Test patterns: `tests/commands/test_runtime.py`, `tests/test_hooks.py`

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

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
uv run python -m unittest tests.commands.test_obpi_pipeline -v
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.13.0-01-01: `gz obpi pipeline <OBPI-ID>` launches successfully, writes the active markers, and prints the follow-up `--from=verify` command.
- [x] REQ-0.13.0-01-02: `gz obpi pipeline <OBPI-ID> --from=verify` executes the OBPI verification command block plus Heavy-lane docs/BDD checks and clears markers on success.
- [x] REQ-0.13.0-01-03: `gz obpi pipeline <OBPI-ID> --from=ceremony` prints the ceremony/accounting next steps and clears markers on exit.
- [x] REQ-0.13.0-01-04: The command emits `BLOCKERS:` and exits non-zero for completed briefs, matching `FAIL` receipts, conflicting active markers, and failing verification commands.
- [x] REQ-0.13.0-01-05: Command docs, workflow docs, runbook, and wrapper skill all point to `uv run gz obpi pipeline` as the canonical runtime launch surface.

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

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run python -m unittest tests.commands.test_obpi_pipeline -v
Ran 5 tests in 0.159s
OK

uv run gz test
Ran 386 tests in 9.304s
OK
```

### Code Quality

```text
uv run gz validate --documents
All validations passed.

uv run gz lint
All checks passed!
ADR path contract check passed.
Lint passed.

uv run gz typecheck
All checks passed!
Type check passed.
```

### Gate 3 (Docs)

```text
uv run mkdocs build --strict
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/jeff/Documents/Code/gzkit/site
INFO    -  Documentation built in 0.69 seconds
```

### Gate 4 (BDD)

```text
uv run -m behave features/
2 features passed, 0 failed, 0 skipped
6 scenarios passed, 0 failed, 0 skipped
31 steps passed, 0 failed, 0 skipped
```

### Gate 5 (Human)

```text
Human attestation received on 2026-03-13: "completed"

$ uv run gz git-sync --apply --lint --test
Git sync execution
  Branch: main
  Remote: origin
  ahead=0 behind=0 diverged=False dirty=False
  Actions:
    - git fetch --prune origin
  Executed:
    - gz lint (pre-sync)
    - gz test (pre-sync)
    - gz lint (post-sync)
Git sync completed.

$ uv run gz obpi emit-receipt OBPI-0.13.0-01-runtime-command-contract --event completed --attestor "human:jeff" --evidence-json '{...}'
OBPI receipt emitted.
  OBPI: OBPI-0.13.0-01-runtime-command-contract
  Parent ADR: ADR-0.13.0-obpi-pipeline-runtime-surface
  Event: completed
  Attestor: human:jeff
```

## Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

Before this OBPI, `gz-obpi-pipeline` existed only as a skill/operator ritual,
so hooks and docs could tell an operator to run the pipeline but gzkit did not
own a first-class CLI runtime for it. Now `uv run gz obpi pipeline <OBPI-ID>`
exists as a code-owned command surface with launch, `--from=verify`, and
`--from=ceremony` entry points, active-marker compatibility for the existing
`ADR-0.12.0` hook chain, and fail-closed blockers for missing/invalid
governance prerequisites.

## Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

```text
$ uv run gz obpi pipeline OBPI-0.13.0-01-runtime-command-contract
OBPI pipeline: OBPI-0.13.0-01-runtime-command-contract
  Parent ADR: ADR-0.13.0-obpi-pipeline-runtime-surface
  Lane: heavy
  Entry: full
  Receipt: MISSING
  Stages: 1. Load Context -> 2. Implement -> 3. Verify -> 4. Present Evidence -> 5. Sync And Account

Next:
- Implement the approved OBPI within the brief allowlist.
- When implementation is ready, run: uv run gz obpi pipeline OBPI-0.13.0-01-runtime-command-contract --from=verify
```

### Implementation Summary

- Files created/modified: `src/gzkit/cli.py`, `src/gzkit/commands/common.py`,
  `tests/commands/test_obpi_pipeline.py`,
  `docs/user/commands/obpi-pipeline.md`, `docs/user/commands/index.md`,
  `docs/user/concepts/workflow.md`, `docs/user/index.md`,
  `docs/user/runbook.md`, `mkdocs.yml`,
  `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, mirrored skill files, and this
  brief.
- Tests added: `tests/commands/test_obpi_pipeline.py`
- Date completed: `2026-03-13`
- Attestation status: human attestation recorded
- Defects noted: fixed missing MkDocs nav registration for
  `docs/user/commands/obpi-pipeline.md`; fixed command-manpage examples to use
  real CLI output; fixed this brief's verification block to include Heavy-lane
  docs and BDD commands; the missing plan-audit receipt remains an explicit
  evidence gap surfaced by the runtime warning.

## Human Attestation

- Attestor: human:jeff
- Attestation: completed
- Date: 2026-03-13

---

**Brief Status:** Completed

**Date Completed:** 2026-03-13

**Evidence Hash:** acad34c
