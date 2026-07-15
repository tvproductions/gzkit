---
id: OBPI-0.0.65-03-gz-handoff-cli-verb
parent: ADR-0.0.65-handoff-system-consolidation
item: 3
lane: Heavy
status: Completed
req_atomic:
  # Thin-adapter OBPI: each REQ is one indivisible labor unit with no step below
  # the REQ to subdivide — a single adapter function + its @covers test, one docs
  # bundle, one skill edit. seq=01-per-REQ matches the actual labor shape.
  - REQ-0.0.65-03-01  # handoff_list_cmd + TestHandoffList (one adapter fn + test)
  - REQ-0.0.65-03-02  # handoff_resume_cmd + TestHandoffResume (one adapter fn + test)
  - REQ-0.0.65-03-03  # handoff_create_cmd + TestHandoffCreate (one adapter fn + test)
  - REQ-0.0.65-03-04  # manpages/index/doc-coverage authored as one docs bundle
  - REQ-0.0.65-03-05  # gz-session-handoff SKILL.md verb reference (one skill edit)
---

# OBPI-0.0.65-03-gz-handoff-cli-verb: **gz-handoff-cli-verb** — Add `handoff` CLI verb with `create`, `resume`, `list` subcommands routing authoring through the validation gate. Add manpage under `docs/user/manpages/`. Add behave coverage for create/resume/list flows.

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/ADR-0.0.65-handoff-system-consolidation.md`
- **Checklist Item:** #3 - "OBPI-0.0.65-03: **gz-handoff-cli-verb** — Add `handoff` CLI verb with `create`, `resume`, `list` subcommands routing authoring through the validation gate. Add manpage under `docs/user/manpages/`. Add behave coverage for create/resume/list flows."

**Status:** Completed

## Objective

Ship a `handoff` CLI verb — `create`, `resume`, `list` subcommands — as a thin adapter over the shipped `src/gzkit/handoff_api.py`, so handoff authoring routes through the fail-closed `validate_handoff_document` gate instead of hand-written markdown, with heavy-lane manpages and BDD coverage. **Done** = `handoff create` refuses an invalid document (non-zero exit, no file written) and writes a valid one under `.gzkit/handoffs/`; `list` and `resume` each render a human default plus a `--json` structured form; `uv run gz cli audit` exits 0; the `gz-session-handoff` skill wields the verb.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

**Runtime adapter (the verb):**

- `src/gzkit/commands/handoff.py` — **CREATE** command module: `handoff_create_cmd`, `handoff_resume_cmd`, `handoff_list_cmd` + human/JSON renderers, wrapping the shipped `src/gzkit/handoff_api.py`. Sibling to `src/gzkit/commands/airlock.py`.
- `src/gzkit/cli/parser_maintenance.py` — register the `handoff` verb + `create`/`resume`/`list` subparsers (`_register_handoff_parsers`, mirroring `_register_frontmatter_parsers`). Homed here so OBPI-0.0.65-05 can attach `archive` to the same verb.
- `src/gzkit/cli/parser_handler_manifest.py` — map `handoff_create_cmd`/`handoff_resume_cmd`/`handoff_list_cmd` → `gzkit.commands.handoff`.

**Docs / CLI-audit parity (Gate 3):**

- `docs/user/manpages/handoff.md` — **CREATE** umbrella manpage (verb-name H1 + subcommand table).
- `docs/user/manpages/handoff-create.md` — **CREATE** `create` subcommand manpage (subcommand-name H1 + Overview/Usage/Options/Example/Exit-codes).
- `docs/user/manpages/handoff-resume.md` — **CREATE** `resume` subcommand manpage (same section shape).
- `docs/user/manpages/handoff-list.md` — **CREATE** `list` subcommand manpage (same section shape).
- `docs/user/manpages/index.md` — one linked row per subcommand.
- `config/doc-coverage.json` — one `CommandEntry` per subcommand (five surfaces + `governance_relevant: true`).
- `docs/user/runbook.md` — reference each command name (cross-coverage surface).
- `docs/governance/governance_runbook.md` — reference each command name (cross-coverage surface).

**Skill coherence (tool-skill-runbook-alignment Invariant 1):**

- `.gzkit/skills/gz-session-handoff/SKILL.md` — reference `handoff` (a skill must wield every new verb); bump `skill-version` + `last_reviewed`. Then `uv run gz agent sync control-surfaces` regenerates mirrors.

**Tests / BDD (Gate 2 + Gate 4):**

- `tests/test_handoff_cli.py` — **CREATE** `unittest` classes with `@covers("REQ-…")` on BEHAVIOR test methods.
- `features/handoff.feature` — **CREATE** `@REQ-0.0.65-03-0N`-tagged scenarios.
- `features/steps/handoff_steps.py` — **CREATE** `Given` scaffolding (global subprocess `When`/`Then` steps are reused).

**Release + brief:**

- `RELEASE_NOTES.md` — heavy-lane subcommand entry.
- `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/obpis/OBPI-0.0.65-03-gz-handoff-cli-verb.md` — this brief (evidence sections at completion).
- `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/ADR-0.0.65-handoff-system-consolidation.md` — parent ADR (checklist tick at closeout).

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/handoff_api.py` — the business logic shipped by OBPI-0.0.65-02; **imported/read, never edited** (the verb is a thin adapter over it).
- `src/gzkit/handoff_validation.py`, `src/gzkit/lock_manager.py`, `src/gzkit/ledger*.py` — registered security surfaces (`data/security_surfaces.json`); read/import only. Editing any would force `sensitivity: security` — out of scope here.
- `src/gzkit/commands/handoff_archive.py`, `src/gzkit/handoff_archive.py`, and the `handoff archive` subcommand — owned by OBPI-0.0.65-05.
- Any path not listed in Allowed Paths; new runtime dependencies; CI files; lockfiles.

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `handoff create` MUST route document authoring through `validate_handoff_document` (via `handoff_api.create_handoff`). A document with a validation violation MUST be refused — no file written, non-zero exit — never silently written. This is the ADR § Decision item #3 contract ("routes through the validation gate instead of hand-authored markdown").
1. REQUIREMENT: `handoff list` and `handoff resume` MUST be read-only — they never write, move, or delete any handoff file or ledger event.
1. REQUIREMENT: The verb MUST be homed in `src/gzkit/cli/parser_maintenance.py` so OBPI-0.0.65-05 can attach the `archive` subcommand to the same `handoff` parent (coupled-surface constraint declared in OBPI-05's Allowed Paths).
1. REQUIREMENT: The adapter MUST NOT re-implement handoff logic — it wraps the existing `handoff_api.py` public functions only. `handoff_api.py` and every registered security surface stay untouched.
1. REQUIREMENT: Every subcommand MUST offer both a human-readable default rendering and a `--json` structured form (Output-Contract parity with sibling read verbs).
1. NEVER: Mark the OBPI accepted while any scaffold default (placeholder REQ text, `test -f <dir>`, empty Demo) remains in the brief.
1. NEVER: Add a doc reference to a `handoff` verb before the parser registers it — `gz validate --cli-alignment` fails closed (exit 3) on an unresolvable verb. Register the parser first.
1. ALWAYS: Keep all edits inside the Allowed Paths; `gz cli audit` MUST exit 0 (every subcommand covered across all five doc surfaces) before acceptance.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/ADR-0.0.65-handoff-system-consolidation.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] OBPI-0.0.65-02 (`programmatic-api-implementation`) — shipped the `handoff_api.py` surface this verb wraps; read its completed brief.
- [ ] OBPI-0.0.65-05 (`handoff-archive-retention`) — the dependent that attaches `archive` to this verb in `parser_maintenance.py`; read its Allowed Paths to honor the coupled-surface constraint.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/handoff_api.py` exists and exports `create_handoff` / `resume_handoff` / `list_handoffs` / `load_handoff_chain` (the wrapped surface).
- [ ] `src/gzkit/cli/parser_maintenance.py` exists (verb-registration home).
- [ ] `src/gzkit/cli/parser_handler_manifest.py` exists (handler-name → module map).
- [ ] `data/security_surfaces.json` confirmed to NOT list the new command module or the maintenance parser (verified: only `handoff_validation.py` matches → this brief stays non-security).

**Existing Code (understand current state — read before implementing):**

- [ ] `src/gzkit/commands/airlock.py` — the exemplar command module (payload builder + `_render_human` + JSON) this adapter mirrors.
- [ ] `src/gzkit/cli/parser_governance.py` lines ~1030–1090 — the `airlock` verb + subparser registration idiom (`add_subparsers`, `add_json_flag`, `_lazy` `set_defaults`).
- [ ] `src/gzkit/handoff_api.py` — exact signatures of the wrapped functions and `HandoffValidationError` (the fail-closed contract for `create`).
- [ ] `src/gzkit/handoff_validation.py` — `REQUIRED_SECTIONS` + `validate_handoff_document` (read-only): what makes a `create` document valid.
- [ ] `tests/test_airlock_enter.py` — the `unittest` + `@covers` + `enterContext(TemporaryDirectory())` test shape.
- [ ] `features/airlock.feature` + `features/steps/airlock_steps.py` — the REQ-tagged subprocess BDD pattern (global `When`/`Then` steps reused).
- [ ] `docs/user/manpages/airlock-in.md` + `docs/user/manpages/index.md` + `config/doc-coverage.json` (airlock rows) — the manpage/index/manifest shape `gz cli audit` enforces.

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
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
uv run mkdocs build --strict
uv run gz covers OBPI-0.0.65-03 --json
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

<!-- gz-validate-skip: command-shape -->
```bash
# List handoffs newest-first as a structured payload
uv run gz handoff list --json

# List scoped to this ADR (human table). The handoff frontmatter schema keys
# adr_id in short form (ADR-X.Y.Z), so --adr takes ADR-0.0.65, not the full slug.
uv run gz handoff list --adr ADR-0.0.65

# Resume the newest handoff for an ADR — staleness classification + extracted next-step
uv run gz handoff resume --adr ADR-0.0.65

# Author a handoff through the fail-closed validation gate (writes under .gzkit/handoffs/)
uv run gz handoff create --adr ADR-0.0.65 --slug demo-gz-handoff-create --agent g0 --decisions "Demonstrate that gz handoff create routes authoring through validate_handoff_document."
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.65-03-01 [BEHAVIOR]: Given handoff files under `.gzkit/handoffs/`, when `handoff list` runs, then it returns the frontmatter-filtered handoffs newest-first; `--adr <ID>` scopes to that ADR and `--json` emits the structured `HandoffInfo` list. Proven by a `@covers`-decorated test in `tests/test_handoff_cli.py`.
- [ ] REQ-0.0.65-03-02 [BEHAVIOR]: Given handoff files for an ADR, when `handoff resume --adr <ID>` runs, then it selects the newest handoff and reports its staleness classification plus extracted next-step; `--json` emits the structured `ResumeResult`. Proven by a `@covers`-decorated test in `tests/test_handoff_cli.py`.
- [ ] REQ-0.0.65-03-03 [BEHAVIOR]: Given create inputs, when `handoff create` runs, then authoring routes through `validate_handoff_document`: a violating document is refused (non-zero exit, no file written) and a clean one is written under `.gzkit/handoffs/` with its path reported. Proven by a `@covers`-decorated test in `tests/test_handoff_cli.py` asserting both the refusal (exit + absence-of-file) and the success (file present).
- [ ] REQ-0.0.65-03-04 [SUPPORT]: The umbrella + three subcommand manpages, the `index.md` rows, and the `config/doc-coverage.json` entries exist so `gz cli audit` exits 0 — proof: `gz validate --documents` admits the doc shape + an `artifact_edited` ledger event records the manpage/manifest edits.
- [ ] REQ-0.0.65-03-05 [SUPPORT]: The `gz-session-handoff` skill wields the new `handoff` verb (tool-skill-runbook-alignment Invariant 1) — proof: `gz validate --cli-alignment` resolves the verb reference + an `artifact_edited` ledger event records the skill edit.

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

### Step 4b — Independent Adversarial Validation

- **Adversary:** Codex (`gpt-5.6-sol`), tier-1 (different-vendor), run via direct
  `codex exec` — the Codex *plugin's* background relay stalled on a dead
  shared-runtime broker, so the verdict was obtained through the healthy direct
  path. A tier-2 independent Claude subagent was also run.
- **First-pass verdict: REFUTED.** Codex broke three claims:
  1. **Weak create-routing test** — a mutant that wrote an *invalid* document
     without calling `validate_handoff_document` still passed the original
     existence-only assertions.
  2. **Weak resume staleness assertion** — set-membership let a hard-coded
     wrong-but-legal staleness value pass.
  3. **CWD-relative store** — `handoff list`/`resume` read `.gzkit/handoffs/`
     relative to the CWD.
- **Resolution:**
  1. `test_create_valid_input_writes_handoff_through_the_gate` now re-runs
     `validate_handoff_document` on the written file and asserts zero violations
     — the invalid-writer mutant is killed.
  2. Added an injectable `now` seam to `handoff_resume_cmd`; tests assert exact
     staleness at two controlled ages (`Fresh` at 2h, `Very-Stale` at ~6wk) so no
     single constant satisfies both.
  3. **Determined a false positive** — `get_project_root()` is `Path.cwd()` and
     every gz command assumes run-from-root (siblings `gz status` / `gz obpi lock
     list` also fail from a subdir). handoff already matches the gz-wide
     convention; the attempted fix was a no-op and was reverted. gz-wide
     subdirectory execution is logged as a separate out-of-scope concern in
     `.gzkit/insights/agent-insights.jsonl`.
- **Re-adjudication verdict: NOT-REFUTED** (tier-1 Codex, mutation-tested:
  `INVALID_WRITER_MUTANT_KILLED=True`, `ALL_SINGLE_CONSTANT_MUTANTS_KILLED=True`;
  read-only proven by ledger + 205-handoff hash equality; denied-path diff empty;
  ground #1 false-positive independently confirmed).

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


`gz handoff create --adr ADR-BOGUS --slug x --agent g0 --decisions "x"` exits 1 with "Invalid ADR ID format" and writes ZERO files (fail-closed through `validate_handoff_document`); `gz handoff create --adr ADR-0.0.65 ...` writes a valid handoff whose on-disk content re-passes the validator. Evidence: `tests.test_handoff_cli` 6/6 (receipt `arb-step-unittest-439d76e8ca81402fb40be33635cfc21a`), behave 5/5, `gz cli audit` 128/128, `gz covers` behavior_uncovered=0. Tier-1 Codex adversary NOT-REFUTED (mutation-tested) after REFUTED->remediation.

### Implementation Summary


- Capability: `gz handoff` verb (`create`/`resume`/`list`) as a thin adapter over the shipped `handoff_api.py` (OBPI-02); no domain logic, security surfaces untouched.
- Files created: `src/gzkit/commands/handoff.py`, `tests/test_handoff_cli.py`, `features/handoff.feature`, `features/steps/handoff_steps.py`, four manpages under `docs/user/manpages/`.
- Files modified: `parser_maintenance.py` (+handoff verb), `parser_handler_manifest.py` (handler map), `index.md`, `config/doc-coverage.json`, `runbook.md`, `governance_runbook.md`, `gz-session-handoff/SKILL.md` (+3 mirrors).
- Tests added: 6 (`TestHandoffList` x2, `TestHandoffResume` x2 exact-staleness, `TestHandoffCreate` x2 incl. gate re-validation).
- Defects fixed in-flight: brief Demo ADR-id drift (full-slug -> short-form); `handoff-resume` manpage staleness-enum drift (`Aging` -> real enum, Codex-caught); adversary-driven test hardening.
- Date completed: 2026-07-15. Attestation: operator `attest completed` (g0), Gate 5.

## Tracked Defects

- REQ-count drift: 8 declared vs 5 acceptance criteria (brief reconcile, attestor g0)

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — gz handoff verb (create/resume/list) shipped as a thin adapter over handoff_api.py routing create through the fail-closed validate_handoff_document gate; 6/6 unittest (arb-step-unittest-439d76e8ca81402fb40be33635cfc21a), behave 5/5, cli audit 128/128, covers behavior_uncovered=0; tier-1 Codex adversary NOT-REFUTED after remediation (mutation-tested); attested by g0 2026-07-15.
- Date: 2026-07-15

---

**Date Completed:** 2026-07-15

**Evidence Hash:** -
