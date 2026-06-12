---
id: OBPI-0.0.70-01-stop-hook-turn-end-feedback
parent: ADR-0.0.70-turn-end-feedback-and-correction-mining
item: 1
lane: Lite
status: Draft
---

# OBPI-0.0.70-01-stop-hook-turn-end-feedback: Stop Hook Turn End Feedback

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md`
- **Checklist Item:** #1 - "Stop-hook turn-end deterministic feedback — `.claude/hooks/stop-turn-feedback.py` + `Stop` matcher wiring in `.claude/settings.json`; ruff over session-dirty Python files; sub-2s budget; `stop_hook_active` loop guard; off-switch; block telemetry line; agent-actionable block prose; unit tests"

**Status:** Draft

## Objective

A Stop hook at `.claude/hooks/stop-turn-feedback.py`, wired via a `Stop` matcher in
`.claude/settings.json`, runs `ruff check` over session-dirty Python files at every agent
turn end under a sub-2-second budget; on findings it blocks the stop with agent-actionable
prose (what failed / why it is forbidden / the governed next step) so the agent
self-corrects before declaring done; it honors `stop_hook_active` (at most one block per
turn), honors the `GZ_STOP_FEEDBACK=off` environment off-switch, appends one bounded
telemetry line per block, and fails open on every internal error or timeout.

## Lane

**Lite** — No new `gz` verb, schema, or external product contract. The named counterargument — a Stop hook is operator-experienced runtime behavior — is defeated by blast-radius bounds: fail-open, `stop_hook_active` single-block, and the `GZ_STOP_FEEDBACK=off` off-switch (parent ADR § Boundary Invariants 1); Gate 5 human attestation fires regardless of lane (ADR-0.0.36).

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md` — parent ADR for intent and scope
- `.claude/hooks/stop-turn-feedback.py` **CREATE** — NEW: the hook script
- `.claude/settings.json` — `Stop` matcher wiring
- `tests/hooks/test_stop_turn_feedback.py` **CREATE** — NEW: unit tests (importlib-loading precedent: `tests/hooks/test_ghi_triage_chat_silence.py`)
- `.gitignore` — exclude the local telemetry log directory `.gzkit/sensors/`
- `src/gzkit/hooks/scripts/quality.py` — canonical template source for the hook script (reconciled in-flight 2026-06-12: `.claude/hooks/**` and `.claude/settings.json` are GENERATED surfaces owned by `setup_claude_hooks`; the hand-edit path in the original allowlist was drift)
- `src/gzkit/hooks/claude.py` — settings generation, merge ownership, setup writer, hooks README
- `src/gzkit/sync_surfaces.py` — drift-detection phase coverage for the `Stop` phase
- `tests/test_hooks.py` — generator test coherence (coupled-surface, DO IT RIGHT 1a)
- `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/obpis/OBPI-0.0.70-01-stop-hook-turn-end-feedback.md` — this brief (evidence recording)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: The hook MUST scope checks to git-dirty `*.py` files only; with no dirty Python files it MUST exit 0 silently.
1. REQUIREMENT: The hook MUST NEVER block when `stop_hook_active` is true, and MUST fail open (exit 0, no block output) on any internal error, missing tool, malformed stdin, or timeout — a turn can always end (parent ADR § Boundary Invariants, Invariant 1).
1. REQUIREMENT: Block feedback MUST satisfy the guardrail-feedback-prose bar (what failed / why it is forbidden / the governed next step) — this hook is the first enforcement consumer of OBPI-0.0.70-03's rule.
1. REQUIREMENT: `GZ_STOP_FEEDBACK=off` MUST disable the hook without editing `.claude/settings.json`.
1. REQUIREMENT: Each block MUST append exactly one JSON line to `.gzkit/sensors/stop-turn-feedback.jsonl`; the log MUST stay bounded and MUST be gitignored.
1. REQUIREMENT: The hook script MUST import stdlib only (parent ADR § Boundary Invariants, Invariant 3); ruff runs as a subprocess of the existing toolchain.
1. ALWAYS: TDD (RED→GREEN); tests assert REQ semantics, not incidental output strings.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md`
- [ ] Required path exists or is intentionally created in this OBPI: `.claude/hooks/stop-turn-feedback.py`
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

# Specific verification for this OBPI
test -f .claude/hooks/stop-turn-feedback.py
test -f tests/hooks/test_stop_turn_feedback.py
uv run -m unittest tests.hooks.test_stop_turn_feedback -q
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# --demo runs the real check pipeline against a synthetic lint violation and
# prints the exact block prose an agent would receive at turn end.
uv run python .claude/hooks/stop-turn-feedback.py --demo
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.70-01-01 [behavior]: Given session-dirty Python files with ruff findings and `stop_hook_active` false, when the hook runs, then it emits a block decision whose prose names the findings (what failed), why the stop is blocked, and the governed next step. (@covers test)
- [ ] REQ-0.0.70-01-02 [behavior]: Given `stop_hook_active` true in the stdin payload, when the hook runs, then it exits 0 without blocking regardless of lint state — at most one block per turn. (@covers test)
- [ ] REQ-0.0.70-01-03 [behavior]: Given `GZ_STOP_FEEDBACK=off` in the environment, when the hook runs, then it exits 0 without invoking ruff. (@covers test)
- [ ] REQ-0.0.70-01-04 [behavior]: Given an internal failure (ruff unavailable, subprocess timeout, malformed stdin, non-git directory), when the hook runs, then it fails open with exit 0 and no block output. (@covers test)
- [ ] REQ-0.0.70-01-05 [behavior]: Given a block is emitted, when the hook completes, then exactly one JSON telemetry line is appended to `.gzkit/sensors/stop-turn-feedback.jsonl`; the cap is 1 MiB, and at append time an over-cap log is rewritten keeping only its newest 500 lines. (@covers test)
- [ ] REQ-0.0.70-01-06 [behavior]: Given `.claude/settings.json`, when parsed, then a `Stop` matcher entry invokes `.claude/hooks/stop-turn-feedback.py` and the referenced script exists. (@covers test)
- [ ] REQ-0.0.70-01-07 [structural-fence]: The hook MUST NOT be able to trap an agent in a blocked-stop loop — `stop_hook_active` honored and fail-open on self-error are structural guarantees. Verified at ADR-0.0.70 closeout via the parent ADR `## Boundary Invariants` (Invariant 1).
- [ ] REQ-0.0.70-01-08 [behavior]: Given the `--demo` argv flag, when the hook is invoked, then it runs the real check pipeline against a synthetic lint violation and prints the block prose without reading stdin, without blocking, and without writing telemetry. (@covers test)
- [ ] REQ-0.0.70-01-09 [behavior]: Given the settings generator, when `.claude/settings.json` is produced or merged, then the `Stop` phase is gzkit-owned — present in `generate_claude_settings`, preserved by `merge_settings`, and covered by `detect_claude_settings_drift`. (@covers test)

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
RED observed 2026-06-12: uv run -m unittest tests.hooks.test_stop_turn_feedback -q
  -> FileNotFoundError: .claude/hooks/stop-turn-feedback.py (test authored first)
GREEN: Ran 11 tests in 0.047s OK (REQs 01-01..06, 01-08, 01-09, 03-02 covered)
GREEN receipt: `arb-step-unittest-721f7a2b9dc34c24a7246422592f7c64` exit_status=0 (full suite)
```

### Code Quality

```text
Lint: `arb-ruff-891d4ff9d22045769631d134d5de49f2` exit_status=0
Typecheck: `arb-step-typecheck-9ad2c564358d443f97119b315b57acc1` exit_status=0
gz check exit 0 (full pipeline incl. behave distribution invariant)
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

Before: gzkit had no deterministic sensor at the agent turn boundary — Behavior
Rules Never #5 ('do not summarize and stop') was prose-only, and an agent could end
a turn with red lint on session-dirty files (the appraisal's #1 named gap: 'agents
work blind between gate transitions'). Now: a gzkit-owned `Stop` phase runs ruff over
git-dirty Python files at every turn end and blocks with three-part prose so the
agent self-corrects in-flight; fail-open by construction (a turn can always end);
each block leaves a telemetry line so the fence's catch-rate is observable.

Discovered in-flight and reconciled into Allowed Paths: `.claude/hooks/**` and
`.claude/settings.json` are GENERATED surfaces — the hook therefore lives as a
canonical template in `src/gzkit/hooks/scripts/quality.py`, the `Stop` phase is
gzkit-owned in `generate_claude_settings`/`merge_settings`/`detect_claude_settings_drift`,
and REQ-0.0.70-01-09 pins generator ownership as the regression fence (the hand-wired
entry was observed being silently reverted by the settings sync before the fix).

### Key Proof

```
$ uv run python .claude/hooks/stop-turn-feedback.py --demo
stop-turn-feedback: BLOCKED — turn-end lint check failed across 1 dirty Python file(s).
What failed: F401 [*] `os` imported but unused --> demo_violation.py:1:8 ...
Why this is forbidden: gzkit forbids ending a turn while the cheap deterministic
tier is red (AGENTS.md Behavior Rules — Never #5; ADR-0.0.70 ...)
Governed next step: fix the findings above, verify with `uv run ruff check <files>`,
then end the turn. One block per turn — the next stop proceeds even if findings
remain (fail-open).
```
(observed output, 2026-06-12; exit 0)

### Implementation Summary

- Parent ADR § Decision item (verbatim, per Discovery Checklist): "**1. Stop-hook
  turn-end deterministic feedback (`.claude/hooks/stop-turn-feedback.py` + `Stop`
  wiring in `.claude/settings.json`).** At every agent turn end, the hook runs the
  cheapest deterministic check tier — `ruff check` over session-dirty Python files
  (git working-tree dirty `.py` paths) — under a hard sub-2-second budget ..."
- Files created/modified: `.claude/hooks/stop-turn-feedback.py` (generated),
  `tests/hooks/test_stop_turn_feedback.py`, `src/gzkit/hooks/scripts/quality.py`
  (canonical template), `src/gzkit/hooks/claude.py` (Stop phase generation/merge/
  setup/README), `src/gzkit/sync_surfaces.py` (drift coverage), `tests/test_hooks.py`,
  `.claude/settings.json` (generated), `.gitignore`
- Tests added: 11 unit tests (importlib-loaded hook module; generator ownership test)
- Date completed: 2026-06-12 (implementation; Gate 5 pending)
- Attestation status: AWAITING operator Gate 5 (universal, ADR-0.0.36)
- Defects noted: generated-surface allowlist drift reconciled in-flight (brief
  § Allowed Paths note); external-process stash/reset race against in-flight locked
  OBPIs observed mid-session — insight logged to agent-insights.jsonl

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
