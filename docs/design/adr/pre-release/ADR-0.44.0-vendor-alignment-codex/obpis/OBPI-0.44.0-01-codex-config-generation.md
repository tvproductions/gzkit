---
id: OBPI-0.44.0-01-codex-config-generation
parent: ADR-0.44.0-vendor-alignment-codex
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.44.0-01-codex-config-generation: Codex Config Generation

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md`
- **Checklist Item:** #1 - "OBPI-0.44.0-01: **codex-config-generation** — Generate and validate project-scoped `.codex/config.toml` from gzkit configuration while preserving user-owned settings"

**Status:** Completed

## Objective

`gz init` and control-surface sync deterministically create project-scoped
`.codex/config.toml` at the configured path, while existing operator-owned
settings survive unchanged and drift is observable.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md` — parent ADR intent and boundary invariants
- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/obpis/OBPI-0.44.0-01-codex-config-generation.md` — this execution contract and evidence
- `src/gzkit/config.py` — configurable Codex config and hook paths
- `src/gzkit/sync_surfaces.py` — deterministic Codex config renderer and sync wiring
- `src/gzkit/sync.py` — public sync facade exercised by REQ tests
- `src/gzkit/commands/init_cmd.py` — init and repair integration
- `src/gzkit/schemas/manifest.json` — manifest path registration
- `src/gzkit/validate_pkg/surface.py` — Codex config semantic validation
- `src/gzkit/validate_pkg/sync_parity.py` — generated-config drift validation
- `src/gzkit/commands/task.py` — canonical OBPI task-event identifiers required by completion accounting
- `src/gzkit/commands/validate_task_envelope.py` — lineage-compatible accounting for historical task events
- `.codex/config.toml` — generated repository baseline
- `.gzkit/manifest.json` — generated path metadata
- `tests/test_codex_config_surface.py` — generator, preservation, and config semantics
- `tests/test_config_paths.py` — Codex path configuration coverage
- `tests/commands/test_init.py` — init/repair integration coverage
- `tests/test_sync.py` — control-surface generation coverage
- `tests/test_validate_sync_parity.py` — generated-config drift coverage
- `tests/test_tasks.py` — canonical task-event identifier regression coverage
- `tests/governance/test_task_envelope_coherence.py` — historical/canonical lineage accounting coverage
- `features/agent_sync.feature` — operator-visible sync behavior
- `features/steps` — focused Codex config fixture steps for generated, operator-owned, custom-path, and drift states
- `docs/user/manpages/init.md` — generated Codex surface documentation

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.claude/**` — Claude hook behavior is unchanged in this increment
- `.agents/**` — generated skill/persona surfaces belong to OBPI-03
- `src/gzkit/pipeline_runtime.py` — harness-aware runtime belongs to OBPI-04
- `.gzkit/ledger.jsonl` direct edits — ledger events are emitted only by `gz`
- Paths not listed in Allowed Paths
- New dependencies, CI files, and lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Generate `.codex/config.toml` with `sandbox_mode =
   "workspace-write"`, project network access, and `[features].hooks = true`
   when the configured target is absent.
2. REQUIREMENT: Preserve a non-empty operator-owned config byte-for-byte across
   init, repair, and sync, using only stdlib TOML-reading and existing helpers.
3. REQUIREMENT: Resolve the Codex config path through `PathConfig`, publish the
   same path in generated manifest metadata, and write no default-path duplicate.
4. NEVER: Hide missing or stale generated config from surface/sync-parity
   validation, add a dependency, or generate hook registration in this increment.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [x] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [x] Parent ADR § Intent — the why-frame for the Decision read above.
- [x] Parent ADR file: `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` - repo structure
- [x] `AGENTS.md` and `CLAUDE.md` - agent operating contract

**Context:**

- [x] Related OBPIs in same ADR, especially OBPI-04 runtime, OBPI-02 hook policy, and OBPI-05 validation

**Prerequisites (check existence, STOP if missing):**

- [x] Parent ADR exists and its Decision item is quoted below
- [x] `.codex/config.toml` exists as the observed hand-maintained baseline
- [x] `src/gzkit/hooks/` contains established Claude and Copilot adapter precedents
- [x] `tests/commands/test_init.py` and `tests/test_codex_config_surface.py` establish adjacent test conventions

**Existing Code (understand current state):**

- [x] `src/gzkit/sync_surfaces.py`, `src/gzkit/validate_pkg/sync_parity.py`, and `src/gzkit/commands/init_cmd.py` reviewed
- [x] `tests/test_hooks.py`, `tests/test_codex_config_surface.py`, and `tests/commands/test_init.py` reviewed

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [x] Tests derived from brief acceptance criteria, not from implementation
- [x] Red-Green-Refactor cycle followed per behavior increment
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

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run -m unittest tests.test_codex_config_surface tests.test_config_paths tests.test_sync tests.test_validate_sync_parity tests.commands.test_init
uv run -m behave --tags=@REQ-0.44.0-01-01,@REQ-0.44.0-01-02,@REQ-0.44.0-01-03,@REQ-0.44.0-01-04 features/agent_sync.feature
uv run gz validate --surfaces
uv run gz agent sync control-surfaces --dry-run
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
uv run gz validate --surfaces
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.44.0-01-01 [BEHAVIOR]: Given an initialized project without a Codex surface, `gz init` creates parseable `.codex/config.toml` with workspace-write, project network access, and stable hooks enabled.
- [x] REQ-0.44.0-01-02 [BEHAVIOR]: Given operator-owned Codex config keys, rerunning init or control-surface sync preserves the non-empty file byte-for-byte.
- [x] REQ-0.44.0-01-03 [BEHAVIOR]: Given non-default `PathConfig` Codex paths, generation writes only the configured location and generated manifest metadata names the same path.
- [x] REQ-0.44.0-01-04 [BEHAVIOR]: Given a missing or stale generated Codex config, surface and sync-parity validation report the drift while an operator-owned non-empty config remains valid.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [x] Intent and scope recorded. Parent ADR Decision item is quoted in the
  Implementation Summary; plan audit passed for the approved execution plan.

### Gate 2 (TDD — Red-Green-Refactor)

```text
Scoped: Ran 170 tests in 11.582s — OK
Full: Ran 6953 tests in 66.765s — OK
Coverage: 4/4 BEHAVIOR REQs covered; 0 uncovered
Stage 3 independent verifier: PASS, 4/4 REQs

Final receipts:
- arb-step-unittest-a3249225fc4849178fb8b03065373aa0.json (scoped)
- arb-step-unittest-cd5347ddf4e04665b0f15cd374668f9d.json (full)
- arb-red-REQ-0.44.0-01-01-70c7c51ecf6c4c329ec7a4c5215bba72.json
- arb-red-REQ-0.44.0-01-02-41e5fc5b356f432292b8be4926ce7342.json
- arb-red-REQ-0.44.0-01-03-1e84ac460ba2449a8fb0f7be0f613fa2.json
- arb-red-REQ-0.44.0-01-04-e69d14dfbeac48ff90c798aeb08817f3.json

The four reconstructed-base RED witnesses are failure_class=error (weak RED),
not assertion REDs. The implementation pass separately captured assertion REDs
for missing generation, operator preservation, custom paths, stale validation,
and sync-parity discovery before each production change.
```

### Code Quality

```text
Ruff: exit_status=0 — arb-ruff-053b1b27c2804c2c8b82e61bde10c4a4.json
Typecheck: exit_status=0 — arb-step-typecheck-5cedefec6e214462a70953f650ebf3fe.json

gz-obpi-simplify findings fixed:
- identical managed config no longer incurs a write or mtime churn
- manifest-schema tests use the canonical gzkit.schemas.load_schema helper
- parity restore preserves bytes, mode, mtime, and pre-existing directory shape
- CRLF markers, normalized path aliases, zero-byte legacy defaults, directory
  targets, and project-root escapes fail safely with focused regression coverage

Completion preflight also exposed GHI #653's task-ID canonicalization regression;
the direct correction has focused task-envelope coverage and passes the repository
coherence validator. The existing oversized-module/test census remains tracked by Build-to-1.0
Movement IV ("Oversized modules ... census-driven, with working proof"); GHI
#652 is the module-size precedent and GHI #644 owns the test-management cut.
```

### Gate 3 (Docs)

```text
Documentation built in 3.14 seconds; exit_status=0.
Receipt: arb-step-mkdocs-6295e6dd754e47ada7905a035ce55f03.json
Updated docs/user/manpages/init.md with the exact generated baseline,
ownership marker semantics, custom-path behavior, and recovery procedure.
```

### Gate 4 (BDD)

```text
1 feature passed, 8 scenarios passed, 45 steps passed, 0 failed.
Receipt: arb-step-behave-9204a5b3cfb8440fb660b7c566f01fa1.json
```

### Gate 5 (Human)

```text
Human attestation received: `attest completed` (pending atomic completion record).
```

### Step 4b — Independent Adversarial Validation

- **Adversary:** independent Codex subagent, separate refute-framed context
- **Initial verdict:** REFUTED — marked operator settings were overwritten, and
  default-to-custom path transitions left an undetected duplicate.
- **Resolution:** changed sync to preserve every non-empty config; exact generated
  defaults retire safely; customized defaults remain byte-identical and are
  reported by both surface and sync-parity validation. Added assertion REDs for
  the two failures plus CRLF, path-alias, mode/mtime, directory, and escape cases.
- **Final verdict:** NOT-REFUTED after rerunning the adversary's original mutations.

```text
marked sync + real init repair: bytes_preserved=True, key_survives=True
exact default transition: default_exists=False, generated_config_count=1
customized default: old_bytes_preserved=True
surface_reports_default=True, parity_reports_default=True
focused suite: 170 passed; BDD: 8 scenarios / 45 steps passed
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

Before this increment, gzkit did not own a project-scoped Codex execution
baseline: init could leave Codex unconfigured, path metadata had no Codex config
entry, and surface checks could not distinguish generated drift from operator
settings. Now init and sync create one deterministic, validated baseline at the
configured path while preserving every non-empty unmarked operator config
byte-for-byte through both sync and repair.

### Key Proof


<!-- One concrete usage example, command, or before/after behavior. -->

`uv run gz validate --surfaces` exits 0 with:

```text
Validated: surfaces

✓ All validations passed (1 scopes).
```

The focused behavior suite independently reports `Ran 170 tests ... OK`, and
the tagged operator workflow reports 8 scenarios / 45 steps passed.

### Implementation Summary


- Parent Decision quote: **codex-config-generation** — Generate and validate project-scoped `.codex/config.toml` from gzkit configuration while preserving user-owned settings
- Implemented generated-config ownership and path metadata in `config.py`,
  `sync_surfaces.py`, and both surface/sync-parity validators; kept the shared
  manifest schema backward-compatible with v1 inputs.
- Added focused unit/init/parity coverage, eight BDD scenarios with exact-byte and
  parsed-TOML assertions, the committed `.codex/config.toml` baseline, and init
  manpage ownership/recovery guidance. Adversarial repair made parity restoration
  metadata- and directory-safe.
- Tests added: 4/4 REQs covered; 170 focused and 6953 full-suite tests pass
- Date completed: pending human Gate 5
- Attestation status: pending Gate 5
- Defects noted: the Stage 4b refutation was fixed and independently rechecked as
  NOT-REFUTED; no unresolved parity defect remains. The existing oversized-module
  and test-file census is tracked by Build-to-1.0 Movement IV, GHI #652, and GHI #644

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- Build-to-1.0 Movement IV tracks the existing oversized-module census; GHI #652
  is the open module-size precedent.
- GHI #644 tracks the existing test-suite segmentation/consolidation surface.
- GHI #653 tracks the task-event canonicalization regression found by completion
  preflight; the correction is included in this implementation and verified by
  focused task-envelope tests.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Codex config generation preserves every non-empty operator config, generates and validates the managed baseline at the configured safe path, and retires only exact legacy defaults; 6953 full tests passed (arb-step-unittest-cd5347ddf4e04665b0f15cd374668f9d.json), 170 focused tests passed (arb-step-unittest-a3249225fc4849178fb8b03065373aa0.json), ruff passed (arb-ruff-053b1b27c2804c2c8b82e61bde10c4a4.json), typecheck passed (arb-step-typecheck-5cedefec6e214462a70953f650ebf3fe.json), strict docs passed (arb-step-mkdocs-6295e6dd754e47ada7905a035ce55f03.json), and 8 BDD scenarios passed (arb-step-behave-9204a5b3cfb8440fb660b7c566f01fa1.json).
- Date: 2026-07-10

---

**Date Completed:** 2026-07-10

**Evidence Hash:** -
